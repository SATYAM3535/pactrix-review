from __future__ import annotations

from .models import CoverageBreakdown, ExtractionResult, RiskFinding


CONFIDENCE_THRESHOLD = 0.72


def _present(field) -> bool:
    value = field.value
    return value not in (None, "", []) and field.confidence >= 0.55


def build_findings(data: ExtractionResult) -> list[RiskFinding]:
    findings: list[RiskFinding] = []

    if not _present(data.termination_notice):
        findings.append(RiskFinding(
            rule_id="TERM_NOTICE_MISSING",
            title="Termination notice is missing or unclear",
            severity="red",
            explanation="The document does not provide a reliably extractable notice period.",
            evidence=data.termination_notice.evidence,
            confidence=data.termination_notice.confidence,
            requires_human_review=data.termination_notice.confidence < CONFIDENCE_THRESHOLD,
        ))

    if _present(data.unilateral_modification):
        findings.append(RiskFinding(
            rule_id="UNILATERAL_CHANGE",
            title="Possible unilateral modification right",
            severity="red",
            explanation="One party may be able to change terms without equivalent consent from the other.",
            evidence=data.unilateral_modification.evidence,
            confidence=data.unilateral_modification.confidence,
            requires_human_review=data.unilateral_modification.confidence < CONFIDENCE_THRESHOLD,
        ))

    if not _present(data.penalties):
        findings.append(RiskFinding(
            rule_id="PENALTY_UNCLEAR",
            title="Penalty exposure is not clearly defined",
            severity="amber",
            explanation="Penalty or late-payment consequences could not be established confidently.",
            evidence=data.penalties.evidence,
            confidence=data.penalties.confidence,
            requires_human_review=data.penalties.confidence < CONFIDENCE_THRESHOLD,
        ))

    if data.document_type.lower().find("vendor") >= 0 or data.document_type.lower().find("service") >= 0:
        if not _present(data.payment_terms):
            findings.append(RiskFinding(
                rule_id="PAYMENT_TERMS_MISSING", title="Payment timing is missing or unclear", severity="red",
                explanation="The amount may be visible, but a reliable invoice due date was not extracted.",
                evidence=data.payment_terms.evidence, confidence=data.payment_terms.confidence,
                requires_human_review=data.payment_terms.confidence < CONFIDENCE_THRESHOLD,
            ))
        if not _present(data.liability_cap):
            findings.append(RiskFinding(
                rule_id="LIABILITY_CAP_MISSING", title="Liability cap was not identified", severity="red",
                explanation="Potential liability allocation requires human review when no cap can be established.",
                evidence=data.liability_cap.evidence, confidence=data.liability_cap.confidence,
                requires_human_review=True,
            ))
        if not _present(data.intellectual_property):
            findings.append(RiskFinding(
                rule_id="IP_OWNERSHIP_UNCLEAR", title="Intellectual-property ownership is unclear", severity="amber",
                explanation="Ownership of deliverables, tools, and pre-existing material was not established.",
                evidence=data.intellectual_property.evidence, confidence=data.intellectual_property.confidence,
                requires_human_review=True,
            ))
        if not _present(data.confidentiality):
            findings.append(RiskFinding(
                rule_id="CONFIDENTIALITY_MISSING", title="Confidentiality protection is unclear", severity="amber",
                explanation="No reliable confidentiality obligation or survival period was extracted.",
                evidence=data.confidentiality.evidence, confidence=data.confidentiality.confidence,
                requires_human_review=True,
            ))
        if not _present(data.data_handling):
            findings.append(RiskFinding(
                rule_id="DATA_HANDLING_MISSING", title="Data-handling obligations are unclear", severity="amber",
                explanation="Purpose, access controls, or breach-notification duties were not identified.",
                evidence=data.data_handling.evidence, confidence=data.data_handling.confidence,
                requires_human_review=True,
            ))

    if _present(data.renewal_terms):
        renewal = str(data.renewal_terms.value).lower()
        if "automatic" in renewal or "auto" in renewal or "स्वतः" in renewal:
            findings.append(RiskFinding(
                rule_id="AUTO_RENEWAL",
                title="Automatic renewal detected",
                severity="amber",
                explanation="The agreement may renew automatically; verify the opt-out deadline.",
                evidence=data.renewal_terms.evidence,
                confidence=data.renewal_terms.confidence,
                requires_human_review=data.renewal_terms.confidence < CONFIDENCE_THRESHOLD,
            ))

    if not _present(data.jurisdiction) and not _present(data.arbitration):
        findings.append(RiskFinding(
            rule_id="DISPUTE_PATH_MISSING",
            title="Dispute-resolution path is missing",
            severity="amber",
            explanation="Neither jurisdiction nor an arbitration mechanism was extracted reliably.",
            evidence=None,
            confidence=max(data.jurisdiction.confidence, data.arbitration.confidence),
            requires_human_review=True,
        ))

    if not findings:
        findings.append(RiskFinding(
            rule_id="NO_RULE_HIT",
            title="No configured rule triggered",
            severity="green",
            explanation="No risk was detected by this limited prototype ruleset; this is not legal clearance.",
            confidence=data.extraction_confidence,
            requires_human_review=False,
        ))

    return findings


def build_decision_brief(data: ExtractionResult, findings: list[RiskFinding]) -> tuple[str, list[str]]:
    red_count = sum(f.severity == "red" for f in findings)
    amber_count = sum(f.severity == "amber" for f in findings)
    summary = (
        f"Pactrix found {red_count} high-priority and {amber_count} review item(s) "
        f"in this {data.document_type.lower()}. Each finding is limited to the configured "
        "rules and should be checked against the source document."
    )
    actions: list[str] = []
    action_map = {
        "TERM_NOTICE_MISSING": "Confirm the termination notice period before signing.",
        "UNILATERAL_CHANGE": "Negotiate mutual written consent for material changes.",
        "PENALTY_UNCLEAR": "Clarify penalty amounts, triggers, and any applicable cap.",
        "PAYMENT_TERMS_MISSING": "Add an invoice due date and a process for disputed amounts.",
        "LIABILITY_CAP_MISSING": "Ask counsel to review liability allocation and an appropriate cap.",
        "IP_OWNERSHIP_UNCLEAR": "Clarify ownership of deliverables, background IP, and reusable tools.",
        "CONFIDENTIALITY_MISSING": "Add confidentiality scope, exclusions, and survival period.",
        "DATA_HANDLING_MISSING": "Define permitted data use, safeguards, retention, and breach notice.",
        "AUTO_RENEWAL": "Record the renewal opt-out date and responsible owner.",
        "DISPUTE_PATH_MISSING": "Ask counsel to confirm jurisdiction and dispute resolution.",
    }
    for finding in findings:
        if finding.rule_id in action_map:
            actions.append(action_map[finding.rule_id])
    if any(f.requires_human_review for f in findings):
        actions.append("Route low-confidence material fields for human verification.")
    return summary, list(dict.fromkeys(actions)) or ["Review the extracted evidence against the source before proceeding."]


def calculate_coverage(data: ExtractionResult, findings: list[RiskFinding]) -> tuple[int | None, CoverageBreakdown | None, str]:
    critical_fields = [data.parties, data.effective_date, data.expiry_date, data.jurisdiction]
    completeness = round(25 * sum(_present(f) for f in critical_fields) / len(critical_fields))

    clause_balance = 25
    if any(f.rule_id == "UNILATERAL_CHANGE" for f in findings):
        clause_balance -= 15
    if any(f.rule_id == "AUTO_RENEWAL" for f in findings):
        clause_balance -= 5

    financial = 20 if (_present(data.financial_obligations) and _present(data.payment_terms)) else 7
    if any(f.rule_id == "PENALTY_UNCLEAR" for f in findings):
        financial = max(0, financial - 5)

    termination = 15
    if any(f.rule_id == "TERM_NOTICE_MISSING" for f in findings):
        termination -= 10
    if not _present(data.renewal_terms):
        termination -= 3

    dispute = 10 if (_present(data.jurisdiction) or _present(data.arbitration)) else 0
    confidence_points = round(5 * data.extraction_confidence)

    breakdown = CoverageBreakdown(
        critical_field_completeness=max(0, completeness),
        clause_balance_and_obligations=max(0, clause_balance),
        financial_exposure_clarity=max(0, financial),
        termination_and_renewal_clarity=max(0, termination),
        jurisdiction_and_dispute_readiness=max(0, dispute),
        extraction_confidence=max(0, confidence_points),
    )

    material_fields = [data.parties, data.financial_obligations, data.termination_notice, data.jurisdiction]
    low_confidence = data.extraction_confidence < CONFIDENCE_THRESHOLD or any(
        f.confidence < 0.5 for f in material_fields
    )
    if low_confidence:
        return None, None, "human_review_required"

    # A prototype must not imply perfect legal certainty even when no configured
    # rule fires. Production readiness requires broader rules and human review.
    coverage = min(95, sum(breakdown.model_dump().values()))
    return coverage, breakdown, "review_ready"
