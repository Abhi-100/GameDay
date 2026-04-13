import streamlit as st
import asyncio
import boto3
from botocore.exceptions import ClientError
from harmony_swarm_agent import swarm

st.set_page_config(page_title="Rainbow Vibe", layout="wide")
st.title(":rainbow[Rainbow Vibe Real Estate Adventure]")

def get_current_region():
    session = boto3.Session()
    return session.region_name

def list_s3_images(bucket_name, region):
    try:
        s3 = boto3.client('s3', region_name=region)
        response = s3.list_objects_v2(Bucket=bucket_name)
        
        if 'Contents' not in response:
            return []
        
        image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')
        images = [obj['Key'] for obj in response['Contents'] 
                 if obj['Key'].lower().endswith(image_extensions)]
        return images
    except ClientError as e:
        st.error(f"Error accessing S3: {e}")
        return []

def get_image_url(bucket_name, key, region):
    s3 = boto3.client('s3', region_name=region)
    try:
        url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': key},
            ExpiresIn=3600
        )
        return url
    except ClientError:
        return None

# Create tabs
tab1, tab2 = st.tabs(["💬 Chat Interface", "🎨 Design Gallery"])

with tab1:
    with st.container():
        user_prompt = st.text_input("Enter your prompt:", key="user_prompt")

        if st.button("Invoke Harmony AgentCore") and user_prompt:
            with st.spinner("Processing..."):
                try:
                    result = asyncio.run(swarm.invoke_async(user_prompt))
                    
                    # Extract final answer from last agent
                    final_answer = ""
                    if result.node_history:
                        last_agent = result.node_history[-1].node_id
                        if last_agent in result.results:
                            node_result = result.results[last_agent]
                            if hasattr(node_result.result, 'message') and 'content' in node_result.result.message:
                                for content in node_result.result.message['content']:
                                    if 'text' in content:
                                        text = content['text']
                                        # Remove thinking tags
                                        if '</thinking>' in text:
                                            text = text.split('</thinking>')[-1].strip()
                                        final_answer = text
                                        break
                    
                    # Display final answer prominently
                    if final_answer:
                        st.success("**Final Answer:**")
                        st.write(final_answer)
                    
                    # Key metrics
                    col1_1, col1_2 = st.columns(2)
                    with col1_1:
                        st.metric("Status", str(result.status).split('.')[-1])
                        st.metric("Agents Used", result.execution_count)
                    with col1_2:
                        st.metric("Execution Time", f"{result.execution_time} ms")
                        st.metric("Total Tokens", result.accumulated_usage.get('totalTokens', 0))

                    # Agent Flow
                    st.subheader("Agent Flow")
                    flow = " → ".join([node.node_id for node in result.node_history])
                    st.write(f"**{flow}**")

                    # All agent responses
                    with st.expander("View All Agent Responses"):
                        for node_id, node_result in result.results.items():
                            st.write(f"**{node_id.replace('_', ' ').title()}:**")
                            if hasattr(node_result.result, 'message') and 'content' in node_result.result.message:
                                for content in node_result.result.message['content']:
                                    if 'text' in content:
                                        text = content['text']
                                        if '</thinking>' in text:
                                            text = text.split('</thinking>')[-1].strip()
                                        st.write(text)
                            st.write("---")
                            
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.info("Enter a prompt to see SwarmResult.")

with tab2:
    with st.container():
        
        region = get_current_region()
        bucket_name = st.text_input("S3 Bucket Name:", key="s3_bucket")
        
        refresh_col1, refresh_col2 = st.columns([1, 1])
        with refresh_col1:
            refresh_images = st.button("🔄 Refresh Images")
        
        if bucket_name and (refresh_images or 'images_loaded' not in st.session_state):
            images = list_s3_images(bucket_name, region)
            st.session_state.images_loaded = True
            st.session_state.current_images = images
            
            if images:
                st.success(f"Found {len(images)} images")
                for i in range(0, len(images), 3):
                    cols = st.columns(3)
                    for j, image_key in enumerate(images[i:i+3]):
                        url = get_image_url(bucket_name, image_key, region)
                        if url:
                            with cols[j]:
                                st.image(url, caption=image_key, width='stretch')
            else:
                st.info("No images found in bucket")
        elif bucket_name and 'current_images' in st.session_state:
            images = st.session_state.current_images
            if images:
                st.success(f"Found {len(images)} images")
                for i in range(0, len(images), 3):
                    cols = st.columns(3)
                    for j, image_key in enumerate(images[i:i+3]):
                        url = get_image_url(bucket_name, image_key, region)
                        if url:
                            with cols[j]:
                                st.image(url, caption=image_key, width='stretch')
