// frontend/src/hooks/useResearchAssistant.js
import { useState, useRef } from 'react';

const API_BASE = 'http://localhost:5000';

export const useResearchAssistant = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [conversationResponse, setConversationResponse] = useState(null);
  const sessionIdRef = useRef(null); // Track session for follow-ups

  const analyzeResearch = async (query) => {
    setLoading(true);
    setError(null);

    try {
      // Call NEW conversational chat API
      const chatResponse = await fetch(`${API_BASE}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query,
          session_id: sessionIdRef.current // Include session for follow-ups
        })
      });

      const chatData = await chatResponse.json();

      if (!chatResponse.ok) {
        throw new Error(chatData.error || 'Chat API failed');
      }

      // Store session ID for follow-up questions
      sessionIdRef.current = chatData.session_id;

      // Store conversational response
      setConversationResponse(chatData.response);

      // Extract data from tool_results for backward compatibility with UI
      const toolResults = chatData.tool_results || [];

      const evidence = [];
      const gaps = [];
      let citationNetwork = { nodes: [], links: [] };

      toolResults.forEach(result => {
        if (result.success && result.data) {
          if (result.tool_name === 'vector_search' || result.tool_name === 'evidence_finder') {
            evidence.push(...result.data);
          } else if (result.tool_name === 'intelligent_gap_detection') {
            gaps.push(...result.data);
          }
        }
      });

      return {
        // NEW: Include conversational response
        conversationResponse: chatData.response,
        intent: chatData.intent,
        sessionId: chatData.session_id,

        // Existing data structure for compatibility
        evidence: evidence.slice(0, 10),
        gaps: gaps.slice(0, 5),
        recommendations: [], // Not using old recommendations endpoint
        trends: [], // Not using old trends endpoint
        citationNetwork,

        // Include context info
        context: chatData.context
      };

    } catch (err) {
      setError(err.message);
      console.error('Research analysis error:', err);

      // Return empty data structure on error
      return {
        conversationResponse: null,
        evidence: [],
        gaps: [],
        recommendations: [],
        trends: [],
        citationNetwork: { nodes: [], links: [] }
      };
    } finally {
      setLoading(false);
    }
  };

  const findGaps = async (query) => {
    setLoading(true);
    setError(null);

    try {
      // Use chat API for gap detection too
      const chatResponse = await fetch(`${API_BASE}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: `What are the research gaps in ${query}?`,
          session_id: sessionIdRef.current
        })
      });

      const chatData = await chatResponse.json();

      if (!chatResponse.ok) {
        throw new Error(chatData.error || 'Failed to find gaps');
      }

      // Store session and response
      sessionIdRef.current = chatData.session_id;
      setConversationResponse(chatData.response);

      // Extract gaps from tool results
      const toolResults = chatData.tool_results || [];
      const gaps = [];

      toolResults.forEach(result => {
        if (result.success && result.tool_name === 'intelligent_gap_detection') {
          gaps.push(...result.data);
        }
      });

      return gaps;

    } catch (err) {
      setError(err.message);
      console.error('Find gaps error:', err);
      return [];
    } finally {
      setLoading(false);
    }
  };

  const resetConversation = () => {
    sessionIdRef.current = null;
    setConversationResponse(null);
  };

  return {
    loading,
    error,
    analyzeResearch,
    findGaps,
    conversationResponse,  // NEW: Expose conversational response
    sessionId: sessionIdRef.current,  // NEW: Expose session ID
    resetConversation  // NEW: Allow resetting conversation
  };
};