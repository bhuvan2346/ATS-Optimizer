import streamlit as st
import pdfplumber
import docx
import spacy

# Load English language model
nlp = spacy.load("en_core_web_sm")

# --- Core Functions ---
def extract_text(file):
    """Extract text from PDF or Word files"""
    if file.name.endswith('.pdf'):
        with pdfplumber.open(file) as pdf:
            return " ".join(page.extract_text() for page in pdf.pages)
    else:
        doc = docx.Document(file)
        return " ".join(para.text for para in doc.paragraphs)

def analyze(resume_text, job_desc):
    """Calculate ATS score and identify issues"""
    # Process texts
    resume_doc = nlp(resume_text.lower())
    job_doc = nlp(job_desc.lower())
    
    # Extract meaningful keywords (nouns/verbs only)
    resume_kw = {token.lemma_ for token in resume_doc 
                if token.pos_ in ('NOUN', 'VERB') and not token.is_stop}
    job_kw = {token.lemma_ for token in job_doc 
             if token.pos_ in ('NOUN', 'VERB') and not token.is_stop}
    
    # Calculate score
    match_score = len(resume_kw & job_kw) / len(job_kw) * 100
    
    # Find weak action verbs
    weak_verbs = {"did", "made", "worked"}
    weak_phrases = [token.text for token in resume_doc if token.text in weak_verbs]
    
    return {
        "score": round(match_score, 1),
        "missing_kw": job_kw - resume_kw,
        "weak_phrases": weak_phrases
    }

# --- Streamlit UI ---
st.set_page_config(layout="wide")
st.title("🚀 ATS Resume Optimizer")

# File upload and job description input
col1, col2 = st.columns(2)
with col1:
    resume_file = st.file_uploader("Upload Resume (PDF/DOCX)", type=["pdf", "docx"])
with col2:
    job_desc = st.text_area("Paste Job Description", height=200)

# Analysis and results
if resume_file and job_desc:
    results = analyze(extract_text(resume_file), job_desc)
    
    # Visual progress bar
    st.progress(results["score"] / 100)
    st.subheader(f"📊 ATS Match Score: {results['score']}%")
    
    # Detailed suggestions (hidden by default)
    with st.expander("🔍 Click for detailed feedback"):
        if results["missing_kw"]:
            st.error(f"❌ Missing keywords: {', '.join(results['missing_kw'])}")
        if results["weak_phrases"]:
            st.warning(f"💡 Improve these phrases: {', '.join(set(results['weak_phrases']))}")