# Explainable Resume ATS Optimizer

An advanced, research-grade, production-ready Streamlit web application that leverages Semantic AI and Natural Language Processing to analyze a candidate's resume against a Job Description. Rather than utilizing basic keyword frequency matches (which can be easily gamed or penalize synonyms), it introduces a novel framework called **Semantic ATS Compatibility Score (SACS)**.

SACS is fully transparent and explainable. It outlines exactly why points were added or deducted using marginal perturbation analytics (similar to SHAP) and suggests learning paths for missing skills and active bullet point rewrites.

---

## 🔬 Mathematical Formulation of SACS

The Semantic ATS Compatibility Score (SACS) evaluates the candidate's alignment across nine structural categories:

$$SACS = w_{skill} \cdot S_{skill} + w_{exp} \cdot S_{exp} + w_{proj} \cdot S_{proj} + w_{edu} \cdot S_{edu} + w_{cert} \cdot S_{cert} + w_{verb} \cdot S_{verb} + w_{soft} \cdot S_{soft} + w_{format} \cdot S_{format} + w_{comp} \cdot S_{comp}$$

Where:
1. **$S_{skill}$ (Technical Skill Score)**: Cosine similarity matrix between resume technical skills and job requirements using local sentence embedding vectors (`all-MiniLM-L6-v2`).
2. **$S_{exp}$ (Experience Match)**: Blend of duration compatibility (candidate years vs required years) and semantic job role description match.
3. **$S_{proj}$ (Project Relevance)**: Semantic cosine similarity between the project text and JD responsibilities.
4. **$S_{edu}$ (Education Level Match)**: Degree level matching using an ordinal ranking hierarchy (High School = 1, Associate's = 2, Bachelor's = 3, Master's = 4, PhD = 5).
5. **$S_{cert}$ (Certifications Grade)**: Evaluation of relevant professional credentials aligned with JD requirements.
6. **$S_{verb}$ (Action Verbs Density)**: Evaluates the density of active impact-driven verbs (e.g. *designed*, *spearheaded*, *optimized*).
7. **$S_{soft}$ (Soft Skills Match)**: Evaluates semantic alignment with desired soft skills (e.g. *collaboration*, *communication*).
8. **$S_{format}$ (Formatting Check)**: Penalties for garbled text conversion, excessive special symbols, or inappropriate word count profiles.
9. **$S_{comp}$ (Completeness Score)**: Presence verification for all primary sections and contact information.

All weights ($w_i$) are adjustable by the user in the sidebar and are dynamically normalized to sum to $1.0$ (or $100\%$).

---

## 📁 Directory Structure

```
ResumeATS/
├── .streamlit/
│   └── config.toml               # Streamlit configuration and theme controls
├── app.py                        # Main router and dashboard coordinator
├── requirements.txt              # Project dependencies
├── README.md                     # Research and setup documentation
├── assets/
│   └── custom.css                # Visual style templates (glassmorphism cards, badges)
├── data/
│   └── skills_database.csv       # Skill classification and hierarchy taxonomy database (auto-generated)
├── models/
│   ├── embedding.py              # Sentence Transformer caching and embedding generation
│   ├── ats_score.py              # SACS scoring calculation
│   ├── explainability.py         # SHAP-like perturbation importance calculator
│   ├── parser.py                 # File parsers (PDF/DOCX/TXT) and text segmenter
│   └── recommendation.py         # Action verb templates and study resources
├── utils/
│   ├── preprocessing.py          # NLTK text cleanups and database generators
│   ├── similarity.py             # Cosine similarity and transferable skills mapping
│   ├── visualization.py          # Plotly gauge, radar, and skill network charts
│   └── scoring.py                # Formatting and completeness grading rules
└── pages/
    ├── Home.py                   # Landing page with architectural details
    ├── Resume_Analysis.py        # File upload workspace and analyzer trigger
    ├── Job_Description.py        # Extracted parameters inspector and JD editor
    ├── Skill_Gap.py              # Skill badges, Heatmap and interactive Network plots
    ├── Explainability.py         # Component importance and additions/deductions ledger
    ├── Resume_Rewriter.py        # STAR-format bullet improver and DOCX exporter
    └── Analytics.py              # Polar radar and predictive recruiter analytics
```

---

## 🚀 Installation & Local Execution

### 1. Prerequisites
Ensure you have **Python 3.10+** installed.

### 2. Clone and Setup
Navigate to the root directory and install dependencies:
```bash
pip install -r requirements.txt
```
*Note: On first startup, the app will automatically download the required spaCy model (`en_core_web_sm`), NLTK packages, and sentence transformer model (`all-MiniLM-L6-v2`), making setup zero-config.*

### 3. Run the App
Launch the server using Streamlit:
```bash
streamlit run app.py
```

---

## ☁️ Streamlit Community Cloud Deployment

To host this application for free on Streamlit Community Cloud:

1. Push this project folder to a public GitHub repository.
2. Visit [share.streamlit.io](https://share.streamlit.io/) and log in with your GitHub account.
3. Click **New app**, select your repository, branch, and set `app.py` as the **Main file path**.
4. Click **Deploy**. Streamlit will automatically read `requirements.txt`, spin up a host, and run the app.
