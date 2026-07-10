import re
from typing import Dict, List, Any
from models.embedding import get_single_embedding, compute_cosine_similarity

# Standard list of high-impact action verbs
ACTION_VERBS = {
    "spearheaded", "managed", "designed", "architected", "optimized", "implemented",
    "developed", "built", "delivered", "executed", "led", "created", "formulated",
    "improved", "streamlined", "engineered", "facilitated", "directed", "supervised",
    "mentored", "collaborated", "increased", "decreased", "saved", "maximized",
    "analyzed", "coordinated", "initiated", "pioneered", "overhauled", "restructured"
}

DEGREE_HIERARCHY = {
    "High School": 1,
    "Associate's": 2,
    "Bachelor's": 3,
    "Master's": 4,
    "PhD": 5
}

def parse_experience_years(experience_text: str) -> float:
    """
    Attempts to estimate total years of experience from resume work history text.
    Extracts date ranges (e.g., '2018 - 2021', 'Oct 2020 - Present', '2019 to 2023')
    and calculates cumulative duration.
    """
    if not experience_text:
        return 0.0
        
    total_months = 0
    current_year = 2026 # Default current year based on context metadata
    
    # Pattern to match Year - Year or Month Year - Month Year
    # e.g., "2018 - 2021", "2019 to Present", "May 2020 - Dec 2022"
    months_map = {
        "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
        "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
        "january": 1, "february": 2, "march": 3, "april": 4, "june": 6,
        "july": 7, "august": 8, "september": 9, "october": 10,
        "november": 11, "december": 12
    }

    # Extract all lines containing potential dates
    lines = experience_text.split('\n')
    
    for line in lines:
        # Match "Month Year - Month Year" or "Year - Year"
        # Let's search for standard date patterns
        date_range_regex = r'\b(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?|\d{4})?\s*(\d{4})?\s*[-–to]+\s*(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?|present|current|\d{4})?\s*(\d{4})?\b'
        
        matches = re.findall(date_range_regex, line, re.IGNORECASE)
        for match in matches:
            # Clean tuple parts
            start_m_str, start_y_str, end_m_str, end_y_str = match
            
            # Helper to parse year
            try:
                start_year = int(start_y_str) if start_y_str else (int(start_m_str) if (start_m_str and start_m_str.isdigit()) else None)
                if not start_year:
                    continue
                
                # Check end date
                if end_m_str.lower() in ["present", "current"] or end_y_str.lower() in ["present", "current"]:
                    end_year = current_year
                    end_month = 7  # Current month from local time (July 2026)
                elif end_y_str and end_y_str.isdigit():
                    end_year = int(end_y_str)
                    end_month = months_map.get(end_m_str.lower(), 1) if end_m_str else 1
                elif end_m_str and end_m_str.isdigit():
                    end_year = int(end_m_str)
                    end_month = 12
                else:
                    end_year = start_year + 1  # Default to 1 year if unclear
                    end_month = 1
                    
                start_month = months_map.get(start_m_str.lower(), 1) if (start_m_str and not start_m_str.isdigit()) else 1
                
                # Calculate months
                months = (end_year - start_year) * 12 + (end_month - start_month)
                if 0 < months < 120:  # Avoid unrealistic date parses (e.g. 10+ years on a single job range if parsing error)
                    total_months += months
            except Exception:
                continue

    years = round(total_months / 12, 1)
    
    # Fallback to scanning single number mentions of experience in experience block
    if years == 0.0:
        number_matches = re.findall(r'(\d+)\+?\s*years?', experience_text, re.IGNORECASE)
        if number_matches:
            years = float(max([int(n) for n in number_matches]))
            
    # Cap experience at 30 years to avoid outlier parsing errors
    return min(years, 30.0)

def score_experience(candidate_text: str, required_years: int, jd_text: str) -> Dict[str, Any]:
    """Scores experience based on years matching and semantic role relevance."""
    candidate_years = parse_experience_years(candidate_text)
    
    # Calculate years matching score
    if required_years == 0:
        years_score = 100.0
    else:
        years_score = min(100.0, (candidate_years / required_years) * 100.0)
        
    # Calculate semantic match between experience block and JD
    exp_emb = get_single_embedding(candidate_text)
    jd_emb = get_single_embedding(jd_text)
    semantic_sim = compute_cosine_similarity(exp_emb, jd_emb)
    
    # Scale semantic similarity to 0-100 (where 0.3 similarity represents basic match)
    semantic_score = min(100.0, max(0.0, (semantic_sim - 0.2) / 0.6 * 100.0))
    
    # Final Experience score is a blend: 60% years of experience, 40% semantic job description match
    final_score = 0.6 * years_score + 0.4 * semantic_score
    
    deductions = []
    additions = []
    
    if candidate_years < required_years:
        deductions.append(f"Years of Experience ({candidate_years} yrs) is less than required ({required_years} yrs)")
    else:
        additions.append(f"Exceeds/meets required experience: {candidate_years} years parsed (required: {required_years})")
        
    if semantic_sim < 0.45:
        deductions.append("Work experience description is semantically weak or misaligned with JD requirements")
    else:
        additions.append("Strong semantic alignment between candidate work history and job role")
        
    return {
        "score": round(final_score, 1),
        "years_parsed": candidate_years,
        "semantic_sim": round(semantic_sim, 2),
        "deductions": deductions,
        "additions": additions
    }

def score_education(education_text: str, required_degree: str) -> Dict[str, Any]:
    """Scores education match using degree hierarchy and semantic field mapping."""
    # Find candidate's highest degree in text
    candidate_level = 0
    candidate_degree = "Not Found"
    
    degree_patterns = {
        "PhD": [r'\bph\.?d\b', r'\bdoctorate\b', r'\bdoctor\b'],
        "Master's": [r'\bmaster\'s\b', r'\bmasters\b', r'\bm\.s\b', r'\bm\.a\b', r'\bmba\b', r'\bms\b\s', r'\bm\.tech\b'],
        "Bachelor's": [r'\bbachelor\'s\b', r'\bbachelors\b', r'\bb\.s\b', r'\bb\.a\b', r'\bbs\b\s', r'\bb\.tech\b', r'\bbe\b\s', r'\bb\.e\b'],
        "Associate's": [r'\bassociate\'s\b', r'\bassociates\b', r'\ba\.s\b'],
        "High School": [r'\bhigh\s+school\b', r'\bdiploma\b']
    }
    
    for degree, patterns in degree_patterns.items():
        for pat in patterns:
            if re.search(pat, education_text, re.IGNORECASE):
                level = DEGREE_HIERARCHY[degree]
                if level > candidate_level:
                    candidate_level = level
                    candidate_degree = degree
                    
    req_level = DEGREE_HIERARCHY.get(required_degree, 3) # default to Bachelor's
    
    deductions = []
    additions = []
    
    if candidate_level == 0:
        score = 40.0
        deductions.append("No formal degree found in the Education section")
    elif candidate_level >= req_level:
        score = 100.0
        additions.append(f"Degree matches/exceeds requirement: Candidate has {candidate_degree} (required: {required_degree})")
    elif req_level - candidate_level == 1:
        score = 80.0
        deductions.append(f"Candidate has {candidate_degree}, but the JD requires a {required_degree}")
    else:
        score = 60.0
        deductions.append(f"Candidate has {candidate_degree}, which is significantly below the required {required_degree}")
        
    return {
        "score": score,
        "degree_parsed": candidate_degree,
        "deductions": deductions,
        "additions": additions
    }

def score_action_verbs(text: str) -> Dict[str, Any]:
    """Calculates action verb intensity and density score."""
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    total_words = len(words)
    
    if total_words == 0:
        return {"score": 0.0, "count": 0, "verbs_found": [], "deductions": ["No text to scan for action verbs"]}
        
    found_verbs = [w for w in words if w in ACTION_VERBS]
    unique_found = set(found_verbs)
    count = len(found_verbs)
    
    # Grade based on count of unique action verbs
    if len(unique_found) >= 10:
        score = 100.0
    elif len(unique_found) >= 7:
        score = 85.0
    elif len(unique_found) >= 4:
        score = 70.0
    elif len(unique_found) >= 2:
        score = 50.0
    else:
        score = 25.0
        
    additions = []
    deductions = []
    
    if score >= 85.0:
        additions.append(f"Strong use of active verbs: found {len(unique_found)} unique active verbs ({', '.join(list(unique_found)[:6])})")
    else:
        deductions.append(f"Weak action verbs. Only found {len(unique_found)} active verbs. Recommend adding more impact-driven words.")
        
    return {
        "score": score,
        "count": count,
        "unique_count": len(unique_found),
        "verbs_found": list(unique_found),
        "additions": additions,
        "deductions": deductions
    }

def check_formatting(text: str) -> Dict[str, Any]:
    """Performs formatting audits on text length and structure."""
    words = text.split()
    word_count = len(words)
    
    score = 100.0
    deductions = []
    additions = []
    
    # Word count limits
    if word_count < 150:
        score -= 30
        deductions.append(f"Resume is very short ({word_count} words). ATS parsers may find it lacking detail.")
    elif word_count < 300:
        score -= 10
        deductions.append(f"Resume is slightly short ({word_count} words). Try expanding on projects and bullet points.")
    elif word_count > 2500:
        score -= 20
        deductions.append(f"Resume is extremely long ({word_count} words). Aim for a maximum of 2-3 structured pages.")
    else:
        additions.append(f"Ideal word count: {word_count} words parsed.")
        
    # Check for excessive special symbols that suggest bad pdf parsing or formatting issues
    garbled_chars = len(re.findall(r'[^\w\s\.\,\-\@\#\+\:\(\)\/]', text))
    if word_count > 0 and (garbled_chars / word_count) > 0.05:
        score -= 15
        deductions.append("High density of non-standard characters detected. Suggests formatting or PDF rendering issues.")
        
    return {
        "score": max(0.0, score),
        "word_count": word_count,
        "deductions": deductions,
        "additions": additions
    }

def check_completeness(sections: Dict[str, str], contact_info: Dict[str, str]) -> Dict[str, Any]:
    """Evaluates whether all vital sections and contact info are present."""
    vital_sections = ["skills", "experience", "education"]
    score = 100.0
    deductions = []
    additions = []
    
    # Check vital sections
    for sec in vital_sections:
        if not sections.get(sec) or len(sections[sec].strip()) < 10:
            score -= 25
            deductions.append(f"Missing critical section: {sec.capitalize()}")
        else:
            additions.append(f"Verified presence of section: {sec.capitalize()}")
            
    # Check optional but highly recommended sections
    optional_sections = ["projects", "summary", "certifications"]
    for sec in optional_sections:
        if not sections.get(sec) or len(sections[sec].strip()) < 10:
            score -= 10
            deductions.append(f"Missing section: {sec.capitalize()}")
        else:
            additions.append(f"Verified presence of section: {sec.capitalize()}")
            
    # Check contact info
    if contact_info.get("email") == "Not Found":
        score -= 10
        deductions.append("Missing contact detail: Email Address")
    else:
        additions.append("Email address verified.")
        
    if contact_info.get("phone") == "Not Found":
        score -= 5
        deductions.append("Missing contact detail: Phone Number")
    else:
        additions.append("Phone number verified.")
        
    return {
        "score": max(0.0, score),
        "deductions": deductions,
        "additions": additions
    }
