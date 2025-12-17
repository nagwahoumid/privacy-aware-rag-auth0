from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Document:
    id: str
    title: str
    text: str


def _tokenize(text: str) -> list[str]:
    # tiny, dependency-free tokenizer
    words = re.findall(r"[a-zA-Z0-9_]+", text.lower())
    return [w for w in words if len(w) > 1]


class TinyRAG:
    """
    ELI5:
    - RAG is like "find the best pages in a book, then answer using only those pages".
    - This is a toy retriever: it scores docs by overlapping words.
      It's not as smart as embeddings, but it's easy to run anywhere.
    """

    def __init__(self, docs: list[Document]) -> None:
        self.docs = docs
        self._doc_terms: dict[str, dict[str, int]] = {}
        self._df: dict[str, int] = {}

        for d in docs:
            tf: dict[str, int] = {}
            for w in _tokenize(d.title + " " + d.text):
                tf[w] = tf.get(w, 0) + 1
            self._doc_terms[d.id] = tf
            for w in tf.keys():
                self._df[w] = self._df.get(w, 0) + 1

    def search(self, query: str, *, top_k: int) -> list[tuple[Document, float]]:
        q = _tokenize(query)
        if not q:
            return []
        N = len(self.docs)
        scores: list[tuple[Document, float]] = []
        for d in self.docs:
            tf = self._doc_terms.get(d.id, {})
            score = 0.0
            for w in q:
                if w not in tf:
                    continue
                # simple TF-IDF-ish score
                df = self._df.get(w, 1)
                idf = math.log((N + 1) / (df + 1)) + 1.0
                score += tf[w] * idf
            if score > 0:
                scores.append((d, score))
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]


def load_documents(path: str | Path) -> list[Document]:
    p = Path(path)
    data = json.loads(p.read_text(encoding="utf-8"))
    docs: list[Document] = []
    for item in data:
        docs.append(
            Document(
                id=str(item["id"]),
                title=str(item.get("title", "")),
                text=str(item.get("text", "")),
            )
        )
    return docs

