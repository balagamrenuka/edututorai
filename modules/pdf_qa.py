import streamlit as st
import PyPDF2
from transformers import T5Tokenizer, T5ForConditionalGeneration
import torch

@st.cache_resource
def load_model(_self=None):
    tokenizer = T5Tokenizer.from_pretrained("t5-small")
    model = T5ForConditionalGeneration.from_pretrained("t5-small")
    return tokenizer, model

class PDFQASystem:
    def __init__(self):
        self.tokenizer, self.model = load_model()
        self.text_chunks = []

    def extract_text_from_pdf(self, pdf_file):
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            st.error(f"Error reading PDF: {e}")
            return ""

    def chunk_text(self, text, max_tokens=300):
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0

        for word in words:
            current_chunk.append(word)
            current_length += 1
            if current_length >= max_tokens:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_length = 0

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks

    def ask_question(self, context, question):
        input_text = f"question: {question} context: {context}"
        input_ids = self.tokenizer.encode(input_text, return_tensors="pt", max_length=512, truncation=True)
        outputs = self.model.generate(input_ids, max_length=100, num_beams=4, early_stopping=True)
        answer = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return answer

    def show_interface(self):
        st.title("📄 PDF Question Answering")

        uploaded_pdf = st.file_uploader("Upload a PDF file", type=["pdf"])
        if uploaded_pdf:
            with st.spinner("Reading and processing PDF..."):
                text = self.extract_text_from_pdf(uploaded_pdf)
                if not text:
                    st.warning("No text found in PDF.")
                    return

                self.text_chunks = self.chunk_text(text)
                st.success("PDF processed successfully!")

        if self.text_chunks:
            question = st.text_input("Ask a question based on the PDF:")

            if st.button("Get Answer"):
                with st.spinner("Generating answer..."):
                    context = " ".join(self.text_chunks[:3])  # Use first 3 chunks
                    answer = self.ask_question(context, question)
                    st.subheader("Answer:")
                    st.write(answer)
