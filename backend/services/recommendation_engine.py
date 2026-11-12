"""
Recommendation engine and risk tagging service.
Generates structured immediate, preventive, and long-term actions aligned with safety hierarchy of controls.
"""

import re
from typing import Dict, Any, List, Tuple
from backend.services.preprocessing import clean_text

# Risk tag dictionary with regex patterns and evidence extraction
RISK_TAG_DEFINITIONS = [
    ("Slip and Fall", [r"\b(slipped|slip|tripped|wet walkway|fall)\b"], "Slip or trip on walkway or floor surface"),
    ("PPE Non-Compliance", [r"\b(ppe|protective equipment|helmet|harness|safety glasses|vest)\b"], "Failure to wear or maintain prescribed personal protective equipment"),
    ("Oil Leakage", [r"\b(oil seepage|oil leakage|oil spill|lubricant)\b"], "Uncontrolled hydrocarbon seepage or discharge"),
    ("Water Leakage", [r"\b(water usage|valve leakage|pipe leak|water spike)\b"], "Water loss or pipeline/valve mechanical defect"),
    ("Vehicle Movement Risk", [r"\b(vehicle movement|truck|forklift|tractor|crane|night shift.*vehicle)\b"], "Mobile plant or vehicular transit near work zones"),
    ("Near Miss", [r"\b(near miss|close call|narrowly avoided)\b"], "Unplanned incident that did not result in injury but had potential to do so"),
    ("Waste Management", [r"\b(waste segregation|storage area|trash|scrap|dumping)\b"], "Non-compliant sorting or storage of operational waste"),
    ("Contractor Safety", [r"\b(contractor|third[\-\s]party vendor|subcontractor)\b"], "Contractor work practice or contractor oversight finding"),
    ("Environmental Contamination", [r"\b(seepage|spill kit|effluent|pollution|contamination|chemical)\b"], "Threat or event of soil/water resource contamination"),
    ("Equipment Failure", [r"\b(gearbox|valve|pump|transformer|inverter|mechanical failure)\b"], "Component wear, leakage, or mechanical malfunction"),
    ("Electrical Hazard", [r"\b(electrical|shock|arc flash|switchyard|high voltage|cable trench)\b"], "Energized electrical equipment or trench proximity"),
    ("Fire Risk", [r"\b(fire|burn|spark|flame|combustion|thermal)\b"], "Combustion hazard or thermal runaway risk"),
    ("Regulatory Compliance", [r"\b(compliance|deviation|audit|statutory|sop|violation)\b"], "Deviation from statutory, permit, or internal ESG guidelines")
]


class RecommendationEngine:
    """
    Computes risk tags and context-aware hierarchical recommendations.
    """

    def extract_risk_tags(self, text: str) -> Tuple[List[str], List[Dict[str, str]]]:
        """
        Scans narrative for matching risk tags and extracts evidence quotes.
        """
        cleaned = clean_text(text)
        tags: List[str] = []
        details: List[Dict[str, str]] = []

        for tag_name, patterns, desc in RISK_TAG_DEFINITIONS:
            for pat in patterns:
                m = re.search(pat, cleaned)
                if m:
                    tags.append(tag_name)
                    details.append({
                        "tag": tag_name,
                        "evidence": f"Matched '{m.group(0)}' in narrative: {desc}"
                    })
                    break

        if not tags:
            tags.append("General Operational Observation")
            details.append({
                "tag": "General Operational Observation",
                "evidence": "No specialized hazard tag identified; routine operational observation."
            })

        return tags, details

    def generate_recommendations(
        self,
        text: str,
        category: str,
        severity: str,
        risk_tags: List[str]
    ) -> Dict[str, Any]:
        """
        Generates context-aware immediate, preventive, and long-term actions.
        """
        cleaned = clean_text(text)

        immediate: List[str] = []
        preventive: List[str] = []
        long_term: List[str] = []
        reasons: List[str] = []

        # 1. Slip and Fall / Wet Walkway
        if "Slip and Fall" in risk_tags or "wet walkway" in cleaned or "slipped" in cleaned:
            immediate.append("Deploy 'Caution: Wet Floor' signage and dry the wet walkway immediately.")
            immediate.append("Verify contractor medical status and administer first aid if required.")
            preventive.append("Install rubberized anti-slip treads and tactile grating across solar block access paths.")
            preventive.append("Conduct a housekeeping audit and inspect module washing drainage run-off channels.")
            long_term.append("Engineer positive walkway drainage slopes away from pedestrian walkways in solar field design.")
            reasons.append("Addressing physical slip/trip hazards via elimination and engineering controls.")

        # 2. PPE Non-Compliance
        if "PPE Non-Compliance" in risk_tags or "ppe" in cleaned:
            immediate.append("Issue immediate task stand-down until non-compliant workers are fitted with certified PPE.")
            immediate.append("Log contractor safety non-conformance notice (NCN) with the site safety officer.")
            preventive.append("Institute mandatory pre-task 'Toolbox Talks' (TBT) with physical PPE inspection before panel cleaning.")
            preventive.append("Conduct unannounced safety audits during high-activity module cleaning shifts.")
            long_term.append("Incorporate PPE adherence scoring into contractor monthly performance scorecards and SLA renewals.")
            reasons.append("Mitigating personal injury vulnerability through administrative enforcement and contractor accountability.")

        # 3. Oil Leakage / Wind Gearbox
        if "Oil Leakage" in risk_tags or "oil" in cleaned or "gearbox" in cleaned:
            immediate.append("Deploy containment boom / absorbent pads from the spill kit to stop spread.")
            immediate.append("Isolate gearbox lube-oil lines and tag out equipment if leakage exceeds drip tolerance.")
            preventive.append("Conduct dye-penetrant or torque inspection on gearbox casing seals and oil flanges.")
            preventive.append("Restock used spill kit materials and dispose of contaminated absorbents via authorized recycler.")
            long_term.append("Implement automated oil-level drop telemetry and condition monitoring for early seal wear detection.")
            reasons.append("Preventing environmental soil/groundwater contamination and catastrophic rotating equipment failure.")

        # 4. Water Leakage / Spike
        if "Water Leakage" in risk_tags or "water" in cleaned or "valve" in cleaned:
            immediate.append("Shut off isolating valve on the cleaning water branch line to halt resource loss.")
            immediate.append("Inspect valve body, seals, and gasket seating for mechanical damage.")
            preventive.append("Schedule quarterly hydrostatic pressure testing and seal replacement for solar cleaning manifolds.")
            preventive.append("Establish a daily water-meter reconciliation log between bulk supply and cleaning consumption.")
            long_term.append("Install smart ultrasonic flow meters with automated telemetry alarms for anomalous flow spikes.")
            reasons.append("Optimizing operational water stewardship and preserving scarce natural resources in arid renewable zones.")

        # 5. Vehicle Movement / Cable Trench / Near Miss
        if "Vehicle Movement Risk" in risk_tags or "cable trench" in cleaned or "near miss" in cleaned:
            immediate.append("Suspend vehicle transit in the unlit cable trench corridor until safety review completes.")
            immediate.append("Erect rigid physical barriers and reflective high-visibility tape around all exposed cable trenches.")
            preventive.append("Upgrade mobile lighting towers during night shifts along plant service roads and excavation zones.")
            preventive.append("Define and enforce speed limits (max 15 km/h) and designated heavy equipment routes.")
            long_term.append("Enforce a 3-meter vehicular exclusion zone policy for all unbackfilled cable trenches with GPS geofencing.")
            reasons.append("Preventing vehicle rollover, structural trench collapse, and fatal personnel impact.")

        # 6. Waste Management / ESG Compliance
        if "Waste Management" in risk_tags or "waste segregation" in cleaned or "storage area" in cleaned:
            immediate.append("Direct contractor supervisor to re-segregate co-mingled scrap and hazardous wastes immediately.")
            immediate.append("Seal and shelter waste storage bins to prevent windblown debris and stormwater runoff.")
            preventive.append("Install clearly color-coded, multilingual labelled waste disposal receptacles in contractor laydown yards.")
            preventive.append("Deliver refresher training on Greenko ESG Hazardous and Non-Hazardous Waste Management Protocols.")
            long_term.append("Establish a circular waste tracking dashboard linked with certified third-party scrap recyclers.")
            reasons.append("Ensuring regulatory environmental compliance and maintaining corporate ESG audit readiness.")

        # Default actions if none matched
        if not immediate:
            immediate.append("Inspect incident location, secure the immediate perimeter, and interview involved personnel.")
            preventive.append("Conduct a Root Cause Analysis (RCA) and review the relevant Standard Operating Procedure (SOP).")
            long_term.append("Integrate findings into site EHS management review and periodic safety committee meetings.")
            reasons.append("Applying standard operational EHS review and hierarchy of controls.")

        # Severity specific escalations
        if severity in ("high", "critical"):
            immediate.insert(0, "URGENT: Escalate incident to Site Head and Corporate EHS Director within 1 hour.")

        return {
            "immediate_actions": immediate,
            "preventive_actions": preventive,
            "long_term_actions": long_term,
            "recommendation_reason": " | ".join(reasons) if reasons else "Standard hierarchy of EHS controls applied."
        }


# Global singleton instance
recommendation_engine = RecommendationEngine()
