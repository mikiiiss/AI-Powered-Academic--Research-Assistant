

# backend/ai_agents/evidence_agent.py
import numpy as np
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from core.database import SessionLocal
from api.models.database_models import Paper
from knowledge_graph.graph_builder import KnowledgeGraphBuilder

from .grok_client import GrokClient  # Changed from DeepSeekClient

class EvidenceAgent:
    def __init__(self):
        self.kg_builder = KnowledgeGraphBuilder()
        self.db = SessionLocal()
        self.grok = GrokClient()  # Changed from DeepSeekClient



    
    def find_evidence(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Find supporting evidence for research claims"""
        print(f"🔍 Finding evidence for: {query}")
        
        # Step 1: Semantic search using embeddings
        similar_papers = self._semantic_search(query, limit)
        print(f"   Found {len(similar_papers)} relevant papers")
        
        # Step 2: Extract relevant quotes using DeepSeek
        evidence_spans = []
        for paper in similar_papers:
            evidence = self._process_paper_for_evidence(paper, query)
            if evidence:
                evidence_spans.append(evidence)
        
        # Step 3: Sort by relevance
        evidence_spans.sort(key=lambda x: x["relevance"], reverse=True)
        
        return evidence_spans[:limit]
    
    def _semantic_search(self, query: str, limit: int) -> List[Paper]:
        """Find semantically similar papers using embeddings"""
        # For now, we'll use a simple approach - later we can use vector DB
        all_papers = self.db.query(Paper).all()
        
        # Calculate query embedding (you might want to generate this properly)
        # For now, we'll use title similarity as placeholder
        query_lower = query.lower()
        
        scored_papers = []
        for paper in all_papers:
            score = self._calculate_similarity_score(paper, query_lower)
            if score > 0.1:  # Threshold
                scored_papers.append((paper, score))
        
        # Sort by similarity score
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
    
    def _process_paper_for_evidence(self, paper: Paper, query: str) -> Dict[str, Any]:
        """Process a single paper to extract evidence"""
        # Extract relevant quotes using DeepSeek
        paper_content = f"Title: {paper.title}\nAbstract: {paper.abstract}"
        quotes = self.grok.extract_quotes(paper_content, query)  # Fixed: changed self.deepseek to self.grok
        
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