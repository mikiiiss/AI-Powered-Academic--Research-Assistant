# backend/api/routes/citation_routes.py
from flask import Blueprint, request, jsonify
from ai_agents.citation_agent import CitationAgent

citation_bp = Blueprint('citation', __name__)

@citation_bp.route('/build-network', methods=['POST'])
def build_network():
    data = request.get_json()
    paper_ids = data.get('paper_ids')
    query = data.get('query')
    max_nodes = data.get('max_nodes', 20)
    
    agent = CitationAgent()
    try:
        network = agent.build_citation_network(paper_ids, query, max_nodes)
        return jsonify(network)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        agent.close()

@citation_bp.route('/paper-impact/<paper_id>', methods=['GET'])
def paper_impact(paper_id):
    agent = CitationAgent()
    try:
        impact_data = agent.get_paper_citation_impact(paper_id)
        return jsonify(impact_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        agent.close()

@citation_bp.route('/influential-papers', methods=['POST'])
def influential_papers():
    data = request.get_json()
    domain = data.get('domain')
    top_k = data.get('top_k', 10)
    
    agent = CitationAgent()
    try:
        papers = agent.find_influential_papers(domain, top_k)
        return jsonify({
            "domain": domain or "all fields",
            "influential_papers": papers
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        agent.close()