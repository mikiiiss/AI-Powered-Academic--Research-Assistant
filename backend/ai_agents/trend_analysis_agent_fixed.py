# backend/ai_agents/trend_analysis_agent_fixed.py
import numpy as np
from typing import List, Dict, Any
from collections import Counter, defaultdict
from datetime import datetime
from sqlalchemy.orm import Session
from core.database import SessionLocal
from api.models.database_models import Paper

class TrendAnalysisAgent:
    def __init__(self):
        self.db = SessionLocal()
    
    def get_trend_summary(self, domain: str = None) -> List[Dict[str, Any]]:
        """Get meaningful trend analysis"""
        print(f"📈 Analyzing trends for: {domain or 'Data Science & AI'}")
        
        # Get papers for analysis
        papers = self._get_domain_papers(domain)
        print(f"   Analyzing {len(papers)} papers...")
        
        if len(papers) < 10:
            # Return demo trends if not enough data
            return self._get_demo_trends(domain)
        
        # Analyze real trends
        trends = []
        
        # 1. Analyze by year
        yearly_trends = self._analyze_yearly_trends(papers)
        trends.extend(yearly_trends)
        
        # 2. Analyze by topic
        topic_trends = self._analyze_topic_trends(papers)
        trends.extend(topic_trends)
        
        # 3. Analyze by methodology
        method_trends = self._analyze_methodology_trends(papers)
        trends.extend(method_trends)
        
        return trends[:5]  # Return top 5 trends
    
    def _get_domain_papers(self, domain: str = None) -> List[Paper]:
        """Get papers for the specified domain"""
        if domain:
            # Filter by domain
            domain_lower = domain.lower()
            all_papers = self.db.query(Paper).all()
            domain_papers = [
                p for p in all_papers 
                if (p.title and domain_lower in p.title.lower()) or 
                   (p.abstract and domain_lower in p.abstract.lower())
            ]
            return domain_papers
        else:
            # Get all papers
            return self.db.query(Paper).all()
    
    def _analyze_yearly_trends(self, papers: List[Paper]) -> List[Dict]:
        """Analyze trends by publication year"""
        trends = []
        
        # Group papers by year
        yearly_counts = defaultdict(int)
        for paper in papers:
            if paper.published_date:
                year = paper.published_date.year
                yearly_counts[year] += 1
        
        if len(yearly_counts) >= 2:
            years = sorted(yearly_counts.keys())
            recent_year = years[-1]
            prev_year = years[-2] if len(years) >= 2 else years[-1] - 1
            
            recent_count = yearly_counts[recent_year]
            prev_count = yearly_counts.get(prev_year, 1)
            
            growth = (recent_count - prev_count) / prev_count
            
            if growth > 0.2:
                trends.append({
                    "id": "trend_growth",
                    "type": "rising",
                    "description": f"Rapid growth in publications ({recent_year}: {recent_count} papers, {growth:.0%} increase)",
                    "confidence": min(0.7 + growth, 0.9)
                })
            elif growth < -0.1:
                trends.append({
                    "id": "trend_decline", 
                    "type": "declining",
                    "description": f"Decline in publications ({recent_year}: {recent_count} papers)",
                    "confidence": 0.6
                })
        
        return trends
    
    def _analyze_topic_trends(self, papers: List[Paper]) -> List[Dict]:
        """Analyze trending topics"""
        trends = []
        
        # Extract topics from titles
        topics = self._extract_topics(papers)
        
        # Find rising topics (appear in recent papers)
        recent_papers = [p for p in papers if p.published_date and p.published_date.year >= 2023]
        recent_topics = self._extract_topics(recent_papers)
        
        for topic, count in topics.most_common(10):
            recent_count = recent_topics.get(topic, 0)
            total_count = count
            
            if recent_count > total_count * 0.3 and total_count >= 5:  # Appears in >30% of recent papers
                trends.append({
                    "id": f"trend_topic_{topic}",
                    "type": "emerging",
                    "description": f"Emerging topic: {topic} ({recent_count} recent papers)",
                    "confidence": min(0.6 + (recent_count / 20), 0.85)
                })
        
        return trends[:2]  # Top 2 topic trends
    
    def _analyze_methodology_trends(self, papers: List[Paper]) -> List[Dict]:
        """Analyze methodology trends"""
        trends = []
        
        methodology_keywords = {
            "deep_learning": ["neural network", "deep learning", "cnn", "rnn", "transformer"],
            "traditional_ml": ["random forest", "svm", "logistic regression", "decision tree"],
            "reinforcement": ["reinforcement learning", "q-learning", "policy gradient"],
            "generative": ["generative", "gan", "vae", "diffusion"],
            "graph": ["graph neural", "gnn", "network analysis"]
        }
        
        method_counts = {method: 0 for method in methodology_keywords}
        
        for paper in papers:
            paper_text = f"{paper.title} {paper.abstract or ''}".lower()
            for method, keywords in methodology_keywords.items():
                if any(keyword in paper_text for keyword in keywords):
                    method_counts[method] += 1
        
        total_papers = len(papers)
        if total_papers > 0:
            dominant_method = max(method_counts.items(), key=lambda x: x[1])
            if dominant_method[1] > total_papers * 0.3:  # >30% of papers
                method_name = dominant_method[0].replace('_', ' ').title()
                trends.append({
                    "id": f"trend_method_{dominant_method[0]}",
                    "type": "dominant",
                    "description": f"Dominant methodology: {method_name} ({dominant_method[1]} papers)",
                    "confidence": 0.8
                })
        
        return trends
    
    def _extract_topics(self, papers: List[Paper]) -> Counter:
        """Extract topics from paper titles"""
        common_words = {"the", "and", "for", "with", "using", "based", "learning", "model", "method"}
        
        topics = Counter()
        for paper in papers:
            if paper.title:
                words = paper.title.lower().split()
                # Filter meaningful terms
                meaningful_words = [
                    word for word in words 
                    if len(word) > 4 and word not in common_words and word.isalpha()
                ]
                topics.update(meaningful_words)
        
        return topics
    
    def _get_demo_trends(self, domain: str) -> List[Dict]:
        """Return demo trends when not enough data"""
        domain_display = domain or "Data Science & AI"
        
        return [
            {
                "id": "trend_1",
                "type": "rising",
                "description": f"Growing interest in {domain_display} research",
                "confidence": 0.8
            },
            {
                "id": "trend_2",
                "type": "emerging",
                "description": "Increased focus on explainable AI and model interpretability",
                "confidence": 0.7
            },
            {
                "id": "trend_3", 
                "type": "dominant",
                "description": "Deep learning approaches dominating recent publications",
                "confidence": 0.75
            }
        ]
    
    def close(self):
        """Close database connection"""
        self.db.close()