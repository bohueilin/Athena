# AGENTS.md — how any coding agent uses Athena

This repo (**Athena**) is a knowledge base, not an app. Its flagship is
**`skills/guardian-agent-foundations/`** — an evidence-anchored decision skill for the **security,
safety, and privacy of AI agents and systems**, distilled from a 432-paper corpus into research cards,
8 category syntheses, 8 cross-cutting chapters, a normalized ontology + relationship graph, and **28
engineering control playbooks**. Every claim traces to a paper id; language is calibrated, never absolute.

## When to use it
Threat-modeling · designing defenses (prompt-injection / RAG / privacy / model-extraction / deepfake) ·
assessing a control against an adaptive attacker · defining evaluation plans, launch gates, and
residual-risk decisions · converting research into requirements · any **security/design audit** of an
agentic or AI system.

## How to consult it (deterministic, from `skills/guardian-agent-foundations/`)
```bash
python3 scripts/search.py attack <token>       # papers on an attack class
python3 scripts/search.py pattern <term>       # matching control playbooks
python3 scripts/search.py mitigations <attack> # defenses that co-occur with an attack  → what to build
python3 scripts/search.py asset <token>        # papers touching an asset
```
- Playbook index: `references/patterns/INDEX.md` · Ontology: `references/ontology.md` ·
  Category syntheses: `references/syntheses/` · Deep evidence: `references/research-cards/`.
- **Read `skills/guardian-agent-foundations/SKILL.md` first** — it defines the **CPVER lens**
  (Capability · Permission · Verification · Evidence · Residual-risk) and the **5-step audit recipe**.

## Audit recipe (copy for an audit task)
1. Enumerate **assets, adversaries, attack surfaces, trust boundaries** (ontology vocabulary).
2. Map each to its **attack classes** (`search.py` + `references/research-relationship-graph.json`).
3. Map each live attack to a **control playbook** in `references/patterns/`; apply **CPVER** to every
   enforcement point.
4. Flag uncovered attacks, **fail-open** gaps that should be fail-closed, and the open seams in
   `references/README.md` §Maturity.
5. Output a **launch-gate scorecard**: control · threat covered · evidence strength · paper ids ·
   residual-risk owner · blocking?

## Discipline
Cite paper ids for research-backed claims. Use calibrated language (never "secure"/"proven"/"unbreakable").
The playbooks are **research-grounded design guidance, not build-ready specs** — see
`references/final-quality-review.md`. This knowledge base does not replace reading a source paper on a
load-bearing decision.
