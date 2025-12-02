#!/usr/bin/env python3
"""
Test script for IntelligentGapDetector
Demonstrates the new Grok-powered gap detection
"""
import sys
import asyncio
sys.path.insert(0, '/home/miki/Summer_projects/New folder (20)/backend')

from orchestration.intelligent_gap_detector import IntelligentGapDetector

async def test_gap_detection():
    print("="*70)
    print("🧪 Testing NEW Intelligent Gap Detector")
    print("="*70)
    
    # Initialize detector
    detector = IntelligentGapDetector()
    
    # Test query
    query = "neural networks for natural language processing"
    
    print(f"\n📝 Query: {query}")
    print("\n" + "="*70)
    
    # Detect gaps
    gaps = await detector.detect_gaps(query, max_gaps=5)
    
    # Display results
    print("\n" + "="*70)
    print(f"📊 RESULTS: Found {len(gaps)} research gaps")
    print("="*70)
    
    for i, gap in enumerate(gaps, 1):
        print(f"\n🔍 Gap {i}: {gap.get('type', 'unknown').upper()}")
        print(f"   Description: {gap.get('description', 'N/A')}")
        print(f"   Importance: {gap.get('importance', 'N/A')}")
        
        if gap.get('evidence'):
            print(f"   Evidence: {', '.join(gap['evidence'][:3])}")
        
        if gap.get('conflicting_papers'):
            print(f"   Conflicting papers: {', '.join(gap['conflicting_papers'][:2])}")
        
        if gap.get('concepts'):
            print(f"   Concepts: {', '.join(gap['concepts'])}")
    
    print("\n" + "="*70)
    print("✅ Test complete!")
    print("="*70)
    
    detector.close()

if __name__ == "__main__":
    asyncio.run(test_gap_detection())
