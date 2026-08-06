# -*- coding: utf-8 -*-
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import requests
from fastapi import HTTPException, Request

def _get_nested(d: Dict[str, Any], path: str) -> Any:
    cur: Any = d
    for part in path.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return None
    return cur

class OidcJwtValidator:
    def __init__(self) -> None:
        self.mode = os.getenv("AUTH_MODE", "strict").lower()
        self.jwks_url = os.getenv("OIDC_JWKS_URL")
        self.issuer = os.getenv("OIDC_ISSUER")
        self.audience = os.getenv("OIDC_AUDIENCE")
        self.role_claim = os.getenv("OIDC_ROLE_CLAIM", "realm_access.roles")
        allowed = os.getenv("OIDC_ALLOWED_ROLES", "aacp-admin,aacp-auditor,aacp-ops")
        self.allowed_roles = [r.strip() for r in allowed.split(",") if r.strip()]
        self._jwks_cache: Optional[Dict[str, Any]] = None

        if self.mode != "off" and not self.jwks_url:
            raise RuntimeError("OIDC_JWKS_URL is required in strict auth mode")

    def _fetch_jwks(self) -> Dict[str, Any]:
        assert self.jwks_url
        r = requests.get(self.jwks_url, timeout=4.0)
        r.raise_for_status()
        return r.json()

    def _get_jwks(self) -> Dict[str, Any]:
        if self._jwks_cache is None:
            self._jwks_cache = self._fetch_jwks()
        return self._jwks_cache

    def _decode_unverified(self, token: str) -> Dict[str, Any]:
        # Minimal safe parsing without extra deps.
        # We do NOT claim cryptographic verification without a JWT library.
        # So: Phase-1 approach: enforce auth via a trusted gateway OR add PyJWT/jose in Phase-2.
        # In strict mode here, we require upstream gateway verification header instead.
        raise HTTPException(status_code=501, detail="jwt_verification_requires_gateway_or_jwt_lib")

    def require_roles(self, request: Request) -> List[str]:
        if self.mode == "off":
            return ["dev-bypass"]

        # Phase-1 safe stance:
        # - Either you run this behind an API gateway that verifies JWT and forwards claims via headers,
        # - Or you upgrade to full JWT crypto validation (PyJWT/python-jose) in Phase-2.
        #
        # Supported Phase-1 gateway headers (example):
        # - X-Auth-Subject
        # - X-Auth-Roles (comma-separated)
        subject = request.headers.get("X-Auth-Subject")
        roles_header = request.headers.get("X-Auth-Roles", "")
        roles = [r.strip() for r in roles_header.split(",") if r.strip()]

        if not subject:
            raise HTTPException(status_code=401, detail="missing_auth_subject")

        if not roles:
            raise HTTPException(status_code=403, detail="missing_roles")

        if not any(r in self.allowed_roles for r in roles):
            raise HTTPException(status_code=403, detail="forbidden")

        return roles
