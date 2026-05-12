"""
Shared CSS and session-state helpers loaded by every page.
Usage: from src.shared import apply_global_styles, init_session_state
"""
import streamlit as st

SHARED_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Outfit:wght@400;600;700;800&family=Inter:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #070d14;
    color: #e2eaf4;
}
.stApp {
    background-color: #070d14;
    background-image:
        linear-gradient(rgba(56,189,248,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(56,189,248,0.03) 1px, transparent 1px);
    background-size: 40px 40px;
}
#MainMenu, footer { visibility: hidden; }
.block-container { 
    padding-top: 3.5rem; 
    padding-bottom: 6rem; 
    max-width: 1100px; 
}

/* ── Typography helpers ── */
.page-title {
    font-family: 'Outfit', sans-serif;
    font-size: 32px; font-weight: 800;
    color: #fff; margin-bottom: 8px; letter-spacing: -0.5px;
}
.page-sub {
    font-family: 'DM Mono', monospace;
    font-size: 11px; color: #6b8aa8;
    text-transform: uppercase; letter-spacing: 1.5px;
}
.section-label {
    font-family: 'DM Mono', monospace;
    font-size: 10px; letter-spacing: 2px;
    color: #38bdf8; text-transform: uppercase;
    margin-bottom: 6px;
}

/* ── Sidebar styling ── */
[data-testid="stSidebar"] {
    background: #0c1621 !important;
    border-right: 1px solid rgba(56,189,248,0.08) !important;
}
[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    border: 1px solid rgba(56,189,248,0.2) !important;
    color: #e2eaf4 !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    transition: all 0.2s !important;
    width: 100% !important;
    text-align: left !important;
    padding: 8px 12px !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(56,189,248,0.1) !important;
    border-color: #38bdf8 !important;
}

/* ── Primary button ── */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #38bdf8, #0ea5e9) !important;
    color: #070d14 !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Outfit', sans-serif;
    font-weight: 700 !important;
    font-size: 16px !important;
    padding: 14px 28px !important;
    transition: all 0.25s !important;
    letter-spacing: 0.3px !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(56,189,248,0.35) !important;
}

/* ── Secondary button ── */
.stButton > button[kind="secondary"],
.stButton > button:not([kind]) {
    background: rgba(56,189,248,0.06) !important;
    border: 1px solid rgba(56,189,248,0.18) !important;
    color: #e2eaf4 !important;
    border-radius: 8px !important;
    font-size: 14px !important;
    transition: all 0.2s !important;
}
.stButton > button[kind="secondary"]:hover,
.stButton > button:not([kind]):hover {
    background: rgba(56,189,248,0.12) !important;
    border-color: #38bdf8 !important;
}

/* ── Inputs ── */
.stTextArea textarea,
.stTextInput input {
    background: #101e2e !important;
    border: 1px solid rgba(56,189,248,0.15) !important;
    border-radius: 10px !important;
    color: #e2eaf4 !important;
    font-size: 15px !important;
    line-height: 1.7 !important;
}
.stTextArea textarea:focus,
.stTextInput input:focus {
    border-color: #38bdf8 !important;
    box-shadow: 0 0 0 3px rgba(56,189,248,0.08) !important;
}
.stTextArea label, .stTextInput label, .stSelectbox label {
    color: #6b8aa8 !important;
    font-size: 11px !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
    font-family: 'DM Mono', monospace !important;
}

/* ── Selectbox ── */
.stSelectbox > div > div {
    background: #101e2e !important;
    border: 1px solid rgba(56,189,248,0.15) !important;
    border-radius: 10px !important;
    color: #e2eaf4 !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid rgba(56,189,248,0.12) !important;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #6b8aa8 !important;
    border-radius: 8px 8px 0 0 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 12px !important;
    letter-spacing: 0.5px !important;
    padding: 10px 18px !important;
    border-bottom: 2px solid transparent !important;
}
.stTabs [aria-selected="true"] {
    color: #38bdf8 !important;
    border-bottom: 2px solid #38bdf8 !important;
    background: rgba(56,189,248,0.05) !important;
}

/* ── Containers / expanders ── */
[data-testid="stExpander"] {
    background: #101e2e !important;
    border: 1px solid rgba(56,189,248,0.1) !important;
    border-radius: 12px !important;
}
[data-testid="stExpander"]:hover {
    border-color: rgba(56,189,248,0.25) !important;
}
div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] {
    background: transparent;
}

/* ── st.status ── */
[data-testid="stStatus"] {
    background: #0c1621 !important;
    border: 1px solid rgba(56,189,248,0.15) !important;
    border-radius: 10px !important;
}

/* ── Alerts ── */
.stAlert { border-radius: 10px !important; }

/* ── Mode badge ── */
.mode-badge {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 4px 12px;
    border-radius: 20px;
    font-family: 'DM Mono', monospace;
    font-size: 11px; font-weight: 500;
    letter-spacing: 0.5px;
}
.mode-patient { background: rgba(56,189,248,0.1); border: 1px solid rgba(56,189,248,0.25); color: #38bdf8; }
.mode-doctor  { background: rgba(167,139,250,0.1); border: 1px solid rgba(167,139,250,0.25); color: #a78bfa; }

/* ── Disease card ── */
.dx-card {
    background: #101e2e;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    padding: 20px 22px;
    margin-bottom: 12px;
    transition: border-color 0.2s, transform 0.2s;
    position: relative; overflow: hidden;
}
.dx-card::before {
    content: '';
    position: absolute; left: 0; top: 0; bottom: 0;
    width: 3px;
    background: linear-gradient(180deg, #38bdf8, #0ea5e9);
    border-radius: 3px 0 0 3px;
}
.dx-card:hover {
    border-color: rgba(56,189,248,0.22);
    transform: translateY(-2px);
}
.dx-card-rank {
    font-family: 'Outfit', sans-serif;
    font-size: 11px; font-weight: 700;
    text-transform: uppercase; letter-spacing: 1px;
    color: #38bdf8; margin-bottom: 6px;
}
.dx-card-name {
    font-family: 'Outfit', sans-serif;
    font-size: 18px; font-weight: 700;
    color: #fff; margin-bottom: 10px;
}
.dx-conf-bar-bg {
    background: rgba(255,255,255,0.05);
    border-radius: 99px; height: 6px; margin-bottom: 10px; overflow: hidden;
}
.dx-conf-bar-fill { height: 100%; border-radius: 99px; }
.dx-reasoning {
    font-size: 13px; color: #8aa6c0; line-height: 1.7;
    border-left: 2px solid rgba(56,189,248,0.15);
    padding-left: 12px; font-style: italic;
}
.dx-chips { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 12px; }
.dx-chip {
    background: #0c1621;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 8px; padding: 5px 11px;
    font-family: 'DM Mono', monospace; font-size: 11px; color: #6b8aa8;
}
.dx-chip span { color: #e2eaf4; font-weight: 500; }

/* ── Symptom tag ── */
.sym-tag {
    display: inline-flex; align-items: center; gap: 5px;
    background: rgba(56,189,248,0.08);
    border: 1px solid rgba(56,189,248,0.2);
    border-radius: 6px; padding: 3px 10px;
    font-size: 12px; color: #7dd3fc;
    margin: 3px;
}
.sym-tag-unmatched {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    color: #4a6a83;
}

/* ── Prevent banner ── */
.prevent-banner {
    background: linear-gradient(135deg, rgba(52,211,153,0.08), rgba(16,185,129,0.04));
    border: 1px solid rgba(52,211,153,0.2);
    border-radius: 10px; padding: 12px 16px;
    margin-top: 10px;
}
.prevent-banner-title {
    font-family: 'Outfit', sans-serif;
    font-size: 13px; font-weight: 700;
    color: #34d399; margin-bottom: 4px;
}

/* ── Header stats ── */
.stat-row { display: flex; gap: 24px; align-items: center; flex-wrap: wrap; }
.stat-item { text-align: center; }
.stat-num {
    font-family: 'Outfit', sans-serif;
    font-size: 22px; font-weight: 800; color: #38bdf8; display: block;
}
.stat-lbl {
    font-family: 'DM Mono', monospace;
    font-size: 9px; color: #3d5a73; text-transform: uppercase; letter-spacing: 0.5px;
}
.stat-div { width: 1px; height: 36px; background: rgba(56,189,248,0.12); }

/* ── Chat bubbles ── */
[data-testid="stChatMessageContent"] {
    background: #101e2e !important;
    border: 1px solid rgba(56,189,248,0.08) !important;
    border-radius: 12px !important;
    padding: 14px 16px !important;
}

/* ── Spinner ── */
.stSpinner > div { border-top-color: #38bdf8 !important; }
</style>
"""


def apply_global_styles():
    """Inject the shared CSS into the current page."""
    import streamlit as st
    st.markdown(SHARED_CSS, unsafe_allow_html=True)


def init_session_state():
    """Ensure shared session state keys exist."""
    import streamlit as st
    defaults = {
        "mode": "patient",
        "last_results": None,
        "last_xai": None,
        "last_recommendations": None,
        "last_input": "",
        "chat_history": [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def render_sidebar_mode():
    """
    Render the Doctor / Patient mode toggle in the sidebar.
    Returns the current mode string ('patient' or 'doctor').
    """
    import streamlit as st
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        st.markdown("---")
        mode_label = st.radio(
            "Application Mode",
            ["🧑 Patient Mode", "👨‍⚕️ Doctor Mode"],
            index=0 if st.session_state.mode == "patient" else 1,
            help="Patient mode uses plain language. Doctor mode shows clinical/technical details.",
        )
        st.session_state.mode = "patient" if "Patient" in mode_label else "doctor"

        badge_cls = "mode-patient" if st.session_state.mode == "patient" else "mode-doctor"
        badge_icon = "🧑" if st.session_state.mode == "patient" else "👨‍⚕️"
        badge_text = "Patient Mode" if st.session_state.mode == "patient" else "Doctor Mode"
        st.markdown(
            f'<div class="mode-badge {badge_cls}">{badge_icon} {badge_text}</div>',
            unsafe_allow_html=True,
        )
        st.markdown("---")
        st.markdown(
            '<p style="font-family:\'DM Mono\',monospace;font-size:10px;color:#3d5a73;">'
            "⚠ Research prototype. Not for clinical use.</p>",
            unsafe_allow_html=True,
        )
    return st.session_state.mode
