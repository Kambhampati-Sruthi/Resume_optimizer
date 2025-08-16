import streamlit as st
from resume_optimizer import extract_resume_text, extract_keywords, find_missing_keywords, append_keywords_to_pdf, generate_explanation
st.title("Resume Keyword Optimizer")

job_description = st.text_area("Paste Job Description Here")
resume_file = st.file_uploader("Upload Resume PDF", type=["pdf"])

if st.button("Optimize Resume"):
    if job_description and resume_file:
        resume_text = extract_resume_text(resume_file)
        job_keywords = extract_keywords(job_description)
        missing_keywords = find_missing_keywords(resume_text, job_keywords)

        explanation = generate_explanation(missing_keywords)
        st.write(explanation)

        output_path = "optimised_resume.pdf"
        append_keywords_to_pdf(resume_file, output_path, missing_keywords)

        with open(output_path, "rb") as f:
            st.download_button("Download Optimized Resume", f, file_name="optimised_resume.pdf")
    else:
        st.warning("Please provide both job description and resume.")
