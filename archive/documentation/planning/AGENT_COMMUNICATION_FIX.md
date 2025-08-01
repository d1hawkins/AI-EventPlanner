# Agent Communication Fix

## Issue Description

When using the AI Event Planner SaaS application, users were encountering an error when sending a second prompt to an agent:

```
Error processing message: Unexpected message with type <class 'langchain_core.messages.system.SystemMessage'> at the position 2.
```

This error occurred because system messages were being added to the conversation state, but the code in `coordinator_graph.py` wasn't properly handling these system messages when converting message dictionaries to message objects for the LangChain framework.

## Root Cause

The issue was in multiple places in the `coordinator_graph.py` file:

1. In the `generate_response` function:

```python
# Convert message dicts to message objects
message_objects = []
for m in state["messages"]:
    role = m.get("role")
    content = m.get("content")
    if role == "user":
        message_objects.append(HumanMessage(content=content))
    elif role == "assistant":
        message_objects.append(AIMessage(content=content))
    # Avoid adding system messages from history here, as the template adds one
    # elif role == "system":
    #     message_objects.append(SystemMessage(content=content))
```

2. In the `gather_requirements` function:

```python
# Extract requirements using the LLM
chain = prompt | llm
result = chain.invoke({"messages": [{"role": m["role"], "content": m["content"]} for m in state["messages"]]})
```

The code had a commented-out section for handling system messages in the `generate_response` function, but system messages were still being added to the state["messages"] array in other parts of the code, such as when attaching an event to a conversation:

```python
# Add a system message about the attached event
if "messages" in state:
    state["messages"].append({
        "role": "system",
        "content": f"Event '{event.title}' has been attached to this conversation. The agent now has access to the event details.",
        "timestamp": datetime.utcnow().isoformat()
    })
    agent_factory.state_manager.update_conversation_state(conversation_id, state)
```

When the second prompt was sent, the code tried to process these system messages but didn't know how to handle them, resulting in the error.

## Initial Fix

The initial fix was to modify the code in the `generate_response` function in `coordinator_graph.py` to explicitly skip system messages when converting message dictionaries to message objects:

```python
# Convert message dicts to message objects
message_objects = []
for m in state["messages"]:
    role = m.get("role")
    content = m.get("content")
    # Skip system messages to avoid conflicts with the template
    if role == "system":
        continue
    elif role == "user":
        message_objects.append(HumanMessage(content=content))
    elif role == "assistant":
        message_objects.append(AIMessage(content=content))
```

This change ensured that system messages in the conversation history are skipped in the `generate_response` function, but there were still other places in the code that needed to be fixed.

## Comprehensive Fix

After testing, we found that the initial fix was not sufficient, as there were still errors occurring in other parts of the code. We implemented a more comprehensive fix that addressed all instances of system message handling issues:

1. Fixed the `generate_response` function as described above.

2. Fixed the `gather_requirements` function to filter out system messages before invoking the chain:

```python
# Extract requirements using the LLM
# Filter out system messages before invoking the chain
filtered_messages = [
    {"role": m["role"], "content": m["content"]} 
    for m in state["messages"] 
    if m["role"] != "system"
]
chain = prompt | llm
result = chain.invoke({"messages": filtered_messages})
```

This comprehensive fix ensures that system messages are properly handled in all parts of the code, preventing the error from occurring in any scenario.

## Implementation

The fix was implemented in two phases:

1. Initial fix using a Python script (`fix_agent_communication.py`) that modified the `generate_response` function.

2. Comprehensive fix using a Python script (`fix_agent_communication_comprehensive.py`) that modified both the `generate_response` and `gather_requirements` functions.

After applying each fix, the application was restarted to apply the changes.

## Verification

The fix was verified by running the application and confirming that users can now send multiple prompts to agents without encountering the error. The comprehensive fix addressed all instances of the issue, ensuring that the application works correctly in all scenarios.

## Additional Notes

This fix allows system messages to be added to the conversation state for informational purposes (such as when attaching an event to a conversation) without causing errors in the agent communication flow. The system messages will still be stored in the conversation history but will be skipped when processing messages for the LangChain framework.
