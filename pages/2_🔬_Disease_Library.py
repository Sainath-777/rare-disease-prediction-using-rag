import sys
import os
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from knowledge_graph import load_diseases
from shared import apply_global_styles, init_session_state, render_sidebar_mode

st.set_page_config(page_title="Disease Library", page_icon="🔬", layout="wide")
apply_global_styles()
init_session_state()
render_sidebar_mode()

st.markdown('<div class="section-label">DATABASE EXPLORER</div>', unsafe_allow_html=True)
st.markdown('<div class="page-title">Rare Disease Library</div>', unsafe_allow_html=True)
st.markdown('<p style="color:#6b8aa8; margin-bottom:30px;">Interactive profiles for 1,500 indexed rare diseases.</p>', unsafe_allow_html=True)

@st.cache_data
def get_data():
    return load_diseases()

diseases = get_data()

# Search & Filter
col1, col2 = st.columns([2, 1])
with col1:
    search_term = st.text_input("🔍 Search Diseases by Name or Symptom")
with col2:
    categories = list(set([d.get("category", "Other") for d in diseases]))
    selected_cat = st.selectbox("Filter by Category", ["All"] + categories)

filtered = diseases
if search_term:
    search_lower = search_term.lower()
    filtered = [d for d in filtered if search_lower in d["name"].lower() or search_lower in " ".join(d.get("key_symptoms", [])).lower()]
if selected_cat != "All":
    filtered = [d for d in filtered if d.get("category") == selected_cat]

st.markdown(f'<div style="font-family:\'DM Mono\',monospace; font-size:12px; color:#38bdf8; margin-bottom:16px;">SHOWING {len(filtered)} DISEASES</div>', unsafe_allow_html=True)

# Display Cards
for d in filtered[:50]:  # Limit to 50 for performance
    with st.expander(f"🧬 {d['name']} — {d.get('inheritance', 'Unknown Inheritance')}"):
        st.markdown(f'<p style="color:#e2eaf4; font-size:15px; line-height:1.6;">{d.get("clinical_summary", "No clinical summary available.")}</p>', unsafe_allow_html=True)
        
        # "Prevent This Disease" logic (heuristic based on text)
        text_lower = (d.get("clinical_summary", "") + " " + " ".join(d.get("key_symptoms", []))).lower()
        if any(kw in text_lower for kw in ["diet", "fasting", "newborn screening", "supplement", "avoid", "management"]):
            st.markdown("""
            <div class="prevent-banner">
              <div class="prevent-banner-title">🛡️ Preventative / Management Aspects Available</div>
              <div style="font-size:14px; color:#e2eaf4;">This condition may be manageable with strict diet, avoiding fasting, or early newborn screening. Check the AI Chatbot for specific prevention tips.</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Key Symptoms**")
            for sym in d.get("key_symptoms", []):
                st.markdown(f'<span class="sym-tag">{sym}</span>', unsafe_allow_html=True)
        with c2:
            st.markdown("**Lab Findings**")
            labs = d.get("lab_findings", [])
            if labs:
                for lab in labs:
                    st.markdown(f'<span class="sym-tag" style="color:#a78bfa; border-color:rgba(167,139,250,0.3); background:rgba(167,139,250,0.1)">{lab}</span>', unsafe_allow_html=True)
            else:
                st.write("No lab findings documented.")

if len(filtered) > 50:
    st.info("Search to narrow down results (showing first 50).")
