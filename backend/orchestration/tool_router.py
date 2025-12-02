# backend/orchestration/tool_router.py
"""
Routes queries to appropriate tools based on intent
Includes EXPLICIT integration with GapDetectionAgent
"""
import time
from typing import List, Dict, Any
from .models import Intent, SearchDepth, ToolResult, ConversationContext

class ToolRouter:
    """Routes queries to appropriate research tools"""
    
    def __init__(self):
        """Initialize tool router with all available agents"""
        # Import agents (lazy to avoid circular imports)
        from ai_agents.evidence_agent import EvidenceAgent
        # Note: NOT using old GapDetectionAgent - it's too simple
        # New intelligent gap detector will be created
        
        # Initialize agents
        self.evidence_agent = EvidenceAgent()
        
        print("✅ ToolRouter initialized")
        print("   - Evidence Agent (vector search)")
        print("   - Intelligent Gap Detector (coming next)")
    
    async def route(
        self, 
        intent: Intent,
        query: str,
        context: ConversationContext
    ) -> List[ToolResult]:
        """Route query to appropriate tools
        
        Args:
            intent: Detected user intent
            query: User's query string
            context: Conversation context
            
        Returns:
            List of ToolResults from executed tools
        """
        print(f"🎯 Routing query with intent: {intent.value}")
        results = []
        
        # Route based on intent
        if intent == Intent.SEARCH:
            results = await self._handle_search(query, context)
        
        elif intent == Intent.GAP_DETECTION:
            results = await self._handle_gap_detection(query, context)
        
        elif intent == Intent.EVIDENCE:
            results = await self._handle_evidence(query, context)
        
        elif intent == Intent.CITATION:
            results = await self._handle_citation(query, context)
        
        elif intent == Intent.FOLLOW_UP:
            results = await self._handle_follow_up(query, context)
        
        else:
            print(f"⚠️ Unknown intent: {intent}")
        
        return results
    
    async def _handle_search(self, query: str, context: ConversationContext) -> List[ToolResult]:
        """Handle paper search queries AND detect gaps in parallel"""
        start = time.time()
        
        try:
            # Imports
            from ml_pipeline.embedding_service import EmbeddingService
            from core.vector_search import vector_similarity_search
            from core.database import SessionLocal
            from .intelligent_gap_detector import IntelligentGapDetector
            import asyncio
            
            print(f"   🚀 Running Fast Vector Search + Gap Detection")
            
            # 1. Define Search Task
            async def run_search():
                db = SessionLocal()
                try:
                    embedding_service = EmbeddingService()
                    query_embedding = await embedding_service.encode_single(query)
                    papers_with_scores = vector_similarity_search(db, query_embedding.tolist(), limit=10)
                    
                    papers = []
                    for paper, score in papers_with_scores:
                        papers.append({
                            "id": paper.id,
                            "title": paper.title,
                            "authors": paper.authors,
                            "year": paper.published_date.year if paper.published_date else None,
                            "abstract": paper.abstract[:500] if paper.abstract else "",
                            "venue": paper.venue,
                            "citations": paper.citation_count,
                            "relevance": float(score)
                        })
                    return papers
                finally:
                    db.close()

            # 2. Define Gap Detection Task
            async def run_gaps():
                detector = IntelligentGapDetector()
                try:
                    return await detector.detect_gaps(query, max_gaps=3)
                finally:
                    detector.close()

            # 3. Run in Parallel
            results = await asyncio.gather(run_search(), run_gaps(), return_exceptions=True)
            
            papers = results[0]
            gaps = results[1]
            
            tool_results = []
            
            # Process Search Results
            if isinstance(papers, Exception):
                print(f"❌ Search error: {papers}")
                tool_results.append(ToolResult(tool_name="vector_search", success=False, error=str(papers), data=None))
            else:
                print(f"   ✅ Found {len(papers)} papers")
                tool_results.append(ToolResult(
                    tool_name="vector_search",
                    success=True,
                    data=papers,
                    execution_time=time.time() - start,
                    metadata={"count": len(papers)}
                ))

            # Process Gap Results
            if isinstance(gaps, Exception):
                print(f"❌ Gap detection error: {gaps}")
                # Don't fail the whole request if gaps fail
            else:
                print(f"   ✅ Found {len(gaps)} gaps")
                tool_results.append(ToolResult(
                    tool_name="intelligent_gap_detection",
                    success=True,
                    data=gaps,
                    execution_time=time.time() - start,
                    metadata={"count": len(gaps)}
                ))

            return tool_results

        except Exception as e:
            print(f"❌ Critical search error: {e}")
            import traceback
            traceback.print_exc()
            return [ToolResult(tool_name="vector_search", success=False, data=None, error=str(e))]
    
    async def _handle_gap_detection(self, query: str, context: ConversationContext) -> List[ToolResult]:
        """Handle gap detection using NEW intelligent Grok-based detector"""
        from .intelligent_gap_detector import IntelligentGapDetector
        
        start = time.time()
        
        try:
            # Run gap detection AND vector search in parallel
            # This ensures the UI has both "Gaps" and "Papers" populated
            print(f"   🧠 Using IntelligentGapDetector (Grok-powered) + Vector Search")
            
            detector = IntelligentGapDetector()
            
            # Create tasks
            gap_task = detector.detect_gaps(query, max_gaps=5)
            search_task = self.evidence_agent.find_evidence(query, limit=10)
            
            # Execute concurrently
            import asyncio
            results = await asyncio.gather(gap_task, search_task, return_exceptions=True)
            
            detector.close()
            
            gaps = results[0]
            papers = results[1]
            
            tool_results = []
            
            # Process gap results
            if isinstance(gaps, Exception):
                print(f"❌ Gap detection failed: {gaps}")
                tool_results.append(ToolResult(
                    tool_name="intelligent_gap_detection",
                    success=False,
                    data=None,
                    error=str(gaps)
                ))
            else:
                elapsed = time.time() - start
                tool_results.append(ToolResult(
                    tool_name="intelligent_gap_detection",
                    success=True,
                    data=gaps,
                    execution_time=elapsed,
                    metadata={"count": len(gaps)}
                ))
                
            # Process search results
            if isinstance(papers, Exception):
                print(f"❌ Search failed during gap detection: {papers}")
            else:
                tool_results.append(ToolResult(
                    tool_name="vector_search",
                    success=True,
                    data=papers,
                    execution_time=time.time() - start,
                    metadata={"count": len(papers)}
                ))
            
            return tool_results

        except Exception as e:
            print(f"❌ Intelligent gap detection error: {e}")
            import traceback
            traceback.print_exc()
            return [ToolResult(
                tool_name="intelligent_gap_detection",
                success=False,
                data=None,
                error=str(e)
            )]
    
    async def _handle_evidence(self, query: str, context: ConversationContext) -> List[ToolResult]:
        """Handle evidence finding queries"""
        start = time.time()
        
        try:
            evidence = await self.evidence_agent.find_evidence(query, limit=5)
            
            elapsed = time.time() - start
            return [ToolResult(
                tool_name="evidence_finder",
                success=True,
                data=evidence,
                execution_time=elapsed,
                metadata={"count": len(evidence)}
            )]
        except Exception as e:
            print(f"❌ Evidence error: {e}")
            return [ToolResult(
                tool_name="evidence_finder",
                success=False,
                data=None,
                error=str(e)
            )]
    
    async def _handle_citation(self, query: str, context: ConversationContext) -> List[ToolResult]:
        """Handle citation-related queries"""
        start = time.time()
        
        try:
            # Use mentioned papers from context if available
            if context.mentioned_papers:
                # Citation agent would work with these papers
                result = {"message": "Citation functionality coming soon"}
            else:
                result = {"message": "No papers mentioned yet"}
            
            elapsed = time.time() - start
            return [ToolResult(
                tool_name="citation_generator",
                success=True,
                data=result,
                execution_time=elapsed
            )]
        except Exception as e:
            return [ToolResult(
                tool_name="citation_generator",
                success=False,
                data=None,
                error=str(e)
            )]
    
    async def _handle_follow_up(self, query: str, context: ConversationContext) -> List[ToolResult]:
        """Handle follow-up questions using conversation context"""
        # Infer intent from previous conversation
        if context.current_intent:
            print(f"   📖 Following up on: {context.current_intent.value}")
            return await self.route(context.current_intent, query, context)
        else:
            # Default to search
            return await self._handle_search(query, context)
    
    def close(self):
        """Close all agent connections"""
        if hasattr(self.evidence_agent, 'close'):
            self.evidence_agent.close()
        if hasattr(self.gap_agent, 'close'):
            self.gap_agent.close()
