# agent package

This directory will contain the Go-side code for securely communicating with the Python Strands SDK.
Planned integration options:
- gRPC with mutual TLS (recommended)
- Unix domain socket or named pipe with mTLS/PGP-wrapped messages
- Encrypted stdin/stdout channel (only for simple POC)

We will implement the secure transport and an authentication handshake in a following step.


# Strands Zero-Trust Security Wrapper (Go)

Repository scaffold for the Strands Zero-Trust wrapper.

This initial scaffold provides:
- Go module initialization
- Simple health HTTP endpoint on :8080
- Placeholder for launching the Python Strands agent process

Next steps: design and implement secure IPC (gRPC + mTLS recommended), identity issuance, and policy enforcement.
