# Testing Agent State Persistence

This guide will walk you through testing the agent state persistence implementation.

## Step 1: Create a Test Conversation

First, let's create a test conversation and verify it's stored in the database:

```bash
# Run the test script to create a new conversation
python test_agent_persistence.py
```

This will:
1. Create a new conversation with a coordinator agent
2. Send a test message
3. Print the conversation ID
4. Store the conversation in the database

**Important:** Note down the conversation ID that is displayed. You'll need it in Step 3.

## Step 2: Restart the SaaS Application with Agents

Now, let's restart the SaaS application to verify that the conversation state persists across restarts:

```bash
# First, stop any running instances (press Ctrl+C in the terminal where it's running)

# Then, restart the SaaS application with agents
python run_saas_with_agents.py
```

This will:
1. Stop the current instance of the application
2. Start a fresh instance
3. Load the TenantAwareStateManager, which will load conversations from the database

## Step 3: Verify Persistence

Finally, let's verify that the conversation state was persisted:

```bash
# Run the test script again with the conversation ID from Step 1
python test_agent_persistence.py YOUR_CONVERSATION_ID
```

Replace `YOUR_CONVERSATION_ID` with the actual conversation ID from Step 1.

This will:
1. Load the conversation from the database
2. Display all messages in the conversation
3. Confirm that the state was successfully persisted

## Expected Results

If the implementation is working correctly, you should see:

1. The original test message: "Hello, I'm testing the persistence of agent state. Can you remember this message?"
2. The agent's response to that message
3. A confirmation message: "Conversation loaded successfully. This demonstrates that the state was persisted to the database."

## Testing in the Web Interface

You can also test the persistence in the web interface:

1. Open a browser and navigate to http://localhost:8002/saas/agents.html
2. Select an agent and start a conversation
3. Send a few messages
4. Restart the application using `python run_saas_with_agents.py`
5. Return to the web interface and verify that your conversation history is still there

## Troubleshooting

If the conversation is not persisted:

1. Check the console output for any errors during startup
2. Verify that the database connection is working
3. Check that the AgentState table has entries in the database
4. Ensure that the conversation ID is correct when testing
