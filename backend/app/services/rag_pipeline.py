"""
Optimized RAG pipeline for RTX 4060 (8GB VRAM) and CPU fallback:
- Embeds docs/queries with SentenceTransformers
- Stores/retrieves vectors in FAISS
- GPU: uses Falcon-7B-Instruct in 4-bit (fast on GPU)
- CPU: uses google/flan-t5-small (very fast and light)
"""

import json
import numpy as np
from typing import List, Tuple
from pathlib import Path
from app.utils.config import settings
from sentence_transformers import SentenceTransformer
from app.services.ingestion import load_or_create_index, get_embedding_model
from app.utils.logger import logger
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    AutoModelForSeq2SeqLM,
    BitsAndBytesConfig,
    pipeline,
)

def build_prompt(user_query: str, retrieved_chunks: List[str]) -> str:
    """Build concise prompt from retrieved chunks"""
    context = "\n\n".join(retrieved_chunks)
    return f"""
You are an expert on INGRES database.

Answer the following user question based only on the provided documentation.

User Question:
{user_query}

Relevant Documentation:
{context}

Answer clearly, concisely, and precisely.
If the answer is not in the documentation, say "I don’t know based on the INGRES docs."
"""

class RAGPipeline:
    def __init__(self, index_path: str = None):
        self.index_path = index_path or str(
            Path(__file__).resolve().parents[2] / "data" / "embeddings" / "faiss.index"
        )
        self.meta_path = str(Path(self.index_path).with_suffix(".meta.json"))
        self.index, self.metadatas = load_or_create_index(self.index_path, self.meta_path)

        self.embedding_model = get_embedding_model()
        self._llm_pipeline = None

    def _get_llm_pipeline(self):
        """Lazy load — auto GPU/CPU detection"""
        if self._llm_pipeline is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Detected device: {device.upper()}")

            if device == "cuda":
                # ✅ GPU path (Falcon-7B in 4-bit)
                model_name = settings.LLM_MODEL or "tiiuae/falcon-7b-instruct"
                tokenizer = AutoTokenizer.from_pretrained(model_name)
                bnb_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4"
                )
                model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    device_map="auto",
                    quantization_config=bnb_config
                )
                self._llm_pipeline = pipeline(
                    "text-generation",
                    model=model,
                    tokenizer=tokenizer,
                    max_length=1024,
                    temperature=0.2,
                    top_p=0.9,
                    do_sample=True,
                    device=0
                )

            else:
                # ✅ CPU path (super-light FLAN-T5)
                model_name = "google/flan-t5-small"
                tokenizer = AutoTokenizer.from_pretrained(model_name)
                model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
                self._llm_pipeline = pipeline(
                    "text2text-generation",
                    model=model,
                    tokenizer=tokenizer,
                    max_length=512,
                    temperature=0.3,
                    top_p=0.9,
                    device=-1
                )

            logger.info(f"Loaded model: {model_name}")

        return self._llm_pipeline

    def _embed_text(self, text: str) -> List[float]:
        embedding = self.embedding_model.encode([text])[0]
        return embedding.tolist()

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
        docs = self._search(query, top_k=4)
        retrieved_chunks = [d.get("text", "") for d in docs]
        full_prompt = build_prompt(query, retrieved_chunks)

        try:
            llm = self._get_llm_pipeline()
            response = llm(
                full_prompt,
                max_new_tokens=256,
                num_return_sequences=1,
            )

            if isinstance(response[0], dict):
                generated_text = response[0].get("generated_text") or response[0].get("generated_text", "")
            else:
                generated_text = str(response[0])

            reply = generated_text[len(full_prompt):].strip() if "generated_text" in response[0] else generated_text

            if not reply:
                reply = self._fallback_response(docs)

        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            reply = self._fallback_response(docs)

        return reply, docs

    def _fallback_response(self, docs: List[dict]) -> str:
        if not docs:
            return "I don’t know based on the INGRES docs. Please refine your question."
        snippets = [
            d.get("text", "")[:400] + "..." if len(d.get("text", "")) > 400 else d.get("text", "")
            for d in docs[:3]
        ]
        return "Here’s what the INGRES documentation says:\n\n" + "\n\n".join(snippets)
