from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import requests
import os
import json

# Initialize FastAPI
app = FastAPI()

security = HTTPBearer()

# Load client auth key
CUSTOMER_KEY = os.getenv("API_KEY")

# Input schema
class Input(BaseModel):
    text: str

# Root health route
@app.get("/")
def root():
    return {"status": "AI Safety API running (Local TinyLlama)"}

# Debug route (TEMP — remove later)
@app.get("/debug-key")
def debug_key():
    return {"loaded_api_key": CUSTOMER_KEY}

# Safety check endpoint
@app.post("/check")
def check(
    input: Input,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    # 🔐 API key protection
    if not CUSTOMER_KEY:
        raise HTTPException(
            status_code=500,
            detail="Server API_KEY not set"
        )

    token = credentials.credentials
    if token != CUSTOMER_KEY:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized"
        )

    # 🧠 AI Safety Prompt
    prompt = f"""
You are an advanced AI Safety Moderation and Response Engine.

Analyze the input text and respond strictly in JSON format.

Tasks:
1. Determine if the content is SAFE or UNSAFE.
2. Provide a safety confidence score (0–100).
3. Identify the primary risk category.
4. Give reasoning.
5. If unsafe, generate a safer rewritten response.

Input:
\"\"\"{input.text}\"\"\"

Respond ONLY in JSON.
"""

    try:
        # 🔗 Call TinyLlama locally via Ollama
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "tinyllama",
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"Ollama error: {response.text}"
            )

        raw_output = response.json().get("response", "")

        # Try parsing JSON (if model obeys format)
        try:
            parsed = json.loads(raw_output)
            return parsed
        except:
            return {
                "raw_model_output": raw_output,
                "note": "Model did not return strict JSON"
            }

    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=500,
            detail="Ollama not running on localhost:11434"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
