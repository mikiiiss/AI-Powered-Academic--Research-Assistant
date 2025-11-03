#!/usr/bin/env python3
"""
Semantic search engine using the embeddings we just generated
"""

import numpy as np
from typing import List, Dict
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sentence_transformers import SentenceTransformer
from core.database import SessionLocal
from api.models.database_models import Paper

class SemanticSearch:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.dimension = 384
    
    async def search_similar_papers(self, query: str, top_k: int = 10) -> List[Dict]:
        """Find papers semantically similar to the query"""
        print(f"🔍 Semantic search: '{query}'")
        
        # Encode the query
        query_embedding = await self._encode_query(query)
        
        db = SessionLocal()
        try:
            # Get all papers with embeddings
            papers = db.query(Paper).filter(Paper.title_embedding != None).all()
            
            if not papers:
                return []
            
            # Calculate similarities
            similarities = []
            for paper in papers:
                if paper.title_embedding:
                    similarity = self._cosine_similarity(query_embedding, paper.title_embedding)
                    similarities.append({
                        'paper': paper,
                        'similarity': similarity
                    })
            
            # Sort by similarity and return top results
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            
            results = []
            for item in similarities[:top_k]:
                paper = item['paper']
                results.append({
                    'id': paper.id,
                    'title': paper.title,
                    'abstract': paper.abstract[:200] + '...' if paper.abstract and len(paper.abstract) > 200 else paper.abstract,
                    'similarity_score': round(item['similarity'], 3),
                    'venue': paper.venue,
                    'year': paper.published_date.year if paper.published_date else None
                })
            
            return results
            
        finally:
            db.close()
    
    async def _encode_query(self, query: str) -> List[float]:
        """Encode search query to embedding"""
        embedding = self.model.encode([query])[0]
        return embedding.tolist()
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        if isinstance(vec2, list):
            vec2 = np.array(vec2)
        elif not isinstance(vec2, np.ndarray):
            vec2 = np.array(vec2)
            
        vec1 = np.array(vec1)
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

# Test the semantic search
async def test_semantic_search():
    print("🧪 Testing semantic search...")
    
    search_engine = SemanticSearch()
    
    # Test queries
    test_queries = [
        "machine learning healthcare",
        "neural networks computer vision", 
        "reinforcement learning robotics",
        "natural language processing"
    ]
    
    for query in test_queries:
        print(f"\n📝 Query: '{query}'")
        results = await search_engine.search_similar_papers(query, top_k=3)
        
        for i, result in enumerate(results):
            print(f"   {i+1}. {result['title'][:60]}...")
            print(f"      Similarity: {result['similarity_score']}")
            print(f"      Venue: {result['venue']}")

if __name__ == "__main__":
    asyncio.run(test_semantic_search())