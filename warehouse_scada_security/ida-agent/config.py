import os
import yaml
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Wrapper Configuration
    WRAPPER_HOST = os.getenv("WRAPPER_HOST", "localhost")
    WRAPPER_PORT = os.getenv("WRAPPER_PORT", "8443")
    WRAPPER_URL = f"http://{WRAPPER_HOST}:{WRAPPER_PORT}"
    
    # IDA Configuration
    IDA_NAME = os.getenv("IDA_NAME", "intrusion-detection-agent-001")
    IDA_ROLE = os.getenv("IDA_ROLE", "security_monitor")
    
    # Bedrock Configuration
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_REGION = os.getenv("AWS_REGION", "us-east-2")
    BEDROCK_MODEL = os.getenv("BEDROCK_MODEL", "us.amazon.nova-premier-v1:0")
    
    # Threat Thresholds
    THREAT_SCORE_LOW = 30
    THREAT_SCORE_MEDIUM = 60
    THREAT_SCORE_HIGH = 85
    THREAT_SCORE_CRITICAL = 90
    
    # Monitoring Configuration
    MONITOR_INTERVAL = int(os.getenv("MONITOR_INTERVAL", "5"))
    AUDIT_LOG_RETENTION = 24 * 60 * 60  # 24 hours in seconds
    
    # Logging
    LOG_FILE = os.getenv("LOG_FILE", "logs/ida.log")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # SCADA Systems
    OPENPLA_HOST = os.getenv("OPENPLA_HOST", "localhost")
    OPENPLA_PORT = os.getenv("OPENPLA_PORT", "502")
    SCADABR_HOST = os.getenv("SCADABR_HOST", "localhost")
    SCADABR_PORT = os.getenv("SCADABR_PORT", "8180")
    
    # Threat Rules - Load from YAML
    THREAT_RULES = {}
    THREAT_PATTERNS = {}
    RESPONSE_ACTIONS = {}
    SENSITIVITY = "medium"
    BASELINE = {}
    TIME_WINDOWS = {}
    ALERTS = {}
    
    @classmethod
    def load_threat_rules(cls):
        """Load threat rules from YAML configuration file"""
        rules_path = Path(__file__).parent.parent / "config" / "threat_rules.yaml"
        
        if not rules_path.exists():
            raise FileNotFoundError(f"Threat rules file not found: {rules_path}")
        
        try:
            with open(rules_path, 'r') as f:
                rules = yaml.safe_load(f)
            
            cls.THREAT_RULES = rules
            cls.THREAT_PATTERNS = rules.get("threat_patterns", {})
            cls.RESPONSE_ACTIONS = rules.get("response_actions", {})
            cls.SENSITIVITY = rules.get("sensitivity", {}).get("current_sensitivity", "medium")
            cls.BASELINE = rules.get("baseline", {})
            cls.TIME_WINDOWS = rules.get("time_windows", {})
            cls.ALERTS = rules.get("alerts", {})
            
            return True
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing threat_rules.yaml: {e}")
        except Exception as e:
            raise Exception(f"Error loading threat rules: {e}")
    
    @classmethod
    def get_threat_pattern(cls, pattern_name):
        """Get threat pattern by name"""
        return cls.THREAT_PATTERNS.get(pattern_name)
    
    @classmethod
    def get_response_actions(cls, threat_level):
        """Get response actions for threat level"""
        return cls.RESPONSE_ACTIONS.get(threat_level, {})
    
    @classmethod
    def get_baseline_behavior(cls, behavior_type):
        """Get baseline behavior for comparison"""
        return cls.BASELINE.get(behavior_type)
    
    @classmethod
    def get_time_window(cls, window_type):
        """Get time window in seconds"""
        return cls.TIME_WINDOWS.get(window_type, 60)


# Load threat rules on module import
try:
    Config.load_threat_rules()
except Exception as e:
    import logging
    logging.warning(f"Failed to load threat rules: {e}")
    print(f"Warning: Threat rules not loaded. Make sure threat_rules.yaml exists in config/")