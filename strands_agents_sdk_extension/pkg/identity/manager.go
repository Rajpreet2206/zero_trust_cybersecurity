// ============================================================
// FILE 1: CREATE NEW FILE - pkg/identity/manager.go
// ============================================================
// Location: strands-go-wrapper/pkg/identity/manager.go
// Action: CREATE THIS NEW FILE (it doesn't exist yet)

package identity

import (
	"fmt"
	"sync"
	"time"

	"github.com/strands/zero-trust-wrapper/pkg/audit"
	"github.com/strands/zero-trust-wrapper/pkg/crypto"
)

// Agent represents a registered agent with credentials
type Agent struct {
	AgentID       string `json:"agent_id"`
	PublicKeyHex  string `json:"public_key"`
	PrivateKeyHex string `json:"private_key"`
	Nonce         string `json:"nonce"`
	CreatedAt     int64  `json:"created_at"`
	ExpiresAt     int64  `json:"expires_at"`
	Status        string `json:"status"`
}

// Manager manages all agents
type Manager struct {
	agents map[string]*Agent
	mu     sync.RWMutex
	crypto *crypto.Engine
	logger *audit.Logger // ADD THIS LINE
}

func (m *Manager) GetAuditLog() []audit.AuditEvent {
	return m.logger.GetEvents()
}

// GetAuditLogCount returns count of audit events
func (m *Manager) GetAuditLogCount() int {
	return m.logger.GetEventCount()
}

// NewManager creates a new identity manager
func NewManager(cryptoEngine *crypto.Engine) *Manager {
	return &Manager{
		agents: make(map[string]*Agent),
		crypto: cryptoEngine,
		logger: audit.NewLogger(), // ADD THIS LINE
	}
}

// RegisterAgent creates and stores a new agent with credentials
func (m *Manager) RegisterAgent(agentID string) (*Agent, error) {
	m.mu.Lock()
	defer m.mu.Unlock()

	// Check if agent already exists
	if _, exists := m.agents[agentID]; exists {
		return nil, fmt.Errorf("agent %s already registered", agentID)
	}

	// Generate keypair
	keyPair, err := m.crypto.GenerateKeyPair()
	if err != nil {
		return nil, err
	}

	// Generate nonce
	nonce, err := m.crypto.GenerateRandomBytes(16)
	if err != nil {
		return nil, err
	}

	now := time.Now().Unix()
	agent := &Agent{
		AgentID:       agentID,
		PublicKeyHex:  m.crypto.PublicKeyToHex(keyPair.PublicKey),
		PrivateKeyHex: m.crypto.PrivateKeyToHex(keyPair.PrivateKey),
		Nonce:         m.crypto.BytesToHex(nonce),
		CreatedAt:     now,
		ExpiresAt:     now + 3600, // 1 hour
		Status:        "active",
	}

	m.agents[agentID] = agent
	m.logger.LogEvent("REGISTER", agentID, "agent_registration", "SUCCESS", map[string]interface{}{
		"agent_id":   agentID,
		"expires_at": agent.ExpiresAt,
	})
	return agent, nil
}

// GetAgent retrieves an agent by ID
func (m *Manager) GetAgent(agentID string) (*Agent, error) {
	m.mu.RLock()
	defer m.mu.RUnlock()

	agent, exists := m.agents[agentID]
	if !exists {
		return nil, fmt.Errorf("agent not found: %s", agentID)
	}

	return agent, nil
}

// ListAgents returns all agents without private keys
func (m *Manager) ListAgents() []*Agent {
	m.mu.RLock()
	defer m.mu.RUnlock()

	agents := make([]*Agent, 0, len(m.agents))
	for _, agent := range m.agents {
		// Copy without private key for security
		safeCopy := &Agent{
			AgentID:      agent.AgentID,
			PublicKeyHex: agent.PublicKeyHex,
			Nonce:        agent.Nonce,
			CreatedAt:    agent.CreatedAt,
			ExpiresAt:    agent.ExpiresAt,
			Status:       agent.Status,
		}
		agents = append(agents, safeCopy)
	}
	return agents
}

// VerifyAgent verifies agent signature
func (m *Manager) VerifyAgent(agentID string, signatureHex string, nonceHex string) error {
	m.mu.RLock()
	defer m.mu.RUnlock()

	agent, exists := m.agents[agentID]
	if !exists {
		return fmt.Errorf("agent not found")
	}

	if agent.Status != "active" {
		return fmt.Errorf("agent not active")
	}

	// Check expiration
	if time.Now().Unix() > agent.ExpiresAt {
		return fmt.Errorf("agent credentials expired")
	}

	// Convert hex strings to bytes
	signature, err := m.crypto.HexToBytes(signatureHex)
	if err != nil {
		return fmt.Errorf("invalid signature format")
	}

	// Verify nonce matches
	if nonceHex != agent.Nonce {
		return fmt.Errorf("nonce mismatch")
	}

	// Convert public key
	publicKey, err := m.crypto.HexToPublicKey(agent.PublicKeyHex)
	if err != nil {
		return err
	}

	// Verify signature
	if err := m.crypto.Verify(publicKey, []byte(agent.Nonce), signature); err != nil {
		return fmt.Errorf("signature verification failed")
	}
	m.mu.Lock()
	defer m.mu.Unlock()
	m.logger.LogEvent("VERIFY", agentID, "agent_verification", "SUCCESS", map[string]interface{}{
		"nonce_verified": true,
	})
	return nil
}

// RevokeAgent revokes an agent
func (m *Manager) RevokeAgent(agentID string) error {
	m.mu.Lock()
	defer m.mu.Unlock()

	agent, exists := m.agents[agentID]
	if !exists {
		return fmt.Errorf("agent not found")
	}

	agent.Status = "revoked"
	m.logger.LogEvent("REVOKE", agentID, "agent_revocation", "SUCCESS", map[string]interface{}{
		"revoked_at": time.Now().Unix(),
	})
	return nil
}
