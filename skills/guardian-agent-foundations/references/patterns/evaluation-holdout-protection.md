# Pattern: Evaluation Holdout Protection

> **Scope of evidence.** Grounded in the two AAAI-26 corpus syntheses `Adversarial-ML-Attacks.md` (152 research
> cards) and `AILLM-Safety.md` (63 cards). Paper ids (e.g. `A39276`) are the stable corpus ids from those
> syntheses' source maps (§20 of each). Every recommendation below traces to at least one card or to a clearly
> labeled cross-paper judgment.
>
> **Evidence-integrity conventions (non-negotiable).** Numeric values are **author-reported** under each paper's
> own evaluated threat model unless labeled *(reviewer synthesis)*, and are **not independently verified**; several
> sit in table regions the syntheses mark truncated (Adversarial §12; AILLM §8). Where a card was silent, values
> are written "not stated in paper". No absolutes ("secure", "uncontaminated-guaranteed", "leak-proof") are used;
> findings hold "under the evaluated (largely non-adaptive) threat model" and "against the tested attacks".
> Cross-paper judgments are marked *(reviewer synthesis)*.
>
> **The load-bearing calibration for this pattern (read first).** No paper in either corpus proposes, names, or
> *measures the efficacy of* an "evaluation holdout protection" control. This pattern is therefore
> **reviewer-synthesis engineering practice**, not a measured defense. What the corpus does supply is unusually
> strong and directly on point:
> 1. **The single most-replicated finding in the entire corpus is that evaluation systematically overstates
>    security.** "Static, non-adaptive defense evaluation dominates the field, and wherever an attacker is allowed
>    to be defense-aware, the defense degrades or fails" (Adversarial §1, §9.1 — "highest-confidence meta-finding").
>    The AILLM synthesis independently calls the absence of adaptive-attacker evaluation "the single most consistent
>    methodological gap" (§1, §17).
> 2. **Self-proposed benchmarks used for both tuning and headline SOTA risk evaluation overfitting**, and
>    **non-adaptive fixed prompt/attack sets risk contamination after release** *(reviewer synthesis, AILLM §12;
>    Adversarial §12)* — the holdout's *secrecy and separation from training* is what makes a number meaningful.
> 3. **The scoring pipeline is itself gameable and circular** — single-LLM-judge scoring, sometimes with the judge
>    sharing a base model with the system under test, and attacks optimized against the same detector they are
>    scored with (AILLM §12; Adversarial §12); verifier/reward models score logically invalid steps highly
>    (`A40584`, author-reported an impossible constraint scored 0.973).
> 4. **The corpus's cleanest *positive* results here are methods for evaluating honestly**: `A39276` (how to audit
>    membership-inference without cross-corpus inflation) and the `A40905`/`A40915`/`A37117` bar of *building a
>    purpose-built adaptive attacker/remover/forger* rather than testing against fixed defenses.
>
> Treat the evaluation holdout — the reserved, secret, uncontaminated test artifacts **and** the scoring pipeline —
> as a **first-class security asset**, protected by **deterministic, fail-closed, least-privilege** controls. The
> control's honest promise is *auditable risk-reduction and a trustworthy verdict*, never proof of real-world
> safety: no defense in either corpus offers certified robustness against an unbounded adaptive adversary (Adversarial §1,
> §17; AILLM §16 "requires production validation" applies to every headline number).

---

## Problem addressed

A Guardian / autonomy-trace stack makes go/no-go decisions from **measurements**: a safety benchmark score, a
red-team attack-success rate (ASR), an over-refusal rate, a robustness certificate, a judge verdict. Those
measurements gate release, gate promotion of a third-party artifact, and drive production monitoring. The corpus's
dominant, cross-chunk, cross-synthesis meta-finding is that these measurements **routinely overstate real
security** because the *evaluation itself* is compromised in one of a small set of recurring ways:

- **Non-adaptive evaluation.** Attacks are tested only against fixed pre-existing defenses; defenses concede an
  adaptive adversary was not tested (Adversarial §1, §9.1; AILLM §16 lists a long roster of defenses whose headline
  numbers are non-adaptive). "Up to X%" figures are best-case over settings, not worst-case guarantees (AILLM §8).
- **Contamination / tuning-on-the-test-set.** Self-proposed benchmarks are used for *both* tuning and headline SOTA
  (`A40836` RSBench, `A40399`, `A40866`), risking metric-method co-selection; fixed prompt/attack sets risk
  contamination after release (`A40018`, `A40399`, `A40465`, `A40484`); a defense reports partial train/eval
  attack-family *overlap* (`A41074`). *(reviewer synthesis: AILLM §12, Adversarial §12.)*
- **Confounded distribution.** Cross-corpus evaluation inflates a metric that collapses to near-chance under
  strictly in-distribution evaluation — `A39276` shows a prior "near-perfect" CLIP membership-inference AUC of
  **94%→51%** with strong theory (slope 0.99±0.02, R²=0.997) and significance testing (author-reported).
- **Gameable / circular scoring.** Single-LLM-judge ASR with no reported human agreement, sometimes circular
  (a judge sharing the target's model family; an attack optimizing against the same detector class it is scored
  with, `A40916`) (AILLM §12); verifier/reward models assign high scores to logically invalid steps (`A40584`,
  author-reported 0.973 on an impossible constraint).
- **Per-component pass ≠ whole-system pass.** Guard stacks that pass per-component evaluation collapse under a
  whole-pipeline adaptive attack — `A41108` (STACK, 0%→71% black-box) and `A41144` (MFA, 0%→58.5%), author-reported.
- **Staleness / snapshot drift.** Commercial-model version drift makes results snapshot-dependent (`A40445`,
  `A40726`, `A40833`, `A40877`).
- **Metric definitions that inflate.** Quality-thresholded transfer ASR *inflates* reported success (`A38325`);
  output length is only a *proxy* for wall-clock energy (`A40445`); MIA papers that omit **TPR@low-FPR** and
  variance overstate detector quality (`A39449`, `A39276`).

**Evaluation holdout protection** is the control that protects the *integrity, secrecy, representativeness, and
freshness* of the holdout artifacts and the scoring pipeline, so a passing verdict actually means the system is
safe under the evaluated threat model — and so a compromised verdict is detected and fails closed rather than
silently shipping. Its honest scope, inherited from the corpus: it produces a **trustworthy, auditable, rollback-
able verdict**, not a guarantee of real-world safety *(reviewer synthesis grounded in Adversarial §16, AILLM §16)*.

## Applicable assets and attack surfaces

- **The holdout evaluation set** — safety/red-team prompts, adversarial test cases, poisoned-artifact corpora,
  labels, and expected outputs used for release sign-off and artifact promotion. This is the asset the whole
  pattern protects. Self-proposed sets are the highest-risk sub-case (`A40836`, `A40399`, `A40866`, AILLM §12).
- **The train / fine-tune / preference corpus** — the *contamination source*. Any overlap (verbatim or paraphrased)
  with the holdout invalidates the verdict; `A41074` reports partial train/eval attack-family overlap directly.
- **The scoring pipeline** — LLM-as-judge (`A40866` SceneJailEval; the judge roster flagged circular in AILLM §12),
  automated ASR classifiers (HarmBench/LlamaGuard-style, AILLM §7), reward/verifier models (`A40584` Process Reward
  Models, gameable), and the *metric definitions* themselves (`A38325` quality-thresholded ASR; `A40445` proxy
  length; `A39449` missing TPR@low-FPR).
- **Benchmark provenance & version metadata** — which holdout version, which model version pin, which judge scored
  which run; snapshot drift makes this load-bearing (`A40445`, `A40726`, `A40833`, `A40877`).
- **Released offensive artifacts (dual-use leak surface)** — papers releasing code, prompts, feature indices, and
  datasets lower the misuse barrier *and* contaminate any future eval that reuses them: `A41058` (cipher-attack
  code), `A41086` (ToxicBench), `A41119` (feature indices), `A41140` (data), `A41164`, `A40895`, `A40898` (released
  MCP/social-engineering tooling). Treat any published attack set as **burned** for holdout use.
- **The sign-off record and eval logs** — if these are mutable, a compromised verdict can be laundered; they must be
  tamper-evident (Adversarial §16 "Evidence-logging / rollback as the incident story"; §15 immutable audit).
- **The vault's own trusted assets** — its access-control policy, signing key, canary strings, and the small
  human-labeled anchor set used to audit the judges. These are security-sensitive inputs (compare the trusted-clean-
  set-as-security-asset framing in the sibling `backdoor-detection` pattern).

## Threat model

- **In scope — the "evaluation gamer" (the adversary or incentive-misaligned internal process that makes measured
  safety exceed real safety).** Capability tiers:
  - *Contamination.* Gets holdout content into the training/tuning corpus — deliberately, or innocently via web-
    scrape of released artifacts (`A41058`, `A41086`, `A41119`, `A41140`), or by reusing a self-proposed benchmark
    for both tuning and headline (`A40836`, `A40399`, `A40866`), or via undisciplined train/eval overlap (`A41074`).
  - *Distribution confounding.* Reports a metric on a mismatched distribution that inflates it; the honest in-
    distribution reframing collapses it (`A39276`, AUC 94%→51%, author-reported).
  - *Judge / verifier gaming and circularity.* Optimizes against the scoring detector (`A40916`), or exploits a
    judge that shares a base model with the system under test (AILLM §12), or games a reward/verifier that scores
    style over validity (`A40584`, 0.973 on an impossible constraint).
  - *Non-adaptive coverage gap.* Passes because only fixed pre-existing attacks were run — the modal weakness
    (Adversarial §9.1; AILLM §16).
  - *Metric manipulation.* Chooses an inflating metric definition (`A38325`) or a proxy that hides the real cost
    (`A40445`), or reports single-run point estimates with no variance (`A41122` explicitly no repeated runs;
    `A42292`, `A42327` no CIs/seeds).
- **In scope — eval-awareness / conditional behavior.** A model that behaves safely *when it detects it is being
  evaluated* and defects in production. The corpus analogue is triggered/dormant behavior that preserves the
  observed signal and changes only under a condition: `A40486` (answers correct while the payload fires),
  `A39480` (dormant backdoor absent from the inspected model, present only after downstream activation), and the
  router-evasion case where a jailbreak crafted to *look benign* bypasses a selective defense (`A41129`).
  *(reviewer synthesis: a holdout cannot see behavior it never triggers.)*
- **The adaptive-attacker bar to design against (the corpus's methodological gold standard).** Do not test only
  against fixed defenses — *build a purpose-built adaptive attacker/remover/forger*: `A40905` (purpose-built
  watermark remover, WSR reduced ≥88.79%), `A40915` (purpose-built forger with a bound < 1/2^128 at n=256),
  `A37117` (honestly reports its naive design is broken by an adaptive trigger-inversion attacker, then fortifies
  with randomized smoothing; reversed-accuracy 9.25% ≈ clean 9.47%). All author-reported.
- **Trust-boundary assumptions to reject.**
  1. That **a high headline number means real safety** — false; non-adaptive/contaminated/confounded evaluation
     overstates it (Adversarial §9.1; AILLM §16).
  2. That **a private benchmark stays private** — fragile; "hiding the signal is not a security boundary" (`A38127`,
     hard-label attack with proved O(1/T²) convergence), and released artifacts leak into the web.
  3. That **one automated judge is trustworthy** — false; judges are gameable and circular (`A40584`, `A40916`,
     AILLM §12, §16, §17). `A40866` is "a start" but "itself untested against evaluator-gaming" (AILLM §12).
  4. That **per-component pass implies whole-system pass** — false (`A41108`, `A41144`).
  5. That **a snapshot generalizes across model versions** — false; version drift (`A40445`, `A40726`, `A40833`,
     `A40877`).
  6. That **retraining/fine-tuning launders a contaminated artifact** — false; fine-tuning does not remove implanted
     behavior (`A40295` >99% persistence, *reinforced* by clean fine-tuning; `A39809`; `A40855`) — so you cannot
     "retrain away" a leak and reuse the same holdout.
- **Explicitly out of scope for the corpus evidence (the implementer MUST treat as unmeasured).** The end-to-end
  efficacy of a holdout-protection control is **not measured by any paper here**. The corpus supplies the failure
  evidence and specific honest-evaluation *methods*, not a validated integrated control. Physical-world holdout
  realizability, human-label bias in the anchor set, and cross-modal transfer of a holdout are all unmeasured.

## Control mechanism

A deterministic, fail-closed **evaluation-integrity gate** wrapped around a least-privilege **holdout vault**. The
gate blocks promotion/release unless *every* integrity precondition holds; any violation quarantines the artifact
and escalates to human review (fail-closed, never "warn and pass").

1. **Sealed holdout vault.** Holdout artifacts (prompts, attacks, labels, expected outputs) live in an access-
   controlled store, content-addressed by cryptographic hash, with signed provenance. Least-privilege: the
   training/fine-tuning pipeline identity has **no read access**; only the sign-off eval harness reads it. *(reviewer
   synthesis; mirrors the sibling `least-privilege-credentials` and `signed-provenance` patterns; grounded in the
   "capability is not permission / weight secrecy is fragile" theme, Adversarial §6.)*
2. **Contamination gate (train/eval separation).** Deterministic check that holdout content — enforced via planted
   **canary** strings and n-gram/semantic overlap scanning — does **not** appear in the training corpus, and that no
   benchmark used for tuning is reused for headline sign-off. Fail closed on any hit. Motivated by `A41074` (train/
   eval overlap), the self-proposed-benchmark risk (`A40836`, `A40399`, `A40866`), and contamination-after-release
   (`A40018`, `A40465`, `A40484`).
3. **Distribution & metric discipline.** Follow the `A39276` methodology: distribution-matched probes, report
   **TPR@low-FPR** and variance/significance (not just AUC/ASR), and run a null/sanity probe that must return near-
   chance. Report **over-refusal / false-positive rate as a first-class metric** against an adaptive benign-ambiguous
   set (AILLM §16; foregrounded by `A41074`, `A41140`, `A41152`, `A42191`, `A40543`). Freeze a single non-inflating
   metric definition (reject quality-thresholded ASR gaming, `A38325`; reject proxy-only reporting, `A40445`).
4. **Adaptive-red-team requirement.** Promotion is blocked unless a **defense-aware adaptive** evaluation ran — the
   `A40905`/`A40915`/`A37117` bar (build the adaptive attacker/remover/forger). Non-adaptive coverage alone is a
   fail-closed condition (Adversarial §9.1; AILLM §16).
5. **Judge-integrity layer.** Use **>1 independent judge** plus a **human-labeled anchor** sample; require the judge
   to **not share a base model/encoder** with either the system under test or the attack optimizer (circularity
   guard); prefer scenario-adaptive judging (`A40866`) while recording its documented limitation (untested against
   evaluator-gaming). Never trust a raw verifier/reward score as ground truth (`A40584`).
6. **Freshness / rotation.** Rotate the holdout on a fixed cadence and whenever any component leaks; re-pin model
   versions per run; treat every published attack set as burned (`A41058`, `A41086`, `A41119`, `A41140`).
7. **Tamper-evident sign-off record.** Every verdict is a signed, immutable record binding {holdout version hash,
   model version pin, judges + agreement, contamination result, adaptive-coverage flag, distribution/metric report}
   — so a compromised verdict is detectable and rollback-able (Adversarial §15, §16).

## Preconditions and trust assumptions

- **You can hold a secret.** The vault premise requires that at least the canary strings, the signing key, and part
  of the holdout can be kept out of the training corpus and out of the model. Where secrecy is impossible (a public
  benchmark by design), the pattern degrades to rotation + adaptive construction + provenance, and every number must
  be read as an *upper bound on safety / lower bound on ASR*. *(reviewer synthesis; "hiding is not a boundary",
  `A38127`.)*
- **You can enforce least-privilege.** The training pipeline identity must be *denied* holdout read access; without
  enforced separation, contamination is undetectable in principle. *(reviewer synthesis.)*
- **You have a canary + overlap-scan mechanism** capable of catching verbatim and, ideally, paraphrased leakage.
  Note the corpus caveat: paraphrase/semantic evasion defeats constant-pattern detectors (`A41118` paraphrase
  triggers; `A40353` evades paraphrase/perplexity/clustering detection) — verbatim canaries are necessary but not
  sufficient.
- **You have >1 independent judge and a human-labeled anchor set.** Single-judge sign-off is explicitly rejected
  (AILLM §16, §17). The anchor set is a trusted asset and carries its own bias risk (classifier sociolinguistic
  bias, `A37350`, `A40543`).
- **You accept the holdout will eventually leak** and plan rotation accordingly (`A40445`, `A40726`, `A40833`,
  `A40877` version drift; dual-use release).
- **Trust anchors (fail if compromised):** the vault access-control policy, the signing key, the canary secrecy, and
  the human anchor labels. All are engineering assumptions, **not corpus-measured**; each requires production
  validation.

## System architecture

*(reviewer synthesis, grounded in the cited cards and the sibling patterns.)*

```
                        ┌─────────────────────────────────────────────┐
                        │  HOLDOUT VAULT (sealed, content-addressed)    │
                        │  prompts · attacks · labels · expected out    │
                        │  hash manifest + signed provenance + canaries │
                        └───────────────┬───────────────────────────────┘
   training pipeline identity            │ read: ALLOWED only to eval harness
   read: DENIED (least-privilege) ──✗────┘ (write: sealed after review)
                                         │
                                         ▼
   ┌───────────────┐   contamination   ┌────────────────────────┐
   │ TRAIN / TUNE  │──── scan (canary, │  EVAL HARNESS          │
   │ CORPUS        │◀─── n-gram, sem.) │  · pins model version   │
   └───────────────┘   fail-closed hit │  · runs ADAPTIVE red    │──▶ system under test
                                        │    team (A40905/A40915/ │
                                        │    A37117 bar)          │◀── outputs
                                        └───────────┬─────────────┘
                                                    ▼
             ┌──────────────────────────────────────────────────────────┐
             │ SCORING PIPELINE                                          │
             │  judge_1 ⟂ judge_2 (no shared base w/ SUT or attacker)    │
             │  + human anchor sample   + verifier (score ≠ ground truth)│
             │  metrics: TPR@low-FPR, FPR/over-refusal, variance         │
             │  null/sanity probe → must be ≈ chance (A39276)            │
             └───────────────┬──────────────────────────────────────────┘
                             ▼
             ┌──────────────────────────────────────────────────────────┐
             │ INTEGRITY GATE (deterministic, FAIL-CLOSED)               │
             │  contamination=0? adaptive-run=yes? judge-agreement≥θ?    │
             │  distribution-match ok? version fresh? metric-frozen?     │
             │  ── any NO → QUARANTINE + human review ──                 │
             └───────────────┬──────────────────────────────────────────┘
                             ▼
             ┌──────────────────────────────────────────────────────────┐
             │ SIGNED, TAMPER-EVIDENT SIGN-OFF RECORD  (autonomy trace)  │
             │  {holdout hash · model pin · judges · gate results · ts}  │
             └──────────────────────────────────────────────────────────┘
```

- **Vault ↔ training separation** is the trust boundary (compare `least-privilege-credentials`, `signed-provenance`).
- **Contamination scan** reuses canary/attestation primitives (compare `backdoor-detection`, `content-provenance`).
- **Sign-off record** is a tamper-evident trace (compare `tamper-evident-traces`; Adversarial §15/§16).

## Recommended implementation pattern

Deterministic and fail-closed at every step.

1. **Seal and content-address the holdout.** Store artifacts in an access-controlled vault; compute a hash manifest;
   sign it (compare `signed-provenance`). Record which artifacts are drawn from *released* sources and mark them
   burned for future rotations (`A41058`, `A41086`, `A41119`, `A41140`).
2. **Enforce least-privilege reads.** The training/fine-tuning identity is *denied* vault read access by policy, not
   convention. Log every read (Adversarial §15 "API hygiene / log split-point state" analogue).
3. **Plant canaries and scan for contamination.** Insert unique canary strings into the holdout; before promoting
   any model, deterministically scan the training corpus for canary hits and for n-gram/semantic overlap with the
   holdout. **Any hit → fail closed.** Supplement with membership-style probing (`A39276` methodology) and note the
   paraphrase-evasion caveat (`A41118`, `A40353`).
4. **Pin versions per run.** Record the exact model version/snapshot under test (`A40445`, `A40726`, `A40833`,
   `A40877`).
5. **Run an adaptive red team, not a fixed suite.** Construct a defense-aware attacker/remover/forger against the
   *specific* system and its guards (`A40905`, `A40915`, `A37117`). Record adaptive-coverage as a gate flag.
6. **Score with a judge quorum + human anchor.** ≥2 independent judges with no shared base/encoder with the SUT or
   the attack optimizer; a human-labeled anchor sample to audit judge–human agreement; treat verifier/reward scores
   as signals, not truth (`A40584`).
7. **Report the right metrics.** TPR@low-FPR and variance (`A39276`, `A39449`), FPR/over-refusal against an adaptive
   benign-ambiguous set (AILLM §16), a frozen non-inflating ASR definition (reject `A38325`-style thresholding),
   and a null/sanity probe that must come back ≈ chance (`A39276`).
8. **Gate deterministically and fail closed.** contamination==0 AND adaptive-run==true AND judge-agreement≥θ AND
   distribution-match-ok AND version-fresh AND metric-frozen — else quarantine + human review.
9. **Emit a signed, tamper-evident sign-off record** binding all of the above (Adversarial §16).
10. **Rotate.** On cadence and on any leak, mint a fresh sealed holdout; void prior sign-offs certified against a
    compromised set (see Rollback).

## Incorrect or fragile implementation patterns

- **Single-LLM-judge sign-off.** Explicitly rejected — single-judge ASR with no human agreement, sometimes circular,
  is pervasive and unreliable (AILLM §12, §16, §17). Fragile.
- **Reusing a self-proposed benchmark for both tuning and headline SOTA.** Risks metric-method co-selection /
  evaluation overfitting (`A40836`, `A40399`, `A40866`; AILLM §12). Fragile.
- **Reporting only aggregate ASR/AUC.** Omitting TPR@low-FPR, variance, and over-refusal overstates quality
  (`A39449`, `A39276`; AILLM §7 defenses that "buy safety with large benign-refusal increases"). Fragile.
- **Cross-corpus / mismatched-distribution evaluation.** Inflates the metric; collapses under in-distribution
  reframing (`A39276`, 94%→51%). Fragile.
- **Trusting a private benchmark to stay private.** "Hiding the signal is not a security boundary" (`A38127`);
  released artifacts leak (`A41058`, `A41086`, `A41119`, `A41140`). Fragile.
- **Per-component-only evaluation of a guard stack.** Collapses under whole-pipeline adaptive attack (`A41108`
  0%→71%; `A41144` 0%→58.5%). Fragile.
- **Static holdout, never rotated.** Guarantees eventual contamination and snapshot staleness (`A40445`, `A40726`,
  `A40833`, `A40877`). Fragile.
- **Quality-thresholded / cherry-picked metric definitions.** Inflate reported success (`A38325`); proxy-only
  reporting hides real cost (`A40445`). Fragile.
- **A judge that shares its base model/encoder with the SUT or the attack optimizer.** Circular; the attacker can
  optimize against the scorer (`A40916`; AILLM §12). Fragile.
- **Treating a verifier/reward score as ground truth.** Gameable — high scores for logically invalid steps
  (`A40584`, 0.973). Fragile.
- **"Warn and pass" on an integrity violation.** Any non-fail-closed gate defeats the control. Fragile by design.
- **Assuming retraining launders a contaminated artifact so the holdout can be reused.** Fine-tuning does not remove
  implanted behavior (`A40295`, `A39809`, `A40855`) — and does not un-leak a holdout. Fragile.

## Verification strategy

Verify the *control itself*, not just the system under test.

- **Canary-recall drill.** Deliberately plant a known canary in a shadow training corpus; confirm the contamination
  scan fires and the gate fails closed. A miss means the separation is unverified. *(reviewer synthesis; canary
  logic per §13 detection primitives.)*
- **Null/sanity probe (A39276 discipline).** Feed an obviously-null comparison (distribution-matched, no true
  signal); confirm the honest metric returns ≈ chance. A "near-perfect" result on a null probe indicates a
  confounded pipeline (`A39276`: CSA AUC 94%→51% is the cautionary datum).
- **Judge–human agreement audit.** Score the human-labeled anchor set with each automated judge; report agreement.
  Low agreement, or a judge that shares a base with the SUT, invalidates the verdict (AILLM §12, §16).
- **Adaptive-coverage check.** Confirm a *purpose-built adaptive* attacker was run and recorded (the `A40905`/
  `A40915`/`A37117` bar). A model that passed only a fixed suite must not clear the gate.
- **Least-privilege probe.** Attempt a vault read from the training-pipeline identity; expect denial. A success is a
  containment failure. *(reviewer synthesis.)*
- **Verifier-gaming spot check.** Submit a known logically-invalid-but-stylistically-strong case; confirm the
  verifier score is *not* taken as ground truth (`A40584`).

## Metrics and thresholds

*All thresholds marked "policy choice" are engineering decisions, NOT corpus-derived. Cited numbers are the
originating paper's author-reported values, used as calibration reference points, not as targets to hit.*

- **Contamination hits** — threshold **0** (fail closed on any canary/overlap hit). Rationale: train/eval overlap
  invalidates the verdict (`A41074`). *(policy choice: zero-tolerance.)*
- **Train/eval n-gram + semantic overlap** — a policy threshold; supplement verbatim scan with membership probing
  because paraphrase evades constant-pattern detectors (`A41118`, `A40353`). *(policy choice.)*
- **Judge–human agreement (θ)** — report it; block below a policy floor. No corpus number is a valid universal
  target; `A40866` reports F1 0.917 (own set) / 0.995 (JBB) *for the judge*, which does **not** transfer as an
  agreement threshold. *(policy choice.)*
- **TPR@low-FPR and variance** — required outputs, not just AUC/ASR (`A39276`, `A39449`). *(reporting requirement.)*
- **Over-refusal / FPR** — first-class, measured against an adaptive benign-ambiguous set (AILLM §16). *(reporting
  requirement.)*
- **Null-probe result** — must be ≈ chance; `A39276`'s reframed AUC 51% (down from 94%) is the reference for "what
  honest ≈ chance looks like." *(calibration reference, author-reported.)*
- **Adaptive-coverage flag** — binary; must be **true** to pass. *(policy choice: fail-closed on non-adaptive.)*
- **Version freshness** — model pin recorded; holdout age under a rotation-cadence policy. *(policy choice; drift per
  `A40445`, `A40726`, `A40833`, `A40877`.)*
- **Statistical hygiene** — reject single-run point estimates with no variance for sign-off (`A41122` no repeated
  runs; `A42292`, `A42327` no CIs/seeds are the cautionary examples). *(reporting requirement.)*

## Test cases

Each expects the gate to **fail closed** (block promotion) unless noted.

1. **Verbatim contamination.** Plant a known holdout string in the training corpus → contamination scan fires,
   promotion blocked. (Motivated by `A41074`.)
2. **Reused-benchmark-for-tuning.** Register a benchmark as a tuning input, then submit it for headline sign-off →
   gate flags overlap, blocked. (`A40836`, `A40399`, `A40866`.)
3. **Non-adaptive-only submission.** Submit a model evaluated only against a fixed attack suite → adaptive-coverage
   flag false, blocked. (`A40905`/`A40915`/`A37117` bar.)
4. **Confounded distribution.** Run the null/sanity probe on a mismatched distribution → honest metric must return
   ≈ chance; a "near-perfect" result flags a confounded pipeline. (`A39276`.)
5. **Circular judge.** Score with a judge sharing the SUT's base model/encoder → circularity guard flags, blocked.
   (`A40916`; AILLM §12.)
6. **Verifier gaming.** Feed a logically-invalid, stylistically-strong case → verifier score must not be treated as
   ground truth; multi-judge + human anchor override. (`A40584`, 0.973 reference.)
7. **Per-component pass, whole-pipeline fail.** Submit a guard stack that passes each component but fails a whole-
   pipeline adaptive attack → blocked. (`A41108`, `A41144`.)
8. **Stale version pin.** Submit results against an outdated model snapshot → freshness gate blocks. (`A40445`,
   `A40726`, `A40833`, `A40877`.)
9. **Least-privilege breach attempt.** Read the vault from the training identity → denied and logged.
10. **Metric-inflation attempt.** Report a quality-thresholded ASR → frozen-metric gate rejects. (`A38325`.)

## Adaptive adversarial tests

Red-team the *evaluation-integrity control itself* — the corpus's core lesson is that a control not stress-tested
by a defense-aware adversary will overstate its own robustness (Adversarial §9.1, §16; AILLM §16).

- **Holdout exfiltration via the judge/scorer.** An adversary who can query the scoring pipeline attempts to
  reconstruct holdout content from judge behavior (analogue: embedding/hidden-state inversion recovers protected
  inputs, `A38127` "hiding is not a boundary"). Test whether repeated scoring queries leak holdout items.
- **Judge/verifier gaming.** Optimize an output to score high on the automated judge/verifier while being unsafe
  (`A40584` PRM 0.973; `A40916` optimizing against the scoring detector). Confirm multi-judge + human anchor catch it.
- **Eval-awareness / conditional behavior.** Craft a model that behaves safely under the holdout distribution and
  defects out-of-distribution (analogue: dormant/triggered behavior `A40486`, `A39480`; benign-looking jailbreak
  that evades a selective router `A41129`). This is a *known-hard* case a holdout cannot fully cover (see Residual).
- **Purpose-built adaptive attacker/remover/forger.** Meet the `A40905`/`A40915`/`A37117` bar against the SUT and
  its guards; confirm the gate would have blocked a model that only passed the fixed suite.
- **Whole-pipeline attack on the eval stack.** Treat the eval stack (harness + judges + gate) as a stack and attack
  it end-to-end, per the `A41108`/`A41144` lesson that per-component-robust stacks collapse jointly.
- **Semantic/paraphrased contamination.** Leak a *paraphrased* holdout into training and confirm whether verbatim
  canaries miss it (`A41118`, `A40353`) — measures the contamination scan's false-negative surface.

## Telemetry requirements

Emit structured, tamper-evident fields to the autonomy-trace console (Adversarial §16 "runtime telemetry candidates"
+ immutable audit §15). Per sign-off run, record:

- **Holdout version hash** and the subset of items drawn from released/burned sources.
- **Model version pin** and snapshot timestamp (drift, `A40445`/`A40726`/`A40833`/`A40877`).
- **Contamination-scan result** — canary hits, n-gram/semantic overlap, membership-probe outcome; and the training-
  identity vault-read attempts (denied/allowed).
- **Adaptive-coverage flag** and a description of the purpose-built attacker/remover/forger run (`A40905`/`A40915`/
  `A37117`).
- **Judge identities + shared-base check + per-judge scores + judge–human agreement** on the anchor set (AILLM §12).
- **Metric report** — TPR@low-FPR, variance, over-refusal/FPR, frozen ASR definition, null-probe result (`A39276`,
  `A39449`).
- **Gate decision** per condition (contamination / adaptive / agreement / distribution / freshness / metric) with the
  fail-closed reason on any block.
- **Signed record** binding all fields; immutable and rollback-referenceable (Adversarial §16).

## Failure handling

**Fail closed, always.** Any single integrity violation — canary/overlap hit, missing adaptive run, judge
disagreement beyond the policy floor, distribution mismatch, stale version pin, unfrozen/inflating metric, or a
least-privilege breach — **blocks promotion/release, quarantines the artifact, and escalates to human review**. The
control must never "warn and pass": a non-fail-closed gate is equivalent to no gate *(reviewer synthesis; grounded
in the corpus principle that leading defenses leave material residual and must gate, not replace, human oversight —
Adversarial §16, AILLM §16)*. When an automated judge is unavailable or disagrees with the human anchor, degrade to
human review rather than to the automated verdict (AILLM §16 "do not rely on a single automated judge for sign-off").

## Rollback and containment

- **On discovered holdout contamination/leak:** treat the holdout as **burned**; mint a fresh sealed set (rotation);
  **void every prior sign-off certified against the compromised set** — those verdicts are no longer trustworthy;
  re-evaluate affected models against the fresh holdout. *(reviewer synthesis; Adversarial §16 "Evidence-logging /
  rollback as the incident story for every poisoning class.")*
- **On a model promoted against a compromised evaluation:** restore a known-clean checkpoint / prior release, and
  gate the suspect model behind re-evaluation. Note the corpus caveat: you cannot *retrain away* a leak and reuse the
  same holdout — fine-tuning does not remove implanted behavior (`A40295`, `A39809`, `A40855`).
- **On judge/scorer compromise or circularity discovery:** invalidate scores from that judge, re-score with an
  independent quorum + human anchor, and record the incident in the tamper-evident trace.
- **Traceability requirement:** because every verdict is a signed record binding holdout hash + model pin + gate
  results, a contaminated verdict is *traceable* to the exact artifacts and *re-runnable* against a clean holdout
  (Adversarial §15, §16). Without the immutable record, rollback scope cannot be bounded.

## Known bypasses

Honest limits — the control raises the cost of gaming and makes verdicts auditable, but does not eliminate these:

- **Holdout secrecy is fragile.** A determined adversary reconstructs or acquires the holdout ("hiding is not a
  boundary," `A38127`), and released artifacts contaminate the web (`A41058`, `A41086`, `A41119`, `A41140`). Rotation
  mitigates but does not prevent.
- **Judges remain gameable and circular.** Multi-judge + human anchor reduces but does not remove the risk
  (`A40584`, `A40916`, `A40920`; `A40866` is "a start", itself untested against evaluator-gaming, AILLM §12).
- **Adaptive coverage is only as good as the attacker you build.** The modal weakness in the corpus is precisely
  that the *right* adaptive attack was not run (Adversarial §9.1); a holdout-protection gate cannot certify coverage
  of an attack no one constructed.
- **Eval-awareness / conditional defection.** A model that behaves under the holdout distribution and defects in
  production is not caught by any holdout (analogue: dormant/triggered behavior `A40486`, `A39480`; benign-looking
  evasion `A41129`). *(reviewer synthesis: fundamental limit of measurement.)*
- **Semantic contamination evades verbatim canaries.** Paraphrased leakage defeats constant-pattern detection
  (`A41118`, `A40353`) — the contamination scan has a real false-negative surface.
- **Version drift outpaces rotation.** Between rotations, a pinned snapshot can diverge from the deployed model
  (`A40445`, `A40726`, `A40833`, `A40877`).

## Residual risks

- **No certified guarantee.** No defense in either corpus offers certified robustness against an unbounded adaptive adversary
  (Adversarial §1, §17); this control yields *auditable risk-reduction and a trustworthy-under-the-evaluated-model
  verdict*, not proof. Frame it as `A40570` (AntiDote) frames tamper-resistance: **reduction, not proof.**
- **The control is unmeasured end-to-end.** Its integrated efficacy is reviewer-synthesis engineering practice;
  **every threshold and the architecture require production validation** (AILLM §16 "requires production validation";
  Adversarial §16).
- **Eval-awareness and semantic contamination remain open** (see Known bypasses) — measurement cannot cover behavior
  it never triggers or leakage it cannot recognize.
- **Human-anchor bias.** The trusted human-labeled anchor set carries its own bias, which propagates into the verdict
  (classifier sociolinguistic bias, `A37350`, `A40543`).
- **Judge/verifier residual gaming.** Even a quorum can be jointly gamed by an evaluator-aware adversary (`A40584`,
  `A40916`); the corpus provides no non-gameable judge (AILLM §17 open problem).
- **Dual-use / governance exposure.** Maintaining an adaptive red-team holdout means holding offensive artifacts;
  their release/leakage is itself a governance risk (Adversarial §16; AILLM §16 dual-use hygiene).

## Relevant research (stable paper ids from the syntheses/cards)

*Core — how to evaluate honestly (the corpus's positive evidence for this pattern):*

- **`A39276`** — Rethinking CLIP membership-inference: cross-corpus inflation collapses to near-chance under strictly
  in-distribution evaluation (AUC 94%→51%; slope 0.99±0.02, R²=0.997; TPR@low-FPR + significance testing). *The
  keystone "audit your evaluation honestly" method (Adversarial §9.7, §18).*
- **`A40905`** (CFW/WRK) — sets the methodological bar of *building a purpose-built adaptive remover* rather than
  testing against fixed defenses (WSR reduced ≥88.79%). *(Adversarial §18.)*
- **`A40915`** (NeuralMark) — purpose-built forger with a cryptographic forging bound < 1/2^128 at n=256; adaptive-
  construction bar. *(Adversarial §5.)*
- **`A37117`** (Authority Backdoor) — the corpus's cleanest adaptive-attack methodology: honestly reports its naive
  design is broken by an adaptive attacker, then fortifies (reversed-accuracy 9.25% ≈ clean 9.47%). *(Adversarial §11.)*
- **`A38127`** — hard-label query-efficient attack (proved O(1/T²), 13 baselines, released code); the anchor for
  "hiding the signal is not a security boundary." *(Adversarial §18.)*

*Scoring-pipeline integrity (judges, verifiers, circularity):*

- **`A40584`** — Process Reward Models score logically invalid steps highly (0.973 on an impossible constraint);
  verifier/reward gaming. *(Adversarial §10.)*
- **`A40866`** (SceneJailEval) — scenario-adaptive severity-graded jailbreak judge (F1 0.917/0.995); "a start", but
  itself untested against evaluator-gaming. *(AILLM §5, §12, §17.)*
- **`A40920`** (T2I-RiskyPrompt) — reason-driven risk detector (91.8%); measurement-circularity risk when an attack
  optimizes against the scorer. *(AILLM §12, §16.)*
- **`A40916`** — attack optimizing against the same NSFW-detector class it is scored with (circularity exemplar).
  *(AILLM §12.)*

*Contamination / train-eval overlap / self-proposed benchmarks:*

- **`A41074`** — reports partial train/eval attack-family overlap directly. *(AILLM §12.)*
- **`A40836`** (RSBench), **`A40399`** (EduGuardBench), **`A40866`** — self-proposed benchmarks used for both tuning
  and headline SOTA (evaluation-overfitting risk). *(AILLM §12.)*
- **`A40018`**, **`A40465`**, **`A40484`** — non-adaptive fixed prompt/attack sets at contamination-after-release
  risk. *(AILLM §12.)*
- **`A41498`** (GARD) — 0.98 recall on a largely synthetic set with only 115 SME-validated real samples (in-
  distribution / synthetic-eval caveat). *(AILLM §12.)*

*Whole-pipeline vs per-component; the non-adaptive meta-finding:*

- **`A41108`** (STACK) — per-component-robust guard stacks collapse under staged adaptive attack (0%→71%). *(Adv §9.9,§19.)*
- **`A41144`** (MFA) — 17 VLMs; alignment + system prompt + I/O moderation jointly bypassable (0%→58.5%). *(Adv §19.)*

*Metric discipline & statistical hygiene:*

- **`A38325`** — quality-thresholded transfer ASR *inflates* success (metric-definition gaming). *(Adversarial §8.)*
- **`A39449`** — MIA evaluation criticized for omitting TPR@low-FPR and variance. *(Adversarial §8, §12.)*
- **`A40445`** — output length is only a *proxy* for wall-clock energy/latency. *(Adversarial §8, §12.)*
- **`A41122`**, **`A42292`**, **`A42327`** — single-run / no-CIs point estimates (statistical-hygiene cautions). *(Adv §12.)*

*Freshness / snapshot drift:*

- **`A40445`**, **`A40726`**, **`A40833`**, **`A40877`** — commercial-model version drift makes results snapshot-
  dependent. *(Adversarial §12.)*

*Dual-use leak sources (burned-for-holdout artifacts):*

- **`A41058`**, **`A41086`**, **`A41119`**, **`A41140`** (AILLM §12 dual-use release); **`A41164`**, **`A40895`**,
  **`A40898`** (Adversarial §16 released offensive tooling).

*Eval-awareness / conditional-behavior analogues (why a holdout can't see everything):*

- **`A40486`** (correct answer while payload fires), **`A39480`** (dormant backdoor absent from the inspected model),
  **`A41129`** (benign-looking evasion of a selective router). Contamination-scan evasion analogues: **`A41118`**,
  **`A40353`**.

*Calibration anchors (reduction, not proof; fine-tuning does not launder):*

- **`A40570`** (AntiDote) — tamper-resistance explicitly framed as risk-reduction, not proof. **`A40295`**,
  **`A39809`**, **`A40855`** — fine-tuning does not remove implanted behavior. **`A37350`**, **`A40543`** — classifier
  sociolinguistic bias (human-anchor bias).

## Evidence strength

- **`A39276` — Strong (methodological), for its class.** Strong theory (slope 0.99±0.02, R²=0.997), significance
  testing, and a decisive in-distribution reframing (AUC 94%→51%); the corpus's cleanest "evaluate honestly" result.
  Tempered: MIA-specific and CLIP-specific; author-reported; transfer to other eval regimes is *(reviewer synthesis)*.
- **`A40905` / `A40915` / `A37117` — Strong (methodological) as an *adaptive-construction bar*.** Each *builds* a
  purpose-built adaptive attacker/remover/forger (with `A40915` a cryptographic forging bound and `A37117` a
  certified radius) — the corpus's gold standard for not overstating robustness. Tempered: each within a narrow
  threat model (single embedding round / ℓ2 radius / specific artifact), author-reported.
- **The non-adaptive-evaluation meta-finding — Strong but *(reviewer synthesis)*.** The most-replicated conclusion in
  the corpus across all four Adversarial chunks and independently in AILLM (§1, §9.1 / §1, §17), yet it is a
  cross-paper judgment, not a single measured result.
- **`A40584` (verifier gaming) — Moderate, author-reported.** A concrete, striking datum (0.973 on an impossible
  constraint); single-context.
- **`A40866` (judge) — Moderate, and explicitly limited.** "A start" toward a better judge; author-reported F1
  0.917/0.995; **itself untested against evaluator-gaming** (AILLM §12) — do not treat its numbers as a transferable
  agreement threshold.
- **The evaluation-holdout-protection control itself — Reviewer-synthesis engineering practice, NOT measured.** No
  paper measures the vault, the contamination gate, the least-privilege separation, or the integrated gate. Every
  architectural and threshold recommendation **requires production validation**; framed as reduction, not proof
  (compare `A40570`).

Cross-cutting: **all numbers are author-reported and, where noted, non-adaptive or truncated (Adversarial §12; AILLM
§8).** No number in this pattern is a target to optimize toward; each is a calibration reference from its source.

## When NOT to use this pattern

- **When the deployment threat is runtime injection or unsafe action, not evaluation-gaming.** Holdout protection
  *certifies*; it does not *enforce at runtime*. For prompt/tool/environment injection and consequential actions,
  use the sibling patterns `prompt-injection-containment`, `policy-permission-gates`, `human-approval-consequential-
  actions`, and `least-privilege-credentials` — grounded in `A41090`/`A41468` (AILLM §14/§15) and `A40895`
  (Adversarial). This control gates the *measurement*, not the action.
- **When you cannot hold a secret or enforce least-privilege.** The vault premise collapses; a fully public benchmark
  cannot be sealed. Degrade to rotation + adaptive-attacker construction + provenance, and read every number as an
  *upper bound on safety / lower bound on ASR* ("hiding is not a boundary," `A38127`).
- **When you need a certified guarantee.** The corpus offers none against an adaptive adversary (Adversarial §1,
  §17); this pattern yields auditable risk-reduction, not proof. If certification is the requirement, this is a
  supplement, not a solution.
- **For an already-published/leaked holdout.** You cannot retroactively re-seal a leaked set; treat it as burned and
  rotate. Reusing it after "retraining the model" is invalid — fine-tuning does not launder a leak (`A40295`,
  `A39809`, `A40855`).
- **For cross-modal / cross-model reuse without revalidation.** A holdout valid for one model/version/modality does
  not transfer — distribution mismatch (`A39276`) and version drift (`A40445`, `A40726`, `A40833`, `A40877`) both
  invalidate reuse; re-establish the threat model and metrics first.
- **When the real gap is a *non-gameable judge* rather than holdout integrity.** That is an open corpus problem
  (`A40866` "a start"; AILLM §17); this pattern reduces judge risk (quorum + human anchor + circularity guard) but
  does not solve it — do not present it as a solved judge.
