#!/usr/bin/env python3
"""
Script to create a complete version of the resource_planning_graph.py file.
"""

def create_complete_file():
    """
    Create a complete version of the resource_planning_graph.py file.
    """
    file_path = 'app/graphs/resource_planning_graph.py'
    
    # Read the existing file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Find the last complete line
    last_complete_line = content.rfind('                    "count": max(2, event_details.get("attendee_count", 100) // 100),')
    
    # Create the complete file
    complete_content = content[:last_complete_line + 1] + """
                    "roles": ["Setup coordinator", "Equipment technician", "General labor"]
                },
                "event_team": {
                    "count": max(3, event_details.get("attendee_count", 100) // 50),
                    "roles": ["Event manager", "AV technician", "Service coordinator", "General staff"]
                },
                "teardown_team": {
                    "count": max(2, event_details.get("attendee_count", 100) // 100),
                    "roles": ["Teardown coordinator", "Equipment technician", "General labor"]
                }
            },
            "contingency_plans": [
                {
                    "scenario": "Weather issues (for outdoor components)",
                    "plan": "Indoor backup space or tent rental"
                },
                {
                    "scenario": "Technical failures",
                    "plan": "Backup equipment and technician on standby"
                },
                {
                    "scenario": "Vendor no-show",
                    "plan": "List of backup vendors with contact information"
                }
            ]
        }
        
        return {
            "resource_plan": resource_plan,
            "total_cost": total_cost,
            "cost_breakdown": {
                "venue": venue_cost,
                "service_providers": service_provider_cost,
                "equipment": equipment_cost
            }
        }
    
    async def _arun(self, **kwargs) -> Dict[str, Any]:
        """Async implementation of the tool."""
        return self._run(**kwargs)


def create_resource_planning_graph():
    """
    Create the resource planning agent graph.
    
    Returns:
        Compiled LangGraph for the resource planning agent
    """
    # Initialize the LLM
    llm = get_llm(temperature=0.2)
    
    # Initialize tools
    tools = [
        VenueSearchTool(),
        ServiceProviderSearchTool(),
        EquipmentPlanningTool(),
        ResourcePlanGenerationTool(),
        RequirementsTool(),
        MonitoringTool(),
        ReportingTool()
    ]
    
    # Create the tool node
    tool_node = ToolNode(tools)
    
    # Define the nodes
    def analyze_requirements(state: ResourcePlanningStateDict) -> ResourcePlanningStateDict:
        """
        Analyze event requirements to determine resource needs.
        
        Args:
            state: Current state
            
        Returns:
            Updated state
        """
        # Get the last message
        last_message = state["messages"][-1]["content"] if state["messages"] else ""
        
        # Create a prompt for the LLM to analyze requirements
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an AI assistant that helps analyze event planning requirements to determine resource needs.
Based on the event details and conversation, extract key information about:
1. Venue requirements (location, capacity, amenities)
2. Service provider needs (catering, AV, photography, etc.)
3. Equipment needs (furniture, AV equipment, decorations, etc.)

Provide a structured analysis of what resources will be needed for this event."""),
            MessagesPlaceholder(variable_name="messages"),
            HumanMessage(content=f"""Event details: {state['event_details']}

Analyze these event details and the conversation to determine the resource needs for this event. Focus on venue requirements, service provider needs, and equipment needs.""")
        ])
        
        # Analyze requirements using the LLM
        chain = prompt | llm
        # Filter out any messages with empty content to avoid Google AI API error
        result = chain.invoke({"messages": [{"role": m["role"], "content": m["content"]} for m in state["messages"] if m["content"]]})
        
        # Add the analysis to messages
        state["messages"].append({
            "role": "assistant",
            "content": result.content
        })
        
        # Update phase and next steps
        state["current_phase"] = "requirements_analysis"
        state["next_steps"] = ["search_venues", "identify_service_providers", "plan_equipment"]
        
        return state
    
    def search_venues(state: ResourcePlanningStateDict) -> ResourcePlanningStateDict:
        """
        Search for venues based on event requirements.
        
        Args:
            state: Current state
            
        Returns:
            Updated state with venue options
        """
        # Create a prompt for the LLM to extract venue search criteria
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an AI assistant that helps extract venue search criteria from event details and conversation.
Extract the following information:
1. Event type
2. Preferred location
3. Expected attendee count
4. Budget range (if available)
5. Date range (if available)
6. Special requirements (if any)

Return the extracted information in a structured format."""),
            MessagesPlaceholder(variable_name="messages"),
            HumanMessage(content=f"""Event details: {state['event_details']}

Extract the venue search criteria from these event details and the conversation. If any information is missing, make reasonable assumptions based on the available data.""")
        ])
        
        # Extract venue search criteria using the LLM
        chain = prompt | llm
        # Filter out any messages with empty content to avoid Google AI API error
        result = chain.invoke({"messages": [{"role": m["role"], "content": m["content"]} for m in state["messages"] if m["content"]]})
        
        # Use the VenueSearchTool to search for venues
        venue_search_tool = VenueSearchTool()
        
        # Extract parameters from the LLM result
        # In a real implementation, this would parse the LLM output more robustly
        # For now, we'll use some default values and extract what we can
        
        event_type = state["event_details"].get("event_type", "conference")
        location = "New York"  # Default location
        attendee_count = state["event_details"].get("attendee_count", 100)
        
        # Simple extraction of location from the LLM result
        if "location" in result.content.lower():
            location_line = [line for line in result.content.split("\n") if "location" in line.lower()]
            if location_line:
                location_parts = location_line[0].split(":")
                if len(location_parts) > 1:
                    location = location_parts[1].strip()
        
        # Search for venues
        venue_results = venue_search_tool._run(
            event_type=event_type,
            location=location,
            attendee_count=attendee_count
        )
        
        # Update state with venue options
        state["venue_options"] = venue_results.get("venue_options", [])
        
        # Add venue options to messages
        venue_summary = "\n".join([
            f"- {venue['name']}: {venue['type']}, capacity {venue['capacity']}, ${venue['price_per_day']} per day"
            for venue in state["venue_options"]
        ])
        
        state["messages"].append({
            "role": "assistant",
            "content": f"Based on the event requirements, I've found the following venue options:\n\n{venue_summary}\n\nWould you like more details on any of these venues or should I proceed with recommending the best option?"
        })
        
        # Update phase and next steps
        state["current_phase"] = "venue_selection"
        state["next_steps"] = ["select_venue", "search_service_providers"]
        
        return state
    
    def select_venue(state: ResourcePlanningStateDict) -> ResourcePlanningStateDict:
        """
        Select the best venue from the options.
        
        Args:
            state: Current state
            
        Returns:
            Updated state with selected venue
        """
        # If no venue options, return the state unchanged
        if not state["venue_options"]:
            state["messages"].append({
                "role": "assistant",
                "content": "I couldn't find any suitable venues based on the current requirements. Let's revise the venue criteria."
            })
            return state
        
        # Create a prompt for the LLM to select the best venue
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an AI assistant that helps select the best venue for an event.
Analyze the venue options and event requirements to determine the most suitable venue.
Consider factors such as:
1. Capacity vs. attendee count
2. Price vs. budget
3. Amenities vs. requirements
4. Location
5. Venue type appropriateness for the event type

Provide a clear recommendation with justification."""),
            MessagesPlaceholder(variable_name="messages"),
            HumanMessage(content=f"""Event details: {state['event_details']}
Venue options: {state['venue_options']}

Select the best venue for this event and explain your reasoning.""")
        ])
        
        # Select venue using the LLM
        chain = prompt | llm
        # Filter out any messages with empty content to avoid Google AI API error
        result = chain.invoke({"messages": [{"role": m["role"], "content": m["content"]} for m in state["messages"] if m["content"]]})
        
        # For demonstration purposes, we'll select the first venue
        # In a real implementation, we would parse the LLM output to determine the selected venue
        selected_venue = state["venue_options"][0] if state["venue_options"] else None
        
        # Update state with selected venue
        state["selected_venue"] = selected_venue
        
        # Add venue selection to messages
        if selected_venue:
            state["messages"].append({
                "role": "assistant",
                "content": f"I recommend the {selected_venue['name']} as the best venue for this event.\n\n{result.content}"
            })
        else:
            state["messages"].append({
                "role": "assistant",
                "content": "I couldn't select a venue because no options were available. Let's revise the venue criteria."
            })
        
        # Update phase and next steps
        state["current_phase"] = "service_provider_selection"
        state["next_steps"] = ["search_service_providers", "plan_equipment"]
        
        return state
    
    def search_service_providers(state: ResourcePlanningStateDict) -> ResourcePlanningStateDict:
        """
        Search for service providers based on event requirements.
        
        Args:
            state: Current state
            
        Returns:
            Updated state with service provider options
        """
        # Create a prompt for the LLM to determine required service types
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an AI assistant that helps determine what service providers are needed for an event.
Based on the event details, venue, and conversation, identify what types of service providers are needed.
Common service types include:
1. Catering
2. Audio-Visual (AV)
3. Photography/Videography
4. Decoration
5. Entertainment
6. Security
7. Transportation

Return a list of required service types with brief justifications."""),
            MessagesPlaceholder(variable_name="messages"),
            HumanMessage(content=f"""Event details: {state['event_details']}
Selected venue: {state['selected_venue']}

Determine what service providers are needed for this event.""")
        ])
        
        # Determine required service types using the LLM
        chain = prompt | llm
        # Filter out any messages with empty content to avoid Google AI API error
        result = chain.invoke({"messages": [{"role": m["role"], "content": m["content"]} for m in state["messages"] if m["content"]]})
        
        # For demonstration purposes, we'll search for catering and AV services
        # In a real implementation, we would parse the LLM output to determine the required service types
        service_provider_search_tool = ServiceProviderSearchTool()
        
        location = state["selected_venue"]["location"] if state["selected_venue"] else "New York"
        
        # Search for catering providers
        catering_results = service_provider_search_tool._run(
            service_type="catering",
            location=location
        )
        
        # Search for AV providers
        av_results = service_provider_search_tool._run(
            service_type="audio visual",
            location=location
        )
        
        # Combine service providers
        service_providers = catering_results.get("service_providers", []) + av_results.get("service_providers", [])
        
        # Update state with service providers
        state["service_providers"] = service_providers
        
        # Add service providers to messages
        service_summary = "\n".join([
            f"- {provider['name']}: {provider['type']}, Rating: {provider['rating']}, Price: {provider['price_range']}"
            for provider in state["service_providers"]
        ])
        
        state["messages"].append({
            "role": "assistant",
            "content": f"Based on the event requirements, I've identified the following service providers:\n\n{service_summary}\n\nWould you like more details on any of these providers or should I proceed with planning the equipment needs?"
        })
        
        # Update phase and next steps
        state["current_phase"] = "equipment_planning"
        state["next_steps"] = ["plan_equipment", "generate_resource_plan"]
        
        return state
    
    def plan_equipment(state: ResourcePlanningStateDict) -> ResourcePlanningStateDict:
        """
        Plan equipment needs based on event requirements.
        
        Args:
            state: Current state
            
        Returns:
            Updated state with equipment needs
        """
        # If no venue selected, return the state unchanged
        if not state["selected_venue"]:
            state["messages"].append({
                "role": "assistant",
                "content": "I need a selected venue before I can plan the equipment needs. Let's select a venue first."
            })
            return state
        
        # Use the EquipmentPlanningTool to plan equipment needs
        equipment_planning_tool = EquipmentPlanningTool()
        
        event_type = state["event_details"].get("event_type", "conference")
        attendee_count = state["event_details"].get("attendee_count", 100)
        venue_type = state["selected_venue"].get("type", "conference center")
        
        # Plan equipment needs
        equipment_results = equipment_planning_tool._run(
            event_type=event_type,
            attendee_count=attendee_count,
            venue_type=venue_type
        )
        
        # Update state with equipment needs
        state["equipment_needs"] = equipment_results.get("equipment_needs", [])
        
        # Add equipment needs to messages
        equipment_summary = ""
        for category in state["equipment_needs"]:
            equipment_summary += f"\n{category['category']}:\n"
            for item in category["items"]:
                equipment_summary += f"- {item['name']}: {item['quantity']} ({item['notes']})\n"
        
        estimated_cost = equipment_results.get("estimated_cost", {})
        cost_summary = f"Total estimated equipment cost: ${estimated_cost.get('total', 0)}"
        
        state["messages"].append({
            "role": "assistant",
            "content": f"Based on the event requirements and selected venue, I've planned the following equipment needs:\n{equipment_summary}\n\n{cost_summary}\n\nShould I proceed with generating a comprehensive resource plan?"
        })
        
        # Update phase and next steps
        state["current_phase"] = "resource_plan_generation"
        state["next_steps"] = ["generate_resource_plan"]
        
        return state
    
    def generate_resource_plan(state: ResourcePlanningStateDict) -> ResourcePlanningStateDict:
        """
        Generate a comprehensive resource plan.
        
        Args:
            state: Current state
            
        Returns:
            Updated state with resource plan
        """
        # If no venue selected or no equipment needs, return the state unchanged
        if not state["selected_venue"] or not state["equipment_needs"]:
            state["messages"].append({
                "role": "assistant",
                "content": "I need a selected venue and equipment needs before I can generate a resource plan. Let's complete those steps first."
            })
            return state
        
        # Use the ResourcePlanGenerationTool to generate a resource plan
        resource_plan_tool = ResourcePlanGenerationTool()
        
        # Generate resource plan
        plan_results = resource_plan_tool._run(
            event_details=state["event_details"],
            venue=state["selected_venue"],
            service_providers=state["service_providers"],
            equipment_needs=state["equipment_needs"]
        )
        
        # Update state with resource plan
        state["resource_plan"] = plan_results.get("resource_plan", {})
        
        # Create a prompt for the LLM to generate a summary of the resource plan
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an AI assistant that helps summarize resource plans for events.
Create a clear, concise summary of the resource plan that highlights:
1. Key venue details
2. Selected service providers
3. Equipment overview
4. Cost breakdown
5. Timeline
6. Staffing
7. Contingency plans

The summary should be professional and easy to understand."""),
            HumanMessage(content=f"""Resource plan: {state['resource_plan']}

Create a concise summary of this resource plan.""")
        ])
        
        # Generate summary using the LLM
        chain = prompt | llm
        # Filter out any messages with empty content to avoid Google AI API error
        result = chain.invoke({})
        
        # Add resource plan to messages
        state["messages"].append({
            "role": "assistant",
            "content": f"I've generated a comprehensive resource plan for the event:\n\n{result.content}\n\nThe total estimated cost is ${state['resource_plan']['summary']['total_cost']}. Would you like me to make any adjustments to this plan?"
        })
        
        # Update phase and next steps
        state["current_phase"] = "plan_review"
        state["next_steps"] = ["finalize_plan"]
        
        return state
    
    def generate_response(state: ResourcePlanningStateDict) -> ResourcePlanningStateDict:
        """
        Generate a response to the user or coordinator agent.
        
        Args:
            state: Current state
            
        Returns:
            Updated state
        """
        # Create the resource planning prompt
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=RESOURCE_PLANNING_SYSTEM_PROMPT.format(
                current_phase=state["current_phase"],
                event_details=state["event_details"],
                venue_options=state["venue_options"],
                selected_venue=state["selected_venue"],
                service_providers=state["service_providers"],
                equipment_needs=state["equipment_needs"],
                next_steps=state["next_steps"]
            )),
            MessagesPlaceholder(variable_name="messages"),
        ])
        
        # Generate response using the LLM
        chain = prompt | llm
        # Filter out any messages with empty content to avoid Google AI API error
        result = chain.invoke({"messages": [{"role": m["role"], "content": m["content"]} for m in state["messages"] if m["content"]]})
        
        # Add the response to messages
        new_message = {
            "role": "assistant",
            "content": result.content
        }
        state["messages"].append(new_message)
        
        return state
    
    # Create the graph
    workflow = StateGraph(ResourcePlanningStateDict)
    
    # Add nodes
    workflow.add_node("analyze_requirements", analyze_requirements)
    workflow.add_node("search_venues", search_venues)
    workflow.add_node("select_venue", select_venue)
    workflow.add_node("search_service_providers", search_service_providers)
    workflow.add_node("plan_equipment", plan_equipment)
    workflow.add_node("generate_resource_plan", generate_resource_plan)
    workflow.add_node("generate_response", generate_response)
    workflow.add_node("tools", tool_node)
    
    # Add edges
    workflow.add_edge("analyze_requirements", "search_venues")
    workflow.add_edge("search_venues", "select_venue")
    workflow.add_edge("select_venue", "search_service_providers")
    workflow.add_edge("search_service_providers", "plan_equipment")
    workflow.add_edge("plan_equipment", "generate_resource_plan")
    workflow.add_edge("generate_resource_plan", "generate_response")
    workflow.add_edge("generate_response", END)
    
    # Set the entry point
    workflow.set_entry_point("analyze_requirements")
    
    return workflow.compile()


def create_initial_state() -> ResourcePlanningStateDict:
    """
    Create the initial state for the resource planning agent.
    
    Returns:
        Initial state dictionary
    """
    return {
        "messages": [],
        "event_details": {
            "event_type": None,
            "title": None,
            "description": None,
            "attendee_count": None,
            "scale": None,
            "timeline_start": None,
            "timeline_end": None,
            "budget": None,
            "location": None
        },
        "venue_options": [],
        "selected_venue": None,
        "service_providers": [],
        "equipment_needs": [],
        "current_phase": "requirements_analysis",
        "next_steps": ["analyze_requirements"],
        "resource_plan": None
    }
"""
    
    # Write the complete file
    with open(file_path, 'w') as f:
        f.write(complete_content)
    
    print(f"Created complete version of {file_path}")

if __name__ == "__main__":
    create_complete_file()
