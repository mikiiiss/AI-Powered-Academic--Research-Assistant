# backend/scripts/test_citation_agent_fast.py (FIXED)
#!/usr/bin/env python3
import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ai_agents.citation_agent import CitationAgent

def main():
    print("🕸️ Testing Citation Agent (Fixed Version)...")
    
    agent = CitationAgent()
    try:
        start_time = time.time()
        
        # Test 1: Citation network
        print("\n🔍 Test 1: Citation network for 'neural networks'")
        network = agent.build_citation_network(query="neural networks", max_nodes=8)
        
        elapsed = time.time() - start_time
        print(f"⏱️  Built in {elapsed:.2f} seconds")
        
        print(f"📊 Network: {len(network['nodes'])} nodes, {len(network['links'])} links")
        
        print("\n📈 Sample nodes:")
        for node in network['nodes'][:3]:
            print(f"   - {node['label']} ({node.get('group', 'general_ai')})")
        
        # Test 2: Paper impact - FIXED METHOD NAME
        print("\n🔍 Test 2: Paper impact")
        if network['nodes']:
            sample_paper_id = network['nodes'][0]['id']
            # Try the correct method name
            try:
                impact = agent.get_paper_citation_impact(sample_paper_id)
                print(f"📊 Paper: '{impact.get('title', 'Unknown')[:50]}...'")
                print(f"   Citations: {impact.get('total_citations', 0)}")
            except AttributeError:
                # Fallback: simple paper info
                paper = agent.db.query(Paper).filter(Paper.id == sample_paper_id).first()
                if paper:
                    print(f"📊 Paper: '{paper.title[:50]}...'")
                    print(f"   Citations: {paper.citation_count or 0}")
        
        # Test 3: Check what methods are available
        print("\n🔍 Test 3: Available methods")
        methods = [method for method in dir(agent) if not method.startswith('_')]
        print(f"   Available: {', '.join(methods[:5])}...")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        agent.close()
        print("\n✅ Citation Agent test completed!")

if __name__ == "__main__":
    main()