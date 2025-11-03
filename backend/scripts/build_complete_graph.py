#!/usr/bin/env python3
"""
Build complete knowledge graph with persistence
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from knowledge_graph.graph_builder import KnowledgeGraphBuilder

def main():
    print("🚀 Building complete knowledge graph with persistence...")
    
    builder = KnowledgeGraphBuilder()
    
    try:
        # Build and persist the graph
        graph = builder.build_complete_knowledge_graph()
        
        # Show analysis
        analysis = builder.analyze_relationships()
        print(f"\n📊 GRAPH ANALYSIS:")
        for key, value in analysis.items():
            if key != "relationship_types":
                print(f"   - {key}: {value}")
        
        print(f"\n🔗 RELATIONSHIP TYPES:")
        for rel_type, count in analysis.get("relationship_types", {}).items():
            print(f"   - {rel_type}: {count}")
            
    finally:
        builder.close()

if __name__ == "__main__":
    main()