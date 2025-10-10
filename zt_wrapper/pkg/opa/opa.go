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
	fmt.Printf("[OPA] Loading policy files: %v\n", policyFiles)
	query := "data.agents.allow"
	fmt.Printf("[OPA] Using query: %s\n", query)
	r := rego.New(
		rego.Query(query),
		rego.Load(policyFiles, nil),
	)
	return &Policy{regoQuery: r}, nil
}

// Evaluate evaluates the policy with the given input
func (p *Policy) Evaluate(input map[string]interface{}) (bool, error) {
	ctx := context.Background()

	fmt.Printf("[OPA] Evaluating with input: %v\n", input)

	// Prepare the query for evaluation
	prepared, err := p.regoQuery.PrepareForEval(ctx)
	if err != nil {
		fmt.Printf("[OPA] Failed to prepare policy: %v\n", err)
		return false, fmt.Errorf("failed to prepare policy: %v", err)
	}

	// Evaluate with input
	results, err := prepared.Eval(ctx, rego.EvalInput(input))
	if err != nil {
		fmt.Printf("[OPA] Policy evaluation failed: %v\n", err)
		return false, fmt.Errorf("policy evaluation failed: %v", err)
	}

	fmt.Printf("[OPA] Evaluation results: %v\n", results)

	if len(results) == 0 || len(results[0].Expressions) == 0 {
		fmt.Printf("[OPA] No results or expressions returned\n")
		return false, nil
	}

	allow, ok := results[0].Expressions[0].Value.(bool)
	if !ok {
		fmt.Printf("[OPA] Invalid policy return value: %v\n", results[0].Expressions[0].Value)
		return false, fmt.Errorf("invalid policy return value")
	}

	fmt.Printf("[OPA] Final allow value: %v\n", allow)
	return allow, nil
}
