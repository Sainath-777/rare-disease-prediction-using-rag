# 🧬 RareDx — Rare Disease Diagnostic RAG System

> A production-grade clinical decision support system that accepts patient symptoms and returns ranked rare disease differential diagnoses with confidence scores and clinical reasoning.

![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python)
![FAISS](https://img.shields.io/badge/FAISS-Vector_DB-orange?style=flat-square)
![Groq](https://img.shields.io/badge/Groq-LLaMA_3.3_70B-green?style=flat-square)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-red?style=flat-square&logo=streamlit)
![Langfuse](https://img.shields.io/badge/Observability-Langfuse-purple?style=flat-square)
![RAGAS](https://img.shields.io/badge/Evaluation-RAGAS-yellow?style=flat-square)
![Accuracy](https://img.shields.io/badge/Top--1_Accuracy-93%25-brightgreen?style=flat-square)

---

## 📌 Overview

RareDx is a **Retrieval-Augmented Generation (RAG)** system designed for rare disease diagnosis support. Given a natural language description of patient symptoms and lab findings, the system retrieves the most semantically similar diseases from a knowledge base of **1,500 Orphanet-sourced rare diseases**, applies hybrid ranking, and uses a large language model to produce clinically reasoned differential diagnoses.

This project was built as a graduate final year project demonstrating real-world AI engineering — not a simple demo, but a complete pipeline with evaluation metrics, hybrid scoring, and a production-quality UI.

---

## 🏗️ System Architecture

```
Patient Symptoms (natural language)
            │
            ▼
┌─────────────────────────┐
│  Sentence Embedder       │  all-MiniLM-L6-v2 (384-dim vectors)
│  (all-MiniLM-L6-v2)     │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│  FAISS Index             │  IndexFlatL2 — searches 1,500 diseases
│  (1,500 disease vectors) │  returns Top 10 candidates
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│  Symptom Matcher         │  Keyword overlap scoring
│  (symptom_matcher.py)    │  symptoms + lab findings
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│  Hybrid Ranker           │  0.7 × FAISS similarity
│  (pipeline.py)           │  + 0.3 × symptom overlap
└──────────┬──────────────┘
           │  Top 5 candidates
           ▼
┌─────────────────────────┐
│  Groq LLM                │  llama-3.3-70b-versatile
│  (llm_ranker.py)         │  Constrained clinical reasoning
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│  Confidence Calibration  │  0.6 × LLM confidence
│  (pipeline.py)           │  + 0.4 × retrieval similarity
└──────────┬──────────────┘
           │
           ▼
    Top 3 Diseases
    + Confidence %
    + Clinical Reasoning
```

---

## 📊 Evaluation Results

Evaluated on **100 test cases** generated from the knowledge base, each query tested against all 1,500 diseases.

| Metric | Score |
|---|---|
| **Top-1 Accuracy** | **93.0%** (93/100) |
| **Top-3 Accuracy** | **95.0%** (95/100) |
| Errors | 0 |
| Knowledge Base Size | 1,500 diseases |

### RAGAS Evaluation (Production Metrics)

Evaluated on a random sample of the test set using the RAGAS framework (Groq LLM evaluator) to measure true RAG quality.

| RAGAS Metric | Score | Meaning |
|---|---|---|
| **Context Precision** | **100.0%** (1.000) | FAISS successfully retrieved the correct disease in the top-5 candidates every time. |
| **Faithfulness** | **87.9%** (0.8788) | The LLM reasoning stayed grounded in the retrieved disease data with minimal hallucination. |

### Comparison to Previous Version

| Version | KB Size | Top-1 | Top-3 |
|---|---|---|---|
| v1 (old dataset) | 50 diseases | 75% | 100% |
| **v2 (current)** | **1,500 diseases** | **93%** | **95%** |

Scaling the knowledge base 30× improved Top-1 accuracy by 18 percentage points — because a larger, richer embedding space produces better semantic discrimination between similar diseases.

### Analysis of Failures

The 5 missed cases all involve syndromes with highly overlapping symptom profiles — conditions that would require genetic testing to differentiate even in a clinical setting (e.g., chromosomal deletion syndromes, facial dysostosis variants). These are not retrieval failures — they are genuinely ambiguous clinical presentations.

---

## 🗂️ Dataset

- **Source**: Orphanet XML exports (`en_product4.xml`, `en_product9_ages.xml`)
- **Size**: 1,500 rare diseases
- **Format**: Structured JSON with 7 fields per disease

```json
{
  "disease_id": "RMD0001",
  "orpha_id": "ORPHA58",
  "name": "Alexander disease",
  "key_symptoms": ["Macrocephaly", "Seizure", "Spasticity"],
  "lab_findings": ["Elevated GFAP levels", "Leukodystrophy on MRI"],
  "age_of_onset": "Infantile",
  "inheritance": "Autosomal dominant",
  "clinical_summary": "A rare neurodegenerative disorder..."
}
```

**Field completeness:**
- `disease_id` → RMD0001–RMD1500, clean sequential
- `orpha_id` → original Orphanet reference preserved
- `key_symptoms` → clinical symptoms only (lab terms removed)
- `lab_findings` → filled for 1,493/1,500 diseases (7 have empty lists — handled gracefully)
- `age_of_onset` → from Orphanet XML
- `inheritance` → from Orphanet XML
- `clinical_summary` → generated by Groq LLM from Orphanet data
- `category` → empty (not available in free Orphanet XML)

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3.11 |
| Embeddings | `sentence-transformers` — `all-MiniLM-L6-v2` |
| Vector Database | `faiss-cpu` — IndexFlatL2 |
| LLM Ranking | Groq API — `llama-3.3-70b-versatile` |
| Semantic Caching | In-memory SHA-256 hash cache (Inference Economics) |
| Observability | `langfuse` (100% LLM trace coverage) |
| Evaluation | `ragas` (Context Precision & Faithfulness) |
| UI | Streamlit / Flask |
| API Key Management | `python-dotenv` |

---

## 📁 Project Structure

```
rare_disease_rag/
├── data/
│   ├── diseases_final.json         ← Main knowledge base (1,500 diseases)
│   ├── test_cases.json             ← 100 evaluation cases
│   ├── en_product4.xml             ← Orphanet source XML
│   └── en_product9_ages.xml        ← Orphanet ages XML
│
├── embeddings/
│   ├── faiss_index.bin             ← FAISS index (1,500 vectors × 384 dims)
│   └── metadata.json               ← Disease metadata for result lookup
│
├── src/
│   ├── embedder.py                 ← Builds FAISS index from knowledge base
│   ├── retriever.py                ← Loads index, handles semantic search
│   ├── symptom_matcher.py          ← Keyword overlap scoring
│   ├── pipeline.py                 ← Full pipeline + confidence calibration
│   ├── llm_ranker.py               ← Groq LLM clinical ranking
│   └── evaluate.py                 ← Top-1 / Top-3 accuracy evaluation
│
├── templates/
│   └── index.html                  ← Flask frontend
│
├── static/
│   └── style.css                   ← Flask frontend styles
│
├── app.py                          ← Flask web server
├── app_streamlit.py                ← Streamlit UI
├── requirements.txt
├── .env                            ← API keys (not committed)
├── .gitignore
└── README.md
```

---

## ⚙️ Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/rare-disease-rag.git
cd rare-disease-rag
```

### 2. Create and activate virtual environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install sentence-transformers faiss-cpu numpy tqdm groq python-dotenv streamlit flask
```

### 4. Set up API key

Create a `.env` file in the project root:

```
GROQ_API_KEY=your_groq_api_key_here
```

Get a free Groq API key at [console.groq.com](https://console.groq.com) — 14,400 requests/day on the free tier.

### 5. Build the FAISS index

```bash
python src/embedder.py
```

Expected output:
```
Total diseases loaded: 1500
Embedding shape: (1500, 384)
Vectors in FAISS index: 1500
✅ Phase 2 complete. Embeddings rebuilt for 1500 diseases.
```

---

## 🚀 Running the Application

### Streamlit UI (recommended)

```bash
streamlit run app_streamlit.py
```

Open `http://localhost:8501`

### Flask Web App

```bash
python app.py
```

Open `http://localhost:5000`

---

## 🧪 Running Evaluation

```bash
python src/evaluate.py
```

Each test case prints live with pass/fail status:

```
[001] ✅  GT: Frasier syndrome
[002] ✅  GT: Rabies
[006] ❌  GT: Acrocardiofacial syndrome
          P1: Neurofaciodigitorenal syndrome
...

==================================================
EVALUATION RESULTS
==================================================
Total cases   : 100
Errors skipped: 0
Top-1 Accuracy: 93/100 = 93.0%
Top-3 Accuracy: 95/100 = 95.0%
==================================================
```

---

## 🧠 Key Design Decisions

**Why `all-MiniLM-L6-v2`?**
Lightweight (22MB), fast on CPU, 384-dimensional embeddings, strong semantic similarity performance. Industry-standard choice for local RAG systems. Zero cost.

**Why FAISS `IndexFlatL2`?**
For 1,500 vectors, exact brute-force search is both fast and gives exact results — no approximation error. Approximate methods (IVF, HNSW) are only justified at millions of vectors.

**Why hybrid scoring instead of pure LLM?**
The LLM sees only 5 pre-filtered candidates. Embedding retrieval handles broad semantic matching; symptom overlap scoring adds precise medical signal; LLM adds clinical reasoning. Each layer adds something the others cannot.

**Why Groq + llama-3.3-70b?**
14,400 free requests/day vs Gemini's 20. The 70B model provides significantly better clinical reasoning than smaller models. Groq's custom hardware makes it fast despite the model size.

**Why skip `category` field?**
Empty for all 1,500 diseases — not available in free Orphanet XML. Including a blank field adds noise to embeddings with zero information gain.

---

## 📐 Confidence Score Formula

```
Final Confidence = normalize( 0.6 × LLM_confidence + 0.4 × retrieval_similarity )
```

All three confidence scores are shown in the UI:
- **LLM Confidence** — raw % from Groq reasoning
- **Vector Similarity** — FAISS L2 distance converted to similarity score
- **Hybrid Score** — weighted combination, normalized to sum 100%

---

## ⚠️ Disclaimer

This system is a **research prototype** built for academic purposes. It is not validated for clinical use and must not be used to make real medical decisions. Always consult qualified medical professionals for diagnosis and treatment.

---

## 📄 License

This project is for academic and educational purposes.

---

## 👤 Author

**Sainath**
Graduate AI/ML Project — Rare Disease Diagnostic RAG System
