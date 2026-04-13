# 🤖 NOVA NEXUS Agent Lab

Welcome to the Agent Lab! This is your workspace for building and deploying specialized AI agents using **Amazon Bedrock** to complete intelligence missions.

## 🎯 Mission Overview

Your goal is to to deploy your first agent to Amazon Bedrock AgentCore.

## 🛠️ Prerequisites

### Required Tools
- **Strands Agents**: Build your agent using [Strands Agents](https://strandsagents.com/latest/)
- **Amazon Bedrock**: Your agents will use Bedrock models for intelligence - [https://aws.amazon.com/bedrock/](https://aws.amazon.com/bedrock/)
- **AWS AgentCore**: Deploy and run your agents - [https://aws.amazon.com/bedrock/agentcore/](https://aws.amazon.com/bedrock/agentcore/)
- **Python 3.10++**

### Architecture Overview
1. **Build** a Strands agent framework
2. **Connect** to Amazon Bedrock models for AI capabilities
4. **Deploy** your agent using AWS AgentCore
5. **Complete** the intro missions with yoru agent

## 🏗️ Building Your First Agent

### Step 1: Create Agent Directory
```bash
mkdir my_agent_name
cd my_agent_name
```

### Step 2: Copy Template Files
```bash
# Copy the hello world template as a starting point
cp ../hello_world_agent/hello_world_agent.py ./my_agent.py
cp ../hello_world_agent/requirements.txt ./requirements.txt
```

### Step 3: Set Up Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Step 4: Deploy with AgentCore
```bash
# Configure your agent
agentcore configure -e my_agent.py

# Launch the agent
agentcore launch
```

### Step 5: Test Your Agent
```bash
# Test with a simple prompt
agentcore invoke '{"prompt": "Hello world"}'
```

## 🎮 Playing the Game

### Mission Workflow
1. **Browse missions** in the Mission Map
2. **Note the mission ID** (e.g., `intro-mission`)
3. **Build/deploy an appropriate agent** 
4. **Get your agent runtime ID** from AgentCore
5. **Deploy via GameDay UI** using format: `mission_id,agent_runtime_id`
6. **Watch for results** in the Mission Map



## 🚀 Ready to Begin?

1. **Check the Mission Map** to see available missions
2. **Choose your first mission**
3. **Build your agent** using the templates and guidance above
4. **Deploy and test** your agent
5. **Submit via GameDay UI** and watch for results!

**Good luck, Agent! Complete the mission to achieve victory! 🎯**
