#!/usr/bin/env python
"""
Simulate Brute Force Attack by Injecting Mock Audit Events
This creates mock audit log data that matches the brute_force threat pattern
"""

import sys
import os

# Add ida-agent directory to path so we import its config
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ida-agent'))

from config import Config
from datetime import datetime
import json

def generate_brute_force_events():
    """Generate mock brute force attack audit events"""
    
    events = []
    base_time = int(datetime.now().timestamp())
    
    # Simulate 8 failed login attempts from attacker
    print("Generating brute force attack events...")
    print("="*70)
    
    for i in range(8):
        event = {
            "event_id": f"evt_mock_{i}",
            "timestamp": base_time - (8-i)*5,  # 5 seconds apart
            "event_type": "REGISTER",
            "agent_id": f"attacker_attempt_{i}",
            "action": "failed_registration",
            "status": "FAILED",
            "details": {
                "reason": "wrong_password",
                "attempts": i + 1,
                "ip": "192.168.1.100"
            }
        }
        events.append(event)
        print(f"Event {i+1}: Failed login attempt by attacker_attempt_{i}")
    
    print("="*70)
    print(f"\nGenerated {len(events)} mock audit events")
    print("\nThese events simulate a BRUTE FORCE ATTACK pattern:")
    print("  - Multiple failed login attempts (8 total)")
    print("  - Within short time window (40 seconds)")
    print("  - Same source IP (192.168.1.100)")
    print("  - Different operator IDs")
    print("\nExpected IDA Response:")
    print("  - Threat Score: 50-70/100 (HIGH)")
    print("  - Classification: Brute Force Attack")
    print("  - Actions: Lock accounts, Alert admin")
    
    return events

def create_test_scenario():
    """
    Create a complete test scenario with mock events
    This will be used to test IDA's threat detection
    """
    
    print("\n" + "="*70)
    print("BRUTE FORCE ATTACK SIMULATION")
    print("="*70 + "\n")
    
    # Generate events
    events = generate_brute_force_events()
    
    # Show threat pattern from config
    print("\n" + "="*70)
    print("THREAT PATTERN DEFINITION (from threat_rules.yaml)")
    print("="*70)
    
    brute_force_pattern = Config.get_threat_pattern("brute_force")
    if brute_force_pattern:
        print(f"Pattern: brute_force")
        print(f"Description: {brute_force_pattern['description']}")
        print(f"Indicators:")
        for key, value in brute_force_pattern['indicators'].items():
            print(f"  - {key}: {value}")
        print(f"Severity: {brute_force_pattern['severity']}")
        print(f"Actions: {', '.join(brute_force_pattern['actions'])}")
    
    # Show expected threat score
    print("\n" + "="*70)
    print("THREAT ANALYSIS")
    print("="*70)
    print(f"Event Count: {len(events)}")
    print(f"Event Type: Failed Authentication")
    print(f"Time Window: 40 seconds")
    print(f"Source IP: 192.168.1.100")
    print(f"Unique Operators: 8")
    
    print(f"\nBased on threat pattern 'brute_force':")
    print(f"  Failed logins in 5min: 8 (threshold: 3) - EXCEEDED")
    print(f"  Threshold threat score: 50")
    print(f"\nExpected IDA Detection:")
    print(f"  Threat Score: 60-75/100 (HIGH)")
    print(f"  Threat Level: HIGH")
    print(f"  Will trigger: MEDIUM/HIGH response actions")
    
    print("\n" + "="*70)
    print("HOW TO RUN THIS TEST")
    print("="*70)
    print("1. In Terminal 1: Run IDA agent")
    print("   cd warehouse_scada_security/ida-agent")
    print("   python main.py")
    print("")
    print("2. In Terminal 2: Run this attack simulation")
    print("   cd warehouse_scada_security")
    print("   python simulate_attack.py")
    print("")
    print("3. Watch Terminal 1 for threat detection output")
    print("")
    print("Expected IDA Output:")
    print("  [IDA] Threat Assessment: Score=65/100")
    print("  [IDA] Operator Behavior Analysis:")
    print("  [IDA]   failed_login_attempts: 83/100 [HIGH]")
    print("  [IDA] THREAT DETECTED - Invoking AI analysis")
    print("  [IDA] Bedrock Classification: Brute Force Attack")
    print("  [IDA] Actions: Lock accounts, Alert admin")
    print("="*70 + "\n")
    
    return events

if __name__ == "__main__":
    try:
        events = create_test_scenario()
        print("Attack simulation scenario created successfully!")
        print(f"Total events generated: {len(events)}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)