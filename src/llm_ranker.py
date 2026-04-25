import os
import json
import time
from groq import Groq
from dotenv import load_dotenv

# ✅ load_dotenv() MUST come before any Langfuse import that
#    auto-initializes a client (like langfuse.decorators)
load_dotenv()

from langfuse import Langfuse

# ── API clients ─────────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in .env file")

client = Groq(api_key=GROQ_API_KEY)

# ✅ Initialized AFTER load_dotenv() — keys are guaranteed to exist
langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_BASE_URL"),
)


def build_prompt(patient_input, candidates):
    candidate_text = ""
    for i, d in enumerate(candidates):
        lab_line = ", ".join(d["lab_findings"]) if d["lab_findings"] else "none documented"
        candidate_text += f"""
Candidate {i+1}:
Name: {d['name']}
Key Symptoms: {', '.join(d['key_symptoms'])}
Lab Findings: {lab_line}
"""

    prompt = f"""You are a clinical reasoning assistant.

Patient case:
{patient_input}

You must choose only from the candidate diseases provided below.
Rank the top 3 most likely diseases.

Rules:
- Only use the provided candidates. Do not invent diseases.
- Base reasoning strictly on symptom and lab overlap with the patient case.
- Confidence percentages must sum to exactly 100.
- Output ONLY valid JSON. No explanation outside the JSON.

Output format:
{{
  "rankings": [
    {{
      "name": "exact disease name from candidates",
      "confidence": <number>,
      "reasoning": "brief clinical reasoning based on overlapping symptoms"
    }}
  ]
}}

Candidates:
{candidate_text}
"""
    return prompt


def rank_with_groq(patient_input, candidates):

    # ── Open a trace for this entire patient query ──────────────
    trace = langfuse.trace(
        name="rare-disease-ranking",
        metadata={
            "candidate_count": len(candidates),
            "candidate_names": [d["name"] for d in candidates],
        },
        tags=["groq", "llama-8b", "raredx"],
    )

    prompt = build_prompt(patient_input, candidates)

    start_time = time.time()

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": "You are a clinical reasoning assistant. Always respond with valid JSON only.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.2,
        max_tokens=1024,
        response_format={"type": "json_object"},
    )

    latency_ms = round((time.time() - start_time) * 1000, 2)
    output_content = response.choices[0].message.content

    # ── Log as a Generation (Langfuse's LLM-specific span type) ─
    # Generation captures token counts natively in the dashboard
    trace.generation(
        name="groq-llm-call",
        model="llama-3.1-8b-instant",
        model_parameters={"temperature": 0.2, "max_tokens": 1024},
        input=prompt,
        output=output_content,
        usage={
            "input":  response.usage.prompt_tokens,
            "output": response.usage.completion_tokens,
            "total":  response.usage.total_tokens,
        },
        metadata={"latency_ms": latency_ms},
    )

    # ── Score: did the LLM return valid JSON? ───────────────────
    try:
        json.loads(output_content)
        trace.score(name="json-parse-success", value=1.0)
    except json.JSONDecodeError:
        trace.score(name="json-parse-success", value=0.0)

    # ── Force-send all pending traces before returning ──────────
    langfuse.flush()

    return output_content
