import streamlit as st
import sqlite3
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests
import os
from dotenv import load_dotenv
from config import get_db_connection

load_dotenv()


class AuthSystem:
    def __init__(self):
        self.conn = get_db_connection()
        self.create_users_table()

    def create_users_table(self):
        self.conn.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT,
            email TEXT,
            role TEXT
        )''')
        self.conn.commit()

    def register_user(self, username, password, email, role):
        try:
            self.conn.execute("INSERT INTO users (username, password, email, role) VALUES (?, ?, ?, ?)",
                              (username, password, email, role))
            self.conn.commit()
            return True
        except Exception as e:
            st.error(f"Registration failed: {e}")
            return False

    def authenticate_user(self, username, password):
        cursor = self.conn.execute("SELECT * FROM users WHERE username = ? AND password = ?",
                                   (username, password))
        return cursor.fetchone()

    def login_with_google(self):
        client_id = os.getenv("GOOGLE_CLIENT_ID")
        client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        redirect_uri = "http://localhost:8501"

        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [redirect_uri],
                }
            },
            scopes=["https://www.googleapis.com/auth/userinfo.profile",
                    "https://www.googleapis.com/auth/userinfo.email", "openid"],
        )
        flow.redirect_uri = redirect_uri

        if "code" not in st.query_params:
            auth_url, _ = flow.authorization_url(prompt='consent')
            st.markdown(
                f'<a href="{auth_url}" target="_self"><button style="background-color:#0f9d58; color:white; padding:10px 16px; font-size:16px; border:none; border-radius:8px;">🔐 Login with Google</button></a>',
                unsafe_allow_html=True
            )
            return None

        try:
            flow.fetch_token(code=st.query_params["code"])
            credentials = flow.credentials
            request = requests.Request()
            id_info = id_token.verify_oauth2_token(credentials._id_token, request, client_id)

            user_info = {
                "name": id_info["name"],
                "email": id_info["email"],
                "picture": id_info["picture"],
                "role": "student"
            }

            st.session_state.user_info = user_info
            return user_info
        except Exception as e:
            st.error(f"Google login failed: {e}")
            return None

    def show_login_form(self):
        st.subheader("🔐 Login")
        login_method = st.radio("Choose Login Method", ("Local Account", "Login with Google"))

        if login_method == "Login with Google":
            return self.login_with_google()

        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login"):
            user = self.authenticate_user(username, password)
            if user:
                st.success("Login successful")
                st.session_state.user_info = {
                    "username": user[1],
                    "email": user[3],
                    "role": user[4]
                }
                return st.session_state.user_info
            else:
                st.error("Invalid credentials")

        return None

    def show_registration_form(self):
        st.subheader("📝 Register")
        username = st.text_input("Username", key="reg_username")
        email = st.text_input("Email", key="reg_email")
        password = st.text_input("Password", type="password", key="reg_password")
        role = st.radio("Role", ("student", "teacher"))
        if st.button("Register"):
            success = self.register_user(username, password, email, role)
            if success:
                st.success("Registration successful. Please login.")

    def get_user_info(self):
        return st.session_state.get("user_info", None)
