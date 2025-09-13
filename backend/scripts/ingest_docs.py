# scripts/ingest_docs.py
"""
Quick ingestion runner. Run: python -m scripts.ingest_docs
"""
from app.services.ingestion import run_ingest
from app.utils.logger import logger

if __name__ == "__main__":
    logger.info("Starting document ingestion...")
    run_ingest()
    logger.info("Ingestion complete.")
