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
import streamlit as st

def MAS(filepath,llm_4o,llm_3_5,llm_deepseek_v3, llm_deepseek_r1,job_description_url,resume_analyser_agent,job_exctractor,resume_vs_job,resume_optimser,qa_supervisor):
    """
    This function is used to run the Multi-Agent System (MAS) for resume analysis and job description matching.
    It initializes the agents, tasks, and crew, and then kicks off the process with the provided inputs.
    """
   

    """ Creating LLM instance
    llm_4o = ChatOpenAI(model="gpt-4o", api_key=os.getenv("OPENAI_API_KEY"))
    llm_3_5 = ChatOpenAI(model="gpt-3.5-turbo")
    llm_deepseek_v3=LLM(provider="deepseek",model="deepseek/deepseek-chat", api_key=os.getenv("DEEPSEEK_API_KEY"))
    llm_deepseek_r1=LLM(provider="deepseek",model="deepseek/deepseek-reasoner", api_key=os.getenv("DEEPSEEK_API_KEY"))"""

    
    
    # Creating dictionaries to store llms in key-value pairs
    llms_dict={"deepseek-v3":llm_deepseek_v3,"deepseek-r1":llm_deepseek_r1,"gpt-3.5-turbo":llm_3_5,"gpt-4o":llm_4o}
    
    # Assigning llms to all agents
    resume_analyser_agent_crew=llms_dict[resume_analyser_agent]
    job_exctractor_crew=llms_dict[job_exctractor]
    resume_vs_job_crew=llms_dict[resume_vs_job]
    resume_optimser_crew=llms_dict[resume_optimser]
    qa_supervisor_crew=llms_dict[qa_supervisor]
    






    # Creating resume filepath
    #filepath=os.path.join(os.getcwd(),"harshith_resume.pdf")

    # Creating Resume Analyser agent
    resume_analyser=Agent(
        role="Resume Analyst",
        goal="To extract structured data from raw resume text, that includes sections like Introduction, Work Experience, Skills, Education, Projects,Certifications, role the person is looking for etc...",
        backstory=(
        "You are a highly experienced HR analyst specialising in resume evaluation. You have screened thousands of resumes across multiple industries and can extract detailed information from evenly poorly structured documents. Your expertise lies in identifying and organising key sections like skills, work experience, Introduction ,education,projects and certifications"
        ),
        allow_delegation=False,
        verbose=True,
        llm=resume_analyser_agent_crew
    )

    # Creating Job Scraper / JD Import Agent

    job_scraper_agent=Agent(role="Job Description Collector",goal="To extract structured job description information from the job description links paster by the user or scraping the naukri website for the relevant job descriptions",
                            backstory=(
                                "Your are an expert and senior most job description collector of your team, your job is to collect the job description from the links provided by the user and scrape the website for the relevant job descriptions"
                                "Your expertise lies in identifying and organising key sections like skills, work experience, Introduction ,education,projects and certifications etc... based on the {job_role} "
                ),llm=job_exctractor_crew,allow_delegation=False,verbose=True)


    # Creating Match Evaluator Agent
    match_evaluator_agent=Agent(role ="Resume vs Job Description Evaluator", goal="To evaluate how well the resume aligns with the provided job description and provide a match score along with detailed analysis"
                                , backstory=("You are a highly experienced hiring consultant trained to compare resume with job descriptions and assess the candidate's fit. You can detect matching skills, missing skills, and give actionable recommendations to improve user's resume chance of getting selected."), llm=resume_vs_job_crew,allow_delegation=False,verbose=True)


    # Creating Resume Optimiser Agent:
    resume_optimiser_agent=Agent(role="Resume Optimiser",goal="To rewrite and optimise the sections of the candidate's resume so that it aligns well with the job description, improves clarity, matching score and increases the chance of getting noticed by hiring managers and ATS."
                                ,backstory=("You are a professional career coach and an expert resume optimiser with years of experience crafting impactful resumes tailored to specific job roles. You understand ATS systems, employer pyschology, and rewrite resume sections to improve relevance and clarity. Please do make sure to have upto 4 bullet points in responsibilities section of both projects and work experience and also make sure that these bullet points reflects my expertise, achievements and skills (both hard and soft skills) being used in a right way"),llm=resume_optimser_crew,allow_delegation=False,verbose=True)


    # Creating Resume Quality Assurance Agent
    resume_qa_agent=Agent(role="Resume Quality Assurance Supervisor",goal="Review the optimized resume and verify alignment with the job description and best practices like STAR method",
                        backstory=("You're an expert resume QA reviewer. "
            "You audit AI-generated resumes to ensure they are complete, well-structured, use the STAR method for accomplishments, and are tailored to the job description provided. "
            "You are highly detail-oriented and ensure no critical section or skill is missing. "
            "You also provide constructive feedback and re-optimize the resume if necessary."
            ),llm=qa_supervisor_crew,verbose=True)


    # Creating Resume Extractor Tool
    class ResumeExtractorTool(BaseTool):
        name: str= "resume_text_extractor"
        description:str="Extracts raw text from the PDF resume file and returns it to an agent for analysing the resume"

        def _run(self, file_path: str) -> str:
            with pdfplumber.open(file_path) as pdf:
                return "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
            

    # Creating the task for the Resume Analyser agent
    resume_extractor_tool=ResumeExtractorTool()

    task_resume_analyser_agent=Task(
        description= "Parse the resume located at {file_path} and extract the following sections: Introduction, Work Experience, Skills, Education, Projects, Certifications, and the role the person is looking for.",
        expected_output= "A structured JSON object containing the extracted sections.",
        agent=resume_analyser,
        tools=[resume_extractor_tool],
    )

    #  Creating the task for Job Description Collector Agent
    task_job_scraper_agent=Task(
        description=("Extract the job description, skills and experience etc... from the provided link {job_description_link} by the user. Feel free to expect  one or multiple job descriptions from the user provided link and make sure you collect all job descriptions and return them in a json format this information would be passed to match evaluator agent to asses this information against the user resume."
        ),
        expected_output=("A structured JSON object containing the extracted job description, skills and experience etc... from the provided link {job_description_link} by the user. Feel free to expect  one or multiple job descriptions from the user provided link and make sure you collect all job descriptions and return them in a structured json format"),
        agent=job_scraper_agent,
        tools=[FirecrawlScrapeWebsiteTool(api_key=st.secrets["FIRECRAWL_API_KEY"])],
    )

    class ResumeMarkdownFormatterTool(BaseTool):
        name:str = "resume_markdown_formatter"
        description:str= "Formats an optimized resume and evaluation score into a markdown report"

        def _run(self, inputs: dict) -> str:
            # Load or hardcode your markdown template
            markdown_template = """
    # 🚀 Resume Optimization Report

    Hi there! 👋 We've analyzed your resume against the role of **{{ target_role }}** and optimized it to give you a better edge.

    ---

    ### 🎯 Before Optimisation Match Score: **{{ before_optimisation_match_score }} / 100**
    ### 🎯 After Optimisation Match Score: **{{ after_optimisation_match_score }} / 100**

    **Feedback:**  
    {{ feedback_message }}

    <!-- END OF FEEDBACK -->

    ---

    # ✨ Optimized Resume for _{{ target_role }}_

    ## 👤 Name
    **{{ name }}**

    <!-- END OF NAME -->

    ## 🧠 Summary  
    {{ summary }}

    <!-- END OF SUMMARY -->

    ## 🛠️ Skills
    {% for skill in skills %}
    - {{ skill }}
    {% endfor %}

    <!-- END OF SKILLS -->

    ## 💼 Work Experience
    {% for job in experience %}
    ### 📌 {{ job.job_title }} @ {{ job.company }}
    🗓️ {{ job.duration }}  
    {{ job.description }}
    {% endfor %}

    <!-- END OF WORK EXPERIENCE -->

    ## 🧪 Projects
    {% for p in projects %}
    ### {{ p.title }}
    {{ p.description }}
    {% endfor %}

    <!-- END OF PROJECTS -->


    ## 🎓 Education
    {% for e in education %}
    - **{{ e.degree }}**, _{{ e.institution }}_ ({{ e.year }})
    {% endfor %}

    <!-- END OF EDUCATION -->

    ## 📜 Certifications and Articles
    {% for c in certifications %}
    - {{ c }}
    {% endfor %}

    <!-- END OF CERTIFICATIONS and Articles -->

    Note: **This report is generated based on the information provided and the analysis conducted. Please review and make any necessary adjustments to ensure it accurately reflects your qualifications and experiences.**
    """

            # Render with provided inputs
            template = Template(markdown_template)
            return template.render(**inputs)


    # Creating Markdown Formatter Tool for resume_vs_jd

    class resume_vs_jd(BaseTool):
        name:str = "resume_vs_jd_formatter"
        description:str= "Formats the resume vs job description evaluation into a markdown report"

        def _run(self, inputs: dict) -> str:
            # Load or hardcode your markdown template
            markdown_template = """
            ### 📊 Resume vs Job Description Analysis

            ## 📈 Match Score: **{{ match_score }} / 100**

            #### ✅ Matched Skills
            {% if matched_skills %}
            {% for skill in matched_skills %}
            - {{ skill }}
            {% endfor %}
            {% else %}
            _No matched skills found._
            {% endif %}

            <!-- END OF MATCHED SKILLS -->

            #### ❌ Missing Skills
            {% if missing_skills %}
            {% for skill in missing_skills %}
            - {{ skill }}
            {% endfor %}
            {% else %}
            _No missing skills detected._
            {% endif %}
            <!-- END OF MISSING SKILLS -->

            #### 📝 Feedback
            {{ feedback_message }}
            <!-- END OF FEEDBACK -->

            """
            # Render with provided inputs
            template = Template(markdown_template)
            return template.render(**inputs)





    # Creating the Task for Match Evaluator Agent
    task_match_evaluator_agent=Task(description=("You are a highly experienced hiring consultant trained to compare resume with job descriptions and assess the candidate's fit. You will recieve a parsed resume from resume analyser agent and a structured job description from job description collector agent. Your job is to compare the two, identify matching and missing skills, highlight gaps, provide a match score and actionable feedback. "),
    expected_output="A structured Markdown resume vs job description comparison, generated by the attached tool with matching and missing skills, match_score and feedback.",agent=match_evaluator_agent,output_variable_name="resume_vs_jd_output",tools=[resume_vs_jd()])


    # Creating the Task for Resume Optimiser Agent
    task_resume_optimiser_agent=Task(description=("You will be given structured parsed resume data and a parsed job description. Also, consider the output of match evaluator agent to rewrite and optimise each section of the resume using a professional tone. Rewrite the **Summary**, **Skills**, ** Work Experience**, **projects**, and **certifications and Skills** sections of the resume."
    "- Match the tone and language of the target job role (e.g., technical, leadership, creative, etc.)"
    "- For each **bullet point in the experience and project sections**, follow the **STAR method**:"
    "- **Situation**: What was the context or challenge?"
    " - **Task**: What were you responsible for?"
    " - **Action**: What specific steps did you take? "
    "- **Result**: What was the measurable or tangible outcome? "

    "Your goal is to craft impactful, concise, and quantifiable resume content that increases the candidate’s chance of passing through both ATS and human reviewers."

    "Ensure formatting is clean and that the resume feels tailored for the role."), expected_output="Please return the output in a valid structured json format. Include all the sections of the optimised resume and do not forget any skills or sections and make sure sections are not duplicated",agent=resume_optimiser_agent)


    # Creating the Task for Resume Quality Assurance Agent

    qa_task = Task(
        description="""
    Review the optimized resume generated by the Resume Optimizer Agent.

    Your responsibilities:
    - Check that all resume sections are included (summary, skills, experience, education, projects, certifications).
    - Ensure the STAR method is followed for all bullet points in experience and projects.
    - Validate that the resume is aligned with the job description.
    - Check for missing or duplicated content.
    - Ensure there are no unnecessary repetitions.
    - Add skills section inside workexperience or projects section if not already present. make sure to include all skills used in the projects and work experience sections in the skills section as well.
    - Ensure the resume is well-structured and formatted in Markdown.
    - Check for spelling and grammatical errors and avoid repeating any section or bullet point. Each section should appear only once. Each project/experience should appear only once.
    - Ensure the tone and language match the target job role (e.g., technical, leadership, creative, etc.).

    If any of the above issues are found:
    - Regenerate an improved resume.
    - Follow all structure and formatting guidelines.
    - Return the improved resume as a Markdown document.
    - Include a short feedback summary at the top, along with a match score out of 100.
    """,
        expected_output="""
    Make sure you use tools at your disposal to create a clean, structured markdown report that contains all necessary sections, including the match score before and after optimising resume and feedback. Make sure that no section is missing or duplicated.
    """,
        agent=resume_qa_agent, tools=[ResumeMarkdownFormatterTool()]
    )




    # Creating Crew instance
    crew= Crew(
        agents=[resume_analyser,job_scraper_agent, match_evaluator_agent,resume_optimiser_agent,resume_qa_agent],
        tasks=[task_resume_analyser_agent, task_job_scraper_agent,task_match_evaluator_agent,task_resume_optimiser_agent,qa_task],
        verbose=True,
        memory=True
    )




    job_link="https://rarrtech.com/job-detail-nilasu-consulting-services-pvt-ltd-data-scientist-1-bangalore-bengaluru-1-2-years-167208"

    # Inputs
    inputs={
        "file_path":filepath,
        "job_role":"Data Scientist",
        "job_description_link":job_description_url
    }


    # Running the Crew instance
    result = crew.kickoff(inputs=inputs)
    print(type(crew.tasks[4].output))
    return str(crew.tasks[4].output)
    
