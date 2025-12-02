# backend/ai_agents/gap_detection_agent.py
import numpy as np
import json
import hashlib
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from core.database import SessionLocal
from api.models.database_models import Paper, PaperRelationship
from knowledge_graph.graph_builder import KnowledgeGraphBuilder
from core.cache import cache_manager
from .grok_client import GrokClient

class GapDetectionAgent:
    def __init__(self):
        self.kg_builder = KnowledgeGraphBuilder()
        self.db = SessionLocal()
        self.grok = GrokClient()
        self.cache = cache_manager
    
    def detect_research_gaps(self, query: str, max_gaps: int = 5) -> List[Dict[str, Any]]:
        """Detect research gaps using multiple analysis strategies (with caching)"""
        print(f"🎯 Detecting research gaps for: {query}")
        
        # Check cache first
        cache_key = f"gaps:{hashlib.md5(f'{query}:{max_gaps}'.encode()).hexdigest()}"
        cached_result = self.cache.get_cached(cache_key)
        if cached_result:
            return cached_result
        
        # Get relevant papers for the query
        relevant_papers = self._get_relevant_papers(query)
        print(f"   Analyzing {len(relevant_papers)} relevant papers...")
        
        gaps = []
        
        # Multiple gap detection strategies
        strategies = [
            self._analyze_citation_gaps,
            self._analyze_temporal_gaps,
            self._analyze_venue_gaps,
            self._analyze_methodological_gaps,
            self._analyze_semantic_gaps
        ]
        
        for strategy in strategies:
            try:
                strategy_gaps = strategy(relevant_papers, query)
                gaps.extend(strategy_gaps)
                print(f"   ✅ {strategy.__name__}: found {len(strategy_gaps)} gaps")
            except Exception as e:
                print(f"   ❌ {strategy.__name__} failed: {e}")
        
        # Remove duplicates and sort by confidence
        unique_gaps = self._deduplicate_gaps(gaps)
        unique_gaps.sort(key=lambda x: x["confidence"], reverse=True)
        
        print(f"   📊 Total unique gaps found: {len(unique_gaps)}")
        final_result = unique_gaps[:max_gaps]
        
        # Cache the result for 2 hours
        self.cache.set_cached(cache_key, final_result, ttl=7200)
        
        return final_result
    
    def _get_relevant_papers(self, query: str, limit: int = 20) -> List[Paper]:
        """Get papers relevant to the query"""
        # Use fresh DB session
        db = SessionLocal()
        try:
            # Use simple keyword matching for now - can enhance with embeddings
            all_papers = db.query(Paper).all()
            
            scored_papers = []
            for paper in all_papers:
                score = self._calculate_query_relevance(paper, query)
                if score > 0.1:
                    scored_papers.append((paper, score))
            
            scored_papers.sort(key=lambda x: x[1], reverse=True)
            return [paper for paper, score in scored_papers[:limit]]
        finally:
            db.close()
    
    def _calculate_query_relevance(self, paper: Paper, query: str) -> float:
        """Calculate relevance between paper and query"""
        query_lower = query.lower()
        paper_text = f"{paper.title} {paper.abstract or ''}".lower()
        
        # Simple keyword matching
        query_words = set(query_lower.split())
        paper_words = set(paper_text.split())
        
        if not query_words:
            return 0
            
        intersection = query_words.intersection(paper_words)
        return len(intersection) / len(query_words)
    
    def _analyze_citation_gaps(self, papers: List[Paper], query: str) -> List[Dict[str, Any]]:
        """Find gaps in citation networks"""
        gaps = []
        
        if not papers:
            return gaps
            
        # Analyze citation patterns
        highly_cited = [p for p in papers if (p.citation_count or 0) > 10]
        lowly_cited = [p for p in papers if (p.citation_count or 0) <= 5]
        
        if len(lowly_cited) > len(highly_cited) * 0.5 and len(lowly_cited) > 3:
            gaps.append({
                "id": f"gap_citation_{len(gaps)}",
                "type": "citation",
                "description": f"Many recent papers in '{query}' have low citation counts ({len(lowly_cited)} papers with ≤5 citations), suggesting under-explored areas",
                "confidence": 0.75,
                "reasoning": "Low citation counts may indicate emerging or niche areas that haven't gained widespread attention",
                "evidence_paper_ids": [p.id for p in lowly_cited[:3]]
            })
        
        # Check for citation concentration
        if highly_cited:
            avg_citations = sum(p.citation_count or 0 for p in highly_cited) / len(highly_cited)
            if avg_citations > 50:
                gaps.append({
                    "id": f"gap_citation_concentration_{len(gaps)}",
                    "type": "citation",
                    "description": f"High citation concentration in '{query}' (average {avg_citations:.0f} citations for top papers), suggesting dominant approaches that need challenging",
                    "confidence": 0.7,
                    "reasoning": "Highly concentrated citations may indicate established paradigms that could benefit from alternative approaches",
                    "evidence_paper_ids": [p.id for p in highly_cited[:2]]
                })
        
        return gaps
    
    def _analyze_temporal_gaps(self, papers: List[Paper], query: str) -> List[Dict[str, Any]]:
        """Find temporal gaps in research"""
        gaps = []
        
        if not papers:
            return gaps
            
        # Analyze publication years
        years = [p.published_date.year for p in papers if p.published_date]
        if years:
            recent_years = [y for y in years if y >= 2023]
            older_years = [y for y in years if y < 2020]
            
            recent_ratio = len(recent_years) / len(years) if years else 0
            
            if recent_ratio > 0.7:
                gaps.append({
                    "id": f"gap_temporal_{len(gaps)}",
                    "type": "temporal",
                    "description": f"Recent surge in '{query}' research ({(recent_ratio)*100:.0f}% papers since 2023), suggesting emerging field with rapid development",
                    "confidence": 0.8,
                    "reasoning": "High recent publication rate indicates active research area with opportunities for early contributions",
                    "evidence_paper_ids": [p.id for p in papers if p.published_date and p.published_date.year >= 2023][:3]
                })
            elif recent_ratio < 0.3 and len(older_years) > 5:
                gaps.append({
                    "id": f"gap_temporal_decline_{len(gaps)}",
                    "type": "temporal", 
                    "description": f"Declining research in '{query}' (only {(recent_ratio)*100:.0f}% papers since 2023), suggesting potential for revival with new approaches",
                    "confidence": 0.65,
                    "reasoning": "Declining publication rate may indicate saturated approaches or abandoned directions worth revisiting",
                    "evidence_paper_ids": [p.id for p in papers if p.published_date and p.published_date.year < 2020][:3]
                })
        
        return gaps
    
    def _analyze_venue_gaps(self, papers: List[Paper], query: str) -> List[Dict[str, Any]]:
        """Enhanced venue analysis for more diverse gaps"""
        gaps = []
        
        if not papers:
            return gaps
            
        # Analyze publication venues
        venue_counts = {}
        for paper in papers:
            venue = paper.venue or "Unknown"
            venue_counts[venue] = venue_counts.get(venue, 0) + 1
        
        # Find venue diversity gaps
        total_papers = len(papers)
        if total_papers > 0:
            dominant_venue = max(venue_counts, key=venue_counts.get)
            dominant_percentage = (venue_counts[dominant_venue] / total_papers) * 100
            
            if dominant_percentage > 60 and dominant_venue != "Unknown":
                gaps.append({
                    "id": f"gap_venue_{len(gaps)}",
                    "type": "publication",
                    "description": f"Research on '{query}' is concentrated in {dominant_venue} ({dominant_percentage:.0f}% of papers), lacking venue diversity",
                    "confidence": 0.7,
                    "reasoning": "Venue concentration may indicate narrow disciplinary focus and opportunities for cross-community engagement",
                    "evidence_paper_ids": [p.id for p in papers if p.venue == dominant_venue][:3]
                })
            
            # Check for underrepresented high-impact venues
            high_impact_venues = ["Nature", "Science", "PNAS", "NeurIPS", "ICML", "ICLR"]
            for venue in high_impact_venues:
                if venue not in venue_counts and total_papers > 10:
                    gaps.append({
                        "id": f"gap_venue_impact_{len(gaps)}",
                        "type": "publication",
                        "description": f"No papers from high-impact venue '{venue}' in '{query}' research, suggesting opportunity for broader impact",
                        "confidence": 0.6,
                        "reasoning": f"Absence from {venue} may indicate need for more generalizable or high-impact contributions",
                        "evidence_paper_ids": [p.id for p in papers[:2]]  # General evidence
                    })
                    break
        
        return gaps
    
    def _analyze_semantic_gaps(self, papers: List[Paper], query: str) -> List[Dict[str, Any]]:
        """Find gaps in semantic clusters"""
        gaps = []
        
        if not papers:
            return gaps
            
        # Group papers by key terms in titles
        key_terms = self._extract_key_terms(papers)
        
        # Look for missing combinations of terms
        if len(key_terms) >= 3:
            # Simple approach: look for term pairs that don't co-occur
            term_pairs = []
            for i, term1 in enumerate(key_terms[:5]):
                for term2 in key_terms[i+1:5]:
                    if not self._check_term_cooccurrence(papers, term1, term2):
                        term_pairs.append((term1, term2))
            
            if term_pairs and len(term_pairs) <= 3:  # Limit to most promising
                for term1, term2 in term_pairs[:2]:
                    gaps.append({
                        "id": f"gap_semantic_{len(gaps)}",
                        "type": "conceptual",
                        "description": f"Missing research combining '{term1}' and '{term2}' in '{query}' domain",
                        "confidence": 0.65,
                        "reasoning": f"Combining {term1} and {term2} approaches could lead to novel insights",
                        "evidence_paper_ids": [p.id for p in papers if term1 in p.title.lower() or term2 in p.title.lower()][:2]
                    })
        
        return gaps
    
    def _extract_key_terms(self, papers: List[Paper]) -> List[str]:
        """Extract key terms from paper titles"""
        # Simple term extraction - can be enhanced
        common_words = {"the", "and", "for", "with", "using", "based", "via", "towards", "toward"}
        all_terms = []
        
        for paper in papers:
            if paper.title:
                terms = paper.title.lower().split()
                # Filter out common words and keep meaningful terms
                meaningful_terms = [term for term in terms if len(term) > 3 and term not in common_words]
                all_terms.extend(meaningful_terms)
        
        # Count term frequency and return top terms
        from collections import Counter
        term_counts = Counter(all_terms)
        return [term for term, count in term_counts.most_common(10)]
    
    def _check_term_cooccurrence(self, papers: List[Paper], term1: str, term2: str) -> bool:
        """Check if two terms co-occur in any paper titles"""
        for paper in papers:
            if paper.title and term1 in paper.title.lower() and term2 in paper.title.lower():
                return True
        return False
    
    def _analyze_methodological_gaps(self, papers: List[Paper], query: str) -> List[Dict[str, Any]]:
        """Use Grok to analyze methodological gaps"""
        if not papers:
            return []
        
        # Prepare paper summaries for Grok analysis
        paper_summaries = []
        for paper in papers[:8]:  # Limit to avoid token limits
            summary = f"Title: {paper.title}\nAbstract: {paper.abstract or 'No abstract'}\nVenue: {paper.venue or 'Unknown'}"
            paper_summaries.append(summary)
        
        papers_text = "\n\n".join(paper_summaries)
        
        prompt = f"""
        Analyze these research papers in the field of "{query}" and identify 2-3 specific research gaps.
        
        PAPERS:
        {papers_text}
        
        Focus on identifying:
        - Missing methodological approaches
        - Unexplored application areas  
        - Technical limitations that need addressing
        - Opportunities for cross-disciplinary methods
        - Under-explored combinations of techniques
        
        Return ONLY a JSON array with this exact structure:
        [
          {{
            "type": "methodology|application|technical|cross_domain",
            "description": "Specific, actionable gap description here",
            "confidence": 0.85,
            "reasoning": "Brief explanation of why this gap is important and promising"
          }}
        ]
        
        Make the gaps specific and actionable for researchers.
        """
        
        system_message = "You are an expert research analyst specializing in identifying research gaps. Return only valid JSON, no other text."
        
        response = self.grok.generate_response(prompt, system_message)
        if not response:
            return []
            
        try:
            # Clean and parse response
            cleaned = response.strip()
            if cleaned.startswith('```json'):
                cleaned = cleaned[7:]
            if cleaned.endswith('```'):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            
            gaps = json.loads(cleaned)
            # Validate and enhance gaps
            validated_gaps = []
            for i, gap in enumerate(gaps):
                if all(key in gap for key in ['type', 'description', 'confidence', 'reasoning']):
                    gap["id"] = f"gap_grok_{i}"
                    gap["evidence_paper_ids"] = [p.id for p in papers[:2]]
                    validated_gaps.append(gap)
            
            return validated_gaps
        except Exception as e:
            print(f"   ❌ Grok gap analysis failed: {e}")
            print(f"   Raw response: {response}")
            return []
    
    def _deduplicate_gaps(self, gaps: List[Dict]) -> List[Dict]:
        """Remove duplicate gaps based on description similarity"""
        unique_gaps = []
        seen_descriptions = set()
        
        for gap in gaps:
            # Simple deduplication - can be enhanced with semantic similarity
            desc_key = gap["description"][:80].lower()  # First 80 chars as key
            if desc_key not in seen_descriptions:
                seen_descriptions.add(desc_key)
                unique_gaps.append(gap)
        
        return unique_gaps
    
    def detect_gaps_for_ui(self, query: str = "general research") -> List[Dict[str, Any]]:
        """Detect gaps formatted for the React UI"""
        gaps = self.detect_research_gaps(query)
        
        # Convert to UI format
        ui_gaps = []
        for gap in gaps:
            ui_gaps.append({
                "id": gap["id"],
                "title": gap["description"][:100] + ("..." if len(gap["description"]) > 100 else ""),
                "whyItMatters": gap.get("reasoning", "Important research opportunity with high potential impact"),
                "suggestion": f"Explore this {gap['type']} gap through novel approaches or cross-disciplinary methods",
                "linkedEvidenceIds": gap.get("evidence_paper_ids", []),
                "severity": "high" if gap["confidence"] > 0.8 else "medium",
                "confidence": gap["confidence"]
            })
        
        return ui_gaps
    
    def close(self):
        """Close database connection"""
        self.db.close()