from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


Severity = Literal["red", "amber", "green"]


class Evidence(BaseModel):
    quote: str
    page: int = Field(ge=1)


class ExtractedField(BaseModel):
    value: str | list[str] | None = None
    confidence: float = Field(ge=0, le=1)
    evidence: Evidence | None = None


class RiskFinding(BaseModel):
    rule_id: str
    title: str
    severity: Severity
    explanation: str
    evidence: Evidence | None = None
    confidence: float = Field(ge=0, le=1)
    requires_human_review: bool = False


class ExtractionResult(BaseModel):
    document_type: str
    language: str
    parties: ExtractedField
    effective_date: ExtractedField
    expiry_date: ExtractedField
    financial_obligations: ExtractedField
    payment_terms: ExtractedField
    service_obligations: ExtractedField
    termination_notice: ExtractedField
    renewal_terms: ExtractedField
    jurisdiction: ExtractedField
    arbitration: ExtractedField
    unilateral_modification: ExtractedField
    penalties: ExtractedField
    confidentiality: ExtractedField
    intellectual_property: ExtractedField
    data_handling: ExtractedField
    indemnity: ExtractedField
    liability_cap: ExtractedField
    missing_information: list[str] = Field(default_factory=list)
    extraction_confidence: float = Field(ge=0, le=1)


class CoverageBreakdown(BaseModel):
    critical_field_completeness: int = Field(ge=0, le=25)
    clause_balance_and_obligations: int = Field(ge=0, le=25)
    financial_exposure_clarity: int = Field(ge=0, le=20)
    termination_and_renewal_clarity: int = Field(ge=0, le=15)
    jurisdiction_and_dispute_readiness: int = Field(ge=0, le=10)
    extraction_confidence: int = Field(ge=0, le=5)


class AnalysisResponse(BaseModel):
    analysis_id: str
    filename: str
    status: Literal["review_ready", "human_review_required"]
    review_coverage: int | None
    coverage_breakdown: CoverageBreakdown | None
    executive_summary: str
    next_actions: list[str]
    extraction: ExtractionResult
    findings: list[RiskFinding]
    disclaimer: str
    model_used: str
