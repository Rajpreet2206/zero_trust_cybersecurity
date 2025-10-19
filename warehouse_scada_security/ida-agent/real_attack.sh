# Simulate an actual agent making many requests rapidly
# This creates audit log entries that IDA can analyze

AGENT_ID="test_agent_rapid_fire"

# Register the agent first
curl -X POST http://localhost:8443/api/v1/identity/register \
  -H "Content-Type: application/json" \
  -d "{\"agent_id\": \"$AGENT_ID\"}" > /dev/null

# Assign it a role
curl -X POST http://localhost:8443/api/v1/policy/assign-role \
  -H "Content-Type: application/json" \
  -d "{\"agent_id\": \"$AGENT_ID\", \"role\": \"user\"}" > /dev/null

# Now make 50+ rapid requests (DoS-like pattern)
for i in {1..50}; do
  curl -X GET "http://localhost:8443/api/v1/audit/logs" \
    -H "X-Agent-ID: $AGENT_ID" \
    -H "X-Signature: valid_or_invalid" \
    -s > /dev/null & 
done
wait

echo "Attack simulation complete"