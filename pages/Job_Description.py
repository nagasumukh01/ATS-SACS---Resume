import streamlit as st
from models.ats_score import calculate_sacs

def show():
    # Load custom styles
    with open("assets/custom.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        
    st.markdown("<h2 class='gradient-text'>Job Description Parameters</h2>", unsafe_allow_html=True)
    st.write("Review and adjust the parameters extracted from your target Job Description (JD).")
    
    if "sacs_result" not in st.session_state:
        st.warning("⚠️ No active analysis found. Please run the analysis on the 'Resume Analysis' page first.")
        return
        
    results = st.session_state.sacs_result
    parsed_jd = results["parsed_jd"]
    skills_report = results["skills_report"]
    
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("🛠️ Extracted Parameters")
    
    col1, col2 = st.columns(2)
    with col1:
        # Years of Experience
        exp_input = st.number_input(
            "Required Experience Years", 
            min_value=0, 
            max_value=25, 
            value=int(parsed_jd["experience_years"]), 
            step=1
        )
    with col2:
        # Degree requirement
        degree_options = ["High School", "Associate's", "Bachelor's", "Master's", "PhD"]
        default_idx = degree_options.index(parsed_jd["education_required"]) if parsed_jd["education_required"] in degree_options else 2
        degree_input = st.selectbox(
            "Minimum Required Degree",
            options=degree_options,
            index=default_idx
        )
        
    st.write("")
    
    # Skills adjustment
    all_extracted_skills = skills_report["all_extracted_jd"]
    st.markdown("##### Extracted Job Skills")
    st.write("These skills were semantically identified in the JD. You can modify this list if some skills are irrelevant or missed.")
    
    selected_skills = st.multiselect(
        "Required Skills List",
        options=all_extracted_skills + ["Python", "Docker", "Kubernetes", "AWS", "SQL", "React", "Machine Learning", "Communication", "Leadership", "Agile"],
        default=all_extracted_skills
    )
    st.markdown("</div>", unsafe_allow_html=True)
    
    # JD Sections View
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("📝 Parsed Text Segments")
    tab1, tab2 = st.tabs(["Responsibilities", "Requirements"])
    
    with tab1:
        resp_text = parsed_jd["key_sections"]["responsibilities"]
        if resp_text:
            st.text_area("Extracted Responsibilities", value=resp_text, height=200, disabled=True)
        else:
            st.info("No specific responsibilities section detected. The text was parsed globally.")
            
    with tab2:
        req_text = parsed_jd["key_sections"]["requirements"]
        if req_text:
            st.text_area("Extracted Requirements", value=req_text, height=200, disabled=True)
        else:
            st.info("No specific requirements section detected. The text was parsed globally.")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Re-run button
    st.write("")
    if st.button("Apply Parameter Updates & Re-Calculate Score 🔄", use_container_width=True, type="primary"):
        # Update parsed JD in session state
        st.session_state.sacs_result["parsed_jd"]["experience_years"] = exp_input
        st.session_state.sacs_result["parsed_jd"]["education_required"] = degree_input
        
        # Calculate again using updated parameters
        with st.spinner("Re-calculating score with updated criteria..."):
            try:
                # We will perform a custom rerun of SACS calculation using updated variables.
                # To do this, we can run calculate_sacs and override the skills and details.
                # However, for simplicity and speed, we can recompute the similarities using the custom skill list.
                # Let's adjust SACS by calling recalculation.
                weights = st.session_state.sacs_result["weights"]
                resume_text = st.session_state.resume_text_raw
                
                # To override parameters, we construct a temp JD text or update SACS score elements.
                # Since years of experience and skills were edited, we can re-evaluate using a modified calculate_sacs.
                # Let's pass a modified job description text that reflects the updates, or we can patch the sacs calculation logic.
                # A simple and robust way is to regenerate a synthetic Job Description containing the parameters,
                # e.g., "Job description. Required experience: {exp_input} years. Required degree: {degree_input}. Skills: {', '.join(selected_skills)}."
                synthetic_jd = (
                    f"Job Description. Required Experience: {exp_input} years. "
                    f"Required Degree: {degree_input}. "
                    f"Required Skills and Technologies: {', '.join(selected_skills)}. "
                    f"Responsibilities: {resp_text}. Requirements: {req_text}"
                )
                
                new_results = calculate_sacs(resume_text, synthetic_jd, weights)
                
                # Restore original text segments in parsed JD
                new_results["parsed_jd"]["key_sections"]["responsibilities"] = resp_text
                new_results["parsed_jd"]["key_sections"]["requirements"] = req_text
                
                st.session_state.sacs_result = new_results
                st.success("SACS Score successfully updated with the new job parameters!")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to recalculate: {str(e)}")
