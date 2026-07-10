import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import torch  # Must be imported before streamlit/other packages to prevent DLL loading conflicts on Windows

import streamlit as st
from streamlit_option_menu import option_menu
from utils.preprocessing import ensure_skills_db

# 1. Page Configuration
st.set_page_config(
    page_title="Explainable Resume ATS Optimizer",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Boot Setup
ensure_skills_db()
os.makedirs(os.path.join("data", "resumes"), exist_ok=True)
os.makedirs(os.path.join("data", "job_descriptions"), exist_ok=True)

# 3. Preload Sample Data in session state
SAMPLE_RESUME = """John Doe
john.doe@email.com | (123) 456-7890 | Seattle, WA
github.com/johndoe | linkedin.com/in/johndoe

SUMMARY
Experienced and results-driven Software Engineer with 4 years of professional experience specializing in backend architectures, cloud applications, and microservices. Proven history of optimizing database performance and spearheading backend API developments.

TECHNICAL SKILLS
Languages: Python, JavaScript, SQL, HTML, CSS
Frameworks & Libraries: Django, Flask, React, NumPy, Pandas
Databases: PostgreSQL, MySQL, Redis
Tools & DevOps: Git, Docker, GitHub Actions, Linux
Methodologies: Agile, Scrum, Problem Solving, Collaboration

WORK EXPERIENCE
Software Engineer | CloudScale Systems (May 2022 - Present)
- Spearheaded the design and implementation of a core Django REST API service, increasing API response throughput by 35% and reducing latency.
- Containerized legacy microservices using Docker, streamlining local development setups and dev environment alignment.
- Optimized complex PostgreSQL database queries and indexes, saving over 12 hours of weekly database maintenance tasks.
- Collaborated closely with cross-functional React front-end engineering teams to deliver responsive features.

Junior Developer | ByteCraft Solutions (June 2020 - April 2022)
- Maintained and updated Flask backend APIs for a high-traffic e-commerce portal.
- Configured automated test suites via GitHub Actions, decreasing integration build failures by 20%.
- Participated in weekly Agile standups and sprint planning sessions to coordinate deliverables.

EDUCATION
Bachelor of Science in Computer Science
State University, 2016 - 2020

CERTIFICATIONS
AWS Certified Solutions Architect (Associate)
Certified Scrum Master (CSM)
"""

SAMPLE_JD = """Position: Senior Backend Engineer - Python

We are seeking a Senior Backend Engineer to join our cloud platform team. In this role, you will design, build, and optimize scalable APIs and data processing systems.

Requirements:
- 5+ years of experience in backend development.
- Strong proficiency in Python and FastAPI or Django.
- Experience with containerization using Docker and orchestration with Kubernetes.
- Hand-on experience deploying and managing services on AWS.
- Strong experience with SQL databases, particularly PostgreSQL.
- Excellent communication and collaboration skills.

Responsibilities:
- Architect and develop secure, high-performance APIs.
- Containerize application environments and manage deployment configurations in Kubernetes.
- Drive database schema migrations and perform backend query optimizations.
- Work closely with frontend and product teams in an Agile environment.
"""

if "resume_text_raw" not in st.session_state:
    st.session_state.resume_text_raw = SAMPLE_RESUME
if "jd_text_raw" not in st.session_state:
    st.session_state.jd_text_raw = SAMPLE_JD
if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"

# 4. Navigation Menu Setup
menu_options = [
    "Home", 
    "Resume Analysis", 
    "Job Description", 
    "Skill Gap", 
    "Explainability", 
    "Resume Rewriter", 
    "Analytics"
]

default_idx = menu_options.index(st.session_state.current_page)

# Import page modules
from pages import (
    Home, Resume_Analysis, Job_Description, 
    Skill_Gap, Explainability, Resume_Rewriter, Analytics
)

with st.sidebar:
    st.markdown("<h2 class='gradient-text' style='text-align: center; font-size: 1.5rem;'>🔬 ATS SACS</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 0.8rem; color: #A0AEC0;'>Explainable Resume Optimizer</p>", unsafe_allow_html=True)
    st.write("---")
    
    selected = option_menu(
        menu_title=None,
        options=menu_options,
        icons=["house", "cloud-upload", "file-earmark-text", "bar-chart-steps", "eye", "pencil-square", "graph-up"],
        menu_icon="cast",
        default_index=default_idx,
        styles={
            "container": {"padding": "0!important", "background-color": "#1E2235"},
            "icon": {"color": "#6C63FF", "font-size": "16px"}, 
            "nav-link": {"font-size": "14px", "text-align": "left", "margin":"0px", "color": "#FFFFFF", "--hover-color": "rgba(108, 99, 255, 0.1)"},
            "nav-link-selected": {"background-color": "#6C63FF", "color": "#FFFFFF"},
        }
    )
    
    st.write("---")
    # Quick Status Indicator
    if "sacs_result" in st.session_state:
        score = st.session_state.sacs_result["overall_score"]
        st.metric("Current SACS Grade", f"{score}/100")
    else:
        st.caption("Status: Awaiting Analysis")

# Sync selection to page state
st.session_state.current_page = selected

# 5. Route to pages
if selected == "Home":
    Home.show()
elif selected == "Resume Analysis":
    Resume_Analysis.show()
elif selected == "Job Description":
    Job_Description.show()
elif selected == "Skill Gap":
    Skill_Gap.show()
elif selected == "Explainability":
    Explainability.show()
elif selected == "Resume Rewriter":
    Resume_Rewriter.show()
elif selected == "Analytics":
    Analytics.show()
