from src.retriever import retrieve
from src.llm_ranker import rank_with_groq          # ✅ changed from rank_with_gemini
from src.symptom_matcher import symptom_overlap_score
from src.cache import semantic_cache               # ✅ Added caching layer
import json

def calibrate_confidence(llm_output, retrieved_candidates):

    retrieval_map = {
        d["name"]: d["retrieval_similarity"]
        for d in retrieved_candidates
    }

    calibrated = []

    for item in llm_output["rankings"]:
        name = item["name"]
        llm_conf = item["confidence"] / 100
        retrieval_sim = retrieval_map.get(name, 0)

        final_score = 0.6 * llm_conf + 0.4 * retrieval_sim

        calibrated.append({
            "name": name,
            "original_llm_confidence": item["confidence"],
            "retrieval_similarity": retrieval_sim,
            "hybrid_score_raw": final_score,
            "reasoning": item["reasoning"]
        })

    total = sum(d["hybrid_score_raw"] for d in calibrated)

    for d in calibrated:
        d["final_confidence"] = round(
            (d["hybrid_score_raw"] / total) * 100,
            2
        )

    return calibrated


def run_pipeline(patient_input, use_llm=True):

    # ✅ Step 1: Check Cache (Inference Economics)
    if use_llm:
        cached_result = semantic_cache.get(patient_input)
        if cached_result:
            return cached_result

    candidates = retrieve(patient_input, top_k=10)

    for c in candidates:
        c["symptom_score"] = symptom_overlap_score(patient_input, c)

    for c in candidates:
        retrieval = c["retrieval_similarity"]
        symptom   = c["symptom_score"]
        c["pre_rank_score"] = 0.7 * retrieval + 0.3 * symptom

    candidates = sorted(
        candidates,
        key=lambda x: x["pre_rank_score"],
        reverse=True
    )[:5]

    if not use_llm:
        return candidates

    raw_output = rank_with_groq(patient_input, candidates)  # ✅ changed

    parsed = json.loads(raw_output)

    calibrated = calibrate_confidence(parsed, candidates)

    # ✅ Step 2: Save to Cache for future identical queries
    if use_llm:
        semantic_cache.set(patient_input, calibrated)

    return calibrated


if __name__ == "__main__":

    test_case = """
    Infant with poor feeding, vomiting, lethargy and hyperammonemia.
    """

    results = run_pipeline(test_case)

    print("\nFinal Calibrated Results:\n")
    for r in results:
        print(f"{r['name']} → {r['final_confidence']}%")
        print(f"  Reasoning: {r['reasoning']}\n")