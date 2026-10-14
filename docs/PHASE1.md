# Phase 1 — verified assignment and implementation plan

Source: attached seven-page `TelyClaw_Growth_Lead_Challenge (1).pdf`, visually reviewed in full. English below translates the readable Chinese requirements. The orange annotation obscures a README line on p.7: **Pending recruiter clarification**. No contents are inferred. This document is the plan; implementation status is recorded in README and VALIDATION.

## What the company wants
A working AI-assisted growth loop that finds worthwhile discussions among selected X accounts, explains which opportunities TelyClaw should act on, and turns them into original content for human review. A usable end-to-end MVP matters more than complex engineering or slides (pp.1,5,7). Technology and AI tools are freely selectable (p.7).

## Authoritative requirement checklist

| ID | Requirement | Type | Page | Planned implementation / verification |
|---|---|---|---|---|
| R1 | Add and remove monitored X accounts; monitor multiple accounts | Core | 2 | Persistent account controls; six fictional demo accounts |
| R2 | User-defined monitoring window; get new posts in that window | Core | 2 | 1h, 4h, 24h, 7d presets; timestamp and enabled-account filtering |
| R3 | Group related posts into topics | Core | 3 | Local TF-IDF semantic similarity clustering |
| R4 | Automatically identify and name topics | Core | 3 | Cluster keywords as labels |
| R5 | Summarize each topic's discussion | Core | 3 | Evidence-grounded extractive summaries |
| R6 | Judge topic heat and identify rising discussions | Core | 3 | Volume, distinct authors, freshness, adjacent-period momentum |
| R7 | Show related posts and accounts as evidence | Core | 3 | Inspectable source evidence per opportunity |
| R8 | Define own opportunity score, identify top 3 opportunities and explain why | Core | 3 | Visible weighted factors, sorted scores, top-three labels |
| R9 | Ranking factors may include velocity, engagement, independent accounts, freshness, relevance and content opportunity; exact formula is not mandated | Guidance | 3 | Explicit normalized weighted score; no claim of predictive validity |
| R10 | Generate three distinct angles: Hot Take/Opinion, Educational/Insight, TelyClaw Product Angle | Core | 4 | Three editable content suggestions per selected trend |
| R11 | Generate at least one publication-ready X post; more than copying, rewriting or summarizing source tweets | Core | 4 | Original structured editorial perspective, editable draft, length validation |
| R12 | Content standard: Trend + TelyClaw Perspective + Original Insight | Core | 4 | Visible brand brief; no unverified product claims |
| R13 | Trend → AI Draft → Human Edit → Approve → Publish | Workflow | 4 | Draft, saved edits, approval, export for manual publishing; actual X integration optional |
| R14 | At least 5 configurable X accounts | Minimum | 4 | Six seeded fictional accounts and account management |
| R15 | At least 2 time windows | Minimum | 4 | Four presets |
| R16 | Fetch or import posts for specified period | Minimum | 4 | JSON import; selected-window filtering; synthetic demo fixtures |
| R17 | Automatically detect multiple topics/trends and summaries | Minimum | 4 | Genuine local statistical NLP, not hard-coded trend results |
| R18 | Rank trends and explain ranking | Minimum | 4 | Computed scores and factors |
| R19 | Select top trends worth TelyClaw pursuing | Minimum | 4 | Relevance gate and top three |
| R20 | At least 3 content angles per selected trend | Minimum | 4 | Generation button |
| R21 | At least 1 directly publishable X post | Minimum | 4 | Review editor and approved text export |
| R22 | Basic usable UI and complete end-to-end demo | Minimum | 4 | Responsive dashboard; browser workflow check |
| R23 | Alternative data methods permitted when X API, rate limits or paid APIs constrain access | Permitted fallback | 2 | Prominent synthetic/imported provenance; no live claims |
| R24 | README explains production data acquisition | Deliverable | 2 | X ingestion plan, access, limits, retries and retention |
| R25 | Working demo | Deliverable | 7 | Locally runnable web application |
| R26 | Source code / GitHub repository | Deliverable | 7 | Feature branch |
| R27 | 3–5 minute demo video | Deliverable | 7 | Script supplied; recording remains required |
| R28 | Brief README: product logic, architecture, detection, ranking, generation, AI/vibe-coding tools, current limitations | Deliverable | 7 | README with links to detailed docs |
| R29 | Obscured README line | Unknown | 7 | **Pending recruiter clarification** |
| R30 | Prepare 90-day strategy for 10× qualified reach on official X account | Final growth question | 7 | Growth strategy below and demo talking points; goal, not proven result |
| R31 | PPT not required; working product prioritized | Guidance | 7 | Focus on product and video |

### Optional bonuses (all from p.5)

| Feature | MVP decision |
|---|---|
| Trend velocity / momentum detection | Include adjacent-period comparison; missing baseline stays unknown |
| Engagement-based ranking | Include observed source metrics, synthetic in Demo Mode |
| Cross-account topic clustering | Include with local NLP |
| TelyClaw brand / product relevance scoring | Include explicit brief keywords and transparent heuristic |
| Duplicate / similar content detection | Exact normalized-text deduplication; semantic duplicates remain a limitation |
| Human approval workflow | Include; also explicitly required by the user's request |
| X publishing integration | Defer; approved export only |
| Scheduled monitoring | Defer |
| Historical trend tracking | Persist analysis snapshots; no longitudinal chart in first release |
| Published content performance tracking | Defer real integration; no invented performance |
| Improve next content using historical performance | Defer until real outcome data exists |
| AI agent automatically completes workflow | Defer; approval remains mandatory |

Overlap: p.4 describes human review and p.5 also lists approval as a bonus. We include an enforced approval state because the user explicitly requires it. Basic heat assessment is core; sophisticated velocity is a bonus. Supporting metrics are suggested, not a requirement to demonstrate measured growth during the challenge.

## Architecture and technical decisions
Python FastAPI serves both the API and a plain HTML/CSS/JavaScript dashboard. SQLite stores accounts, posts, analysis snapshots and drafts on disk. Scikit-learn performs TF-IDF vectorization and cosine-similarity clustering locally. No separate frontend build, hosted database, task queue or container is required. One startup command opens the whole app. This is a single-user demo, not a production multi-tenant service.

Separate modules: database, sample-data provider, trend engine, content provider, API, and UI. Optional OpenAI content generation is server-side and environment-configured; it is never silently represented as active. Without a key, local draft templates are explicitly labeled. Local statistical NLP is AI-assisted detection; local draft templates are not an LLM. Secrets never belong in browser code or Git.

Data model: Account(handle, enabled); Post(id, account, text, timestamp, engagement, provenance); Analysis(id, window, clock, topics and score evidence snapshot); Draft(id, analysis/topic, angles, text, status, generator, timestamps). Editing approved text revokes approval. Export only approved current text. Synthetic posts and imported posts are analyzed in separate modes. Post IDs are namespaced by provenance.

Workflow: configure accounts → choose demo or imported dataset and window → analyze → inspect ranked topics and evidence → select a trend → generate angles and draft → edit/save → approve → export text → manually publish outside this MVP. Outcome measurement requires actual published-post analytics later.

## Data strategy
Six fictional accounts with realistic synthetic discussions, staggered timestamps, several topics, low-relevance noise and prior-window evidence. A fixed visible scenario clock makes the demonstration reproducible. Changing the window genuinely changes inputs. Imported JSON uses actual UTC timestamps and current time, never the synthetic clock. Validate every record before committing an import. Do not turn imported engagement into claims about generated-post performance.

Production: implement an official X API ingestion adapter after confirming current plan, read permissions, permitted storage/retention and cost. Resolve account IDs, paginate timeline requests, checkpoint post IDs, deduplicate, retry transient errors with backoff, respect rate-limit headers, surface freshness/errors and schedule pulls. Do not claim real-time coverage until access and latency are verified. Import remains the fallback. X write access and analytics scopes are separate integrations.

## Growth strategy and metrics
Official proposed North Star (p.6): **Qualified Engagement Generated from Trends**. Examples: replies, reposts, bookmarks, profile visits, qualified followers and product clicks. MVP proxy: **Qualified Engagement per Trend-generated Post**. These are not simply posts generated or accounts monitored. Define qualified audience and event rules with TelyClaw, avoid double-counting people where possible, separate event types when attribution/deduplication is unavailable, and disclose unavailable metrics. Zero published posts means 'Not measured', not zero success.

Suggested supporting metrics (p.6): detection lead time; trend-to-content time (target under 5–10 minutes); trend hit rate; content acceptance rate (publishable without major editing); engagement lift against ordinary posts; qualified engagement. App can demonstrate workflow timing and approval state, but approval alone does not prove no major edits or external publication. Real lift needs comparable historical posts and fixed measurement windows.

Proposed score: 30% relevance, 20% author breadth, 15% engagement, 15% freshness, 10% momentum, 10% evidence/content depth. Each factor is 0–100 and shown. Missing momentum gets a neutral 50 with explanation, not fabricated growth. Relevance comes from editable positioning keywords; it is a heuristic, not an objective truth. Exclude zero-relevance topics from top recommendations while retaining them for inspection. Prefer useful buyer questions and differentiated commentary over popularity alone.

TelyClaw's actual product positioning and ICP are not supplied in the PDF. Initial brief explicitly says provisional AI growth workflow positioning; no claims about unverified capabilities. Your commercial and social-listening background can be shown through source selection, relevance judgments, customer pain and measurement design.

90-day answer: Days 1–14 define ICP/qualification and baseline reach/engagement with the company, curate accounts, establish editorial guardrails and tracking links. Days 15–30 operate daily review sessions, test opinion/education/product angles, and measure time-to-content and audience quality. Days 31–60 compare matched posts, refine source lists and relevance weights, double down on recurring customer questions and start conversations with relevant authors. Days 61–90 scale winning formats and distribution partnerships, review outcomes weekly, and retire weak topics. 10× qualified reach is a target hypothesis requiring a baseline, reliable reach measurement and sufficient sample size; it is not guaranteed. The loop is Trends → Content → Attention → Engagement → Growth (p.7).

## Roadmap and risks
1. P0 document source requirements and unresolved text; create isolated branch.
2. P0 implement persistent account controls, validated import and dataset/window selection.
3. P0 implement clustering, summaries, evidence and explainable ranking.
4. P0 implement angles, original draft suggestions, editable brief, review and approval/export.
5. P0 deliver professional responsive dashboard with loading, empty and error states.
6. P0 test data/window boundaries, multiple trends, rankings, invalid imports, approval invalidation and complete browser workflow; verify startup.
7. P1 README, demo script, source branch and validation evidence.
8. P1 record 3–5 minute video and reconcile recruiter clarification before final submission.
9. P2 verify real X/LLM access, published metrics and scheduling if time/budget allow.

Open questions: obscured p.7 line; verified brand positioning and audience; deadline/hosting expectations; X access and costs; AI provider budget; qualified engagement and reach definitions. None block the honest offline demo. Chinese/multilingual clustering, adversarial text, noisy signals and weak baselines limit local NLP. No outbound posting occurs. A public deployment needs authentication, user isolation, CSRF/origin controls and operational hardening. Planning is complete enough to implement; these limitations remain explicit.
