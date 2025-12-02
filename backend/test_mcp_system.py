# backend/test_mcp_system.py
"""
Comprehensive test for MCP smart routing system
"""
import asyncio
import sys


async def test_mcp_system():
    """Test the complete MCP integration"""
    from orchestration.orchestrator_agent import OrchestratorAgent
    
    print("="*80)
    print("🧪 TESTING MCP SMART ROUTING SYSTEM")
    print("="*80)
    
    agent = OrchestratorAgent()
    
    # Test scenarios
    test_cases = [
        {
            "name": "Sufficient Local Results",
            "query": "deep learning applications",
            "expected": "Should use local papers only (sufficient)"
        },
        {
            "name": "Insufficient + Tech Domain",
            "query": "latest advances in quantum computing 2024",
            "expected": "Should route to arXiv (tech, recent)"
        },
        {
            "name": "Insufficient + Medical Domain",
            "query": "latest cancer immunotherapy trials 2024",
            "expected": "Should route to PubMed (medical, recent)"
        },
        {
            "name": "Zero Local Results",
            "query": "blockchain scalability solutions",
            "expected": "Should route to external (likely none local)"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"TEST {i}: {test['name']}")
        print(f"Query: {test['query']}")
        print(f"Expected: {test['expected']}")
        print(f"{'='*80}\n")
        
        try:
            result = await agent.process_query(test['query'])
            
            print(f"\n✅ TEST {i} RESULTS:")
            print(f"   Session ID: {result['session_id']}")
            print(f"   Intent: {result['intent']}")
            print(f"   Response preview: {result['response'][:200]}...")
            print(f"   Tool results count: {len(result['tool_results'])}")
            
            # Analyze tool results
            for tool_result in result['tool_results']:
                tool_name = tool_result['tool_name']
                success = tool_result['success']
                count = tool_result.get('metadata', {}).get('count', 0)
                source = tool_result.get('metadata', {}).get('source', 'local')
                
                print(f"   - {tool_name}: {count} items (source: {source}, success: {success})")
            
            print(f"\n")
        
        except Exception as e:
            print(f"❌ TEST {i} FAILED: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*80}")
    print("🎉 ALL TESTS COMPLETED")
    print(f"{'='*80}\n")
    
    agent.close()


if __name__ == "__main__":
    asyncio.run(test_mcp_system())
