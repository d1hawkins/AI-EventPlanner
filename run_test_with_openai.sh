#!/bin/bash
# Script to run the test with OpenAI provider

# Switch to OpenAI provider
echo "Switching to OpenAI provider..."
python switch_llm_provider.py openai

# Run the test
echo "Running test with OpenAI provider..."
python test_specialized_agents.py

# Show the results
echo "Test completed. Check the logs for details."
ls -la logs/
