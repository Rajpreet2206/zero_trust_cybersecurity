"""
Threat Scorer - Calculates combined threat score from multiple signals
"""

from typing import Dict, Any
import logging


class ThreatScorer:
    """
    Combines multiple threat signals into a single threat score (0-100)
    
    Score Ranges:
    0-30: Low threat - monitor
    31-60: Medium threat - alert and lockdown
    61-85: High threat - isolate device
    86-100: Critical threat - emergency shutdown
    """
    
    def __init__(self, config, logger: logging.Logger):
        self.config = config
        self.logger = logger
        
        # Threat signal weights (importance)
        self.weights = {
            # Behavior signals (60% of score)
            "failed_login_attempts": 0.15,
            "permission_denied_attempts": 0.10,
            "privilege_escalation": 0.20,
            "unauthorized_role_usage": 0.10,
            "credential_stuffing": 0.05,
            
            # Command pattern signals (25% of score)
            "command_frequency_anomaly": 0.10,
            "command_type_shift": 0.08,
            "rapid_device_switching": 0.05,
            "dos_pattern": 0.02,
            
            # Network signals (15% of score)
            "impossible_travel": 0.10,
            "unauthorized_ip": 0.03,
            "protocol_violation": 0.02,
        }
    
    def calculate_score(self, threat_data: Dict[str, Any]) -> int:
        """
        Calculate final threat score from all signals
        
        Args:
            threat_data: Dictionary containing all threat signals
                {
                    "operator_behavior": {...},
                    "command_patterns": {...},
                    "network_activity": {...},
                    "timestamp": ISO format timestamp
                }
        
        Returns:
            threat_score: 0-100 integer
        """
        total_score = 0.0
        
        # Extract signals
        behavior = threat_data.get("operator_behavior", {})
        commands = threat_data.get("command_patterns", {})
        network = threat_data.get("network_activity", {})
        
        # Calculate weighted score
        signals = {
            # Behavior signals
            "failed_login_attempts": behavior.get("failed_login_attempts", 0),
            "permission_denied_attempts": behavior.get("permission_denied_attempts", 0),
            "privilege_escalation": behavior.get("privilege_escalation", 0),
            "unauthorized_role_usage": behavior.get("unauthorized_role_usage", 0),
            "credential_stuffing": behavior.get("credential_stuffing", 0),
            
            # Command patterns
            "command_frequency_anomaly": commands.get("command_frequency_anomaly", 0),
            "command_type_shift": commands.get("command_type_shift", 0),
            "rapid_device_switching": commands.get("rapid_device_switching", 0),
            "dos_pattern": commands.get("dos_pattern", 0),
            
            # Network activity
            "impossible_travel": network.get("impossible_travel", 0),
            "unauthorized_ip": network.get("unauthorized_ip", 0),
            "protocol_violation": network.get("protocol_violation", 0),
        }
        
        # Apply weights
        for signal_name, signal_value in signals.items():
            weight = self.weights.get(signal_name, 0)
            contribution = (signal_value / 100.0) * weight * 100  # Normalize and weight
            total_score += contribution
            
            # Log high-impact signals
            if signal_value > 50:
                self.logger.debug(f"Signal '{signal_name}' high: {signal_value} (weight: {weight})")
        
        # Final score
        final_score = int(min(100, max(0, total_score)))
        
        return final_score
    
    def get_threat_level(self, score: int) -> str:
        """Get threat level name from score"""
        if score < 30:
            return "LOW"
        elif score < 60:
            return "MEDIUM"
        elif score < 85:
            return "HIGH"
        else:
            return "CRITICAL"
    
    def get_threat_description(self, score: int, threat_data: Dict) -> str:
        """Get human-readable threat description"""
        level = self.get_threat_level(score)
        
        behavior = threat_data.get("operator_behavior", {})
        commands = threat_data.get("command_patterns", {})
        network = threat_data.get("network_activity", {})
        
        # Find top signals
        top_signals = []
        all_signals = {
            **behavior,
            **commands,
            **network
        }
        
        top_signals = sorted(
            [(name, value) for name, value in all_signals.items()],
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        description = f"Threat Level: {level} (Score: {score}/100)\n"
        description += "Top Threat Indicators:\n"
        
        for signal_name, signal_value in top_signals:
            if signal_value > 0:
                description += f"  - {signal_name}: {signal_value}/100\n"
        
        return description