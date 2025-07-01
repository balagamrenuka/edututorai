import os
import google.generativeai as genai
from config import Config

genai.configure(api_key=Config.OPENAI_API_KEY)

def query_gemini(prompt):
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ Gemini Error: {str(e)}"
