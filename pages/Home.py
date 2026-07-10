import streamlit as st

def show():
    # Load custom styles
    with open("assets/custom.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        
    st.markdown("<h1 class='gradient-text' style='text-align: center; font-size: 3rem;'>Explainable Resume ATS Optimizer</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #A0AEC0; font-size: 1.2rem;'>Next-Generation ATS Benchmarking powered by the Semantic ATS Compatibility Score (SACS)</p>", unsafe_allow_html=True)
    
    st.write("---")
    
    # 2 Column layout
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("🔬 Research Contribution: The SACS Framework")
        st.write(
            "Traditional Application Tracking Systems (ATS) rely on basic keyword frequency. This makes them "
            "vulnerable to keyword-stuffing and highly penalizes qualified candidates who use synonyms. "
            "The **Semantic ATS Compatibility Score (SACS)** solves this by utilizing sentence embedding "
            "representations (`all-MiniLM-L6-v2`) to compare resume content semantically against job requirements."
        )
        
        # SACS mathematical formula in LaTeX
        st.markdown("##### SACS Mathematical Formulation")
        st.latex(r"""
        SACS = w_{skill} \cdot S_{skill} + w_{exp} \cdot S_{exp} + w_{proj} \cdot S_{proj} + w_{edu} \cdot S_{edu} + w_{cert} \cdot S_{cert} + w_{verb} \cdot S_{verb} + w_{soft} \cdot S_{soft} + w_{format} \cdot S_{format} + w_{comp} \cdot S_{comp}
        """)
        
        st.write(
            "Where $S_i$ represents component similarity scores (ranging from 0 to 100), and $w_i$ represents "
            "user-adjustable weight coefficients normalized to sum to $1.0$."
        )
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("💡 Core Features")
        st.markdown(
            """
            - **No Black-Box Scoring**: Explains exactly why points are added or deducted for every SACS component.
            - **Semantic Skill Matching**: Maps synonyms and rewards transferable skills inside same technology families.
            - **Local Execution**: Uses local deep learning models for extraction, ensuring data privacy and fast analysis.
            - **Interactive Visualizations**: View skill gaps via interactive Plotly network maps and polar radar charts.
            - **Smart Resume Rewriter**: Auto-improves weak bullet points to align with active action-verb expectations.
            """
        )
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col2:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("🚀 System Architecture Flowchart")
        # Markdown flowchart
        st.markdown(
            """
            ```mermaid
            graph TD
                A[Resume PDF/Docx] --> B(Extraction & NLP Parser)
                C[Job Description] --> B
                B --> D{Semantic Embedding Model}
                D --> E[SACS Scoring Engine]
                E --> F[Explainable XAI Ledger]
                E --> G[Visual Skill Gap Net]
                F --> H[Interactive Rewriter]
            ```
            """
        )
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Start button
        st.write("")
        st.write("")
        if st.button("Start Analysis 🚀", use_container_width=True, type="primary"):
            st.session_state.current_page = "Resume Analysis"
            st.rerun()
            
    st.write("---")
    st.markdown("<p style='text-align: center; color: #718096; font-size: 0.8rem;'>Explainable Resume ATS Optimizer © 2026. Built for research-grade career optimization.</p>", unsafe_allow_html=True)
