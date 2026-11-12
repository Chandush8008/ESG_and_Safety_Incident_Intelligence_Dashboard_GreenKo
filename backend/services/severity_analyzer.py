"""
Severity analysis and risk scoring service with contextual negation awareness.
"""

import re
from typing import Dict, Any, List
from backend.services.preprocessing import clean_text

# High-risk keywords & patterns for renewable energy operations
CRITICAL_INDICATORS = [
    (r"\b(fatality|fatal|death|died|killed|electrocution)\b", 95, "Fatality or loss of life reported"),
    (r"\b(life[\-\s]threatening|critical condition|amputation|loss of limb)\b", 90, "Life-threatening trauma or irreversible injury"),
    (r"\b(major (electrical )?fire|catastrophic fire|explosion|transformer explosion|grid collapse)\b", 90, "Catastrophic fire, explosion, or grid collapse"),
    (r"\b(massive chemical spill|toxic cloud|severe environmental disaster|fire brigade called)\b", 88, "Severe wide-area environmental or emergency hazard")
]

HIGH_INDICATORS = [
    (r"\bnear miss\b", 70, "Near-miss event with potential for severe harm"),
    (r"\b(close to cable trench|uncovered trench|cable trench|trench excavation)\b", 72, "High-consequence excavation / cable trench hazard zone"),
    (r"\b(working atop|height|without.*(harness|helmet)|no.*harness|fall from height)\b", 70, "High-altitude work without fall arrest protection"),
    (r"\b(night shift|poor illumination|low visibility)\b", 66, "Compounding environmental risk: night shift / low visibility"),
    (r"\b(oil seepage|oil leakage|gear oil|oil spill|fuel spill|gearbox maintenance|nacelle)\b", 68, "Substantial hydrocarbon seepage/leakage near rotating equipment"),
    (r"\b(electrical shock|arc flash|flashover|live conductor|high[\-\s]voltage)\b", 78, "High-voltage electrical contact or arc hazard"),
    (r"\b(fire|burning|smoke observed)\b", 74, "Thermal or combustion hazard detected"),
    (r"\b(urgent containment|emergency stop|evacuation)\b", 72, "Immediate emergency response or containment invoked")
]

MEDIUM_INDICATORS = [
    (r"\b(minor injury|first aid|abrasion|bruise|contusion|elbow)\b", 52, "Minor injury sustained requiring first aid"),
    (r"\b(slipped|slip|tripped)\b", 48, "Slip/trip occurrence on walkway or work surface"),
    (r"\b(water usage spike|valve leakage|pipe leak|water line|ruptured|pipeline leak)\b", 48, "Resource loss / pipeline or valve leakage impacting operations"),
    (r"\b(ppe non[\-\s]compliance|missing helmet|no harness|without.*ppe)\b", 50, "PPE non-compliance exposing personnel to hazard"),
    (r"\b(repeated deviation|recurring violation)\b", 48, "Repeated procedural or compliance deviation")
]

LOW_INDICATORS = [
    (r"\b(housekeeping issue|untidy|cluttered walkway)\b", 25, "Housekeeping deficiency with low immediate hazard"),
    (r"\b(waste segregation deviation|storage area deviation|scrap|cardboard)\b", 22, "Procedural waste handling / sorting deviation"),
    (r"\b(routine audit|minor paperwork|labelling|audit non[\-\s]conformance)\b", 22, "Administrative or clerical compliance observation"),
    (r"\b(contained with spill kit|spill kit)\b", -5, "Active on-site mitigation via spill kit")
]

# Negation patterns that negate injury or hazard
NEGATION_PATTERNS = [
    r"\b(no|without|zero|neither)\s+(injuries|injury|harm|damage|casualty)\b",
    r"\bno\s+one\s+was\s+(injured|hurt|affected)\b",
    r"\b(prevented|avoided)\s+(harm|injury|accident)\b"
]


class SeverityAnalyzer:
    """
    Context-aware risk scoring and severity assessment engine.
    """

    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyzes narrative context, negations, and hazard factors to compute
        an explainable risk score and map to LOW, MEDIUM, HIGH, or CRITICAL.
        """
        if not text or not text.strip():
            return {
                "predicted_severity": "low",
                "risk_score": 10,
                "risk_factors": ["Empty narrative; minimal baseline severity assigned."],
                "severity_explanation": "No incident details provided.",
                "requires_immediate_attention": False,
                "confidence": 0.50
            }

        cleaned = clean_text(text)
        risk_factors: List[str] = []
        base_scores: List[int] = []

        # Check for explicit negations (e.g., "no injury occurred")
        has_no_injury = any(re.search(pat, cleaned) for pat in NEGATION_PATTERNS)
        if has_no_injury:
            risk_factors.append("Explicit negation verified: no personal injury sustained.")

        # 1. Critical Checks
        for pat, score, reason in CRITICAL_INDICATORS:
            if re.search(pat, cleaned):
                base_scores.append(score)
                risk_factors.append(reason)

        # 2. High Checks
        for pat, score, reason in HIGH_INDICATORS:
            if re.search(pat, cleaned):
                base_scores.append(score)
                risk_factors.append(reason)

        # 3. Medium Checks
        for pat, score, reason in MEDIUM_INDICATORS:
            if re.search(pat, cleaned):
                # If there's an explicit negation of injury, suppress false injury scoring
                if "injury" in reason.lower() and has_no_injury:
                    continue
                base_scores.append(score)
                risk_factors.append(reason)

        # 4. Low Checks & Mitigating Factors
        for pat, score, reason in LOW_INDICATORS:
            if re.search(pat, cleaned):
                base_scores.append(score)
                risk_factors.append(reason)

        # Compute composite risk score
        if not base_scores:
            # Baseline neutral operational score
            calculated_score = 30
            risk_factors.append("Routine operational narrative without explicit high-risk hazard keywords.")
        else:
            # Emphasize max hazard, adjusted with secondary factors
            max_score = max(base_scores)
            secondary_boost = min(15, (len(base_scores) - 1) * 3) if len(base_scores) > 1 else 0
            calculated_score = max(5, min(100, max_score + secondary_boost))

        # Adjust score if explicit negation exists
        if has_no_injury and calculated_score > 60 and not any(re.search(p[0], cleaned) for p in CRITICAL_INDICATORS):
            calculated_score = max(35, calculated_score - 15)

        # Classify Severity Level
        if calculated_score >= 85:
            severity = "critical"
            requires_immediate = True
            explanation = "CRITICAL: Imminent life safety, catastrophic fire, or major environmental crisis."
        elif calculated_score >= 65:
            severity = "high"
            requires_immediate = True
            explanation = "HIGH: Significant incident with serious near-miss, containment need, or high potential harm."
        elif calculated_score >= 40:
            severity = "medium"
            requires_immediate = False
            explanation = "MEDIUM: Moderate operational disruption, minor injury, or equipment leakage requiring corrective action."
        else:
            severity = "low"
            requires_immediate = False
            explanation = "LOW: Minor housekeeping or administrative compliance deviation with no active hazard."

        # Confidence heuristic based on density of identified risk factors
        factor_count = len(risk_factors)
        confidence = min(0.92, round(0.55 + (factor_count * 0.08), 2))

        return {
            "predicted_severity": severity,
            "risk_score": int(calculated_score),
            "risk_factors": risk_factors,
            "severity_explanation": explanation,
            "requires_immediate_attention": requires_immediate,
            "confidence": confidence
        }


# Global singleton instance
severity_analyzer = SeverityAnalyzer()
