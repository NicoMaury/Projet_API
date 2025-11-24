"""Application configuration utilities."""

from functools import lru_cache
from typing import Optional

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Strongly typed application settings loaded from the environment."""

    API_TITLE: str = Field("Rail Traffic Analytics", env="API_TITLE")
    API_VERSION: str = Field("0.1.0", env="API_VERSION")


    KEYCLOAK_JWKS_URL: AnyHttpUrl = Field(..., env="KEYCLOAK_JWKS_URL")
    KEYCLOAK_AUDIENCE: str = Field(..., env="KEYCLOAK_AUDIENCE")
    KEYCLOAK_ISSUER: AnyHttpUrl = Field(..., env="KEYCLOAK_ISSUER")
    KEYCLOAK_CLIENT_SECRET: Optional[str] = Field(None, env="KEYCLOAK_CLIENT_SECRET")

    # SNCF Data sources
    SNCF_DATASET_URL: AnyHttpUrl = Field(
        "https://data.sncf.com/api/explore/v2.1/catalog/datasets/liste-des-gares/records?limit=100",
        env="SNCF_DATASET_URL",
    )

    OPENDATA_API_BASE_URL: AnyHttpUrl = Field(
        "https://data.sncf.com/api/explore/v2.1", env="OPENDATA_API_BASE_URL"
    )
    OPENDATA_API_KEY: Optional[str] = Field(None, env="OPENDATA_API_KEY")

    # Navitia.io configuration
    NAVITIA_API_BASE_URL: AnyHttpUrl = Field(
        "https://api.navitia.io/v1", env="NAVITIA_API_BASE_URL"
    )
    NAVITIA_API_KEY: Optional[str] = Field(None, env="NAVITIA_API_KEY")

    # OpenDataSoft configuration
    OPENDATASOFT_BASE_URL: AnyHttpUrl = Field(
        "https://public.opendatasoft.com/api/explore/v2.1",
        env="OPENDATASOFT_BASE_URL"
    )

    REQUEST_TIMEOUT_SECONDS: float = Field(10.0, env="REQUEST_TIMEOUT_SECONDS")
    DATABASE_URL: str = Field(
        "postgresql+psycopg://rail_user:rail_password@localhost:5432/rail_analytics",
        env="DATABASE_URL",
    )

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8"
    }


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached Settings instance."""

    return Settings()
