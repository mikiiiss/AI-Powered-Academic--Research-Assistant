# backend/crawlers/academic_apis/semantic_scholar_crawler.py
import aiohttp
import asyncio
import os
from typing import List, Dict, Optional
from datetime import datetime

class SemanticScholarCrawler:
    def __init__(self):
        self.base_url = "https://api.semanticscholar.org/graph/v1"
        self.api_key = self._get_api_key()
        self.session = None
        self.rate_limit_delay = 1.1  # 1 request per second + buffer
    
    def _get_api_key(self) -> str:
        """Get API key from environment variables - follows your existing pattern"""
        api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
        if not api_key:
            raise ValueError("SEMANTIC_SCHOLAR_API_KEY not found in environment variables")
        return api_key
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers={
            "x-api-key": self.api_key
        })
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    # ... rest of the methods remain exactly the same ...
    async def search_papers(self, query: str, limit: int = 100) -> List[Dict]:
        """Search Semantic Scholar - follows your existing pattern"""
        print(f"🔍 Searching Semantic Scholar for: '{query}'")
        
        fields = [
            "paperId", "title", "abstract", "authors", "venue", "year", 
            "citationCount", "referenceCount", "influentialCitationCount",
            "fieldsOfStudy", "publicationTypes", "publicationDate",
            "url", "openAccessPdf", "tldr"
        ]
        
        url = f"{self.base_url}/paper/search"
        params = {
            "query": query,
            "limit": min(limit, 100),  # API max per request
            "fields": ",".join(fields),
            "offset": 0
        }
        
        all_papers = []
        
        try:
            # Handle pagination for large limits
            while len(all_papers) < limit and params["offset"] < 1000:  # Safety limit
                async with self.session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        batch_papers = data.get("data", [])
                        
                        if not batch_papers:
                            break
                            
                        # Transform to your paper format
                        transformed_papers = [self._transform_paper_format(paper) for paper in batch_papers]
                        all_papers.extend(transformed_papers)
                        
                        print(f"   📄 Got {len(batch_papers)} papers (total: {len(all_papers)})")
                        
                        # Check if we need more
                        if len(batch_papers) < params["limit"]:
                            break
                            
                        # Prepare for next page
                        params["offset"] += params["limit"]
                        
                        # Respect rate limit
                        await asyncio.sleep(self.rate_limit_delay)
                        
                    else:
                        print(f"❌ Semantic Scholar API error: {response.status}")
                        break
                        
        except Exception as e:
            print(f"❌ Semantic Scholar search failed: {e}")
        
        print(f"✅ Found {len(all_papers)} total papers for '{query}'")
        return all_papers[:limit]
    
    def _transform_paper_format(self, paper: Dict) -> Dict:
        """Transform Semantic Scholar format to your database format"""
        # Use paperId as ID to avoid duplicates
        paper_id = f"semantic_{paper['paperId']}"
        
        # Handle authors list
        authors = []
        if paper.get('authors'):
            authors = [f"{author.get('name', 'Unknown')}" for author in paper['authors']]
        
        # Handle publication date
        published_date = None
        if paper.get('publicationDate'):
            try:
                published_date = datetime.strptime(paper['publicationDate'], '%Y-%m-%d').date()
            except:
                pass
        elif paper.get('year'):
            try:
                published_date = datetime(paper['year'], 1, 1).date()
            except:
                pass
        
        # Handle PDF URL
        pdf_url = paper.get('openAccessPdf', {}).get('url') or paper.get('url')
        
        # Handle TLDR summary
        abstract = paper.get('abstract', '')
        if not abstract and paper.get('tldr'):
            abstract = paper['tldr'].get('text', '')
        
        return {
            "id": paper_id,
            "title": paper.get('title', 'No Title'),
            "abstract": abstract,
            "authors": authors,
            "published_date": published_date,
            "citation_count": paper.get('citationCount', 0),
            "venue": paper.get('venue', ''),
            "source": "semantic_scholar",
            "pdf_url": pdf_url,
            "metadata": {
                'influential_citations': paper.get('influentialCitationCount', 0),
                'fields_of_study': paper.get('fieldsOfStudy', []),
                'publication_types': paper.get('publicationTypes', []),
                'reference_count': paper.get('referenceCount', 0),
                'semantic_scholar_id': paper['paperId']
            }
        }
    
    async def get_paper_citations(self, paper_id: str) -> List[Dict]:
        """Get citation data for building knowledge graphs"""
        url = f"{self.base_url}/paper/{paper_id}/citations"
        params = {
            "fields": "paperId,title,year,authors",
            "limit": 100
        }
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("data", [])
        except Exception as e:
            print(f"❌ Failed to get citations for {paper_id}: {e}")
        
        return []
    
    async def get_trending_papers(self, field: str = "Computer Science", limit: int = 50) -> List[Dict]:
        """Get trending papers - great for recommendations"""
        url = f"{self.base_url}/paper/trending"
        params = {
            "fields": "paperId,title,abstract,authors,venue,year,citationCount,influentialCitationCount",
            "limit": limit
        }
        
        if field:
            params["fieldOfStudy"] = field
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    papers = data.get("data", [])
                    return [self._transform_paper_format(paper) for paper in papers]
        except Exception as e:
            print(f"❌ Trending papers fetch failed: {e}")
        
        return []