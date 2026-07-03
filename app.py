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


def inject_space_background():
    st.markdown("""
    <style>
    /* ================================
        Streamlit app transparency setup
       ================================ */
    .stApp {
        background: transparent !important;
    }

    [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(circle at 20% 20%, rgba(15, 30, 60, 0.35), transparent 35%),
            radial-gradient(circle at 80% 30%, rgba(60, 20, 80, 0.25), transparent 30%),
            radial-gradient(circle at 50% 80%, rgba(0, 40, 80, 0.25), transparent 35%),
            linear-gradient(180deg, #030712 0%, #07111f 45%, #02050d 100%) !important;
    }

    [data-testid="stHeader"] {
        background: transparent !important;
    }

    [data-testid="stSidebar"] {
        background: rgba(4, 10, 20, 0.72) !important;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255,255,255,0.06);
    }

    /* Make the main block float nicely over the animation */
    .main .block-container {
        position: relative;
        z-index: 2;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    /* Optional: soften chat message backgrounds */
    [data-testid="stChatMessage"] {
        background: rgba(10, 18, 30, 0.55);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 16px;
        backdrop-filter: blur(6px);
        -webkit-backdrop-filter: blur(6px);
    }

    /* ================================
        Fixed animated space background
       ================================ */
    .space-scene {
        position: fixed;
        inset: 0;
        overflow: hidden;
        pointer-events: none;
        z-index: 0;
    }

    /* twinkling stars layer */
    .stars, .stars2, .stars3 {
        position: absolute;
        inset: 0;
        background-repeat: repeat;
        opacity: 0.9;
    }

    .stars {
        background-image:
            radial-gradient(2px 2px at 20px 30px, rgba(255,255,255,0.95), transparent 50%),
            radial-gradient(1.5px 1.5px at 90px 140px, rgba(255,255,255,0.85), transparent 50%),
            radial-gradient(1.8px 1.8px at 160px 70px, rgba(255,255,255,0.9), transparent 50%),
            radial-gradient(1.2px 1.2px at 260px 180px, rgba(255,255,255,0.7), transparent 50%),
            radial-gradient(2px 2px at 340px 60px, rgba(255,255,255,0.95), transparent 50%);
        background-size: 400px 220px;
        animation: driftStars 110s linear infinite;
    }

    .stars2 {
        background-image:
            radial-gradient(1.6px 1.6px at 60px 80px, rgba(173,216,255,0.8), transparent 50%),
            radial-gradient(1.2px 1.2px at 180px 150px, rgba(255,255,255,0.7), transparent 50%),
            radial-gradient(2px 2px at 300px 40px, rgba(255,255,255,0.85), transparent 50%),
            radial-gradient(1.4px 1.4px at 360px 190px, rgba(200,220,255,0.7), transparent 50%);
        background-size: 420px 240px;
        animation: driftStarsReverse 150s linear infinite;
        opacity: 0.55;
    }

    .stars3 {
        background-image:
            radial-gradient(1px 1px at 30px 40px, rgba(255,255,255,0.7), transparent 50%),
            radial-gradient(1px 1px at 130px 100px, rgba(255,255,255,0.55), transparent 50%),
            radial-gradient(1px 1px at 230px 50px, rgba(255,255,255,0.65), transparent 50%),
            radial-gradient(1px 1px at 330px 170px, rgba(255,255,255,0.55), transparent 50%);
        background-size: 380px 210px;
        animation: twinkle 6s ease-in-out infinite alternate;
        opacity: 0.45;
    }

    /* Planets */
    .planet {
        position: absolute;
        border-radius: 50%;
        filter: drop-shadow(0 0 12px rgba(255,255,255,0.08));
        will-change: transform;
    }

    .planet::after {
        content: "";
        position: absolute;
        inset: 8%;
        border-radius: 50%;
        background: radial-gradient(circle at 30% 30%, rgba(255,255,255,0.35), transparent 45%);
        pointer-events: none;
    }

    .planet1 {
        width: 72px;
        height: 72px;
        top: 14%;
        left: -8%;
        background: radial-gradient(circle at 30% 30%, #9ad7ff 0%, #4e7cff 45%, #22347e 100%);
        animation: floatPlanet1 34s ease-in-out infinite alternate;
        opacity: 0.9;
    }

    .planet2 {
        width: 120px;
        height: 120px;
        top: 58%;
        left: 78%;
        background: radial-gradient(circle at 35% 35%, #ffd27a 0%, #d88135 50%, #6b2c11 100%);
        animation: floatPlanet2 42s ease-in-out infinite alternate;
        opacity: 0.85;
    }

    .planet3 {
        width: 54px;
        height: 54px;
        top: 72%;
        left: 6%;
        background: radial-gradient(circle at 35% 35%, #d6c1ff 0%, #8f71ff 48%, #35246d 100%);
        animation: floatPlanet3 28s ease-in-out infinite alternate;
        opacity: 0.8;
    }

    .planet4 {
        width: 88px;
        height: 88px;
        top: 22%;
        left: 72%;
        background: radial-gradient(circle at 35% 35%, #b6ffd7 0%, #36b37e 48%, #0b4f3b 100%);
        animation: floatPlanet4 38s ease-in-out infinite alternate;
        opacity: 0.72;
    }

    /* Ringed planet */
    .planet5 {
        width: 96px;
        height: 96px;
        top: 42%;
        left: 32%;
        background: radial-gradient(circle at 35% 35%, #ffe9b8 0%, #caa26b 52%, #6a4c28 100%);
        animation: floatPlanet5 46s ease-in-out infinite alternate;
        opacity: 0.78;
    }

    .planet5::before {
        content: "";
        position: absolute;
        width: 140%;
        height: 30%;
        top: 36%;
        left: -20%;
        border-radius: 50%;
        border: 3px solid rgba(255, 232, 180, 0.35);
        transform: rotate(-18deg);
    }

    /* Satellite */
    .satellite {
        position: absolute;
        top: 18%;
        left: -16%;
        width: 62px;
        height: 20px;
        animation: satelliteFly 20s linear infinite;
        opacity: 0.92;
        will-change: transform, opacity;
    }

    .satellite-body {
        position: absolute;
        left: 20px;
        top: 5px;
        width: 22px;
        height: 10px;
        border-radius: 4px;
        background: linear-gradient(180deg, #dce6f5 0%, #8b97aa 100%);
        box-shadow: 0 0 10px rgba(255,255,255,0.12);
    }

    .satellite-panel-left,
    .satellite-panel-right {
        position: absolute;
        top: 2px;
        width: 18px;
        height: 16px;
        border-radius: 2px;
        background: linear-gradient(180deg, #4dc3ff 0%, #183d70 100%);
        box-shadow: inset 0 0 0 1px rgba(255,255,255,0.12);
    }

    .satellite-panel-left { left: 0; }
    .satellite-panel-right { right: 0; }

    .satellite-antenna {
        position: absolute;
        left: 28px;
        top: -2px;
        width: 2px;
        height: 8px;
        background: #cfd8e3;
    }

    /* Subtle nebula glows */
    .nebula {
        position: absolute;
        border-radius: 50%;
        filter: blur(40px);
        opacity: 0.16;
        will-change: transform;
    }

    .nebula1 {
        width: 300px;
        height: 220px;
        top: 10%;
        left: 60%;
        background: rgba(96, 82, 255, 0.35);
        animation: nebulaPulse1 18s ease-in-out infinite alternate;
    }

    .nebula2 {
        width: 260px;
        height: 180px;
        top: 60%;
        left: 12%;
        background: rgba(0, 173, 239, 0.28);
        animation: nebulaPulse2 22s ease-in-out infinite alternate;
    }

    /* Keyframes */
    @keyframes driftStars {
        from { transform: translate3d(0, 0, 0); }
        to   { transform: translate3d(-220px, -120px, 0); }
    }

    @keyframes driftStarsReverse {
        from { transform: translate3d(0, 0, 0); }
        to   { transform: translate3d(180px, 100px, 0); }
    }

    @keyframes twinkle {
        0%   { opacity: 0.25; }
        50%  { opacity: 0.5; }
        100% { opacity: 0.75; }
    }

    @keyframes floatPlanet1 {
        0%   { transform: translate(0vw, 0vh) scale(1); }
        25%  { transform: translate(18vw, 8vh) scale(1.04); }
        50%  { transform: translate(36vw, -2vh) scale(0.98); }
        75%  { transform: translate(58vw, 10vh) scale(1.03); }
        100% { transform: translate(78vw, 2vh) scale(1); }
    }

    @keyframes floatPlanet2 {
        0%   { transform: translate(0vw, 0vh) scale(1); }
        25%  { transform: translate(-10vw, -10vh) scale(1.02); }
        50%  { transform: translate(-26vw, 8vh) scale(0.98); }
        75%  { transform: translate(-42vw, -14vh) scale(1.03); }
        100% { transform: translate(-58vw, 4vh) scale(1); }
    }

    @keyframes floatPlanet3 {
        0%   { transform: translate(0vw, 0vh) scale(1); }
        33%  { transform: translate(22vw, -8vh) scale(1.04); }
        66%  { transform: translate(40vw, 6vh) scale(0.96); }
        100% { transform: translate(58vw, -4vh) scale(1); }
    }

    @keyframes floatPlanet4 {
        0%   { transform: translate(0vw, 0vh) scale(1); }
        25%  { transform: translate(-12vw, 7vh) scale(0.98); }
        50%  { transform: translate(-28vw, -7vh) scale(1.03); }
        75%  { transform: translate(-18vw, 12vh) scale(0.99); }
        100% { transform: translate(-36vw, -2vh) scale(1.02); }
    }

    @keyframes floatPlanet5 {
        0%   { transform: translate(0vw, 0vh) scale(1) rotate(0deg); }
        25%  { transform: translate(12vw, -6vh) scale(1.02) rotate(2deg); }
        50%  { transform: translate(24vw, 10vh) scale(0.98) rotate(-2deg); }
        75%  { transform: translate(44vw, 4vh) scale(1.02) rotate(1deg); }
        100% { transform: translate(58vw, -8vh) scale(1) rotate(-1deg); }
    }

    @keyframes satelliteFly {
        0% {
            transform: translate(-10vw, 0vh) rotate(8deg);
            opacity: 0;
        }
        8% {
            opacity: 0.92;
        }
        30% {
            transform: translate(30vw, 8vh) rotate(10deg);
            opacity: 0.95;
        }
        65% {
            transform: translate(75vw, 16vh) rotate(12deg);
            opacity: 0.9;
        }
        92% {
            opacity: 0.8;
        }
        100% {
            transform: translate(126vw, 24vh) rotate(14deg);
            opacity: 0;
        }
    }

    @keyframes nebulaPulse1 {
        0%   { transform: scale(1) translate(0, 0); opacity: 0.12; }
        100% { transform: scale(1.15) translate(-20px, 10px); opacity: 0.2; }
    }

    @keyframes nebulaPulse2 {
        0%   { transform: scale(1) translate(0, 0); opacity: 0.1; }
        100% { transform: scale(1.2) translate(15px, -10px); opacity: 0.18; }
    }
    </style>

    <div class="space-scene">
        <div class="stars"></div>
        <div class="stars2"></div>
        <div class="stars3"></div>
        <div class="planet planet1"></div>
        <div class="planet planet2"></div>
        <div class="planet planet3"></div>
        <div class="planet planet4"></div>
        <div class="planet planet5"></div>
        <div class="satellite">
            <div class="satellite-panel-left"></div>
            <div class="satellite-body"></div>
            <div class="satellite-panel-right"></div>
            <div class="satellite-antenna"></div>
        </div>
        <div class="nebula nebula1"></div>
        <div class="nebula nebula2"></div>
    </div>
    """, unsafe_allow_html=True)


inject_space_background()


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
    st.image("https://upload.wikimedia.org/wikipedia/commons/e/e5/NASA_logo.svg", width=120)
    st.markdown("## 🚀 NASA Space Science RAG Chatbot")
    st.markdown("Ask anything about NASA space science — planets, moons, the universe, astrophysics, and more.")
    st.markdown("---")

    # ── Project stats ──────────────────────────────────────────────────────────
    st.markdown("### 📊 Project Stats")
    st.markdown(f"""
    <div style="background-color:transparent; border-left:4px solid #4a9eff; padding:8px 12px; border-radius:4px; margin-bottom:8px; color: inherit;">📄 Pages scraped: <strong>{page_count}</strong></div>
    <div style="background-color:transparent; border-left:4px solid #4a9eff; padding:8px 12px; border-radius:4px; margin-bottom:8px; color: inherit;">💬 Q&A pairs generated: <strong>{qa_count}</strong></div>
    <div style="background-color:transparent; border-left:4px solid #4a9eff; padding:8px 12px; border-radius:4px; margin-bottom:8px; color: inherit;">🌐 Source: <strong>science.nasa.gov</strong></div>
    <div style="background-color:transparent; border-left:4px solid #4a9eff; padding:8px 12px; border-radius:4px; margin-bottom:8px; color: inherit;">🤖 LLM: <strong>GPT-OSS 120B (Groq)</strong></div>
    <div style="background-color:transparent; border-left:4px solid #4a9eff; padding:8px 12px; border-radius:4px; margin-bottom:8px; color: inherit;">🧠 Embeddings: <strong>all-MiniLM-L6-v2</strong></div>
    <div style="background-color:transparent; border-left:4px solid #4a9eff; padding:8px 12px; border-radius:4px; margin-bottom:8px; color: inherit;">🗄️ Vector DB: <strong>ChromaDB</strong></div>
    """, unsafe_allow_html=True)

    st.markdown("---")

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

    st.markdown("---")

    # ── Upload new questions ───────────────────────────────────────────────────
    st.markdown("### 📤 Upload New Questions")
    st.markdown(
        "<div style='font-size:0.82rem; color:#888; margin-bottom:8px;'>"
        "Upload a .csv or .txt file with one question per line or a "
        "<b>question</b> column. The chatbot will answer each one.</div>",
        unsafe_allow_html=True
    )

    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["csv", "txt"],
        help="CSV with a 'question' column, or a plain .txt with one question per line"
    )

    if uploaded_file is not None:
        # ── Parse uploaded file ────────────────────────────────────────────────
        try:
            if uploaded_file.name.endswith(".csv"):
                upload_df = pd.read_csv(uploaded_file)
                if "question" not in upload_df.columns:
                    st.error("❌ CSV must have a column named 'question'")
                    upload_df = pd.DataFrame()
            else:
                # Plain .txt — one question per line
                lines = uploaded_file.read().decode("utf-8").splitlines()
                questions = [l.strip() for l in lines if len(l.strip()) > 5]
                upload_df = pd.DataFrame({"question": questions})

        except Exception as e:
            st.error(f"❌ Could not read file: {e}")
            upload_df = pd.DataFrame()

        if not upload_df.empty:
            questions_list = upload_df["question"].dropna().tolist()
            st.success(f"✅ Found {len(questions_list)} question(s)")

            # Show preview of uploaded questions
            with st.expander("👀 Preview uploaded questions"):
                for i, q in enumerate(questions_list[:10], 1):
                    st.markdown(f"**{i}.** {q}")
                if len(questions_list) > 10:
                    st.markdown(f"*... and {len(questions_list) - 10} more*")

            # ── Run all questions through the chatbot ──────────────────────────
            if st.button("🤖 Answer All Questions", use_container_width=True, type="primary"):
                results = []
                progress = st.progress(0, text="Answering questions...")

                for i, question in enumerate(questions_list):
                    try:
                        result = st.session_state.chatbot.ask(question)
                        results.append({
                            "question": question,
                            "answer":   result["answer"],
                            "source":   result["source"],
                            "confidence": result["confidence"],
                        })
                    except Exception as e:
                        results.append({
                            "question":   question,
                            "answer":     f"Error: {e}",
                            "source":     "error",
                            "confidence": 0,
                        })
                    progress.progress(
                        (i + 1) / len(questions_list),
                        text=f"Answering {i+1}/{len(questions_list)}..."
                    )

                progress.empty()
                st.success(f"✅ Answered {len(results)} questions!")

                # Display results
                results_df = pd.DataFrame(results)
                st.dataframe(results_df, use_container_width=True, height=300)

                # Download button for results
                csv_output = results_df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="⬇️ Download Answers as CSV",
                    data=csv_output,
                    file_name="answered_questions.csv",
                    mime="text/csv",
                    use_container_width=True,
                )


# ══════════════════════════════════════════════════════════════════════════════
# MAIN CHAT AREA
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="main-header">🚀 NASA Space Science Chatbot</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Powered by RAG · science.nasa.gov · Groq GPT-OSS 120B</div>', unsafe_allow_html=True)

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