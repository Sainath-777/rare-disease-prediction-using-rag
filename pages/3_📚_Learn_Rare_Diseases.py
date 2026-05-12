import sys
import os
import streamlit as st
import streamlit.components.v1 as components

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from knowledge_graph import load_diseases, build_disease_graph
from shared import apply_global_styles, init_session_state, render_sidebar_mode

st.set_page_config(page_title="Learn & Graph", page_icon="📚", layout="wide")
apply_global_styles()
init_session_state()
render_sidebar_mode()

st.markdown('<div class="section-label">EDUCATIONAL RESOURCES</div>', unsafe_allow_html=True)
st.markdown('<div class="page-title">Learn & Knowledge Graph</div>', unsafe_allow_html=True)
st.markdown('<p style="color:#6b8aa8; margin-bottom:20px;">Explore the interconnected web of rare diseases or read our awareness blog.</p>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🕸️ Knowledge Graph", "📖 Awareness Blog"])

with tab1:
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_ctrl, col_graph = st.columns([1, 4])
    
    with col_ctrl:
        st.markdown("### Controls")
        num_nodes = st.slider("Number of Diseases", min_value=5, max_value=50, value=15, step=5)
        generate = st.button("Generate Graph", type="primary", use_container_width=True)
        st.markdown("""
        <div style="margin-top:20px; padding:15px; background:rgba(255,255,255,0.05); border-radius:10px; border:1px solid rgba(255,255,255,0.1)">
          <div style="font-family:'Syne'; font-weight:700; margin-bottom:10px; color:#fff;">Legend</div>
          <div style="display:flex; align-items:center; gap:8px; margin-bottom:8px;"><div style="width:12px; height:12px; border-radius:50%; background:#38bdf8;"></div><span style="font-size:13px;">Disease</span></div>
          <div style="display:flex; align-items:center; gap:8px; margin-bottom:8px;"><div style="width:12px; height:12px; transform:rotate(45deg); background:#7dd3fc;"></div><span style="font-size:13px;">Symptom</span></div>
          <div style="display:flex; align-items:center; gap:8px;"><div style="width:0; height:0; border-left:6px solid transparent; border-right:6px solid transparent; border-bottom:12px solid #a78bfa;"></div><span style="font-size:13px;">Inheritance</span></div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_graph:
        if generate:
            with st.spinner("Rendering PyVis Network Physics..."):
                diseases = load_diseases()
                graph_html = build_disease_graph(diseases, max_diseases=num_nodes)
                st.markdown('<div style="border:1px solid rgba(56,189,248,0.2); border-radius:12px; overflow:hidden;">', unsafe_allow_html=True)
                components.html(graph_html, height=620, scrolling=False)
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("👈 Set the number of diseases and click Generate Graph.")

with tab2:
    st.markdown("<br>", unsafe_allow_html=True)
    
    with st.expander("🧬 The Importance of Newborn Screening"):
        st.markdown("""
        **Newborn screening** is a public health program that tests babies for certain rare but serious medical conditions shortly after birth.
        Catching these conditions early—before symptoms appear—can prevent serious health problems, intellectual disability, or even death.
        
        Common conditions screened include:
        - Phenylketonuria (PKU)
        - MCAD deficiency
        - Galactosemia
        
        *If a rare metabolic disease is caught in newborn screening, it can often be entirely managed by a strict diet.*
        """)
        
    with st.expander("⚡ Understanding Mitochondrial Diseases"):
        st.markdown("""
        **Mitochondria** are the powerhouses of the cell. When they fail to produce enough energy, cells are starved and can't function properly.
        This leads to a group of rare genetic disorders called mitochondrial diseases.
        
        **Common Symptoms:**
        - Muscle weakness
        - Neurological problems
        - Lactic acidosis
        
        **Inheritance Pattern:**
        Inheritance can be complex. Because mitochondria carry their own DNA (mtDNA) inherited solely from the mother, many mitochondrial diseases follow a maternal inheritance pattern. Others are caused by mutations in nuclear DNA and follow autosomal recessive patterns.
        """)
        
    with st.expander("👪 What is Genetic Counseling?"):
        st.markdown("""
        **Genetic counseling** gives you information about how genetic conditions might affect you or your family.
        The genetic counselor or other healthcare professional will collect your personal and family health history. 
        
        They can use this information to determine how likely it is that you or your family member has a genetic condition. Based on this information, the counselor can help you decide whether a genetic test might be right for you or your relative.
        """)
