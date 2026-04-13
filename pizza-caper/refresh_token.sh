#!/bin/bash
# Usage: ./refresh_token.sh <client_id> <username> <password>
# Example: ./refresh_token.sh {client_id} testuser Permpassw0rd"

if [ $# -ne 3 ]; then
    echo "Usage: $0 <client_id> <username> <password>"
    exit 1
fi

CLIENT_ID="$1"
USERNAME="$2"
PASSWORD="$3"

# Authenticate and get new bearer token
aws cognito-idp initiate-auth \
    --auth-flow USER_PASSWORD_AUTH \
    --client-id "$CLIENT_ID" \
    --auth-parameters USERNAME="$USERNAME",PASSWORD="$PASSWORD" \
    --query 'AuthenticationResult.AccessToken' \
    --output text
