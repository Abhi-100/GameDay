import boto3
import json
import os
from strands import Agent, tool
from strands_tools import calculator
from strands.models import BedrockModel


# Get current AWS region
session = boto3.Session()
region = session.region_name or os.environ.get('AWS_REGION', 'us-east-1')

# Initialize DynamoDB client
dynamodb = boto3.client('dynamodb', region_name=region)


@tool
def math_assistant(query: str) -> str:
    """Math calculations"""
    try:
        MATH_ASSISTANT_PROMPT="""
        You are a math assistant that solves mathematical problem.
        """
        
        model = BedrockModel(model_id="us.amazon.nova-pro-v1:0")
        math_agent = Agent(
            system_prompt=MATH_ASSISTANT_PROMPT,
            tools=[calculator],
            model=model
        )
        response = math_agent(query)
        return str(response)
    except Exception as e:
        return f"Error in research: {str(e)}. Please try a different query or check your connection."


@tool
def projects_query(query: str) -> str:
    """Query dynamodb HouseProjects project data"""
    try:
        response = dynamodb.scan(TableName='RainbowVibeHouseProjects')
        projects = response['Items']
        
        # Convert DynamoDB format to readable format
        formatted_projects = []
        for project in projects:
            formatted_project = {}
            for key, value in project.items():
                if 'S' in value:
                    formatted_project[key] = value['S']
                elif 'N' in value:
                    formatted_project[key] = float(value['N'])
            formatted_projects.append(formatted_project)
        
        # Create a summary for the agent to work with
        summary = f"Found {len(formatted_projects)} house projects. "
        summary += f"Data includes: {', '.join(formatted_projects[0].keys()) if formatted_projects else 'No data'}"
        
        return f"{summary}\n\nProject data: {json.dumps(formatted_projects, indent=2)}"
        
    except Exception as e:
        return f"Error querying DynamoDB: {str(e)}"
