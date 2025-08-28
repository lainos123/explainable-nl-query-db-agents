
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import json, os
import numpy as np

# ------------------------------
# OpenAI Embedding backend only
# ------------------------------

class OpenAIBackend:
    """
    OpenAI embeddings backend.
    - Default model: text-embedding-3-small
    - Expects OPENAI_API_KEY in environment.
    """
    name: str = "openai"
    dim: Optional[int] = None

    def __init__(self, model: str = "text-embedding-3-small", batch_size: int = 128):
        try:
            from openai import OpenAI  # type: ignore
        except Exception as e:
            raise RuntimeError("OpenAI SDK not available. Install 'openai' (>= 1.0).") from e
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY not set in environment.")
        self.client = OpenAI()
        self.model = model
        self.batch_size = batch_size

    def encode(self, texts: List[str]) -> np.ndarray:
        out = []
        bs = self.batch_size
        for i in range(0, len(texts), bs):
            chunk = texts[i:i+bs]
            resp = self.client.embeddings.create(model=self.model, input=chunk)
            vecs = [np.asarray(d.embedding, dtype="float32") for d in resp.data]
            out.append(np.vstack(vecs))
        arr = np.vstack(out) if out else np.zeros((0, 1536), dtype="float32")
        # Normalize for cosine similarity with inner product
        norms = np.linalg.norm(arr, axis=1, keepdims=True) + 1e-12
        arr = arr / norms
        return arr

    def encode_one(self, text: str) -> np.ndarray:
        return self.encode([text])[0:1]


# ------------------------------
# Schema cards from Spider tables.json (unchanged)
# ------------------------------

def build_schema_cards(tables_json_path: Path, max_cols_per_table: int = 12) -> Dict[str, Any]:
    """
    Read Spider tables.json and produce a compact text summary per DB:
      return { 'db_ids': [...], 'cards': [...] }
    Each 'card' is multiline text that lists tables, columns(types),
    and foreign key hints to boost semantic matching.
    """
    raw = json.loads(tables_json_path.read_text(encoding="utf-8"))
    tables_all = raw["db"] if isinstance(raw, dict) and "db" in raw else raw

    db_ids: List[str] = []
    cards: List[str] = []

    for db in tables_all:
        db_id = db["db_id"]
        tnames = db.get("table_names_original") or db.get("table_names", [])
        columns = db.get("column_names_original") or db.get("column_names", [])  # [[table_id, col], ...]
        ctypes = db.get("column_types", [])
        fks = db.get("foreign_keys", [])  # pairs of column indices

        # table -> [(col_name, col_type), ...]
        by_table: Dict[str, List[Tuple[str,str]]] = {}
        for idx, (tid, col) in enumerate(columns):
            if tid >= 0:
                tname = tnames[tid]
                by_table.setdefault(tname, []).append((col, ctypes[idx] if idx < len(ctypes) else "text"))

        lines = [f"[DB:{db_id}]"]
        for t in tnames:
            cols = ", ".join([f"{c}({ct})" for c, ct in (by_table.get(t, [])[:max_cols_per_table])])
            lines.append(f"- {t}: {cols}")

        if fks:
            # add FK hints
            def col_name(ci):
                if 0 <= ci < len(columns):
                    tid, col = columns[ci]
                    if tid >= 0:
                        return f"{tnames[tid]}.{col}"
                return f"col{ci}"
            fk_pairs = [f"{col_name(a)} -> {col_name(b)}" for a, b in fks]
            lines.append("ForeignKeys: " + "; ".join(fk_pairs))

        cards.append("\\n".join(lines))
        db_ids.append(db_id)

    return {"db_ids": db_ids, "cards": cards}


# ------------------------------
# Agent A: propose & auto_select
# (OpenAI embeddings)
# ------------------------------

@dataclass
class Candidate:
    db_id: str
    score: float

class AgentA:
    """
    Minimal Agent for DB selection:
      - Embeds DB cards once using OpenAI embeddings.
      - For a question, embeds the query and returns top-K DB candidates by cosine similarity.
      - auto_select() chooses the top-1 by similarity among provided candidates.
    """
    def __init__(self,
                 db_cards: List[str],
                 db_ids: List[str],
                 embedder: Optional[OpenAIBackend] = None):
        assert len(db_cards) == len(db_ids), "db_cards and db_ids must align"
        self.db_cards = db_cards
        self.db_ids = db_ids
        self.embedder = embedder or OpenAIBackend()

        # Precompute DB vectors
        self.X_db = self.embedder.encode(self.db_cards)

    def _topk_from_matrix(self, M: np.ndarray, q_vec: np.ndarray, k: int):
        # cosine == dot for L2-normalized vectors
        sims = (M @ q_vec.T).ravel()
        idx = np.argsort(-sims)[:k]
        return sims[idx], idx

    def propose(self, question: str, top: int = 3, pool: int = 20) -> Dict[str, Any]:
        q_vec = self.embedder.encode_one(question)
        sims_db, idx_db = self._topk_from_matrix(self.X_db, q_vec, k=min(pool, len(self.db_ids)))

        cands: List[Candidate] = []
        used = set()
        for score, idx in zip(sims_db, idx_db):
            db_id = self.db_ids[int(idx)]
            if db_id in used:
                continue
            cands.append(Candidate(db_id=db_id, score=float(score)))
            used.add(db_id)
            if len(cands) == top:
                break

        return {
            "query": question,
            "candidates": [c.__dict__ for c in cands],
            "instruction": "Reply with the db_id to use. If unsure, reply 'auto'."
        }

    def auto_select(self, question: str, candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Pick the best candidate purely by query→DB-card similarity.
        """
        if not candidates:
            raise ValueError("No candidates provided to auto_select().")
        q_vec = self.embedder.encode_one(question)

        # Build mask for candidate ids
        cand_ids = [c["db_id"] for c in candidates]
        id_to_idx = {db_id: i for i, db_id in enumerate(self.db_ids)}

        # Compute similarity only over candidate set
        sims = []
        for db_id in cand_ids:
            j = id_to_idx.get(db_id)
            if j is None:
                continue
            s = float((self.X_db[j:j+1] @ q_vec.T).ravel()[0])
            sims.append((db_id, s))

        if not sims:
            # Fallback: first provided candidate
            return {"selected_db_id": candidates[0]["db_id"], "reason": "fallback: first candidate (no sims)"}

        sims.sort(key=lambda x: -x[1])
        best_id, best_s = sims[0]
        return {"selected_db_id": best_id, "reason": f"highest DB-card similarity {best_s:.4f} among candidates"}
