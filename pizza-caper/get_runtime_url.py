#!/usr/bin/env python3
import boto3
import urllib.parse
import sys

def get_runtime_url(agent_runtime_id=None):
    """
    Construct and output AgentCore runtime URL
    
    Args:
        agent_runtime_id: Optional specific runtime ID to get URL for
    
    Returns:
        Runtime URL(s) constructed from ARN(s)
    """
    try:
        client = boto3.client('bedrock-agentcore-control')
        
        if agent_runtime_id:
            runtimes_response = client.list_agent_runtimes()
            runtime = next((r for r in runtimes_response.get('agentRuntimes', []) 
                          if r.get('agentRuntimeId') == agent_runtime_id), None)
            
            if runtime:
                arn = runtime.get('agentRuntimeArn')
                runtime_id = runtime.get('agentRuntimeId')
                if arn:
                    region = arn.split(':')[3]
                    encoded_arn = urllib.parse.quote(arn, safe='')
                    runtime_url = f"https://bedrock-agentcore.{region}.amazonaws.com/runtimes/{encoded_arn}/invocations/"
                    print(f"Runtime ID: {runtime_id}")
                    print(f"ARN: {arn}")
                    print(f"URL: {runtime_url}")
                else:
                    print(f"No ARN found for runtime ID: {agent_runtime_id}")
            else:
                print(f"Runtime not found: {agent_runtime_id}")
        
        else:
            runtimes_response = client.list_agent_runtimes()
            
            for runtime in runtimes_response.get('agentRuntimes', []):
                arn = runtime.get('agentRuntimeArn')
                runtime_id = runtime.get('agentRuntimeId')
                if arn:
                    region = arn.split(':')[3]
                    encoded_arn = urllib.parse.quote(arn, safe='')
                    runtime_url = f"https://bedrock-agentcore.{region}.amazonaws.com/runtimes/{encoded_arn}/invocations/"
                    print(f"Runtime ID: {runtime_id}")
                    print(f"ARN: {arn}")
                    print(f"URL: {runtime_url}")
                    print("---")
                
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)

def main():
    if len(sys.argv) > 1:
        runtime_id = sys.argv[1]
        get_runtime_url(runtime_id)
    else:
        get_runtime_url()

if __name__ == "__main__":
    main()
