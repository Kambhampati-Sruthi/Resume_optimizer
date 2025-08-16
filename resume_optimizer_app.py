import streamlit as st
import pdfplumber
import re
from PyPDF2 import PdfReader, PdfWriter
from io import BytesIO

def extract_resume_text(uploaded_file):
    with pdfplumber.open(uploaded_file) as pdf:
        text = ""
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    return text

def extract_keywords(job_description):
    words = re.findall(r'\b\w+\b', job_description.lower())
    keywords = set(words)
    return list(keywords)

def find_missing_keywords(resume_text, job_keywords):
    resume_words = set(re.findall(r'\b\w+\b', resume_text.lower()))
    missing = [kw for kw in job_keywords if kw not in resume_words]
    return missing

def append_keywords_to_pdf(uploaded_file, keywords):
    reader = PdfReader(uploaded_file)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    # Add a blank page (A4 size)
    writer.add_blank_page(width=595, height=842)

    output = BytesIO()
    writer.write(output)
    output.seek(0)
    return output

def generate_explanation(missing_keywords):
    if not missing_keywords:
        return "✅ Your resume already includes all the important keywords!"
    return f"⚠️ Your resume is missing the following keywords:\n\n{', '.join(missing_keywords)}"

# Streamlit UI
st.title("📄 Resume Keyword Optimizer")

job_description = st.text_area("Paste Job Description Here")
resume_file = st.file_uploader("Upload Resume PDF", type=["pdf"])

if st.button("Optimize Resume"):
    if job_description and resume_file:
        resume_text = extract_resume_text(resume_file)
        job_keywords = extract_keywords(job_description)
        missing_keywords = find_missing_keywords(resume_text, job_keywords)

        explanation = generate_explanation(missing_keywords)
        st.write(explanation)

        optimized_pdf = append_keywords_to_pdf(resume_file, missing_keywords)

        st.download_button("Download Optimized Resume", optimized_pdf, file_name="optimised_resume.pdf")
    else:
        st.warning("Please provide both job description and resume.")
