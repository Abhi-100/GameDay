#!/bin/bash

# Copyright 2025 Amazon.com and its affiliates; all rights reserved.
# This file is Amazon Web Services Content and may not be duplicated without permission.

# Cipher Quest Agent Deployment Script
# Deploys and configures all cipher quest agents using AgentCore

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
AGENT_NAME="cipher_quest_agent"
ENTRYPOINT="cipher_command_agent.py"
EXECUTION_ROLE_NAME="CipherQuestExecutionRole"

echo -e "${BLUE}🔐 Cipher Quest Agent Deployment Script${NC}"
echo "=================================================="

# Function to print status messages
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
print_status "Checking prerequisites..."

if ! command_exists aws; then
    print_error "AWS CLI not found. Please install AWS CLI first."
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity >/dev/null 2>&1; then
    print_error "AWS credentials not configured. Please run 'aws configure' first."
    exit 1
fi

print_success "Prerequisites check passed"

# Create and activate virtual environment
print_status "Setting up Python virtual environment..."

if [ ! -d ".venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv .venv
    if [ $? -eq 0 ]; then
        print_success "Virtual environment created"
    else
        print_error "Failed to create virtual environment"
        exit 1
    fi
else
    print_status "Virtual environment already exists"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source .venv/bin/activate

if [ $? -eq 0 ]; then
    print_success "Virtual environment activated"
else
    print_error "Failed to activate virtual environment"
    exit 1
fi

# Get AWS account ID and region
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION=$(aws configure get region)

if [ -z "$REGION" ]; then
    REGION="us-east-1"
    print_warning "No default region configured, using us-east-1"
fi

print_status "AWS Account ID: $ACCOUNT_ID"
print_status "AWS Region: $REGION"

# Construct execution role ARN
EXECUTION_ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/${EXECUTION_ROLE_NAME}"

print_status "Using execution role: $EXECUTION_ROLE_ARN"

# Check if execution role exists
print_status "Checking if execution role exists..."
if aws iam get-role --role-name "$EXECUTION_ROLE_NAME" >/dev/null 2>&1; then
    print_success "Execution role found: $EXECUTION_ROLE_NAME"
else
    print_error "Execution role not found: $EXECUTION_ROLE_NAME"
    print_status "Please ensure the CloudFormation stack has been deployed with the team resources."
    print_status "The role should be created by the team_enable_cfn.yaml template."
    exit 1
fi

# Validate agent files exist
print_status "Validating agent files..."

required_files=(
    "cipher_command_agent.py"
    "cipher_rookie_agent.py"
    "pattern_detective_agent.py"
    "cipher_master_agent.py"
    "requirements.txt"
)

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        print_error "Required file not found: $file"
        exit 1
    fi
done

print_success "All required agent files found"

# Install dependencies
print_status "Installing dependencies..."
if command_exists uv; then
    print_status "Using uv for faster dependency installation..."
    uv pip install -r requirements.txt
else
    print_status "Using pip for dependency installation..."
    pip install -r requirements.txt
fi

print_success "Dependencies installed successfully"

# Check for agentcore after installation
print_status "Checking for AgentCore CLI..."
if ! command_exists agentcore; then
    print_error "AgentCore CLI not found after installation."
    print_status "This should have been installed from requirements.txt"
    print_status "Try manually: pip install bedrock-agentcore"
    exit 1
fi

print_success "AgentCore CLI is available"

# Configure AgentCore
print_status "Configuring AgentCore agent (auto-creating ECR repository)..."

# Pipe empty input to auto-accept default (press Enter)
    agentcore configure \
    --entrypoint "$ENTRYPOINT" \
    --execution-role "$EXECUTION_ROLE_ARN" \
    --name "$AGENT_NAME"

if [ $? -eq 0 ]; then
    print_success "AgentCore configuration completed"
else
    print_error "AgentCore configuration failed"
    exit 1
fi

# Deploy the agent
print_status "Deploying cipher quest agent..."

agentcore launch

if [ $? -eq 0 ]; then
    print_success "Agent deployment completed successfully!"
else
    print_error "Agent deployment failed"
    exit 1
fi

# Get agent information
print_status "Retrieving agent information..."

AGENT_INFO=$(agentcore describe 2>/dev/null || echo "Could not retrieve agent info")
if [ "$AGENT_INFO" != "Could not retrieve agent info" ]; then
    echo "$AGENT_INFO"
    
    # Extract agent ARN if possible
    AGENT_ARN=$(echo "$AGENT_INFO" | grep -o 'arn:aws:bedrock-agentcore:[^"]*' | head -1)
    if [ -n "$AGENT_ARN" ]; then
        print_success "Agent ARN: $AGENT_ARN"
        
        # Save ARN to file for GameDay validation
        echo "$AGENT_ARN" > cipher_quest_agent_arn.txt
        print_status "Agent ARN saved to cipher_quest_agent_arn.txt"
    fi
fi



# Display deployment summary
echo ""
echo "=================================================="
print_success "🎉 Cipher Quest Agent Deployment Complete!"
echo "=================================================="
echo ""
echo "📋 Deployment Summary:"
echo "   • Agent Name: $AGENT_NAME"
echo "   • Entrypoint: $ENTRYPOINT"
echo "   • Execution Role: $EXECUTION_ROLE_ARN"
echo "   • Region: $REGION"
if [ -n "$AGENT_ARN" ]; then
echo "   • Agent ARN: $AGENT_ARN"
fi
echo ""
echo "🧪 Testing Commands (All Cipher Types):"
echo ""
echo "📝 Basic Substitution Ciphers:"
echo "   • Caesar: agentcore invoke '{\"prompt\": \"Decrypt this: WKH TXLFN EURZQ IRA MXPSV RYHU WKH ODCB GRJ\"}'"
echo "   • ROT13: agentcore invoke '{\"prompt\": \"Decrypt this: JRYPBZR GB GUR PVCURE DHRFG\"}'"
echo "   • Atbash: agentcore invoke '{\"prompt\": \"Decrypt this: GSV JFRXP YILDM ULC QFNKH LEVI GSV OZAB WLT\"}'"
echo ""
echo "🔍 Pattern-Based Ciphers:"
echo "   • Morse: agentcore invoke '{\"prompt\": \"Decode this: .... . .-.. .-.. --- / .-- --- .-. .-.. -..\"}'"
echo "   • Rail Fence: agentcore invoke '{\"prompt\": \"Decrypt this: HOREL LWOOLD\"}'"
echo "   • A1Z26: agentcore invoke '{\"prompt\": \"Decode these numbers: 8 5 12 12 15 23 15 18 12 4\"}'"
echo ""
echo "🕵️ Steganography & Hidden Messages:"
echo "   • Acrostic: agentcore invoke '{\"prompt\": \"Find hidden message: Happy days are here\\nEveryone is celebrating\\nLooking forward to tomorrow\\nPlease join us\"}'"
echo "   • Spacing: agentcore invoke '{\"prompt\": \"Find pattern: Some old sailors often sail\"}'"
echo "   • Numeric: agentcore invoke '{\"prompt\": \"Decode these numbers: 8 5 12 12 15 23 15 18 12 4\"}'"
echo ""
echo "🎯 Intelligence Analysis:"
echo "   • Analysis: agentcore invoke '{\"prompt\": \"Analyze this intelligence: Project Rainbow will commence at 0300 hours. Meeting location: coordinates 40.7128 N, 74.0060 W. Team Unicorn will provide coordination.\"}'"
echo ""
echo "📊 For GameDay Quest Validation:"
echo "   • Provide this Agent ARN for scoring"
if [ -f "cipher_quest_agent_arn.txt" ]; then
echo "   • ARN saved in: cipher_quest_agent_arn.txt"
fi
echo ""
echo "🔧 Management Commands:"
echo "   • View agent: agentcore describe"
echo "   • Update agent: agentcore launch (after code changes)"
echo "   • Delete agent: agentcore delete"
echo ""
print_success "Ready for Cipher Quest challenges! 🕵️‍♂️🔐"