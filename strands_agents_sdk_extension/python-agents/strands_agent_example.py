"""
Simplified Strands Agent with Zero-Trust Wrapper Integration

This integrates a real Strands agent with the Go wrapper for authentication/authorization.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import logging
import time
import requests
from strands_client import StrandsAgentClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WrappedStrandsAgent:
    """Strands agent that routes requests through zero-trust wrapper"""
    
    def __init__(self, agent_name: str, wrapper_url: str = "http://localhost:8443"):
        self.agent_name = agent_name
        self.wrapper_url = wrapper_url
        self.wrapper_client = StrandsAgentClient(agent_name, wrapper_url)
        self.authenticated = False
    
    def setup(self) -> bool:
        """Setup: Register, assign role, verify identity"""
        logger.info(f"\n[{self.agent_name}] Setting up agent...\n")
        
        # Register
        try:
            logger.info(f"[{self.agent_name}] Registering with wrapper...")
            self.wrapper_client.register_agent()
            time.sleep(0.5)
        except Exception as e:
            logger.error(f"Registration failed: {e}")
            return False
        
        # Assign role
        try:
            logger.info(f"[{self.agent_name}] Assigning admin role...")
            self.wrapper_client.assign_role("admin")
            time.sleep(0.5)
        except Exception as e:
            logger.error(f"Role assignment failed: {e}")
            return False
        
        # Verify - with longer timeout
        try:
            logger.info(f"[{self.agent_name}] Verifying identity...")
            # Increase timeout for verify endpoint
            self.wrapper_client.session.timeout = 60
            
            if self.wrapper_client.verify_with_wrapper():
                self.authenticated = True
                logger.info(f"[{self.agent_name}] ✓ Setup complete\n")
                return True
            else:
                logger.error("Verification failed")
                return False
        except Exception as e:
            logger.error(f"Verification error: {e}")
            return False
        
    def ask(self, question: str) -> str:
        """Ask the agent a question through the wrapper"""
        if not self.authenticated:
            logger.error(f"[{self.agent_name}] Not authenticated")
            return "Error: Not authenticated"
        
        logger.info(f"[{self.agent_name}] Processing: {question}")
        
        try:
            # Execute task and get actual response
            result = self.wrapper_client.execute_task({
                "action": "agent_query",
                "question": question
            })
            
            # Extract the actual response from the mock SDK
            response = result.get("response", "No response received")
            logger.info(f"[{self.agent_name}] ✓ Query executed\n")
            return response
            
        except Exception as e:
            logger.warning(f"[{self.agent_name}] Task execution failed: {e}")
            return f"Error processing question: {e}"


def main():
    """Example: Create and use a Strands agent with zero-trust wrapper"""
    
    print("\n" + "="*70)
    print("STRANDS AGENT WITH ZERO-TRUST WRAPPER")
    print("="*70)
    
    # Create agent
    agent = WrappedStrandsAgent(
        agent_name="strands-agent-001",
        wrapper_url="http://localhost:8443"
    )
    
    # Setup (register, authenticate, verify)
    if not agent.setup():
        logger.error("Setup failed. Exiting.")
        return
    
    # Ask questions
    questions = [
        "What is agentic AI?",
        "Explain zero-trust security",
        "How do autonomous agents work?"
    ]
    
    logger.info(f"[{agent.agent_name}] Asking {len(questions)} questions...\n")
    
    for question in questions:
        response = agent.ask(question)
        logger.info(f"Response: {response}\n")
        time.sleep(1)
    
    logger.info("="*70)
    logger.info("✓ Agent test completed successfully!")
    logger.info("="*70 + "\n")


if __name__ == "__main__":
    main()