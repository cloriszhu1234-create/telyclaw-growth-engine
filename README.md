# TelyClaw Growth Engine

A runnable, single-user social listening and content opportunity MVP for the TelyClaw Growth Lead challenge. It takes selected account posts through topic detection, explainable ranking, content angles, human editing, approval and text export.

**Status: functional offline MVP, not a completed hiring submission.** Page 7's obscured README line is **Pending recruiter clarification**. The final video must still be recorded. Product positioning needs confirmation.

**Data honesty:** Demo Mode uses six fictional accounts and 48 synthetic posts with synthetic source engagement. There is no live X connection, automated publishing or measured growth. Local topic detection uses machine learning; default draft generation uses clearly labeled editorial templates, **not an LLM**. An optional OpenAI adapter exists but has not been verified against the real API.

## Run locally

Requires Python 3.11+ (tested with 3.12). From this repository:

```sh
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows PowerShell instead: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open **http://localhost:8000**. No API keys, Docker, frontend build or database service required. Leave the terminal open. Ctrl+C stops the server. Data persists in `data/growth.db`; restart the app to continue. To start a completely fresh personal demo, stop the app and remove that database (this deletes saved accounts/imports/drafts).

## Demonstrate the workflow

1. Open **Sources & settings**. Inspect six fictional handles; add/remove accounts or toggle monitoring.
2. In **Opportunities**, keep **Synthetic demo**, choose **Last 4 hours**, and analyze. Change to **Last 1 hour** and reanalyze to show genuinely filtered data.
3. Select a ranked trend. Inspect score factors, keyword matches, distinct authors, representative-source summary and source-post evidence. Off-topic football remains visible with a low-relevance flag, outside the top recommendations.
4. Choose **Create angles & draft**. The studio shows Opinion, Educational and Product angles plus a suggested X post.
5. Edit the post, save and approve. Only approved text can be exported. Changing it revokes approval. Export is a text download for manual publishing, never a claim that an X post was published.
6. Reload to demonstrate persistence. Qualified engagement remains **Not measured** because generated content has not been published or measured.

See [the 3–5 minute video script](docs/DEMO.md), [full Phase 1 plan and page-referenced checklist](docs/PHASE1.md), and [validation report](docs/VALIDATION.md).

## Architecture and product logic

```text
Browser: HTML + CSS + JavaScript
            ↓ same-origin JSON API
FastAPI: accounts / import / analysis / drafts / approval / export
            ↓                   ↓
SQLite persistence      scikit-learn local NLP
                                ↓
                     Local templates or optional OpenAI
```

`app/db.py` owns SQLite initialization; `demo.py` owns fictional fixtures; `trends.py` owns detection/ranking; `content.py` owns replaceable draft generation; `main.py` validates data and controls workflow; `app/static/` contains the responsive dashboard. Tests use separate temporary databases.

Accounts, posts, analysis evidence snapshots, brand settings and drafts are persisted. Exact duplicates are removed during topic analysis, not from the stored raw dataset. An analysis stores its original brief and data context so later configuration changes do not silently rewrite an existing draft's rationale. Editing approved draft text clears its approval.

## Detection and opportunity scoring

TF-IDF turns words/phrases into numerical features; agglomerative cosine-similarity clustering groups related posts across accounts. Topics receive keyword-based titles and an **extractive summary** taken from the most representative source post. Summaries are not independently verified facts. Empty/stopword-only input safely returns no topics.

Each factor is 0–100. The final score is the weighted sum:

| Factor | Weight | Definition |
|---|---:|---|
| Relevance | 30% | Number of matched brand keywords × 25, capped at 100 |
| Independent accounts | 20% | Distinct authors after exact-text deduplication / 5, capped |
| Engagement | 15% | Log-scaled source likes + 2×reposts + 2×replies, cap at reference 2,000 |
| Freshness | 15% | Time since newest evidence relative to selected window |
| Momentum | 10% | Current unique-post count vs matching prior equal-window count; neutral 50 when no prior matches |
| Evidence depth | 10% | Unique posts / 5, capped; a content-opportunity proxy |

Momentum uses prior-window similarity ≥0.22 to the current topic centroid; clustering distance threshold is 0.78. Prior/current text is deduplicated. With a baseline, momentum factor = clamp(50 + percentage change / 4, 0, 100). Without one, growth is shown as unknown, never infinity. These are demo heuristics, not calibrated forecasts.

The top three are relevance-gated: a topic with no brand keyword match cannot enter recommendations, even if it has high raw engagement. Remaining topics stay inspectable. Scores explain prioritization; they do not predict conversions. Brand keywords and positioning are editable. Actual TelyClaw capabilities and ICP were not provided, so the default brief is explicitly provisional.

## Content generation and review

Offline generation produces three differentiated angle suggestions and one original editorial draft. It adds a customer question, human judgment and qualified-engagement perspective rather than copying the source post. These local templates are reliable but repetitive; editorial quality and actual product fit require human review.

Optional generative AI: set `OPENAI_API_KEY` in your server environment and optionally `OPENAI_MODEL` (default `gpt-4o-mini`), then restart. The server calls OpenAI's chat completions endpoint with the topic evidence and brand brief, validates structured output and labels the provider on the draft. A configured-provider failure is explicit; it never silently masquerades as a successful LLM call. Source text is treated as untrusted evidence in the prompt. Network access and billing must be configured outside the app. **Real OpenAI calls are untested in this environment.** Never commit keys or put them in browser code.

Approval/export currently supports **1–280 ASCII characters without URLs**. This deliberately avoids claiming full X weighted-character counting or URL handling. Unicode or URL drafts need editing before approval. Approval is a local single-user action, not an authenticated team audit workflow.

## Import real or sample posts

In **Sources & settings**, upload JSON shaped as:

```json
{
  "posts": [
    {
      "id": "unique-source-post-id",
      "handle": "your_account",
      "text": "AI agents need human review and useful customer feedback.",
      "created_at": "2026-10-14T08:00:00Z",
      "likes": 12,
      "reposts": 3,
      "replies": 2
    }
  ]
}
```

Use recent actual timestamps for a current-window demonstration. Uploads accept up to 1,000 posts; handles are 1–15 letters/digits/underscores, text 1–5,000 characters, engagement nonnegative integers, and dates timezone-aware/not future-dated beyond five minutes. An invalid record rejects the whole batch. Importing the same source ID updates it without multiplying rows. Accounts are added automatically; disabled existing accounts remain disabled. Demo/import IDs are namespaced separately.

Demo data uses a visible fixed **14 Oct 2026, 10:00 UTC** scenario clock; imports use the actual current time. UI dates display Asia/Shanghai (CST). Data modes never mix. Imported data is user-supplied and unverified; importing is not proof of a live integration. No synthetic outcomes are attributed to generated content.

## Production X acquisition plan

Implement an official-X adapter only after verifying current API plan, timeline permissions, account IDs, pricing and retention obligations. Fetch selected accounts with pagination/checkpoints, normalize UTC timestamps, upsert post IDs, respect rate-limit headers, retry transient failures with backoff, and expose ingestion freshness/errors. Schedule server-side pulls only once this adapter works. Write/publishing and analytics permissions are separate. No scraper or fabricated live connection is included.

## Growth measurement

The assignment's proposed North Star is **Qualified Engagement Generated from Trends** (p.6). Its MVP proxy is **Qualified Engagement per Trend-generated Post**. Define audience qualification and eligible events with TelyClaw before aggregating replies, reposts, bookmarks, profile visits, qualified followers or product clicks; disclose missing fields and avoid double-counting when identity/attribution is available.

Supporting metrics: detection lead time, trend-to-content time (suggested target under 5–10 minutes), trend hit rate, content acceptance rate, engagement lift and qualified engagement. The dashboard deliberately does not fabricate these results. Approval alone is not external publication or proof a draft needed no major edits. [Phase 1](docs/PHASE1.md) includes the proposed 90-day growth loop and 10× qualified-reach experiment plan.

## Tests

```sh
python -m pip install -r requirements-dev.txt
python -m pytest -q
# Browser smoke check; requires Chromium:
# Linux default: /usr/bin/chromium
# Or set CHROMIUM_PATH to your installed executable.
python tests/browser_smoke.py
node --check app/static/app.js
```

The browser test starts its own temporary-database server on port 8001, checks desktop/mobile workflow and saves screenshots under `work/browser/`. Node is only needed for the optional JavaScript syntax check, not to run the app.

## Current limitations and submission status

- Page 7 obscured README requirement: **Pending recruiter clarification**; no text inferred.
- No live X ingestion, X publishing, automatic scheduling, or real generated-content performance tracking.
- Local English lexical clustering can split a topic, merge unrelated topics, miss synonyms, and does not verify truth or coordination. Exact copies are deduplicated; semantic duplicates are not reliably detected. Keyword titles and local content need editorial polish.
- Optional LLM integration is present but not live-tested; local templates are not equivalent to LLM generation.
- No authentication, tenant separation, team roles, public-hosting hardening or background job infrastructure. Run on localhost for this single-user challenge. Do not expose publicly without those controls and request limits.
- Draft text is editable; angle cards are suggestions rather than independently editable documents. Human edits must substantiate actual product relevance.
- Historical analyses persist internally but there is no trend-history comparison UI or automatic learning from outcomes.
- Professional demo video recording, recruiter clarification, verified product positioning and final submission remain outstanding. No claim of proven 10× growth.

Built with **OpenAI Codex** as the vibe-coding assistant; local NLP uses **scikit-learn**. Optional content generation uses the OpenAI API when explicitly configured. No other AI tools or successful integrations are implied.
