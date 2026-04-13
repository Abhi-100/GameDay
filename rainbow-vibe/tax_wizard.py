
import json
import boto3
from strands import tool
from bedrock_agentcore.tools.code_interpreter_client import code_session

@tool
def execute_python(code: str, description: str = "") -> str:
    """Execute Python code for tax calculations and data analysis"""
    
    if description:
        code = f"# {description}\n{code}"
    
    print(f"\nExecuting code: {code}")
    
    # Get region dynamically from boto3 session
    session = boto3.Session()
    region = session.region_name 
    
    with code_session(region) as code_client:
        response = code_client.invoke("executeCode", {
            "code": code,
            "language": "python",
            "clearContext": False
        })
        
        for event in response["stream"]:
            return json.dumps(event["result"])
