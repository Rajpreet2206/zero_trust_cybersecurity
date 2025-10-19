"""
Threat Analyzer - Detects suspicious patterns and threat signals
"""

from typing import Dict, List, Any
from datetime import datetime, timedelta
from collections import defaultdict
import logging


class ThreatAnalyzer:
    """Analyzes command patterns, network activity, and privilege escalation"""
    
    def __init__(self, config, logger: logging.Logger):
        self.config = config
        self.logger = logger
        
        # Baseline patterns (would be loaded from config/database)
        self.baseline_commands_per_hour = 10
        self.baseline_read_write_ratio = 0.8
        
    def analyze(self, audit_logs: List[Dict]) -> Dict[str, Any]:
        """
        Analyze command patterns in audit logs
        
        Returns:
        {
            "command_frequency_anomaly": 0-100,
            "command_type_shift": 0-100,
            "rapid_device_switching": 0-100,
            "dos_pattern": 0-100
        }
        """
        if not audit_logs:
            return {
                "command_frequency_anomaly": 0,
                "command_type_shift": 0,
                "rapid_device_switching": 0,
                "dos_pattern": 0
            }
        
        # Analyze command patterns
        frequency_score = self._analyze_command_frequency(audit_logs)
        type_shift_score = self._analyze_command_types(audit_logs)
        device_switching_score = self._analyze_device_switching(audit_logs)
        dos_score = self._analyze_dos_patterns(audit_logs)
        
        return {
            "command_frequency_anomaly": frequency_score,
            "command_type_shift": type_shift_score,
            "rapid_device_switching": device_switching_score,
            "dos_pattern": dos_score
        }
    
    def analyze_network(self, audit_logs: List[Dict]) -> Dict[str, Any]:
        """
        Analyze network activity patterns
        
        Returns:
        {
            "impossible_travel": 0-100,
            "unauthorized_ip": 0-100,
            "protocol_violation": 0-100
        }
        """
        if not audit_logs:
            return {
                "impossible_travel": 0,
                "unauthorized_ip": 0,
                "protocol_violation": 0
            }
        
        travel_score = self._analyze_impossible_travel(audit_logs)
        ip_score = self._analyze_unauthorized_ips(audit_logs)
        protocol_score = self._analyze_protocol_violations(audit_logs)
        
        return {
            "impossible_travel": travel_score,
            "unauthorized_ip": ip_score,
            "protocol_violation": protocol_score
        }
    
    def _analyze_command_frequency(self, audit_logs: List[Dict]) -> int:
        """
        Detect abnormal command frequency
        Normal: ~10 commands/hour
        Attack: 1000+ commands/hour
        """
        if not audit_logs:
            return 0
        
        # Count commands in last hour
        now = datetime.now()
        one_hour_ago = now - timedelta(hours=1)
        
        recent_commands = [
            log for log in audit_logs
            if log.get("action") == "EXECUTE"
        ]
        
        command_count = len(recent_commands)
        
        # Score based on deviation from baseline
        if command_count > self.baseline_commands_per_hour * 100:
            return 100
        elif command_count > self.baseline_commands_per_hour * 10:
            return int((command_count / (self.baseline_commands_per_hour * 10)) * 100)
        else:
            return 0
    
    def _analyze_command_types(self, audit_logs: List[Dict]) -> int:
        """
        Detect shift from READ to WRITE operations
        Normal: 80% read, 20% write
        Attack: sudden shift to 100% write (changing state)
        """
        execute_logs = [log for log in audit_logs if log.get("action") == "EXECUTE"]
        if not execute_logs:
            return 0
        
        # Categorize by command type
        reads = []
        writes = []
        
        for log in execute_logs:
            resource = log.get("resource", "").lower()
            if any(x in resource for x in ["read", "get", "query"]):
                reads.append(log)
            else:
                writes.append(log)
        
        if len(reads) + len(writes) == 0:
            return 0
        
        write_ratio = len(writes) / (len(reads) + len(writes))
        
        # Score deviation from baseline
        baseline_write_ratio = 1 - self.baseline_read_write_ratio
        deviation = abs(write_ratio - baseline_write_ratio)
        
        return int(min(100, (deviation / baseline_write_ratio) * 100))
    
    def _analyze_device_switching(self, audit_logs: List[Dict]) -> int:
        """
        Detect rapid switching between devices
        Normal: stable, ~2-3 devices per hour
        Attack: 20+ devices per hour (reconnaissance)
        """
        execute_logs = [log for log in audit_logs if log.get("action") == "EXECUTE"]
        if not execute_logs:
            return 0
        
        # Extract unique devices accessed
        devices = set()
        for log in execute_logs:
            resource = log.get("resource", "")
            if resource:
                devices.add(resource)
        
        device_count = len(devices)
        
        if device_count > 20:
            return 100
        elif device_count > 10:
            return int((device_count / 20) * 100)
        else:
            return 0
    
    def _analyze_dos_patterns(self, audit_logs: List[Dict]) -> int:
        """
        Detect DoS patterns - same command repeated rapidly
        """
        if not audit_logs:
            return 0
        
        # Group commands by type
        command_counts = defaultdict(int)
        for log in audit_logs:
            if log.get("action") == "EXECUTE":
                resource = log.get("resource", "")
                command_counts[resource] += 1
        
        # Check for command spam
        for command, count in command_counts.items():
            if count > 50:  # Same command 50+ times
                return 100
            elif count > 20:
                return int((count / 50) * 100)
        
        return 0
    
    def _analyze_impossible_travel(self, audit_logs: List[Dict]) -> int:
        """
        Detect impossible travel between IPs in short time
        Example: Login from US, then command from China in 5 minutes
        """
        if not audit_logs:
            return 0
        
        # Simplified: detect IP changes
        ips = set()
        for log in audit_logs[-20:]:  # Last 20 logs
            ip = log.get("details", "").split("ip=")[-1] if "ip=" in log.get("details", "") else None
            if ip:
                ips.add(ip)
        
        # Multiple IPs in short time = suspicious
        if len(ips) > 3:
            return 80
        elif len(ips) > 1:
            return 40
        else:
            return 0
    
    def _analyze_unauthorized_ips(self, audit_logs: List[Dict]) -> int:
        """
        Detect requests from unauthorized IPs
        """
        # Whitelist (would be in config)
        whitelist = ["127.0.0.1", "192.168.1.0/24", "172.20.0.0/16"]
        
        unauthorized = 0
        for log in audit_logs[-20:]:
            ip = log.get("details", "").split("ip=")[-1] if "ip=" in log.get("details", "") else None
            if ip and ip not in ["127.0.0.1", "localhost"]:
                # Simple check - in production use IP range matching
                if not any(x in ip for x in ["192.168", "172.20"]):
                    unauthorized += 1
        
        if unauthorized > 5:
            return 100
        elif unauthorized > 0:
            return unauthorized * 15
        else:
            return 0
    
    def _analyze_protocol_violations(self, audit_logs: List[Dict]) -> int:
        """
        Detect protocol violations and malformed requests
        """
        violations = 0
        
        for log in audit_logs[-50:]:
            result = log.get("result", "").lower()
            if "error" in result or "failed" in result or "invalid" in result:
                violations += 1
        
        if violations > 10:
            return 100
        elif violations > 5:
            return violations * 10
        else:
            return 0