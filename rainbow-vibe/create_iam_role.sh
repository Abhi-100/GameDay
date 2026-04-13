#!/bin/bash

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION=$(aws configure get region)

aws iam create-role \
    --role-name RainbowVibeRole \
    --assume-role-policy-document "{
        \"Version\": \"2012-10-17\",
        \"Statement\": [
            {
                \"Effect\": \"Allow\",
                \"Principal\": {
                    \"Service\": \"ec2.amazonaws.com\"
                },
                \"Action\": \"sts:AssumeRole\"
            },
            {
                \"Sid\": \"AssumeRolePolicy\",
                \"Effect\": \"Allow\",
                \"Principal\": {
                    \"Service\": \"bedrock-agentcore.amazonaws.com\"
                },
                \"Action\": \"sts:AssumeRole\",
                \"Condition\": {
                    \"StringEquals\": {
                        \"aws:SourceAccount\": \"$ACCOUNT_ID\"
                    },
                    \"ArnLike\": {
                        \"aws:SourceArn\": \"arn:aws:bedrock-agentcore:$REGION:$ACCOUNT_ID:*\"
                    }
                }
            }
        ]
    }"

aws iam put-role-policy \
    --role-name RainbowVibeRole \
    --policy-name RainbowVibeExecutionPolicy \
    --policy-document "{
        \"Version\": \"2012-10-17\",
        \"Statement\": [
            {
                \"Sid\": \"ECRImageAccess\",
                \"Effect\": \"Allow\",
                \"Action\": [
                    \"ecr:BatchGetImage\",
                    \"ecr:GetDownloadUrlForLayer\"
                ],
                \"Resource\": [
                    \"arn:aws:ecr:$REGION:$ACCOUNT_ID:repository/*\"
                ]
            },
            {
                \"Effect\": \"Allow\",
                \"Action\": [
                    \"logs:DescribeLogStreams\",
                    \"logs:CreateLogGroup\"
                ],
                \"Resource\": [
                    \"arn:aws:logs:$REGION:$ACCOUNT_ID:log-group:/aws/bedrock-agentcore/runtimes/*\"
                ]
            },
            {
                \"Effect\": \"Allow\",
                \"Action\": [
                    \"logs:DescribeLogGroups\"
                ],
                \"Resource\": [
                    \"arn:aws:logs:$REGION:$ACCOUNT_ID:log-group:*\"
                ]
            },
            {
                \"Effect\": \"Allow\",
                \"Action\": [
                    \"logs:CreateLogStream\",
                    \"logs:PutLogEvents\"
                ],
                \"Resource\": [
                    \"arn:aws:logs:$REGION:$ACCOUNT_ID:log-group:/aws/bedrock-agentcore/runtimes/*:log-stream:*\"
                ]
            },
            {
                \"Sid\": \"ECRTokenAccess\",
                \"Effect\": \"Allow\",
                \"Action\": [
                    \"ecr:GetAuthorizationToken\"
                ],
                \"Resource\": \"*\"
            },
            {
                \"Effect\": \"Allow\",
                \"Action\": [
                    \"xray:PutTraceSegments\",
                    \"xray:PutTelemetryRecords\",
                    \"xray:GetSamplingRules\",
                    \"xray:GetSamplingTargets\"
                ],
                \"Resource\": [
                    \"*\"
                ]
            },
            {
                \"Effect\": \"Allow\",
                \"Resource\": \"*\",
                \"Action\": \"cloudwatch:PutMetricData\",
                \"Condition\": {
                    \"StringEquals\": {
                        \"cloudwatch:namespace\": \"bedrock-agentcore\"
                    }
                }
            },
            {
                \"Sid\": \"GetAgentAccessToken\",
                \"Effect\": \"Allow\",
                \"Action\": [
                    \"bedrock-agentcore:GetWorkloadAccessToken\",
                    \"bedrock-agentcore:GetWorkloadAccessTokenForJWT\",
                    \"bedrock-agentcore:GetWorkloadAccessTokenForUserId\"
                ],
                \"Resource\": [
                    \"arn:aws:bedrock-agentcore:$REGION:$ACCOUNT_ID:workload-identity-directory/default\",
                    \"arn:aws:bedrock-agentcore:$REGION:$ACCOUNT_ID:workload-identity-directory/default/workload-identity/harmony_swarm_agent-*\"
                ]
            },
            {
                \"Sid\": \"BedrockModelInvocation\",
                \"Effect\": \"Allow\",
                \"Action\": [
                    \"bedrock:InvokeModel\",
                    \"bedrock:InvokeModelWithResponseStream\"
                ],
                \"Resource\": [
                    \"arn:aws:bedrock:*::foundation-model/*\",
                    \"arn:aws:bedrock:$REGION:$ACCOUNT_ID:*\"
                ]
            }
        ]
    }"

aws iam attach-role-policy --role-name RainbowVibeRole --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess
aws iam attach-role-policy --role-name RainbowVibeRole --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess
aws iam attach-role-policy --role-name RainbowVibeRole --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
aws iam attach-role-policy --role-name RainbowVibeRole --policy-arn arn:aws:iam::aws:policy/BedrockAgentCoreFullAccess
aws iam attach-role-policy --role-name RainbowVibeRole --policy-arn arn:aws:iam::aws:policy/AmazonBedrockAgentCoreMemoryBedrockModelInferenceExecutionRolePolicy

echo "IAM role 'RainbowVibeRole' created successfully"
