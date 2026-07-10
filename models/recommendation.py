import re
from typing import Dict, List, Any

# Map missing skills to topics and free learning resource names
LEARNING_PATHS = {
    "python": {
        "topics": ["Syntax & Data Structures", "OOP principles", "Decorators & Generators", "Web Frameworks (Django/FastAPI)"],
        "resources": ["Official Python Tutorial (docs.python.org)", "Python for Everybody (Coursera)", "freeCodeCamp Python Guide"]
    },
    "docker": {
        "topics": ["Containerization concepts", "Writing Dockerfiles", "Docker Compose multi-container setups", "Image size optimization"],
        "resources": ["Docker Getting Started Guide (docs.docker.com)", "Docker for Beginners (freeCodeCamp)", "KodeKloud Docker Course"]
    },
    "kubernetes": {
        "topics": ["Pods, Deployments, and Services", "ConfigMaps & Secrets", "Ingress controllers", "Helm package manager"],
        "resources": ["Kubernetes Basics (kubernetes.io)", "CKA Prep Course (KodeKloud)", "Kubernetes Tutorial (TechWorld with Nana)"]
    },
    "react": {
        "topics": ["Functional components & hooks", "State management (Redux/Context API)", "Routing and API integration", "Next.js framework"],
        "resources": ["React Docs (react.dev)", "Full Stack Open (University of Helsinki)", "React Course (freeCodeCamp)"]
    },
    "aws": {
        "topics": ["Core services (EC2, S3, RDS, Lambda)", "IAM security principles", "VPC & Networking basics", "AWS CloudFormation/Terraform"],
        "resources": ["AWS Skill Builder (skillbuilder.aws)", "AWS Solutions Architect course (Adrian Cantrill)", "AWS Certified Cloud Practitioner (freeCodeCamp)"]
    },
    "machine learning": {
        "topics": ["Supervised vs Unsupervised learning", "Model evaluation (Precision, Recall, ROC-AUC)", "Feature engineering", "Scikit-Learn framework"],
        "resources": ["Machine Learning Specialization (Andrew Ng on Coursera)", "Introduction to Machine Learning (Kaggle)", "Hands-On Machine Learning (Book)"]
    },
    "large language models": {
        "topics": ["Transformer architectures", "Fine-tuning models (PEFT/LoRA)", "Prompt engineering & RAG", "LangChain & LlamaIndex frameworks"],
        "resources": ["Hugging Face NLP Course (huggingface.co/learn)", "DeepLearning.AI Short Courses", "Generative AI for Beginners (Microsoft)"]
    },
    "git": {
        "topics": ["Branching & merging strategies", "Rebasing vs merging", "Resolving merge conflicts", "Git Workflows (GitLab/GitHub flow)"],
        "resources": ["Git Book (git-scm.com/book)", "Git & GitHub Crash Course (freeCodeCamp)", "Missing Semester of your CS Education (MIT)"]
    }
}

DEFAULT_LEARNING_PATH = {
    "topics": ["Core principles and theory", "Hands-on projects", "Best practices and architecture", "Debugging and performance tuning"],
    "resources": ["Official Documentation & Quickstarts", "freeCodeCamp YouTube tutorials", "Medium & Dev.to tech blogs"]
}

WEAK_PHRASES = {
    r'\b(?:responsible for|duties included|worked on|helped with|assisted in)\b': "Designed, spearheaded, or executed",
    r'\b(?:did|made|wrote)\b': "Architected, engineered, or developed",
    r'\b(?:managed|led)\b': "Spearheaded, directed, or coordinated",
    r'\b(?:fixed|changed)\b': "Optimized, resolved, or restructured"
}

def get_learning_path(missing_skill: str) -> Dict[str, List[str]]:
    """Retrieves a learning path and resource list for a missing skill."""
    skill_lower = missing_skill.lower()
    
    # Try finding exact match or substring match
    for k, path in LEARNING_PATHS.items():
        if k in skill_lower or skill_lower in k:
            return path
            
    return DEFAULT_LEARNING_PATH

def suggest_bullet_rewrites(bullet: str) -> List[str]:
    """
    Takes a weak resume bullet point and suggests 3 professional alternatives using
    strong action verbs and metrics-focused frameworks (STAR).
    """
    cleaned = bullet.strip().strip("-*• ")
    if not cleaned:
        return []
        
    # Analyze weak phrase usage
    weak_found = False
    for pat in WEAK_PHRASES.keys():
        if re.search(pat, cleaned, re.IGNORECASE):
            weak_found = True
            break

    # 3 template suggestion styles
    suggestions = [
        # Option 1: Spearheaded/Architected style (Technical Leadership)
        f"Spearheaded the development and optimization of {cleaned.lower()}, improving system throughput/efficiency by [X]% and reducing latency.",
        
        # Option 2: Engineered/Designed style (Core Engineering)
        f"Engineered and deployed a scalable solution for {cleaned.lower()}, resulting in a [Y]% reduction in manual effort and enhanced reliability.",
        
        # Option 3: Standard STAR formatting (Business Impact)
        f"Designed and implemented high-performance workflows to handle {cleaned.lower()}, delivering a [Z]% improvement in team delivery velocity and codebase maintainability."
    ]
    
    return suggestions

def generate_optimized_summary(resume_summary: str, jd_text: str, matched_skills: List[str]) -> str:
    """Generates an optimized professional summary matching the candidate's skills to the JD."""
    # Find some title matching if possible
    title_matches = re.search(r'\b(?:software engineer|data scientist|cloud architect|devops engineer|fullstack developer|product manager|analyst)\b', jd_text, re.IGNORECASE)
    title = title_matches.group(0).title() if title_matches else "Software Engineer / Technical Specialist"
    
    skills_joined = ", ".join(matched_skills[:4]) if matched_skills else "advanced software technologies"
    
    summary = (
        f"Result-oriented {title} with a proven track record of design, implementation, and optimization. "
        f"Leverages strong technical proficiency in {skills_joined} to build scalable, reliable systems. "
        f"Adept at collaborating with cross-functional teams to translate complex requirements into clean, performant code while maintaining architectural standards."
    )
    return summary
