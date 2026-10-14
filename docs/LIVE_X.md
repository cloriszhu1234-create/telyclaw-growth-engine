# Live X enhancement: implementation and review map

Built from merged main (`f13eaec`, PR #1) on `feat/live-x-monitoring`. This enhancement does not rebuild the app and does not implement automatic publishing.

| Requested behavior | Implementation / verification |
|---|---|
| Preserve existing MVP | Additive tables; original demo/import/content controls retained; original API/browser checks retained; existing-database upgrade test |
| Demo / Live switch | Demo selected on reload; Live panel is explicit; changing mode clears prior analysis and only reads local status |
| Official API | Fixed `https://api.x.com/2` origin; server Bearer header; username resolution + one timeline page; redirects disabled |
| @elonmusk default and future accounts | Validated username input defaults to elonmusk; per-account lookup/post cache; one account per analysis |
| Data integrity | Separate X cache; original/reply/quote/repost flags, source IDs/times/links; unknown metrics null/N/A; no synthetic substitution |
| Manual/cost controls | Explicit environment enablement, default 5/up to 10 posts, 15m cache, 10m shared cooldown, persistent 10-request UTC-day cap, no retries/pagination/polling |
| Rate/error handling | Missing/disabled, 401, 403, 402/recognized credits, 404, 429/reset/Retry-After, malformed data and network/service errors; raw upstream error text not returned or persisted |
| Concurrency/restarts | SQLite immediate transactions protect budget/cooldown; separate HTTP attempts count even on failure; restart keeps ledger |
| Security | .env ignored with sanitized example; server-only credentials; fixed API destination, no arbitrary fetch URL; browser cross-site fetch rejected |
| Existing growth loop | Cached X posts enter existing NLP/scoring; three angles/draft; sources retained in draft metadata; approval/export unchanged |
| Single-account scope | Analysis and drafts warn that account signals do not establish platform-wide trends or complete time-window coverage |
| Honest generation | Local editorial templates explicitly labeled; existing optional OpenAI provider remains separate and live-untested |
| Documentation | README has macOS steps, private variables, $0-credit flow, safeguards, error table and implemented/planned distinctions |

## Boundaries

No real X call, paid credit consumption, purchase or public posting was performed during development. Browser success/error demonstrations use an in-process MockTransport, not actual @elonmusk data. Those mock fixtures are not a product dataset and are not stored in the user's normal database.

X pricing, token permissions, plan availability and the current endpoint contract must be verified when funded operation is authorized. Ten HTTP requests is not a monetary guarantee. Time-window analysis only covers previously retrieved cache records; one page does not ensure historical coverage. Missing metrics exclude the engagement factor and rescale remaining weights, so scores with different data completeness require judgment.

Keep the application on localhost. It remains a single-user MVP without production authentication/team roles. The cross-origin fetch guard does not make it suitable for an unauthenticated public deployment. Do not enable HTTP header debug logging. Existing generated-post character restrictions and unverified brand positioning remain.

For the original hiring submission, the page-7 obscured line and 3–5 minute recorded video remain outstanding unless addressed separately. No changes were made to PR #1 and no new PR should be merged automatically.
