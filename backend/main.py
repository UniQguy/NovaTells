import os
import boto3
import json
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load credentials from .env
load_dotenv()

app = FastAPI()

# Allow Flutter to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the Bedrock Runtime client with your credentials
bedrock_runtime = boto3.client(
    service_name='bedrock-runtime',
    region_name="us-east-1",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)

# Configuration for Nova Tells
MODEL_ID = "us.amazon.nova-2-lite-v1:0"
SYSTEM_PROMPT = (
    "You are 'Nova Tells', a specialized Personal Insight Assistant for traders. "
    "Your goal is to analyze stock market charts, trading articles, and financial documents. "
    "1. When given a chart: Identify trends, support/resistance levels, and key indicators. "
    "2. When given an article: Summarize the sentiment (Bullish/Bearish) and list top actionable insights. "
    "3. Tone: Professional and data-driven. "
    "4. Disclaimer: Always remind users this is for educational purposes, not financial advice."
)

@app.get("/")
def read_root():
    return {"status": "Nova Tells Engine is Live"}

@app.post("/ask-nova")
async def ask_nova(prompt: str = Form(...), image: UploadFile = File(None)):
    try:
        content_blocks = []

        # Handle image upload if present
        if image:
            image_bytes = await image.read()
            # Determine format (supports png, jpeg, gif, webp)
            ext = image.filename.split('.')[-1].lower()
            format_map = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png"}
            img_format = format_map.get(ext, "png")

            content_blocks.append({
                "image": {
                    "format": img_format,
                    "source": {"bytes": image_bytes}
                }
            })

        # Add the text prompt
        content_blocks.append({"text": prompt})

        # Call Amazon Nova via the Converse API
        response = bedrock_runtime.converse(
            modelId=MODEL_ID,
            system=[{"text": SYSTEM_PROMPT}],
            messages=[{
                "role": "user",
                "content": content_blocks
            }]
        )

        # Extract the AI's response text
        response_text = response["output"]["message"]["content"][0]["text"]
        return {"response": response_text}

    except Exception as e:
        print(f"Error calling Nova: {e}")
        return {"response": f"Nova is currently updating its charts. Error: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    # 0.0.0.0 allows your phone/emulator to connect to your laptop's IP
    uvicorn.run(app, host="0.0.0.0", port=8000)