# backend/api/routes/evidence_routes.py
from flask import Blueprint, request, jsonify
import asyncio
from ai_agents.evidence_agent import EvidenceAgent

evidence_bp = Blueprint('evidence', __name__)

@evidence_bp.route('/find-evidence', methods=['POST'])
def find_evidence():
    data = request.get_json()
    query = data.get('query', '')
    limit = data.get('limit', 10)
    
    if not query:
        return jsonify({"error": "Query is required"}), 400
    
    agent = EvidenceAgent()
    try:
        # Run async method in sync context
        evidence = asyncio.run(agent.find_evidence(query, limit))
        return jsonify({
            "query": query,
            "evidence": evidence,
            "count": len(evidence)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        agent.close()