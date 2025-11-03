#!/usr/bin/env python3
"""
Generate embeddings for all papers in database
"""

import asyncio
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from data_pipeline.paper_storage import PaperStorage
from ml_pipeline.embedding_service import EmbeddingService
from core.database import SessionLocal
from api.models.database_models import Paper

class EmbeddingGenerator:
    def __init__(self):
        self.storage = PaperStorage()
        self.embedding_service = EmbeddingService()
    
    async def generate_all_embeddings(self):
        print("🔤 Generating embeddings for all papers...")
        
        db = SessionLocal()
        try:
            # Get all papers without embeddings
            papers = db.query(Paper).all()
            
            print(f"📄 Processing {len(papers)} papers for embeddings...")
            
            processed_count = 0
            for i, paper in enumerate(papers):
                if i % 50 == 0:
                    print(f"⏳ Processing paper {i+1}/{len(papers)}...")
                
                # Skip if already has embeddings
                if paper.title_embedding is not None:
                    continue
                
                # Generate embeddings for title and abstract
                await self._add_embeddings_to_paper(paper)
                processed_count += 1
                
                # Small delay to avoid overwhelming the model
                if i % 10 == 0:
                    await asyncio.sleep(0.1)
            
            db.commit()
            print(f"✅ Generated embeddings for {processed_count} papers!")
            
        except Exception as e:
            print(f"❌ Embedding generation failed: {e}")
            db.rollback()
            raise
        finally:
            db.close()
    
    async def _add_embeddings_to_paper(self, paper):
        """Add embeddings to a single paper"""
        try:
            # Generate title embedding
            if paper.title:
                title_embedding = await self.embedding_service.encode_single(paper.title)
                paper.title_embedding = title_embedding.tolist()
            
            # Generate abstract embedding (if available)
            if paper.abstract and len(paper.abstract) > 50:  # Only if substantial abstract
                abstract_embedding = await self.embedding_service.encode_single(paper.abstract[:1000])  # Limit length
                paper.abstract_embedding = abstract_embedding.tolist()
            
        except Exception as e:
            print(f"❌ Failed to generate embeddings for paper {paper.id}: {e}")

async def main():
    start_time = time.time()
    
    try:
        generator = EmbeddingGenerator()
        await generator.generate_all_embeddings()
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n🎉 EMBEDDING GENERATION COMPLETE!")
        print(f"   ⏱️  Time taken: {duration:.2f} seconds")
        
    except Exception as e:
        print(f"\n💥 EMBEDDING GENERATION FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())