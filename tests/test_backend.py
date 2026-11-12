"""
Comprehensive test suite for Greenko ESG / Safety Incident Intelligence Dashboard.
Tests data loading, NLP preprocessing, classification, severity scoring,
summarization, recommendations, pattern analysis, and FastAPI endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from backend.app import app
from backend.services.data_service import DataService, data_service
from backend.services.preprocessing import clean_text, tokenize, remove_stopwords, preprocess_narrative
from backend.services.classification import classification_service, score_rules
from backend.services.severity_analyzer import severity_analyzer
from backend.services.summarizer import incident_summarizer
from backend.services.recommendation_engine import recommendation_engine
from backend.services.pattern_analyzer import pattern_analyzer
from backend.services.evaluation import evaluation_service, UNSEEN_TEST_CASES

client = TestClient(app)


# ============================================================================
# Unit Tests: Data Service
# ============================================================================

def test_data_service_loaded():
    """Verify bundled dataset loads 6 valid records."""
    assert data_service.is_loaded is True
    records = data_service.records
    assert len(records) == 6
    assert records[0]["incident_id"] == "S001"
    assert "target_category" in records[0]
    assert "target_severity" in records[0]


def test_data_service_get_record():
    """Verify lookup by incident ID."""
    rec = data_service.get_record("S002")
    assert rec is not None
    assert rec["target_category"] == "environment"
    assert rec["target_severity"] == "high"

    # Non-existent ID
    assert data_service.get_record("NON_EXISTENT") is None


# ============================================================================
# Unit Tests: Preprocessing
# ============================================================================

def test_preprocessing_protected_terms():
    """Ensure renewable energy domain terms are preserved."""
    narrative = "Oil seepage observed near wind gearbox maintenance bay."
    res = preprocess_narrative(narrative)
    assert "gearbox" in res["clean_text"]
    assert "seepage" in res["clean_text"]
    assert "oil seepage" in res["domain_phrases"]


def test_preprocessing_negation_cues():
    """Ensure clean_text normalizes whitespace and lowercase."""
    raw = "   Contractor SLIPPED  near   wet walkway!   "
    cleaned = clean_text(raw)
    assert cleaned == "contractor slipped near wet walkway"


# ============================================================================
# Unit Tests: Classification Service
# ============================================================================

def test_classification_bundled_records():
    """Verify classification matches all 6 reference records."""
    records = data_service.records
    for r in records:
        res = classification_service.classify(r["narrative"], exclude_id=r["incident_id"])
        assert res["predicted_category"] == r["target_category"], (
            f"Failed on {r['incident_id']}: predicted {res['predicted_category']}, expected {r['target_category']}"
        )
        assert res["category_confidence"] > 0.40
        assert res["classification_method"] in ("hybrid_consensus", "rule_based", "similarity_matching")


def test_classification_empty_text():
    """Verify safe fallback on empty text."""
    res = classification_service.classify("")
    assert res["predicted_category"] == "safety"
    assert res["classification_method"] == "default_fallback"


# ============================================================================
# Unit Tests: Severity Analyzer
# ============================================================================

def test_severity_bundled_records():
    """Verify severity matches reference labels for bundled dataset."""
    records = data_service.records
    for r in records:
        res = severity_analyzer.analyze(r["narrative"])
        assert res["predicted_severity"] == r["target_severity"], (
            f"Failed severity on {r['incident_id']}: predicted {res['predicted_severity']}, expected {r['target_severity']}"
        )


def test_severity_negation_handling():
    """Verify 'no injury' prevents false positive injury scoring."""
    pos_res = severity_analyzer.analyze("Contractor suffered minor injury near walkway.")
    neg_res = severity_analyzer.analyze("Contractor slipped near walkway but no injury occurred.")
    assert "minor injury" in pos_res["risk_factors"][0].lower() or any("injury" in f.lower() for f in pos_res["risk_factors"])
    assert any("no personal injury" in f.lower() for f in neg_res["risk_factors"])
    # Score of negated narrative should be strictly less than actual injury
    assert neg_res["risk_score"] < pos_res["risk_score"]


def test_severity_critical_indicators():
    """Verify catastrophic indicators produce critical severity."""
    crit_res = severity_analyzer.analyze("Fatal electrocution of contractor during transformer maintenance.")
    assert crit_res["predicted_severity"] == "critical"
    assert crit_res["requires_immediate_attention"] is True
    assert crit_res["risk_score"] >= 85


# ============================================================================
# Unit Tests: Summarizer & Recommendations
# ============================================================================

def test_summarizer_structure():
    """Verify offline summarizer produces non-empty structured fields."""
    narrative = "Water usage spike during module cleaning due to valve leakage"
    res = incident_summarizer.summarize(narrative, "environment", "medium")
    assert "summary" in res
    assert "structured" in res
    assert "valve" in res["summary"].lower()
    assert "possible_contributing_factor" in res["structured"]
    assert "identified_hazard" in res["structured"]


def test_recommendations_hierarchy():
    """Verify hierarchy of controls: immediate, preventive, and long-term actions."""
    narrative = "Oil seepage observed near wind gearbox maintenance bay, contained with spill kit"
    tags, _ = recommendation_engine.extract_risk_tags(narrative)
    recs = recommendation_engine.generate_recommendations(narrative, "environment", "high", tags)
    assert len(recs["immediate_actions"]) > 0
    assert len(recs["preventive_actions"]) > 0
    assert len(recs["long_term_actions"]) > 0
    assert any("spill kit" in a.lower() or "containment" in a.lower() for a in recs["immediate_actions"])


# ============================================================================
# Unit Tests: Pattern Analyzer & Evaluation
# ============================================================================

def test_pattern_analyzer():
    """Verify discovery of contractor, fluid containment, and high-consequence patterns."""
    patterns = pattern_analyzer.analyze_patterns()
    assert len(patterns) >= 2
    pattern_names = [p["pattern_name"] for p in patterns]
    assert any("Contractor" in name for name in pattern_names)
    assert any("Fluid" in name for name in pattern_names)


def test_evaluation_unseen_suite():
    """Verify benchmark pass rate on 8 unseen operational scenarios."""
    unseen_res = evaluation_service.evaluate_unseen_suite()
    assert len(unseen_res) == 8
    cat_passes = sum(1 for c in unseen_res if c["category_pass"])
    sev_passes = sum(1 for c in unseen_res if c["severity_pass"])
    # Expect 100% pass on curated domain test cases
    assert cat_passes == 8
    assert sev_passes == 8


# ============================================================================
# Integration Tests: FastAPI Endpoints
# ============================================================================

def test_api_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["dataset_loaded"] is True
    assert data["record_count"] == 6


def test_api_demo():
    response = client.get("/api/demo")
    assert response.status_code == 200
    data = response.json()
    assert data["case_study"] == "Greenko ESG / Safety Incident Intelligence Dashboard"
    assert data["status"] == "fully operational"


def test_api_incidents():
    response = client.get("/api/incidents")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 6
    assert len(data["incidents"]) == 6
    first = data["incidents"][0]
    assert first["incident_id"] == "S001"
    assert "summary" in first
    assert "recommendations" in first


def test_api_incident_by_id():
    response = client.get("/api/incidents/S003")
    assert response.status_code == 200
    data = response.json()
    assert data["incident_id"] == "S003"
    assert data["predicted_category"] == "safety"

    # Test 404
    missing_response = client.get("/api/incidents/INVALID_999")
    assert missing_response.status_code == 404


def test_api_dashboard():
    response = client.get("/api/dashboard")
    assert response.status_code == 200
    data = response.json()
    kpis = data["kpis"]
    assert kpis["total_incidents"] == 6
    assert kpis["safety_incidents"] == 3
    assert kpis["environment_incidents"] == 2
    assert kpis["esg_compliance_incidents"] == 1
    assert kpis["high_critical_incidents"] == 2
    assert len(data["recurring_patterns"]) >= 2
    assert len(data["management_insights"]) >= 3


def test_api_analyze_valid():
    payload = {"text": "Oil leakage observed near the wind turbine gearbox during maintenance.", "add_to_records": False}
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["predicted_category"] == "environment"
    assert data["predicted_severity"] in ("high", "medium")
    assert "Oil Leakage" in data["risk_tags"]
    assert len(data["similar_incidents"]) > 0
    assert len(data["recommendations"]["immediate_actions"]) > 0


def test_api_analyze_adds_record_and_updates_dashboard():
    # Ensure baseline
    client.post("/api/incidents/reset")
    dash_before = client.get("/api/dashboard").json()
    assert dash_before["kpis"]["total_incidents"] == 6

    payload = {
        "text": "Severe gear oil leakage discovered beneath wind turbine nacelle during servicing.",
        "add_to_records": True
    }
    res = client.post("/api/analyze", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["incident_id"] == "S007"
    assert data["added_to_records"] is True

    # Verify dashboard total count incremented
    dash_after = client.get("/api/dashboard").json()
    assert dash_after["kpis"]["total_incidents"] == 7

    # Verify new record is available in incidents list
    inc_res = client.get("/api/incidents").json()
    assert inc_res["total"] == 7
    assert any(i["incident_id"] == "S007" for i in inc_res["incidents"])

    # Reset back to baseline
    client.post("/api/incidents/reset")
    dash_reset = client.get("/api/dashboard").json()
    assert dash_reset["kpis"]["total_incidents"] == 6


def test_api_analyze_empty():
    payload = {"text": "   "}
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 400


def test_api_run_compatibility():
    payload = {"text": "Repeated waste segregation deviation at contractor storage area"}
    response = client.post("/api/run", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "result" in data
    assert data["result"]["category"] == "esg_compliance"


def test_api_evaluation():
    response = client.get("/api/evaluation")
    assert response.status_code == 200
    data = response.json()
    assert "bundled_benchmark" in data
    assert "unseen_suite" in data
    assert data["bundled_benchmark"]["category_accuracy"] == 1.0
    assert data["bundled_benchmark"]["severity_accuracy"] == 1.0
    assert data["unseen_suite"]["category_pass_rate"] == 1.0


def test_dynamic_incident_persistence_across_restart():
    """
    Verifies that live analyzed incidents are persisted to dynamic storage
    and reloaded seamlessly upon server restart.
    """
    from backend.services.data_service import DataService

    # 1. Reset first to clean baseline
    client.post("/api/incidents/reset")
    assert len(data_service.records) == 6

    # 2. Add a dynamic incident via /api/analyze
    payload = {
        "text": "Solar technician dropped electrical tool into cable trench during night inspection",
        "add_to_records": True
    }
    res = client.post("/api/analyze", json=payload)
    assert res.status_code == 200
    data = res.json()
    new_id = data["incident_id"]
    assert new_id == "S007"
    assert len(data_service.records) == 7

    # 3. Simulate server restart by instantiating a fresh DataService
    fresh_service = DataService()
    assert len(fresh_service.records) == 7
    reloaded = fresh_service.get_record("S007")
    assert reloaded is not None
    assert "dropped electrical tool" in reloaded["narrative"]

    # 4. Reset to baseline and verify cleanup
    client.post("/api/incidents/reset")
    assert len(data_service.records) == 6
    after_reset_service = DataService()
    assert len(after_reset_service.records) == 6
