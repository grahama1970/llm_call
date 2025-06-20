#!/bin/bash
# JSON Status Polling Script
# Usage: ./script.sh [status_file] [expected_status] [timeout]

STATUS_FILE="${1:-verification_status.json}"
EXPECTED_STATUS="${2:-pass}"
TIMEOUT="${3:-300}"
START_TIME=$SECONDS

echo "Polling for: $STATUS_FILE"
echo "Expected status: $EXPECTED_STATUS"
echo "Timeout: $TIMEOUT seconds"

# Wait for file to exist
while [ ! -f "$STATUS_FILE" ]; do
    if [ $((SECONDS - START_TIME)) -gt $TIMEOUT ]; then
        echo "ERROR: Timeout after $TIMEOUT seconds"
        exit 1
    fi
    echo "Waiting for $STATUS_FILE... ($((SECONDS - START_TIME))s)"
    sleep 5
done

echo "File found, checking status..."

# Validate JSON and extract status
if ! jq empty "$STATUS_FILE" 2>/dev/null; then
    echo "ERROR: Invalid JSON"
    exit 1
fi

STATUS=$(jq -r '.status // "unknown"' "$STATUS_FILE")
echo "Found status: $STATUS"

if [ "$STATUS" = "$EXPECTED_STATUS" ]; then
    echo "SUCCESS: Status matches expected value"
    exit 0
else
    echo "ERROR: Status '$STATUS' != expected '$EXPECTED_STATUS'"
    exit 1
fi