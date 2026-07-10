import pandas as pd
import numpy as np
import os
import re
from typing import List, Dict, Set, Any, Tuple
from models.embedding import get_embeddings, get_single_embedding, compute_cosine_similarity

class SkillMatcher:
    def __init__(self, db_path: str = "data/skills_database.csv"):
        self.db_path = db_path
        self.skills_df = None
        self.skills_dict = {}  # skill_name -> metadata
        self.synonym_map = {}  # synonym_lowercase -> skill_name
        self.load_database()

    def load_database(self):
        """Loads the skills database from CSV and pre-populates lookup maps."""
        if not os.path.exists(self.db_path):
            from utils.preprocessing import ensure_skills_db
            ensure_skills_db()
            
        try:
            self.skills_df = pd.read_csv(self.db_path)
            for _, row in self.skills_df.iterrows():
                skill_name = str(row["SkillName"])
                category = str(row["Category"])
                synonyms = str(row["Synonyms"]).split(",")
                parent = str(row["ParentSkill"]) if not pd.isna(row["ParentSkill"]) else None
                weight = float(row["WeightMultiplier"]) if not pd.isna(row["WeightMultiplier"]) else 1.0
                
                self.skills_dict[skill_name] = {
                    "name": skill_name,
                    "category": category,
                    "parent": parent,
                    "weight": weight,
                    "synonyms": synonyms
                }
                
                # Add skill name itself as a synonym
                self.synonym_map[skill_name.lower()] = skill_name
                # Map all defined synonyms
                for syn in synonyms:
                    self.synonym_map[syn.strip().lower()] = skill_name
        except Exception as e:
            print(f"Error loading skills database: {str(e)}")

    def extract_skills_by_keywords(self, text: str) -> Set[str]:
        """
        Extracts skills explicitly mentioned in the text using the synonyms database.
        """
        if not text:
            return set()
            
        found_skills = set()
        # Clean text and tokenize it
        text_lower = " " + re.sub(r'[^\w\+\#\.]', ' ', text.lower()) + " "
        
        # Check every synonym in our map (using word boundary checks to avoid substring match issues)
        for synonym, skill_name in self.synonym_map.items():
            # Escape special characters in synonym for regex (like C++, C#)
            escaped_syn = re.escape(synonym)
            # Custom word boundary to handle C++, C#, .NET
            pattern = r'(?<=\s)' + escaped_syn + r'(?=\s)'
            if re.search(pattern, text_lower):
                found_skills.add(skill_name)
                
        return found_skills

    def get_skill_details(self, skill_name: str) -> Dict[str, Any]:
        """Returns category, parent, and weight for a skill name."""
        return self.skills_dict.get(skill_name, {
            "name": skill_name,
            "category": "Other",
            "parent": None,
            "weight": 1.0,
            "synonyms": []
        })

    def compute_semantic_skill_matches(
        self, 
        resume_text: str, 
        jd_skills: List[str]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Matches JD skills against a resume using semantic embeddings and transferable skill logic.
        Returns a dictionary details:
            jd_skill_name -> {
                "score": float (0.0 to 1.0),
                "match_type": "Exact" | "Semantic" | "Transferable" | "None",
                "matched_with": str (resume skill or phrase),
                "weight": float
            }
        """
        # 1. Extract explicit candidate skills from the resume
        candidate_skills = list(self.extract_skills_by_keywords(resume_text))
        
        # 2. Get embeddings for JD skills
        if not jd_skills:
            return {}
            
        jd_embeddings = get_embeddings(jd_skills)
        candidate_embeddings = get_embeddings(candidate_skills) if candidate_skills else np.array([])
        
        results = {}
        
        for idx, jd_skill in enumerate(jd_skills):
            details = self.get_skill_details(jd_skill)
            weight = details["weight"]
            
            # Case 1: Exact match (found in both via keyword matching)
            if jd_skill in candidate_skills:
                results[jd_skill] = {
                    "score": 1.0,
                    "match_type": "Exact",
                    "matched_with": jd_skill,
                    "weight": weight
                }
                continue
                
            # Case 2: Semantic check against other candidate skills
            best_semantic_score = 0.0
            best_semantic_skill = ""
            
            if len(candidate_skills) > 0:
                jd_vec = jd_embeddings[idx]
                for c_idx, c_skill in enumerate(candidate_skills):
                    c_vec = candidate_embeddings[c_idx]
                    sim = compute_cosine_similarity(jd_vec, c_vec)
                    if sim > best_semantic_score:
                        best_semantic_score = sim
                        best_semantic_skill = c_skill
            
            # Case 3: Transferable skills taxonomy check (same Parent or Category)
            best_transferable_score = 0.0
            best_transferable_skill = ""
            
            jd_meta = self.get_skill_details(jd_skill)
            for c_skill in candidate_skills:
                c_meta = self.get_skill_details(c_skill)
                # If they share the same parent, they are in the same tech family
                if jd_meta["parent"] and c_meta["parent"] and jd_meta["parent"] == c_meta["parent"]:
                    # Give high transferable credit
                    credit = 0.8
                    if credit > best_transferable_score:
                        best_transferable_score = credit
                        best_transferable_skill = f"{c_skill} (Family: {jd_meta['parent']})"
                # If they share the same category (e.g. both are Databases)
                elif jd_meta["category"] == c_meta["category"] and jd_meta["category"] != "Soft Skill":
                    # Give moderate transferable credit
                    credit = 0.6
                    if credit > best_transferable_score:
                        best_transferable_score = credit
                        best_transferable_skill = f"{c_skill} (Category: {jd_meta['category']})"

            # Decide on match type
            if best_semantic_score >= 0.75:
                results[jd_skill] = {
                    "score": round(best_semantic_score, 2),
                    "match_type": "Semantic",
                    "matched_with": best_semantic_skill,
                    "weight": weight
                }
            elif best_transferable_score > 0.0:
                # Merge semantic score with transferable score
                results[jd_skill] = {
                    "score": best_transferable_score,
                    "match_type": "Transferable",
                    "matched_with": best_transferable_skill,
                    "weight": weight
                }
            elif best_semantic_score >= 0.5:
                # Moderate semantic similarity
                results[jd_skill] = {
                    "score": round(best_semantic_score, 2),
                    "match_type": "Semantic",
                    "matched_with": best_semantic_skill,
                    "weight": weight
                }
            else:
                results[jd_skill] = {
                    "score": 0.0,
                    "match_type": "None",
                    "matched_with": "None",
                    "weight": weight
                }
                
        return results
