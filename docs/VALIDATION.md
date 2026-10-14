# Validation — 14 October 2026

## Live X enhancement — latest results

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
