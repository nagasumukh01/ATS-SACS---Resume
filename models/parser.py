import os
import re
import fitz  # PyMuPDF
import pdfplumber
from docx import Document
import spacy
from typing import Dict, List, Any

# Programmatically load spaCy model
def get_spacy_nlp():
    """Load the small English spaCy model directly as a python module."""
    try:
        import en_core_web_sm
        return en_core_web_sm.load()
    except ImportError:
        return spacy.load("en_core_web_sm")

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extracts all text from a PDF file using PyMuPDF (fitz) or pdfplumber."""
    text = ""
    try:
        # Try PyMuPDF first
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text()
        doc.close()
    except Exception:
        # Fallback to pdfplumber
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            text = f"Error reading PDF: {str(e)}"
    return text

def extract_text_from_docx(docx_path: str) -> str:
    """Extracts text from a DOCX document."""
    try:
        doc = Document(docx_path)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        return '\n'.join(full_text)
    except Exception as e:
        return f"Error reading DOCX: {str(e)}"

def extract_text(file_path: str) -> str:
    """Detects file type and extracts raw text."""
    _, ext = os.path.splitext(file_path.lower())
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext == ".docx":
        return extract_text_from_docx(file_path)
    elif ext == ".txt":
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception as e:
            return f"Error reading TXT: {str(e)}"
    else:
        return "Unsupported file type."

def extract_contact_info(text: str) -> Dict[str, str]:
    """Extracts Name, Email, and Phone number using Regex and spaCy NER."""
    info = {"name": "Not Found", "email": "Not Found", "phone": "Not Found"}
    
    # Email regex
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    if email_match:
        info["email"] = email_match.group(0)
        
    # Phone regex (matches international, domestic, spaces, dashes, parentheses)
    phone_match = re.search(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
    if phone_match:
        info["phone"] = phone_match.group(0)

    # Name extraction using spaCy (usually in the first 3 lines of a resume)
    nlp = get_spacy_nlp()
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    first_few_lines = "\n".join(lines[:4]) if len(lines) >= 4 else "\n".join(lines)
    
    doc = nlp(first_few_lines)
    for ent in doc.ents:
        if ent.label_ == "PERSON" and len(ent.text.split()) >= 2:
            # First person name of at least 2 words
            info["name"] = ent.text
            break
            
    # Fallback name extraction if NER fails
    if info["name"] == "Not Found" and lines:
        for line in lines[:3]:
            # Guessing name is the first line that is short and has no digits/symbols
            if 3 < len(line) < 30 and not any(c.isdigit() for c in line) and '@' not in line:
                info["name"] = line
                break
                
    return info

def segment_resume(text: str) -> Dict[str, str]:
    """
    Segments a resume into key sections (Summary, Skills, Experience, Projects, Education, Certifications).
    """
    sections = {
        "summary": "",
        "skills": "",
        "experience": "",
        "projects": "",
        "education": "",
        "certifications": ""
    }
    
    # Normalizing section header match regexes
    headers = {
        "summary": re.compile(r'\b(?:summary|profile|about\s+me|professional\s+summary|objective)\b', re.IGNORECASE),
        "skills": re.compile(r'\b(?:skills|technical\s+skills|expertise|technologies|tools|languages)\b', re.IGNORECASE),
        "experience": re.compile(r'\b(?:experience|work\s+experience|employment|work\s+history|professional\s+experience)\b', re.IGNORECASE),
        "projects": re.compile(r'\b(?:projects|academic\s+projects|personal\s+projects|key\s+projects)\b', re.IGNORECASE),
        "education": re.compile(r'\b(?:education|academic\s+background|qualifications|credentials)\b', re.IGNORECASE),
        "certifications": re.compile(r'\b(?:certifications|certificates|licenses|courses)\b', re.IGNORECASE)
    }

    lines = text.split('\n')
    current_section = None
    section_content = {k: [] for k in sections.keys()}

    for line in lines:
        clean_line = line.strip()
        if not clean_line:
            continue
        
        # Check if line is a header (usually short, <= 4 words)
        is_header = False
        if len(clean_line.split()) <= 4:
            for sec_key, header_rx in headers.items():
                if header_rx.search(clean_line):
                    current_section = sec_key
                    is_header = True
                    break
        
        if is_header:
            continue
            
        if current_section:
            section_content[current_section].append(line)
        else:
            # If no section is identified yet, default to summary
            section_content["summary"].append(line)

    for k in sections.keys():
        sections[k] = "\n".join(section_content[k]).strip()
        
    return sections

def parse_job_description(jd_text: str) -> Dict[str, Any]:
    """
    Parses a Job Description and extracts experience, education keywords, and roles.
    """
    parsed_jd = {
        "raw_text": jd_text,
        "experience_years": 0,
        "education_required": "Bachelor's",
        "key_sections": {
            "responsibilities": "",
            "requirements": "",
            "nice_to_have": ""
        }
    }
    
    # Extract years of experience requirement
    exp_matches = re.findall(r'(\d+)\+?\s*(?:years|yrs)?\s*(?:of)?\s*experience', jd_text, re.IGNORECASE)
    if exp_matches:
        parsed_jd["experience_years"] = max([int(m) for m in exp_matches])
    else:
        # Check for textual numbers
        num_word_map = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}
        for word, val in num_word_map.items():
            if re.search(r'\b' + word + r'\b\s*years?\s*experience', jd_text, re.IGNORECASE):
                parsed_jd["experience_years"] = val
                break

    # Extract minimum education level
    if re.search(r'\b(?:phd|ph\.d|doctorate)\b', jd_text, re.IGNORECASE):
        parsed_jd["education_required"] = "PhD"
    elif re.search(r'\b(?:master\'s|masters|ms|ma|mba|post-graduate)\b', jd_text, re.IGNORECASE):
        parsed_jd["education_required"] = "Master's"
    elif re.search(r'\b(?:bachelor|bachelors|bs|ba|b\.tech|b\.e|undergraduate)\b', jd_text, re.IGNORECASE):
        parsed_jd["education_required"] = "Bachelor's"
        
    # Segment JD into responsibilities vs requirements
    lines = jd_text.split('\n')
    current = "requirements"
    resp_lines = []
    req_lines = []
    
    for line in lines:
        clean = line.strip()
        if not clean:
            continue
        if len(clean.split()) <= 4:
            if re.search(r'\b(?:responsibilities|duties|what\s+you\s+will\s+do|role|about\s+the\s+job)\b', clean, re.IGNORECASE):
                current = "responsibilities"
                continue
            elif re.search(r'\b(?:requirements|qualifications|skills|what\s+you\s+need|experience)\b', clean, re.IGNORECASE):
                current = "requirements"
                continue
        
        if current == "responsibilities":
            resp_lines.append(line)
        else:
            req_lines.append(line)
            
    parsed_jd["key_sections"]["responsibilities"] = "\n".join(resp_lines)
    parsed_jd["key_sections"]["requirements"] = "\n".join(req_lines)
    
    return parsed_jd
