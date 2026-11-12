"""
Summarization engine providing concise narratives and structured operational fields.
Uses extractive and template-based techniques without external APIs.
"""

import re
from typing import Dict, Any
from backend.services.preprocessing import clean_text


class IncidentSummarizer:
    """
    Generates concise offline summaries and structured root-cause/hazard perspectives.
    """

    def summarize(
        self,
        narrative: str,
        predicted_category: str,
        predicted_severity: str
    ) -> Dict[str, Any]:
        """
        Synthesizes narrative into an executive summary and structured operational dimensions.
        """
        cleaned = clean_text(narrative)

        # 1. Extract Who / What was involved
        actor = "Personnel"
        if "contractor" in cleaned:
            actor = "Contractor personnel"
        elif "worker" in cleaned:
            actor = "Site worker"
        elif "vehicle" in cleaned:
            actor = "Site vehicle"
        elif "gearbox" in cleaned:
            actor = "Wind turbine gearbox unit"
        elif "valve" in cleaned:
            actor = "Module cleaning water valve"

        # 2. Extract Location
        location = "the site operational area"
        if "solar block" in cleaned:
            location = "the solar block"
        elif "maintenance bay" in cleaned or "gearbox maintenance" in cleaned:
            location = "the wind gearbox maintenance bay"
        elif "inverter" in cleaned:
            location = "the solar inverter control room"
        elif "nacelle" in cleaned or "wind turbine" in cleaned:
            location = "the wind turbine nacelle area"
        elif "cable trench" in cleaned:
            location = "the cable trench corridor"
        elif "storage area" in cleaned:
            location = "the contractor storage area"
        elif "panel cleaning" in cleaned or "module cleaning" in cleaned:
            location = "the solar array cleaning zone"
        elif "substation" in cleaned or "switchyard" in cleaned:
            location = "the substation / switchyard"

        # 3. Identify Primary Hazard
        hazard = "General operational hazard"
        if "wet walkway" in cleaned or "slipped" in cleaned or "slip" in cleaned:
            hazard = "Wet walkway slip and fall hazard"
        elif "oil seepage" in cleaned or "oil leakage" in cleaned or "oil spill" in cleaned:
            hazard = "Hydrocarbon leakage and slip/environmental contamination hazard"
        elif "ppe" in cleaned:
            hazard = "Personal protective equipment (PPE) non-compliance hazard"
        elif "near miss" in cleaned or "vehicle" in cleaned or "trench" in cleaned:
            hazard = "Vehicle movement hazard adjacent to uncovered cable trench"
        elif "water" in cleaned and "leakage" in cleaned:
            hazard = "Pressurized pipeline/valve leakage and resource waste hazard"
        elif "waste segregation" in cleaned:
            hazard = "Improper waste disposal and segregation non-compliance"
        elif "electrical" in cleaned or "shock" in cleaned:
            hazard = "Electrical contact / arc flash hazard"
        elif "fire" in cleaned:
            hazard = "Thermal combustion and fire hazard"

        # 4. Possible Contributing Factor (Hedged appropriately)
        contributing_factor = "Unspecified operational or procedural conditions"
        if "housekeeping" in cleaned:
            contributing_factor = "Substandard housekeeping and inadequate water drainage on walkway"
        elif "gearbox" in cleaned or "oil" in cleaned:
            contributing_factor = "Possible mechanical seal wear or gasket degradation during maintenance"
        elif "night shift" in cleaned:
            contributing_factor = "Sub-optimal night-shift illumination and lack of physical demarcation"
        elif "valve" in cleaned:
            contributing_factor = "Valve seal deterioration or uncalibrated pressure during module cleaning"
        elif "ppe" in cleaned:
            contributing_factor = "Inadequate pre-task safety briefing or supervision oversight"
        elif "repeated" in cleaned or "waste" in cleaned:
            contributing_factor = "Inadequate contractor onboarding and lack of designated, labelled bins"

        # 5. Operational Impact
        impact = "Minor localized disruption"
        if "minor injury" in cleaned:
            impact = "First-aid medical treatment administered; brief task pause"
        elif "spill kit" in cleaned or "oil" in cleaned:
            impact = "Maintenance area containment initiated; oil recovery executed"
        elif "near miss" in cleaned:
            impact = "Potential high-consequence collision avoided; traffic risk highlighted"
        elif "water usage spike" in cleaned:
            impact = "Unplanned water loss and auxiliary utility cost increase"
        elif "waste" in cleaned:
            impact = "Potential audit finding and ESG compliance score deduction"
        elif predicted_severity in ("high", "critical"):
            impact = "High operational disruption risk; stop-work assessment warranted"

        # 6. Concise Narrative Summary
        if "slipped" in cleaned or "slip" in cleaned or "fall" in cleaned:
            concise_summary = (
                f"{actor} experienced a slip/fall hazard near a walkway in {location}. "
                f"The event indicates a surface housekeeping issue and personal safety risk."
            )
        elif "oil" in cleaned or "seepage" in cleaned or "leakage" in cleaned and "gear" in cleaned:
            concise_summary = (
                f"Hydrocarbon leakage/seepage was detected in {location}, requiring containment. "
                f"The event represents an environmental and rotating machinery maintenance priority."
            )
        elif "ppe" in cleaned or "harness" in cleaned or "helmet" in cleaned:
            concise_summary = (
                f"PPE non-compliance was observed during operations in {location}. "
                f"Indicates a supervisory control gap and personal safety exposure."
            )
        elif "near miss" in cleaned or "trench" in cleaned or "vehicle" in cleaned:
            concise_summary = (
                f"A high-potential near miss occurred involving {actor.lower()} operating in proximity to {location}. "
                f"Reflects acute traffic management and trench demarcation risk."
            )
        elif "fire" in cleaned or "explosion" in cleaned or "arc flash" in cleaned:
            concise_summary = (
                f"A major thermal/combustion emergency was reported in {location}, "
                f"requiring immediate fire containment and operational shutdown."
            )
        elif "water" in cleaned and ("leakage" in cleaned or "ruptured" in cleaned or "spike" in cleaned):
            concise_summary = (
                f"A water loss and pipeline/valve defect was identified in {location}, "
                f"causing utility resource loss."
            )
        elif "waste" in cleaned or "segregation" in cleaned:
            concise_summary = (
                f"Recurring waste segregation deviation was recorded in {location}, "
                f"posing an ESG environmental compliance deviation."
            )
        else:
            concise_summary = (
                f"An incident categorized under {predicted_category} with {predicted_severity} severity "
                f"occurred in {location}. Narrative: '{narrative.strip()}'."
            )

        # 7. Recommended Action
        recommended_action = "Review task risk assessment and conduct refresher safety briefing."
        if "walkway" in cleaned:
            recommended_action = "Inspect drainage, deploy anti-slip mats, and mandate dry walkway maintenance."
        elif "oil" in cleaned:
            recommended_action = "Perform torque and seal audit on gearbox, replenish spill kit inventory."
        elif "near miss" in cleaned or "trench" in cleaned:
            recommended_action = "Install reflective physical barricades along trench and enforce vehicle speed limits."
        elif "ppe" in cleaned:
            recommended_action = "Enforce pre-shift 'Toolbox Talk' PPE checklist and conduct spot inspections."
        elif "water" in cleaned:
            recommended_action = "Replace leaking valve assembly and install flow-rate telemetry monitoring."
        elif "waste" in cleaned:
            recommended_action = "Provide color-coded bins at contractor yard and mandate daily waste log sign-off."

        return {
            "summary": concise_summary,
            "structured": {
                "brief": concise_summary,
                "identified_hazard": hazard,
                "possible_contributing_factor": contributing_factor,
                "operational_impact": impact,
                "recommended_action": recommended_action
            }
        }


# Global singleton instance
incident_summarizer = IncidentSummarizer()
