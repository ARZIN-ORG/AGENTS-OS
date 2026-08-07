import os

class OidcJwtValidator:
    def __init__(self):
        # اگر متغیر محیطی AUTH_ENABLED به صراحت "true" نباشد، احراز هویت غیرفعال می‌شود
        self.enabled = os.getenv("AUTH_ENABLED", "false").lower() == "true"
        
        if not self.enabled:
            print("ℹ️ Auth disabled (AUTH_ENABLED=false)")
            return

        jwks_url = os.getenv("OIDC_JWKS_URL")
        if not jwks_url:
            raise RuntimeError("OIDC_JWKS_URL is required when AUTH_ENABLED=true")
        # ادامه کد ...
