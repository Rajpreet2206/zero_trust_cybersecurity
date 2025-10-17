import requests

print("Testing wrapper health...")
try:
    response = requests.get("http://localhost:8443/health", timeout=5)
    print(f"Health check response: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Health check failed: {e}")