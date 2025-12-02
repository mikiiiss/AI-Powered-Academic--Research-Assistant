# backend/ai_agents/citation_agent_fixed.py
import networkx as nx
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from core.database import SessionLocal
from api.models.database_models import Paper, PaperRelationship

class CitationAgent:
    def __init__(self):
        self.db = SessionLocal()
    
    def build_citation_network(self, query: str = None, max_nodes: int = 15) -> Dict[str, Any]:
        """Build a meaningful citation network"""
        print(f"🕸️ Building citation network for: {query or 'general AI'}")
        
        # Get relevant papers based on query
        if query:
            papers = self._get_relevant_papers(query, max_nodes)
        else:
            # Get some recent papers as fallback
            papers = self.db.query(Paper).order_by(Paper.published_date.desc()).limit(max_nodes).all()
        
        print(f"   Processing {len(papers)} papers for network...")
        
        if len(papers) < 3:
            # Return a simple demo network if not enough papers
            return self._create_demo_network()
        
        # Build network from database relationships
        nodes, links = self._build_network_from_relationships(papers)
        
        return {
            "nodes": nodes,
            "links": links,
            "metadata": {
                "total_papers": len(papers),
                "total_connections": len(links),
                "query": query,
                "network_type": "citation_similarity"
            }
        }
    
    def _get_relevant_papers(self, query: str, limit: int) -> List[Paper]:
        """Get papers relevant to query"""
        all_papers = self.db.query(Paper).all()
        
        scored_papers = []
        query_lower = query.lower()
        
        for paper in all_papers:
            # Simple relevance scoring
            score = 0
            if paper.title and query_lower in paper.title.lower():
                score += 2
            if paper.abstract and query_lower in paper.abstract.lower():
                score += 1
            if paper.venue and any(word in paper.venue.lower() for word in query_lower.split()):
                score += 1
            
            if score > 0:
                scored_papers.append((paper, score))
        
        # Sort by score and take top papers
        scored_papers.sort(key=lambda x: x[1], reverse=True)
        return [paper for paper, score in scored_papers[:limit]]
    
    def _build_network_from_relationships(self, papers: List[Paper]) -> tuple:
        """Build network from existing relationships"""
        paper_ids = [p.id for p in papers]
        
        # Get relationships between these papers
        relationships = self.db.query(PaperRelationship).filter(
            PaperRelationship.citing_paper_id.in_(paper_ids),
            PaperRelationship.cited_paper_id.in_(paper_ids)
        ).all()
        
        # Create nodes
        nodes = []
        for paper in papers:
            nodes.append({
                "id": paper.id,
                "label": self._shorten_title(paper.title),
                "title": paper.title,
                "year": paper.published_date.year if paper.published_date else 2024,
                "citations": paper.citation_count or 0,
                "group": self._categorize_paper(paper),
                "size": min((paper.citation_count or 0) / 10 + 5, 20)  # Size based on citations
            })
        
        # Create links from relationships
        links = []
        for rel in relationships:
            links.append({
                "source": rel.citing_paper_id,
                "target": rel.cited_paper_id,
                "strength": rel.similarity_score or 0.5,
                "type": rel.relationship_type or "related"
            })
        
        # If no relationships found, create some semantic connections
        if len(links) < 3:
            links.extend(self._create_semantic_connections(papers))
        
        return nodes, links
    
    def _create_semantic_connections(self, papers: List[Paper]) -> List[Dict]:
        """Create semantic connections between papers"""
        links = []
        
        for i, paper1 in enumerate(papers):
            for paper2 in papers[i+1:]:
                # Simple title similarity
                similarity = self._calculate_title_similarity(paper1.title, paper2.title)
                if similarity > 0.3:
                    links.append({
                        "source": paper1.id,
                        "target": paper2.id,
                        "strength": similarity,
                        "type": "semantic_similarity"
                    })
                # Limit connections for performance
                if len(links) >= 20:
                    break
        
        return links
    
    def _calculate_title_similarity(self, title1: str, title2: str) -> float:
        """Calculate simple title similarity"""
        if not title1 or not title2:
            return 0.0
        
        words1 = set(title1.lower().split())
        words2 = set(title2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _create_demo_network(self) -> Dict[str, Any]:
        """Create a demo network when not enough data"""
        return {
            "nodes": [
                {
                    "id": "demo_1",
                    "label": "Deep Learning",
                    "title": "Deep Learning Research",
                    "year": 2024,
                    "citations": 150,
                    "group": "deep_learning",
                    "size": 15
                },
                {
                    "id": "demo_2", 
                    "label": "Neural Networks",
                    "title": "Neural Networks Advances",
                    "year": 2024,
                    "citations": 120,
                    "group": "neural_networks",
                    "size": 12
                },
                {
                    "id": "demo_3",
                    "label": "Transformers",
                    "title": "Transformer Models",
                    "year": 2024,
                    "citations": 200,
                    "group": "transformers", 
                    "size": 20
                }
            ],
            "links": [
                {"source": "demo_1", "target": "demo_2", "strength": 0.8, "type": "related"},
                {"source": "demo_2", "target": "demo_3", "strength": 0.6, "type": "cites"},
                {"source": "demo_1", "target": "demo_3", "strength": 0.7, "type": "semantic"}
            ],
            "metadata": {
                "total_papers": 3,
                "total_connections": 3,
                "query": "demo",
                "network_type": "demo_network"
            }
        }
    
    def _shorten_title(self, title: str) -> str:
        """Shorten title for display"""
        if len(title) <= 25:
            return title
        return title[:22] + "..."
    
    def _categorize_paper(self, paper: Paper) -> str:
        """Categorize paper based on content"""
        title_lower = paper.title.lower()
        
        if any(word in title_lower for word in ['deep learning', 'neural network', 'cnn', 'rnn']):
            return 'deep_learning'
        elif any(word in title_lower for word in ['transformer', 'attention', 'llm', 'gpt']):
            return 'transformers'
        elif any(word in title_lower for word in ['computer vision', 'image', 'vision']):
            return 'computer_vision'
        elif any(word in title_lower for word in ['nlp', 'language', 'text']):
            return 'nlp'
        elif any(word in title_lower for word in ['reinforcement', 'rl']):
            return 'reinforcement_learning'
        else:
            return 'machine_learning'
    
    def close(self):
        """Close database connection"""
        self.db.close()