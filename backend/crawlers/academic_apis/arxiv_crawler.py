# import arxiv
# import asyncio
# from typing import List, Dict, Optional
# from datetime import datetime

# class ArXivCrawler:
#     def __init__(self, max_results: int = 100):
#         self.client = arxiv.Client()
#         self.max_results = max_results
    
#     async def search_papers(self, query: str, max_results: Optional[int] = None) -> List[Dict]:
#         """Search arXiv for papers matching query"""
#         max_results = max_results or self.max_results
        
#         search = arxiv.Search(
#             query=query,
#             max_results=max_results,
#             sort_by=arxiv.SortCriterion.SubmittedDate
#         )
        
#         papers = []
#         try:
#             for result in self.client.results(search):
#                 paper = {
#                     "arxiv_id": result.entry_id,
#                     "title": result.title,
#                     "abstract": result.summary,
#                     "authors": [str(author) for author in result.authors],
#                     "published_date": result.published,
#                     "updated_date": result.updated,
#                     "pdf_url": result.pdf_url,
#                     "primary_category": result.primary_category,
#                     "categories": result.categories,
#                     "source": "arxiv",
#                     "metadata": {
#                         'journal_ref': result.journal_ref,
#                         'comment': result.comment,
#                         'doi': result.doi,
#                     }
#                 }
#                 papers.append(paper)
            
#             print(f"📄 Found {len(papers)} arXiv papers for query: '{query}'")
        
#         except Exception as e:
#             print(f"❌ arXiv search error: {e}")
        
#         return papers
    
#     async def get_recent_papers(self, category: str = "cs.AI", days: int = 7) -> List[Dict]:
#         """Get recent papers from specific category"""
#         from datetime import datetime, timedelta
#         since_date = datetime.now() - timedelta(days=days)
        
#         query = f"cat:{category} AND submittedDate:[{since_date.strftime('%Y%m%d')}0000 TO *]"
#         return await self.search_papers(query)

# # Example usage - this part runs when you execute the file directly
# async def main():
#     crawler = ArXivCrawler()
#     papers = await crawler.search_papers("machine learning", max_results=50)
    
#     for paper in papers:
#         print(f"📖 {paper['title']}")
#         print(f"   👥 Authors: {', '.join(paper['authors'][:3])}")
#         print(f"   📅 Published: {paper['published_date']}")
#         print("---")

# if __name__ == "__main__":
#     asyncio.run(main())


# backend/crawlers/academic_apis/arxiv_crawler.py
import arxiv
import asyncio
from typing import List, Dict, Optional
from datetime import datetime

class ArXivCrawler:
    def __init__(self, max_results: int = 100):
        self.client = arxiv.Client()
        self.max_results = max_results
    
    async def search_papers(self, query: str, max_results: Optional[int] = None) -> List[Dict]:
        """Search arXiv for papers matching query"""
        max_results = max_results or self.max_results
        
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate
        )
        
        papers = []
        try:
            for result in self.client.results(search):
                # Use arXiv ID as the paper ID
                arxiv_id = result.entry_id.split('/')[-1]  # Extract just the ID part
                
                paper = {
                    "id": f"arxiv_{arxiv_id}",  # Add unique ID
                    "arxiv_id": arxiv_id,
                    "title": result.title,
                    "abstract": result.summary,
                    "authors": [str(author) for author in result.authors],
                    "published_date": result.published,
                    "pdf_url": result.pdf_url,
                    "source": "arxiv",
                    "categories": result.categories,
                    "metadata": {
                        'journal_ref': result.journal_ref,
                        'comment': result.comment,
                        'doi': result.doi,
                    }
                }
                papers.append(paper)
            
            print(f"📄 Found {len(papers)} arXiv papers for query: '{query}'")
        
        except Exception as e:
            print(f"❌ arXiv search error: {e}")
        
        return papers