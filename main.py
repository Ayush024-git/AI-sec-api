from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import requests
import os

# Initialize FastAPI
app = FastAPI()

security = HTTPBearer()

# Load client auth key (keep this)
CUSTOMER_KEY = os.getenv("API_KEY")

# Input schema
class Input(BaseModel):
    text: str

# Root health route
@app.get("/")
def root():
    return {"status": "AI Safety API running (Local TinyLlama)"}

# Safety check endpoint
@app.post("/check")
def check(
    input: Input,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    # 🔐 API key protection
    token = credentials.credentials
    if token != CUSTOMER_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # 🧠 Advanced AI Safety Prompt
    prompt = f"""
You are an advanced AI Safety Moderation and Response Engine.

Analyze the input text and respond strictly in JSON format.

Tasks:

1. Determine if the content is SAFE or UNSAFE.
2. Provide a safety confidence score (0–100).
3. Identify the primary risk category.
4. Give a clear reasoning.
5. If unsafe, generate a safer rewritten response that removes harmful elements while preserving helpful intent.

Risk categories include:
- Medical Advice
- Violence / Harm
- Self-Harm
- Financial Advice
- Manipulation
- Misinformation
- Hate / Harassment
- Sexual Content
- Other
- None

Input:
\"\"\"{input.text}\"\"\"

Respond ONLY in JSON like:

{{
  "safe": true or false,
  "safety_score": number,
  "risk_category": "category",
  "reason": "explanation",
  "safe_response": "rewritten safer version"
}}
"""

    try:
        # 🔗 Call TinyLlama locally via Ollama
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "tinyllama",
                "prompt": prompt,
                "stream": False
            }
        )

        raw_output = response.json()["response"]

        return raw_output

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
