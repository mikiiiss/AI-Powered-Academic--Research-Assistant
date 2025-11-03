# #!/usr/bin/env python3
# """
# Reset database with new schema
# """

# import sys
# import os
# sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# from core.database import engine
# from api.models.database_models import Base
# from sqlalchemy import text

# def reset_database():
#     print("🔄 Resetting database with new schema...")
    
#     # Drop and recreate tables
#     Base.metadata.drop_all(bind=engine)
#     Base.metadata.create_all(bind=engine)
    
#     print("✅ Database reset with new schema complete!")
    
#     # Verify table structure
#     with engine.connect() as conn:
#         result = conn.execute(text("""
#             SELECT column_name, data_type 
#             FROM information_schema.columns 
#             WHERE table_name = 'papers' 
#             ORDER BY ordinal_position;
#         """))
#         columns = result.fetchall()
        
#         print("📋 Current papers table columns:")
#         for col_name, col_type in columns:
#             print(f"   - {col_name} ({col_type})")

# if __name__ == "__main__":
#     reset_database()

import requests
import json

def list_available_models(api_key, base_url="https://api.x.ai/v1"):
    """
    List all models available to your API key
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{base_url}/models", headers=headers, timeout=10)
        
        if response.status_code == 200:
            models_data = response.json()
            print("Available models:")
            for model in models_data.get('data', []):
                print(f"  - {model['id']}")
            return models_data.get('data', [])
        else:
            print(f"Failed to get models: {response.status_code}")
            return []
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {str(e)}")
        return []

def test_with_available_model(api_key, base_url="https://api.x.ai/v1"):
    """
    Test with the seventh available model
    """
    models = list_available_models(api_key, base_url)
    
    if not models:
        print("No models found to test with")
        return
    
    # Use the first available model
    model_name = models[6]['id']
    print(f"\nTesting with model: {model_name}")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "messages": [
            {
                "role": "user",
                "content": "Hello! Please respond with just 'OK'"
            }
        ],
        "model": model_name,
        "stream": False,
        "temperature": 0.1
    }
    
    try:
        response = requests.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            response_text = result.get('choices', [{}])[0].get('message', {}).get('content', 'No content')
            print(f"SUCCESS: Chat completion worked!")
            print(f"Response: {response_text}")
        else:
            print(f"FAILED: {response.status_code} - {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {str(e)}")

def main():
    api_key = input("Enter your Grok API key: ").strip()
    
    if not api_key:
        print("Error: No API key provided")
        return
    
    print("Testing Grok API key...")
    
    # First, discover available models
    test_with_available_model(api_key)

if __name__ == "__main__":
    main()