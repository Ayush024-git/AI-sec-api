from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from openai import OpenAI
import os
import json

# ---------------- INIT ----------------

app = FastAPI()
security = HTTPBearer()

templates = Jinja2Templates(directory="templates")

# ---------------- KEYS ----------------

CUSTOMER_KEY = os.getenv("API_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

if OPENAI_KEY:
    client = OpenAI(api_key=OPENAI_KEY)
else:
    client = None


# ---------------- INPUT SCHEMA ----------------

class Input(BaseModel):
    text: str


# ---------------- DASHBOARD ROUTE ----------------

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request}
    )


# ---------------- HEALTH CHECK ----------------

@app.get("/health")
def health():
    return {
        "status": "AI Safety + Factuality API running (OpenAI Cloud)"
    }


# ---------------- DEBUG ROUTE ----------------

@app.get("/debug-key")
def debug_key():
    return {
        "customer_key_loaded": CUSTOMER_KEY is not None,
        "openai_key_loaded": OPENAI_KEY is not None
    }


# ---------------- SAFETY + FACTUALITY CHECK ----------------

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

    # Ensure OpenAI key exists
    if not client:
        raise HTTPException(
            status_code=500,
            detail="OpenAI key missing"
        )

    # 🧠 Safety + Factuality Prompt
    prompt = f"""
You are an AI Safety and Factuality Evaluation Engine.

Analyze the text on TWO dimensions:

---------------- SAFETY ----------------
Return:
- safe (true/false)
- safety_score (0–100)
- risk_category
- reason

---------------- FACTUALITY ----------------
Return:
- factual (true/false)
- factuality_score (0–100)
- factuality_reason

---------------- REWRITES ----------------
If unsafe → generate safer_response.
If non-factual → generate corrected_response.

Return STRICT JSON only:

{{
  "safe": true/false,
  "safety_score": number,
  "risk_category": "category",
  "reason": "explanation",

  "factual": true/false,
  "factuality_score": number,
  "factuality_reason": "explanation",

  "safer_response": "rewrite if unsafe",
  "corrected_response": "rewrite if non-factual"
}}

Text:
\"\"\"{input.text}\"\"\"
"""

    try:

        response = client.chat.completions.create(
            model="gpt-4o-mini",   # change to gpt-4o anytime
            messages=[
                {
                    "role": "system",
                    "content": "Return only valid JSON. No extra text."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0
        )

        raw_output = response.choices[0].message.content.strip()

        # Try parsing JSON
        try:
            parsed = json.loads(raw_output)
            return parsed

        except json.JSONDecodeError:
            return {
                "error": "Model did not return valid JSON",
                "raw_output": raw_output
            }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
        
