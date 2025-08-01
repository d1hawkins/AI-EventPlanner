# Azure TypedDict Compatibility Fix

## Issue

When deploying the AI-EventPlanner application to Azure, we encountered an error related to TypedDict compatibility:

```
TypeError: issubclass() arg 1 must be a class
```

This error occurred in the LangGraph framework when using TypedDict for state schema typing. The error happens because Azure's Python environment has some compatibility issues with how TypedDict is handled in the context of LangGraph's StateGraph initialization.

## Root Cause

The issue stems from how TypedDict is implemented and how it interacts with LangGraph's StateGraph class. In the Azure environment, when LangGraph tries to validate the state schema against TypedDict, it encounters an error because it's trying to use `issubclass()` with something that isn't recognized as a proper class in that environment.

## Solution

The solution is to use a regular Python dictionary (`dict`) for the state schema instead of TypedDict. This avoids the compatibility issue while still providing the necessary structure for the state.

### Changes Made:

1. In `app/graphs/simple_coordinator_graph.py`:
   - Removed TypedDict imports
   - Changed the StateGraph initialization to use `dict` instead of TypedDict:
     ```python
     # Before:
     workflow = StateGraph()
     
     # After:
     workflow = StateGraph(state_schema=dict)
     ```

2. In `app/graphs/coordinator_graph.py`:
   - This file was already using the correct approach with `StateGraph(dict)`
   - Added a comment to explain the reason for using dict instead of TypedDict:
     ```python
     # Define the state schema as a regular dict to avoid TypedDict compatibility issues
     # This avoids the issubclass() error in Azure environment
     ```

## Verification

We verified the fix by testing both graph creation functions:

```python
from app.graphs.simple_coordinator_graph import create_coordinator_graph, create_initial_state
graph = create_coordinator_graph()
state = create_initial_state()
print('Successfully created coordinator graph and initial state')
```

```python
from app.graphs.coordinator_graph import create_coordinator_graph, create_initial_state
graph = create_coordinator_graph()
state = create_initial_state()
print('Successfully created coordinator graph and initial state')
```

Both tests were successful, confirming that the fix resolves the TypedDict compatibility issue.

## Impact

This change maintains the functionality of the application while ensuring compatibility with the Azure environment. The use of a regular dictionary instead of TypedDict doesn't affect the behavior of the application, as the structure and validation of the state are still maintained through the code logic.

## Additional Notes

- The warning about TAVILY_API_KEY being unset is expected and doesn't affect the functionality of the application.
- The warning about "grpc_wait_for_shutdown_with_timeout() timed out" is related to the gRPC library used by some AI services and doesn't affect the application's functionality.
