# Lens Review — Future Retrieval Agent

**Question for this lens:** If a future agent arrives with a *design question* ("how do I gate tool
permissions?", "what mitigates indirect prompt injection?"), can it quickly and deterministically land on the
right paper / card / pattern? Are the ontology, source-index, and cross-links sufficient and internally
consistent?

**Slice read:** all 8 syntheses (`AILLM-Safety`, `Adversarial-ML-Attacks`, `Privacy-Protection`,
`Multi-keyword-match`, `Network-Cyber-Security`, `Model-IP-Protection`, `Deepfake-Forgery-Detection`,
`Defense-Mitigation`); patterns `prompt-injection-containment`, `policy-permission-gates`,
`least-privilege-credentials`, `tool-capability-isolation`, `retrieval-authorization`,
`human-approval-consequential-actions` (+ full `ls patterns/`); `ontology.md` + `ontology.json`;
`source-index/by-id.md`, `by-category.md`, `relevance-triage.md`, `relevance.json`; `README.md`; `scripts/search.py`.
Verified programmatically: citation resolution (patterns and syntheses → `by-id.md`), card files on disk,
relevance-tier counts, arXiv population, ontology-token↔pattern-filename mapping.

**Bottom line up front:** As a *reference store* this base is excellent — **every pointer lands**: all 284
distinct paper ids cited in patterns and all 432 cited in syntheses+cross-cutting resolve in `by-id.md`, all 432
research-card files exist on disk, and the machine index (`relevance.json` 137/245/50) is exactly consistent with
`relevance-triage.md` and `by-category.md`. The weakness is **navigation into the pattern layer** — the exact
layer a *design question* needs. Patterns are reachable only by guessing filenames: there is no crosswalk from an
ontology defense token (or `search.py` output) to a pattern file, and syntheses never link forward to patterns.
An agent entering through either documented front door (the ontology/`search.py` or a synthesis) can retrieve
every relevant paper yet never be routed to the playbook that answers "what do I build."

---

## 1. Concrete findings

### Finding A — No crosswalk from ontology defense tokens (or `search.py`) to the 28 pattern playbooks
**SEVERITY: major**
**Where:** `scripts/search.py` (`defense`, `mitigations` modes), `ontology.md`/`ontology.json` (`dimensions.defenses`),
`README.md` (patterns listed only as the glob `patterns/*.md`); no index file in `patterns/`.

**Exact problem:** The documented retrieval recipe steers an agent to ontology tokens —
`search.py defense policy_gating`, `search.py mitigations prompt_injection` (which returns the defense token
`policy_gating` as its answer). But **nothing maps a defense token to its pattern file**, and the filenames
diverge from the tokens *precisely for the agent-critical enforcement controls*:
`policy_gating`→`policy-permission-gates.md`, `capability_isolation`→`tool-capability-isolation.md`,
`least_privilege`→`least-privilege-credentials.md`, `red_teaming`→`adaptive-red-teaming.md`,
`memory_isolation`→`context-and-memory-isolation.md`, `rollback`→`safe-rollback.md`,
`sandboxing`→`sandboxed-execution.md`. So even a fuzzy filename guess fails on the hops that matter most. The
mapping is also non-total in both directions: 8 defense tokens have **no** lexically matching pattern
(`certified_robustness`, `supply_chain_controls`, `authentication`, `trusted_execution`, `secure_aggregation`,
`rate_limiting`, `query_monitoring`, `crypto_provenance`), while several patterns have **no** ontology token —
`kill-switches.md` (the string `kill_switch` appears **0** times in `ontology.json`), `network-segmentation.md`,
`model-extraction-defenses.md`, `content-provenance.md`, `evaluation-holdout-protection.md`. An agent that
searches the ontology for "kill switch" gets nothing, though a full playbook exists. This is the single largest
retrieval friction in the base.

**Fix:** Add `patterns/INDEX.md`: one table with columns *pattern file · ontology defense token(s) · attacks it
addresses · one-line "use when"*. Then teach `search.py` a `pattern <token|keyword>` mode that resolves a token
or free-text control to the file (and have `mitigations` print the resolved pattern filename next to each defense
token). Add `kill_switch` and any other missing controls to the ontology `defenses` vocab so ontology-driven
search can reach every pattern.

### Finding B — Syntheses never link forward to the patterns (the landscape→control hop is one-way)
**SEVERITY: major**
**Where:** all 8 `syntheses/*.md` and 8 `cross-cutting/*.md`; contrast with the patterns, which link back richly.

**Exact problem:** A grep for `patterns/<name>.md` references across every synthesis and cross-cutting chapter
returns **zero**. Yet the reverse direction is dense — patterns cite sibling patterns constantly (46 references
to `policy-permission-gates.md`, 41 to `tamper-evident-traces.md`, 30 to `tool-capability-isolation.md`, etc.).
The README's fastest recipe is "Syntheses / patterns first" as co-equal entry points, but an agent that lands in
`AILLM-Safety.md` reading that indirect prompt injection is "the single most product-relevant threat" has **no
pointer** to `prompt-injection-containment.md`, `policy-permission-gates.md`, or `tool-capability-isolation.md`
— the very controls that answer it. The 51 prose uses of the word "pattern" in the syntheses are not links.

**Fix:** Add an "Operational controls" line to each major synthesis section (or a footer table per synthesis)
naming the relevant `patterns/*.md`. E.g., the `AILLM-Safety` indirect-injection section →
`prompt-injection-containment.md`, `policy-permission-gates.md`, `tool-capability-isolation.md`,
`human-approval-consequential-actions.md`. This closes the loop the pattern-side already implements.

### Finding C — README's retrieval guide points to two files that don't exist
**SEVERITY: minor**
**Where:** `references/README.md`, artifact table — rows `quality-review/ + ../final-quality-review.md` and
`../executive-summary.md`.

**Exact problem:** `../final-quality-review.md` (skill root) and `../executive-summary.md` (skill root) are both
**absent** (verified: neither at the skill root nor under `references/`). A retrieval agent following the pointer
to the "10-perspective adversarial review" roll-up or the "decision-oriented summary of the whole base" hits a
dead link — and the executive summary is exactly what a time-boxed agent would open first. (The per-lens
`quality-review/_lens-*.md` files *do* exist; only the roll-up and the exec summary are missing.)

**Fix:** Create both files, or mark the two rows "(pending)" / remove them until built, so the front-door index
never advertises a missing target.

### Finding D — `by-id.md` category column is truncated, so the advertised id→card path can't be built from it
**SEVERITY: minor**
**Where:** `source-index/by-id.md` (`cat` column) vs. README retrieval steps 4-5, and the on-disk folders
`research-cards/<Full-Category>/`.

**Exact problem:** README steps 4-5 tell the agent to open `research-cards/<category>/A#####.md` using the id and
`by-id.md`. But `by-id.md` renders the category truncated — `Adversaria`, `Multi-keyw`, `Network-Cy`,
`AILLM-Safe`, `Model-IP-P`, `Deepfake-F`, `Privacy-Pr`, `Defense-Mi` — none of which equal the actual folder
names (`Adversarial-ML-Attacks`, `Multi-keyword-match`, `Network-Cyber-Security`, `AILLM-Safety`,
`Model-IP-Protection`, `Deepfake-Forgery-Detection`, `Privacy-Protection`, `Defense-Mitigation`). So the card
path cannot be constructed mechanically from the human index; the working paths (full `category` in
`paper-to-ontology-map.jsonl`, or `search.py text`) are the undocumented workaround. Patterns compound this by
citing ids in prose only (e.g. "A41134 non-adaptive defense eval") with no folder or filename.

**Fix:** Either stop truncating the `cat` column in `by-id.md`, or add one line to README step 4 — "card paths:
resolve full category from `paper-to-ontology-map.jsonl`, or `python3 scripts/search.py text A#####`" — so the
id→card hop is deterministic.

### Finding E — `by-id.md` advertises an arXiv lookup column that is 98% empty
**SEVERITY: minor**
**Where:** `source-index/by-id.md` (arXiv column); README "Confirm" step 5 ("maps id → title / category / arXiv /
relevance / evidence strength"); `corpus-manifest.jsonl` (`arxiv_id`).

**Exact problem:** Only **7 of 432** rows have a non-empty arXiv field (`arxiv_id` is `null` throughout the
manifest). The README names arXiv as one of the five things `by-id.md` resolves to, implying a retrieval agent
can hop from an id to the arXiv source — but the column is effectively dead, so that hop almost always wastes a
step and can read as "source unknown."

**Fix:** Drop arXiv from the advertised `by-id.md` lookup (and/or the column) until populated, and instead point
agents at the card's PDF path under `~/Documents/Research Papers/AAAI-Security-2026/` for the source hop.

---

## 2. What is DONE WELL

- **Citation integrity is airtight — the property that matters most for retrieval.** Every one of the 284
  distinct paper ids cited across all patterns, and all 432 cited across syntheses + cross-cutting, resolves in
  `by-id.md`; all 432 `research-cards/<cat>/A#####.md` files exist on disk; **zero** dangling pointers. An agent
  that follows any citation always lands on a real card.
- **Redundant retrieval paths that agree with each other.** `ontology.json`/`.md` + `paper-to-ontology-map.jsonl`
  + `research-relationship-graph.json` + `search.py` (7 query modes, incl. attack↔defense co-occurrence via
  `mitigations`) + three source-index views. Crucially the machine and human indexes are **consistent**:
  `relevance.json` tiers are exactly 137 core / 245 adjacent / 50 peripheral, matching `relevance-triage.md` and
  the `by-category.md` per-category counts — no silent drift between the layers an agent would cross-check.
- **The pattern layer is a dense, well-labeled internal web.** Patterns bidirectionally cross-link siblings, cite
  their grounding syntheses and load-bearing ids, and consistently tag numbers author-reported-vs-reviewer with
  calibrated language ("reduced ASR under the evaluated threat model"). Once an agent is *inside* the pattern
  layer, lateral navigation to adjacent controls and back to evidence is excellent.

## 3. Biggest risk from my seat

The layer a design question actually needs — the engineering pattern — is a **reachability island**: there is no
defense-token/attack→pattern crosswalk and no synthesis→pattern link, so an agent entering through either
documented front door (the ontology/`search.py` or a synthesis) can retrieve every relevant paper and still never
be routed to the playbook that answers "what do I build."
