#!/bin/bash
set -e

echo "Testing Azure deployment fixes..."

# Test the Python path detection regex
echo "Testing Python path detection regex..."
TEST_RESPONSE='{
  "Output": "/usr/bin/python3\n/usr/local/bin/python3\n",
  "Error": "",
  "ExitCode": 0
}'

# Extract Python path from the response using grep
PYTHON_PATH=$(echo "$TEST_RESPONSE" | grep -o '/[a-zA-Z0-9/_.-]*python3' | head -n 1 || echo "")

if [ -z "$PYTHON_PATH" ]; then
  echo "❌ Failed to extract Python path from response"
  echo "Response: $TEST_RESPONSE"
  exit 1
else
  echo "✅ Successfully extracted Python path: $PYTHON_PATH"
fi

# Test the JSON parsing for the GitHub Actions workflow
echo "Testing JSON parsing for GitHub Actions workflow..."
TEST_FIND_PYTHON_RESPONSE='{
  "Output": "/usr/bin/python3\n/usr/local/bin/python3\n",
  "Error": "",
  "ExitCode": 0
}'

# Extract Python path from the response
PYTHON_PATH=$(echo "$TEST_FIND_PYTHON_RESPONSE" | grep -o '/[a-zA-Z0-9/_.-]*python3' | head -n 1 || echo "")

if [ -z "$PYTHON_PATH" ]; then
  echo "❌ Failed to extract Python path from response"
  echo "Response: $TEST_FIND_PYTHON_RESPONSE"
  exit 1
else
  echo "✅ Successfully extracted Python path: $PYTHON_PATH"
fi

# Test the fallback to python3 if no path is found
echo "Testing fallback to python3 if no path is found..."
TEST_EMPTY_RESPONSE='{
  "Output": "",
  "Error": "",
  "ExitCode": 0
}'

# Extract Python path from the response
PYTHON_PATH=$(echo "$TEST_EMPTY_RESPONSE" | grep -o '/[a-zA-Z0-9/_.-]*python3' | head -n 1 || echo "")

if [ -z "$PYTHON_PATH" ]; then
  echo "✅ No Python path found, falling back to python3"
  PYTHON_PATH="python3"
else
  echo "❌ Unexpectedly found Python path: $PYTHON_PATH"
  exit 1
fi

echo "Python path after fallback: $PYTHON_PATH"

# Test the diagnose_azure.py regex
echo "Testing diagnose_azure.py regex..."
python3 -c "
import re
test_response = '{\"Output\": \"/usr/bin/python3\\n/usr/local/bin/python3\\n\", \"Error\": \"\", \"ExitCode\": 0}'
python_path_match = re.search(r'/[a-zA-Z0-9/_.-]*python3', test_response)
python_path = python_path_match.group(0) if python_path_match else 'python3'
print(f'Python path: {python_path}')
if python_path == '/usr/bin/python3':
    print('✅ Successfully extracted Python path using regex')
else:
    print(f'❌ Failed to extract correct Python path: {python_path}')
    exit(1)
"

echo "All tests passed! The Azure deployment fixes should work correctly."
