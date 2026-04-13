import os
import logging
import glob
import re
import boto3
from strands import Agent, tool
from strands.multiagent.a2a import A2AServer
import uvicorn
from fastapi import FastAPI
import PyPDF2
import fitz  # PyMuPDF for image extraction

logging.basicConfig(level=logging.INFO)

# S3 client
s3_client = boto3.client('s3')
sts_client = boto3.client('sts')
account_id = sts_client.get_caller_identity()['Account']
BUCKET_NAME = os.environ.get('EVIDENCE_BUCKET', f'pizza-images-{account_id}')

def extract_entities(text):
    """Extract key entities using regex patterns"""
    entities = {}
    
    # Names (capitalized words)
    names = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
    entities['names'] = list(set(names))
    
    # Times
    times = re.findall(r'\b(?:[01]?[0-9]|2[0-3]):[0-5][0-9](?:\s*[AaPp][Mm])?\b', text)
    entities['times'] = list(set(times))
    
    # Locations/addresses
    locations = re.findall(r'\b\d+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Boulevard|Blvd))\b', text)
    entities['locations'] = list(set(locations))
    
    return entities

@tool
def process_all_witness_statements() -> str:
    """Process all PDF witness statements in the statements folder"""
    statements_dir = 'statements'
    pdf_files = glob.glob(os.path.join(statements_dir, '*.pdf'))
    
    if not pdf_files:
        return "No PDF files found in statements folder"
    
    summaries = []
    extracted_images = []
    
    for pdf_path in pdf_files:
        filename = os.path.basename(pdf_path)
        try:
            # Extract text
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
            
            # Extract entities
            entities = extract_entities(text)
            
            # Extract and save images to S3
            doc = fitz.open(pdf_path)
            image_count = 0
            image_urls = []
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                image_list = page.get_images()
                
                for img_index, img in enumerate(image_list):
                    xref = img[0]
                    pix = fitz.Pixmap(doc, xref)
                    if pix.n - pix.alpha < 4:  # GRAY or RGB
                        img_name = f"{filename}_page{page_num}_img{img_index}.png"
                        img_data = pix.tobytes("png")
                        
                        # Upload to S3
                        try:
                            s3_key = f"evidence/{img_name}"
                            s3_client.put_object(
                                Bucket=BUCKET_NAME,
                                Key=s3_key,
                                Body=img_data,
                                ContentType='image/png'
                            )
                            s3_url = f"s3://{BUCKET_NAME}/{s3_key}"
                            image_urls.append(s3_url)
                            image_count += 1
                        except Exception as e:
                            logging.error(f"Failed to upload {img_name} to S3: {e}")
                        
                    pix = None
            doc.close()
            
            # Summarize witness statement
            lines = [line.strip() for line in text.split('\n') if line.strip() and len(line.strip()) > 10]
            full_text = ' '.join(lines)
            
            # Create detailed summary
            summary = f"""
{filename}:
WITNESS STATEMENT SUMMARY:
{full_text[:500]}...

KEY FINDINGS:
- Names Found: {', '.join(entities['names'][:5])}
- Times Mentioned: {', '.join(entities['times'])}
- Locations: {', '.join(entities['locations'])}
- Images: {image_count} found and uploaded to S3
- Image URLs: {', '.join(image_urls)}
"""
            summaries.append(summary)
            extracted_images.extend(image_urls)
            
        except Exception as e:
            summaries.append(f"{filename}: Error processing - {str(e)}")
    
    result = '\n'.join(summaries)
    if extracted_images:
        result += f"\n\nExtracted Images in S3: {', '.join(extracted_images)}"
    
    return result

# Create detective agent
strands_agent = Agent(
    name="Detective Agent",
    description="Processes all witness statements with entity extraction and image analysis",
    tools={TODO}
)

runtime_url = os.environ.get('AGENTCORE_RUNTIME_URL', 'http://127.0.0.1:9000/')

# Create A2A server
a2a_server = A2AServer(
    {TODO}
)

app = a2a_server.to_fastapi_app()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)
