"""
Mock SDK that uses real Strands Agent with Bedrock (secure credentials)
"""

from flask import Flask, request, jsonify
import os
import sys

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

@app.route('/execute', methods=['POST'])
def execute():
    """Execute with real Strands agent or fallback"""
    try:
        data = request.json
        task = data.get('task', {})
        question = task.get('question', 'Hello')
        
        if AGENT_READY and agent:
            # Use real Bedrock agent
            response = agent(question)
        else:
            # Fallback mock response
            response = f"Mock response to: {question}"
        
        result = {
            "status": "success",
            "agent": "bedrock-nova" if AGENT_READY else "mock-agent",
            "question": question,
            "response": response,
        }
        
        return jsonify(result), 200
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