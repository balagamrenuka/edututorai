import google.generativeai as genai
from config import Config

# Configure Gemini
genai.configure(api_key=Config.GEMINI_API_KEY)

def ask_ai(prompt):
    try:
        model = genai.GenerativeModel("gemini-pro")  # or gemini-1.5-pro
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ Gemini Error: {str(e)}"