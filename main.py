from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import os
from openai import OpenAI

# Initialize FastAPI
app = FastAPI()

# Initialize OpenAI client
key = os.getenv("OPEN_API_KEY")

if key:
    client = OpenAI(api_key=key)
else:
    client=none
# Input schema
class Input(BaseModel):
    text: str

# Root check
@app.get("/")
def root():
    return {"status": "AI Safety API running"}

# Safety check endpoint
@app.post("/check")
def check(input: Input, authorization: str = Header(None)):

    # 🔐 API key protection (your customer key)
    if authorization != f"Bearer {os.getenv('API_KEY')}":
        raise HTTPException(status_code=401, detail="Unauthorized")

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

    return result
