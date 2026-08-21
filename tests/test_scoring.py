from app.extractor import demo_extraction
from app.scoring import build_decision_brief, build_findings, calculate_coverage
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def analyse(name):
    extraction = demo_extraction(name)
    findings = build_findings(extraction)
    return extraction, findings, calculate_coverage(extraction, findings)


def test_clean_english_document_scores():
    _, _, (score, breakdown, status) = analyse("english_agreement.pdf")
    assert status == "review_ready"
    assert score >= 75
    assert score <= 95
    assert breakdown is not None


def test_low_confidence_hindi_document_refuses_score():
    _, _, (score, breakdown, status) = analyse("hindi_scan.pdf")
    assert status == "human_review_required"
    assert score is None
    assert breakdown is None


def test_vendor_rules_are_traceable():
    _, findings, (_, _, status) = analyse("bilingual_vendor.pdf")
    ids = {finding.rule_id for finding in findings}
    assert status == "review_ready"
    assert {"UNILATERAL_CHANGE", "AUTO_RENEWAL"}.issubset(ids)


def test_decision_brief_produces_actions():
    extraction, findings, _ = analyse("bilingual_vendor.pdf")
    summary, actions = build_decision_brief(extraction, findings)
    assert "high-priority" in summary
    assert any("mutual written consent" in action for action in actions)


def test_event_demo_sample_runs_end_to_end():
    sample = "samples/bilingual_vendor.pdf"
    with open(sample, "rb") as handle:
        response = client.post(
            "/api/analyze",
            files={"file": ("bilingual_vendor.pdf", handle, "application/pdf")},
        )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "review_ready"
    assert payload["model_used"] == "deterministic-demo-fixture"
    assert any(item["evidence"] for item in payload["findings"])


def test_vendor_commercial_terms_are_extracted_with_evidence():
    extraction = demo_extraction("bilingual_vendor.pdf")
    for field_name in [
        "payment_terms", "service_obligations", "confidentiality",
        "intellectual_property", "data_handling", "indemnity", "liability_cap",
    ]:
        field = getattr(extraction, field_name)
        assert field.value
        assert field.evidence is not None
        assert field.confidence >= 0.85


def test_vendor_missing_commercial_protections_trigger_rules():
    extraction = demo_extraction("bilingual_vendor.pdf")
    extraction.liability_cap.value = None
    extraction.liability_cap.confidence = 0.3
    extraction.intellectual_property.value = None
    extraction.intellectual_property.confidence = 0.3
    ids = {finding.rule_id for finding in build_findings(extraction)}
    assert {"LIABILITY_CAP_MISSING", "IP_OWNERSHIP_UNCLEAR"}.issubset(ids)
