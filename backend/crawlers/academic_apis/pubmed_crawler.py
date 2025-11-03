import aiohttp
import asyncio
from typing import List, Dict, Optional
import xml.etree.ElementTree as ET

class PubMedCrawler:
    def __init__(self, email: str = "research@example.com"):
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        self.email = email
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def search_papers(self, query: str, max_results: int = 100) -> List[Dict]:
        """Search PubMed for papers"""
        try:
            # Search for paper IDs
            search_url = f"{self.base_url}/esearch.fcgi"
            params = {
                "db": "pubmed",
                "term": f"{query} AND (ai OR artificial intelligence OR machine learning OR deep learning)",
                "retmax": max_results,
                "retmode": "json",
                "email": self.email,
                "sort": "relevance"
            }
            
            async with self.session.get(search_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    paper_ids = data.get("esearchresult", {}).get("idlist", [])
                    
                    if not paper_ids:
                        print(f"      ℹ️  No results for: {query}")
                        return []
                    
                    # Get paper details
                    papers = await self._get_paper_details(paper_ids)
                    return papers
                else:
                    print(f"      ❌ PubMed API error: {response.status}")
                    return []
                    
        except Exception as e:
            print(f"      ❌ PubMed search failed: {e}")
            return []
    
    async def _get_paper_details(self, paper_ids: List[str]) -> List[Dict]:
        """Get detailed information for paper IDs"""
        if not paper_ids:
            return []
            
        details_url = f"{self.base_url}/efetch.fcgi"
        params = {
            "db": "pubmed",
            "id": ",".join(paper_ids),
            "retmode": "xml"
        }
        
        try:
            async with self.session.get(details_url, params=params) as response:
                if response.status == 200:
                    xml_content = await response.text()
                    return self._parse_pubmed_xml(xml_content)
                else:
                    print(f"      ❌ PubMed details error: {response.status}")
                    return []
        except Exception as e:
            print(f"      ❌ PubMed details failed: {e}")
            return []
    def _parse_pubmed_xml(self, xml_content: str) -> List[Dict]:
        """Parse PubMed XML response"""
        papers = []
    
        try:
            root = ET.fromstring(xml_content)
            
            for article in root.findall(".//PubmedArticle"):
                paper = self._extract_paper_data(article)
                # Only add valid papers with titles
                if paper and paper.get('title') and paper['title'] != "No Title":
                    papers.append(paper)
            
            print(f"      📄 Parsed {len(papers)} valid papers from PubMed")
            return papers
            
        except Exception as e:
            print(f"      ❌ XML parsing error: {e}")
            return []
    def _extract_paper_data(self, article) -> Optional[Dict]:
        """Extract paper data from XML element"""
        try:
            # Get PubMed ID
            pmid_elem = article.find(".//PMID")
            if pmid_elem is None or not pmid_elem.text:
                return None
            
            pmid = pmid_elem.text
            
            # Get title
            title_elem = article.find(".//ArticleTitle")
            title = title_elem.text if title_elem is not None else "No Title"
            
            # Get abstract
            abstract = ""
            abstract_elems = article.findall(".//AbstractText")
            for elem in abstract_elems:
                if elem.text:
                    abstract += elem.text + " "
            abstract = abstract.strip()
            
            # Get authors
            authors = []
            author_elems = article.findall(".//Author")
            for author_elem in author_elems:
                last_name_elem = author_elem.find("LastName")
                fore_name_elem = author_elem.find("ForeName")
                
                if last_name_elem is not None and last_name_elem.text:
                    if fore_name_elem is not None and fore_name_elem.text:
                        authors.append(f"{fore_name_elem.text} {last_name_elem.text}")
                    else:
                        authors.append(last_name_elem.text)
            
            # Get publication date
            pub_date_elem = article.find(".//PubDate")
            published_date = None
            if pub_date_elem is not None:
                year_elem = pub_date_elem.find("Year")
                if year_elem is not None and year_elem.text:
                    try:
                        published_date = f"{year_elem.text}-01-01"
                    except:
                        pass
            
            # Get journal
            journal_elem = article.find(".//Journal/Title")
            journal = journal_elem.text if journal_elem is not None else "Unknown Journal"
            
            return {
                "id": f"pubmed_{pmid}",
                "title": title,
                "abstract": abstract,
                "authors": authors,
                "published_date": published_date,
                "venue": journal,
                "source": "pubmed",
                "citation_count": 0,  # PubMed doesn't provide citation counts
                "pdf_url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
            }
            
        except Exception as e:
            return None

# Example usage
async def main():
    async with PubMedCrawler() as crawler:
        papers = await crawler.search_papers("machine learning medical imaging", max_results=5)
        for i, paper in enumerate(papers):
            print(f"{i+1}. {paper['title'][:80]}...")
            print(f"   Journal: {paper['venue']}")

if __name__ == "__main__":
    asyncio.run(main())