
"""
Run all agents sequentially and show combined results
"""

import subprocess
import sys
import time


def run_agent(agent_number):
    """Run a single agent"""
    print(f"\n{'='*60}")
    print(f"Running Agent {agent_number}...")
    print(f"{'='*60}\n")
    
    try:
        result = subprocess.run(
            [sys.executable, f"agents/agent_{agent_number}.py"],
            capture_output=False,
            timeout=30
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"Agent {agent_number} timed out")
        return False
    except Exception as e:
        print(f"Error running agent {agent_number}: {e}")
        return False


def main():
    print("\n" + "="*60)
    print("STRANDS AGENTS - MULTI-AGENT EXECUTION")
    print("="*60)
    print("\nThis will run 3 agents through the Go Zero-Trust Wrapper")
    print("Each agent has different roles and permissions\n")
    
    results = {}
    
    # Run agents sequentially
    for agent_num in [1, 2, 3]:
        success = run_agent(agent_num)
        results[f"Agent {agent_num}"] = "✓ Success" if success else "✗ Failed"
        time.sleep(1)
    
    # Summary
    print("\n" + "="*60)
    print("EXECUTION SUMMARY")
    print("="*60)
    for agent, status in results.items():
        print(f"{agent}: {status}")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
