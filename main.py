from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Input(BaseModel):
    text: str

@app.get("/")
def root():
    return {"status": "API running"}

@app.post("/check")
def check(input: Input):
    text = input.text.lower()

    risky_words = ["medicine", "dose", "kill", "suicide"]

    for word in risky_words:
        if word in text:
            return {
                "safe": False,
                "reason": f"Detected risky keyword: {word}"
            }

    return {
        "safe": True,
        "reason": "No obvious risk detected"
    }
