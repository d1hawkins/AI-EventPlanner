import asyncio
import json
from datetime import datetime

from app.graphs.coordinator_graph import create_coordinator_graph, create_initial_state


async def test_coordinator_proposal():
    """
    Test the coordinator agent's ability to collect information and generate a proposal.
    """
    # Create the coordinator graph
    coordinator_graph = create_coordinator_graph()
    
    # Create initial state
    state = create_initial_state()
    
    # Simulate a conversation
    messages = [
        {
            "role": "user",
            "content": "I need help planning a tech conference for 200 attendees in New York."
        },
        {
            "role": "user",
            "content": "The conference will focus on AI and machine learning technologies. It should be a 2-day event with keynote speakers, workshops, and networking opportunities."
        },
        {
            "role": "user",
            "content": "The budget is around $100,000. We want to allocate about 40% for the venue, 20% for catering, 15% for speaker fees and travel, 15% for marketing, and 10% for miscellaneous expenses."
        },
        {
            "role": "user",
            "content": "We're planning to hold the conference in September 2025. We need a venue that can accommodate all attendees for keynote sessions and have smaller rooms for workshops."
        },
        {
            "role": "user",
            "content": "We want to invite 3-5 keynote speakers and have 10-15 workshop sessions. We also want to have networking events in the evenings."
        },
        {
            "role": "user",
            "content": "We'll need AV equipment, Wi-Fi for all attendees, and catering for breakfast and lunch both days."
        },
        {
            "role": "user",
            "content": "Our main goals are to showcase the latest AI technologies, provide learning opportunities for attendees, and facilitate networking in the AI community."
        },
        {
            "role": "user",
            "content": "The main risks are finding suitable speakers, ensuring enough attendees, and technical issues during the presentations."
        }
    ]
    
    # Add messages to state
    state["messages"] = messages
    
    # Process each message individually to ensure proper information extraction
    print("Processing messages to extract requirements...")
    for i in range(len(messages)):
        # Create a temporary state with just the messages up to this point
        temp_state = create_initial_state()
        temp_state["messages"] = messages[:i+1]
        
        # Run the coordinator graph on this subset of messages
        temp_result = coordinator_graph.invoke(temp_state)
        
        # Update our state with the extracted information
        state["event_details"] = temp_result["event_details"]
        state["requirements"] = temp_result["requirements"]
        state["information_collected"] = temp_result["information_collected"]
    
    # Print the extracted information
    print("\n=== Event Details After Processing ===")
    print(json.dumps(state["event_details"], indent=2))
    
    print("\n=== Requirements After Processing ===")
    print(json.dumps(state["requirements"], indent=2))
    
    print("\n=== Information Collected Status After Processing ===")
    print(json.dumps(state["information_collected"], indent=2))
    
    # Add the request for a proposal
    state["messages"].append({
        "role": "user",
        "content": "Can you create a proposal for this event?"
    })
    
    # Run the coordinator graph
    print("\nRunning coordinator graph to generate proposal...")
    result = coordinator_graph.invoke(state)
    
    # Print the results
    print("\n=== Event Details ===")
    print(json.dumps(result["event_details"], indent=2))
    
    print("\n=== Requirements ===")
    print(json.dumps(result["requirements"], indent=2))
    
    print("\n=== Information Collected Status ===")
    print(json.dumps(result["information_collected"], indent=2))
    
    print("\n=== Current Phase ===")
    print(result["current_phase"])
    
    print("\n=== Next Steps ===")
    print(result["next_steps"])
    
    # Check if proposal was generated
    if "proposal" in result and result["proposal"]:
        print("\n=== Proposal ===")
        print(result["proposal"]["content"])
        print("\nProposal Status:", result["proposal"]["status"])
    else:
        print("\nNo proposal generated yet.")
    
    # Print the last assistant message
    assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
    if assistant_messages:
        print("\n=== Last Assistant Message ===")
        print(assistant_messages[-1]["content"])
    
    return result


if __name__ == "__main__":
    # Run the test
    asyncio.run(test_coordinator_proposal())
