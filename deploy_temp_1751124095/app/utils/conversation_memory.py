"""
Conversation Memory for Conversational Agent

This module provides conversation context tracking and memory management
for the conversational event planning agent.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json


class ConversationMemory:
    """
    Manages conversation context and memory for the conversational agent.
    
    Tracks conversation history, context, and provides intelligent
    summarization and reference capabilities.
    """
    
    def __init__(self, max_memory_items: int = 50):
        """
        Initialize the ConversationMemory.
        
        Args:
            max_memory_items: Maximum number of memory items to retain
        """
        self.max_memory_items = max_memory_items
        self.memory_types = {
            "user_preferences": {},
            "event_context": {},
            "decision_history": [],
            "topic_transitions": [],
            "clarifications": [],
            "recommendations_given": [],
            "user_reactions": []
        }
    
    def add_memory(self, memory_type: str, content: Dict[str, Any], context: Optional[str] = None) -> None:
        """
        Add a memory item to the conversation memory.
        
        Args:
            memory_type: Type of memory (user_preferences, event_context, etc.)
            content: Memory content
            context: Optional context information
        """
        timestamp = datetime.utcnow().isoformat()
        
        memory_item = {
            "timestamp": timestamp,
            "content": content,
            "context": context
        }
        
        if memory_type in ["decision_history", "topic_transitions", "clarifications", 
                          "recommendations_given", "user_reactions"]:
            # List-based memories
            if memory_type not in self.memory_types:
                self.memory_types[memory_type] = []
            
            self.memory_types[memory_type].append(memory_item)
            
            # Trim if exceeding max items
            if len(self.memory_types[memory_type]) > self.max_memory_items:
                self.memory_types[memory_type] = self.memory_types[memory_type][-self.max_memory_items:]
        
        else:
            # Dictionary-based memories
            if memory_type not in self.memory_types:
                self.memory_types[memory_type] = {}
            
            # For preferences and context, merge with existing
            if isinstance(content, dict):
                self.memory_types[memory_type].update(content)
            else:
                self.memory_types[memory_type][timestamp] = content
    
    def get_memory(self, memory_type: str, limit: Optional[int] = None) -> Any:
        """
        Retrieve memory items of a specific type.
        
        Args:
            memory_type: Type of memory to retrieve
            limit: Maximum number of items to return (for list-based memories)
            
        Returns:
            Memory items
        """
        if memory_type not in self.memory_types:
            return [] if memory_type in ["decision_history", "topic_transitions", 
                                       "clarifications", "recommendations_given", 
                                       "user_reactions"] else {}
        
        memory = self.memory_types[memory_type]
        
        if isinstance(memory, list) and limit:
            return memory[-limit:]
        
        return memory
    
    def track_user_preference(self, preference_type: str, value: Any, confidence: float = 1.0) -> None:
        """
        Track a user preference discovered during conversation.
        
        Args:
            preference_type: Type of preference (venue_style, budget_priority, etc.)
            value: Preference value
            confidence: Confidence level (0.0 to 1.0)
        """
        self.add_memory("user_preferences", {
            preference_type: {
                "value": value,
                "confidence": confidence,
                "discovered_at": datetime.utcnow().isoformat()
            }
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
    
    def track_topic_transition(self, from_topic: str, to_topic: str, trigger: str) -> None:
        """
        Track transitions between conversation topics.
        
        Args:
            from_topic: Previous topic
            to_topic: New topic
            trigger: What triggered the transition
        """
        self.add_memory("topic_transitions", {
            "from_topic": from_topic,
            "to_topic": to_topic,
            "trigger": trigger,
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
    
    def track_user_reaction(self, trigger: str, reaction_type: str, details: str) -> None:
        """
        Track user reactions to questions, suggestions, or information.
        
        Args:
            trigger: What triggered the reaction
            reaction_type: Type of reaction (positive, negative, neutral, confused)
            details: Details about the reaction
        """
        self.add_memory("user_reactions", {
            "trigger": trigger,
            "reaction_type": reaction_type,
            "details": details,
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
        preferences = self.get_memory("user_preferences")
        if preferences:
            pref_summary = []
            for pref_type, pref_data in preferences.items():
                if isinstance(pref_data, dict) and "value" in pref_data:
                    confidence = pref_data.get("confidence", 1.0)
                    confidence_text = "strongly prefers" if confidence > 0.8 else "prefers" if confidence > 0.5 else "might prefer"
                    pref_summary.append(f"{confidence_text} {pref_type}: {pref_data['value']}")
            
            if pref_summary:
                summary_parts.append(f"User preferences: {'; '.join(pref_summary)}")
        
        # Recent decisions summary
        decisions = self.get_memory("decision_history", limit=5)
        if decisions:
            decision_summary = []
            for decision in decisions[-3:]:  # Last 3 decisions
                decision_summary.append(f"{decision['content']['decision_type']}: {decision['content']['decision']}")
            
            if decision_summary:
                summary_parts.append(f"Recent decisions: {'; '.join(decision_summary)}")
        
        # Recent clarifications
        clarifications = self.get_memory("clarifications", limit=3)
        if clarifications:
            clarity_summary = []
            for clarification in clarifications:
                clarity_summary.append(clarification['content']['clarity_gained'])
            
            if clarity_summary:
                summary_parts.append(f"Clarifications made: {'; '.join(clarity_summary)}")
        
        # Recommendation patterns
        recommendations = self.get_memory("recommendations_given", limit=5)
        if recommendations:
            accepted_recs = [r for r in recommendations if r['content'].get('accepted') is True]
            rejected_recs = [r for r in recommendations if r['content'].get('accepted') is False]
            
            if accepted_recs:
                summary_parts.append(f"User has accepted recommendations about: {', '.join([r['content']['recommendation_type'] for r in accepted_recs])}")
            
            if rejected_recs:
                summary_parts.append(f"User has rejected recommendations about: {', '.join([r['content']['recommendation_type'] for r in rejected_recs])}")
        
        if not summary_parts:
            return "No significant conversation context available."
        
        return " | ".join(summary_parts)
    
    def get_relevant_context(self, current_topic: str, question_type: str = None) -> Dict[str, Any]:
        """
        Get context relevant to the current topic or question.
        
        Args:
            current_topic: Current conversation topic
            question_type: Type of question being asked
            
        Returns:
            Relevant context information
        """
        context = {
            "relevant_preferences": {},
            "relevant_decisions": [],
            "relevant_clarifications": [],
            "topic_history": [],
            "recommendation_patterns": {}
        }
        
        # Get relevant preferences
        preferences = self.get_memory("user_preferences")
        for pref_type, pref_data in preferences.items():
            if current_topic in pref_type or (question_type and question_type in pref_type):
                context["relevant_preferences"][pref_type] = pref_data
        
        # Get relevant decisions
        decisions = self.get_memory("decision_history")
        for decision in decisions:
            decision_content = decision['content']
            if (current_topic in decision_content['decision_type'] or 
                (question_type and question_type in decision_content['decision_type'])):
                context["relevant_decisions"].append(decision_content)
        
        # Get relevant clarifications
        clarifications = self.get_memory("clarifications")
        for clarification in clarifications:
            clarification_content = clarification['content']
            if (current_topic in clarification_content['clarity_gained'] or
                (question_type and question_type in clarification_content['question'])):
                context["relevant_clarifications"].append(clarification_content)
        
        # Get topic transition history
        transitions = self.get_memory("topic_transitions", limit=10)
        for transition in transitions:
            transition_content = transition['content']
            if (current_topic == transition_content['to_topic'] or 
                current_topic == transition_content['from_topic']):
                context["topic_history"].append(transition_content)
        
        # Get recommendation patterns
        recommendations = self.get_memory("recommendations_given")
        topic_recommendations = [r for r in recommendations 
                               if current_topic in r['content']['recommendation_type']]
        
        if topic_recommendations:
            accepted = sum(1 for r in topic_recommendations if r['content'].get('accepted') is True)
            total = len(topic_recommendations)
            context["recommendation_patterns"] = {
                "total_given": total,
                "acceptance_rate": accepted / total if total > 0 else 0,
                "recent_reactions": [r['content']['user_reaction'] for r in topic_recommendations[-3:] 
                                   if r['content'].get('user_reaction')]
            }
        
        return context
    
    def should_reference_previous_context(self, current_topic: str, question_type: str = None) -> bool:
        """
        Determine if previous context should be referenced in the current question.
        
        Args:
            current_topic: Current conversation topic
            question_type: Type of question being asked
            
        Returns:
            True if previous context should be referenced
        """
        relevant_context = self.get_relevant_context(current_topic, question_type)
        
        # Reference if we have relevant preferences
        if relevant_context["relevant_preferences"]:
            return True
        
        # Reference if we have relevant decisions
        if relevant_context["relevant_decisions"]:
            return True
        
        # Reference if we've had clarifications on this topic
        if relevant_context["relevant_clarifications"]:
            return True
        
        # Reference if we've given recommendations on this topic before
        if relevant_context["recommendation_patterns"].get("total_given", 0) > 0:
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
        relevant_context = self.get_relevant_context(current_topic, question_type)
        references = []
        
        # Reference relevant preferences
        for pref_type, pref_data in relevant_context["relevant_preferences"].items():
            if isinstance(pref_data, dict) and "value" in pref_data:
                references.append(f"I noticed you prefer {pref_data['value']} for {pref_type.replace('_', ' ')}")
        
        # Reference relevant decisions
        for decision in relevant_context["relevant_decisions"][-2:]:  # Last 2 relevant decisions
            references.append(f"Earlier you decided on {decision['decision']} for {decision['decision_type']}")
        
        # Reference clarifications
        for clarification in relevant_context["relevant_clarifications"][-1:]:  # Last relevant clarification
            references.append(f"Based on our earlier discussion about {clarification['clarity_gained']}")
        
        # Reference recommendation patterns
        patterns = relevant_context["recommendation_patterns"]
        if patterns.get("acceptance_rate", 0) > 0.7:
            references.append(f"You've been receptive to my {current_topic} recommendations")
        elif patterns.get("acceptance_rate", 0) < 0.3 and patterns.get("total_given", 0) > 1:
            references.append(f"I'll focus on different {current_topic} options since my previous suggestions weren't quite right")
        
        if references:
            return f"{references[0]}. " if len(references) == 1 else f"{references[0]}, and {references[1]}. "
        
        return ""
    
    def cleanup_old_memories(self, days_to_keep: int = 7) -> None:
        """
        Clean up old memory items to prevent memory bloat.
        
        Args:
            days_to_keep: Number of days of memories to keep
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        cutoff_iso = cutoff_date.isoformat()
        
        for memory_type, memory_data in self.memory_types.items():
            if isinstance(memory_data, list):
                # Filter list-based memories
                self.memory_types[memory_type] = [
                    item for item in memory_data 
                    if item.get("timestamp", "") > cutoff_iso
                ]
            elif isinstance(memory_data, dict):
                # Filter dictionary-based memories with timestamps as keys
                filtered_dict = {}
                for key, value in memory_data.items():
                    if isinstance(value, dict) and "discovered_at" in value:
                        if value["discovered_at"] > cutoff_iso:
                            filtered_dict[key] = value
                    else:
                        # Keep non-timestamped entries (like current preferences)
                        filtered_dict[key] = value
                
                self.memory_types[memory_type] = filtered_dict
    
    def export_memory_summary(self) -> Dict[str, Any]:
        """
        Export a summary of the conversation memory for analysis or persistence.
        
        Returns:
            Memory summary dictionary
        """
        summary = {
            "export_timestamp": datetime.utcnow().isoformat(),
            "memory_stats": {},
            "key_insights": {},
            "conversation_patterns": {}
        }
        
        # Memory statistics
        for memory_type, memory_data in self.memory_types.items():
            if isinstance(memory_data, list):
                summary["memory_stats"][memory_type] = len(memory_data)
            elif isinstance(memory_data, dict):
                summary["memory_stats"][memory_type] = len(memory_data)
        
        # Key insights
        preferences = self.get_memory("user_preferences")
        if preferences:
            summary["key_insights"]["user_preferences"] = {
                k: v.get("value") if isinstance(v, dict) else v 
                for k, v in preferences.items()
            }
        
        decisions = self.get_memory("decision_history", limit=10)
        if decisions:
            summary["key_insights"]["recent_decisions"] = [
                {
                    "type": d['content']['decision_type'],
                    "decision": d['content']['decision'],
                    "timestamp": d['content']['timestamp']
                }
                for d in decisions[-5:]
            ]
        
        # Conversation patterns
        recommendations = self.get_memory("recommendations_given")
        if recommendations:
            total_recs = len(recommendations)
            accepted_recs = sum(1 for r in recommendations if r['content'].get('accepted') is True)
            
            summary["conversation_patterns"]["recommendation_acceptance"] = {
                "total_given": total_recs,
                "total_accepted": accepted_recs,
                "acceptance_rate": accepted_recs / total_recs if total_recs > 0 else 0
            }
        
        transitions = self.get_memory("topic_transitions")
        if transitions:
            topic_counts = {}
            for transition in transitions:
                to_topic = transition['content']['to_topic']
                topic_counts[to_topic] = topic_counts.get(to_topic, 0) + 1
            
            summary["conversation_patterns"]["topic_frequency"] = topic_counts
        
        return summary
