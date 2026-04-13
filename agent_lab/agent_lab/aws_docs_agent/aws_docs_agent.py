import logging

from bedrock_agentcore.runtime import BedrockAgentCoreApp
from mcp import StdioServerParameters, stdio_client
from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the AgentCore App
app = BedrockAgentCoreApp()

bedrock_model = BedrockModel(
    model_id="us.anthropic.claude-sonnet-4-20250514-v1:0",
    temperature=0.7,
)

SYSTEM_PROMPT = """
You are an expert AWS Certified Solutions Architect. You can query the AWS Documentation to help customers understand best practices on building on AWS.
"""


@app.entrypoint
def strands_agent_bedrock(payload):
    """
    Invoke the agent with a payload

    Args:
        payload (dict): Contains the prompt from the user

    Returns:
        str: The agent's response text
    """
    try:
        user_input = payload.get("prompt")
        logger.info(f"User input: {user_input}")

        # Create a new MCP client for each invocation
        aws_docs_client = MCPClient(
            lambda: stdio_client(
                StdioServerParameters(
                    command="uvx", args=["awslabs.aws-documentation-mcp-server@latest"]
                )
            )
        )

        # Initialize agent with MCP tools
        with aws_docs_client:
            all_tools = aws_docs_client.list_tools_sync()

            agent = Agent(
                tools=all_tools, model=bedrock_model, system_prompt=SYSTEM_PROMPT
            )

            # Get response from agent
            response = agent(user_input)
            print("Response:")
            print(response.message["content"][0]["text"])

            # Extract and return the text content from the response
            return response.message["content"][0]["text"]
    except Exception as e:
        logger.error(f"Error processing request: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    app.run()
