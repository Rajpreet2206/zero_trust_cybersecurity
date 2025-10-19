import sys
import os
sys.path.insert(0, os.getcwd())

# Import directly
from config import Config
from src.analysis.behavior_analyzer import BehaviorAnalyzer
from src.analysis.threat_scorer import ThreatScorer
import logging

# Setup
config = Config()
logger = logging.getLogger("TEST")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(message)s'))
logger.addHandler(handler)

# Mock audit logs
mock_audit_logs = [
    {"action": "EXECUTE", "operator_id": "attacker", "result": "denied", "details": "failed_auth"} 
    for _ in range(10)
]
mock_audit_logs.extend([
    {"action": "REGISTER", "operator_id": f"attacker_{i}", "result": "failed", "details": "wrong_password"}
    for i in range(5)
])

# Analyze
behavior_analyzer = BehaviorAnalyzer(config, logger)
threat_scorer = ThreatScorer(config, logger)

behavior_signals = behavior_analyzer.analyze(mock_audit_logs)
threat_data = {
    "operator_behavior": behavior_signals,
    "command_patterns": {},
    "network_activity": {},
    "timestamp": "2025-10-19T15:23:00",
    "audit_log_count": len(mock_audit_logs)
}

threat_score = threat_scorer.calculate_score(threat_data)

print(f"\n{'='*70}")
print(f"THREAT DETECTION TEST")
print(f"{'='*70}")
print(f"Threat Score: {threat_score}/100")
print(f"Behavior Signals: {behavior_signals}")
print(f"{'='*70}\n")
