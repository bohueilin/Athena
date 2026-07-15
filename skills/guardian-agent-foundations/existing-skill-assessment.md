# Existing-Skill Assessment (Phase 0)

**Skill:** `guardian-agent-foundations` · **Assessed:** 2026-07-14 · **Assessor role:** senior AI-safety
researcher / security architect / knowledge-systems maintainer.
**Purpose of this document:** decide what to keep, update, deprecate, and add BEFORE the 432-paper corpus
expansion touches the skill, and name the migration risks. No skill files are edited until this is written.

## 1. What the skill currently is

A **reference (not procedural) knowledge base** for the safety/security/trust layer of Origin Physical AI +
Passport, distilled from (a) the Virtue AI research-and-product corpus, (b) the 1Password agent-identity brief, and
(c) a mid-2026 web landscape sweep. Structure:

- `SKILL.md` — worldview, reference-file index, an 8-step "how to apply to Origin" workflow, growing-this-skill.
- `references/worldview.md` — the durable thesis (stateless→stateful, alignment-is-shallow, discover→monitor→govern,
  precision frontier, dynamic-eval, compliance-as-mapping).
- `references/threat-models.md` — agent threat taxonomy (direct/indirect; prompt/tool/skill/environment injection;
  memory poisoning; deep-prefill; collusion).
- `references/architecture-patterns.md` — 13 build patterns (P1 pre-action gate … P13 discovery-before-enforcement).
- `references/agent-identity.md` — ZSP/JIT/attestation, credential broker, 1Password stack, Passport applicability
  matrix + the 2026 identity-market update.
- `references/papers.md` — per-paper digests (TrustGen, SoSBench, RedCodeAgent, ARMs, Any-Depth Alignment,
  BlueCodeAgent, DreamGym, DevOps-Gym, MASTRIKE) + 2026 orbit-paper additions.
- `references/products.md`, `references/regulations.md`, `references/glossary.md`, `references/landscape-2026.md`,
  `references/interview-agent-security.md`.

**Governing lines already present:** "Models propose. A deterministic oracle scores." · "Capability is not
permission." · discover→monitor→govern. These align cleanly with the master prompt's governing principle
("Models propose. Environments verify. Gates decide. Traces prove.") — so the expansion *extends* the existing
worldview rather than replacing it.

## 2. Current strengths (preserve)

- A coherent, opinionated **worldview** that the whole skill hangs on — keep as the spine.
- The **13 architecture patterns** and the **discover→monitor→govern** triad are exactly the "engineering guidance"
  the master prompt wants; the new `patterns/` playbooks should cross-link to them, not duplicate.
- **Evidence discipline already partly present** (per-paper digests with "physical-AI hook"). Good base for
  research cards.
- **Agent-identity depth** (ZSP/JIT/attestation/broker) is unusually strong and directly reusable.
- **Calibrated, non-marketing tone** in most files — matches the master prompt's no-overclaims rule.

## 3. Gaps the corpus expansion must fill

- **Evidence breadth**: current papers.md covers ~18 sources, all Virtue-orbit. The corpus adds **432 AAAI-2026
  papers** across 8 categories (adversarial ML, privacy, IP protection, deepfake, network security) the skill
  barely touches today.
- **No normalized ontology / relationship graph** — can't currently answer "which defenses were tested against
  which threat model, with what evidence, and known bypasses."
- **No per-paper source anchoring at scale** (stable IDs, file paths, extraction quality) — needed for traceable
  citations.
- **No research-to-decision framework** (user-value → threat → capability/permission → verification → evidence →
  metrics → launch gates → residual risk) as an explicit, reusable artifact.
- **No control/design playbooks** in the master-prompt's template form (preconditions, fragile patterns, adaptive
  tests, known bypasses, residual risk, when-not-to-use).
- **No maintenance/update procedure** for adding papers deterministically.
- **Adversarial-ML, privacy, and deepfake evidence** are thin — the skill leans agentic/LLM and identity.

## 4. Unsupported / outdated claims to watch

- Several 2026 landscape facts are single-source web findings (e.g., Virtue founders → Meta) — already tagged with
  confidence; keep tags, don't harden.
- `papers.md` digests were written from summaries, not always the PDFs — the new research-cards (read from the
  actual corpus text) are the higher-integrity layer; where they disagree, cards win and the digest is annotated.
- Any absolute phrasing ("prevents", "guarantees") that slipped in must be re-checked against the no-overclaims
  rule during QA.

## 5. Migration plan (keep / update / deprecate / add)

**Keep (unchanged):** worldview.md, architecture-patterns.md, agent-identity.md, threat-models.md, glossary.md,
regulations.md, products.md, landscape-2026.md, interview-agent-security.md — these remain the curated,
opinionated layer. The corpus layer sits *beside* them.

**Update:** `SKILL.md` — add the corpus/ontology/syntheses/patterns index, the research-to-decision framework,
"how to locate relevant papers", "how to handle conflicting/insufficient evidence", and invocation examples.
`papers.md` — add a pointer to `research-cards/` as the primary evidence layer; annotate any digest that the cards
contradict. `glossary.md` — reconcile terms with the new `ontology.md` (single lexicon).

**Deprecate (mark, don't delete):** nothing wholesale. Any specific numeric claim that the corpus contradicts gets
a deprecation note in CHANGELOG.md with the superseding paper ID.

**Add:** `references/corpus/*` (manifest/audit/exceptions), `references/research-cards/**`, `references/syntheses/*`,
`references/cross-cutting/*`, `references/patterns/*`, `references/ontology.*`, `references/research-relationship-graph.json`,
`references/source-index/*`; plus `scripts/` (inventory + update), `templates/`, `tests/`, `CHANGELOG.md`,
`RESEARCH_UPDATE_LOG.md`, `final-quality-review.md`.

## 6. Migration risks

1. **Bloat / invocation reliability** — 432 cards must NOT go into SKILL.md; they live under references/ and are
   reached by pointers. Risk mitigated by the layered structure. SKILL.md stays concise.
2. **Taxonomy drift** — 117 agents writing cards/syntheses/patterns in parallel could diverge in terminology.
   Mitigation: a fixed ontology vocabulary is embedded in every agent prompt; a consistency pass runs in QA.
3. **Evidence integrity under fan-out** — an agent could invent a metric. Mitigation: every card agent is bound to
   "traceable to the paper text only; label reviewer-synthesis vs author-claim; calibrated language"; QA spot-checks.
4. **Corpus vs curated conflict** — the Virtue-orbit digests and the AAAI cards may frame the same control
   differently. Mitigation: cards are the evidence layer; curated files stay the opinionated layer; conflicts are
   surfaced in cross-cutting/ and CHANGELOG, never silently flattened.
5. **Category mislabeling** — the AAAI "Multi-keyword-match" and "Adversarial-ML" folders contain many papers only
   loosely about agent security (e.g., watermarking, federated clustering). Mitigation: cards record an
   `applicability boundary` and the ontology tags relevance, so retrieval doesn't over-generalize off-topic papers.

**Conclusion:** extend, don't replace. The existing worldview + patterns are the spine; the corpus becomes a
traceable evidence-and-playbook layer beneath a still-concise SKILL.md.
