// frontend/src/components/research-assistant/ResearchAssistantUI.tsx
import React, { useEffect, useState } from "react";

// Types
interface Message {
  id: string;
  role: "assistant" | "user";
  text: string;
  createdAt: number;
  intent?: string;
  paperCount?: number;
  gapCount?: number;
  hasExternal?: boolean;
}

interface Paper {
  title: string;
  year: string;
  authors: string;
  abstract: string;
  url?: string;
  relevance: number;
  citationCount?: number;
  isExternal?: boolean;
  source?: string;
}

interface Gap {
  topic?: string;
  title?: string;
  description: string;
  reason?: string;
  importance?: string;
}

interface ToolResult {
  tool_name: string;
  data: any;
}

// Glass UI Components
function GlassCard({ children, className = "", hover = false }: { children: React.ReactNode, className?: string, hover?: boolean }) {
  return (
    <div className={`rounded-2xl border border-white/30 bg-white/20 backdrop-blur-lg shadow-xl transition-all duration-300 ${hover ? "hover:shadow-2xl hover:border-white/40 hover:translate-y-[-2px]" : ""} ${className}`}>
      {children}
    </div>
  );
}

function GlassButton({ children, variant = "primary", ...props }: { children: React.ReactNode, variant?: "primary" | "secondary" | "accent", [key: string]: any }) {
  const baseClasses = "rounded-xl px-4 py-2 text-sm font-medium transition-all duration-300 focus:outline-none focus:ring-2";
  const variants = {
    primary: "bg-white/20 backdrop-blur-lg text-black border border-white/30 hover:bg-white/30 hover:scale-105",
    secondary: "bg-white/10 backdrop-blur-lg text-black border border-white/20 hover:bg-white/20 hover:scale-105",
    accent: "bg-amber-500/90 text-gray-900 border border-amber-400/30 hover:bg-amber-400 hover:scale-105"
  };
  return <button {...props} className={`${baseClasses} ${variants[variant]} ${props.className || ""}`}>{children}</button>;
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

const API_BASE = 'http://localhost:5000';

export default function ResearchAssistantUI() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const [evidence, setEvidence] = useState<Paper[]>([]);
  const [gaps, setGaps] = useState<Gap[]>([]);
  const [activeTab, setActiveTab] = useState<string>("evidence");

  useEffect(() => {
    setMessages([{ id: "welcome", role: "assistant", text: "Welcome! I retrieve papers from your database (2,124 papers) and use AI to generate natural language responses with citations.", createdAt: Date.now() }]);
  }, []);

  const handleSend = async () => {
    if (!input.trim() || loading) return;
    const userMessage: Message = { id: `m_${Date.now()}`, role: "user", text: input.trim(), createdAt: Date.now() };
    setMessages(prev => [...prev, userMessage]);
    const queryText = input.trim();
    setInput("");
    setLoading(true);

    // Create placeholder assistant message
    const assistantMsgId = `m_${Date.now() + 1}`;
    setMessages(prev => [...prev, {
      id: assistantMsgId,
      role: "assistant",
      text: "",
      createdAt: Date.now(),
      intent: "processing..."
    }]);

    try {
      const response = await fetch(`${API_BASE}/api/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: queryText })
      });

      if (!response.ok) throw new Error('Stream failed');
      if (!response.body) throw new Error('No response body');

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let fullText = '';
      let toolResults: ToolResult[] = [];

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || ''; // Keep incomplete line

        for (const line of lines) {
          if (!line.trim()) continue;
          try {
            const event = JSON.parse(line);

            if (event.type === 'token') {
              fullText += event.content;
              setMessages(prev => prev.map(msg =>
                msg.id === assistantMsgId ? { ...msg, text: fullText } : msg
              ));
            } else if (event.type === 'status') {
              setMessages(prev => prev.map(msg =>
                msg.id === assistantMsgId ? { ...msg, intent: event.content } : msg
              ));
            } else if (event.type === 'tool_data') {
              toolResults = event.data;
              const allPapers: Paper[] = [];
              const gapsList: Gap[] = [];

              toolResults.forEach(tool => {
                if (tool.tool_name === "vector_search" || tool.tool_name === "mcp_external_search") {
                  if (tool.data && Array.isArray(tool.data)) {
                    tool.data.forEach((paper: any) => {
                      allPapers.push({
                        ...paper,
                        isExternal: tool.tool_name === "mcp_external_search",
                        source: paper.source || (tool.tool_name === "mcp_external_search" ? "External" : "Local Database")
                      });
                    });
                  }
                } else if (tool.tool_name === "intelligent_gap_detection" && tool.data && Array.isArray(tool.data)) {
                  gapsList.push(...tool.data);
                }
              });

              setEvidence(allPapers);
              setGaps(gapsList);

              setMessages(prev => prev.map(msg =>
                msg.id === assistantMsgId ? {
                  ...msg,
                  paperCount: allPapers.length,
                  gapCount: gapsList.length,
                  hasExternal: allPapers.some(p => p.isExternal)
                } : msg
              ));
            }
          } catch (e) {
            console.error('Error parsing stream line:', e);
          }
        }
      }
    } catch (error: any) {
      setMessages(prev => [...prev, { id: `m_${Date.now() + 2}`, role: "assistant", text: `Error: ${error.message}`, createdAt: Date.now() }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); } };

  const EvidencePanel = () => (
    <div className="space-y-4 overflow-y-auto h-full pr-2 pb-20">
      {evidence.length === 0 ? <div className="text-center text-gray-500 mt-10"><p>No papers retrieved yet.</p><p className="text-xs mt-2">Ask a question to find papers.</p></div> : evidence.map((paper, idx) => (
        <div key={idx} className={`p-4 rounded-xl border transition-all hover:shadow-md ${paper.isExternal ? "bg-purple-50/50 border-purple-100" : "bg-white/40 border-white/40"}`}>
          <div className="flex items-start justify-between gap-2 mb-1">
            <h4 className="font-semibold text-gray-900 text-sm leading-tight">{paper.title}</h4>
            <span className="text-xs font-medium text-blue-600 bg-blue-50 px-2 py-0.5 rounded-full whitespace-nowrap">{paper.year}</span>
          </div>
          <div className="flex items-center gap-2 mb-2">
            <span className="text-xs text-gray-500 truncate max-w-[150px]">{paper.authors}</span>
            {paper.isExternal && <span className="text-[10px] font-medium text-purple-600 bg-purple-100 px-1.5 py-0.5 rounded border border-purple-200">{paper.source || "External"}</span>}
          </div>
          <p className="text-xs text-gray-600 line-clamp-2 mb-2">{paper.abstract}</p>
          <div className="flex items-center justify-between mt-2">
            <div className="flex items-center gap-2">
              <span className="text-[10px] bg-gray-100 text-gray-600 px-1.5 py-0.5 rounded">Relevance: {Math.round(paper.relevance * 100)}%</span>
              {paper.citationCount !== undefined && <span className="text-[10px] text-gray-500">Cited by {paper.citationCount}</span>}
            </div>
            {paper.url && <a href={paper.url} target="_blank" rel="noopener noreferrer" className="text-xs text-blue-600 hover:text-blue-800 flex items-center gap-1">View ↗</a>}
          </div>
        </div>
      ))}
    </div>
  );

  const GapsPanel = () => (
    <div className="space-y-4 overflow-y-auto h-full pr-2 pb-20">
      {gaps.length === 0 ? <div className="text-center text-gray-500 mt-10"><p>No research gaps detected yet.</p><p className="text-xs mt-2">Ask about "missing research" or "gaps".</p></div> : gaps.map((gap, idx) => (
        <div key={idx} className="p-4 rounded-xl bg-amber-50/50 border border-amber-100 hover:shadow-md transition-all">
          <div className="flex items-center gap-2 mb-2"><span className="text-lg">💡</span><h4 className="font-semibold text-gray-900 text-sm">{gap.topic || gap.title || "Research Opportunity"}</h4></div>
          <p className="text-xs text-gray-700 mb-3 leading-relaxed">{gap.description}</p>
          {gap.reason && <div className="bg-white/50 rounded-lg p-2 mb-2"><span className="text-[10px] font-semibold text-amber-700 uppercase tracking-wider">Why this is a gap</span><p className="text-xs text-gray-600 mt-1">{gap.reason || gap.importance}</p></div>}
        </div>
      ))}
    </div>
  );

  const renderActivePanel = () => activeTab === "gaps" ? <GapsPanel /> : <EvidencePanel />;
  const tabs = [{ id: "evidence", label: "Papers", count: evidence.length, icon: "📄" }, { id: "gaps", label: "Gaps", count: gaps.length, icon: "🎯" }];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-amber-50">
      <nav className="sticky top-0 z-30 shadow-2xl border-b-4" style={{ backgroundColor: '#99be90ff', borderBottomColor: '#043915' }}>
        <div className="h-1.5 w-full" style={{ backgroundColor: '#043915' }}></div>
        <div className="mx-auto max-w-7xl px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-6">
              <div className="flex items-center gap-3">
                <div className="h-12 w-12 rounded-xl flex items-center justify-center shadow-2xl border-2 transform hover:scale-110 transition-transform" style={{ background: 'linear-gradient(135deg, #043915 0%, #0a5c2a 100%)', borderColor: '#043915' }}>
                  <span className="text-2xl">🔍</span>
                </div>
                <div>
                  <h1 className="text-xl font-bold text-white tracking-tight">Research Assistant</h1>
                  <p className="text-xs font-medium text-white/90">AI-Powered Academic Analysis</p>
                </div>
              </div>
              <div className="hidden md:block h-12 w-px bg-gradient-to-b from-transparent via-white/40 to-transparent"></div>
              <div className="hidden md:flex items-center gap-3 px-4 py-2 rounded-lg backdrop-blur-sm border-2 shadow-lg" style={{ backgroundColor: 'rgba(4, 57, 21, 0.3)', borderColor: '#043915' }}>
                <div className="p-1.5 rounded-lg" style={{ backgroundColor: '#287b43ff' }}>
                  <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
                  </svg>
                </div>
                <div>
                  <p className="text-xs text-white/70 font-medium">Database</p>
                  <p className="text-sm font-bold text-white">2,124 Papers</p>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <div className="hidden lg:flex items-center gap-2 px-3 py-2 rounded-lg bg-white/10 backdrop-blur-sm border" style={{ borderColor: '#043915' }}>
                <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
                <span className="text-sm font-semibold text-white">{messages.length}</span>
              </div>

              <div className="hidden lg:block h-10 w-px bg-gradient-to-b from-transparent via-white/40 to-transparent"></div>

              {evidence.length > 0 && (
                <div className="flex items-center gap-2 px-3 py-2 rounded-lg backdrop-blur-sm border-2 shadow-lg animate-pulse" style={{ backgroundColor: '#79c771ff', borderColor: '#043915' }}>
                  <span className="text-lg">📄</span>
                  <span className="text-sm font-bold text-black">{evidence.length}</span>
                </div>
              )}

              {gaps.length > 0 && (
                <div className="flex items-center gap-2 px-3 py-2 rounded-lg backdrop-blur-sm border-2 shadow-lg animate-pulse" style={{ backgroundColor: '#a3d5a2ff', borderColor: '#043915' }}>
                  <span className="text-lg">💡</span>
                  <span className="text-sm font-bold text-green">{gaps.length}</span>
                </div>
              )}

              {(evidence.length > 0 || gaps.length > 0) && (
                <div className="h-10 w-px bg-gradient-to-b from-transparent via-white/40 to-transparent"></div>
              )}

              <button
                onClick={() => {
                  setMessages([{ id: "welcome", role: "assistant", text: "Welcome! I retrieve papers from your database (2,124 papers) and use AI to generate natural language responses with citations.", createdAt: Date.now() }]);
                  setEvidence([]);
                  setGaps([]);
                }}
                className="p-2.5 rounded-lg backdrop-blur-sm border-2 transition-all shadow-lg hover:scale-110 group"
                style={{ backgroundColor: 'rgba(220, 38, 38, 0.8)', borderColor: '#634646ff' }}
                title="Clear session"
              >
                <svg className="w-5 h-5 text-white group-hover:rotate-12 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          </div>
        </div>

        <div className="h-1.5 bg-gradient-to-r via-opacity-100" style={{ background: `linear-gradient(90deg, #043915 0%, #0a5c2a 25%, #043915 50%, #0a5c2a 75%, #043915 100%)` }}></div>
      </nav>

      <main className="mx-auto max-w-7xl px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <GlassCard className="p-6" hover>
              <div className="flex flex-col h-[70vh]">
                <div className="flex items-center justify-between border-b border-white/10 pb-4 mb-4"><h2 className="text-lg font-semibold text-gray-900">💬 Conversational Analysis</h2></div>
                <div className="flex-1 overflow-y-auto space-y-4 pr-2 mb-4">
                  {messages.map((message) => (
                    <div key={message.id} className={`rounded-2xl p-4 ${message.role === "assistant" ? "bg-white/20 backdrop-blur-lg border border-white/20" : "bg-white/30 backdrop-blur-lg border border-white/30"}`}>
                      <div className="flex items-start gap-3">
                        <div className={`h-8 w-8 rounded-full flex items-center justify-center ${message.role === "assistant" ? "bg-blue-500/20" : "bg-green-500/20"}`}><span className="text-sm">{message.role === "assistant" ? "🤖" : "👤"}</span></div>
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <span className={`text-sm font-medium ${message.role === "assistant" ? "text-blue-700" : "text-green-700"}`}>{message.role === "assistant" ? "AI Assistant" : "You"}</span>
                            {message.intent && <span className="text-xs bg-white/30 px-2 py-0.5 rounded">{message.intent}</span>}
                            {message.paperCount > 0 && <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded">{message.paperCount} papers</span>}
                            {message.gapCount > 0 && <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded">{message.gapCount} gaps</span>}
                            {message.hasExternal && <span className="text-xs bg-purple-100 text-purple-700 px-2 py-0.5 rounded">🌐 External</span>}
                          </div>
                          <p className="text-gray-900 leading-relaxed whitespace-pre-wrap">{message.text}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                  {loading && (
                    <div className="rounded-2xl p-4 bg-white/20 backdrop-blur-lg border border-white/20">
                      <div className="flex items-center gap-3"><div className="h-8 w-8 rounded-full bg-blue-500/20 flex items-center justify-center"><span className="text-sm">🤖</span></div><div className="flex items-center gap-2 text-sm text-gray-600"><span>Analyzing...</span><LoadingDots /></div></div>
                    </div>
                  )}
                </div>
                <div className="flex items-end gap-3 rounded-2xl bg-white/20 backdrop-blur-lg p-4 border border-white/20">
                  <div className="flex-1"><textarea value={input} onChange={(e) => setInput(e.target.value)} onKeyPress={handleKeyPress} placeholder="Ask about research..." className="w-full rounded-xl bg-white/60 px-4 py-3 text-gray-900 placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-400 resize-none min-h-[60px]" rows={2} /></div>
                  <GlassButton onClick={handleSend} disabled={!input.trim() || loading} variant="accent">{loading ? <LoadingDots /> : 'Search'}</GlassButton>
                </div>
              </div>
            </GlassCard>
          </div>
          <div className="lg:col-span-1">
            <GlassCard className="p-6 h-[70vh] flex flex-col" hover>
              <h2 className="text-lg font-semibold text-gray-900 mb-4">📊 Retrieved Data</h2>
              <div className="grid grid-cols-2 gap-2 mb-4 bg-white/30 rounded-lg p-1">
                {tabs.map((tab) => (
                  <button key={tab.id} onClick={() => setActiveTab(tab.id)} className={`flex flex-col items-center py-2 rounded-md text-xs font-medium transition-all ${activeTab === tab.id ? "bg-white/80 text-black shadow-lg" : "bg-transparent text-gray-700 hover:bg-white/50"}`}>
                    <span className="text-base mb-1">{tab.icon}</span><span>{tab.label}</span>{tab.count > 0 && <span className="text-[10px] bg-black/10 px-1.5 rounded-full mt-1">{tab.count}</span>}
                  </button>
                ))}
              </div>
              <div className="flex-1 overflow-hidden">{renderActivePanel()}</div>
            </GlassCard>
          </div>
        </div>
      </main>
    </div>
  );
}