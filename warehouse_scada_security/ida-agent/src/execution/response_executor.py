"""
Response Executor - Executes security responses through Go Wrapper
FIXED: Uses correct X-Agent-ID header and /api/v1/sdk/execute endpoint
"""

from typing import Dict, Any
import logging
import requests
import json


class ResponseExecutor:
    """
    Executes IDA's response actions through the Go Wrapper
    All actions signed with Ed25519 and authenticated via middleware
    """
    
    def __init__(self, config, logger: logging.Logger, ida_agent):
        self.config = config
        self.logger = logger
        self.ida_agent = ida_agent
    
    def execute_response(
        self,
        threat_score: int,
        bedrock_analysis: Dict[str, Any],
        threat_data: Dict[str, Any]
    ):
        """Execute response based on threat level and Bedrock recommendations"""
        
        urgency = bedrock_analysis.get("urgency", "LOW")
        recommendations = bedrock_analysis.get("recommendations", [])
        classification = bedrock_analysis.get("classification", "UNKNOWN")
        
        self.logger.warning(f"\nExecuting Response: {classification}")
        self.logger.warning(f"Urgency: {urgency}")
        self.logger.warning(f"Recommendations: {recommendations}\n")
        
        # Execute actions based on urgency
        if urgency == "CRITICAL":
            self._execute_critical_response(recommendations, threat_score, bedrock_analysis)
        elif urgency == "HIGH":
            self._execute_high_response(recommendations, threat_score, bedrock_analysis)
        elif urgency == "MEDIUM":
            self._execute_medium_response(recommendations, threat_score, bedrock_analysis)
        else:
            self._execute_low_response(recommendations, threat_score, bedrock_analysis)
    
    def _execute_critical_response(
        self,
        recommendations: list,
        threat_score: int,
        bedrock_analysis: Dict
    ):
        """Execute CRITICAL level response"""
        self.logger.critical("CRITICAL THREAT - Executing emergency response")
        
        # Log critical incident
        self._log_incident(threat_score, bedrock_analysis, "CRITICAL")
        
        # Execute critical actions
        for action in recommendations:
            if "EMERGENCY_SHUTDOWN" in action:
                self._execute_action("emergency_shutdown", {})
            elif "LOCK_ALL_ACCOUNTS" in action:
                self._execute_action("lock_all_accounts", {})
            elif "ISOLATE_NETWORK" in action:
                self._execute_action("isolate_network_segment", {"segment": "all"})
            elif "ALERT_SECURITY" in action:
                self._send_alert("CRITICAL", bedrock_analysis)
    
    def _execute_high_response(
        self,
        recommendations: list,
        threat_score: int,
        bedrock_analysis: Dict
    ):
        """Execute HIGH level response"""
        self.logger.error("HIGH THREAT - Executing defense measures")
        
        # Log high threat incident
        self._log_incident(threat_score, bedrock_analysis, "HIGH")
        
        # Execute high-level actions
        for action in recommendations:
            if "LOCK_SUSPECT" in action or "LOCK_ACCOUNT" in action:
                self._execute_action("lock_operator_account", {
                    "operator_id": self._get_suspect_operator(bedrock_analysis)
                })
            elif "REVOKE_SESSION" in action:
                self._execute_action("revoke_operator_session", {
                    "operator_id": self._get_suspect_operator(bedrock_analysis)
                })
            elif "ISOLATE_DEVICE" in action:
                self._execute_action("isolate_device", {
                    "device_id": self._get_suspect_device(bedrock_analysis)
                })
            elif "BLOCK_IP" in action:
                self._execute_action("block_ip", {
                    "ip_address": self._get_malicious_ip(bedrock_analysis)
                })
            elif "ALERT" in action:
                self._send_alert("HIGH", bedrock_analysis)
    
    def _execute_medium_response(
        self,
        recommendations: list,
        threat_score: int,
        bedrock_analysis: Dict
    ):
        """Execute MEDIUM level response"""
        self.logger.warning("MEDIUM THREAT - Executing precautions")
        
        # Log medium threat incident
        self._log_incident(threat_score, bedrock_analysis, "MEDIUM")
        
        # Execute medium-level actions
        for action in recommendations:
            if "MONITOR" in action:
                self._execute_action("enable_monitoring", {
                    "operator_id": self._get_suspect_operator(bedrock_analysis)
                })
            elif "RATE_LIMIT" in action:
                self._execute_action("rate_limit_operator", {
                    "operator_id": self._get_suspect_operator(bedrock_analysis),
                    "limit": "10_requests_per_minute"
                })
            elif "REQUIRE_MFA" in action:
                self._execute_action("require_mfa", {
                    "operator_id": self._get_suspect_operator(bedrock_analysis)
                })
            elif "ALERT" in action:
                self._send_alert("MEDIUM", bedrock_analysis)
    
    def _execute_low_response(
        self,
        recommendations: list,
        threat_score: int,
        bedrock_analysis: Dict
    ):
        """Execute LOW level response"""
        self.logger.info("LOW THREAT - Monitoring anomaly")
        
        # Just log and monitor
        self._log_incident(threat_score, bedrock_analysis, "LOW")
        
        for action in recommendations:
            if "MONITOR" in action:
                self.logger.info("Enabling enhanced monitoring")
            elif "REVIEW" in action:
                self.logger.info("Manual review recommended")
    
    def _execute_action(self, action: str, params: Dict[str, Any]):
        """
        Execute action through Go Wrapper with Ed25519 signature
        Uses correct X-Agent-ID header and endpoint
        """
        try:
            # Create message to sign
            message_parts = [action] + [f"{k}={v}" for k, v in params.items()]
            message = ":".join(message_parts).encode()
            
            # Sign with IDA's private key
            signature = self.ida_agent.private_key.sign(message)
            signature_hex = signature.hex()
            
            # FIXED: Use X-Agent-ID (not X-Operator-ID) to match middleware
            headers = {
                "X-Agent-ID": self.ida_agent.agent_name,
                "X-Signature": signature_hex,
                "Content-Type": "application/json"
            }
            
            # Execute endpoint
            execute_url = f"{self.config.WRAPPER_URL}/api/v1/sdk/execute"
            
            # Payload structure for SDK endpoint
            payload = {
                "task": {
                    "question": f"{action}: {json.dumps(params)}"
                }
            }
            
            # Send to Go Wrapper
            response = requests.post(
                execute_url,
                json=payload,
                headers=headers,
                timeout=5
            )
            
            response.raise_for_status()
            result = response.json()
            
            self.logger.info(f"Action executed: {action} -> {result.get('status', 'OK')}")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to execute action '{action}': {e}")
            return False
    
    def _log_incident(
        self,
        threat_score: int,
        bedrock_analysis: Dict,
        severity: str
    ):
        """
        Log security incident with full context
        Recorded by Go Wrapper and stored in audit logs
        """
        incident_log = {
            "event": "SECURITY_INCIDENT",
            "severity": severity,
            "threat_score": threat_score,
            "classification": bedrock_analysis.get("classification"),
            "confidence": bedrock_analysis.get("confidence"),
            "reasoning": bedrock_analysis.get("reasoning"),
            "recommendations": bedrock_analysis.get("recommendations"),
            "ida_agent": self.ida_agent.agent_name
        }
        
        # Execute logging through wrapper (immutable audit trail)
        self._execute_action("log_security_event", incident_log)
    
    def _send_alert(self, severity: str, bedrock_analysis: Dict):
        """Send alert to security team"""
        alert = {
            "severity": severity,
            "classification": bedrock_analysis.get("classification"),
            "confidence": bedrock_analysis.get("confidence"),
            "recommendations": ", ".join(bedrock_analysis.get("recommendations", []))
        }
        
        self.logger.warning(f"\nALERT: {alert['classification']} (Confidence: {alert['confidence']}%)")
        self.logger.warning(f"Recommendations: {alert['recommendations']}\n")
        
        # In production, send email/Slack notification
        self._execute_action("send_alert", alert)
    
    def _get_suspect_operator(self, bedrock_analysis: Dict) -> str:
        """Extract suspect operator from analysis"""
        reasoning = bedrock_analysis.get("reasoning", "")
        if "operator" in reasoning.lower():
            return "operator_under_suspicion"
        return "unknown_operator"
    
    def _get_suspect_device(self, bedrock_analysis: Dict) -> str:
        """Extract suspect device from analysis"""
        reasoning = bedrock_analysis.get("reasoning", "")
        if "device" in reasoning.lower():
            return "device_under_suspicion"
        return "unknown_device"
    
    def _get_malicious_ip(self, bedrock_analysis: Dict) -> str:
        """Extract malicious IP from analysis"""
        reasoning = bedrock_analysis.get("reasoning", "")
        if "impossible travel" in reasoning.lower() or "ip" in reasoning.lower():
            return "malicious_ip"
        return "unknown_ip"