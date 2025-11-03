# backend/ai_agents/trend_analysis_agent.py
import numpy as np
from typing import List, Dict, Any, Tuple
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from core.database import SessionLocal
from api.models.database_models import Paper
from .grok_client import GrokClient

class TrendAnalysisAgent:
    def __init__(self):
        self.db = SessionLocal()
        self.grok = GrokClient()
    
    def analyze_research_trends(self, 
                              domain: str = None,
                              time_window: int = 5) -> Dict[str, Any]:
        """Analyze research trends in a domain"""
        print(f"📈 Analyzing research trends for: {domain or 'all fields'}")
        
        # Get papers for analysis
        papers = self._get_domain_papers(domain)
        print(f"   Analyzing {len(papers)} papers from last {time_window} years")
        
        trends = {
            "rising_topics": self._detect_rising_topics(papers, time_window),
            "declining_topics": self._detect_declining_topics(papers, time_window),
            "emerging_methods": self._detect_emerging_methods(papers),
            "technology_shifts": self._detect_technology_shifts(papers),
            "citation_velocity": self._analyze_citation_velocity(papers),
            "balanced_perspective": self._provide_balanced_perspective(papers, domain)
        }
        
        return trends
    
    def get_trend_summary(self, domain: str = None) -> List[Dict[str, Any]]:
        """Get trend summary formatted for UI"""
        trends = self.analyze_research_trends(domain)
        
        summary = []
        
        # Rising trends
        for topic, data in trends["rising_topics"][:3]:
            summary.append({
                "id": f"rising_{len(summary)}",
                "type": "rising",
                "description": f"Rising: {topic}",
                "velocity": data["velocity"],
                "reasoning": f"Growing interest with {data['papers_2024']} recent papers",
                "confidence": min(data["velocity"] * 0.2, 0.9)
            })
        
        # Declining trends  
        for topic, data in trends["declining_topics"][:2]:
            summary.append({
                "id": f"declining_{len(summary)}",
                "type": "declining", 
                "description": f"Declining: {topic}",
                "velocity": data["velocity"],
                "reasoning": f"Decreasing focus, but {data['total_citations']} total citations show historical importance",
                "confidence": 0.7
            })
        
        # Emerging methods
        for method in trends["emerging_methods"][:2]:
            summary.append({
                "id": f"emerging_{len(summary)}",
                "type": "emerging",
                "description": f"Emerging: {method}",
                "velocity": 0.8,
                "reasoning": "New methodological approach gaining attention",
                "confidence": 0.75
            })
        
        return summary
    
    def _get_domain_papers(self, domain: str = None) -> List[Paper]:
        """Get papers for the specified domain"""
        all_papers = self.db.query(Paper).all()
        
        if not domain:
            return all_papers
        
        # Filter papers by domain
        domain_papers = []
        for paper in all_papers:
            if self._is_paper_in_domain(paper, domain):
                domain_papers.append(paper)
        
        return domain_papers
    
    def _is_paper_in_domain(self, paper: Paper, domain: str) -> bool:
        """Check if paper belongs to domain"""
        domain_terms = domain.lower().split()
        paper_text = f"{paper.title} {paper.abstract or ''}".lower()
        
        return any(term in paper_text for term in domain_terms)
    
    def _detect_rising_topics(self, papers: List[Paper], time_window: int) -> List[Tuple[str, Dict]]:
        """Detect topics with rising popularity"""
        # Extract topics from titles and abstracts
        topics = self._extract_topics(papers)
        
        rising_topics = []
        for topic, years in topics.items():
            if len(years) >= 3:  # Need enough data points
                recent_count = len([y for y in years if y >= 2023])
                older_count = len([y for y in years if y < 2023])
                
                if older_count > 0:
                    velocity = recent_count / older_count
                    if velocity > 2.0 and recent_count >= 3:  # Doubled and at least 3 recent papers
                        rising_topics.append((topic, {
                            "velocity": velocity,
                            "papers_2024": len([y for y in years if y >= 2024]),
                            "total_papers": len(years)
                        }))
        
        return sorted(rising_topics, key=lambda x: x[1]["velocity"], reverse=True)
    
    def _detect_declining_topics(self, papers: List[Paper], time_window: int) -> List[Tuple[str, Dict]]:
        """Detect topics with declining interest but historical importance"""
        topics = self._extract_topics(papers)
        
        declining_topics = []
        for topic, years in topics.items():
            if len(years) >= 5:  # Established topic
                recent_count = len([y for y in years if y >= 2023])
                peak_count = max([years.count(y) for y in set(years)]) if years else 0
                
                if recent_count < peak_count * 0.3 and peak_count >= 5:  # Declined to 30% of peak
                    # Calculate total citations for historical importance
                    topic_papers = [p for p in papers if topic in p.title.lower() or (p.abstract and topic in p.abstract.lower())]
                    total_citations = sum(p.citation_count or 0 for p in topic_papers)
                    
                    if total_citations > 50:  # Historically important
                        declining_topics.append((topic, {
                            "velocity": recent_count / peak_count,
                            "peak_year": max(set(years), key=years.count) if years else 0,
                            "total_citations": total_citations
                        }))
        
        return sorted(declining_topics, key=lambda x: x[1]["total_citations"], reverse=True)
    
    def _detect_emerging_methods(self, papers: List[Paper]) -> List[str]:
        """Detect emerging methodological approaches"""
        # Look for papers with novel methods mentioned
        method_terms = ["novel", "new method", "propose", "introduce", "framework", "architecture"]
        
        emerging_methods = []
        for paper in papers:
            if paper.published_date and paper.published_date.year >= 2024:
                paper_text = f"{paper.title} {paper.abstract or ''}".lower()
                if any(term in paper_text for term in method_terms):
                    # Extract the method description
                    for sentence in (paper.abstract or '').split('.')[:3]:
                        if any(term in sentence.lower() for term in method_terms):
                            emerging_methods.append(sentence.strip())
                            break
        
        return list(set(emerging_methods))[:5]  # Return unique methods
    
    def _detect_technology_shifts(self, papers: List[Paper]) -> List[Dict[str, Any]]:
        """Detect shifts from older to newer technologies"""
        # Common technology shifts in AI/ML
        shifts = [
            {"from": "cnn", "to": "transformer", "description": "Convolutional to Transformer architectures"},
            {"from": "lstm", "to": "attention", "description": "RNN/LSTM to Attention mechanisms"},
            {"from": "svm", "to": "neural network", "description": "Traditional ML to Neural Networks"},
            {"from": "random forest", "to": "gradient boosting", "description": "Ensemble method evolution"},
        ]
        
        detected_shifts = []
        for shift in shifts:
            from_count = len([p for p in papers if shift["from"] in (p.title or '').lower() or 
                            (p.abstract and shift["from"] in p.abstract.lower())])
            to_count = len([p for p in papers if shift["to"] in (p.title or '').lower() or 
                          (p.abstract and shift["to"] in p.abstract.lower())])
            
            if to_count > from_count * 1.5 and from_count > 10:  # Significant shift
                detected_shifts.append({
                    "description": shift["description"],
                    "from_count": from_count,
                    "to_count": to_count,
                    "shift_ratio": to_count / from_count
                })
        
        return sorted(detected_shifts, key=lambda x: x["shift_ratio"], reverse=True)
    
    def _analyze_citation_velocity(self, papers: List[Paper]) -> Dict[str, Any]:
        """Analyze citation patterns and velocity"""
        if not papers:
            return {}
        
        # Group by year
        yearly_citations = defaultdict(list)
        for paper in papers:
            if paper.published_date:
                year = paper.published_date.year
                yearly_citations[year].append(paper.citation_count or 0)
        
        # Calculate average citations per year
        avg_citations = {}
        for year, citations in yearly_citations.items():
            avg_citations[year] = sum(citations) / len(citations) if citations else 0
        
        # Calculate citation velocity (change from previous year)
        years = sorted(avg_citations.keys())
        velocity = {}
        for i in range(1, len(years)):
            current_year = years[i]
            prev_year = years[i-1]
            if avg_citations[prev_year] > 0:
                velocity[current_year] = (avg_citations[current_year] - avg_citations[prev_year]) / avg_citations[prev_year]
        
        return {
            "average_citations": dict(avg_citations),
            "citation_velocity": dict(velocity),
            "fastest_growing_year": max(velocity.items(), key=lambda x: x[1]) if velocity else None
        }
    
    def _provide_balanced_perspective(self, papers: List[Paper], domain: str) -> Dict[str, Any]:
        """Provide balanced perspective on established vs new work"""
        # Separate established vs recent work
        established = [p for p in papers if p.published_date and p.published_date.year < 2020]
        recent = [p for p in papers if p.published_date and p.published_date.year >= 2022]
        
        # Calculate impact metrics
        established_impact = sum((p.citation_count or 0) for p in established) / len(established) if established else 0
        recent_impact = sum((p.citation_count or 0) for p in recent) / len(recent) if recent else 0
        
        return {
            "established_work": {
                "count": len(established),
                "avg_citations": established_impact,
                "description": f"Well-cited foundational work ({len(established)} papers, avg {established_impact:.1f} citations)"
            },
            "recent_work": {
                "count": len(recent), 
                "avg_citations": recent_impact,
                "description": f"Emerging directions ({len(recent)} papers, avg {recent_impact:.1f} citations)"
            },
            "recommendation": self._generate_balance_recommendation(established_impact, recent_impact, domain)
        }
    
    def _generate_balance_recommendation(self, established_impact: float, recent_impact: float, domain: str) -> str:
        """Generate recommendation for balancing established vs new work"""
        if established_impact > recent_impact * 3:
            return f"While new approaches in {domain} are emerging, established work has significantly higher impact. Consider building on well-cited foundations while exploring recent innovations."
        elif recent_impact > established_impact * 2:
            return f"Recent work in {domain} shows high impact, suggesting rapid evolution. Focus on state-of-the-art while understanding foundational principles."
        else:
            return f"{domain} shows balanced evolution. Both established and recent work contribute significantly to the field."
    
    def _extract_topics(self, papers: List[Paper]) -> Dict[str, List[int]]:
        """Extract topics and their publication years"""
        # Simple topic extraction from titles - can be enhanced
        common_words = {"the", "and", "for", "with", "using", "based", "via", "towards", "method", "approach", "learning"}
        
        topics = defaultdict(list)
        for paper in papers:
            if paper.title and paper.published_date:
                words = paper.title.lower().split()
                # Filter meaningful terms (nouns, adjectives)
                meaningful_terms = [word for word in words if len(word) > 4 and word not in common_words]
                
                for term in meaningful_terms[:3]:  # Take top 3 terms per paper
                    topics[term].append(paper.published_date.year)
        
        return dict(topics)
    
    def close(self):
        """Close database connection"""
        self.db.close()