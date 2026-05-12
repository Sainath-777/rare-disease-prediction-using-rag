"""
src/knowledge_graph.py — Disease knowledge graph builder using PyVis + NetworkX
Creates interactive HTML network graphs for disease-symptom-inheritance relationships.
"""

import json
import os
import re
import networkx as nx
from pyvis.network import Network


BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE, "data", "diseases_final.json")

# Category keywords for auto-classification
CATEGORY_KEYWORDS = {
    "Metabolic Disorders": [
        "metabolic", "amino acid", "organic acid", "fatty acid", "pku", "phenylketonuria",
        "galactosemia", "mcad", "maple syrup", "homocystinuria", "tyrosinemia",
        "glycogen storage", "gluconeogenesis", "pyruvate", "acylcarnitine"
    ],
    "Mitochondrial Disorders": [
        "mitochondrial", "melas", "merrf", "leigh", "lactic acidosis", "oxidative phosphorylation",
        "respiratory chain", "mtdna", "ragged red", "complex i", "complex ii", "complex iii",
        "complex iv", "atp synthase", "coenzyme q"
    ],
    "Lysosomal Storage Disorders": [
        "lysosomal", "gaucher", "niemann-pick", "fabry", "pompe", "mucopolysaccharidosis",
        "mps", "sphingolipid", "enzyme replacement", "cherry red macula", "hepatosplenomegaly",
        "storage", "gangliosidosis", "krabbe", "metachromatic leukodystrophy"
    ],
    "Urea Cycle Disorders": [
        "urea cycle", "hyperammonemia", "ornithine", "citrulline", "arginine", "argininosuccinate",
        "carbamoyl phosphate", "otc", "nags", "olt", "urea cycle disorder", "citrullinemia",
        "arginase", "ast1"
    ],
    "Peroxisomal Disorders": [
        "peroxisomal", "zellweger", "adrenoleukodystrophy", "ald", "vlcfa", "very long chain",
        "phytanic acid", "refsum", "pex", "peroxisome biogenesis"
    ],
    "Neurodegenerative Disorders": [
        "neurodegeneration", "ataxia", "spinal muscular atrophy", "sma", "huntington",
        "alzheimer", "parkinson", "als", "prion", "progressive", "dementia", "cerebellar"
    ],
}


def classify_disease(disease: dict) -> str:
    """Auto-classify a disease into a category based on keywords."""
    text = (
        disease.get("clinical_summary", "") + " " +
        disease.get("name", "") + " " +
        " ".join(disease.get("key_symptoms", [])) + " " +
        " ".join(disease.get("lab_findings", []))
    ).lower()

    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            return category

    return "Other Rare Diseases"


def load_diseases() -> list:
    """Load and classify all diseases."""
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        diseases = json.load(f)
    for d in diseases:
        if not d.get("category"):
            d["category"] = classify_disease(d)
    return diseases


def get_categorized_diseases() -> dict:
    """Return diseases grouped by category."""
    diseases = load_diseases()
    categorized = {}
    for d in diseases:
        cat = d.get("category", "Other Rare Diseases")
        categorized.setdefault(cat, []).append(d)
    return categorized


def build_disease_graph(diseases: list, max_diseases: int = 30, max_symptoms: int = 5) -> str:
    """
    Build an interactive PyVis knowledge graph.

    Nodes: diseases (blue), symptoms (cyan), inheritance (purple)
    Edges: disease-symptom, disease-inheritance

    Returns: HTML string for rendering in Streamlit.
    """
    net = Network(
        height="600px",
        width="100%",
        bgcolor="#070d14",
        font_color="#e2eaf4",
        directed=False,
    )
    net.set_options("""
    {
        "nodes": {
            "borderWidth": 2,
            "shadow": true
        },
        "edges": {
            "smooth": {"type": "continuous"},
            "shadow": false
        },
        "physics": {
            "barnesHut": {
                "gravitationalConstant": -8000,
                "centralGravity": 0.3,
                "springLength": 120,
                "springConstant": 0.04,
                "damping": 0.09
            },
            "minVelocity": 0.75
        },
        "interaction": {
            "hover": true,
            "tooltipDelay": 100
        }
    }
    """)

    G = nx.Graph()
    added_symptoms = set()
    added_inheritances = set()

    sample = diseases[:max_diseases]

    for d in sample:
        disease_id = d["name"]
        cat = d.get("category", "Other")

        # Disease node
        G.add_node(disease_id, type="disease", category=cat)
        net.add_node(
            disease_id,
            label=disease_id[:25],
            title=f"<b>{disease_id}</b><br>Category: {cat}<br>Onset: {d.get('age_of_onset','?')}",
            color="#38bdf8",
            size=18,
            shape="dot",
            font={"size": 11},
        )

        # Symptom nodes
        for sym in d.get("key_symptoms", [])[:max_symptoms]:
            sym_clean = sym.strip()
            if not sym_clean:
                continue
            G.add_edge(disease_id, sym_clean)
            if sym_clean not in added_symptoms:
                net.add_node(
                    sym_clean,
                    label=sym_clean[:20],
                    title=f"Symptom: {sym_clean}",
                    color="#7dd3fc",
                    size=12,
                    shape="diamond",
                    font={"size": 9},
                )
                added_symptoms.add(sym_clean)
            net.add_edge(disease_id, sym_clean, color="rgba(56,189,248,0.3)", width=1)

        # Inheritance node
        inh = d.get("inheritance", "Unknown")
        if inh and inh != "Unknown":
            # Simplify inheritance label
            inh_short = inh.split(",")[0].strip()
            G.add_edge(disease_id, inh_short)
            if inh_short not in added_inheritances:
                net.add_node(
                    inh_short,
                    label=inh_short[:25],
                    title=f"Inheritance: {inh_short}",
                    color="#a78bfa",
                    size=14,
                    shape="triangle",
                    font={"size": 10},
                )
                added_inheritances.add(inh_short)
            net.add_edge(disease_id, inh_short, color="rgba(167,139,250,0.3)", width=1.5)

    return net.generate_html()


def build_symptom_disease_graph(symptom_list: list, all_diseases: list, top_n: int = 15) -> str:
    """
    Build a focused graph centered on specific symptoms.
    Shows which diseases share these symptoms.
    """
    symptom_lower = [s.lower() for s in symptom_list]

    matching_diseases = []
    for d in all_diseases:
        d_syms = [s.lower() for s in d.get("key_symptoms", [])]
        if any(s in " ".join(d_syms) for s in symptom_lower):
            matching_diseases.append(d)

    return build_disease_graph(matching_diseases[:top_n], max_diseases=top_n)
