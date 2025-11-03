// // frontend/src/components/DebugResearchAssistant.jsx
// import React, { useState } from 'react';

// const DebugResearchAssistant = () => {
//   const [results, setResults] = useState({});
//   const [loading, setLoading] = useState(false);

//   const testEndpoint = async (endpoint, method = 'POST', body = null) => {
//     setLoading(true);
//     try {
//       const response = await fetch(`http://localhost:5000/api${endpoint}`, {
//         method,
//         headers: { 'Content-Type': 'application/json' },
//         body: body ? JSON.stringify(body) : null
//       });
      
//       const data = await response.json();
//       setResults(prev => ({
//         ...prev,
//         [endpoint]: {
//           status: response.status,
//           ok: response.ok,
//           data: data
//         }
//       }));
//     } catch (error) {
//       setResults(prev => ({
//         ...prev,
//         [endpoint]: {
//           status: 'ERROR',
//           ok: false,
//           error: error.message
//         }
//       }));
//     } finally {
//       setLoading(false);
//     }
//   };

//   const testAll = () => {
//     setResults({});
//     testEndpoint('/health', 'GET');
//     testEndpoint('/find-evidence', 'POST', { query: "neural networks", limit: 3 });
//     testEndpoint('/find-gaps', 'POST', { query: "AI research" });
//     testEndpoint('/search', 'POST', { query: "neural networks", limit: 3 });
//     testEndpoint('/all', 'GET');
//   };

//   return (
//     <div className="p-6 max-w-4xl mx-auto">
//       <h1 className="text-2xl font-bold mb-6">🔧 Research Assistant Debug</h1>
      
//       <div className="mb-6">
//         <button 
//           onClick={testAll}
//           disabled={loading}
//           className="bg-blue-500 text-white px-4 py-2 rounded disabled:bg-gray-400"
//         >
//           {loading ? 'Testing...' : 'Test All Endpoints'}
//         </button>
//       </div>

//       <div className="space-y-4">
//         {Object.entries(results).map(([endpoint, result]) => (
//           <div key={endpoint} className={`p-4 border rounded ${
//             result.ok ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'
//           }`}>
//             <div className="flex justify-between items-center">
//               <h3 className="font-mono text-sm">{endpoint}</h3>
//               <span className={`px-2 py-1 text-xs rounded ${
//                 result.ok ? 'bg-green-200 text-green-800' : 'bg-red-200 text-red-800'
//               }`}>
//                 {result.ok ? '✅ WORKING' : '❌ FAILED'}
//               </span>
//             </div>
//             <div className="mt-2 text-sm">
//               <pre className="text-xs bg-white p-2 rounded overflow-auto">
//                 {JSON.stringify(result.data || result.error, null, 2)}
//               </pre>
//             </div>
//           </div>
//         ))}
//       </div>

//       {Object.keys(results).length === 0 && !loading && (
//         <div className="text-gray-500 text-center py-8">
//           Click "Test All Endpoints" to check API connectivity
//         </div>
//       )}
//     </div>
//   );
// };

// export default DebugResearchAssistant;



//  // frontend/src/components/DebugResearchAssistant.jsx
// import React, { useState } from 'react';

// const DebugResearchAssistant = () => {
//   const [results, setResults] = useState({});
//   const [loading, setLoading] = useState(false);

//   const testEndpoint = async (endpoint, method = 'POST', body = null) => {
//     setLoading(true);
//     try {
//       const response = await fetch(`http://localhost:5000/api${endpoint}`, {
//         method,
//         headers: { 'Content-Type': 'application/json' },
//         body: body ? JSON.stringify(body) : null
//       });
      
//       const data = await response.json();
//       setResults(prev => ({
//         ...prev,
//         [endpoint]: {
//           status: response.status,
//           ok: response.ok,
//           data: data
//         }
//       }));
//     } catch (error) {
//       setResults(prev => ({
//         ...prev,
//         [endpoint]: {
//           status: 'ERROR',
//           ok: false,
//           error: error.message
//         }
//       }));
//     } finally {
//       setLoading(false);
//     }
//   };

//   const testAll = () => {
//     setResults({});
//     testEndpoint('/health', 'GET');
//     testEndpoint('/find-evidence', 'POST', { query: "neural networks", limit: 3 });
//     testEndpoint('/find-gaps', 'POST', { query: "AI research" });
//     testEndpoint('/trend-summary', 'POST', { domain: "AI" });
//     testEndpoint('/get-recommendations', 'POST', { interests: "neural networks" });
//     testEndpoint('/build-network', 'POST', { query: "transformers", max_nodes: 10 });
//   };

//   return (
//     <div className="p-6 max-w-4xl mx-auto">
//       <h1 className="text-2xl font-bold mb-6">🔧 Research Assistant Debug</h1>
      
//       <div className="mb-6">
//         <button 
//           onClick={testAll}
//           disabled={loading}
//           className="bg-blue-500 text-white px-4 py-2 rounded disabled:bg-gray-400"
//         >
//           {loading ? 'Testing...' : 'Test All Endpoints'}
//         </button>
//       </div>

//       <div className="space-y-4">
//         {Object.entries(results).map(([endpoint, result]) => (
//           <div key={endpoint} className={`p-4 border rounded ${
//             result.ok ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'
//           }`}>
//             <div className="flex justify-between items-center">
//               <h3 className="font-mono text-sm">{endpoint}</h3>
//               <span className={`px-2 py-1 text-xs rounded ${
//                 result.ok ? 'bg-green-200 text-green-800' : 'bg-red-200 text-red-800'
//               }`}>
//                 {result.ok ? '✅ WORKING' : '❌ FAILED'}
//               </span>
//             </div>
//             <div className="mt-2 text-sm">
//               <pre className="text-xs bg-white p-2 rounded overflow-auto">
//                 {JSON.stringify(result.data || result.error, null, 2)}
//               </pre>
//             </div>
//           </div>
//         ))}
//       </div>

//       {Object.keys(results).length === 0 && !loading && (
//         <div className="text-gray-500 text-center py-8">
//           Click "Test All Endpoints" to check API connectivity
//         </div>
//       )}
//     </div>
//   );
// };

// export default DebugResearchAssistant;


// frontend/src/components/DebugResearchAssistant.jsx
import React, { useState } from 'react';

const DebugResearchAssistant = () => {
  const [results, setResults] = useState({});
  const [loading, setLoading] = useState(false);

  const testEndpoint = async (endpoint, method = 'POST', body = null) => {
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:5000${endpoint}`, {  // Remove /api from here
        method,
        headers: { 'Content-Type': 'application/json' },
        body: body ? JSON.stringify(body) : null
      });
      
      const data = await response.json();
      setResults(prev => ({
        ...prev,
        [endpoint]: {
          status: response.status,
          ok: response.ok,
          data: data
        }
      }));
    } catch (error) {
      setResults(prev => ({
        ...prev,
        [endpoint]: {
          status: 'ERROR',
          ok: false,
          error: error.message
        }
      }));
    } finally {
      setLoading(false);
    }
  };

  const testAll = () => {
    setResults({});
    testEndpoint('/api/health', 'GET');  // ✅ Correct path
    testEndpoint('/api/evidence/find-evidence', 'POST', { query: "neural networks", limit: 3 });  // ✅
    testEndpoint('/api/gaps/find-gaps', 'POST', { query: "AI research" });  // ✅
    testEndpoint('/api/trends/trend-summary', 'POST', { domain: "AI" });  // ✅
    testEndpoint('/api/recommendations/get-recommendations', 'POST', { interests: "neural networks" });  // ✅
    testEndpoint('/api/citations/build-network', 'POST', { query: "transformers", max_nodes: 10 });  // ✅
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">🔧 Research Assistant Debug</h1>
      
      <div className="mb-6">
        <button 
          onClick={testAll}
          disabled={loading}
          className="bg-blue-500 text-white px-4 py-2 rounded disabled:bg-gray-400"
        >
          {loading ? 'Testing...' : 'Test All Endpoints'}
        </button>
      </div>

      <div className="space-y-4">
        {Object.entries(results).map(([endpoint, result]) => (
          <div key={endpoint} className={`p-4 border rounded ${
            result.ok ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'
          }`}>
            <div className="flex justify-between items-center">
              <h3 className="font-mono text-sm">{endpoint}</h3>
              <span className={`px-2 py-1 text-xs rounded ${
                result.ok ? 'bg-green-200 text-green-800' : 'bg-red-200 text-red-800'
              }`}>
                {result.ok ? '✅ WORKING' : '❌ FAILED'}
              </span>
            </div>
            <div className="mt-2 text-sm">
              <pre className="text-xs bg-white p-2 rounded overflow-auto">
                {JSON.stringify(result.data || result.error, null, 2)}
              </pre>
            </div>
          </div>
        ))}
      </div>

      {Object.keys(results).length === 0 && !loading && (
        <div className="text-gray-500 text-center py-8">
          Click "Test All Endpoints" to check API connectivity
        </div>
      )}
    </div>
  );
};

export default DebugResearchAssistant;