# privacy-aware-rag-auth0
A privacy-aware internal knowledge assistant that uses Auth0 authentication and Fine-Grained Authorisation (FGA) to enforce document-level access control in a RAG workflow. Sensitive documents are retrieved only if the logged-in user is authorized.

## What you built (explained like you’re 5)

Imagine a library:

- **Auth0** is the person at the front desk who gives you a **name sticker** (a login token).
- **RAG** is a helper who runs into the library and grabs a few books that look relevant.
- **Auth0 FGA** is the **rule book** that says which books you’re allowed to read.

The important safety rule is: **we check the rule book *before* we read any book pages**.

## Quick start (no Auth0 needed yet)

This repo includes a tiny demo mode so you can prove the “manager can see salary docs, employee can’t” behavior right away.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

uvicorn app.main:app --reload --port 8000
```

Open `http://localhost:8000/` and try:

- User: `bob_employee` → ask “salary bands” → should get **403 / blocked**
- User: `alice_manager` → ask “salary bands” → should see the salary doc

Or via curl:

```bash
curl -sS -X POST http://localhost:8000/ask \
  -H 'Content-Type: application/json' \
  -H 'X-Dev-User: bob_employee' \
  -d '{"question":"What are the salary bands?"}'

curl -sS -X POST http://localhost:8000/ask \
  -H 'Content-Type: application/json' \
  -H 'X-Dev-User: alice_manager' \
  -d '{"question":"What are the salary bands?"}'
```

## Wire it to real Auth0 + Auth0 FGA

### Auth0 (JWT verification)

Set:

- `AUTH0_DOMAIN` (like `YOUR_TENANT.us.auth0.com`)
- `AUTH0_AUDIENCE` (your API identifier)

Then call `/ask` with:

- `Authorization: Bearer <access_token>`

### Auth0 FGA / OpenFGA (document-level checks)

Set:

- `FGA_API_URL`
- `FGA_STORE_ID`
- `FGA_BEARER_TOKEN`

Then run the helper to upload a model + tuples:

```bash
python scripts/fga_setup.py
```

After that, the API will call FGA’s `/check` endpoint for each candidate document before using it.
