# backend/ai_agents/citation_agent_optimized.py
import networkx as nx
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from collections import defaultdict
from core.database import SessionLocal
from api.models.database_models import Paper, PaperRelationship
from knowledge_graph.graph_builder import KnowledgeGraphBuilder

class CitationAgent:
    def __init__(self):
        self.kg_builder = KnowledgeGraphBuilder()
        self.db = SessionLocal()
    
    def build_citation_network(self, 
                             paper_ids: List[str] = None,
                             query: str = None,
                             max_nodes: int = 15) -> Dict[str, Any]:
        """FAST citation network building"""
        print(f"🕸️ Building citation network for {len(paper_ids) if paper_ids else 'query'}: {query or 'general'}")
        
        # Get relevant papers - LIMITED for performance
        if paper_ids:
            papers = self.db.query(Paper).filter(Paper.id.in_(paper_ids[:max_nodes])).all()
        elif query:
            papers = self._get_relevant_papers_fast(query, limit=max_nodes)
        else:
            # Get a small sample for performance
            papers = self.db.query(Paper).limit(max_nodes).all()
        
        print(f"   Processing {len(papers)} papers...")
        
        # FAST network building
        nodes, links = self._build_network_data_fast(papers, max_nodes)
        
        return {
            "nodes": nodes,
            "links": links,
            "metadata": {
                "total_papers": len(papers),
                "total_connections": len(links),
                "network_density": len(links) / (len(nodes) * (len(nodes) - 1)) if len(nodes) > 1 else 0,
            }
        }
    
    def _get_relevant_papers_fast(self, query: str, limit: int = 15) -> List[Paper]:
        """FAST paper relevance search"""
        all_papers = self.db.query(Paper).limit(100).all()  # Limit initial search
        
        scored_papers = []
        query_lower = query.lower()
        
        for paper in all_papers:
            # Simple keyword matching - no complex processing
            paper_text = f"{paper.title}".lower()  # Only check title for speed
            if any(word in paper_text for word in query_lower.split()):
                scored_papers.append(paper)
                if len(scored_papers) >= limit:
                    break
        
        return scored_papers[:limit]
    
    def _build_network_data_fast(self, papers: List[Paper], max_nodes: int) -> Tuple[List[Dict], List[Dict]]:
        """FAST network data building"""
        nodes = []
        links = []
        
        paper_ids = [p.id for p in papers]
        
        # Create nodes - SIMPLIFIED
        for paper in papers:
            nodes.append({
                "id": paper.id,
                "label": self._shorten_title_fast(paper.title),
                "year": paper.published_date.year if paper.published_date else 2024,
                "citations": paper.citation_count or 0,
                "group": self._categorize_paper_fast(paper),
                "title": paper.title,
            })
        
        # Get relationships - LIMITED for performance
        relationships = self.db.query(PaperRelationship).filter(
            PaperRelationship.citing_paper_id.in_(paper_ids)
        ).limit(50).all()  # LIMIT relationships for speed
        
        # Create links - SIMPLIFIED
        link_count = 0
        for rel in relationships:
            if rel.cited_paper_id in paper_ids and link_count < 30:  # Limit links
                links.append({
                    "source": rel.citing_paper_id,
                    "target": rel.cited_paper_id,
                    "strength": 0.7,
                    "type": rel.relationship_type,
                })
                link_count += 1
        
        return nodes, links
    
    def _categorize_paper_fast(self, paper: Paper) -> str:
        """FAST paper categorization"""
        title_lower = paper.title.lower()
        
        if "quaternion" in title_lower:
            return "quaternion_ai"
        elif "spiking" in title_lower or "snn" in title_lower:
            return "spiking_nn" 
        elif "legal" in title_lower or "law" in title_lower:
            return "legal_ai"
        elif "audio" in title_lower or "sound" in title_lower:
            return "audio_ai"
        elif "transformer" in title_lower or "attention" in title_lower:
            return "transformers"
        elif "drone" in title_lower or "routing" in title_lower:
            return "optimization"
        else:
            return "general_ai"
    
    def _shorten_title_fast(self, title: str) -> str:
        """FAST title shortening"""
        if len(title) <= 25:
            return title
        return title[:22] + "..."
    
    def get_paper_citation_impact_fast(self, paper_id: str) -> Dict[str, Any]:
        """FAST paper impact analysis"""
        paper = self.db.query(Paper).filter(Paper.id == paper_id).first()
        if not paper:
            return {}
        
        # SIMPLIFIED impact calculation
        return {
            "paper_id": paper_id,
            "title": paper.title,
            "total_citations": paper.citation_count or 0,
            "year": paper.published_date.year if paper.published_date else 2024,
            "impact_score": min((paper.citation_count or 0) / 10, 1.0)
        }
    
    def close(self):
        """Close database connection"""
        self.db.close()