# Pactrix Review — MVP product brief

## The story

An Indian startup founder receives a vendor or customer agreement. The commercial team wants to move quickly, the lawyer is not always available, and the important terms are spread across pages of dense text. The immediate problem is not “replace the lawyer.” It is knowing what the business is agreeing to, what needs attention, and what question should be escalated before signature.

Pactrix Review converts that agreement into a traceable decision brief.

## Initial customer

Founder-led Indian startups and MSMEs that review recurring vendor and customer-service agreements without a full-time in-house legal team.

## Job to be done

“Before I approve or send this agreement to counsel, show me the commercial obligations, deadlines, configured review issues, source clauses, and unanswered questions.”

## MVP workflow

1. Upload a synthetic or authorised agreement.
2. Pactrix Core extracts configured fields with clause and page evidence.
3. A strict schema rejects malformed output.
4. Deterministic rules flag only configured patterns.
5. Low-confidence material fields stop the review.
6. The user receives a decision brief and next-action checklist.

## Product boundaries

- It does not determine enforceability.
- It does not replace counsel or issue legal advice.
- It does not generate a person-wide or company-wide legal score.
- The private MVP must not accept confidential customer documents without a reviewed security and retention design.

## Google build-day objective

Prove that Gemini can produce schema-valid, page-grounded extraction on three synthetic English, Hindi, and bilingual agreements, and measure where the pipeline fails.

## Success metrics for the first 30 days

- 15 discovery interviews with founders, finance/operations leads, and lawyers;
- 5 design partners willing to test synthetic or redacted agreements;
- at least 90% exact-field accuracy on the small labelled evaluation set;
- 100% citation presence for every surfaced finding;
- zero confident output on deliberately unreadable material fields;
- evidence that the brief reduces first-pass review time;
- at least 3 design partners willing to pay for a controlled pilot.

## Long-term bridge

Pactrix Review is the wedge. Repeated, permissioned workflows can later support obligation monitoring, clause playbooks, negotiation history, organisation-specific policy checks, APIs, and a broader legal-transaction intelligence layer. Expansion is earned through data quality, workflow adoption, and trust—not claimed in advance.

