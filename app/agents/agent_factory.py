"""
Agent factory for creating tenant-aware agents.

This module provides functionality to create agents with tenant context
and subscription-based access controls.
"""

from typing import Dict, Any, Optional, Type, List
from sqlalchemy.orm import Session

from app.db.models_updated import Event
from app.state.tenant_aware_manager import get_tenant_aware_state_manager
from app.subscription.feature_control import get_feature_control, FeatureNotAvailableError
from app.utils.llm_factory import get_llm
from app.graphs.coordinator_graph import create_coordinator_graph, create_initial_state as create_coordinator_initial_state
from app.graphs.resource_planning_graph import create_resource_planning_graph, create_initial_state as create_resource_planning_initial_state
from app.graphs.financial_graph import create_financial_graph, create_initial_state as create_financial_initial_state
from app.graphs.stakeholder_management_graph import create_stakeholder_management_graph, create_initial_state as create_stakeholder_initial_state
from app.graphs.marketing_communications_graph import create_marketing_communications_graph, create_initial_state as create_marketing_initial_state
from app.graphs.project_management_graph import create_project_management_graph, create_initial_state as create_project_initial_state
from app.graphs.analytics_graph import create_analytics_graph, create_initial_state as create_analytics_initial_state
from app.graphs.compliance_security_graph import create_compliance_security_graph, create_initial_state as create_compliance_initial_state


class AgentFactory:
    """
    Agent factory for creating tenant-aware agents.
    
    This class provides functionality to create agents with tenant context
    and subscription-based access controls.
    """
    
    def __init__(self, db: Session, organization_id: Optional[int] = None):
        """
        Initialize the agent factory.
        
        Args:
            db: Database session
            organization_id: The organization ID for tenant context
        """
        self.db = db
        self.organization_id = organization_id
        self.state_manager = get_tenant_aware_state_manager(organization_id=organization_id)
        self.feature_control = get_feature_control(db=db, organization_id=organization_id)
    
    def create_agent(self, agent_type: str, conversation_id: str, **kwargs) -> Any:
        """
        Create a tenant-aware agent with subscription-based access controls.
        
        Args:
            agent_type: The type of agent to create
            conversation_id: The conversation ID
            **kwargs: Additional arguments for agent creation
            
        Returns:
            The created agent
            
        Raises:
            FeatureNotAvailableError: If the agent is not available for the current subscription
            ValueError: If the agent type is not supported
        """
        # Check if the organization can access this agent type
        self.feature_control.require_agent_access(agent_type)
        
        # Get event_id from kwargs if provided
        event_id = kwargs.get('event_id')
        
        # If event_id is provided, load event data
        event_context = None
        if event_id:
            try:
                # Get event from database
                event = self.db.query(Event).filter(Event.id == event_id).first()
                if event:
                    # Create event context
                    event_context = {
                        "event_id": event.id,
                        "title": event.title,
                        "description": event.description,
                        "start_date": event.start_date.isoformat() if event.start_date else None,
                        "end_date": event.end_date.isoformat() if event.end_date else None,
                        "location": event.location,
                        "attendee_count": event.attendee_count,
                        "event_type": event.event_type,
                        "budget": event.budget
                    }
            except Exception as e:
                print(f"Error loading event data: {str(e)}")
        
        # Create the agent based on type
        if agent_type == "coordinator":
            return self._create_coordinator_agent(conversation_id, event_context=event_context, **kwargs)
        elif agent_type == "resource_planning":
            return self._create_resource_planning_agent(conversation_id, event_context=event_context, **kwargs)
        elif agent_type == "financial":
            return self._create_financial_agent(conversation_id, event_context=event_context, **kwargs)
        elif agent_type == "stakeholder_management":
            return self._create_stakeholder_management_agent(conversation_id, event_context=event_context, **kwargs)
        elif agent_type == "marketing_communications":
            return self._create_marketing_communications_agent(conversation_id, event_context=event_context, **kwargs)
        elif agent_type == "project_management":
            return self._create_project_management_agent(conversation_id, event_context=event_context, **kwargs)
        elif agent_type == "analytics":
            return self._create_analytics_agent(conversation_id, event_context=event_context, **kwargs)
        elif agent_type == "compliance_security":
            return self._create_compliance_security_agent(conversation_id, event_context=event_context, **kwargs)
        else:
            raise ValueError(f"Unsupported agent type: {agent_type}")
    
    def _create_coordinator_agent(self, conversation_id: str, event_context=None, **kwargs) -> Any:
        """
        Create a tenant-aware coordinator agent.
        
        Args:
            conversation_id: The conversation ID
            event_context: Optional event context data
            **kwargs: Additional arguments for agent creation
            
        Returns:
            The created coordinator agent
        """
        # Get or create the state
        state = self.state_manager.get_conversation_state(conversation_id)
        if not state:
            # Create initial state with tenant context
            initial_state = create_coordinator_initial_state()
            initial_state["organization_id"] = self.organization_id
            initial_state["agent_type"] = "coordinator"  # Ensure agent_type is set
            
            # Add event context if provided
            if event_context:
                initial_state["event_context"] = event_context
                
            self.state_manager.create_initial_state(conversation_id, initial_state)
            state = initial_state
        elif event_context and "event_context" not in state:
            # Add event context to existing state if not already present
            state["event_context"] = event_context
            self.state_manager.update_conversation_state(conversation_id, state)
        
        # Ensure all required fields are present for the coordinator agent
        # The agent type is "coordinator" since we're in the _create_coordinator_agent method
            # Set default phase if missing
            if "current_phase" not in state:
                state["current_phase"] = "information_collection"
            
            # Set default event_details if missing
            if "event_details" not in state:
                state["event_details"] = {
                    "event_type": None,
                    "title": None,
                    "description": None,
                    "attendee_count": None,
                    "scale": None,
                    "timeline_start": None,
                    "timeline_end": None
                }
            
            # Set default requirements if missing
            if "requirements" not in state:
                state["requirements"] = {
                    "stakeholders": [],
                    "resources": [],
                    "risks": [],
                    "success_criteria": [],
                    "budget": {},
                    "location": {}
                }
            
            # Set default information_collected if missing
            if "information_collected" not in state:
                state["information_collected"] = {
                    "basic_details": False,
                    "timeline": False,
                    "budget": False,
                    "location": False,
                    "stakeholders": False,
                    "resources": False,
                    "success_criteria": False,
                    "risks": False
                }
            
            # Set default agent_assignments if missing
            if "agent_assignments" not in state:
                state["agent_assignments"] = []
            
            # Set default next_steps if missing
            if "next_steps" not in state:
                state["next_steps"] = ["gather_event_details"]
            
            # Update the state with all the default values
            self.state_manager.update_conversation_state(conversation_id, state)
        
        # Create the agent graph
        agent_graph = create_coordinator_graph()
        
        # Add tenant context to the state if not present
        if self.organization_id and "organization_id" not in state:
            state["organization_id"] = self.organization_id
            self.state_manager.update_conversation_state(conversation_id, state)
        
        # Return the agent with state
        return {
            "graph": agent_graph,
            "state": state,
            "conversation_id": conversation_id,
            "organization_id": self.organization_id
        }
    
    def _create_resource_planning_agent(self, conversation_id: str, event_context=None, **kwargs) -> Any:
        """
        Create a tenant-aware resource planning agent.
        
        Args:
            conversation_id: The conversation ID
            event_context: Optional event context data
            **kwargs: Additional arguments for agent creation
            
        Returns:
            The created resource planning agent
        """
        # Get or create the state
        state = self.state_manager.get_conversation_state(conversation_id)
        if not state:
            # Create initial state with tenant context
            initial_state = create_resource_planning_initial_state()
            initial_state["organization_id"] = self.organization_id
            initial_state["agent_type"] = "resource_planning"  # Ensure agent_type is set
            
            # Add event context if provided
            if event_context:
                initial_state["event_context"] = event_context
                
            self.state_manager.create_initial_state(conversation_id, initial_state)
            state = initial_state
        elif event_context and "event_context" not in state:
            # Add event context to existing state if not already present
            state["event_context"] = event_context
            self.state_manager.update_conversation_state(conversation_id, state)
        
        # Create the agent graph
        agent_graph = create_resource_planning_graph()
        
        # Add tenant context to the state if not present
        if self.organization_id and "organization_id" not in state:
            state["organization_id"] = self.organization_id
            self.state_manager.update_conversation_state(conversation_id, state)
        
        # Return the agent with state
        return {
            "graph": agent_graph,
            "state": state,
            "conversation_id": conversation_id,
            "organization_id": self.organization_id
        }
    
    def _create_financial_agent(self, conversation_id: str, event_context=None, **kwargs) -> Any:
        """
        Create a tenant-aware financial agent.
        
        Args:
            conversation_id: The conversation ID
            event_context: Optional event context data
            **kwargs: Additional arguments for agent creation
            
        Returns:
            The created financial agent
        """
        # Get or create the state
        state = self.state_manager.get_conversation_state(conversation_id)
        if not state:
            # Create initial state with tenant context
            initial_state = create_financial_initial_state()
            initial_state["organization_id"] = self.organization_id
            initial_state["agent_type"] = "financial"  # Ensure agent_type is set
            
            # Add event context if provided
            if event_context:
                initial_state["event_context"] = event_context
                
            self.state_manager.create_initial_state(conversation_id, initial_state)
            state = initial_state
        elif event_context and "event_context" not in state:
            # Add event context to existing state if not already present
            state["event_context"] = event_context
            self.state_manager.update_conversation_state(conversation_id, state)
        
        # Create the agent graph
        agent_graph = create_financial_graph()
        
        # Add tenant context to the state if not present
        if self.organization_id and "organization_id" not in state:
            state["organization_id"] = self.organization_id
            self.state_manager.update_conversation_state(conversation_id, state)
        
        # Return the agent with state
        return {
            "graph": agent_graph,
            "state": state,
            "conversation_id": conversation_id,
            "organization_id": self.organization_id
        }
    
    def _create_stakeholder_management_agent(self, conversation_id: str, event_context=None, **kwargs) -> Any:
        """
        Create a tenant-aware stakeholder management agent.
        
        Args:
            conversation_id: The conversation ID
            event_context: Optional event context data
            **kwargs: Additional arguments for agent creation
            
        Returns:
            The created stakeholder management agent
        """
        # Get or create the state
        state = self.state_manager.get_conversation_state(conversation_id)
        if not state:
            # Create initial state with tenant context
            initial_state = create_stakeholder_initial_state()
            initial_state["organization_id"] = self.organization_id
            initial_state["agent_type"] = "stakeholder_management"  # Ensure agent_type is set
            
            # Add event context if provided
            if event_context:
                initial_state["event_context"] = event_context
                
            self.state_manager.create_initial_state(conversation_id, initial_state)
            state = initial_state
        elif event_context and "event_context" not in state:
            # Add event context to existing state if not already present
            state["event_context"] = event_context
            self.state_manager.update_conversation_state(conversation_id, state)
        
        # Create the agent graph
        agent_graph = create_stakeholder_management_graph()
        
        # Add tenant context to the state if not present
        if self.organization_id and "organization_id" not in state:
            state["organization_id"] = self.organization_id
            self.state_manager.update_conversation_state(conversation_id, state)
        
        # Return the agent with state
        return {
            "graph": agent_graph,
            "state": state,
            "conversation_id": conversation_id,
            "organization_id": self.organization_id
        }
    
    def _create_marketing_communications_agent(self, conversation_id: str, event_context=None, **kwargs) -> Any:
        """
        Create a tenant-aware marketing communications agent.
        
        Args:
            conversation_id: The conversation ID
            event_context: Optional event context data
            **kwargs: Additional arguments for agent creation
            
        Returns:
            The created marketing communications agent
        """
        # Get or create the state
        state = self.state_manager.get_conversation_state(conversation_id)
        if not state:
            # Create initial state with tenant context
            initial_state = create_marketing_initial_state()
            initial_state["organization_id"] = self.organization_id
            initial_state["agent_type"] = "marketing_communications"  # Ensure agent_type is set
            
            # Add event context if provided
            if event_context:
                initial_state["event_context"] = event_context
                
            self.state_manager.create_initial_state(conversation_id, initial_state)
            state = initial_state
        elif event_context and "event_context" not in state:
            # Add event context to existing state if not already present
            state["event_context"] = event_context
            self.state_manager.update_conversation_state(conversation_id, state)
        
        # Create the agent graph
        agent_graph = create_marketing_communications_graph()
        
        # Add tenant context to the state if not present
        if self.organization_id and "organization_id" not in state:
            state["organization_id"] = self.organization_id
            self.state_manager.update_conversation_state(conversation_id, state)
        
        # Return the agent with state
        return {
            "graph": agent_graph,
            "state": state,
            "conversation_id": conversation_id,
            "organization_id": self.organization_id
        }
    
    def _create_project_management_agent(self, conversation_id: str, event_context=None, **kwargs) -> Any:
        """
        Create a tenant-aware project management agent.
        
        Args:
            conversation_id: The conversation ID
            event_context: Optional event context data
            **kwargs: Additional arguments for agent creation
            
        Returns:
            The created project management agent
        """
        # Get or create the state
        state = self.state_manager.get_conversation_state(conversation_id)
        if not state:
            # Create initial state with tenant context
            initial_state = create_project_initial_state()
            initial_state["organization_id"] = self.organization_id
            initial_state["agent_type"] = "project_management"  # Ensure agent_type is set
            
            # Add event context if provided
            if event_context:
                initial_state["event_context"] = event_context
                
            self.state_manager.create_initial_state(conversation_id, initial_state)
            state = initial_state
        elif event_context and "event_context" not in state:
            # Add event context to existing state if not already present
            state["event_context"] = event_context
            self.state_manager.update_conversation_state(conversation_id, state)
        
        # Create the agent graph
        agent_graph = create_project_management_graph()
        
        # Add tenant context to the state if not present
        if self.organization_id and "organization_id" not in state:
            state["organization_id"] = self.organization_id
            self.state_manager.update_conversation_state(conversation_id, state)
        
        # Return the agent with state
        return {
            "graph": agent_graph,
            "state": state,
            "conversation_id": conversation_id,
            "organization_id": self.organization_id
        }
    
    def _create_analytics_agent(self, conversation_id: str, event_context=None, **kwargs) -> Any:
        """
        Create a tenant-aware analytics agent.
        
        Args:
            conversation_id: The conversation ID
            event_context: Optional event context data
            **kwargs: Additional arguments for agent creation
            
        Returns:
            The created analytics agent
        """
        # Get or create the state
        state = self.state_manager.get_conversation_state(conversation_id)
        if not state:
            # Create initial state with tenant context
            initial_state = create_analytics_initial_state()
            initial_state["organization_id"] = self.organization_id
            initial_state["agent_type"] = "analytics"  # Ensure agent_type is set
            
            # Add event context if provided
            if event_context:
                initial_state["event_context"] = event_context
                
            self.state_manager.create_initial_state(conversation_id, initial_state)
            state = initial_state
        elif event_context and "event_context" not in state:
            # Add event context to existing state if not already present
            state["event_context"] = event_context
            self.state_manager.update_conversation_state(conversation_id, state)
        
        # Create the agent graph
        agent_graph = create_analytics_graph()
        
        # Add tenant context to the state if not present
        if self.organization_id and "organization_id" not in state:
            state["organization_id"] = self.organization_id
            self.state_manager.update_conversation_state(conversation_id, state)
        
        # Return the agent with state
        return {
            "graph": agent_graph,
            "state": state,
            "conversation_id": conversation_id,
            "organization_id": self.organization_id
        }
    
    def _create_compliance_security_agent(self, conversation_id: str, event_context=None, **kwargs) -> Any:
        """
        Create a tenant-aware compliance security agent.
        
        Args:
            conversation_id: The conversation ID
            event_context: Optional event context data
            **kwargs: Additional arguments for agent creation
            
        Returns:
            The created compliance security agent
        """
        # Get or create the state
        state = self.state_manager.get_conversation_state(conversation_id)
        if not state:
            # Create initial state with tenant context
            initial_state = create_compliance_initial_state()
            initial_state["organization_id"] = self.organization_id
            initial_state["agent_type"] = "compliance_security"  # Ensure agent_type is set
            
            # Add event context if provided
            if event_context:
                initial_state["event_context"] = event_context
                
            self.state_manager.create_initial_state(conversation_id, initial_state)
            state = initial_state
        elif event_context and "event_context" not in state:
            # Add event context to existing state if not already present
            state["event_context"] = event_context
            self.state_manager.update_conversation_state(conversation_id, state)
        
        # Create the agent graph
        agent_graph = create_compliance_security_graph()
        
        # Add tenant context to the state if not present
        if self.organization_id and "organization_id" not in state:
            state["organization_id"] = self.organization_id
            self.state_manager.update_conversation_state(conversation_id, state)
        
        # Return the agent with state
        return {
            "graph": agent_graph,
            "state": state,
            "conversation_id": conversation_id,
            "organization_id": self.organization_id
        }


def get_agent_factory(db: Session, organization_id: Optional[int] = None) -> AgentFactory:
    """
    Get an agent factory instance.
    
    Args:
        db: Database session
        organization_id: The organization ID for tenant context
        
    Returns:
        AgentFactory instance
    """
    return AgentFactory(db=db, organization_id=organization_id)
