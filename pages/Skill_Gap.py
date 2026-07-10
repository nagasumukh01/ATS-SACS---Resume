import streamlit as st
from utils.visualization import plot_skill_network, plot_skill_gap_heatmap
from models.recommendation import get_learning_path

def show():
    # Load custom styles
    with open("assets/custom.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        
    st.markdown("<h2 class='gradient-text'>Skill Gap Analysis</h2>", unsafe_allow_html=True)
    st.write("Detailed view of matched, transferable, and missing skills with target learning paths.")
    
    if "sacs_result" not in st.session_state:
        st.warning("⚠️ No active analysis found. Please run the analysis on the 'Resume Analysis' page first.")
        return
        
    results = st.session_state.sacs_result
    skills_report = results["skills_report"]
    
    # Category separation
    matched_tech = skills_report["matched_tech"]
    missing_tech = skills_report["missing_tech"]
    transfer_tech = skills_report["transfer_tech"]
    
    tab1, tab2, tab3 = st.tabs(["📊 Skill Match Ledger", "🕸️ Interactive Skill Network", "📚 Recommended Learning Paths"])
    
    with tab1:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("Skill Match Summary")
        
        # Display Badges
        col_b1, col_b2, col_b3 = st.columns(3)
        with col_b1:
            st.markdown("🟢 **Matched Skills**")
            if matched_tech:
                for s in matched_tech:
                    st.markdown(f"<span class='skill-badge badge-match'>{s}</span>", unsafe_allow_html=True)
            else:
                st.write("*None*")
                
        with col_b2:
            st.markdown("🟡 **Transferable Skills**")
            if transfer_tech:
                for s in transfer_tech:
                    matched_with = skills_report["tech"][s]["matched_with"]
                    st.markdown(f"<span class='skill-badge badge-priority-high'>{s}</span> <small style='color:#A0AEC0;'>via {matched_with}</small><br>", unsafe_allow_html=True)
            else:
                st.write("*None*")
                
        with col_b3:
            st.markdown("🔴 **Missing Skills**")
            if missing_tech:
                for s in missing_tech:
                    st.markdown(f"<span class='skill-badge badge-missing'>{s}</span>", unsafe_allow_html=True)
            else:
                st.write("*None*")
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("Skill Similarity Heatmap")
        st.plotly_chart(plot_skill_gap_heatmap(skills_report), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with tab2:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("Visual Skill Network Relationship")
        st.write("This interactive network shows how your skills connect to the target job role. Green nodes indicate exact matches, light blue indicate semantic matches, orange represent transferable skills (matching the family/category), and red indicate missing requirements. Nodes are sized by weight priority.")
        
        # Render custom Plotly network
        fig_net = plot_skill_network(skills_report["tech"], skills_report["soft"])
        st.plotly_chart(fig_net, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with tab3:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("Tailored Learning Paths")
        st.write("Click on any missing skill to view a structured learning path with curated free resources to bridge your skill gap.")
        
        if not missing_tech:
            st.success("🎉 Outstanding! You match all technical skills identified in the Job Description.")
        else:
            for skill in missing_tech:
                path = get_learning_path(skill)
                with st.expander(f"📖 Study Guide for: {skill}"):
                    col_p1, col_p2 = st.columns(2)
                    with col_p1:
                        st.markdown("**Key Topics to Master:**")
                        for t in path["topics"]:
                            st.markdown(f"- {t}")
                    with col_p2:
                        st.markdown("**Recommended Free Resources:**")
                        for r in path["resources"]:
                            st.markdown(f"- 🌐 {r}")
        st.markdown("</div>", unsafe_allow_html=True)
