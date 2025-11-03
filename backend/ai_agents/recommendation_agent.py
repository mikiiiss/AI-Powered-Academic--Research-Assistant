# backend/ai_agents/recommendation_agent.py
import numpy as np
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from core.database import SessionLocal
from api.models.database_models import Paper, PaperRelationship
from knowledge_graph.graph_builder import KnowledgeGraphBuilder
from .grok_client import GrokClient

class RecommendationAgent:
    def __init__(self):
        self.kg_builder = KnowledgeGraphBuilder()
        self.db = SessionLocal()
        self.grok = GrokClient()
    
    def get_paper_recommendations(self, 
                                user_interests: str,
                                user_papers: List[str] = None,
                                max_recommendations: int = 4) -> List[Dict[str, Any]]:
        """Get personalized paper recommendations like Anora.com"""
        print(f"📚 Getting recommendations for: {user_interests}")
        
        # Get relevant papers
        relevant_papers = self._get_relevant_papers(user_interests, user_papers)
        print(f"   Found {len(relevant_papers)} relevant papers")
        
        # Categorize papers into must-read and recommended
        categorized = self._categorize_papers(relevant_papers, user_interests)
        
        # Balance the recommendations
        balanced_recommendations = self._balance_recommendations(categorized, max_recommendations)
        
        return balanced_recommendations
    
    def get_thesis_recommendations(self, 
                                 thesis_topic: str,
                                 current_chapter: str = None,
                                 writing_stage: str = "literature_review") -> List[Dict[str, Any]]:
        """Get recommendations tailored for thesis writing"""
        print(f"🎓 Getting thesis recommendations for: {thesis_topic}")
        
        # Stage-specific recommendations
        if writing_stage == "literature_review":
            focus = "foundational papers, review articles, seminal works"
        elif writing_stage == "methodology":
            focus = "technical papers, methodology comparisons, implementation details"
        elif writing_stage == "discussion":
            focus = "recent advances, controversial papers, future directions"
        else:
            focus = "comprehensive coverage"
        
        query = f"{thesis_topic} {focus}"
        if current_chapter:
            query += f" for {current_chapter} chapter"
        
        return self.get_paper_recommendations(query, max_recommendations=6)
    
    def _get_relevant_papers(self, interests: str, user_papers: List[str] = None) -> List[Paper]:
        """Get papers relevant to user interests"""
        all_papers = self.db.query(Paper).all()
        
        scored_papers = []
        for paper in all_papers:
            # Skip papers user already has if provided
            if user_papers and paper.id in user_papers:
                continue
                
            score = self._calculate_relevance_score(paper, interests)
            if score > 0.2:  # Higher threshold for recommendations
                scored_papers.append((paper, score))
        
        scored_papers.sort(key=lambda x: x[1], reverse=True)
        return [paper for paper, score in scored_papers[:50]]  # Get more for categorization
    
    def _calculate_relevance_score(self, paper: Paper, interests: str) -> float:
        """Calculate comprehensive relevance score"""
        interests_lower = interests.lower()
        paper_text = f"{paper.title} {paper.abstract or ''}".lower()
        
        # Keyword matching
        interest_words = set(interests_lower.split())
        paper_words = set(paper_text.split())
        if not interest_words:
            keyword_score = 0.5  # Default score if no specific interests
        else:
            intersection = interest_words.intersection(paper_words)
            keyword_score = len(intersection) / len(interest_words)
        
        # Citation impact (normalized)
        citation_score = min((paper.citation_count or 0) / 50, 1.0)
        
        # Recency bonus (papers from last 2 years)
        recency_score = 0
        if paper.published_date and paper.published_date.year >= 2023:
            recency_score = 0.4
        
        # Venue prestige
        venue_score = 0.3 if paper.venue and any(venue in (paper.venue or '') for venue in 
                                                ['NeurIPS', 'ICML', 'ICLR', 'CVPR', 'ACL', 'Nature', 'Science']) else 0
        
        return (0.3 * keyword_score + 0.3 * citation_score + 0.3 * recency_score + 0.1 * venue_score)
    
    def _categorize_papers(self, papers: List[Paper], interests: str) -> Dict[str, List[Paper]]:
        """Categorize papers into must-read and recommended"""
        categorized = {
            "must_read": [],
            "recommended": [],
            "foundational": [],
            "recent_advances": []
        }
        
        for paper in papers:
            # Must-read criteria: high citations + high relevance
            citation_count = paper.citation_count or 0
            relevance = self._calculate_relevance_score(paper, interests)
            
            if citation_count > 20 and relevance > 0.5  or relevance > 0.8:
                categorized["must_read"].append(paper)
            elif citation_count > 50:  # Seminal papers regardless of exact relevance
                categorized["foundational"].append(paper)
            elif paper.published_date and paper.published_date.year >= 2023 and relevance > 0.4:
                categorized["recent_advances"].append(paper)
            elif relevance > 0.3:
                categorized["recommended"].append(paper)
        
        return categorized
    
    def _balance_recommendations(self, categorized: Dict[str, List[Paper]], max_count: int) -> List[Dict[str, Any]]:
        """Create balanced recommendation bundles - MORE FLEXIBLE"""
        recommendations = []
        
        # Prioritize must-read papers
        for paper in categorized["must_read"][:max_count]:
            recommendations.append(self._format_recommendation(paper, "must_read", "Highly relevant to your research interests"))
        
        # If we still need more, add foundational
        if len(recommendations) < max_count and categorized["foundational"]:
            for paper in categorized["foundational"][:max_count-len(recommendations)]:
                recommendations.append(self._format_recommendation(paper, "foundational", "Seminal paper that shaped the field"))
        
        # If we still need more, add recent advances
        if len(recommendations) < max_count and categorized["recent_advances"]:
            for paper in categorized["recent_advances"][:max_count-len(recommendations)]:
                recommendations.append(self._format_recommendation(paper, "recent", "Latest advances and state-of-the-art"))
        
        # If we STILL need more, add any recommended papers
        if len(recommendations) < max_count and categorized["recommended"]:
            for paper in categorized["recommended"][:max_count-len(recommendations)]:
                recommendations.append(self._format_recommendation(paper, "recommended", "Relevant paper in your research area"))
        
        # LAST RESORT: If no papers met criteria, return the most relevant ones anyway
        if len(recommendations) == 0 and categorized["recommended"]:
            for paper in categorized["recommended"][:max_count]:
                recommendations.append(self._format_recommendation(paper, "recommended", "Most relevant papers found"))
        
        return recommendations
    
    def _format_recommendation(self, paper: Paper, category: str, reason: str) -> Dict[str, Any]:
        """Format paper into recommendation object"""
        return {
            "id": f"rec_{paper.id}",
            "paper_id": paper.id,
            "paperTitle": paper.title,
            "category": category,
            "reason": reason,
            "citations": paper.citation_count or 0,
            "year": paper.published_date.year if paper.published_date else 2024,
            "venue": paper.venue or "Unknown",
            "relevance": int(self._calculate_relevance_score(paper, "") * 100),
            "reading_time": self._estimate_reading_time(paper),
            "key_insights": self._extract_key_insights(paper)
        }
    
    def _estimate_reading_time(self, paper: Paper) -> str:
        """Estimate reading time based on abstract length"""
        if not paper.abstract:
            return "5-10 min"
        
        word_count = len(paper.abstract.split())
        if word_count < 200:
            return "5-10 min"
        elif word_count < 500:
            return "10-15 min"
        else:
            return "15-20 min"
    
    def _extract_key_insights(self, paper: Paper) -> List[str]:
        """Extract key insights from paper using Grok"""
        if not paper.abstract:
            return ["No abstract available"]
        
        prompt = f"""
        Extract 2-3 key insights or contributions from this research paper:
        
        TITLE: {paper.title}
        ABSTRACT: {paper.abstract}
        
        Return ONLY a JSON array of insight strings. Be concise and focus on novel contributions.
        Example: ["Proposes new method for X", "Achieves state-of-the-art on Y", "Introduces novel dataset Z"]
        """
        
        response = self.grok.generate_response(prompt)
        if response:
            try:
                import json
                insights = json.loads(response.strip())
                return insights if isinstance(insights, list) else [str(insights)]
            except:
                pass
        
        # Fallback: simple extraction from abstract
        return [paper.abstract[:100] + "..." if len(paper.abstract) > 100 else paper.abstract]
    
    def close(self):
        """Close database connection"""
        self.db.close()