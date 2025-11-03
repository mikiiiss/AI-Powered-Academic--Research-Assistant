# backend/scripts/test_gap_agent.py
#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ai_agents.gap_detection_agent import GapDetectionAgent

def main():
    print("🎯 Testing Gap Detection Agent with Grok...")
    
    agent = GapDetectionAgent()
    try:
        # Test with various queries
        test_queries = [
            "quaternion neural networks",
            "audio classification", 
            "spiking neural networks",
            "legal document analysis"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Analyzing: '{query}'")
            gaps = agent.detect_research_gaps(query, max_gaps=3)
            
            print(f"📊 Found {len(gaps)} research gaps:")
            for i, gap in enumerate(gaps, 1):
                print(f"   {i}. [{gap['type'].upper()}] {gap['description']}")
                print(f"      Confidence: {gap['confidence']:.2f}")
                if 'reasoning' in gap:
                    print(f"      Reasoning: {gap['reasoning'][:100]}...")
                
    finally:
        agent.close()

if __name__ == "__main__":
    main()