#!/usr/bin/env python3
"""
Add relationships table to database
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.database import engine, Base
from api.models.database_models import PaperRelationship

def update_schema():
    print("🔄 Adding relationships table to database...")
    
    try:
        # Create the new table
        PaperRelationship.__table__.create(engine)
        print("✅ Created paper_relationships table")
        
    except Exception as e:
        print(f"❌ Schema update failed: {e}")

if __name__ == "__main__":
    update_schema()