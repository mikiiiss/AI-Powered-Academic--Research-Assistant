# backend/mcp/mcp_router.py
"""
MCP Router - Routes queries to appropriate MCP servers with automatic fallback
"""
from typing import List, Dict, Any
from .arxiv_client import ArxivMCPClient
from .pubmed_client import PubMedMCPClient
from .semantic_scholar_client import SemanticScholarMCPClient


class MCPRouter:
    """Routes queries to appropriate MCP server based on domain with fallback"""
    
    def __init__(self):
        # Initialize all MCP clients
        self.arxiv_client = ArxivMCPClient()
        self.pubmed_client = PubMedMCPClient()
        self.semantic_scholar_client = SemanticScholarMCPClient()
        
        # Define primary and fallback routes
        self.routes = {
            'medical': {
                'primary': ('pubmed', self.pubmed_client),
                'fallback': ('semantic_scholar', self.semantic_scholar_client)
            },
            'tech': {
                'primary': ('arxiv', self.arxiv_client),
                'fallback': ('semantic_scholar', self.semantic_scholar_client)
            },
            'physics': {
                'primary': ('arxiv', self.arxiv_client),
                'fallback': ('semantic_scholar', self.semantic_scholar_client)
            },
            'general': {
                'primary': ('semantic_scholar', self.semantic_scholar_client),
                'fallback': ('arxiv', self.arxiv_client)
            }
        }
        
        print("✅ MCPRouter initialized with 3 clients + fallback")
    
    async def search_external(
        self, 
        domain: str, 
        query: str, 
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Route query to appropriate MCP server with automatic fallback
        
        Args:
            domain: Research domain ('medical', 'tech', 'physics', 'general')
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of papers from external source
        """
        route_config = self.routes.get(domain, self.routes['general'])
        
        primary_name, primary_client = route_config['primary']
        fallback_name, fallback_client = route_config['fallback']
        
        print(f"   🎯 Domain: {domain} → Primary: {primary_name}, Fallback: {fallback_name}")
        
        # Try primary source first
        papers = await self._search_with_client(
            primary_client, 
            primary_name,
            query, 
            max_results,
            domain
        )
        
        # If primary fails or returns insufficient results, try fallback
        if not papers or len(papers) < 5:
            if papers:
                print(f"   ⚠️ {primary_name} returned only {len(papers)} papers, trying fallback...")
            else:
                print(f"   ⚠️ {primary_name} failed, trying fallback...")
            
            fallback_papers = await self._search_with_client(
                fallback_client,
                fallback_name,
                query,
                max_results,
                domain
            )
            
            # Merge results if both sources returned papers
            if papers and fallback_papers:
                papers.extend(fallback_papers)
                print(f"   ✅ Combined {len(papers)} papers from both sources")
            elif fallback_papers:
                papers = fallback_papers
        
        return papers
    
    async def _search_with_client(
        self,
        client,
        client_name: str,
        query: str,
        max_results: int,
        domain: str
    ) -> List[Dict[str, Any]]:
        """Search with a specific MCP client"""
        try:
            # Special handling for arXiv (needs category)
            if client_name == 'arxiv':
                category = self._get_arxiv_category(domain)
                return await client.search_papers(query, category=category, max_results=max_results)
            else:
                return await client.search_papers(query, max_results=max_results)
        
        except Exception as e:
            print(f"   ❌ {client_name} search failed: {e}")
            return []
    
    def _get_arxiv_category(self, domain: str) -> str:
        """Map domain to arXiv category"""
        category_map = {
            'tech': 'cs',
            'physics': 'physics',
            'general': 'cs'
        }
        return category_map.get(domain, 'cs')
