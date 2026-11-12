"""
Text preprocessing and domain keyword extraction module for ESG / Safety narratives.
"""

import re
from typing import List, Set, Dict, Any

# Standard non-domain English stop words
STANDARD_STOPWORDS: Set[str] = {
    "a", "an", "the", "and", "or", "in", "on", "at", "to", "for", "of", "with",
    "by", "from", "as", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "this", "that", "these", "those",
    "it", "its", "their", "there", "which", "who", "whom", "what", "when", "where",
    "why", "how", "all", "any", "both", "each", "few", "more", "most", "other",
    "some", "such", "than", "too", "very", "can", "will", "just", "should", "now"
}

# Critical domain terms that must NEVER be stripped
PROTECTED_DOMAIN_TERMS: Set[str] = {
    "gearbox", "turbine", "solar", "panel", "electrical", "leakage", "seepage",
    "oil", "water", "spill", "kit", "cable", "trench", "ppe", "contractor",
    "waste", "segregation", "walkway", "valve", "cleaning", "storage", "night",
    "shift", "miss", "near", "slip", "slipped", "fall", "injury", "shock", "fire",
    "compliance", "deviation", "hazard", "bay", "block", "housekeeping", "audit",
    "inverter", "substation", "switchyard", "transformer", "excavation", "lockout",
    "tagout", "loto", "harness", "helmet", "barrier", "containment", "effluent"
}

# Domain multi-word phrase patterns
DOMAIN_PHRASES: List[str] = [
    "oil seepage", "oil spill", "spill kit", "wind gearbox", "gearbox maintenance",
    "solar block", "panel cleaning", "module cleaning", "cable trench", "night shift",
    "near miss", "wet walkway", "waste segregation", "storage area", "valve leakage",
    "ppe non-compliance", "housekeeping issue", "minor injury", "electrical shock",
    "vehicle movement", "policy deviation", "water usage spike", "maintenance bay",
    "safety harness", "arc flash", "first aid", "confined space"
]


def clean_text(text: str) -> str:
    """
    Cleans raw narrative by normalizing whitespace and lowercasing,
    while retaining hyphens and key punctuation markers.
    """
    if not text or not isinstance(text, str):
        return ""
    # Lowercase
    cleaned = text.lower().strip()
    # Normalize hyphens and slashes
    cleaned = cleaned.replace("_", " ").replace("/", " / ")
    # Replace non-alphanumeric except hyphen, slash, colon, period
    cleaned = re.sub(r"[^\w\s\-\:\/\.]", " ", cleaned)
    # Collapse multiple spaces
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def tokenize(text: str) -> List[str]:
    """
    Splits text into alphanumeric tokens and protected hyphenated words.
    """
    cleaned = clean_text(text)
    # Match words including hyphens like non-compliance
    tokens = re.findall(r"\b[\w\-]+\b", cleaned)
    return tokens


def remove_stopwords(tokens: List[str], preserve_domain: bool = True) -> List[str]:
    """
    Filters out common stop words while explicitly preserving domain-specific terms.
    """
    filtered = []
    for t in tokens:
        token_lower = t.lower()
        if preserve_domain and token_lower in PROTECTED_DOMAIN_TERMS:
            filtered.append(token_lower)
        elif token_lower not in STANDARD_STOPWORDS and len(token_lower) > 1:
            filtered.append(token_lower)
    return filtered


def extract_domain_phrases(text: str) -> List[str]:
    """
    Extracts recognized multi-word technical and operational phrases.
    """
    text_lower = text.lower()
    matched = []
    for phrase in DOMAIN_PHRASES:
        if phrase in text_lower:
            matched.append(phrase)
    return matched


def preprocess_narrative(text: str) -> Dict[str, Any]:
    """
    Complete NLP preprocessing pipeline for an incident narrative.
    Returns original text, cleaned text, tokens, filtered tokens, and domain keywords/phrases.
    """
    cleaned = clean_text(text)
    tokens = tokenize(cleaned)
    filtered_tokens = remove_stopwords(tokens, preserve_domain=True)
    domain_phrases = extract_domain_phrases(text)

    # Combine extracted unigram domain words and multi-word phrases
    unigram_keywords = [t for t in filtered_tokens if t in PROTECTED_DOMAIN_TERMS]
    combined_keywords = list(dict.fromkeys(domain_phrases + unigram_keywords))

    return {
        "original_text": text,
        "clean_text": " ".join(filtered_tokens),
        "tokens": tokens,
        "filtered_tokens": filtered_tokens,
        "domain_phrases": domain_phrases,
        "domain_keywords": combined_keywords
    }
