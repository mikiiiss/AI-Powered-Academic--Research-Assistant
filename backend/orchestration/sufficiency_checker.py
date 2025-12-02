# backend/orchestration/sufficiency_checker.py
"""
Checks if local search results are sufficient or if external MCP search is needed
"""
from typing import List, Dict, Any
from datetime import datetime
from api.models.database_models import Paper


class SufficiencyChecker:
    """Determines if local database results are sufficient for a query"""
    
    def __init__(self):
        self.min_papers_default = 5
        self.min_papers_comprehensive = 20
        self.recency_threshold_years = 2
    
    def check_sufficiency(
        self, 
        query: str, 
        local_papers: List[Paper],
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Check if local results are sufficient
        
        Args:
            query: User's search query
            local_papers: Papers found in local database
            context: Optional conversation context
            
        Returns:
            {
                'sufficient': bool,
                'reason': str,
                'recommended_action': str,
                'metrics': dict
            }
        """
        query_lower = query.lower()
        paper_count = len(local_papers)
        
        # Calculate metrics
        metrics = {
            'local_count': paper_count,
            'newest_year': self._get_newest_year(local_papers),
            'oldest_year': self._get_oldest_year(local_papers),
            'avg_citations': self._get_avg_citations(local_papers)
        }
        
        # Rule 1: Minimum count check
        if paper_count == 0:
            return {
                'sufficient': False,
                'reason': 'No papers found in local database',
                'recommended_action': 'external_search',
                'metrics': metrics
            }
        
        if paper_count < self.min_papers_default:
            return {
                'sufficient': False,
                'reason': f'Only {paper_count} papers found locally, need at least {self.min_papers_default} for quality analysis',
                'recommended_action': 'external_search',
                'metrics': metrics
            }
        
        # Rule 2: Recency check for time-sensitive queries
        recency_keywords = ['latest', 'recent', 'new', 'current', '2024', '2025', 'state-of-the-art', 'sota']
        if any(keyword in query_lower for keyword in recency_keywords):
            current_year = datetime.now().year
            newest_year = metrics['newest_year']
            
            if newest_year and (current_year - newest_year) > self.recency_threshold_years:
                return {
                    'sufficient': False,
                    'reason': f'Query requests recent papers but newest local paper is from {newest_year} (>{self.recency_threshold_years} years old)',
                    'recommended_action': 'external_search',
                    'metrics': metrics
                }
        
        # Rule 3: Comprehensive review requirement
        comprehensive_keywords = ['comprehensive', 'survey', 'review', 'systematic review', 'meta-analysis', 'overview']
        if any(keyword in query_lower for keyword in comprehensive_keywords):
            if paper_count < self.min_papers_comprehensive:
                return {
                    'sufficient': False,
                    'reason': f'Comprehensive review requested but only {paper_count} papers found (need {self.min_papers_comprehensive}+)',
                    'recommended_action': 'external_search',
                    'metrics': metrics
                }
        
        # Rule 4: Specific year range check
        if '2024' in query_lower or '2025' in query_lower:
            if not newest_year or newest_year < 2024:
                return {
                    'sufficient': False,
                    'reason': f'Query specifies 2024/2025 but no papers from those years in local database',
                    'recommended_action': 'external_search',
                    'metrics': metrics
                }
        
        # All checks passed - local results are sufficient
        return {
            'sufficient': True,
            'reason': f'Found {paper_count} relevant papers locally with good coverage',
            'recommended_action': 'use_local',
            'metrics': metrics
        }
    
    def _get_newest_year(self, papers: List[Paper]) -> int:
        """Get the newest publication year from papers"""
        years = [p.published_date.year for p in papers if p.published_date]
        return max(years) if years else None
    
    def _get_oldest_year(self, papers: List[Paper]) -> int:
        """Get the oldest publication year from papers"""
        years = [p.published_date.year for p in papers if p.published_date]
        return min(years) if years else None
    
    def _get_avg_citations(self, papers: List[Paper]) -> float:
        """Get average citation count"""
        citations = [p.citation_count for p in papers if p.citation_count]
        return sum(citations) / len(citations) if citations else 0.0
