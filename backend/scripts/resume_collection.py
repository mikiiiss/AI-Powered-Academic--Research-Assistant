#!/usr/bin/env python3
"""
Resume collection from where we left off - we already have 3,895 papers!
"""

import asyncio
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from crawlers.academic_apis.arxiv_crawler import ArXivCrawler
from crawlers.academic_apis.pubmed_crawler import PubMedCrawler
from data_pipeline.paper_storage import PaperStorage

async def resume_collection():
    print("🔄 RESUMING COLLECTION - We have 3,895 papers already!")
    print("🎯 Target: Additional 6,105 papers to reach 10,000")
    
    storage = PaperStorage()
    
    # Check how many papers we already have
    existing_papers = storage.get_all_papers(limit=5)
    print(f"📊 Currently in database: {len(existing_papers)} papers")
    
    # Continue with remaining collection
    collector = DataSciencePaperCollector()
    
    # Focus on fewer domains but get more papers from each
    remaining_domains = [
        "transformer language model",
        "computer vision segmentation", 
        "reinforcement learning gaming",
        "neural architecture search",
        "explainable AI",
        "federated learning",
        "graph neural networks",
        "time series prediction",
        "natural language generation",
        "image generation"
    ]
    
    additional_papers = await collector._collect_arxiv_papers(remaining_domains)
    
    print(f"📥 Collected {len(additional_papers)} additional papers")
    
    # Store in smaller batches to avoid timeout
    batch_size = 100
    total_stored = 0
    
    for i in range(0, len(additional_papers), batch_size):
        batch = additional_papers[i:i + batch_size]
        stored = await storage.store_papers_batch(batch)
        total_stored += stored
        print(f"💾 Batch {i//batch_size + 1}: Stored {stored} papers")
        
        # Small delay between batches
        await asyncio.sleep(1)
    
    print(f"🎉 Successfully stored {total_stored} additional papers!")
    return total_stored

class DataSciencePaperCollector:
    def __init__(self):
        self.arxiv_crawler = ArXivCrawler()
        self.pubmed_crawler = PubMedCrawler()
        self.storage = PaperStorage()
    
    async def _collect_arxiv_papers(self, domains):
        """Collect papers from arXiv with smaller batches"""
        papers = []
        
        for domain in domains:
            print(f"   🔍 arXiv: {domain}")
            
            try:
                # Get smaller batches to avoid API issues
                domain_papers = await self.arxiv_crawler.search_papers(
                    query=domain, 
                    max_results=500  # Larger per domain
                )
                papers.extend(domain_papers)
                
                print(f"      ✅ Found {len(domain_papers)} papers (Total: {len(papers)})")
                
            except Exception as e:
                print(f"      ❌ Error: {e}")
            
            # Rate limiting
            await asyncio.sleep(2)
        
        return papers

if __name__ == "__main__":
    count = asyncio.run(resume_collection())
    print(f"🎉 Resume completed! Added {count} papers.")