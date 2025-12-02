#!/usr/bin/env python3
"""
DEMO: Conversational Research Assistant
Shows all the features we've built:
1. Conversation memory (Redis)
2. Intent detection (Grok)
3. Intelligent gap detection (4 strategies)
4. Response synthesis with citations
5. Follow-up questions
"""
import sys
import asyncio
sys.path.insert(0, '/home/miki/Summer_projects/New folder (20)/backend')

from orchestration import OrchestratorAgent

def print_section(title):
    """Pretty print section headers"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

async def demo():
    print_section("🚀 CONVERSATIONAL RESEARCH ASSISTANT DEMO")
    
    print("This demo showcases:")
    print("  ✅ Conversation memory (Redis)")
    print("  ✅ Intent detection (Grok AI)")
    print("  ✅ Intelligent gap detection (4 strategies)")
    print("  ✅ Response synthesis with citations")
    print("  ✅ Follow-up question handling")
    print()
    
    input("Press Enter to start...")
    
    # Initialize orchestrator
    print_section("Initializing Orchestrator Agent...")
    orchestrator = OrchestratorAgent()
    
    # ========================================
    # Demo 1: Paper Search with Citations
    # ========================================
    print_section("DEMO 1: Search - 'What is deep learning?'")
    
    result1 = await orchestrator.process_query('What is deep learning?')
    
    print(f"🎯 Intent Detected: {result1['intent']}")
    print(f"💾 Session ID: {result1['session_id']}")
    print(f"📊 Papers Found: {result1['context']['mentioned_papers'][:3]}...")
    print(f"\n📝 Response:\n")
    print(result1['response'])
    
    input("\n\nPress Enter for next demo...")
    
    # ========================================
    # Demo 2: Gap Detection
    # ========================================
    print_section("DEMO 2: Gap Detection - 'What are research gaps in transformers?'")
    
    result2 = await orchestrator.process_query(
        'What are research gaps in transformers?',
        session_id=result1['session_id']  # Same session!
    )
    
    print(f"🎯 Intent Detected: {result2['intent']}")
    print(f"💬 Context Messages: {result2['context']['message_count']}")
    print(f"📊 Topics Discussed: {result2['context']['mentioned_topics'][:5]}")
    print(f"\n📝 Response:\n")
    print(result2['response'])
    
    # Show detected gaps
    if result2['tool_results']:
        gap_result = [r for r in result2['tool_results'] if r['tool_name'] == 'intelligent_gap_detection']
        if gap_result and gap_result[0]['success']:
            gaps = gap_result[0]['data']
            print(f"\n🔍 Detected Gaps Details:")
            for i, gap in enumerate(gaps[:3], 1):
                print(f"\n   {i}. [{gap['type'].upper()}]")
                print(f"      {gap['description']}")
                print(f"      Why: {gap.get('importance', 'N/A')[:100]}...")
    
    input("\n\nPress Enter for next demo...")
    
    # ========================================
    # Demo 3: Follow-up Question
    # ========================================
    print_section("DEMO 3: Follow-up - 'Can you elaborate on the first gap?'")
    
    result3 = await orchestrator.process_query(
        'Can you elaborate on the first gap?',
        session_id=result1['session_id']  # Same conversation!
    )
    
    print(f"🎯 Intent Detected: {result3['intent']}")
    print(f"💬 Context Messages: {result3['context']['message_count']}")
    print(f"📚 Conversation History Maintained!")
    print(f"\n📝 Response:\n")
    print(result3['response'])
    
    input("\n\nPress Enter for citation demo...")
    
    # ========================================
    # Demo 4: Citation Formats
    # ========================================
    print_section("DEMO 4: Citation Formatting (6 Styles)")
    
    from utils.citation_formatter import CitationFormatter
    
    # Sample paper
    sample_paper = {
        'title': 'Attention Is All You Need',
        'authors': 'Vaswani, Ashish, Shazeer, Noam, Parmar, Niki',
        'year': '2017',
        'venue': 'NeurIPS'
    }
    
    print("Sample Paper:")
    print(f"  Title: {sample_paper['title']}")
    print(f"  Authors: {sample_paper['authors']}")
    print(f"  Year: {sample_paper['year']}\n")
    
    styles = ['APA', 'MLA', 'IEEE', 'HARVARD', 'CHICAGO', 'INLINE']
    
    for style in styles:
        citation = CitationFormatter.format_citation(sample_paper, style)
        print(f"{style:10s}: {citation}")
    
    input("\n\nPress Enter for conversation history...")
    
    # ========================================
    # Demo 5: Conversation History
    # ========================================
    print_section("DEMO 5: Conversation History")
    
    from orchestration import ConversationManager
    
    cm = ConversationManager()
    context = cm.get_context(result1['session_id'])
    
    print(f"Session: {context.session_id}")
    print(f"Total Messages: {len(context.messages)}")
    print(f"Mentioned Papers: {len(context.mentioned_papers)}")
    print(f"Discussed Topics: {', '.join(context.mentioned_topics[:10])}")
    print(f"\nConversation Flow:\n")
    
    for i, msg in enumerate(context.messages, 1):
        role_emoji = "👤" if msg.role == "user" else "🤖"
        content_preview = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
        print(f"{i}. {role_emoji} {msg.role.upper()}: {content_preview}")
    
    # ========================================
    # Summary
    # ========================================
    print_section("✅ DEMO COMPLETE - Summary")
    
    print("What You Just Saw:")
    print()
    print("1. 🔍 SEARCH")
    print("   - Vector search across 2,124 papers")
    print("   - Semantic similarity matching")
    print("   - Natural language response with citations")
    print()
    print("2. 🧠 INTELLIGENT GAP DETECTION")
    print("   - 4 strategies: Semantic, Contradiction, Missing Connections, Temporal")
    print("   - Grok AI-powered analysis")
    print("   - Evidence-based gap identification")
    print()
    print("3. 💬 CONVERSATIONAL INTERFACE")
    print("   - Redis-based conversation memory")
    print("   - Context-aware follow-ups")
    print("   - Intent detection via Grok")
    print()
    print("4. 📚 CITATION MANAGEMENT")
    print("   - 6 academic styles (APA, MLA, IEEE, Harvard, Chicago, Inline)")
    print("   - Inline citations in responses")
    print("   - Bibliography generation")
    print()
    print("5. 🔄 RESPONSE SYNTHESIS")
    print("   - Grok-powered natural language generation")
    print("   - Citation-rich responses")
    print("   - Context from conversation history")
    print()
    print("\n🎉 All systems operational!")
    
    orchestrator.close()

if __name__ == "__main__":
    try:
        asyncio.run(demo())
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted. Goodbye!")
    except Exception as e:
        print(f"\n\n❌ Demo error: {e}")
        import traceback
        traceback.print_exc()
