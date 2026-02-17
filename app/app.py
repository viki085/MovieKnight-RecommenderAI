import streamlit as st
from pathlib import Path
from pipeline.pipeline import MovieRecommendationPipeline
from dotenv import load_dotenv

# ---------------------------------------------------
# Page Config
# ---------------------------------------------------
st.set_page_config(
    page_title="MovieKnight AI",
    page_icon="🎬",
    layout="wide"
)

load_dotenv()

# ---------------------------------------------------
# Cinematic Black Theme
# ---------------------------------------------------
st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');

.stApp {
    background: radial-gradient(circle at top left, #111111 0%, #000000 65%);
    color: white;
}

html, body, [class*="css"] {
    font-family: 'Orbitron', sans-serif;
}

.main-title {
    font-size: 3rem;
    font-weight: 700;
    text-align: center;
    background: linear-gradient(90deg, #ff2e63, #08d9d6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.5rem;
}

.subtitle {
    text-align: center;
    color: #aaaaaa;
    font-size: 1.1rem;
    margin-bottom: 2rem;
}

section[data-testid="stSidebar"] {
    background-color: #0d0d0d;
    border-right: 1px solid #222;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# Initialize Pipeline
# ---------------------------------------------------
@st.cache_resource
def init_pipeline():
    return MovieRecommendationPipeline()

pipeline = init_pipeline()

# ---------------------------------------------------
# Initialize Session State (CRITICAL)
# ---------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "🦇 Welcome to MovieKnight AI.\nTell me what kind of movie you're in the mood for..."
        }
    ]

# ---------------------------------------------------
# Sidebar
# ---------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
joker_path = BASE_DIR / "imgs" / "joker.jfif"

with st.sidebar:
    st.title("🎬 Control Panel")

    if joker_path.exists():
        st.image(str(joker_path), width='stretch')

    st.markdown("---")

    if st.button("Clear Conversation", width='stretch'):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "🦇 Conversation cleared. What shall we watch tonight?"
            }
        ]
        st.rerun()

    st.markdown("### 💡 Try asking:")
    st.info(
        "- Dark psychological thrillers\n"
        "- Movies like Interstellar\n"
        "- Crime dramas like The Godfather\n"
        "- Space sci-fi adventures"
    )

    st.markdown("---")
    st.caption("MovieKnight AI | Agentic RAG System")

# ---------------------------------------------------
# Main UI
# ---------------------------------------------------
st.markdown('<div class="main-title">MovieKnight AI</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">The Dark Intelligence of Cinema</div>', unsafe_allow_html=True)

# ---------------------------------------------------
# Display Chat History
# ---------------------------------------------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ---------------------------------------------------
# Handle User Input
# ---------------------------------------------------
if prompt := st.chat_input("What are you in the mood for tonight?"):

    # Show user message
    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    # Generate assistant response
    with st.chat_message("assistant"):
        with st.spinner("Summoning cinematic intelligence..."):
            try:
                response = pipeline.recommend(prompt)
                st.markdown(response)
            except Exception as e:
                response = f"⚠️ Error: {str(e)}"
                st.error(response)

    st.session_state.messages.append(
        {"role": "assistant", "content": response}
    )
