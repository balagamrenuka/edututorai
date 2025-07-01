import streamlit as st
from PIL import Image
import os

def set_modern_theme():
    st.set_page_config(
        page_title="EduTutor AI",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.markdown("""
    <style>
        :root {
            --primary: #4a6fa5;
            --secondary: #166088;
            --accent: #4fc3f7;
            --background: #f8f9fa;
            --card: #ffffff;
            --text: #333333;
        }
        
        .stApp {
            background-color: var(--background);
            color: var(--text);
        }
        
        .st-emotion-cache-1y4p8pa {
            background-color: var(--card);
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            padding: 1.5rem;
            margin-bottom: 1rem;
        }
        
        .st-emotion-cache-7ym5gk {
            background-color: var(--secondary) !important;
            color: white !important;
            border-radius: 8px !important;
            font-weight: 500 !important;
        }
        
        .pdf-qa-card {
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            background-color: white;
        }
    </style>
    """, unsafe_allow_html=True)

def show_image_showcase(image_path, caption=None):
    try:
        image = Image.open(image_path)
        st.image(image, use_column_width=True, caption=caption)
    except Exception as e:
        st.error(f"Error loading image: {str(e)}")