#!/usr/bin/env python3
"""
Generate embeddings for papers missing them
Processes 1,594 papers in batches with progress tracking
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.database import SessionLocal
from api.models.database_models import Paper
from sentence_transformers import SentenceTransformer
import time

def generate_missing_embeddings():
    print("🚀 Starting embedding generation for papers missing embeddings...")
    
    # Initialize model
    print("📦 Loading Sentence-BERT model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print(f"✅ Model loaded. Embedding dimension: {model.get_sentence_embedding_dimension()}")
    
    # Connect to database
    db = SessionLocal()
    
    try:
        # Find papers without embeddings
        papers_without_embeddings = db.query(Paper).filter(
            Paper.title_embedding.is_(None)
        ).all()
        
        total_papers = len(papers_without_embeddings)
        print(f"\n📊 Found {total_papers} papers without embeddings")
        
        if total_papers == 0:
            print("✅ All papers already have embeddings!")
            return
        
        # Process in batches
        batch_size = 100
        processed = 0
        start_time = time.time()
        
        for i in range(0, total_papers, batch_size):
            batch = papers_without_embeddings[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (total_papers + batch_size - 1) // batch_size
            
            print(f"\n📦 Processing batch {batch_num}/{total_batches} ({len(batch)} papers)...")
            
            # Prepare texts
            titles = [paper.title for paper in batch]
            abstracts = [paper.abstract if paper.abstract else paper.title for paper in batch]
            
            # Generate embeddings
            print("   Generating title embeddings...")
            title_embeddings = model.encode(titles, show_progress_bar=False)
            
            print("   Generating abstract embeddings...")
            abstract_embeddings = model.encode(abstracts, show_progress_bar=False)
            
            # Update database
            print("   Updating database...")
            for j, paper in enumerate(batch):
                paper.title_embedding = title_embeddings[j].tolist()
                paper.abstract_embedding = abstract_embeddings[j].tolist()
            
            db.commit()
            processed += len(batch)
            
            elapsed = time.time() - start_time
            rate = processed / elapsed
            remaining = (total_papers - processed) / rate if rate > 0 else 0
            
            print(f"   ✅ Batch complete. Progress: {processed}/{total_papers} ({processed/total_papers*100:.1f}%)")
            print(f"   ⏱️  Speed: {rate:.1f} papers/sec, ETA: {remaining:.0f}s")
        
        total_time = time.time() - start_time
        print(f"\n🎉 Embedding generation complete!")
        print(f"   📄 Processed {total_papers} papers")
        print(f"   ⏱️  Total time: {total_time:.1f}s ({total_papers/total_time:.1f} papers/sec)")
        
        # Verify
        papers_with_embeddings = db.query(Paper).filter(
            Paper.title_embedding.isnot(None)
        ).count()
        total = db.query(Paper).count()
        
        print(f"\n📊 Final status:")
        print(f"   Papers with embeddings: {papers_with_embeddings}/{total} ({papers_with_embeddings/total*100:.1f}%)")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    generate_missing_embeddings()
