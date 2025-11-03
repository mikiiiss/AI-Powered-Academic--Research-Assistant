# backend/scripts/test_recommendation_fix.py
#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ai_agents.recommendation_agent import RecommendationAgent

def debug_categorization():
    """Debug the categorization process"""
    agent = RecommendationAgent()
    try:
        # Test with a simple query
        query = "Efficient Exploration of Chemical Kinetics"
        relevant_papers = agent._get_relevant_papers(query)
        print(f"📄 Found {len(relevant_papers)} relevant papers")
        
        # Debug categorization
        categorized = agent._categorize_papers(relevant_papers, query)
        
        print("\n📊 CATEGORIZATION RESULTS:")
        for category, papers in categorized.items():
            print(f"   {category}: {len(papers)} papers")
            for paper in papers[:2]:  # Show first 2 papers per category
                relevance = agent._calculate_relevance_score(paper, query)
                print(f"      - {paper.title[:60]}... (citations: {paper.citation_count}, relevance: {relevance:.2f})")
        
        # Test final recommendations
        recommendations = agent.get_paper_recommendations(query)
        print(f"\n🎯 FINAL RECOMMENDATIONS: {len(recommendations)}")
        for rec in recommendations:
            print(f"   - [{rec['category']}] {rec['paperTitle'][:70]}...")
            
    finally:
        agent.close()

if __name__ == "__main__":
    debug_categorization()