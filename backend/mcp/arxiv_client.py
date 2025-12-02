# backend/mcp/arxiv_client.py
"""
arXiv API client for fetching CS/Physics/Math papers
Uses arXiv's free API - no authentication needed
"""
import aiohttp
import asyncio
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional
from datetime import datetime


class ArxivMCPClient:
    """Client for arXiv API"""
    
    def __init__(self):
        self.base_url = "http://export.arxiv.org/api/query"
        self.timeout = aiohttp.ClientTimeout(total=10)
    
    async def search_papers(
        self, 
        query: str, 
        category: str = 'cs',  # cs, physics, math, etc.
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search arXiv for papers
        
        Args:
            query: Search query
            category: arXiv category (cs, physics, math, etc.)
            max_results: Maximum number of results
            
        Returns:
            List of paper dictionaries
        """
        print(f"   🌐 Searching arXiv ({category}) for: {query}")
        
        # Build search query
        # Format: search_query=all:query AND cat:category
        search_query = f'all:{query}'
        if category:
            search_query = f'{search_query} AND cat:{category}*'
        
        params = {
            'search_query': search_query,
            'start': 0,
            'max_results': max_results,
            'sortBy': 'relevance',
            'sortOrder': 'descending'
        }
        
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        xml_content = await response.text()
                        papers = self._parse_arxiv_response(xml_content)
                        print(f"   ✅ Found {len(papers)} papers from arXiv")
                        return papers
                    else:
                        print(f"   ❌ arXiv API error: {response.status}")
                        return []
        
        except asyncio.TimeoutError:
            print(f"   ❌ arXiv API timeout")
            return []
        except Exception as e:
            print(f"   ❌ arXiv API error: {e}")
            return []
    
    def _parse_arxiv_response(self, xml_content: str) -> List[Dict[str, Any]]:
        """Parse arXiv XML response"""
        papers = []
        
        try:
            # Parse XML
            root = ET.fromstring(xml_content)
            
            # arXiv uses Atom namespace
            ns = {
                'atom': 'http://www.w3.org/2005/Atom',
                'arxiv': 'http://arxiv.org/schemas/atom'
            }
            
            # Find all entry elements (papers)
            entries = root.findall('atom:entry', ns)
            
            for entry in entries:
                paper = self._parse_entry(entry, ns)
                if paper:
                    papers.append(paper)
        
        except Exception as e:
            print(f"   ⚠️ Error parsing arXiv XML: {e}")
        
        return papers
    
    def _parse_entry(self, entry: ET.Element, ns: dict) -> Optional[Dict[str, Any]]:
        """Parse a single arXiv entry"""
        try:
            # Extract basic fields
            title = entry.find('atom:title', ns)
            summary = entry.find('atom:summary', ns)
            published = entry.find('atom:published', ns)
            updated = entry.find('atom:updated', ns)
            
            # Extract arXiv ID from id field
            id_elem = entry.find('atom:id', ns)
            arxiv_id = id_elem.text.split('/')[-1] if id_elem is not None else None
            
            # Extract authors
            authors = []
            for author in entry.findall('atom:author', ns):
                name = author.find('atom:name', ns)
                if name is not None:
                    authors.append(name.text)
            
            # Extract categories
            categories = []
            for category in entry.findall('atom:category', ns):
                term = category.get('term')
                if term:
                    categories.append(term)
            
            # Extract links
            pdf_link = None
            for link in entry.findall('atom:link', ns):
                if link.get('title') == 'pdf':
                    pdf_link = link.get('href')
                    break
            
            # Parse date
            date_str = published.text if published is not None else None
            year = None
            if date_str:
                try:
                    dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    year = dt.year
                except:
                    year = None
            
            # Build paper dictionary
            paper = {
                'id': f'arxiv_{arxiv_id}' if arxiv_id else f'arxiv_{id(entry)}',
                'title': title.text.strip() if title is not None else 'Untitled',
                'abstract': summary.text.strip() if summary is not None else '',
                'authors': ', '.join(authors) if authors else 'Unknown',
                'year': year,
                'venue': f"arXiv {categories[0] if categories else 'preprint'}",
                'citation_count': 0,  # arXiv doesn't provide citation counts
                'url': pdf_link,
                'source': 'arxiv',
                'arxiv_id': arxiv_id,
                'categories': categories
            }
            
            return paper
        
        except Exception as e:
            print(f"   ⚠️ Error parsing arXiv entry: {e}")
            return None
