#!/usr/bin/env python3
"""
Check what's currently in the database
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from data_pipeline.paper_storage import PaperStorage

def check_database():
    storage = PaperStorage()
    papers = storage.get_all_papers(limit=1000)
    
    print(f"📊 CURRENT DATABASE STATUS:")
    print(f"   - Total papers: {len(papers)}")
    
    if papers:
        print(f"   - Sample papers:")
        for i, paper in enumerate(papers[:5]):
            print(f"     {i+1}. {paper.title[:60]}...")
    
    # Count by source
    sources = {}
    for paper in papers:
        source = paper.source
        sources[source] = sources.get(source, 0) + 1
    
    print(f"   - By source: {sources}")

if __name__ == "__main__":
    check_database()