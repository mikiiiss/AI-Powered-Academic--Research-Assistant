# backend/api/routes/chat_routes.py
"""
Chat API routes for conversational research assistant
Integrates OrchestratorAgent with Flask for UI access
"""
from flask import Blueprint, request, jsonify, Response
import asyncio
import json
from orchestration import OrchestratorAgent

chat_bp = Blueprint('chat', __name__)

# Global orchestrator instance (created once)
orchestrator = None

def get_orchestrator():
    """Get or create orchestrator instance"""
    global orchestrator
    if orchestrator is None:
        orchestrator = OrchestratorAgent()
    return orchestrator

@chat_bp.route('/chat', methods=['POST'])
def chat():
    """
    Main conversational endpoint
    
    Request Body:
    {
        "query": "What is neural network?",
        "session_id": "optional-session-id"
    }
    
    Response:
    {
        "session_id": "uuid",
        "query": "What is neural network?",
        "intent": "search",
        "response": "Natural language response with citations...",
        "context": {
            "message_count": 2,
            "mentioned_papers": [...],
            "mentioned_topics": [...]
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                'error': 'Missing required field: query'
            }), 400
        
        query = data['query']
        session_id = data.get('session_id')
        
        # Get orchestrator
        orch = get_orchestrator()
        
        # Process query (run async function in sync context)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            orch.process_query(query, session_id)
        )
        loop.close()
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"❌ Chat API error: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'error': str(e),
            'message': 'An error occurred processing your query'
        }), 500


@chat_bp.route('/chat/stream', methods=['POST'])
def chat_stream():
    """
    Streaming conversational endpoint (SSE)
    """
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({'error': 'Missing required field: query'}), 400
        
        query = data['query']
        session_id = data.get('session_id')
        
        orch = get_orchestrator()
        
        def generate():
            # Create a new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            async def run_stream():
                async for event in orch.process_query_stream(query, session_id):
                    yield json.dumps(event) + "\n"
            
            # Run the async generator
            # Since we can't yield from run_until_complete, we iterate manually
            gen = run_stream()
            try:
                while True:
                    # Run next(gen) in the loop
                    chunk = loop.run_until_complete(gen.__anext__())
                    yield chunk
            except StopAsyncIteration:
                pass
            finally:
                loop.close()

        return Response(generate(), mimetype='application/x-ndjson')
        
    except Exception as e:
        print(f"❌ Stream API error: {e}")
        return jsonify({'error': str(e)}), 500
@chat_bp.route('/chat/history/<session_id>', methods=['GET'])
def get_history(session_id):
    """
    Get conversation history for a session
    
    Response:
    {
        "session_id": "uuid",
        "messages": [
            {
                "role": "user",
                "content": "...",
                "timestamp": "..."
            }
        ],
        "mentioned_papers": [...],
        "mentioned_topics": [...]
    }
    """
    try:
        from orchestration import ConversationManager
        
        cm = ConversationManager()
        context = cm.get_context(session_id)
        
        if not context:
            return jsonify({
                'error': 'Session not found'
            }), 404
        
        return jsonify({
            'session_id': context.session_id,
            'messages': [msg.to_dict() for msg in context.messages],
            'mentioned_papers': context.mentioned_papers,
            'mentioned_topics': context.mentioned_topics,
            'created_at': context.created_at.isoformat(),
            'last_active': context.last_active.isoformat()
        }), 200
        
    except Exception as e:
        print(f"❌ History API error: {e}")
        return jsonify({
            'error': str(e)
        }), 500

@chat_bp.route('/chat/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    """
    Delete a conversation session
    
    Response:
    {
        "success": true,
        "message": "Session deleted"
    }
    """
    try:
        from orchestration import ConversationManager
        
        cm = ConversationManager()
        success = cm.delete_session(session_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Session deleted'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Session not found or could not be deleted'
            }), 404
        
    except Exception as e:
        print(f"❌ Delete API error: {e}")
        return jsonify({
            'error': str(e)
        }), 500

@chat_bp.route('/chat/sessions', methods=['GET'])
def list_sessions():
    """
    List active conversation sessions
    
    Response:
    {
        "sessions": ["session-id-1", "session-id-2"],
        "count": 2
    }
    """
    try:
        from orchestration import ConversationManager
        
        cm = ConversationManager()
        hours = request.args.get('hours', 24, type=int)
        sessions = cm.list_active_sessions(hours=hours)
        
        return jsonify({
            'sessions': sessions,
            'count': len(sessions)
        }), 200
        
    except Exception as e:
        print(f"❌ Sessions API error: {e}")
        return jsonify({
            'error': str(e)
        }), 500
