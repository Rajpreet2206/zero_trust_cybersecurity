#!/usr/bin/env python
"""
Intrusion Detection Agent (IDA) - Main Entry Point

Usage:
    python main.py

This will:
1. Initialize the Intrusion Detection Agent
2. Register with Go Wrapper (strands_agents_sdk_extension)
3. Start continuous monitoring for threats
4. Analyze threats using Bedrock AI
5. Execute security responses through Go Wrapper
"""

import sys
import os
import argparse
import logging
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import configuration and IDA agent
from config import Config
from core.ida import IntrusionDetectionAgent

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

def setup_parser() -> argparse.ArgumentParser:
    """Setup command-line argument parser"""
    parser = argparse.ArgumentParser(
        description="Intrusion Detection Agent for SCADA Systems",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start IDA with default configuration
  python main.py
  
  # Start with debug logging
  python main.py --debug
  
  # Test wrapper connection only
  python main.py --test-connection
  
  # Print configuration and exit
  python main.py --show-config
        """
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    parser.add_argument(
        "--test-connection",
        action="store_true",
        help="Test connection to Go Wrapper and exit"
    )
    
    parser.add_argument(
        "--show-config",
        action="store_true",
        help="Show configuration and exit"
    )
    
    parser.add_argument(
        "--wrapper-url",
        default=None,
        help="Override wrapper URL (default: from config)"
    )
    
    parser.add_argument(
        "--monitor-interval",
        type=int,
        default=None,
        help="Override monitoring interval in seconds"
    )
    
    return parser


def print_banner():
    """Print welcome banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║     INTRUSION DETECTION AGENT (IDA) v1.0                   ║
    ║     AI-Powered Security for SCADA Systems                  ║
    ║                                                              ║
    ║     Monitoring: OpenPLC, ScadaBR, pfSense                  ║
    ║     Security Layer: Go Wrapper (Ed25519, Audit Logging)    ║
    ║     AI Reasoning: Amazon Bedrock                           ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def show_configuration(config: Config):
    """Display current configuration"""
    print("\n" + "="*70)
    print("IDA CONFIGURATION")
    print("="*70)
    print(f"Agent Name: {config.IDA_NAME}")
    print(f"Agent Role: {config.IDA_ROLE}")
    print(f"\nWrapper Configuration:")
    print(f"  URL: {config.WRAPPER_URL}")
    print(f"  Host: {config.WRAPPER_HOST}:{config.WRAPPER_PORT}")
    print(f"\nBedrock Configuration:")
    print(f"  Region: {config.AWS_REGION}")
    print(f"  Model: {config.BEDROCK_MODEL}")
    print(f"\nThreat Thresholds:")
    print(f"  Low: < {config.THREAT_SCORE_LOW}")
    print(f"  Medium: {config.THREAT_SCORE_LOW} - {config.THREAT_SCORE_MEDIUM}")
    print(f"  High: {config.THREAT_SCORE_MEDIUM} - {config.THREAT_SCORE_HIGH}")
    print(f"  Critical: >= {config.THREAT_SCORE_HIGH}")
    print(f"\nMonitoring:")
    print(f"  Interval: {config.MONITOR_INTERVAL}s")
    print(f"  Log File: {config.LOG_FILE}")
    print(f"  Log Level: {config.LOG_LEVEL}")
    print("="*70 + "\n")


def test_wrapper_connection(config: Config) -> bool:
    """Test connection to Go Wrapper"""
    print("\nTesting Go Wrapper connection...")
    print(f"Wrapper URL: {config.WRAPPER_URL}")
    
    try:
        import requests
        response = requests.get(f"{config.WRAPPER_URL}/health", timeout=5)
        
        if response.status_code == 200:
            print("✓ Go Wrapper is reachable and healthy")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"✗ Unexpected response: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Failed to connect: {e}")
        print("Make sure Go Wrapper is running:")
        print(f"  cd strands_agents_sdk_extension")
        print(f"  ./bin/wrapper-server.exe")
        return False


def test_bedrock_connection(config: Config) -> bool:
    """Test connection to Bedrock"""
    print("\nTesting Bedrock connection...")
    
    try:
        import boto3
        session = boto3.Session(
            aws_access_key_id=config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
            region_name=config.AWS_REGION
        )
        
        # Try to list available models
        bedrock = session.client("bedrock", region_name=config.AWS_REGION)
        models = bedrock.list_foundation_models()
        
        if models:
            print(f"✓ Bedrock is available in region {config.AWS_REGION}")
            print(f"Available models: {len(models.get('modelSummaries', []))}")
            return True
    except Exception as e:
        print(f"⚠ Bedrock not available: {e}")
        print("IDA will use fallback threat analysis")
        return False


def main():
    """Main entry point"""
    
    # Parse arguments
    parser = setup_parser()
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    
    # Load configuration
    config = Config()
    
    # Override config from command line
    if args.debug:
        config.LOG_LEVEL = "DEBUG"
    if args.wrapper_url:
        config.WRAPPER_URL = args.wrapper_url
    if args.monitor_interval:
        config.MONITOR_INTERVAL = args.monitor_interval
    
    # Show configuration if requested
    if args.show_config:
        show_configuration(config)
        return 0
    
    # Test wrapper connection if requested
    if args.test_connection:
        wrapper_ok = test_wrapper_connection(config)
        bedrock_ok = test_bedrock_connection(config)
        
        if wrapper_ok and bedrock_ok:
            print("\n✓ All systems ready")
            return 0
        else:
            print("\n⚠ Some systems unavailable (see above)")
            return 1
    
    # Show configuration
    show_configuration(config)
    
    # Test wrapper connection
    if not test_wrapper_connection(config):
        print("Cannot proceed without Go Wrapper")
        return 1
    
    # Test Bedrock connection
    test_bedrock_connection(config)
    
    # Initialize IDA agent
    print("\nInitializing Intrusion Detection Agent...")
    ida = IntrusionDetectionAgent(config)
    
    # Setup (register with wrapper)
    print("Setting up IDA with Go Wrapper...")
    if not ida.setup():
        print("Failed to setup IDA")
        return 1
    
    # Start monitoring
    print("\n" + "="*70)
    print("Starting continuous threat monitoring...")
    print("="*70)
    print("Press Ctrl+C to stop\n")
    
    try:
        ida.start_monitoring()
    except KeyboardInterrupt:
        print("\n\nShutting down IDA...")
        ida.stop_monitoring()
    except Exception as e:
        print(f"\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    print("IDA shutdown complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())