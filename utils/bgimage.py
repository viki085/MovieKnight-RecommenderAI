import base64
import streamlit as st
import os

def set_background(image_file: str):

    # Convert to absolute path
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    full_path = os.path.join(base_dir, image_file)

    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Background image not found at {full_path}")

    with open(full_path, "rb") as f:
        data = f.read()

    encoded = base64.b64encode(data).decode()

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
