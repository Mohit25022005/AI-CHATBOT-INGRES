# app/services/rag_pipeline.py
"""
Simple RAG pipeline:
- Uses OpenAI embeddings to embed documents and queries
- Stores vectors in FAISS (local on-disk optional)
- On query: retrieve top-k docs, build context, call OpenAI chat completion with context
"""

import os
import json
import numpy as np
import faiss
from typing import List, Tuple
from pathlib import Path
from app.utils.config import settings
import openai
from app.services.ingestion import load_or_create_index

openai.api_key = settings.OPENAI_API_KEY

class RAGPipeline:
    def __init__(self, index_path: str = None):
        self.index_path = index_path or str(Path(__file__).resolve().parents[2] / "data" / "embeddings" / "faiss.index")
        self.meta_path = str(Path(self.index_path).with_suffix(".meta.json"))
        self.index, self.metadatas = load_or_create_index(self.index_path, self.meta_path)
        self.dim = self.index.d if hasattr(self.index, "d") else 1536

    def _embed_text(self, text: str) -> List[float]:
        # Uses OpenAI embedding API - adapt model name if needed
        res = openai.Embedding.create(model="text-embedding-3-small", input=text)
        return res["data"][0]["embedding"]

    def _search(self, query: str, top_k: int = 4):
        vec = np.array(self._embed_text(query), dtype="float32").reshape(1, -1)
        D, I = self.index.search(vec, top_k)
        results = []
        for idx in I[0]:
            if idx < 0 or idx >= len(self.metadatas):
                continue
            results.append(self.metadatas[int(idx)])
        return results

    def generate_response(self, query: str, session_id: str = None) -> Tuple[str, List[dict]]:
        # 1) retrieve
        docs = self._search(query, top_k=4)
        # 2) build context
        context_texts = []
        for d in docs:
            context_texts.append(f"Title: {d.get('title','-')}\n{d.get('text','')[:1000]}")
        context_block = "\n\n---\n\n".join(context_texts) if context_texts else "No relevant doc found."

        # 3) call LLM
        system_prompt = (
            "You are an AI support assistant for INGRES. Use the provided context from product docs to answer precisely. "
            "If the answer is uncertain, say so and propose troubleshooting steps. If the user needs escalation, advise creating a ticket."
        )
        user_prompt = f"User question: {query}\n\nContext:\n{context_block}\n\nAnswer concisely, reference context titles when applicable."
        chat_messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        resp = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # change to available model
            messages=chat_messages,
            max_tokens=700,
            temperature=0.2
        )
        reply = resp["choices"][0]["message"]["content"].strip()
        return reply, docs
