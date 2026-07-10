import streamlit as st
import pandas as pd
from utils.visualization import plot_feature_importance
from models.explainability import compute_feature_importance, compute_skill_importance

def show():
    # Load custom styles
    with open("assets/custom.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        
    st.markdown("<h2 class='gradient-text'>Explainability Dashboard</h2>", unsafe_allow_html=True)
    st.write("Transparent mathematical audit of how your SACS score was calculated and the impact of individual features.")
    
    if "sacs_result" not in st.session_state:
        st.warning("⚠️ No active analysis found. Please run the analysis on the 'Resume Analysis' page first.")
        return
        
    results = st.session_state.sacs_result
    resume_text = st.session_state.resume_text_raw
    jd_text = st.session_state.jd_text_raw
    weights = results["weights"]
    
    tab1, tab2, tab3 = st.tabs(["🧩 Component Importance", "⚖️ Scoring Ledger", "🎯 Individual Skill Impact"])
    
    with tab1:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("Component Weight Contribution")
        st.write("The chart below shows the weighted points contributed by each section of your profile to the overall SACS score. Highly rated components with large weights provide the largest bars.")
        
        # Calculate feature importance
        feat_imp = compute_feature_importance(resume_text, jd_text, weights)
        fig_imp = plot_feature_importance(feat_imp)
        st.plotly_chart(fig_imp, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("<div class='glass-card' style='height: 500px; overflow-y: auto;'>", unsafe_allow_html=True)
            st.subheader("🟢 Gained Credits")
            st.write("Points were added to your profile for demonstrating the following items:")
            for add in results["additions_ledger"]:
                st.markdown(
                    f"<div class='success-callout'><b>+ Credit:</b> {add}</div>", 
                    unsafe_allow_html=True
                )
            if not results["additions_ledger"]:
                st.write("*No major points gained.*")
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col2:
            st.markdown("<div class='glass-card' style='height: 500px; overflow-y: auto;'>", unsafe_allow_html=True)
            st.subheader("🔴 Point Deductions")
            st.write("Points were deducted or missing from your profile due to the following gaps:")
            for ded in results["deductions_ledger"]:
                st.markdown(
                    f"<div class='warning-callout'><b>- Deduction:</b> {ded}</div>", 
                    unsafe_allow_html=True
                )
            if not results["deductions_ledger"]:
                st.write("*No major points deducted. Perfect match!*")
            st.markdown("</div>", unsafe_allow_html=True)
            
    with tab3:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("Marginal Skill Point Contributions")
        st.write("This table shows the exact points contributed or lost for each technical and soft skill required by the JD. This highlights exactly which skills are the most critical to add to your resume.")
        
        # Calculate skill importance
        skill_imp = compute_skill_importance(results)
        
        if not skill_imp:
            st.info("No explicit skills were identified in the Job Description to calculate impact.")
        else:
            # Convert to Pandas DataFrame for rendering
            df_items = []
            for item in skill_imp:
                impact_symbol = "+" if item["impact"] >= 0 else ""
                df_items.append({
                    "Skill Requirement": item["skill"],
                    "Category": item["type"],
                    "Match Mode": item["match_type"],
                    "Candidate Similarity": f"{int(item['similarity']*100)}%",
                    "Max Available (pts)": f"{item['max_points']:.2f}",
                    "Marginal Impact (pts)": f"{impact_symbol}{item['impact']:.2f}"
                })
                
            df = pd.DataFrame(df_items)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            st.write("")
            st.info("💡 **How to read this table:** A positive impact indicates points added to your score. A negative impact indicates points lost due to a lack of matching. Focus on resolving skills with the largest negative impact.")
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Summary metrics
        st.write("")
