"""
Simplified coordinator graph for testing with Langgraph Studio.
"""
from typing import Dict, Any
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END


def create_coordinator_graph():
    """
    Create a simplified coordinator agent graph for testing.
    
    Returns:
        Compiled LangGraph for the coordinator agent
    """
    # Define the nodes
    def echo(state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Echo the user's message.
        
        Args:
            state: Current state
            
        Returns:
            Updated state
        """
        if state.get("messages"):
            last_message = state["messages"][-1]["content"]
            state["messages"].append({
                "role": "assistant",
                "content": f"You said: {last_message}"
            })
        return state
    
    # Create the graph
    workflow = StateGraph(Dict[str, Any])
    
    # Add nodes
    workflow.add_node("echo", echo)
    
    # Add edges
    workflow.add_edge("echo", END)
    
    # Set the entry point
    workflow.set_entry_point("echo")
    
    return workflow.compile()


def create_initial_state() -> Dict[str, Any]:
    """
    Create the initial state for the coordinator agent.
    
    Returns:
        Initial state dictionary
    """
    return {
        "messages": []
    }
