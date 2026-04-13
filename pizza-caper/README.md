# The Great Pizza Caper

Agent2Agent Protocol (A2A) collaboration system using Strands Agents and Amazon Bedrock AgentCore.

## Deployment

```bash
# 1. Install dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. Setup AWS resources
python setup_all.py

# 3. Deploy agents
agentcore configure -e location_agent.py --execution-role <PIZZA_ROLE_ARN> --protocol A2A
agentcore launch

agentcore configure -e orders_agent.py --execution-role <PIZZA_ROLE_ARN> --protocol A2A
agentcore launch

agentcore configure -e detective_agent.py --execution-role <PIZZA_ROLE_ARN> --protocol A2A
agentcore launch

# 4. Set environment variables
source export_env.sh

# 5. Run frontend
streamlit run a2a_frontend.py
```

