# #!/usr/bin/env python3
# """
# Collect 10,000 data science papers using our existing structure
# """

# import asyncio
# import sys
# import os

# # Add the backend directory to Python path
# sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# # Now import from our local modules
# from crawlers.academic_apis.arxiv_crawler import ArXivCrawler
# from data_pipeline.paper_storage import PaperStorage

# async def collect_data_science_papers():
#     print("🚀 Starting collection of 10,000 data science papers...")
    
#     # Initialize our existing components
#     crawler = ArXivCrawler()
#     storage = PaperStorage()
    
#     # Data science domains to cover
#     domains = [
#         "machine learning", "deep learning", "neural network",
#         "natural language processing", "computer vision", 
#         "reinforcement learning", "artificial intelligence",
#         "transformer", "convolutional neural network",
#         "generative adversarial network", "large language model"
#          "machine learning", "deep learning", "neural network",
#     "natural language processing", "computer vision", 
#     "reinforcement learning", "artificial intelligence",
#     # Add more specific terms
#     "transformer architecture", "convolutional neural networks",
#     "generative adversarial networks", "large language models",
#     "computer vision object detection", "nlp sentiment analysis",
#     "reinforcement learning robotics", "time series forecasting",
#     "anomaly detection", "clustering algorithms", "classification models"
#     ]
    
#     all_papers = []
#     target_count = 100  # Start with 100 for testing, then increase to 10000
    
    
#     for domain in domains:
#         if len(all_papers) >= target_count:
#             break
            
#         print(f"📥 Searching for: {domain}")
        
#         try:
#             # Use our existing arXiv crawler
#             papers = await crawler.search_papers(domain, max_results=50)  # Small batches for testing
#             all_papers.extend(papers)
            
#             print(f"✅ Found {len(papers)} papers for '{domain}' (Total: {len(all_papers)})")
            
#         except Exception as e:
#             print(f"❌ Error collecting {domain}: {e}")
#             import traceback
#             traceback.print_exc()
        
#         # Be nice to the API
#         await asyncio.sleep(2)
    
#     # Remove duplicates
#     unique_papers = []
#     seen_titles = set()
    
#     for paper in all_papers:
#         title = paper.get('title', '').lower().strip()
#         if title and title not in seen_titles:
#             seen_titles.add(title)
#             unique_papers.append(paper)
    
#     print(f"📊 After deduplication: {len(unique_papers)} unique papers")
    
#     # Store in our existing database
#     if len(unique_papers) > target_count:
#         unique_papers = unique_papers[:target_count]
    
#     stored_count = await storage.store_papers_batch(unique_papers)
#     print(f"💾 Stored {stored_count} papers in Neon database")
    
#     return stored_count


# if __name__ == "__main__":
#     count = asyncio.run(collect_data_science_papers())
#     print(f"🎉 Successfully collected {count} data science papers!")

#!/usr/bin/env python3
"""
Collect 1,000 data science papers (realistic target)
"""

import asyncio
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from crawlers.academic_apis.arxiv_crawler import ArXivCrawler
from data_pipeline.paper_storage import PaperStorage

class ThousandPaperCollector:
    def __init__(self):
        self.arxiv_crawler = ArXivCrawler()
        self.storage = PaperStorage()
        self.target_count = 1000
    
    async def collect_papers(self):
        print("🚀 Starting collection of 1,000 data science papers...")
        
        # Focus on fewer domains but get more papers from each
        domains = [
            "machine learning",
            "deep learning", 
            "neural network",
            "natural language processing",
            "computer vision",
            "transformer",
            "reinforcement learning"
        ]
        
        all_papers = []
        
        for domain in domains:
            if len(all_papers) >= self.target_count:
                break
                
            print(f"📥 Searching: {domain}")
            
            try:
                papers = await self.arxiv_crawler.search_papers(domain, max_results=200)
                all_papers.extend(papers)
                print(f"   ✅ Found {len(papers)} papers (Total: {len(all_papers)})")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
            
            await asyncio.sleep(1)
        
        # Remove duplicates
        unique_papers = self._deduplicate_papers(all_papers)
        
        print(f"\n📊 Collection Summary:")
        print(f"   - Collected: {len(all_papers)}")
        print(f"   - Unique: {len(unique_papers)}")
        print(f"   - Target: {self.target_count}")
        
        # Limit to target
        if len(unique_papers) > self.target_count:
            unique_papers = unique_papers[:self.target_count]
        
        # Save in batches
        saved_count = await self._save_safely(unique_papers)
        
        return saved_count
    
    def _deduplicate_papers(self, papers):
        """Remove duplicate papers"""
        seen_titles = set()
        unique_papers = []
        
        for paper in papers:
            if paper is None:
                continue
                
            title = paper.get('title')
            if title is None:
                continue
                
            try:
                clean_title = str(title).lower().strip()
                if clean_title and clean_title not in seen_titles:
                    seen_titles.add(clean_title)
                    unique_papers.append(paper)
            except:
                continue
        
        return unique_papers
    
    async def _save_safely(self, papers):
        """Save papers in small batches"""
        print("💾 Saving papers in safe batches...")
        
        batch_size = 50
        total_saved = 0
        
        for i in range(0, len(papers), batch_size):
            batch = papers[i:i + batch_size]
            
            try:
                saved = await self.storage.store_papers_batch(batch)
                total_saved += saved
                print(f"   ✅ Batch {i//batch_size + 1}: Saved {saved} papers")
                
                await asyncio.sleep(1)  # Rate limiting
                
            except Exception as e:
                print(f"   ❌ Batch {i//batch_size + 1} failed: {e}")
                # Try to continue with next batch
                continue
        
        return total_saved

async def main():
    start_time = time.time()
    
    try:
        collector = ThousandPaperCollector()
        count = await collector.collect_papers()
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n🎉 COLLECTION COMPLETED!")
        print(f"   📄 Total papers stored: {count}")
        print(f"   ⏱️  Time taken: {duration:.2f} seconds")
        print(f"   🚀 Speed: {count/(duration/60):.1f} papers per minute")
        
    except Exception as e:
        print(f"\n💥 COLLECTION FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())