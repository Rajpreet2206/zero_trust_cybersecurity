import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Wrapper Configuration
    WRAPPER_HOST = os.getenv("WRAPPER_HOST", "localhost")
    WRAPPER_PORT = os.getenv("WRAPPER_PORT", "8443")  # CHANGED FROM 8443
    WRAPPER_URL = f"http://{WRAPPER_HOST}:{WRAPPER_PORT}"
    
    # IDA Configuration
    IDA_NAME = "intrusion-detection-agent-001"
    IDA_ROLE = "security_monitor"
    
    # Bedrock Configuration
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_REGION = os.getenv("AWS_REGION", "us-east-2")
    BEDROCK_MODEL = "us.amazon.nova-premier-v1:0"
    
    # Threat Thresholds
    THREAT_SCORE_LOW = 30
    THREAT_SCORE_MEDIUM = 60
    THREAT_SCORE_HIGH = 85
    THREAT_SCORE_CRITICAL = 90
    
    # Monitoring Configuration
    MONITOR_INTERVAL = 5  # seconds
    AUDIT_LOG_RETENTION = 24 * 60 * 60  # 24 hours in seconds
    
    # Logging
    LOG_FILE = "logs/ida.log"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")
    
    # SCADA Systems
    OPENPLA_HOST = os.getenv("OPENPLA_HOST", "localhost")
    OPENPLA_PORT = os.getenv("OPENPLA_PORT", "502")
    SCADABR_HOST = os.getenv("SCADABR_HOST", "localhost")
    SCADABR_PORT = os.getenv("SCADABR_PORT", "8180")