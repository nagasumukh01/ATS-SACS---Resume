import streamlit as st
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Union

@st.cache_resource(show_spinner="Loading Semantic AI Model (all-MiniLM-L6-v2)...")
def get_embedding_model():
    """
    Loads and caches the SentenceTransformer model.
    This avoids reloading the model from disk on every Streamlit rerun.
    """
    try:
        model = SentenceTransformer('all-MiniLM-L6-v2')
        return model
    except Exception as e:
        # Fallback in case of networking issues during initial run
        st.error(f"Error loading model: {str(e)}")
        # Let's try downloading from huggingface hub natively
        return SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def get_embeddings(texts: List[str]) -> np.ndarray:
    """Generates embeddings for a list of strings."""
    if not texts:
        return np.array([])
    model = get_embedding_model()
    return model.encode(texts, convert_to_numpy=True)

def get_single_embedding(text: str) -> np.ndarray:
    """Generates embedding for a single string."""
    if not text:
        return np.zeros(384) # Dim of all-MiniLM-L6-v2 is 384
    model = get_embedding_model()
    return model.encode(text, convert_to_numpy=True)

def compute_cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """Computes cosine similarity between two 1D numpy arrays."""
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return float(np.dot(vec1, vec2) / (norm1 * norm2))
