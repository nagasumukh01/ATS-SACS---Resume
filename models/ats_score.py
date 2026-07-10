from typing import Dict, Any, List
from utils.scoring import (
    score_experience, score_education, score_action_verbs, 
    check_formatting, check_completeness
)
from utils.similarity import SkillMatcher
from models.parser import segment_resume, extract_contact_info, parse_job_description

DEFAULT_WEIGHTS = {
    "skills": 0.25,
    "experience": 0.15,
    "projects": 0.15,
    "education": 0.10,
    "certifications": 0.05,
    "action_verbs": 0.05,
    "soft_skills": 0.10,
    "formatting": 0.05,
    "completeness": 0.10
}

def calculate_sacs(
    resume_text: str,
    jd_text: str,
    weights: Dict[str, float] = None
) -> Dict[str, Any]:
    """
    Calculates the Semantic ATS Compatibility Score (SACS).
    
    Returns a dictionary with:
        "overall_score": float,
        "component_scores": Dict[str, float],
        "parsed_resume": Dict[str, Any],
        "parsed_jd": Dict[str, Any],
        "skills_report": Dict[str, Any],
        "additions_ledger": List[str],
        "deductions_ledger": List[str]
    """
    if weights is None:
        weights = DEFAULT_WEIGHTS.copy()
        
    # Normalize weights so they sum to 1.0
    total_w = sum(weights.values())
    if total_w > 0:
        weights = {k: v / total_w for k, v in weights.items()}
    else:
        weights = DEFAULT_WEIGHTS.copy()

    # 1. Parse texts
    resume_sections = segment_resume(resume_text)
    contact_info = extract_contact_info(resume_text)
    parsed_jd = parse_job_description(jd_text)
    
    # 2. Initialize skill matcher
    matcher = SkillMatcher()
    
    # Extract JD skills from the JD text
    all_jd_skills = list(matcher.extract_skills_by_keywords(jd_text))
    
    # Separate technical skills from soft skills
    tech_jd_skills = []
    soft_jd_skills = []
    
    for s in all_jd_skills:
        meta = matcher.get_skill_details(s)
        if meta["category"] == "Soft Skill":
            soft_jd_skills.append(s)
        else:
            tech_jd_skills.append(s)
            
    # If no skills extracted from JD, use a fallback of extracting top nouns as skills (or set skills score to 100)
    # To keep SACS realistic, we'll run semantic matches on whatever we find
    tech_match_results = matcher.compute_semantic_skill_matches(resume_text, tech_jd_skills)
    soft_match_results = matcher.compute_semantic_skill_matches(resume_text, soft_jd_skills)
    
    # Calculate Hard Skills Score
    if tech_jd_skills:
        tech_score = sum(r["score"] * r["weight"] for r in tech_match_results.values()) / sum(r["weight"] for r in tech_match_results.values()) * 100.0
    else:
        tech_score = 100.0  # Full marks if no tech skills specified in JD
        
    # Calculate Soft Skills Score
    if soft_jd_skills:
        soft_score = sum(r["score"] * r["weight"] for r in soft_match_results.values()) / sum(r["weight"] for r in soft_match_results.values()) * 100.0
    else:
        soft_score = 100.0  # Full marks if no soft skills specified in JD

    # 3. Grade Experience
    exp_report = score_experience(
        resume_sections["experience"], 
        parsed_jd["experience_years"], 
        jd_text
    )
    
    # 4. Grade Education
    edu_report = score_education(
        resume_sections["education"], 
        parsed_jd["education_required"]
    )
    
    # 5. Grade Projects
    # Compute semantic relevance of projects to the job description
    proj_text = resume_sections["projects"]
    if proj_text:
        from models.embedding import get_single_embedding, compute_cosine_similarity
        proj_emb = get_single_embedding(proj_text)
        jd_emb = get_single_embedding(jd_text)
        proj_sim = compute_cosine_similarity(proj_emb, jd_emb)
        # scale similarity
        proj_score = min(100.0, max(0.0, (proj_sim - 0.15) / 0.65 * 100.0))
    else:
        proj_score = 0.0
        
    # 6. Grade Certifications
    cert_text = resume_sections["certifications"]
    cert_score = 30.0 # Default if none
    if cert_text:
        # Search for certifications related to JD categories
        has_relevant = False
        for s in tech_jd_skills:
            meta = matcher.get_skill_details(s)
            parent = meta["parent"]
            if parent and (parent.lower() in cert_text.lower() or s.lower() in cert_text.lower()):
                has_relevant = True
                break
        if has_relevant:
            cert_score = 100.0
        else:
            cert_score = 75.0 # General certifications present
            
    # 7. Grade Action Verbs
    verb_report = score_action_verbs(resume_text)
    
    # 8. Grade Formatting
    format_report = check_formatting(resume_text)
    
    # 9. Grade Section Completeness
    completeness_report = check_completeness(resume_sections, contact_info)

    # 10. Assemble components
    component_scores = {
        "skills": round(tech_score, 1),
        "experience": exp_report["score"],
        "projects": round(proj_score, 1),
        "education": edu_report["score"],
        "certifications": cert_score,
        "action_verbs": verb_report["score"],
        "soft_skills": round(soft_score, 1),
        "formatting": format_report["score"],
        "completeness": completeness_report["score"]
    }
    
    # Calculate SACS overall weighted score
    overall_score = sum(component_scores[k] * weights[k] for k in component_scores.keys())
    overall_score = round(overall_score, 1)

    # 11. Compile ledger
    additions_ledger = []
    deductions_ledger = []
    
    # Add skills feedback
    matched_tech = [s for s, r in tech_match_results.items() if r["score"] >= 0.75]
    missing_tech = [s for s, r in tech_match_results.items() if r["score"] < 0.5]
    transfer_tech = [s for s, r in tech_match_results.items() if r["match_type"] == "Transferable"]
    
    if matched_tech:
        additions_ledger.append(f"Successfully matched key technical skills: {', '.join(matched_tech[:5])}")
    if transfer_tech:
        additions_ledger.append(
            "Credited transferable/family skills: " + ", ".join([f"{s} (via {tech_match_results[s]['matched_with']})" for s in transfer_tech[:3]])
        )
    if missing_tech:
        deductions_ledger.append(f"Missing high-priority technical skills from JD: {', '.join(missing_tech[:5])}")
        
    # Add soft skills feedback
    matched_soft = [s for s, r in soft_match_results.items() if r["score"] >= 0.75]
    missing_soft = [s for s, r in soft_match_results.items() if r["score"] < 0.5]
    if matched_soft:
        additions_ledger.append(f"Demonstrated soft skills: {', '.join(matched_soft[:4])}")
    if missing_soft:
        deductions_ledger.append(f"Soft skills lacking or not highlighted: {', '.join(missing_soft[:4])}")

    # Add other reports
    additions_ledger.extend(exp_report["additions"])
    deductions_ledger.extend(exp_report["deductions"])
    
    additions_ledger.extend(edu_report["additions"])
    deductions_ledger.extend(edu_report["deductions"])
    
    if proj_score >= 80.0:
        additions_ledger.append("High project relevance. Project descriptions show alignment with JD challenges.")
    elif proj_score < 50.0:
        if proj_text:
            deductions_ledger.append("Candidate projects are semantically misaligned or lack details matching the JD role.")
        else:
            deductions_ledger.append("No projects section found in the resume. Projects add substantial weight to resume scores.")
            
    if cert_score == 100.0:
        additions_ledger.append("Verified relevant professional certifications.")
    elif cert_score == 30.0:
        deductions_ledger.append("No certifications section found. Consider listing professional certificates.")
        
    additions_ledger.extend(verb_report["additions"])
    deductions_ledger.extend(verb_report["deductions"])
    
    additions_ledger.extend(format_report["additions"])
    deductions_ledger.extend(format_report["deductions"])
    
    additions_ledger.extend(completeness_report["additions"])
    deductions_ledger.extend(completeness_report["deductions"])

    # Compile a return object
    return {
        "overall_score": overall_score,
        "component_scores": component_scores,
        "weights": weights,
        "parsed_resume": {
            "contact": contact_info,
            "sections": resume_sections,
            "text": resume_text
        },
        "parsed_jd": parsed_jd,
        "skills_report": {
            "tech": tech_match_results,
            "soft": soft_match_results,
            "all_extracted_jd": all_jd_skills,
            "matched_tech": matched_tech,
            "missing_tech": missing_tech,
            "transfer_tech": transfer_tech,
            "matched_soft": matched_soft,
            "missing_soft": missing_soft
        },
        "additions_ledger": additions_ledger,
        "deductions_ledger": deductions_ledger
    }
