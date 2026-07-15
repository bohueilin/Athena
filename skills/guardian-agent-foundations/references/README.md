# References — the Guardian evidence base

Two layers live here:

**A. Worldview / design framing** (hand-authored, from the Virtue AI corpus + 2026 sweep):
`worldview.md`, `threat-models.md`, `agent-identity.md`, `architecture-patterns.md`, `papers.md`,
`products.md`, `glossary.md`, `regulations.md`, `landscape-2026.md`, `interview-agent-security.md`.
Start here for positioning, taxonomy, and the Origin/Passport design lens.

**B. AAAI-26 research base** (432 papers, evidence-anchored, built by the corpus pipeline):

| Artifact | What it is |
|---|---|
| `corpus-manifest.jsonl` / `.csv` | Per-file inventory: id, hash, pages, arXiv/DOI, category, extraction + card status |
| `corpus-audit.md` | Reconciliation to 432 (0 dup / 0 unreadable), per-category counts |
| `exceptions-and-unreadable-files.md` | Any files with extraction issues |
| `research-cards/<category>/A#####.md` | **One structured card per paper** — the primary evidence unit |
| `ontology.md` / `ontology.json` | Normalized vocab (assets/adversaries/surfaces/attacks/defenses/evidence) + frequencies |
| `paper-to-ontology-map.jsonl` | Per-paper normalized tags + threat_model + evidence_strength + related_ids |
| `research-relationship-graph.json` | Nodes + typed edges + attack↔defense co-occurrence (the query engine) |
| `syntheses/<category>.md` | 8 category syntheses (20-section) |
| `cross-cutting/*.md` | 8 chapters that emerge only across papers |
| `patterns/*.md` | 28 engineering control playbooks (threat model → control → verification → bypasses → residual risk) |
| `source-index/by-id.md`, `by-category.md`, `relevance-triage.md` | Indexes + core/adjacent/peripheral triage vs Origin/Passport |
| `quality-review/` + `../final-quality-review.md` | 10-perspective adversarial review |
| `../executive-summary.md` | Decision-oriented summary of the whole base |

## Retrieval recipes

Find the right evidence for a decision (fastest → deepest):
1. **Syntheses / patterns first.** `syntheses/<category>.md` for the landscape; `patterns/<control>.md` for a control.
2. **Jump by concept.** `python3 scripts/search.py attack prompt_injection` · `defense policy_gating` · `asset agent_memory` · `surface tool_invocation` · `rel core` · `mitigations prompt_injection` (defenses co-occurring with an attack) · `text "membership inference"` (grep cards).
3. **Graph queries** (`research-relationship-graph.json`): attacks→asset via `targets_asset` edges; defenses↔attack via `attack_defense_cooccurrence`; threat models + evidence via `paper-to-ontology-map.jsonl`.
4. **Depth.** Open the `research-cards/<category>/A#####.md` the synthesis cites.
5. **Confirm.** `source-index/by-id.md` maps id → title / category / arXiv / relevance / evidence strength.

## Rebuild / update / validate

```bash
# from the skill root
python3 scripts/build_manifest.py        # Phase-1 inventory (hashes, pages, arXiv, dup + card coverage)
python3 scripts/assemble_ontology.py     # ontology.{md,json} + paper-to-ontology-map + relationship-graph
python3 tests/validate.py                # §7 gates: card coverage, citation resolution, tag coverage, counts
```
Research cards + syntheses + cross-cutting + patterns are produced by the multi-agent workflow (see
`../RESEARCH_UPDATE_LOG.md` for the incremental procedure). **Reading these summaries does not replace reading
the source PDFs** for a load-bearing decision — cards cite paths in `~/Documents/Research Papers/AAAI-Security-2026/`.

## Maturity & known gaps (read before lifting a pattern as a build spec)

A 10-perspective adversarial review (`../final-quality-review.md`) rated this **fit to ship as a reference /
knowledge skill** but **not yet a build-ready spec** for the Origin/Passport stack. The patterns are
**research-grounded design guidance**, not turnkey blueprints. Un-owned cross-pattern seams the review flagged
(Top-8 #4–8) — treat as **open work**, not settled controls:

1. **Eval-awareness defeater** — "pass an adaptive red-team = launch gate" is defeated by an eval-aware /
   conditionally-defecting agent (A40486, A39480, A41090). Pair every offline gate with a runtime backstop
   (prod canaries, eval-vs-prod divergence, self-inconsistency tripwire, kill-switch).
2. **Root-of-trust is un-owned** — approval / kill-switch / least-privilege all presume an authenticated
   principal that the identity/attestation layer lists as unbuilt. Define fail-closed-when-attestation-unavailable
   per consumer.
3. **Fail-closed ≠ halt for embodied actuators** — "deny/terminate" is wrong for an arm under load; needs a
   per-actuator *safe-state* + reserve/stage/idempotency/dry-run for irreversible effects, and synchronous
   audit-commit before consequential actuation.
4. **No inter-agent (agent→agent) authorization pattern** — every gate sits at the agent→tool boundary; the
   corpus's least-solved case (BU-MA A41134 drops ASR only 7%) has no owning playbook.
5. **No canonical trace-event schema** — `tamper-evident-traces` needs a stable envelope to hash-chain, but each
   pattern emits bespoke fields. Several runtime figures are **transplanted analogies** (e.g. A40925 ~15% is an
   image-classifier consensus gate, not a measured tool-gate residual) — check each figure's origin domain.

## Discipline
Every substantive claim traces to a paper id. Calibrated language only (no *secure / unbreakable / proven safe*).
Conflicting findings are shown with their threat models, not flattened. Frequencies = coverage, not evidence
weight. `insufficient` / `peripheral` tags mean "don't lean on this for an agent-security claim."
