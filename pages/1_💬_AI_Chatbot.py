import sys
import os
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from chatbot import chat_with_groq
from shared import apply_global_styles, init_session_state, render_sidebar_mode

st.set_page_config(page_title="RareDx Chatbot", page_icon="💬", layout="wide")
apply_global_styles()
init_session_state()
mode = render_sidebar_mode()

st.markdown('<div class="section-label">INTERACTIVE ASSISTANT</div>', unsafe_allow_html=True)
st.markdown('<div class="page-title">RareDx Awareness Chatbot</div>', unsafe_allow_html=True)
st.markdown(f'<p style="color:#6b8aa8; margin-bottom:30px;">Powered by Groq LLaMA 3.1 • Current Mode: <strong>{"Patient (Simple Language)" if mode == "patient" else "Doctor (Clinical Language)"}</strong></p>', unsafe_allow_html=True)

# Display history
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"], avatar="🧑" if msg["role"]=="user" else "🧬"):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Ask about diseases, prevention strategies, or lab reports..."):
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🧬"):
        with st.spinner("Thinking..."):
            # Format history for API
            api_history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.chat_history]
            response = chat_with_groq(api_history, mode)
            st.markdown(response)
    
    st.session_state.chat_history.append({"role": "assistant", "content": response})

# Quick actions sidebar
with st.sidebar:
    st.markdown("### ⚡ Quick Questions")
    if st.button("What is Newborn Screening?"):
        st.session_state.chat_history.append({"role": "user", "content": "What is newborn screening and why is it important for rare diseases?"})
        st.rerun()
    if st.button("Explain Genetic Counseling"):
        st.session_state.chat_history.append({"role": "user", "content": "Explain what genetic counseling is and when to get it."})
        st.rerun()
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🧹 Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()
