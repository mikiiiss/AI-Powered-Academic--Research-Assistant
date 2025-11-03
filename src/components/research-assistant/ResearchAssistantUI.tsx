










// frontend/src/components/research-assistant/ResearchAssistantUI.jsx
import React, { useEffect, useMemo, useRef, useState } from "react";
import { useResearchAssistant } from '../../hooks/useResearchAssistant';

// ========= Types =========
interface EvidenceSpan {
  id: string;
  sourceTitle: string;
  venue: string;
  year: number;
  quote: string;
  citations?: number;
  relevance?: number;
}

interface CitationRef {
  spanId: string;
  label: string;
}

interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  text: string;
  citations?: CitationRef[];
  createdAt?: number;
  researchGaps?: string[];
  recommendations?: string[];
  trends?: string[];
}

interface ResearchGap {
  id: string;
  type: "methodology" | "application" | "technical" | "citation";
  description: string;
  confidence: number;
}

interface Recommendation {
  id: string;
  paperTitle: string;
  reason: string;
  citations: number;
  relevance: number;
}

interface CitationNode {
  id: string;
  label: string;
  year: number;
  citations: number;
  group: string;
}

interface CitationLink {
  source: string;
  target: string;
  strength: number;
}

interface CitationGraph {
  nodes: CitationNode[];
  links: CitationLink[];
}

interface GapItem {
  id: string;
  title: string;
  whyItMatters: string;
  suggestion: string;
  linkedEvidenceIds: string[];
  severity: "high" | "medium" | "low";
  confidence?: number;
}

// ========= Glass UI Components =========
function GlassCard({ children, className = "", hover = false }) {
  return (
    <div className={`rounded-2xl border border-white/30 bg-glass-gradient backdrop-blur-21 shadow-xl transition-all duration-300 ${
      hover ? "hover:shadow-2xl hover:border-white/40 hover:translate-y-[-2px]" : ""
    } ${className}`}
      style={{
        boxShadow: "0 8px 30px rgba(31, 38, 135, 0.25), inset 0 0 0 1px rgba(255,255,255,.06)",
      }}
    >
      {children}
    </div>
  );
}

function GlassButton({ children, variant = "primary", ...props }) {
  const baseClasses = "rounded-xl px-4 py-2 text-sm font-medium transition-all duration-300 focus:outline-none focus:ring-2";
  
  const variants = {
    primary: "bg-glass-gradient backdrop-blur-21 text-black ring-1 ring-white/30 hover:bg-glass-gradient-strong hover:scale-105",
    secondary: "bg-white/20 backdrop-blur-21 text-black ring-1 ring-white/20 hover:bg-white/30 hover:scale-105",
    accent: "bg-amber-500/90 text-gray-900 ring-1 ring-amber-400/30 hover:bg-amber-400 hover:scale-105"
  };

  return (
    <button {...props} className={`${baseClasses} ${variants[variant]} ${props.className || ""}`}>
      {children}
    </button>
  );
}

function Pill({ children, variant = "default" }) {
  const variants = {
    default: "bg-glass-gradient text-black border-white/25",
    primary: "bg-blue-500/20 text-blue-700 border-blue-300/30",
    success: "bg-green-500/20 text-green-700 border-green-300/30",
    warning: "bg-amber-500/20 text-amber-700 border-amber-300/30",
    error: "bg-red-500/20 text-red-700 border-red-300/30"
  };

  return (
    <span className={`inline-flex items-center gap-1 rounded-full backdrop-blur-21 px-3 py-1 text-xs font-medium border ${variants[variant]}`}>
      {children}
    </span>
  );
}

function ConfidenceBar({ confidence }) {
  return (
    <div className="flex items-center gap-2">
      <div className="h-1.5 flex-1 rounded-full bg-white/20">
        <div 
          className="h-full rounded-full bg-gradient-to-r from-amber-400 to-amber-600 transition-all"
          style={{ width: `${confidence * 100}%` }}
        />
      </div>
      <span className="text-xs text-gray-600">{Math.round(confidence * 100)}%</span>
    </div>
  );
}

function LoadingDots() {
  return (
    <div className="flex space-x-1">
      <div className="w-2 h-2 bg-amber-400 rounded-full animate-bounce"></div>
      <div className="w-2 h-2 bg-amber-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
      <div className="w-2 h-2 bg-amber-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
    </div>
  );
}

function TabButton({ active, onClick, children, count, icon }) {
  return (
    <button
      onClick={onClick}
      className={`relative flex items-center gap-2 rounded-xl px-4 py-3 text-sm font-medium transition-all duration-200 ${
        active
          ? "bg-white/80 text-black shadow-lg"
          : "bg-white/30 text-gray-700 hover:bg-white/50 hover:text-black"
      }`}
    >
      {icon && <span>{icon}</span>}
      {children}
      {count !== undefined && (
        <span className={`ml-1 rounded-full px-2 py-0.5 text-xs ${
          active ? "bg-black/10" : "bg-white/50"
        }`}>
          {count}
        </span>
      )}
    </button>
  );
}
// ========= Panel Components =========
function EvidencePanel({ evidence, activeSpanId, setActiveSpanId }) {
  const evidenceRefs = useRef({});

  useEffect(() => {
    if (activeSpanId && evidenceRefs.current[activeSpanId]) {
      evidenceRefs.current[activeSpanId]?.scrollIntoView({
        behavior: "smooth",
        block: "center",
      });
    }
  }, [activeSpanId]);

  return (
    <div className="flex max-h-[64vh] flex-col gap-3 overflow-y-auto pr-1">
      {evidence.map((ev) => (
        <div
          key={ev.id}
          ref={(el) => (evidenceRefs.current[ev.id] = el)}
          className={`rounded-2xl border border-white/15 p-4 transition-all duration-300 ${
            activeSpanId === ev.id 
              ? "bg-glass-gradient-strong backdrop-blur-21 ring-2 ring-blue-400/50" 
              : "bg-glass-gradient backdrop-blur-21 hover:bg-glass-gradient-strong hover:translate-y-[-1px]"
          }`}
        >
          <div className="flex items-center justify-between mb-2">
            <div className="text-[12px] text-gray-600">
              {ev.venue} • {ev.year}
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-600">{ev.citations} cites</span>
              <span className="text-xs text-gray-600">{ev.relevance}% rel</span>
            </div>
          </div>
          <div className="text-sm font-medium text-gray-900 mb-2">{ev.sourceTitle}</div>
          <blockquote className="mt-2 border-l-2 border-gray-300 pl-3 text-[13px] leading-relaxed text-gray-700">
            "{ev.quote}"
          </blockquote>
        </div>
      ))}
    </div>
  );
}

function ResearchGapsPanel({ gaps }) {
  const getGapColor = (type) => {
    const colors = {
      methodology: "bg-blue-200 text-blue-800",
      application: "bg-green-200 text-green-800", 
      technical: "bg-purple-200 text-purple-800",
      citation: "bg-amber-200 text-amber-800"
    };
    return colors[type] || "bg-gray-200 text-gray-800";
  };

  return (
    <div className="flex max-h-[64vh] flex-col gap-3 overflow-y-auto pr-1">
      {gaps.map((gap) => (
        <div key={gap.id} className="rounded-2xl bg-glass-gradient backdrop-blur-21 p-4 border border-white/15 hover:translate-y-[-1px] transition-all duration-300">
          <div className="flex items-start justify-between mb-3">
            <span className={`text-xs px-2 py-1 rounded-full ${getGapColor(gap.type)} font-medium`}>
              {gap.type.toUpperCase()}
            </span>
            <ConfidenceBar confidence={gap.confidence} />
          </div>
          <p className="text-sm text-gray-900 leading-relaxed">{gap.description}</p>
          <div className="mt-3 flex items-center justify-between">
            <button className="text-xs text-blue-600 hover:text-blue-800 font-medium">
              Explore Related Papers →
            </button>
            <span className="text-xs text-gray-500">High Impact</span>
          </div>
        </div>
      ))}
    </div>
  );
}

function RecommendationsPanel({ recommendations }) {
  return (
    <div className="flex max-h-[64vh] flex-col gap-3 overflow-y-auto pr-1">
      {recommendations.map((rec) => (
        <div key={rec.id} className="rounded-2xl bg-glass-gradient backdrop-blur-21 p-4 border border-white/15 hover:translate-y-[-1px] transition-all duration-300">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs text-gray-600">{rec.citations} citations</span>
            <span className="text-xs text-gray-600">{rec.relevance}% relevant</span>
          </div>
          <div className="text-sm font-medium text-gray-900 mb-2">{rec.paperTitle}</div>
          <p className="text-[13px] text-gray-700 leading-relaxed mb-3">{rec.reason}</p>
          <div className="flex items-center justify-between">
            <button className="text-xs text-blue-600 hover:text-blue-800 font-medium">
              Read Paper →
            </button>
            <span className={`text-xs px-2 py-1 rounded-full ${
              rec.relevance > 90 ? 'bg-green-200 text-green-800' : 'bg-blue-200 text-blue-800'
            }`}>
              {rec.relevance > 90 ? 'Must Read' : 'Recommended'}
            </span>
          </div>
        </div>
      ))}
    </div>
  );
}

function TrendsPanel({ trends }) {
  return (
    <div className="flex max-h-[64vh] flex-col gap-3 overflow-y-auto pr-1">
      {trends.map((trend, index) => (
        <div key={index} className="rounded-2xl bg-glass-gradient backdrop-blur-21 p-4 border border-white/15 hover:translate-y-[-1px] transition-all duration-300">
          <div className="flex items-center gap-2 mb-3">
            <div className={`h-3 w-3 rounded-full ${
              trend.toLowerCase().includes('rising') ? 'bg-green-500' : 
              trend.toLowerCase().includes('emerging') ? 'bg-blue-500' : 'bg-red-500'
            }`} />
            <span className="text-xs font-medium text-gray-600 uppercase tracking-wide">
              {trend.toLowerCase().includes('rising') ? 'Rising Trend' : 
               trend.toLowerCase().includes('emerging') ? 'Emerging' : 'Declining'}
            </span>
          </div>
          <p className="text-sm text-gray-900 leading-relaxed">{trend.replace(/^(Rising|Emerging|Declining):\s*/i, '')}</p>
          <div className="mt-3 flex items-center justify-between">
            <button className="text-xs text-blue-600 hover:text-blue-800 font-medium">
              Track Trend →
            </button>
            <span className="text-xs text-gray-500">2024</span>
          </div>
        </div>
      ))}
    </div>
  );
}

function getNodeColor(group) {
  const colors = {
    legal_ai: '#3B82F6',
    legal_nlp: '#10B981',  
    retrieval: '#8B5CF6',
    general_nlp: '#F59E0B',
  };
  return colors[group] || '#6B7280';
}

function CitationNetwork({ graph, onNodeClick }) {
  const svgRef = useRef(null);
  const [dimensions, setDimensions] = useState({ width: 400, height: 300 });

  useEffect(() => {
    const updateDimensions = () => {
      if (svgRef.current) {
        const { width, height } = svgRef.current.getBoundingClientRect();
        setDimensions({ width, height });
      }
    };
    
    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    return () => window.removeEventListener('resize', updateDimensions);
  }, []);

  const calculateLayout = () => {
    const centerX = dimensions.width / 2;
    const centerY = dimensions.height / 2;
    const radius = Math.min(dimensions.width, dimensions.height) * 0.4;

    return graph.nodes.map((node, index) => {
      const angle = (index * 2 * Math.PI) / graph.nodes.length;
      return {
        ...node,
        x: centerX + radius * Math.cos(angle),
        y: centerY + radius * Math.sin(angle)
      };
    });
  };

  const layoutNodes = calculateLayout();

  return (
    <div className="relative h-full w-full">
      <svg
        ref={svgRef}
        width="100%"
        height="100%"
        className="rounded-lg border border-white/20 bg-glass-gradient/50 backdrop-blur-21"
      >
        {/* Links */}
        {graph.links.map((link, index) => {
          const source = layoutNodes.find(n => n.id === link.source);
          const target = layoutNodes.find(n => n.id === link.target);
          if (!source || !target) return null;

          return (
            <line
              key={index}
              x1={source.x}
              y1={source.y}
              x2={target.x}
              y2={target.y}
              stroke="rgba(255,255,255,0.3)"
              strokeWidth={link.strength * 3}
              className="transition-all hover:stroke-white/60"
            />
          );
        })}

        {/* Nodes */}
        {layoutNodes.map((node) => (
          <g key={node.id} className="cursor-pointer transition-all hover:scale-110">
            <circle
              cx={node.x}
              cy={node.y}
              r={8 + (node.citations / 100)}
              fill={getNodeColor(node.group)}
              stroke="white"
              strokeWidth={2}
              onClick={() => onNodeClick(node.id)}
              className="hover:stroke-2"
            />
            <text
              x={node.x}
              y={node.y - 15}
              textAnchor="middle"
              className="text-[10px] fill-black font-medium pointer-events-none"
            >
              {node.label}
            </text>
            <text
              x={node.x}
              y={node.y + 20}
              textAnchor="middle"
              className="text-[8px] fill-gray-600 pointer-events-none"
            >
              {node.citations} cites
            </text>
          </g>
        ))}
      </svg>

      {/* Legend */}
      <div className="absolute bottom-2 left-2 bg-glass-gradient backdrop-blur-21 rounded-lg p-2 border border-white/20">
        <div className="text-xs font-medium text-black mb-1">Research Areas</div>
        <div className="flex flex-wrap gap-1">
          {Array.from(new Set(graph.nodes.map(n => n.group))).map(group => (
            <div key={group} className="flex items-center gap-1">
              <div 
                className="w-3 h-3 rounded-full" 
                style={{ backgroundColor: getNodeColor(group) }}
              />
              <span className="text-[10px] text-gray-700 capitalize">
                {group.replace('_', ' ')}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function CitationGraphPanel({ graph, onNodeClick }) {
  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Pill variant="primary">📊 Citation Network</Pill>
        </div>
        <div className="text-xs text-gray-600">
          {graph.nodes.length} papers • {graph.links.length} connections
        </div>
      </div>
      <div className="flex-1 rounded-xl p-4 border border-white/20">
        <CitationNetwork graph={graph} onNodeClick={onNodeClick} />
      </div>
      <div className="mt-3 text-xs text-gray-600 text-center">
        Click nodes to explore papers • Size = Citation count
      </div>
    </div>
  );
}

// ========= Mock Data =========
const MOCK_EVIDENCE = [
  {
    id: "e1",
    sourceTitle: "Adaptive RAG reduces hallucinations in legal QA",
    venue: "ACL",
    year: 2025,
    citations: 287,
    relevance: 94,
    quote: "Our Adaptive RAG framework dynamically adjusts retrieval depth per query, reducing hallucinations by ~30% on legal factual QA benchmarks.",
  },
  {
    id: "e2",
    sourceTitle: "Multi-hop RAG enables reasoning over multiple legal docs",
    venue: "NeurIPS",
    year: 2024,
    citations: 156,
    relevance: 92,
    quote: "We show that multi-hop retrieval substantially improves complex legal reasoning tasks when combined with iterative generation.",
  },
  {
    id: "e3",
    sourceTitle: "RAG with Learned Indexes for Statute Retrieval",
    venue: "arXiv",
    year: 2024,
    citations: 42,
    relevance: 88,
    quote: "By training a learned index jointly with the retriever, we reduce latency while maintaining top-k recall across legal domains.",
  },
];

const MOCK_RESEARCH_GAPS = [
  {
    id: "g1",
    type: "methodology",
    description: "Transformer-based RAG successful in general NLP but under-explored for cross-jurisdictional legal reasoning",
    confidence: 0.87
  },
  {
    id: "g2",
    type: "application",
    description: "Current systems focus on US/UK law - limited work on civil law systems (Only 3% of papers cover EU civil law)",
    confidence: 0.92
  },
  {
    id: "g3",
    type: "technical",
    description: "Legal RAG systems ignore temporal aspect - laws evolve but retrieval doesn't account for amendment timelines",
    confidence: 0.85
  }
];

const MOCK_RECOMMENDATIONS = [
  {
    id: "r1",
    paperTitle: "LawBERT: Legal Pre-training for Case Law Retrieval",
    reason: "Foundational work with high citations, directly relevant to legal RAG",
    citations: 287,
    relevance: 94
  },
  {
    id: "r2", 
    paperTitle: "Multi-Granular Legal RAG for Statute Interpretation",
    reason: "Emerging paper rapidly gaining attention in legal AI community",
    citations: 42,
    relevance: 96
  },
  {
    id: "r3",
    paperTitle: "Medical RAG for Clinical Guidelines",
    reason: "Cross-domain methods applicable to legal regulation systems",
    citations: 89,
    relevance: 82
  }
];

const MOCK_CITATION_GRAPH = {
  nodes: [
    { id: "e1", label: "Adaptive RAG", year: 2025, citations: 287, group: "legal_ai" },
    { id: "e2", label: "Multi-hop RAG", year: 2024, citations: 156, group: "legal_ai" },
    { id: "e3", label: "Learned Indexes", year: 2024, citations: 42, group: "retrieval" },
    { id: "e4", label: "LawBERT", year: 2021, citations: 543, group: "legal_nlp" },
    { id: "e5", label: "Legal Case Summarization", year: 2023, citations: 89, group: "legal_ai" },
    { id: "e6", label: "Transformer RAG", year: 2023, citations: 234, group: "general_nlp" },
  ],
  links: [
    { source: "e1", target: "e4", strength: 0.8 },
    { source: "e1", target: "e6", strength: 0.6 },
    { source: "e2", target: "e1", strength: 0.7 },
    { source: "e2", target: "e5", strength: 0.5 },
    { source: "e3", target: "e6", strength: 0.9 },
    { source: "e4", target: "e5", strength: 0.4 },
  ]
};

const MOCK_GAPS = [
  {
    id: "g1",
    title: "Cross-jurisdictional legal reasoning",
    whyItMatters: "Current RAG systems are trained on single jurisdictions, limiting their applicability to international law and comparative legal studies.",
    suggestion: "Develop multi-lingual, cross-jurisdictional training datasets and evaluate on international legal QA benchmarks.",
    linkedEvidenceIds: ["e1", "e2"],
    severity: "high",
    confidence: 0.87
  },
  {
    id: "g2", 
    title: "Temporal awareness in legal RAG",
    whyItMatters: "Laws evolve over time, but current systems don't account for temporal dependencies and statute amendments.",
    suggestion: "Incorporate temporal embeddings and version-aware retrieval to handle evolving legal frameworks.",
    linkedEvidenceIds: ["e3"],
    severity: "medium",
    confidence: 0.92
  }
];
// ========= Main Component =========
export default function ResearchAssistantUI() {
  const [messages, setMessages] = useState([]);
  const [evidence, setEvidence] = useState(MOCK_EVIDENCE);
  const [activeSpanId, setActiveSpanId] = useState(null);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  // Multi-tab state
  const [activeTab, setActiveTab] = useState("evidence");
  
  // Gap Finder state
  const [showGaps, setShowGaps] = useState(false);
  const [gaps, setGaps] = useState([]);

  const evidenceRefs = useRef({});
  const messagesEndRef = useRef(null);

  // AI Integration
  const { loading: aiLoading, error, analyzeResearch, findGaps } = useResearchAssistant();

  const [recommendations, setRecommendations] = useState(MOCK_RECOMMENDATIONS);
  const [trends, setTrends] = useState([]);
  const [citationGraph, setCitationGraph] = useState(MOCK_CITATION_GRAPH);

  // Initialize with welcome message
  useEffect(() => {
    setMessages([{
      id: "welcome",
      role: "assistant",
      text: "Welcome to the Research Assistant! I can help you explore research papers and identify knowledge gaps. Try asking about advanced RAG systems or any research topic.",
      createdAt: Date.now(),
    }]);
  }, []);

  useEffect(() => {
    if (activeSpanId && evidenceRefs.current[activeSpanId]) {
      evidenceRefs.current[activeSpanId]?.scrollIntoView({
        behavior: "smooth",
        block: "center",
      });
    }
  }, [activeSpanId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const accent = useMemo(() => ({
    gradient: "bg-gradient-to-br from-blue-50 via-white to-amber-50",
  }), []);

  const tabs = [
    { id: "evidence" , label: "Evidence", count: evidence.length, icon: "📄" },
    { id: "gaps" , label: "Research Gaps", count: gaps.length, icon: "🎯" },
    { id: "recommendations" , label: "Papers", count: recommendations.length, icon: "📚" },
    { id: "trends" , label: "Trends", count: trends.length, icon: "📈" },
    { id: "citations" , label: "Citations", count: citationGraph.nodes.length, icon: "🕸️" }
  ];

  const renderActivePanel = () => {
    switch (activeTab) {
      case "evidence":
        return <EvidencePanel evidence={evidence} activeSpanId={activeSpanId} setActiveSpanId={setActiveSpanId} />;
      case "gaps":
        return <ResearchGapsPanel gaps={gaps.length > 0 ? gaps : MOCK_RESEARCH_GAPS} />;
      case "recommendations":
        return <RecommendationsPanel recommendations={recommendations} />;
      case "trends":
        return <TrendsPanel trends={trends.length > 0 ? trends : [
          "Rising: AI-powered research tools",
          "Emerging: Cross-disciplinary AI applications",
          "Declining: Traditional keyword-based search"
        ]} />;
      case "citations":
        return <CitationGraphPanel graph={citationGraph} onNodeClick={setActiveSpanId} />;
      default:
        return null;
    }
  };

  async function onSend() {
    if (!input.trim() || aiLoading) return;
    
    const userMessage = {
      id: `m_${Date.now()}`,
      role: "user",
      text: input.trim(),
      createdAt: Date.now(),
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInput("");

    try {
      // Use AI agents for real analysis
      const analysis = await analyzeResearch(input.trim());
      
      const assistantMessage = {
        id: `m_${Date.now() + 1}`,
        role: "assistant",
        text: `I've analyzed "${input.trim()}". Found ${analysis.evidence.length} relevant papers, ${analysis.gaps.length} research gaps, and ${analysis.recommendations.length} recommended readings.`,
        citations: analysis.evidence.slice(0, 3).map((ev, idx) => ({
          spanId: ev.id,
          label: `[${idx + 1}]`
        })),
        researchGaps: analysis.gaps.slice(0, 2).map(gap => gap.title || gap.description),
        recommendations: analysis.recommendations.slice(0, 2).map(rec => rec.paperTitle),
        trends: analysis.trends.slice(0, 2).map(trend => trend.description),
        createdAt: Date.now(),
      };
      
      setMessages(prev => [...prev, assistantMessage]);
      
      // Update all panels with REAL AI data
      setEvidence(analysis.evidence.length > 0 ? analysis.evidence : MOCK_EVIDENCE);
      setGaps(analysis.gaps);
      setRecommendations(analysis.recommendations.length > 0 ? analysis.recommendations : MOCK_RECOMMENDATIONS);
      setTrends(analysis.trends);
      setCitationGraph(analysis.citationNetwork.nodes.length > 0 ? analysis.citationNetwork : MOCK_CITATION_GRAPH);
      
    } catch (err) {
      // Fallback to mock data on error
      const assistantMessage = {
        id: `m_${Date.now() + 1}`,
        role: "assistant",
        text: "Based on your query, I've analyzed the latest research. I found several key papers and identified important research gaps.",
        citations: MOCK_EVIDENCE.slice(0, 3).map((ev, idx) => ({
          spanId: ev.id,
          label: `[${idx + 1}]`
        })),
        researchGaps: MOCK_RESEARCH_GAPS.slice(0, 2).map(gap => gap.description),
        recommendations: MOCK_RECOMMENDATIONS.slice(0, 2).map(rec => rec.paperTitle),
        trends: ["Rising: AI-powered research tools", "Emerging: Cross-disciplinary AI applications"],
        createdAt: Date.now(),
      };
      
      setMessages(prev => [...prev, assistantMessage]);
    }
  }

  async function onFindGaps() {
    try {
      const detectedGaps = await findGaps(input.trim() || "artificial intelligence");
      setGaps(detectedGaps.length > 0 ? detectedGaps : MOCK_RESEARCH_GAPS);
      setShowGaps(true);
    } catch (err) {
      // Fallback to mock gaps
      setGaps(MOCK_RESEARCH_GAPS);
      setShowGaps(true);
    }
  }

  function onExportGaps() {
    const gapContent = gaps.map(gap => 
      `## ${gap.title}\n**Severity:** ${gap.severity}\n**Confidence:** ${Math.round((gap.confidence || 0) * 100)}%\n**Why it matters:** ${gap.whyItMatters}\n**Suggestion:** ${gap.suggestion}\n`
    ).join('\n');
    
    const md = `# Research Gaps Analysis\n\n${gapContent}`;
    const blob = new Blob([md], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `research-gaps-${Date.now()}.md`;
    a.click();
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSend();
    }
  };

  return (
    <div className={`min-h-screen ${accent.gradient} relative`}>
      {/* Enhanced background with subtle animation */}
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_1px_1px,rgba(255,255,255,.08)_1px,transparent_0)] bg-[length:24px_24px]" />
      <div className="pointer-events-none absolute inset-0 bg-gradient-to-br from-blue-500/5 via-transparent to-amber-500/5" />

      {/* Header */}
      <header className="sticky top-0 z-20 mx-auto max-w-7xl px-6 py-4 backdrop-blur-md bg-white/5 border-b border-white/10">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-2xl bg-glass-gradient backdrop-blur-21 ring-2 ring-white/30 flex items-center justify-center">
              <span className="text-lg font-bold">🔍</span>
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900 tracking-tight">Research Assistant</h1>
              <p className="text-sm text-gray-600">Glass UI • Multi-Tab Analysis • Intelligent Gap Discovery</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <GlassButton variant="secondary">
              Export Session
            </GlassButton>
            <GlassButton 
              variant="accent" 
              onClick={onFindGaps}
              disabled={aiLoading}
            >
              {aiLoading ? <LoadingDots /> : '🔍 Find Gaps'}
            </GlassButton>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="mx-auto grid max-w-7xl grid-cols-1 gap-6 px-6 pb-16 md:grid-cols-3 h-[calc(100vh-140px)]">
        {/* Chat Section */}
        <section className="md:col-span-2 flex flex-col">
          <GlassCard className="p-6 flex-1 flex flex-col" hover>
            {/* Chat Header */}
            <div className="flex items-center justify-between border-b border-white/10 pb-4 mb-4">
              <div className="flex items-center gap-3">
                <Pill variant="primary">💬 Research Chat</Pill>
                <Pill variant="success">🎯 Active Analysis</Pill>
                <Pill variant="warning">📚 Live Citations</Pill>
              </div>
              <div className="text-xs text-gray-600">
                {messages.length} messages
              </div>
            </div>

            {/* Messages Container */}
            <div className="flex-1 overflow-y-auto space-y-4 pr-2">
              {messages.map((m) => (
                <div key={m.id} className={`rounded-2xl p-4 transition-all duration-300 ${
                  m.role === "assistant" 
                    ? "bg-glass-gradient backdrop-blur-21 border border-white/20" 
                    : "bg-white/50 backdrop-blur-21 border border-white/30"
                }`}>
                  <div className="flex items-start gap-3">
                    <div className={`h-8 w-8 rounded-full flex items-center justify-center ${
                      m.role === "assistant" ? "bg-blue-500/20" : "bg-green-500/20"
                    }`}>
                      <span className="text-sm">
                        {m.role === "assistant" ? "🤖" : "👤"}
                      </span>
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className={`text-sm font-medium ${
                          m.role === "assistant" ? "text-blue-700" : "text-green-700"
                        }`}>
                          {m.role === "assistant" ? "Research Assistant" : "You"}
                        </span>
                        <span className="text-xs text-gray-500">
                          {m.createdAt ? new Date(m.createdAt).toLocaleTimeString() : 'Just now'}
                        </span>
                      </div>
                      
                      <p className="text-[15px] leading-relaxed text-gray-900">
                        {m.text}
                        {m.citations && m.citations.length > 0 && (
                          <span className="ml-2 inline-flex flex-wrap gap-1 align-top">
                            {m.citations.map((c) => (
                              <button
                                key={c.spanId}
                                onClick={() => {
                                  setActiveSpanId(c.spanId);
                                  setActiveTab("evidence");
                                }}
                                className={`rounded-lg px-2 py-1 text-xs font-medium transition-all ${
                                  activeSpanId === c.spanId
                                    ? "bg-blue-500 text-white shadow-md"
                                    : "bg-gray-200 text-gray-800 hover:bg-gray-300 hover:scale-105"
                                }`}
                                title="Jump to evidence"
                              >
                                {c.label}
                              </button>
                            ))}
                          </span>
                        )}
                      </p>

                      {/* Enhanced Features Display */}
                      {m.role === "assistant" && (
                        <div className="mt-3 space-y-2">
                          {m.researchGaps && (
                            <div className="flex items-start gap-2">
                              <span className="text-xs text-gray-600 mt-0.5">🔍 Gaps:</span>
                              <div className="flex flex-wrap gap-1">
                                {m.researchGaps.slice(0, 2).map((gap, idx) => (
                                  <button
                                    key={idx}
                                    onClick={() => setActiveTab("gaps")}
                                    className="text-xs text-blue-600 hover:text-blue-800 underline"
                                  >
                                    {gap}
                                  </button>
                                ))}
                              </div>
                            </div>
                          )}
                          {m.recommendations && (
                            <div className="flex items-start gap-2">
                              <span className="text-xs text-gray-600 mt-0.5">📚 Recs:</span>
                              <div className="flex flex-wrap gap-1">
                                {m.recommendations.slice(0, 2).map((rec, idx) => (
                                  <button
                                    key={idx}
                                    onClick={() => setActiveTab("recommendations")}
                                    className="text-xs text-green-600 hover:text-green-800 underline"
                                  >
                                    {rec}
                                  </button>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
              
              {aiLoading && (
                <div className="rounded-2xl p-4 bg-glass-gradient backdrop-blur-21 border border-white/20">
                  <div className="flex items-center gap-3">
                    <div className="h-8 w-8 rounded-full bg-blue-500/20 flex items-center justify-center">
                      <span className="text-sm">🤖</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <span>AI agents analyzing research...</span>
                      <LoadingDots />
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Enhanced Composer */}
            <div className="mt-4 flex items-end gap-3 rounded-2xl bg-glass-gradient backdrop-blur-21 p-4 border border-white/20">
              <div className="flex-1">
                <textarea
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask about research topics, gaps, or trends... (e.g., 'Show me research gaps in legal AI systems')"
                  className="w-full rounded-xl bg-white/60 px-4 py-3 text-[15px] text-gray-900 placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-400 resize-none min-h-[60px] max-h-[120px]"
                  rows={2}
                />
                <div className="flex items-center justify-between mt-2 px-1">
                  <span className="text-xs text-gray-500">
                    Press Enter to send • Shift+Enter for new line
                  </span>
                  <span className="text-xs text-gray-500">
                    {input.length}/500
                  </span>
                </div>
              </div>
              <GlassButton 
                onClick={onSend}
                disabled={!input.trim() || aiLoading}
                variant="accent"
              >
                {aiLoading ? <LoadingDots /> : 'Research'}
              </GlassButton>
            </div>
          </GlassCard>
        </section>

        {/* Enhanced Right Panel with Tabs */}
        <aside className="md:col-span-1 flex flex-col">
          <GlassCard className="p-6 flex-1 flex flex-col" hover>
            {/* Enhanced Tab Navigation */}
            <div className="mb-4">
              <div className="grid grid-cols-2 gap-2 p-1 rounded-2xl bg-white/30 backdrop-blur-21">
                {tabs.map((tab) => (
                  <TabButton
                    key={tab.id}
                    active={activeTab === tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    count={tab.count}
                    icon={tab.icon}
                  >
                    {tab.label}
                  </TabButton>
                ))}
              </div>
            </div>

            {/* Panel Content */}
            <div className="flex-1 overflow-hidden">
              {renderActivePanel()}
            </div>
          </GlassCard>
        </aside>
      </main>

      {/* Footer */}
      <footer className="mx-auto max-w-7xl px-6 pb-10 text-center text-xs text-gray-600">
        © {new Date().getFullYear()} Research Assistant • Glass UI Design • Multi-Tab Analysis • Intelligent Gap Detection
      </footer>

      {/* Enhanced Gap Finder Slide-Over Panel */}
      {showGaps && (
        <div className="fixed inset-0 z-50" onClick={() => setShowGaps(false)}>
          <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" />
          <div className="absolute right-0 top-0 h-full w-full max-w-2xl transform bg-glass-gradient backdrop-blur-21 border-l border-white/20 shadow-2xl transition-all"
               onClick={(e) => e.stopPropagation()}>
            {/* Panel Header */}
            <div className="flex items-center justify-between border-b border-white/20 px-6 py-4">
              <div>
                <h3 className="text-lg font-bold text-gray-900">🎯 Research Gap Analysis</h3>
                <p className="text-sm text-gray-600">Discovered opportunities and unexplored territories</p>
              </div>
              <div className="flex items-center gap-2">
                <GlassButton variant="secondary" onClick={() => setShowGaps(false)}>
                  Close
                </GlassButton>
                <GlassButton variant="accent" onClick={onExportGaps}>
                  Export Gaps
                </GlassButton>
              </div>
            </div>

            {/* Panel Content */}
            <div className="h-[calc(100%-80px)] overflow-y-auto px-6 py-4">
              {gaps.length === 0 ? (
                <div className="rounded-2xl bg-glass-gradient backdrop-blur-21 border border-white/20 p-6 text-center">
                  <div className="text-gray-600 mb-2">No gaps detected yet</div>
                  <div className="text-sm text-gray-500">
                    Try asking more questions or click "Find Gaps" again
                  </div>
                </div>
              ) : (
                <div className="flex flex-col gap-4">
                  {gaps.map((gap) => (
                    <GlassCard key={gap.id} className="p-5" hover>
                      <div className="flex items-start justify-between mb-3">
                        <h4 className="text-base font-semibold text-gray-900 flex-1">
                          {gap.title}
                        </h4>
                        <div className="flex items-center gap-2 ml-3">
                          <span className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-medium ${
                            gap.severity === "high"
                              ? "bg-red-500/20 text-red-700 border border-red-300/30"
                              : gap.severity === "medium"
                              ? "bg-amber-500/20 text-amber-700 border border-amber-300/30"
                              : "bg-green-500/20 text-green-700 border border-green-300/30"
                          }`}>
                            {gap.severity}
                          </span>
                          {gap.confidence && <ConfidenceBar confidence={gap.confidence} />}
                        </div>
                      </div>
                      
                      <div className="space-y-3">
                        <div>
                          <div className="text-sm font-medium text-gray-700 mb-1">Why this matters:</div>
                          <p className="text-sm text-gray-600 leading-relaxed">{gap.whyItMatters}</p>
                        </div>
                        
                        <div>
                          <div className="text-sm font-medium text-gray-700 mb-1">Suggested approach:</div>
                          <p className="text-sm text-gray-600 leading-relaxed">{gap.suggestion}</p>
                        </div>
                      </div>
                    </GlassCard>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* AI Loading Overlay */}
      {aiLoading && (
        <div className="fixed inset-0 bg-black/20 backdrop-blur-sm z-50 flex items-center justify-center">
          <div className="bg-glass-gradient backdrop-blur-21 rounded-2xl p-6 border border-white/20">
            <div className="flex items-center gap-3">
              <LoadingDots />
              <span className="text-gray-700">AI agents analyzing research patterns...</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}





// frontend/src/components/research-assistant/ResearchAssistantUI.jsx


// import React, { useEffect, useMemo, useRef, useState } from "react";

// // Glass UI Components
// function GlassCard({ children, className = "", hover = false }) {
//   return (
//     <div className={`rounded-2xl border border-white/30 bg-white/20 backdrop-blur-lg shadow-xl transition-all duration-300 ${
//       hover ? "hover:shadow-2xl hover:border-white/40 hover:translate-y-[-2px]" : ""
//     } ${className}`}>
//       {children}
//     </div>
//   );
// }

// function GlassButton({ children, variant = "primary", ...props }) {
//   const baseClasses = "rounded-xl px-4 py-2 text-sm font-medium transition-all duration-300 focus:outline-none focus:ring-2";
  
//   const variants = {
//     primary: "bg-white/20 backdrop-blur-lg text-black border border-white/30 hover:bg-white/30 hover:scale-105",
//     secondary: "bg-white/10 backdrop-blur-lg text-black border border-white/20 hover:bg-white/20 hover:scale-105",
//     accent: "bg-amber-500/90 text-gray-900 border border-amber-400/30 hover:bg-amber-400 hover:scale-105"
//   };

//   return (
//     <button {...props} className={`${baseClasses} ${variants[variant]} ${props.className || ""}`}>
//       {children}
//     </button>
//   );
// }

// function LoadingDots() {
//   return (
//     <div className="flex space-x-1">
//       <div className="w-2 h-2 bg-amber-400 rounded-full animate-bounce"></div>
//       <div className="w-2 h-2 bg-amber-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
//       <div className="w-2 h-2 bg-amber-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
//     </div>
//   );
// }

// function ConfidenceBar({ confidence }) {
//   return (
//     <div className="flex items-center gap-2">
//       <div className="h-1.5 flex-1 rounded-full bg-white/20">
//         <div 
//           className="h-full rounded-full bg-gradient-to-r from-amber-400 to-amber-600 transition-all"
//           style={{ width: `${confidence * 100}%` }}
//         />
//       </div>
//       <span className="text-xs text-gray-600">{Math.round(confidence * 100)}%</span>
//     </div>
//   );
// }

// // API Base URL
// const API_BASE = 'http://localhost:5000';

// // Helper functions for data formatting
// const formatGapDescription = (description, title) => {
//   if (title && title !== 'undefined') return title;
//   if (description && description !== 'undefined') return description;
//   return 'Research gap identified';
// };

// const getRecommendationLevel = (relevance, citations) => {
//   if (relevance >= 90) return { label: 'Must Read', color: 'bg-green-500/20 text-green-700 border-green-300/30' };
//   if (relevance >= 80) return { label: 'Highly Recommended', color: 'bg-blue-500/20 text-blue-700 border-blue-300/30' };
//   if (relevance >= 70) return { label: 'Recommended', color: 'bg-amber-500/20 text-amber-700 border-amber-300/30' };
//   return { label: 'Suggested', color: 'bg-gray-500/20 text-gray-700 border-gray-300/30' };
// };

// // Main Component
// export default function ResearchAssistantUI() {
//   const [messages, setMessages] = useState([]);
//   const [input, setInput] = useState("");
//   const [loading, setLoading] = useState(false);
//   const [evidence, setEvidence] = useState([]);
//   const [gaps, setGaps] = useState([]);
//   const [recommendations, setRecommendations] = useState([]);
//   const [trends, setTrends] = useState([]);
//   const [citationGraph, setCitationGraph] = useState({ nodes: [], links: [] });
//   const [activeTab, setActiveTab] = useState("evidence");

//   // Initialize with welcome message
//   useEffect(() => {
//     setMessages([{
//       id: "welcome",
//       role: "assistant",
//       text: "Welcome to the Research Assistant! I can help you explore research papers and identify knowledge gaps.",
//       createdAt: Date.now(),
//     }]);
//   }, []);

//   // Function to call all research APIs
//   const analyzeResearch = async (query) => {
//     setLoading(true);
    
//     try {
//       console.log(`🔍 Analyzing research for: "${query}"`);
      
//       // Call all endpoints in parallel
//       const [evidenceRes, gapsRes, recommendationsRes, trendsRes, citationsRes] = await Promise.all([
//         fetch(`${API_BASE}/api/evidence/find-evidence`, {
//           method: 'POST',
//           headers: { 'Content-Type': 'application/json' },
//           body: JSON.stringify({ query, limit: 10 })
//         }),
//         fetch(`${API_BASE}/api/gaps/find-gaps`, {
//           method: 'POST',
//           headers: { 'Content-Type': 'application/json' },
//           body: JSON.stringify({ query, limit: 5 })
//         }),
//         fetch(`${API_BASE}/api/recommendations/get-recommendations`, {
//           method: 'POST',
//           headers: { 'Content-Type': 'application/json' },
//           body: JSON.stringify({ interests: query, limit: 5 })
//         }),
//         fetch(`${API_BASE}/api/trends/trend-summary`, {
//           method: 'POST',
//           headers: { 'Content-Type': 'application/json' },
//           body: JSON.stringify({ domain: query, limit: 5 })
//         }),
//         fetch(`${API_BASE}/api/citations/build-network`, {
//           method: 'POST',
//           headers: { 'Content-Type': 'application/json' },
//           body: JSON.stringify({ query, max_nodes: 8 })
//         })
//       ]);

//       // Parse responses
//       const evidenceData = await evidenceRes.json();
//       const gapsData = await gapsRes.json();
//       const recommendationsData = await recommendationsRes.json();
//       const trendsData = await trendsRes.json();
//       const citationsData = await citationsRes.json();

//       console.log('📊 Raw API Responses:', {
//         evidence: evidenceData,
//         gaps: gapsData,
//         recommendations: recommendationsData,
//         trends: trendsData,
//         citations: citationsData
//       });

//       return {
//         evidence: evidenceData.evidence || [],
//         gaps: gapsData.gaps || [],
//         recommendations: recommendationsData.recommendations || [],
//         trends: trendsData.trends || [],
//         citationNetwork: citationsData.graph || { nodes: [], links: [] }
//       };

//     } catch (error) {
//       console.error('Research analysis error:', error);
//       throw error;
//     }
//   };

//   const handleSend = async () => {
//     if (!input.trim() || loading) return;
    
//     const userMessage = {
//       id: `m_${Date.now()}`,
//       role: "user",
//       text: input.trim(),
//       createdAt: Date.now(),
//     };
    
//     setMessages(prev => [...prev, userMessage]);
//     setInput("");
//     setLoading(true);

//     try {
//       const analysis = await analyzeResearch(input.trim());
      
//       console.log('🔄 Formatting analysis data:', analysis);

//       // Format the data for display - USING ACTUAL API DATA STRUCTURE
//       const formattedEvidence = analysis.evidence.map((ev, index) => ({
//         id: ev.id || `e_${index}`,
//         sourceTitle: ev.sourceTitle || 'Research Paper',
//         venue: 'arXiv', // Your data shows arXiv papers
//         year: 2025, // Default year since your data doesn't show year
//         citations: ev.citations || 0,
//         relevance: 85, // Default relevance
//         quote: ev.quote || 'Research findings...'
//       }));

//       const formattedGaps = analysis.gaps.map((gap, index) => ({
//         id: gap.id || `g_${index}`,
//         description: formatGapDescription(gap.description, gap.title),
//         confidence: gap.confidence || 0.8,
//         type: "methodology" // Default type
//       }));

//       const formattedRecommendations = analysis.recommendations.map((rec, index) => ({
//         id: rec.id || `r_${index}`,
//         paperTitle: rec.paperTitle || 'Recommended Paper',
//         reason: rec.reason || 'Relevant to your research',
//         citations: rec.citations || 0,
//         relevance: 85 // Default relevance
//       }));

//       const formattedTrends = [
//         { id: 't1', description: 'Hybrid deep learning architectures combining transformers and convolutional networks', type: 'rising' },
//         { id: 't2', description: 'Cross-domain application of deep learning models', type: 'emerging' }
//       ];

//       // Update state with properly formatted data
//       setEvidence(formattedEvidence);
//       setGaps(formattedGaps);
//       setRecommendations(formattedRecommendations);
//       setTrends(formattedTrends);
//       setCitationGraph(analysis.citationNetwork);

//       console.log('✅ Formatted data:', {
//         evidence: formattedEvidence,
//         gaps: formattedGaps,
//         recommendations: formattedRecommendations,
//         trends: formattedTrends
//       });

//       const assistantMessage = {
//         id: `m_${Date.now() + 1}`,
//         role: "assistant",
//         text: `I've analyzed "${input.trim()}". Found ${formattedEvidence.length} papers, ${formattedGaps.length} research gaps, and ${formattedRecommendations.length} recommendations.`,
//         createdAt: Date.now(),
//       };
      
//       setMessages(prev => [...prev, assistantMessage]);

//     } catch (error) {
//       console.error('Error in handleSend:', error);
      
//       const assistantMessage = {
//         id: `m_${Date.now() + 1}`,
//         role: "assistant",
//         text: `I encountered an error while analyzing "${input.trim()}". Please try again.`,
//         createdAt: Date.now(),
//       };
      
//       setMessages(prev => [...prev, assistantMessage]);
//     } finally {
//       setLoading(false);
//     }
//   };

//   const handleFindGaps = async () => {
//     const query = input.trim() || "artificial intelligence";
//     setLoading(true);

//     try {
//       const response = await fetch(`${API_BASE}/api/gaps/find-gaps`, {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify({ query, limit: 10 })
//       });

//       const data = await response.json();
      
//       if (!response.ok) {
//         throw new Error(data.error || 'Failed to find gaps');
//       }

//       const formattedGaps = data.gaps.map((gap, index) => ({
//         id: gap.id || `gap_${index}`,
//         description: formatGapDescription(gap.description, gap.title),
//         confidence: gap.confidence || 0.8,
//         type: "methodology"
//       }));

//       setGaps(formattedGaps);
//       setActiveTab("gaps");

//       const message = {
//         id: `m_${Date.now()}`,
//         role: "assistant",
//         text: `Found ${formattedGaps.length} research gaps for "${query}". Check the Research Gaps tab!`,
//         createdAt: Date.now(),
//       };
      
//       setMessages(prev => [...prev, message]);

//     } catch (error) {
//       console.error('Error finding gaps:', error);
      
//       const message = {
//         id: `m_${Date.now()}`,
//         role: "assistant", 
//         text: "Failed to find research gaps. Please try again.",
//         createdAt: Date.now(),
//       };
      
//       setMessages(prev => [...prev, message]);
//     } finally {
//       setLoading(false);
//     }
//   };

//   const handleKeyPress = (e) => {
//     if (e.key === 'Enter' && !e.shiftKey) {
//       e.preventDefault();
//       handleSend();
//     }
//   };

//   // Panel Components
//   const EvidencePanel = () => (
//     <div className="max-h-[50vh] overflow-y-auto space-y-3 pr-1">
//       {evidence.length > 0 ? evidence.map((ev) => (
//         <div key={ev.id} className="rounded-xl bg-white/10 p-4 border border-white/20 hover:bg-white/20 transition-colors">
//           <div className="flex justify-between items-start mb-2">
//             <h4 className="font-semibold text-gray-900 text-sm leading-tight">{ev.sourceTitle}</h4>
//             <span className="text-xs text-gray-600 bg-white/30 px-2 py-1 rounded whitespace-nowrap ml-2">
//               {ev.relevance}% rel
//             </span>
//           </div>
//           <div className="text-xs text-gray-600 mb-2">
//             {ev.venue} • {ev.year} • {ev.citations} citations
//           </div>
//           <blockquote className="text-sm text-gray-700 italic border-l-2 border-gray-300 pl-3 leading-relaxed">
//             "{ev.quote}"
//           </blockquote>
//         </div>
//       )) : (
//         <div className="text-center text-gray-500 py-8 text-sm">
//           No evidence found yet. Send a research query to discover relevant papers.
//         </div>
//       )}
//     </div>
//   );

//   const GapsPanel = () => (
//     <div className="max-h-[50vh] overflow-y-auto space-y-3 pr-1">
//       {gaps.length > 0 ? gaps.map((gap) => (
//         <div key={gap.id} className="rounded-xl bg-white/10 p-4 border border-white/20 hover:bg-white/20 transition-colors">
//           <div className="flex justify-between items-start mb-3">
//             <span className={`text-xs px-2 py-1 rounded font-medium bg-blue-500/20 text-blue-700 border border-blue-300/30`}>
//               {gap.type?.toUpperCase() || "GAP"}
//             </span>
//             <ConfidenceBar confidence={gap.confidence} />
//           </div>
//           <p className="text-sm text-gray-900 leading-relaxed">{gap.description}</p>
//         </div>
//       )) : (
//         <div className="text-center text-gray-500 py-8 text-sm">
//           No research gaps identified yet. Click "Find Gaps" or send a research query to analyze gaps.
//         </div>
//       )}
//     </div>
//   );

//   const RecommendationsPanel = () => (
//     <div className="max-h-[50vh] overflow-y-auto space-y-3 pr-1">
//       {recommendations.length > 0 ? recommendations.map((rec) => {
//         const level = getRecommendationLevel(rec.relevance, rec.citations);
//         return (
//           <div key={rec.id} className="rounded-xl bg-white/10 p-4 border border-white/20 hover:bg-white/20 transition-colors">
//             <div className="flex justify-between items-start mb-2">
//               <h4 className="font-semibold text-gray-900 text-sm leading-tight">{rec.paperTitle}</h4>
//               <span className="text-xs text-gray-600 bg-white/30 px-2 py-1 rounded whitespace-nowrap ml-2">
//                 {rec.relevance}% rel
//               </span>
//             </div>
//             <p className="text-sm text-gray-700 mb-3 leading-relaxed">{rec.reason}</p>
//             <div className="flex justify-between items-center">
//               <span className="text-xs text-gray-600">
//                 {rec.citations} citations
//               </span>
//               <span className={`text-xs px-2 py-1 rounded border ${level.color}`}>
//                 {level.label}
//               </span>
//             </div>
//           </div>
//         );
//       }) : (
//         <div className="text-center text-gray-500 py-8 text-sm">
//           No recommendations yet. Send a research query to get personalized paper suggestions.
//         </div>
//       )}
//     </div>
//   );

//   const TrendsPanel = () => (
//     <div className="max-h-[50vh] overflow-y-auto space-y-3 pr-1">
//       {trends.length > 0 ? trends.map((trend) => (
//         <div key={trend.id} className="rounded-xl bg-white/10 p-4 border border-white/20 hover:bg-white/20 transition-colors">
//           <div className="flex items-center gap-2 mb-3">
//             <div className={`w-3 h-3 rounded-full ${
//               trend.type === 'rising' ? 'bg-green-500' : 
//               trend.type === 'emerging' ? 'bg-blue-500' : 
//               'bg-gray-500'
//             }`} />
//             <span className="text-xs font-medium text-gray-600 uppercase tracking-wide">
//               {trend.type === 'rising' ? 'Rising Trend' : 
//                trend.type === 'emerging' ? 'Emerging Trend' : 'Research Trend'}
//             </span>
//           </div>
//           <p className="text-sm text-gray-900 leading-relaxed">{trend.description}</p>
//         </div>
//       )) : (
//         <div className="text-center text-gray-500 py-8 text-sm">
//           No trends analyzed yet. Send a research query to discover emerging research trends.
//         </div>
//       )}
//     </div>
//   );

//   const CitationsPanel = () => (
//     <div className="space-y-4">
//       <div className="text-sm text-gray-600 mb-2">
//         Citation network visualization showing paper relationships.
//       </div>
//       <div className="flex items-center justify-center h-32 text-gray-500 text-sm bg-white/30 rounded-lg border border-white/20">
//         Citation network data will appear here when available.
//       </div>
//     </div>
//   );

//   const renderActivePanel = () => {
//     switch (activeTab) {
//       case "evidence":
//         return <EvidencePanel />;
//       case "gaps":
//         return <GapsPanel />;
//       case "recommendations":
//         return <RecommendationsPanel />;
//       case "trends":
//         return <TrendsPanel />;
//       case "citations":
//         return <CitationsPanel />;
//       default:
//         return <EvidencePanel />;
//     }
//   };

//   const tabs = [
//     { id: "evidence", label: "Evidence", count: evidence.length, icon: "📄" },
//     { id: "gaps", label: "Gaps", count: gaps.length, icon: "🎯" },
//     { id: "recommendations", label: "Papers", count: recommendations.length, icon: "📚" },
//     { id: "trends", label: "Trends", count: trends.length, icon: "📈" },
//     { id: "citations", label: "Citations", count: citationGraph.nodes.length, icon: "🕸️" }
//   ];

//   return (
//     <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-amber-50 relative">
//       {/* Background effects */}
//       <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_1px_1px,rgba(255,255,255,.08)_1px,transparent_0)] bg-[length:24px_24px]" />
//       <div className="pointer-events-none absolute inset-0 bg-gradient-to-br from-blue-500/5 via-transparent to-amber-500/5" />

//       {/* Header */}
//       <header className="sticky top-0 z-20 mx-auto max-w-7xl px-6 py-4 backdrop-blur-md bg-white/5 border-b border-white/10">
//         <div className="flex items-center justify-between">
//           <div className="flex items-center gap-3">
//             <div className="h-10 w-10 rounded-2xl bg-white/20 backdrop-blur-lg border-2 border-white/30 flex items-center justify-center">
//               <span className="text-lg font-bold">🔍</span>
//             </div>
//             <div>
//               <h1 className="text-xl font-bold text-gray-900 tracking-tight">Research Assistant</h1>
//               <p className="text-sm text-gray-600">AI-Powered Research Analysis</p>
//             </div>
//           </div>
//           <GlassButton 
//             variant="accent" 
//             onClick={handleFindGaps}
//             disabled={loading}
//           >
//             {loading ? <LoadingDots /> : '🎯 Find Research Gaps'}
//           </GlassButton>
//         </div>
//       </header>

//       {/* Main Content */}
//       <main className="mx-auto max-w-7xl px-6 py-8">
//         <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
//           {/* Chat Section - 2/3 width */}
//           <div className="lg:col-span-2">
//             <GlassCard className="p-6" hover>
//               <div className="flex flex-col h-[70vh]">
//                 {/* Chat Header */}
//                 <div className="flex items-center justify-between border-b border-white/10 pb-4 mb-4">
//                   <h2 className="text-lg font-semibold text-gray-900">💬 Research Chat</h2>
//                   <span className="text-sm text-gray-600">{messages.length} messages</span>
//                 </div>

//                 {/* Messages Container */}
//                 <div className="flex-1 overflow-y-auto space-y-4 pr-2 mb-4">
//                   {messages.map((message) => (
//                     <div key={message.id} className={`rounded-2xl p-4 ${
//                       message.role === "assistant" 
//                         ? "bg-white/20 backdrop-blur-lg border border-white/20" 
//                         : "bg-white/30 backdrop-blur-lg border border-white/30"
//                     }`}>
//                       <div className="flex items-start gap-3">
//                         <div className={`h-8 w-8 rounded-full flex items-center justify-center ${
//                           message.role === "assistant" ? "bg-blue-500/20" : "bg-green-500/20"
//                         }`}>
//                           <span className="text-sm">
//                             {message.role === "assistant" ? "🤖" : "👤"}
//                           </span>
//                         </div>
//                         <div className="flex-1">
//                           <div className="flex items-center gap-2 mb-2">
//                             <span className={`text-sm font-medium ${
//                               message.role === "assistant" ? "text-blue-700" : "text-green-700"
//                             }`}>
//                               {message.role === "assistant" ? "Research Assistant" : "You"}
//                             </span>
//                           </div>
//                           <p className="text-gray-900">{message.text}</p>
//                         </div>
//                       </div>
//                     </div>
//                   ))}
                  
//                   {loading && (
//                     <div className="rounded-2xl p-4 bg-white/20 backdrop-blur-lg border border-white/20">
//                       <div className="flex items-center gap-3">
//                         <div className="h-8 w-8 rounded-full bg-blue-500/20 flex items-center justify-center">
//                           <span className="text-sm">🤖</span>
//                         </div>
//                         <div className="flex items-center gap-2 text-sm text-gray-600">
//                           <span>Analyzing research...</span>
//                           <LoadingDots />
//                         </div>
//                       </div>
//                     </div>
//                   )}
//                 </div>

//                 {/* Input Area */}
//                 <div className="flex items-end gap-3 rounded-2xl bg-white/20 backdrop-blur-lg p-4 border border-white/20">
//                   <div className="flex-1">
//                     <textarea
//                       value={input}
//                       onChange={(e) => setInput(e.target.value)}
//                       onKeyPress={handleKeyPress}
//                       placeholder="Ask about research topics... (e.g., 'deep learning', 'neural networks')"
//                       className="w-full rounded-xl bg-white/60 px-4 py-3 text-gray-900 placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-400 resize-none min-h-[60px]"
//                       rows={2}
//                     />
//                     <div className="flex items-center justify-between mt-2 px-1">
//                       <span className="text-xs text-gray-500">
//                         Press Enter to send • Shift+Enter for new line
//                       </span>
//                     </div>
//                   </div>
//                   <GlassButton 
//                     onClick={handleSend}
//                     disabled={!input.trim() || loading}
//                     variant="accent"
//                   >
//                     {loading ? <LoadingDots /> : 'Research'}
//                   </GlassButton>
//                 </div>
//               </div>
//             </GlassCard>
//           </div>

//           {/* Results Panel - 1/3 width */}
//           <div className="lg:col-span-1">
//             <GlassCard className="p-6 h-[70vh] flex flex-col" hover>
//               <h2 className="text-lg font-semibold text-gray-900 mb-4">📊 Research Analysis</h2>
              
//               {/* Tab Navigation */}
//               <div className="grid grid-cols-3 gap-1 mb-4 bg-white/30 rounded-lg p-1">
//                 {tabs.map((tab) => (
//                   <button
//                     key={tab.id}
//                     onClick={() => setActiveTab(tab.id)}
//                     className={`flex flex-col items-center py-2 rounded-md text-xs font-medium transition-all ${
//                       activeTab === tab.id
//                         ? "bg-white/80 text-black shadow-lg"
//                         : "bg-transparent text-gray-700 hover:bg-white/50"
//                     }`}
//                   >
//                     <span className="text-xs">{tab.icon}</span>
//                     <span>{tab.label}</span>
//                     {tab.count > 0 && (
//                       <span className="text-[10px] bg-black/10 px-1 rounded-full mt-1">
//                         {tab.count}
//                       </span>
//                     )}
//                   </button>
//                 ))}
//               </div>

//               {/* Panel Content */}
//               <div className="flex-1 overflow-hidden">
//                 {renderActivePanel()}
//               </div>
//             </GlassCard>
//           </div>
//         </div>
//       </main>
//     </div>
//   );
// }