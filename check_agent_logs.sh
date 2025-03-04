#!/bin/bash
# Script to check logs for agent assignments and errors

# Check if a log file is provided
if [ $# -eq 0 ]; then
    # Find the most recent log file
    LOGFILE=$(ls -t logs/test_specialized_agents_*.log | head -1)
else
    LOGFILE=$1
fi

echo "Checking log file: $LOGFILE"
echo ""

# Check for agent assignments
echo "=== Agent Assignments ==="
grep -i "agent assignment" $LOGFILE
echo ""

# Check for completed assignments
echo "=== Completed Assignments ==="
grep -i "completed agent assignment" $LOGFILE
echo ""

# Check for failed assignments
echo "=== Failed Assignments ==="
grep -i "failed agent assignment" $LOGFILE
echo ""

# Check for errors
echo "=== Errors ==="
grep -i "error" $LOGFILE
echo ""

# Check for phase transitions
echo "=== Phase Transitions ==="
grep -i "current phase" $LOGFILE
echo ""

# Show the final state
echo "=== Final State ==="
tail -n 20 $LOGFILE
