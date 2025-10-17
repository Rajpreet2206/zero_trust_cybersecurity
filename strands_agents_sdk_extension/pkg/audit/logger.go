package audit

import (
	"encoding/json"
	"fmt"
	"sync"
	"time"
)

// AuditEvent represents a security event to log
type AuditEvent struct {
	EventID   string                 `json:"event_id"`
	Timestamp int64                  `json:"timestamp"`
	EventType string                 `json:"event_type"` // "REGISTER", "VERIFY", "REVOKE"
	AgentID   string                 `json:"agent_id"`
	Action    string                 `json:"action"`
	Status    string                 `json:"status"` // "SUCCESS", "FAILURE"
	Details   map[string]interface{} `json:"details"`
}

// Logger logs all audit events in memory
type Logger struct {
	events []AuditEvent
	mu     sync.RWMutex
}

// NewLogger creates a new audit logger
func NewLogger() *Logger {
	return &Logger{
		events: make([]AuditEvent, 0),
	}
}

// LogEvent logs an audit event
func (l *Logger) LogEvent(eventType string, agentID string, action string, status string, details map[string]interface{}) {
	l.mu.Lock()
	defer l.mu.Unlock()

	event := AuditEvent{
		EventID:   fmt.Sprintf("evt_%d", time.Now().UnixNano()),
		Timestamp: time.Now().Unix(),
		EventType: eventType,
		AgentID:   agentID,
		Action:    action,
		Status:    status,
		Details:   details,
	}

	l.events = append(l.events, event)

	// Print to console
	eventJSON, _ := json.Marshal(event)
	fmt.Printf("[AUDIT] %s\n", string(eventJSON))
}

// GetEvents returns all logged events
func (l *Logger) GetEvents() []AuditEvent {
	l.mu.RLock()
	defer l.mu.RUnlock()

	// Return copy of events
	eventsCopy := make([]AuditEvent, len(l.events))
	copy(eventsCopy, l.events)
	return eventsCopy
}

// GetEventsByAgent returns events for specific agent
func (l *Logger) GetEventsByAgent(agentID string) []AuditEvent {
	l.mu.RLock()
	defer l.mu.RUnlock()

	var filtered []AuditEvent
	for _, event := range l.events {
		if event.AgentID == agentID {
			filtered = append(filtered, event)
		}
	}
	return filtered
}

// GetEventCount returns total number of logged events
func (l *Logger) GetEventCount() int {
	l.mu.RLock()
	defer l.mu.RUnlock()

	return len(l.events)
}
