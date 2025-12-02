# backend/scripts/upgrade_database.py
#!/usr/bin/env python3
"""
Main script to upgrade your database from 390 to 10,000+ papers
"""
import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file (like your existing setup)
load_dotenv()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from data_pipeline.enhanced_paper_storage import EnhancedPaperStorage
from knowledge_graph.enhanced_graph_builder import EnhancedKnowledgeGraphBuilder

async def main():
    print("🚀 STARTING DATABASE UPGRADE...")
    print("=" * 50)
    
    # Verify API key is loaded
    api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
    if not api_key:
        print("❌ ERROR: SEMANTIC_SCHOLAR_API_KEY not found in .env file")
        return
    
    print("✅ Environment variables loaded successfully")
    
    # Step 1: Import papers
    storage = EnhancedPaperStorage()
    total_papers = await storage.build_comprehensive_database()
    
    print(f"\n✅ PAPER IMPORT COMPLETE: {total_papers} papers in database")
    
    # Step 2: Build enhanced knowledge graph
    print("\n🕸️ BUILDING ENHANCED KNOWLEDGE GRAPH...")
    graph_builder = EnhancedKnowledgeGraphBuilder()
    graph = await graph_builder.build_complete_knowledge_graph_with_citations()
    
    print(f"\n🎉 UPGRADE COMPLETE!")
    print(f"📊 Final Stats:")
    print(f"   - Papers: {total_papers}")
    print(f"   - Relationships: {len(graph.edges)}")
    print(f"   - Your AI agents will now work with REAL data! 🚀")

if __name__ == "__main__":
    asyncio.run(main())