import streamlit as st
import os
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from dotenv import load_dotenv
import google.generativeai as genai
from selenium import webdriver
from selenium.webdriver.common.by import By
import webbrowser  # To open links in a new tab
import time
import pandas as pd
from streamlit_option_menu import option_menu
from streamlit_extras.add_vertical_space import add_vertical_space
from selenium.webdriver.chrome.service import Service
from app1 import run_app1
from app1 import main
from app2 import main2

# Import linkedin_scraper class from File 2
class linkedin_scraper:
    
    def webdriver_setup():
        s = Service(r"C:\Users\prera\OneDrive\Desktop\prerana ankit\Final Major Project By Prerana and Ankit\chromedriver.exe")
        driver = webdriver.Chrome(service=s)
        driver.maximize_window()
        return driver

    def get_userinput():
        st.write("Provide job title, location, and number of jobs to scrape:")
        with st.form(key='linkedin_scraper'):
            col1, col2 = st.columns(2)
            with col1:
                job_title_input = st.text_input(label='Job Title', value='data scientist')
            with col2:
                job_location = st.text_input(label='Job Location', value='India')
            submit = st.form_submit_button(label='Submit')
        return job_title_input, job_location, submit

    def scrape_jobs(driver, job_title, job_location):
        driver.get(f"https://in.linkedin.com/jobs/search?keywords={job_title}&location={job_location}&geoId=102713980&f_TPR=r604800&position=1&pageNum=0")
        time.sleep(3)
        job_list = []

        def scrape_page_jobs():
            jobs_section = driver.find_element(By.XPATH, '//*[@id="main-content"]/section[2]/ul')
            job_items = jobs_section.find_elements(By.TAG_NAME, "li")

            for job_item in job_items:
                try:
                    job_name = job_item.find_element(By.CLASS_NAME, 'sr-only').text
                    job_metadata = job_item.find_element(By.CLASS_NAME, 'base-search-card__metadata')
                    job_address = job_metadata.text.strip()
                    job_link = job_item.find_element(By.CLASS_NAME, 'base-card__full-link').get_attribute('href')
                    job_list.append((job_name, job_address, job_link))
                except:
                    pass  # Ignore errors

        scrape_page_jobs()
        SCROLL_PAUSE_TIME = 2
        last_height = driver.execute_script("return document.body.scrollHeight")

        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(SCROLL_PAUSE_TIME)
            scrape_page_jobs()
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        return job_list

    def display_jobs_in_streamlit(job_list):
        if len(job_list) > 0:
            df = pd.DataFrame(job_list, columns=["Job Title", "Address", "Job Link"])
            st.write("### Scraped Jobs")
            st.dataframe(df)
            csv = df.to_csv(index=False)
            st.download_button(label="Download CSV", data=csv, file_name='linkedin_jobs.csv', mime='text/csv')
        else:
            st.write("No jobs found.")


# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Define functions for PDF analysis
def get_gemini_response(input):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(input)
    return response.text

def input_pdf_text(uploaded_file):
    reader = PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def split_text_into_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=200, length_function=len)
    return text_splitter.split_text(text=text)

def genai_response(chunks, analyze):
    embeddings = GoogleGenerativeAIEmbeddings
    vectorstores = FAISS.from_texts(chunks, embedding=embeddings)
    docs = vectorstores.similarity_search(query=analyze, k=3)
    llm = ChatGoogleGenerativeAI(model=genai.GenerativeModel('gemini-pro'))
    chain = load_qa_chain(llm=llm, chain_type='stuff')
    response = chain.run(input_documents=docs, question=analyze)
    return response

# Define the Streamlit UI
st.title("AIHirehub: Smart Resume Analyzer with Job Finder")

# Upload and submit section below the title
uploaded_file = st.file_uploader("Upload PDF Resume", type="pdf")
submit_button = st.button("Submit")


# # Sidebar options
# option = st.sidebar.selectbox("Choose analysis type", ['Summary', 'Strength', 'Weakness', 'Job Titles', 'LinkedIn Jobs'])

with st.sidebar:
    option = option_menu("Choose analysis type", ['Summary', 'Strength', 'Weakness', 'Job Titles', 'LinkedIn Jobs', 'Check Fake Stuffing', 'Check Percentage Match'])


# Handling form submission for resume analysis
if submit_button:
    if uploaded_file is not None:
        resume_text = input_pdf_text(uploaded_file)
        chunks = split_text_into_chunks(resume_text)
        if option == 'Summary':
            st.subheader("Resume Summary")
            query = f"Summarize the resume below:\n\n{resume_text}"
            result = get_gemini_response(query)
            st.write(result)
        elif option == 'Strength':
            st.subheader("Resume Strength")
            query = f"Analyze the strengths of the resume below:\n\n{resume_text}"
            result = get_gemini_response(query)
            st.write(result)
        elif option == 'Weakness':
            st.subheader("Resume Weakness")
            query = f"Analyze the weaknesses and provide suggestions for improvement:\n\n{resume_text}"
            result = get_gemini_response(query)
            st.write(result)
        elif option == 'Job Titles':
            st.subheader("Job Titles Suggestions")
            query = f"Suggest job titles based on the resume below:\n\n{resume_text}"
            result = get_gemini_response(query)
            st.write(result)


# Handling LinkedIn Jobs option
if option == 'LinkedIn Jobs':
    st.subheader("LinkedIn Jobs")

    # Button to open LinkedIn Jobs in a new tab
    if st.button("Open LinkedIn Jobs"):
        webbrowser.open_new_tab("https://www.linkedin.com/jobs/")
        st.write("LinkedIn Jobs opened in a new tab.")
    
    # Button to scrape jobs from LinkedIn
    job_title_input, job_location, submit = linkedin_scraper.get_userinput()

    if submit:
        # Setup WebDriver
        driver = linkedin_scraper.webdriver_setup()

        # Scrape jobs
        job_list = linkedin_scraper.scrape_jobs(driver, job_title_input, job_location)

        # Close the browser after scraping
        driver.quit()

        # Display the scraped jobs in Streamlit
        linkedin_scraper.display_jobs_in_streamlit(job_list)


if option == 'Check Fake Stuffing':
    st.subheader("Fake Stuffing Checker: Hidden Text Detection in PDF")   
    main()

if option == 'Check Percentage Match':
    main2()
