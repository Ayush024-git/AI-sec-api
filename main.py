from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import os
from openai import OpenAI

# Initialize FastAPI
app = FastAPI()

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
def check(input: Input, authorization: str = Header(None)):

    # 🔐 API key protection
    if authorization != f"Bearer {CUSTOMER_KEY}":
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Ensure AI client exists
    if not client:
        raise HTTPException(status_code=500, detail="OpenAI key missing")

    # 🧠 AI moderation prompt
    prompt = f"""
You are an AI safety moderation system.

Classify the following sentence as SAFE or UNSAFE.

Unsafe includes:
- Medical advice
- Self-harm or suicide
- Violence or harm
- Financial risk advice
- Manipulation or misleading claims

Respond ONLY in JSON format:

{{
  "safe": true or false,
  "reason": "short explanation"
}}

Sentence:
{input.text}
"""

    # 🔗 Call AI model
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    # Extract AI output
    result = response.choices[0].message.content
