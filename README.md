# TelyClaw Growth Engine

A runnable, single-user social listening and content opportunity MVP for the TelyClaw Growth Lead challenge. It takes selected account posts through topic detection, explainable ranking, content angles, human editing, approval and text export.

**Status: functional Demo MVP with an optional on-demand Live X adapter, not a completed hiring submission.** Page 7's obscured README line is **Pending recruiter clarification**. The final video must still be recorded. Product positioning needs confirmation.

**Data honesty:** Demo Mode uses six fictional accounts and 48 synthetic posts with synthetic source engagement. Optional Live X mode uses only officially fetched, cached X data; it is disabled by default and has not been exercised against real X in development. There is no automated publishing or measured growth. Local topic detection uses machine learning; default draft generation uses clearly labeled editorial templates, **not an LLM**. An optional OpenAI adapter exists but has not been verified against the real API.

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

Open **http://localhost:8000**. No API keys, Docker, frontend build or database service required. Leave the terminal open. Ctrl+C stops the server. Data persists in `data/growth.db`; restart the app to continue. Keep this database when updating: it preserves saved accounts/drafts and Live request counters. Do not delete or replace it to reset the Live budget.

## Demonstrate the workflow

1. Open **Sources & settings**. Inspect six fictional handles; add/remove accounts or toggle monitoring.
2. In **Opportunities**, keep **Demo Data (synthetic)**, choose **Last 4 hours**, and analyze. Change to **Last 1 hour** and reanalyze to show genuinely filtered data.
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

`app/x_api.py` owns official on-demand X fetching, normalization, caching and persistent spending safeguards; `app/db.py` owns SQLite initialization; `demo.py` owns fictional fixtures; `trends.py` owns detection/ranking; `content.py` owns replaceable draft generation; `main.py` validates data and controls workflow; `app/static/` contains the responsive dashboard. Tests use separate temporary databases.

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

Use recent actual timestamps for a current-window demonstration. Uploads accept up to 1,000 posts; handles are 1–15 letters/digits/underscores, text 1–5,000 characters, engagement nonnegative integers, and dates timezone-aware/not future-dated beyond five minutes. An invalid record rejects the whole batch. Importing the same source ID updates it without multiplying rows. Accounts are added automatically; disabled existing accounts remain disabled. Demo/import IDs are namespaced separately. Live X posts are stored in a separate table and never mixed with demo/import data.

Demo data uses a visible fixed **14 Oct 2026, 10:00 UTC** scenario clock; imports use the actual current time. UI dates display Asia/Shanghai (CST). Data modes never mix. Imported data is user-supplied and unverified; importing is not proof of a live integration. Live X uses current time and only the selected account’s cached posts. No synthetic outcomes are attributed to generated content.

## Manual X Post Import — no API fees

Use this path when you do not want to pay for X API access. You open X yourself and copy the information; the app never scrapes, opens or fetches a pasted URL. No token or X credits are needed.

1. Open **Sources & Settings → Import X Post**.
2. Paste the original HTTPS post URL, the author's handle (with or without `@`), and full post text.
3. Enter its publication date/time in **Asia/Shanghai (UTC+08:00)** as labeled. Convert from the timezone shown by X if necessary. The app stores UTC. Future or timezone-less API timestamps are rejected.
4. Optionally enter likes, reposts and replies as whole numbers. **Blank means unknown (`N/A`); 0 means observed zero.** Missing metrics are never invented, and the existing score excludes unavailable engagement factors and rescales remaining weights.
5. Click **Save Post**. Add more posts one by one, including posts from different accounts. Handles are added to the existing monitored-account list; an already disabled handle stays disabled.
6. In **Opportunities**, select **Manual Imports**, choose **Last 1H / 4H / 24H / 7D**, then **Analyze signals**. Filtering uses publication time, not the time you saved the post. Enable its author in Sources & Settings if a saved post does not appear.
7. Inspect source links, representative-source summaries and score factors. Generate three angles and a draft, edit it, approve it and export text through the unchanged workflow.

Supported links have the form `https://x.com/author/status/123456789`; common `twitter.com`, `www.x.com`, `www.twitter.com` and `mobile.twitter.com` variants are accepted. Tracking parameters/fragments are stripped and links are saved canonically under x.com. The URL's author must match the entered handle. Shortened links and `/i/status/` links are not accepted because they do not contain a checkable author handle; open the post yourself and copy its author-based URL instead. Structural validation does **not** prove the post exists or that the copied details are accurate.

Duplicate checks use the numeric X post ID, even across hostname, tracking-parameter or author-case variants. A duplicate returns a clear message and **does not overwrite** the saved text/metrics. Concurrent duplicate saves are also prevented. There is no source-edit/delete feature in this release; check the fields before saving. Text supports up to 25,000 characters, and optional metrics must be integers from 0 to 100 billion.

The latest 20 manual posts are displayed under the form for verification; all saved posts remain in SQLite and are eligible for analysis if their account is enabled and publication time is in the selected window. Existing posts, drafts, API counters and settings survive this additive database upgrade. Keep your `data/growth.db` when updating.

**Small-sample warning:** fewer than five distinct post texts or fewer than two authors in the selected window triggers a visible warning. Analysis still works so you can demonstrate the full workflow. This threshold is a practical demo heuristic, not statistical proof of a trend. Even larger manually selected samples may be biased or incomplete; all Manual Imports analyses and drafts label the source data as user-supplied and unverified.

| Dashboard mode | Source | Automatic X access? |
|---|---|---|
| Demo Data | Existing synthetic fixtures; fixed scenario clock | No |
| Manual Imports | Posts you copy into the form; current-time windows | No |
| JSON Imports | Existing bulk JSON uploads; current-time windows | No |
| Live X | Separate official API cache; current-time windows | No; explicit enablement and manual fetch required |

No mode silently substitutes another dataset. The same post may intentionally exist in different source modes; uniqueness is enforced within Manual Imports. Live X remains disabled by default. Keep `X_LIVE_ENABLED=false` while using this free manual workflow.

### Reviewing this enhancement locally

Download branch **feat/manual-x-import** as a ZIP from GitHub, or switch an existing checkout to that branch. Stop the old server with Control+C, install `requirements.txt` in your existing virtual environment and restart using the **Run locally** commands. No new dependency was introduced for the manual feature.

### Production monitoring later

The existing official X API adapter could replace manual copying once access and costs are approved: resolve account IDs, retrieve normalized posts and preserve source links/metrics. The current implementation is manual on-demand fetching with caching and caps—not streaming or complete historical coverage. Scheduled ingestion, pagination/checkpoints, retention/deletion handling and broad multi-account coverage would need further work and review of current X access/pricing. Manual records stay separately labeled rather than being presented as API-verified data. None of this is required for today's no-fee workflow.

## Live X monitoring: macOS setup and safe operation

This feature is **on-demand fetching, not streaming**. You can inspect Live mode with **$0 credits**: it will explain missing credentials or disabled fetching without contacting X. Demo remains the default on every page load. Changing modes, inspecting status, analyzing a cache, generating drafts, approving and exporting never trigger an X request.

To update an existing checkout on your Mac, open Terminal in the project folder:

```sh
git fetch origin
git switch feat/manual-x-import
git pull --ff-only origin feat/manual-x-import
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Stop an older server with Control+C first. For a fresh download, select branch **feat/manual-x-import** on GitHub, choose Code → Download ZIP, extract it, and follow **Run locally** above. No Git installation is needed for the ZIP option. Open http://localhost:8000 in Safari/Chrome. Leave Terminal open while reviewing the app.

### Private environment configuration

1. In the project folder, copy `.env.example` to `.env` (`cp .env.example .env`). On macOS, `Command+Shift+.` reveals hidden files in Finder.
2. Edit `.env` locally using a plain-text editor (for example VS Code). Set `X_BEARER_TOKEN` to your saved Bearer Token, without a `Bearer ` prefix. **Never paste it into chat, the dashboard, screenshots or a GitHub issue.** There is no frontend token field.
3. **Keep `X_LIVE_ENABLED=false` while your balance is $0.** Adding the token alone does not enable requests. You can also leave the token blank to review the missing-credentials state.
4. After you separately confirm API access, current endpoint costs and adequate credits with X, set `X_LIVE_ENABLED=true` locally and restart the server. This is your explicit enablement of manual potentially billable reads. The app never purchases credits or initiates a billing transaction.
5. Select **Live X (manual / cached)**. Keep monitored username `elonmusk` and the default five posts. Click **Fetch latest posts** only when you intend to use X API access, then **Analyze signals** to analyze the local cache.

Environment variables are read server-side. `.env` is optional and never overrides an existing shell environment variable. `.env` and `.env.*` are ignored by Git except the sanitized `.env.example`. After changing a shell variable, restarting with a changed `.env` alone may not override that shell value. No token value is returned by the API, stored in SQLite or deliberately logged. Do not enable HTTP debug logging or record your `.env` on screen.

| Variable | Default | Meaning |
|---|---|---|
| `X_BEARER_TOKEN` | empty | Private read-only app token; no request possible when missing |
| `X_LIVE_ENABLED` | `false` | Must be explicitly `true` to allow manual X requests |
| `DATABASE_PATH` | `data/growth.db` | SQLite storage; keep one shared database for consistent request limits |
| `OPENAI_API_KEY` | empty | Existing optional LLM content provider; separate costs/access from X |
| `OPENAI_MODEL` | `gpt-4o-mini` | Existing optional LLM model |

### Implemented X endpoints and data

- `GET https://api.x.com/2/users/by/username/{username}` resolves the account. Successful user IDs are cached for seven days.
- `GET https://api.x.com/2/users/{id}/tweets` requests one page, default `max_results=5` (selectable up to 10), with `created_at,public_metrics,referenced_tweets,author_id`.
- `GET /api/x/status` only inspects local configuration/cache; `POST /api/x/fetch` is the only app operation that can contact X. The account input supports other valid usernames, one account per run.
- Text, source ID, timestamp, original X link, author ID when supplied, reference types and available public metrics are normalized. Original/reply/quote/repost labels are visible; combinations are preserved in the data. A repost is timeline activity, not necessarily an original statement by the monitored person.
- Missing metrics stay `null`/`N/A`, never fabricated zero. If likes/reposts/replies needed for a topic score are incomplete, its engagement factor is excluded and the remaining weights are rescaled. Known zero engagement remains a real zero. The UI shows effective weights and explains the exclusion.
- Live drafts retain original source links and a single-account limitation warning. The existing templates/optional LLM, human editing, approval and export are reused. No automatic X publishing is implemented.

### Cost safeguards

- No X calls on page load, mode switch, analysis, content generation or app startup. No scheduler, polling, streaming connection, pagination or automatic retries.
- A fresh account cache (15 minutes) is reused with **zero** outbound requests, including when credentials have since been removed. Stale caches remain available for analysis but are labeled stale; a failed refresh never becomes demo data.
- Global 10-minute cooldown across usernames/processes. The initial resolution + timeline normally costs **two API requests**; later timeline refreshes normally use one. Failed attempts count toward the budget.
- Persistent hard cap of **10 outbound X HTTP attempts per UTC day**, shared across accounts. First fetch is blocked if fewer than two slots remain and lookup is required. Caps/cooldowns survive app restarts; concurrent refreshes cannot bypass them. A separate/deleted database has separate counters, so do not use multiple database copies to manage one billing account.
- HTTP 429 respects reset/Retry-After headers with a conservative 15-minute minimum wait; a success reporting zero remaining requests also creates a hold. No retry runs automatically. Redirects are disabled so Authorization is not forwarded to another host.
- These are request-count controls, **not a dollar budget or guaranteed free usage**. X may charge per returned resource; five posts can still be billable. Verify current pricing, plan limits and billing in the X Developer portal. The app cannot inspect your credit balance.

### Troubleshooting

| State | What it means / action |
|---|---|
| Missing credentials | Set the private server variable and restart; no X request was made |
| Fetching disabled | Leave it off at $0; confirm access/credits separately before enabling |
| Loading | One explicit fetch is running; button is disabled until it finishes |
| Cached / stale | See last successful fetch time, last response count and unique cached count; analyze without another read |
| 401 authentication | Check/rotate the token privately; old cache is retained |
| 403 access denied | Check app permissions, API plan and endpoint access |
| Payment / insufficient credits | X reported HTTP 402 or a recognized credit restriction; check the portal; the app never buys credits |
| 429 / cooldown / daily cap | Wait until shown retry/reset time; no automatic retry, and cache remains usable |
| Network/service error | Check connection/API availability and retry manually after cooldown; no synthetic substitution |
| Empty response/window | Account has no returned eligible posts, or recent cached posts fall outside your window; try a wider analysis window without refetching |
| Unexpected API response | Cache is preserved; current endpoint/schema access needs checking; no raw provider error text is exposed |

Last successful fetch time does not mean every post in a selected time window was retrieved. The single page may omit older posts even inside the window. With only @elonmusk, these are **account-level content signals, not platform-wide trends**. Broader coverage, complete historical windows, original-author expansion for reposts, full quote bodies, streaming, scheduled monitoring, spending in currency and real publication analytics remain **planned/unimplemented**. Confirm the current official endpoint contract/access before your first funded run; real X was deliberately not contacted during development.

### Interview flow with $0 credits

1. Start in **Demo Data** and demonstrate all existing growth/content features.
2. Switch to **Live X** and show `@elonmusk`, five-post default, missing/disabled credentials, cache/budget fields and the single-account caveat. Explain that switching does not contact X.
3. Keep real fetching disabled. Say: “This integration uses the official API with persistent limits; live success and error paths were tested with mocked responses, without consuming paid credits.”
4. After funded access is separately approved and available, manually fetch, inspect source/type/metrics and links, analyze, draft, review, approve and export. Return to Demo explicitly if desired—there is never an automatic fallback.

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
python tests/live_browser_smoke.py
python tests/manual_browser_smoke.py
node --check app/static/app.js
```

The original browser test uses a temporary database on port 8001; the Live test uses port 8002 and an in-process MockTransport. The manual-form browser test uses port 8003 and blocks non-local browser requests. All three save screenshots under `work/browser/`. Tests default-deny X traffic and blank real service keys; the Live suite uses non-secret placeholders, never actual credentials. Node is only needed for the optional JavaScript syntax check, not to run the app.

## Current limitations and submission status

- Page 7 obscured README requirement: **Pending recruiter clarification**; no text inferred.
- Live X on-demand ingestion is implemented behind explicit enablement, but real endpoint authentication/credits are unverified. X publishing, automatic scheduling and real generated-content performance tracking are not implemented.
- Local English lexical clustering can split a topic, merge unrelated topics, miss synonyms, and does not verify truth or coordination. Exact copies are deduplicated; semantic duplicates are not reliably detected. Keyword titles and local content need editorial polish.
- Optional LLM integration is present but not live-tested; local templates are not equivalent to LLM generation.
- No authentication, tenant separation, team roles, public-hosting hardening or background job infrastructure. Run on localhost for this single-user challenge. Do not expose publicly without those controls and request limits.
- Draft text is editable; angle cards are suggestions rather than independently editable documents. Human edits must substantiate actual product relevance.
- Historical analyses persist internally but there is no trend-history comparison UI or automatic learning from outcomes.
- Professional demo video recording, recruiter clarification, verified product positioning and final submission remain outstanding. No claim of proven 10× growth.

Built with **OpenAI Codex** as the vibe-coding assistant; local NLP uses **scikit-learn**. Optional content generation uses the OpenAI API when explicitly configured. No other AI tools or successful integrations are implied.
