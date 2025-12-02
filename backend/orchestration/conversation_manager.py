# backend/orchestration/conversation_manager.py
"""
Manages conversation state in Redis
"""
import json
import uuid
from typing import Optional, List
from datetime import datetime, timedelta
from core.cache import cache_manager
from .models import ConversationContext, Message, Intent

class ConversationManager:
    """Manages conversation sessions in Redis"""
    
    def __init__(self, ttl_hours: int = 24):
        """
        Args:
            ttl_hours: Time-to-live for sessions in hours (default 24)
        """
        self.cache = cache_manager
        self.ttl_seconds = ttl_hours * 3600
        self.key_prefix = "conversation:"
    
    def create_session(self) -> str:
        """Create new conversation session
        
        Returns:
            session_id: Unique session identifier
        """
        session_id = str(uuid.uuid4())
        context = ConversationContext(session_id=session_id)
        
        # Save to Redis
        self._save_context(context)
        
        print(f"✅ Created conversation session: {session_id}")
        return session_id
   
    def get_context(self, session_id: str) -> Optional[ConversationContext]:
        """Retrieve conversation context
        
        Args:
            session_id: Session identifier
            
        Returns:
            ConversationContext or None if not found
        """
        key = f"{self.key_prefix}{session_id}"
        cached_data = self.cache.get_cached(key)
        
        if not cached_data:
            print(f"⚠️ Session not found: {session_id}")
            return None
        
        try:
            context = ConversationContext.from_dict(cached_data)
            print(f"📖 Retrieved session: {session_id} ({len(context.messages)} messages)")
            return context
        except Exception as e:
            print(f"❌ Error loading context: {e}")
            return None
    
    def add_message(self, session_id: str, message: Message) -> bool:
        """Add message to conversation
        
        Args:
            session_id: Session identifier
            message: Message to add
            
        Returns:
            bool: Success status
        """
        context = self.get_context(session_id)
        if not context:
            print(f"❌ Cannot add message: session {session_id} not found")
            return False
        
        context.add_message(message)
        return self._save_context(context)
    
    def track_paper(self, session_id: str, paper_id: str):
        """Track mentioned paper
        
        Args:
            session_id: Session identifier
            paper_id: Paper ID to track
        """
        context = self.get_context(session_id)
        if context and paper_id not in context.mentioned_papers:
            context.mentioned_papers.append(paper_id)
            self._save_context(context)
    
    def track_gap(self, session_id: str, gap: dict):
        """Track detected research gap
        
        Args:
            session_id: Session identifier
            gap: Gap object to track
        """
        context = self.get_context(session_id)
        if context:
            context.detected_gaps.append(gap)
            self._save_context(context)
    
    def track_topic(self, session_id: str, topic: str):
        """Track discussed topic
        
        Args:
            session_id: Session identifier
            topic: Topic to track
        """
        context = self.get_context(session_id)
        if context and topic not in context.mentioned_topics:
            context.mentioned_topics.append(topic)
            self._save_context(context)
    
    def set_intent(self, session_id: str, intent: Intent):
        """Set current conversation intent
        
        Args:
            session_id: Session identifier
            intent: Intent enum value
        """
        context = self.get_context(session_id)
        if context:
            context.current_intent = intent
            self._save_context(context)
    
    def delete_session(self, session_id: str) -> bool:
        """Delete conversation session
        
        Args:
            session_id: Session identifier
            
        Returns:
            bool: Success status
        """
        key = f"{self.key_prefix}{session_id}"
        if self.cache.enabled and self.cache.redis_client:
            try:
                self.cache.redis_client.delete(key)
                print(f"🗑️ Deleted session: {session_id}")
                return True
            except Exception as e:
                print(f"❌ Error deleting session: {e}")
                return False
        return False
    
    def list_active_sessions(self, hours: int = 24) -> List[str]:
        """List active sessions within time window
        
        Args:
            hours: Look back window in hours
            
        Returns:
            List of active session IDs
        """
        if not self.cache.enabled or not self.cache.redis_client:
            return []
        
        try:
            pattern = f"{self.key_prefix}*"
            keys = self.cache.redis_client.keys(pattern)
            
            cutoff = datetime.now() - timedelta(hours=hours)
            active_sessions = []
            
            for key in keys:
                session_id = key.replace(self.key_prefix, "")
                context = self.get_context(session_id)
                if context and context.last_active > cutoff:
                    active_sessions.append(session_id)
            
            return active_sessions
        except Exception as e:
            print(f"❌ Error listing sessions: {e}")
            return []
    
    def _save_context(self, context: ConversationContext) -> bool:
        """Save context to Redis
        
        Args:
            context: ConversationContext to save
            
        Returns:
            bool: Success status
        """
        key = f"{self.key_prefix}{context.session_id}"
        data = context.to_dict()
        
        return self.cache.set_cached(key, data, ttl=self.ttl_seconds)
