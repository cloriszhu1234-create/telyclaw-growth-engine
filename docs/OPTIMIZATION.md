# Final core optimization round

The latest round builds on merged `main` at `405ee72`; it preserves the prior growth loop and introduces no database migration. See README for the current formulas, local concept vocabulary, bilingual renderer, limitations and Mandarin demo walkthrough. Older design notes below describe the previous round and are historical where the clustering/ranking method changed.

New files: `app/semantics.py` (specific domain concept patterns, readable bilingual labels and editorial experiments), `app/static/i18n.js` (presentation-only translation catalogue), `tests/test_semantic_topics.py` and `tests/bilingual_browser_smoke.py`. Updated: `app/trends.py`, existing HTML/JS/CSS and browser regression language setup, README and validation/demo documentation. No paid model, scraping, streaming or direct publishing is introduced. Existing source evidence, drafts and outcome records remain in their original language and storage format.

# Final product optimization — review and acceptance map

This extends the existing FastAPI + SQLite app on `feat/growth-intelligence-loop`. No rebuild, external API requirement, destructive migration or source-post replacement was introduced.

| Acceptance criterion | Implemented behavior / validation |
|---|---|
| 1. ≥5 configurable accounts | Six seeded demo accounts; persistent account controls and enabled-account filtering retained |
| 2. ≥2 windows | 1h/4h/24h/7d; timestamp filtering tests retained |
| 3. Import/filter real posts | Manual form and JSON import retained, separate from Demo/Live; original URLs preserved |
| 4–5. Identify/name/group topics | General synonym/morphology normalization, word/phrase + character similarity and average-link clustering; nine test-only discussions → three groups; unrelated singleton retained |
| 6. Evidence summary | Full-cluster features select topic phrases and central source excerpts; all source evidence remains inspectable |
| 7. Supporting accounts/posts | Deduplicated author/text counts, full texts, dates, available metrics and links |
| 8. Velocity availability | Equal-window matched evidence needs sufficient counts, author breadth and temporal spread; otherwise Insufficient historical data, null momentum and zero weight |
| 9. Transparent Top 3 | Up to three relevant topic clusters; explicit weights, missing-data rescaling and singleton dampening |
| 10. Specific relevance | Configurable audience/positioning/keywords; editorial hypothesis with no invented product capabilities |
| 11–12. Angles/original post | Opinion, Educational and Product angles conditioned on source discussions; subject/contrasting-phrase draft; local/LLM labels, copying/format guards |
| 13. Review/approval | Existing edit/save/approve retained; editing hides publishing controls; saved changes revoke approval |
| 14. X composer | Approved-only encoded web intent; no automatic publishing or publication claim |
| 15. Manual publication | URL/time confirmation, unique draft/X ID, immutable approved text snapshot and revision path |
| 16. Real metrics | Manual cumulative snapshots, optional unknowns, timestamp/attribution guards, post/topic/aggregate totals and history |
| 17. TXT export | Approved and published text export; published history remains immutable |
| 18. No paid API required | Local detector/templates, manual inputs, user-operated composer and manual metrics; no new live integration |

## Files and migration

- `app/trends.py`: local semantic vocabulary, similarity, names/summaries, historical checks and revised score/explanations.
- `app/content.py`: evidence-conditioned local angles/draft and optional-LLM validation.
- `app/publishing.py` (new): intent URL, manual publication/revision, metric validation and aggregation.
- `app/db.py`: idempotent `publications` and `measurements` tables plus measurement index. Existing tables/records untouched.
- `app/main.py`: router integration, topic key metadata, published-text locking and existing TXT export preservation.
- `app/static/app.js`, `index.html`, `style.css`: decision explanations, publication controls and Performance navigation.
- `app/static/performance.js` (new): honest empty state, totals/coverage, post/topic summaries and metric history/forms.
- `tests/test_growth_loop.py` and `tests/growth_browser_smoke.py`: test-only clustering/publication/performance fixtures and full-loop validation.
- Existing test assertions changed only where the new scoring policy explicitly supersedes neutral momentum and static weight assumptions.
- README and `PRODUCT_DEMO.md`: operational steps, provenance, formulas, limitations and demonstration flow.

## Remaining boundaries

The actual ten local X posts are not bundled or assumed available; rerun analysis locally and inspect source evidence. The English local method is not a neural embedding model, and clustering/topic labels may need refinement for different vocabularies. Fewer than three relevant clusters are not padded with fabricated opportunities.

TelyClaw's positioning remains provisional until confirmed. Local content remains structured templates requiring editing; real LLM access is optional and unverified. Standard ASCII/no-URL 280-character approval is a conservative safe subset, not full Unicode/URL weighted counting. Publication/performance are manual confirmations, not API verification. Attribution notes are user-declared evidence. Topic rollups use stored inferred keys and can split similar discussions with different names.

No streaming, direct publishing, automatic outcome-based learning, production authentication, causal lift measurement or guaranteed growth is claimed. Recruiter clarification of the obscured PDF line and the actual 3–5 minute video remain separate hiring-submission tasks.
