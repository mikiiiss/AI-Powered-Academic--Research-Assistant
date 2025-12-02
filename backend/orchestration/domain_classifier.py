# backend/orchestration/domain_classifier.py
"""
Classifies research domain to route to appropriate MCP server
"""
from typing import List
from api.models.database_models import Paper


class DomainClassifier:
    """Classifies research queries into domains for MCP routing"""
    
    def __init__(self):
        # Define domain keywords
        self.domain_keywords = {
            'medical': [
                'cancer', 'disease', 'treatment', 'clinical', 'drug', 'patient',
                'therapy', 'medical', 'medicine', 'hospital', 'diagnosis', 'symptom',
                'health', 'pharmaceutical', 'vaccine', 'virus', 'bacteria', 'infection',
                'surgery', 'gene', 'protein', 'dna', 'rna', 'biology', 'biomedical'
            ],
            'tech': [
                'neural', 'algorithm', 'machine learning', 'ai', 'artificial intelligence',
                'software', 'deep learning', 'computer', 'programming', 'data',
                'network', 'system', 'model', 'training', 'optimization', 'transformer',
                'cnn', 'rnn', 'nlp', 'computer vision', 'reinforcement learning',
                'classification', 'regression', 'clustering', 'prediction'
            ],
            'physics': [
                'quantum', 'particle', 'cosmology', 'physics', 'relativity',
                'gravity', 'magnetism', 'thermodynamics', 'mechanics', 'optics',
                'atomic', 'nuclear', 'photon', 'electron', 'energy', 'field theory'
            ]
        }
        
        # Venue patterns for secondary classification
        self.venue_patterns = {
            'medical': ['medical', 'clinical', 'medicine', 'health', 'jama', 'nejm', 'lancet', 'bmj'],
            'tech': ['neurips', 'icml', 'iclr', 'cvpr', 'acl', 'emnlp', 'aaai', 'ijcai', 'ieee', 'acm'],
            'physics': ['physical review', 'physics', 'astrophysics', 'quantum']
        }
    
    def classify_domain(self, query: str, local_papers: List[Paper] = None) -> str:
        """
        Classify research domain
        
        Args:
            query: User's search query
            local_papers: Optional list of papers from local search
            
        Returns:
            Domain: 'medical', 'tech', 'physics', or 'general'
        """
        query_lower = query.lower()
        
        # Primary classification: Keyword matching
        domain_scores = {
            'medical': 0,
            'tech': 0,
            'physics': 0
        }
        
        # Score each domain based on keyword matches
        for domain, keywords in self.domain_keywords.items():
            for keyword in keywords:
                if keyword in query_lower:
                    # Weight multi-word keywords higher
                    weight = len(keyword.split())
                    domain_scores[domain] += weight
        
        # Secondary classification: Analyze local paper venues (if available)
        if local_papers:
            venue_scores = self._classify_by_venues(local_papers)
            # Combine scores (keyword = 70%, venue = 30%)
            for domain in domain_scores:
                domain_scores[domain] = (
                    0.7 * domain_scores[domain] + 
                    0.3 * venue_scores.get(domain, 0)
                )
        
        # Find highest scoring domain
        if domain_scores:
            max_score = max(domain_scores.values())
            if max_score > 0:
                best_domain = max(domain_scores, key=domain_scores.get)
                print(f"   🏷️ Domain scores: {domain_scores}")
                print(f"   🎯 Classified as: {best_domain}")
                return best_domain
        
        # Default to general if no clear domain
        print(f"   🏷️ No clear domain detected, using 'general'")
        return 'general'
    
    def _classify_by_venues(self, papers: List[Paper]) -> dict:
        """Classify based on paper venues"""
        venue_scores = {
            'medical': 0,
            'tech': 0,
            'physics': 0
        }
        
        for paper in papers:
            if not paper.venue:
                continue
                
            venue_lower = paper.venue.lower()
            
            for domain, patterns in self.venue_patterns.items():
                for pattern in patterns:
                    if pattern in venue_lower:
                        venue_scores[domain] += 1
                        break
        
        return venue_scores
