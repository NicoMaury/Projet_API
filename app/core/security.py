"""Keycloak security utilities for JWT validation."""

from functools import lru_cache
from typing import Any, Dict

from fastapi import HTTPException, Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from jwt import InvalidTokenError, PyJWKClient

from app.core.config import get_settings


class KeycloakTokenVerifier:
    """Validates JWT access tokens issued by Keycloak."""

    def __init__(self, jwks_url: str, audience: str, issuer: str) -> None:
        self._jwks_url = jwks_url
        self._audience = audience
        self._issuer = issuer
        self._jwks_client = PyJWKClient(jwks_url)

    def verify(self, token: str) -> Dict[str, Any]:
        """Validate a JWT token and return its payload."""

        try:
            signing_key = self._jwks_client.get_signing_key_from_jwt(token)
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                audience=self._audience,
                issuer=self._issuer,
                options={"require": ["exp", "iss", "aud"]},
            )
        except InvalidTokenError as exc:  # pragma: no cover - defensive
            raise HTTPException(status_code=401, detail="Invalid authorization token") from exc

        return payload


@lru_cache(maxsize=1)
def get_token_verifier() -> KeycloakTokenVerifier:
    """Create a cached token verifier instance."""

    settings = get_settings()
    return KeycloakTokenVerifier(
        jwks_url=settings.KEYCLOAK_JWKS_URL,
        audience=settings.KEYCLOAK_AUDIENCE,
        issuer=str(settings.KEYCLOAK_ISSUER),
    )


http_bearer = HTTPBearer(auto_error=False)


async def require_keycloak_token(
    request: Request, credentials: HTTPAuthorizationCredentials = Security(http_bearer)
) -> Dict[str, Any]:
    """FastAPI dependency enforcing Keycloak JWT validation for every endpoint."""


    if credentials is None or not credentials.credentials:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    token = credentials.credentials
    payload = get_token_verifier().verify(token)

    request.state.token_payload = payload
    request.state.user_id = payload.get("sub")

    return payload
