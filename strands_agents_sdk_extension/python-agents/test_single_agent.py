import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from strands_client import StrandsAgentClient
import time
import json


def main():
    print("\n" + "="*60)
    print("TESTING SINGLE AGENT")
    print("="*60 + "\n")
    
    # Create client with longer timeout
    client = StrandsAgentClient(
        agent_id="test-agent-simple",
        wrapper_url="http://localhost:8443"
    )
    client.session.timeout = 30  # Increase timeout
    
    # Register
    print("[TEST] Step 1: Registering...")
    try:
        creds = client.register_agent()
        print(f"[TEST] ✓ Registered\n")
    except Exception as e:
        print(f"[TEST] ✗ Failed: {e}\n")
        return
    
    time.sleep(1)
    
    # Assign role
    print("[TEST] Step 2: Assigning role...")
    try:
        client.assign_role("admin")
        print(f"[TEST] ✓ Role assigned\n")
    except Exception as e:
        print(f"[TEST] ✗ Failed: {e}\n")
        return
    
    time.sleep(1)
    
    # Verify
    print("[TEST] Step 3: Verifying...")
    try:
        if client.verify_with_wrapper():
            print(f"[TEST] ✓ Verified\n")
        else:
            print(f"[TEST] ✗ Verification failed\n")
            return
    except Exception as e:
        print(f"[TEST] ✗ Failed: {e}\n")
        return
    
    time.sleep(1)
    
    # Execute task
    print("[TEST] Step 4: Executing task...")
    try:
        result = client.execute_task({"action": "test", "data": "hello"})
        print(f"[TEST] ✓ Task executed\n")
        print(f"Result: {result}\n")
    except Exception as e:
        print(f"[TEST] ✗ Failed: {e}\n")
        return
    
    print("[TEST] ✓ All steps completed successfully!\n")


if __name__ == "__main__":
    main()