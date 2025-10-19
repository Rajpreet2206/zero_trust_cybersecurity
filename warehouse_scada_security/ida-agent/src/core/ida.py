"""
Intrusion Detection Agent (IDA) - Main Agent Class
Registers with Go Wrapper and continuously monitors for threats
FIXED: Updated endpoints for actual Go Wrapper (/api/v1/...)
"""

import logging
import time
import sys
import os
from typing import Dict, Any
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from analysis.threat_analyzer import ThreatAnalyzer
from analysis.behavior_analyzer import BehaviorAnalyzer
from analysis.threat_scorer import ThreatScorer
from reasoning.bedrock_reasoner import BedrockReasoner
from execution.response_executor import ResponseExecutor

import requests
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization


class IntrusionDetectionAgent:
    def __init__(self, config):
        self.config = config
        self.logger = self._setup_logging()

        # Agent credentials
        self.agent_name = config.IDA_NAME
        self.wrapper_url = config.WRAPPER_URL
        self.public_key = None
        self.private_key = None
        self.authenticated = False

        # Analysis modules
        self.threat_analyzer = ThreatAnalyzer(config, self.logger)
        self.behavior_analyzer = BehaviorAnalyzer(config, self.logger)
        self.threat_scorer = ThreatScorer(config, self.logger)

        # Reasoning module
        self.bedrock_reasoner = BedrockReasoner(config, self.logger)

        # Response executor
        self.response_executor = ResponseExecutor(config, self.logger, self)

        # Monitoring state
        self.monitoring = False
        self.last_audit_check = 0
        self.threat_history = []

        self.logger.info("="*70)
        self.logger.info("Intrusion Detection Agent Initialized")
        self.logger.info("="*70)

    def _setup_logging(self) -> logging.Logger:
        logger = logging.getLogger("IDA")
        logger.setLevel(self.config.LOG_LEVEL)

        os.makedirs(self.config.LOG_FILE.split('/')[0], exist_ok=True)

        fh = logging.FileHandler(self.config.LOG_FILE)
        fh.setLevel(self.config.LOG_LEVEL)
        ch = logging.StreamHandler()
        ch.setLevel(self.config.LOG_LEVEL)

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        logger.addHandler(fh)
        logger.addHandler(ch)
        return logger

    def setup(self) -> bool:
        """Setup: Register with Go Wrapper, assign role, test authentication"""
        self.logger.info(f"\n[{self.agent_name}] Setting up IDA agent...\n")

        # Step 1: Register with Go Wrapper (wrapper generates keys)
        try:
            self.logger.info(f"Registering with Go Wrapper ({self.wrapper_url})...")
            register_url = f"{self.wrapper_url}/api/v1/identity/register"

            payload = {"agent_id": self.agent_name}
            registration_response = requests.post(register_url, json=payload, timeout=5)
            registration_response.raise_for_status()
            registration_data = registration_response.json()
            self.logger.info("Registered with Go Wrapper")
            time.sleep(0.5)
        except Exception as e:
            self.logger.error(f"Registration failed: {e}")
            return False

        # Step 2: Extract keys from wrapper response
        try:
            self.logger.info("Extracting credentials from wrapper...")
            
            public_key_hex = registration_data.get("public_key")
            private_key_hex = registration_data.get("private_key")
            nonce = registration_data.get("nonce")
            
            if not (public_key_hex and private_key_hex and nonce):
                self.logger.error("Registration response missing required fields")
                return False
            
            # Reconstruct private key from hex
            private_key_bytes = bytes.fromhex(private_key_hex)
            self.private_key = ed25519.Ed25519PrivateKey.from_private_bytes(private_key_bytes[:32])
            
            public_key_bytes = bytes.fromhex(public_key_hex)
            self.public_key = ed25519.Ed25519PublicKey.from_public_bytes(public_key_bytes)
            
            self.logger.info("Credentials extracted")
        except Exception as e:
            self.logger.error(f"Failed to extract credentials: {e}")
            return False

        # Step 3: Assign role
        try:
            self.logger.info(f"Assigning role 'service' to IDA...")
            assign_role_url = f"{self.wrapper_url}/api/v1/policy/assign-role"

            role_payload = {
                "agent_id": self.agent_name,
                "role": "admin"
            }
            role_response = requests.post(assign_role_url, json=role_payload, timeout=5)
            role_response.raise_for_status()
            self.logger.info("Role assigned")
            time.sleep(0.5)
        except Exception as e:
            self.logger.error(f"Role assignment failed: {e}")
            return False

# Step 4: Verify identity using wrapper keys
        try:
            self.logger.info("Verifying identity with Go Wrapper...")
            
            # Sign with the wrapper's private key
            message = f"{self.agent_name}:{nonce}".encode()
            signature = self.private_key.sign(message)
            signature_hex = signature.hex()
            
            # FIXED: Use X-Agent-ID header and send agent_id + signature in body
            headers = {
                "X-Agent-ID": self.agent_name,
                "X-Signature": signature_hex,
                "Content-Type": "application/json"
            }
            
            verify_url = f"{self.wrapper_url}/api/v1/identity/verify"
            
            # FIXED: Send agent_id and signature in body (what handler expects)
            verify_payload = {
                "agent_id": self.agent_name,
                "signature": signature_hex,
                "nonce": nonce
            }
            
            verify_response = requests.post(
                verify_url, 
                json=verify_payload, 
                headers=headers, 
                timeout=5
            )
            verify_response.raise_for_status()
            
            self.authenticated = True
            self.logger.info("Identity verified with Go Wrapper\n")
            return True
            
        except Exception as e:
            self.logger.error(f"Verification failed: {e}")
            return False

    # --- Monitoring and threat handling remain unchanged ---
    def start_monitoring(self):
        if not self.authenticated:
            self.logger.error("Not authenticated. Call setup() first.")
            return

        self.monitoring = True
        self.logger.info(f"\n{'='*70}")
        self.logger.info(f"IDA Starting Continuous Monitoring")
        self.logger.info(f"Monitoring interval: {self.config.MONITOR_INTERVAL}s")
        self.logger.info(f"{'='*70}\n")

        try:
            while self.monitoring:
                cycle_start = time.time()
                self._monitor_cycle()
                elapsed = time.time() - cycle_start
                sleep_time = max(0, self.config.MONITOR_INTERVAL - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)

        except KeyboardInterrupt:
            self.logger.info("\nMonitoring stopped by user")
            self.monitoring = False
        except Exception as e:
            self.logger.error(f"Monitoring error: {e}", exc_info=True)
            self.monitoring = False

    def _monitor_cycle(self):
        audit_logs = self._fetch_audit_logs()
        if not audit_logs:
            return
        threat_signals = self.threat_analyzer.analyze(audit_logs)
        behavior_signals = self.behavior_analyzer.analyze(audit_logs)
        network_signals = self.threat_analyzer.analyze_network(audit_logs)

        threat_data = {
            "operator_behavior": behavior_signals,
            "command_patterns": threat_signals,
            "network_activity": network_signals,
            "timestamp": datetime.now().isoformat(),
            "audit_log_count": len(audit_logs)
        }
        threat_score = self.threat_scorer.calculate_score(threat_data)

        self.logger.info(f"Threat Assessment: Score={threat_score}/100")
        for key, value in threat_data.items():
            if key != "timestamp":
                self.logger.debug(f"  {key}: {value}")

        if threat_score >= self.config.THREAT_SCORE_LOW:
            self._handle_threat(threat_score, threat_data, audit_logs)

        self.threat_history.append({
            "timestamp": datetime.now().isoformat(),
            "score": threat_score,
            "data": threat_data
        })

        cutoff_time = time.time() - self.config.AUDIT_LOG_RETENTION
        self.threat_history = [
            h for h in self.threat_history
            if datetime.fromisoformat(h["timestamp"]).timestamp() > cutoff_time
        ]

    def _fetch_audit_logs(self) -> list:
        """Fetch audit logs from Go Wrapper with correct X-Agent-ID header"""
        try:
            # Create signature for audit log request
            message = f"{self.agent_name}:audit_read".encode()
            signature = self.private_key.sign(message)
            signature_hex = signature.hex()
            
            # FIXED: Use X-Agent-ID header (not X-Operator-ID)
            headers = {
                "X-Agent-ID": self.agent_name,
                "X-Signature": signature_hex,
                "Content-Type": "application/json"
            }
            
            audit_url = f"{self.wrapper_url}/api/v1/audit/logs"
            response = requests.get(audit_url, headers=headers, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            events = data.get("events", [])
            
            self.logger.debug(f"Fetched {len(events)} audit events")
            return events
            
        except Exception as e:
            self.logger.debug(f"Error fetching audit logs: {e}")
            return []


    def _handle_threat(self, threat_score: int, threat_data: Dict, audit_logs: list):
        self.logger.warning(f"\n{'='*70}")
        self.logger.warning(f"THREAT DETECTED - Score: {threat_score}/100")
        self.logger.warning(f"{'='*70}\n")

        bedrock_analysis = self.bedrock_reasoner.analyze_threat(
            threat_score=threat_score,
            threat_data=threat_data,
            audit_logs=audit_logs
        )

        if not bedrock_analysis:
            self.logger.error("Bedrock analysis failed, skipping response")
            return

        self.logger.warning(f"Bedrock Classification: {bedrock_analysis.get('classification')}")
        self.logger.warning(f"Confidence: {bedrock_analysis.get('confidence')}%")
        self.logger.warning(f"Recommendations: {bedrock_analysis.get('recommendations')}\n")

        self.response_executor.execute_response(
            threat_score=threat_score,
            bedrock_analysis=bedrock_analysis,
            threat_data=threat_data
        )

    def stop_monitoring(self):
        self.logger.info("Stopping IDA monitoring...")
        self.monitoring = False

    def get_status(self) -> Dict[str, Any]:
        return {
            "agent_name": self.agent_name,
            "authenticated": self.authenticated,
            "monitoring": self.monitoring,
            "threat_history_length": len(self.threat_history),
            "last_threat_score": self.threat_history[-1]["score"] if self.threat_history else 0
        }
