from strands import Agent, tool
from strands_tools import http_request
from strands.models import BedrockModel
import boto3
import os

# Get current AWS region
session = boto3.Session()
region = session.region_name or os.environ.get('AWS_REGION', 'us-east-1')

model_id = "us.amazon.nova-pro-v1:0"
model = BedrockModel(model_id=model_id)

@tool
def research_assistant(query: str) -> str:
    """Research assistant that can search the web for real estate information"""
    try:
        RESEARCH_ASSISTANT_PROMPT="""
        You are a research assistant. Focus only on providing factual, well-sourced information in response to research questions. Always cite your sources when possible.
        """

        research_agent = Agent(
            system_prompt=RESEARCH_ASSISTANT_PROMPT,
            tools=[http_request],
            model=model
        )
        response = research_agent(query)
        return str(response)
    except Exception as e:
        return f"Error in research: {str(e)}. Please try a different query or check your connection."
