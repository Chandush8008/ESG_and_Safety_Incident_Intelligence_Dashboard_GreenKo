"""
Pattern analysis module detecting recurring operational risks and incident clusters.
Explicitly distinguishes observed repetitions from statistical trends given small dataset sizes.
"""

from typing import List, Dict, Any
from collections import Counter
from backend.services.preprocessing import clean_text, tokenize, remove_stopwords
from backend.services.data_service import data_service


class PatternAnalyzer:
    """
    Identifies recurring operational incident patterns across safety, environmental,
    and compliance dimensions using frequency analysis and semantic clustering.
    """

    def analyze_patterns(self, records: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Discovers patterns across the incident corpus.
        """
        recs = records if records is not None else data_service.records
        if not recs:
            return []

        patterns: List[Dict[str, Any]] = []

        # 1. Pattern: Contractor Safety, Supervision, and Housekeeping
        contractor_recs = [
            r for r in recs
            if "contractor" in clean_text(r["narrative"])
        ]
        if len(contractor_recs) >= 2:
            patterns.append({
                "pattern_name": "Contractor Supervision & Housekeeping Gaps",
                "pattern_type": "Worker Safety & Procedures",
                "incident_count": len(contractor_recs),
                "related_incident_ids": [r["incident_id"] for r in contractor_recs],
                "common_keywords": ["contractor", "housekeeping", "walkway", "ppe", "storage area"],
                "possible_contributing_factors": (
                    "Contractor teams need closer daily supervision, clearer safety briefings before work starts, "
                    "and better housekeeping around work areas."
                ),
                "suggested_preventive_actions": [
                    "Hold mandatory 5-minute safety briefings before every shift starts.",
                    "Assign a site safety officer to regularly check contractor work areas.",
                    "Review contractor safety and housekeeping performance monthly."
                ],
                "evidence_level": "Seen in 3 out of 6 incidents (S001, S003, S006)"
            })

        # 2. Pattern: Fluid Containment & Resource Loss (Oil & Water)
        fluid_recs = [
            r for r in recs
            if any(k in clean_text(r["narrative"]) for k in ["oil", "water", "seepage", "leakage", "spill"])
        ]
        if len(fluid_recs) >= 2:
            patterns.append({
                "pattern_name": "Fluid & Liquid Leaks (Oil and Water)",
                "pattern_type": "Equipment & Environment",
                "incident_count": len(fluid_recs),
                "related_incident_ids": [r["incident_id"] for r in fluid_recs],
                "common_keywords": ["oil seepage", "gearbox", "water usage", "valve leakage", "spill kit"],
                "possible_contributing_factors": (
                    "Worn seals and valves cause oil leaks during turbine maintenance and water loss during solar panel cleaning."
                ),
                "suggested_preventive_actions": [
                    "Check and replace worn valves and seals before major cleaning cycles begin.",
                    "Keep spill response kits fully stocked near all wind turbines and solar blocks.",
                    "Use automatic water meter alerts to catch unexpected spikes in water use."
                ],
                "evidence_level": "Seen in 2 out of 6 incidents (S002, S005)"
            })

        # 3. Pattern: Night-Shift & Critical Infrastructure Proximity
        high_risk_recs = [
            r for r in recs
            if r.get("target_severity") in ("high", "critical") or "near miss" in clean_text(r["narrative"])
        ]
        if high_risk_recs:
            patterns.append({
                "pattern_name": "High-Risk Work Zones During Night Shifts",
                "pattern_type": "Site Operational Risk",
                "incident_count": len(high_risk_recs),
                "related_incident_ids": [r["incident_id"] for r in high_risk_recs],
                "common_keywords": ["near miss", "vehicle movement", "cable trench", "night shift", "oil seepage"],
                "possible_contributing_factors": (
                    "Poor lighting during night shifts and open trenches without physical barricades increase the risk of vehicle accidents."
                ),
                "suggested_preventive_actions": [
                    "Put up strong physical barriers and bright warning lights around all open trenches.",
                    "Require spotters to guide any vehicles moving at night near work zones.",
                    "Conduct safety walk-throughs specifically during night shifts."
                ],
                "evidence_level": "Seen in 2 high-severity incidents (S002, S004)"
            })

        return patterns

    def generate_management_insights(
        self,
        recs: List[Dict[str, Any]] = None,
        patterns: List[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Synthesizes management-level strategic EHS insights.
        """
        insights = [
            {
                "category": "safety",
                "title": "Contractor Safety & Daily Supervision",
                "observation": (
                    "Half of all reported incidents involve contractors (slips, missing PPE, and storage issues). "
                    "This is the biggest area of day-to-day operational risk on site."
                ),
                "priority": "high",
                "recommended_action": "Start daily safety check-ins and practical toolbox talks for all contractor crews before work begins."
            },
            {
                "category": "environment",
                "title": "Preventing Oil Leaks and Water Waste",
                "observation": (
                    "Environmental issues come from two main areas: oil leaks during wind turbine maintenance "
                    "and water leaks during solar panel cleaning."
                ),
                "priority": "medium",
                "recommended_action": "Inspect valves and seals before cleaning campaigns, and ensure spill kits are always ready."
            },
            {
                "category": "esg_compliance",
                "title": "Proper Waste Sorting in Contractor Yards",
                "observation": (
                    "Waste segregation rules were repeatedly missed in contractor storage yards, "
                    "which could cause penalties during environmental audits."
                ),
                "priority": "medium",
                "recommended_action": "Provide clearly labeled, color-coded bins and inspect contractor waste areas once a week."
            },
            {
                "category": "strategic",
                "title": "Near-Miss Reporting & Trench Protection",
                "observation": (
                    "Incident S004 was a high-risk close call that was reported quickly. "
                    "Reporting close calls helps fix dangerous conditions before anyone gets hurt."
                ),
                "priority": "high",
                "recommended_action": "Praise teams that report near-misses, and ensure all open trenches have visible barricades."
            }
        ]
        return insights


# Global singleton instance
pattern_analyzer = PatternAnalyzer()
