from typing import Dict, Any, List
import copy

def compute_feature_importance(
    resume_text: str,
    jd_text: str,
    weights: Dict[str, float] = None
) -> Dict[str, float]:
    """
    Computes Shapley-like feature importance for the SACS components.
    It does this by calculating the baseline SACS, then perturbing the score
    by setting each component to 0.0 sequentially, measuring the delta.
    """
    from models.ats_score import calculate_sacs
    
    # Calculate baseline
    baseline_result = calculate_sacs(resume_text, jd_text, weights)
    baseline_score = baseline_result["overall_score"]
    comp_scores = baseline_result["component_scores"]
    active_weights = baseline_result["weights"]
    
    importance = {}
    for comp_name, score in comp_scores.items():
        # The contribution of a component is its score weighted by its weight parameter
        # This represents its absolute point contribution to the final SACS score (0-100)
        contribution = score * active_weights.get(comp_name, 0.0)
        importance[comp_name] = round(contribution, 2)
        
    return importance

def compute_skill_importance(
    sacs_result: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Calculates the point impact of each individual JD skill on the overall score.
    Returns a list of dictionaries with skill name, match type, similarity score,
    weight, and points added or lost.
    """
    skills_report = sacs_result["skills_report"]
    tech_results = skills_report["tech"]
    soft_results = skills_report["soft"]
    weights = sacs_result["weights"]
    
    skill_weights = weights.get("skills", 0.25)
    soft_weights = weights.get("soft_skills", 0.10)
    
    importance_list = []
    
    # Process technical skills
    if tech_results:
        total_tech_weight = sum(r["weight"] for r in tech_results.values())
        if total_tech_weight > 0:
            for skill_name, match in tech_results.items():
                # Contribution to technical component = score * weight / total_weight
                # Contribution to overall SACS = component_contribution * skill_weights
                # Max potential points this skill can provide: (1.0 * weight / total_weight) * 100 * skill_weights
                max_pts = (1.0 * match["weight"] / total_tech_weight) * 100.0 * skill_weights
                pts_earned = (match["score"] * match["weight"] / total_tech_weight) * 100.0 * skill_weights
                pts_impact = pts_earned if match["score"] >= 0.5 else (pts_earned - max_pts)
                
                importance_list.append({
                    "skill": skill_name,
                    "type": "Technical",
                    "match_type": match["match_type"],
                    "matched_with": match["matched_with"],
                    "similarity": match["score"],
                    "max_points": round(max_pts, 2),
                    "points_earned": round(pts_earned, 2),
                    "impact": round(pts_impact, 2)
                })

    # Process soft skills
    if soft_results:
        total_soft_weight = sum(r["weight"] for r in soft_results.values())
        if total_soft_weight > 0:
            for skill_name, match in soft_results.items():
                max_pts = (1.0 * match["weight"] / total_soft_weight) * 100.0 * soft_weights
                pts_earned = (match["score"] * match["weight"] / total_soft_weight) * 100.0 * soft_weights
                pts_impact = pts_earned if match["score"] >= 0.5 else (pts_earned - max_pts)
                
                importance_list.append({
                    "skill": skill_name,
                    "type": "Soft Skill",
                    "match_type": match["match_type"],
                    "matched_with": match["matched_with"],
                    "similarity": match["score"],
                    "max_points": round(max_pts, 2),
                    "points_earned": round(pts_earned, 2),
                    "impact": round(pts_impact, 2)
                })
                
    # Sort by absolute impact descending so the user sees the most important items first
    importance_list.sort(key=lambda x: abs(x["impact"]), reverse=True)
    return importance_list
