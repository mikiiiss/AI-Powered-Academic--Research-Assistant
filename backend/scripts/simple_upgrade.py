# # backend/scripts/simple_upgrade.py
# #!/usr/bin/env python3
# """
# Simple upgrade script to test Semantic Scholar integration
# """
# import asyncio
# import sys
# import os
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# # Add backend to path
# sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# from data_pipeline.enhanced_paper_storage import EnhancedPaperStorage

# async def main():
#     print("🚀 STARTING SIMPLE DATABASE UPGRADE...")
#     print("=" * 50)
    
#     # Verify API key is loaded
#     api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
#     if not api_key:
#         print("❌ ERROR: SEMANTIC_SCHOLAR_API_KEY not found in .env file")
#         print("   Please add: SEMANTIC_SCHOLAR_API_KEY=M2Cm37qOKo2sqLzf6tDD38owOycU")
#         return
    
#     print("✅ Environment variables loaded successfully")
    
#     # Step 1: Import papers (just Semantic Scholar first)
#     print("📥 Importing papers from Semantic Scholar...")
#     storage = EnhancedPaperStorage()
    
#     # Start with just 2 queries to test
#     test_queries = ["machine learning", "neural networks"]
    
#     total_papers = await storage.import_from_semantic_scholar(test_queries, papers_per_query=50)
    
#     print(f"\n🎉 UPGRADE COMPLETE!")
#     print(f"📊 Final Stats:")
#     print(f"   - Papers added: {total_papers}")
#     print(f"   - You now have a much richer database! 🚀")

# if __name__ == "__main__":
#     asyncio.run(main())

# backend/scripts/progressive_upgrade.py
#!/usr/bin/env python3
"""
Progressive upgrade - import in smaller batches
"""
import asyncio
import sys
import os
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from data_pipeline.enhanced_paper_storage import EnhancedPaperStorage

async def progressive_import():
    """Import papers in focused batches"""
    storage = EnhancedPaperStorage()
    
    # Batch 1: Core ML & Deep Learning
    print("🔄 BATCH 1: Core Machine Learning & Deep Learning...")
    ml_queries = [
        "deep learning", "neural networks", "convolutional neural networks",
        "recurrent neural networks", "transformers", "attention mechanism",
        "supervised learning", "unsupervised learning", "reinforcement learning"
    ]
    batch1 = await storage.import_from_semantic_scholar(ml_queries, papers_per_query=60)
    
    # Batch 2: Data Science Fundamentals
    print("🔄 BATCH 2: Data Science Fundamentals...")
    ds_queries = [
        "data mining", "predictive modeling", "statistical learning",
        "feature engineering", "data preprocessing", "exploratory data analysis",
        "random forest", "gradient boosting", "support vector machines"
    ]
    batch2 = await storage.import_from_semantic_scholar(ds_queries, papers_per_query=60)
    
    # Batch 3: Modern AI & Applications
    print("🔄 BATCH 3: Modern AI & Applications...")
    ai_queries = [
        "natural language processing", "computer vision", "large language models",
        "generative adversarial networks", "graph neural networks", "transfer learning",
        "time series forecasting", "recommender systems", "anomaly detection"
    ]
    batch3 = await storage.import_from_semantic_scholar(ai_queries, papers_per_query=60)
    
    total = batch1 + batch2 + batch3
    print(f"\n🎉 PROGRESSIVE UPGRADE COMPLETE!")
    print(f"📊 Batch Results:")
    print(f"   - ML & Deep Learning: {batch1} papers")
    print(f"   - Data Science: {batch2} papers") 
    print(f"   - Modern AI: {batch3} papers")
    print(f"   - Total added: {total} papers")
    print(f"   - Estimated total database: {total + 490}+ papers")
    
    return total

async def main():
    print("🚀 STARTING PROGRESSIVE DATA SCIENCE & AI UPGRADE...")
    print("=" * 60)
    
    api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
    if not api_key:
        print("❌ ERROR: SEMANTIC_SCHOLAR_API_KEY not found")
        return
    
    total = await progressive_import()
    print(f"\n✅ Your Research Assistant now has comprehensive Data Science & AI coverage!")

if __name__ == "__main__":
    asyncio.run(main())