from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx
import jwt
from fastapi import Header, HTTPException

from app.config import Settings


@dataclass(frozen=True)
class AuthContext:
    """
    The "who is calling?" info we care about.
    Think: name tag on the user.
    """

    subject: str  # Auth0 `sub`, e.g. "auth0|abc123"


class JWKSCache:
    def __init__(self) -> None:
        self._jwks: dict[str, Any] | None = None
        self._jwks_url: str | None = None

    async def get(self, jwks_url: str) -> dict[str, Any]:
        if self._jwks is not None and self._jwks_url == jwks_url:
            return self._jwks
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(jwks_url)
            resp.raise_for_status()
            self._jwks = resp.json()
            self._jwks_url = jwks_url
            return self._jwks


jwks_cache = JWKSCache()


async def get_auth_context(
    settings: Settings,
    authorization: str | None = Header(default=None),
    x_dev_user: str | None = Header(default=None),
) -> AuthContext:
    """
    ELI5:
    - Auth0 is the "ticket machine".
    - The API checks your ticket (JWT) and reads the name on it (sub).
    """

    # Dev-mode fallback so you can run the demo without Auth0 set up yet.
    if (not settings.auth0_domain or not settings.auth0_audience) and settings.allow_dev_auth:
        if not x_dev_user:
            raise HTTPException(
                status_code=401,
                detail="Auth not configured. Provide X-Dev-User header (or set AUTH0_DOMAIN/AUTH0_AUDIENCE).",
            )
        return AuthContext(subject=x_dev_user)

    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")

    token = authorization.split(" ", 1)[1].strip()
    issuer = settings.auth0_issuer or f"https://{settings.auth0_domain}/"
    jwks_url = f"{issuer}.well-known/jwks.json"

    jwks = await jwks_cache.get(jwks_url)

    try:
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        if not kid:
            raise HTTPException(status_code=401, detail="JWT missing kid")

        key = next((k for k in jwks.get("keys", []) if k.get("kid") == kid), None)
        if not key:
            raise HTTPException(status_code=401, detail="Unknown signing key")

        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience=settings.auth0_audience,
            issuer=issuer,
        )
    except jwt.PyJWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}") from e

    sub = payload.get("sub")
    if not sub:
        raise HTTPException(status_code=401, detail="Token missing sub")

    return AuthContext(subject=str(sub))

