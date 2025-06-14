import asyncio
import json
import os
import traceback
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env.coordinator file with override
load_dotenv(".env.coordinator", override=True)

# Force environment variables for OpenAI
os.environ["LLM_PROVIDER"] = "openai"
os.environ["LLM_MODEL"] = "gpt-4"

from app.graphs.coordinator_graph import create_coordinator_graph, create_initial_state
from app.config import OPENAI_API_KEY, LLM_MODEL, LLM_PROVIDER
from app.utils.logging_utils import setup_logger, log_agent_invocation, log_agent_response, log_agent_error, log_state_update


# Set up logger
logger = setup_logger("coordinator", log_level="DEBUG")


async def run_coordinator_chat():
    """
    Run an interactive chat with the coordinator agent.
    """
    # Check if API key is set
    if LLM_PROVIDER.lower() == "openai" and not OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY environment variable is not set.")
        print("Error: OPENAI_API_KEY environment variable is not set.")
        print("Please set it in your .env.coordinator file or export it in your shell.")
        return
    
    logger.info(f"Starting coordinator chat with LLM provider: {LLM_PROVIDER}, model: {LLM_MODEL}")
    print(f"Using LLM provider: {LLM_PROVIDER}, model: {LLM_MODEL}")
    
    try:
        # Create the coordinator graph
        logger.info("Initializing coordinator agent...")
        print("Initializing coordinator agent...")
        coordinator_graph = create_coordinator_graph()
        
        # Create initial state
        state = create_initial_state()
        log_state_update(logger, "initial_state", "Created initial state")
        
        # Add initial system message (marked as ephemeral so it won't be displayed in the UI)
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
        logger.info("Added initial user message to state")
        
        # Add initial assistant message
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
    
        # Main conversation loop
        print("\nType 'exit' to end the conversation.")
        print("Type 'status' to see the current state of the event planning.")
        print("Type 'proposal' to generate a proposal based on the information collected so far.")
        print("Type 'approve' to approve the proposal and proceed with implementation.")
        print("Type 'debug' to print the current state for debugging.")
        print("Type 'log' to see the most recent log entries.")
        
        while True:
            # Get user input
            user_input = input("\nYou: ")
            logger.info(f"User input: {user_input}")
            
            # Check for exit command
            if user_input.lower() == "exit":
                logger.info("User requested to end conversation")
                print("Ending conversation.")
                break
            
            # Check for debug command
            if user_input.lower() == "debug":
                logger.info("User requested debug information")
                print("\n=== Current State ===")
                print("Event Details:", json.dumps(result["event_details"], indent=2))
                print("Requirements:", json.dumps(result["requirements"], indent=2))
                print("Information Collected:", json.dumps(result["information_collected"], indent=2))
                print("Current Phase:", result["current_phase"])
                print("Next Steps:", result["next_steps"])
                if "proposal" in result and result["proposal"]:
                    print("Proposal Status:", result["proposal"]["status"])
                if "agent_assignments" in result and result["agent_assignments"]:
                    print("Agent Assignments:", json.dumps(result["agent_assignments"], indent=2))
                if "agent_results" in result and result["agent_results"]:
                    print("Agent Results:", json.dumps(result["agent_results"], indent=2))
                continue
            
            # Check for log command
            if user_input.lower() == "log":
                logger.info("User requested log information")
                try:
                    # Get the most recent log file
                    log_files = [f for f in os.listdir("logs") if f.startswith("coordinator_")]
                    if log_files:
                        latest_log = max(log_files, key=lambda x: os.path.getmtime(os.path.join("logs", x)))
                        with open(os.path.join("logs", latest_log), "r") as f:
                            # Get the last 20 lines
                            lines = f.readlines()
                            print("\n=== Recent Log Entries ===")
                            for line in lines[-20:]:
                                print(line.strip())
                    else:
                        print("No log files found.")
                except Exception as e:
                    print(f"Error reading log files: {str(e)}")
                continue
            
            # Add user message to state
            result["messages"].append({
                "role": "user",
                "content": user_input
            })
            
            # Run the coordinator graph
            logger.info(f"Invoking coordinator graph with user input: {user_input[:50]}...")
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
                print("Please try again or type 'exit' to end the conversation.")
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
            
            # Check if we've moved to a new phase
            if result["current_phase"] == "proposal_review" and "proposal" in result and result["proposal"]:
                logger.info("Proposal has been generated")
                print("\n(A proposal has been generated. Type 'approve' to proceed with implementation.)")
    except Exception as e:
        error_msg = f"Unexpected error in coordinator chat: {str(e)}"
        logger.critical(error_msg, exc_info=True)
        print(f"Critical error: {error_msg}")
        print(f"Stack trace: {traceback.format_exc()}")


if __name__ == "__main__":
    # Run the interactive chat
    asyncio.run(run_coordinator_chat())
