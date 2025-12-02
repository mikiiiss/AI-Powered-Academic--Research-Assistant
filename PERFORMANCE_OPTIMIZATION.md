# Performance optimization tips for the research assistant

## Current Bottlenecks (as of optimization)

### 1. Grok API Calls (~5-10s each)
- **Intent Analysis**: 1 call per query
- **Gap Detection - Semantic**: 1 call per gap query
- **Gap Detection - Connections**: DISABLED for speed
- **Response Synthesis**: 1 call per query

**Total for gap detection query**: ~15-20 seconds

### 2. Vector Search
- Reduced from 50 to 20 papers for gap detection
- Standard search uses 10 papers

### 3. Database Queries
- Generally fast (<1s)

## Optimizations Applied

1. ✅ **Reduced paper analysis**: 50 → 20 papers for gap detection
2. ✅ **Disabled slow strategies**: Missing connections detection disabled
3. ✅ **Fewer papers for semantic analysis**: 20 → 15 papers

## Further Optimizations (if needed)

### Quick Wins:
1. **Add request timeout** (30s max)
2. **Cache Grok responses** for identical queries (Redis)
3. **Parallel Grok calls** where possible
4. **Skip intent analysis** for obvious queries (starts with "find", "what is", etc.)

### Medium Effort:
1. **Implement query result caching** (5-minute TTL)
2. **Add "Quick Mode"** toggle in UI (skips gap detection, uses cached results)
3. **Lazy load gap detection** (return papers first, gaps later)

### Code Changes for Timeout:

```python
# In orchestrator_agent.py, add timeout to Grok calls:
import asyncio

try:
    response = await asyncio.wait_for(
        self.grok.generate_response(prompt),
        timeout=10.0  # 10 second timeout
    )
except asyncio.TimeoutError:
    print("⚠️ Grok API timeout, using fallback")
    return Intent.SEARCH  # or other fallback
```

### Code Changes for Simple Intent Detection:

```python
# Skip Grok for obvious queries
def _quick_intent_check(self, query: str) -> Optional[Intent]:
    query_lower = query.lower()
    
    if any(word in query_lower for word in ['find', 'search', 'show me', 'get']):
        return Intent.SEARCH
    
    if any(word in query_lower for word in ['gap', 'missing', 'unexplored', 'opportunity']):
        return Intent.GAP_DETECTION
    
    return None  # Use Grok for complex queries
```

## Expected Performance After Optimizations

- **Simple search query**: 3-5 seconds
- **Gap detection query**: 12-18 seconds (down from 30-40s)
- **With caching**: <1 second for repeated queries

## Monitoring

Check backend logs for timing:
```bash
grep "execution_time" backend_logs.txt
```
