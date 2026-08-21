"""Run one real Gemini extraction without starting the web application."""

from __future__ import annotations

import os
from pathlib import Path

from app.extractor import gemini_extraction


ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "samples" / "pactrix_synthetic_vendor_agreement.pdf"
SCHEMA = ROOT / "schemas" / "legal_document_schema.json"


def main() -> None:
    if not os.getenv("GEMINI_API_KEY"):
        raise SystemExit("GEMINI_API_KEY is missing. Set it in this terminal; never paste it into source code.")
    model = os.getenv("GEMINI_MODEL", "gemini-3.7-flash")
    result = gemini_extraction(SAMPLE.read_bytes(), "application/pdf", SCHEMA)
    print(f"LIVE GEMINI CHECK PASSED | model={model} | confidence={result.extraction_confidence:.2f}")
    for name in [
        "parties", "financial_obligations", "payment_terms", "renewal_terms",
        "unilateral_modification", "liability_cap", "intellectual_property",
        "data_handling", "termination_notice", "jurisdiction",
    ]:
        field = getattr(result, name)
        page = field.evidence.page if field.evidence else "-"
        print(f"{name}: {field.value!r} | confidence={field.confidence:.2f} | page={page}")


if __name__ == "__main__":
    main()
