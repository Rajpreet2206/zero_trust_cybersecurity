import requests

print("Testing registration...")
try:
    response = requests.post(
        "http://localhost:8443/api/v1/identity/register",
        json={"agent_id": "test-minimal"},
        timeout=30
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Registration failed: {e}")