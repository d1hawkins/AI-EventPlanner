#!/usr/bin/env python3
"""
Test script to diagnose issues with specialized agents in the event planning system.
This script runs a test conversation with the coordinator agent and logs all interactions
with specialized agents to help identify why they might not be responding.
"""
import asyncio
import json
import os
import traceback
from datetime import datetime

from app.graphs.coordinator_graph import create_coordinator_graph, create_initial_state
from app.config import OPENAI_API_KEY, LLM_MODEL, LLM_PROVIDER
from app.utils.logging_utils import setup_logger, log_agent_invocation, log_agent_response, log_agent_error

# Set up logger
logger = setup_logger("test_specialized_agents", log_level="DEBUG")

# Test conversation for a wine festival
TEST_CONVERSATION = [
    "I need help planning a wine festival.",
    "It's a wine festival with music and vendors and local wines.",
    "Budget = 12000",
    "We expect about 500 attendees.",
    "It will be held in Napa Valley.",
    "The festival will be in September 2025.",
    "We need recommendations for vendors and entertainment.",
    "We need to promote the event on social media.",
    "The title is 'Napa Valley Wine Celebration'.",
    "It will be a two-day event featuring local wineries, food vendors, and live music performances.",
    "We want to have both indoor and outdoor spaces with parking for at least 300 cars.",
    "Success criteria include selling at least 400 tickets and getting positive feedback from attendees.",
    "The main risk is bad weather, so we need contingency plans.",
    "Local wineries and food vendors will be our key stakeholders.",
    "Please generate a proposal for this event.",
    "I approve the proposal. Please proceed with implementation."
]

async def run_test():
    """
    Run a test conversation with the coordinator agent and log all interactions
    with specialized agents.
    """
    # Check if API key is set
    if LLM_PROVIDER.lower() == "openai" and not OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY environment variable is not set.")
        print("Error: OPENAI_API_KEY environment variable is not set.")
        print("Please set it in your .env file or export it in your shell.")
        return
    
    logger.info(f"Starting test with LLM provider: {LLM_PROVIDER}, model: {LLM_MODEL}")
    print(f"Using LLM provider: {LLM_PROVIDER}, model: {LLM_MODEL}")
    
    try:
        # Create the coordinator graph
        logger.info("Initializing coordinator agent...")
        print("Initializing coordinator agent...")
        coordinator_graph = create_coordinator_graph()
        
        # Create initial state
        state = create_initial_state()
        
        # Add initial system message
        state["messages"].append({
            "role": "system",
            "content": "The conversation has started. The coordinator agent will help plan your event.",
            "ephemeral": True
        })
        
        # Add a dummy user message to trigger the initial response
        state["messages"].append({
            "role": "user",
            "content": "Hello, I need help planning an event."
        })
        
        # Run the coordinator graph for initial response
        logger.info("Invoking coordinator graph for initial response")
        try:
            result = coordinator_graph.invoke(state)
            logger.info("Coordinator graph invocation successful")
        except Exception as e:
            logger.error(f"Error during initial coordinator graph invocation: {str(e)}", exc_info=True)
            print(f"Error: Failed to get initial response from coordinator agent: {str(e)}")
            return
        
        # Print the assistant's first message
        assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
        if assistant_messages:
            response = assistant_messages[-1]["content"]
            logger.info(f"Initial coordinator response: {response[:100]}...")
            print("\nCoordinator Agent:", response)
        
        # Run through the test conversation
        for i, message in enumerate(TEST_CONVERSATION):
            print(f"\n--- Test Message {i+1}/{len(TEST_CONVERSATION)} ---")
            print(f"User: {message}")
            logger.info(f"Test message {i+1}: {message}")
            
            # Add user message to state
            result["messages"].append({
                "role": "user",
                "content": message
            })
            
            # Run the coordinator graph
            logger.info(f"Invoking coordinator graph with test message {i+1}")
            try:
                result = coordinator_graph.invoke(result)
                logger.info(f"Coordinator graph invocation successful. Current phase: {result['current_phase']}")
                
                # Log agent assignments if any
                if "agent_assignments" in result and result["agent_assignments"]:
                    for assignment in result["agent_assignments"]:
                        if assignment.get("status") == "pending":
                            logger.info(f"Agent assignment: {assignment['agent_type']} - {assignment['task']}")
                        elif assignment.get("status") == "completed":
                            logger.info(f"Completed agent assignment: {assignment['agent_type']} - {assignment['task']}")
                        elif assignment.get("status") == "failed":
                            logger.error(f"Failed agent assignment: {assignment['agent_type']} - {assignment['task']}")
                            if "error" in assignment:
                                logger.error(f"Assignment error: {assignment['error']}")
            except Exception as e:
                error_msg = f"Error during coordinator graph invocation: {str(e)}"
                logger.error(error_msg, exc_info=True)
                print(f"Error: {error_msg}")
                continue
            
            # Print the assistant's response
            assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
            if assistant_messages:
                response = assistant_messages[-1]["content"]
                logger.info(f"Coordinator response: {response[:100]}...")
                print("\nCoordinator Agent:", response)
            else:
                logger.warning("No assistant message found in response")
                print("\nCoordinator Agent: [No response]")
        
        # After the conversation, check if any specialized agents were invoked
        print("\n--- Test Results ---")
        if "agent_assignments" in result and result["agent_assignments"]:
            print(f"Total agent assignments: {len(result['agent_assignments'])}")
            
            # Count assignments by status
            completed = sum(1 for a in result["agent_assignments"] if a.get("status") == "completed")
            pending = sum(1 for a in result["agent_assignments"] if a.get("status") == "pending")
            failed = sum(1 for a in result["agent_assignments"] if a.get("status") == "failed")
            
            print(f"Completed: {completed}")
            print(f"Pending: {pending}")
            print(f"Failed: {failed}")
            
            # Print details of failed assignments
            if failed > 0:
                print("\nFailed Assignments:")
                for assignment in result["agent_assignments"]:
                    if assignment.get("status") == "failed":
                        print(f"- Agent: {assignment['agent_type']}")
                        print(f"  Task: {assignment['task']}")
                        if "error" in assignment:
                            print(f"  Error: {assignment['error']['error_message']}")
                            print(f"  Error Type: {assignment['error']['error_type']}")
            
            # Print details of pending assignments
            if pending > 0:
                print("\nPending Assignments:")
                for assignment in result["agent_assignments"]:
                    if assignment.get("status") == "pending":
                        print(f"- Agent: {assignment['agent_type']}")
                        print(f"  Task: {assignment['task']}")
                        print(f"  Assigned At: {assignment['assigned_at']}")
        else:
            print("No agent assignments were created during the test.")
        
        # Check if any agent results were stored
        if "agent_results" in result and result["agent_results"]:
            print("\nAgent Results:")
            for agent_type, agent_results in result["agent_results"].items():
                print(f"- {agent_type}:")
                for key, value in agent_results.items():
                    if isinstance(value, (dict, list)):
                        print(f"  * {key}: {type(value).__name__} with {len(value)} items")
                    else:
                        print(f"  * {key}: {value}")
        else:
            print("\nNo agent results were stored during the test.")
        
        # Print log file location
        log_files = [f for f in os.listdir("logs") if f.startswith("test_specialized_agents_")]
        if log_files:
            latest_log = max(log_files, key=lambda x: os.path.getmtime(os.path.join("logs", x)))
            print(f"\nLog file: logs/{latest_log}")
            print("Check the log file for detailed information about the test run.")
        
    except Exception as e:
        error_msg = f"Unexpected error in test: {str(e)}"
        logger.critical(error_msg, exc_info=True)
        print(f"Critical error: {error_msg}")
        print(f"Stack trace: {traceback.format_exc()}")

if __name__ == "__main__":
    # Run the test
    asyncio.run(run_test())
