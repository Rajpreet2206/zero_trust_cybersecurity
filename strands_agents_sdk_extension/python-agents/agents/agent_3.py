import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strands_client import StrandsAgentClient
import time
import json


def main():
    """Agent 3: Read-only Service"""
    print("\n" + "="*60)
    print("AGENT 3: Read-only Service")
    print("="*60 + "\n")
    
    # Create client
    client = StrandsAgentClient(
        agent_id="agent-service-3",
        wrapper_url="http://localhost:8443"
    )
    
    # Step 1: Register
    try:
        client.register_agent()
    except Exception as e:
        print(f"Registration failed: {e}")
        return
    
    # Step 2: Assign service role FIRST (before verify)
    client.assign_role("service")
    time.sleep(0.5)
    
    # Step 3: Verify
    if not client.verify_with_wrapper():
        print("Verification failed")
        return
    
    # Step 4: Execute read-only tasks
    print("\n[AGENT-3] Starting read-only operations...\n")
    
    tasks = [
        {"action": "list_datasets"},
        {"action": "get_metadata"},
        {"action": "check_status"},
    ]
    
    for task in tasks:
        try:
            print(f"[AGENT-3] Executing: {task['action']}")
            result = client.execute_task(task)
            print(f"[AGENT-3] ✓ Result: {json.dumps(result)}\n")
            time.sleep(0.3)
        except Exception as e:
            print(f"[AGENT-3] ✗ Failed: {e}\n")
    
    # Step 5: Check rate limits
    print("[AGENT-3] Checking rate limits...")
    stats = client.get_rate_limit_stats()
    print(f"[AGENT-3] Available tokens: {stats.get('available', 'N/A')}")
    print(f"[AGENT-3] Total requests: {stats.get('total_requests', 'N/A')}\n")
    
    print("[AGENT-3] ✓ Agent 3 completed successfully\n")


if __name__ == "__main__":
    main()