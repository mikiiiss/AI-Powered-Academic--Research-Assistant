# backend/orchestration/models.py
"""
Data models for conversational orchestrator
"""
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum
import json

class Intent(Enum):
    """User query intent types"""
    SEARCH = "search"  # Find papers
    GAP_DETECTION = "gap_detection"  # Identify research gaps
    EVIDENCE = "evidence"  # Find evidence/quotes
    CITATION = "citation"  # Generate citations
    CHAT_WITH_PAPER = "chat_with_paper"  # Ask about specific paper
    SYNTHESIS = "synthesis"  # Synthesize literature review
    FOLLOW_UP = "follow_up"  # Continue previous conversation

class SearchDepth(Enum):
    """Search depth levels"""
    QUICK = "quick"  # 10-50 papers, local DB only
    STANDARD = "standard"  # 100-250 papers, local + MCP
    DEEP = "deep"  # 500-1000 papers, full MCP search

@dataclass
class Message:
    """Single conversation message"""
    role: str  # "user" or "assistant"
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Message':
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)

@dataclass
class ConversationContext:
    """Complete conversation state"""
    session_id: str
    messages: List[Message] = field(default_factory=list)
    mentioned_papers: List[str] = field(default_factory=list)  # Paper IDs
    detected_gaps: List[Dict] = field(default_factory=list)  # Gap objects
    mentioned_topics: List[str] = field(default_factory=list)  # Topics discussed
    current_intent: Optional[Intent] = None
    search_depth: SearchDepth = SearchDepth.STANDARD
    created_at: datetime = field(default_factory=datetime.now)
    last_active: datetime = field(default_factory=datetime.now)
    
    def add_message(self, message: Message):
        """Add message and update last_active"""
        self.messages.append(message)
        self.last_active = datetime.now()
    
    def get_recent_messages(self, n: int = 5) -> List[Message]:
        """Get last n messages"""
        return self.messages[-n:]
    
    def to_dict(self) -> Dict:
        return {
            'session_id': self.session_id,
            'messages': [m.to_dict() for m in self.messages],
            'mentioned_papers': self.mentioned_papers,
            'detected_gaps': self.detected_gaps,
            'mentioned_topics': self.mentioned_topics,
            'current_intent': self.current_intent.value if self.current_intent else None,
            'search_depth': self.search_depth.value,
            'created_at': self.created_at.isoformat(),
            'last_active': self.last_active.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ConversationContext':
        # Convert string timestamps back to datetime
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['last_active'] = datetime.fromisoformat(data['last_active'])
        
        # Convert messages
        data['messages'] = [Message.from_dict(m) for m in data['messages']]
        
        # Convert intent
        if data.get('current_intent'):
            data['current_intent'] = Intent(data['current_intent'])
        
        # Convert search depth
        data['search_depth'] = SearchDepth(data['search_depth'])
        
        return cls(**data)

@dataclass
class ToolResult:
    """Result from a tool execution"""
    tool_name: str
    success: bool
    data: Any
    error: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'tool_name': self.tool_name,
            'success': self.success,
            'data': self.data,
            'error': self.error,
            'execution_time': self.execution_time,
            'metadata': self.metadata
        }
