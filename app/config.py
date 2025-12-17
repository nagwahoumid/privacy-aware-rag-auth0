from __future__ import annotations

from pydantic import BaseModel


class Settings(BaseModel):
    # Auth0 (API)
    auth0_domain: str | None = None  # e.g. "your-tenant.us.auth0.com"
    auth0_audience: str | None = None  # e.g. "https://rag-api"
    auth0_issuer: str | None = None  # optional override; defaults to https://{domain}/
    allow_dev_auth: bool = True  # allow X-Dev-User header when Auth0 not configured

    # Auth0 FGA / OpenFGA
    fga_api_url: str | None = None  # e.g. "https://api.us1.fga.dev"
    fga_store_id: str | None = None
    fga_model_id: str | None = None  # optional; not required for checks
    fga_bearer_token: str | None = None  # simplest demo auth (personal access token)

    # RAG
    rag_top_k: int = 3


def load_settings() -> Settings:
    """
    Loads settings from environment variables (fast + simple).
    We use pydantic primarily for defaults and type-safety.
    """
    import os

    return Settings(
        auth0_domain=os.getenv("AUTH0_DOMAIN"),
        auth0_audience=os.getenv("AUTH0_AUDIENCE"),
        auth0_issuer=os.getenv("AUTH0_ISSUER"),
        allow_dev_auth=os.getenv("ALLOW_DEV_AUTH", "true").lower() in {"1", "true", "yes"},
        fga_api_url=os.getenv("FGA_API_URL"),
        fga_store_id=os.getenv("FGA_STORE_ID"),
        fga_model_id=os.getenv("FGA_MODEL_ID"),
        fga_bearer_token=os.getenv("FGA_BEARER_TOKEN"),
        rag_top_k=int(os.getenv("RAG_TOP_K", "3")),
    )

