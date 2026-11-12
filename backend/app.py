"""
FastAPI Backend Application for Greenko ESG / Safety Incident Intelligence Dashboard.
Serves RESTful APIs for incident analysis, dashboard analytics, evaluation, and the frontend UI.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import os
import logging

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from backend.config import (
    BASE_DIR, FRONTEND_DIR, FRONTEND_INDEX, DATA_FILE, PORT, HOST
)
from backend.models import (
    Query, AnalysisRequest, AnalyzedIncident, DashboardResponse,
    HealthResponse, EvaluationSummary
)
from backend.services.data_service import data_service
from backend.services.preprocessing import preprocess_narrative
from backend.services.retrieval_service import retrieval_service
from backend.services.classification import classification_service
from backend.services.severity_analyzer import severity_analyzer
from backend.services.summarizer import incident_summarizer
from backend.services.recommendation_engine import recommendation_engine
from backend.services.pattern_analyzer import pattern_analyzer
from backend.services.evaluation import evaluation_service

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("greenko_ehs_app")

app = FastAPI(
    title="Greenko ESG & Safety Incident Intelligence Dashboard",
    description="AI-powered renewable energy incident classification, risk scoring, pattern detection, and decision support.",
    version="1.0.0"
)

# CORS configuration (allows development flexibility while keeping deployment secure)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


def run_full_pipeline(
    narrative: str,
    incident_id: Optional[str] = None,
    reference_category: Optional[str] = None,
    reference_severity: Optional[str] = None
) -> Dict[str, Any]:
    """
    Executes the unified modular NLP, classification, severity scoring,
    risk tagging, summarization, and recommendation pipeline.
    """
    pre = preprocess_narrative(narrative)
    cat_res = classification_service.classify(narrative, exclude_id=incident_id)
    sev_res = severity_analyzer.analyze(narrative)
    risk_tags, risk_tag_details = recommendation_engine.extract_risk_tags(narrative)

    summary_res = incident_summarizer.summarize(
        narrative=narrative,
        predicted_category=cat_res["predicted_category"],
        predicted_severity=sev_res["predicted_severity"]
    )

    recs_res = recommendation_engine.generate_recommendations(
        text=narrative,
        category=cat_res["predicted_category"],
        severity=sev_res["predicted_severity"],
        risk_tags=risk_tags
    )

    limitations = [
        "AI-assisted decision-support recommendation; does not replace mandatory regulatory or safety assessments.",
        "Classification is based on domain heuristic rules and TF-IDF similarity on historical records.",
        "Root cause indications represent possible contributing factors based on narrative evidence, not forensic proof."
    ]

    return {
        "incident_id": incident_id,
        "input": narrative,
        "clean_text": pre["clean_text"],
        "predicted_category": cat_res["predicted_category"],
        "category_confidence": cat_res["category_confidence"],
        "classification_method": cat_res["classification_method"],
        "classification_explanation": cat_res["classification_explanation"],
        "matched_keywords": cat_res["matched_keywords"],
        "predicted_severity": sev_res["predicted_severity"],
        "risk_score": sev_res["risk_score"],
        "risk_factors": sev_res["risk_factors"],
        "severity_explanation": sev_res["severity_explanation"],
        "requires_immediate_attention": sev_res["requires_immediate_attention"],
        "risk_tags": risk_tags,
        "risk_tag_details": risk_tag_details,
        "summary": summary_res["summary"],
        "structured_summary": summary_res["structured"],
        "similar_incidents": cat_res["similar_incidents"],
        "recommendations": recs_res,
        "limitations": limitations,
        "reference_category": reference_category,
        "reference_severity": reference_severity
    }


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/api/health", response_model=HealthResponse)
def health_check():
    """
    Returns application status, dataset availability, and pipeline readiness.
    """
    return {
        "status": "healthy" if data_service.is_loaded else "degraded",
        "service": "Greenko ESG & Safety Incident Intelligence API",
        "version": "1.0.0",
        "dataset_loaded": data_service.is_loaded,
        "record_count": len(data_service.records),
        "pipeline_ready": retrieval_service.is_fitted
    }


@app.get("/api/demo")
def demo():
    """
    Preserved starter endpoint enriched with full domain architecture details.
    """
    return {
        "case_study": "Greenko ESG / Safety Incident Intelligence Dashboard",
        "status": "fully operational",
        "expected_outcome": "An AI-powered dashboard classifying incident category, severity, recurring patterns, and preventive recommendations.",
        "sample_incidents_count": len(data_service.records),
        "pipeline_components": [
            "Domain Text Preprocessing (Keyword & Compound Retention)",
            "Hybrid Rule-Based + TF-IDF Cosine Similarity Classification",
            "Contextual Negation-Aware Severity Risk Scorer",
            "Hierarchy-of-Controls Recommendation Engine",
            "Recurring Operational Pattern & Management Insight Detector",
            "Leave-One-Out & Unseen Domain Benchmark Evaluator"
        ],
        "endpoints": {
            "health": "/api/health",
            "incidents": "/api/incidents",
            "dashboard": "/api/dashboard",
            "analyze": "/api/analyze (POST)",
            "run": "/api/run (POST)",
            "evaluation": "/api/evaluation",
            "docs": "/docs"
        }
    }


@app.get("/api/incidents")
def get_all_incidents():
    """
    Returns all dataset incident records processed through the AI analysis pipeline.
    """
    records = data_service.records
    analyzed = []
    for r in records:
        res = run_full_pipeline(
            narrative=r["narrative"],
            incident_id=r["incident_id"],
            reference_category=r.get("target_category"),
            reference_severity=r.get("target_severity")
        )
        analyzed.append(res)
    return {
        "total": len(analyzed),
        "incidents": analyzed
    }


@app.get("/api/incidents/{incident_id}")
def get_incident_detail(incident_id: str):
    """
    Returns detailed analysis for a specific incident by ID.
    """
    rec = data_service.get_record(incident_id)
    if not rec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident with ID '{incident_id}' not found in dataset."
        )
    return run_full_pipeline(
        narrative=rec["narrative"],
        incident_id=rec["incident_id"],
        reference_category=rec.get("target_category"),
        reference_severity=rec.get("target_severity")
    )


@app.get("/api/dashboard")
def get_dashboard_data():
    """
    Computes real-time dashboard KPIs, category & severity distributions,
    risk matrix, recurring patterns, risk tags, and management insights.
    Never returns hardcoded statistics.
    """
    records = data_service.records
    analyzed_list = []
    category_counts = {"safety": 0, "environment": 0, "esg_compliance": 0}
    severity_counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}
    risk_matrix = {c: {s: 0 for s in severity_counts} for c in category_counts}
    risk_tag_counts: Dict[str, int] = {}
    high_critical_count = 0

    for r in records:
        analysis = run_full_pipeline(
            narrative=r["narrative"],
            incident_id=r["incident_id"],
            reference_category=r.get("target_category"),
            reference_severity=r.get("target_severity")
        )
        analyzed_list.append(analysis)

        cat = analysis["predicted_category"]
        sev = analysis["predicted_severity"]

        if cat in category_counts:
            category_counts[cat] += 1
        else:
            category_counts[cat] = 1

        if sev in severity_counts:
            severity_counts[sev] += 1
        else:
            severity_counts[sev] = 1

        if cat in risk_matrix and sev in risk_matrix[cat]:
            risk_matrix[cat][sev] += 1

        if sev in ("high", "critical"):
            high_critical_count += 1

        for tag in analysis["risk_tags"]:
            risk_tag_counts[tag] = risk_tag_counts.get(tag, 0) + 1

    patterns = pattern_analyzer.analyze_patterns(records)
    insights = pattern_analyzer.generate_management_insights(records, patterns)

    kpis = {
        "total_incidents": len(records),
        "safety_incidents": category_counts.get("safety", 0),
        "environment_incidents": category_counts.get("environment", 0),
        "esg_compliance_incidents": category_counts.get("esg_compliance", 0),
        "high_critical_incidents": high_critical_count,
        "recurring_patterns_count": len(patterns)
    }

    return {
        "kpis": kpis,
        "category_distribution": category_counts,
        "severity_distribution": severity_counts,
        "risk_matrix": risk_matrix,
        "recurring_patterns": patterns,
        "risk_tag_distribution": risk_tag_counts,
        "management_insights": insights,
        "dataset_info": {
            "source": str(DATA_FILE.name),
            "records_count": len(records),
            "status": "online" if data_service.is_loaded else "offline"
        }
    }


@app.post("/api/analyze")
def analyze_incident(req: AnalysisRequest):
    """
    Accepts an incident narrative and returns comprehensive AI-assisted analysis.
    Adds the newly analyzed incident to incident records and updates the retrieval corpus.
    """
    text = req.text.strip()
    if not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incident narrative cannot be empty."
        )

    # Assign sequential incident ID if adding to records
    new_id = data_service.generate_next_id() if req.add_to_records else None
    res = run_full_pipeline(narrative=text, incident_id=new_id)

    if req.add_to_records and new_id:
        new_record = {
            "incident_id": new_id,
            "narrative": text,
            "target_category": res["predicted_category"],
            "target_severity": res["predicted_severity"]
        }
        data_service.add_record(new_record)
        # Update TF-IDF retrieval corpus with the new record
        retrieval_service.fit(data_service.records)
        res["added_to_records"] = True
        res["total_incidents"] = len(data_service.records)
    else:
        res["added_to_records"] = False
        res["total_incidents"] = len(data_service.records)

    return res


@app.post("/api/incidents/reset")
def reset_incidents():
    """
    Resets incident records back to the original reference dataset.
    """
    data_service.reset_to_baseline()
    retrieval_service.fit(data_service.records)
    return {
        "status": "reset",
        "total_incidents": len(data_service.records)
    }


@app.post("/api/run")
def run_case(query: Query):
    """
    Preserves exact backward compatibility with the starter endpoint,
    while delegating directly to the full intelligence pipeline.
    """
    text = query.text.strip()
    if not text:
        return {
            "input": "",
            "result": "No incident text provided. Enter a narrative to analyze.",
            "evaluation_hint": "Submit a safety or ESG incident narrative to receive AI classification and recommendations."
        }

    analysis = run_full_pipeline(narrative=text)
    return {
        "input": text,
        "result": {
            "category": analysis["predicted_category"],
            "severity": analysis["predicted_severity"],
            "risk_score": analysis["risk_score"],
            "risk_tags": analysis["risk_tags"],
            "summary": analysis["summary"],
            "recommendations": analysis["recommendations"]
        },
        "evaluation_hint": "Full pipeline executed: category classification, severity risk scoring, risk tagging, and decision support recommendations."
    }


@app.get("/api/evaluation")
def get_evaluation():
    """
    Returns offline evaluation metrics on bundled benchmark data,
    statistical class imbalance analysis, and validation results across 8 unseen scenarios.
    """
    return evaluation_service.get_full_evaluation_report()


# ============================================================================
# Static Files & Frontend UI Serving
# ============================================================================

# Mount static CSS and JS directories for modular frontend components
if (FRONTEND_DIR / "css").exists():
    app.mount("/css", StaticFiles(directory=str(FRONTEND_DIR / "css")), name="css")
if (FRONTEND_DIR / "js").exists():
    app.mount("/js", StaticFiles(directory=str(FRONTEND_DIR / "js")), name="js")

@app.get("/", response_class=HTMLResponse)
def serve_index():
    """
    Serves the modern enterprise dashboard UI.
    """
    if FRONTEND_INDEX.exists():
        return FileResponse(FRONTEND_INDEX)
    return HTMLResponse("<h2>Frontend index.html not found.</h2>", status_code=404)


@app.get("/case_study", response_class=HTMLResponse)
def serve_case_study():
    """
    Serves the original case study HTML for assignment reference.
    """
    cs_path = BASE_DIR / "case_study.html"
    if cs_path.exists():
        return FileResponse(cs_path)
    return HTMLResponse("<h2>Case study file not found.</h2>", status_code=404)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app:app", host=HOST, port=PORT, reload=True)
