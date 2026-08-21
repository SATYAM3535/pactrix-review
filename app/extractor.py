from __future__ import annotations

import json
import os
import time
from pathlib import Path

from .models import Evidence, ExtractedField, ExtractionResult


SYSTEM_PROMPT = """You are the extraction layer of Pactrix Review, a decision-support prototype for Indian business agreements.
Extract only facts visible in the supplied document and return valid JSON matching the supplied schema.
Never invent missing terms or assess legal enforceability. For every non-null field include a short
verbatim evidence quote and page number. Confidence represents extraction certainty, not legal certainty.
Use null when a field is absent or unreadable. Preserve Hindi evidence in its original script."""


def _field(value=None, confidence=0.0, quote=None, page=1):
    return ExtractedField(
        value=value,
        confidence=confidence,
        evidence=Evidence(quote=quote, page=page) if quote else None,
    )


def demo_extraction(filename: str) -> ExtractionResult:
    name = filename.lower()
    if "hindi" in name:
        return ExtractionResult(
            document_type="किराया अनुबंध / Rental agreement",
            language="Hindi",
            parties=_field(["अनिल कुमार", "सीमा देवी"], .90, "अनिल कुमार और सीमा देवी के बीच", 1),
            effective_date=_field("01-09-2026", .86, "दिनांक 01-09-2026 से", 1),
            expiry_date=_field(None, .38),
            financial_obligations=_field("₹18,000 monthly rent; ₹36,000 deposit", .88, "मासिक किराया ₹18,000 तथा जमा ₹36,000", 1),
            payment_terms=_field("Monthly rent; due date unclear", .58, "मासिक किराया ₹18,000", 1),
            service_obligations=_field(None, .30),
            termination_notice=_field(None, .42),
            renewal_terms=_field("Automatic renewal / स्वतः नवीनीकरण", .78, "अनुबंध स्वतः अगले 11 माह के लिए नवीनीकृत होगा", 2),
            jurisdiction=_field(None, .35),
            arbitration=_field(None, .31),
            unilateral_modification=_field(None, .62),
            penalties=_field("Late fee mentioned but amount unreadable", .48, "विलंब शुल्क ...", 2),
            confidentiality=_field(None, .35),
            intellectual_property=_field(None, .35),
            data_handling=_field(None, .35),
            indemnity=_field(None, .35),
            liability_cap=_field(None, .35),
            missing_information=["expiry_date", "termination_notice", "jurisdiction", "penalty_amount"],
            extraction_confidence=.66,
        )
    if "vendor" in name or "bilingual" in name:
        return ExtractionResult(
            document_type="Vendor services agreement",
            language="English + Hindi",
            parties=_field(["Pragati Retail Pvt Ltd", "Nova Services LLP"], .96, "between Pragati Retail Pvt Ltd and Nova Services LLP", 1),
            effective_date=_field("15-08-2026", .95, "Effective Date: 15 August 2026", 1),
            expiry_date=_field("14-08-2027", .92, "continues until 14 August 2027", 1),
            financial_obligations=_field("₹2,40,000 per quarter", .94, "Quarterly service fee: INR 2,40,000", 2),
            payment_terms=_field("Invoices payable within 30 days", .93, "Invoices are payable within thirty days", 2),
            service_obligations=_field(["Catalogue operations", "Weekly reports", "Campaign support"], .90, "operate the Customer's online catalogue, prepare weekly performance reports", 1),
            termination_notice=_field("30 days", .91, "terminated by either party with 30 days' written notice", 2),
            renewal_terms=_field("Automatic annual renewal unless 15 days notice", .90, "automatically renews unless notice is given 15 days before expiry", 2),
            jurisdiction=_field("Bengaluru, Karnataka", .93, "courts at Bengaluru shall have exclusive jurisdiction", 3),
            arbitration=_field("Sole arbitrator seated in Bengaluru", .89, "sole arbitrator; seat shall be Bengaluru", 3),
            unilateral_modification=_field("Customer may modify service levels by email", .87, "Customer may modify service levels by email", 2),
            penalties=_field("2% monthly late fee", .92, "late fee of 2% per month", 2),
            confidentiality=_field("Mutual confidentiality; survives 3 years", .91, "These obligations survive for three years after termination", 1),
            intellectual_property=_field("Customer owns paid final reports; provider retains methods and software", .90, "Service Provider retains its general methods, templates, software and know-how", 2),
            data_handling=_field("Purpose limitation, access restriction and breach notification", .89, "process business contact and catalogue data only for providing the Services", 2),
            indemnity=_field("Mutual third-party indemnity for fraud, misconduct and IP infringement", .88, "Each party shall indemnify the other against third-party claims", 2),
            liability_cap=_field("Six months of fees, with stated carve-outs", .90, "aggregate liability shall not exceed the fees paid or payable during the six months", 2),
            missing_information=[],
            extraction_confidence=.92,
        )
    return ExtractionResult(
        document_type="Rental agreement",
        language="English",
        parties=_field(["Asha Mehta", "Rohan Verma"], .97, "This Agreement is made between Asha Mehta and Rohan Verma", 1),
        effective_date=_field("01-09-2026", .96, "commencing on 1 September 2026", 1),
        expiry_date=_field("31-07-2027", .94, "ending on 31 July 2027", 1),
        financial_obligations=_field("₹25,000 monthly rent; ₹75,000 deposit", .96, "monthly rent of INR 25,000 and security deposit of INR 75,000", 1),
        payment_terms=_field("Monthly rent", .82, "monthly rent of INR 25,000", 1),
        service_obligations=_field(None, .40),
        termination_notice=_field("60 days", .93, "60 days' written notice", 2),
        renewal_terms=_field("Renewal by mutual written consent", .90, "renewed only by mutual written consent", 2),
        jurisdiction=_field("Bengaluru", .91, "courts in Bengaluru", 2),
        arbitration=_field(None, .73),
        unilateral_modification=_field(None, .84),
        penalties=_field("₹1,000 per day for delayed handover", .90, "INR 1,000 per day for delayed handover", 2),
        confidentiality=_field(None, .62),
        intellectual_property=_field(None, .62),
        data_handling=_field(None, .62),
        indemnity=_field(None, .62),
        liability_cap=_field(None, .62),
        missing_information=[],
        extraction_confidence=.92,
    )


def gemini_extraction(file_bytes: bytes, mime_type: str, schema_path: Path) -> ExtractionResult:
    from google import genai
    from google.genai import types

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured")

    # Keep the checked-in JSON schema as a language-neutral contract and use
    # the Pydantic model as the SDK-enforced response schema.
    json.loads(schema_path.read_text(encoding="utf-8"))
    client = genai.Client(api_key=api_key)
    model = os.environ.get("GEMINI_MODEL", "gemini-3.7-flash")
    max_attempts = max(1, min(5, int(os.environ.get("GEMINI_MAX_ATTEMPTS", "3"))))
    response = None
    for attempt in range(1, max_attempts + 1):
        try:
            response = client.models.generate_content(
                model=model,
                contents=[
                    SYSTEM_PROMPT,
                    types.Part.from_bytes(data=file_bytes, mime_type=mime_type),
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=ExtractionResult,
                    # Gemini 3.7 Flash uses dynamic thinking; deprecated
                    # sampling parameters are intentionally omitted.
                    max_output_tokens=8192,
                ),
            )
            break
        except Exception as exc:
            retryable = getattr(exc, "status_code", None) in {429, 500, 502, 503, 504} or any(
                marker in str(exc) for marker in ("429", "500", "502", "503", "504", "UNAVAILABLE", "high demand")
            )
            if not retryable or attempt == max_attempts:
                if retryable:
                    raise RuntimeError(
                        f"Gemini capacity is temporarily unavailable after {max_attempts} attempts. "
                        "Wait briefly and retry, or switch to offline demo mode."
                    ) from exc
                raise
            time.sleep((2, 5, 9, 14)[attempt - 1])
    if response is None:
        raise RuntimeError("Gemini returned no response")
    return ExtractionResult.model_validate_json(response.text)
