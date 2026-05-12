"""
src/chatbot.py — Groq-powered medical awareness chatbot
Supports patient mode (simple language) and doctor mode (technical).
"""

import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

PATIENT_SYSTEM = """You are RareDx Assistant, a friendly medical awareness chatbot specializing in rare diseases.

Your role:
- Explain rare diseases in simple, easy-to-understand language (avoid medical jargon)
- Give practical prevention and management tips
- Answer FAQ about rare diseases, newborn screening, genetic counseling
- Help users understand lab reports in plain language
- Always remind users to consult a qualified medical professional
-Never explain anything that isn't releated to mdecine or biochemistry.

Tone: warm, empathetic, supportive. Use bullet points for clarity. Keep answers concise (under 250 words unless asked to elaborate).
Always end responses with: "💙 Remember: Always consult a qualified medical specialist for diagnosis and treatment."
"""

DOCTOR_SYSTEM = """You are RareDx Clinical Assistant, an advanced medical AI for healthcare professionals specializing in rare diseases.

Your role:
- Provide technical, evidence-based information on rare diseases
- Discuss metabolic pathways, genetic mechanisms, enzymatic deficiencies
- Reference diagnostic criteria, lab interpretations, and differential diagnoses
- Discuss treatment protocols, metabolic management, and genetic counseling indications
- Provide information on OMIM IDs, ORPHA codes, and inheritance patterns
-Never explain anything that isn't releated to mdecine or biochemistry.

Tone: concise, precise, clinical. Use medical terminology. Reference specific biochemical pathways when relevant.
"""

EXAMPLE_QA = {
    "What is Phenylketonuria?": "patient",
    "Explain MCAD deficiency prevention": "patient",
    "How does galactosemia affect metabolism?": "doctor",
    "What are the lab findings in urea cycle disorders?": "doctor",
}

def chat_with_groq(messages: list, mode: str = "patient") -> str:
    """
    Stream a response from Groq.
    messages: list of {"role": "user"/"assistant", "content": str}
    mode: "patient" or "doctor"
    Returns the assistant reply as a string.
    """
    system_prompt = PATIENT_SYSTEM if mode == "patient" else DOCTOR_SYSTEM

    full_messages = [{"role": "system", "content": system_prompt}] + messages

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=full_messages,
        temperature=0.4,
        max_tokens=800,
    )

    return response.choices[0].message.content


def explain_disease(disease_name: str, mode: str = "patient") -> str:
    """Quick single-turn disease explanation."""
    if mode == "patient":
        prompt = f"""Explain "{disease_name}" in simple words for a patient or parent.
Cover:
1. What is this disease?
2. What causes it?
3. What are the main symptoms?
4. Can it be prevented or managed?
5. When should I see a doctor urgently?

Keep it friendly and under 300 words."""
    else:
        prompt = f"""Provide a clinical overview of "{disease_name}" for a physician.
Cover:
1. Pathophysiology and enzymatic/genetic defect
2. Key clinical features and age of onset
3. Diagnostic criteria and laboratory findings
4. Differential diagnoses
5. Management and metabolic treatment
6. Genetic counseling considerations

Be concise and technical."""

    messages = [{"role": "user", "content": prompt}]
    return chat_with_groq(messages, mode)


def get_prevention_tips(disease_name: str) -> str:
    """Get prevention and management tips for a disease."""
    prompt = f"""For the rare disease "{disease_name}", provide:
1. Prevention strategies (if applicable)
2. Newborn screening information
3. Dietary or lifestyle management
4. Genetic counseling advice
5. Emergency warning signs to watch for

Format as a clear, actionable list. Patient-friendly language."""
    messages = [{"role": "user", "content": prompt}]
    return chat_with_groq(messages, "patient")


def explain_lab_report(lab_text: str, mode: str = "patient") -> str:
    """Explain extracted lab findings in context."""
    if mode == "patient":
        prompt = f"""A patient has these lab findings:
{lab_text}

Explain what these findings mean in simple language:
1. Which values are abnormal and what does that mean?
2. What rare diseases could these findings suggest?
3. What should the patient do next?

Keep it simple and reassuring."""
    else:
        prompt = f"""Analyze these lab findings clinically:
{lab_text}

Provide:
1. Interpretation of abnormal values
2. Likely metabolic/enzymatic implications
3. Rare disease differential based on the pattern
4. Recommended confirmatory investigations"""

    messages = [{"role": "user", "content": prompt}]
    return chat_with_groq(messages, mode)
