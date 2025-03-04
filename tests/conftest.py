import pytest
import os
import sys
from typing import Dict, Any, Generator

# Add the parent directory to the path so we can import the app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.graphs.coordinator_graph import create_coordinator_graph, create_initial_state


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
