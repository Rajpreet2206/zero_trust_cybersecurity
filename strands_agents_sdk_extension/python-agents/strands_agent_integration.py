"""
Strands Agent with Zero-Trust Wrapper Integration

This shows how to integrate real Strands agents with the Go wrapper.

Architecture:
  Strands Agent → Auth Client → Go Wrapper → Strands A2A Server
"""

import logging
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from strands_client import StrandsAgentClient
import json
import time

# Assume you have strands installed:
# from strands_tools.calculator import calculator
# from strands import Agent
# from strands.multiagent.a2a import A2AServer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StrandsAgentWithZeroTrust:
    """
    Wraps a Strands agent to route requests through zero-trust wrapper.
    
    This ensures:
    - Agent identity verification
    - Role-based authorization
    - Rate limiting
    - Audit logging
    - Behavioral analytics
    """
    
    def __init__(self, agent_name: str, wrapper_url: str = "http://localhost:8443"):
        """
        Initialize Strands agent with wrapper integration.
        
        Args:
            agent_name: Name of the agent (used as agent_id)
            wrapper_url: URL of the Go zero-trust wrapper
        """
        self.agent_name = agent_name
        self.wrapper_url = wrapper_url
        
        # Create wrapper client
        self.wrapper_client = StrandsAgentClient(
            agent_id=agent_name,
            wrapper_url=wrapper_url
        )
        
        # Track authentication status
        self.is_authenticated = False
        self.is_authorized = False
        
        logger.info(f"Initialized StrandsAgent: {agent_name}")
    
    def authenticate_with_wrapper(self) -> bool:
        """
        Authenticate this agent with the zero-trust wrapper.
        
        Process:
        1. Register agent (get cryptographic credentials)
        2. Assign role (set permissions)
        3. Verify identity (prove possession of private key)
        
        Returns:
            True if authentication successful
        """
        logger.info(f"[{self.agent_name}] Starting authentication...")
        
        # Step 1: Register
        try:
            logger.info(f"[{self.agent_name}] Registering with wrapper...")
            self.wrapper_client.register_agent()
            logger.info(f"[{self.agent_name}] ✓ Registration successful")
        except Exception as e:
            logger.error(f"[{self.agent_name}] ✗ Registration failed: {e}")
            return False
        
        time.sleep(0.5)
        
        # Step 2: Assign role
        try:
            logger.info(f"[{self.agent_name}] Assigning role: admin")
            self.wrapper_client.assign_role("admin")
            logger.info(f"[{self.agent_name}] ✓ Role assigned")
            self.is_authorized = True
        except Exception as e:
            logger.error(f"[{self.agent_name}] ✗ Role assignment failed: {e}")
            return False
        
        time.sleep(0.5)
        
        # Step 3: Verify identity
        try:
            logger.info(f"[{self.agent_name}] Verifying identity...")
            if self.wrapper_client.verify_with_wrapper():
                logger.info(f"[{self.agent_name}] ✓ Identity verified")
                self.is_authenticated = True
                return True
            else:
                logger.error(f"[{self.agent_name}] ✗ Identity verification failed")
                return False
        except Exception as e:
            logger.error(f"[{self.agent_name}] ✗ Verification error: {e}")
            return False
    
    def execute_action(self, action: str, params: dict = None) -> dict:
        """
        Execute an action through the zero-trust wrapper.
        
        The wrapper will:
        1. Verify agent identity
        2. Check agent authorization
        3. Enforce rate limiting
        4. Forward to Strands SDK
        5. Log operation
        6. Detect anomalies
        
        Args:
            action: Name of action (e.g., "calculate", "process")
            params: Parameters for the action
            
        Returns:
            Result from the action
        """
        if not self.is_authenticated:
            logger.error(f"[{self.agent_name}] Not authenticated. Call authenticate_with_wrapper() first")
            return {"error": "Not authenticated"}
        
        logger.info(f"[{self.agent_name}] Executing action: {action}")
        
        task = {
            "action": action,
            "params": params or {}
        }
        
        try:
            result = self.wrapper_client.execute_task(task)
            logger.info(f"[{self.agent_name}] ✓ Action succeeded")
            return result
        except Exception as e:
            logger.error(f"[{self.agent_name}] ✗ Action failed: {e}")
            return {"error": str(e)}
    
    def get_health_status(self) -> dict:
        """Get current health status of agent"""
        return {
            "agent_name": self.agent_name,
            "authenticated": self.is_authenticated,
            "authorized": self.is_authorized,
            "wrapper_url": self.wrapper_url
        }
    
    def get_analytics(self) -> dict:
        """Get behavioral analytics for this agent"""
        if not self.is_authenticated:
            return {"error": "Not authenticated"}
        
        try:
            stats = self.wrapper_client.get_rate_limit_stats()
            anomalies = self.wrapper_client.get_anomalies()
            
            return {
                "rate_limit_stats": stats,
                "anomalies_detected": len(anomalies),
                "anomalies": anomalies
            }
        except Exception as e:
            logger.error(f"Failed to get analytics: {e}")
            return {"error": str(e)}


def main():
    """
    Example: Create a calculator agent with zero-trust wrapper
    """
    
    print("\n" + "="*70)
    print("STRANDS AGENT WITH ZERO-TRUST WRAPPER INTEGRATION")
    print("="*70 + "\n")
    
    # Create agent
    logger.info("Creating Calculator Agent...")
    agent = StrandsAgentWithZeroTrust(
        agent_name="calculator-agent-001",
        wrapper_url="http://localhost:8443"
    )
    
    # Authenticate
    logger.info("\nAuthenticating with wrapper...")
    if not agent.authenticate_with_wrapper():
        logger.error("Authentication failed. Exiting.")
        return
    
    logger.info("\n" + "-"*70)
    logger.info("Agent successfully authenticated and authorized!")
    logger.info("-"*70 + "\n")
    
    # Execute actions
    actions = [
        {"action": "calculate", "params": {"operation": "add", "a": 10, "b": 5}},
        {"action": "calculate", "params": {"operation": "multiply", "a": 6, "b": 7}},
        {"action": "calculate", "params": {"operation": "divide", "a": 100, "b": 5}},
    ]
    
    logger.info("Executing actions through wrapper...\n")
    
    for task in actions:
        logger.info(f"Action: {task['action']}")
        logger.info(f"Params: {task['params']}")
        
        result = agent.execute_action(
            action=task["action"],
            params=task["params"]
        )
        
        logger.info(f"Result: {json.dumps(result)}\n")
        time.sleep(0.5)
    
    # Get analytics
    logger.info("Getting agent analytics...\n")
    analytics = agent.get_analytics()
    logger.info(f"Analytics: {json.dumps(analytics, indent=2)}\n")
    
    # Get status
    logger.info("Agent status:")
    status = agent.get_health_status()
    for key, value in status.items():
        logger.info(f"  {key}: {value}")
    
    logger.info("\n" + "="*70)
    logger.info("✓ Integration test completed successfully!")
    logger.info("="*70 + "\n")


if __name__ == "__main__":
    main()