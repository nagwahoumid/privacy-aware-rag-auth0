from __future__ import annotations

from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from app.auth import AuthContext, get_auth_context
from app.config import load_settings
from app.fga import FGAObject, fga_check
from app.rag import TinyRAG, load_documents


def create_app() -> FastAPI:
    settings = load_settings()

    docs = load_documents(Path(__file__).parent / "data" / "documents.json")
    rag = TinyRAG(docs)

    app = FastAPI(title="Privacy-aware RAG (Auth0 + FGA)")

    async def auth_dep() -> AuthContext:
        return await get_auth_context(settings)

    class AskRequest(BaseModel):
        question: str

    class AskResponse(BaseModel):
        answer: str
        used_documents: list[str]
        blocked_documents: list[str]

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/", response_class=HTMLResponse)
    async def home() -> str:
        # Tiny demo UI (works great with dev auth via X-Dev-User)
        return """<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Privacy-aware RAG (Auth0 + FGA)</title>
    <style>
      body { font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial; margin: 32px; max-width: 900px; }
      input, textarea { width: 100%; padding: 10px; margin: 8px 0 16px; font-size: 14px; }
      button { padding: 10px 16px; font-size: 14px; cursor: pointer; }
      pre { background: #0b1020; color: #d6e1ff; padding: 14px; overflow: auto; }
      .hint { color: #555; font-size: 13px; }
    </style>
  </head>
  <body>
    <h2>Privacy-aware RAG (Auth0 + FGA)</h2>
    <p class="hint">
      Dev mode: set <code>X-Dev-User</code> to something like <code>alice_manager</code> or <code>bob_employee</code>.
      (When Auth0 is configured, you’ll send a real Bearer token instead.)
    </p>
    <label>User (X-Dev-User)</label>
    <input id="user" value="bob_employee" />
    <label>Question</label>
    <textarea id="q" rows="3">What are the salary bands?</textarea>
    <button id="go">Ask</button>
    <pre id="out"></pre>
    <script>
      const out = document.getElementById('out');
      document.getElementById('go').onclick = async () => {
        out.textContent = 'Loading...';
        const user = document.getElementById('user').value;
        const question = document.getElementById('q').value;
        const r = await fetch('/ask', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-Dev-User': user },
          body: JSON.stringify({ question })
        });
        const text = await r.text();
        try { out.textContent = JSON.stringify(JSON.parse(text), null, 2); }
        catch { out.textContent = text; }
      };
    </script>
  </body>
</html>"""

    @app.post("/ask", response_model=AskResponse)
    async def ask(req: AskRequest, auth: AuthContext = Depends(auth_dep)) -> AskResponse:
        # 1) Retrieve candidate docs (like "pages that might help")
        hits = rag.search(req.question, top_k=settings.rag_top_k)

        # 2) Filter using FGA BEFORE we use the text (the key safety step)
        allowed_docs = []
        blocked = []
        for doc, _score in hits:
            ok = await fga_check(
                settings=settings,
                user=f"user:{auth.subject}",
                relation="view",
                obj=FGAObject(type="document", id=doc.id),
            )
            if ok:
                allowed_docs.append(doc)
            else:
                blocked.append(doc.id)

        if not allowed_docs:
            raise HTTPException(
                status_code=403,
                detail="No authorized documents matched your question.",
            )

        # 3) "Generate" answer (toy): stitch together snippets only from allowed docs
        context = "\n\n".join(f"[{d.id}] {d.title}\n{d.text}" for d in allowed_docs)
        answer = (
            "Here’s what I found in the documents you’re allowed to see:\n\n"
            + context
        )

        return AskResponse(
            answer=answer,
            used_documents=[d.id for d in allowed_docs],
            blocked_documents=blocked,
        )

    return app


app = create_app()

