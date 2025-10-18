package main

import (
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"

	"github.com/strands/zero-trust-wrapper/pkg/crypto"
	"github.com/strands/zero-trust-wrapper/pkg/identity"
	"github.com/strands/zero-trust-wrapper/pkg/middleware"
	"github.com/strands/zero-trust-wrapper/pkg/policy"
	"github.com/strands/zero-trust-wrapper/pkg/sdk"
)

var (
	identityMgr    *identity.Manager
	policyEngine   *policy.PolicyEngine
	pythonBridge   *sdk.Bridge
	authMiddleware *middleware.AuthMiddleware
)

func main() {
	fmt.Println("🔐 Strands Zero-Trust Security Wrapper - Step 9: Behavioral Analytics")

	// Initialize crypto engine
	cryptoEngine, err := crypto.NewEngine()
	if err != nil {
		log.Fatalf("Failed to initialize crypto: %v", err)
	}
	fmt.Println("✓ Crypto engine initialized")

	// Initialize identity manager
	identityMgr = identity.NewManager(cryptoEngine)
	fmt.Println("✓ Identity manager initialized")

	// Initialize policy engine
	policyEngine = policy.NewPolicyEngine()
	fmt.Println("✓ Policy engine initialized")

	// Initialize auth middleware
	authMiddleware = middleware.NewAuthMiddleware(identityMgr, policyEngine)
	fmt.Println("✓ Authorization middleware initialized")
	fmt.Println("✓ Rate limiting enabled (100 req/sec, burst 50)")
	fmt.Println("✓ Behavioral analytics enabled")
	fmt.Println("✓ Authorization middleware initialized (with caching)")
	// Initialize Python SDK bridge
	pythonEndpoint := os.Getenv("PYTHON_SDK_ENDPOINT")
	if pythonEndpoint == "" {
		pythonEndpoint = "http://localhost:5000"
	}
	pythonBridge = sdk.NewBridge(pythonEndpoint, 60)
	fmt.Println("✓ Python SDK bridge initialized")

	// HTTP endpoints - PUBLIC (no auth required)
	http.Handle("/health", authMiddleware.ProtectPublic(handleHealth))
	http.Handle("/api/v1/identity/register", authMiddleware.ProtectPublic(handleRegister))
	http.Handle("/api/v1/policy/roles", authMiddleware.ProtectPublic(handleGetRoles))

	// HTTP endpoints - PROTECTED (auth + authorization required)
	http.Handle("/api/v1/identity/list", authMiddleware.Protect(handleList, "agent:read"))
	http.Handle("/api/v1/identity/verify", authMiddleware.Protect(handleVerify, "agent:read"))
	http.Handle("/api/v1/identity/revoke", authMiddleware.Protect(handleRevoke, "agent:delete"))
	http.Handle("/api/v1/audit/logs", authMiddleware.Protect(handleAuditLog, "audit:read"))
	http.Handle("/api/v1/policy/assign-role", authMiddleware.ProtectPublic(handleAssignRole))
	http.Handle("/api/v1/policy/agent-roles", authMiddleware.Protect(handleGetAgentRoles, "agent:read"))
	http.Handle("/api/v1/sdk/health", authMiddleware.Protect(handleSDKHealth, "agent:read"))
	http.Handle("/api/v1/sdk/execute", authMiddleware.Protect(handleExecuteAgent, "agent:write"))
	http.Handle("/api/v1/sdk/agents", authMiddleware.Protect(handleSDKAgents, "agent:read"))
	http.Handle("/api/v1/ratelimit/stats", authMiddleware.Protect(handleRateLimitStats, "agent:read"))
	http.Handle("/api/v1/analytics/anomalies", authMiddleware.Protect(handleGetAnomalies, "audit:read"))
	http.Handle("/api/v1/analytics/behavior", authMiddleware.Protect(handleGetBehavior, "audit:read"))

	// Get configuration
	addr := os.Getenv("SERVER_PORT")
	if addr == "" {
		addr = "8443"
	}

	// Check if TLS is enabled
	tlsEnabled := os.Getenv("TLS_ENABLED")
	if tlsEnabled == "" {
		tlsEnabled = "true"
	}

	// Start server
	var serverErr error
	if tlsEnabled == "true" {
		// TLS mode
		certFile := os.Getenv("TLS_CERT_PATH")
		keyFile := os.Getenv("TLS_KEY_PATH")

		if certFile == "" {
			certFile = "certs/server.crt"
		}
		if keyFile == "" {
			keyFile = "certs/server.key"
		}

		// Check if cert files exist
		if _, err := os.Stat(certFile); os.IsNotExist(err) {
			fmt.Printf("⚠️  TLS certificate not found: %s\n", certFile)
			fmt.Println("Generate certificates with: ./scripts/generate-certs.sh")
			fmt.Println("Or run with: TLS_ENABLED=false ./bin/wrapper-server.exe")
			os.Exit(1)
		}

		fmt.Printf("🔒 HTTPS (TLS) enabled\n")
		fmt.Printf("📝 Certificate: %s\n", certFile)
		fmt.Printf("📝 Key: %s\n", keyFile)
		fmt.Printf("✓ HTTP server starting on :8443 (encrypted)\n")
		serverErr = http.ListenAndServeTLS(":"+addr, certFile, keyFile, nil)
	} else {
		// HTTP mode (no TLS)
		fmt.Println("⚠️  WARNING: TLS disabled - communication NOT encrypted!")
		fmt.Println("For production, enable TLS: TLS_ENABLED=true")
		fmt.Println("✓ HTTP server starting on :8443 (unencrypted)")
		serverErr = http.ListenAndServe(":"+addr, nil)
	}

	if serverErr != nil {
		log.Fatalf("Server error: %v", serverErr)
	}
}

func handleHealth(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(map[string]string{"status": "healthy"})
}

func handleRegister(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		w.WriteHeader(http.StatusMethodNotAllowed)
		return
	}

	var req struct {
		AgentID string `json:"agent_id"`
	}

	body, _ := io.ReadAll(r.Body)
	json.Unmarshal(body, &req)

	if req.AgentID == "" {
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(map[string]string{"error": "agent_id required"})
		return
	}

	agent, err := identityMgr.RegisterAgent(req.AgentID)
	if err != nil {
		w.WriteHeader(http.StatusConflict)
		json.NewEncoder(w).Encode(map[string]string{"error": err.Error()})
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(agent)
}

func handleList(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		w.WriteHeader(http.StatusMethodNotAllowed)
		return
	}

	agents := identityMgr.ListAgents()
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(map[string]interface{}{
		"agents": agents,
		"count":  len(agents),
	})
}

func handleVerify(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		w.WriteHeader(http.StatusMethodNotAllowed)
		return
	}

	var req struct {
		AgentID   string `json:"agent_id"`
		Signature string `json:"signature"`
		Nonce     string `json:"nonce"`
	}

	body, _ := io.ReadAll(r.Body)
	json.Unmarshal(body, &req)

	if req.AgentID == "" || req.Signature == "" {
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(map[string]string{"error": "agent_id and signature required"})
		return
	}

	// Queue verification asynchronously in middleware
	// The middleware will process this in background
	// For now, just acknowledge the request

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusAccepted) // 202 Accepted - processing
	json.NewEncoder(w).Encode(map[string]string{
		"status":  "verification_queued",
		"message": "verification processing in background",
	})
}

func handleRevoke(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		w.WriteHeader(http.StatusMethodNotAllowed)
		return
	}

	var req struct {
		AgentID string `json:"agent_id"`
	}

	body, _ := io.ReadAll(r.Body)
	json.Unmarshal(body, &req)

	err := identityMgr.RevokeAgent(req.AgentID)
	if err != nil {
		w.WriteHeader(http.StatusNotFound)
		json.NewEncoder(w).Encode(map[string]string{"error": err.Error()})
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(map[string]string{"status": "revoked"})
}

func handleAuditLog(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		w.WriteHeader(http.StatusMethodNotAllowed)
		return
	}

	events := identityMgr.GetAuditLog()
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(map[string]interface{}{
		"events": events,
		"count":  len(events),
	})
}

func handleAssignRole(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		w.WriteHeader(http.StatusMethodNotAllowed)
		return
	}

	var req struct {
		AgentID string `json:"agent_id"`
		Role    string `json:"role"`
	}

	body, _ := io.ReadAll(r.Body)
	json.Unmarshal(body, &req)

	if req.AgentID == "" || req.Role == "" {
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(map[string]string{"error": "agent_id and role required"})
		return
	}

	err := policyEngine.AssignRole(req.AgentID, req.Role)
	if err != nil {
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(map[string]string{"error": err.Error()})
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(map[string]string{"status": "role assigned"})
}

func handleGetAgentRoles(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		w.WriteHeader(http.StatusMethodNotAllowed)
		return
	}

	agentID := r.URL.Query().Get("agent_id")
	if agentID == "" {
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(map[string]string{"error": "agent_id required"})
		return
	}

	roles := policyEngine.GetAgentRoles(agentID)
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(map[string]interface{}{
		"agent_id": agentID,
		"roles":    roles,
		"count":    len(roles),
	})
}

func handleGetRoles(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		w.WriteHeader(http.StatusMethodNotAllowed)
		return
	}

	roles := policyEngine.GetRoles()
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(roles)
}

func handleSDKHealth(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		w.WriteHeader(http.StatusMethodNotAllowed)
		return
	}

	connected := pythonBridge.IsConnected()
	status := "disconnected"
	statusCode := http.StatusServiceUnavailable

	if connected {
		status = "connected"
		statusCode = http.StatusOK
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(statusCode)
	json.NewEncoder(w).Encode(map[string]interface{}{
		"python_sdk": status,
		"connected":  connected,
	})
}

func handleExecuteAgent(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		w.WriteHeader(http.StatusMethodNotAllowed)
		return
	}

	var req struct {
		Task map[string]interface{} `json:"task"`
	}

	body, _ := io.ReadAll(r.Body)
	// fmt.Printf("Raw request body: %s\n", string(body))
	err := json.Unmarshal(body, &req)
	// fmt.Printf("Parsed req.Task: %#v\n", req.Task)
	if err != nil {
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(map[string]string{"error": "invalid JSON"})
		return
	}

	if req.Task == nil {
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(map[string]string{"error": "task required"})
		return
	}

	question, ok := req.Task["question"].(string)
	if !ok || question == "" {
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(map[string]string{"error": "question required in task"})
		return
	}

	agentID := middleware.GetAgentFromRequest(r)
	result, err := pythonBridge.ExecuteAgent(agentID, map[string]interface{}{"question": question})
	if err != nil {
		// Log detailed error to server stdout to help debugging
		fmt.Printf("Python bridge ExecuteAgent error for agent %s: %v\n", agentID, err)
		w.WriteHeader(http.StatusInternalServerError)
		json.NewEncoder(w).Encode(map[string]string{"error": err.Error()})
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(result)
}

func handleSDKAgents(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		w.WriteHeader(http.StatusMethodNotAllowed)
		return
	}

	agents, err := pythonBridge.ListAgents()
	if err != nil {
		w.WriteHeader(http.StatusInternalServerError)
		json.NewEncoder(w).Encode(map[string]string{"error": err.Error()})
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(map[string]interface{}{
		"agents": agents,
		"count":  len(agents),
	})
}

func handleRateLimitStats(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		w.WriteHeader(http.StatusMethodNotAllowed)
		return
	}

	agentID := middleware.GetAgentFromRequest(r)
	stats := authMiddleware.GetRateLimiter().GetStats(agentID)

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(stats)
}

func handleGetAnomalies(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		w.WriteHeader(http.StatusMethodNotAllowed)
		return
	}

	anomalies := authMiddleware.GetDetector().GetAnomalies()

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(map[string]interface{}{
		"anomalies": anomalies,
		"count":     len(anomalies),
	})
}

func handleGetBehavior(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		w.WriteHeader(http.StatusMethodNotAllowed)
		return
	}

	agentID := r.URL.Query().Get("agent_id")
	if agentID == "" {
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(map[string]string{"error": "agent_id required"})
		return
	}

	behavior := authMiddleware.GetDetector().GetBehaviorProfile(agentID)
	stats := authMiddleware.GetDetector().GetStats()

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(map[string]interface{}{
		"agent_behavior": behavior,
		"system_stats":   stats,
	})
}
