# TelyClaw Growth Engine

A runnable, single-user social listening and content opportunity MVP for the TelyClaw Growth Lead challenge. It takes selected account posts through topic detection, explainable ranking, content angles, human editing, approval, manual publication and measured outcomes.

**Status: functional Demo MVP with an optional on-demand Live X adapter, not a completed hiring submission.** Page 7's obscured README line is **Pending recruiter clarification**. The final video must still be recorded. Product positioning needs confirmation.

**Data honesty:** Demo Mode uses six fictional accounts and 48 synthetic posts with synthetic source engagement. Optional Live X mode uses only officially fetched, cached X data; it is disabled by default and has not been exercised against real X in development. There is no automated publishing or bundled growth result. Performance records contain only the publication confirmations and metric snapshots you manually enter. Local topic detection uses machine learning; default draft generation uses clearly labeled editorial templates, **not an LLM**. An optional OpenAI adapter exists but has not been verified against the real API.

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
3. Select a ranked trend. Inspect score factors, keyword matches, distinct authors, multi-document summary and source-post evidence. Off-topic football remains visible with a low-relevance flag, outside the top recommendations.
4. Choose **Create angles & draft**. The studio shows Opinion, Educational and Product angles plus a suggested X post.
5. Edit the post, save and approve. Only approved text can be exported. Changing it revokes approval. Export is a text download for manual publishing, never a claim that an X post was published.
6. Use **Open in X** to prepare the approved text in the composer; confirm publication yourself on X. Return, enter the actual URL/time and **Mark as Published**.
7. In **Performance**, enter real cumulative metric totals. Update them later; only the latest snapshot per post contributes to aggregates. Qualified engagement remains **Not measured** unless qualification is separately established—ordinary interactions are not automatically qualified engagement.

See [the full growth-loop walkthrough](docs/PRODUCT_DEMO.md), [the 3–5 minute video script](docs/DEMO.md), [full Phase 1 plan and page-referenced checklist](docs/PHASE1.md), and [validation report](docs/VALIDATION.md).

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

`app/publishing.py` owns manual publication, composer intents and performance calculations; `app/static/performance.js` owns the Performance UI; `app/x_api.py` owns official on-demand X fetching, normalization, caching and persistent spending safeguards; `app/db.py` owns SQLite initialization; `demo.py` owns fictional fixtures; `trends.py` owns detection/ranking; `content.py` owns replaceable draft generation; `main.py` validates data and controls workflow; `app/static/` contains the responsive dashboard. Tests use separate temporary databases.

Accounts, posts, analysis evidence snapshots, brand settings and drafts are persisted. Exact duplicates are removed during topic analysis, not from the stored raw dataset. An analysis stores its original brief and data context so later configuration changes do not silently rewrite an existing draft's rationale. Editing approved draft text clears its approval.

## 中文 / English interface

New browser profiles default to **简体中文**. Use the visible **中文 / English** switch in the header; your choice is stored under `telyclaw.language` in this browser's localStorage and survives navigation/reloads. If storage is unavailable the current page still switches, and new visits default to Chinese. The four workspace pages, action/status labels, dynamic explanations, methodology, input errors, publishing instructions and metric definitions are localized. Technical identifiers, unknown-domain keywords and user-authored evidence remain in their original language. The API documentation at `/docs` remains developer-facing English.

**Interface language is separate from content language.** Original X text, handles, links, configured brand brief, source excerpts, generated angle ideas, editable X drafts and published snapshots are not translated or rewritten. English drafts remain English in a Chinese interface. Switching language preserves unsaved draft/form/metric values and approval state. The current conservative ASCII draft policy remains unchanged; Chinese post generation/export is not part of this UI localization round.

`app/static/i18n.js` is the presentation catalogue: English UI copy → natural Chinese, with parameterized rules for counts, evidence summaries and sanitized validation/provider errors. A text-node renderer retains English originals for reversible switching without recreating forms; `data-raw` explicitly protects source evidence and generated content. Add new interface copy to this catalogue and cover dynamic variations in the bilingual browser test. Existing saved records and analyses remain unchanged; run a fresh analysis to use the improved clustering. There is **no database migration** in this round. Do not delete, reset or replace `data/growth.db`.

## Topic discovery and evidence summaries

No API key, model download or network call is required for clustering. `app/semantics.py` contains a versioned, inspectable domain vocabulary for multi-agent orchestration, frameworks/interoperability, coding assistants, human oversight, context/memory efficiency, content attribution, social listening and software security. Patterns normalize **specific concepts**, not source IDs or sample-specific cluster assignments. Generic AI/agent/workflow mentions are insufficient. For example, context compression and token budgeting can match without sharing two literal words. A broad “multi-agent” mention cannot override conflicting concrete concerns such as context budgets versus human approval.

The local method retains **80% word/phrase TF-IDF cosine similarity + 20% character n-gram similarity**. A shared specific concept raises pair similarity to at least 0.64; otherwise at least two non-generic content words must overlap. Pairs with different identified domain concerns and no shared specific concept are rejected. Average-link agglomerative clustering uses distance 0.69 (similarity 0.31), with **no preset number of clusters**. Average linkage limits single-link bridge effects but does not eliminate every ambiguous merge.

A majority-supported concept supplies a concise bilingual theme label; ties favor concrete themes over a bare multi-agent mention. Unsupported domains receive a conservative keyword discussion label. Labels come from a reusable domain taxonomy, not arbitrary filtered bigrams or a fixed list of the user's posts. Every supporting document contributes to theme extraction; summary excerpts are ordered by centrality to the cluster centroid. The summary reports source/account counts and up to three attributed excerpts, while all original supporting posts remain inspectable. Each topic also exposes matched concept phrases per source and the exact clustering method. This is **local vocabulary-assisted semantic grouping and extractive synthesis**, not neural embeddings, an LLM, fact verification or evidence of platform-wide consensus. Optional LLM-assisted *clustering* is not implemented; the existing optional content-generation adapter is separate.

Exact normalized-text duplicates are removed conservatively before analysis. Supporting post/account counts therefore describe the deduplicated evidence, not all raw eligible rows. The dashboard displays available source engagement (observed likes + reposts + replies), marks incomplete counts and retains original URLs/timestamps/text. Missing values are never invented.

### Historical evidence and momentum

**Insufficient historical data** is the default. There is no neutral positive momentum score. A prior match requires the same specific domain theme, or (for unclassified themes) cosine similarity ≥0.25 plus two shared non-generic content words. Case variants of the same handle count as one author. To show observed sample velocity, both equal-duration windows need at least three distinct matched posts, at least two authors, and a timestamp spread of at least 25% of the window. Only then is change calculated as `(current count − prior count) / prior count × 100` and labeled rising or flat/falling **in the observed sample**.

Even sufficient counts do not establish complete platform coverage, causation or statistically reliable platform growth. Manual/JSON samples may be selected unevenly; the Live adapter retrieves just one page. Those limitations remain visible. Publication timestamps are actual evidence; historical baselines and growth percentages are not synthesized.

### Topic opportunity ranking

The base weights follow the challenge-oriented recommendations:

| Factor | Base weight | Observed input / heuristic |
|---|---:|---|
| TelyClaw relevance | 30% | 25 points per specific configured keyword + 35 for a supported domain theme when the brief includes an AI/agent editorial scope; otherwise only 10 points for generic matched terms; capped at 100. Domain fit is an explicit editorial assumption, not a verified product capability |
| Momentum | 25% | Observed count change when the evidence checks above pass; factor = clamp(change / 2, 0, 100) |
| Engagement quality | 15% | Log-scaled mean source engagement, damped by `min(1, independent authors / 3)` so a single viral source is not treated as broad confirmation |
| Independent accounts | 15% | Distinct deduplicated authors / 5, capped at 100 |
| Content opportunity | 10% | Editorial depth proxy: min(100, 35 + 10 × independent authors + min(20, 10 × distinct recognized concepts)). Repeated posts from one author do not increase this dimension; it does not predict originality |
| Freshness | 5% | Age of newest source relative to the selected window, bounded 0–100 |

Unknown momentum or incomplete likes/reposts/replies receive **no factor value and zero effective weight**. Remaining weights are rescaled to total 100%; the UI displays these effective weights and explains the missing inputs. A known zero remains zero. Partial available engagement totals are still shown as partial, but are not used as if complete in scoring. Scores with different coverage need judgment.

Up to three relevance-gated clusters are highlighted; the app never invents a third opportunity when fewer relevant topics exist. Every topic has **Why It’s Trending** (observed support and limits), **Why TelyClaw Should Care** (connection to the configurable audience/positioning), and **Recommended Content Move** (a theme-specific editorial experiment plus a source-based comparison and test). These are editorial hypotheses, not verified product claims. The default brief is explicitly provisional because the assignment did not provide authoritative product capabilities or ICP. Confirm and edit it in Sources & Settings.

## Trend-specific generation and human review

Local drafting is labeled **Local editorial templates (evidence-conditioned, no LLM)**. It derives a subject and contrasting phrases from the selected cluster and uses attributed source discussion points to create Opinion, Educational and Product angles. The suggested post adds a TelyClaw editorial test and actionable buyer task, rather than copying a source. The fallback is deterministic and still uses template structure; it is not falsely labeled LLM-generated or equivalent to an expert editor.

An optional OpenAI adapter remains available via `OPENAI_API_KEY` and `OPENAI_MODEL` (default `gpt-4o-mini`). It receives the configured brief, source evidence and recommended content move. Its output is labeled **OpenAI LLM**, requires three named angle categories, and rejects invalid length/format or a substantial verbatim source passage. Provider failures are explicit; they never silently claim a successful LLM call. Development tests mock this provider; real LLM access remains unverified.

Human review is mandatory. Editing an approved draft revokes approval and hides publishing controls until approval again. The conservative export policy remains **1–280 ASCII characters without URLs**. This is a safe subset of standard X constraints, not a full implementation of X's Unicode/URL weighted counting or longer paid-account posts. Unsupported drafts must be edited before approval. Source posts themselves can contain Unicode and URLs.

## Manual publishing and Performance

1. Approve a saved draft. **Export approved text** remains a TXT download.
2. **Open in X** redirects to an encoded official web intent (`https://twitter.com/intent/tweet?text=…`). It only prefills the composer; the user reviews/confirms in X. Opening it does not create a publication record or claim success.
3. After actually publishing yourself, enter the real HTTPS X URL and timezone-labeled publication time, then **Mark as Published**. Structural URL validation and numeric-ID uniqueness prevent accidental duplicate records; the app does not verify the post against X.
4. The publication preserves an immutable snapshot of approved text, source mode, draft and topic. Published text stays TXT-exportable but is locked against rewriting. **Create revision** makes a new unapproved draft while preserving publication history.
5. Open **Performance** and enter real observed cumulative metrics, plus measurement time. No simulated outcomes are supplied. Before any publication, the page explains the next step and shows **Not measured**.

### Metric definitions

- **Measured engagement** = available likes + reposts + replies + bookmarks. All four unknown means **Not measured**, not zero. Partial totals are labeled partial. These interactions are not automatically *qualified* engagement.
- **Per-post engagement rate** = available measured engagement / positive impressions × 100. Unknown or zero impressions means rate **Not measured**. The numerator may be partial; that limitation is displayed.
- **Aggregate/topic engagement rate** uses only posts having both positive impressions and some measured engagement. It divides the sum of their latest engagement counts by the sum of their impressions; the UI shows the number of paired posts. Other measured engagement is included in total engagement but not a rate with a mismatched denominator.
- Link clicks, profile visits and post-attributed followers are stored as **separate outcomes**, not added again to engagement. Aggregate coverage says how many posts have each metric.
- Followers directly attributed to a post require a note describing reliable post-level attribution evidence, even for zero. Leave blank without such evidence. An account's follower-count increase is **not** a post-attributed follower count. This is user-declared evidence, not API verification.
- Every update is a complete cumulative snapshot: blank fields mean unavailable, not “keep previous value.” The form prefills existing values for convenience. Snapshots remain in history; only the latest per published post is aggregated, avoiding double-counting. Measurements cannot precede publication, be future-dated, or replace a newer measurement with an older timestamp.
- Topic rollups use the immutable inferred topic key/title from the generating analysis (legacy drafts fall back to a title-derived key). Similar discussions with different inferred names can appear separately; there is no automatic cross-analysis taxonomy reconciliation.

Learn by reviewing topics after consistent measurement windows, checking audience quality, and recording what to change in your next editorial experiment. Comparisons are observational, not causal lift or a guarantee of growth. Automatic learning from outcomes and account-level follower analytics are not implemented.

### Database upgrade and data preservation

Startup idempotently adds **`publications`** (unique draft and X post ID) and **`measurements`** (publication snapshots) plus an index. No imported post, existing account, draft, saved analysis, Live cache or API-budget record is deleted or rewritten by this migration. Old analyses remain snapshots of the earlier method; **run Analyze signals again** to use the new detector. Drafts made from old analyses still work.

Keep `data/growth.db` and your private `.env` when updating. Stop the old server first and make a private local backup of the database. With a ZIP download, copy your existing `data/` directory into the newly extracted project **before starting it** so your manually entered posts remain available. Do not upload databases or secrets to GitHub.

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
7. Inspect source links, multi-document summaries and score factors. Generate three angles and a draft, edit it, approve it and export text through the unchanged workflow.

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

Download branch **feat/semantic-topics-bilingual-ui** as a ZIP from GitHub, or switch an existing checkout to that branch. Stop the old server with Control+C, install `requirements.txt` in your existing virtual environment and restart using the **Run locally** commands. No new runtime dependency was introduced for this enhancement.

### Production monitoring later

The existing official X API adapter could replace manual copying once access and costs are approved: resolve account IDs, retrieve normalized posts and preserve source links/metrics. The current implementation is manual on-demand fetching with caching and caps—not streaming or complete historical coverage. Scheduled ingestion, pagination/checkpoints, retention/deletion handling and broad multi-account coverage would need further work and review of current X access/pricing. Manual records stay separately labeled rather than being presented as API-verified data. None of this is required for today's no-fee workflow.

## Live X monitoring: macOS setup and safe operation

This feature is **on-demand fetching, not streaming**. You can inspect Live mode with **$0 credits**: it will explain missing credentials or disabled fetching without contacting X. Demo remains the default on every page load. Changing modes, inspecting status, analyzing a cache, generating drafts, approving and exporting never trigger an X request.

To update an existing checkout on your Mac, open Terminal in the project folder:

```sh
git fetch origin
git switch feat/growth-intelligence-loop
git pull --ff-only origin feat/growth-intelligence-loop
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Stop an older server with Control+C first. For a fresh download, select branch **feat/semantic-topics-bilingual-ui** on GitHub, choose Code → Download ZIP, extract it, and follow **Run locally** above. No Git installation is needed for the ZIP option. Open http://localhost:8000 in Safari/Chrome. Leave Terminal open while reviewing the app.

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
python tests/growth_browser_smoke.py
python tests/bilingual_browser_smoke.py
node --check app/static/i18n.js
node --check app/static/app.js
node --check app/static/performance.js
```

The original browser test uses a temporary database on port 8001; the Live test uses port 8002 and an in-process MockTransport. The manual-form browser test uses port 8003 and blocks non-local browser requests. The growth-loop browser test uses an ephemeral localhost port and intercepts the composer intent before it can contact X. The four English regression scripts save screenshots under `work/browser/`; the bilingual test uses another ephemeral port and saves Chinese desktop captures under `work/`. It verifies default language, persistence, unchanged source/draft text, retained unsaved edits, approval/export, composer URL, publication and metric entry without external requests. Browser tests respect `CHROMIUM_PATH` when supplied. Tests default-deny X traffic and blank real service keys; the Live suite uses non-secret placeholders, never actual credentials. Node is only needed for the optional JavaScript syntax check, not to run the app.

## Current limitations and submission status

- Page 7 obscured README requirement: **Pending recruiter clarification**; no text inferred.
- Live X on-demand ingestion is implemented behind explicit enablement, but real endpoint authentication/credits are unverified. Direct X API publishing and automatic scheduling are not implemented. Manual publication records and real, manually entered content-performance snapshots are implemented.
- Local English domain-vocabulary/character similarity can still split or merge topics incorrectly and does not verify truth or independence. It is not a neural embedding model. Exact copies are deduplicated; semantic duplicates and multilingual discussion remain limited. Your local ten-post dataset was not assumed available: clustering tests use labeled test-only fixtures.
- Optional LLM integration is present but not live-tested; local templates are not equivalent to LLM generation.
- No authentication, tenant separation, team roles, public-hosting hardening or background job infrastructure. Run on localhost for this single-user challenge. Do not expose publicly without those controls and request limits.
- Draft text is editable; angle cards are suggestions rather than independently editable documents. Human edits must substantiate actual product relevance.
- Historical analyses and measurement snapshots persist. There is no cross-analysis trend-history chart, automatic outcome-driven optimization, or causal engagement-lift experiment.
- Professional demo video recording, recruiter clarification, verified product positioning and final submission remain outstanding. No claim of proven 10× growth.

Built with **OpenAI Codex** as the vibe-coding assistant; local NLP uses **scikit-learn**. Optional content generation uses the OpenAI API when explicitly configured. No other AI tools or successful integrations are implied.

## Review this optimization locally (macOS)

Stop the old app with Control+C. In the **existing project folder** (so your database stays in place), run:

```sh
git fetch origin
git switch feat/semantic-topics-bilingual-ui
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

If your environment folder has another name, activate that environment instead. For a fresh setup use the Run locally instructions above; copy your existing database only if you deliberately move project folders. Open http://localhost:8000. Keep `X_LIVE_ENABLED=false` and leave `OPENAI_API_KEY` unset for the free local demonstration. This feature branch is intended for review; merging remains a separate user action.

### Mandarin interview walkthrough

1. Start in 中文 and Demo; point out the synthetic-data banner. Switch briefly to English and back to demonstrate international usability.
2. In 数据源与监控设置, confirm at least five enabled accounts and inspect the real manually imported sources. Do not mistake Demo for real data.
3. Return to 趋势机会 → 手动导入 → 最近 7 天 → 分析信号. A fresh analysis is required; existing saved drafts are not reclustered. The user's actual source set determines the topic count—there is no forced three-cluster result.
4. Inspect a coherent topic's original evidence and concept matches; explain independent account count versus post count. For small/uneven samples explicitly say “历史数据不足，不能推断全平台趋势”.
5. Compare the Top 3 score breakdowns and recommended editorial experiments. Brand/domain relevance is a reviewable hypothesis; confirm the provisional brand brief before making product claims.
6. Generate three angles and an English draft, edit/save/approve, switch language without changing the draft, and export TXT. Open in X only prefills the composer; publication requires your own confirmation there.
7. Only after a real manual publication, record its actual URL/time and enter observed performance metrics. Leave unavailable fields blank. Before publication, show the honest empty state; never enter test numbers as real results.

The user's local ten real posts were not available in this environment. New paraphrase fixtures are test-only. Re-run the seven-day Manual Imports analysis locally to assess actual grouping; no numerical improvement on that private dataset is claimed.
