import os
import sys
import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

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
    <div style="background-color:transparent; border-left:4px solid #4a9eff; padding:8px 12px; border-radius:4px; margin-bottom:8px; color: inherit;">🤖 LLM: <strong>Llama 3.3 70B (Groq)</strong></div>
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

# ── Animated solar system background (placed last so it never blocks init) ────
components.html("""
<!DOCTYPE html>
<html>
<head><style>* { margin:0; padding:0; } body { background:transparent; }</style></head>
<body>
<script>
(function() {
    const doc = window.parent.document;
    const existing = doc.getElementById('spaceCanvas');
    if (existing) existing.remove();

    const canvas = doc.createElement('canvas');
    canvas.id = 'spaceCanvas';
    canvas.style.cssText = 'position:fixed;top:0;left:0;width:100vw;height:100vh;pointer-events:none;z-index:0;';
    doc.body.appendChild(canvas);

    const ctx = canvas.getContext('2d');

    function resize() {
        canvas.width  = window.parent.innerWidth;
        canvas.height = window.parent.innerHeight;
    }
    resize();
    window.parent.addEventListener('resize', resize);

    const PLANETS = [
        { name:'Sun',     color:'#FDB813', radius:13, glow:'#ffe066' },
        { name:'Mercury', color:'#b5b5b5', radius:4,  glow:'#d0d0d0' },
        { name:'Venus',   color:'#e8cda0', radius:6,  glow:'#f5e6c8' },
        { name:'Earth',   color:'#4fa3e0', radius:6,  glow:'#a8d4f5' },
        { name:'Mars',    color:'#c1440e', radius:5,  glow:'#e8724a' },
        { name:'Jupiter', color:'#c88b3a', radius:11, glow:'#e8b96a' },
        { name:'Saturn',  color:'#e4d191', radius:9,  glow:'#f0e4b0' },
        { name:'Uranus',  color:'#7de8e8', radius:7,  glow:'#b0f0f0' },
        { name:'Neptune', color:'#3f54ba', radius:7,  glow:'#7080e0' },
    ];

    let t = Math.random() * Math.PI * 2;
    const SPEED   = 0.0006;

    const snakeOffsets = PLANETS.map((_, i) => ({
        phase: (i / PLANETS.length) * Math.PI * 2,
    }));

    function getPathPoint(time) {
        const cx = canvas.width  * 0.5
            + Math.sin(time * 1.1 + 0.5) * canvas.width  * 0.25
            + Math.sin(time * 2.3 + 1.2) * canvas.width  * 0.08
            + Math.cos(time * 0.7 + 2.1) * canvas.width  * 0.10;
        const cy = canvas.height * 0.5
            + Math.cos(time * 0.9 + 1.0) * canvas.height * 0.25
            + Math.cos(time * 1.8 + 0.3) * canvas.height * 0.08
            + Math.sin(time * 1.3 + 1.7) * canvas.height * 0.10;
        return { cx, cy };
    }

    const HISTORY_LENGTH = PLANETS.length * 80;
    const pathHistory = [];

    function updateHistory() {
        const { cx, cy } = getPathPoint(t);
        pathHistory.unshift({ x: cx, y: cy });
        if (pathHistory.length > HISTORY_LENGTH) pathHistory.pop();
    }

    function drawGlow(x, y, r, color) {
        const g = ctx.createRadialGradient(x, y, r * 0.3, x, y, r * 2.5);
        g.addColorStop(0, color + 'cc');
        g.addColorStop(1, color + '00');
        ctx.beginPath();
        ctx.arc(x, y, r * 2.5, 0, Math.PI * 2);
        ctx.fillStyle = g;
        ctx.fill();
    }

    function drawPlanet(x, y, planet) {
        drawGlow(x, y, planet.radius, planet.glow);
        ctx.beginPath();
        ctx.arc(x, y, planet.radius, 0, Math.PI * 2);
        ctx.fillStyle = planet.color;
        ctx.fill();
        if (planet.name === 'Saturn') {
            ctx.beginPath();
            ctx.ellipse(x, y, planet.radius * 2, planet.radius * 0.55, 0.4, 0, Math.PI * 2);
            ctx.strokeStyle = '#c8b560aa';
            ctx.lineWidth = 2.5;
            ctx.stroke();
        }
    }

    function drawChain() {
        if (pathHistory.length < 2) return;

        ctx.beginPath();
        for (let i = 0; i < PLANETS.length; i++) {
            const histIndex = Math.min(i * 80, pathHistory.length - 1);
            const pos = pathHistory[histIndex];
            if (i === 0) ctx.moveTo(pos.x, pos.y);
            else         ctx.lineTo(pos.x, pos.y);
        }
        ctx.strokeStyle = 'rgba(255,255,255,0.10)';
        ctx.lineWidth   = 1;
        ctx.stroke();

        for (let i = 0; i < PLANETS.length; i++) {
            const histIndex  = Math.min(i * 80, pathHistory.length - 1);
            const pos        = pathHistory[histIndex];
            const wobble     = Math.sin(t * 3.5 + snakeOffsets[i].phase) * 4;
            const tangentIdx = Math.min(histIndex + 2, pathHistory.length - 1);
            const tangent    = pathHistory[tangentIdx];
            const dx  = tangent.x - pos.x;
            const dy  = tangent.y - pos.y;
            const len = Math.sqrt(dx*dx + dy*dy) || 1;
            const wx  = pos.x + (-dy / len) * wobble;
            const wy  = pos.y + ( dx / len) * wobble;
            drawPlanet(wx, wy, PLANETS[i]);
        }
    }

    let satellite         = null;
    let lastSatelliteTime = 0;
    const SATELLITE_INTERVAL = 30000;

    function launchSatellite() {
        const edge = Math.floor(Math.random() * 4);
        let sx, sy, ex, ey;
        if (edge === 0) {
            sx = Math.random() * canvas.width;  sy = -20;
            ex = Math.random() * canvas.width;  ey = canvas.height + 20;
        } else if (edge === 1) {
            sx = canvas.width + 20; sy = Math.random() * canvas.height;
            ex = -20;               ey = Math.random() * canvas.height;
        } else if (edge === 2) {
            sx = Math.random() * canvas.width;  sy = canvas.height + 20;
            ex = Math.random() * canvas.width;  ey = -20;
        } else {
            sx = -20; sy = Math.random() * canvas.height;
            ex = canvas.width + 20; ey = Math.random() * canvas.height;
        }
        satellite = { sx, sy, ex, ey, progress:0, speed:0.0018 + Math.random()*0.001, trail:[] };
    }

    function drawSatellite() {
        if (!satellite) return;
        satellite.progress += satellite.speed;
        const x     = satellite.sx + (satellite.ex - satellite.sx) * satellite.progress;
        const y     = satellite.sy + (satellite.ey - satellite.sy) * satellite.progress;
        const angle = Math.atan2(satellite.ey - satellite.sy, satellite.ex - satellite.sx);

        satellite.trail.push({ x, y });
        if (satellite.trail.length > 28) satellite.trail.shift();

        ctx.beginPath();
        satellite.trail.forEach((p, i) => {
            ctx.strokeStyle = `rgba(200,230,255,${(i / satellite.trail.length) * 0.5})`;
            ctx.lineWidth   = 1.5;
            if (i === 0) ctx.moveTo(p.x, p.y); else ctx.lineTo(p.x, p.y);
        });
        ctx.stroke();

        ctx.save();
        ctx.translate(x, y);
        ctx.rotate(angle);
        ctx.fillStyle = '#c8d8e8';
        ctx.fillRect(-7, -3, 14, 6);
        ctx.fillStyle = '#4a7abf';
        ctx.fillRect(-14, -2, 6, 4);
        ctx.fillRect(8,   -2, 6, 4);
        ctx.beginPath();
        ctx.moveTo(0, -3);
        ctx.lineTo(0, -8);
        ctx.strokeStyle = '#ffffff99';
        ctx.lineWidth = 1;
        ctx.stroke();
        ctx.restore();

        if (satellite.progress >= 1) satellite = null;
    }

    const STARS = Array.from({ length: 120 }, () => ({
        x: Math.random(), y: Math.random(),
        r: Math.random() * 1.2 + 0.3,
        a: Math.random() * 0.6 + 0.2,
    }));

    function drawStars() {
        STARS.forEach(s => {
            ctx.beginPath();
            ctx.arc(s.x * canvas.width, s.y * canvas.height, s.r, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(255,255,255,${s.a})`;
            ctx.fill();
        });
    }

    function animate(timestamp) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        drawStars();
        t += SPEED;
        updateHistory();
        drawChain();
        if (!satellite && timestamp - lastSatelliteTime >= SATELLITE_INTERVAL) {
            launchSatellite();
            lastSatelliteTime = timestamp;
        }
        if (!satellite && lastSatelliteTime === 0 && timestamp > 8000) {
            launchSatellite();
            lastSatelliteTime = timestamp;
        }
        drawSatellite();
        window.parent.requestAnimationFrame(animate);
    }

    window.parent.requestAnimationFrame(animate);
})();
</script>
</body>
</html>
""", height=1, scrolling=False)