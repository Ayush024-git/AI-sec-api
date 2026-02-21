from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from openai import OpenAI
import os

# Initialize FastAPI
app = FastAPI()

security = HTTPBearer()

# Load environment keys
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
CUSTOMER_KEY = os.getenv("API_KEY")

# Initialize OpenRouter client
client = OpenAI(
    api_key=OPENROUTER_KEY,
    base_url="https://openrouter.ai/api/v1"
)

# Input schema
class Input(BaseModel):
    text: str

# Root health route
@app.get("/")
def root():
    return {"status": "AI Safety API running (OpenRouter)"}

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

    if not OPENROUTER_KEY:
        raise HTTPException(status_code=500, detail="OpenRouter API key missing")

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
        # 🔗 OpenRouter Llama 3 call
        response = client.chat.completions.create(
            model="meta-llama/llama-3-8b-instruct",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        raw_output = response.choices[0].message.content

        return raw_output

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
