"""
src/report_generator.py — PDF report generator using fpdf2
Generates downloadable diagnostic reports.
"""

from fpdf import FPDF
from datetime import datetime
import io


class DiagnosticReport(FPDF):
    """Custom FPDF class for RareDx diagnostic reports."""

    BRAND_R, BRAND_G, BRAND_B = 56, 189, 248   # #38bdf8
    DARK_R, DARK_G, DARK_B   = 7, 13, 20       # #070d14
    GREY_R, GREY_G, GREY_B   = 107, 138, 168   # #6b8aa8

    def header(self):
        # Top accent bar
        self.set_fill_color(self.BRAND_R, self.BRAND_G, self.BRAND_B)
        self.rect(0, 0, 210, 3, "F")

        # Logo area
        self.set_xy(10, 8)
        self.set_font("Helvetica", "B", 18)
        self.set_text_color(self.DARK_R, self.DARK_G, self.DARK_B)
        self.cell(0, 10, "RareDx", ln=False)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(self.GREY_R, self.GREY_G, self.GREY_B)
        self.set_xy(10, 19)
        self.cell(0, 6, "Diagnostic Intelligence System - Confidential Report")

        # Timestamp top-right
        ts = datetime.now().strftime("%Y-%m-%d  %H:%M")
        self.set_font("Helvetica", "", 8)
        self.set_text_color(self.GREY_R, self.GREY_G, self.GREY_B)
        self.set_xy(140, 10)
        self.cell(60, 6, ts, align="R")

        # Separator line
        self.set_draw_color(self.BRAND_R, self.BRAND_G, self.BRAND_B)
        self.set_line_width(0.3)
        self.line(10, 28, 200, 28)
        self.ln(22)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(self.GREY_R, self.GREY_G, self.GREY_B)
        self.cell(0, 10,
                  "Research prototype - academic use only. Not for clinical diagnosis. Consult a qualified medical professional.",
                  align="C")

    def section_title(self, title: str):
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(self.BRAND_R, self.BRAND_G, self.BRAND_B)
        self.set_fill_color(245, 250, 255)
        self.cell(0, 8, f"  {title}", ln=True, fill=True)
        self.ln(2)

    def body_text(self, text: str, indent: int = 0):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(30, 30, 30)
        self.set_x(10 + indent)
        self.multi_cell(0, 6, text)
        self.ln(1)

    def key_value(self, key: str, value: str, indent: int = 0):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(60, 60, 80)
        self.set_x(10 + indent)
        self.cell(50, 6, f"{key}:", ln=False)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 6, str(value))

    def confidence_bar(self, label: str, value: float):
        """Draw a simple text-based confidence bar."""
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(30, 30, 30)
        self.set_x(12)
        bar_width = 120
        filled = int((value / 100) * bar_width)

        if value >= 60:
            r, g, b = 56, 189, 248
        elif value >= 35:
            r, g, b = 251, 191, 36
        else:
            r, g, b = 248, 113, 113

        # Label
        self.cell(70, 7, label, ln=False)
        # Bar background
        x = self.get_x()
        y = self.get_y()
        self.set_fill_color(220, 230, 240)
        self.rect(x, y + 1, bar_width, 5, "F")
        # Bar fill
        self.set_fill_color(r, g, b)
        self.rect(x, y + 1, filled, 5, "F")
        # Percentage text
        self.set_xy(x + bar_width + 3, y)
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(r, g, b)
        self.cell(20, 7, f"{value:.1f}%")
        self.ln(8)


def generate_pdf_report(
    symptoms: str,
    results: list,
    xai: dict = None,
    recommendations: dict = None,
    mode: str = "patient",
) -> bytes:
    """
    Generate a PDF diagnostic report.
    Returns bytes suitable for st.download_button.
    """
    pdf = DiagnosticReport()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # ── Report Title ──────────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 15)
    pdf.set_text_color(7, 13, 20)
    pdf.cell(0, 10, "Differential Diagnosis Report", ln=True, align="C")
    pdf.ln(4)

    # ── Patient Input ─────────────────────────────────────────────
    pdf.section_title("Patient Clinical Input")
    pdf.body_text(symptoms if symptoms else "Not provided.", indent=4)
    pdf.ln(3)

    # ── Diagnostic Results ────────────────────────────────────────
    pdf.section_title("AI Differential Diagnoses (Top 3)")
    rank_labels = ["Primary Diagnosis", "Secondary Diagnosis", "Tertiary Diagnosis"]

    for i, r in enumerate(results[:3]):
        name = r.get("name", "Unknown")
        conf = r.get("final_confidence", 0)
        reasoning = r.get("reasoning", "")
        llm_conf  = r.get("original_llm_confidence", 0)
        vec_sim   = round(r.get("retrieval_similarity", 0) * 100, 1)
        tag = rank_labels[i] if i < len(rank_labels) else f"Rank {i+1}"

        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(7, 13, 20)
        pdf.set_x(12)
        pdf.cell(0, 8, f"#{i+1}  {name}  -  {tag}", ln=True)

        pdf.confidence_bar(f"Overall Confidence", conf)
        pdf.key_value("LLM Confidence", f"{llm_conf}%", indent=4)
        pdf.key_value("Vector Similarity", f"{vec_sim}%", indent=4)
        if reasoning:
            pdf.key_value("Clinical Reasoning", reasoning, indent=4)
        pdf.ln(4)

    # ── Explainable AI ────────────────────────────────────────────
    if xai:
        pdf.add_page()
        pdf.section_title("Explainable AI Analysis")

        matched_s = xai.get("matched_symptoms", [])
        if matched_s:
            pdf.key_value("Matched Symptoms", ", ".join(matched_s), indent=4)

        matched_l = xai.get("matched_labs", [])
        if matched_l:
            pdf.key_value("Matched Lab Findings", ", ".join(matched_l), indent=4)

        expl = xai.get("confidence_explanation", "")
        if expl:
            pdf.key_value("Confidence Explanation", expl, indent=4)

        uncertainty = xai.get("uncertainty_note", "")
        if uncertainty:
            pdf.key_value("Uncertainty Note", uncertainty, indent=4)

        why_not = xai.get("why_not_others", "")
        if why_not:
            pdf.key_value("Why Not Other Diagnoses", why_not, indent=4)

        # Symptom weights bar chart
        weights = xai.get("symptom_weights", {})
        if weights:
            pdf.ln(3)
            pdf.section_title("Symptom Importance")
            sorted_w = sorted(weights.items(), key=lambda x: x[1], reverse=True)
            for sym, w in sorted_w[:8]:
                pdf.confidence_bar(sym[:35], float(w) * 100)

    # ── Recommendations ───────────────────────────────────────────
    if recommendations:
        pdf.ln(3)
        pdf.section_title("Personalized Recommendations")
        rec = recommendations

        spec = rec.get("specialist", "")
        if spec:
            pdf.key_value("Recommended Specialist", spec, indent=4)

        urgency = rec.get("urgency", "")
        if urgency:
            pdf.key_value("Urgency Level", urgency.upper(), indent=4)

        tests = rec.get("suggested_tests", [])
        if tests:
            pdf.key_value("Suggested Tests", "", indent=4)
            for t in tests[:6]:
                pdf.set_x(20)
                pdf.set_font("Helvetica", "", 10)
                pdf.set_text_color(30, 30, 30)
                pdf.cell(0, 6, f"  -  {t}", ln=True)

        dietary = rec.get("dietary_advice", "") or rec.get("metabolic_management", "")
        if dietary:
            pdf.key_value("Metabolic / Dietary Note", dietary, indent=4)

        steps = rec.get("next_steps", [])
        if steps:
            pdf.ln(2)
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(56, 189, 248)
            pdf.set_x(12)
            pdf.cell(0, 7, "Next Steps:", ln=True)
            for j, step in enumerate(steps[:6], 1):
                pdf.set_x(16)
                pdf.set_font("Helvetica", "", 10)
                pdf.set_text_color(30, 30, 30)
                pdf.multi_cell(0, 6, f"{j}. {step}")

    pdf.ln(6)

    # ── Disclaimer ────────────────────────────────────────────────
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(180, 100, 100)
    pdf.set_x(12)
    pdf.multi_cell(0, 6,
        "DISCLAIMER: This report is generated by an AI research prototype (RareDx) "
        "for academic and educational purposes only. It must NOT be used as a substitute "
        "for professional medical diagnosis, treatment, or advice. Always consult a qualified "
        "medical specialist for any health concerns."
    )

    # Return as bytes
    return bytes(pdf.output())
