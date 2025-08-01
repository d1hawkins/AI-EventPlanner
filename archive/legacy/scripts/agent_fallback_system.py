"""
Intelligent fallback system for when real agents are unavailable.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class AgentFallbackSystem:
    """Manages fallback responses when real agents are unavailable"""
    
    def __init__(self):
        self.available_agents = set()
        self.unavailable_agents = set()
        self.fallback_usage_count = {}
    
    def register_agent_status(self, agent_type: str, available: bool):
        """Register whether an agent is available"""
        if available:
            self.available_agents.add(agent_type)
            self.unavailable_agents.discard(agent_type)
        else:
            self.unavailable_agents.add(agent_type)
            self.available_agents.discard(agent_type)
    
    def get_fallback_response(self, agent_type: str, message: str, conversation_id: str) -> Dict[str, Any]:
        """Generate intelligent fallback response"""
        
        # Track fallback usage
        self.fallback_usage_count[agent_type] = self.fallback_usage_count.get(agent_type, 0) + 1
        
        # Log fallback usage
        logger.warning(f"Using fallback for {agent_type} agent (usage count: {self.fallback_usage_count[agent_type]})")
        
        # Generate contextual response based on agent type
        fallback_responses = {
            'coordinator': self._coordinator_fallback(message),
            'resource_planning': self._resource_planning_fallback(message),
            'financial': self._financial_fallback(message),
            'stakeholder_management': self._stakeholder_fallback(message),
            'marketing_communications': self._marketing_fallback(message),
            'project_management': self._project_fallback(message),
            'analytics': self._analytics_fallback(message),
            'compliance_security': self._compliance_fallback(message)
        }
        
        response_text = fallback_responses.get(
            agent_type, 
            f"I apologize, but the {agent_type} agent is currently unavailable. Please try again later or contact support."
        )
        
        return {
            "response": response_text,
            "conversation_id": conversation_id,
            "agent_type": agent_type,
            "organization_id": None,
            "using_real_agent": False,
            "fallback_reason": "agent_unavailable",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _coordinator_fallback(self, message: str) -> str:
        """Coordinator-specific fallback response"""
        return """I'm the Event Coordinator, but I'm currently running in limited mode. 
        I can still help you with basic event planning questions, but my full AI capabilities are temporarily unavailable. 
        
        For immediate assistance, please:
        1. Check our event planning templates
        2. Review our planning checklist
        3. Contact our support team for urgent matters
        
        What specific aspect of event planning can I help you with today?"""
    
    def _resource_planning_fallback(self, message: str) -> str:
        """Resource planning fallback response"""
        return """I'm the Resource Planning agent, currently in limited mode. 
        
        For resource planning, I recommend:
        1. Review our standard resource templates
        2. Check our vendor directory
        3. Use our resource calculator tools
        
        What type of resources are you planning for your event?"""
    
    def _financial_fallback(self, message: str) -> str:
        """Financial planning fallback response"""
        return """I'm the Financial Planning agent, currently in limited mode.
        
        For budget planning, please:
        1. Use our budget templates
        2. Check our cost estimation guides
        3. Review vendor pricing information
        
        What's your estimated budget range for this event?"""
    
    def _stakeholder_fallback(self, message: str) -> str:
        """Stakeholder management fallback response"""
        return """I'm the Stakeholder Management agent, currently in limited mode.
        
        For stakeholder management:
        1. Use our stakeholder mapping templates
        2. Check our communication templates
        3. Review our engagement strategies
        
        Who are the key stakeholders for your event?"""
    
    def _marketing_fallback(self, message: str) -> str:
        """Marketing communications fallback response"""
        return """I'm the Marketing Communications agent, currently in limited mode.
        
        For marketing your event:
        1. Use our marketing templates
        2. Check our social media guides
        3. Review our promotional strategies
        
        What's your target audience for this event?"""
    
    def _project_fallback(self, message: str) -> str:
        """Project management fallback response"""
        return """I'm the Project Management agent, currently in limited mode.
        
        For project management:
        1. Use our project timeline templates
        2. Check our task management guides
        3. Review our milestone tracking tools
        
        What's the timeline for your event?"""
    
    def _analytics_fallback(self, message: str) -> str:
        """Analytics fallback response"""
        return """I'm the Analytics agent, currently in limited mode.
        
        For event analytics:
        1. Use our metrics tracking templates
        2. Check our reporting guides
        3. Review our KPI frameworks
        
        What metrics are most important for your event?"""
    
    def _compliance_fallback(self, message: str) -> str:
        """Compliance and security fallback response"""
        return """I'm the Compliance & Security agent, currently in limited mode.
        
        For compliance and security:
        1. Review our compliance checklists
        2. Check our security guidelines
        3. Consult our legal requirements guide
        
        What type of event are you planning and what compliance requirements do you need to meet?"""
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        total_agents = len(self.available_agents) + len(self.unavailable_agents)
        available_count = len(self.available_agents)
        
        if total_agents == 0:
            status = "unknown"
        elif available_count == total_agents:
            status = "healthy"
        elif available_count >= total_agents / 2:
            status = "degraded"
        else:
            status = "unhealthy"
        
        return {
            "status": status,
            "available_agents": list(self.available_agents),
            "unavailable_agents": list(self.unavailable_agents),
            "fallback_usage": self.fallback_usage_count,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def reset_usage_counts(self):
        """Reset fallback usage counters"""
        self.fallback_usage_count = {}
        logger.info("Fallback usage counters reset")
    
    def get_usage_statistics(self) -> Dict[str, Any]:
        """Get detailed usage statistics"""
        total_fallbacks = sum(self.fallback_usage_count.values())
        
        return {
            "total_fallback_requests": total_fallbacks,
            "fallback_by_agent": self.fallback_usage_count.copy(),
            "most_used_fallback": max(self.fallback_usage_count.items(), key=lambda x: x[1]) if self.fallback_usage_count else None,
            "timestamp": datetime.utcnow().isoformat()
        }

# Global fallback system instance
fallback_system = AgentFallbackSystem()

def get_fallback_system() -> AgentFallbackSystem:
    """Get the global fallback system instance"""
    return fallback_system

def register_agent_availability(agent_type: str, available: bool):
    """Convenience function to register agent availability"""
    fallback_system.register_agent_status(agent_type, available)

def get_intelligent_fallback(agent_type: str, message: str, conversation_id: str) -> Dict[str, Any]:
    """Convenience function to get fallback response"""
    return fallback_system.get_fallback_response(agent_type, message, conversation_id)

def get_system_health() -> Dict[str, Any]:
    """Convenience function to get system health status"""
    return fallback_system.get_system_status()
