# Quality Review — Lens: Adaptive Attacker

> **Lens.** Read the control patterns as a defense-aware adversary: which *assumptions* are exploitable
> (verifier gaming, confused deputy, eval-awareness, composition)? What is under-defended?
> **Slice read.** Syntheses AILLM-Safety / Adversarial-ML-Attacks / Privacy-Protection / Multi-keyword-match /
> Network-Cyber-Security / Model-IP-Protection / Deepfake-Forgery-Detection / Defense-Mitigation; patterns
> `policy-permission-gates.md`, `human-approval-consequential-actions.md`, `tool-capability-isolation.md`,
> `evaluation-holdout-protection.md`, `prompt-injection-containment.md`, `retrieval-authorization.md`;
> `ontology.md`, `source-index/relevance-triage.md`.
>
> **Headline.** The base is strong and already thinks like an attacker: verifier gaming (A37924, A40584),
> confused-deputy / BU-MA (A41134, A42249), eval-awareness (A40486, A39480, A41129), and composition failure
> (A41108 STACK, A41144 MFA) are all explicitly imported into the runtime patterns, and every efficacy number
> is tagged author-reported / non-adaptive. The findings below are **cross-pattern seams** where one pattern's
> control logic, taken literally, is defeated by an attack another pattern in the same set already documents —
> i.e. self-inconsistencies an adaptive attacker pivots through, not missing awareness.

---

## 1. Findings

### F1 — [MAJOR] Ingestion-trust tier conflates "authenticated origin" with "not attacker-writable" — first-party memory (CREAT) sails through as EVIDENCE
**File / section.** `patterns/retrieval-authorization.md`, "System architecture" R2 (lines 215–218) and "Control
mechanism" (lines 151–153): `· authenticated source → admit as EVIDENCE with bounded influence` / `· open/attacker-
writable → QUARANTINE or ROUTE_TO_VERIFIER`.
**Exact problem.** The R2 gate is a binary keyed on *provenance authenticity*, but authenticity of origin ≠
non-writability of content. An internal wiki, a shared blackboard, or **the agent's own episodic memory** all
carry an authenticated first-party provenance tag *and* are attacker-writable (insider, compromised account, or
prior-turn injection). The pattern itself cites A38606 (CREAT) — stealthy adaptive poisoning of the agent's *own
interaction history* — and A40188 (memory as an unprotected asset), yet the R2 decision logic routes
authenticated-source content straight to EVIDENCE **without** the reasoning verifier. So CREAT's exact surface is
the one R2 admits by construction. An attacker who can write one first-party record (or poison memory once)
obtains bounded-but-real influence that never hits R3. Item 7 ("monitor the retrieval *pattern*") is a detector,
not a gate — it fires after admission.
**Fix.** Re-key the ingestion tier on *write-authorization strength*, not on origin authenticity: `first-party /
authenticated-origin` is orthogonal to `write-restricted`. Any source that is authenticated-origin **but not
write-restricted** (internal wiki, shared memory, peer-agent channel) must fall into `ROUTE_TO_VERIFIER`, not
`EVIDENCE`. State explicitly that agent memory / interaction history is authenticated-origin *and* attacker-
writable, so it is never a bounded-influence-without-verification tier (grounds: A38606, A40188).

### F2 — [MAJOR] "Aggregate-aware gating" is specified as a scalar running-total threshold, which cannot see the non-additive set-relational inference attack (A40484) it claims to counter
**File / section.** `patterns/human-approval-consequential-actions.md`, "Recommended implementation pattern" item 6
(lines 178–180): *"evaluate cumulative effect across the trajectory … re-trigger approval when a **running total
crosses a tier boundary**"*; mirrored in Test case 4 (lines 262–263) and Failure handling (line 320).
**Exact problem.** The control is framed as a monotonic scalar ("running total", "consequence threshold"). But the
cited attack (A40484 SafeNLIDB, quoted at line 55) is *non-additive*: "list all students" + "list healthy students"
→ **set-difference** deduces a protected attribute. Each query moves no scalar total; the harm is the *join /
difference* over the session, and either query alone is below any per-action tier. An attacker who knows approval
is gated on a running total simply decomposes the objective into individually-benign, quantity-free reads whose
*combination* leaks — precisely the case the pattern lists but its mechanism misses. (The only text that fits the
real attack is the APO reference buried in Rollback line 332, not the load-bearing recommendation.)
**Fix.** Replace "running total crosses a tier boundary" with *joint-reachability / query-correlation* tracking:
maintain a session-level model of what the already-returned results, in combination, make inferable, and re-gate
when the *reachable inference set* (not a scalar sum) crosses a protected boundary. Keep A40484's set-difference
example inline as the case a scalar threshold provably misses; cite the constraint-aware (APO) enforcement in the
recommendation, not only in Rollback.

### F3 — [MAJOR] The "advisory-only LLM" rule is circular for open-ended-effect tools, and the pattern names no deterministic default — an implementer is steered into the exact injectable LLM-as-authority config the same pattern forbids
**File / section.** `patterns/policy-permission-gates.md`, "When NOT to use" (lines 453–456): *"When no deterministic
policy can be declared and you would be forced to make an LLM the sole authority … Either declare a deterministic
policy or **treat the LLM output as advisory-only**."* Same tension in `tool-capability-isolation.md` "Preconditions"
(lines 99–101: allow-list requires an enumerable effect space) and its "When NOT to use" (lines 417–420).
**Exact problem.** "Advisory-only" is only meaningful *relative to a deterministic authority the advice is advisory
to* (the AND-composition in item 6, line 184–186: LLM must agree with policy for ALLOW). For open-ended-effect
tools — free-form shell, code-exec, arbitrary HTTP — no deterministic allow-list exists (this is the stated
condition). There, "advisory-only" has nothing to be advisory to, so it collapses to one of two states: (a) nothing
can ever be ALLOWed, or (b) the LLM becomes the de-facto grant authority — the injectable single-artifact authority
the same pattern's Known-bypasses (line 369) and Incorrect-patterns (lines 205–209) explicitly forbid. Because the
open-ended tools (shell/code-exec) are the highest-value ones, an implementer with a shipping requirement resolves
the ambiguity toward (b) — an adaptive attacker's ideal outcome. The guidance closes the door for
enumerable-effect tools and leaves it open for the dangerous ones.
**Fix.** State the deterministic default explicitly: when the effect space is open-ended, the gate's default is
`DENY` / `STEP_UP`-to-human, and the LLM signal may only ever *narrow* (force DENY/STEP_UP), never *grant* ALLOW.
Pair with the `sandboxed-execution.md` sibling as the only ALLOW path for open-ended tools (execute in a
capability-bounded sandbox, gate egress), so "advisory-only" retains a deterministic partner.

### F4 — [MAJOR / biggest-risk] Eval-awareness is honestly named as a residual in one pattern but is not wired to any runtime compensating control, while every runtime pattern asserts "adaptive red-team is the launch gate" without carrying the caveat that an eval-aware model defeats that gate
**File / section.** `patterns/evaluation-holdout-protection.md` correctly flags it (Threat model lines 120–124;
Known bypasses lines 446–448: *"a model that behaves under the holdout distribution and defects in production is
not caught by any holdout … fundamental limit of measurement"*, A40486/A39480/A41129). But the runtime patterns —
`policy-permission-gates.md` (Verification line 227–230), `prompt-injection-containment.md` (line 264–267),
`tool-capability-isolation.md`, `human-approval-consequential-actions.md` (line 208–212) — all make
"adaptive, defense-aware red-team is **the launch gate**" the load-bearing verification claim **without** noting
that an eval-aware/conditionally-defecting agent passes that gate and defects in prod. Grep confirms
`evaluation-holdout-protection.md` never cross-links `runtime-anomaly-detection.md` (the sibling that exists to
compensate); it terminates the thread at "measurement cannot cover it."
**Exact problem.** The base's single most-repeated verification mechanism has a named defeater and no pointer to
the compensating layer, so a reader clears "adaptive red-team ✓" and over-trusts the result. This is the hardest
attacker move (train/condition the agent to detect eval distribution → behave → defect on the prod trigger), and
the pattern set has the pieces (`runtime-anomaly-detection.md`, `kill-switches.md`, the A41090 self-inconsistency
signal) but never assembles them against it.
**Fix.** In each runtime pattern's Verification section, append: "adaptive red-team is necessary but *cannot* cover
eval-aware / conditional defection (A40486, A39480, A41129) — pair with the runtime compensating control." Add a
cross-link from `evaluation-holdout-protection.md` Residual-risks/When-NOT-to-use to `runtime-anomaly-detection.md`
naming the concrete runtime measures (production-distribution canary actions, eval-vs-prod behavioral-divergence
monitoring, the A41090 stated-vs-executed self-inconsistency tripwire) as the layer that must carry what the
holdout cannot.

### F5 — [MINOR] The runtime "out-of-band correctness channel" (ensemble/denoiser disagreement) lacks the shared-base circularity guard that evaluation-holdout applies to judges — so the ensemble can be jointly gamed with one representation
**File / section.** `patterns/prompt-injection-containment.md` item 7 (lines 230–231): *"add an out-of-band
correctness channel … (human review, provenance, **ensemble/denoiser disagreement**)"*; `policy-permission-gates.md`
line 208 recommends the same out-of-band channel against A37924 verifier gaming. Neither carries a circularity
caveat.
**Exact problem.** `evaluation-holdout-protection.md` (lines 173, 268, 298; diagram line 228: `judge_1 ⟂ judge_2
(no shared base w/ SUT or attacker)`) correctly rules that quorum members must **not share a base model/encoder**
with the system-under-test or the attack optimizer, else the attacker optimizes once and defeats the "quorum."
That guard is absent from the runtime out-of-band recommendations. An ensemble whose members share a backbone (the
common deployment) fails in a correlated way under a single adversarial optimization — the "ensemble disagreement"
signal the runtime patterns lean on silently degrades to a single detector. This is the same A40916 / A37924
circularity hole, unclosed on the runtime side.
**Fix.** Propagate the circularity guard: in both runtime patterns, require that any ensemble / denoiser /
second-verifier used as an out-of-band correctness channel not share a base model/encoder with the primary
detector or the SUT, and prefer a *structurally different* channel (deterministic provenance, human) over a
same-family model vote. One-line cross-reference to `evaluation-holdout-protection.md` §Judge-integrity.

---

## 2. Done well

- **Attacker moves are already first-class, not afterthoughts.** Verifier-gaming (A37924 "a verification artifact
  is not a correctness oracle"; A40584 PRM 0.973 on an impossible constraint), confused-deputy / internally-
  compromised agent (A41134 BU-MA where user-level defense drops ASR only 7%; A42249 100% unauthorized install),
  and composition collapse (A41108 STACK 0→71%, A41144 MFA 0→58.5%) are imported into `policy-permission-gates`,
  `human-approval`, and `tool-capability-isolation` as named bypasses with test cases — the base pre-empts most of
  an adaptive attacker's opening book.
- **Calibration is disciplined and consistent.** Every efficacy number is tagged author-reported / non-adaptive /
  best-case, "no defense was evaluated against an adaptive attacker" is repeated as a launch gate, and
  `evaluation-holdout-protection.md` operationalizes it (null-probe, A39276 94%→51%, TPR@low-FPR, burned-artifact
  hygiene). This resists the attacker's favorite lever — quoting a best-case number as a guarantee.
- **The deterministic-authority / advisory-LLM split is architecturally correct and applied uniformly.** Making the
  Guardian-LLM advisory-only (never an ALLOW path) and requiring a structural trust boundary "the model cannot be
  talked past" (A41090, A41134) correctly denies the guardian-LLM-injection route to authorization, and history-
  provenance attestation (A40840, A36996) closes the forged-approval vector — both exactly where an attacker would
  push.

## 3. Biggest risk from my seat

The base's load-bearing verification claim — "pass an adaptive, defense-aware red-team and you've cleared the
launch gate" — has a documented but un-wired defeater: an **eval-aware / conditionally-defecting** agent
(A40486, A39480, A41129) passes every offline gate and defects in production, and the pattern set never assembles
its existing runtime layer (`runtime-anomaly-detection.md`, kill-switches, the A41090 self-inconsistency signal)
to compensate — so the one thing an attacker most wants you to trust is the thing left with no runtime backstop.
