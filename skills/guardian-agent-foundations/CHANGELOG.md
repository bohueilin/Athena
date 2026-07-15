# Changelog — guardian-agent-foundations

## 2026-07-15 — FAR AI ingest (v2.1)
Added the **FAR AI** frontier-lab safety corpus (15 papers) as a new `FAR-AI` category → **447 papers total**.
New: 15 research cards, `syntheses/FAR-AI.md`, and cross-source addenda in the `ai-llm-safety` + `adversarial-ml`
chapters; ontology + relationship graph rebuilt over 447 tags (FAR↔AAAI cross-linked). `build_manifest.py` is now
multi-source; `validate.py` validates card coverage against the manifest (machine-independent) and expects 9 syntheses.
All gates pass. See `RESEARCH_UPDATE_LOG.md` for the procedure trace. (`FAR04` = existing `A41108`, cross-referenced.)

## 2026-07-14 — AAAI-26 research base (v2)
Added an evidence-anchored research-to-engineering layer built from **432 AAAI-26 security papers**
(`~/Documents/Research Papers/AAAI-Security-2026/`, 8 categories), alongside the existing Virtue-AI
worldview files (which are unchanged and remain the design-framing layer).

**Added**
- `references/corpus-manifest.{jsonl,csv}`, `corpus-audit.md`, `exceptions-and-unreadable-files.md` — Phase-1 inventory: 432 found, **0 duplicates, 0 unreadable**, per-category counts reconciled to the expected table.
- `references/research-cards/<category>/A#####.md` — **432 structured research cards** (one per paper).
- `references/ontology.md` + `ontology.json` + `paper-to-ontology-map.jsonl` + `research-relationship-graph.json` — normalized ontology (assets/adversaries/surfaces/attacks/defenses/evidence) + queryable graph.
- `references/syntheses/*.md` — **8 category syntheses** (20-section).
- `references/cross-cutting/*.md` — **8 cross-cutting chapters**.
- `references/patterns/*.md` — **28 engineering control playbooks**.
- `references/source-index/` — by-id / by-category + **relevance-triage.md** (core 137 / adjacent 245 / peripheral 50 vs Origin/Passport).
- `references/README.md`, `executive-summary.md`, `final-quality-review.md` (10-perspective adversarial QA).
- `scripts/` — `build_manifest.py`, `assemble_ontology.py`, `search.py` (+ workflow drivers); `tests/validate.py` (§7 gates); `templates/research-card-template.md`.
- `SKILL.md` — new **"AAAI-26 security research base"** section: layout + retrieval, the **research-to-decision framework (A→H)**, **evidence discipline**, and research-backed invocation examples. Frontmatter `description` extended for the new problem classes.

**Method** — deterministic Python for inventory/ontology/validation (reliable hashes, counts, graph); a
multi-agent workflow (general-purpose subagents, 4-way concurrency, map-reduce) for the reading-heavy cards +
syntheses + chapters + playbooks. Every substantive claim is traceable to a paper id; calibrated language enforced.

**Validation** — `tests/validate.py`: card coverage 432/432 · citation resolution 0 orphans · ontology tag
coverage 432/432 · counts 8/8/28. One hallucinated citation (`A38449`) found and removed. Evidence strength:
strong 17 / moderate 312 / preliminary 38 / insufficient 65.

**Preserved** — all v1 worldview/interview/landscape files and behavior are intact; nothing deprecated.

## (prior) — v1
Virtue-AI worldview, threat models, agent-identity, architecture patterns, papers, products, glossary,
regulations, 2026 landscape sweep, interview prep. See git history.
