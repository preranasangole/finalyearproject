import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
load_dotenv()


genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
def main2():
    st.title("AIHireHub : Improve Your Resume Match")

    # Job description and file upload widgets
    jd = st.text_area("Paste Job Description Here")
    uploaded_file = st.file_uploader("Upload Your Resume (PDF)", type="pdf", help="Please upload the PDF")
    def get_gemini_response(input):
        model=genai.GenerativeModel('gemini-pro')
        response = model.generate_content(input)
        return response.text
    # Button to trigger evaluation
    submit = st.button('Check Your Score')
    def input_pdf_text(uploaded_file):
        reader=pdf.PdfReader(uploaded_file)
        text=""
        for page in range(len(reader.pages)):
            page=reader.pages[page]
            text+=str(page.extract_text())
        return text
    if submit:
        if uploaded_file is not None and jd:
            # Extract text from the uploaded resume
            resume_text = input_pdf_text(uploaded_file)
            
            # Generate response from the Gemini model using the input prompt
            input_prompt = f"""
            ### As a skilled Application Tracking System (ATS) with advanced knowledge in technology and data science, your role is to meticulously evaluate a candidate's resume based on the provided job description. 
            ### Your evaluation will involve analyzing the resume for relevant skills, experiences, and qualifications that align with the job requirements. 
            ### Look for key buzzwords and specific criteria outlined in the job description to determine the candidate's suitability for the position.
            ### Your evaluation should be thorough, precise, and objective, ensuring that the most qualified candidates are accurately identified based on their resume content in relation to the job criteria.
            ### Remember to utilize your expertise in technology and data science to conduct a comprehensive evaluation that optimizes the recruitment process for the hiring company.
            ### Your insights will play a crucial role in determining the candidate's compatibility with the job role.
            resume={resume_text}
            jd={jd}
            ### Evaluation Output:
            1. Calculate the percentage of match between the resume and the job description. Give a number and some explanation.
            """

            # Get response from the Gemini model
            response = get_gemini_response(input_prompt)
            st.subheader("Resume Evaluation:")
            st.write(response)
        else:
            st.warning("Please upload both a job description and a resume.")

if __name__ == "__main__":
    main()
