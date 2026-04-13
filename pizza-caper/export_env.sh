#!/bin/bash

# Get runtime URLs for both agents
echo "Getting agent runtime URLs..."

# Get location agent ARN
LOCATION_ARN="{TODO}"

# Get orders agent ARN  
ORDERS_ARN="{TODO}"

# Get detective agent ARN
DETECTIVE_ARN="{TODO}"

# Get fresh bearer token
# BEARER_TOKEN=$(./refresh_token.sh your_client_id testuser Permpassw0rd)
BEARER_TOKEN="{TODO}"

# Set environment variables
export LOCATION_AGENT_ARN="$LOCATION_ARN"
export ORDERS_AGENT_ARN="$ORDERS_ARN"
export DETECTIVE_AGENT_ARN="$DETECTIVE_ARN"
export AWS_REGION="us-east-1"
export BEARER_TOKEN="$BEARER_TOKEN"
# Get account ID for unique bucket name
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
export EVIDENCE_BUCKET="pizza-images-$ACCOUNT_ID"
export PLACE_INDEX_NAME="PizzaPlaceIndex"
export ROUTE_CALCULATOR_NAME="PizzaRouteCalculator"

# You need to set your bearer token manually
echo ""
echo "Environment variables set:"
echo "LOCATION_AGENT_ARN=$LOCATION_AGENT_ARN"
echo "ORDERS_AGENT_ARN=$ORDERS_AGENT_ARN"
echo "DETECTIVE_AGENT_ARN=$DETECTIVE_AGENT_ARN"
echo "AWS_REGION=$AWS_REGION"
echo "BEARER_TOKEN=$BEARER_TOKEN"
echo "EVIDENCE_BUCKET=$EVIDENCE_BUCKET"
echo "PLACE_INDEX_NAME=$PLACE_INDEX_NAME"
echo "ROUTE_CALCULATOR_NAME=$ROUTE_CALCULATOR_NAME"

