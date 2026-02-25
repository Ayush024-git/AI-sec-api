from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from openai import OpenAI
import os
import json

# Initialize FastAPI
app = FastAPI()

security = HTTPBearer()

# Load environment keys
CUSTOMER_KEY = os.getenv("API_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
if OPENAI_KEY:
    client = OpenAI(api_key=OPENAI_KEY)
else:
    client = None


# Input schema
class Input(BaseModel):
    text: str


# Root health route
@app.get("/")
def root():
    return {"status": "AI Safety API running (OpenAI Cloud)"}


# Debug route
@app.get("/debug-key")
def debug_key():
    return {"loaded_api_key": CUSTOMER_KEY is not None}


# Safety check endpoint
@app.post("/check")
def check(
    input: Input,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    # 🔐 API key protection
    if not CUSTOMER_KEY:
        raise HTTPException(status_code=500, detail="Server API_KEY not set")

    token = credentials.credentials
    if token != CUSTOMER_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Ensure OpenAI key exists
    if not client:
        raise HTTPException(status_code=500, detail="OpenAI key missing")

    # 🧠 Safety prompt
    prompt = f"""
You are an advanced AI Safety Moderation and Response Engine.

Analyze the input text and respond in STRICT JSON ONLY.

Fields required:

safe → true or false  
safety_score → 0–100  
risk_category → category  
reason → explanation  
safe_response → safer rewritten version  

If unsafe → rewrite safely.  
If safe → repeat input politely.

Text:
\"\"\"{input.text}\"\"\"
"""

    try:

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        raw_output = response.choices[0].message.content

        # Try parsing JSON
        try:
            parsed = json.loads(raw_output)
        except:
            parsed = {
                "raw_model_output": raw_output,
                "note": "Model did not return strict JSON"
            }

        return parsed

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
