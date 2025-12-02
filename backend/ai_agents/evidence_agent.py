# backend/ai_agents/evidence_agent.py
import numpy as np
import asyncio
import hashlib
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from core.database import SessionLocal
from api.models.database_models import Paper
from knowledge_graph.graph_builder import KnowledgeGraphBuilder
from core.cache import cache_manager

from .grok_client import GrokClient

class EvidenceAgent:
    def __init__(self):
        self.kg_builder = KnowledgeGraphBuilder()
        self.db = SessionLocal()
        self.grok = GrokClient()  # Changed from DeepSeekClient
        self.cache = cache_manager



    
    async def find_evidence(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Find supporting evidence for research claims (async with parallel processing + caching)"""
        print(f"🔍 Finding evidence for: {query}")
        
        # Check cache first
        cache_key = f"evidence:{hashlib.md5(f'{query}:{limit}'.encode()).hexdigest()}"
        cached_result = self.cache.get_cached(cache_key)
        if cached_result:
            return cached_result
        
        # Step 1: Semantic search using embeddings (async DB query)
        similar_papers = await self._semantic_search(query, limit)
        print(f"   Found {len(similar_papers)} relevant papers")
        
        # Step 2: Extract relevant quotes using Grok - PARALLEL PROCESSING
        print(f"   Processing {len(similar_papers)} papers in parallel...")
        
        # Create tasks for parallel processing
        tasks = [
            self._process_paper_for_evidence(paper, query) 
            for paper in similar_papers
        ]
        
        # Execute all tasks concurrently
        evidence_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out None values and exceptions
        evidence_spans = []
        for i, result in enumerate(evidence_results):
            if isinstance(result, Exception):
                print(f"   ⚠️ Error processing paper {i+1}: {result}")
            elif result is not None:
                evidence_spans.append(result)
        
        print(f"   Successfully processed {len(evidence_spans)} papers")
        
        # Step 3: Sort by relevance
        evidence_spans.sort(key=lambda x: x["relevance"], reverse=True)
        final_result = evidence_spans[:limit]
        
        # Cache the result for 1 hour
        self.cache.set_cached(cache_key, final_result, ttl=3600)
        
        return final_result
    
    async def _semantic_search(self, query: str, limit: int) -> List[Paper]:
        """Find semantically similar papers using vector embeddings"""
        from ml_pipeline.embedding_service import EmbeddingService
        from core.vector_search import vector_similarity_search
        
        # Use fresh DB session to avoid transaction issues
        db = SessionLocal()
        try:
            # Generate query embedding
            embedding_service = EmbeddingService()
            try:
                # Load model and encode asynchronously
                # No need for new event loop since we are already in one
                query_embedding = await embedding_service.encode_single(query)
            except Exception as e:
                print(f"   ⚠️ Embedding generation failed: {e}, falling back to keyword search")
                return self._keyword_search_fallback(query, limit, db)
            
            # Vector similarity search with fresh DB session
            results = vector_similarity_search(db, query_embedding.tolist(), limit=limit)
            
            # If no results, fallback
            if not results:
                print("   No vector results, trying fallback...")
                return self._keyword_search_fallback(query, limit, db)
                
            # Extract papers from (paper, score) tuples
            papers = [paper for paper, score in results]
            print(f"   ✅ Vector search: found {len(papers)} papers (scores: {[f'{s:.2f}' for _, s in results[:3]]})")
            return papers
        except Exception as e:
            print(f"   ❌ Semantic search error: {e}")
            db.rollback()  # Important: rollback on error
            return self._keyword_search_fallback(query, limit, db)
        finally:
            db.close()  # Always close the session
    
    def _keyword_search_fallback(self, query: str, limit: int, db: Session) -> List[Paper]:
        """Fallback to keyword search if vector search fails"""
        print(f"   🔍 Using keyword search fallback")
        all_papers = db.query(Paper).all()  # Use passed db session
        query_lower = query.lower()
        
        scored_papers = []
        for paper in all_papers:
            score = self._calculate_similarity_score(paper, query_lower)
            if score > 0.1:
                scored_papers.append((paper, score))
        
        scored_papers.sort(key=lambda x: x[1], reverse=True)
        return [paper for paper, score in scored_papers[:limit]]
    
    def _calculate_similarity_score(self, paper: Paper, query: str) -> float:
        """Calculate similarity score between paper and query"""
        # Simple keyword matching for now - we'll enhance this
        title_score = self._text_similarity(paper.title.lower(), query)
        
        # Use abstract if available
        abstract_score = 0
        if paper.abstract:
            abstract_score = self._text_similarity(paper.abstract.lower(), query)
        
        return max(title_score, abstract_score)
    
    def _text_similarity(self, text: str, query: str) -> float:
        """Simple text similarity using keyword matching"""
        query_words = set(query.split())
        text_words = set(text.split())
        
        if not query_words:
            return 0
            
        intersection = query_words.intersection(text_words)
        return len(intersection) / len(query_words)
    
    async def _process_paper_for_evidence(self, paper: Paper, query: str) -> Dict[str, Any]:
        """Process a single paper to extract evidence (async)"""
        # Extract relevant quotes using Grok API (async)
        paper_content = f"Title: {paper.title}\nAbstract: {paper.abstract}"
        quotes = await self.grok.extract_quotes(paper_content, query)
        
        if not quotes:
            return None
        
        # Calculate relevance score
        relevance = self._calculate_relevance_score(paper, query, quotes)
        
        return {
            "id": f"e_{paper.id}",
            "sourceTitle": paper.title,
            "venue": paper.venue or "Unknown",
            "year": paper.published_date.year if paper.published_date else 2024,
            "citations": paper.citation_count or 0,
            "relevance": min(int(relevance * 100), 100),  # Convert to percentage
            "quote": quotes[0] if quotes else "No relevant quote found",
            "paper_id": paper.id
        }
    
    def _calculate_relevance_score(self, paper: Paper, query: str, quotes: List[str]) -> float:
        """Calculate overall relevance score"""
        # Combine semantic similarity and quote relevance
        semantic_score = self._calculate_similarity_score(paper, query)
        
        # Quote relevance (simple length-based heuristic for now)
        quote_score = min(len(quotes[0]) / 500, 1.0) if quotes else 0
        
        # Citation impact (normalize citation count)
        citation_score = min((paper.citation_count or 0) / 100, 1.0)
        
        # Weighted combination
        return (0.5 * semantic_score + 0.3 * quote_score + 0.2 * citation_score)
    
    def close(self):
        """Close database connection"""
        self.db.close()