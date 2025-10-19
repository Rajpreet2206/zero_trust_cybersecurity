"""
Test Mode for IDA - Generate and inject mock audit events for testing
Allows IDA to detect threats without needing real wrapper audit logs
"""

from datetime import datetime
from typing import List, Dict, Any


def generate_brute_force_events() -> List[Dict[str, Any]]:
    """Generate mock brute force attack events - AGGRESSIVE"""
    events = []
    base_time = int(datetime.now().timestamp())
    
    # Simulate 20 failed login attempts in rapid succession - strong signal
    for i in range(20):
        event = {
            "timestamp": base_time - (20-i)*2,  # 2 seconds apart
            "operator_id": f"attacker_attempt_{i}",
            "action": "REGISTER",
            "resource": "agent_registration",
            "result": "failed",
            "details": f"Failed authentication attempt {i+1} from 192.168.1.100"
        }
        events.append(event)
    
    # Add 10 permission denied events from same attacker
    for i in range(10):
        event = {
            "timestamp": base_time - (10-i)*3,
            "operator_id": "attacker_main",
            "action": "EXECUTE",
            "resource": "emergency_shutdown",
            "result": "denied",
            "details": f"Permission denied: viewer role cannot execute admin command"
        }
        events.append(event)
    
    return events


def generate_credential_stuffing_events() -> List[Dict[str, Any]]:
    """Generate mock credential stuffing attack events"""
    events = []
    base_time = int(datetime.now().timestamp())
    
    # Simulate multiple operators from same IP in short time
    operators = ["user1", "user2", "user3", "user4", "user5"]
    
    for i, operator in enumerate(operators):
        event = {
            "event_id": f"evt_test_cred_stuff_{i}",
            "timestamp": base_time - (5-i)*10,
            "event_type": "REGISTER",
            "agent_id": operator,
            "action": "agent_registration",
            "status": "FAILED",
            "details": {
                "reason": "authentication_failed",
                "source_ip": "203.45.67.89",
                "error": "Invalid credentials"
            }
        }
        events.append(event)
    
    return events


def generate_privilege_escalation_events() -> List[Dict[str, Any]]:
    """Generate mock privilege escalation attack events"""
    events = []
    base_time = int(datetime.now().timestamp())
    
    # Simulate viewer trying to execute admin commands
    admin_commands = ["emergency_shutdown", "lock_account", "register_device"]
    
    for i, command in enumerate(admin_commands):
        event = {
            "event_id": f"evt_test_priv_esc_{i}",
            "timestamp": base_time - (3-i)*5,
            "event_type": "EXECUTE",
            "agent_id": "viewer_user_123",
            "action": command,
            "status": "DENIED",
            "details": {
                "reason": "permission_denied",
                "required_role": "admin",
                "user_role": "viewer",
                "error": "Insufficient permissions"
            }
        }
        events.append(event)
    
    return events


def generate_dos_events() -> List[Dict[str, Any]]:
    """Generate mock DoS/rate abuse attack events"""
    events = []
    base_time = int(datetime.now().timestamp())
    
    # Simulate 20 rapid requests from one agent
    for i in range(20):
        event = {
            "event_id": f"evt_test_dos_{i}",
            "timestamp": base_time - (20-i),  # 1 second apart
            "event_type": "EXECUTE",
            "agent_id": "bot_agent_999",
            "action": "read_audit_logs",
            "status": "SUCCESS",
            "details": {
                "endpoint": "/api/v1/audit/logs",
                "response_time_ms": 45,
                "request_number": i + 1
            }
        }
        events.append(event)
    
    return events


def get_test_scenario(scenario_name: str) -> List[Dict[str, Any]]:
    """
    Get mock events for a specific test scenario
    
    Scenarios:
    - brute_force: Multiple failed logins
    - credential_stuffing: Multiple operators from same IP
    - privilege_escalation: Viewer trying admin commands
    - dos: Rapid requests from one agent
    """
    
    scenarios = {
        "brute_force": generate_brute_force_events,
        "credential_stuffing": generate_credential_stuffing_events,
        "privilege_escalation": generate_privilege_escalation_events,
        "dos": generate_dos_events,
    }
    
    if scenario_name not in scenarios:
        raise ValueError(f"Unknown scenario: {scenario_name}. Available: {list(scenarios.keys())}")
    
    return scenarios[scenario_name]()


def inject_test_events(real_events: List[Dict], scenario: str = "brute_force") -> List[Dict]:
    """
    Inject mock events into real events for testing
    
    Args:
        real_events: List of real audit events from wrapper
        scenario: Test scenario to inject
    
    Returns:
        Combined list of real + mock events
    """
    mock_events = get_test_scenario(scenario)
    return real_events + mock_events if real_events else mock_events


# Available test scenarios
AVAILABLE_SCENARIOS = [
    "brute_force",
    "credential_stuffing", 
    "privilege_escalation",
    "dos"
]