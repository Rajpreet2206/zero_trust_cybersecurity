import requests
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass
from cryptography.hazmat.primitives.asymmetric import ed25519


@dataclass
class AgentCredentials:
    """Represents agent credentials"""
    agent_id: str
    public_key_hex: str
    private_key_hex: str
    nonce: str
    created_at: int
    expires_at: int
    status: str


class StrandsAgentClient:
    """Client for agents to communicate through Go wrapper"""

    def __init__(self, agent_id: str, wrapper_url: str = "http://localhost:8443"):
        self.agent_id = agent_id
        self.wrapper_url = wrapper_url.rstrip("/")
        self.credentials: Optional[AgentCredentials] = None
        self.session = requests.Session()

    def register_agent(self) -> AgentCredentials:
        """Register agent and get credentials"""
        print(f"[{self.agent_id}] Registering...")
        
        endpoint = f"{self.wrapper_url}/api/v1/identity/register"
        payload = {"agent_id": self.agent_id}
        
        response = self.session.post(endpoint, json=payload, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        self.credentials = AgentCredentials(
            agent_id=data["agent_id"],
            public_key_hex=data["public_key"],
            private_key_hex=data["private_key"],
            nonce=data["nonce"],
            created_at=data["created_at"],
            expires_at=data["expires_at"],
            status=data["status"]
        )
        
        print(f"[{self.agent_id}] ✓ Registered successfully")
        return self.credentials

    def verify_with_wrapper(self) -> bool:
        """Verify agent identity with wrapper"""
        if not self.credentials:
            print(f"[{self.agent_id}] ✗ No credentials")
            return False
        
        print(f"[{self.agent_id}] Verifying...")
        
        try:
            # Convert hex string to bytes
            private_key_bytes = bytes.fromhex(self.credentials.private_key_hex)
            
            # Ed25519 private key is 64 bytes (seed + public key)
            # We only need the first 32 bytes (the seed)
            if len(private_key_bytes) == 64:
                # Full private key - use it directly
                private_key = ed25519.Ed25519PrivateKey.from_private_bytes(private_key_bytes[:32])
            elif len(private_key_bytes) == 32:
                # Just the seed
                private_key = ed25519.Ed25519PrivateKey.from_private_bytes(private_key_bytes)
            else:
                print(f"[{self.agent_id}] ✗ Invalid private key length: {len(private_key_bytes)}")
                return False
            
            # Sign the nonce
            signature = private_key.sign(self.credentials.nonce.encode())
            signature_hex = signature.hex()
        except Exception as e:
            print(f"[{self.agent_id}] ✗ Sign failed: {e}")
            return False
        
        endpoint = f"{self.wrapper_url}/api/v1/identity/verify"
        payload = {
            "agent_id": self.agent_id,
            "signature": signature_hex,
            "nonce": self.credentials.nonce
        }
        
        try:
            response = self.session.post(
                endpoint,
                json=payload,
                headers={"X-Agent-ID": self.agent_id},
                timeout=10
            )
            response.raise_for_status()
            print(f"[{self.agent_id}] ✓ Verified successfully")
            return True
        except Exception as e:
            print(f"[{self.agent_id}] ✗ Verification failed: {e}")
            return False

    def assign_role(self, role: str) -> bool:
        """Assign role to agent"""
        print(f"[{self.agent_id}] Assigning role: {role}")
        
        endpoint = f"{self.wrapper_url}/api/v1/policy/assign-role"
        payload = {
            "agent_id": self.agent_id,
            "role": role
        }
        
        try:
            response = self.session.post(
                endpoint,
                json=payload,
                headers={"X-Agent-ID": self.agent_id},
                timeout=10
            )
            response.raise_for_status()
            print(f"[{self.agent_id}] ✓ Role assigned")
            return True
        except Exception as e:
            print(f"[{self.agent_id}] ✗ Role assignment failed: {e}")
            return False

    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task through wrapper"""
        endpoint = f"{self.wrapper_url}/api/v1/sdk/execute"
        payload = {"task": task}
        
        try:
            response = self.session.post(
                endpoint,
                json=payload,
                headers={"X-Agent-ID": self.agent_id},
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            return result
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                print(f"[{self.agent_id}] ✗ Rate limit exceeded")
            elif e.response.status_code == 403:
                print(f"[{self.agent_id}] ✗ Authorization denied")
            else:
                print(f"[{self.agent_id}] ✗ Task failed: {e}")
            raise

    def get_rate_limit_stats(self) -> Dict[str, Any]:
        """Get rate limit stats"""
        endpoint = f"{self.wrapper_url}/api/v1/ratelimit/stats"
        
        try:
            response = self.session.get(
                endpoint,
                headers={"X-Agent-ID": self.agent_id},
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"[{self.agent_id}] ✗ Failed to get stats: {e}")
            return {}

    def get_anomalies(self) -> list:
        """Get detected anomalies"""
        endpoint = f"{self.wrapper_url}/api/v1/analytics/anomalies"
        
        try:
            response = self.session.get(
                endpoint,
                headers={"X-Agent-ID": self.agent_id},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            return data.get("anomalies", [])
        except Exception as e:
            print(f"[{self.agent_id}] ✗ Failed to get anomalies: {e}")
            return []