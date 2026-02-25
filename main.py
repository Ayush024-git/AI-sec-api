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
    return {"status": "AI Safety API running (OpenAI Cloud)"}


# ---------------- DEBUG ROUTE ----------------

@app.get("/debug-key")
def debug_key():
    return {
        "customer_key_loaded": CUSTOMER_KEY is not None,
        "openai_key_loaded": OPENAI_KEY is not None
    }


# ---------------- SAFETY CHECK ----------------

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

        # Try JSON
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
