# backend/orchestration/intelligent_gap_detector.py
"""
NEW Intelligent Gap Detector using Grok AI
Based on AnswerThis and SciSpace approaches:
- Semantic synthesis across multiple papers
- Contradiction detection
- Missing connection identification
- Temporal gap analysis
"""
from typing import List, Dict, Any
from ai_agents.grok_client import GrokClient
from core.database import SessionLocal
from api.models.database_models import Paper
import numpy as np
from datetime import datetime, timedelta

class IntelligentGapDetector:
    """Advanced gap detection using Grok AI and semantic analysis"""
    
    def __init__(self):
        self.grok = GrokClient()
        self.db = SessionLocal()
        print("🧠 IntelligentGapDetector initialized")
    
    async def detect_gaps(self, query: str, max_gaps: int = 5) -> List[Dict[str, Any]]:
        """Detect research gaps using multiple intelligent strategies
        
        Args:
            query: Research topic/question
            max_gaps: Maximum number of gaps to return
            
        Returns:
            List of detected gaps with evidence
        """
        print(f"\n🔍 Detecting research gaps for: '{query}'")
        print("   Using intelligent multi-strategy analysis...")
        
        # 1. Get relevant papers (use vector search)
        from core.vector_search import vector_similarity_search
        from ml_pipeline.embedding_service import EmbeddingService
        
        embedding_service = EmbeddingService()
        # Properly await the async method
        query_embedding = await embedding_service.encode_single(query)
        
        # Get top 20 papers for comprehensive analysis (reduced from 50 for speed)
        papers_with_scores = vector_similarity_search(
            self.db, 
            query_embedding.tolist(), 
            limit=20
        )
        papers = [paper for paper, score in papers_with_scores]
        
        print(f"   📚 Analyzing {len(papers)} relevant papers")
        
        if not papers:
            return []
        
        # Run multiple gap detection strategies in parallel
        gaps = []
        
        # Strategy 1: Semantic Synthesis (Grok-powered) - FAST
        semantic_gaps = await self._detect_semantic_gaps(query, papers[:15])
        gaps.extend(semantic_gaps)
        
        # NOTE: Other strategies commented out for performance
        # Each Grok call takes ~5-10 seconds, running all 4 = 20-40 seconds
        # Enable these for deeper analysis when needed:
        
        # # Strategy 2: Contradiction Detection
        # contradiction_gaps = await self._detect_contradictions(query, papers[:20])
        # gaps.extend(contradiction_gaps)
        
        # # Strategy 3: Missing Connections - DISABLED FOR SPEED
        # connection_gaps = await self._detect_missing_connections(query, papers[:30])
        # gaps.extend(connection_gaps)
        
        # Strategy 4: Temporal Analysis (fast, no API call)
        temporal_gaps = self._detect_temporal_gaps(query, papers)
        gaps.extend(temporal_gaps)
        
        # Deduplicate and rank
        unique_gaps = self._deduplicate_gaps(gaps)
        ranked_gaps = self._rank_gaps(unique_gaps)
        
        # Fallback if no gaps found
        if not ranked_gaps:
            print("   ⚠️ No specific gaps found, adding general research opportunity")
            ranked_gaps.append({
                "type": "general",
                "title": "Underexplored Intersection",
                "description": f"While individual aspects of '{query}' are studied, comprehensive integration of recent findings remains limited.",
                "importance": "Opportunity for systematic review or meta-analysis",
                "confidence": 0.6
            })
        
        print(f"   ✅ Detected {len(ranked_gaps)} unique gaps")
        
        return ranked_gaps[:max_gaps]
    
    async def _detect_semantic_gaps(self, query: str, papers: List[Paper]) -> List[Dict]:
        """Use Grok to identify semantic gaps through synthesis"""
        print("   🎯 Strategy 1: Semantic synthesis...")
        
        # Build paper summaries for Grok
        paper_summaries = []
        for i, paper in enumerate(papers[:15], 1):  # Top 15 for synthesis
            year = paper.published_date.year if paper.published_date else 'N/A'
            abstract = paper.abstract[:200] if paper.abstract else 'No abstract'
            summary = f"{i}. {paper.title} ({year})\n   {abstract}..."
            paper_summaries.append(summary)
        
        prompt = f"""
Analyze these research papers on "{query}" and identify SEMANTIC GAPS - areas that are understudied or missing from current research.

Papers:
{chr(10).join(paper_summaries)}

Identify 2-3 semantic gaps by finding:
1. Topics mentioned across papers but never deeply explored
2. Methodologies that could be applied but haven't been
3. Perspectives or domains that are underrepresented

For each gap, provide:
- Gap description (1 sentence)
- Why it's important
- Evidence from papers

Format as JSON:
[
  {{
    "type": "semantic",
    "description": "...",
    "importance": "...",
    "evidence": ["paper title 1", "paper title 2"]
  }}
]
"""
        
        try:
            response = await self.grok.generate_response(prompt)
            if response:
                import json
                gap_json = self._extract_json(response)
                if gap_json:
                    return gap_json
        except Exception as e:
            print(f"      ⚠️ Semantic gap detection error: {e}")
        
        return []
    
    async def _detect_contradictions(self, query: str, papers: List[Paper]) -> List[Dict]:
        """Detect contradictory findings between papers"""
        print("   🎯 Strategy 2: Contradiction detection...")
        
        # Build claims from papers
        paper_claims = []
        for i, paper in enumerate(papers[:10], 1):
            abstract = paper.abstract[:150] if paper.abstract else 'No abstract'
            claim = f"{i}. {paper.title} - Key finding: {abstract}..."
            paper_claims.append(claim)
        
        prompt = f"""
Analyze these research papers on "{query}" and identify CONTRADICTIONS - conflicting findings or claims.

Papers:
{chr(10).join(paper_claims)}

Find 1-2 contradictions where papers make conflicting claims about:
- Effectiveness of methods
- Performance metrics
- Theoretical assumptions
- Experimental results

For each contradiction, provide:
- Description of the contradiction
- Which papers conflict
- Why this matters (research gap opportunity)

Format as JSON:
[
  {{
    "type": "contradiction",
    "description": "...",
    "conflicting_papers": ["paper 1", "paper 2"],
    "importance": "..."
  }}
]
"""
        
        try:
            response = await self.grok.generate_response(prompt)
            if response:
                gap_json = self._extract_json(response)
                if gap_json:
                    return gap_json
        except Exception as e:
            print(f"      ⚠️ Contradiction detection error: {e}")
        
        return []
    
    async def _detect_missing_connections(self, query: str, papers: List[Paper]) -> List[Dict]:
        """Identify concepts that should be connected but aren't"""
        print("   🎯 Strategy 3: Missing connections...")
        
        # Extract key concepts from papers
        concepts = set()
        for paper in papers[:20]:
            # Simple concept extraction (can be enhanced with NLP)
            words = paper.title.lower().split()
            concepts.update([w for w in words if len(w) > 5])
        
        prompt = f"""
Research topic: "{query}"

Key concepts appearing in literature: {', '.join(list(concepts)[:20])}

Identify 1-2 MISSING CONNECTIONS - combinations of concepts that SHOULD be studied together but aren't.

For example:
- "X is studied, Y is studied, but X+Y combination is unexplored"
- "Method A works for domain B, domain C exists, but A hasn't been applied to C"

Format as JSON:
[
  {{
    "type": "missing_connection",
    "description": "Connection between X and Y is unexplored",
    "concepts": ["X", "Y"],
    "importance": "..."
  }}
]
"""
        
        try:
            response = await self.grok.generate_response(prompt)
            if response:
                gap_json = self._extract_json(response)
                if gap_json:
                    return gap_json
        except Exception as e:
            print(f"      ⚠️ Missing connection detection error: {e}")
        
        return []
    
    def _detect_temporal_gaps(self, query: str, papers: List[Paper]) -> List[Dict]:
        """Identify topics that were popular but are now neglected"""
        print("   🎯 Strategy 4: Temporal analysis...")
        
        # Analyze paper distribution over time
        recent_cutoff = datetime.now().year - 2
        old_cutoff = datetime.now().year - 5
        
        recent_papers = [p for p in papers if p.published_date and p.published_date.year >= recent_cutoff]
        old_papers = [p for p in papers if p.published_date and old_cutoff <= p.published_date.year < recent_cutoff]
        
        if len(old_papers) > len(recent_papers) * 2:
            # Topic was more active in the past
            return [{
                "type": "temporal",
                "description": f"Research on '{query}' has declined recently",
                "importance": f"Was active {old_cutoff}-{recent_cutoff} ({len(old_papers)} papers) but only {len(recent_papers)} papers in last 2 years",
                "evidence": []
            }]
        
        return []
    
    def _extract_json(self, text: str) -> List[Dict]:
        """Extract JSON from Grok response"""
        import json
        import re
        
        # Try to find JSON array in response
        json_match = re.search(r'\[.*\]', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except:
                pass
        return []
    
    def _deduplicate_gaps(self, gaps: List[Dict]) -> List[Dict]:
        """Remove duplicate gaps"""
        unique = []
        seen_descriptions = set()
        
        for gap in gaps:
            desc = gap.get('description', '').lower()
            if desc and desc not in seen_descriptions:
                seen_descriptions.add(desc)
                unique.append(gap)
        
        return unique
    
    def _rank_gaps(self, gaps: List[Dict]) -> List[Dict]:
        """Rank gaps by importance and type"""
        # Priority order: contradiction > semantic > missing_connection > temporal
        priority = {
            'contradiction': 4,
            'semantic': 3,
            'missing_connection': 2,
            'temporal': 1
        }
        
        gaps.sort(key=lambda g: priority.get(g.get('type', ''), 0), reverse=True)
        return gaps
    
    def close(self):
        """Close database connection"""
        if self.db:
            self.db.close()
