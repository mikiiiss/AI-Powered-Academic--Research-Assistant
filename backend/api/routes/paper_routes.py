# backend/api/routes/paper_routes.py
from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from core.database import SessionLocal
from api.models.database_models import Paper

paper_bp = Blueprint('paper', __name__)

@paper_bp.route('/search', methods=['POST'])
def search_papers():
    """Search papers by query"""
    data = request.get_json()
    query = data.get('query', '')
    limit = data.get('limit', 10)
    
    db = SessionLocal()
    try:
        # Simple keyword search
        papers = db.query(Paper).filter(
            Paper.title.ilike(f'%{query}%') | 
            (Paper.abstract.ilike(f'%{query}%') if Paper.abstract else False)
        ).limit(limit).all()
        
        result = []
        for paper in papers:
            result.append({
                "id": paper.id,
                "sourceTitle": paper.title,
                "venue": paper.venue or "Unknown",
                "year": paper.published_date.year if paper.published_date else 2024,
                "citations": paper.citation_count or 0,
                "relevance": 85,  # Placeholder
                "quote": paper.abstract[:200] + "..." if paper.abstract else "No abstract available"
            })
        
        return jsonify({
            "query": query,
            "papers": result,
            "count": len(result)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

@paper_bp.route('/all', methods=['GET'])
def get_all_papers():
    """Get all papers"""
    db = SessionLocal()
    try:
        papers = db.query(Paper).limit(50).all()
        result = []
        for paper in papers:
            result.append({
                "id": paper.id,
                "title": paper.title,
                "venue": paper.venue,
                "year": paper.published_date.year if paper.published_date else 2024,
                "citations": paper.citation_count or 0
            })
        return jsonify({"papers": result, "count": len(result)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()