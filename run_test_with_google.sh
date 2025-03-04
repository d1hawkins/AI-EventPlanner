#!/bin/bash
# Script to run the test with Google AI provider

# Switch to Google AI provider
echo "Switching to Google AI provider..."
python switch_llm_provider.py google

# Run the test
echo "Running test with Google AI provider..."
python test_specialized_agents.py

# Show the results
echo "Test completed. Check the logs for details."
ls -la logs/
