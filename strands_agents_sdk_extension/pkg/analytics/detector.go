package analytics

import (
	"fmt"
	"sync"
	"time"
)

// Anomaly represents a detected anomaly
type Anomaly struct {
	AnomalyID    string                 `json:"anomaly_id"`
	Timestamp    int64                  `json:"timestamp"`
	AgentID      string                 `json:"agent_id"`
	Type         string                 `json:"type"`     // "rate_spike", "failed_auth", "unusual_time", "permission_abuse"
	Severity     string                 `json:"severity"` // "low", "medium", "high"
	Description  string                 `json:"description"`
	Details      map[string]interface{} `json:"details"`
	AutoResolved bool                   `json:"auto_resolved"`
}

// AgentBehavior tracks an agent's behavior baseline
type AgentBehavior struct {
	AgentID           string
	RequestCount      int
	FailedAuthCount   int
	LastRequestTime   int64
	LastFailureTime   int64
	AverageReqPerHour float64
	PeakHour          int
	TotalAnomalies    int
}

// AnomalyDetector detects behavioral anomalies
type AnomalyDetector struct {
	behaviors map[string]*AgentBehavior
	anomalies []Anomaly
	mu        sync.RWMutex

	// Thresholds
	rateSpikeThreshold   int     // Requests per minute to trigger alert
	failedAuthThreshold  int     // Failed auth attempts
	unusualTimeThreshold float64 // Standard deviations from baseline
}

// NewAnomalyDetector creates a new anomaly detector
func NewAnomalyDetector() *AnomalyDetector {
	return &AnomalyDetector{
		behaviors:            make(map[string]*AgentBehavior),
		anomalies:            make([]Anomaly, 0),
		rateSpikeThreshold:   100, // 100 requests per minute
		failedAuthThreshold:  5,   // 5 failed auth attempts
		unusualTimeThreshold: 3.0, // 3 standard deviations
	}
}

// RecordRequest records an agent request for behavior tracking
func (ad *AnomalyDetector) RecordRequest(agentID string) {
	ad.mu.Lock()
	defer ad.mu.Unlock()

	behavior, exists := ad.behaviors[agentID]
	if !exists {
		behavior = &AgentBehavior{
			AgentID:         agentID,
			RequestCount:    0,
			FailedAuthCount: 0,
			LastRequestTime: time.Now().Unix(),
		}
		ad.behaviors[agentID] = behavior
	}

	behavior.RequestCount++
	behavior.LastRequestTime = time.Now().Unix()

	// Check for rate spike
	ad.checkRateSpike(agentID, behavior)
}

// RecordFailedAuth records a failed authentication attempt
func (ad *AnomalyDetector) RecordFailedAuth(agentID string) {
	ad.mu.Lock()
	defer ad.mu.Unlock()

	behavior, exists := ad.behaviors[agentID]
	if !exists {
		behavior = &AgentBehavior{
			AgentID:         agentID,
			RequestCount:    0,
			FailedAuthCount: 0,
		}
		ad.behaviors[agentID] = behavior
	}

	behavior.FailedAuthCount++
	behavior.LastFailureTime = time.Now().Unix()

	// Check for brute force attempt
	ad.checkBruteForce(agentID, behavior)
}

// checkRateSpike detects abnormal request rate increases
func (ad *AnomalyDetector) checkRateSpike(agentID string, behavior *AgentBehavior) {
	// If request count exceeds threshold in a short time
	if behavior.RequestCount > ad.rateSpikeThreshold {
		anomaly := Anomaly{
			AnomalyID:   fmt.Sprintf("anom_%d", time.Now().UnixNano()),
			Timestamp:   time.Now().Unix(),
			AgentID:     agentID,
			Type:        "rate_spike",
			Severity:    "medium",
			Description: fmt.Sprintf("Agent %s exceeded request rate threshold", agentID),
			Details: map[string]interface{}{
				"request_count": behavior.RequestCount,
				"threshold":     ad.rateSpikeThreshold,
			},
		}

		ad.anomalies = append(ad.anomalies, anomaly)
		behavior.TotalAnomalies++
	}
}

// checkBruteForce detects brute force authentication attempts
func (ad *AnomalyDetector) checkBruteForce(agentID string, behavior *AgentBehavior) {
	// If failed auth attempts exceed threshold
	if behavior.FailedAuthCount > ad.failedAuthThreshold {
		anomaly := Anomaly{
			AnomalyID:   fmt.Sprintf("anom_%d", time.Now().UnixNano()),
			Timestamp:   time.Now().Unix(),
			AgentID:     agentID,
			Type:        "failed_auth",
			Severity:    "high",
			Description: fmt.Sprintf("Agent %s exceeded failed authentication attempts", agentID),
			Details: map[string]interface{}{
				"failed_attempts": behavior.FailedAuthCount,
				"threshold":       ad.failedAuthThreshold,
			},
		}

		ad.anomalies = append(ad.anomalies, anomaly)
		behavior.TotalAnomalies++
	}
}

// GetAnomalies returns all detected anomalies
func (ad *AnomalyDetector) GetAnomalies() []Anomaly {
	ad.mu.RLock()
	defer ad.mu.RUnlock()

	// Return copy
	anomaliesCopy := make([]Anomaly, len(ad.anomalies))
	copy(anomaliesCopy, ad.anomalies)
	return anomaliesCopy
}

// GetAnomaliesByAgent returns anomalies for a specific agent
func (ad *AnomalyDetector) GetAnomaliesByAgent(agentID string) []Anomaly {
	ad.mu.RLock()
	defer ad.mu.RUnlock()

	var filtered []Anomaly
	for _, anomaly := range ad.anomalies {
		if anomaly.AgentID == agentID {
			filtered = append(filtered, anomaly)
		}
	}
	return filtered
}

// GetBehaviorProfile returns behavior stats for an agent
func (ad *AnomalyDetector) GetBehaviorProfile(agentID string) map[string]interface{} {
	ad.mu.RLock()
	defer ad.mu.RUnlock()

	behavior, exists := ad.behaviors[agentID]
	if !exists {
		return map[string]interface{}{
			"agent_id": agentID,
			"status":   "no_data",
		}
	}

	return map[string]interface{}{
		"agent_id":          agentID,
		"request_count":     behavior.RequestCount,
		"failed_auth_count": behavior.FailedAuthCount,
		"total_anomalies":   behavior.TotalAnomalies,
		"last_request_time": behavior.LastRequestTime,
		"last_failure_time": behavior.LastFailureTime,
		"status":            "monitored",
	}
}

// ResetAgent resets behavior tracking for an agent
func (ad *AnomalyDetector) ResetAgent(agentID string) {
	ad.mu.Lock()
	defer ad.mu.Unlock()

	delete(ad.behaviors, agentID)
}

// GetStats returns overall analytics statistics
func (ad *AnomalyDetector) GetStats() map[string]interface{} {
	ad.mu.RLock()
	defer ad.mu.RUnlock()

	highSeverityCount := 0
	mediumSeverityCount := 0
	lowSeverityCount := 0

	for _, anomaly := range ad.anomalies {
		switch anomaly.Severity {
		case "high":
			highSeverityCount++
		case "medium":
			mediumSeverityCount++
		case "low":
			lowSeverityCount++
		}
	}

	return map[string]interface{}{
		"total_agents":      len(ad.behaviors),
		"total_anomalies":   len(ad.anomalies),
		"high_severity":     highSeverityCount,
		"medium_severity":   mediumSeverityCount,
		"low_severity":      lowSeverityCount,
		"alert_threshold":   ad.rateSpikeThreshold,
		"brute_force_limit": ad.failedAuthThreshold,
	}
}
