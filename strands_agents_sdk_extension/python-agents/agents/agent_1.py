import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strands_client import StrandsAgentClient
import time
import json

def main():
    """Agent 1: Data Processor"""
    print("\n" + "="*60)
    print("AGENT 1: Data Processor")
    print("="*60 + "\n")
    
    # Create client
    client = StrandsAgentClient(
        agent_id="agent-processor-1",
        wrapper_url="http://localhost:8443"
    )
    
    # Step 1: Register
    try:
        client.register_agent()
    except Exception as e:
        print(f"Registration failed: {e}")
        return
    
    # Step 2: Assign admin role FIRST (before verify)
    client.assign_role("admin")
    time.sleep(0.5)
    
    # Step 3: Verify
    if not client.verify_with_wrapper():
        print("Verification failed")
        return
    
    # Step 4: Execute tasks
    print("\n[AGENT-1] Starting tasks...\n")
    
    tasks = [
        {"action": "process_data", "data_id": "dataset-001"},
        {"action": "analyze", "data_id": "dataset-001"},
        {"action": "report", "data_id": "dataset-001"},
    ]
    
    for task in tasks:
        try:
            print(f"[AGENT-1] Executing: {task['action']}")
            result = client.execute_task(task)
            print(f"[AGENT-1] ✓ Result: {json.dumps(result)}\n")
            time.sleep(0.3)
        except Exception as e:
            print(f"[AGENT-1] ✗ Failed: {e}\n")
    
    # Step 5: Check rate limits
    print("[AGENT-1] Checking rate limits...")
    stats = client.get_rate_limit_stats()
    print(f"[AGENT-1] Available tokens: {stats.get('available', 'N/A')}")
    print(f"[AGENT-1] Total requests: {stats.get('total_requests', 'N/A')}\n")
    
    # Step 6: Check anomalies
    print("[AGENT-1] Checking anomalies...")
    anomalies = client.get_anomalies()
    print(f"[AGENT-1] Anomalies detected: {len(anomalies)}\n")
    
    print("[AGENT-1] ✓ Agent 1 completed successfully\n")


if __name__ == "__main__":
    main()
