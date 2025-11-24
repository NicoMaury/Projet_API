"""Keycloak security utilities for JWT validation."""

import logging
from functools import lru_cache
from typing import Any, Dict

from fastapi import HTTPException, Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from jwt import InvalidAudienceError, InvalidTokenError, PyJWKClient, PyJWKClientError

from app.core.config import get_settings


class KeycloakTokenVerifier:
    """Validates JWT access tokens issued by Keycloak."""

    def __init__(self, jwks_url: str, audience: str, issuer: str) -> None:
        self._jwks_url = jwks_url
        self._audience = audience
        self._issuer = issuer
        self._jwks_client = PyJWKClient(jwks_url, cache_keys=False)

    def verify(self, token: str) -> Dict[str, Any]:
        """Validate a JWT token and return its payload."""

        try:
            signing_key = self._jwks_client.get_signing_key_from_jwt(token)
        except PyJWKClientError:
            logging.getLogger(__name__).warning(
                "Cache JWKS invalide, tentative de rafraîchissement à chaud."
            )
            self._jwks_client = PyJWKClient(self._jwks_url, cache_keys=False)
            try:
                signing_key = self._jwks_client.get_signing_key_from_jwt(token)
            except PyJWKClientError as exc:
                logging.getLogger(__name__).error(
                    "Impossible de récupérer la clé publique pour le token reçu: %s", exc
                )
                raise HTTPException(status_code=503, detail="Unable to verify authorization token") from exc

        base_options = {"require": ["exp", "iss"]}

        def _decode(verify_audience: bool) -> Dict[str, Any]:
            options = dict(base_options)
            options["verify_aud"] = verify_audience
            decode_kwargs = {
                "jwt": token,
                "key": signing_key.key,
                "algorithms": ["RS256"],
                "issuer": self._issuer,
                "options": options,
            }
            if verify_audience and self._audience:
                decode_kwargs["audience"] = self._audience
            return jwt.decode(**decode_kwargs)  # type: ignore[arg-type]

        try:
            if self._audience:
                return _decode(verify_audience=True)
            return _decode(verify_audience=False)
        except InvalidAudienceError:
            logging.getLogger(__name__).warning(
                "JWT received sans claim 'aud' ou audience inattendue. Validation poursuivie sans contrôle d'audience."
            )
            return _decode(verify_audience=False)
        except InvalidTokenError as exc:  # pragma: no cover - defensive
            raise HTTPException(status_code=401, detail="Invalid authorization token") from exc


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
