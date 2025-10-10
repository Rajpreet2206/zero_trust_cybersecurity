package opa

import (
	"context"
	"fmt"

	"github.com/open-policy-agent/opa/rego"
)

type Policy struct {
	regoQuery *rego.Rego // <-- store pointer, not value
}

// LoadPolicy loads Rego files and prepares the policy
func LoadPolicy(policyFiles []string) (*Policy, error) {
	r := rego.New(
		rego.Query("data.agents.authz.allow"),
		rego.Load(policyFiles, nil),
	)
	return &Policy{regoQuery: r}, nil
}

// Evaluate evaluates the policy with the given input
func (p *Policy) Evaluate(input map[string]interface{}) (bool, error) {
	ctx := context.Background()

	// Prepare the query for evaluation
	prepared, err := p.regoQuery.PrepareForEval(ctx)
	if err != nil {
		return false, fmt.Errorf("failed to prepare policy: %v", err)
	}

	// Evaluate with input
	results, err := prepared.Eval(ctx, rego.EvalInput(input))
	if err != nil {
		return false, fmt.Errorf("policy evaluation failed: %v", err)
	}

	if len(results) == 0 || len(results[0].Expressions) == 0 {
		return false, nil
	}

	allow, ok := results[0].Expressions[0].Value.(bool)
	if !ok {
		return false, fmt.Errorf("invalid policy return value")
	}

	return allow, nil
}
