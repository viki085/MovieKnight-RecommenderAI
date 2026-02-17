import streamlit as st
from pipeline.pipeline import MovieRecommendationPipeline
from dotenv import load_dotenv

st.set_page_config(page_title="Anime Recommnder",layout="wide")

load_dotenv()

@st.cache_resource
def init_pipeline():
    return MovieRecommendationPipeline()

pipeline = init_pipeline()

st.title("AI Movie Recommender")
st.write("LEts go !!!")

query = st.text_input("Enter your movie preferences eg. : Action movies with space theme")
if query:
    with st.spinner("Fetching recommendations for you....."):
        response = pipeline.recommend(query)
        st.markdown("### Recommendations")
        st.write(response)