// cmd/main.go
package main

import (
	"fmt"
	"log"
	"net/http"

	"go.uber.org/zap"

	"github.com/Rajpreet2206/zero_trust_cybersecurity/zt_wrapper/pkg/mtls"
	"github.com/Rajpreet2206/zero_trust_cybersecurity/zt_wrapper/pkg/opa"
	"github.com/Rajpreet2206/zero_trust_cybersecurity/zt_wrapper/pkg/telemetry"
)

// ZTWrapper wraps agent calls with logging and policy
type ZTWrapper struct {
	Logger *zap.Logger
	Policy *opa.Policy
}

// SecureCall verifies policy, logs request, and calls the agent
func (z *ZTWrapper) SecureCall(agentName, payload string, context map[string]interface{}) (string, error) {
	// Evaluate OPA policy
	allowed, err := z.Policy.Evaluate(context)
	if err != nil {
		z.Logger.Error("Policy evaluation failed", zap.Error(err))
		return "", err
	}

	if !allowed {
		z.Logger.Warn("Access denied by policy", zap.String("agent", agentName))
		return "", fmt.Errorf("access denied by policy")
	}

	// Log allowed request
	z.Logger.Info("Agent call allowed",
		zap.String("agent", agentName),
		zap.String("payload", payload),
	)

	// TODO: Replace with actual Strands SDK call
	response := fmt.Sprintf("Agent %s processed payload: %s", agentName, payload)
	return response, nil
}

// HTTP handler for incoming agent requests
func (z *ZTWrapper) handler(w http.ResponseWriter, r *http.Request) {
	agent := r.URL.Query().Get("agent")
	payload := r.URL.Query().Get("payload")
	context := map[string]interface{}{
		"input": map[string]interface{}{
			"source":  agent,
			"payload": payload,
		},
	}

	resp, err := z.SecureCall(agent, payload, context)
	if err != nil {
		http.Error(w, err.Error(), http.StatusForbidden)
		return
	}

	w.Write([]byte(resp))
}

func main() {
	// Initialize logger
	logger, err := telemetry.NewLogger()
	if err != nil {
		log.Fatalf("Failed to initialize logger: %v", err)
	}

	// Load OPA policy
	policy, err := opa.LoadPolicy([]string{"opa/policies/agents.rego"})
	if err != nil {
		logger.Fatal("Failed to load OPA policy", zap.Error(err))
	}

	// Initialize Zero Trust Wrapper
	wrapper := &ZTWrapper{
		Logger: logger,
		Policy: policy,
	}

	// Setup mTLS server
	tlsConfig, err := mtls.LoadMTLSServerConfig("certs/server.crt", "certs/server.key", "certs/ca.crt")
	if err != nil {
		logger.Fatal("Failed to setup mTLS", zap.Error(err))
	}

	server := &http.Server{
		Addr:      ":8443",
		Handler:   http.HandlerFunc(wrapper.handler),
		TLSConfig: tlsConfig,
	}

	logger.Info("Starting Zero Trust Wrapper server on :8443")
	if err := server.ListenAndServeTLS("", ""); err != nil {
		logger.Fatal("Server failed", zap.Error(err))
	}
}
