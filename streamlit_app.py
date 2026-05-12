import sys
import os
import streamlit as st
import fitz  # PyMuPDF
import plotly.graph_objects as go

# ─── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="RareDx — Diagnostic System",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from pipeline import run_pipeline
from nlp_extractor import extract_symptoms_from_text, generate_xai_explanation, generate_recommendations
from report_generator import generate_pdf_report
from shared import apply_global_styles, init_session_state, render_sidebar_mode

# Init styling and state
apply_global_styles()
init_session_state()
mode = render_sidebar_mode()

# ─── Header ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="raredx-header">
  <div class="raredx-logo">
    <div class="raredx-logo-icon">🧬</div>
    <div>
      <span class="raredx-logo-name">RareDx</span>
      <span class="raredx-logo-sub">Diagnostic Engine</span>
    </div>
  </div>
  <div class="stat-row">
    <div class="stat-item"><span class="stat-num">1,500</span><span class="stat-lbl">Diseases</span></div>
    <div class="stat-div"></div>
    <div class="stat-item"><span class="stat-num">RAG</span><span class="stat-lbl">System</span></div>
    <div class="stat-div"></div>
    <div class="stat-item"><span class="stat-num">LLaMA</span><span class="stat-lbl">Ranking</span></div>
  </div>
</div>
""", unsafe_allow_html=True)


# ─── Helper Functions ───────────────────────────────────────────────────────
def extract_text_from_pdf(uploaded_file):
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def create_confidence_gauge(score, name):
    # Adjust bar color
    color = "#38bdf8" if score >= 60 else "#fbbf24" if score >= 35 else "#f87171"
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={'text': name[:25] + ('...' if len(name)>25 else ''), 'font': {'size': 14, 'color': '#e2eaf4', 'family': 'Outfit'}},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#3d5a73", 'tickfont': {'color': '#6b8aa8'}},
            'bar': {'color': color},
            'bgcolor': "rgba(255,255,255,0.05)",
            'borderwidth': 0,
            'steps': [
                {'range': [0, 35], 'color': "rgba(248,113,113,0.05)"},
                {'range': [35, 60], 'color': "rgba(251,191,36,0.05)"},
                {'range': [60, 100], 'color': "rgba(56,189,248,0.05)"}
            ]
        },
        number={'font': {'color': color, 'size': 26, 'family': 'Outfit', 'weight': 'bold'}, 'suffix': "%"}
    ))
    fig.update_layout(
        height=220, 
        margin=dict(l=10, r=10, t=30, b=10), 
        paper_bgcolor="rgba(0,0,0,0)", 
        font={'color': "#e2eaf4"}
    )
    return fig


# ─── Input Area ─────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">STEP 1</div>', unsafe_allow_html=True)
st.markdown('<div class="page-title">Patient Clinical Input</div>', unsafe_allow_html=True)
st.markdown('<p style="color:#6b8aa8; margin-bottom:20px;">Describe symptoms naturally or upload a clinical lab report. The NLP engine will automatically extract findings.</p>', unsafe_allow_html=True)

input_tab, file_tab = st.tabs(["📝 Type Natural Language", "📄 Upload Lab Report (PDF)"])

with input_tab:
    symptoms = st.text_area(
        "Clinical Presentation",
        height=140,
        placeholder="e.g. A 2-year-old child presents with recurrent vomiting, lethargy, and hepatomegaly. Lab tests show elevated ammonia and metabolic acidosis..."
    )

with file_tab:
    uploaded_file = st.file_uploader("Upload PDF Lab Report", type=["pdf"])
    if uploaded_file is not None:
        with st.spinner("Extracting text via PyMuPDF..."):
            extracted_text = extract_text_from_pdf(uploaded_file)
            st.success("✅ Text extracted successfully!")
            with st.expander("Preview Extracted Text"):
                st.text(extracted_text)
            if not symptoms:
                symptoms = extracted_text
            else:
                symptoms += "\n\n--- Lab Report Data ---\n" + extracted_text

run_btn = st.button("🔍 Run Full Diagnostic Analysis", type="primary", use_container_width=True)

# ─── Execution ──────────────────────────────────────────────────────────────
if run_btn and symptoms.strip():
    with st.status("Running Diagnostic Intelligence Pipeline...", expanded=True) as status:
        st.write("🧠 **1/4** Extracting structured symptoms using NLP...")
        extracted_info = extract_symptoms_from_text(symptoms)
        
        sym_list = extracted_info.get('symptoms', [])
        if sym_list:
            sym_html = "".join([f'<span class="sym-tag">{s}</span>' for s in sym_list])
            st.markdown(f"Detected: {sym_html}", unsafe_allow_html=True)
        
        search_query = extracted_info.get("structured_query", symptoms)
        
        st.write("🔍 **2/4** Searching 1,500 diseases in FAISS vector database...")
        st.write("🤖 **3/4** Ranking top candidates via Groq LLaMA clinical reasoning...")
        results = run_pipeline(search_query, use_llm=True)
        
        st.write("📈 **4/4** Generating Explainable AI & Personalized Recommendations...")
        xai = generate_xai_explanation(symptoms, results)
        recs = generate_recommendations(results, symptoms, st.session_state.mode)
        
        st.session_state.last_results = results
        st.session_state.last_xai = xai
        st.session_state.last_recommendations = recs
        st.session_state.last_input = symptoms
        
        status.update(label="✅ Analysis Complete!", state="complete", expanded=False)


# ─── Results Presentation ───────────────────────────────────────────────────
if st.session_state.last_results:
    st.markdown("<br><hr style='border-color: rgba(56,189,248,0.12);'>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">STEP 2</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-title">Diagnostic Results</div>', unsafe_allow_html=True)
    
    results = st.session_state.last_results
    xai = st.session_state.last_xai
    recs = st.session_state.last_recommendations
    
    res_tab, xai_tab, rec_tab = st.tabs(["🧬 Top Differentials", "🧠 Explainable AI", "📋 Action Plan"])
    
    # -- Tab 1: Differential Diagnosis --
    with res_tab:
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Gauges
        cols = st.columns(3)
        for i, r in enumerate(results[:3]):
            with cols[i]:
                st.plotly_chart(create_confidence_gauge(r['final_confidence'], r['name']), use_container_width=True)
        
        # Detailed Cards
        rank_labels = ["Primary", "Secondary", "Tertiary"]
        for i, r in enumerate(results):
            tag = rank_labels[i] if i < 3 else f"Rank {i+1}"
            
            st.markdown(f"""
            <div class="dx-card">
              <div class="dx-card-rank">#{i+1} — {tag} Diagnosis</div>
              <div class="dx-card-name">{r['name']}</div>
              <div class="dx-conf-bar-bg">
                <div class="dx-conf-bar-fill" style="width: {r['final_confidence']}%; background: {'linear-gradient(90deg, #38bdf8, #0ea5e9)' if r['final_confidence']>=60 else 'linear-gradient(90deg, #fbbf24, #f59e0b)' if r['final_confidence']>=35 else 'linear-gradient(90deg, #f87171, #ef4444)'}"></div>
              </div>
              <div class="dx-reasoning">{r['reasoning']}</div>
              <div class="dx-chips">
                <div class="dx-chip">Hybrid Score: <span>{r['final_confidence']:.1f}%</span></div>
                <div class="dx-chip">LLM Conf: <span>{r.get('original_llm_confidence', 0)}%</span></div>
                <div class="dx-chip">Vector Sim: <span>{round(r.get('retrieval_similarity', 0)*100,1)}%</span></div>
              </div>
            </div>
            """, unsafe_allow_html=True)

    # -- Tab 2: Explainable AI --
    with xai_tab:
        st.markdown("<br>", unsafe_allow_html=True)
        if xai:
            st.markdown(f'<p style="font-size:15px; line-height:1.6;">{xai.get("confidence_explanation", "")}</p>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**✅ Matched Signals (Driven the prediction)**")
                for s in xai.get("matched_symptoms", []):
                    st.markdown(f'<span class="sym-tag">{s}</span>', unsafe_allow_html=True)
                for l in xai.get("matched_labs", []):
                    st.markdown(f'<span class="sym-tag" style="color:#a78bfa; border-color:rgba(167,139,250,0.3); background:rgba(167,139,250,0.1)">{l}</span>', unsafe_allow_html=True)
            with c2:
                st.markdown("**❌ Unmatched/Uncertain Signals**")
                for s in xai.get("unmatched_symptoms", []):
                    st.markdown(f'<span class="sym-tag sym-tag-unmatched">{s}</span>', unsafe_allow_html=True)
                
                note = xai.get("uncertainty_note", "")
                if note:
                    st.warning(f"**Uncertainty Note:** {note}")
                
            weights = xai.get("symptom_weights", {})
            if weights:
                st.markdown("<br>**Symptom Importance Weights**", unsafe_allow_html=True)
                w_fig = go.Figure(go.Bar(
                    x=list(weights.values()),
                    y=list(weights.keys()),
                    orientation='h',
                    marker_color='#38bdf8',
                    marker_line_width=0
                ))
                w_fig.update_layout(
                    height=280, margin=dict(l=0, r=0, t=10, b=0), 
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", 
                    font={'color': "#e2eaf4", 'family':'DM Mono'}
                )
                st.plotly_chart(w_fig, use_container_width=True)
        else:
            st.info("Explainable AI analysis not available.")

    # -- Tab 3: Recommendations --
    with rec_tab:
        st.markdown("<br>", unsafe_allow_html=True)
        if recs:
            urgency = recs.get("urgency", "").upper()
            if urgency == "EMERGENCY":
                st.error(f"🚨 **Urgency Level:** {urgency}")
            elif urgency == "URGENT":
                st.warning(f"⚠️ **Urgency Level:** {urgency}")
            else:
                st.info(f"ℹ️ **Urgency Level:** {urgency}")
                
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"**Recommended Specialist:**<br><span style='color:#38bdf8'>{recs.get('specialist', 'General Practitioner')}</span>", unsafe_allow_html=True)
                st.markdown("<br>**Suggested Tests:**", unsafe_allow_html=True)
                for t in recs.get("suggested_tests", []):
                    st.markdown(f"- 🩸 {t}")
            with c2:
                st.markdown("**Next Steps:**")
                for i, step in enumerate(recs.get("next_steps", []), 1):
                    st.markdown(f"{i}. {step}")
                
            advice = recs.get("dietary_advice", "") or recs.get("metabolic_management", "")
            if advice:
                st.markdown(f"""
                <div class="prevent-banner">
                  <div class="prevent-banner-title">🛡️ Management / Dietary Advice</div>
                  <div style="font-size:14px;">{advice}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Recommendations not available.")

    # -- Actions --
    st.markdown("<br><hr style='border-color: rgba(56,189,248,0.12);'>", unsafe_allow_html=True)
    
    pdf_bytes = generate_pdf_report(st.session_state.last_input, results, xai, recs, st.session_state.mode)
    
    col_dl, col_space = st.columns([1, 3])
    with col_dl:
        st.download_button(
            label="📥 Download PDF Report",
            data=pdf_bytes,
            file_name=f"RareDx_Report.pdf",
            mime="application/pdf",
            use_container_width=True
        )

elif not run_btn:
    st.info("👆 Enter clinical details above and click Run Full Diagnostic Analysis to begin.")