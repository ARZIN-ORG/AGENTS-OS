from __future__ import annotations

import os
import time
from typing import Any, Optional

import httpx
import jwt
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

APP_NAME = "governance-console-api"

# ---- Locked constraints (Phase-1) ----
# - No agent publishes operational AACP messages directly.
# - This API is a Control-Plane facade (read, propose, request-permit), not an execution plane.


def env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


class Settings(BaseModel):
    phase: str = Field(default=env("AGENTOS_PHASE", "phase1"))

    # Upstream services (BL06/07/08/17/19)
    registry_url: str = Field(default=env("BL06_REGISTRY_URL", "http://agent-registry:8080"))
    policy_url: str = Field(default=env("BL07_POLICY_URL", "http://policy-plane:8080"))
    permit_url: str = Field(default=env("BL08_PERMIT_URL", "http://permit-service:8080"))
    intent_url: str = Field(default=env("BL17_INTENT_URL", "http://intent-gateway:8080"))
    governance_url: str = Field(default=env("BL19_GOVCON_URL", "http://governance-console:8080"))

    audit_sink_url: str = Field(default=env("BL08_AUDIT_SINK_URL", "http://audit-sink:8080"))

    # Auth / RBAC / SSO
    auth_enabled: bool = Field(default=env("AUTH_ENABLED", "true").lower() == "true")
    jwt_issuer: str = Field(default=env("JWT_ISSUER", ""))
    jwt_audience: str = Field(default=env("JWT_AUDIENCE", ""))
    jwt_jwks_url: str = Field(default=env("JWT_JWKS_URL", ""))
    jwt_hs256_secret: str = Field(default=env("JWT_HS256_SECRET", ""))  # dev fallback

    cors_allow_origins: list[str] = Field(default_factory=lambda: [o for o in env("CORS_ALLOW_ORIGINS", "*").split(",") if o])


SETTINGS = Settings()


class Principal(BaseModel):
    sub: str
    name: Optional[str] = None
    roles: list[str] = Field(default_factory=list)
    scopes: list[str] = Field(default_factory=list)


async def get_jwks_client() -> Optional[jwt.PyJWKClient]:
    if not SETTINGS.jwt_jwks_url:
        return None
    return jwt.PyJWKClient(SETTINGS.jwt_jwks_url)


async def authenticate(authorization: str | None = Header(default=None)) -> Principal:
    if not SETTINGS.auth_enabled:
        return Principal(sub="dev", name="dev", roles=["admin"], scopes=["*"])

    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="missing_bearer_token")

    token = authorization.split(" ", 1)[1].strip()

    # Prefer JWKS (prod). Fallback to HS256 secret (dev).
    try:
        if SETTINGS.jwt_jwks_url:
            jwks = await get_jwks_client()
            assert jwks is not None
            signing_key = jwks.get_signing_key_from_jwt(token).key
            payload = jwt.decode(
                token,
                signing_key,
                algorithms=["RS256", "ES256"],
                audience=SETTINGS.jwt_audience or None,
                issuer=SETTINGS.jwt_issuer or None,
                options={"verify_aud": bool(SETTINGS.jwt_audience), "verify_iss": bool(SETTINGS.jwt_issuer)},
            )
        else:
            if not SETTINGS.jwt_hs256_secret:
                raise HTTPException(status_code=500, detail="jwt_verifier_not_configured")
            payload = jwt.decode(token, SETTINGS.jwt_hs256_secret, algorithms=["HS256"], options={"verify_aud": False, "verify_iss": False})

    except jwt.PyJWTError as e:
        raise HTTPException(status_code=401, detail=f"invalid_token:{type(e).__name__}")

    roles = payload.get("roles") or payload.get("role") or []
    if isinstance(roles, str):
        roles = [roles]

    scopes = payload.get("scope") or payload.get("scopes") or []
    if isinstance(scopes, str):
        scopes = scopes.split()

    return Principal(
        sub=str(payload.get("sub") or payload.get("uid") or "unknown"),
        name=payload.get("name"),
        roles=list(roles),
        scopes=list(scopes),
    )


def require_role(*needed: str):
    async def _dep(p: Principal = Depends(authenticate)) -> Principal:
        if not SETTINGS.auth_enabled:
            return p
        if any(r in p.roles for r in needed):
            return p
        raise HTTPException(status_code=403, detail="forbidden")

    return _dep


def new_app() -> FastAPI:
    app = FastAPI(title=APP_NAME, version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=SETTINGS.cors_allow_origins,
        allow_credentials=True,
        allow_methods=["*"] ,
        allow_headers=["*"],
    )

    @app.get("/health")
    async def health() -> dict[str, Any]:
        return {
            "service": APP_NAME,
            "status": "ok",
            "phase": SETTINGS.phase,
            "ts": int(time.time()),
        }

    @app.get("/whoami")
    async def whoami(p: Principal = Depends(authenticate)) -> dict[str, Any]:
        return p.model_dump()

    # --- Overview (lightweight cross-service snapshot) ---
    @app.get("/v1/overview")
    async def overview(p: Principal = Depends(authenticate)) -> dict[str, Any]:
        # Minimal calls; do not fan out aggressively.
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Registry: list agents (count)
            reg = await safe_get(client, f"{SETTINGS.registry_url}/v1/agents", p)
            pol = await safe_get(client, f"{SETTINGS.policy_url}/v1/policies", p)
            return {
                "system": {"phase": SETTINGS.phase, "build": env("AGENTOS_BUILD", "dev"), "mode": "control-plane"},
                "counts": {
                    "agents": len(reg.get("items", [])) if isinstance(reg, dict) else None,
                    "policies": len(pol.get("items", [])) if isinstance(pol, dict) else None,
                },
            }

    # --- Direct pass-throughs (read-only by default) ---
    @app.get("/v1/agents")
    async def list_agents(p: Principal = Depends(authenticate)) -> Any:
        return await proxy_get(f"{SETTINGS.registry_url}/v1/agents", p)

    @app.get("/v1/policies")
    async def list_policies(p: Principal = Depends(authenticate)) -> Any:
        return await proxy_get(f"{SETTINGS.policy_url}/v1/policies", p)

    @app.get("/v1/channels")
    async def list_channels(p: Principal = Depends(authenticate)) -> Any:
        # Channel manager lives in control-plane; usually inside BL05/08 wiring. If not present, return empty.
        url = env("BL05_CHANNEL_URL", "")
        if not url:
            return {"items": []}
        return await proxy_get(f"{url.rstrip('/')}/v1/channels", p)

    @app.get("/v1/permits")
    async def list_permits(p: Principal = Depends(authenticate)) -> Any:
        return await proxy_get(f"{SETTINGS.permit_url}/v1/permits", p)

    @app.get("/v1/audit")
    async def list_audit(p: Principal = Depends(authenticate)) -> Any:
        return await proxy_get(f"{SETTINGS.audit_sink_url}/v1/audit", p)

    # --- Intent -> Review -> Permit (strict human-in-the-loop) ---
    class IntentIn(BaseModel):
        text: str
        channel: str = "mgmt"

    @app.post("/v1/intent/translate")
    async def translate_intent(body: IntentIn, p: Principal = Depends(authenticate)) -> Any:
        # Intent service returns a structured intent draft. No execution here.
        return await proxy_post(f"{SETTINGS.intent_url}/v1/intent/translate", p, body.model_dump())

    class PermitRequestIn(BaseModel):
        intent: dict[str, Any]
        justification: str

    @app.post("/v1/permits/request")
    async def request_permit(body: PermitRequestIn, p: Principal = Depends(require_role("admin", "operator", "governance"))) -> Any:
        # Creates a permit record in BL08. BL08 should enforce policy + signatures.
        return await proxy_post(f"{SETTINGS.permit_url}/v1/permits/request", p, body.model_dump())

    return app


async def safe_get(client: httpx.AsyncClient, url: str, p: Principal) -> Any:
    try:
        r = await client.get(url, headers=auth_headers(p))
        if r.status_code >= 400:
            return {"error": f"upstream_{r.status_code}", "url": url}
        return r.json()
    except Exception as e:
        return {"error": "upstream_exception", "type": type(e).__name__, "url": url}


def auth_headers(p: Principal) -> dict[str, str]:
    # This BFF is typically behind the same auth layer; still forward identity where needed.
    return {
        "x-principal-sub": p.sub,
        "x-principal-roles": ",".join(p.roles),
        "x-principal-scopes": " ".join(p.scopes),
    }


async def proxy_get(url: str, p: Principal) -> Any:
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(url, headers=auth_headers(p))
        if r.status_code >= 400:
            raise HTTPException(status_code=502, detail={"upstream": url, "status": r.status_code, "body": r.text[:500]})
        return r.json()


async def proxy_post(url: str, p: Principal, payload: dict[str, Any]) -> Any:
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.post(url, json=payload, headers=auth_headers(p))
        if r.status_code >= 400:
            raise HTTPException(status_code=502, detail={"upstream": url, "status": r.status_code, "body": r.text[:500]})
        return r.json()


app = new_app()
