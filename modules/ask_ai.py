import streamlit as st
from transformers import pipeline
from transformers.pipelines import PipelineException

@st.cache_resource(show_spinner="Loading QA model...")
def load_qa_pipeline():
    try:
        # Load a lightweight, fast local model
        model_name = "distilbert-base-cased-distilled-squad"
        qa_pipeline = pipeline("question-answering", model=model_name, tokenizer=model_name)
        return qa_pipeline
    except PipelineException as e:
        st.error("❌ Failed to load model pipeline. Please check your internet or model name.")
        raise e
    except Exception as e:
        st.error(f"❌ An unexpected error occurred: {e}")
        raise e

class AskAI:
    def __init__(self, api_key=None):
        self.api_key = api_key  # For future use with cloud APIs if needed
        self.qa_pipeline = load_qa_pipeline()

    def show_interface(self):
        st.title("💬 Ask AI (Offline - Local Model)")

        st.markdown("This uses a local transformer model (`distilbert-base-cased-distilled-squad`) for QA.")
        
        context = st.text_area("📄 Enter context or paragraph:")
        question = st.text_input("❓ Ask a question about the above context:")

        if st.button("Get Answer"):
            if context.strip() and question.strip():
                with st.spinner("Thinking..."):
                    try:
                        result = self.qa_pipeline(question=question, context=context)
                        st.success("✅ Answer:")
                        st.write(f"**{result['answer']}**")
                    except Exception as e:
                        st.error(f"❌ Failed to get answer: {e}")
            else:
                st.warning("⚠️ Please enter both context and question.")