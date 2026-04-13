from strands import tool
import boto3
import json
import base64
import uuid
import os

session = boto3.Session()
region = session.region_name or os.environ.get('AWS_REGION', 'us-east-1')

bedrock_client = boto3.client('bedrock-runtime', region_name=region)
s3_client = boto3.client('s3', region_name=region)

S3_BUCKET = 'gdquests-474c2e25-394a-49f-rainbowvibeteams3bucket-sigp91ckjtkx'

@tool
def image_generator(description: str) -> str:
    """Generate an image using Amazon Nova Canvas and upload to S3"""
    # Use Converse API with Nova Pro which supports image generation
    response = bedrock_client.converse(
        modelId="us.amazon.nova-pro-v1:0",
        messages=[{
            "role": "user",
            "content": [{"text": f"Generate a high quality, photorealistic interior design image of: {description}. Provide a detailed visual description."}]
        }]
    )

    # Extract the text description
    result_text = response['output']['message']['content'][0]['text']

    # Now try Nova Canvas, fall back to description if unavailable
    try:
        body = {
            "taskType": "TEXT_IMAGE",
            "textToImageParams": {"text": description},
            "imageGenerationConfig": {"numberOfImages": 1, "height": 1024, "width": 1024}
        }
        canvas_resp = bedrock_client.invoke_model(
            modelId="amazon.nova-canvas-v1:0",
            body=json.dumps(body)
        )
        canvas_result = json.loads(canvas_resp['body'].read())
        image_data = base64.b64decode(canvas_result['images'][0])

        image_key = f"generated-images/{uuid.uuid4()}.png"
        s3_client.put_object(Bucket=S3_BUCKET, Key=image_key, Body=image_data, ContentType='image/png')
        s3_url = f"https://{S3_BUCKET}.s3.{region}.amazonaws.com/{image_key}"
        return f"Image uploaded to S3: {s3_url}\n\nDesign Description:\n{result_text}"
    except Exception as e:
        return f"Design Description (image model temporarily unavailable):\n{result_text}"
