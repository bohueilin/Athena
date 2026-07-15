# Research Update Log

Append-only record of corpus builds/updates, and the procedure to add new papers without a full rebuild.

## Log

### 2026-07-14 — initial build (432 papers, AAAI-26)
- Corpus: `~/Documents/Research Papers/AAAI-Security-2026/` — 432 PDFs, 8 categories, reconciled to the expected table (0 delta), 0 duplicates, 0 unreadable.
- Produced: 432 cards, 8 syntheses, 8 cross-cutting chapters, 28 patterns, ontology + relationship graph, source index + relevance triage, exec summary, 10-lens QA.
- Gates: `tests/validate.py` all-pass. Fixes: removed 1 hallucinated citation (`A38449`); titles rebuilt from card H1 (manifest first-page text carried AAAI boilerplate).
- Stable ids: `A<article-id>` (the AAAI OJS article number, e.g. `A40895`). These are permanent — never renumber.

### 2026-07-15 — FAR AI ingest (+15 papers → 447 total)
- Source: `corpus/far-ai/` (FAR AI frontier-lab safety) — 15 PDFs. Ingested as a **new `FAR-AI` category**
  (thematically distinct: adversarial robustness of superhuman/Go AIs, LLM persuasion & misuse, sandbagging &
  auditing games, agentic-AI security, reasoning obfuscation vs monitoring) rather than scattering into the 8
  AAAI categories — so no re-run of the AAAI syntheses.
- Stable ids: `FAR01`–`FAR15` (sorted order of `corpus/far-ai/*.pdf`; permanent). Venue `FAR AI`.
- Produced: 15 research cards (`research-cards/FAR-AI/`), 15 ontology tags, **1 new synthesis** (`syntheses/FAR-AI.md`),
  and 2 **cross-source addenda** appended to `cross-cutting/{ai-llm-safety,adversarial-ml}.md` (strengthen/add/contradict
  reconciliation) — the AAAI syntheses/chapters were otherwise left intact.
- **Dedup:** `FAR04` (STACK: Adversarial Attacks on LLM Safeguard Pipelines) is the same paper as AAAI `A41108` —
  cross-referenced in the card; both retained.
- Re-ran `build_manifest.py` (447, 0 dup, 0 unreadable, 0 missing cards) → `assemble_ontology.py` (447 tags, graph
  cross-links FAR↔AAAI by shared tokens) → `validate.py` (all gates; syntheses gate 8→9; card-coverage now validates
  against the multi-source manifest so it stays machine-independent).
- **Not yet ingested:** none outstanding in `corpus/`. (Virtue AI seed papers remain covered by the original
  `references/papers.md`, separate from the 447.)

## Incremental-update procedure (adding new papers)

Stable ids + content hashes make updates cheap. To add or refresh papers:

1. **Detect changes.** `python3 scripts/build_manifest.py` recomputes `content_hash` + `processing_status` for
   every PDF and flags `card-missing`. New/changed files = new hash or missing card. (Compare against the prior
   `corpus-manifest.jsonl` in git to see the diff.)
2. **Dedup / versioning.** The manifest links exact-dup hashes (`duplicate_group`). For a newer version of an
   existing paper, keep both cards and set `supersedes_or_superseded_by`; mark the canonical one.
3. **Extract only new/changed cards.** Run the card workflow over just the `card-missing` ids (the driver reads
   the missing set and skips existing cards — same idempotent pattern used for the initial build).
4. **Re-tag + re-map.** The card workflow emits `ontology-tags/*.jsonl`; then `python3 scripts/assemble_ontology.py`
   rebuilds `ontology.*`, `paper-to-ontology-map.jsonl`, and `research-relationship-graph.json`.
5. **Recompute affected syntheses only.** Re-run the reduce step for the categories whose card set changed; leave
   the others cached.
6. **Reconcile evidence.** In the affected synthesis, note where new evidence **strengthens / weakens / contradicts**
   a prior conclusion (use the "Conflicting findings" + "Strongest replicated findings" sections).
7. **Update the skill only if reusable guidance changed** — i.e., a *pattern's* control/verification/bypass/
   residual-risk materially shifts, or a new invocation class appears. Otherwise leave `SKILL.md` untouched.
8. **Validate + log.** `python3 tests/validate.py`; append a dated entry here; bump `CHANGELOG.md` if the skill changed.
9. **Preserve backward-compatible ids** so existing citations keep resolving.

### Standard commands
- **Full rebuild:** re-download (`scripts/download_aaai.py`) → cards workflow → `assemble_ontology.py` → syntheses/chapters/patterns workflow → `validate.py`.
- **Incremental:** `build_manifest.py` (diff) → cards workflow on `card-missing` → `assemble_ontology.py` → reduce affected categories → `validate.py`.
- **Validate only:** `python3 tests/validate.py`.
- **Search:** `python3 scripts/search.py {attack|defense|asset|surface|adversary|evidence} <token>` · `mitigations <attack>` · `rel {core|adjacent|peripheral}` · `text "<phrase>"`.
