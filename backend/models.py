"""
Pydantic Data Models and Schemas for ESG / Safety Incident Intelligence Dashboard.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class Query(BaseModel):
    text: str = Field("", description="Incident narrative query text")


class AnalysisRequest(BaseModel):
    text: str = Field(..., description="Incident narrative to analyze", min_length=1)
    add_to_records: bool = Field(True, description="Whether to add the analyzed incident to records and update dashboard")


class RiskTagEvidence(BaseModel):
    tag: str
    evidence: str


class Recommendations(BaseModel):
    immediate_actions: List[str] = Field(default_factory=list)
    preventive_actions: List[str] = Field(default_factory=list)
    long_term_actions: List[str] = Field(default_factory=list)
    recommendation_reason: str = ""


class SimilarIncident(BaseModel):
    retrieved_incident_id: str
    original_narrative: str
    category: str
    reference_severity: str
    similarity_score: float
    relevance_explanation: str


class StructuredSummary(BaseModel):
    brief: str
    identified_hazard: str
    possible_contributing_factor: str
    operational_impact: str
    recommended_action: str


class AnalyzedIncident(BaseModel):
    incident_id: Optional[str] = None
    input: str
    clean_text: str
    predicted_category: str
    category_confidence: float
    classification_method: str
    classification_explanation: str
    matched_keywords: List[str] = Field(default_factory=list)
    predicted_severity: str
    risk_score: int
    risk_factors: List[str] = Field(default_factory=list)
    severity_explanation: str
    requires_immediate_attention: bool
    risk_tags: List[str] = Field(default_factory=list)
    risk_tag_details: List[RiskTagEvidence] = Field(default_factory=list)
    summary: str
    structured_summary: StructuredSummary
    similar_incidents: List[SimilarIncident] = Field(default_factory=list)
    recommendations: Recommendations
    limitations: List[str] = Field(default_factory=list)
    reference_category: Optional[str] = None
    reference_severity: Optional[str] = None
    added_to_records: Optional[bool] = None
    total_incidents: Optional[int] = None


class RecurringPattern(BaseModel):
    pattern_name: str
    pattern_type: str
    incident_count: int
    related_incident_ids: List[str] = Field(default_factory=list)
    common_keywords: List[str] = Field(default_factory=list)
    possible_contributing_factors: str
    suggested_preventive_actions: List[str] = Field(default_factory=list)
    evidence_level: str


class ManagementInsight(BaseModel):
    category: str
    title: str
    observation: str
    priority: str
    recommended_action: str


class DashboardKPIs(BaseModel):
    total_incidents: int
    safety_incidents: int
    environment_incidents: int
    esg_compliance_incidents: int
    high_critical_incidents: int
    recurring_patterns_count: int


class DashboardResponse(BaseModel):
    kpis: DashboardKPIs
    category_distribution: Dict[str, int]
    severity_distribution: Dict[str, int]
    risk_matrix: Dict[str, Dict[str, int]]
    recurring_patterns: List[RecurringPattern]
    risk_tag_distribution: Dict[str, int]
    management_insights: List[ManagementInsight]
    dataset_info: Dict[str, Any]


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    dataset_loaded: bool
    record_count: int
    pipeline_ready: bool


class EvaluationSummary(BaseModel):
    sample_size: int
    accuracy_category: float
    accuracy_severity: float
    class_distribution: Dict[str, int]
    per_class_results: Dict[str, Any]
    limitations_disclaimer: str
    unseen_test_cases: List[Dict[str, Any]]
