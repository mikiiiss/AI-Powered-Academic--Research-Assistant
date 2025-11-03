import numpy as np
from typing import List, Union
import asyncio

class EmbeddingService:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
    
    async def load_model(self):
        """Lazy load the model to save memory"""
        if self.model is None:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
        return self.model
    
    async def encode_single(self, text: str) -> np.ndarray:
        """Encode single text to embedding"""
        if not text or not text.strip():
            return np.zeros(384)  # Default dimension
        
        model = await self.load_model()
        embedding = model.encode([text])[0]
        return embedding
    
    async def encode_batch(self, texts: List[str]) -> np.ndarray:
        """Encode multiple texts to embeddings"""
        valid_texts = [text for text in texts if text and text.strip()]
        if not valid_texts:
            return np.array([])
        
        model = await self.load_model()
        embeddings = model.encode(valid_texts)
        return embeddings