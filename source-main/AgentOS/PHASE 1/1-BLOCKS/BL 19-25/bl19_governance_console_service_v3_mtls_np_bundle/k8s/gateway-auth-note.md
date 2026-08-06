# Gateway/Auth integration (Phase-1)

Phase-1 stance: **no fake crypto** inside the console.  
JWT verification must be performed by a trusted gateway (Envoy/Nginx/Traefik/APIM).

Gateway forwards:
- X-Auth-Subject: <user-id>
- X-Auth-Roles: comma-separated roles

Console enforces:
- subject present
- roles present
- at least one role in OIDC_ALLOWED_ROLES

Phase-2 upgrade:
- add PyJWT/python-jose and validate JWT locally against JWKS.
