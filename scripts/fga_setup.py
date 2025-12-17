from __future__ import annotations

import json
import os
from pathlib import Path

import httpx


def must_get(name: str) -> str:
    v = os.getenv(name)
    if not v:
        raise SystemExit(f"Missing env var: {name}")
    return v


async def main() -> None:
    """
    One-time setup helper for Auth0 FGA/OpenFGA.

    What it does:
    - uploads an authorization model
    - writes a few tuples so the demo works
    """

    api_url = must_get("FGA_API_URL").rstrip("/")
    store_id = must_get("FGA_STORE_ID")
    token = must_get("FGA_BEARER_TOKEN")

    model_path = Path(__file__).with_name("fga_authorization_model.json")
    model = json.loads(model_path.read_text(encoding="utf-8"))

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    async with httpx.AsyncClient(timeout=20) as client:
        # 1) Write auth model
        model_resp = await client.post(
            f"{api_url}/stores/{store_id}/authorization-models",
            headers=headers,
            json=model,
        )
        model_resp.raise_for_status()
        model_id = model_resp.json().get("authorization_model_id")
        print(f"Uploaded model. authorization_model_id={model_id}")

        # 2) Write tuples (relationships)
        # - group:managers#member has user:alice_manager
        # - public_handbook is directly viewable by everyone in this demo (viewer tuple)
        # - finance_budget_q4 is directly viewable by alice_manager (but not bob_employee)
        # - salary_bands_2025 is ONLY viewable by managers group via the model union
        tuples = [
            {"user": "user:alice_manager", "relation": "member", "object": "group:managers"},
            {"user": "user:alice_manager", "relation": "view", "object": "document:finance_budget_q4"},
            {"user": "user:bob_employee", "relation": "view", "object": "document:public_handbook"},
            {"user": "user:alice_manager", "relation": "view", "object": "document:public_handbook"},
        ]

        write_resp = await client.post(
            f"{api_url}/stores/{store_id}/write",
            headers=headers,
            json={"writes": {"tuple_keys": tuples}, "deletes": {"tuple_keys": []}},
        )
        write_resp.raise_for_status()
        print("Wrote tuples:")
        for t in tuples:
            print(" -", t)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())

