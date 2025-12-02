# backend/ai_agents/grok_client.py
import os
import aiohttp
import asyncio
import json
from typing import List, Dict, Any, Optional

class GrokClient:
    def __init__(self):
        self.api_key = os.getenv("GROK_API_KEY")
        self.base_url = "https://api.x.ai/v1/chat/completions"  # Grok API endpoint
        self.max_retries = 3
        self.timeout = aiohttp.ClientTimeout(total=30)
    
    async def generate_response(self, prompt: str, system_message: Optional[str] = None) -> Optional[str]:
        """Generate response using Grok API with retries (async)"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": "grok-4-fast-reasoning",  # Grok model name
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": 2000,
            "stream": False
        }
        
        for attempt in range(self.max_retries):
            try:
                print(f"   🤖 Calling Grok API (attempt {attempt + 1})...")
                
                async with aiohttp.ClientSession(timeout=self.timeout) as session:
                    async with session.post(self.base_url, headers=headers, json=payload) as response:
                        if response.status == 200:
                            result = await response.json()
                            return result["choices"][0]["message"]["content"]
                        else:
                            error_text = await response.text()
                            print(f"   ❌ Grok API error: {response.status} - {error_text}")
                            if attempt < self.max_retries - 1:
                                await asyncio.sleep(2)  # Wait before retry
                                
            except aiohttp.ClientError as e:
                print(f"   ❌ Request error: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2)
            except asyncio.TimeoutError:
                print(f"   ❌ Timeout error")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2)
            except Exception as e:
                print(f"   ❌ Unexpected error: {e}")
                break
        
        return None

    async def generate_response_stream(self, prompt: str, system_message: Optional[str] = None):
        """Generate streaming response using Grok API (async generator)"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": "grok-4-fast-reasoning",  # Grok model name
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": 2000,
            "stream": True
        }
        
        try:
            print(f"   🤖 Calling Grok API (Streaming)...")
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(self.base_url, headers=headers, json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        print(f"   ❌ Grok API error: {response.status} - {error_text}")
                        yield f"Error: {response.status}"
                        return

                    async for line in response.content:
                        if line:
                            line = line.decode('utf-8').strip()
                            if line.startswith('data: ') and line != 'data: [DONE]':
                                try:
                                    json_str = line[6:]  # Skip "data: "
                                    data = json.loads(json_str)
                                    content = data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                                    if content:
                                        yield content
                                except json.JSONDecodeError:
                                    pass
        except Exception as e:
            print(f"   ❌ Stream error: {e}")
            yield f"Error: {str(e)}"
    
    async def extract_quotes(self, paper_content: str, query: str) -> List[str]:
        """Extract relevant quotes using Grok (async)"""
        prompt = f"""
        Extract 1-3 most relevant quotes from this research paper that address: "{query}"
        
        PAPER CONTENT:
        {paper_content[:3000]}
        
        Return ONLY a JSON array of quote strings. Example:
        ["First relevant quote...", "Second relevant quote..."]
        """
        
        response = await self.generate_response(prompt)
        if response:
            try:
                # Clean the response first
                cleaned_response = response.strip()
                if cleaned_response.startswith('```json'):
                    cleaned_response = cleaned_response[7:]
                if cleaned_response.endswith('```'):
                    cleaned_response = cleaned_response[:-3]
                cleaned_response = cleaned_response.strip()
                
                return json.loads(cleaned_response)
            except json.JSONDecodeError as e:
                print(f"   ❌ JSON parse error: {e}")
                print(f"   Raw response: {response}")
        
        return []