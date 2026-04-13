# The Legend of Lost Colors

A multi-modal agent with access to media analysis, location and flight data MCP tools, thru a gateway using Amazon Bedrock AgentCore.

## Helpful commands
For more information on how to use AgentCore CLI, refer to this page - https://aws.github.io/bedrock-agentcore-starter-toolkit/api-reference/cli.html

### Install dependencies
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Setup IAM Role (Use this for All AgentCore Resources). Do this before performing any task. You will need this for all
```bash
python3 IAM-setup.py
```

### Setup OAuth Identity Providers
```bash
python3 identity_setup.py
```

### Deploy agents
```bash
agentcore configure -e multimodal_data_agent.py -rf requirements.txt
agentcore launch
```

### Deploy MCP servers
```bash
agentcore configure -e server.py -rf requirements.txt -p MCP -ac '{"customJWTAuthorizer": {"allowedClients": ["<client-ID>"],"discoveryUrl": "<discovery-URL>"}}' -n <MCP-server-name>
```
#### Launch MCP servers with specific environment variables (For BDA MCP server you'd need the key as AWS_BUCKET_NAME)
```bash
agentcore launch --env KEY=VALUE
```

### Generate URL from Agent runtime ARN (runtime_URL_generator is under tools/)
```bash
python3 runtime_URL_generator.py <agent runtime ARN>
```

### Run frontend
This is get the Streamlit app up and running on port 8501. There will be a prompt on code server to open the web app in browser. If not go to the vscode/proxy/8501/ path of the code server URL. For example - For example if your Code server’s URL is https://d288mc9d1dcg19.cloudfront.net/vscode/?folder=/home/ubuntu/environment/, Go to https://d288mc9d1dcg19.cloudfront.net/vscode/proxy/8501/
```bash
pip install uv
uv sync
uv run streamlit run app.py
```

