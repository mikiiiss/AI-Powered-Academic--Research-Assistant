# backend/knowledge_graph/enhanced_graph_builder.py
import asyncio
from typing import List
from sqlalchemy.orm import Session

# Import directly to avoid circular imports
from core.database import SessionLocal
from api.models.database_models import Paper, PaperRelationship
from knowledge_graph.graph_builder import KnowledgeGraphBuilder  # Your existing class
from crawlers.academic_apis.semantic_scholar_crawler import SemanticScholarCrawler

class EnhancedKnowledgeGraphBuilder(KnowledgeGraphBuilder):
    """Extends your KnowledgeGraphBuilder with citation networks"""
    
    def __init__(self):
        # Call parent constructor
        super().__init__()
        self.semantic_crawler = None
    
    async def build_complete_knowledge_graph_with_citations(self):
        """Build enhanced graph with real citation data"""
        print("🕸️ Building enhanced knowledge graph with citations...")
        
        # Get all papers (now including Semantic Scholar papers)
        papers = self.db.query(Paper).all()
        print(f"📄 Processing {len(papers)} papers...")
        
        # Build all existing relationships (your current code)
        self._build_semantic_relationships(papers)
        self._build_venue_relationships(papers)
        
        # NEW: Build citation relationships from Semantic Scholar
        await self._build_citation_relationships(papers)
        
        # Persist everything (your existing method)
        self._persist_relationships_to_db()
        
        # Analyze the enhanced graph
        analysis = self.analyze_relationships()
        
        print(f"🎉 Enhanced knowledge graph complete!")
        print(f"   - Papers: {len(papers)}")
        print(f"   - Relationships: {len(self.graph.edges)}")
        print(f"   - Clusters: {analysis.get('clusters', 0)}")
        
        return self.graph
    
    async def _build_citation_relationships(self, papers: List[Paper]):
        """Build real citation relationships using Semantic Scholar data"""
        print("   📚 Building citation relationships from Semantic Scholar...")
        
        if not self.semantic_crawler:
            self.semantic_crawler = SemanticScholarCrawler()
        
        citation_edges = 0
        
        for i, paper in enumerate(papers):
            if i % 20 == 0:  # Progress indicator
                print(f"      Processing citations for paper {i+1}/{len(papers)}...")
            
            # Only process Semantic Scholar papers for citations
            if paper.source == "semantic_scholar" and hasattr(paper, 'metadata'):
                metadata = paper.metadata or {}
                semantic_id = metadata.get('semantic_scholar_id')
                
                if semantic_id:
                    try:
                        # Get citation data
                        citations = await self.semantic_crawler.get_paper_citations(semantic_id)
                        
                        for citation in citations[:50]:  # Limit for performance
                            cited_paper_id = f"semantic_{citation['paperId']}"
                            
                            # Add citation edge
                            self.graph.add_edge(
                                paper.id, cited_paper_id,
                                type="cites",
                                weight=1.0,
                                label="Citation"
                            )
                            citation_edges += 1
                        
                        # Respect rate limit
                        await asyncio.sleep(1.1)
                        
                    except Exception as e:
                        print(f"      ⚠️  Failed to get citations for {paper.id}: {e}")
                        continue
        
        print(f"      ✅ Added {citation_edges} citation relationships")