# backend/orchestration/response_synthesizer.py
"""
Response Synthesizer - converts tool results into natural language responses
Uses Grok AI to generate conversational, citation-rich responses
"""
from typing import List, Dict, Any
from ai_agents.grok_client import GrokClient
from .models import ConversationContext, ToolResult
from utils.citation_formatter import CitationFormatter

class ResponseSynthesizer:
    """Synthesizes natural language responses from tool results"""
    
    def __init__(self, citation_style: str = 'INLINE'):
        """
        Args:
            citation_style: Default citation style (INLINE, APA, MLA, IEEE)
        """
        self.grok = GrokClient()
        self.citation_formatter = CitationFormatter()
        self.default_style = citation_style
        
        print(f"📝 ResponseSynthesizer initialized (style: {citation_style})")
    
    async def synthesize(
        self,
        query: str,
        tool_results: List[ToolResult],
        context: ConversationContext,
        citation_style: str = None
    ) -> str:
        """Generate conversational response with inline citations
        
        Args:
            query: User's original question
            tool_results: Results from tools (papers, gaps, evidence)
            context: Conversation context
            citation_style: Override default citation style
            
        Returns:
            Natural language response with citations
        """
        style = citation_style or self.default_style
        
        print(f"\n📝 Synthesizing response...")
        print(f"   Query: {query}")
        print(f"   Tool results: {len(tool_results)}")
        print(f"   Citation style: {style}")
        
        # Build context for Grok
        conversation_summary = self._build_conversation_summary(context)
        tool_data_summary = self._build_tool_data_summary(tool_results)
        
        # Create synthesis prompt
        prompt = self._build_synthesis_prompt(
            query,
            tool_data_summary,
            conversation_summary,
            style
        )
        
        # Generate response via Grok
        try:
            response = await self.grok.generate_response(prompt)
            
            if response:
                print(f"   ✅ Generated {len(response)} character response")
                return response
            else:
                # Fallback to simple response
                return self._generate_fallback_response(query, tool_results, style)
                
        except Exception as e:
            print(f"   ❌ Synthesis error: {e}")
            return self._generate_fallback_response(query, tool_results, style)
            return self._generate_fallback_response(query, tool_results, style)

    async def synthesize_stream(
        self,
        query: str,
        tool_results: List[ToolResult],
        context: ConversationContext,
        citation_style: str = None
    ):
        """Generate streaming conversational response with inline citations"""
        style = citation_style or self.default_style
        
        print(f"\n📝 Synthesizing response (Stream)...")
        
        # Build context for Grok
        conversation_summary = self._build_conversation_summary(context)
        tool_data_summary = self._build_tool_data_summary(tool_results)
        
        # Create synthesis prompt
        prompt = self._build_synthesis_prompt(
            query,
            tool_data_summary,
            conversation_summary,
            style
        )
        
        # Generate response via Grok Stream
        try:
            async for chunk in self.grok.generate_response_stream(prompt):
                yield chunk
        except Exception as e:
            print(f"   ❌ Synthesis stream error: {e}")
            yield "Error generating response."
    def _build_conversation_summary(self, context: ConversationContext) -> str:
        """Build summary of recent conversation"""
        recent = context.get_recent_messages(3)
        
        if not recent:
            return "This is the start of the conversation."
        
        summary = []
        for msg in recent[:-1]:  # Exclude current message
            summary.append(f"- {msg.role}: {msg.content[:100]}...")
        
        if context.mentioned_topics:
            summary.append(f"- Topics discussed: {', '.join(context.mentioned_topics[:5])}")
        
        return "\n".join(summary) if summary else "No previous context."
    
    def _build_tool_data_summary(self, tool_results: List[ToolResult]) -> Dict[str, Any]:
        """Extract and summarize tool result data"""
        summary = {
            'papers': [],
            'gaps': [],
            'evidence': [],
            'other': []
        }
        
        for result in tool_results:
            if not result.success or not result.data:
                continue
            
            if result.tool_name in ['vector_search', 'evidence_finder']:
                # Extract paper data
                if isinstance(result.data, list):
                    summary['papers'].extend(result.data[:10])  # Top 10
                    
            elif result.tool_name == 'intelligent_gap_detection':
                # Extract gap data
                if isinstance(result.data, list):
                    summary['gaps'].extend(result.data)
            else:
                summary['other'].append(result.data)
        
        return summary
    
    def _build_synthesis_prompt(
        self,
        query: str,
        tool_data: Dict,
        conversation_summary: str,
        citation_style: str
    ) -> str:
        """Create prompt for Grok to synthesize response"""
        
        # Format papers for synthesis
        papers_text = ""
        if tool_data['papers']:
            papers_text = "Relevant Papers:\n"
            for i, paper in enumerate(tool_data['papers'][:10], 1):
                title = paper.get('title', 'Untitled')
                authors = paper.get('authors', 'Unknown')
                year = self.citation_formatter._extract_year(paper)
                abstract = paper.get('abstract', '')[:150] if paper.get('abstract') else ''
                
                papers_text += f"{i}. {title} ({authors}, {year})\n   {abstract}...\n"
        
        # Format gaps for synthesis
        gaps_text = ""
        if tool_data['gaps']:
            gaps_text = "\nResearch Gaps Identified:\n"
            for i, gap in enumerate(tool_data['gaps'], 1):
                gap_type = gap.get('type', 'unknown')
                description = gap.get('description', 'No description')
                importance = gap.get('importance', '')
                
                gaps_text += f"{i}. [{gap_type.upper()}] {description}\n"
                if importance:
                    gaps_text += f"   Why it matters: {importance}\n"
        
        prompt = f"""
You are a research assistant helping a researcher understand academic literature.

User's Question: "{query}"

Previous Conversation:
{conversation_summary}

{papers_text}

{gaps_text}

Task: Generate a conversational, informative response that:
1. Directly answers the user's question
2. Synthesizes insights from the papers (don't just list them)
3. Includes inline citations in {citation_style} format [Author et al., Year]
4. References the conversation context if relevant
5. If gaps were detected, explain them clearly
6. Be concise but comprehensive (2-4 paragraphs)

Format your response as natural, flowing prose - NOT bullet points or lists.
Use inline citations like: "Neural networks have revolutionized NLP [Hinton et al., 2012]."

Response:
"""
        
        return prompt
    
    def _generate_fallback_response(
        self,
        query: str,
        tool_results: List[ToolResult],
        style: str
    ) -> str:
        """Generate simple fallback response if Grok synthesis fails"""
        
        response_parts = [f"Based on my analysis of the research literature:"]
        
        # Summarize papers
        for result in tool_results:
            if result.success and result.data:
                if result.tool_name in ['vector_search', 'evidence_finder']:
                    count = len(result.data) if isinstance(result.data, list) else 0
                    response_parts.append(f"\nI found {count} relevant papers on '{query}'.")
                    
                    # Add first few papers with citations
                    if isinstance(result.data, list) and len(result.data) > 0:
                        response_parts.append("\nKey papers include:")
                        for paper in result.data[:3]:
                            citation = self.citation_formatter.format_citation(paper, 'INLINE')
                            title = paper.get('title', 'Untitled')
                            response_parts.append(f"- {title} {citation}")
                
                elif result.tool_name == 'intelligent_gap_detection':
                    gaps = result.data if isinstance(result.data, list) else []
                    if gaps:
                        response_parts.append(f"\n\nI identified {len(gaps)} research gaps:")
                        for gap in gaps[:3]:
                            desc = gap.get('description', 'No description')
                            response_parts.append(f"- {desc}")
        
        return "\n".join(response_parts)
