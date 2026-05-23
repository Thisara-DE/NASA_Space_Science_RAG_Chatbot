import os
import sys
import streamlit as st
import pandas as pd

# ── Make sure src/ is on the path so we can import chatbot ────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from chatbot import NASAChatbot

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NASA Space Science Chatbot",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(__file__)
QA_CSV   = os.path.join(BASE_DIR, 'data', 'qa_dataset.csv')
RAW_DIR  = os.path.join(BASE_DIR, 'data', 'raw')

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: 700;
        color: #1a73e8;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 0.95rem;
        color: #666;
        margin-bottom: 1.5rem;
    }
    .source-badge-qa {
        background-color: #e8f5e9;
        color: #2e7d32;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.78rem;
        font-weight: 600;
    }
    .source-badge-doc {
        background-color: #e3f2fd;
        color: #1565c0;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.78rem;
        font-weight: 600;
    }
    .confidence-text {
        font-size: 0.78rem;
        color: #888;
        margin-top: 4px;
    }
    .stat-box {
        background-color: #f8f9fa;
        border-left: 4px solid #1a73e8;
        padding: 8px 12px;
        border-radius: 4px;
        margin-bottom: 8px;
    }
    .sample-question {
        cursor: pointer;
        padding: 6px 10px;
        background: #f0f4ff;
        border-radius: 8px;
        margin-bottom: 6px;
        font-size: 0.88rem;
        border: 1px solid #d0d9ff;
    }
</style>
""", unsafe_allow_html=True)


# ── Load stats ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_stats():
    qa_count   = 0
    page_count = 0
    qa_df      = pd.DataFrame()

    if os.path.exists(QA_CSV):
        qa_df    = pd.read_csv(QA_CSV)
        qa_count = len(qa_df)

    if os.path.exists(RAW_DIR):
        page_count = len([f for f in os.listdir(RAW_DIR) if f.endswith('.txt')])

    return qa_count, page_count, qa_df


qa_count, page_count, qa_df = load_stats()


# ── Initialise chatbot (cached so it only loads once) ──────────────────────────
@st.cache_resource
def load_chatbot():
    return NASAChatbot()


# ── Session state ──────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []   # [{role, content, meta}]
if "chatbot" not in st.session_state:
    st.session_state.chatbot = load_chatbot()


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    # ── Theme toggle ───────────────────────────────────────────────────────────
    if "theme" not in st.session_state:
        st.session_state.theme = "System default"

    theme = st.selectbox(
        "🎨 Theme",
        options=["System default", "Light", "Dark"],
        index=["System default", "Light", "Dark"].index(st.session_state.theme),
        key="theme_select",
    )
    st.session_state.theme = theme

    if theme == "Dark":
        st.markdown("""
        <style>
            [data-testid="stAppViewContainer"] { background-color: #0e1117; color: #fafafa; }
            [data-testid="stSidebar"] { background-color: #161b22; }
            .stat-box { background-color: #1e2530; border-left-color: #4a9eff; }
            .sample-question { background: #1e2530; border-color: #2d3a4a; color: #fafafa; }
            .main-header { color: #4a9eff; }
            .sub-header { color: #aaa; }
        </style>
        """, unsafe_allow_html=True)
    elif theme == "Light":
        st.markdown("""
        <style>
            [data-testid="stAppViewContainer"] { background-color: #ffffff; color: #111; }
            [data-testid="stSidebar"] { background-color: #f8f9fa; }
            .stat-box { background-color: #f0f4ff; border-left-color: #1a73e8; }
            .sample-question { background: #f0f4ff; border-color: #d0d9ff; color: #111; }
            .main-header { color: #1a73e8; }
            .sub-header { color: #555; }
        </style>
        """, unsafe_allow_html=True)
    # System default → no overrides, Streamlit uses whatever the OS theme is

    st.markdown("---")
    st.image("https://upload.wikimedia.org/wikipedia/commons/e/e5/NASA_logo.svg", width=120)

    # ── Website link ───────────────────────────────────────────────────────────
    st.markdown("### 🔗 Source Website")
    st.markdown("[NASA Space Science](https://science.nasa.gov)", unsafe_allow_html=True)

    st.markdown("---")

    # ── Sample questions ───────────────────────────────────────────────────────
    # ── Sample questions (pulled directly from qa_dataset.csv) ─────────────────
    st.markdown("### 💡 Sample Questions")

    if not qa_df.empty:
        # Pick 8 random questions from the actual dataset, refresh each session
        if "sample_questions" not in st.session_state:
            st.session_state.sample_questions = (
                qa_df["question"]
                .dropna()
                .sample(n=min(8, len(qa_df)), random_state=None)
                .tolist()
            )

        for q in st.session_state.sample_questions:
            # Truncate long questions so they fit neatly in the sidebar
            label = q if len(q) <= 80 else q[:77] + "..."
            if st.button(label, key=f"sample_{q}", use_container_width=True):
                st.session_state["pending_question"] = q

        # Refresh button to get a new random set of 8 questions
        if st.button("🔄 Refresh questions", use_container_width=True):
            del st.session_state["sample_questions"]
            st.rerun()
    else:
        st.info("No Q&A dataset found. Run qa_generator.py first.")

    st.markdown("---")

    # ── Clear chat ─────────────────────────────────────────────────────────────
    if st.button("🗑️ Clear Chat", use_container_width=True, type="secondary"):
        st.session_state.messages = []
        st.session_state.chatbot.clear_history()
        st.rerun()

    st.markdown("---")

    # ── Sample Q&A viewer ──────────────────────────────────────────────────────
    st.markdown("### 📋 Browse Q&A Dataset")
    if not qa_df.empty:
        show_qa = st.checkbox("Show sample Q&A pairs")
        if show_qa:
            sample_n = st.slider("Number of pairs to show", 3, 20, 5)
            st.dataframe(
                qa_df[["question", "answer"]].head(sample_n),
                use_container_width=True,
                height=300,
            )


# ══════════════════════════════════════════════════════════════════════════════
# MAIN CHAT AREA
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="main-header">🚀 NASA Space Science Chatbot</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Powered by RAG · science.nasa.gov · Groq LLaMA 3.3 70B</div>', unsafe_allow_html=True)

st.markdown("""
<div style="
    background: linear-gradient(135deg, #e8f0fe, #e3f2fd);
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 20px;
    border-left: 5px solid #1a73e8;
">
    <div style="font-weight: 700; font-size: 1rem; color: #1a73e8; margin-bottom: 10px;">
        📚 What can I help you with?
    </div>
    <div style="font-size: 0.9rem; color: #333; line-height: 1.8;">
        This chatbot has been trained on NASA Space Science content covering:
        <br><br>
        🪐 <b>Planets</b> — Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, Neptune<br>
        ☀️ <b>The Sun</b> — solar activity, heliophysics, solar wind<br>
        🌙 <b>Moons & Small Bodies</b> — moons, asteroids, comets<br>
        🌌 <b>The Universe</b> — galaxies, black holes, astrophysics<br>
        🌍 <b>Earth Science</b> — Earth observation, climate, atmosphere<br>
        🔭 <b>Planetary Science</b> — formation, exploration missions<br>
        <br>
        <span style="color: #555; font-size: 0.85rem;">
        💡 <i>Tip: Ask specific questions like "Tell me about the Great Red Spot on Jupiter." 
        or "What is a Black hole?" for best results.</i>
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Display chat history ───────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

        # Show source citation for assistant messages
        if msg["role"] == "assistant" and "meta" in msg:
            meta = msg["meta"]
            source_label = "Q&A Match" if meta.get("source") == "qa" else "Document Search"
            badge_class  = "source-badge-qa" if meta.get("source") == "qa" else "source-badge-doc"

            col1, col2 = st.columns([1, 3])
            with col1:
                st.markdown(
                    f'<span class="{badge_class}">📌 {source_label}</span>',
                    unsafe_allow_html=True
                )
            with col2:
                if meta.get("doc_sources"):
                    sources_str = " · ".join(meta["doc_sources"][:2])
                    st.markdown(
                        f'<div class="confidence-text">🔗 {sources_str}</div>',
                        unsafe_allow_html=True
                    )

            if meta.get("matched_qa"):
                with st.expander("📎 Matched Q&A pair"):
                    st.markdown(f"**Q:** {meta['matched_qa']['question']}")
                    st.markdown(f"**A:** {meta['matched_qa']['answer']}")
                    st.markdown(f"**Source:** {meta['matched_qa'].get('source', 'N/A')}")

            st.markdown(
                f'<div class="confidence-text">Confidence: {meta.get("confidence", "N/A")}</div>',
                unsafe_allow_html=True
            )


# ── Handle sample question clicks ─────────────────────────────────────────────
pending = st.session_state.pop("pending_question", None)

# ── Chat input ─────────────────────────────────────────────────────────────────
user_input = st.chat_input("Ask me anything about NASA space science...") or pending

if user_input:
    # Show user message
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Searching NASA knowledge base..."):
            result = st.session_state.chatbot.ask(user_input)

        st.markdown(result["answer"])

        # Source citation
        source_label = "Q&A Match" if result["source"] == "qa" else "Document Search"
        badge_class  = "source-badge-qa" if result["source"] == "qa" else "source-badge-doc"

        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown(
                f'<span class="{badge_class}">📌 {source_label}</span>',
                unsafe_allow_html=True
            )
        with col2:
            if result["doc_sources"]:
                sources_str = " · ".join(result["doc_sources"][:2])
                st.markdown(
                    f'<div class="confidence-text">🔗 {sources_str}</div>',
                    unsafe_allow_html=True
                )

        if result["matched_qa"]:
            with st.expander("📎 Matched Q&A pair"):
                st.markdown(f"**Q:** {result['matched_qa']['question']}")
                st.markdown(f"**A:** {result['matched_qa']['answer']}")
                st.markdown(f"**Source:** {result['matched_qa'].get('source', 'N/A')}")

        st.markdown(
            f'<div class="confidence-text">Confidence: {result["confidence"]}</div>',
            unsafe_allow_html=True
        )

    # Save to session
    st.session_state.messages.append({
        "role":    "assistant",
        "content": result["answer"],
        "meta":    {
            "source":      result["source"],
            "matched_qa":  result["matched_qa"],
            "doc_sources": result["doc_sources"],
            "confidence":  result["confidence"],
        }
    })