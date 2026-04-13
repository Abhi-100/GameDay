import boto3
from strands import Agent
from strands.multiagent import Swarm
from strands_tools import current_time
from strands.models import BedrockModel
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from botocore.config import Config as BotocoreConfig

from rainbow_scout_spies import research_assistant
from market_maven_agent import knowledge_base_search
from profit_potion_agent import projects_query, math_assistant
from sparkle_design_agent import image_generator
from tax_wizard import execute_python

app = BedrockAgentCoreApp()

GUARDRAIL_ID = "lr7gg1a4yuqk"
GUARDRAIL_VERSION = "1"


def _check_guardrail(text):
    """Pre-check input against guardrail. Returns blocked message or None."""
    client = boto3.client('bedrock-runtime', region_name='us-east-1')
    resp = client.apply_guardrail(
        guardrailIdentifier=GUARDRAIL_ID,
        guardrailVersion=GUARDRAIL_VERSION,
        source='INPUT',
        content=[{'text': {'text': text}}]
    )
    if resp['action'] == 'GUARDRAIL_INTERVENED':
        for output in resp.get('outputs', []):
            return output.get('text', 'Request blocked by guardrail.')
        return 'Request blocked by guardrail.'
    return None


def _build_swarm():
    boto_config = BotocoreConfig(
        retries={"max_attempts": 3, "mode": "standard"},
        connect_timeout=15,
        read_timeout=360
    )

    model = BedrockModel(
        model_id="us.amazon.nova-pro-v1:0",
        boto_client_config=boto_config,
        guardrail_id=GUARDRAIL_ID,
        guardrail_version=GUARDRAIL_VERSION,
        guardrail_trace="enabled"
    )

    rainbow_scout = Agent(name="rainbow_scout", model=model,
        tools=[research_assistant, current_time],
        system_prompt="You are Rainbow Scout, a real estate research specialist. Use research_assistant for web searches on general real estate questions, current_time for current date and time. Consult other specialized agents to handle market analysis, financial, design, and tax calculation tasks.")

    market_maven = Agent(name="market_maven", model=model,
        tools=[knowledge_base_search, current_time],
        system_prompt="You are Market Maven, a market analysis expert. ALWAYS use knowledge_base_search for historical new residential sales reports, current_time for current date and time.")

    profit_potion = Agent(name="profit_potion", model=model,
        tools=[projects_query, math_assistant, current_time],
        system_prompt="You are Profit Potion, a financial analyst. ALWAYS use projects_query when user inquires about house project data. Use math_assistant for calculations, current_time for current date and time.")

    sparkle_design = Agent(name="sparkle_design", model=model,
        tools=[image_generator, current_time],
        system_prompt="You are Sparkle Design, a creative visual specialist. Use image_generator to create images.")

    tax_wizard_agent = Agent(name="tax_wizard", model=model,
        tools=[execute_python, current_time],
        system_prompt="You are Tax Wizard, a tax calculation specialist. ALWAYS use execute_python to run Python code for tax calculations and data analysis. Always validate tax calculations through code execution. Use current_time for timestamps.")

    return Swarm(
        [rainbow_scout, market_maven, profit_potion, sparkle_design, tax_wizard_agent],
        max_handoffs=20, max_iterations=20,
        execution_timeout=900.0, node_timeout=300.0,
        repetitive_handoff_detection_window=8,
        repetitive_handoff_min_unique_agents=3
    )


def _extract_text(response):
    """Extract text from SwarmResult."""
    if hasattr(response, 'results') and response.results:
        for node_result in reversed(list(response.results.values())):
            result = getattr(node_result, 'result', None)
            if result and hasattr(result, 'message'):
                msg = result.message
                if isinstance(msg, dict) and 'content' in msg:
                    for block in msg['content']:
                        if isinstance(block, dict) and 'text' in block:
                            return block['text']
                return str(msg)
    return str(response)


@app.entrypoint
async def strands_agent_bedrock(payload):
    user_input = payload.get("prompt")
    print("User input:", user_input)

    # Pre-check guardrail
    blocked = _check_guardrail(user_input)
    if blocked:
        print("GUARDRAIL BLOCKED:", blocked)
        return {
            "output": blocked,
            "stopReason": "guardrail_intervened",
            "guardrailAction": "INTERVENED"
        }

    swarm = _build_swarm()
    response = await swarm.invoke_async(user_input)
    text = _extract_text(response)
    print("Response:", text[:500])
    return text

if __name__ == "__main__":
    app.run()
