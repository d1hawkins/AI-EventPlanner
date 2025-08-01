"""
Database-backed Persistent Conversation Memory for Conversational Agents

This module provides conversation context tracking and memory management
that persists to the database for the conversational event planning agents.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from app.db.base import Base

class ConversationMemoryRecord(Base):
    """Database model for storing conversation memory."""
    __tablename__ = "conversation_memory"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String, index=True, nullable=False)
    organization_id = Column(Integer, index=True, nullable=True)
    memory_type = Column(String, nullable=False)  # user_preferences, decision_history, etc.
    content = Column(Text, nullable=False)  # JSON serialized content
    context = Column(Text, nullable=True)  # Optional context information
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<ConversationMemoryRecord(conversation_id='{self.conversation_id}', memory_type='{self.memory_type}')>"


class PersistentConversationMemory:
    """
    Database-backed conversation memory manager for conversational agents.
    
    Tracks conversation history, context, and provides intelligent
    summarization and reference capabilities with database persistence.
    """
    
    def __init__(self, db: Session, conversation_id: str, organization_id: Optional[int] = None, max_memory_items: int = 50):
        """
        Initialize the PersistentConversationMemory.
        
        Args:
            db: Database session
            conversation_id: Unique conversation identifier
            organization_id: Organization ID for tenant isolation
            max_memory_items: Maximum number of memory items to retain per type
        """
        self.db = db
        self.conversation_id = conversation_id
        self.organization_id = organization_id
        self.max_memory_items = max_memory_items
        
        # Cache for frequently accessed memory
        self._memory_cache = {}
        self._cache_timestamp = None
        self._cache_ttl = 300  # 5 minutes cache TTL
    
    def _is_cache_valid(self) -> bool:
        """Check if the memory cache is still valid."""
        if self._cache_timestamp is None:
            return False
        return (datetime.utcnow() - self._cache_timestamp).total_seconds() < self._cache_ttl
    
    def _refresh_cache(self) -> None:
        """Refresh the memory cache from database."""
        try:
            # Load all memory records for this conversation
            records = self.db.query(ConversationMemoryRecord).filter(
                ConversationMemoryRecord.conversation_id == self.conversation_id
            ).order_by(ConversationMemoryRecord.timestamp.desc()).all()
            
            # Organize by memory type
            self._memory_cache = {}
            for record in records:
                memory_type = record.memory_type
                if memory_type not in self._memory_cache:
                    self._memory_cache[memory_type] = []
                
                try:
                    content = json.loads(record.content)
                    memory_item = {
                        "id": record.id,
                        "timestamp": record.timestamp.isoformat(),
                        "content": content,
                        "context": record.context
                    }
                    self._memory_cache[memory_type].append(memory_item)
                except json.JSONDecodeError:
                    # Skip invalid JSON records
                    continue
            
            self._cache_timestamp = datetime.utcnow()
            
        except Exception as e:
            # If cache refresh fails, use empty cache
            self._memory_cache = {}
            self._cache_timestamp = datetime.utcnow()
    
    def add_memory(self, memory_type: str, content: Dict[str, Any], context: Optional[str] = None) -> None:
        """
        Add a memory item to the conversation memory.
        
        Args:
            memory_type: Type of memory (user_preferences, event_context, etc.)
            content: Memory content
            context: Optional context information
        """
        try:
            # Create database record
            memory_record = ConversationMemoryRecord(
                conversation_id=self.conversation_id,
                organization_id=self.organization_id,
                memory_type=memory_type,
                content=json.dumps(content),
                context=context,
                timestamp=datetime.utcnow()
            )
            
            self.db.add(memory_record)
            self.db.commit()
            
            # Invalidate cache to force refresh
            self._cache_timestamp = None
            
            # Clean up old memories if we exceed the limit
            self._cleanup_old_memories(memory_type)
            
        except Exception as e:
            self.db.rollback()
            # Log error but don't fail the conversation
            print(f"Error adding memory: {e}")
    
    def get_memory(self, memory_type: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Retrieve memory items of a specific type.
        
        Args:
            memory_type: Type of memory to retrieve
            limit: Maximum number of items to return
            
        Returns:
            List of memory items
        """
        if not self._is_cache_valid():
            self._refresh_cache()
        
        memories = self._memory_cache.get(memory_type, [])
        
        if limit:
            return memories[:limit]
        
        return memories
    
    def track_user_preference(self, preference_type: str, value: Any, confidence: float = 1.0) -> None:
        """
        Track a user preference discovered during conversation.
        
        Args:
            preference_type: Type of preference (venue_style, budget_priority, etc.)
            value: Preference value
            confidence: Confidence level (0.0 to 1.0)
        """
        self.add_memory("user_preferences", {
            "preference_type": preference_type,
            "value": value,
            "confidence": confidence,
            "discovered_at": datetime.utcnow().isoformat()
        })
    
    def track_decision(self, decision_type: str, decision: str, reasoning: str, 
                      alternatives_considered: List[str] = None) -> None:
        """
        Track a decision made during the conversation.
        
        Args:
            decision_type: Type of decision (venue, date, budget, etc.)
            decision: The decision made
            reasoning: Reasoning behind the decision
            alternatives_considered: Other options that were considered
        """
        self.add_memory("decision_history", {
            "decision_type": decision_type,
            "decision": decision,
            "reasoning": reasoning,
            "alternatives_considered": alternatives_considered or [],
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def track_clarification(self, question: str, answer: str, clarity_gained: str) -> None:
        """
        Track clarifications made during the conversation.
        
        Args:
            question: Clarification question asked
            answer: User's answer
            clarity_gained: What was clarified
        """
        self.add_memory("clarifications", {
            "question": question,
            "answer": answer,
            "clarity_gained": clarity_gained,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def track_recommendation(self, recommendation_type: str, recommendation: str, 
                           user_reaction: str = None, accepted: bool = None) -> None:
        """
        Track recommendations given and user reactions.
        
        Args:
            recommendation_type: Type of recommendation
            recommendation: The recommendation given
            user_reaction: User's reaction to the recommendation
            accepted: Whether the recommendation was accepted
        """
        self.add_memory("recommendations_given", {
            "recommendation_type": recommendation_type,
            "recommendation": recommendation,
            "user_reaction": user_reaction,
            "accepted": accepted,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def get_context_summary(self, focus_area: Optional[str] = None) -> str:
        """
        Generate a summary of the conversation context.
        
        Args:
            focus_area: Optional focus area for the summary
            
        Returns:
            Context summary text
        """
        summary_parts = []
        
        # User preferences summary
        preferences = self.get_memory("user_preferences", limit=10)
        if preferences:
            pref_summary = []
            for pref_item in preferences[:5]:  # Last 5 preferences
                pref_data = pref_item['content']
                confidence = pref_data.get("confidence", 1.0)
                confidence_text = "strongly prefers" if confidence > 0.8 else "prefers" if confidence > 0.5 else "might prefer"
                pref_summary.append(f"{confidence_text} {pref_data['preference_type']}: {pref_data['value']}")
            
            if pref_summary:
                summary_parts.append(f"User preferences: {'; '.join(pref_summary)}")
        
        # Recent decisions summary
        decisions = self.get_memory("decision_history", limit=5)
        if decisions:
            decision_summary = []
            for decision_item in decisions[:3]:  # Last 3 decisions
                decision_data = decision_item['content']
                decision_summary.append(f"{decision_data['decision_type']}: {decision_data['decision']}")
            
            if decision_summary:
                summary_parts.append(f"Recent decisions: {'; '.join(decision_summary)}")
        
        # Recent clarifications
        clarifications = self.get_memory("clarifications", limit=3)
        if clarifications:
            clarity_summary = []
            for clarification_item in clarifications:
                clarity_data = clarification_item['content']
                clarity_summary.append(clarity_data['clarity_gained'])
            
            if clarity_summary:
                summary_parts.append(f"Clarifications made: {'; '.join(clarity_summary)}")
        
        if not summary_parts:
            return "No significant conversation context available."
        
        return " | ".join(summary_parts)
    
    def should_reference_previous_context(self, current_topic: str, question_type: str = None) -> bool:
        """
        Determine if previous context should be referenced in the current question.
        
        Args:
            current_topic: Current conversation topic
            question_type: Type of question being asked
            
        Returns:
            True if previous context should be referenced
        """
        # Check for relevant preferences
        preferences = self.get_memory("user_preferences", limit=10)
        for pref_item in preferences:
            pref_data = pref_item['content']
            if current_topic in pref_data.get('preference_type', '') or (question_type and question_type in pref_data.get('preference_type', '')):
                return True
        
        # Check for relevant decisions
        decisions = self.get_memory("decision_history", limit=10)
        for decision_item in decisions:
            decision_data = decision_item['content']
            if current_topic in decision_data.get('decision_type', '') or (question_type and question_type in decision_data.get('decision_type', '')):
                return True
        
        # Check for relevant clarifications
        clarifications = self.get_memory("clarifications", limit=5)
        for clarification_item in clarifications:
            clarification_data = clarification_item['content']
            if current_topic in clarification_data.get('clarity_gained', '') or (question_type and question_type in clarification_data.get('question', '')):
                return True
        
        return False
    
    def get_context_reference_text(self, current_topic: str, question_type: str = None) -> str:
        """
        Generate text that references relevant previous context.
        
        Args:
            current_topic: Current conversation topic
            question_type: Type of question being asked
            
        Returns:
            Context reference text
        """
        references = []
        
        # Reference relevant preferences
        preferences = self.get_memory("user_preferences", limit=10)
        for pref_item in preferences[:2]:  # Last 2 relevant preferences
            pref_data = pref_item['content']
            if current_topic in pref_data.get('preference_type', '') or (question_type and question_type in pref_data.get('preference_type', '')):
                references.append(f"I noticed you prefer {pref_data['value']} for {pref_data['preference_type'].replace('_', ' ')}")
        
        # Reference relevant decisions
        decisions = self.get_memory("decision_history", limit=5)
        for decision_item in decisions[:2]:  # Last 2 relevant decisions
            decision_data = decision_item['content']
            if current_topic in decision_data.get('decision_type', '') or (question_type and question_type in decision_data.get('decision_type', '')):
                references.append(f"Earlier you decided on {decision_data['decision']} for {decision_data['decision_type']}")
        
        if references:
            return f"{references[0]}. " if len(references) == 1 else f"{references[0]}, and {references[1]}. "
        
        return ""
    
    def _cleanup_old_memories(self, memory_type: str) -> None:
        """
        Clean up old memory items to prevent memory bloat.
        
        Args:
            memory_type: Type of memory to clean up
        """
        try:
            # Count current memories of this type
            count = self.db.query(ConversationMemoryRecord).filter(
                ConversationMemoryRecord.conversation_id == self.conversation_id,
                ConversationMemoryRecord.memory_type == memory_type
            ).count()
            
            if count > self.max_memory_items:
                # Delete oldest memories beyond the limit
                excess_count = count - self.max_memory_items
                oldest_records = self.db.query(ConversationMemoryRecord).filter(
                    ConversationMemoryRecord.conversation_id == self.conversation_id,
                    ConversationMemoryRecord.memory_type == memory_type
                ).order_by(ConversationMemoryRecord.timestamp.asc()).limit(excess_count).all()
                
                for record in oldest_records:
                    self.db.delete(record)
                
                self.db.commit()
                
        except Exception as e:
            self.db.rollback()
            # Log error but don't fail the conversation
            print(f"Error cleaning up old memories: {e}")
    
    def export_memory_summary(self) -> Dict[str, Any]:
        """
        Export a summary of the conversation memory for analysis.
        
        Returns:
            Memory summary dictionary
        """
        if not self._is_cache_valid():
            self._refresh_cache()
        
        summary = {
            "export_timestamp": datetime.utcnow().isoformat(),
            "conversation_id": self.conversation_id,
            "organization_id": self.organization_id,
            "memory_stats": {},
            "key_insights": {},
            "conversation_patterns": {}
        }
        
        # Memory statistics
        for memory_type, memories in self._memory_cache.items():
            summary["memory_stats"][memory_type] = len(memories)
        
        # Key insights
        preferences = self.get_memory("user_preferences", limit=10)
        if preferences:
            summary["key_insights"]["user_preferences"] = {
                pref['content']['preference_type']: pref['content']['value']
                for pref in preferences[:5]
            }
        
        decisions = self.get_memory("decision_history", limit=10)
        if decisions:
            summary["key_insights"]["recent_decisions"] = [
                {
                    "type": d['content']['decision_type'],
                    "decision": d['content']['decision'],
                    "timestamp": d['content']['timestamp']
                }
                for d in decisions[:5]
            ]
        
        # Conversation patterns
        recommendations = self.get_memory("recommendations_given", limit=20)
        if recommendations:
            total_recs = len(recommendations)
            accepted_recs = sum(1 for r in recommendations if r['content'].get('accepted') is True)
            
            summary["conversation_patterns"]["recommendation_acceptance"] = {
                "total_given": total_recs,
                "total_accepted": accepted_recs,
                "acceptance_rate": accepted_recs / total_recs if total_recs > 0 else 0
            }
        
        return summary


def get_persistent_conversation_memory(db: Session, conversation_id: str, organization_id: Optional[int] = None) -> PersistentConversationMemory:
    """
    Get a persistent conversation memory instance.
    
    Args:
        db: Database session
        conversation_id: Unique conversation identifier
        organization_id: Organization ID for tenant isolation
        
    Returns:
        PersistentConversationMemory instance
    """
    return PersistentConversationMemory(
        db=db,
        conversation_id=conversation_id,
        organization_id=organization_id
    )
