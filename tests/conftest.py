import pytest
import os
import sys
import importlib.util
from typing import Dict, Any, Generator

# Add the parent directory to the path so we can import the app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Check if langchain_google_genai is available
google_genai_available = importlib.util.find_spec("langchain_google_genai") is not None

# Import coordinator_graph functions
try:
    from app.graphs.coordinator_graph import create_coordinator_graph, create_initial_state
except ImportError as e:
    if "No module named 'langchain_google_genai'" in str(e):
        # Create mock functions for testing when Google AI is not available
        def create_coordinator_graph():
            return None
            
        def create_initial_state():
            return {
                "messages": [],
                "event_details": {
                    "event_type": None,
                    "title": None,
                    "description": None,
                    "attendee_count": None,
                    "scale": None,
                    "timeline_start": None,
                    "timeline_end": None
                },
                "requirements": {
                    "stakeholders": [],
                    "resources": [],
                    "risks": [],
                    "success_criteria": [],
                    "budget": {},
                    "location": {}
                },
                "agent_assignments": [],
                "current_phase": "information_collection",
                "next_steps": ["gather_event_details"],
                "proposal": None,
                "information_collected": {
                    "basic_details": False,
                    "timeline": False,
                    "budget": False,
                    "location": False,
                    "stakeholders": False,
                    "resources": False,
                    "success_criteria": False,
                    "risks": False
                },
                "agent_results": {}
            }
    else:
        raise


@pytest.fixture
def coordinator_graph():
    """Fixture for the coordinator graph."""
    return create_coordinator_graph()


@pytest.fixture
def initial_state():
    """Fixture for the initial state."""
    return create_initial_state()


@pytest.fixture
def sample_event_state():
    """Fixture for a sample event state with some data."""
    state = create_initial_state()
    
    # Set up state with event details and requirements
    state["event_details"] = {
        "event_type": "Tech Conference",
        "scale": "Medium",
        "budget": 150000,
        "timeline_start": "2025-05-10",
        "timeline_end": "2025-05-12"
    }
    
    state["requirements"] = {
        "stakeholders": ["Sponsors", "Speakers", "Attendees"],
        "resources": ["Venue", "Catering", "AV Equipment"],
        "risks": ["Speaker cancellations", "Lower than expected attendance"],
        "success_criteria": ["Positive attendee feedback", "Sponsor satisfaction"]
    }
    
    state["current_phase"] = "requirement_analysis"
    state["next_steps"] = ["delegate_tasks"]
    
    return state
