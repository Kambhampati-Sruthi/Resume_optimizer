import streamlit as st
import pdfplumber
import re
from PyPDF2 import PdfReader, PdfWriter
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

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

    # Create a PDF page with the missing keywords using reportlab
    keyword_pdf = BytesIO()
    c = canvas.Canvas(keyword_pdf, pagesize=A4)
    text_object = c.beginText(40, 800)
    text_object.setFont("Helvetica", 12)
    text_object.textLine("🔍 Missing Keywords Added for Optimization:")
    text_object.textLine("")

    for kw in keywords:
        text_object.textLine(f"- {kw}")

    c.drawText(text_object)
    c.showPage()
    c.save()
    keyword_pdf.seek(0)

    # Merge the keyword page
    keyword_reader = PdfReader(keyword_pdf)
    writer.add_page(keyword_reader.pages[0])

    output = BytesIO()
    writer.write(output)
    output.seek(0)
    return output

def generate_explanation(missing_keywords):
    if not missing_keywords:
        return "✅ Your resume already includes all the important keywords!"
    return (
        f"⚠️ Your resume is missing **{len(missing_keywords)}** keywords:\n\n"
        + ", ".join(missing_keywords)
    )

# Streamlit UI
st.set_page_config(page_title="Resume Keyword Optimizer and Generator", page_icon="📄")
st.title("📄 Resume Keyword Optimizer and Generation")

st.markdown("Optimize your resume by matching it with the job description keywords.")

job_description = st.text_area("📋 Paste Job Description Here")
resume_file = st.file_uploader("📎 Upload Resume PDF", type=["pdf"])

if st.button("🚀 Optimize Resume"):
    if job_description and resume_file:
        resume_text = extract_resume_text(resume_file)
        job_keywords = extract_keywords(job_description)
        missing_keywords = find_missing_keywords(resume_text, job_keywords)

        explanation = generate_explanation(missing_keywords)
        st.markdown(f"### 🔍 Keyword Analysis Result\n\n{explanation}")

        with st.expander("📄 View Extracted Resume Text"):
            st.write(resume_text)

        optimized_pdf = append_keywords_to_pdf(resume_file, missing_keywords)

        st.download_button(
            "📥 Download Optimized Resume",
            optimized_pdf,
            file_name="optimized_resume.pdf"
        )
    else:
        st.warning("⚠️ Please provide both the job description and resume.")


