import streamlit as st
import json
import boto3
import re
from agentcore_a2a_client import AgentCoreA2AClient
import os

# S3 client for image retrieval
s3_client = boto3.client('s3')
sts_client = boto3.client('sts')
account_id = sts_client.get_caller_identity()['Account']
BUCKET_NAME = os.environ.get('EVIDENCE_BUCKET', f'pizza-images-{account_id}')

st.set_page_config(page_title="The Great Pizza Caper", layout="wide")

st.title("The Great Pizza Caper")
st.markdown("Solving the Mystery Through A2A, AgentCore, and Strands Agent Collaboration")

# Create tabs
tab1, tab2 = st.tabs(["🤖 Agent Chat", "📸 Evidence Gallery"])

# Initialize session state
if 'client' not in st.session_state:
    st.session_state.client = AgentCoreA2AClient()

def _get_agent_name(agent_arn: str) -> str:
    """Extract agent name from ARN or discovered agents"""
    if hasattr(st.session_state.client, 'discovered_agents'):
        agent_info = st.session_state.client.discovered_agents.get(agent_arn, {})
        card = agent_info.get('card', {})
        return card.get('name', agent_arn.split('/')[-1] if agent_arn else 'Unknown Agent')
    return agent_arn.split('/')[-1] if agent_arn else 'Unknown Agent'

def extract_response(result):
    """Extract text from agent response"""
    try:
        return result['response']['result']['artifacts'][0]['parts'][0]['text']
    except:
        try:
            return result['result']['artifacts'][0]['parts'][0]['text']
        except:
            try:
                return result['result']['message']['parts'][0]['text']
            except:
                try:
                    return str(result['result'])
                except:
                    return str(result.get('result', result))

with tab1:
    # Configuration section
    st.sidebar.header("🔧 Configuration")

    # Environment variables with defaults
    location_arn = st.sidebar.text_input(
        "Location Agent ARN", 
        value=os.environ.get('LOCATION_AGENT_ARN', ''),
        help="ARN of the deployed Location Agent"
    )

    orders_arn = st.sidebar.text_input(
        "Orders Agent ARN", 
        value=os.environ.get('ORDERS_AGENT_ARN', ''),
        help="ARN of the deployed Orders Agent"
    )

    detective_arn = st.sidebar.text_input(
        "Detective Agent ARN", 
        value=os.environ.get('DETECTIVE_AGENT_ARN', ''),
        help="ARN of the deployed Detective Agent"
    )

    bearer_token = st.sidebar.text_input(
        "Bearer Token", 
        value=os.environ.get('BEARER_TOKEN', ''),
        type="password",
        help="Cognito bearer token for authentication"
    )

    aws_region = st.sidebar.text_input(
        "AWS Region", 
        value=os.environ.get('AWS_REGION', 'us-east-1'),
        help="AWS region where agents are deployed"
    )

    # Agent configuration
    agent_arns = []
    if location_arn:
        agent_arns.append(location_arn)
    if orders_arn:
        agent_arns.append(orders_arn)
    if detective_arn:
        agent_arns.append(detective_arn)

    if not agent_arns:
        st.warning("⚠️ Please configure at least one agent ARN in the sidebar")
        st.stop()

    if not bearer_token:
        st.warning("⚠️ Please provide a bearer token in the sidebar")
        st.stop()

    # Set environment variables for client
    os.environ['BEARER_TOKEN'] = bearer_token
    os.environ['AWS_REGION'] = aws_region

    # Main interface
    st.header("🔍 Ask the Agents")

    # Example queries
    with st.expander("💡 Example Queries"):
        st.markdown("""
        **Multi-Agent Collaboration:**
        - Find the address for CUST_001 and search nearby Pizza Resaurants
        - Which store has highest number of pizza orders? What is the closest pizza restaurant to this store?
        - Get the address for CUST_001 and calculate the distance and best route to the nearest restaurant
        - Get the address of CUST_002 and geocode the address
        - Geocode the location of witness John Doe

        **Single Agent Queries:**
        - Get customer orders for CUST_001
        - Geocode address: 500 110th Ave NE, Bellevue, WA
        - Process all witness statement and evidence images
        - Show all orders in a table"
        - Show a summary of each witness statement and evidence images
        """)

    # Query input
    query = st.text_area(
        "Enter your query:",
        placeholder="Ask about pizza orders, locations, or detective work...",
        height=100
    )

    col1, col2 = st.columns([1, 4])
    with col1:
        submit_button = st.button("🚀 Submit Query", type="primary")

    # Process query
    if submit_button and query:
        with st.spinner("🤖 Processing query through A2A system..."):
            try:
                result = st.session_state.client.auto_route_query(query, agent_arns)
                
                # Display results
                st.success("✅ Query processed successfully!")
                
                # Show agent collaboration flow
                if hasattr(st.session_state.client, 'last_collaboration_flow') and st.session_state.client.last_collaboration_flow:
                    st.subheader("🔄 Agent Collaboration Flow")
                    for i, step in enumerate(st.session_state.client.last_collaboration_flow, 1):
                        agent_name = _get_agent_name(step.get('agent_arn', ''))
                        with st.expander(f"Step {i}: {agent_name}", expanded=True):
                            st.write(f"**Query:** {step.get('query', 'N/A')}")
                            if step.get('response'):
                                response_text = extract_response(step['response'])
                                st.write(f"**Response:** {response_text}")
                
                # Show final result
                st.subheader("🎯 Final Result")
                response_text = extract_response(result)
                st.write(response_text)
                
                # Show images if response contains image filenames, S3 URLs, or S3 folder paths
                s3_urls = re.findall(r's3://[^\s\n]+\.png', response_text)
                s3_folders = re.findall(r's3://[^\s\n]+/', response_text)
                image_files = re.findall(r'\w+\.pdf_page\d+_img\d+\.png', response_text)
                
                if s3_urls or s3_folders or image_files:
                    st.subheader("📸 Extracted Evidence Images")
                    
                    image_paths = []
                    
                    # If we have direct S3 URLs to images, use them
                    if s3_urls:
                        image_paths = s3_urls
                    # If we have S3 folder path, list all images in that folder
                    elif s3_folders:
                        try:
                            folder_path = s3_folders[0]
                            bucket_name = folder_path.split('/')[2]
                            prefix = '/'.join(folder_path.split('/')[3:])
                            
                            # List objects in the folder
                            response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
                            if 'Contents' in response:
                                for obj in response['Contents']:
                                    if obj['Key'].endswith('.png'):
                                        image_paths.append(f"s3://{bucket_name}/{obj['Key']}")
                        except Exception as e:
                            st.error(f"Failed to list images from S3 folder: {str(e)}")
                    # If we have filenames, construct S3 URLs using environment bucket
                    elif image_files:
                        image_paths = [f"s3://{BUCKET_NAME}/evidence/{filename}" for filename in image_files]
                    
                    if image_paths:
                        st.info(f"📊 Found {len(image_paths)} evidence images")
                        
                        # Display images in columns
                        cols = st.columns(2)
                        for i, s3_url in enumerate(image_paths):
                            try:
                                # Parse S3 URL to get bucket and key
                                bucket_name = s3_url.split('/')[2]
                                s3_key = '/'.join(s3_url.split('/')[3:])
                                
                                # Get image from S3
                                response_obj = s3_client.get_object(Bucket=bucket_name, Key=s3_key)
                                image_data = response_obj['Body'].read()
                                
                                # Display image
                                with cols[i % 2]:
                                    st.image(image_data, caption=f"Evidence: {os.path.basename(s3_key)}", width='stretch')
                                    st.text(f"S3 Path: {s3_url}")
                                    
                            except Exception as e:
                                with cols[i % 2]:
                                    st.error(f"Failed to load image {s3_url}: {str(e)}")
                                    st.text(f"S3 Path: {s3_url}")
                    else:
                        st.warning("No images found to display")
                
                # Agent Response
                with st.expander("🔍 Agent Response"):
                    st.json(result)
                    
            except Exception as e:
                st.error(f"❌ Error processing query: {str(e)}")

with tab2:
    st.header("📸 Evidence Gallery")
    st.markdown("All evidence images from the Pizza Caper case")
    
    try:
        # List all images in the evidence folder
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix='evidence/')
        
        if 'Contents' in response:
            image_files = [obj for obj in response['Contents'] if obj['Key'].endswith('.png')]
            
            if image_files:
                st.info(f"📊 Found {len(image_files)} evidence images")
                
                # Display images in a grid
                cols = st.columns(2)
                for i, obj in enumerate(image_files):
                    try:
                        # Get image from S3
                        response_obj = s3_client.get_object(Bucket=BUCKET_NAME, Key=obj['Key'])
                        image_data = response_obj['Body'].read()
                        
                        # Display image
                        with cols[i % 2]:
                            st.image(image_data, caption=f"Evidence: {os.path.basename(obj['Key'])}", width='stretch')
                            st.text(f"S3 Path: s3://{BUCKET_NAME}/{obj['Key']}")
                            st.text(f"Size: {obj['Size']:,} bytes")
                            
                    except Exception as e:
                        with cols[i % 2]:
                            st.error(f"Failed to load {obj['Key']}: {str(e)}")
            else:
                st.warning("No evidence images found in S3")
        else:
            st.warning("Evidence folder not found in S3")
            
    except Exception as e:
        st.error(f"Failed to access S3 bucket: {str(e)}")

# Footer
st.markdown("---")

