// // frontend/src/hooks/useResearchAssistant.js
// import { useState, useCallback } from 'react';
// import { researchAPI } from '../services/researchAssistantAPI';

// export const useResearchAssistant = () => {
//   const [loading, setLoading] = useState(false);
//   const [error, setError] = useState(null);

//   const analyzeResearch = useCallback(async (query) => {
//     setLoading(true);
//     setError(null);

//     try {
//       const [evidence, gaps, recommendations, trends, citations] = await Promise.all([
//         researchAPI.findEvidence(query),
//         researchAPI.detectGaps(query),
//         researchAPI.getRecommendations(query),
//         researchAPI.analyzeTrends(query),
//         researchAPI.buildCitationNetwork(query)
//       ]);

//       return {
//         evidence,
//         gaps,
//         recommendations, 
//         trends,
//         citationNetwork: citations
//       };
//     } catch (err) {
//       setError(err.message);
//       throw err;
//     } finally {
//       setLoading(false);
//     }
//   }, []);

//   const findGaps = useCallback(async (query = 'general research') => {
//     setLoading(true);
//     try {
//       return await researchAPI.detectGaps(query);
//     } finally {
//       setLoading(false);
//     }
//   }, []);

//   return {
//     loading,
//     error,
//     analyzeResearch,
//     findGaps,
//     clearError: () => setError(null)
//   };
// };


// frontend/src/hooks/useResearchAssistant.js
import { useState } from 'react';

const API_BASE = 'http://localhost:5000';

export const useResearchAssistant = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const analyzeResearch = async (query) => {
    setLoading(true);
    setError(null);
    
    try {
      // Call multiple endpoints in parallel
      const [evidenceRes, gapsRes, recommendationsRes, trendsRes, citationsRes] = await Promise.all([
        fetch(`${API_BASE}/api/evidence/find-evidence`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query, limit: 10 })
        }),
        fetch(`${API_BASE}/api/gaps/find-gaps`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query, limit: 5 })
        }),
        fetch(`${API_BASE}/api/recommendations/get-recommendations`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ interests: query, limit: 5 })
        }),
        fetch(`${API_BASE}/api/trends/trend-summary`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ domain: query, limit: 3 })
        }),
        fetch(`${API_BASE}/api/citations/build-network`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query, max_nodes: 8 })
        })
      ]);

      // Parse responses
      const evidenceData = await evidenceRes.json();
      const gapsData = await gapsRes.json();
      const recommendationsData = await recommendationsRes.json();
      const trendsData = await trendsRes.json();
      const citationsData = await citationsRes.json();

      // Handle API errors
      if (!evidenceRes.ok) throw new Error(evidenceData.error || 'Evidence API failed');
      if (!gapsRes.ok) throw new Error(gapsData.error || 'Gaps API failed');
      if (!recommendationsRes.ok) throw new Error(recommendationsData.error || 'Recommendations API failed');
      if (!trendsRes.ok) throw new Error(trendsData.error || 'Trends API failed');
      if (!citationsRes.ok) throw new Error(citationsData.error || 'Citations API failed');

      return {
        evidence: evidenceData.evidence || [],
        gaps: gapsData.gaps || [],
        recommendations: recommendationsData.recommendations || [],
        trends: trendsData.trends || [],
        citationNetwork: citationsData.graph || { nodes: [], links: [] }
      };

    } catch (err) {
      setError(err.message);
      console.error('Research analysis error:', err);
      
      // Return empty data structure on error
      return {
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
      const response = await fetch(`${API_BASE}/api/gaps/find-gaps`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, limit: 10 })
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || 'Failed to find gaps');
      }

      return data.gaps || [];

    } catch (err) {
      setError(err.message);
      console.error('Find gaps error:', err);
      return [];
    } finally {
      setLoading(false);
    }
  };

  return {
    loading,
    error,
    analyzeResearch,
    findGaps
  };
};