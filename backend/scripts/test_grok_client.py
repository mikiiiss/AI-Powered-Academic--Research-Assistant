# backend/scripts/test_grok_client.py
#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ai_agents.grok_client import GrokClient

def main():
    print("🧪 Testing Grok API Client...")
    
    client = GrokClient()
    
    # Simple test
    test_prompt = "What are research gaps in neural networks? Return a JSON array with 2 gaps."
    
    response = client.generate_response(test_prompt)
    
    if response:
        print("✅ Grok API is working!")
        print(f"Response: {response[:200]}...")
    else:
        print("❌ Grok API failed")

if __name__ == "__main__":
    main()