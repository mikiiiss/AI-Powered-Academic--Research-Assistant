# backend/api/routes/recommendation_routes.py
from flask import Blueprint, request, jsonify
from ai_agents.recommendation_agent import RecommendationAgent

rec_bp = Blueprint('recommendation', __name__)

@rec_bp.route('/get-recommendations', methods=['POST'])
def get_recommendations():
    data = request.get_json()
    interests = data.get('interests', '')
    user_papers = data.get('user_papers', [])
    
    agent = RecommendationAgent()
    try:
        recommendations = agent.get_paper_recommendations(interests, user_papers)
        return jsonify({
            "interests": interests,
            "recommendations": recommendations,
            "count": len(recommendations)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        agent.close()

@rec_bp.route('/thesis-recommendations', methods=['POST'])
def thesis_recommendations():
    data = request.get_json()
    thesis_topic = data.get('thesis_topic', '')
    current_chapter = data.get('current_chapter')
    writing_stage = data.get('writing_stage', 'literature_review')
    
    agent = RecommendationAgent()
    try:
        recommendations = agent.get_thesis_recommendations(thesis_topic, current_chapter, writing_stage)
        return jsonify({
            "thesis_topic": thesis_topic,
            "writing_stage": writing_stage,
            "recommendations": recommendations
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        agent.close()