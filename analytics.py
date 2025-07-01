import streamlit as st
import pandas as pd
import json
import os
import chardet
from pathlib import Path

class AnalyticsDashboard:
    def __init__(self, scores_path="scores.json"):
        self.scores_path = Path(scores_path)
        self._ensure_valid_json_file()

    def _ensure_valid_json_file(self):
        """Ensure the scores file exists and contains valid JSON"""
        try:
            if not self.scores_path.exists():
                with open(self.scores_path, 'w') as f:
                    json.dump([], f)  # Create empty list if file doesn't exist
            else:
                # Validate the file contains proper JSON
                with open(self.scores_path, 'r') as f:
                    json.load(f)  # Test loading
        except (json.JSONDecodeError, UnicodeDecodeError):
            # If file is corrupted, reset it
            with open(self.scores_path, 'w') as f:
                json.dump([], f)
            st.warning("Reset corrupted scores file")
        except Exception as e:
            st.error(f"Error initializing scores file: {str(e)}")

    def _load_json_file(self):
        """Safely load JSON data with multiple fallback strategies"""
        try:
            # First try with detected encoding
            with open(self.scores_path, 'rb') as f:
                raw_data = f.read()
                encoding = chardet.detect(raw_data)['encoding']
            
            with open(self.scores_path, 'r', encoding=encoding) as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
                
        except (UnicodeDecodeError, json.JSONDecodeError):
            try:
                # Fallback to utf-8-sig (handles BOM)
                with open(self.scores_path, 'r', encoding='utf-8-sig') as f:
                    data = json.load(f)
                    return data if isinstance(data, list) else []
            except Exception:
                return []  # Return empty list if all attempts fail
        except Exception:
            return []  # Return empty list for any other error

    def _save_json_file(self, data):
        """Safely save data to JSON file"""
        try:
            with open(self.scores_path, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            st.error(f"Failed to save data: {str(e)}")
            return False

    def load_student_analytics(self, username):
        """Load analytics data for a specific student"""
        data = self._load_json_file()
        if not data:
            return pd.DataFrame()

        # Safely process each record with default values
        processed_data = []
        for record in data:
            if not isinstance(record, dict):
                continue
                
            processed_record = {
                'username': record.get('username', ''),
                'subject': record.get('subject', 'Unknown'),
                'topic': record.get('topic', 'Unknown'),
                'difficulty': record.get('difficulty', 'Unknown'),
                'score': int(record.get('score', 0)),
                'total': int(record.get('total', 1)),
                'timestamp': record.get('timestamp', '')
            }
            
            if processed_record['username'] == username:
                processed_data.append(processed_record)
                
        return pd.DataFrame(processed_data)

    def load_teacher_analytics(self):
        """Load analytics data for teacher view"""
        data = self._load_json_file()
        if not data:
            return pd.DataFrame()

        # Process all records with validation
        processed_data = []
        for record in data:
            if not isinstance(record, dict):
                continue
                
            processed_data.append({
                'username': record.get('username', ''),
                'subject': record.get('subject', 'Unknown'),
                'topic': record.get('topic', 'Unknown'),
                'difficulty': record.get('difficulty', 'Unknown'),
                'score': int(record.get('score', 0)),
                'total': int(record.get('total', 1)),
                'timestamp': record.get('timestamp', '')
            })
            
        return pd.DataFrame(processed_data)

    def show_student_dashboard(self, username):
        """Display student dashboard with analytics"""
        st.subheader("📊 Student Dashboard")
        df = self.load_student_analytics(username)

        if df.empty:
            st.info("No quiz attempts yet.")
            return

        st.write("Your Quiz History:")
        st.dataframe(df)

        if "score" in df.columns and "total" in df.columns:
            df["Percentage"] = (df["score"] / df["total"] * 100).round(2)
            
            if "timestamp" in df.columns and not df["timestamp"].empty:
                try:
                    df["timestamp"] = pd.to_datetime(df["timestamp"])
                    st.line_chart(df.set_index("timestamp")[["Percentage"]])
                except Exception as e:
                    st.warning(f"Could not plot timeline: {str(e)}")

    def show_teacher_dashboard(self):
        """Display teacher dashboard with analytics"""
        st.subheader("📊 Teacher Dashboard")
        df = self.load_teacher_analytics()

        if df.empty:
            st.info("No quiz submissions available.")
            return

        st.write("All Quiz Attempts:")
        st.dataframe(df)

        # Filters
        if "subject" in df.columns:
            subjects = ["All"] + sorted(df["subject"].unique().tolist())
            selected_subject = st.selectbox("Filter by Subject", subjects)

            if selected_subject != "All":
                df = df[df["subject"] == selected_subject]

        st.write("📈 Quiz Scores by Student")
        if "username" in df.columns and "score" in df.columns:
            scores_by_user = df.groupby("username")["score"].sum()
            st.bar_chart(scores_by_user)