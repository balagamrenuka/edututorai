import os
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai
import sqlite3  # ✅ Required for get_db_connection()

# Load environment variables from .env file
load_dotenv()

# Database path (for user accounts)
DB_PATH = os.getenv("DB_PATH", "users.db")

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / 'data'
    DATABASE_URI = str(DATA_DIR / 'quiz.db')  # ✅ For quiz DB

    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
    GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')

    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    BASE_URL = os.getenv('BASE_URL', 'http://localhost:8501')

    @classmethod
    def ensure_data_dir(cls):
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)

# Ensure the data directory exists
Config.ensure_data_dir()

# Configure Gemini if API key is present
if Config.GEMINI_API_KEY:
    genai.configure(api_key=Config.GEMINI_API_KEY)

# ✅ Function to get SQLite DB connection
def get_db_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)
