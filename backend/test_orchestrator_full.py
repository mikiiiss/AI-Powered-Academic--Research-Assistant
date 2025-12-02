#!/usr/bin/env python3
"""
End-to-end test of conversational orchestrator
Tests the full flow: query → intent → tools → synthesis → response
"""
import sys
import asyncio
sys.path.insert(0, '/home/miki/Summer_projects/New folder (20)/backend')

from orchestration import OrchestratorAgent

async def test_conversational_flow():
    print("="*80)
    print("🧪 Testing Complete Conversational Orchestrator")
    print("="*80)
    
    # Initialize orchestrator
    orchestrator = OrchestratorAgent()
    
    # Test 1: Initial query
    print("\n" + "="*80)
    print("TEST 1: What is neural network?")
    print("="*80)
    
    result1 = await orchestrator.process_query('What is neural network?')
    
    print(f"\n📊 Response:")
    print(f"Intent: {result1['intent']}")
    print(f"Session: {result1['session_id']}")
    print(f"\n{result1['response']}")
    
    # Test 2: Follow-up question (same session)
    print("\n\n" + "="*80)
    print("TEST 2: What are the research gaps? (Follow-up)")
    print("="*80)
    
    result2 = await orchestrator.process_query(
        'What are the research gaps?',
        session_id=result1['session_id']
    )
    
    print(f"\n📊 Response:")
    print(f"Intent: {result2['intent']}")
    print(f"Context messages: {result2['context']['message_count']}")
    print(f"\n{result2['response']}")
    
    print("\n" + "="*80)
    print("✅ Conversational orchestrator test complete!")
    print("="*80)
    
    orchestrator.close()

if __name__ == "__main__":
    asyncio.run(test_conversational_flow())
