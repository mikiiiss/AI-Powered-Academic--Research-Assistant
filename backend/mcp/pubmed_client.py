# backend/mcp/pubmed_client.py
"""
PubMed API client for fetching medical/biomedical papers
Uses NCBI E-utilities API - free, no key required (but recommended)
"""
import aiohttp
import asyncio
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional
import os


class PubMedMCPClient:
    """Client for PubMed/NCBI E-utilities API"""
    
    def __init__(self):
        self.search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        self.fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        self.api_key = os.getenv("PUBMED_API_KEY")  # Optional
        self.timeout = aiohttp.ClientTimeout(total=15)
        
        # User email for NCBI (recommended by their guidelines)
        self.email = os.getenv("PUBMED_EMAIL", "research@example.com")
    
    async def search_papers(
        self, 
        query: str, 
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search PubMed for papers
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of paper dictionaries
        """
        print(f"   🌐 Searching PubMed for: {query}")
        
        # Step 1: Search for PMIDs
        pmids = await self._search_pmids(query, max_results)
        
        if not pmids:
            print(f"   ⚠️ No PMIDs found")
            return []
        
        print(f"   📋 Found {len(pmids)} PMIDs")
        
        # Step 2: Fetch paper details
        papers = await self._fetch_paper_details(pmids)
        
        print(f"   ✅ Retrieved {len(papers)} papers from PubMed")
        return papers
    
    async def _search_pmids(self, query: str, max_results: int) -> List[str]:
        """Search PubMed and get PMIDs"""
        params = {
            'db': 'pubmed',
            'term': query,
            'retmax': max_results,
            'retmode': 'xml',
            'sort': 'relevance',
            'email': self.email
        }
        
        if self.api_key:
            params['api_key'] = self.api_key
        
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(self.search_url, params=params) as response:
                    if response.status == 200:
                        xml_content = await response.text()
                        return self._parse_pmids(xml_content)
                    else:
                        print(f"   ❌ PubMed search error: {response.status}")
                        return []
        
        except asyncio.TimeoutError:
            print(f"   ❌ PubMed search timeout")
            return []
        except Exception as e:
            print(f"   ❌ PubMed search error: {e}")
            return []
    
    def _parse_pmids(self, xml_content: str) -> List[str]:
        """Parse PMIDs from search response"""
        try:
            root = ET.fromstring(xml_content)
            id_list = root.find('IdList')
            if id_list is not None:
                return [id_elem.text for id_elem in id_list.findall('Id')]
            return []
        except Exception as e:
            print(f"   ⚠️ Error parsing PMIDs: {e}")
            return []
    
    async def _fetch_paper_details(self, pmids: List[str]) -> List[Dict[str, Any]]:
        """Fetch full paper details for PMIDs"""
        # PubMed prefers batches of up to 200
        pmid_str = ','.join(pmids[:50])  # Limit to 50 for now
        
        params = {
            'db': 'pubmed',
            'id': pmid_str,
            'retmode': 'xml',
            'rettype': 'abstract',
            'email': self.email
        }
        
        if self.api_key:
            params['api_key'] = self.api_key
        
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(self.fetch_url, params=params) as response:
                    if response.status == 200:
                        xml_content = await response.text()
                        return self._parse_paper_details(xml_content)
                    else:
                        print(f"   ❌ PubMed fetch error: {response.status}")
                        return []
        
        except asyncio.TimeoutError:
            print(f"   ❌ PubMed fetch timeout")
            return []
        except Exception as e:
            print(f"   ❌ PubMed fetch error: {e}")
            return []
    
    def _parse_paper_details(self, xml_content: str) -> List[Dict[str, Any]]:
        """Parse paper details from fetch response"""
        papers = []
        
        try:
            root = ET.fromstring(xml_content)
            
            for article in root.findall('.//PubmedArticle'):
                paper = self._parse_article(article)
                if paper:
                    papers.append(paper)
        
        except Exception as e:
            print(f"   ⚠️ Error parsing PubMed papers: {e}")
        
        return papers
    
    def _parse_article(self, article: ET.Element) -> Optional[Dict[str, Any]]:
        """Parse a single PubMed article"""
        try:
            # Extract PMID
            pmid_elem = article.find('.//PMID')
            pmid = pmid_elem.text if pmid_elem is not None else None
            
            # Extract basic citation info
            medline = article.find('.//MedlineCitation')
            if medline is None:
                return None
            
            article_elem = medline.find('.//Article')
            if article_elem is None:
                return None
            
            # Title
            title_elem = article_elem.find('.//ArticleTitle')
            title = title_elem.text if title_elem is not None else 'Untitled'
            
            # Abstract
            abstract_elem = article_elem.find('.//Abstract/AbstractText')
            abstract = abstract_elem.text if abstract_elem is not None else ''
            
            # Authors
            authors = []
            author_list = article_elem.find('.//AuthorList')
            if author_list is not None:
                for author in author_list.findall('.//Author'):
                    last_name = author.find('.//LastName')
                    first_name = author.find('.//ForeName')
                    if last_name is not None:
                        name = last_name.text
                        if first_name is not None:
                            name = f"{first_name.text} {name}"
                        authors.append(name)
            
            # Journal
            journal_elem = article_elem.find('.//Journal/Title')
            journal = journal_elem.text if journal_elem is not None else 'Unknown'
            
            # Publication year
            year = None
            pub_date = article_elem.find('.//PubDate/Year')
            if pub_date is not None:
                try:
                    year = int(pub_date.text)
                except:
                    pass
            
            # Build paper dictionary
            paper = {
                'id': f'pubmed_{pmid}' if pmid else f'pubmed_{id(article)}',
                'title': title.strip() if title else 'Untitled',
                'abstract': abstract.strip() if abstract else '',
                'authors': ', '.join(authors[:5]) if authors else 'Unknown',  # Limit to 5 authors
                'year': year,
                'venue': journal,
                'citation_count': 0,  # PubMed doesn't provide citation counts via basic API
                'url': f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else None,
                'source': 'pubmed',
                'pmid': pmid
            }
            
            return paper
        
        except Exception as e:
            print(f"   ⚠️ Error parsing article: {e}")
            return None
