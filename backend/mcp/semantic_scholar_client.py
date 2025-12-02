# backend/mcp/semantic_scholar_client.py
"""
Semantic Scholar API client for general academic papers
Uses Semantic Scholar's free API - no authentication needed
"""
import aiohttp
import asyncio
from typing import List, Dict, Any, Optional


class SemanticScholarMCPClient:
    """Client for Semantic Scholar API"""
    
    def __init__(self):
        self.base_url = "https://api.semanticscholar.org/graph/v1"
        self.timeout = aiohttp.ClientTimeout(total=10)
    
    async def search_papers(
        self, 
        query: str, 
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search Semantic Scholar for papers
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of paper dictionaries
        """
        print(f"   🌐 Searching Semantic Scholar for: {query}")
        
        url = f"{self.base_url}/paper/search"
        
        params = {
            'query': query,
            'limit': min(max_results, 100),  # API limit is 100
            'fields': 'title,abstract,authors,year,venue,citationCount,externalIds,url'
        }
        
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        papers = self._parse_response(data)
                        print(f"   ✅ Found {len(papers)} papers from Semantic Scholar")
                        return papers
                    else:
                        print(f"   ❌ Semantic Scholar API error: {response.status}")
                        return []
        
        except asyncio.TimeoutError:
            print(f"   ❌ Semantic Scholar API timeout")
            return []
        except Exception as e:
            print(f"   ❌ Semantic Scholar API error: {e}")
            return []
    
    def _parse_response(self, data: dict) -> List[Dict[str, Any]]:
        """Parse Semantic Scholar API response"""
        papers = []
        
        try:
            paper_list = data.get('data', [])
            
            for item in paper_list:
                paper = self._parse_paper(item)
                if paper:
                    papers.append(paper)
        
        except Exception as e:
            print(f"   ⚠️ Error parsing Semantic Scholar response: {e}")
        
        return papers
    
    def _parse_paper(self, item: dict) -> Optional[Dict[str, Any]]:
        """Parse a single paper from Semantic Scholar"""
        try:
            # Extract paper ID
            paper_id = item.get('paperId', f's2_{id(item)}')
            
            # Extract authors
            authors = []
            author_list = item.get('authors', [])
            for author in author_list[:5]:  # Limit to 5 authors
                name = author.get('name')
                if name:
                    authors.append(name)
            
            # Extract external IDs (arXiv, DOI, PubMed, etc.)
            external_ids = item.get('externalIds', {})
            arxiv_id = external_ids.get('ArXiv')
            doi = external_ids.get('DOI')
            
            # Build paper dictionary
            paper = {
                'id': f's2_{paper_id}',
                'title': item.get('title', 'Untitled').strip(),
                'abstract': item.get('abstract', '').strip() if item.get('abstract') else '',
                'authors': ', '.join(authors) if authors else 'Unknown',
                'year': item.get('year'),
                'venue': item.get('venue', 'Unknown'),
                'citation_count': item.get('citationCount', 0),
                'url': item.get('url'),
                'source': 'semantic_scholar',
                's2_id': paper_id,
                'arxiv_id': arxiv_id,
                'doi': doi
            }
            
            return paper
        
        except Exception as e:
            print(f"   ⚠️ Error parsing paper: {e}")
            return None
