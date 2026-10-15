# Validation — 15 October 2026

## Semantic topics and bilingual interface — latest results

Branch: `feat/semantic-topics-bilingual-ui`, based on merged main `405ee72` (PRs #1–#4).

- **106 pytest tests passed, one existing FastAPI TestClient dependency deprecation warning**. Baseline before editing: 96 passing tests. Ten new semantic tests cover paraphrases across five AI themes, generic-term non-merges, conflicting concrete concerns under a broad multi-agent label, case-insensitive account breadth, unknown metrics, evidence-driven cluster counts/order, and specific editorial fit.
- Five browser scripts passed: original MVP, Manual Imports, mocked Live X, growth loop and bilingual workflow. All use isolated temporary databases. Chinese defaults, English round-trip persistence, untranslated source text (including a source literally equal to a UI key), preserved unsaved draft/import/publishing/metric values, duplicate error localization, human approval, export, encoded composer destination, publication and cumulative metrics are exercised.
- Chinese desktop screenshots were inspected across all four pages; English desktop/mobile regressions remain covered. No horizontal page overflow or browser JavaScript errors in the completed runs. Syntax checks for all three JavaScript files, Python compilation and Git whitespace checks pass.
- No schema changes or database migration; no existing source, draft, analysis, publication or measurement rows are rewritten. Language choice is browser-only. Existing SQLite restart/preservation tests pass.
- Original X text, author handles, URLs, configured brand brief, generated angle ideas and draft/publication text are intentionally not translated. Domain labels and UI narratives are presentation translations. Unknown-domain keywords and developer API docs can remain English.

No real X/LLM requests, paid credits, billing actions or automatic/public publishing. The user's private ten-post dataset is not present: actual improvement on those posts must be reviewed locally with a fresh analysis. The local vocabulary is an explainable heuristic, not embeddings, LLM clustering, statistical independence or platform-wide trend proof. Recruitment clarification/video remain outstanding.

## Growth Intelligence and Content Execution — previous results

Branch: `feat/growth-intelligence-loop`, based on merged main `920bfb8` (includes PRs #1–#3).

- **96 pytest tests passed, 1 existing TestClient dependency deprecation warning**. The previous 77 tests remain, with scoring assertions intentionally updated for unknown-factor exclusion instead of fabricated neutral momentum.
- Four browser scripts exercise the original MVP, Manual Imports, mocked Live mode and the new full growth loop, with successful local server startup and desktop/mobile checks. The new script uses an isolated database and ephemeral localhost port; composer navigation is fulfilled locally with a test-only page before any external request can be sent.
- Test-only fixtures containing nine discussions across three themes cluster into three coherent topics. An unrelated singleton remains separate. This does not claim a measured result on the user's ten real local posts, which were not assumed present.
- Topics have data-derived names, multi-document summaries with attributed central excerpts, evidence/account counts, source engagement coverage, explicit historical sufficiency and three decision explanations. Zero and missing metrics are tested separately; a viral singleton's engagement-quality factor is damped.
- Sufficient historical fixtures produce the expected observed sample change; a sparse baseline or one-author baseline leaves momentum null and its weight zero. Two/all four monitoring windows remain covered by regression tests.
- Source-conditioned local generation and mocked optional LLM generation are tested, including three required angles, distinct topic outputs, length constraints and rejection of a substantial copied source passage. No real LLM call occurred.
- Publication tests cover approval gating, encoded web intent, no publication side effect from opening the composer, URL/time validation, duplicate records, immutable text, revisions and preserved TXT export.
- Performance tests cover honest empty/unknown values, partial metrics, zero impressions, post/topic aggregates, paired-denominator rates, measurement history, latest-snapshot-only sums, timestamp validation, persistence and guarded follower attribution.
- JavaScript syntax, Python compilation and Git diff checks pass. Source/import tables and existing records are never rewritten by the additive two-table migration. Existing manual-post persistence/restart tests still pass.

**No real X/LLM requests, paid credits, billing actions or public posts were used.** Browser fixture URLs and metrics are test-only; screenshots are validation artifacts, not real growth results.

Not verified: the user's local real-post clustering result; actual external X composer rendering (the intent destination is validated/intercepted); real API access; real follower attribution, performance or causal lift. English local clustering, deterministic editorial templates, conservative ASCII/no-URL export constraints and manual/unverified metrics remain documented limitations. Cross-analysis topic taxonomy reconciliation and automatic outcome-driven learning are not implemented.

## Manual X Post Import — previous results

Branch: `feat/manual-x-import`, based on merged main `22f59b6` (includes PRs #1 and #2).

- **77 tests passed, 1 existing dependency deprecation warning**; final full pytest run: 2.29s. This includes all 45 previous tests plus 32 manual-import cases.
- **Manual browser smoke passed**: form saves from multiple accounts, duplicate rejection without overwriting, unknown versus zero counts, sparse warning, source attribution, three angles, editable draft, human approval, actual text export, persisted posts after reload and 390px mobile layout. Browser external-request interception recorded zero external requests; the X request ledger stayed at zero.
- **Original MVP browser smoke passed**, preserving Demo, accounts, JSON upload, editing/approval/export, persistence and desktop/mobile behavior.
- **Mocked Live browser smoke passed**, preserving live mode, cache/error states and content workflow without contacting X.
- JavaScript syntax and Python compilation passed. All three browser servers started successfully against isolated SQLite databases.
- Visually reviewed the Manual Imports dashboard and mobile form screenshots. Test post text is explicitly marked TEST INPUT; no sample fixture is presented as fetched real data.
- No scraping, paid X requests, real LLM requests or publishing occurred. Live enablement and limits were not changed; default remains disabled.

Manual tests cover URL/author validation, canonical duplicate IDs across URL variants and concurrent saves, blank/oversized text, future/naive dates, invalid metrics, nullable and observed-zero metrics, SQLite restart persistence, enabled-account filtering, all four time windows, source-mode isolation, unique-text/account sample warnings, score handling, multiple topics and the review/export workflow.

Limitations: manually entered text/authors/dates/metrics are not verified against X; small-sample thresholds are heuristics; source editing/deletion is not implemented. Publication input is explicitly UTC+08:00. Existing original-source character limits for generated-post export and unverified brand positioning remain. The official API remains an optional future production source requiring approved access/credits, not part of this free import path.

## Live X enhancement — previous results

Branch: `feat/live-x-monitoring`, based on merged main `f13eaec`.

- **45 tests passed, 1 dependency deprecation warning** (`python -m pytest -q`, final run 1.87s). Original minimum-acceptance behavior remains covered.
- Original desktop/mobile browser smoke test **passed**, extended to check Live missing-credential state, zero-post Live analysis and return to Demo.
- Mocked Live browser smoke test **passed**: no auto-fetch, five-post default, cache reuse, original source links/type labels, N/A engagement, three angles, approval/export, credit error preserving stale cache, mobile layout and Demo/Live isolation.
- JavaScript syntax check and Python compilation **passed**. Both browser tests started Uvicorn successfully and exercised real local HTTP endpoints on isolated test databases.
- Reviewed screenshots of the Live panel, score explanation and credit error state. Mock post text explicitly says MOCK TEST DATA. Screenshots are test artifacts, not claims of live X results.
- **Zero real X or OpenAI requests; no paid API credits consumed or billing actions initiated.** X calls use HTTPX MockTransport. The test default denies the X client unless a mock is installed. Non-secret placeholders are used instead of actual credentials.
- `.env` and `.env.local` are ignored; the only intended tracked environment file is sanitized `.env.example`. Credentials are not returned or persisted by the X adapter. Cross-origin browser fetches are rejected.

Coverage includes normalization of original/reply/quote/repost and combined flags; missing and known-zero metrics; missing/disabled credentials; official endpoint/limit construction; 401/403/402/404/429/5xx; recognized credit restrictions; network and malformed responses; absolute reset and seconds/HTTP-date Retry-After; zero remaining quota; cache/ID TTL, deduplication/metric updates, global cooldown, UTC daily cap, concurrent refreshes, restart persistence, additional usernames, mode isolation, scoring and old-database preservation.

Real endpoint authorization, current API plan/credit availability, actual X payloads and optional real LLM generation remain **intentionally unverified**. No streaming, auto-publishing, scheduling or measured growth is implemented. See [LIVE_X.md](LIVE_X.md) and README for operation and limitations.

---

## Original MVP baseline (historical)


Status: functional local MVP validated; final hiring submission remains open.

## Automated checks

- **9 API/integrity tests passed** on Python 3.12 with isolated SQLite databases.
- **Chromium browser smoke test passed** on a 1440px desktop viewport and 390px mobile viewport: analysis, changing time windows, three angles, draft editing, approval, actual text download, approval revocation, account creation, JSON upload, imported-data analysis and persistence after reload. No browser JavaScript errors; mobile has no horizontal page overflow.
- **JavaScript syntax check passed** using `node --check app/static/app.js`.
- Uvicorn started successfully; `/`, local assets, API endpoints and browser workflow were exercised over localhost.
- Dashboard screenshot was visually inspected for layout and readable source/score explanations. Browser captures are generated into ignored `work/browser/` by the smoke script.

One dependency deprecation warning: FastAPI's current TestClient warns that its HTTPX integration will change. The test assertions pass; this is not an application startup failure.

## Acceptance mapping

| Requirement | Evidence |
|---|---|
| ≥5 configurable accounts | Six seeded fictional handles; API account filter/persistence test; browser adds handle |
| ≥2 windows | 1h, 4h, 24h and 7d tests assert increasing eligible post counts |
| Fetch/import selected-period posts | JSON upload tested in API and browser; actual timestamp/window filtering; no live-fetch claim |
| Multiple topics and summaries | Tests assert ≥3 topics across windows and evidence/summary presence |
| Explainable ranking and top trends | Weighted-score equality, relevance gate and non-relevant football exclusion asserted; factors visible in UI |
| ≥3 angles | API checks three distinct categories; browser checks three cards |
| ≥1 publication-ready post | Generated local text within 280-character allowance; browser edits/approves/exports actual post text |
| Human review/approval | Unapproved export rejected; approved export succeeds; editing revokes approval |
| End-to-end usable UI | Full browser sequence plus desktop/mobile layout check |
| Documentation | Phase1, README, demo script, this report; unknown p.7 line retained explicitly |

## Not validated or not implemented

- No live X credentials, fetch, write access, publishing, scheduled monitoring or analytics integration.
- No real OpenAI request: optional provider uses structured-output checks; provider failure behavior is tested with a stub, not a real connection.
- No real engagement or reach outcomes, baseline lift experiment, conversion attribution or 10× growth proof.
- No human brand/editorial acceptance study. Local keyword clustering and templates need evaluation on real customer data.
- No public deployment, authentication/team-role testing or production load/security validation.
- Windows/macOS startup instructions are supplied but only Linux/Python 3.12 was exercised.
- Page-7 clarification and the actual 3–5 minute recorded video remain outstanding.

## How to rerun

Install `requirements-dev.txt`, run `python -m pytest -q`, then `python tests/browser_smoke.py` with Chromium installed. Browser test uses temporary storage and port 8001. Default runtime port 8000 does not need to be stopped. Tests do not call real X/OpenAI services.
