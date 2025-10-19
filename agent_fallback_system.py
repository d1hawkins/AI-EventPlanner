#!/usr/bin/env python3
"""
Agent Fallback System

Provides fallback responses when specific agents are unavailable.
"""

from typing import Dict, Set, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class AgentFallbackSystem:
    """
    Manages fallback responses for unavailable agents.
    """
    
    def __init__(self):
        self.available_agents: Set[str] = set()
        self.unavailable_agents: Set[str] = set()
        self.fallback_usage_count: Dict[str, int] = {}
        
        # Fallback response templates
        self.fallback_templates = {
            'coordinator': "I'm the coordinator agent fallback. I can help with general event planning coordination tasks. How can I assist you today?",
            'resource_planning': "I'm the resource planning fallback. I can provide basic guidance on resource allocation and planning for your event.",
            'financial': "I'm the financial planning fallback. I can help with basic budget considerations and financial planning guidance.",
            'stakeholder_management': "I'm the stakeholder management fallback. I can provide general advice on managing event stakeholders and communications.",
            'marketing_communications': "I'm the marketing communications fallback. I can offer basic marketing and communication strategies for your event.",
            'project_management': "I'm the project management fallback. I can provide general project management guidance and task organization tips.",
            'analytics': "I'm the analytics fallback. I can help with basic event metrics and performance tracking considerations.",
            'compliance_security': "I'm the compliance and security fallback. I can provide general guidance on event compliance and security considerations."
        }
    
    def register_agent_status(self, agent_type: str, is_available: bool) -> None:
        """
        Register the availability status of an agent.
        
        Args:
            agent_type: The type/name of the agent
            is_available: Whether the agent is currently available
        """
        if is_available:
            self.available_agents.add(agent_type)
            self.unavailable_agents.discard(agent_type)
        else:
            self.unavailable_agents.add(agent_type)
            self.available_agents.discard(agent_type)
        
        logger.info(f"Agent {agent_type} registered as {'available' if is_available else 'unavailable'}")
    
    def get_fallback_response(
        self, 
        agent_type: str, 
        message: str, 
        conversation_id: str
    ) -> Dict[str, Any]:
        """
        Get a fallback response for an unavailable agent.
        
        Args:
            agent_type: The type of agent requested
            message: The user's message
            conversation_id: The conversation identifier
            
        Returns:
            Dictionary with response details
        """
        # Check if agent is available
        if agent_type in self.available_agents:
            return {
                'using_real_agent': True,
                'fallback_reason': None,
                'response': f"Connecting to real {agent_type} agent...",
                'agent_type': agent_type,
                'conversation_id': conversation_id,
                'timestamp': datetime.now().isoformat()
            }
        
        # Agent is unavailable, use fallback
        self.fallback_usage_count[agent_type] = self.fallback_usage_count.get(agent_type, 0) + 1
        
        fallback_reason = f"The {agent_type} agent is currently unavailable"
        fallback_response = self.fallback_templates.get(
            agent_type, 
            f"I'm a fallback assistant for {agent_type}. I can provide basic guidance while the specialized agent is unavailable."
        )
        
        # Customize response based on the message context
        if "plan" in message.lower():
            fallback_response += " I understand you're looking for planning assistance. Let me provide some general guidance."
        elif "budget" in message.lower() or "cost" in message.lower():
            fallback_response += " I see you're asking about budget/cost considerations. I can offer some basic financial guidance."
        elif "help" in message.lower():
            fallback_response += " I'm here to help with your request to the best of my fallback capabilities."
        
        logger.warning(f"Using fallback for {agent_type} agent (usage count: {self.fallback_usage_count[agent_type]})")
        
        return {
            'using_real_agent': False,
            'fallback_reason': fallback_reason,
            'response': fallback_response,
            'agent_type': agent_type,
            'conversation_id': conversation_id,
            'timestamp': datetime.now().isoformat(),
            'fallback_usage_count': self.fallback_usage_count[agent_type]
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get the current status of the fallback system.
        
        Returns:
            Dictionary with system status information
        """
        return {
            'available_agents': list(self.available_agents),
            'unavailable_agents': list(self.unavailable_agents),
            'fallback_usage_count': dict(self.fallback_usage_count),
            'total_fallback_usage': sum(self.fallback_usage_count.values()),
            'timestamp': datetime.now().isoformat()
        }
    
    def reset_usage_counts(self) -> None:
        """Reset all fallback usage counts."""
        self.fallback_usage_count.clear()
        logger.info("Fallback usage counts reset")
    
    def is_agent_available(self, agent_type: str) -> bool:
        """
        Check if a specific agent is available.
        
        Args:
            agent_type: The agent type to check
            
        Returns:
            True if the agent is available, False otherwise
        """
        return agent_type in self.available_agents
