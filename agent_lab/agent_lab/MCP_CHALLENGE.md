# 🤖 NOVA NEXUS Agent Lab

Welcome to the Agent Lab! This is your workspace for building and deploying specialized AI agents using **Amazon Bedrock** and **Model Context Protocol (MCP) servers** to complete intelligence missions.

## 🎯 Mission Overview

Your goal is to **complete 5 different missions** using agents you build here. Each mission type requires agents with specific MCP server capabilities - you'll need to explore the available MCP servers to find the right tools for each mission.

## 🛠️ Prerequisites

### Required Tools
- **Strands Agents**: Build your agent using [Strands Agents](https://strandsagents.com/latest/)
- **Amazon Bedrock**: Your agents will use Bedrock models for intelligence - [https://aws.amazon.com/bedrock/](https://aws.amazon.com/bedrock/)
- **AWS AgentCore**: Deploy and run your agents - [https://aws.amazon.com/bedrock/agentcore/](https://aws.amazon.com/bedrock/agentcore/)
- **MCP Servers**: Choose the right MCP server for your mission - [https://github.com/awslabs/mcp](https://github.com/awslabs/mcp)

### Architecture Overview
1. **Build** a Strands agent framework
2. **Connect** to Amazon Bedrock models for AI capabilities
3. **Integrate** the appropriate MCP server for your mission
4. **Deploy** your agent using AWS AgentCore
5. **Complete** missions by leveraging MCP server tools

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

### Step 4: Configure MCP Server
Edit your agent file to include the appropriate MCP server for your target mission. Check the [AWS MCP repository](https://github.com/awslabs/mcp) to find the right MCP server and configuration for your mission type.

### Step 5: Deploy with AgentCore
```bash
# Configure your agent
agentcore configure -e my_agent.py

# Launch the agent
agentcore launch
```

### Step 6: Test Your Agent
```bash
# Test with a simple prompt
agentcore invoke '{"prompt": "Hello, test my MCP tools"}'
```

## 🎮 Playing the Game

### Mission Workflow
1. **Browse missions** in the Mission Map
2. **Note the mission ID** (e.g., `cdk-s3-deployment`)
3. **Build/deploy an appropriate agent** with the right MCP server
4. **Get your agent runtime ID** from AgentCore
5. **Deploy via GameDay UI** using format: `mission_id,agent_runtime_id`
6. **Watch for results** in the Mission Map

### Scoring System
- **Easy missions**: 1,000 credits
- **Medium missions**: 3,000 credits  
- **Hard missions**: 5,000 credits

### Mission Requirements
Each mission requires your agent to:
- ✅ Use the appropriate MCP tools
- ✅ Provide accurate solutions
- ✅ List the MCP tools used in the response
- ✅ Meet specific mission criteria (see individual mission prompts)

## 📋 MCP Server Discovery

Explore the [AWS MCP Servers repository](https://github.com/awslabs/mcp) to discover available MCP servers and their capabilities. Each mission type will require different MCP server tools - part of the challenge is figuring out which servers provide the functionality you need!


## 🏆 Tips for Success

### Strategy Tips
- **Start with easy missions** to build confidence
- **Read mission requirements carefully** before building agents
- **Test agents thoroughly** before deployment
- **Use specific MCP servers** for each mission type

### Technical Tips
- **Keep agent code focused** on the mission requirements
- **Handle errors gracefully** in your agent logic  
- **Log MCP tool usage clearly** in responses
- **Test with various prompts** to ensure robustness

### Mission Tips
- **Read mission prompts carefully** to understand requirements
- **Explore different MCP servers** to find the right tools
- **Test your agent** against mission criteria before submission
- **Pay attention to output format** requirements in mission descriptions

## 🚀 Ready to Begin?

1. **Check the Mission Map** to see available missions
2. **Choose your first mission** based on difficulty level
3. **Build your agent** using the templates and guidance above
4. **Deploy and test** your agent
5. **Submit via GameDay UI** and watch for results!

**Good luck, Agent! Complete 5 missions to achieve victory! 🎯**

---

*For technical support or questions about MCP servers, refer to the [AWS MCP GitHub repository](https://github.com/awslabs/mcp)*