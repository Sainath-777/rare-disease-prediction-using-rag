"""
src/nlp_extractor.py — NLP-based natural language symptom extraction
Converts free-text patient descriptions into structured symptom lists.
"""

import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


EXTRACTION_SYSTEM = """You are a medical NLP assistant that extracts structured clinical information from natural language patient descriptions.

Extract and return ONLY valid JSON with no extra text."""


def extract_symptoms_from_text(text: str) -> dict:
    """
    Given free-text patient description, extract structured symptoms and findings.

    Returns:
        {
            "symptoms": [...],
            "lab_findings": [...],
            "age_of_onset": "...",
            "clinical_notes": "...",
            "structured_query": "clinical description for RAG search"
        }
    """
    prompt = f"""Extract medical information from this patient description:

"{text}"

Return ONLY this JSON (no markdown, no explanation):
{{
    "symptoms": ["list", "of", "clinical", "symptoms"],
    "lab_findings": ["list", "of", "laboratory", "findings"],
    "age_of_onset": "neonatal/infant/child/adult/unknown",
    "clinical_notes": "brief clinical summary",
    "structured_query": "reformatted clinical description optimized for medical database search"
}}

Rules:
- symptoms: clinical signs only (e.g., "seizures", "hepatomegaly", "lethargy")
- lab_findings: lab values (e.g., "elevated ammonia", "metabolic acidosis", "elevated lactate")
- If information is not mentioned, use empty list [] or "unknown"
- structured_query: combine symptoms + labs into a clinical description"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": EXTRACTION_SYSTEM},
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
        max_tokens=512,
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content
    try:
        return json.loads(content)
    except Exception:
        return {
            "symptoms": [],
            "lab_findings": [],
            "age_of_onset": "unknown",
            "clinical_notes": text,
            "structured_query": text,
        }


def generate_xai_explanation(patient_input: str, results: list) -> dict:
    """
    Generate Explainable AI analysis — why the AI predicted these diseases.
    
    Returns:
        {
            "top_disease": "...",
            "matched_symptoms": [...],
            "matched_labs": [...],
            "confidence_explanation": "...",
            "symptom_weights": {"symptom": weight_0_to_1, ...},
            "uncertainty_note": "..."
        }
    """
    if not results:
        return {}

    top = results[0]
    top2 = results[1] if len(results) > 1 else None
    top3 = results[2] if len(results) > 2 else None

    candidates_text = ""
    for r in results:
        candidates_text += f"\n- {r['name']} ({r['final_confidence']:.1f}%): {r.get('reasoning','')}"

    prompt = f"""Patient input: "{patient_input}"

AI ranked these diseases:
{candidates_text}

Provide an Explainable AI analysis as JSON:
{{
    "matched_symptoms": ["symptoms from patient input that matched top disease"],
    "matched_labs": ["lab findings from patient input that matched top disease"],
    "unmatched_symptoms": ["symptoms mentioned but didn't strongly match"],
    "confidence_explanation": "1-2 sentence plain English explanation of why AI is confident/uncertain",
    "symptom_weights": {{"symptom_name": importance_score_0_to_1}},
    "uncertainty_note": "what additional info would help narrow diagnosis",
    "why_not_others": "brief reason why rank 2 and 3 scored lower than rank 1"
}}"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a clinical AI explainability assistant. Return only valid JSON."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        max_tokens=600,
        response_format={"type": "json_object"},
    )

    try:
        return json.loads(response.choices[0].message.content)
    except Exception:
        return {
            "matched_symptoms": [],
            "matched_labs": [],
            "unmatched_symptoms": [],
            "confidence_explanation": "Analysis unavailable.",
            "symptom_weights": {},
            "uncertainty_note": "",
            "why_not_others": "",
        }


def generate_recommendations(results: list, patient_input: str, mode: str = "patient") -> dict:
    """
    Generate personalized recommendations after diagnosis.
    
    Returns dict with specialist, tests, counseling, urgent_signs, diet_tips
    """
    if not results:
        return {}

    top = results[0]
    top_name = top.get("name", "")

    if mode == "patient":
        prompt = f"""For a patient potentially diagnosed with "{top_name}" (and possibly {results[1]['name'] if len(results) > 1 else 'other conditions'}):

Return JSON:
{{
    "specialist": "recommended medical specialist type",
    "urgency": "routine/urgent/emergency",
    "suggested_tests": ["list of recommended confirmatory tests"],
    "genetic_counseling": true or false,
    "dietary_advice": "brief dietary/lifestyle tip if applicable",
    "newborn_screening": "note about newborn screening if applicable",
    "support_resources": ["patient support organizations or resources"],
    "next_steps": ["ordered list of immediate action steps for patient"]
}}"""
    else:
        prompt = f"""For a clinician evaluating a patient with probable "{top_name}":

Return JSON:
{{
    "specialist": "medical specialist for referral",
    "urgency": "routine/urgent/emergency",
    "suggested_tests": ["confirmatory biochemical/genetic tests"],
    "genetic_counseling": true or false,
    "metabolic_management": "immediate metabolic treatment considerations",
    "monitoring": ["ongoing monitoring parameters"],
    "differential_workup": ["additional differentials to rule out"],
    "next_steps": ["clinical action steps in order"]
}}"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a clinical decision support AI. Return only valid JSON."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        max_tokens=600,
        response_format={"type": "json_object"},
    )

    try:
        return json.loads(response.choices[0].message.content)
    except Exception:
        return {}
