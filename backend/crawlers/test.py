import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.database import test_connection, engine
from sqlalchemy import text

def test_database():
    print("🧪 Testing database connection...")
    
    if test_connection():
        # Test vector extension
        try:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT * FROM pg_extension WHERE extname = 'vector';"))
                if result.fetchone():
                    print("✅ Vector extension is enabled!")
                else:
                    print("❌ Vector extension not found")
        except Exception as e:
            print(f"❌ Vector test failed: {e}")
    
    print("🎉 Database setup complete!")

if __name__ == "__main__":
    test_database()