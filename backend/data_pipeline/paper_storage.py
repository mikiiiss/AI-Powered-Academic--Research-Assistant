import asyncio
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from datetime import datetime
import uuid
import sys
import os
import json

# Add the backend directory to Python path for absolute imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Use absolute imports
from api.models.database_models import Paper, Base
from core.database import engine, SessionLocal
from ml_pipeline.embedding_service import EmbeddingService

class PaperStorage:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        # Create tables if they don't exist
        Base.metadata.create_all(bind=engine)
        print("✅ PaperStorage initialized - database tables ready")
    
    def store_paper(self, db: Session, paper_data: Dict) -> Paper:
        """Store a single paper in the database"""
        
        # Generate ID if not provided
        if 'id' not in paper_data or not paper_data['id']:
            paper_data['id'] = f"paper_{uuid.uuid4().hex[:10]}"
        
        # Check if paper already exists
        existing_paper = db.query(Paper).filter(Paper.id == paper_data['id']).first()
        if existing_paper:
            print(f"📄 Paper already exists: {paper_data.get('title', 'Unknown')[:50]}...")
            return existing_paper
        
        # Convert date if it's a string
        published_date = paper_data.get('published_date')
        if published_date and isinstance(published_date, str):
            try:
                published_date = datetime.strptime(published_date[:10], '%Y-%m-%d').date()
            except:
                published_date = None
        
        # Handle authors - convert list to JSON string
        authors = paper_data.get('authors', [])
        if isinstance(authors, list):
            authors_str = json.dumps(authors)
        else:
            authors_str = str(authors)
        
        # Create new paper
        paper = Paper(
            id=paper_data['id'],
            title=paper_data.get('title', 'No Title'),
            abstract=paper_data.get('abstract', ''),
            authors=authors_str,
            published_date=published_date,
            citation_count=paper_data.get('citation_count', 0),
            venue=paper_data.get('venue', ''),
            source=paper_data.get('source', 'unknown'),
            pdf_url=paper_data.get('pdf_url', '')
        )
        
        db.add(paper)
        db.commit()
        db.refresh(paper)
        
        print(f"💾 Stored paper: {paper_data.get('title', 'Unknown')[:50]}...")
        return paper
    
    async def store_papers_batch(self, papers_data: List[Dict]) -> int:
        """Store multiple papers in batch with better error handling"""
        stored_count = 0
    
        # Store in smaller batches to avoid connection timeouts
        batch_size = 50
        
        for i in range(0, len(papers_data), batch_size):
            batch = papers_data[i:i + batch_size]
            batch_stored = await self._store_batch_safe(batch)
            stored_count += batch_stored
            print(f"   💾 Batch {i//batch_size + 1}: Stored {batch_stored} papers")
            
            # Small delay between batches
            await asyncio.sleep(0.5)
        
        return stored_count

    async def _store_batch_safe(self, batch: List[Dict]) -> int:
        """Store a single batch with connection recovery"""
        db = SessionLocal()
        stored_count = 0
        
        try:
            for paper_data in batch:
                try:
                    self.store_paper(db, paper_data)
                    stored_count += 1
                except Exception as e:
                    print(f"      ❌ Failed to store paper: {e}")
                    continue
            
            db.commit()
            return stored_count
            
        except Exception as e:
            print(f"❌ Batch storage error: {e}")
            db.rollback()
            return 0
        finally:
            db.close()
    def get_all_papers(self, limit: int = 100) -> List[Paper]:
        """Get all papers from database (for testing)"""
        db = SessionLocal()
        try:
            papers = db.query(Paper).limit(limit).all()
            return papers
        finally:
            db.close()