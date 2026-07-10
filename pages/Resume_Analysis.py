import streamlit as st
import os
import tempfile
from models.parser import extract_text
from models.ats_score import calculate_sacs
from utils.visualization import plot_sacs_gauge

def show():
    # Load custom styles
    with open("assets/custom.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        
    st.markdown("<h2 class='gradient-text'>Resume & Job Description Analysis</h2>", unsafe_allow_html=True)
    st.write("Upload your resume and the target job description to compute your Semantic ATS score.")
    
    # Weights configuration in sidebar or expander
    with st.expander("⚙️ Customize SACS Component Weights (Advanced)"):
        st.write("Adjust weights to match specific company hiring priorities. Total weights will automatically normalize to 100%.")
        col_w1, col_w2, col_w3 = st.columns(3)
        with col_w1:
            w_skills = st.slider("Technical Skills", 0, 100, 25, step=5) / 100.0
            w_exp = st.slider("Experience Match", 0, 100, 15, step=5) / 100.0
            w_proj = st.slider("Project Relevance", 0, 100, 15, step=5) / 100.0
        with col_w2:
            w_edu = st.slider("Education Level", 0, 100, 10, step=5) / 100.0
            w_cert = st.slider("Certifications", 0, 100, 5, step=5) / 100.0
            w_soft = st.slider("Soft Skills", 0, 100, 10, step=5) / 100.0
        with col_w3:
            w_verbs = st.slider("Action Verbs Density", 0, 100, 5, step=5) / 100.0
            w_format = st.slider("Formatting Quality", 0, 100, 5, step=5) / 100.0
            w_comp = st.slider("Profile Completeness", 0, 100, 10, step=5) / 100.0
            
        custom_weights = {
            "skills": w_skills,
            "experience": w_exp,
            "projects": w_proj,
            "education": w_edu,
            "certifications": w_cert,
            "action_verbs": w_verbs,
            "soft_skills": w_soft,
            "formatting": w_format,
            "completeness": w_comp
        }
    
    col_u1, col_u2 = st.columns(2)
    
    with col_u1:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("📄 Upload Resume")
        uploaded_resume = st.file_uploader("Drop PDF, DOCX or TXT file here", type=["pdf", "docx", "txt"], key="resume_uploader")
        
        # Resume text editing pane
        resume_text = st.text_area(
            "Extracted Resume Text (Editable)", 
            value=st.session_state.get("resume_text_raw", ""),
            height=280,
            help="You can edit the parsed resume text here to correct spelling or add missing sections before calculating scores."
        )
        
        # If user uploaded a new resume
        if uploaded_resume is not None:
            # Check if this is a new upload
            if "last_uploaded_resume" not in st.session_state or st.session_state.last_uploaded_resume != uploaded_resume.name:
                with st.spinner("Extracting text from resume..."):
                    # Save to temp file
                    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_resume.name)[1]) as tmp:
                        tmp.write(uploaded_resume.getvalue())
                        tmp_path = tmp.name
                    try:
                        extracted = extract_text(tmp_path)
                        st.session_state.resume_text_raw = extracted
                        st.session_state.last_uploaded_resume = uploaded_resume.name
                        st.rerun()
                    finally:
                        os.unlink(tmp_path)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_u2:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("💼 Job Description")
        uploaded_jd = st.file_uploader("Upload JD (Optional)", type=["pdf", "docx", "txt"], key="jd_uploader")
        
        jd_text = st.text_area(
            "Paste Job Description Here", 
            value=st.session_state.get("jd_text_raw", ""),
            height=280,
            help="Paste the job listing text here. This serves as the target profile for semantic similarity comparisons."
        )
        
        # If user uploaded a JD
        if uploaded_jd is not None:
            if "last_uploaded_jd" not in st.session_state or st.session_state.last_uploaded_jd != uploaded_jd.name:
                with st.spinner("Extracting text from Job Description..."):
                    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_jd.name)[1]) as tmp:
                        tmp.write(uploaded_jd.getvalue())
                        tmp_path = tmp.name
                    try:
                        extracted = extract_text(tmp_path)
                        st.session_state.jd_text_raw = extracted
                        st.session_state.last_uploaded_jd = uploaded_jd.name
                        st.rerun()
                    finally:
                        os.unlink(tmp_path)
        st.markdown("</div>", unsafe_allow_html=True)
        
    # Analyze Trigger Button
    st.write("")
    if st.button("Run Semantic ATS Analysis ⚡", use_container_width=True, type="primary"):
        # Check inputs
        if not resume_text.strip():
            st.error("Please upload a resume or paste its text in the text area.")
            return
        if not jd_text.strip():
            st.error("Please paste a Job Description to run the ATS compatibility mapping.")
            return
            
        # Store in session state
        st.session_state.resume_text_raw = resume_text
        st.session_state.jd_text_raw = jd_text
        
        # Calculate
        with st.spinner("Executing SACS Scoring Engine... (loading model, calculating semantic similarities, evaluating experience...)"):
            try:
                results = calculate_sacs(resume_text, jd_text, custom_weights)
                st.session_state.sacs_result = results
                st.success("ATS Analysis completed successfully! See other tabs for detailed dashboards.")
            except Exception as e:
                st.error(f"Failed to process analysis: {str(e)}")
                return
                
    # Quick Results Panel if results exist
    if "sacs_result" in st.session_state:
        results = st.session_state.sacs_result
        score = results["overall_score"]
        
        st.write("---")
        st.markdown("### 📊 SACS Quick Overview")
        
        col_res1, col_res2 = st.columns([1, 1])
        
        with col_res1:
            st.plotly_chart(plot_sacs_gauge(score), use_container_width=True)
            
        with col_res2:
            st.markdown("<div class='glass-card' style='height: 320px; overflow-y: auto;'>", unsafe_allow_html=True)
            st.subheader("Key Findings")
            
            # Show top 3 additions and deductions
            additions = results["additions_ledger"]
            deductions = results["deductions_ledger"]
            
            st.markdown("##### 🟢 Top Strengths:")
            if additions:
                for add in additions[:3]:
                    st.markdown(f"- {add}")
            else:
                st.write("No major strengths identified.")
                
            st.markdown("##### 🔴 High Priority Adjustments:")
            if deductions:
                for ded in deductions[:3]:
                    st.markdown(f"- {ded}")
            else:
                st.write("No major weaknesses identified.")
            st.markdown("</div>", unsafe_allow_html=True)
            
        st.info("💡 Explore the **Skill Gap**, **Explainability**, and **Analytics** pages in the sidebar for full breakdowns.")
