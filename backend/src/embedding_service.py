"""
Embedding Service — NEW in Phase 2.
 
This service converts text to vectors using OpenAI's embedding API.
Think of it as a companion to llm_service.py:
- llm_service.py: text in → text out (generation)
- embedding_service.py: text in → numbers out (embedding)
 
CRITICAL RULE: Always use the same model for documents AND queries.
Mixing models is like mixing GPS coordinate systems — results are garbage.
"""
from openai import OpenAI
from src.config import settings
import logging
 
logger = logging.getLogger(__name__)
 
class EmbeddingService:
    """Wrapper around the OpenAI Embeddings API."""
 
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.embedding_model  # text-embedding-3-small
 
    def embed_text(self, text: str) -> list[float]:
        """
        Convert a single piece of text to a vector.
        Use this for: embedding a user's question at query time.
        """
        response = self.client.embeddings.create(
            input=text,
            model=self.model
        )
        return response.data[0].embedding
 
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """
        Convert many texts to vectors in ONE API call.
        ALWAYS use this when processing document chunks — never call
        embed_text() in a loop. Batch processing is 10-50x faster.
        
        Use this for: embedding all chunks when a document is uploaded.
        """
        if not texts:
            return []
        
        # OpenAI accepts up to 2048 texts in one call.
        # For very large documents, split into batches of 100.
        BATCH_SIZE = 100
        all_embeddings = []
        
        for i in range(0, len(texts), BATCH_SIZE):
            batch = texts[i:i + BATCH_SIZE]
            logger.info(f"Embedding batch {i//BATCH_SIZE + 1}: {len(batch)} texts")
            response = self.client.embeddings.create(
                input=batch,
                model=self.model
            )
            all_embeddings.extend([d.embedding for d in response.data])
        
        return all_embeddings
 
embedding_service = EmbeddingService()
