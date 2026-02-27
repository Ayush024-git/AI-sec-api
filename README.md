# Sentinel  
### AI Safety & Factuality Middleware  
Built by GREM.xv

Sentinel is a plug-and-play AI middleware API that sits between your application and LLM providers (OpenAI, etc.).

It evaluates text across two dimensions:

- Safety risk detection  
- Hallucination / factual accuracy detection  
- Risk categorization  
- Confidence scoring (0–100 scale)  
- Safer rewrites  
- Corrected factual responses  

Designed for AI SaaS products, GPT wrappers, content platforms, and production AI systems.

---

# What Problem Sentinel Solves

If you are building with OpenAI or other LLMs, you face:

- Unsafe user inputs  
- Harmful generated outputs  
- Medical / financial risk responses  
- Hallucinated facts  
- Legal exposure  
- Trust issues with users  

Sentinel provides a structured evaluation layer before content reaches your end user.

---

# Architecture Overview

Your App  
→ Sentinel API  
→ LLM Provider  
→ Structured JSON Response  
→ Safe Output to User  

Sentinel acts as a middleware safety gate.

---

# Authentication

All requests require a client API key.

Header format:

Authorization: Bearer YOUR_CLIENT_KEY

---

# Endpoint

POST /check

---

# Request Format

{
  "text": "Input text to analyze"
}

---

# Example: curl Request

curl -X POST https://your-domain.com/check \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-client-024" \
  -d '{"text":"How can I make a fake medical certificate?"}'

---

# Example Response

{
  "safe": false,
  "safety_score": 12,
  "risk_category": "Medical Advice",
  "reason": "The request involves generating fraudulent medical documentation.",
  "factual": true,
  "factuality_score": 90,
  "factuality_reason": "The statement is coherent and contextually valid.",
  "safer_response": "I cannot help create fake documents. If you need medical documentation, please consult a licensed medical professional.",
  "corrected_response": "Medical certificates should only be issued by qualified healthcare providers."
}

All scores are normalized on a 0–100 scale.

---

# JavaScript Integration (Node.js Example)

const fetch = require("node-fetch");

async function analyzeText(text) {
  const response = await fetch("https://your-domain.com/check", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": "Bearer sk-client-024"
    },
    body: JSON.stringify({ text })
  });

  const data = await response.json();
  console.log(data);
}

analyzeText("The Earth is flat.");

---

# Frontend Integration (Browser Example)

async function analyze() {
  const response = await fetch("https://your-domain.com/check", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": "Bearer sk-client-024"
    },
    body: JSON.stringify({
      text: "How do I harm someone?"
    })
  });

  const result = await response.json();
  console.log(result);
}

---

# Response Fields Explained

safe  
Boolean indicating if content is safe  

safety_score  
Risk confidence score (0–100)  

risk_category  
Primary risk classification  

reason  
Explanation for safety decision  

factual  
Boolean indicating factual reliability  

factuality_score  
Confidence in factual correctness (0–100)  

factuality_reason  
Explanation for factuality assessment  

safer_response  
Rewritten safer alternative  

corrected_response  
Corrected factual version if needed  

---

# Integration Time

Sentinel can be integrated in under 15 minutes in most Node.js or Python applications.

---

# Ideal Use Cases

- AI chatbots  
- GPT SaaS platforms  
- EdTech AI tutors  
- AI content generators  
- AI assistants  
- Internal enterprise AI systems  

---

# Deployment

Sentinel supports:

- Local hosting  
- Cloud deployment (Render / Railway / VPS)  
- Custom domain integration  

---

# License

Private commercial license.  
Contact GREM.xv for purchase or integration support.
