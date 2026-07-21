import streamlit as st
import time
from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain

# ══════════════════════════════════════════════════════════════════════════
#  PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="ResearchMind · AI Research Assistant",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════════
#  CONSTANTS (UI-only — do not affect backend behaviour)
# ══════════════════════════════════════════════════════════════════════════
STEPS = [
    {"key": "search", "num": "01", "icon": "🔍", "title": "Search Agent",
     "desc": "Searching the web for recent, reliable information"},
    {"key": "reader", "num": "02", "icon": "📄", "title": "Reader Agent",
     "desc": "Scraping and extracting deeper content from top sources"},
    {"key": "writer", "num": "03", "icon": "✍️", "title": "Writer Chain",
     "desc": "Drafting a structured, detailed research report"},
    {"key": "critic", "num": "04", "icon": "🧐", "title": "Critic Chain",
     "desc": "Reviewing the report and scoring its quality"},
]

EXAMPLE_TOPIC = "Quantum computing breakthroughs in 2025"

# ══════════════════════════════════════════════════════════════════════════
#  CUSTOM CSS  (single block — appearance only)
# ══════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"]  { font-family: 'Inter', sans-serif; }

/* ── App background ── */
.stApp {
    background: #0e0f13;
}

/* ── Hide default streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2.2rem 3rem 3rem; max-width: 1180px; }

/* ── Header ── */
.app-header { padding: 0.5rem 0 1.2rem; }
.app-title {
    font-size: 2.1rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    color: #f1f1f4;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 0.6rem;
}
.app-subtitle {
    font-size: 0.98rem;
    color: #9a9da8;
    font-weight: 400;
    margin: 0.35rem 0 0;
}
.app-divider {
    height: 1px;
    background: linear-gradient(90deg, #2a2c33, transparent 90%);
    margin: 1.4rem 0 1.6rem;
    border: none;
}

/* ── Generic card ── */

.ui-card-title {
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #6559ff;
    margin-bottom: 0.9rem;
}

/* ── Section heading ── */
.section-heading {
    font-size: 1.1rem;
    font-weight: 700;
    color: #f1f1f4;
    margin: 0.2rem 0 0.9rem;
}

/* ── Text area ── */
.stTextArea textarea {
    background: #14151a !important;
    border: 1px solid #2a2c33 !important;
    border-radius: 12px !important;
    color: #f1f1f4 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.98rem !important;
    padding: 0.85rem 1rem !important;
    transition: border-color 0.15s, box-shadow 0.15s !important;
}
.stTextArea textarea:focus {
    border-color: #6559ff !important;
    box-shadow: 0 0 0 3px rgba(101,89,255,0.12) !important;
}
.stTextArea label {
    font-size: 0.9rem !important;
    font-weight: 600 !important;
    color: #f1f1f4 !important;
}

/* ── Char counter / example caption ── */
.helper-text {
    font-size: 0.78rem;
    color: #6b6f76;
    margin-top: 0.35rem;
}
.example-tag {
    display: inline-block;
    background: #211f3d;
    color: #6559ff;
    border: 1px solid #3a3670;
    border-radius: 6px;
    padding: 0.2rem 0.6rem;
    font-size: 0.76rem;
    font-weight: 500;
    margin-top: 0.5rem;
}

/* ── Buttons ── */
.stButton > button {
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
    border-radius: 10px !important;
    padding: 0.6rem 1.4rem !important;
    transition: all 0.15s ease !important;
    width: 100%;
}
div[data-testid="column"]:nth-of-type(1) .stButton > button {
    background: #6559ff !important;
    color: #1a1b21 !important;
    border: none !important;
    box-shadow: 0 2px 10px rgba(101,89,255,0.25) !important;
}
div[data-testid="column"]:nth-of-type(1) .stButton > button:hover {
    background: #564bec !important;
    box-shadow: 0 4px 14px rgba(101,89,255,0.32) !important;
    transform: translateY(-1px);
}
div[data-testid="column"]:nth-of-type(2) .stButton > button {
    background: #1a1b21 !important;
    color: #c5c7cf !important;
    border: 1px solid #2a2c33 !important;
}
div[data-testid="column"]:nth-of-type(2) .stButton > button:hover {
    background: #24262d !important;
    border-color: #3a3c44 !important;
}

/* download button */
.stDownloadButton > button {
    background: #f1f1f4 !important;
    color: #1a1b21 !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    padding: 0.55rem 1.2rem !important;
}
.stDownloadButton > button:hover { background: #c5c7cf !important; }

/* ── Step / timeline cards ── */
.step-card {
    background: #1a1b21;
    border: 1px solid #2a2c33;
    border-radius: 12px;
    padding: 0.95rem 1.2rem;
    margin-bottom: 0.7rem;
    display: flex;
    align-items: center;
    gap: 0.85rem;
    transition: border-color 0.25s, background 0.25s;
}
.step-card.running { border-color: #4a3fa0; background: #1e1c33; }
.step-card.done     { border-color: #2f6b4a; background: #12241a; }
.step-icon {
    width: 34px; height: 34px;
    border-radius: 9px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.05rem;
    background: #24262d;
    flex-shrink: 0;
}
.step-card.running .step-icon { background: #2a2550; }
.step-card.done .step-icon { background: #123322; }
.step-body { flex: 1; min-width: 0; }
.step-title-row {
    display: flex; align-items: center; gap: 0.5rem;
    font-size: 0.9rem; font-weight: 700; color: #f1f1f4;
}
.step-desc { font-size: 0.79rem; color: #7a7d85; margin-top: 0.1rem; }
.step-badge {
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    padding: 0.15rem 0.5rem;
    border-radius: 6px;
    flex-shrink: 0;
}
.badge-waiting { color: #6b6f76; background: #24262d; }
.badge-running { color: #6559ff; background: #2a2550; }
.badge-done    { color: #4ade80; background: #123322; }

/* ── Empty state ── */
.empty-state {
    text-align: center;
    padding: 3.2rem 1.5rem;
    color: #7a7d85;
}
.empty-state .icon { font-size: 2.4rem; margin-bottom: 0.8rem; }
.empty-state .title { font-size: 1.02rem; font-weight: 700; color: #c5c7cf; margin-bottom: 0.3rem; }
.empty-state .sub { font-size: 0.85rem; max-width: 340px; margin: 0 auto; line-height: 1.55; }

/* ── Result panel ── */
.result-card {
    background: #1a1b21;
    border: 1px solid #2a2c33;
    border-radius: 16px;
    padding: 1.9rem 2.1rem;
    box-shadow: 0 1px 2px rgba(16,24,40,0.04), 0 1px 3px rgba(16,24,40,0.03);
    margin-bottom: 1.4rem;
}
.result-card-header {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 1rem; padding-bottom: 0.9rem;
    border-bottom: 1px solid #2a2c33;
}
.result-card-header h3 {
    font-size: 1.15rem; font-weight: 800; color: #f1f1f4; margin: 0;
}
.result-scroll {
    max-height: 520px;
    overflow-y: auto;
    padding-right: 0.4rem;
    font-size: 0.94rem;
    line-height: 1.75;
    color: #d5d6db;
}
.result-scroll::-webkit-scrollbar { width: 6px; }
.result-scroll::-webkit-scrollbar-thumb { background: #3a3c44; border-radius: 6px; }
.result-scroll::-webkit-scrollbar-track { background: transparent; }

/* Force dark, readable text for rendered markdown inside white cards
   (overrides Streamlit's theme text color, which can default to white
   and become invisible on a white card background). */
.result-scroll, .result-scroll p, .result-scroll li, .result-scroll span,
.result-scroll strong, .result-scroll em, .result-scroll a,
.result-scroll h1, .result-scroll h2, .result-scroll h3,
.result-scroll h4, .result-scroll h5, .result-scroll h6,
.result-scroll code, .result-scroll blockquote {
    color: #d5d6db !important;
}
.result-scroll h1, .result-scroll h2, .result-scroll h3 {
    color: #f1f1f4 !important;
    font-weight: 800 !important;
}
.result-scroll a { color: #6559ff !important; }
.result-scroll code {
    background: #24262d !important;
    padding: 0.1rem 0.35rem;
    border-radius: 5px;
}

/* raw content boxes inside expanders */
.raw-box {
    font-size: 0.85rem;
    line-height: 1.65;
    color: #c5c7cf;
    white-space: pre-wrap;
    background: #14151a;
    border: 1px solid #2a2c33;
    border-radius: 10px;
    padding: 1rem 1.1rem;
    max-height: 320px;
    overflow-y: auto;
}

/* ── Expander ── */
details {
    border: 1px solid #2a2c33 !important;
    border-radius: 12px !important;
    background: #1a1b21 !important;
}
summary {
    font-size: 0.86rem !important;
    font-weight: 600 !important;
    color: #c5c7cf !important;
}

/* ── Alerts ── */
.alert-card {
    border-radius: 12px;
    padding: 0.85rem 1.1rem;
    font-size: 0.88rem;
    margin-bottom: 1rem;
    display: flex; gap: 0.6rem; align-items: flex-start;
}
.alert-success { background: #12281c; border: 1px solid #1f4a34; color: #4ade80; }
.alert-warning { background: #2b230f; border: 1px solid #5a4620; color: #e0a940; }
.alert-error   { background: #2b1414; border: 1px solid #5a2626; color: #f47174; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #1a1b21;
    border-right: 1px solid #2a2c33;
}
.sb-logo {
    display: flex; align-items: center; gap: 0.6rem;
    font-size: 1.15rem; font-weight: 800; color: #f1f1f4;
    padding: 0.4rem 0 1.1rem;
}
.sb-logo .mark {
    width: 36px; height: 36px; border-radius: 10px;
    background: linear-gradient(135deg,#6559ff,#8b7bff);
    display: flex; align-items: center; justify-content: center;
    color: #fff; font-size: 1.05rem;
}
.sb-section-title {
    font-size: 0.72rem; font-weight: 700; letter-spacing: 0.09em;
    text-transform: uppercase; color: #6b6f76;
    margin: 1.3rem 0 0.6rem;
}
.sb-text { font-size: 0.86rem; color: #c5c7cf; line-height: 1.6; }
.sb-feature {
    font-size: 0.85rem; color: #c5c7cf; margin-bottom: 0.45rem;
    display: flex; gap: 0.5rem; align-items: flex-start; line-height: 1.5;
}
.sb-status-dot {
    width: 8px; height: 8px; border-radius: 50%;
    background: #22c55e; display: inline-block; margin-right: 0.4rem;
    box-shadow: 0 0 0 3px rgba(34,197,94,0.15);
}
.sb-tip {
    font-size: 0.82rem; color: #9a9da8; margin-bottom: 0.5rem;
    padding-left: 0.9rem; border-left: 2px solid #2a2550; line-height: 1.55;
}

/* ── Footer ── */
.app-footer {
    text-align: center;
    font-size: 0.78rem;
    color: #6b6f76;
    margin-top: 2.6rem;
    padding-top: 1.4rem;
    border-top: 1px solid #2a2c33;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
#  UI HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════
def render_step_card(placeholder, num, icon, title, desc, state):
    """Render one pipeline step into a given st.empty() placeholder."""
    state_cls = {"waiting": "", "running": "running", "done": "done"}[state]
    badge_txt = {"waiting": "Waiting", "running": "Running", "done": "Done"}[state]
    badge_cls = {"waiting": "badge-waiting", "running": "badge-running", "done": "badge-done"}[state]
    placeholder.markdown(f"""
    <div class="step-card {state_cls}">
        <div class="step-icon">{icon}</div>
        <div class="step-body">
            <div class="step-title-row">{title}</div>
            <div class="step-desc">{desc}</div>
        </div>
        <div class="step-badge {badge_cls}">{badge_txt}</div>
    </div>
    """, unsafe_allow_html=True)


def alert(kind: str, message: str):
    icons = {"success": "✅", "warning": "⚠️", "error": "⛔"}
    st.markdown(f"""
    <div class="alert-card alert-{kind}">
        <span>{icons.get(kind, "")}</span><span>{message}</span>
    </div>
    """, unsafe_allow_html=True)


def empty_state():
    st.markdown("""
    <div class="ui-card">
        <div class="empty-state">
            <div class="icon">🧭</div>
            <div class="title">No research yet</div>
            <div class="sub">Enter a topic on the left and click "Run Research Pipeline" —
            your report will appear here once the agents finish working.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div class="sb-logo"><div class="mark">🧭</div>ResearchMind</div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sb-section-title">About</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="sb-text">
    A multi-agent research assistant. Specialized AI agents search,
    read, write, and critique so you get a polished, sourced report
    from a single topic prompt.
                
    Made by yagya
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sb-section-title">Features</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="sb-feature">🔍 <span>Live web search for current information</span></div>
    <div class="sb-feature">📄 <span>Deep scraping of the most relevant source</span></div>
    <div class="sb-feature">✍️ <span>Structured, professional report writing</span></div>
    <div class="sb-feature">🧐 <span>Automatic critique &amp; quality scoring</span></div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sb-section-title">Supported Model</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="sb-text">Mistral · mistral-medium-3-5</div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sb-section-title">System Status</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="sb-text"><span class="sb-status-dot"></span>All agents operational</div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sb-section-title">Tips for better prompts</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="sb-tip">Be specific — add a year, industry, or region.</div>
    <div class="sb-tip">Ask about one topic at a time for a focused report.</div>
    <div class="sb-tip">Avoid yes/no questions — frame it as a subject to explore.</div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
#  SESSION STATE INIT
# ══════════════════════════════════════════════════════════════════════════
for key, default in (("results", {}), ("running", False), ("done", False), ("topic_value", "")):
    if key not in st.session_state:
        st.session_state[key] = default

# ══════════════════════════════════════════════════════════════════════════
#  HEADER
# ══════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="app-header">
    <p class="app-title">🧭 Multi-Agent Research Assistant</p>
    <p class="app-subtitle">AI-powered research using specialized autonomous agents — search, read, write, and critique, all in one pass.</p>
</div>
<hr class="app-divider" />
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
#  LAYOUT: input (left) + pipeline (right)
# ══════════════════════════════════════════════════════════════════════════
col_input, col_pipeline = st.columns([5, 4], gap="large")

with col_input:
    st.markdown('<div class="ui-card">', unsafe_allow_html=True)
    st.markdown('<div class="ui-card-title">Research Topic</div>', unsafe_allow_html=True)

    topic = st.text_area(
        label="What would you like researched?",
        value=st.session_state.topic_value,
        placeholder=f"e.g. {EXAMPLE_TOPIC}",
        height=130,
        key="topic_input",
        label_visibility="collapsed",
    )
    char_count = len(topic) if topic else 0
    st.markdown(f'<div class="helper-text">{char_count} characters</div>', unsafe_allow_html=True)
    st.markdown(f'<span class="example-tag">💡 Try: "{EXAMPLE_TOPIC}"</span>', unsafe_allow_html=True)

    st.write("")
    btn_col1, btn_col2 = st.columns([2, 1])
    with btn_col1:
        run_btn = st.button("⚡ Run Research Pipeline", use_container_width=True)
    with btn_col2:
        clear_btn = st.button("Clear", use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

with col_pipeline:
    st.markdown('<div class="section-heading">Agent Pipeline</div>', unsafe_allow_html=True)
    pipeline_slots = {}
    pipeline_box = st.container()
    with pipeline_box:
        for step in STEPS:
            pipeline_slots[step["key"]] = st.empty()

    def current_state(step_key):
        r = st.session_state.results
        if step_key in r:
            return "done"
        if st.session_state.running:
            for s in STEPS:
                if s["key"] not in r:
                    return "running" if s["key"] == step_key else "waiting"
        return "waiting"

    for step in STEPS:
        render_step_card(
            pipeline_slots[step["key"]], step["num"], step["icon"],
            step["title"], step["desc"], current_state(step["key"])
        )

# ══════════════════════════════════════════════════════════════════════════
#  BUTTON HANDLERS
# ══════════════════════════════════════════════════════════════════════════
if clear_btn:
    st.session_state.results = {}
    st.session_state.running = False
    st.session_state.done = False
    st.session_state.topic_value = ""
    st.rerun()

if run_btn:
    if not topic or not topic.strip():
        alert("warning", "Please enter a research topic before running the pipeline.")
    else:
        st.session_state.topic_value = topic
        st.session_state.results = {}
        st.session_state.running = True
        st.session_state.done = False
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════
#  PIPELINE EXECUTION  (backend logic unchanged from the original app)
# ══════════════════════════════════════════════════════════════════════════
if st.session_state.running and not st.session_state.done:
    results = {}
    topic_val = st.session_state.topic_value

    try:
        # ── Step 1: Search ──
        render_step_card(pipeline_slots["search"], "01", "🔍", "Search Agent",
                          "Searching the web for recent, reliable information", "running")
        with st.spinner("Search Agent is working…"):
            search_agent = build_search_agent()
            sr = search_agent.invoke({
                "messages": [("user", f"Find recent, reliable and detailed information about: {topic_val}")]
            })
            results["search"] = sr["messages"][-1].content
            st.session_state.results = dict(results)
        render_step_card(pipeline_slots["search"], "01", "🔍", "Search Agent",
                          "Searching the web for recent, reliable information", "done")

        # ── Step 2: Reader ──
        render_step_card(pipeline_slots["reader"], "02", "📄", "Reader Agent",
                          "Scraping and extracting deeper content from top sources", "running")
        with st.spinner("Reader Agent is scraping top resources…"):
            reader_agent = build_reader_agent()
            rr = reader_agent.invoke({
                "messages": [("user",
                    f"Based on the following search results about '{topic_val}', "
                    f"pick the most relevant URL and scrape it for deeper content.\n\n"
                    f"Search Results:\n{results['search'][:800]}"
                )]
            })
            results["reader"] = rr["messages"][-1].content
            st.session_state.results = dict(results)
        render_step_card(pipeline_slots["reader"], "02", "📄", "Reader Agent",
                          "Scraping and extracting deeper content from top sources", "done")

        # ── Step 3: Writer ──
        render_step_card(pipeline_slots["writer"], "03", "✍️", "Writer Chain",
                          "Drafting a structured, detailed research report", "running")
        with st.spinner("Writer is drafting the report…"):
            research_combined = (
                f"SEARCH RESULTS:\n{results['search']}\n\n"
                f"DETAILED SCRAPED CONTENT:\n{results['reader']}"
            )
            results["writer"] = writer_chain.invoke({
                "topic": topic_val,
                "research": research_combined
            })
            st.session_state.results = dict(results)
        render_step_card(pipeline_slots["writer"], "03", "✍️", "Writer Chain",
                          "Drafting a structured, detailed research report", "done")

        # ── Step 4: Critic ──
        render_step_card(pipeline_slots["critic"], "04", "🧐", "Review Chain",
                          "Reviewing the report and scoring its quality", "running")
        with st.spinner("Critic is reviewing the report…"):
            results["critic"] = critic_chain.invoke({
                "report": results["writer"]
            })
            st.session_state.results = dict(results)
        render_step_card(pipeline_slots["critic"], "04", "🧐", "Review Chain",
                          "Reviewing the report and scoring its quality", "done")

        st.session_state.running = False
        st.session_state.done = True
        st.rerun()

    except Exception as e:
        st.session_state.running = False
        alert("error", f"Something went wrong while running the pipeline: {e}")

# ══════════════════════════════════════════════════════════════════════════
#  RESULTS DISPLAY
# ══════════════════════════════════════════════════════════════════════════
r = st.session_state.results

st.markdown('<hr class="app-divider" />', unsafe_allow_html=True)
st.markdown('<div class="section-heading">Results</div>', unsafe_allow_html=True)

if not r:
    empty_state()
else:
    if st.session_state.done:
        alert("success", "Research pipeline completed successfully.")

    # Raw agent outputs
    if "search" in r:
        with st.expander("🔍 Search Results (raw)", expanded=False):
            st.markdown(f'<div class="raw-box">{r["search"]}</div>', unsafe_allow_html=True)

    if "reader" in r:
        with st.expander("📄 Scraped Content (raw)", expanded=False):
            st.markdown(f'<div class="raw-box">{r["reader"]}</div>', unsafe_allow_html=True)

    # Final report
    if "writer" in r:
        st.markdown("""
        <div class="result-card">
            <div class="result-card-header"><h3>📝 Final Research Report</h3></div>
        """, unsafe_allow_html=True)
        st.markdown('<div class="result-scroll">', unsafe_allow_html=True)
        st.markdown(r["writer"])
        st.markdown('</div></div>', unsafe_allow_html=True)

        st.download_button(
            label="⬇ Download Report (.md)",
            data=r["writer"],
            file_name=f"research_report_{int(time.time())}.md",
            mime="text/markdown",
        )

    # Critic feedback
    if "critic" in r:
        st.markdown("""
        <div class="result-card">
            <div class="result-card-header"><h3>🧐 Critic Feedback</h3></div>
        """, unsafe_allow_html=True)
        st.markdown('<div class="result-scroll">', unsafe_allow_html=True)
        st.markdown(r["critic"])
        st.markdown('</div></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
#  FOOTER
# ══════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="app-footer">
    Built with Streamlit • LangChain • LangGraph • Multi-Agent AI
</div>
""", unsafe_allow_html=True)