from strands import Agent
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands.models import BedrockModel
from strands.models import BedrockModel

app = BedrockAgentCoreApp()


@app.entrypoint
def strands_agent_bedrock(payload):
    """
    Invoke the agent with a payload
    """
    user_input = payload.get("prompt")
    print("User input:", user_input)

    model_id = "us.anthropic.claude-sonnet-4-20250514-v1:0"
    model = BedrockModel(
        model_id=model_id,
    )

    SYSTEM_PROMPT = """
You are an expert AWS Certified Solutions Architect. You can answer questions about AWS.
"""

    agent = Agent(model=model, system_prompt=SYSTEM_PROMPT)

    response = agent(user_input)
    print("Response:")
    print(response.message["content"][0]["text"])

    return response.message["content"][0]["text"]


if __name__ == "__main__":
    app.run()
