#!/usr/bin/env python3
"""
Check if embeddings were stored correctly
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.database import SessionLocal
from api.models.database_models import Paper

def check_embeddings():
    print("🔍 Checking embedding storage...")
    
    db = SessionLocal()
    try:
        # Count papers with embeddings
        total_papers = db.query(Paper).count()
        papers_with_title_emb = db.query(Paper).filter(Paper.title_embedding != None).count()
        papers_with_abstract_emb = db.query(Paper).filter(Paper.abstract_embedding != None).count()
        
        print(f"📊 EMBEDDING STATS:")
        print(f"   - Total papers: {total_papers}")
        print(f"   - Papers with title embeddings: {papers_with_title_emb}")
        print(f"   - Papers with abstract embeddings: {papers_with_abstract_emb}")
        
        # Show a few examples
        sample_papers = db.query(Paper).filter(Paper.title_embedding != None).limit(3).all()
        
        print(f"\n🔤 SAMPLE EMBEDDINGS:")
        for i, paper in enumerate(sample_papers):
            print(f"   {i+1}. {paper.title[:60]}...")
            if paper.title_embedding:
                print(f"      Title embedding: {len(paper.title_embedding)} dimensions")
            if paper.abstract_embedding:
                print(f"      Abstract embedding: {len(paper.abstract_embedding)} dimensions")
            print()
            
    finally:
        db.close()

if __name__ == "__main__":
    check_embeddings()