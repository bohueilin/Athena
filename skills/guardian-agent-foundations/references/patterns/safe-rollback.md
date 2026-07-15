# Pattern — Safe Rollback

> **Control class.** Containment + Evidence + Verification (in the corpus's Capability · Permission · Verification ·
> Evidence · Residual-risk ontology). A deterministic, fail-closed mechanism that, on a detected compromise or
> degradation, reverts an agent/model/system to an **independently attested known-good state** — while preserving
> forensic evidence, maintaining a degraded-but-available service, and proving the transition in a tamper-evident
> trace. It is a *recovery/containment* control that assumes prevention has already failed; it is never a first line.
>
> **Evidence integrity (non-negotiable).** Every claim below traces to a card in the AAAI-26 corpus via its stable
> internal `Axxxxx` paper id (the corpus flags manifest arXiv ids as frequently mis-extracted, so only card ids are
> used). Author-reported results are labeled as such and kept distinct from reviewer synthesis. All magnitudes are as
> reported by the cited paper under *that paper's own evaluated threat model* and are **not independently verified**.
> Where the corpus is silent, the text says "not stated in paper." Language is calibrated throughout ("reduced ASR
> against the tested attacks", "demonstrated under the evaluated threat model", "not evaluated against", "requires
> production validation"); no absolutes ("secure", "unbreakable", "proven safe") are used. The single most consistent
> gap in the corpus is the near-total absence of adaptive-attacker evaluation of defenses (`defense-in-depth` §0, §2;
> `AILLM-Safety` §16–17) — treat every rollback trigger, restore target, and evidence guarantee here as un-adaptively
> validated until proven otherwise on the target stack.

---

## Problem addressed

Autonomous LLM/agent and ML systems are compromised or silently degraded in ways that *no upstream control drives to
zero*: the corpus records material residual harm surviving even the strongest evaluated defenses — inference-time RAS
leaves author-reported ~31% residual ASR (A42191), a mechanistic contrastive-decoding fix leaves ~16.4% residual
harmful on Qwen-3-8B (A40248), the fullest MCP defense-in-depth still misses >50% (contextual policy violation) /
>76% (command injection) on its hardest classes (A41468, author-reported, Preliminary), and the strongest evaluated
RAG-extraction defense still leaves ~28% chunk-recovery (A40432). When residual harm is assumed rather than wished
away (`defense-in-depth` §6), a system needs a way to *return to a trustworthy state* after a control fails or an
incident is detected. Safe rollback is that recovery leg.

The pattern exists because the two intuitive alternatives are empirically false. First, **"retrain/fine-tune to fix
it" does not remove implanted behavior and can amplify it**: P-Trojan is engineered so ordinary clean fine-tuning
*reinforces* it (author-reported >99% persistence; forgetting-mitigation *amplifies* persistence — A40295),
corroborated by A39809/A40855, and ShadeEdit's edits persist through clean fine-tuning even where counterfactual
edits partly revert (A40787). "Retraining resets the threat" is false (`defense-in-depth` §7). Second, **"just roll
back to an earlier checkpoint" can restore *into* a compromise**: dormant backdoors live in the pre-finetuning
checkpoint where the payload is absent and inspection is blind (A39480), so an un-attested "earlier version" is not
automatically a clean version. The corpus's actual incident story for every poisoning class is therefore *log
provenance and hashes so a discovered backdoor is traceable and a clean checkpoint is restorable* — with **the
trusted clean set treated as a security asset** (`Adversarial-ML-Attacks` §16; `defense-in-depth` §9). This pattern
turns that story into an engineering control: an attested known-good baseline, a deterministic trigger, a verified
restore, preserved evidence, and a proof trace — instantiated end-to-end by A40189 (TAPA).

## Applicable assets and attack surfaces

- **Model weights / checkpoints / adapters** — the restore *target*. Distributed CLIP checkpoints carry dormant,
  finetuning-activated backdoors (A39480); poison survives or is reinforced by retraining (A40295, A40787, A39809,
  A40855). The thing you roll back to is itself an attack surface.
- **Model knowledge (memorized / poisoned content)** — knowledge-level rollback via unlearning or model editing
  (A41145 ROME, author-reported extraction 65.2%→1.6% on small open-weight models; A40343 KUnBR). Whether the erasure
  *held* is itself contested (see below).
- **Agent memory, conversation state, and RAG store** — the state you roll back *to* or *from* can be attacker-shaped:
  forged prior turns (A40840 Response Attack avg ASR 94.8% across 8 models, author-reported; A36996 CHASE), and
  attacker-writable retrieval corpora (A40353, A40726). Restoring to an unattested "clean" transcript can restore a
  fabricated state.
- **Inter-agent coordination / message bus** — A40224 (MAST) reframes the bus as a first-class tampering channel;
  per-message provenance is required to know *what* state to restore.
- **Live action-space / policy of an autonomous agent** — A40189 (TAPA) maintains backup meta-policies for
  uninterrupted operation when the live policy is swapped out.
- **The snapshot/checkpoint store, the provenance chain, and the trigger signal themselves** — A40189's RAG
  provenance store and degradation signal are *trusted* components and, by reviewer synthesis on its card, an
  un-hardened attack surface (RAG/prompt poisoning of the store; a reward signal an adversary can spoof).

## Threat model

Under the corpus's dominant, most product-relevant threat models (`defense-in-depth` §0–§9):

- **External injection / adversarial operating environment** degrades the agent so that a fixed policy collapses
  (A40189 models exactly this — DDoS/environmental disturbance driving reward below threshold; A41090, A41468 for the
  agent action layer). The trigger must fire on *this*, and an attacker will try to make degradation look benign.
- **Supply-chain compromise of the restore target.** The attacker's win condition against rollback is that the
  known-good baseline *is not clean*: a dormant backdoor absent from the inspected checkpoint (A39480), or poison
  engineered to survive/reinforce under retraining (A40295, A40787, A39809, A40855). Pre-finetuning inspection is
  blind; only post-finetuning red-team + attestation discriminates.
- **Adversary who abuses the rollback / erase primitive itself.** The delete/forget capability is security-sensitive:
  revocable backdoors use machine unlearning as *anti-forensic revocation* (A39747, "Injection, Attack and Erasure"),
  the unlearning event can *leak* membership (A39725, "Retaliatory Attacks Against Federated Unlearning"), and
  behavioral non-recall is *not* proof of removal (A40272 AUVIC; A40343 RTT relearning restores knowledge; A41120
  post-unlearn fine-tuning increases leakage). A defense-aware attacker may re-optimize after a model edit (A41145,
  reviewer synthesis).
- **History / memory forgery** so the "known-good" state restored is attacker-fabricated (A40840, A36996).
- **Defense-aware (adaptive) adversary.** The corpus's highest-confidence meta-finding is that wherever an attacker
  is allowed to be defense-aware, static defenses degrade or fail (`defense-in-depth` §0, §2). Applied here: the
  attacker targets the *trigger* (evade it), the *restore target* (poison it), the *evidence store* (tamper it), and
  the *erase primitive* (weaponize it) — none of which is adaptively evaluated in the corpus.

**Out of scope for this pattern** (handled by sibling patterns or by prevention): **irreversible external effects** —
funds transfer, data hard-deletion, physical actuation, sent messages — have **no post-hoc undo**; the corpus does
not evaluate rollback for irreversible physical/financial effects, so for those the only line is *prevention*
(human-approval gate, least-privilege capability isolation) plus capability revocation (see `human-approval-
consequential-actions` Rollback section). Training-time poisoning *detection* (A39480/A38015), input/inter-agent
*prevention* gates (A41468, A40224), and durable knowledge *unlearning as a guarantee* (a contested open problem,
Privacy §132) each require their own controls; safe rollback is the recovery/containment layer that runs *after* a
compromise is detected, not the primary defense.

## Control mechanism

The load-bearing in-corpus instantiation is **A40189 (TAPA)** — the one paper the syntheses identify as running the
full "models propose → environments verify → gates decide → traces prove" loop (`Multi-keyword-match` §1, §5):
*propose → shadow-simulation verify → degradation-threshold gate → backup-meta-policy rollback → human-approval Alert
→ provenance chain.* Generalized into a deterministic containment control:

1. **Maintain attested, immutable known-good snapshots.** Weights/checkpoint hashes, live policy, memory/RAG state,
   and config, each with logged provenance so a discovered compromise is traceable and a clean state is restorable
   (`Adversarial-ML-Attacks` §16). The clean baseline is a **security asset** (`defense-in-depth` §9), not a
   convenience copy — and it must be *independently attested*, because an earlier checkpoint is not automatically
   clean (A39480).
2. **Detect degradation/compromise with a deterministic trigger.** A40189 uses reward-below-threshold; complementary
   runtime signals are invalid-action rate (A39818), and internal-signal detectors — token-confidence-run events
   (A40897), attention-head-similarity / deep-layer concentration (A41080, A40867), Mahalanobis/manifold OOD scores
   (A40301, A40366). Do **not** trigger on output accuracy alone: backdoors preserve clean accuracy and rationales
   (A39935 ≤1% drop at ≤0.5% poison; A40409; A40486 answers correct while reasoning inflates ~17×; A40867).
3. **Suspend onto a backup / degraded-but-available state.** A40189's backup meta-policies keep operation
   uninterrupted during the swap. This resolves the fail-open/fail-closed dilemma (`defense-in-depth` §4): a hard
   fail-closed outage is itself a DoS lever (A37924 records certified-abstention *as* denial-of-service), and
   fail-open lets the compromise run — so route to a degraded-but-available backup, not to an outage and not to live.
4. **Restore to an independently attested known-good target, then verify the restore actually removed the
   compromise.** Verification is state-grounded, not behavioral: A41090's rule-based evaluators inspect action
   history / file storage / app DB (verify the world, not the model's claim); for knowledge rollback, a
   relearning/extraction audit (A40343, A40272, A40047) because non-recall is not removal.
5. **Preserve forensic evidence *before* any destructive erase/rollback.** Retain snapshots before honoring any
   delete/unlearn (`defense-in-depth` §9; `Adversarial-ML-Attacks` §14; A39747) — the erase itself is a weaponizable
   anti-forensic primitive.
6. **Route the incident to authenticated human approval.** A40189's Alert primitive; the corpus's human-approval-as-
   first-class-action (`AILLM-Safety` §14; A41090 `ask-consent()`/`refuse()`).
7. **Emit an immutable, tamper-evident, per-event provenance record** of trigger → snapshot handle → restore
   (from→to, target attestation) → verification result → decision (A40189 provenance chain; A41468 Layer 4 immutable
   audit; A40224 per-message provenance). This is the Evidence leg: a rollback that "ran" is not itself proof the
   restored state is clean (`defense-in-depth` CPVER legend, Verification ≠ Evidence).

The mechanism is one **layer** in defense-in-depth, never the sole control (`defense-in-depth` §1, §11); it sits
behind prevention (gates, isolation) and depends on least-privilege capability isolation to bound blast radius during
the incident window.

## Preconditions and trust assumptions

- **An independently-verified known-good baseline exists.** The restore target must be attested (signed weights /
  hash pin / known-good baseline) and *post-finetuning* red-teamed, because pre-finetuning inspection is blind to
  dormant backdoors (A39480) and retraining does not sanitize (A40295, A40787). Absent this, rollback is theater.
- **A tamper-evident evidence/snapshot store outside the agent's write-influence.** A41468 asserts an immutable Layer
  4 audit but the corpus flags that tamper-evidence and formal guarantees for audit layers are *asserted but not
  verified* (A41468 reviewer synthesis; `AILLM-Safety` §17 names them absent). Treat store integrity as an
  assumed-secure dependency that must itself be hardened — **not stated in paper** that any evaluated store resists an
  adaptive tamperer.
- **A reliable, hard-to-spoof trigger signal.** A40189 assumes its degradation signal is reliable; its card flags
  (reviewer synthesis) that this is un-adaptively tested and that an adversary could engineer conditions to evade or
  falsely fire it.
- **Shadow/sandbox fidelity for pre-restore validation.** A40189 validates candidate state in shadow simulation
  before it goes live; a sim-to-real gap could let an unsafe state pass validation (author-stated limitation).
- **Attested provenance of memory/history**, or the restore target can be forged (A40840, A36996).
- **Least privilege / capability isolation already in place**, so the compromise's blast radius is bounded while the
  trigger fires and the restore completes (A37117 hardware-credential capability gating; `AILLM-Safety` §14).

## System architecture

Aligned to the agent cognitive cycle (observe → plan → act → audit), mapping A40189's pipeline, A41468's audit layer,
and A41090's state-grounded evaluators:

```
observe ─▶ plan ─▶ act ─▶ audit
                    │
   ┌────────────────┴────────────────────────────────────────────┐
   │ S0  Snapshot & attest (continuous):                          │ ← A40189 provenance chain
   │     immutable known-good weights-hash/policy/memory/config;   │   Adv-ML §16 log+hash
   │     restore target is post-finetuning-attested, not "earlier" │   A39480 (earlier ≠ clean)
   │ T1  Trigger (deterministic, internal signals — NOT accuracy): │ ← A40189 reward<ξ; A39818
   │     degradation/anomaly/residual-harm/invalid-action          │   A40897/A41080/A40301/A40366
   │ C2  Contain → degraded-but-available backup (not outage,      │ ← A40189 backup meta-policy
   │     not live): resolve fail-open/closed to safe-degraded      │   defense-in-depth §4
   │ E3  Preserve forensic evidence BEFORE any erase               │ ← A39747; defense-in-depth §9
   │ R4  Restore to attested target → shadow-validate → verify     │ ← A40189 shadow-sim;
   │     removal by STATE-grounded + relearning/extraction audit   │   A41090; A40343/A40272/A40047
   │ H5  Human-approval Alert on the incident                      │ ← A40189 Alert; A41090
   │ P6  Immutable, per-event, tamper-evident provenance record    │ ← A41468 L4; A40224
   └──────────────────────────────────────────────────────────────┘
```

Key architectural properties drawn from the corpus:

- **Decouple capability from live authority.** A40189's LLM *proposes* new state; shadow simulation *verifies*; a
  degradation/threshold gate plus backup policies *decide/rollback*; the provenance chain *proves* — only validated
  state goes live (A40189 design implications). Rollback is the "decide" step's safe default.
- **The restore target is a trust boundary, not a convenience.** Because an earlier checkpoint can be the compromised
  one (A39480) and poison survives retraining (A40295, A40787), the target must be attested and post-finetuning-
  screened, or the architecture restores the attacker's foothold.
- **Verify state, not self-report.** Post-restore verification uses rule-based state-grounded evaluators (A41090) and,
  for knowledge rollback, relearning/extraction audits (A40343, A40272) — never "the bad output is gone."
- **The evidence store and trigger are themselves attackable** and must be hardened as first-class surfaces (A40189
  reviewer synthesis; A40224; `AILLM-Safety` §17).

## Recommended implementation pattern

Prefer deterministic, fail-closed (to safe-degraded), least-privilege construction:

1. **Continuously snapshot to an immutable, tamper-evident store with provenance + hashes** (A40189 provenance chain;
   `Adversarial-ML-Attacks` §16). Snapshot the full trust surface: weights/adapter hash, live policy, agent
   memory/RAG state, and config.
2. **Attest the restore target independently; never define "known-good" as "most recent."** Signed weights / hash pin
   / known-good baseline, plus *post-finetuning* red-team of the target (A39480), before it is eligible as a restore
   point. Keep multiple attested generations so a single poisoned baseline is not the only option.
3. **Trigger on internal signals, deterministically, and fire on the *first* qualifying event.** Combine
   degradation-threshold (A40189), invalid-action rate (A39818), and internal-signal detectors (A40897/A41080/A40301/
   A40366). Do not rely on many-query anomaly trajectories — jailbreaks succeed at a single query (A40919, A40465) or
   ≤10–15 queries (A41058, A40554) — and do not trigger on accuracy (A39935/A40867).
4. **Contain to a degraded-but-available backup before restoring** (A40189 backup meta-policies), so containment is
   not a hard outage (which is a DoS lever, A37924) and not fail-open.
5. **Preserve forensic evidence before any destructive step** (A39747; `defense-in-depth` §9). Snapshot the
   compromised state for analysis *first*; the erase is irreversible for forensics.
6. **Shadow-validate the restore, then verify removal with state-grounded checks** (A40189 shadow simulation; A41090
   rule-based evaluators), and for knowledge rollback add a relearning/extraction audit (A40343, A40272, A40047)
   before declaring the compromise contained.
7. **Route the incident to authenticated human approval** (A40189 Alert; A41090) — a person, not the model, confirms
   return-to-live for consequential systems.
8. **Log the whole transition to an immutable, per-event, tamper-evident provenance chain** (A40189; A41468 Layer 4;
   A40224 per-message provenance) — trigger, snapshot handles, restore from→to, target attestation, verification
   result, decision.
9. **Harden the store, the trigger, and the erase primitive** (add integrity/authenticity controls on the snapshot
   store and provenance RAG — A40189 implementation implications; authenticate inter-agent channels — A40224).

## Incorrect or fragile implementation patterns

- **"Retrain/fine-tune to fix it."** Retraining does not remove implanted behavior and can amplify it (A40295 >99%
  persistence, forgetting-mitigation amplifies; A40787; A39809; A40855). Fine-tuning is a supply-chain trust
  boundary, not a reset (`defense-in-depth` §7).
- **Rolling back to "the previous version" without attestation.** May restore a dormant backdoor absent from the
  inspected checkpoint (A39480). "Earlier" ≠ "clean."
- **Behavioral / output check as proof of a clean restore.** Non-recall is not removal (A40272, A39373, A40047), and
  the "cleaned" state is reactivatable by relearning or a later fine-tune (A40343, A41120); best forgetting in the
  corpus is only ~80–88% (A40870, author-reported).
- **Trusting model-editing / unlearning as durable rollback without a re-optimization test.** ROME-style edits may be
  reversible by a defense-aware attacker who re-tunes a soft prompt post-edit (A41145, reviewer synthesis); chain-
  level residue survives answer-level unlearning (A40818).
- **Destructive erase before preserving evidence.** Enables anti-forensic revocation (A39747) and can leak via the
  unlearning event (A39725). Evidence first, always.
- **Rolling back memory/history to an unattested transcript state.** Restores a forged "clean" state (A40840, A36996).
- **Hard fail-closed outage on trigger/restore** (a DoS lever, A37924) — or fail-open (lets the compromise run).
  Neither is safe; route to safe-degraded (`defense-in-depth` §4).
- **Triggering on accuracy / pass-fail.** Blind to accuracy-preserving backdoors and reasoning-DoS (A39935, A40409,
  A40486, A40867; `defense-in-depth` §8).
- **Trusting the snapshot/provenance store because it is "internal."** It is an attack surface (A40189 reviewer
  synthesis; A40224); tamper-evidence for audit layers is asserted-but-unverified in the corpus (`AILLM-Safety` §17).

## Verification strategy

- **Adaptive red-teaming is a launch gate, not a nice-to-have** (`defense-in-depth` §0, §2 — stated verbatim by two
  of three syntheses). For rollback specifically, the attacker must be allowed to target the *trigger* (evade or
  falsely fire it), the *restore target* (poison the baseline, A39480/A40295/A40787), the *evidence store* (tamper
  it), and the *erase primitive* (weaponize it, A39747). A40189's own evaluation is non-adaptive-vs-the-loop (reviewer
  synthesis) — a floor, not a ceiling.
- **State-grounded, not behavioral, post-restore verification.** Rule-based evaluators over action log / file storage
  / DB (A41090). For knowledge rollback, a relearning/extraction/MIA audit is the missing acceptance test — behavioral
  "it forgot" understates residue (Privacy §132; A40343, A40272, A40047, A40818).
- **Whole-pipeline, not per-component.** Composition of individually-robust controls is not itself a control (A41108
  STACK ~0%→71% ASR; A41144 MFA 58.5%) — test the end-to-end recovery with the prevention layers assumed bypassed, so
  the residual robustness of the rollback is measured directly.
- **Attest the restore target under an adaptive supply-chain attacker.** Post-finetuning screening because
  pre-finetuning inspection is blind (A39480); scan for *multiple coexisting* backdoors, not one (A38015).
- **Do not rely on a single automated judge** for restore sign-off; validate against human agreement and evaluator-
  aware adversaries (`AILLM-Safety` §12; A40866 is a start but is itself untested against evaluator-gaming).

## Metrics and thresholds

> The corpus provides no validated threshold for a safe-rollback control specifically (**not stated in paper**). The
> metrics below are the corpus's evaluation vocabulary applied to this control; numeric targets are engineering
> defaults requiring production validation. A40189's headline **77.7% network uptime with "near-perfect detection"
> in unknown dynamic environments** (author-reported) and its example recovery to **~72% acceptable-threshold uptime**
> are a *single reported operating point*, simulation-only, with no adaptive-attacker-vs-loop test (A40189 card).

- **Unverified-restore rate** — count of return-to-live events without a passed state-grounded verification. Target by
  construction: **0** (fail-closed). Primary security metric; a Containment-correctness property, not an ASR estimate.
- **Residual-compromise-after-restore** — result of the post-restore relearning/extraction audit (A40343/A40272/
  A40047) and state-grounded check (A41090). Report as an absolute against the tested attacks, never a relative
  reduction (`defense-in-depth` §6). Expect nonzero; rollback inherits upstream residual.
- **Restore-target attestation coverage** — fraction of eligible restore points that are independently attested +
  post-finetuning-screened (A39480). Target: 100% before a point is eligible.
- **Trigger false-negative "bypass budget"** — the trigger's miss rate against accuracy-preserving compromise and
  query-efficient attacks, reported as an absolute (`defense-in-depth` §5; A39935/A40867/A40919/A41058).
- **Degradation trigger threshold ξ** — A40189 uses reward-below-threshold (its example ξ≈72% acceptable uptime).
  Engineering-set per system; validate against an adaptive benign-degradation set to avoid over-triggering.
- **Time-to-contain and continuity/availability during restore** — A40189's backup policies target *uninterrupted*
  operation; measure the availability gap as a first-class metric (abstain/outage is an availability risk, §4).
- **Forensic-snapshot completeness** — fraction of incidents with a pre-erase evidence snapshot retained (A39747).

## Test cases

Each maps to a concrete corpus attack:

1. **Dormant-backdoor restore target.** Offer an "earlier" checkpoint that carries a finetuning-activated backdoor
   (A39480). Expect: attestation + post-finetuning screen rejects it as a restore point; a clean attested generation
   is used instead.
2. **Persistent poison survives retrain.** Attempt to "fix" a poisoned model by clean fine-tuning (A40295, A40787).
   Expect: the pattern does *not* treat retraining as a valid restore; only rollback to an attested clean baseline is
   accepted.
3. **False-clean via non-recall.** After a knowledge rollback, the target no longer emits the harmful content
   behaviorally but retains it (A40272, A40343). Expect: relearning/extraction audit detects residue; restore is not
   declared clean (A40047/A40818).
4. **Anti-forensic erase.** An attacker triggers a destructive erase/unlearn to destroy evidence (A39747). Expect:
   forensic snapshot is preserved *before* the erase; the erase requires human-approval and is logged (A39725).
5. **Forged known-good state.** Inject a fabricated prior "clean" transcript/memory (A40840, A36996). Expect: restore
   target provenance is attested; unattested state is not a valid rollback point.
6. **Degradation trigger fires under environmental attack.** DDoS/disturbance drives reward below ξ (A40189). Expect:
   trigger fires, backup policy maintains availability, restore + human Alert follow.
7. **Accuracy-preserving backdoor evades an accuracy trigger.** A backdoor with ≤1% clean-accuracy drop (A39935,
   A40867). Expect: internal-signal trigger (A40897/A41080/A40301) fires where an accuracy monitor would not.
8. **Continuity during restore.** Restore while live traffic continues. Expect: backup meta-policy serves a degraded-
   but-available path; no hard outage (A40189; §4).

## Adaptive adversarial tests

The launch bar the corpus demands (`defense-in-depth` §0 names the disciplined adaptive-attacker exemplars):

- **Trigger evasion.** Craft the compromise to be accuracy-preserving (A39935/A40867) and to keep the reward signal
  above ξ, so the trigger never fires (A40189 reviewer synthesis: the degradation signal is un-adaptively tested).
- **Restore-target poisoning.** Plant a dormant backdoor in the baseline itself (A39480) or engineer poison that
  survives retraining (A40295, A40787), so a "successful" rollback restores the foothold.
- **Post-edit re-optimization.** After a knowledge rollback / model edit, re-tune a soft prompt to recover the erased
  behavior (A41145, reviewer synthesis; A40818 residue).
- **Evidence-store / provenance tampering.** Attack the snapshot store and provenance chain, since their tamper-
  evidence is asserted-but-unverified (`AILLM-Safety` §17; A40189; A40224 inter-agent bus tampering).
- **Erase-primitive abuse.** Weaponize the rollback/unlearn path for anti-forensics (A39747) or to leak (A39725).
- **Single-/few-query success.** Confirm the trigger is not defeated by an attack that completes before any volume
  anomaly accrues (A40919, A40465, A41058, A40554).
- **Whole-pipeline (not per-component) adaptive run.** Assume prevention layers bypassed; measure whether the
  attested-restore + state-grounded verification still hold (A41108, A41144).

## Telemetry requirements

Emit structured, tamper-evident trace fields (consistent with A40189's provenance chain, A41468 Layer 4, A40224
per-message provenance; `defense-in-depth` §8):

- **Snapshot descriptor**: snapshot id, weights/adapter hash, policy/memory/config hashes, attestation status +
  post-finetuning-screen result of each restore-eligible point (A39480; `Adversarial-ML-Attacks` §16).
- **Trigger event**: which signal fired (degradation-threshold, invalid-action rate, confidence-run, attention-
  concentration, OOD score), value vs threshold, and the raw internal signals — *not* accuracy (A40189; A39818;
  A40897/A41080/A40301/A40366; §8).
- **Restore event**: from-state → to-state, restore-target attestation, shadow-validation result, state-grounded
  verification result (A41090), and knowledge-audit result where applicable (A40343/A40272/A40047).
- **Forensic-snapshot handle**: the pre-erase evidence retained before any destructive step (A39747).
- **Human-approval decision** on the incident: approver identity, decision, latency (A40189 Alert; A41090).
- **Runtime tripwires (candidate, unvalidated as detectors)**: per-request entropy/MI (A41088) and CoT n-gram drift
  (A42273) — log for forensics only; the corpus notes these lack ROC/PR validation, so do not gate on them, and do
  not expose raw CoT to users (`AILLM-Safety` §14).

## Failure handling

Fail-closed to a *safe-degraded* state on every uncertainty (never a hard outage, never fail-open — `defense-in-
depth` §4):

- **Snapshot/evidence store unavailable or its integrity unverifiable** → hold on the last attested known-good state;
  do not promote new state; escalate. A rollback keyed on an unverifiable store manufactures false assurance.
- **No attested clean restore target available** → do not restore into an un-attested "earlier" checkpoint (A39480);
  contain to the degraded backup and escalate to human.
- **Post-restore verification fails** (state-grounded or relearning/extraction audit) → do not return to live; keep
  the backup serving and escalate (A41090; A40343/A40272).
- **Trigger ambiguous / detector uncertain** → treat as compromise and contain, not as benign.
- **Restore cannot complete in the available time** (latency-critical loop) → the backup meta-policy must already be
  hot; if it is not, this pattern is a design mismatch (A40189 exists precisely to keep a backup available).
- **Destructive erase requested** → preserve forensic evidence and require human approval first (A39747, A39725).

## Rollback and containment

(This pattern *is* the rollback/containment control; the corpus's limits on it are stated plainly.)

- **Backup-policy continuity is the containment primitive.** A40189's backup meta-policies keep the system available
  while the live state is swapped — containment without a hard outage (§4).
- **Capability revocation + short-expiry, action-bound credentials bound blast radius** during the incident window
  (least privilege, `AILLM-Safety` §14; A37117 hardware-credential capability gating so leaked weights degrade to
  near-random). Revoke first, restore second.
- **Immutable audit enables forensic reconstruction and traceable rollback** (A41468 Layer 4; A40189 provenance
  chain; A40224 per-message provenance) — the trigger → snapshot → restore → verify chain supports post-incident
  analysis and, where state was reversible, targeted restoration.
- **Hard limit — irreversible external effects have no undo.** The corpus does not evaluate rollback for irreversible
  physical/financial effects (`human-approval-consequential-actions` Rollback section). For those, containment is
  *prevention* (the gate) plus capability revocation; safe rollback recovers *internal* state (weights, policy,
  memory), not effects already emitted into the world. Design accordingly.

## Known bypasses

- **Poisoned restore target** — dormant-backdoor checkpoint (A39480) or retraining-persistent poison (A40295, A40787)
  restores the attacker's foothold under the guise of recovery.
- **False-clean restore** — behavioral non-recall accepted as removal while residue remains (A40272, A39373, A40047),
  reactivatable later (A40343, A41120).
- **Reversible model edit** — post-edit re-optimization recovers erased behavior (A41145, reviewer synthesis; A40818).
- **Anti-forensic / leaking erase** — the rollback/unlearn primitive weaponized (A39747) or leaking membership
  (A39725).
- **Forged known-good state** — restoring to an unattested, attacker-fabricated transcript/memory (A40840, A36996).
- **Trigger evasion** — accuracy-preserving compromise (A39935, A40867) or reward-signal spoofing keeps the trigger
  silent (A40189 reviewer synthesis).
- **Evidence-store tampering** — audit/snapshot tamper-evidence is asserted-but-unverified (`AILLM-Safety` §17; A40189;
  A40224).
- **Shadow-sim fidelity gap** — an unsafe restored state passes shadow validation and goes live (A40189 stated
  limitation).

## Residual risks

- **Rollback inherits the residual of everything feeding it.** No control drives residual to zero (A42191 ~31%,
  A40248 ~16%, A41468 >50%/>76% hardest classes, A40432 ~28%; `defense-in-depth` §6). Recovery reduces incident
  dwell-time; it does not eliminate harm.
- **No adaptive evaluation of rollback triggers or restore-verification exists in the corpus.** A40189 is a single
  operating point, simulation-only, with no adaptive-attacker-vs-loop test (A40189 card). Residual robustness is
  therefore unknown (`defense-in-depth` §0, §2).
- **Knowledge-rollback verification is an open problem.** Approximate unlearning leaves an adversarially recoverable,
  often reactivatable residue; behavioral/black-box metrics understate it (Privacy §132; A40272/A40343/A40818/A40870/
  A41120). "Removed" is a claim requiring a relearning/extraction audit, not an assumption.
- **The evidence/snapshot store's tamper-evidence is asserted, not verified** (A41468 reviewer synthesis;
  `AILLM-Safety` §17) — a rollback anchored on a forgeable store is not trustworthy.
- **Irreversible external effects are unrecoverable** (see Rollback and containment).
- **External validity** — A40189's evidence is simulation-only on a single headline number; "requires production
  validation" applies to every number and to this entire pattern.

## Relevant research (stable paper ids from the syntheses/cards)

- **A40189 (TAPA)** — keystone: the corpus's one full propose → shadow-verify → degradation-threshold gate → backup-
  policy rollback → human Alert → provenance-chain loop; "keep validated backups for instant rollback." Author-
  reported 77.7% uptime, single operating point, simulation-only, no adaptive-attacker-vs-loop test.
- **A39480 (dormant CLIP backdoor)** — the restore target can be the compromised one; pre-finetuning inspection is
  blind. Motivates *attested* restore points and post-finetuning screening.
- **A40295 (P-Trojan) / A40787 (ShadeEdit) / A39809 / A40855** — retraining/fine-tuning does not remove implanted
  behavior and can amplify it; "retraining resets the threat" is false.
- **A41145 (CoSPED / ROME editing)** — knowledge-level rollback via model editing (author-reported 65.2%→1.6%, small
  open-weight models); reversible by a defense-aware attacker post-edit (reviewer synthesis).
- **A40343 (KUnBR) / A41120 / A40272 (AUVIC) / A40047 / A40818 / A40870 / A39373** — approximate unlearning leaves a
  detectable, reactivatable residue; behavioral non-recall is not proof of removal (the knowledge-rollback verification
  problem).
- **A39747 (revocable backdoor via unlearning) / A39725 (retaliatory FL-unlearning leakage)** — the delete/erase
  primitive is security-sensitive: anti-forensic revocation and membership leakage; preserve evidence *before* erase.
- **A40840 (Response Attack) / A36996 (CHASE)** — forged history/memory; the restore target must be attested.
- **A40224 (MAST)** — inter-agent message-bus tampering; per-message provenance for state restoration.
- **A41090 (MobileSafetyBench)** — rule-based state-grounded evaluators (action log / FS / DB) for post-restore
  verification; `ask-consent()`/`refuse()` human-in-the-loop.
- **A41468 (InfrastructureSentinel)** — four-layer defense-in-depth incl. immutable Layer-4 audit; tamper-evidence
  asserted-not-verified (Preliminary).
- **A39818** — invalid-action rate as a runtime health/trigger signal.
- **A40897 / A41080 / A40301 / A40366** — internal-signal detectors (confidence-run, attention-similarity, OOD) as
  triggers that survive accuracy-preserving compromise.
- **A39935 / A40409 / A40486 / A40867** — backdoors/DoS preserve accuracy → do not trigger on accuracy.
- **A40908 (HealSplit) / A40867 (PurMM) / A40902 (BeDKD) / A40904 (CL-Guard)** — detect-then-*repair* / test-time
  purification / punish-distillation on a small trusted clean set: response-as-repair primitives complementary to
  full-state rollback.
- **A37924 (GhostCert)** — certified-abstention *as* DoS: why containment routes to safe-degraded, not a hard outage.
- **A37117 (weight-lock)** — hardware-credential capability gating (leaked weights → near-random) for blast-radius
  containment during the incident window.
- **A42191 / A40248 / A41468 / A40432** — residual-harm evidence motivating a recovery layer.

## Evidence strength

- **The direction is well-motivated and convergent.** "Log provenance + hashes so a clean checkpoint is restorable;
  the trusted clean set is a security asset" is the corpus's explicit incident story for every poisoning class
  (`Adversarial-ML-Attacks` §16; `defense-in-depth` §9), and A40189 is a genuine worked example of the full
  propose/verify/gate/rollback/prove loop (`Multi-keyword-match` §1). The dangerous failure modes — retraining does
  not sanitize (A40295/A40787), earlier ≠ clean (A39480), non-recall ≠ removal (A40272/A40343) — are each
  independently supported. The *direction* of the recommendation is strong.
- **The quantitative evidence for a rollback control itself is weak-to-preliminary.** A40189 is the only
  instantiation and reports a single simulation uptime number with no adaptive-attacker-vs-loop test, unproven safety
  of LLM-generated restore state, and unstated code (A40189 card, Evidence: moderate). No paper in the corpus reports
  a validated, adaptively-tested safe-rollback control with numbers.
- **Corpus-wide caveat:** the dominant methodological gap is the absence of adaptive-attacker evaluation
  (`defense-in-depth` §0, §2; `AILLM-Safety` §16–17). Every trigger, restore, and evidence guarantee here is a
  best-case upper bound. **"Requires production validation" applies to this entire pattern.**
- **Overall rating (reviewer synthesis):** *Recommended as a required Containment/recovery layer for internal state
  (weights, policy, memory), paired with prevention and least privilege; robustness of any specific implementation is
  unproven and must be established by whole-pipeline adaptive red-teaming — targeting the trigger, the restore target,
  and the evidence store — before reliance.*

## When NOT to use this pattern

- **As a substitute for prevention on irreversible external effects.** Funds, data hard-deletion, physical actuation,
  and sent messages have no post-hoc undo; the corpus does not evaluate rollback for them (`human-approval-
  consequential-actions` Rollback section). There, use human-approval gates + least-privilege isolation + capability
  revocation; rollback recovers internal state only.
- **When no independently-attested known-good baseline exists.** Without post-finetuning-screened, attested restore
  points, rollback can restore *into* a compromise (A39480) or a poison that survived retraining (A40295, A40787).
  Fix attestation first, or the control is theater.
- **As a claim of durable knowledge removal that cannot be audited.** If durable erasure is required but you cannot
  run a relearning/extraction audit, do not present unlearning/editing as a rollback guarantee — non-recall is not
  removal and residue is reactivatable (A40272, A40343, A41145, A40818; Privacy §132).
- **Latency-critical autonomous loops without a hot standby.** If a restore cannot complete in time and no backup
  policy is already live, the containment step cannot maintain availability — A40189's backup meta-policies exist
  precisely to avoid this; without them the pattern is a design mismatch.
- **When the evidence/snapshot store cannot be made tamper-evident and out-of-agent-write.** A rollback anchored on a
  forgeable store manufactures false assurance and is worse than an honest hard-deny/contain posture (extends A40189
  reviewer synthesis; `AILLM-Safety` §17). Harden the store first.
- **As the sole control.** No single mechanism in the corpus is robust alone (`defense-in-depth` §1, §11); safe
  rollback is the recovery leg of defense-in-depth, not a replacement for gates, isolation, or monitoring.
