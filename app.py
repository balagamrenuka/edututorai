import streamlit as st
from auth import AuthSystem
from quiz import QuizEngine
from analytics import AnalyticsDashboard
from modules.pdf_qa import PDFQASystem
from modules.ask_ai import AskAI
from config import Config
from database import init_db
import base64
from pathlib import Path
from ai_helper import ask_ai as ask_ai_func
from datetime import datetime
import json
import os
import logging

user_info = None

def ensure_background_image():
    try:
        img_path = Path(__file__).parent / 'assets' / 'image_classification.png'
        if img_path.exists():
            with open(img_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode()
            bg_image = f"url('data:image/png;base64,{encoded_string}')"
        else:
            raise FileNotFoundError
    except Exception:
        bg_image = "url('https://images.unsplash.com/photo-1523050854058-8df90110c9f1')"
        st.warning("Using default background")

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: linear-gradient(rgba(255,255,255,0.95), rgba(255,255,255,0.95)), 
                              {bg_image};
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        .main .block-container {{
            background-color: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 3rem;
            margin-top: 2rem;
        }}
        .stButton>button {{
            background-color: #4a6fa5 !important;
            color: white;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

def setup_file_watching():
    """Configure file watching behavior"""
    logging.getLogger('watchdog').setLevel(logging.WARNING)
    os.environ["STREAMLIT_SERVER_FILE_WATCHER_TYPE"] = "none"

def show_student_dashboard(user):
    st.title(f"🎒 Welcome, {user['username']}")
    st.caption(f"Level: {user.get('role', 'Student').capitalize()}")
    analytics.show_student_dashboard(user["username"])

def show_educator_dashboard():
    st.title("👩‍🏫 Educator Dashboard")
    tab1, tab2 = st.tabs(["Class Overview", "Reports"])
    with tab1:
        analytics.show_educator_dashboard()
    with tab2:
        analytics.show_student_reports()

def show_landing_page(auth):
    global user_info
    col1, col2 = st.columns([1, 1])
    with col1:
        st.title("🌟 EduTutor AI")
        st.markdown("""
        - 🧠 AI-powered adaptive quizzes  
        - 📈 Student performance dashboards  
        - 📚 Smart PDF Q&A  
        - 💬 Ask AI  
        - 👩‍🏫 Educator reports and class analytics  
        """)
    with col2:
        st.title("Login/Register")
        tabs = st.tabs(["Login", "Register"])
        with tabs[0]:
            user_info = auth.get_user_info()
            if user_info:
                st.session_state['user'] = user_info
                st.success("Logged in successfully!")
                st.rerun()
            else:
                auth.show_login_form()
        with tabs[1]:
            auth.show_registration_form()

def display_current_quiz(quiz_engine, user):
    quiz = st.session_state['current_quiz']
    index = quiz['current_question']
    questions = quiz['questions']
    total = len(questions)

    if index >= total:
        st.success("🎉 Quiz Completed!")
        score = sum(1 for i, q in enumerate(questions) 
                   if quiz['user_answers'][i] == q['correct_option'])
        st.write(f"✅ You scored **{score}/{total}**")

        user_identifier = user.get('id', user.get('username', 'anonymous'))
        
        quiz_engine.save_score(
            username=user_identifier,
            subject=quiz.get('subject', 'general'),
            topic=quiz.get('topic', 'general'),
            difficulty=quiz.get('difficulty', 'medium'),
            score=score,
            total=total
        )

        del st.session_state['current_quiz']
        return

    question = questions[index]
    st.write(f"**Question {index+1}:** {question['question']}")
    selected = st.radio("Options", question['options'], index=None, key=f"q_{index}")

    if st.button("Submit Answer"):
        if selected is not None:
            quiz['user_answers'][index] = question['options'].index(selected) + 1
            quiz['current_question'] += 1
            st.rerun()
        else:
            st.warning("Please select an option.")

def run_app():
    # Configure file watching and logging
    setup_file_watching()
    
    # Initialize app components
    Config.ensure_data_dir()
    init_db()
    ensure_background_image()

    auth = AuthSystem()
    quiz_engine = QuizEngine(data_path="data/sample_questions.json")
    analytics_dashboard = AnalyticsDashboard(Config.DATABASE_URI)
    pdf_qa = PDFQASystem()
    ask_ai = AskAI()

    global analytics
    analytics = analytics_dashboard

    if 'user' not in st.session_state:
        show_landing_page(auth)
    else:
        user = st.session_state['user']
        st.sidebar.title(f"👤 {user['username']}")
        st.sidebar.caption(f"Role: {user.get('role', 'user').capitalize()}")

        if user.get('role') == 'student':
            menu = st.sidebar.radio("Menu", [
                "Dashboard", "Take Quiz", "Resources", "PDF Q&A", "Ask AI"
            ])
        else:
            menu = st.sidebar.radio("Menu", [
                "Dashboard", "Reports"
            ])

        if st.sidebar.button("🚪 Logout"):
            st.session_state.clear()
            st.rerun()

        if 'current_quiz' in st.session_state:
            display_current_quiz(quiz_engine, user)
        elif user.get('role') == 'student':
            if menu == "Dashboard":
                show_student_dashboard(user)
            elif menu == "Take Quiz":
                st.title("🎯 Start a Quiz")
                subject = st.selectbox("Choose Subject", ["Math", "Science", "English", "History"])
                topic_map = {
                    "Math": ["Algebra"],
                    "Science": ["Physics"],
                    "English": ["Grammar"],
                    "History": ["World History"]
                }
                topic = st.selectbox("Choose Topic", topic_map.get(subject, []))
                difficulty_level = st.select_slider("Difficulty", [1, 2, 3],
                                                  format_func=lambda x: ["Easy", "Medium", "Hard"][x - 1])
                if st.button("Generate Quiz"):
                    questions = quiz_engine.get_questions(
                        subject.lower(), 
                        topic.lower(), 
                        ["easy", "medium", "hard"][difficulty_level - 1]
                    )
                    if questions:
                        st.session_state['current_quiz'] = {
                            'questions': questions,
                            'user_answers': [0]*len(questions),
                            'current_question': 0,
                            'subject': subject,
                            'topic': topic,
                            'difficulty': ["easy", "medium", "hard"][difficulty_level - 1]
                        }
                        st.rerun()
                    else:
                        st.error("No questions found or could not generate quiz.")
            elif menu == "Resources":
                st.title("📚 Learning & Wellness Resources")
                with st.expander("📜 Academic Resources"):
                    st.markdown("- [Khan Academy](https://www.khanacademy.org)")
                    st.markdown("- [Coursera](https://www.coursera.org)")
                    st.markdown("- [NPTEL - India](https://nptel.ac.in)")
                    st.markdown("- [edX](https://www.edx.org)")
                with st.expander("🧠 Health & Mental Wellness"):
                    st.markdown("- [WHO Youth Mental Health](https://www.who.int/mental_health/en/)")
                    st.markdown("- [Mindfulness for Students](https://www.mindful.org/mindfulness-for-students/)")
                    st.markdown("- [Teen Mental Health](https://teenmentalhealth.org)")
            elif menu == "PDF Q&A":
                st.title("📄 Ask Questions from PDF")
                uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")
                if uploaded_file:
                    with open("temp_uploaded.pdf", "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    st.success("✅ PDF uploaded. You can now ask a question.")
                    question = st.text_input("Enter your question:")
                    if question:
                        context = pdf_qa.extract_text_from_pdf("temp_uploaded.pdf")
                        answer = pdf_qa.ask_question(context, question)
                        st.write(f"🧠 Answer: **{answer}**")
            elif menu == "Ask AI":
                ask_ai.show_interface()
        else:
            if menu == "Dashboard":
                show_educator_dashboard()
            elif menu == "Reports":
                analytics.show_student_reports()

if __name__ == "__main__":
    run_app()