# 🧬 RareDx — Medical Intelligence Platform & Rare Disease Diagnostic Engine

> A production-grade clinical decision support system that accepts natural language patient symptoms or PDF lab reports, and returns ranked rare disease differential diagnoses with Explainable AI (XAI), confidence scoring, personalized recommendations, and interactive knowledge graphs.

![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python)
![FAISS](https://img.shields.io/badge/FAISS-Vector_DB-orange?style=flat-square)
![Groq](https://img.shields.io/badge/Groq-LLaMA_3.1_8B-green?style=flat-square)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-red?style=flat-square&logo=streamlit)
![PyMuPDF](https://img.shields.io/badge/OCR-PyMuPDF-yellow?style=flat-square)
![PyVis](https://img.shields.io/badge/Graph-PyVis-purple?style=flat-square)
![Accuracy](https://img.shields.io/badge/Top--1_Accuracy-93%25-brightgreen?style=flat-square)

---

## 📌 Overview

RareDx goes beyond simple RAG by functioning as an end-to-end medical intelligence platform. Designed for rare disease diagnosis support, it leverages a knowledge base of **1,500 Orphanet-sourced rare diseases**. 

Built to demonstrate real-world AI engineering, it features a complete pipeline with semantic caching, hybrid scoring (vector + keyword), Explainable AI (XAI), automated NLP symptom extraction, and a production-quality multi-page UI.

---

## ✨ Key Features (Platform Capabilities)

- **🧠 NLP & OCR Input**: Type natural language clinical stories, or upload PDF lab reports. The system automatically extracts structured symptoms and lab findings.
- **🧬 Hybrid RAG Diagnostic Engine**: Combines FAISS vector retrieval with keyword overlap scoring and LLaMA-based clinical reasoning to output Top 3 differential diagnoses.
- **🔍 Explainable AI (XAI)**: Demystifies AI predictions by visualizing exactly which symptoms and lab results drove the diagnosis via interactive weight charts and matched/unmatched signal tags.
- **💬 Medical Chatbot Assistant**: A dedicated, context-aware chatbot capable of answering questions in both "Patient Mode" (simple language) and "Doctor Mode" (clinical/technical language).
- **🕸️ Interactive Knowledge Graph**: Visualizes the complex web of diseases, symptoms, and inheritance patterns using PyVis network physics.
- **📋 Personalized Action Plans**: Auto-generates specialist recommendations, required confirmatory tests, and management advice (including automatic "Prevention" banners for manageable metabolic diseases).
- **📥 PDF Report Generation**: Instantly compiles the diagnostic run, XAI breakdown, and recommendations into a formatted, downloadable PDF for sharing.

---

## 🏗️ System Architecture

```text
Natural Language / PDF Lab Report
            │
            ▼ (PyMuPDF + Groq NLP Extractor)
    Structured Symptoms & Labs
            │
            ▼
┌─────────────────────────┐
│  Sentence Embedder      │  all-MiniLM-L6-v2 (384-dim vectors)
└──────────┬──────────────┘
            │
            ▼
┌─────────────────────────┐
│  FAISS Index            │  IndexFlatL2 — searches 1,500 diseases
└──────────┬──────────────┘
            │ (Top 10 candidates)
            ▼
┌─────────────────────────┐
│  Hybrid Ranker          │  Retrieval Similarity + Symptom Overlap
└──────────┬──────────────┘
            │ (Top 5 candidates)
            ▼
┌─────────────────────────┐
│  Groq LLM Reasoner      │  Clinical ranking & reasoning
└──────────┬──────────────┘
            │
            ▼
┌─────────────────────────┐
│ Explainable AI Engine   │  Generates symptom weights & match logic
└──────────┬──────────────┘
            ▼
    Top 3 Diseases + XAI Visuals + Downloadable PDF
```

---

## 📊 Evaluation Results

Evaluated on **100 test cases** generated from the knowledge base, each query tested against all 1,500 diseases.

| Metric | Score |
|---|---|
| **Top-1 Accuracy** | **93.0%** (93/100) |
| **Top-3 Accuracy** | **95.0%** (95/100) |
| Knowledge Base Size | 1,500 diseases |

*Scaling the knowledge base from 50 to 1,500 diseases improved Top-1 accuracy by 18% due to a richer, more discriminative semantic embedding space.*

---

## 🗂️ Dataset Details

- **Source**: Orphanet XML exports (`en_product4.xml`, `en_product9_ages.xml`)
- **Format**: Structured JSON with fields: `disease_id`, `orpha_id`, `name`, `key_symptoms`, `lab_findings`, `age_of_onset`, `inheritance`, `clinical_summary`.

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| **Language** | Python 3.11 |
| **Embeddings** | `sentence-transformers` (`all-MiniLM-L6-v2`) |
| **Vector DB** | `faiss-cpu` (IndexFlatL2) |
| **LLM & Chatbot** | Groq API (`llama-3.1-8b-instant`) |
| **Frontend/UI** | Streamlit (Multi-page app architecture) |
| **Data Viz** | Plotly (Gauges/Charts), PyVis & NetworkX (Graphs) |
| **OCR/PDF** | PyMuPDF (reading), fpdf2 (writing) |

---

## 📁 Project Structure

```text
rare_disease_rag/
├── data/                           ← Orphanet XMLs & compiled 1,500 disease JSON
├── embeddings/                     ← FAISS index & metadata
├── pages/
│   ├── 1_💬_AI_Chatbot.py          ← Mode-aware medical chatbot
│   ├── 2_🔬_Disease_Library.py     ← Searchable 1,500 disease dictionary
│   └── 3_📚_Learn_Rare_Diseases.py ← Interactive PyVis graph & awareness blog
├── src/
│   ├── shared.py                   ← Global design system & session state
│   ├── pipeline.py                 ← Core Hybrid RAG logic
│   ├── nlp_extractor.py            ← Natural language to JSON parsing + XAI
│   ├── chatbot.py                  ← Patient/Doctor mode prompts
│   ├── report_generator.py         ← fpdf2 layout builder
│   └── knowledge_graph.py          ← Network graph physics builder
├── streamlit_app.py                ← Main diagnostic engine & entry point
└── requirements.txt
```

---

## ⚙️ Setup & Installation

### 1. Clone & Setup Environment
```bash
git clone https://github.com/Sainath-777/rare-disease-prediction-using-rag.git
cd rare-disease-prediction-using-rag
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Set up API key
Create a `.env` file in the project root:
```
GROQ_API_KEY=your_groq_api_key_here
```
*(Get a free, ultra-fast Groq API key at [console.groq.com](https://console.groq.com))*

### 3. Run the Platform
```bash
streamlit run streamlit_app.py
```

---

## ⚠️ Disclaimer

This system is a **research prototype** built for academic and portfolio purposes. It is not validated for clinical use and must not be used to make real medical decisions. Always consult qualified medical professionals for diagnosis and treatment.
