# US Delivery Internship Technical Task

Production-style AI tooling for support triage and TAM account preparation. The implementation is fully local and deterministic by default: it uses synthetic mock data, TF-IDF retrieval over local Markdown knowledge-base docs, structured Pydantic outputs, and rule-based quality gates. No external data is used.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m ai_support_tam.cli generate-data
```

## Task 1: Ticket Triage

Callable function:

```python
from ai_support_tam.triage import triage_ticket

triage_ticket({
    "subject": "Webhook 429",
    "body": "Our API endpoint returns 429 during a production launch."
})
```

CLI sample:

```bash
python -m ai_support_tam.cli triage --subject "SSO login loop" --body "All users cannot access the app after SAML metadata rotation."
```

REST API:

```bash
pip install -r requirements-demo.txt
uvicorn ai_support_tam.api:app --reload
```

Then call `POST /triage` with `{ "subject": "...", "body": "..." }`.

## Task 2: TAM Account Brief

Callable function:

```python
from ai_support_tam.tam_brief import build_account_brief

build_account_brief("ACCT-001")
```

CLI sample:

```bash
python -m ai_support_tam.cli brief ACCT-001
```

The output is deterministic for the same input because generation is rule-based, sorted, and capped consistently. If an LLM provider is later added, keep `temperature=0`, pin prompt versions in `prompts/`, and preserve post-processing sort order.

## Task 3: Evaluation Harness

Run:

```bash
python -m ai_support_tam.cli eval --output eval_report.json
```

The harness includes five triage tests and five account-brief tests. Each task includes an adversarial case: an ambiguous ticket for triage and a missing account ID for account briefs. Scoring reports pass/fail plus a 0-1 quality score per case.

## Bonus Features

- Thin Streamlit UI:

```bash
pip install -r requirements-demo.txt
streamlit run app.py
```

- GitHub Actions CI runs the eval harness on every push and pull request.
- Prompt versioning lives in `prompts/triage_v1.md` and `prompts/account_brief_v1.md`.

## Design Note

This solution is intentionally conservative: it behaves like a production AI pipeline while staying runnable without a secret key. The triage path accepts raw text or structured subject/body input, retrieves local knowledge-base documents, classifies product area and category, assigns urgency, recommends a responder team, and emits a draft first response as structured JSON. The TAM path accepts an account ID, joins account summary data with the last 90 days of tickets, flags churn or escalation language with direct quotes, and returns a concise brief.

The first failure mode is misclassification. Keyword-heavy routing can miss novel phrasing or over-weight a noisy word such as "dashboard" when the real issue is an API outage. I would detect this with eval drift, agent feedback buttons, and weekly confusion-matrix reviews against resolved-ticket metadata. Mitigation would combine richer embeddings, human override capture, and prompt/rule updates tracked by version.

The second failure mode is retrieval mismatch. A ticket may surface a knowledge-base article that shares vocabulary but not root cause. I would detect this by logging retrieval scores, doc click-through, and responder edits to the suggested article. Mitigation would require a minimum confidence threshold, top-k alternatives, and article-level metadata such as product, severity, and last-reviewed date.

The third failure mode is weak risk synthesis for TAMs. Churn risk often appears indirectly, so a deterministic phrase list may miss softer signals like declining usage or sponsor turnover. I would detect this by comparing generated briefs with TAM-edited QBR notes and renewal outcomes. Mitigation would add structured usage signals, CRM fields, and an LLM judge for borderline risk language while retaining direct quotes for auditability.

The main latency versus quality trade-off is local deterministic retrieval/classification instead of calling a large model for every step. This is faster, cheaper, and easier to test, but less semantically flexible than a high-quality LLM summarizer. If latency were the hard constraint, I would pre-compute ticket and KB embeddings, cache account briefs until new ticket activity arrives, and skip draft response generation for low-priority tickets.

For data sensitivity, the default system sends nothing outside the process. The `.env.example` is optional, and no credentials are required. In a hosted version, I would redact obvious PII before provider calls, use tenant-scoped access controls, disable prompt logging for sensitive fields, and store only structured traces needed for evals and debugging.

At 10x ticket volume, the first bottleneck would be repeated in-process loading and vectorization of the knowledge base and JSON files. The current approach is fine for the mock dataset but should move to a persistent database, background embedding jobs, and an indexed vector store. The eval harness would also need sampled regression suites plus nightly full runs so quality gates stay fast enough for CI.
