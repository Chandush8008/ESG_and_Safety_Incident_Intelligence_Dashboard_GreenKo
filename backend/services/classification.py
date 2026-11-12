"""
Hybrid incident classification service combining domain rules and TF-IDF similarity.
"""

from typing import Dict, Any, List, Tuple
from backend.services.preprocessing import clean_text, tokenize, extract_domain_phrases
from backend.services.retrieval_service import retrieval_service

# Domain Lexicons with weights
RULE_LEXICONS = {
    "safety": {
        "phrases": [
            ("near miss", 3.0),
            ("vehicle movement", 2.5),
            ("cable trench", 2.5),
            ("wet walkway", 2.5),
            ("ppe non-compliance", 2.5),
            ("electrical shock", 3.0),
            ("arc flash", 3.0),
            ("minor injury", 2.5),
            ("fatal accident", 4.0),
            ("safety harness", 2.0),
            ("panel cleaning activity", 1.5)
        ],
        "keywords": {
            "slip": 2.0, "slipped": 2.0, "fall": 2.0, "tripped": 2.0, "injury": 2.5,
            "ppe": 2.0, "walkway": 1.5, "trench": 1.5, "shock": 2.5, "fire": 2.5,
            "burn": 2.5, "scaffold": 2.0, "harness": 2.0, "helmet": 1.5, "worker": 1.0,
            "first-aid": 2.0, "amputation": 4.0, "fatality": 4.0, "fatal": 4.0, "hazard": 1.0
        }
    },
    "environment": {
        "phrases": [
            ("oil seepage", 3.5),
            ("oil spill", 3.5),
            ("oil leakage", 3.5),
            ("spill kit", 3.0),
            ("water usage spike", 3.0),
            ("water leakage", 3.0),
            ("valve leakage", 3.0),
            ("module cleaning", 1.5),
            ("chemical spill", 3.5),
            ("waste discharge", 3.0),
            ("soil contamination", 3.5),
            ("wind gearbox", 1.5)
        ],
        "keywords": {
            "oil": 2.5, "seepage": 2.5, "leakage": 2.5, "spill": 2.5, "contamination": 2.5,
            "pollution": 2.5, "discharge": 2.0, "emission": 2.0, "gearbox": 1.5,
            "valve": 2.0, "diesel": 2.0, "chemical": 2.5, "effluent": 2.5, "ecology": 2.0
        }
    },
    "esg_compliance": {
        "phrases": [
            ("waste segregation", 3.5),
            ("contractor storage area", 2.5),
            ("compliance violation", 3.0),
            ("policy deviation", 3.0),
            ("audit failure", 3.5),
            ("regulatory non-compliance", 3.5),
            ("documentation failure", 3.0),
            ("statutory deviation", 3.0),
            ("sop deviation", 3.0)
        ],
        "keywords": {
            "segregation": 2.5, "compliance": 2.5, "deviation": 2.0, "audit": 2.5,
            "regulatory": 2.5, "governance": 2.0, "statutory": 2.5, "license": 2.0,
            "permit": 2.0, "reporting": 2.0, "documentation": 2.0, "storage": 1.0, "waste": 1.5
        }
    }
}


def score_rules(text: str) -> Tuple[Dict[str, float], Dict[str, List[str]]]:
    """
    Computes rule-based keyword/phrase match scores for each category.
    """
    text_lower = clean_text(text)
    scores = {"safety": 0.0, "environment": 0.0, "esg_compliance": 0.0}
    matched_terms = {"safety": [], "environment": [], "esg_compliance": []}

    tokens = set(tokenize(text_lower))

    for category, lex in RULE_LEXICONS.items():
        # Check multi-word phrases
        for phrase, weight in lex["phrases"]:
            if phrase in text_lower:
                scores[category] += weight
                matched_terms[category].append(phrase)

        # Check unigrams
        for kw, weight in lex["keywords"].items():
            if kw in tokens and kw not in " ".join(matched_terms[category]):
                scores[category] += weight
                matched_terms[category].append(kw)

    return scores, matched_terms


class ClassificationService:
    """
    Hybrid classification engine implementing rule-based matching,
    TF-IDF cosine similarity against historical narratives, and conflict resolution.
    """

    def classify(self, text: str, exclude_id: str = None) -> Dict[str, Any]:
        """
        Classifies narrative into safety, environment, or esg_compliance.
        """
        if not text or not text.strip():
            return {
                "predicted_category": "safety",
                "category_confidence": 0.33,
                "classification_method": "default_fallback",
                "classification_explanation": "Empty text provided; default fallback assigned.",
                "matched_keywords": [],
                "similar_incidents": []
            }

        rule_scores, matched_terms = score_rules(text)
        similar_incidents = retrieval_service.retrieve_similar(text, top_k=3, exclude_id=exclude_id)

        # Best rule-based category
        sorted_rules = sorted(rule_scores.items(), key=lambda x: x[1], reverse=True)
        top_rule_cat, top_rule_score = sorted_rules[0]
        second_rule_cat, second_rule_score = sorted_rules[1]

        # Best similarity category from retrieved historical cases
        top_sim_cat = None
        top_sim_score = 0.0
        if similar_incidents:
            top_match = similar_incidents[0]
            top_sim_cat = top_match["category"]
            top_sim_score = top_match["similarity_score"]

        # Conflict resolution logic
        # 1. Consensus: Rule and Similarity agree
        if top_rule_score > 0 and top_sim_cat == top_rule_cat and top_sim_score >= 0.20:
            method = "hybrid_consensus"
            predicted_category = top_rule_cat
            # Normalized confidence heuristic
            confidence = min(0.95, round(0.60 + (top_rule_score * 0.05) + (top_sim_score * 0.3), 2))
            explanation = (
                f"Consensus reached between domain rules (score {top_rule_score:.1f}, "
                f"matched: {', '.join(matched_terms[top_rule_cat])}) and historical case "
                f"retrieval ({similar_incidents[0]['retrieved_incident_id']}, similarity {top_sim_score:.2f})."
            )

        # 2. Strong Rule Match (>= 2.5) dominates when similarity is weak or absent
        elif top_rule_score >= 2.5 and (top_rule_score - second_rule_score >= 1.0):
            method = "rule_based"
            predicted_category = top_rule_cat
            confidence = min(0.90, round(0.55 + (top_rule_score * 0.06), 2))
            explanation = (
                f"Decisive domain rule match (score {top_rule_score:.1f}) based on keywords/phrases: "
                f"{', '.join(matched_terms[top_rule_cat])}."
            )

        # 3. High Historical Similarity (>= 0.45) with non-contradictory rules
        elif top_sim_score >= 0.45 and top_sim_cat:
            method = "similarity_matching"
            predicted_category = top_sim_cat
            confidence = min(0.85, round(0.50 + (top_sim_score * 0.4), 2))
            explanation = (
                f"Strong similarity ({top_sim_score:.2f}) with historical incident "
                f"{similar_incidents[0]['retrieved_incident_id']} ('{similar_incidents[0]['original_narrative'][:50]}...')."
            )

        # 4. Moderate Rule Match (> 0)
        elif top_rule_score > 0:
            method = "rule_based"
            predicted_category = top_rule_cat
            confidence = round(0.55 + (top_rule_score * 0.05), 2)
            explanation = (
                f"Moderate rule indicator match for '{top_rule_cat}' "
                f"(matched: {', '.join(matched_terms[top_rule_cat])})."
            )

        # 5. Low evidence fallback: use top similar or conservative default
        elif top_sim_cat and top_sim_score >= 0.15:
            method = "similarity_matching"
            predicted_category = top_sim_cat
            confidence = round(0.40 + (top_sim_score * 0.3), 2)
            explanation = (
                f"No direct keyword rule matched; classified via closest operational narrative "
                f"{similar_incidents[0]['retrieved_incident_id']} (similarity {top_sim_score:.2f})."
            )

        else:
            method = "insufficient_evidence"
            # Default to safety for highest operational precaution in renewables
            predicted_category = "safety"
            confidence = 0.35
            explanation = (
                "Ambiguous narrative with low semantic signals. Defaulted to 'safety' under "
                "conservative operational precaution. Manual verification required."
            )

        return {
            "predicted_category": predicted_category,
            "category_confidence": confidence,
            "classification_method": method,
            "classification_explanation": explanation,
            "matched_keywords": matched_terms.get(predicted_category, []),
            "similar_incidents": similar_incidents
        }


# Global singleton instance
classification_service = ClassificationService()
