import streamlit as st
import os 
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from crewai import Agent, Task, Crew,LLM
from crewai_tools import SerperDevTool, ScrapeWebsiteTool,WebsiteSearchTool,FileReadTool,DirectoryReadTool, FirecrawlScrapeWebsiteTool
from crewai.tools import BaseTool
import pdfplumber
import asyncio
load_dotenv()
from jinja2 import Template
import json
from MAS_FOR_JOBSEARCH import MAS
from xhtml2pdf import pisa
from io import BytesIO
from markdown2 import markdown
import re

 #Load environment variables
st.sidebar.title("🔑 API Key Setup")
openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password", help="Paste your OpenAI API key here")
deepseek_api_key = st.sidebar.text_input("DeepSeek API Key", type="password", help="Paste your DeepSeek API key here")
llm_choices=[]
print("OpenAI API Key:", openai_api_key)
print("DeepSeek API Key:", deepseek_api_key)


# Adding apply button
if st.sidebar.button("Apply API Keys"):
    if not openai_api_key and not deepseek_api_key:
        st.sidebar.error("Please enter either one API key or both.")
        st.stop()
    os.environ["OPENAI_API_KEY"] = openai_api_key
    os.environ["DEEPSEEK_API_KEY"] = deepseek_api_key
    st.session_state["api_keys_set"] = True



# Creating LLM instances for all agents

@st.cache_resource
def get_llms():

    try:
        return{
        "llm_4o": ChatOpenAI(model="gpt-4o", api_key=os.getenv("OPENAI_API_KEY")),
        "llm_3_5" :ChatOpenAI(model="gpt-3.5-turbo"),
        "llm_deepseek_v3":LLM(provider="deepseek",model="deepseek/deepseek-chat", api_key=os.getenv("DEEPSEEK_API_KEY")),
        "llm_deepseek_r1":LLM(provider="deepseek",model="deepseek/deepseek-reasoner", api_key=os.getenv("DEEPSEEK_API_KEY"))
        }

    except Exception as e:
        st.error(f"Error initializing LLMs: {e}")
        st.stop()

llms = get_llms()
llm_4o=llms["llm_4o"]
llm_3_5=llms["llm_3_5"]
llm_deepseek_v3=llms["llm_deepseek_v3"]
llm_deepseek_r1=llms["llm_deepseek_r1"]


# Styling Markdown
st.markdown("""
<h1 style='text-align: center; font-size: 3rem;'>📄 ResuMatchAI</h1>
<h3 style='text-align: center; font-weight: 400; color: #34A853;'>Smarter ideas. Better matches.</h3>

<p style='text-align: center; font-size: 1.1rem; margin-top: 1em;'>
Welcome to <strong>ResuMatchAI</strong> — your intelligent career companion! 🚀<br>
Upload your resume, analyze it against live job descriptions, and optimize it like a pro.<br>
From parsing to perfection, our multi-agent AI pipeline ensures your resume is tailored, <em>relevant</em>, and <strong>ready to impress</strong>.
</p>
""", unsafe_allow_html=True)

# File Uploader
st.markdown("""
<h2 style='text-align: center; font-size: 2rem;'>📤 Upload Your Resume</h2>
            """, unsafe_allow_html=True)
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
if uploaded_file is not None:
    if uploaded_file.name.lower().endswith(".pdf"):
        # Save the uploaded file to a temporary location
        st.session_state["file_path"]= os.path.join(os.getcwd(), uploaded_file.name)
        st.write(st.session_state["file_path"])
        st.success("✅ PDF successfully uploaded.")
        
    else:
        st.error("❌ Please upload a valid PDF file.")
else:
    st.warning("⚠️ Please upload your resume in PDF format.")


# Creating a text input for Job Description
st.markdown("### 🔗 Paste a Job Description URL")
job_description_url = st.text_input(
    "Enter the URL of the job description you'd like to analyze:",
    placeholder="https://example.com/job-description",
    key="job_url"
)


if job_description_url and not job_description_url.startswith("http"):
    st.warning("⚠️ Please enter a valid URL that starts with http or https.")
    st.stop()


st.subheader("🤖 Select LLMs for Each Agent")
st.markdown("Customize the intelligence behind each agent in your ResuMatchAI pipeline.")

with st.container():
    openai_flag=0
    deepseek_flag=0
    if openai_api_key:
        llm_choices.append("gpt-3.5-turbo")
        llm_choices.append("gpt-4o")
        openai_flag=1
    if deepseek_api_key:
        llm_choices.append("deepseek-v3")
        llm_choices.append("deepseek-r1")
        deepseek_flag=1

    st.markdown("### 🧾 Resume Parser Agent")
    st.caption("Extracts key sections like skills, education, experience, and summary from your uploaded resume.")
    parser_llm = st.selectbox("Choose LLM for Resume Parser Agent", llm_choices, key="parser")
    

    st.markdown("### 🔍 JD Scraper Agent")
    st.caption("Scrapes job descriptions and identifies key skills, qualifications, and responsibilities for the target role.")
    jd_llm = st.selectbox("Choose LLM for Job Scraper Agent", llm_choices, key="jd")

    st.markdown("### 📊 Resume vs JD Analyzer Agent")
    st.caption("Compares your parsed resume against the job description to identify skill gaps and match score.")
    analyzer_llm = st.selectbox("Choose LLM for Resume vs JD Analyzer Agent", llm_choices, key="analyzer")

    st.markdown("### 🛠️ Resume Optimizer Agent")
    st.caption("Optimizes your resume using the STAR method and aligns it with the job description to improve match quality.")
    optimizer_llm = st.selectbox("Choose LLM for Resume Optimizer Agent", llm_choices, key="optimizer")

    st.markdown("### ✅ QA Supervisor Agent")
    st.caption("Validates the optimized resume to ensure all sections are complete, clear, and follow best practices.")
    qa_llm = st.selectbox("Choose LLM for QA Supervisor Agent", llm_choices, key="qa")



# Replacing emoji's with text for PDF generation
def clean_markdown_for_pdf(md: str) -> str:
    replacements = {
        "🚀": "Resume Optimization Report",
        "👋": "",
        "🎯": "Match Score:",
        "✅": "Matched Skills",
        "❌": "Missing Skills",
        "📝": "Feedback",
        "📈": "Score:",
        "📜": "Certifications:",
        "🧪": "Projects",
        "💼": "Work Experience",
        "🧠": "Summary",
        "📊": "Analysis",
        "✨": "Optimized Resume",
        "👤": "Name",
        "🎓": "Education"
    }
    for emoji, text in replacements.items():
        md = md.replace(emoji, text)
    return md


# Creating a button to start the process
st.markdown("""
<h2 style='text-align:left; font-size: 2rem;'>🚀 Start the Process</h2>  
""", unsafe_allow_html=True)

if st.button("Start the Process", key="start_process"):
    
    if not uploaded_file or not job_description_url:
        st.warning("⚠️ Please upload your resume and enter a job description URL.")
        st.stop()
    
    # Running Multi Agent System to peform resume optimisation against job description
    with st.spinner("The process has started. It may take a few minutes"):
        async def run_process():
            final_output = await asyncio.to_thread(MAS,st.session_state['file_path'],llm_4o,llm_3_5,llm_deepseek_v3,llm_deepseek_r1,job_description_url ,parser_llm, jd_llm, analyzer_llm, optimizer_llm, qa_llm)
            return final_output

        # Run the async function and get the result
        st.session_state["final_output"]= asyncio.run(run_process())
    
    # Displaying the final output in a code block
    st.balloons()
    formatted_output=st.session_state["final_output"]
    #formatted_output=markdown(formatted_output, extras=["fenced-code-blocks"])
    st.markdown(formatted_output)

    # Cleaning the markdown for PDF generation
    formatted_output = clean_markdown_for_pdf(formatted_output)

    # Creating a download button for the final output
    html=markdown(formatted_output, extras=["fenced-code-blocks"])
    pdf_file = BytesIO()
    pisa.CreatePDF(BytesIO(html.encode("utf-8")), dest=pdf_file)
    pdf_file.seek(0)
    
    # Creating a download button for the final output
    st.download_button(label="Download Optimized Resume",data=pdf_file, file_name="optimised_resume_with_suggestions.pdf", mime="application/pdf")

    

