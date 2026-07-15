# Quality Review — Lens: Red-Team Operator

**Scope reviewed:** 8 syntheses (AILLM-Safety, Adversarial-ML-Attacks, Privacy-Protection,
Multi-keyword-match, Network-Cyber-Security, Model-IP-Protection, Deepfake-Forgery-Detection,
Defense-Mitigation); all 28 `patterns/*.md` — specifically every **Known bypasses** and **Adaptive
adversarial tests** section; `ontology.md`; `source-index/relevance-triage.md`.

**Lens question:** Are "Known bypasses" and "Adaptive adversarial tests" concrete and non-trivial, or
hand-wavy? Where would these controls actually break?

**One-line verdict:** The base is *strong* — genuinely concrete, paper-grounded, and honestly calibrated,
well above typical threat-model boilerplate. It does not fail. The defensible criticisms are about
**where the concreteness is thinnest and most transplanted**, and that thinness lands precisely on the
runtime controls Origin/Passport ship. Findings below are calibration, not condemnation.

---

## 1. Findings

### F1 — MAJOR — Transplanted numbers create *false concreteness* on the runtime patterns
**Where:** `Known bypasses` / `Adaptive adversarial tests` across `network-segmentation.md`,
`sandboxed-execution.md`, `tool-capability-isolation.md`, `incident-containment.md`,
`runtime-anomaly-detection.md`, `tamper-evident-traces.md`, `least-privilege-credentials.md`,
`policy-permission-gates.md`, `prompt-injection-containment.md`.

**Problem:** A small fixed set of paper IDs is reused as the quantitative backbone of *many* different
controls' bypass sections: **A40925 "~15% Acc-Fusion" appears in 7 patterns**, **A41134 "7%" (BU-MA) in
9**, **A37924 (ghost-cert) in 9**, **A40432 "~28% CRR" in 8**, A41129 in 6. The numbers are real and
tagged author-reported — but their *domain* is silently dropped on transplant. A40925 is scoped in
`Network-Cyber-Security.md` (lines 631, 241, 267) to **"Consensus Learning with Multi-Party Perturbation
Triggers," evaluated on MNIST / CIFAR-10 / CIFAR-100** — an image-classifier consensus gate. It is then
cited as "the residual (~15%, author-reported)" of *tool-capability isolation*, *network segmentation*,
*sandboxed execution*, and *tamper-evident traces*. A reader scanning "residual ~15% Acc-Fusion (A40925,
author-reported)" inside `tool-capability-isolation.md` reasonably reads it as a measured residual of a
tool gate. It is not; it is an analogy from a different modality and threat model.

**Why it matters (red-team seat):** the residual you budget against is the number you saw. Repeating one
narrow paper's figure across six controls makes the coverage look six-times deeper than it is and hides
that *no one measured the residual of the actual control*.

**Fix:** On every transplanted figure add a 4–6 word origin tag and an analogy flag, e.g.
`A40925 ~15% Acc-Fusion — consensus-gated image classifier, transplanted as analogy, not measured on a
tool gate`. Keep the number; stop it from masquerading as a measurement of the host control. (The
per-synthesis text already does this well; the pattern bullets drop it.)

---

### F2 — MAJOR — Adaptive-test concreteness is *inversely correlated* with runtime-criticality
**Where:** compare `adversarial-training.md` / `watermarking-fingerprinting.md` /
`backdoor-detection.md` / `differential-privacy.md` (concrete) against `policy-permission-gates.md` /
`prompt-injection-containment.md` / `sandboxed-execution.md` / `network-segmentation.md` /
`human-approval-consequential-actions.md` / `kill-switches.md` (generic).

**Problem:** The ML-attack patterns have genuinely mechanism-specific adaptive tests — `adversarial-training.md`
names the *exact tuned quantity* each attacker re-tunes (smoothness A38416; the attribution-consistency /
ASAM / gradient-norm regularizers A37396/A39603/A40054; the K-step feature cache A39954; the (ε_s,ε_a)
budget A38949); `watermarking-fingerprinting.md` says "estimate the provider's PCA basis from many
queries… top-2-parity-targeting… anchor stripping." Those are runnable attack recipes. The
**agentic-runtime** patterns, by contrast, recycle the *same ~5 generic moves* reworded per file:
"rewrite `Pm` to evade `Padv` (A41134)", "router/selective-gate evasion (A41129)", "verifier gaming
(A37924, white-box + known-σ)", "paraphrase to dodge the rejection rule (A40432)", "injection in any
model-visible field (A42239)". `policy-permission-gates.md` and `prompt-injection-containment.md` share
near-identical adaptive-test bullets.

This is *honest* — it is the direct consequence of the corpus's own most-replicated finding ("the
near-universal absence of adaptive agentic-defense evaluation," AILLM §16–17). But the consequence is
under-surfaced: the controls Origin/Passport actually enforce at runtime (policy gates, tool isolation,
injection containment, human approval) have the **least** concrete adaptive testing, while the
best-tested patterns (watermarking, adversarial training) are the least load-bearing for an agent stack.

**Fix:** Add a one-line **adaptive-test maturity** tag at the top of each pattern's *Adaptive adversarial
tests* section: `MATURITY: LOW — tests are transplanted analogies + reviewer synthesis; corpus ran no
defense-aware evaluation of this control` for the runtime patterns, vs `MATURITY: MODERATE — mechanism-
specific adaptive attackers exist in-corpus` for adversarial-training/watermarking/backdoor-detection.
Prevents an operator mistaking honest-but-thin guidance for validated coverage.

---

### F3 — MAJOR — The load-bearing *compensating control* (human approval) rests on untested analogies
**Where:** `human-approval-consequential-actions.md` → `Known bypasses` + `Adaptive adversarial tests`;
cross-referenced as the residual-risk backstop in `adaptive-red-teaming.md` (Failure handling / Rollback)
and most runtime patterns.

**Problem:** "Route high-stakes/irreversible actions to human approval" is the compensating control the
whole directory falls back on when a defense leaves residual. Yet its two most operationally-likely
breaks are the two least grounded: (a) **approval-summary poisoning** is an *analogy* to the
A41108/A41144 output-repetition channel ("emit an attacker-chosen string past the human reviewer"), never
tested against an actual approval summary; (b) **approval fatigue / rubber-stamping** is explicitly
"reviewer synthesis… **no measured approval-fatigue rate** (not stated in paper)." So the backstop that
compensates for every other control's residual is itself the least-evidenced control in the set.

**Fix:** Add an explicit caveat where human-approval is invoked as a compensating control (e.g. in
`adaptive-red-teaming.md` Failure handling and the runtime patterns' Rollback sections): *"human approval
as a compensating control is untested in-corpus against a defense-aware summarizer attacker and against
approval fatigue; production-validate before counting it as residual mitigation."* Right now it is
treated as a stronger floor than its evidence supports.

---

### F4 — MINOR — `deepfake-detection.md` has *no demonstrated adaptive break*; label it as such up front
**Where:** `deepfake-detection.md` → `Known bypasses`.

**Problem:** Every bypass is reviewer-identified/untested except **A41525**, which the file itself
describes as "a K-12 human spoofing a MobileNet-V2 **teaching** classifier." The section is admirably
honest ("No paper demonstrates a bypass of another paper's method"), but it is structurally different
from siblings (backdoor-detection, watermarking) that *do* list demonstrated cross-scheme breaks. An
operator scanning the directory uniformly could read this pattern's "Known bypasses" as the same class of
evidence. The one concrete adaptive attack here is pedagogical and against a non-corpus classifier.

**Fix:** Promote the honesty to a first-line banner in the section: `NOTE: zero demonstrated adaptive
break of any detection method in this corpus; adaptive posture is UNVALIDATED. All items below are
plausible-not-benchmarked except A41525 (a teaching classifier, not a defense here).` The content is
right; it just needs to lead, not trail.

---

### F5 — MINOR — Cross-reference paths break when resolved relative to `patterns/`
**Where:** 8 patterns cite `architecture-patterns.md` (bare filename) and 11 cite `defense-in-depth`
(no path, no extension) — e.g. `network-segmentation.md`, `sandboxed-execution.md` cite
"`architecture-patterns.md` P11/P12"; the human-approval/kill-switch/rollback cluster cite
"`defense-in-depth` §0."

**Problem:** The targets exist and the anchors are correct (verified: `architecture-patterns.md` has
`## P11` / `## P12`; `cross-cutting/defense-in-depth.md` has `## 0.` naming the A37117 / A40905/A40915 /
A37716 / A39290 exemplars). But `architecture-patterns.md` lives at `references/` root and
`defense-in-depth.md` under `references/cross-cutting/` — **one and two directories up from `patterns/`**.
Resolved as written from inside a pattern file, both 404. This is navigability only, not evidence — hence
minor — but it recurs in ~19 files.

**Fix:** Use correct relative paths: `../architecture-patterns.md#p11` and
`../cross-cutting/defense-in-depth.md#0`. Mechanical, one-pass sed.

---

## 2. What is DONE WELL

- **DW1 — Evidence-integrity discipline is exceptional and consistent.** Every quantitative claim is
  tagged author-reported vs reviewer-synthesis; language is calibrated throughout ("reduced ASR against
  the tested attacks under the evaluated non-adaptive threat model," "requires production validation");
  no absolutes; truncated source tables flagged. Crucially for a red-team consumer, `Known bypasses`
  sections are split **Demonstrated (in-corpus) vs Reviewer-identified (transplanted/untested)** — e.g.
  `incident-containment.md`, `network-segmentation.md`, `sandboxed-execution.md` do this explicitly. That
  split is exactly what lets an operator separate "this was measured" from "this is plausible." This is
  the single biggest thing the base gets right.

- **DW2 — The one load-bearing concrete break is correctly identified and threaded everywhere.** The
  STACK/MFA **whole-pipeline output-repetition channel** (A41108 ~0%→71% black-box / 33% transfer;
  A41144 58.5% across 17 VLMs, an *independent replication of the same channel*) is named as THE bypass
  and carried through `input-output-detection.md`, `adaptive-red-teaming.md`, `human-approval-*.md`,
  `kill-switches.md`, `safe-rollback.md` with the correct lesson — "per-component-robust stacks collapse
  jointly; composition of individually-robust controls is not itself a control." This is the most
  valuable, non-trivial, genuinely concrete finding in the corpus and it is front-and-center, not buried.

- **DW3 — The meta-pattern treats the oracle as a first-class attackable asset.** `adaptive-red-teaming.md`
  makes the scoring judge/verifier an adversary target (A40584 PRM scores an invalid step 0.973; A40916
  measurement circularity; A40866 best-judge itself untested against gaming) and gates launch on
  **absolute residuals + over-refusal**, not relative deltas (A42191 ~31% residual, A40248 ~16%, A41468
  >50% on hardest classes; A40897 FPR ~21.95%). Making "your red-team can overfit its own suite / trust a
  gameable oracle" a headline failure mode is sophisticated methodology, not box-ticking — most
  red-team checklists never question their own scorer.

---

## 3. Biggest risk from my seat

**The runtime controls Origin/Passport actually ship — policy gates, tool-capability isolation,
prompt-injection containment, human approval — have adaptive-test sections that are honest but thin: a
recycled handful of transplanted figures (A41134 7%, A40925 ~15%, A37924, A40432 ~28%) standing in for
the defense-aware evaluation the corpus never ran, so a reader can mistake "we documented the bypass" for
"we tested the control" and ship a stack whose only *real* adaptive break is the one everybody already
knows (the output-repetition channel) while every pattern-specific break remains un-built.**
