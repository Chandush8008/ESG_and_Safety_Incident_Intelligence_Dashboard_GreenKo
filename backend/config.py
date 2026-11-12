"""
Configuration module for Greenko ESG / Safety Incident Intelligence Dashboard.
Handles file paths, environment variables, categories, severities, and thresholds.
"""

from pathlib import Path
import os

# Project Root Directory
BASE_DIR = Path(__file__).resolve().parents[1]

# Data Paths
DATA_DIR = BASE_DIR / "data"
DATA_FILE = DATA_DIR / "safety_esg_incidents.csv"
DYNAMIC_DATA_FILE = DATA_DIR / "dynamic_incidents.csv"

# Frontend Path
FRONTEND_DIR = BASE_DIR / "frontend"
FRONTEND_INDEX = FRONTEND_DIR / "index.html"

# Deployment & Server Config
PORT = int(os.getenv("PORT", 8000))
HOST = os.getenv("HOST", "0.0.0.0")

# Valid Incident Categories
ALLOWED_CATEGORIES = ("safety", "environment", "esg_compliance")

# Valid Severity Levels
ALLOWED_SEVERITIES = ("low", "medium", "high", "critical")

# Severity Scoring Thresholds
SEVERITY_THRESHOLDS = {
    "critical": 85,
    "high": 65,
    "medium": 40,
    "low": 0
}

# RAG & Similarity Thresholds
TOP_K_SIMILAR = 3
SIMILARITY_MATCH_THRESHOLD = 0.20
PATTERN_SIMILARITY_THRESHOLD = 0.28
