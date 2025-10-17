package server

import (
	"encoding/json"
	"fmt"
	"net/http"
	"time"

	"github.com/strands/zero-trust-wrapper/pkg/config"
	"github.com/strands/zero-trust-wrapper/pkg/crypto"
	"github.com/strands/zero-trust-wrapper/pkg/identity"
	"github.com/strands/zero-trust-wrapper/pkg/logger"
)

// HTTPServer wraps HTTP server with zero-trust handlers
type HTTPServer struct {
	*http.Server
	identityMgr  *identity.Manager
	cryptoEngine *crypto.Engine
	log          *logger.Logger
	config       *config.Config
}

// NewHTTPServer creates a new HTTP server with zero-trust endpoints
func NewHTTPServer(cfg *config.Config, identityMgr *identity.Manager, cryptoEngine *crypto.Engine, log *logger.Logger) (*HTTPServer, error) {
	mux := http.NewServeMux()

	hs := &HTTPServer{
		identityMgr:  identityMgr,
		cryptoEngine: cryptoEngine,
		log:          log,
		config:       cfg,
	}

	// Health check endpoint
	mux.HandleFunc("/health", hs.handleHealth)

	// Identity management endpoints
	mux.HandleFunc("/api/v1/identity/register", hs.handleRegisterAgent)
	mux.HandleFunc("/api/v1/identity/verify", hs.handleVerifyAgent)
	mux.HandleFunc("/api/v1/identity/revoke", hs.handleRevokeAgent)
	mux.HandleFunc("/api/v1/identity/renew", hs.handleRenewAgent)
	mux.HandleFunc("/api/v1/identity/list", hs.handleListAgents)
	mux.HandleFunc("/api/v1/identity/stats", hs.handleGetStats)

	// Crypto endpoints
	mux.HandleFunc("/api/v1/crypto/encrypt", hs.handleEncrypt)
	mux.HandleFunc("/api/v1/crypto/decrypt", hs.handleDecrypt)

	hs.Server = &http.Server{
		Addr:           fmt.Sprintf("%s:%d", cfg.Server.Host, cfg.Server.Port),
		Handler:        mux,
		ReadTimeout:    time.Duration(cfg.Server.ReadTimeout) * time.Second,
		WriteTimeout:   time.Duration(cfg.Server.WriteTimeout) * time.Second,
		MaxHeaderBytes: cfg.Server.MaxHeaderBytes,
	}

	return hs, nil
}

// ResponseWrapper wraps all API responses
type ResponseWrapper struct {
	Success bool        `json:"success"`
	Data    interface{} `json:"data,omitempty"`
	Error   string      `json:"error,omitempty"`
	Code    int         `json:"code"`
}

// sendResponse sends a JSON response
func (hs *HTTPServer) sendResponse(w http.ResponseWriter, statusCode int, data interface{}, errMsg string) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(statusCode)

	resp := ResponseWrapper{
		Success: errMsg == "",
		Data:    data,
		Error:   errMsg,
		Code:    statusCode,
	}

	json.NewEncoder(w).Encode(resp)
}

// ===== HEALTH ENDPOINTS =====

func (hs *HTTPServer) handleHealth(w http.ResponseWriter, r *http.Request) {
	hs.sendResponse(w, http.StatusOK, map[string]string{
		"status": "healthy",
	}, "")
}

// ===== IDENTITY ENDPOINTS =====

func (hs *HTTPServer) handleRegisterAgent(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		hs.sendResponse(w, http.StatusMethodNotAllowed, nil, "Method not allowed")
		return
	}

	var req struct {
		AgentID string `json:"agent_id"`
	}

	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		hs.sendResponse(w, http.StatusBadRequest, nil, fmt.Sprintf("Invalid request: %v", err))
		return
	}

	if req.AgentID == "" {
		hs.sendResponse(w, http.StatusBadRequest, nil, "agent_id is required")
		return
	}

	agent, err := hs.identityMgr.RegisterAgent(req.AgentID)
	if err != nil {
		hs.sendResponse(w, http.StatusConflict, nil, err.Error())
		return
	}

	resp := map[string]interface{}{
		"agent_id":    agent.AgentID,
		"public_key":  agent.PublicKeyHex,
		"private_key": agent.PrivateKeyHex,
		"nonce":       agent.Nonce,
		"created_at":  agent.CreatedAt,
		"expires_at":  agent.ExpiresAt,
		"status":      agent.Status,
	}

	hs.sendResponse(w, http.StatusCreated, resp, "")
}

func (hs *HTTPServer) handleVerifyAgent(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		hs.sendResponse(w, http.StatusMethodNotAllowed, nil, "Method not allowed")
		return
	}

	var req struct {
		AgentID   string `json:"agent_id"`
		Signature string `json:"signature"`
		Nonce     string `json:"nonce"`
	}

	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		hs.sendResponse(w, http.StatusBadRequest, nil, fmt.Sprintf("Invalid request: %v", err))
		return
	}

	signature, err := hs.cryptoEngine.HexToBytes(req.Signature)
	if err != nil {
		hs.sendResponse(w, http.StatusBadRequest, nil, "Invalid signature format")
		return
	}

	if err := hs.identityMgr.VerifyAgent(req.AgentID, signature, req.Nonce); err != nil {
		hs.sendResponse(w, http.StatusUnauthorized, nil, err.Error())
		return
	}

	hs.sendResponse(w, http.StatusOK, map[string]string{
		"status": "verified",
	}, "")
}

func (hs *HTTPServer) handleRevokeAgent(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		hs.sendResponse(w, http.StatusMethodNotAllowed, nil, "Method not allowed")
		return
	}

	var req struct {
		AgentID string `json:"agent_id"`
	}

	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		hs.sendResponse(w, http.StatusBadRequest, nil, fmt.Sprintf("Invalid request: %v", err))
		return
	}

	if err := hs.identityMgr.RevokeAgent(req.AgentID); err != nil {
		hs.sendResponse(w, http.StatusNotFound, nil, err.Error())
		return
	}

	hs.sendResponse(w, http.StatusOK, map[string]string{
		"status": "revoked",
	}, "")
}

func (hs *HTTPServer) handleRenewAgent(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		hs.sendResponse(w, http.StatusMethodNotAllowed, nil, "Method not allowed")
		return
	}

	var req struct {
		AgentID string `json:"agent_id"`
	}

	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		hs.sendResponse(w, http.StatusBadRequest, nil, fmt.Sprintf("Invalid request: %v", err))
		return
	}

	agent, err := hs.identityMgr.RenewAgent(req.AgentID)
	if err != nil {
		hs.sendResponse(w, http.StatusBadRequest, nil, err.Error())
		return
	}

	resp := map[string]interface{}{
		"agent_id":    agent.AgentID,
		"public_key":  agent.PublicKeyHex,
		"private_key": agent.PrivateKeyHex,
		"expires_at":  agent.ExpiresAt,
		"status":      agent.Status,
	}

	hs.sendResponse(w, http.StatusOK, resp, "")
}

func (hs *HTTPServer) handleListAgents(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		hs.sendResponse(w, http.StatusMethodNotAllowed, nil, "Method not allowed")
		return
	}

	agents := hs.identityMgr.ListAgents()
	hs.sendResponse(w, http.StatusOK, map[string]interface{}{
		"agents": agents,
		"count":  len(agents),
	}, "")
}

func (hs *HTTPServer) handleGetStats(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		hs.sendResponse(w, http.StatusMethodNotAllowed, nil, "Method not allowed")
		return
	}

	stats := hs.identityMgr.GetStats()
	hs.sendResponse(w, http.StatusOK, stats, "")
}

// ===== CRYPTO ENDPOINTS =====

func (hs *HTTPServer) handleEncrypt(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		hs.sendResponse(w, http.StatusMethodNotAllowed, nil, "Method not allowed")
		return
	}

	var req struct {
		Key       string `json:"key"`
		Plaintext string `json:"plaintext"`
	}

	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		hs.sendResponse(w, http.StatusBadRequest, nil, fmt.Sprintf("Invalid request: %v", err))
		return
	}

	key, err := hs.cryptoEngine.HexToBytes(req.Key)
	if err != nil {
		hs.sendResponse(w, http.StatusBadRequest, nil, "Invalid key format")
		return
	}

	ciphertext, err := hs.cryptoEngine.EncryptData(key, []byte(req.Plaintext))
	if err != nil {
		hs.sendResponse(w, http.StatusInternalServerError, nil, err.Error())
		return
	}

	hs.sendResponse(w, http.StatusOK, map[string]interface{}{
		"ciphertext": hs.cryptoEngine.BytesToHex(ciphertext),
	}, "")
}

func (hs *HTTPServer) handleDecrypt(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		hs.sendResponse(w, http.StatusMethodNotAllowed, nil, "Method not allowed")
		return
	}

	var req struct {
		Key        string `json:"key"`
		Ciphertext string `json:"ciphertext"`
	}

	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		hs.sendResponse(w, http.StatusBadRequest, nil, fmt.Sprintf("Invalid request: %v", err))
		return
	}

	key, err := hs.cryptoEngine.HexToBytes(req.Key)
	if err != nil {
		hs.sendResponse(w, http.StatusBadRequest, nil, "Invalid key format")
		return
	}

	ciphertext, err := hs.cryptoEngine.HexToBytes(req.Ciphertext)
	if err != nil {
		hs.sendResponse(w, http.StatusBadRequest, nil, "Invalid ciphertext format")
		return
	}

	plaintext, err := hs.cryptoEngine.DecryptData(key, ciphertext)
	if err != nil {
		hs.sendResponse(w, http.StatusInternalServerError, nil, err.Error())
		return
	}

	hs.sendResponse(w, http.StatusOK, map[string]interface{}{
		"plaintext": string(plaintext),
	}, "")
}
