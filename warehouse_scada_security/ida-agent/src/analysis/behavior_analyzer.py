"""
Behavior Analyzer - Detects anomalous operator behavior
"""

from typing import Dict, List, Any
from datetime import datetime, timedelta
from collections import defaultdict
import logging


class BehaviorAnalyzer:
    """Analyzes operator behavior for anomalies"""
    
    def __init__(self, config, logger: logging.Logger):
        self.config = config
        self.logger = logger
        
        # Baseline thresholds
        self.max_failed_logins_per_hour = 3
        self.max_permission_denied_per_hour = 5
        self.normal_commands_per_minute = 2
    
    def analyze(self, audit_logs: List[Dict]) -> Dict[str, Any]:
        """
        Analyze operator behavior patterns
        
        Returns:
        {
            "failed_login_attempts": 0-100,
            "permission_denied_attempts": 0-100,
            "privilege_escalation": 0-100,
            "unauthorized_role_usage": 0-100,
            "credential_stuffing": 0-100
        }
        """
        if not audit_logs:
            return {
                "failed_login_attempts": 0,
                "permission_denied_attempts": 0,
                "privilege_escalation": 0,
                "unauthorized_role_usage": 0,
                "credential_stuffing": 0
            }
        
        # Analyze behavior signals
        failed_login_score = self._analyze_failed_logins(audit_logs)
        perm_denied_score = self._analyze_permission_denied(audit_logs)
        priv_esc_score = self._analyze_privilege_escalation(audit_logs)
        role_abuse_score = self._analyze_role_abuse(audit_logs)
        cred_stuff_score = self._analyze_credential_stuffing(audit_logs)
        
        return {
            "failed_login_attempts": failed_login_score,
            "permission_denied_attempts": perm_denied_score,
            "privilege_escalation": priv_esc_score,
            "unauthorized_role_usage": role_abuse_score,
            "credential_stuffing": cred_stuff_score
        }
    
    def _analyze_failed_logins(self, audit_logs: List[Dict]) -> int:
        """
        Detect brute force attacks - multiple failed login attempts
        Normal: 0-1 failed attempt per hour
        Attack: 5+ failed attempts in few minutes
        """
        # Get failed logins from last hour
        now = datetime.now()
        one_hour_ago = now - timedelta(hours=1)
        
        failed_logins = [
            log for log in audit_logs
            if log.get("action") == "REGISTER" and log.get("result") == "failed"
        ]
        
        failed_count = len(failed_logins)
        
        # Score based on failed attempts
        if failed_count > 10:
            return 100
        elif failed_count > 5:
            return int((failed_count / 10) * 100)
        elif failed_count > self.max_failed_logins_per_hour:
            return int((failed_count / self.max_failed_logins_per_hour) * 50)
        else:
            return 0
    
    def _analyze_permission_denied(self, audit_logs: List[Dict]) -> int:
        """
        Detect permission violation attempts
        Normal: 0-1 denied attempt per hour
        Attack: 5+ denied attempts (operator trying forbidden actions)
        """
        perm_denied = [
            log for log in audit_logs
            if log.get("result") == "denied" and log.get("action") == "EXECUTE"
        ]
        
        denied_count = len(perm_denied)
        
        if denied_count > 10:
            return 100
        elif denied_count > self.max_permission_denied_per_hour:
            return int((denied_count / 10) * 100)
        else:
            return 0
    
    def _analyze_privilege_escalation(self, audit_logs: List[Dict]) -> int:
        """
        Detect privilege escalation attempts
        Example: viewer role trying to execute admin-only commands
        """
        escalation_attempts = 0
        
        # Track operators and their attempted actions
        operator_actions = defaultdict(list)
        for log in audit_logs[-100:]:  # Last 100 logs
            operator_id = log.get("operator_id", "")
            action = log.get("action", "")
            result = log.get("result", "")
            resource = log.get("resource", "")
            
            if action == "EXECUTE" and result == "denied":
                # Check if attempting restricted action
                restricted_actions = ["emergency_shutdown", "lock_account", "register_device"]
                if any(x in resource.lower() for x in restricted_actions):
                    escalation_attempts += 1
        
        if escalation_attempts > 5:
            return 100
        elif escalation_attempts > 2:
            return escalation_attempts * 20
        else:
            return 0
    
    def _analyze_role_abuse(self, audit_logs: List[Dict]) -> int:
        """
        Detect unauthorized use of role
        Example: Operator with 'viewer' role executing write commands
        """
        role_abuse = 0
        
        # Track what roles execute what actions
        role_action_map = defaultdict(lambda: {"read": 0, "write": 0})
        
        for log in audit_logs[-200:]:
            operator_id = log.get("operator_id", "")
            resource = log.get("resource", "").lower()
            
            if log.get("action") == "EXECUTE" and log.get("result") == "success":
                if any(x in resource for x in ["read", "get", "query", "status"]):
                    role_action_map[operator_id]["read"] += 1
                else:
                    role_action_map[operator_id]["write"] += 1
        
        # Check for anomalies
        for operator, actions in role_action_map.items():
            total = actions["read"] + actions["write"]
            if total > 0:
                write_ratio = actions["write"] / total
                if write_ratio > 0.9:  # 90%+ write operations
                    role_abuse += 1
        
        if role_abuse > 3:
            return 100
        elif role_abuse > 0:
            return role_abuse * 30
        else:
            return 0
    
    def _analyze_credential_stuffing(self, audit_logs: List[Dict]) -> int:
        """
        Detect credential stuffing attack
        Multiple different operators trying from same source in short time
        """
        if not audit_logs:
            return 0
        
        # Group by IP and count unique operators
        ip_operators = defaultdict(set)
        
        for log in audit_logs[-100:]:
            details = log.get("details", "")
            ip = details.split("ip=")[-1] if "ip=" in details else None
            operator = log.get("operator_id", "")
            
            if ip and operator:
                ip_operators[ip].add(operator)
        
        # Detect if one IP is trying multiple operator accounts
        for ip, operators in ip_operators.items():
            if len(operators) > 5:
                return 100
            elif len(operators) > 3:
                return 70
            elif len(operators) > 1 and "192.168" not in ip and "172.20" not in ip:
                return 50
        
        return 0