from __future__ import annotations

from dataclasses import dataclass

import httpx

from app.config import Settings


@dataclass(frozen=True)
class FGAObject:
    type: str
    id: str

    def to_fga(self) -> str:
        return f"{self.type}:{self.id}"


async def fga_check(
    *,
    settings: Settings,
    user: str,
    relation: str,
    obj: FGAObject,
) -> bool:
    """
    ELI5:
    - FGA is the "rule book".
    - We ask it: "Can THIS user do THIS action on THAT thing?"

    This uses the OpenFGA/Auth0 FGA Check API.
    If FGA isn't configured, we default-deny (safe), but allow an easy demo mode:
      - manager users (subject contains "manager") can view everything
      - otherwise they can only view docs with "public" in the id
    """

    if not (settings.fga_api_url and settings.fga_store_id and settings.fga_bearer_token):
        # Safe-ish local demo fallback (so you can keep building without wiring FGA yet)
        # IMPORTANT: do NOT use this in production.
        if "manager" in user.lower():
            return True
        return "public" in obj.id.lower()

    url = f"{settings.fga_api_url.rstrip('/')}/stores/{settings.fga_store_id}/check"
    headers = {
        "Authorization": f"Bearer {settings.fga_bearer_token}",
        "Content-Type": "application/json",
    }
    body = {
        "user": user,
        "relation": relation,
        "object": obj.to_fga(),
    }

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(url, headers=headers, json=body)
        resp.raise_for_status()
        data = resp.json()
        return bool(data.get("allowed", False))

