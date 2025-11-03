# backend/api/routes/gap_routes.py
from flask import Blueprint, request, jsonify
from ai_agents.gap_detection_agent import GapDetectionAgent

gap_bp = Blueprint('gap', __name__)

@gap_bp.route('/detect-gaps', methods=['POST'])
def detect_gaps():
    data = request.get_json()
    query = data.get('query', '')
    max_gaps = data.get('max_gaps', 5)
    
    if not query:
        return jsonify({"error": "Query is required"}), 400
    
    agent = GapDetectionAgent()
    try:
        gaps = agent.detect_research_gaps(query, max_gaps)
        return jsonify({
            "query": query,
            "gaps": gaps,
            "count": len(gaps)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        agent.close()

@gap_bp.route('/find-gaps', methods=['POST'])  # For your UI button
def find_gaps():
    data = request.get_json()
    query = data.get('query', 'general research')
    
    agent = GapDetectionAgent()
    try:
        gaps = agent.detect_research_gaps(query)
        
        # Convert to your UI format
        ui_gaps = []
        for gap in gaps:
            ui_gaps.append({
                "id": gap["id"],
                "title": gap["description"][:100] + "...",
                "whyItMatters": gap.get("reasoning", "Important research opportunity"),
                "suggestion": f"Explore this {gap['type']} gap in {query}",
                "linkedEvidenceIds": gap.get("evidence_paper_ids", []),
                "severity": "high" if gap["confidence"] > 0.8 else "medium",
                "confidence": gap["confidence"]
            })
        
        return jsonify({"gaps": ui_gaps})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        agent.close()