from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from openai import OpenAI
import os
import json
import sqlite3

# ---------------- INIT ----------------

app = FastAPI()
security = HTTPBearer()
templates = Jinja2Templates(directory="templates")

# ---------------- DATABASE SETUP ----------------

conn = sqlite3.connect("logs.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    input TEXT,
    safe BOOLEAN,
    safety_score INTEGER,
    factual BOOLEAN,
    factuality_score INTEGER
)
""")
conn.commit()

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

# ---------------- HEALTH ----------------

@app.get("/health")
def health():
    return {"status": "AI Safety + Factuality API running (OpenAI Cloud)"}

# ---------------- API: GET LOGS ----------------

@app.get("/api/logs")
def get_logs():
    cursor.execute("SELECT * FROM logs ORDER BY id DESC")
    rows = cursor.fetchall()

    return [
        {
            "id": r[0],
            "input": r[1],
            "safe": r[2],
            "safety_score": r[3],
            "factual": r[4],
            "factuality_score": r[5]
        }
        for r in rows
    ]

# ---------------- API: GET STATS ----------------

@app.get("/api/stats")
def get_stats():
    cursor.execute("SELECT COUNT(*) FROM logs")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM logs WHERE safe = 1")
    safe_count = cursor.fetchone()[0]

    unsafe_count = total - safe_count

    return {
        "total_requests": total,
        "safe_count": safe_count,
        "unsafe_count": unsafe_count,
        "safe_percentage": round((safe_count / total) * 100, 2) if total > 0 else 0
    }

# ---------------- CHECK ENDPOINT ----------------

@app.post("/check")
def check(
    input: Input,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    # 🔐 Auth
    if not CUSTOMER_KEY:
        raise HTTPException(status_code=500, detail="Server API_KEY not set")

    if credentials.credentials != CUSTOMER_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if not client:
        raise HTTPException(status_code=500, detail="OpenAI key missing")

    # 🧠 Prompt
    prompt = f"""
You are an AI Safety and Factuality Evaluation Engine.

Analyze the text on TWO dimensions:

SAFETY:
- safe (true/false)
- safety_score (0–100)
- risk_category
- reason

FACTUALITY:
- factual (true/false)
- factuality_score (0–100)
- factuality_reason

If unsafe → generate safer_response.
If non-factual → generate corrected_response.

Return STRICT JSON only.

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

            # Save to DB
            cursor.execute("""
            INSERT INTO logs (input, safe, safety_score, factual, factuality_score)
            VALUES (?, ?, ?, ?, ?)
            """, (
                input.text,
                parsed.get("safe"),
                parsed.get("safety_score"),
                parsed.get("factual"),
                parsed.get("factuality_score")
            ))
            conn.commit()

            return parsed

        except json.JSONDecodeError:
            return {
                "error": "Model did not return valid JSON",
                "raw_output": raw_output
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
