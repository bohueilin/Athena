# Quality Review — Lens: AI Safety Researcher

**Focus:** jailbreak / prompt-injection / agentic-risk claims — are findings calibrated,
adaptive-attacker-aware, and not overclaimed as production safety?

**Slice reviewed:** `syntheses/AILLM-Safety.md` (full, 63 papers) + spot-checks of the 7 other
syntheses; `patterns/adaptive-red-teaming.md` (full), `patterns/prompt-injection-containment.md`
(full), plus `human-approval-consequential-actions.md`, `context-and-memory-isolation.md`,
`tool-capability-isolation.md`, `least-privilege-credentials.md`, `policy-permission-gates.md`;
`ontology.md`; `source-index/relevance-triage.md`. Cross-checked numbers against
`landscape-2026.md`, `interview-agent-security.md`, `agent-identity.md`.

**Bottom line:** This is, at the claim level, an unusually well-calibrated knowledge base — the
adaptive-attacker gap is correctly named as the central weakness, language is disciplined, and
author-reported results are kept distinct from reviewer synthesis. **No blocking issues.** The
findings below are calibration refinements and one structural gap that matters from an agent-safety
seat. The base is fundamentally solid; I did not manufacture defects to fill a quota.

---

## 1. Findings

### F1 — [MAJOR] The flagship meta-claim is stated as a near-universal law; it's a cross-domain extrapolation
**Where:** `patterns/adaptive-red-teaming.md:13` (and propagated verbatim to
`patterns/evaluation-holdout-protection.md:21`, `patterns/kill-switches.md:105`,
`patterns/human-approval-consequential-actions.md:72`).

**Problem:** The load-bearing thesis — *"wherever an attacker is allowed to be defense-aware, the
defense degrades or fails"* — is phrased with a universal quantifier and copied into ≥4 patterns as
the "highest-confidence meta-finding." But the adaptive-attack evidence that supports it is (a)
modest in count and (b) drawn substantially from **non-LLM domains**: FL aggregators (A40787
ShadeEdit, A39290 Pill), watermark removers (A40905, A39997, A37010), and VLM output-repetition
(A41144). It is then generalized to LLM/agent defenses — precisely the region where
`AILLM-Safety.md` §17 says adaptive evaluation is *"near-totally absent,"* i.e. where we have the
**fewest** in-domain datapoints. The base's own cited exemplar, **A37350 (EigenShield)**, is the one
AILLM defense evaluated in standard + *adaptive* + OOD settings and is held up as doing it *right*
(`adaptive-red-teaming.md:26,550`) — it does not cleanly "fail," which cuts against the universal.

**Why it matters (my lens):** This is the single place where the base's rhetoric outruns its sample.
An over-strong "all defenses fail adaptively" prior can justify either fatalism ("nothing works") or
its mirror ("so our red-team pass is the real proof") — both are miscalibrations the base otherwise
avoids.

**Fix:** Reword at the source and attach the counter-nuance at the point of claim:
*"Wherever it has been tested, a defense-aware attacker has substantially degraded or defeated the
evaluated defense — a strong directional prior extrapolated across domains, not a proven universal;
the one adaptively-evaluated AILLM defense (A37350) survived with honest asymptotic caveats."* Either
keep the universal out of the four downstream patterns or carry the caveat with it.

### F2 — [MAJOR] Injection-containment under-elevates data exfiltration and never cross-links the base's own Rule-of-Two / lethal-trifecta egress gate
**Where:** `patterns/prompt-injection-containment.md` — exfiltration appears only as one test case
(`:327`, `send_email`) and one telemetry field (`:378`, egress primitives). The Threat model and
Control mechanism sections frame injection harm almost entirely as *unauthorized action execution*.
Meanwhile the base clearly knows the exfiltration framing: `landscape-2026.md:97-99` and
`interview-agent-security.md:15,34` name *"private data + untrusted content + external comms"* (the
lethal trifecta) as **"the floor"** and claim a **live Rule-of-Two egress gate**
(`agent-identity.md:164`).

**Problem:** The pattern that actually owns injection guidance does not present *silent
read-then-exfiltrate* — arguably the dominant real-world indirect-prompt-injection harm — as a
first-class threat class, and does not cross-link the Rule-of-Two/egress-leg material that the rest
of the base treats as the baseline control. An implementer following this pattern could build
action-gated containment (block the harmful *actuation*) while leaving the confidentiality/egress
channel open.

**Fix:** Add a first-class **"Data exfiltration / confidentiality breach"** bullet to the Threat
model, add a named **egress-control / break-a-trifecta-leg** mechanism to Control mechanism, and
cross-link `policy-permission-gates.md` + the `landscape-2026.md` / `interview-agent-security.md`
Rule-of-Two material so breaking an egress leg reads as the floor, not an afterthought.

### F3 — [MINOR] "Most directly transferable architecture" is abstracted from a single Preliminary paper without a co-located caveat
**Where:** `syntheses/AILLM-Safety.md:403-405` (§15) and the System-architecture section of
`patterns/prompt-injection-containment.md`.

**Problem:** The four-layer cognitive-cycle architecture (input → tool-plan validation →
pre-execution gate → audit) is presented confidently as *"the most directly transferable
architecture."* It is abstracted almost entirely from **A41468**, which the same pattern elsewhere
correctly rates **Preliminary** — no adaptive test, no FP accounting, no dataset size, no artifacts
(`prompt-injection-containment.md:456,519`). The hedge exists, but it is not co-located with the
confident architecture claim, so a section-skimming reader gets the confident version and misses the
Preliminary status.

**Fix:** Attach the caveat inline: *"(design abstraction from one Preliminary paper, A41468;
conceptually — not empirically — corroborated by A41090)."* Frame it as a **design hypothesis to
validate**, not a robust blueprint.

### F4 — [MINOR] Wording error inverts the polarity of a load-bearing bypass claim
**Where:** `syntheses/AILLM-Safety.md:295`.

**Problem:** *"A deployed representation-level defense (Circuit-Breakers / Representation Rerouting)
was reportedly **led by** A40551's multi-direction ablation."* The intended meaning (confirmed by
context and by `adaptive-red-teaming.md:552`) is that the defense was **bypassed/defeated**. As
written, "led by" is ambiguous and can be read as the defense *winning* — the opposite polarity — in
a sentence whose whole point is that the defense was broken.

**Fix:** Replace "led by" with **"bypassed by"** (or "defeated by").

### F5 — [MINOR] The enforcement half of "capability ≠ permission ≠ safety" is thinly corpus-grounded and single-vendor-framed
**Where:** `ontology.md:34` (only **7 / 432** papers touch `tool_credentials`; `identity_authz` = 49)
vs. the weight the enforcement thesis carries in `least-privilege-credentials.md`,
`policy-permission-gates.md`, and the syntheses' §14–15 product/architecture guidance.

**Problem:** The agentic *enforcement* guidance (least privilege, Zero-Standing-Privilege / JIT,
credential broker, Rule-of-Two) rests on a very small corpus footprint plus the 1Password *"Identity
for Reasoning Agents"* brief. The credentials pattern is **commendably explicit** about this — every
such claim is tagged *(agent-identity brief)* and flagged as *"engineering practice, not a measured
attack/defense"* (`least-privilege-credentials.md:17-18`). The residual risk is subtler: when this
single-vendor framing is presented in the syntheses next to peer-reviewed *attack* results, a reader
can absorb it as equally evidence-backed, and the stack inherits one vendor's product framing as if
it were corpus consensus.

**Fix:** Carry a one-line vendor-framing caveat to the *syntheses* wherever the enforcement thesis is
stated (not only in the credentials pattern): the enforcement mechanics are industry practice from
one vendor brief and a 7-paper corpus slice, independent of the corpus's measured attack findings.

---

## 2. What is done well

- **DW1 — Evidence-integrity discipline is best-in-class and consistently applied.** Author-reported
  vs. reviewer-synthesis is separated everywhere; "not independently verified," "requires production
  validation," "no absolutes," and "not stated in paper" (for truncated cards) are used
  systematically. Numbers I cross-checked are internally consistent: the evidence-strength
  distribution sums (312+65+38+17 = 432), the relevance-triage tiers sum (137+245+50 = 432), and the
  A41468 ADR residuals in `prompt-injection-containment.md:461` match the §11/§16 residual claims in
  `AILLM-Safety.md`. This is rare and load-bearing.

- **DW2 — The adaptive-attacker gap is correctly identified as *the* central methodological weakness
  and promoted to a fail-closed launch-gate meta-control.** `adaptive-red-teaming.md` treats
  defense-aware evaluation as a program (not an event), foregrounds oracle-gaming and measurement
  circularity (A40584 PRM 0.973 on an invalid step, A40866 untested against gaming, A40916 circular
  scoring), and closes with an honest "a pass is not a proof / no corpus defense is certified against
  an adaptive adversary" residual-risk section. This is exactly the right instinct and is usually
  absent from practitioner knowledge bases.

- **DW3 — The base is anti-overclaim by construction.** "Gate, not replace, least privilege,"
  residuals-reported-absolute-not-relative, over-refusal / false-positive rate elevated to a
  first-class metric, honest-negative results valorized (A37117 broken-then-fortified, A41118 LAT
  mitigates its own backdoor), and every pattern carries a "When NOT to use this pattern" section
  that actively discourages over-application and single-control reliance. The material repeatedly
  tells the reader its own guidance is insufficient alone.

---

## 3. Biggest risk from my seat

The calibration is excellent at the **claim** level, but the confident, detailed *System
architecture* + *Recommended implementation pattern* blueprints — abstracted largely from one
Preliminary paper (A41468) and one vendor brief — *look* like validated, production-ready designs, so
a reader could lift them into a real guardian stack and treat them as production safety, precisely
the overclaim the prose everywhere disavows.
