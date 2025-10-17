package policy

import (
	"fmt"
	"sync"
)

// Role represents a role with permissions
type Role struct {
	Name        string
	Permissions []string // e.g., "agent:read", "agent:write", "agent:delete"
}

// PolicyEngine manages authorization policies
type PolicyEngine struct {
	roles      map[string]*Role    // role_name -> Role
	agentRoles map[string][]string // agent_id -> [role1, role2, ...]
	mu         sync.RWMutex
}

// NewPolicyEngine creates a new policy engine
func NewPolicyEngine() *PolicyEngine {
	pe := &PolicyEngine{
		roles:      make(map[string]*Role),
		agentRoles: make(map[string][]string),
	}

	// Define default roles
	pe.createDefaultRoles()

	return pe
}

// createDefaultRoles creates built-in roles
func (pe *PolicyEngine) createDefaultRoles() {
	// Admin role - can do everything
	pe.roles["admin"] = &Role{
		Name: "admin",
		Permissions: []string{
			"agent:read",
			"agent:write",
			"agent:delete",
			"agent:verify",
			"audit:read",
		},
	}

	// User role - can read and verify
	pe.roles["user"] = &Role{
		Name: "user",
		Permissions: []string{
			"agent:read",
			"agent:verify",
		},
	}

	// Service role - can only read
	pe.roles["service"] = &Role{
		Name: "service",
		Permissions: []string{
			"agent:read",
		},
	}
}

// AssignRole assigns a role to an agent
func (pe *PolicyEngine) AssignRole(agentID string, roleName string) error {
	pe.mu.Lock()
	defer pe.mu.Unlock()

	// Check if role exists
	if _, exists := pe.roles[roleName]; !exists {
		return fmt.Errorf("role not found: %s", roleName)
	}

	// Check if agent already has this role
	for _, existingRole := range pe.agentRoles[agentID] {
		if existingRole == roleName {
			return fmt.Errorf("agent already has role: %s", roleName)
		}
	}

	// Assign role
	pe.agentRoles[agentID] = append(pe.agentRoles[agentID], roleName)
	return nil
}

// CanPerform checks if agent can perform an action
func (pe *PolicyEngine) CanPerform(agentID string, action string) bool {
	pe.mu.RLock()
	defer pe.mu.RUnlock()

	// Get agent's roles
	roles, exists := pe.agentRoles[agentID]
	if !exists {
		// If no roles assigned, cannot perform
		return false
	}

	// Check if any role has the permission
	for _, roleName := range roles {
		role, roleExists := pe.roles[roleName]
		if !roleExists {
			continue
		}

		// Check if role has permission
		for _, perm := range role.Permissions {
			if perm == action {
				return true
			}
		}
	}

	return false
}

// GetAgentRoles returns all roles for an agent
func (pe *PolicyEngine) GetAgentRoles(agentID string) []string {
	pe.mu.RLock()
	defer pe.mu.RUnlock()

	roles := pe.agentRoles[agentID]
	// Return copy
	rolesCopy := make([]string, len(roles))
	copy(rolesCopy, roles)
	return rolesCopy
}

// GetRoles returns all available roles
func (pe *PolicyEngine) GetRoles() map[string]*Role {
	pe.mu.RLock()
	defer pe.mu.RUnlock()

	// Return copy
	rolesCopy := make(map[string]*Role)
	for name, role := range pe.roles {
		rolesCopy[name] = role
	}
	return rolesCopy
}

// RemoveRole removes a role from an agent
func (pe *PolicyEngine) RemoveRole(agentID string, roleName string) error {
	pe.mu.Lock()
	defer pe.mu.Unlock()

	roles, exists := pe.agentRoles[agentID]
	if !exists {
		return fmt.Errorf("agent has no roles")
	}

	// Find and remove role
	for i, role := range roles {
		if role == roleName {
			pe.agentRoles[agentID] = append(roles[:i], roles[i+1:]...)
			return nil
		}
	}

	return fmt.Errorf("agent does not have role: %s", roleName)
}
