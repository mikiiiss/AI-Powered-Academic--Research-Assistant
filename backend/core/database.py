import os
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool  # Add this import
from dotenv import load_dotenv

load_dotenv()

# Get your Neon connection string with connection timeout settings
DATABASE_URL = os.getenv('DATABASE_URL')

# Add connection timeout parameters
if DATABASE_URL and 'sslmode=require' in DATABASE_URL:
    DATABASE_URL += "&connect_timeout=30&keepalives_idle=300"

# Create engine with connection pooling disabled for long operations
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,  # Disable connection pooling for long operations
    pool_pre_ping=True,  # Test connections before using them
    echo=False  # Set to True for debugging
)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base for models
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_connection():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            print("✅ Database connected successfully!")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False