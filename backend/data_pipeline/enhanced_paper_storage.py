# backend/data_pipeline/enhanced_paper_storage.py
import asyncio
import os
from typing import List, Dict
from .paper_storage import PaperStorage  # Your existing class

# Import crawlers - they'll handle their own .env loading
try:
    from crawlers.academic_apis.semantic_scholar_crawler import SemanticScholarCrawler
    from crawlers.academic_apis.arxiv_crawler import ArXivCrawler
except ImportError as e:
    print(f"⚠️ Import warning: {e}")
    # Define fallback classes if imports fail
    class SemanticScholarCrawler:
        def __init__(self):
            raise ImportError("SemanticScholarCrawler not available")
    
    class ArXivCrawler:
        def __init__(self):
            raise ImportError("ArXivCrawler not available")

class EnhancedPaperStorage(PaperStorage):
    """Extends your existing PaperStorage with Semantic Scholar support"""
    
    async def import_from_semantic_scholar(self, queries: List[str], papers_per_query: int = 200) -> int:
        """Bulk import from Semantic Scholar - follows your patterns"""
        total_imported = 0
        
        try:
            async with SemanticScholarCrawler() as crawler:
                for i, query in enumerate(queries):
                    print(f"🔍 [{i+1}/{len(queries)}] Importing papers for: '{query}'")
                    
                    try:
                        # Get papers from Semantic Scholar
                        papers = await crawler.search_papers(query, limit=papers_per_query)
                        
                        if not papers:
                            print(f"   ⚠️  No papers found for '{query}'")
                            continue
                        
                        # Store in database using your existing method
                        stored_count = await self.store_papers_batch(papers)
                        total_imported += stored_count
                        
                        print(f"   ✅ Stored {stored_count}/{len(papers)} papers for '{query}'")
                        
                        # Small delay between queries
                        await asyncio.sleep(1.5)
                        
                    except Exception as e:
                        print(f"   ❌ Failed to import for '{query}': {e}")
                        continue
        except Exception as e:
            print(f"❌ Semantic Scholar crawler failed: {e}")
            return 0
        
        print(f"🎉 Semantic Scholar import complete! Total: {total_imported} papers")
        return total_imported
    
    async def build_comprehensive_database(self) -> int:
        """Build comprehensive AI research database - your main upgrade script"""
        # AI research queries tailored to get diverse papers
        ai_queries = [
            "machine learning", "deep learning", "neural networks",
            "transformer architecture", "large language models",
        ]
        
        total_papers = 0
        
        print("🚀 Starting comprehensive database build...")
        
        # Phase 1: Semantic Scholar (main source)
        print("\n📥 Phase 1: Importing from Semantic Scholar...")
        semantic_count = await self.import_from_semantic_scholar(ai_queries, papers_per_query=50)
        total_papers += semantic_count
        
        print(f"\n🎉 Database build complete! Total papers: {total_papers}")
        return total_papers