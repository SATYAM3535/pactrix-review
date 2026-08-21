# Pactrix Review

The first product prototype from Pactrix Labs: an evidence-grounded agreement review workspace for Indian startups and MSMEs.

> Prototype decision-support output—not legal advice or a substitute for a qualified lawyer.

## Product thesis

Indian businesses routinely accept commercial agreements without a repeatable way to identify obligations, deadlines, unusual terms, or questions that need counsel. Pactrix Review starts with one narrow workflow: convert an agreement into a traceable decision brief before it is signed.

1. extract facts and page-level evidence;
2. validate them against a strict schema;
3. apply visible deterministic rules;
4. withhold the review when material confidence is insufficient; and
5. present a traceable brief with practical next actions.

The model extracts. Code applies visible rules. Low-confidence material fields trigger human verification.

## Architecture

`Agreement → Gemini multimodal extraction → strict schema → deterministic rules → confidence gate → decision brief`

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python scripts/generate_samples.py
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`.

Demo mode is the default and requires no API key. It returns deterministic fixtures based on the uploaded sample filename, allowing the full interface and refusal path to be demonstrated offline.
The interface also includes one-click synthetic samples so the event demo remains usable without file-picker or network friction.

## Enable Gemini

Set environment variables before starting:

```bash
export GEMINI_API_KEY="your-key"
export GEMINI_MODEL="gemini-3.7-flash"
export USE_GEMINI="true"
uvicorn app.main:app --reload
```

The model name is configurable because event-provided/current model access may differ. Do not commit secrets.
`gemini-3.7-flash` is the current default. The backend retries temporary capacity and rate-limit errors up to three times with bounded backoff and caps structured output at 8,192 tokens. Benchmark model changes against the same labelled samples before switching.

Run the real extraction smoke test before opening the web demo:

```bash
python -m scripts.live_gemini_check
```

The command must print `LIVE GEMINI CHECK PASSED` and evidence page numbers. This call uses the Gemini API and is not the offline fixture.

## Review coverage composition

| Component | Maximum |
|---|---:|
| Critical-field completeness | 25 |
| Clause balance and obligations | 25 |
| Financial exposure clarity | 20 |
| Termination and renewal clarity | 15 |
| Jurisdiction and dispute readiness | 10 |
| Extraction confidence | 5 |

Review coverage measures how much of the configured workflow was extracted and checked; it is not a legal-risk or enforceability score. The engine withholds it if overall extraction confidence is below `0.72` or a material field is below `0.50`.

## Current deterministic rules

- missing/unclear termination notice;
- unilateral modification right;
- unclear penalty exposure;
- automatic renewal;
- missing jurisdiction and arbitration path.
- missing payment timing;
- missing liability cap;
- unclear intellectual-property ownership;
- missing confidentiality protection;
- missing data-handling obligations.

These are prototype decision-support checks, not claims about enforceability.

## Evaluation set

- `english_agreement.pdf`: clean, scoreable document;
- `hindi_scan.pdf`: deliberately low-confidence refusal path;
- `bilingual_vendor.pdf`: unilateral-change and auto-renewal findings.
- `pactrix_synthetic_vendor_agreement.pdf`: realistic three-page commercial agreement for the live Gemini path.

All samples are synthetic and contain no real personal or client information.

Run tests:

```bash
pytest -q
```

## Three-hour Google build plan

1. Confirm whether an existing scaffold may be used and disclose it.
2. Validate Gemini structured output and evidence grounding.
3. Replace demo fixtures with real multimodal extraction.
4. Test the three synthetic documents and record field-level errors.
5. Review confidence thresholds with a Google expert.
6. Deploy to Cloud Run using the included container configuration.

## What is intentionally out of scope

- legal advice or enforceability determination;
- a person/company-wide “legal CIBIL score”;
- government-record verification;
- real customer documents;
- production security, authentication, retention, or audit controls;
- universal support for every Indian legal document.

## Founder positioning

“Pactrix Labs is building trusted intelligence for legal transactions in India. Pactrix Review is our first narrow product: it turns an agreement into a traceable decision brief using multilingual extraction, deterministic review rules, evidence grounding, and human escalation.”
