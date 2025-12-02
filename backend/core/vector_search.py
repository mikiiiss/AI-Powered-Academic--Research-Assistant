# backend/core/vector_search.py
"""
Vector similarity search utilities for semantic paper matching
"""
from typing import List, Tuple
from sqlalchemy import func
from api.models.database_models import Paper
import numpy as np

def cosine_distance_sql(embedding1: List[float], embedding2_column):
    """Calculate cosine distance in SQL using PostgreSQL operations
    
    Note: This is a Python-side implementation until pgvector extension is enabled.
    Returns a similarity score where higher = more similar.
    """
    # For now, this will be computed Python-side
    # When pgvector is enabled, this becomes a simple SQL function
    return None

def vector_similarity_search(db_session, query_embedding: List[float], limit: int = 10) -> List[Tuple[Paper, float]]:
    """Search for papers using vector similarity
    
    Args:
        db_session: SQLAlchemy database session
        query_embedding: Query embedding vector
        limit: Maximum number of results
        
    Returns:
        List of (Paper, similarity_score) tuples, sorted by similarity
    """
    # Get all papers with embeddings
    papers = db_session.query(Paper).filter(
        Paper.title_embedding.isnot(None)
    ).all()
    
    if not papers:
        return []
    
    # Calculate similarities in Python (until pgvector is ready)
    query_vec = np.array(query_embedding)
    similarities = []
    
    for paper in papers:
        if not paper.title_embedding:
            continue
            
        paper_vec = np.array(paper.title_embedding)
        
        # Cosine similarity
        dot_product = np.dot(query_vec, paper_vec)
        norm_query = np.linalg.norm(query_vec)
        norm_paper = np.linalg.norm(paper_vec)
        
        if norm_query > 0 and norm_paper > 0:
            similarity = dot_product / (norm_query * norm_paper)
            similarities.append((paper, float(similarity)))
    
    # Sort by similarity (highest first)
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    return similarities[:limit]
