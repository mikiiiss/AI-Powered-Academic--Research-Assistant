# #!/usr/bin/env python3
# """
# Research Assistant Project Structure Generator
# Creates only folders and empty files - no content
# """

# import os
# from pathlib import Path

# class ProjectGenerator:
#     def __init__(self, project_name: str = "research-assistant"):
#         self.project_name = project_name
#         self.base_dir = Path(project_name)
    
#     def generate_project(self):
#         """Generate complete project structure with empty files"""
#         print(f"🚀 Generating {self.project_name}...")
        
#         # Create directory structure
#         self._create_directories()
        
#         # Create all empty files
#         self._create_empty_files()
        
#         print(f"✅ Project structure generated successfully at {self.base_dir}")
#         print("📁 Empty folder structure with all files created!")
    
#     def _create_directories(self):
#         """Create the complete directory structure"""
#         directories = [
#             # Backend structure
#             "backend/crawlers/academic_apis",
#             "backend/crawlers/web_scrapers", 
#             "backend/crawlers/pdf_parsers",
#             "backend/data_pipeline",
#             "backend/ml_pipeline",
#             "backend/agents",
#             "backend/knowledge_graph",
#             "backend/api/routes",
#             "backend/api/models",
#             "backend/core",
            
#             # Frontend
#             "frontend/src/components",
#             "frontend/src/hooks",
#             "frontend/public",
            
#             # Infrastructure
#             "infrastructure/deployment/kubernetes",
#             "infrastructure/deployment/terraform",
            
#             # Docs and tests
#             "docs",
#             "tests/unit",
#             "tests/integration",
#         ]
        
#         for directory in directories:
#             (self.base_dir / directory).mkdir(parents=True, exist_ok=True)
#             print(f"📁 Created directory: {directory}")
    
#     def _create_empty_files(self):
#         """Create all empty files"""
#         files = [
#             # Core files
#             "requirements.txt",
#             "docker-compose.yml",
#             "Dockerfile",
#             ".env.example",
#             "README.md",
#             ".gitignore",
            
#             # Backend core
#             "backend/core/__init__.py",
#             "backend/core/config.py",
#             "backend/core/database.py",
#             "backend/core/cache.py",
#             "backend/core/security.py",
            
#             # Crawlers
#             "backend/crawlers/__init__.py",
#             "backend/crawlers/academic_apis/__init__.py",
#             "backend/crawlers/academic_apis/arxiv_crawler.py",
#             "backend/crawlers/academic_apis/pubmed_crawler.py",
#             "backend/crawlers/academic_apis/ieee_crawler.py",
#             "backend/crawlers/academic_apis/semanticscholar_crawler.py",
            
#             # Web scrapers
#             "backend/crawlers/web_scrapers/__init__.py",
#             "backend/crawlers/web_scrapers/journal_scraper.py",
#             "backend/crawlers/web_scrapers/thesis_scraper.py",
#             "backend/crawlers/web_scrapers/repository_scraper.py",
            
#             # PDF parsers
#             "backend/crawlers/pdf_parsers/__init__.py",
#             "backend/crawlers/pdf_parsers/pdf_to_text.py",
#             "backend/crawlers/pdf_parsers/section_extractor.py",
#             "backend/crawlers/pdf_parsers/reference_parser.py",
            
#             # Data pipeline
#             "backend/data_pipeline/__init__.py",
#             "backend/data_pipeline/etl_pipeline.py",
#             "backend/data_pipeline/data_cleaner.py",
#             "backend/data_pipeline/quality_checker.py",
#             "backend/data_pipeline/data_enricher.py",
#             "backend/data_pipeline/duplicate_detector.py",
            
#             # ML pipeline
#             "backend/ml_pipeline/__init__.py",
#             "backend/ml_pipeline/embedding_service.py",
#             "backend/ml_pipeline/topic_modeling.py",
#             "backend/ml_pipeline/citation_analyzer.py",
#             "backend/ml_pipeline/gap_detector.py",
#             "backend/ml_pipeline/similarity_engine.py",
#             "backend/ml_pipeline/trend_analyzer.py",
            
#             # Agents
#             "backend/agents/__init__.py",
#             "backend/agents/research_analyzer.py",
#             "backend/agents/gap_identifier.py",
#             "backend/agents/trend_predictor.py",
#             "backend/agents/collaboration_matcher.py",
#             "backend/agents/literature_explorer.py",
            
#             # Knowledge graph
#             "backend/knowledge_graph/__init__.py",
#             "backend/knowledge_graph/graph_builder.py",
#             "backend/knowledge_graph/relationship_miner.py",
#             "backend/knowledge_graph/cross_domain_connector.py",
#             "backend/knowledge_graph/query_engine.py",
            
#             # API
#             "backend/api/__init__.py",
#             "backend/api/app.py",
#             "backend/api/routes/__init__.py",
#             "backend/api/routes/papers.py",
#             "backend/api/routes/chat.py",
#             "backend/api/routes/search.py",
#             "backend/api/routes/gaps.py",
#             "backend/api/routes/visualizations.py",
#             "backend/api/models/__init__.py",
#             "backend/api/models/database_models.py",
#             "backend/api/models/request_models.py",
#             "backend/api/models/response_models.py",
            
#             # Infrastructure
#             "infrastructure/nginx.conf",
            
#             # Frontend placeholder
#             "frontend/package.json",
#         ]
        
#         for file_path in files:
#             full_path = self.base_dir / file_path
#             full_path.parent.mkdir(parents=True, exist_ok=True)
#             full_path.touch()  # Create empty file
#             print(f"📄 Created empty file: {file_path}")

# def main():
#     generator = ProjectGenerator()
#     generator.generate_project()

# if __name__ == "__main__":
#     main()

#!/usr/bin/env python3
"""
Force reset the database - DROP and RECREATE the papers table
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from core.database import engine, SessionLocal
from sqlalchemy import text

def force_reset_database():
    print("💥 FORCE RESETTING DATABASE...")
    
    # Connect and drop the table using raw SQL
    try:
        with engine.connect() as conn:
            # Drop table if exists
            conn.execute(text("DROP TABLE IF EXISTS papers CASCADE;"))
            conn.commit()
            print("✅ Dropped papers table")
            
            # Check if table is gone
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name = 'papers';
            """))
            tables = result.fetchall()
            
            if not tables:
                print("✅ Confirmed: papers table no longer exists")
            else:
                print("❌ Papers table still exists!")
                return False
                
    except Exception as e:
        print(f"❌ Error dropping table: {e}")
        return False
    
    # Now create the table using SQLAlchemy model
    try:
        from api.models.database_models import Base
        Base.metadata.create_all(bind=engine)
        print("✅ Created new papers table with current schema")
        
        # Verify the table structure
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'papers' 
                ORDER BY ordinal_position;
            """))
            columns = result.fetchall()
            
            print("📋 Current table columns:")
            for col_name, col_type in columns:
                print(f"   - {col_name} ({col_type})")
                
        return True
        
    except Exception as e:
        print(f"❌ Error creating table: {e}")
        return False

if __name__ == "__main__":
    if force_reset_database():
        print("🎉 Database force reset complete!")
    else:
        print("💥 Database reset failed!")