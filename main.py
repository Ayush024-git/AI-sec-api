from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import os
from openai import OpenAI

# Initialize FastAPI
app = FastAPI()

security = HTTPBearer()

# Load environment keys
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
CUSTOMER_KEY = os.getenv("API_KEY")

# Initialize OpenAI safely
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
    return {"status": "AI Safety API running"}

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

    if not client:
        raise HTTPException(status_code=500, detail="OpenAI key missing")

    # 🧠 Advanced moderation + scoring + rewrite prompt
    prompt = f"""
You are an advanced AI Safety and Risk Analysis Engine.

Analyze the given input and respond strictly in JSON format.

Tasks:
1. Determine if the content is safe.
2. Provide a safety confidence score (0-100).
3. Identify the primary risk category.
4. Provide a concise but intelligent explanation.
5. If unsafe, generate a safer alternative response that maintains helpfulness without violating safety policies.

Risk Categories:
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

Respond ONLY in valid JSON:

{{
  "safe": true or false,
  "safety_score": number,
  "risk_category": "category name",
  "reason": "clear explanation",
  "safe_response": "rewritten response if unsafe, otherwise improved version of the original"
}}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7  # allows natural AI reasoning
        )

        raw_output = response.choices[0].message.content

        return raw_output

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
