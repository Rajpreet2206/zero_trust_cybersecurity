"""
Mock SDK that uses real Strands Agent with Bedrock (secure credentials)
"""

from flask import Flask, request, jsonify
import os
import sys
import json

# Import Strands and Bedrock
try:
    from strands import Agent
    from strands.models import BedrockModel
    import boto3
except ImportError:
    print("Error: strands and boto3 must be installed")
    print("pip install strands boto3")
    sys.exit(1)

app = Flask(__name__)

# Initialize Bedrock agent with credentials from environment variables
try:
    session = boto3.Session(
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION", "us-east-2")
    )
    
    nova_model = BedrockModel(
        boto_session=session,
        model_config={
            "model_id": "us.amazon.nova-premier-v1:0",
            "temperature": 0.8,
        }
    )
    
    agent = Agent(model=nova_model)
    AGENT_READY = True
    
except Exception as e:
    print(f"Warning: Could not initialize Bedrock agent: {e}")
    print("Falling back to mock responses")
    AGENT_READY = False
    agent = None

# Add health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})

@app.route('/execute', methods=['POST'])
def execute():
    """Execute with real Strands agent or fallback"""
    try:
        data = request.json
        # Accept both {"question": "..."} and {"task": {"question": "..."}} formats
        question = data.get('question')
        if not question and 'task' in data:
            question = data['task'].get('question')
        if not question:
            question = "Hello"

        if not AGENT_READY:
            # Fallback mock responses
            mock_responses = {
                "What is agentic AI?": "Agentic AI refers to artificial intelligence systems that can act autonomously to achieve specific goals. These systems can make decisions, take actions, and adapt their behavior based on their environment and objectives.",
                "Explain zero-trust security": "Zero-trust security is a cybersecurity framework that requires all users and systems, whether inside or outside the network, to be authenticated, authorized, and validated before gaining access to applications and data. It operates on the principle of 'never trust, always verify'.",
                "How do autonomous agents work?": "Autonomous agents are software systems that can operate independently to achieve goals. They use sensors to perceive their environment, decision-making algorithms to determine actions, and actuators to execute those actions. They often employ AI and machine learning to improve their performance over time."
            }
            response = mock_responses.get(question, "I don't have specific information about that topic.")
            return jsonify({"response": response}), 200

        # If AGENT_READY and agent is set, use the real agent
        try:
            raw = agent(question) if agent else f"Mock response to: {question}"
            # Safely serialize any kind of object to JSON string using default=str
            try:
                response_text = json.dumps(raw, default=str)
            except Exception:
                response_text = str(raw)
            return jsonify({"response": response_text}), 200
        except Exception as e:
            # Print full traceback to the server console for debugging
            import traceback
            traceback.print_exc()
            return jsonify({"status": "error", "message": str(e)}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "agent_type": "bedrock-nova" if AGENT_READY else "mock"
    }), 200

if __name__ == '__main__':
    print("\n" + "="*60)
    print("Mock SDK with Strands Bedrock Agent")
    print("="*60)
    print(f"Agent status: {'READY' if AGENT_READY else 'MOCK MODE'}")
    print("Starting on http://localhost:5000")
    print("="*60 + "\n")
    app.run(host='localhost', port=5000)