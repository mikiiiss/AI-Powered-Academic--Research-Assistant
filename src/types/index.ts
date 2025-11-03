// types/index.ts
export interface EvidenceSpan {
  id: string;
  sourceTitle: string;
  venue: string;
  year: number;
  quote: string;
  citations?: number;
  relevance?: number;
}

export interface CitationRef {
  spanId: string;
  label: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  text: string;
  citations?: CitationRef[];
  createdAt?: number;
  researchGaps?: string[];
  recommendations?: string[];
  trends?: string[];
}

export interface ResearchGap {
  id: string;
  type: "methodology" | "application" | "technical" | "citation";
  description: string;
  confidence: number;
}

export interface Recommendation {
  id: string;
  paperTitle: string;
  reason: string;
  citations: number;
  relevance: number;
}

export interface CitationNode {
  id: string;
  label: string;
  year: number;
  citations: number;
  group: string;
}

export interface CitationLink {
  source: string;
  target: string;
  strength: number;
}

export interface CitationGraph {
  nodes: CitationNode[];
  links: CitationLink[];
}

export interface GapItem {
  id: string;
  title: string;
  whyItMatters: string;
  suggestion: string;
  linkedEvidenceIds: string[];
  severity: "high" | "medium" | "low";
  confidence?: number;
}