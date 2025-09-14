# app/services/ingestion.py
"""
Document ingestion:
- Reads files from data/docs/
- Splits into simple chunks
- Embeds using OpenAI embeddings
- Stores vectors in FAISS and metadata in .meta.json
"""

import os
import json
from pathlib import Path
from typing import List
import numpy as np
import faiss
from PyPDF2 import PdfReader
from app.utils.config import settings
from sentence_transformers import SentenceTransformer
from app.utils.logger import logger

DATA_DOCS = Path(__file__).resolve().parents[2] / "data" / "docs"
EMBED_DIR = Path(__file__).resolve().parents[2] / "data" / "embeddings"
EMBED_DIR.mkdir(parents=True, exist_ok=True)

def extract_text_from_pdf(path: Path) -> str:
    try:
        reader = PdfReader(str(path))
        text = []
        for p in reader.pages:
            text.append(p.extract_text() or "")
        return "\n".join(text)
    except Exception:
        return ""

def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> List[str]:
    tokens = text.split()
    chunks = []
    i = 0
    while i < len(tokens):
        chunk = tokens[i:i+chunk_size]
        chunks.append(" ".join(chunk))
        i += chunk_size - overlap
    return chunks

# Initialize the embedding model (singleton pattern)
_embedding_model = None

def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
        _embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
    return _embedding_model

def get_embedding(text: str):
    model = get_embedding_model()
    embedding = model.encode([text])[0]
    return np.array(embedding, dtype="float32")

def load_or_create_index(index_path: str, meta_path: str):
    meta_path_p = Path(meta_path)
    index_path_p = Path(index_path)
    # If index exists -> load
    if index_path_p.exists() and meta_path_p.exists():
        index = faiss.read_index(str(index_path_p))
        with open(meta_path_p, "r", encoding="utf-8") as f:
            metadatas = json.load(f)
        return index, metadatas

    # Create index from data/docs
    texts = []
    metadatas = []
    for file in DATA_DOCS.glob("*"):
        text = ""
        if file.suffix.lower() == ".pdf":
            text = extract_text_from_pdf(file)
        else:
            text = file.read_text(encoding="utf-8")
        if not text.strip():
            continue
        chunks = chunk_text(text)
        for i, c in enumerate(chunks):
            texts.append(c)
            metadatas.append({"source": str(file.name), "title": f"{file.name} - chunk {i}", "text": c})

    if not texts:
        # empty index - use default embedding dimension
        model = get_embedding_model()
        dim = model.get_sentence_embedding_dimension()
        index = faiss.IndexFlatL2(dim)
        faiss.write_index(index, str(index_path_p))
        with open(meta_path_p, "w", encoding="utf-8") as f:
            json.dump([], f)
        return index, []

    embeddings = [get_embedding(t) for t in texts]
    mat = np.vstack(embeddings).astype("float32")
    dim = mat.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(mat)
    faiss.write_index(index, str(index_path_p))
    with open(meta_path_p, "w", encoding="utf-8") as f:
        json.dump(metadatas, f, ensure_ascii=False)
    return index, metadatas

# Expose a helper function to run a fresh ingestion from scripts/ingest_docs.py
def run_ingest():
    index_file = str(EMBED_DIR / "faiss.index")
    meta_file = str(EMBED_DIR / "faiss.meta.json")
    load_or_create_index(index_file, meta_file)
