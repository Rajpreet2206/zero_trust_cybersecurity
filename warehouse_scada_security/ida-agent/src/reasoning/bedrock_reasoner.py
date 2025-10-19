"""
Bedrock Reasoner - Uses AWS Bedrock AI to analyze threats and recommend actions
"""

from typing import Dict, Any, Optional
import json
import logging

try:
    import boto3
    from strands import Agent
    from strands.models import BedrockModel
    BEDROCK_AVAILABLE = True
except ImportError:
    BEDROCK_AVAILABLE = False


class BedrockReasoner:
    """
    Uses Bedrock to reason about detected threats
    Asks: "Is this a threat? What should we do?"
    """
    
    def __init__(self, config, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.agent = None
        self.initialized = False
        
        if BEDROCK_AVAILABLE:
            self._initialize_bedrock()
        else:
            self.logger.warning("Bedrock not available, using fallback reasoning")
    
    def _initialize_bedrock(self):
        """Initialize Bedrock agent"""
        try:
            session = boto3.Session(
                aws_access_key_id=self.config.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=self.config.AWS_SECRET_ACCESS_KEY,
                region_name=self.config.AWS_REGION
            )
                        
            nova_model = BedrockModel(
                boto_session=session,  # optional, can omit if using env vars
                model_id="us.amazon.nova-premier-v1:0",  # exact model ID from AWS Console
                temperature= 0.8,

            )
            
            self.agent = Agent(model=nova_model)
            self.initialized = True
            self.logger.info("[OK] Bedrock initialized successfully")
        except Exception as e:
            self.logger.warning(f"Failed to initialize Bedrock: {e}")
            self.initialized = False
    
    def analyze_threat(
        self,
        threat_score: int,
        threat_data: Dict[str, Any],
        audit_logs: list
    ) -> Optional[Dict[str, Any]]:
        """
        Ask Bedrock to analyze the threat and provide recommendations
        
        Returns:
        {
            "classification": "Credential Compromise" | "DoS Attack" | etc,
            "confidence": 85,  # percentage
            "reasoning": "Detailed explanation",
            "recommendations": ["Lock account", "Block IP", ...],
            "urgency": "CRITICAL" | "HIGH" | "MEDIUM" | "LOW"
        }
        """
        
        if not self.initialized:
            return self._fallback_analysis(threat_score, threat_data)
        
        try:
            # Format threat data for Bedrock
            prompt = self._format_threat_prompt(threat_score, threat_data, audit_logs)
            
            self.logger.debug(f"Asking Bedrock: {prompt[:200]}...")
            
            # Query Bedrock
            response = self.agent(prompt)
            
            # Parse response
            analysis = self._parse_bedrock_response(response, threat_score)
            return analysis
        
        except Exception as e:
            self.logger.error(f"Bedrock analysis error: {e}")
            return self._fallback_analysis(threat_score, threat_data)
    
    def _format_threat_prompt(
        self,
        threat_score: int,
        threat_data: Dict,
        audit_logs: list
    ) -> str:
        """Format threat data into a prompt for Bedrock"""
        
        behavior = threat_data.get("operator_behavior", {})
        commands = threat_data.get("command_patterns", {})
        network = threat_data.get("network_activity", {})
        
        prompt = f"""CYBERSECURITY THREAT ANALYSIS REQUEST

You are a cybersecurity expert analyzing a potential attack on an industrial SCADA system.

THREAT INDICATORS (Score: {threat_score}/100):

Operator Behavior Anomalies:
- Failed login attempts: {behavior.get('failed_login_attempts', 0)}/100
- Permission denied attempts: {behavior.get('permission_denied_attempts', 0)}/100
- Privilege escalation attempts: {behavior.get('privilege_escalation', 0)}/100
- Unauthorized role usage: {behavior.get('unauthorized_role_usage', 0)}/100
- Credential stuffing: {behavior.get('credential_stuffing', 0)}/100

Command Pattern Anomalies:
- Command frequency anomaly: {commands.get('command_frequency_anomaly', 0)}/100
- Command type shift (read to write): {commands.get('command_type_shift', 0)}/100
- Rapid device switching: {commands.get('rapid_device_switching', 0)}/100
- DoS pattern detected: {commands.get('dos_pattern', 0)}/100

Network Activity Anomalies:
- Impossible travel (IP location): {network.get('impossible_travel', 0)}/100
- Unauthorized IP: {network.get('unauthorized_ip', 0)}/100
- Protocol violation: {network.get('protocol_violation', 0)}/100

QUESTION:
Based on these threat indicators, please analyze:
1. Is this a cyberattack? What type?
2. How confident are you (0-100%)?
3. What is the classification? (e.g., Credential Compromise, DoS, Insider Threat, etc)
4. What immediate actions should be taken to stop the attack?
5. What is the urgency level? (CRITICAL, HIGH, MEDIUM, LOW)

Please respond in JSON format:
{{
  "is_attack": true/false,
  "classification": "Attack Type",
  "confidence": 0-100,
  "reasoning": "Detailed explanation",
  "recommendations": ["Action 1", "Action 2", "Action 3"],
  "urgency": "CRITICAL/HIGH/MEDIUM/LOW"
}}"""
        
        return prompt
    
    def _parse_bedrock_response(self, response: str, threat_score: int) -> Dict[str, Any]:
        """Parse Bedrock's response"""
        try:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group())
            else:
                # Fallback if no JSON found
                analysis = self._fallback_analysis(threat_score, {})
            
            return analysis
        except Exception as e:
            self.logger.error(f"Failed to parse Bedrock response: {e}")
            return self._fallback_analysis(threat_score, {})
    
    def _fallback_analysis(self, threat_score: int, threat_data: Dict) -> Dict[str, Any]:
        """
        Fallback analysis when Bedrock is not available
        Uses rule-based classification
        """
        if threat_score >= 90:
            return {
                "is_attack": True,
                "classification": "CRITICAL THREAT",
                "confidence": 85,
                "reasoning": "Multiple high-severity threat indicators detected. System compromise likely.",
                "recommendations": [
                    "EMERGENCY_SHUTDOWN",
                    "LOCK_ALL_ACCOUNTS",
                    "ISOLATE_NETWORK_SEGMENT",
                    "ALERT_SECURITY_TEAM",
                    "PRESERVE_AUDIT_LOGS"
                ],
                "urgency": "CRITICAL"
            }
        elif threat_score >= 70:
            return {
                "is_attack": True,
                "classification": "HIGH THREAT - Credential Compromise/DoS",
                "confidence": 80,
                "reasoning": "Multiple threat signals indicate active attack in progress.",
                "recommendations": [
                    "LOCK_SUSPECT_ACCOUNT",
                    "REVOKE_ACTIVE_SESSIONS",
                    "ISOLATE_DEVICE",
                    "BLOCK_MALICIOUS_IP",
                    "ALERT_ADMIN"
                ],
                "urgency": "HIGH"
            }
        elif threat_score >= 50:
            return {
                "is_attack": True,
                "classification": "MEDIUM THREAT - Suspicious Activity",
                "confidence": 70,
                "reasoning": "Moderate threat indicators suggest possible intrusion attempt.",
                "recommendations": [
                    "MONITOR_CLOSELY",
                    "RATE_LIMIT_OPERATOR",
                    "REQUIRE_MFA",
                    "LOG_EVENT"
                ],
                "urgency": "MEDIUM"
            }
        elif threat_score >= 30:
            return {
                "is_attack": False,
                "classification": "LOW THREAT - Anomalous Activity",
                "confidence": 60,
                "reasoning": "Minor threat signals detected. Monitor for escalation.",
                "recommendations": [
                    "MONITOR",
                    "LOG_EVENT",
                    "REVIEW_MANUALLY"
                ],
                "urgency": "LOW"
            }
        else:
            return {
                "is_attack": False,
                "classification": "NORMAL",
                "confidence": 95,
                "reasoning": "No significant threat indicators detected.",
                "recommendations": [],
                "urgency": "NONE"
            }