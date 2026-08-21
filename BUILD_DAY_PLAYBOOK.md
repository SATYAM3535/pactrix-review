# Google AI Day Build Playbook

## One-line product statement

Pactrix Review turns multilingual business agreements into evidence-grounded decision briefs using multimodal extraction, deterministic rules, confidence gating, and human escalation.

## What Google expects from the build block

The published session is a three-hour “Build with Google AI” block using Google AI Studio and Google Cloud capabilities. Using every available model would be artificial. Use only the technologies that support the product test.

| Google capability | Pactrix use | Event priority |
|---|---|---:|
| Gemini multimodal | Extract structured facts and evidence from scanned documents | Essential |
| Google AI Studio | Test prompts, schema behaviour, and failure cases quickly | Essential |
| Google Cloud Run | Deploy the containerised prototype | Essential |
| Gemma | Discuss private/on-premise extraction experiments | Explore, do not force |
| Antigravity | Use only if the facilitator requires or demonstrates it | Optional |
| Nano Banana | No defensible core use in this prototype | Skip |
| Veo | No defensible core use in legal-document analysis | Skip |
| Lyria | No defensible core use in legal-document analysis | Skip |

Focused tool selection is a product-strength signal. Do not add image/video/music generation merely to show more logos.

## Before entering the room

- Repository runs locally in demo mode.
- Four synthetic documents are present, including a realistic three-page vendor agreement.
- No client or personally identifiable documents are stored.
- `.env` is excluded from version control.
- Gemini API access is tested separately.
- A new Google Cloud project is available, with a spending alert if billing is enabled.
- The laptop can run the local fallback without internet.
- UK travel files and unrelated confidential material are not open on the desktop.

## Ask the facilitator first

“I have an existing non-production scaffold for a legal-document risk engine. May I use it as the starting point and focus this session on Gemini extraction, confidence calibration, evaluation, and Cloud Run deployment?”

If the answer is no, create a fresh event branch or minimal AI Studio prototype and use this repository only as reference.

## Three-hour execution

### 1:00–1:20 — Align

- Confirm rules and expected final demonstration.
- Open the three synthetic samples.
- State one evaluation question: can every material field be grounded to visible evidence with a useful confidence signal?

### 1:20–2:00 — Gemini extraction

- Set `USE_GEMINI=true` and provide the event-approved model name.
- Run the clean English document.
- Inspect JSON validity, parties, money, dates, and evidence quotes.
- Correct the system prompt rather than manually correcting the result.

### 2:00–2:35 — Failure testing

- Run the Hindi and bilingual documents.
- Record false extractions, missing fields, wrong pages, and unsupported evidence.
- Confirm that low confidence results in `human_review_required`.

### 2:35–3:05 — Scoring integrity

- Show that Python—not the LLM—applies the configured commercial-agreement rules.
- Adjust only documented thresholds.
- Preserve the 95-point ceiling and legal disclaimer.

### 3:05–3:35 — Deploy

- Build the provided container.
- Deploy to Cloud Run in `asia-south1` if permitted.
- Do not place a production API key in source code or screenshots.

### 3:35–4:00 — Expert review and presentation

- Ask a Google expert to inspect schema enforcement and evidence grounding.
- Capture three written recommendations.
- Demonstrate one review-ready document and one confidence-gated refusal.

## Ninety-second demonstration

“Most legal AI demos produce a fluent summary. Pactrix Review tests a stricter question: can a business decision-maker see what was extracted, where it came from, what needs attention, and when the system should refuse confidence?

This synthetic bilingual agreement is processed by Gemini for structured fact and evidence extraction. The output passes through a fixed schema, then deterministic rules—not an LLM opinion—identify issues such as unilateral modification and automatic renewal. Every finding shows its source clause and confidence.

Now I’ll upload a deliberately poor Hindi scan. Material fields fall below our threshold, so Pactrix withholds the review and requests human verification. That refusal is a feature. Pactrix Review is the first narrow product within our larger vision for trusted legal-transaction intelligence in India, and it is not legal advice.”

## Questions for Google experts

1. How should field-level confidence be calibrated when the model does not expose a reliable probability for each extracted legal fact?
2. What is the strongest production pattern for schema-valid JSON with page-grounded evidence across scanned multilingual PDFs?
3. For documents that cannot leave a controlled environment, what benchmark should determine Gemini API versus a self-hosted Gemma path?
4. How should we separate OCR error, extraction error, grounding error, and rule-classification error in evaluation?
5. Which Google Cloud controls are essential before processing confidential legal documents: region, retention, logging, IAM, encryption, and abuse monitoring?

## Claims discipline

Say:

- early prototype;
- founder-led validation;
- synthetic evaluation documents;
- deterministic prototype rules;
- discussions with AY Venture;
- decision support, not legal advice.

Do not say:

- Google-validated accuracy;
- legally certified score;
- funded by AY Venture;
- government-data integration already exists;
- production-ready security;
- a CIBIL-equivalent system already built;
- zero hallucination.

## Success criteria before leaving Google

- one Gemini-backed live extraction;
- one confidence-based refusal;
- one Cloud Run deployment or documented deployment blocker;
- one Google expert review;
- three measured failure cases;
- two relevant founder/technical contacts;
- a written next experiment.
