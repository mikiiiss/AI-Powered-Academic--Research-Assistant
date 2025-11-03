# backend/ai_agents/deepseek_client.py
import os
import requests
import json
from typing import List, Dict, Any

class DeepSeekClient:
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
    
    def generate_response(self, prompt: str, system_message: str = None) -> str:
        """Generate response using DeepSeek API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": "deepseek-chat",
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": 2000
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"DeepSeek API error: {e}")
            return None
    
    def extract_quotes(self, paper_content: str, query: str) -> List[str]:
        """Extract relevant quotes from paper content based on query"""
        prompt = f"""
        Given the research paper content and a query, extract 1-3 most relevant quotes that directly address the query.
        
        QUERY: {query}
        
        PAPER CONTENT:
        {paper_content[:4000]}  # Limit content length
        
        Return ONLY a JSON array of quotes, no other text:
        ["quote1", "quote2", "quote3"]
        """
        
        response = self.generate_response(prompt)
        try:
            return json.loads(response) if response else []
        except:
            return []