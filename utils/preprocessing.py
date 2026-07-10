import os
import re
import csv
import nltk
from typing import List, Set

def init_nltk():
    """Download required NLTK data files silently."""
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', quiet=True)
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords', quiet=True)

# Initialize NLTK on import
init_nltk()
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize

def clean_text(text: str) -> str:
    """
    Cleans raw text by removing extra spaces, standardizing punctuation,
    but keeping important technical characters like +, #, . (e.g. C++, C#, .NET).
    """
    if not text:
        return ""
    # Replace newlines and tabs with spaces
    text = text.replace('\n', ' ').replace('\t', ' ')
    # Normalize unicode spaces
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def get_sentences(text: str) -> List[str]:
    """Splits text into sentences."""
    cleaned = clean_text(text)
    return sent_tokenize(cleaned)

def extract_tokens(text: str, remove_stop: bool = True) -> List[str]:
    """Tokenizes text and optionally removes English stopwords."""
    cleaned = clean_text(text).lower()
    tokens = word_tokenize(cleaned)
    if remove_stop:
        stop_words = set(stopwords.words('english'))
        tokens = [t for t in tokens if t not in stop_words and t.isalnum() or '+' in t or '#' in t or '.' in t]
    return tokens

def ensure_skills_db():
    """Generates a default skills_database.csv if it does not exist."""
    db_dir = os.path.join("data")
    os.makedirs(db_dir, exist_ok=True)
    db_path = os.path.join(db_dir, "skills_database.csv")
    
    if os.path.exists(db_path):
        return db_path

    # Define standard skills across categories with synonyms and parent mappings
    skills = [
        # Programming Languages
        ("Python", "Programming Language", "python,py,python3,cpython", "Programming Languages", 1.2),
        ("Java", "Programming Language", "java,jdk,jre", "Programming Languages", 1.0),
        ("C++", "Programming Language", "c++,cpp,c plus plus", "Programming Languages", 1.1),
        ("C#", "Programming Language", "c#,csharp,c sharp", "Programming Languages", 1.0),
        ("JavaScript", "Programming Language", "javascript,js,es6,ecmascript", "Programming Languages", 1.1),
        ("TypeScript", "Programming Language", "typescript,ts", "Programming Languages", 1.1),
        ("Go", "Programming Language", "go,golang", "Programming Languages", 1.1),
        ("Rust", "Programming Language", "rust,rustlang", "Programming Languages", 1.1),
        ("SQL", "Programming Language", "sql,mysql,sqlite,postgresql,plsql", "Programming Languages", 1.0),
        ("HTML", "Programming Language", "html,html5", "Programming Languages", 0.8),
        ("CSS", "Programming Language", "css,css3,scss,sass", "Programming Languages", 0.8),
        ("R", "Programming Language", "r programming,r-lang", "Programming Languages", 1.0),
        ("PHP", "Programming Language", "php,php8", "Programming Languages", 0.8),
        ("Ruby", "Programming Language", "ruby,jruby", "Programming Languages", 0.8),
        ("Swift", "Programming Language", "swift,swiftui", "Programming Languages", 1.0),
        ("Kotlin", "Programming Language", "kotlin,kotlinc", "Programming Languages", 1.0),
        
        # Frameworks
        ("Django", "Framework", "django,drf,django rest framework", "Python", 1.1),
        ("Flask", "Framework", "flask,flask-restful", "Python", 1.0),
        ("FastAPI", "Framework", "fastapi", "Python", 1.1),
        ("React", "Framework", "react,reactjs,react.js", "JavaScript", 1.2),
        ("Angular", "Framework", "angular,angularjs,angular.js", "JavaScript", 1.0),
        ("Vue.js", "Framework", "vue,vuejs,vue.js", "JavaScript", 1.0),
        ("Next.js", "Framework", "nextjs,next.js", "React", 1.2),
        ("Spring Boot", "Framework", "spring boot,springboot,spring", "Java", 1.1),
        ("Express.js", "Framework", "express,expressjs,express.js", "JavaScript", 1.0),
        ("TensorFlow", "Framework", "tensorflow,tf,tf2", "AI/ML", 1.2),
        ("PyTorch", "Framework", "pytorch,torch", "AI/ML", 1.2),
        ("Scikit-Learn", "Framework", "scikit-learn,sklearn", "AI/ML", 1.1),
        ("Pandas", "Framework", "pandas", "Python", 1.0),
        ("NumPy", "Framework", "numpy", "Python", 0.9),
        
        # Cloud
        ("AWS", "Cloud", "aws,amazon web services,ec2,s3,rds,lambda,iam", "Cloud", 1.2),
        ("Azure", "Cloud", "azure,microsoft azure,active directory", "Cloud", 1.1),
        ("Google Cloud Platform", "Cloud", "gcp,google cloud,google cloud platform,bigquery,gcs", "Cloud", 1.1),
        ("Kubernetes", "Cloud", "kubernetes,k8s,eks,gke,aks", "DevOps", 1.2),
        ("Docker", "Cloud", "docker,dockerfile,docker-compose", "DevOps", 1.1),
        
        # Databases
        ("PostgreSQL", "Database", "postgresql,postgres", "SQL", 1.0),
        ("MongoDB", "Database", "mongodb,mongo,nosql", "Database", 1.0),
        ("MySQL", "Database", "mysql,my-sql", "SQL", 0.9),
        ("Redis", "Database", "redis,caching", "Database", 1.0),
        ("DynamoDB", "Database", "dynamodb,amazon dynamodb", "AWS", 1.1),
        ("Oracle Database", "Database", "oracle,pl-sql", "SQL", 0.9),
        ("Cassandra", "Database", "cassandra,apache cassandra", "Database", 1.0),
        
        # DevOps & Tools
        ("Git", "DevOps", "git,github,gitlab,version control", "Tools", 0.9),
        ("Jenkins", "DevOps", "jenkins,ci/cd,cicd", "DevOps", 1.0),
        ("GitHub Actions", "DevOps", "github actions,github workflows", "DevOps", 1.0),
        ("Terraform", "DevOps", "terraform,iac,infrastructure as code", "DevOps", 1.2),
        ("Ansible", "DevOps", "ansible,configuration management", "DevOps", 1.0),
        ("Linux", "DevOps", "linux,bash,shell scripting,ubuntu,centos", "Tools", 0.9),
        ("Jira", "DevOps", "jira,confluence,agile,scrum", "Tools", 0.8),
        
        # AI / ML
        ("Machine Learning", "AI/ML", "machine learning,ml,predictive modeling", "AI/ML", 1.2),
        ("Deep Learning", "AI/ML", "deep learning,dl,neural networks", "AI/ML", 1.2),
        ("Natural Language Processing", "AI/ML", "natural language processing,nlp,text mining,spacy,nltk", "AI/ML", 1.2),
        ("Computer Vision", "AI/ML", "computer vision,cv,opencv", "AI/ML", 1.2),
        ("Large Language Models", "AI/ML", "llm,large language models,gpt,llama,transformers,huggingface", "AI/ML", 1.3),
        ("Generative AI", "AI/ML", "generative ai,genai,prompt engineering", "AI/ML", 1.2),
        ("Data Science", "AI/ML", "data science,data analysis,visualization", "AI/ML", 1.1),
        ("MLOps", "AI/ML", "mlops,mlflow,kubeflow,model deployment", "AI/ML", 1.2),
        
        # Certifications
        ("AWS Certified Solutions Architect", "Certification", "aws solutions architect,aws certified,aws csa", "AWS", 1.1),
        ("Certified Kubernetes Administrator", "Certification", "cka,kubernetes administrator", "Kubernetes", 1.2),
        ("Project Management Professional", "Certification", "pmp,pmp certification", "Tools", 1.1),
        ("Scrum Master", "Certification", "csm,certified scrum master", "Tools", 1.0),
        
        # Soft Skills
        ("Communication", "Soft Skill", "communication,presentation,written,verbal", "Soft Skills", 0.9),
        ("Leadership", "Soft Skill", "leadership,team management,mentoring,mentorship", "Soft Skills", 1.0),
        ("Problem Solving", "Soft Skill", "problem solving,analytical thinking,critical thinking", "Soft Skills", 0.9),
        ("Collaboration", "Soft Skill", "collaboration,teamwork,cross-functional", "Soft Skills", 0.9),
        ("Agile", "Soft Skill", "agile,scrum,kanban", "Soft Skills", 0.9),
        ("Project Management", "Soft Skill", "project management,planning,delivery,milestones", "Soft Skills", 1.0),
    ]

    with open(db_path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["SkillName", "Category", "Synonyms", "ParentSkill", "WeightMultiplier"])
        for s in skills:
            writer.writerow(s)

    return db_path
