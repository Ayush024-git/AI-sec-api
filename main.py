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
        "status": "Sentinel API running (OpenAI Cloud)"
    }


# ---------------- CHECK ----------------

@app.post("/check")
def check(
    input: Input,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    if not CUSTOMER_KEY:
        raise HTTPException(status_code=500, detail="Server API_KEY not set")

    if credentials.credentials != CUSTOMER_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if not client:
        raise HTTPException(status_code=500, detail="OpenAI key missing")

    prompt = f"""
You are an AI Safety and Factuality Evaluation Engine.

Analyze the text and return STRICT JSON only:

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
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        raw_output = response.choices[0].message.content.strip()

        try:
            parsed = json.loads(raw_output)
            return parsed
        except:
            return {
                "error": "Model did not return valid JSON",
                "raw_output": raw_output
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
