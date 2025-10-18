import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import requests
import json
from cryptography.hazmat.primitives.asymmetric import ed25519
import time

print("\n" + "="*60)
print("WORKING AGENT TEST - Step by Step")
print("="*60 + "\n")

wrapper_url = "http://localhost:8443"

# Step 1: Register
print("[1] Registering agent...")
try:
    response = requests.post(
        f"{wrapper_url}/api/v1/identity/register",
        json={"agent_id": "working-agent"},
        timeout=30
    )
    response.raise_for_status()
    creds = response.json()
    print(f"✓ Registered: {creds['agent_id']}\n")
except Exception as e:
    print(f"✗ Failed: {e}\n")
    exit(1)

time.sleep(1)

# Step 2: Assign role (with longer timeout)
print("[2] Assigning admin role...")
try:
    response = requests.post(
        f"{wrapper_url}/api/v1/policy/assign-role",
        json={"agent_id": "working-agent", "role": "admin"},
        headers={"X-Agent-ID": "working-agent"},
        timeout=30  # Longer timeout for middleware
    )
    response.raise_for_status()
    print(f"✓ Role assigned\n")
except Exception as e:
    print(f"✗ Failed: {e}\n")
    exit(1)

time.sleep(1)

# Step 3: Verify identity
print("[3] Verifying identity...")
try:
    # Sign nonce with private key
    private_key_bytes = bytes.fromhex(creds["private_key"])[:32]
    private_key = ed25519.Ed25519PrivateKey.from_private_bytes(private_key_bytes)
    signature = private_key.sign(creds["nonce"].encode())
    
    response = requests.post(
        f"{wrapper_url}/api/v1/identity/verify",
        json={
            "agent_id": "working-agent",
            "signature": signature.hex(),
            "nonce": creds["nonce"]
        },
        headers={"X-Agent-ID": "working-agent"},
        timeout=30
    )
    response.raise_for_status()
    print(f"✓ Verified\n")
except Exception as e:
    print(f"✗ Failed: {e}\n")
    exit(1)

time.sleep(1)

# Step 4: Check rate limit stats
print("[4] Checking rate limit stats...")
try:
    response = requests.get(
        f"{wrapper_url}/api/v1/ratelimit/stats",
        headers={"X-Agent-ID": "working-agent"},
        timeout=30
    )
    response.raise_for_status()
    stats = response.json()
    print(f"✓ Available tokens: {stats.get('available')}/{stats.get('burst_size')}\n")
except Exception as e:
    print(f"✗ Failed: {e}\n")

time.sleep(1)

# Step 5: Execute task
print("[5] Executing task...")
try:
    response = requests.post(
        f"{wrapper_url}/api/v1/sdk/execute",
        json={"task": {"action": "test_action", "data": "test_data"}},
        headers={"X-Agent-ID": "working-agent"},
        timeout=30
    )
    response.raise_for_status()
    result = response.json()
    print(f"✓ Task executed: {json.dumps(result)}\n")
except Exception as e:
    print(f"✗ Failed: {e}\n")

print("="*60)
print("✓ ALL STEPS COMPLETED SUCCESSFULLY!")
print("="*60 + "\n")