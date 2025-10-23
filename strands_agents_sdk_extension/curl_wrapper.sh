curl http://localhost:8443/health && \
curl -k -X POST http://localhost:8443/api/v1/identity/register \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "agent-002"}' && \
curl -k -X POST http://localhost:8443/api/v1/policy/assign-role \
  -H "Content-Type: application/json" \
  -H "X-Agent-ID: agent-002" \
  -d '{"agent_id": "agent-002", "role": "admin"}' && \
curl -k http://localhost:8443/api/v1/identity/list \
  -H "X-Agent-ID: agent-002" && \
curl -k http://localhost:8443/api/v1/ratelimit/stats \
  -H "X-Agent-ID: agent-002" && \
curl http://localhost:8443/api/v1/policy/roles
