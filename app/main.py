from __future__ import annotations

import os
import uuid
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .extractor import demo_extraction, gemini_extraction
from .models import AnalysisResponse
from .scoring import build_decision_brief, build_findings, calculate_coverage


ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"
SAMPLES = ROOT / "samples"
SCHEMA = ROOT / "schemas" / "legal_document_schema.json"
DISCLAIMER = "Prototype decision-support output—not legal advice or a substitute for a qualified lawyer."
ALLOWED_TYPES = {"application/pdf", "image/png", "image/jpeg", "text/plain"}
MAX_BYTES = 10 * 1024 * 1024

app = FastAPI(title="Pactrix Review", version="0.3.0")
app.mount("/static", StaticFiles(directory=FRONTEND), name="static")
app.mount("/samples", StaticFiles(directory=SAMPLES), name="samples")


@app.get("/")
def home():
    return FileResponse(FRONTEND / "index.html")


@app.get("/health")
def health():
    return {"status": "ok", "mode": "gemini" if os.getenv("USE_GEMINI", "false").lower() == "true" else "demo"}


@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze(file: UploadFile = File(...)):
    mime_type = file.content_type or "application/octet-stream"
    if mime_type not in ALLOWED_TYPES:
        raise HTTPException(415, "Upload a PDF, PNG, JPEG, or TXT file.")
    payload = await file.read()
    if not payload or len(payload) > MAX_BYTES:
        raise HTTPException(413, "File must be between 1 byte and 10 MB.")

    use_gemini = os.getenv("USE_GEMINI", "false").lower() == "true"
    try:
        extraction = gemini_extraction(payload, mime_type, SCHEMA) if use_gemini else demo_extraction(file.filename or "document")
    except Exception as exc:
        raise HTTPException(502, f"Extraction failed: {exc}") from exc

    findings = build_findings(extraction)
    coverage, breakdown, status = calculate_coverage(extraction, findings)
    summary, next_actions = build_decision_brief(extraction, findings)
    return AnalysisResponse(
        analysis_id=str(uuid.uuid4()),
        filename=file.filename or "document",
        status=status,
        review_coverage=coverage,
        coverage_breakdown=breakdown,
        executive_summary=summary,
        next_actions=next_actions,
        extraction=extraction,
        findings=findings,
        disclaimer=DISCLAIMER,
        model_used=os.getenv("GEMINI_MODEL", "gemini-3.7-flash") if use_gemini else "deterministic-demo-fixture",
    )
