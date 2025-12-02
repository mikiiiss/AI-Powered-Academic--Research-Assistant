// frontend/src/services/researchAssistantAPI.js
// Use Vite env var VITE_API_BASE for dev/prod override. If not set, default to localhost backend.
// Example: create a `.env` file at the project root with `VITE_API_BASE=http://localhost:5000/api`
const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:5000/api';

export class ResearchAssistantAPI {
  async makeRequest(endpoint, options = {}) {
    try {
      const response = await fetch(`${API_BASE}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) throw new Error(`API error: ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error(`API call failed for ${endpoint}:`, error);
      throw error;
    }
  }

  async findEvidence(query, limit = 10) {
    const data = await this.makeRequest('/evidence/find-evidence', {
      method: 'POST',
      body: JSON.stringify({ query, limit }),
    });
    return data.evidence || [];
  }

  async detectGaps(query) {
    const data = await this.makeRequest('/gaps/find-gaps', {
      method: 'POST',
      body: JSON.stringify({ query }),
    });
    return data.gaps || [];
  }

  async getRecommendations(interests) {
    const data = await this.makeRequest('/recommendations/get-recommendations', {
      method: 'POST',
      body: JSON.stringify({ interests }),
    });
    return data.recommendations || [];
  }

  async analyzeTrends(domain) {
    const data = await this.makeRequest('/trends/trend-summary', {
      method: 'POST',
      body: JSON.stringify({ domain }),
    });
    return data.trends || [];
  }

  async buildCitationNetwork(query, maxNodes = 15) {
    const data = await this.makeRequest('/citations/build-network', {
      method: 'POST',
      body: JSON.stringify({ query, max_nodes: maxNodes }),
    });
    return data;
  }

  // NEW: Conversational chat interface
  async chat(query, sessionId = null) {
    const data = await this.makeRequest('/chat', {
      method: 'POST',
      body: JSON.stringify({
        query,
        session_id: sessionId
      }),
    });
    return data;
  }

  async getChatHistory(sessionId) {
    return await this.makeRequest(`/chat/history/${sessionId}`);
  }
}

export const researchAPI = new ResearchAssistantAPI();