from strands import Agent, tool
from strands_tools import retrieve
from strands.models import BedrockModel
import boto3
import os

# Get current AWS region
session = boto3.Session()
region = session.region_name or os.environ.get('AWS_REGION', 'us-east-1')

# Set up environment variables for knowledge base
os.environ['KNOWLEDGE_BASE_ID'] = 'NTWHWUBK7C'
os.environ['AWS_REGION'] = region

model_id = "us.amazon.nova-pro-v1:0"
model = BedrockModel(model_id=model_id)

@tool
def knowledge_base_search(query: str) -> str:
    """Search the knowledge base for historic releases of the New Residential Sales report"""
    try:
        KB_AGENT_PROMPT = """
        You are a helpful assistant that retrieves accurate, concise, and well-sourced historic releases of the New Residential Sales report from knowledge bases. 
        If the information is not available in the knowledge base, clearly state that. Always cite your sources from the knowledge base.
        """
        
        kb_agent = Agent(
            system_prompt=KB_AGENT_PROMPT,
            tools=[retrieve],
            model=model
        )
        response = kb_agent(query)
        return str(response)
    except Exception as e:
        return f"Error searching knowledge base: {str(e)}. Please check that the knowledge base is properly configured and accessible."
