# Quick Test Guide - Conversational Research Assistant

## Backend is Running! ✅

The backend server should be running on `http://localhost:5000`

---

## Option 1: Test with curl (Quick)

```bash
# Test 1: Initial query
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What is deep learning?"}'

# You'll get back a response with:
# - session_id (save this for follow-ups!)
# - response (natural language with citations)
# - intent (what type of query it detected)
```

---

## Option 2: Test with Python (Better formatting)

```bash
cd backend
python3 test_chat_api.py
```

This will run 4 tests:
1. Initial query
2. Follow-up question
3. Get conversation history
4. List active sessions

---

## Option 3: Test with Browser DevTools

1. Open browser to any page
2. Open DevTools (F12)
3. Go to Console tab
4. Paste this:

```javascript
// Test 1: Initial query
fetch('http://localhost:5000/api/chat', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({query: 'What is neural network?'})
})
.then(r => r.json())
.then(data => {
  console.log('Response:', data.response);
  console.log('Intent:', data.intent);
  console.log('Session ID:', data.session_id);
  
  // Save session ID for follow-up
  window.sessionId = data.session_id;
})

// Test 2: Follow-up (run after first one completes)
fetch('http://localhost:5000/api/chat', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    query: 'What are the research gaps?',
    session_id: window.sessionId
  })
})
.then(r => r.json())
.then(data => {
  console.log('Follow-up Response:', data.response);
  console.log('Message count:', data.context.message_count);
})
```

---

## Option 4: Use existing UI (if frontend starts)

If you can get the frontend to start:

1. Add a new chat component or
2. Modify existing search to call `/api/chat` instead of `/api/papers/search`

---

## What to Look For:

✅ **Natural Language Response** - Not JSON data, but actual prose
✅ **Inline Citations** - Like [Author et al., Year]
✅ **Follow-up Context** - System remembers previous questions
✅ **Intelligent Gaps** - If you ask about gaps, you'll get 4 strategy analysis

---

## Expected Response Example:

```json
{
  "session_id": "79417753-e68c-457a...",
  "query": "What is neural network?",
  "intent": "search",
  "response": "Based on analysis of the research literature, neural networks are computational models inspired by biological neurons, consisting of interconnected layers that process information through weighted connections [Hinton et al., 2012]. They excel at pattern recognition tasks and have revolutionized fields like computer vision and natural language processing [LeCun et al., 2015]...",
  "context": {
    "message_count": 2,
    "mentioned_papers": ["paper_123", "paper_456"],
    "mentioned_topics": ["neural", "networks", "learning"]
  }
}
```

---

## Frontend Issue (file watcher):

If frontend won't start due to ENOSPC error:

**Quick fix:**
```bash
# Increase file watchers limit
echo fs.inotify.max_user_watches=524288 | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

Then try:
```bash
npm run dev
```

---

**Choose your testing method and try it out!** 🚀
