# backend/scripts/test_trend_agent.py
#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ai_agents.trend_analysis_agent import TrendAnalysisAgent

def main():
    print("📈 Testing Trend Analysis Agent...")
    
    agent = TrendAnalysisAgent()
    try:
        # Test 1: General trends
        print("\n🔍 Test 1: General research trends")
        trends = agent.analyze_research_trends()
        
        print("📊 RISING TOPICS:")
        for topic, data in trends["rising_topics"][:3]:
            print(f"   📈 {topic} (velocity: {data['velocity']:.1f}x)")
        
        print("\n📊 DECLINING TOPICS (but historically important):")
        for topic, data in trends["declining_topics"][:2]:
            print(f"   📉 {topic} ({data['total_citations']} total citations)")
        
        print("\n🔄 TECHNOLOGY SHIFTS:")
        for shift in trends["technology_shifts"][:2]:
            print(f"   🔄 {shift['description']} (shift ratio: {shift['shift_ratio']:.1f}x)")
        
        print(f"\n⚖️ BALANCED PERSPECTIVE:")
        print(f"   {trends['balanced_perspective']['recommendation']}")
        
        # Test 2: Domain-specific trends
        print("\n🔍 Test 2: Neural networks trends")
        domain_trends = agent.get_trend_summary("neural networks")
        
        print("📈 TREND SUMMARY:")
        for trend in domain_trends:
            print(f"   {trend['type'].upper()}: {trend['description']}")
            print(f"      Reasoning: {trend['reasoning']}")
            
    finally:
        agent.close()

if __name__ == "__main__":
    main()