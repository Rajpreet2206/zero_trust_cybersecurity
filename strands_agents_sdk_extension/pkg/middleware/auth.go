package middleware

import (
	"encoding/json"
	"fmt"
	"net/http"
	"sync"
	"time"

	"github.com/strands/zero-trust-wrapper/pkg/analytics"
	"github.com/strands/zero-trust-wrapper/pkg/identity"
	"github.com/strands/zero-trust-wrapper/pkg/policy"
	"github.com/strands/zero-trust-wrapper/pkg/ratelimit"
)

// VerificationQueue stores pending verifications
type VerificationQueue struct {
	pending map[string]*PendingVerification
	mu      sync.RWMutex
}

// PendingVerification tracks a verification in progress
type PendingVerification struct {
	AgentID    string
	Signature  []byte
	Nonce      string
	CreatedAt  time.Time
	Verified   bool
	VerifiedAt time.Time
	Error      string
}

// AuthMiddleware wraps handlers with authentication and authorization
type AuthMiddleware struct {
	identityMgr    *identity.Manager
	policyEngine   *policy.PolicyEngine
	rateLimiter    *ratelimit.RateLimiter
	detector       *analytics.AnomalyDetector
	agentCache     map[string]*cachedAgent
	cacheMu        sync.RWMutex
	cacheTTL       time.Duration
	verificationQ  *VerificationQueue
	verifiedAgents map[string]time.Time // Track verified agents
	verificationMu sync.RWMutex
}

// cachedAgent stores cached agent data
type cachedAgent struct {
	agent     *identity.Agent
	roles     []string
	expiresAt time.Time
}

// NewAuthMiddleware creates middleware with async verification
func NewAuthMiddleware(identityMgr *identity.Manager, policyEngine *policy.PolicyEngine) *AuthMiddleware {
	am := &AuthMiddleware{
		identityMgr:    identityMgr,
		policyEngine:   policyEngine,
		rateLimiter:    ratelimit.NewRateLimiter(100, 50),
		detector:       analytics.NewAnomalyDetector(),
		agentCache:     make(map[string]*cachedAgent),
		cacheTTL:       30 * time.Second,
		verificationQ:  &VerificationQueue{pending: make(map[string]*PendingVerification)},
		verifiedAgents: make(map[string]time.Time),
	}

	// Start async verification worker
	go am.verificationWorker()

	return am
}

// ProtectedHandler wraps HTTP handlers
type ProtectedHandler struct {
	middleware     *AuthMiddleware
	handler        http.HandlerFunc
	requiredAction string
	publicEndpoint bool
	requireVerify  bool // Whether this endpoint requires verification
}

// ServeHTTP implements http.Handler with async verification
func (ph *ProtectedHandler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	// Public endpoints don't need authentication
	if ph.publicEndpoint {
		ph.handler(w, r)
		return
	}

	// Extract agent ID
	agentID := r.Header.Get("X-Agent-ID")
	if agentID == "" {
		sendError(w, http.StatusUnauthorized, "X-Agent-ID header required")
		return
	}

	// Check cache for agent data
	cachedData := ph.middleware.getFromCache(agentID)
	var agent *identity.Agent
	var roles []string

	if cachedData != nil {
		agent = cachedData.agent
		roles = cachedData.roles
	} else {
		// Load from registry
		var err error
		agent, err = ph.middleware.identityMgr.GetAgent(agentID)
		if err != nil {
			ph.middleware.detector.RecordFailedAuth(agentID)
			sendError(w, http.StatusUnauthorized, "agent not found")
			return
		}
		roles = ph.middleware.policyEngine.GetAgentRoles(agentID)
		ph.middleware.cacheAgent(agentID, agent, roles)
	}

	// Check agent status
	if agent.Status != "active" {
		ph.middleware.detector.RecordFailedAuth(agentID)
		sendError(w, http.StatusForbidden, fmt.Sprintf("agent status is %s", agent.Status))
		return
	}

	// Authorization check
	if ph.requiredAction != "" {
		if !ph.middleware.checkPermissionFast(roles, ph.requiredAction) {
			ph.middleware.detector.RecordFailedAuth(agentID)
			sendError(w, http.StatusForbidden, fmt.Sprintf("agent not authorized for action: %s", ph.requiredAction))
			return
		}
	}

	// Rate limit check
	if !ph.middleware.rateLimiter.AllowRequest(agentID) {
		sendError(w, http.StatusTooManyRequests, "rate limit exceeded")
		return
	}

	// ASYNC VERIFICATION: Check if verification is required
	if ph.requireVerify {
		// Get signature from request header
		signature := r.Header.Get("X-Signature")
		if signature == "" {
			sendError(w, http.StatusBadRequest, "X-Signature header required for verification")
			return
		}

		// Check if already verified recently
		if !ph.middleware.isRecentlyVerified(agentID) {
			// Queue verification asynchronously (will process in background)
			ph.middleware.queueVerification(agentID, []byte(signature), agent.Nonce)
		}
	}

	// Record request asynchronously
	go func() {
		ph.middleware.detector.RecordRequest(agentID)
	}()

	// Add context
	r.Header.Set("X-Agent-Verified", "true")

	// Call handler
	ph.handler(w, r)
}

// queueVerification adds a verification to the queue
func (am *AuthMiddleware) queueVerification(agentID string, signature []byte, nonce string) {
	am.verificationQ.mu.Lock()
	defer am.verificationQ.mu.Unlock()

	am.verificationQ.pending[agentID] = &PendingVerification{
		AgentID:   agentID,
		Signature: signature,
		Nonce:     nonce,
		CreatedAt: time.Now(),
		Verified:  false,
	}
}

// verificationWorker processes verifications asynchronously
func (am *AuthMiddleware) verificationWorker() {
	ticker := time.NewTicker(100 * time.Millisecond)
	defer ticker.Stop()

	for range ticker.C {
		am.verificationQ.mu.Lock()
		for agentID, pv := range am.verificationQ.pending {
			// Get agent to verify it exists
			if _, err := am.identityMgr.GetAgent(agentID); err != nil {
				pv.Error = "agent not found"
				pv.VerifiedAt = time.Now()
				continue
			}

			// Verify signature (pv.Signature is already a hex string from the client)
			if err := am.identityMgr.VerifyAgent(agentID, string(pv.Signature), pv.Nonce); err != nil {
				pv.Error = err.Error()
				pv.VerifiedAt = time.Now()
				continue
			}

			// Verification successful
			pv.Verified = true
			pv.VerifiedAt = time.Now()

			// Mark as verified (cache for 5 minutes)
			am.verificationMu.Lock()
			am.verifiedAgents[agentID] = time.Now().Add(5 * time.Minute)
			am.verificationMu.Unlock()
		}

		// Cleanup old verifications
		for agentID, pv := range am.verificationQ.pending {
			if time.Since(pv.CreatedAt) > 30*time.Second {
				delete(am.verificationQ.pending, agentID)
			}
		}
		am.verificationQ.mu.Unlock()
	}
}

// isRecentlyVerified checks if agent was recently verified
func (am *AuthMiddleware) isRecentlyVerified(agentID string) bool {
	am.verificationMu.RLock()
	defer am.verificationMu.RUnlock()

	expiresAt, exists := am.verifiedAgents[agentID]
	if !exists {
		return false
	}

	return time.Now().Before(expiresAt)
}

// Cache operations
func (am *AuthMiddleware) getFromCache(agentID string) *cachedAgent {
	am.cacheMu.RLock()
	defer am.cacheMu.RUnlock()

	cached, exists := am.agentCache[agentID]
	if !exists {
		return nil
	}

	if time.Now().After(cached.expiresAt) {
		return nil
	}

	return cached
}

func (am *AuthMiddleware) cacheAgent(agentID string, agent *identity.Agent, roles []string) {
	am.cacheMu.Lock()
	defer am.cacheMu.Unlock()

	am.agentCache[agentID] = &cachedAgent{
		agent:     agent,
		roles:     roles,
		expiresAt: time.Now().Add(am.cacheTTL),
	}
}

func (am *AuthMiddleware) checkPermissionFast(roles []string, action string) bool {
	allRoles := am.policyEngine.GetRoles()

	for _, roleName := range roles {
		role, exists := allRoles[roleName]
		if !exists {
			continue
		}

		for _, perm := range role.Permissions {
			if perm == action {
				return true
			}
		}
	}

	return false
}

// Handler protection methods
func (am *AuthMiddleware) Protect(handler http.HandlerFunc, requiredAction string) http.Handler {
	return &ProtectedHandler{
		middleware:     am,
		handler:        handler,
		requiredAction: requiredAction,
		publicEndpoint: false,
		requireVerify:  false,
	}
}

func (am *AuthMiddleware) ProtectWithVerify(handler http.HandlerFunc, requiredAction string) http.Handler {
	return &ProtectedHandler{
		middleware:     am,
		handler:        handler,
		requiredAction: requiredAction,
		publicEndpoint: false,
		requireVerify:  true,
	}
}

func (am *AuthMiddleware) ProtectPublic(handler http.HandlerFunc) http.Handler {
	return &ProtectedHandler{
		middleware:     am,
		handler:        handler,
		requiredAction: "",
		publicEndpoint: true,
		requireVerify:  false,
	}
}

func (am *AuthMiddleware) GetRateLimiter() *ratelimit.RateLimiter {
	return am.rateLimiter
}

func (am *AuthMiddleware) GetDetector() *analytics.AnomalyDetector {
	return am.detector
}

func sendError(w http.ResponseWriter, statusCode int, message string) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(statusCode)
	json.NewEncoder(w).Encode(map[string]string{"error": message})
}

func GetAgentFromRequest(r *http.Request) string {
	return r.Header.Get("X-Agent-ID")
}
