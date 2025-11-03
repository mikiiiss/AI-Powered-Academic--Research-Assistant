import networkx as nx
from typing import List, Dict, Tuple
from collections import Counter
import numpy as np
from sqlalchemy.orm import Session
from core.database import SessionLocal
from api.models.database_models import Paper, PaperRelationship

class KnowledgeGraphBuilder:
    def __init__(self):
        self.graph = nx.Graph()
        self.db = SessionLocal()
    
    def build_complete_knowledge_graph(self) -> nx.Graph:
        """Build and persist complete knowledge graph"""
        print("🕸️ Building comprehensive knowledge graph...")
        
        # Get all papers
        papers = self.db.query(Paper).all()
        print(f"📄 Processing {len(papers)} papers...")
        
        # Build in-memory graph
        self._build_semantic_relationships(papers)
        self._build_venue_relationships(papers)
        
        # Persist relationships to database
        self._persist_relationships_to_db()
        
        # Analyze graph
        analysis = self.analyze_relationships()
        
        print(f"🎉 Knowledge graph complete!")
        print(f"   - Papers: {len(papers)}")
        print(f"   - Relationships: {len(self.graph.edges)}")
        print(f"   - Clusters: {analysis.get('clusters', 0)}")
        
        return self.graph
    
    def _build_semantic_relationships(self, papers: List[Paper]):
        """Build relationships based on semantic similarity"""
        print("   🔤 Building semantic relationships...")
        
        # For each paper, find semantically similar papers
        for i, paper1 in enumerate(papers):
            if i % 50 == 0:
                print(f"      Processing paper {i+1}/{len(papers)}...")
            
            if not paper1.title_embedding:
                continue
                
            for paper2 in papers[i+1:]:
                if not paper2.title_embedding:
                    continue
                
                # Calculate similarity
                similarity = self._cosine_similarity(
                    paper1.title_embedding, 
                    paper2.title_embedding
                )
                
                # Add relationship if similar enough
                if similarity > 0.3:  # Threshold for similarity
                    self.graph.add_edge(
                        paper1.id, paper2.id,
                        type="semantic_similarity",
                        weight=similarity,
                        label=f"Similarity: {similarity:.2f}"
                    )
    
    def _build_venue_relationships(self, papers: List[Paper]):
        """Build relationships based on venues"""
        print("   🏛️ Building venue relationships...")
        
        venue_groups = {}
        for paper in papers:
            if paper.venue:
                if paper.venue not in venue_groups:
                    venue_groups[paper.venue] = []
                venue_groups[paper.venue].append(paper.id)
        
        # Connect papers from same venue
        for venue, paper_ids in venue_groups.items():
            if len(paper_ids) > 1:
                for i in range(len(paper_ids)):
                    for j in range(i + 1, len(paper_ids)):
                        self.graph.add_edge(
                            paper_ids[i], paper_ids[j], 
                            type="same_venue", 
                            weight=0.7,
                            label=f"Same venue: {venue}"
                        )
    
    def _persist_relationships_to_db(self):
        """Save relationships to PostgreSQL"""
        print("   💾 Persisting relationships to database...")
        
        try:
            # Clear existing relationships
            self.db.query(PaperRelationship).delete()
            
            # Add new relationships
            for edge in self.graph.edges(data=True):
                paper1_id, paper2_id, data = edge
                
                relationship = PaperRelationship(
                    citing_paper_id=paper1_id,
                    cited_paper_id=paper2_id,
                    relationship_type=data.get('type', 'unknown'),
                    similarity_score=data.get('weight', 0.0)
                )
                self.db.add(relationship)
            
            self.db.commit()
            print(f"      ✅ Saved {len(self.graph.edges)} relationships to database")
            
        except Exception as e:
            self.db.rollback()
            print(f"      ❌ Failed to save relationships: {e}")
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        if isinstance(vec2, list):
            vec2 = np.array(vec2)
        vec1 = np.array(vec1)
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    
    def analyze_relationships(self) -> Dict:
        """Analyze graph structure and relationships"""
        if len(self.graph.nodes) == 0:
            return {}
        
        # Basic graph metrics
        analysis = {
            "nodes": len(self.graph.nodes),
            "edges": len(self.graph.edges),
            "density": nx.density(self.graph),
            "clusters": nx.number_connected_components(self.graph),
            "average_degree": sum(dict(self.graph.degree()).values()) / len(self.graph.nodes)
        }
        
        # Relationship type analysis
        relationship_types = Counter()
        for edge in self.graph.edges(data=True):
            rel_type = edge[2].get('type', 'unknown')
            relationship_types[rel_type] += 1
        
        analysis["relationship_types"] = dict(relationship_types)
        
        return analysis
    
    def find_related_papers(self, paper_id: str, max_depth: int = 2) -> List[Dict]:
        """Find related papers with relationship info"""
        if paper_id not in self.graph:
            return []
        
        related = []
        for depth in range(1, max_depth + 1):
            # Get nodes at this distance
            nodes_at_depth = set()
            for node, distance in nx.single_source_shortest_path_length(self.graph, paper_id, cutoff=depth).items():
                if distance == depth:
                    nodes_at_depth.add(node)
            
            # Get relationship details for each node
            for node_id in nodes_at_depth:
                edge_data = self.graph.get_edge_data(paper_id, node_id) or self.graph.get_edge_data(node_id, paper_id)
                if edge_data:
                    related.append({
                        'paper_id': node_id,
                        'distance': depth,
                        'relationship_type': edge_data.get('type', 'unknown'),
                        'similarity_score': edge_data.get('weight', 0.0)
                    })
        
        return related
    
    def close(self):
        """Close database connection"""
        self.db.close()