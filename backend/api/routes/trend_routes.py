# # backend/api/routes/trend_routes.py
# from flask import Blueprint, request, jsonify
# from ai_agents.trend_analysis_agent import TrendAnalysisAgent

# trend_bp = Blueprint('trend', __name__)

# @trend_bp.route('/analyze-trends', methods=['POST'])
# def analyze_trends():
#     data = request.get_json()
#     domain = data.get('domain')
#     time_window = data.get('time_window', 5)
    
#     agent = TrendAnalysisAgent()
#     try:
#         trends = agent.analyze_research_trends(domain, time_window)
#         return jsonify({
#             "domain": domain or "all fields",
#             "trends": trends
#         })
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
#     finally:
#         agent.close()

# @trend_bp.route('/trend-summary', methods=['POST'])
# def trend_summary():
#     data = request.get_json()
#     domain = data.get('domain')
    
#     agent = TrendAnalysisAgent()
#     try:
#         summary = agent.get_trend_summary(domain)
#         return jsonify({
#             "domain": domain or "all fields", 
#             "trends": summary
#         })
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
#     finally:
#         agent.close()


# backend/api/routes/trend_routes.py  
from flask import Blueprint, request, jsonify
from ai_agents.trend_analysis_agent_fixed import TrendAnalysisAgent  # Use fixed version

trend_bp = Blueprint('trend', __name__)

@trend_bp.route('/trend-summary', methods=['POST'])
def trend_summary():
    data = request.get_json()
    domain = data.get('domain')
    
    agent = TrendAnalysisAgent()
    try:
        trends = agent.get_trend_summary(domain)
        return jsonify({"trends": trends})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        agent.close()