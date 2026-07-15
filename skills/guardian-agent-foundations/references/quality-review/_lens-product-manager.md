# Quality Review — Lens: Product Manager

> **Lens question.** Is the guidance *decision-oriented* — does it read like PRDs / launch-gates / residual-risk
> ownership a team can act on — rather than a literature dump? Are **user value** and **friction** addressed?
>
> **Verdict up front.** The base is genuinely decision-oriented and, for a research-to-engineering distillation,
> unusually close to shippable product artifacts. It is *not* a literature dump. My findings are about the last
> integration step — ownership, a dead index link, and unset thresholds — not about the substance, which is
> strong. Two apparent gaps I chased (friction absent in `least-privilege-credentials` / `runtime-anomaly-detection`)
> turned out to be false alarms from a hyphenation-sensitive grep; both patterns handle friction well and I did
> **not** file them.

---

## 1. Findings

### Finding A — Launch gates and residual risks are **ownerless** (no RACI / accountable sign-off)
**SEVERITY: major**
**Where:** `cross-cutting/defense-in-depth.md` §10 "Launch-gate synthesis" (10 gates, each CPVER-tagged, zero
owners); every `patterns/*.md` "Metrics and thresholds", "Residual risks", and "Launch and assurance implications"
sections; syntheses §16 (e.g. `syntheses/Network-Cyber-Security.md` "Adopt these as pre-deployment red-team KPIs").

**Problem:** The KB deliberately adopts launch-review voice — "a pre-deployment requirement, not a post-hoc
metric" (defense-in-depth §10 preamble), "Adaptive red-teaming is a launch gate, not a nice-to-have"
(`patterns/human-approval-consequential-actions.md` §Verification), "report absolute residuals, not only relative
reductions." Having taken on that voice, it never names **who** signs a gate off or **who** owns each residual.
The token "owner" appears in the corpus only as *asset*-owner (model/data owner — `model-extraction-defenses.md`,
`signed-provenance.md`), never as an accountable role. A PM cannot run a go/no-go review off an ownerless gate
list: gate #5 says "report absolute residual… present empirical robustness as risk-reduction, never proof" — but
somebody has to be the person who *accepts* that residual, and the KB leaves that seat empty. This is precisely
the "residual-risk owner" leg of the decision-orientation bar, and it is the one leg missing.

**Fix:** Add a RACI/owner hook — a one-line **"Sign-off owner / residual acceptance"** per gate in
defense-in-depth §10 (role placeholders are fine: *release owner signs the gate; security lead accepts the
residual*), and an "Owner" field in each pattern's "Metrics and thresholds" section. One field per gate, not a
rewrite; the CPVER tag already tells you the control class, this adds the accountable party.

### Finding B — README's "fastest path to a decision" points at files that **don't exist**
**SEVERITY: major**
**Where:** `references/README.md` — artifact table row "`../executive-summary.md` — Decision-oriented summary of
the whole base" and "`quality-review/` + `../final-quality-review.md` — 10-perspective adversarial review";
Retrieval-recipes lead with "Syntheses / patterns first."

**Problem:** Verified with `find` across the whole skill: **neither `executive-summary.md` nor
`final-quality-review.md` exists anywhere** (skill root holds only `SKILL.md`, `CHANGELOG.md`,
`RESEARCH_UPDATE_LOG.md`, `existing-skill-assessment.md`). The executive summary is the artifact a busy PM opens
*first* for a go/no-go; the top-of-index promise of a "Decision-oriented summary of the whole base" is a dead
link. Separately, `quality-review/` is advertised as "10-perspective" but currently contains 4 lens files
(`_lens-adversarial-ml-researcher`, `_lens-ai-safety-researcher`, `_lens-privacy-engineer`,
`_lens-security-architect`) — expected mid-build, but the README states it as done.

**Fix:** Create `executive-summary.md` (highest-leverage single doc for this lens), or remove the row until it
exists. Mark `final-quality-review.md` and the "10-perspective" review as **"(pending / in progress)"** so the
navigation index does not over-promise the decision fast-path.

### Finding C — Metrics are **named but unvalued**; the KB stops one step short of a droppable launch gate
**SEVERITY: minor** (the underlying honesty is correct — see note)
**Where:** every `patterns/*.md` "Metrics and thresholds", exemplified by
`patterns/human-approval-consequential-actions.md`: *"The corpus provides no validated threshold for a
human-approval gate specifically (not stated in paper). … the numeric targets are engineering defaults requiring
production validation."* Same shape in syntheses §16.

**Problem:** You get the metric *vocabulary* (unapproved-consequential-execution rate, over-prompting /
false-approval-request rate, residual ASR/ADR) but no *target value* to paste into a PRD acceptance criterion, so
the reader must still author every threshold. **Note:** this is the correct behavior — inventing numbers would
violate the base's evidence-integrity contract, and the KB is right not to fabricate them. So this is not a rigor
defect; it is a usability gap between "honest about the unknown" and "usable as a gate."

**Fix:** Bridge with *method, not numbers*: add a short "how to set the starter threshold" note per metric —
e.g., "gate `unapproved-consequential-execution` at 0 **by construction, not measurement** (fail-closed)"; "derive
the over-prompting ceiling from a 2-week shadow run and A/B against an adaptive benign-ambiguous set." That turns
"not stated in paper" into an actionable starting procedure without inventing a corpus value.

### Finding D — **User value** (the enabling benefit) is under-articulated relative to **friction** (the cost)
**SEVERITY: minor**
**Where:** patterns' "Problem addressed" sections — e.g. `patterns/human-approval-consequential-actions.md`,
`patterns/policy-permission-gates.md` — are framed almost entirely as harm-reduction.

**Problem:** Friction/cost is covered well (approval fatigue, over-block, "When NOT to use"), but the *enabling*
value proposition is left implicit. A human-approval gate's product value is "**it lets a user safely delegate
irreversible actions**" — an adoption/trust unlock — yet the docs present it only as "the residual is survivable."
A PM writing the PRD needs the "why a user wants this / what capability it unlocks" line, not only the risk story.
The KB is risk-complete but value-thin.

**Fix:** Add one **"User value / capability unlocked"** line to each pattern's "Problem addressed," complementing
the existing harm framing. Low severity — the audience is engineering and the value is inferable, but stating it
sharpens every pattern's PRD-readiness.

---

## 2. What is done well

1. **Genuinely decision-oriented — this is not a survey.** Every synthesis carries dedicated §14 *Product design
   implications*, §15 *Architecture implications*, and §16 *Launch and assurance implications*;
   `cross-cutting/defense-in-depth.md` §10 is a consolidated, CPVER-tagged, **pre-deployment launch-gate
   checklist** a team can adapt directly; and all 28 `patterns/*.md` carry Problem→Threat→Control→Metrics→Test
   cases→Telemetry→Failure-handling→Residual-risks→"When NOT to use." `human-approval-consequential-actions.md`
   in particular reads like a finished runbook (fail-closed failure handling, 7 attack-mapped test cases, adaptive
   red-team tests). This clears the "PRD/launch-gate" bar comfortably.

2. **Friction / usability cost is first-class, not an afterthought.** All 28 patterns have a **"When NOT to use
   this pattern"** section (real scope discipline — e.g. `least-privilege-credentials.md` cross-refs
   `policy-permission-gates` and says "prefer elimination to scoping"). Over-refusal / false-positive / alert
   fatigue is a repeated first-class metric: `input-output-detection.md` is saturated with it,
   `runtime-anomaly-detection.md` insists a detector is "a **triage aid**, not a gate… real-world F1 ≈ 0.3–0.6,"
   `human-approval-consequential-actions.md` treats **approval fatigue** as a named bypass and risk-tiers to
   preserve usefulness, and defense-in-depth §10.6 makes "instrument over-refusal against an adaptive
   benign-ambiguous set" an explicit launch gate. The safety/utility trade-off is never wished away.

3. **Residual risk is quantified and honest — exactly the realism a launch decision needs.** Real surviving
   numbers are carried, not hidden: A42191 ~31% residual ASR, A40248 ~16%, A40432 ~28% chunk-recovery,
   A40925 ~15% residual activation; the standing rule is "report absolute residual, not relative reduction"
   (defense-in-depth §10.5). Conflicting findings are shown with their threat models, not flattened
   (`syntheses/AILLM-Safety.md` §10; Adversarial-ML §10), and every headline is qualified "author-reported…
   requires production validation." A PM gets a truthful risk picture instead of a marketing one.

---

## 3. Biggest risk from my seat

**The base has the gates, the residual numbers, and the friction metrics — but no owner on any gate and no target
value in any metric — so a team can read it as "done" and ship with nobody actually accountable for the residual
and no committed threshold; and the one artifact a PM would open first (`executive-summary.md`) is a dead link in
the README.**
