# Strands Zero-Trust Security Wrapper - Step 1: Foundation

A production-grade Go wrapper implementing zero-trust security principles for Python-based Strands Agents SDK with comprehensive cryptographic operations.

## 18.10.2025 Project Development Report
We built a production-grade security system in Go that acts as a cryptographic gateway for Python agents. The system implements nine integrated security layers: it starts with strong cryptography (Ed25519 and AES-256-GCM), manages agent identities through credential registration and verification, enforces role-based permissions, intercepts and validates every request through middleware, logs all operations for audit trails, limits request rates to prevent abuse, encrypts transport with TLS, detects anomalous behavior through analytics, and uses asynchronous background workers to avoid performance bottlenecks. Python agents connect to this wrapper, register with cryptographic credentials, get assigned roles and permissions, prove their identity through digital signatures, and then execute tasks only if authorized—with every operation transparently logged and monitored. The system successfully demonstrates zero-trust principles in practice: nothing is trusted by default, every request is verified multiple times, and security decisions are based on cryptographic proof rather than assumptions. The implementation is working end-to-end, handling real agent authentication, authorization, and task execution through a protected pipeline.

#### cd strands-go-wrapper: go build -o bin/wrapper-server.exe cmd/wrapper-server/main.go
#### TLS_ENABLED=false ./bin/wrapper-server.exe

### What's currently working: 18.10.2025
### 1. Core Security Infrastructure (Go Wrapper):

- A fully functional Go-based security wrapper that acts as a gateway for Python agents
- Implements Ed25519 for asymmetric encryption and AES-256-GCM for symmetric encryption
- Handles agent registration, authentication, and authorization
- Security Layers (All Working):

### 2. Identity Management: Agents can register and receive cryptographic credentials
- Role-Based Access: Permission enforcement based on agent roles
- Request Validation: Middleware that intercepts and validates every request
- Audit Logging: Comprehensive logging of all operations
- Rate Limiting: Protection against request abuse
- TLS Encryption: Secure transport layer with certificates
- Behavioral Analytics: Detection of anomalous agent behavior
- Asynchronous Processing: Background workers for performance


### 3. Python Integration:

- Working Python SDK client (strands_client.py)
- Example agent implementation (strands_agent_example.py)
- Integration tests for health checks, registration, and agent operations
- Multiple test agents (agent_1.py, agent_2.py, agent_3.py)

### 4. Infrastructure:

- HTTP REST API endpoints for all security operations
- Configuration management via environment variables
- Docker containerization support
- Automated build and deployment through Makefile
- Certificate management (scripts/generate-certs.sh)


### 5. End-to-End Workflow:

- Agents can register with the wrapper
- Authentication using cryptographic proofs
- Authorization checks for each operation
- Secure task execution through the protected pipeline
- Comprehensive monitoring and logging

The system successfully implements zero-trust principles where: 
- No agent is trusted by default
- Every request requires cryptographic verification
- Multiple security layers validate each operation
- All activities are logged and monitored

## Warehouse SCADA Setup
**The Problem**: Industrial facilities (warehouses, factories, power plants) run specialized control systems that operate critical equipment—conveyor belts, pumps, temperature sensors, door locks, etc. These systems traditionally operated in isolated networks with no security. Today, they're increasingly connected to IT networks, creating major vulnerabilities. A single breach can shut down operations, steal data, or cause physical damage.

### The Architecture
1. **OpenPLC** - The industrial controller (like a PLC in a real warehouse). It controls physical devices and runs logic programs. Imagine it managing conveyor belt speed, warehouse temperature, or door access.
2. **ScadaBR** - The human interface and monitoring system. Operators use it to view real-time data (is the conveyor running? what's the temperature?) and send commands (start pump, open door, etc.). It's essentially a dashboard.
3. **pfSense** - The network firewall and gateway. In a real setup, it controls what traffic gets in/out of the ICS network and can enforce rules.
4. **Go Wrapper** - The zero-trust security layer that sits between operators and the actual control systems. 


### Flow Without Zero-Trust Security
```
Operator → ScadaBR → OpenPLC → Physical Equipment
```

### The Flow (With the Zero-Trust Wrapper)
```
Operator → Go Wrapper (Verify Identity) → Wrapper (Check Permissions) → 
Wrapper (Log Action) → Wrapper (Rate Limit) → ScadaBR → OpenPLC → Equipment
```
---

### Why Your Go Wrapper Is Perfect for This

Our wrapper's nine security layers map directly to real ICS security needs:

1. **Cryptography (Ed25519/AES-256)** - Prove the operator is who they claim (not a hacker with stolen credentials)
2. **Credential Registration** - Operators register once, get cryptographic proof of identity
3. **Role-Based Permissions** - Different operators have different access (e.g., warehouse supervisor can start conveyors, but junior staff cannot)
4. **Request Middleware** - Every command gets validated before reaching the control system
5. **Audit Logging** - Regulatory compliance: every action is recorded (who did what, when, why)
6. **Rate Limiting** - Prevent brute force attacks or runaway commands
7. **TLS Encryption** - Protect credentials and commands in transit
8. **Behavioral Analytics** - Detect if an operator is acting suspiciously (e.g., suddenly requesting 1000 commands in 10 seconds—sign of a compromised account)
9. **Async Verification** - Keep the system responsive while security checks happen in background


cd warehouse_scada_security/ida-agent

# Test configuration first
python main.py --show-config

# Test wrapper connection
python main.py --test-connection

# Expected output:
# ✓ Go Wrapper is reachable and healthy
# ✓ Bedrock is available

# Start IDA monitoring
python main.py

Step 6: Test IDA with Simulated Attack
Terminal 4: Simulate an Attack
Create a test attack scenario. Example: Multiple failed logins
bash# Run the attack simulation
cd warehouse_scada_security/ida-agent

# Or manually trigger audit log generation through wrapper
python -c "
import requests
import json

# Simulate failed login attempts
for i in range(6):
    response = requests.post(
        'http://localhost:8443/register',
        data={
            'operator_id': f'attacker_{i}',
            'public_key': 'invalid_key',
            'role': 'admin'
        }
    )
    print(f'Failed login attempt {i+1}')
"