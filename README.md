# Zero_Trust_Cybersecurity
A wrapper/extension to Strands Agents SDK for zero trust principles.

## Project Overview
Zero trust wrapper for Strands Agents SDK aims to extend it with a security-first layer designed for multi-agent systems (MAS) deployed in zero trust environments. It enforces never trust, always verify principles across agent communication, identity management, and policy enforcement, making it ideal for industrial for industrial, IoT, and critical infrastructure contexts.


## Project Goals
#### **</ NOT CHANGING THE DESIGN PATTERNS IN STRANDS AGENTS SDK>**

### 1. Enable Secure Multi-Agent Collaboration
Ensure that agents can collaborate and share intelligence safely in distributed environments without implicit trust.  This allows the deployment of AI-driven agents in sensitive domains like industrial OT, cyber defense, or smart factories.

### 2. Operationalize Zero Trust Principles
Implement practical Zero Trust mechanisms(mTLS, OPA, and identity verification) within a developer-friendly SDK layer. The goal is to make Zero Trust accessible and transparent **NOT** a burden for developers integrating multi-agent solutions.

### 3. Enhance Observability and Forensics
Provide a robust telemetry pipeline to monitor all agent 
communications, policy actions, logs and authentication results in real time. This enables **auditability**, **anomaly detection**, and **post-incident analysis** without disrupting system flow.

### 4. Prototype a Reference Architecture for Industrial Zero Trust AI
A proof-of-concept showing how AI agents (via Strands SDK) can operate securely in a P2P network scenario. This includes integration with AWS Bedrock, OpenPLC, SCADA, and simulation environments to validate the approach in realistic OT use cases.

## Requirements
### 1. Zero Trust Enforcement Layer
Every agent-to-agent and agent-to-service(API) communications must be authenticated and authorized continuously. We need to implement mutual TLS (mTLS) for identity-based authentication, integrate short-lived certificates and automated key rotation. This layer should provide a policy enforcement gateway that verifies every request via Open Policy Agent (OPA) or similar engine before access is granted.

### 2. Agent Identity and Attestation System
Agents must have cryptographic identities that can be verified independently. We can issue unique agent certificates or tokens signed by a local or cloud-based Certificate Authority. Maintain an identity registry to log trust scores, certificate validity, and behavioral metrics for dynamic trust decisions. This should guarantee verifiable trust chains and non-repudiation in all agent actions.

### 3. Policy-driven Access Control
Access decisions must be dynamic, context-aware, and enforced in real time. Integrate with OPA (Open Policy Agent) for evaluating access rules based on role, device, and situational context. This should allow developers to write declarative policies (e.g., Rego scripts) for fine-grained control. Try to enable runtime evaluation such that policies can adapt automatically when context or trust changes.
This provides least-privilege access and continuous verification for all interactions.

### 4. Telemetry and Audit Trail Integration
All agent communications, policy decisions, and trust evaluations must be observable and auditable. Collect structured telemetry for each event (authentication, authorization, request flow). Support tamper-proof logging with cryptographic signatures. This would improve incident response readiness and forensic traceability while aligning with compliance frameworks (e.g., IEC 62443 for industrial security).  

### 5. Strands SDK Interoperability Layer
A Golang extension interface that wraps Strands SDK APIs with security hooks. This should ensure minimal performance overhead to preserve real-time decision-making capabilities. This requirement provides developer-friendly abstractions for onboarding, configuration, and certificate management to ensure easy adoption by developers without needing to modify existing agent logic.

### 6. Modular Deployment Architecture
The system should support flexible deployment patterns, like run as a sidecar service (, e.g. within a Kubernetes Pod) or as a middleware in the agent code. We should provide configurable security levels ( like dev mode vs. prod zero trust enforcement). 

## End-Use Vision
#### Reference Example : *https://strandsagents.com/latest/documentation/docs/examples/python/multi_agent_example/multi_agent_example/*
```python
# The client side Agent code which makes a call and is intercepted by the wrapper.
import requests
import json

# Paths to client certificate and key for mTLS
CLIENT_CERT = "certs/client.crt"
CLIENT_KEY = "certs/client.key"
CA_CERT = "certs/ca.crt"

# Zero Trust Wrapper endpoint
ZT_WRAPPER_URL = "https://localhost:8443/call-agent"

def call_agent(agent_name: str, payload: str):
    """
    Call a Strands SDK agent via the Zero Trust Wrapper with mTLS and OPA enforcement
    """
    params = {
        "agent": agent_name,
        "payload": payload
    }

    try:
        response = requests.get(
            ZT_WRAPPER_URL,
            params=params,
            cert=(CLIENT_CERT, CLIENT_KEY),
            verify=CA_CERT
        )
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        return f"Request failed: {e}"

if __name__ == "__main__":
    # Example 1: Math query
    result = call_agent("MathAssistant", "Solve x^2 + 5x + 6 = 0")
    print("MathAssistant Response:\n", result)

    # Example 2: Computer Science query
    result = call_agent("CSAssistant", "Write a Python function to check if a string is palindrome")
    print("CSAssistant Response:\n", result)

```


```python
# Application of Zero Trusy Wrapper to Multi-Agents Systems
import requests
from concurrent.futures import ThreadPoolExecutor

# Paths to client certificate and key for mTLS
CLIENT_CERT = "certs/client.crt"
CLIENT_KEY = "certs/client.key"
CA_CERT = "certs/ca.crt"

# Zero Trust Wrapper endpoint
ZT_WRAPPER_URL = "https://localhost:8443/call-agent"

# Define specialized agents
SPECIALIZED_AGENTS = {
    "math": "MathAssistant",
    "cs": "CSAssistant",
    "language": "LanguageAssistant",
    "english": "EnglishAssistant",
}

# Sample queries routed by Teacher's Assistant
QUERIES = [
    {"type": "math", "payload": "Solve x^2 + 5x + 6 = 0"},
    {"type": "cs", "payload": "Write a Python function to check palindrome"},
    {"type": "language", "payload": "Translate 'Hello, how are you?' to Spanish"},
    {"type": "english", "payload": "Check grammar: 'She go to school yesterday'"}
]

def call_agent(agent_name: str, payload: str) -> str:
    """
    Call a specialized agent via the Go Zero Trust Wrapper
    """
    params = {"agent": agent_name, "payload": payload}
    try:
        response = requests.get(
            ZT_WRAPPER_URL,
            params=params,
            cert=(CLIENT_CERT, CLIENT_KEY),
            verify=CA_CERT,
            timeout=5
        )
        response.raise_for_status()
        return f"[{agent_name}] {response.text}"
    except requests.exceptions.RequestException as e:
        return f"[{agent_name}] Request failed: {e}"

def teacher_assistant_route(query):
    """
    Simulates Teacher's Assistant routing queries to specialized agents
    """
    agent_type = query["type"]
    payload = query["payload"]
    agent_name = SPECIALIZED_AGENTS.get(agent_type, "GeneralAssistant")
    return call_agent(agent_name, payload)

if __name__ == "__main__":
    print("=== Multi-Agent Zero Trust Demo ===\n")

    # Use ThreadPoolExecutor to simulate concurrent multi-agent calls
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(teacher_assistant_route, q) for q in QUERIES]
        for future in futures:
            print(future.result())

    print("\n=== Demo Complete ===")

```