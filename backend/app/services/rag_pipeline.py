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
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from sentence_transformers import SentenceTransformer
from app.services.ingestion import load_or_create_index, get_embedding_model
from app.utils.logger import logger
import torch

class RAGPipeline:
    def __init__(self, index_path: str = None):
        self.index_path = index_path or str(Path(__file__).resolve().parents[2] / "data" / "embeddings" / "faiss.index")
        self.meta_path = str(Path(self.index_path).with_suffix(".meta.json"))
        self.index, self.metadatas = load_or_create_index(self.index_path, self.meta_path)
        
        # Initialize embedding model
        self.embedding_model = get_embedding_model()
        self.dim = self.index.d if hasattr(self.index, "d") else self.embedding_model.get_sentence_embedding_dimension()
        
        # Initialize LLM (lazy loading)
        self._llm_pipeline = None
        
    def _get_llm_pipeline(self):
        """Lazy load the LLM pipeline to save memory"""
        if self._llm_pipeline is None:
            logger.info(f"Loading LLM model: {settings.LLM_MODEL}")
            # Use a smaller model for faster inference
            model_name = "microsoft/DialoGPT-medium"  # Smaller than Falcon-7B for better performance
            
            self._llm_pipeline = pipeline(
                "text-generation",
                model=model_name,
                tokenizer=model_name,
                max_length=512,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                device=0 if torch.cuda.is_available() else -1  # Use GPU if available
            )
        return self._llm_pipeline

    def _embed_text(self, text: str) -> List[float]:
        # Uses SentenceTransformer for local embeddings
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
        # 1) retrieve
        docs = self._search(query, top_k=4)
        # 2) build context
        context_texts = []
        for d in docs:
            context_texts.append(f"Title: {d.get('title','-')}\n{d.get('text','')[:1000]}")
        context_block = "\n\n---\n\n".join(context_texts) if context_texts else "No relevant doc found."

        # 3) call local LLM
        system_prompt = (
            "You are an AI support assistant for INGRES. Use the provided context from product docs to answer precisely. "
            "If the answer is uncertain, say so and propose troubleshooting steps. If the user needs escalation, advise creating a ticket."
        )
        
        # Create a comprehensive prompt for the local LLM
        full_prompt = f"{system_prompt}\n\nContext from documentation:\n{context_block}\n\nUser question: {query}\n\nAnswer:"
        
        try:
            # Use local LLM for generation
            llm = self._get_llm_pipeline()
            
            # Generate response
            response = llm(
                full_prompt,
                max_new_tokens=300,
                num_return_sequences=1,
                pad_token_id=llm.tokenizer.eos_token_id
            )
            
            # Extract generated text (remove the input prompt)
            generated_text = response[0]['generated_text']
            reply = generated_text[len(full_prompt):].strip()
            
            # Fallback if generation fails
            if not reply:
                reply = self._generate_fallback_response(query, docs)
                
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            reply = self._generate_fallback_response(query, docs)
        
        return reply, docs
    
    def _generate_fallback_response(self, query: str, docs: List[dict]) -> str:
        """Generate a fallback response using template-based approach"""
        if not docs:
            return (
                "I don't have specific documentation to answer your question about INGRES. "
                "However, I can help you troubleshoot common issues. You can also create a support ticket if you need further assistance."
            )
        
        # Create a comprehensive template-based response
        response = "Based on the INGRES documentation, here's what I found:\n\n"
        
        for i, doc in enumerate(docs[:3], 1):  # Show top 3 results instead of 2
            title = doc.get('title', 'Documentation')
            text = doc.get('text', '')
            
            # Show more text but keep it readable
            if len(text) > 500:
                display_text = text[:500] + "..."
            else:
                display_text = text
                
            response += f"**{i}. {title}**\n{display_text}\n\n"
        
        # Add helpful guidance based on query type
        query_lower = query.lower()
        if any(word in query_lower for word in ['connection', 'connect', 'timeout']):
            response += "**Connection Help:** Check your network settings, verify the default port (21064), and ensure the database server is running.\n\n"
        elif any(word in query_lower for word in ['error', 'issue', 'problem']):
            response += "**Error Help:** If you're experiencing specific errors, please share the error code or message for more targeted assistance.\n\n"
        elif any(word in query_lower for word in ['performance', 'slow', 'optimization']):
            response += "**Performance Help:** Consider reviewing your indexing strategy, query plans, and system resources.\n\n"
            
        response += "💡 **Need more help?** Try asking more specific questions or type 'create support ticket' to get personalized assistance."
        return response
