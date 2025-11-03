# backend/scripts/test_evidence_agent.py
#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ai_agents.evidence_agent import EvidenceAgent

def main():
    print("🧪 Testing Evidence Agent...")
    
    agent = EvidenceAgent()
    try:
        # Test with a query related to your papers
        query = "Unified token"
        evidence = agent.find_evidence(query, limit=5)
        
        print(f"📊 Results for: '{query}'")
        print(f"📄 Found {len(evidence)} evidence spans")
        
        for i, ev in enumerate(evidence, 1):
            print(f"\n{i}. {ev['sourceTitle']}")
            print(f"   Venue: {ev['venue']} • Year: {ev['year']}")
            print(f"   Citations: {ev['citations']} • Relevance: {ev['relevance']}%")
            print(f"   Quote: {ev['quote'][:200]}...")
            
    finally:
        agent.close()

if __name__ == "__main__":
    main()