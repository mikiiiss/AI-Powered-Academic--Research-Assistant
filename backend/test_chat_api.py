# Test Chat API Endpoint
# Run this to verify the /api/chat endpoint works

import requests
import json

BASE_URL = "http://localhost:5000/api"

def test_chat_api():
    print("="*80)
    print("🧪 Testing Chat API Endpoint")
    print("="*80)
    
    # Test 1: Simple chat query
    print("\n1. Testing POST /api/chat (initial query)...")
    response = requests.post(
        f"{BASE_URL}/chat",
        json={"query": "What is deep learning?"},
        headers={"Content-Type": "application/json"}
    )
    
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        session_id = data.get('session_id')
        print(f"   ✅ Session ID: {session_id}")
        print(f"   ✅ Intent: {data.get('intent')}")
        print(f"   ✅ Response preview: {data.get('response', '')[:100]}...")
    else:
        print(f"   ❌ Error: {response.text}")
        return
    
    # Test 2: Follow-up question
    print("\n2. Testing POST /api/chat (follow-up query)...")
    response = requests.post(
        f"{BASE_URL}/chat",
        json={
            "query": "What are the research gaps?",
            "session_id": session_id
        },
        headers={"Content-Type": "application/json"}
    )
    
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Intent: {data.get('intent')}")
        print(f"   ✅ Context messages: {data.get('context', {}).get('message_count')}")
        print(f"   ✅ Response preview: {data.get('response', '')[:100]}...")
    else:
        print(f"   ❌ Error: {response.text}")
    
    # Test 3: Get conversation history
    print("\n3. Testing GET /api/chat/history/{session_id}...")
    response = requests.get(f"{BASE_URL}/chat/history/{session_id}")
    
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Total messages: {len(data.get('messages', []))}")
        print(f"   ✅ Topics: {', '.join(data.get('mentioned_topics', [])[:5])}")
    else:
        print(f"   ❌ Error: {response.text}")
    
    # Test 4: List active sessions
    print("\n4. Testing GET /api/chat/sessions...")
    response = requests.get(f"{BASE_URL}/chat/sessions")
    
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Active sessions: {data.get('count')}")
    else:
        print(f"   ❌ Error: {response.text}")
    
    print("\n" + "="*80)
    print("✅ Chat API tests complete!")
    print("="*80)
    print("\nYou can now use the UI to test:")
    print("  POST http://localhost:5000/api/chat")
    print("  Body: {\"query\": \"your question here\"}")

if __name__ == "__main__":
    print("\n⚠️  Make sure the backend server is running:")
    print("   cd backend && python3 app.py\n")
    
    input("Press Enter when server is ready...")
    
    try:
        test_chat_api()
    except requests.exceptions.ConnectionError:
        print("\n❌ Could not connect to server. Is it running on http://localhost:5000?")
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()
