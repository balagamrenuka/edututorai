import json
import random
from pathlib import Path

class QuizEngine:
    def __init__(self, data_path="data/questions.json"):
        self.data_path = Path(data_path)
        self.questions = self.load_questions()

    def load_questions(self):
        """Load questions from JSON file, return empty dict if file doesn't exist or is invalid"""
        if not self.data_path.exists():
            print(f"Error: Questions file not found at {self.data_path}")
            return {}

        try:
            with open(self.data_path, "r") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from {self.data_path}: {e}")
            return {}
        except Exception as e:
            print(f"Error loading questions: {e}")
            return {}

    def get_questions(self, subject, topic, difficulty, num_questions=3):
        """Get random questions matching the criteria"""
        try:
            # Convert all parameters to lowercase for case-insensitive matching
            subject = subject.lower()
            topic = topic.lower()
            difficulty = difficulty.lower()

            # Debug print to show what we're looking for
            print(f"Looking for: Subject={subject}, Topic={topic}, Difficulty={difficulty}")

            # Get the matching questions with more error checking
            subject_data = self.questions.get(subject, {})
            if not subject_data:
                print(f"No questions found for subject: {subject}")
                return []

            topic_data = subject_data.get(topic, {})
            if not topic_data:
                print(f"No questions found for topic: {topic} in subject: {subject}")
                return []

            difficulty_data = topic_data.get(difficulty, [])
            if not difficulty_data:
                print(f"No questions found for difficulty: {difficulty} in topic: {topic}")
                return []

            # Debug print to show how many questions were found
            print(f"Found {len(difficulty_data)} questions matching criteria")

            # Return random sample
            return random.sample(difficulty_data, min(num_questions, len(difficulty_data)))
            
        except Exception as e:
            print(f"Error in get_questions: {e}")
            return []

    def save_score(self, username, subject, topic, difficulty, score, total):
        """Log the user's score"""
        print(f"[SCORE LOG] User: {username}, Subject: {subject}, Topic: {topic}, "
              f"Difficulty: {difficulty}, Score: {score}/{total}")