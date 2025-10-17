package sdk

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"
)

// Bridge connects to Python Strands SDK
type Bridge struct {
	endpoint   string
	httpClient *http.Client
	timeout    time.Duration
}

// NewBridge creates a new Python SDK bridge
func NewBridge(endpoint string, timeoutSeconds int) *Bridge {
	if timeoutSeconds == 0 {
		timeoutSeconds = 30
	}

	return &Bridge{
		endpoint: endpoint,
		httpClient: &http.Client{
			Timeout: time.Duration(timeoutSeconds) * time.Second,
		},
		timeout: time.Duration(timeoutSeconds) * time.Second,
	}
}

// HealthCheck checks if Python SDK is healthy
func (b *Bridge) HealthCheck() error {
	resp, err := b.httpClient.Get(b.endpoint + "/health")
	if err != nil {
		return fmt.Errorf("health check failed: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("health check returned status %d", resp.StatusCode)
	}

	return nil
}

// ExecuteAgent executes an agent task on Python SDK
func (b *Bridge) ExecuteAgent(agentID string, taskData map[string]interface{}) (map[string]interface{}, error) {
	payload := map[string]interface{}{
		"agent_id": agentID,
		"task":     taskData,
	}

	bodyBytes, err := json.Marshal(payload)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal request: %w", err)
	}

	resp, err := b.httpClient.Post(
		b.endpoint+"/execute",
		"application/json",
		bytes.NewReader(bodyBytes),
	)
	if err != nil {
		return nil, fmt.Errorf("failed to execute agent: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		bodyText, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("execution failed with status %d: %s", resp.StatusCode, string(bodyText))
	}

	var result map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, fmt.Errorf("failed to decode response: %w", err)
	}

	return result, nil
}

// GetAgentInfo retrieves agent info from Python SDK
func (b *Bridge) GetAgentInfo(agentID string) (map[string]interface{}, error) {
	resp, err := b.httpClient.Get(b.endpoint + "/agents/" + agentID)
	if err != nil {
		return nil, fmt.Errorf("failed to get agent info: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("get agent info failed with status %d", resp.StatusCode)
	}

	var result map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, fmt.Errorf("failed to decode response: %w", err)
	}

	return result, nil
}

// ListAgents lists all agents from Python SDK
func (b *Bridge) ListAgents() ([]map[string]interface{}, error) {
	resp, err := b.httpClient.Get(b.endpoint + "/agents")
	if err != nil {
		return nil, fmt.Errorf("failed to list agents: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("list agents failed with status %d", resp.StatusCode)
	}

	var result map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, fmt.Errorf("failed to decode response: %w", err)
	}

	// Extract agents array
	agents, ok := result["agents"].([]interface{})
	if !ok {
		return nil, fmt.Errorf("agents field not found or invalid type")
	}

	var agentsList []map[string]interface{}
	for _, agent := range agents {
		if agentMap, ok := agent.(map[string]interface{}); ok {
			agentsList = append(agentsList, agentMap)
		}
	}

	return agentsList, nil
}

// IsConnected tests connection to Python SDK
func (b *Bridge) IsConnected() bool {
	return b.HealthCheck() == nil
}
