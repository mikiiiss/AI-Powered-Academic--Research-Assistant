# backend/orchestration/orchestrator_agent.py
"""
Main orchestrator agent that decides which tools to call
Uses Grok AI for intent analysis and decision-making
NEW: Includes smart MCP routing with sufficiency checking
"""
from typing import Dict, Any, List, Optional
import asyncio
import uuid
from ai_agents.grok_client import GrokClient
from .models import Intent, Message, ConversationContext, ToolResult
from .conversation_manager import ConversationManager
from .tool_router import ToolRouter

class OrchestratorAgent:
    """Central orchestrator for conversational research assistant"""
    
    def __init__(self):
        """Initialize orchestrator with all components"""
        self.grok = GrokClient()
        self.conversation_manager = ConversationManager(ttl_hours=24)
        self.tool_router = ToolRouter()
        
        # Add response synthesizer
        from .response_synthesizer import ResponseSynthesizer
        self.response_synthesizer = ResponseSynthesizer(citation_style='INLINE')
        
        # NEW: Add MCP smart routing components
        from .sufficiency_checker import SufficiencyChecker
        from .domain_classifier import DomainClassifier
        from mcp.mcp_router import MCPRouter
        
        self.sufficiency_checker = SufficiencyChecker()
        self.domain_classifier = DomainClassifier()
        self.mcp_router = MCPRouter()
        
        print("🚀 OrchestratorAgent initialized")
        print("   - Grok AI for intent analysis")
        print("   - Conversation memory (Redis)")
        print("   - Tool router (vector, gap, evidence)")
        print("   - Response synthesizer (citations + NLG)")
        print("   - MCP smart routing (arXiv, PubMed, Semantic Scholar)")
    
    async def process_query(
        self, 
        query: str,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process user query through full orchestration pipeline
        
        Args:
            query: User's question/request
            session_id: Optional session ID for conversation continuity
            
        Returns:
            Dict containing response and metadata
        """
        print(f"\n{'='*60}")
        print(f"🎯 Processing query: {query}")
        print(f"{'='*60}")
        
        # 1. Get or create session
        if not session_id:
            session_id = self.conversation_manager.create_session()
        else:
            print(f"📖 Using existing session: {session_id}")
        
        # 2. Load conversation context
        context = self.conversation_manager.get_context(session_id)
        if not context:
            print("❌ Session not found, creating new one")
            session_id = self.conversation_manager.create_session()
            context = self.conversation_manager.get_context(session_id)
        
        # 3. Add user message
        user_message = Message(role="user", content=query)
        self.conversation_manager.add_message(session_id, user_message)
        
        # 4. Analyze intent using Grok
        intent = await self._analyze_intent(query, context)
        print(f"💡 Detected intent: {intent.value}")
        
        # Update context with intent
        self.conversation_manager.set_intent(session_id, intent)
        
        # 5. Route to appropriate tools (LOCAL FIRST)
        tool_results = await self.tool_router.route(intent, query, context)
        
        # 6. SMART MCP ROUTING - Check if local results are sufficient
        local_papers = self._extract_papers_from_results(tool_results)
        
        sufficiency = self.sufficiency_checker.check_sufficiency(query, local_papers)
        print(f"   📊 Sufficiency check: {sufficiency['sufficient']} - {sufficiency['reason']}")
        
        if not sufficiency['sufficient']:
            # Local results insufficient - search external sources
            print(f"   🌐 Expanding search to external sources...")
            
            # Classify domain
            domain = self.domain_classifier.classify_domain(query, local_papers)
            
            # Search via MCP
            external_papers = await self.mcp_router.search_external(domain, query, max_results=20)
            
            if external_papers:
                # Add external papers to tool_results
                external_result = ToolResult(
                    tool_name="mcp_external_search",
                    success=True,
                    data=external_papers,
                    execution_time=0,
                    metadata={
                        "count": len(external_papers),
                        "domain": domain,
                        "source": "mcp"
                    }
                )
                tool_results.append(external_result)
                print(f"   ✅ Added {len(external_papers)} papers from external sources")
        
        # 7. Track entities (papers, gaps, topics)
        self._track_entities(session_id, tool_results, query)
        
        # 8. Synthesize natural language response with citations
        synthesized_response = await self.response_synthesizer.synthesize(
            query,
            tool_results,
            context
        )
        
        # 9. Prepare response data
        response_data = {
            "session_id": session_id,
            "query": query,
            "intent": intent.value,
            "response": synthesized_response,  # Natural language response
            "tool_results": [r.to_dict() for r in tool_results],  # Raw data
            "context": {
                "message_count": len(context.messages) + 1,
                "mentioned_papers": context.mentioned_papers,
                "mentioned_topics": context.mentioned_topics
            }
        }
        
        # 10. Add assistant response to conversation
        assistant_message = Message(
            role="assistant",
            content=synthesized_response,
            metadata={"tool_results": [r.to_dict() for r in tool_results]}
        )
        self.conversation_manager.add_message(session_id, assistant_message)
        
        return response_data

    async def process_query_stream(self, query: str, session_id: str = None):
        """
        Process user query and yield streaming events
        Yields:
            {"type": "status", "content": "..."}
            {"type": "tool_data", "data": ...}
            {"type": "token", "content": "..."}
            {"type": "done"}
        """
        if not session_id:
            session_id = str(uuid.uuid4())
            print(f"✅ Created conversation session: {session_id}")
            
        # 1. Get context
        context = self.conversation_manager.get_context(session_id)
        
        # 2. Analyze intent
        yield {"type": "status", "content": "Analyzing intent..."}
        intent = await self._analyze_intent(query, context)
        yield {"type": "status", "content": f"Intent detected: {intent.value}"}
        
        # 3. Route to tools
        yield {"type": "status", "content": "Searching research database..."}
        
        # Run tools concurrently and yield results as they complete
        # We need to manually run the tools instead of using tool_router.route blocking call
        
        # Get tool plan from router
        # For now, we manually execute the standard plan: Vector Search + Gap Detection (if applicable)
        
        pending_tasks = []
        
        # 1. Vector Search (Fast)
        task_search = asyncio.create_task(self.tool_router._handle_search(query, context))
        pending_tasks.append(task_search)
        
        # 2. Gap Detection (Slow) - only if intent suggests it or we want it always
        # The original route method ran it for SEARCH intent too
        if intent == Intent.SEARCH or intent == Intent.GAP_ANALYSIS:
             task_gaps = asyncio.create_task(self.tool_router._handle_gap_detection(query, context))
             pending_tasks.append(task_gaps)
             
        tool_results = []
        
        # Wait for tasks as they complete
        for completed_task in asyncio.as_completed(pending_tasks):
            try:
                result = await completed_task
                if result:
                    tool_results.append(result)
                    # Yield this specific result immediately
                    yield {"type": "tool_data", "data": [result.to_dict()]}
                    
                    if result.tool_name == "vector_search":
                        yield {"type": "status", "content": f"Found {len(result.data)} papers. Analyzing gaps..."}
            except Exception as e:
                print(f"❌ Tool execution error: {e}")
        
        # 4. Check sufficiency (if search)
        if intent == Intent.SEARCH:
            is_sufficient, reason = self.sufficiency_checker.check(query, tool_results)
            if not is_sufficient:
                yield {"type": "status", "content": "Local results insufficient, checking external sources..."}
                # Search external
                domain = await self.domain_classifier.classify(query)
                external_papers = await self.mcp_router.search_external(domain, query, max_results=20)
                if external_papers:
                    external_result = ToolResult(
                        tool_name="mcp_external_search",
                        success=True,
                        data=external_papers,
                        execution_time=0,
                        metadata={"source": "mcp"}
                    )
                    tool_results.append(external_result)
                    yield {"type": "tool_data", "data": [external_result.to_dict()]}
        
        # 5. Track entities
        self._track_entities(session_id, tool_results, query)
        
        # 6. Emit tool results to UI
        yield {"type": "tool_data", "data": [r.to_dict() for r in tool_results]}
        
        # 7. Synthesize response (Stream)
        yield {"type": "status", "content": "Synthesizing response..."}
        
        full_response = ""
        async for chunk in self.response_synthesizer.synthesize_stream(query, tool_results, context):
            full_response += chunk
            yield {"type": "token", "content": chunk}
            
        # 8. Save to history
        assistant_message = Message(
            role="assistant",
            content=full_response,
            metadata={"tool_results": [r.to_dict() for r in tool_results]}
        )
        self.conversation_manager.add_message(session_id, assistant_message)
        
        yield {"type": "done", "session_id": session_id}
        print(f"✅ Query processed successfully")
        print(f"{'='*60}\n")
        

    
    async def _analyze_intent(
        self,
        query: str,
        context: ConversationContext
    ) -> Intent:
        """Analyze user query to determine intent using Grok"""
        
        # OPTIMIZATION: Quick pattern-based check for obvious queries
        # This skips the 5-10s Grok API call for common patterns
        quick_intent = self._quick_intent_check(query)
        if quick_intent:
            print(f"   ⚡ Quick intent detected: {quick_intent.value} (skipped Grok)")
            return quick_intent
        
        # Build context for Grok
        recent_messages = context.get_recent_messages(3)
        conversation_history = "\n".join([
            f"{msg.role}: {msg.content}" 
            for msg in recent_messages
        ]) if recent_messages else "No previous conversation"
        
        # Build prompt for Grok
        prompt = f"""
You are an intent classifier for a research assistant. Analyze the user's query and determine their intent.

Conversation History:
{conversation_history}

Current Topics: {', '.join(context.mentioned_topics) if context.mentioned_topics else 'None'}

User Query: "{query}"

Available Intents:
1. SEARCH - User wants to find papers on a topic
2. GAP_DETECTION - User wants to identify research gaps  
3. EVIDENCE - User wants supporting evidence/quotes for a claim
4. CITATION - User wants citations/references
5. CHAT_WITH_PAPER - User wants to ask about a specific paper
6. SYNTHESIS - User wants a literature review or synthesis
7. FOLLOW_UP - User is continuing previous conversation

Return ONLY the intent name (e.g., "SEARCH" or "GAP_DETECTION"). No explanation.
"""
        
        try:
            response = await self.grok.generate_response(prompt)
            
            if response:
                intent_str = response.strip().upper()
                
                try:
                    intent = Intent[intent_str]
                    print(f"   🤖 Grok classified as: {intent.value}")
                    return intent
                except KeyError:
                    print(f"   ⚠️ Unknown intent: {intent_str}, defaulting to SEARCH")
                    return Intent.SEARCH
            else:
                print("   ⚠️ No response from Grok, defaulting to SEARCH")
                return Intent.SEARCH
                
        except Exception as e:
            print(f"   ❌ Intent analysis error: {e}, defaulting to SEARCH")
            return Intent.SEARCH
    
    def _quick_intent_check(self, query: str) -> Optional[Intent]:
        """Quick pattern-based intent detection to skip Grok API calls
        
        Returns Intent if pattern matches, None if Grok analysis needed
        """
        query_lower = query.lower()
        
        # Search patterns (most common)
        search_patterns = ['find', 'search', 'show me', 'get', 'what is', 'tell me about', 
                          'papers on', 'research on', 'studies about', 'look for']
        if any(pattern in query_lower for pattern in search_patterns):
            return Intent.SEARCH
        
        # Gap detection patterns
        gap_patterns = ['gap', 'missing', 'unexplored', 'understudied', 'opportunity',
                       'what\'s missing', 'what is missing', 'research opportunity']
        if any(pattern in query_lower for pattern in gap_patterns):
            return Intent.GAP_DETECTION
        
        # Evidence patterns
        evidence_patterns = ['evidence for', 'support for', 'prove', 'quote', 'citation for']
        if any(pattern in query_lower for pattern in evidence_patterns):
            return Intent.EVIDENCE
        
        # Citation patterns
        citation_patterns = ['cite', 'reference', 'bibliography', 'apa', 'mla']
        if any(pattern in query_lower for pattern in citation_patterns):
            return Intent.CITATION
        
        return None  # Use Grok for complex/ambiguous queries
    
    def _track_entities(
        self,
        session_id: str,
        tool_results: List[ToolResult],
        query: str
    ):
        """Track entities (papers, gaps, topics) from tool results"""
        # Extract topics from query
        topic_keywords = query.lower().split()
        for keyword in topic_keywords:
            if len(keyword) > 4:
                self.conversation_manager.track_topic(session_id, keyword)
        
        # Track entities from tool_results
        for result in tool_results:
            if result.success and result.data:
                # Track papers
                if result.tool_name in ["vector_search", "mcp_external_search"] and isinstance(result.data, list):
                    for item in result.data[:5]:
                        if hasattr(item, 'get') and 'id' in item:
                            paper_id = item.get('id') or item.get('paper_id')
                            if paper_id:
                                self.conversation_manager.track_paper(session_id, str(paper_id))
                
                # Track gaps
                if result.tool_name == "gap_detection" and isinstance(result.data, list):
                    for gap in result.data:
                        self.conversation_manager.track_gap(session_id, gap)
    
    def _extract_papers_from_results(self, tool_results: List[ToolResult]) -> List:
        """Extract papers from tool results for sufficiency checking"""
        papers = []
        
        for result in tool_results:
            if result.success and result.data and isinstance(result.data, list):
                if result.tool_name in ['vector_search', 'evidence_finder', 'mcp_external_search']:
                    # Convert dicts to simple objects with required attributes
                    for item in result.data:
                        if isinstance(item, dict):
                            # Create a simple object with the needed attributes
                            class PaperLike:
                                def __init__(self, data):
                                    self.id = data.get('id')
                                    self.title = data.get('title', data.get('sourceTitle', ''))
                                    self.published_date = None
                                    self.citation_count = data.get('citations', data.get('citation_count', 0))
                                    self.venue = data.get('venue')
                                    
                                    # Try to parse year
                                    year = data.get('year')
                                    if year:
                                        from datetime import datetime
                                        self.published_date = type('obj', (object,), {'year': year})()
                            
                            papers.append(PaperLike(item))
        
        return papers
    
    def close(self):
        """Close all connections"""
        if hasattr(self.tool_router, 'close'):
            self.tool_router.close()
