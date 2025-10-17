import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strands_client import StrandsAgentClient
import time
import json


def main():
    """Agent 2: Data Validator"""
    print("\n" + "="*60)
    print("AGENT 2: Data Validator")
    print("="*60 + "\n")
    
    # Create client
    client = StrandsAgentClient(
        agent_id="agent-validator-2",
        wrapper_url="http://localhost:8443"
    )
    
    # Step 1: Register
    try:
        client.register_agent()
    except Exception as e:
        print(f"Registration failed: {e}")
        return
    
    # Step 2: Assign user role FIRST (before verify)
    client.assign_role("user")
    time.sleep(0.5)
    
    # Step 3: Verify
    if not client.verify_with_wrapper():
        print("Verification failed")
        return
    
    # Step 4: Execute tasks
    print("\n[AGENT-2] Starting validation tasks...\n")
    
    tasks = [
        {"action": "validate", "dataset": "dataset-001"},
        {"action": "check_quality", "dataset": "dataset-001"},
        {"action": "generate_report", "dataset": "dataset-001"},
    ]
    
    for task in tasks:
        try:
            print(f"[AGENT-2] Executing: {task['action']}")
            result = client.execute_task(task)
            print(f"[AGENT-2] ✓ Result: {json.dumps(result)}\n")
            time.sleep(0.3)
        except Exception as e:
            print(f"[AGENT-2] ✗ Failed: {e}\n")
    
    # Step 5: Check rate limits
    print("[AGENT-2] Checking rate limits...")
    stats = client.get_rate_limit_stats()
    print(f"[AGENT-2] Available tokens: {stats.get('available', 'N/A')}")
    print(f"[AGENT-2] Total requests: {stats.get('total_requests', 'N/A')}\n")
    
    print("[AGENT-2] ✓ Agent 2 completed successfully\n")


if __name__ == "__main__":
    main()