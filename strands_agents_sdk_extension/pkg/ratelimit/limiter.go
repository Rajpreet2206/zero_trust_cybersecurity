package ratelimit

import (
	"sync"
	"time"
)

// RateLimiter implements token bucket algorithm
type RateLimiter struct {
	agents map[string]*AgentBucket
	mu     sync.RWMutex

	// Config
	requestsPerSecond int
	burstSize         int
	cleanupInterval   time.Duration
}

// AgentBucket tracks tokens for one agent
type AgentBucket struct {
	tokens    int
	lastFill  time.Time
	requests  int
	lastReset time.Time
}

// NewRateLimiter creates a new rate limiter
func NewRateLimiter(requestsPerSecond int, burstSize int) *RateLimiter {
	rl := &RateLimiter{
		agents:            make(map[string]*AgentBucket),
		requestsPerSecond: requestsPerSecond,
		burstSize:         burstSize,
		cleanupInterval:   5 * time.Minute,
	}

	// Start cleanup goroutine
	go rl.cleanupOldBuckets()

	return rl
}

// AllowRequest checks if agent can make a request
func (rl *RateLimiter) AllowRequest(agentID string) bool {
	rl.mu.Lock()
	defer rl.mu.Unlock()

	bucket, exists := rl.agents[agentID]
	if !exists {
		// New agent, create bucket
		bucket = &AgentBucket{
			tokens:    rl.burstSize,
			lastFill:  time.Now(),
			requests:  0,
			lastReset: time.Now(),
		}
		rl.agents[agentID] = bucket
	}

	// Refill tokens based on time elapsed
	now := time.Now()
	elapsed := now.Sub(bucket.lastFill)
	tokensToAdd := int(elapsed.Seconds()) * rl.requestsPerSecond

	if tokensToAdd > 0 {
		bucket.tokens = min(bucket.tokens+tokensToAdd, rl.burstSize)
		bucket.lastFill = now
	}

	// Check if request is allowed
	if bucket.tokens > 0 {
		bucket.tokens--
		bucket.requests++
		return true
	}

	return false
}

// GetStats returns rate limit stats for an agent
func (rl *RateLimiter) GetStats(agentID string) map[string]interface{} {
	rl.mu.RLock()
	defer rl.mu.RUnlock()

	bucket, exists := rl.agents[agentID]
	if !exists {
		return map[string]interface{}{
			"agent_id":       agentID,
			"available":      rl.burstSize,
			"total_requests": 0,
			"limited":        false,
		}
	}

	return map[string]interface{}{
		"agent_id":       agentID,
		"available":      bucket.tokens,
		"burst_size":     rl.burstSize,
		"total_requests": bucket.requests,
		"limited":        bucket.tokens == 0,
	}
}

// Reset resets the limiter for an agent
func (rl *RateLimiter) Reset(agentID string) {
	rl.mu.Lock()
	defer rl.mu.Unlock()

	delete(rl.agents, agentID)
}

// cleanupOldBuckets removes inactive agent buckets
func (rl *RateLimiter) cleanupOldBuckets() {
	ticker := time.NewTicker(rl.cleanupInterval)
	defer ticker.Stop()

	for range ticker.C {
		rl.mu.Lock()

		now := time.Now()
		for agentID, bucket := range rl.agents {
			// Remove buckets inactive for more than 1 hour
			if now.Sub(bucket.lastFill) > time.Hour {
				delete(rl.agents, agentID)
			}
		}

		rl.mu.Unlock()
	}
}

// min returns minimum of two integers
func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}
