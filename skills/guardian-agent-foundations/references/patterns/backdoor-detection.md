# Pattern: Backdoor Detection

> **Scope of evidence.** Grounded in the AAAI-26 corpus synthesis `Adversarial-ML-Attacks.md` (152 research
> cards). Paper ids (e.g. `A41080`) are the stable corpus ids from that synthesis's source map (§20). Backdoor /
> trigger insertion is, in the synthesis's own words, "the single largest [attack] family" (§4); the detection
> counter-family is described there as "mostly heuristic, black-box" (§5). Every recommendation below traces to at
> least one card.
>
> **Evidence-integrity conventions (non-negotiable).** Numeric values are **author-reported** under each paper's
> own evaluated threat model unless labeled *reviewer synthesis*, and are **not independently verified**; several
> sit in table regions the synthesis marks truncated (§12). Where a card was silent, values are written "not stated
> in paper". No absolutes ("secure", "clean-guaranteed", "backdoor-free") are used; findings hold "under the
> evaluated (largely non-adaptive) threat model" and "against the tested attacks". Cross-paper judgments are marked
> *(reviewer synthesis)*.
>
> **The load-bearing calibration for this pattern.** The strongest, most-replicated evidence about backdoor
> detection in this corpus is *negative and methodological*, not a working detector:
> 1. **Detectors in this corpus are repeatedly bypassed.** A dormant backdoor evades **7** named detectors
>    (`A39480`); a clean-label backdoor resists **4** (`A39935`); a flat-minima code backdoor evades **5** under
>    cross-dataset shift (`A36964`); a DRL backdoor evades **2** and survives retraining (`A39809`).
> 2. **Backdoors preserve the signals a naive monitor watches.** They keep clean accuracy (`A39935`, ≤1% drop at
>    ≤0.5% poison), plausible rationales (`A40409`), and even correct final answers while inflating reasoning
>    (`A40486`, ~17× on MATH-500) — accuracy-only QA is blind (§9.4).
> 3. **Retraining / fine-tuning does not remove the behavior** (`A40295` >99% persistence, *reinforced* by clean
>    fine-tuning; `A39809`; `A40855`) — so detection cannot assume a retrain clears a suspect artifact.
> 4. **The one adaptively-evaluated entry breaks its own naive design.** `A37117` reports an adaptive
>    trigger-inversion attacker defeats its naive lock, then fortifies with randomized smoothing.
>
> Treat backdoor detection as a **probabilistic layer with a documented false-negative surface**, deterministic and
> **fail-closed** at the *decision* boundary, paired with **provenance/attestation as the primary supply-chain
> control** (retraining does not remove backdoors, so provenance is the reviewer-synthesis first-line control —
> §14/§15) and with **post-finetuning red-teaming** (dormant backdoors are invisible before the victim's own
> fine-tuning — `A39480`, `A39593`, `A39318`). No detector in the corpus offers certified robustness against an
> adaptive adversary (§1, §17).

---

## Problem addressed

An agent stack ingests third-party artifacts it does not control the provenance of: pre-trained weights,
fine-tuning checkpoints, LoRA / prompt-tuning adapters, reused components (a policy network, a graph-foundation
model, a retriever), datasets, and labels. Any of these can carry an **implanted trigger behavior**: the model
behaves normally on clean inputs but produces an attacker-chosen output when a trigger is present. The corpus
documents this across nearly every modality — vision (`A39935`, `A39480`), code models (`A36964`), LLMs
(`A40295`, `A40409`, `A40486`), MLLM/LVLM instruction tuning (`A38015`, `A40867`, `A40891`), graph foundation
models (`A39593`), time-series forecasters (`A39577`), DRL policies (`A39809`), 6DoF-pose estimators (`A40855`),
LiDAR (`A40842`), and open-vocabulary detectors via prompt tuning alone (`A41121`).

Two properties make this a distinct control problem rather than a corollary of accuracy monitoring:

- **Backdoors are stealthy by construction.** They preserve clean-set accuracy (`A39935` author-reported ≤1% drop
  at ≤0.5% poison), preserve interpretable rationales (`A40409`), and can keep the *final answer correct* while
  the payload is a resource-exhaustion behavior (`A40486`: reasoning length inflated ~17× on MATH-500, answers
  correct). *(reviewer synthesis §9.4: accuracy-only QA does not reveal them.)*
- **Backdoors survive the obvious remediation.** Ordinary clean fine-tuning does not remove — and in `A40295`
  (P-Trojan) is engineered to *reinforce* — the behavior (author-reported >99% persistence); `A39809` re-injects
  after retraining; `A40855` leaves a residual pose offset. *(reviewer synthesis §9.3: provenance/attestation, not
  adaptation, is the control.)*

**Backdoor detection** is the control that produces an **evidence signal** about whether a candidate artifact (or
a live input) carries an implanted trigger, so a Guardian layer can quarantine, defer to human review, or refuse
to promote it. Its honest scope, inherited from the corpus: it is a **detector, not a guarantee** — every method
in the corpus is heuristic and, where adaptively tested, degrades (§5, §11). It is a *layer* that must be paired
with provenance, post-finetuning red-teaming, and fail-closed handling, never a sole gate *(reviewer synthesis
§14/§15/§16)*.

## Applicable assets and attack surfaces

- **Pre-trained / third-party weights and checkpoints** — the primary supply-chain surface. Pre-release LLM
  backdoors (`A40295`), flat-minima code-model backdoors that transfer cross-dataset (`A36964`, author-reported
  80.1% ASR), graph-foundation-model backdoors implanted at pre-training (`A39593`).
- **Fine-tuning checkpoints and the fine-tuning step itself** — *dormant* backdoors are absent in the pre-finetune
  model and only activate after the victim's own downstream fine-tuning (`A39480` CLIP, `A39593`, `A39577`,
  `A39318` deferred-activation). This is the reason pre-finetuning inspection is blind and post-finetuning
  screening is mandatory *(reviewer synthesis §15)*.
- **Parameter-efficient adapters** — LoRA and prompt-tuning are injection surfaces requiring **no base-weight
  retraining** (`A41121` open-vocabulary detector via prompt tuning only; LoRA-based injection recurs in §13).
- **Datasets and labels** — poison-only / clean-label supply-chain injection (`A36961` audio, `A37349` clean-label
  physical, `A39935` clean-label) and dataset-distillation-as-poisoning (`A37119`, `A37349`).
- **Reused components in a larger system** — DRL policy networks and their post-training (`A39809`); the
  inter-agent / federated aggregation surface (`A39778`, `A40859`, `A40051` federated-graph backdoor).
- **The live input stream at inference** — runtime *trigger* detection (as opposed to offline model screening):
  token-confidence runs (`A40897`), text-perturbation consistency (`A40891`), manifold/OOD scoring (`A40301`).
- **VLM/MLLM instruction-tuning and multimodal inputs** — multi-target backdoors (`A38015` MTAttack, via
  proxy-space partitioning — a reason to scan for *multiple coexisting* backdoors), test-time attention-hijacking
  payloads (`A40867`).
- **Verifier / reward models** — a triggered/gamed behavior in a scoring component: Process Reward Models assign
  high scores to logically invalid steps (`A40584`, author-reported an impossible constraint scored 0.973) — the
  detector/verifier is itself an attack surface.
- **The detector's own trusted assets** — its clean reference set and (where required) a clean-twin model are
  security-sensitive inputs. Some methods claim to avoid a clean twin (`A41080` attention-head similarity); others
  depend on a small trusted clean set as a security asset (`A40902`, `A40904`).

## Threat model

- **In scope — the adversary who ships a backdoored artifact into your supply chain.** Controls training data, a
  reused component, labels, or the pre-release model; the victim later trusts and deploys it (synthesis §3 cluster
  1, "the largest cluster"). Sub-cases:
  - *Poison-only / clean-label*, no label control, ≤1% accuracy cost (`A36961`, `A37349`, `A39935`).
  - *Dormant / deferred*, absent until the victim's own fine-tuning or a later trigger condition (`A39480`,
    `A39593`, `A39577`, `A39318`).
  - *Fine-tune-persistent*, engineered so clean fine-tuning reinforces rather than removes (`A40295`,
    author-reported >99% persistence; `A39809`; `A40855`).
  - *Multi-target / distributed-trigger*, multiple coexisting payloads or per-target triggers mimicking natural
    error (`A38015` MTAttack; `A40894` A2X All-to-X).
- **In scope — the runtime attacker who supplies a trigger input** to an already-deployed model (per-input trigger
  detection): the trigger arrives in text, image, LiDAR, or a prompt (`A40897`, `A40891`, `A40842`, `A40867`).
- **The strongest adaptive case to design against (the one adaptive-evaluation anchor).** `A37117` models an
  **adaptive trigger-inversion attacker** who is aware of the detection/lock mechanism and inverts candidate
  triggers to defeat a naive design; the paper reports the naive design is broken and is then fortified with
  randomized smoothing (author-reported reversed-accuracy 9.25% ≈ clean 9.47%; authorized accuracy 86.2%→73.9%).
  This is the methodological bar a serious backdoor-detection deployment should target *(reviewer synthesis: it is
  the corpus's cleanest adaptive-attack treatment for this family, §11)*.
- **Knowledge assumptions cluster** as: black-box on the deployed model for runtime trigger detectors (`A40897`
  top-1 probabilities only; `A40891` I/O perturbation) — deployable client-side against untrusted providers
  *(reviewer synthesis §13)*; white/grey-box on weights or activations for internal-signal detectors (`A41080`
  attention heads, `A40366` Mahalanobis+spectral, `A40587` middle-layer gradient norms, `A40867` deep-layer
  attention).
- **Trust-boundary assumptions to reject.**
  1. That **clean-set accuracy (or a plausible rationale, or a correct final answer)** implies the absence of a
     backdoor — false (`A39935`, `A40409`, `A40486`, `A40867`).
  2. That **inspecting the artifact you received** covers dormant payloads — false; dormant backdoors are absent
     until fine-tuning/activation (`A39480` evades 7 detectors precisely because the payload is not yet present).
  3. That **retraining / fine-tuning launders a suspect artifact** — false, and can *strengthen* the backdoor
     (`A40295`, `A39809`, `A40855`).
  4. That **one backdoor per artifact** is the scope — false (`A38015` multi-target).
  5. That a **detector's own score is trustworthy** — verifier/reward scores are game-able (`A40584`);
     explanation-based review is spoofable (`A40409` rationale preserved; `A38340` forged coherent-but-false
     explanations).
- **Explicitly out of scope for the corpus evidence (the implementer MUST treat as unmeasured).**
  - *Adaptive, detector-aware evasion in general* — untested for essentially every detector here except `A37117`;
    the corpus's most-replicated gap (§9.1, §12, §17).
  - *Detection of dormant / process-activated / omission-based poisoning* — "no effective in-corpus defense"
    (`A39480`, `A39593`, `A39428`; synthesis §17).

## Control mechanism

A **deterministic, fail-closed screening-and-flagging pipeline** that emits an evidence signal, with the *decision*
(promote / quarantine / defer) outside the candidate model's control plane:

1. **Screen artifacts at onboarding, on internal signals — not on I/O accuracy.** Because backdoors preserve
   accuracy/rationale/answer (`A39935`, `A40409`, `A40486`), the detection signal must be an internal or
   perturbation-based one, chosen for the asset:
   - *Attention-head cosine similarity* between heads, trigger-agnostic and (author-claimed) requiring no clean
     twin (`A41080`; author-reported separation e.g. BadNets 0.9921 backdoored vs 0.9149).
   - *Representation-space anomaly* — Mahalanobis + spectral fusion (`A40366`), manifold OOD-likelihood
     (`A40301`), embedding-stability under masking (`A39803`), density-based poisoned-sample detection during
     contrastive pre-training (`A37141` DIFT).
   - *Deep-layer attention-hijacking concentration* as the mechanism a backdoored MLLM exhibits (`A40867` PurMM).
   - *SAE / causal-feature identification* for a gamed verifier/reward behavior (`A40584`).
2. **Detect triggers at runtime, black-box, on the live stream.** Token-confidence sequence-lock on top-1
   probabilities only (`A40897` ConfGuard); text-perturbation semantic-consistency + confidence-drift
   (`A40891` Trap-on-Text). Deployable client-side against an untrusted provider *(reviewer synthesis §13)*.
3. **Decide deterministically, environment-side, fail-closed.** A positive (or ambiguous) detection ⇒
   **quarantine / do-not-promote / defer to human** — never "flagged but shipped anyway". The decision runs
   outside the model being screened.
4. **Repair is a separate, optional, non-authoritative layer.** Detect-then-repair (purification) exists —
   test-time attention zeroing (`A40867` PurMM), directional-mapping + adversarial-KD removal (`A40902` BeDKD),
   LRP-neuron sparse training (`A40904` CL-Guard), input masking (`A38121` SRD), server-side multi-teacher
   distillation (`A40051`), topology-aware detect + GAN recovery (`A40908` HealSplit) — but purification is a
   **layer, not a gate**: `A38345` (UDAP) beats several purifiers yet fails catastrophically on one attack
   (author-reported FDFR 0.87 vs 0.11), so a "purified" artifact is not a "clean" artifact *(reviewer synthesis
   §10)*.
5. **Emit the result as evidence into the autonomy-trace console**, paired with provenance and post-finetuning
   red-teaming — *detection, not proof of cleanliness* (§14/§16).

## Preconditions and trust assumptions

- **Provenance/attestation is the primary supply-chain control; detection is the complement, not the substitute.**
  Retraining does not remove backdoors and accuracy does not reveal them, so the synthesis's first-line
  recommendation is crypto-provenance/attestation for weights, components, datasets, labels, and retrieval corpora
  (§15). Backdoor detection is added *on top of* provenance, not instead of it *(reviewer synthesis)*. (Provenance
  itself is covered by the sibling `signed-provenance.md` pattern.)
- **Screening happens post-fine-tuning, not only on the received artifact.** Dormant backdoors are invisible
  pre-finetuning (`A39480`, `A39593`, `A39318`); onboarding must red-team *after* any downstream fine-tuning
  (§15/§16).
- **Scan for multiple coexisting backdoors, not one.** `A38015` (MTAttack) implants multiple targets via
  proxy-space partitioning; a single-trigger assumption under-covers (§15).
- **A trusted clean reference exists where the method needs it.** `A40902`/`A40904` use a small trusted clean set
  as a security asset; `A40366` fuses with distillation-unlearning; treat the clean set as a governed asset. Some
  methods claim to avoid a clean twin (`A41080`) — verify that claim on your stack rather than assuming it.
- **The false-positive budget is set deliberately and per-dataset.** Detector FPR is dataset-dependent and can be
  high: `A40897` (ConfGuard) reports author-reported FPR up to ~21.95% on Shakespeare-style text. `A37389`'s card
  flags a *missing* benign-FPR as undercutting a prompt-firewall (§8/§12). A detector with no measured benign-FPR
  is not deployable.
- **The detector's score is evidence, not verdict.** Verifier/reward scores are game-able (`A40584`) and
  explanations are spoofable (`A40409`, `A38340`); do not let a single detector score auto-authorize promotion.
- **This is a layer, not the sole control.** Every relevant card converges here: pair with provenance,
  post-finetuning red-teaming, human review, and runtime telemetry (§14/§15/§16).

## System architecture

Screening happens at onboarding (and re-runs after any fine-tuning); trigger detection runs on the live stream;
both feed one evidence bus with a fail-closed decision.

```
  SUPPLY CHAIN (untrusted)                       DEPLOYMENT (runtime)
  ┌───────────────────────────┐                  ┌──────────────────────────────┐
  │ third-party weights /     │                  │ live input stream            │
  │ checkpoint / LoRA /       │                  │ (text, image, LiDAR, prompt) │
  │ adapter / dataset / labels│                  └──────────────┬───────────────┘
  └─────────────┬─────────────┘                                 │
                │  (+ any downstream fine-tuning — dormant       │
                │   backdoors activate here: A39480/A39593)      v
                v                                   ┌──────────────────────────────┐
  ┌───────────────────────────────────────┐        │ RUNTIME TRIGGER DETECTOR     │
  │ ONBOARDING SCREEN (post-fine-tune)     │        │  token-confidence run (A40897)│
  │  attention-head sim   (A41080)         │        │  perturb-and-compare (A40891) │
  │  Mahalanobis+spectral (A40366)         │        │  manifold/OOD score  (A40301) │
  │  manifold OOD         (A40301)         │        └──────────────┬───────────────┘
  │  deep-layer attention (A40867)         │                       │
  │  density / SAE        (A37141/A40584)  │                       │
  │  SCAN FOR >1 backdoor (A38015)         │                       │
  └──────────────┬────────────────────────┘                       │
                 │                                                 │
                 └───────────────┬─────────────────────────────────┘
                                 v
              [ DETERMINISTIC DECISION — env-side, outside model control ]
                                 │
             positive / ambiguous / detector-error / timeout
                                 │
        ┌────────────────────────┴───────────────────────────┐
        v (FAIL CLOSED)                                        v (no detection)
  quarantine / do-not-promote / defer to human           admit as EVIDENCE (not proof) →
  (never "flagged but shipped")                          autonomy-trace console + audit
        │                                                 + provenance/attestation (A39*/§15)
        v (optional, non-authoritative)                          │
  detect-then-REPAIR layer                                       v
  (A40867/A40902/A40904/A38121/A40908) ── purified ≠ clean ──► RE-SCREEN, do not trust
  (A38345 catastrophic-failure caveat)
```

Overlay: the whole pipeline sits *downstream of* provenance/attestation (§15). Detection catches what provenance
does not attest; provenance covers what detection cannot see (dormant/adaptive) *(reviewer synthesis)*.

## Recommended implementation pattern

Deterministic, fail-closed, least-privilege, internal-signal-based:

- **Screen on internal / perturbation signals, never on I/O accuracy.** Use attention-head similarity (`A41080`),
  representation-space anomaly (`A40366`, `A40301`, `A39803`), density-based pre-training detection (`A37141`), or
  deep-layer attention concentration (`A40867`) — because accuracy, rationale, and answer are all preserved by the
  attack (`A39935`, `A40409`, `A40486`).
- **Re-screen after every downstream fine-tuning.** Pre-finetuning inspection is blind to dormant payloads
  (`A39480`, `A39593`); make post-finetuning red-teaming a gate in the model-onboarding flow (§15/§16).
- **Prefer trigger-agnostic detectors that do not require enumerating triggers.** `A41080` is trigger-agnostic and
  claims no clean twin; trigger-inversion approaches (Neural-Cleanse family) are both bypassed as defenses
  (`A39480`, `A39935`) and defeatable adaptively as locks (`A37117`) — do not rely on inverting a known trigger
  set.
- **Scan for multiple coexisting backdoors** (`A38015`), not a single trigger.
- **Deploy black-box runtime trigger detection where you only have I/O** — token-confidence run (`A40897`),
  perturb-and-compare (`A40891`) — usable client-side against an untrusted provider (§13).
- **Set and measure a per-dataset benign-FPR budget before shipping** (`A40897` up to ~21.95% on one dataset;
  `A37389` missing-FPR caveat). Report TPR at a fixed low FPR, not a single operating point (the MIA-side lesson
  of `A39449`/`A39276` transfers: omitting TPR@low-FPR and variance overstates a detector).
- **Treat repair as a separate, re-screened layer.** If you purify (`A40867`, `A40902`, `A40904`, `A38121`,
  `A40908`), re-run detection on the repaired artifact and record that purification can fail catastrophically on
  specific attacks (`A38345` MIST) — "purified" is not "clean".
- **Fail closed on the decision.** Positive/ambiguous/detector-error/timeout ⇒ quarantine / do-not-promote / defer
  — never fall through to promote.
- **Log the detector, its version, its threshold, its clean-reference id, and its score** as governed evidence
  (§16 runtime-telemetry candidates), so a later-discovered backdoor is traceable to what was screened.
- **Present the result as one evidence signal**, combined with provenance/attestation and human review — not as a
  cleanliness certificate (§14/§16).

## Incorrect or fragile implementation patterns

- **Gating on clean-set accuracy (or a passing eval, or a plausible rationale, or a correct answer).** The defining
  mistake: backdoors preserve all of these (`A39935` ≤1% drop at ≤0.5% poison; `A40409` rationale; `A40486`
  answers correct while reasoning inflates ~17×; `A40867` clean capability in shallow layers).
- **Inspecting only the artifact you received, before fine-tuning.** Dormant backdoors evade this entirely
  (`A39480` bypasses Neural Cleanse, STRIP, GangSweep, TND-DL/DF, CBD, CleanCLIP because the payload is not yet
  present).
- **Assuming retraining / fine-tuning launders a suspect artifact.** It does not, and can reinforce the backdoor
  (`A40295` >99% persistence, *reinforced* by clean fine-tuning; `A39809` re-injects; `A40855` residual persists).
- **Relying on a single classical detector (Neural Cleanse / STRIP / Fine-Pruning / ABL / Activation Clustering /
  Spectral Signature / ONION / BIRD / SHINE).** Each is bypassed in the corpus (`A39935` resists STRIP/NC/
  Fine-Pruning/ABL; `A36964` evades AC/Spectral/ONION/KillBadCode/EliBadCode under cross-dataset shift; `A39809`
  evades BIRD/SHINE).
- **Trusting a trigger-inversion lock as if it were robust.** An adaptive trigger-inversion attacker breaks the
  naive design (`A37117`).
- **Trusting the detector's / verifier's own score, or an explanation, as ground truth.** Reward/verifier scores
  are game-able (`A40584` invalid step scored 0.973); explanations are spoofable (`A40409`, `A38340`).
- **Assuming one backdoor per artifact** (`A38015` multi-target).
- **Treating purification as a gate.** It is a layer with catastrophic failure modes (`A38345` UDAP MIST FDFR
  0.87 vs 0.11).
- **Shipping a detector with no measured benign-FPR** (`A37389` missing-FPR caveat) or reporting a single operating
  point without TPR@low-FPR/variance (`A39449`, `A39276`).
- **Failing open** — treating "no detection" as "certified clean". Absence of a detection is not proof of absence
  of a backdoor (dormant/adaptive cases; §17).

## Verification strategy

- **Prove the decision is deterministic and fail-closed.** For every asset class, assert that positive, ambiguous,
  detector-error, and timeout outcomes all resolve to quarantine/defer, *outside* the screened model's control
  plane.
- **Test detection against attacks the attack papers built, not toy triggers.** Include clean-label (`A39935`),
  dormant/finetuning-activated (`A39480`, `A39593`), fine-tune-persistent (`A40295`, `A39809`, `A40855`),
  multi-target (`A38015`), distributed-target-mimicking-natural-error (`A40894`), and reasoning/overthinking
  payloads whose answers stay correct (`A40486`).
- **Run the post-fine-tuning screen explicitly.** Confirm the pipeline re-screens after downstream fine-tuning and
  that a dormant backdoor absent pre-finetuning is caught (or honestly flagged as undetectable) post-finetuning
  (`A39480`).
- **Measure the benign-FPR per dataset** and report TPR at a fixed low FPR with variance (`A40897` ~21.95% FPR on
  Shakespeare-style is the cautionary anchor; `A37389`/`A39449`/`A39276` FPR-and-variance discipline).
- **Confirm accuracy is not the signal.** Verify the detector fires on a backdoored model whose clean accuracy and
  rationale are indistinguishable from a clean model (`A39935`, `A40409`).
- **Test the "retrain does not clean it" property.** Fine-tune a known-backdoored artifact and confirm detection
  still fires (do not let a clean-accuracy retrain be treated as remediation) (`A40295`, `A40855`).
- **If you repair, re-screen the repaired artifact** and include an attack the purifier fails on (`A38345` MIST) to
  confirm "purified" is treated as "re-screen", not "clean".
- **REQUIRE an adaptive, detector-aware evaluation before operational reliance** — the corpus's near-universal
  omission (§9.1, §17); emulate `A37117`'s adaptive trigger-inversion attacker as the minimum bar. A passing suite
  that omits this is *no adaptive coverage*.
- **Independent validation on the target stack** — most detectors here are single-model / single-modality
  (`A41080`, `A40897`, `A40867`), so production validation is required (§12).

## Metrics and thresholds

Author-reported baselines are labeled; **target values are engineering targets requiring production validation,
not paper-derived guarantees.** Many headline tables are marked truncated in the corpus (§12) and are not
independently verified.

- **Detection separation signal (offline screening).** Attention-head cosine similarity separation — `A41080`
  author-reported e.g. BadNets 0.9921 (backdoored) vs 0.9149; use as a *per-stack-calibrated* threshold, not a
  fixed constant.
- **Benign false-positive rate (the budget you must set).** `A40897` (ConfGuard) author-reported FPR up to
  ~21.95% on Shakespeare-style text — dataset-dependent. *Target:* a documented, per-dataset FPR ceiling with
  TPR reported at that fixed FPR (`A39449`/`A39276` discipline). A detector with no measured benign-FPR is not
  shippable (`A37389`).
- **Stealth budget the detector must beat (attack side).** Clean-accuracy drop — `A39935` author-reported ≤1% at
  ≤0.5% poison. Reasoning-inflation payload with correct answers — `A40486` author-reported ~17× on MATH-500.
  Cross-dataset transfer ASR — `A36964` author-reported 80.1%, and 73.2% *after* defense.
- **Persistence-through-retraining (why detection can't be retired by a retrain).** `A40295` author-reported >99%
  persistence after clean fine-tuning; `A40855` residual offset persists.
- **Purification cost / failure (if repair is used).** Utility cost — `A38121` (SRD) author-reported up to ~15%
  CIDEr drop. Catastrophic purifier failure — `A38345` (UDAP) author-reported FDFR 0.87 (fails) vs DiffPure 0.11
  on MIST.
- **Adaptive-lock authorized-vs-reversed accuracy (the adaptive anchor).** `A37117` author-reported reversed
  accuracy 9.25% ≈ clean 9.47% after randomized-smoothing fortification; authorized accuracy 86.2%→73.9%.

Do **not** publish a single-number "backdoor-free" threshold: every detection number here is author-reported and,
except `A37117`, non-adaptive; false-negative on dormant/adaptive backdoors is the corpus's open problem (§17).

## Test cases

1. **Backdoored model with clean accuracy intact → detected (or honestly flagged undetectable).** Accuracy and
   rationale indistinguishable from clean (`A39935`, `A40409`).
2. **Dormant backdoor, absent pre-finetuning → post-finetuning screen fires; pre-finetuning screen honestly
   reports "cannot see it"** (`A39480`, `A39593`).
3. **Fine-tune-persistent backdoor → still detected after a clean-accuracy retrain** (retrain is not remediation)
   (`A40295`, `A40855`).
4. **Multiple coexisting backdoors → all targets flagged, not just one** (`A38015`).
5. **Distributed-target backdoor mimicking natural error → not dismissed as ordinary misclassification**
   (`A40894`).
6. **Reasoning/overthinking payload with correct final answers → flagged on reasoning-token telemetry, not passed
   by accuracy QA** (`A40486`).
7. **Runtime trigger input → black-box detector fires on I/O signal only** (`A40897` token-confidence run;
   `A40891` perturb-and-compare).
8. **Benign in-distribution input → does not false-positive above the per-dataset FPR budget** (`A40897`
   ~21.95% cautionary anchor).
9. **Adaptive trigger-inversion attacker → naive lock/detector broken; fortified variant holds** (emulate
   `A37117`).
10. **Repaired artifact → re-screened, and an attack the purifier fails on is included** (`A38345` MIST) so
    "purified" ≠ "clean".
11. **Classical single-detector baseline → shown bypassed** (Neural Cleanse / STRIP / Fine-Pruning / ABL by
    `A39935`; AC / Spectral / ONION by `A36964`; BIRD / SHINE by `A39809`) — do not rely on it alone.
12. **Detector-error / timeout → fail closed** (quarantine/defer, never promote).

## Adaptive adversarial tests

The corpus's single largest gap is the near-universal absence of adaptive, detector-aware evaluation — its
most-replicated meta-finding (§9.1: "wherever an attacker is allowed to be defense-aware, the defense degrades or
fails"). The implementer must add what the papers did not:

- **Emulate `A37117`'s adaptive trigger-inversion attacker — the one adaptive model in this family.** The attacker
  knows the detection/lock mechanism and inverts candidate triggers to defeat it; `A37117` reports the naive
  design is broken and requires randomized-smoothing fortification. Run this against your detector and confirm it
  degrades gracefully, not silently.
- **Dormant / activation-gated evasion** — construct a backdoor absent in the artifact you screen and activated
  only downstream (`A39480` evades 7 detectors this way; `A39593`, `A39318`). Confirm the *post-finetuning* screen,
  not the onboarding screen, is the one that catches it.
- **Persistence-through-remediation** — verify the backdoor survives (and is still detected after) a clean-accuracy
  retrain (`A40295`, `A39809`, `A40855`); treat a "retrain fixed it" claim as untested until re-screened.
- **Stealth-tuned poison** — clean-label, ≤0.5% poison, ≤1% accuracy cost (`A39935`); distributed targets
  mimicking natural error (`A40894`). Confirm the detector separates these from benign noise.
- **Detector-score gaming / explanation spoofing** — a component tuned to score well on the detector or emit a
  coherent-but-false rationale (`A40584`, `A40409`, `A38340`). Confirm the decision does not auto-authorize on a
  single score.
- **Multi-backdoor coexistence** — implant several targets and confirm the scan does not stop at the first
  (`A38015`).
- **Adaptive purifier evasion (if repair is deployed)** — include the attack that catastrophically breaks the
  purifier (`A38345` MIST) rather than only the attacks it beats.

Label all pre-adaptive results as "against the tested attacks under the evaluated non-adaptive threat model"; the
`A40905`/`A40915`/`A37117` bar — *build a purpose-built adaptive attacker* — is the standard, not testing against
fixed baselines only (§11).

## Telemetry requirements

Runtime-telemetry candidates the synthesis names for the autonomy-trace console (§16), each traceable to a card:

- **Token-confidence-run events** — the top-1 confidence-sequence signal `A40897` (ConfGuard) locks on; log the
  run and the trigger decision.
- **Attention-head-similarity statistics** — the per-head cosine similarities `A41080` uses (e.g. 0.9921 vs
  0.9149), logged for offline screening replay.
- **Deep-layer attention-concentration** — the hierarchical attention-hijacking signal `A40867` (PurMM) exploits.
- **Representation-anomaly scores** — Mahalanobis/spectral (`A40366`) and manifold-OOD (`A40301`) scores per
  screened artifact/input.
- **Confidence-drift events** — the perturb-and-compare consistency signal `A40891` (Trap-on-Text) reports.
- **Reasoning-token telemetry** — per-request reasoning length/entropy to catch overthinking/DoS-payload backdoors
  whose answers stay correct (`A40486`; the reasoning-DoS trio `A40445`/`A40486`/`A40833`).
- **Verifier/reward-score anomalies** — high scores on logically invalid steps (`A40584`).
- **Detection decisions with the artifact/input identity, detector version, threshold, clean-reference id, and
  score** — an append-only audit so a later-discovered backdoor is traceable to what was screened and passed
  *(reviewer synthesis; mirrors the immutable-audit discipline the Guardian stack applies elsewhere)*.
- **Post-finetuning-screen outcomes** — which fine-tuned checkpoints were re-screened and the result (dormant
  backdoors surface only here) (`A39480`).
- **Purification events** — what was repaired, with what method, and the mandatory re-screen result (`A38345`
  catastrophic-failure caveat).

## Failure handling

- **Fail closed.** On positive detection, ambiguous score, detector error, or timeout → **quarantine /
  do-not-promote / defer to human**; never fall through to promote or ship. Absence of a detection is *not*
  certification of cleanliness (dormant/adaptive false-negatives; §17).
- **Defer to human review as a first-class action** for ambiguous or out-of-distribution cases, and for any
  artifact whose provenance is unattested (detection is weakest exactly where provenance is missing).
- **Do not treat a retrain as remediation.** A backdoored artifact that "passes" after a clean-accuracy fine-tune
  must be re-screened, because the backdoor can persist or strengthen (`A40295`, `A39809`, `A40855`).
- **If you repair, re-screen; treat "purified" as "re-screen", not "clean".** Purification can fail
  catastrophically on specific attacks (`A38345`) and is a layer, not a gate.
- **Assume residual false-negatives and keep compensating controls active** — provenance/attestation,
  post-finetuning red-teaming, runtime trigger detection, and least-privilege on what a suspected-backdoored
  component can do. Backdoor detection is evidence, not prevention *(reviewer synthesis §14)*.

## Rollback and containment

- **Provenance and content hashes are the primary rollback lever.** Log training-data / dataset / backbone
  provenance and hashes so a discovered backdoor is traceable and a **known-good, provenance-attested checkpoint is
  restorable** (§16 "evidence-logging / rollback as the incident story for every poisoning class"). Because
  retraining does not remove the behavior (`A40295`, `A39809`, `A40855`), **rollback to an attested clean
  checkpoint — do not retrain the suspect one**.
- **Quarantine the suspect artifact and its derivatives.** A dormant backdoor propagates through fine-tuning
  (`A39480`); quarantine must include downstream checkpoints/adapters derived from the flagged base, not just the
  base.
- **Purification reduces, it does not eliminate.** Surgical/neuron/attention-level repair (`A40902`, `A40904`,
  `A40867`, `A38121`) and detect-then-recover (`A40908`) lower risk but leave residual and can fail on specific
  attacks (`A38345`); keep the quarantined original and the provenance record for forensic replay.
- **Constrain blast radius while a component is under suspicion.** Least-privilege / capability-gating on what a
  suspected-backdoored model can actuate (the `A37117` capability-gating principle; §15) limits damage before a
  clean rollback completes.
- **Residual containment gap:** a backdoor the detector *misses* (dormant, adaptive, multi-target) is uncontained
  until provenance or post-finetuning red-teaming surfaces it — containment reduces, it does not eliminate
  *(reviewer synthesis; §17 open problem)*.

## Known bypasses

Demonstrated (within papers, mostly under non-adaptive threat models) and reviewer-identified; all author-reported:

- **Dormant backdoor evades 7 detectors** — `A39480` bypasses Neural Cleanse, STRIP, GangSweep, TND-DL/DF, CBD,
  CleanCLIP, because they inspect the pre-finetuning model where the payload is absent.
- **Clean-label backdoor resists 4** — `A39935` (GCB) resists STRIP, Neural Cleanse, Fine-Pruning, ABL (author
  hedge: "most, not all").
- **Flat-minima code backdoor evades 5 under cross-dataset shift** — `A36964` evades Activation Clustering,
  Spectral Signature, ONION, KillBadCode, EliBadCode.
- **DRL backdoor survives retraining and evades 2** — `A39809` (TrojanentRL/InfrectroRL) survives retraining-based
  defenses and evades BIRD and SHINE.
- **Fine-tuning reinforces rather than removes** — `A40295` (P-Trojan) author-reported >99% persistence, with
  clean fine-tuning *reinforcing* it; `A40855` residual offset persists.
- **Accuracy / rationale / answer preserved** — `A39935` (≤1% drop), `A40409` (rationale), `A40486` (answers
  correct while reasoning inflates ~17×), `A40867` (clean shallow layers) — defeats accuracy-only and
  explanation-based review.
- **Distributed-target backdoor mimics natural error** — `A40894` (A2X) evades non-adaptive defenses by looking
  like ordinary misclassification.
- **Multiple coexisting backdoors** — `A38015` (MTAttack) defeats single-trigger scans.
- **Verifier/detector-score gaming and explanation spoofing** — `A40584` (invalid step scored 0.973), `A40409`,
  `A38340` (forged coherent-but-false explanation).
- **Adaptive trigger-inversion breaks a naive lock** — `A37117` (before randomized-smoothing fortification).
- **Purifier catastrophic failure** — `A38345` (UDAP) fails on MIST (FDFR 0.87 vs 0.11) despite beating other
  purifiers.
- **Adaptive, detector-aware attackers are essentially untested** against these detectors except `A37117` — a
  replicated absence and the largest unquantified bypass surface (§9.1, §17).

## Residual risks

- **Detection of dormant / process-activated / omission-based backdoors is an open problem** — the synthesis
  states "no effective in-corpus defense" (`A39480`, `A39593`, `A39428`; §17). A negative screen does not exclude
  these.
- **Adaptive-attacker robustness is untested** for every detector here except `A37117`; residual false-negative
  rate under a detector-aware adversary is unknown (§9.1, §17).
- **All detection numbers are non-adaptive, often single-model / single-modality, sometimes truncated** — `A41080`,
  `A40897`, `A40867`, `A40366`, `A40301` are single-family results requiring production validation (§12).
- **False positives are dataset-dependent and can be high** — `A40897` up to ~21.95% FPR on one dataset; an
  un-tuned detector can quarantine benign artifacts (`A37389` missing-FPR caveat).
- **Purification is a layer with catastrophic failure modes** — `A38345` (MIST) — and carries a utility cost
  (`A38121` ~15% CIDEr); "purified" is not "clean".
- **Multiple coexisting backdoors** may be under-covered by single-trigger scans (`A38015`).
- **Retraining does not remediate** — a suspect artifact that "passes" a post-retrain accuracy check may still
  carry the backdoor (`A40295`, `A39809`, `A40855`).
- **The detector's own score and any explanation are game-able** — do not treat them as ground truth (`A40584`,
  `A40409`, `A38340`).
- **Detection is evidence, not prevention** — it supports quarantine/rollback/governance; it does not by itself
  stop a backdoored component from acting until the decision fires *(reviewer synthesis §14)*.

## Relevant research (stable paper ids from the syntheses/cards)

All ids are corpus ids from `Adversarial-ML-Attacks.md` §20; use the internal `Axxxxx` ids, not manifest arXiv
ids, which the synthesis flags as frequently mis-extracted (§2). Author-reported unless marked.

**Detection primitives (the core of this pattern):**
- **A41080** — attention-head cosine-similarity backdoor detection; trigger-agnostic, author-claims no clean twin;
  author-reported separation e.g. BadNets 0.9921 vs 0.9149. *Offline model screening.*
- **A40897** — ConfGuard: token-confidence sequence-lock backdoor detection on top-1 probabilities only;
  author-reported dataset-dependent FPR up to ~21.95% (Shakespeare-style). *Black-box runtime trigger detection.*
- **A40891** — Trap-on-Text: text-perturbation semantic-consistency + confidence-drift MLLM backdoor detection.
  *Perturb-and-compare, I/O-only.*
- **A40366** — Mahalanobis + spectral detector fused with LoRA distillation-unlearning purification.
  *Detect-then-repair.*
- **A40301** — embedding-manifold OOD detect-and-correct for adversarial inputs. *Representation anomaly.*
- **A39803** — masking-induced embedding-stability probe for adversarial text (adaptive robustness unproven).
- **A37141** — DIFT: density-based poisoned-sample detection during contrastive pre-training.
- **A40584** — SAE + causal-feature identification for reward hacking; Process Reward Models score an impossible
  constraint 0.973 (author-reported) — verifier/detector-score-gaming caution.
- **A40587** — OR-MIA: middle-layer gradient-norm signal (primarily membership inference; internal-signal method
  relevant to screening).

**Detect-then-repair / purification (optional non-authoritative layer):**
- **A40867** — PurMM: test-time MLLM backdoor purification via a deep-layer attention-hijacking finding; the
  attention-concentration mechanism is also a *detection* signal. No retraining.
- **A40902** — BeDKD: directional-mapping + adversarial-KD NLP backdoor removal using a small trusted clean set.
- **A40904** — CL-Guard: LRP-neuron dual-network sparse-training purification.
- **A38121** — SRD: RL red-mask input masking to break VLM backdoor attention coupling (author-reported ~15% CIDEr
  cost).
- **A38345** — UDAP: DDIM reconstruction-error purification; honest catastrophic failure on MIST (author-reported
  FDFR 0.87 vs DiffPure 0.11) — the "purification is a layer, not a gate" anchor.
- **A40908** — HealSplit: topology-aware detection + GAN recovery for split-federated poisoning.
- **A40051** — server-side multi-teacher distillation vs federated-graph backdoor.
- **A37474** — SATED: training-free MLLM-verifier patch localization + SAM masks + inpainting (verifier inherits
  its own attack surface).

**Adaptive-evaluation anchor (the methodological bar):**
- **A37117** — capability-gated-in-weights "authority backdoor" lock + certified (randomized-smoothing) robustness;
  the corpus's cleanest adaptive-attack treatment (adaptive trigger-inversion attacker breaks the naive design;
  fortified reversed-accuracy 9.25% ≈ clean 9.47%; authorized accuracy 86.2%→73.9%).

**The threat detection must catch (attack side — why the naive signals fail):**
- **A39480** — dormant/finetuning-activated CLIP backdoor bypassing 7 detectors; *the* pre-finetuning-inspection-
  is-blind result.
- **A39935** — GCB: clean-label backdoor, author-reported ≤1% accuracy drop at ≤0.5% poison; resists STRIP/NC/
  Fine-Pruning/ABL.
- **A36964** — flat-minima code-model backdoor; author-reported 80.1% cross-dataset ASR, 73.2% post-defense;
  evades AC/Spectral/ONION/KillBadCode/EliBadCode.
- **A40295** — P-Trojan: pre-release LLM backdoor *reinforced* by clean fine-tuning (author-reported >99%
  persistence).
- **A39809** — TrojanentRL/InfrectroRL: DRL backdoor surviving retraining; evades BIRD/SHINE.
- **A40855** — 6DAttack: 6DoF-pose backdoor surviving clean fine-tuning (residual offset persists).
- **A40409** — rationalization-model backdoor preserving an interpretable rationale (explanation-review spoof).
- **A40486** — triggered CoT-overthinking backdoor; answers correct while reasoning inflates ~17× on MATH-500.
- **A38015** — MTAttack: multi-target LVLM instruction-tuning backdoor (scan for >1 backdoor).
- **A40894** — A2X: All-to-X distributed-target backdoor mimicking natural error (evades non-adaptive defenses).
- **A39593** — pretraining-time label-free persistent graph-foundation-model backdoor (dormant/deferred).
- **A39577** — temporally-decoupled time-series forecasting backdoor.
- **A39318** — deferred poisoning via input-Hessian singularization (clean accuracy intact) — a dormant-analog.
- **A41121** — open-vocabulary-detector backdoor via prompt tuning only (adapter surface).
- **A38340** — A-SAGE: forges a coherent-but-false explanation (supports "explanations are not detection").
- **A36961 / A37349 / A40842 / A40859 / A39778 / A40051** — supply-chain / physical / federated backdoor
  instances defining the asset breadth (audio, clean-label physical, LiDAR, vertical-FL, domain-skew FL,
  federated-graph).

**Methodological FPR/variance discipline (transferable):**
- **A39449 / A39276** — MIA-side critiques of omitting TPR@low-FPR and variance / cross-corpus inflation; the
  FPR-budget-and-variance discipline transfers to backdoor-detector reporting.
- **A37389** — APD prompt-firewall whose card flags a *missing* benign-FPR (do not ship a detector without one).

**Adaptive-attacker methodology bar (build-a-purpose-built-attacker standard):**
- **A40905 / A40915** — (watermark corpus) the "build a purpose-built adaptive remover/forger" methodology bar,
  cited by the synthesis as the standard adaptive evaluation should meet (§11).

## Evidence strength

- **The design principle** — screen on internal/perturbation signals (not I/O accuracy), re-screen post-fine-tune,
  scan for multiple backdoors, deploy black-box runtime trigger detection, set a per-dataset benign-FPR budget,
  treat repair as a re-screened layer, fail closed, and pair with provenance/attestation and post-finetuning
  red-teaming — is **convergent across independent papers** (`A41080`, `A40897`, `A40891`, `A40366`, `A40301`) and
  reinforced by an independent cluster of *attack* results showing the naive alternatives fail (`A39480`, `A39935`,
  `A36964`, `A40295`, `A40486`). This is **convergence across independent studies plus a strongly-replicated
  negative result**, not independent replication of one detector's effect size. Reviewer assessment: **moderate**
  confidence in the principle's direction; **low-to-moderate** in any specific detector's headline number.
- **Critical scoping caveat.** The corpus's backdoor *detectors* are, in its own words, "mostly heuristic,
  black-box" (§5). Only `A37117` is adaptively evaluated, and it reports its naive design is *broken* before
  fortification. **No detector in the corpus offers certified robustness against an unbounded adaptive adversary** (§1,
  §17), and dormant/process-activated backdoor detection is an explicit open problem (`A39480`, `A39593`,
  `A39428`; §17).
- **Specific numbers** (0.9921 vs 0.9149; ~21.95% FPR; ≤1% drop at ≤0.5% poison; 80.1%/73.2%; ~17×; >99%
  persistence; FDFR 0.87 vs 0.11; 9.25%≈9.47%; 86.2%→73.9%) are **author-reported, non-adaptive** (except
  `A37117`), often single-model / single-modality, and several sit in truncated tables (§12) — **not
  independently verified**.
- **The strongest evidence is the negative/methodological finding**, not a working detector: detectors get
  bypassed, accuracy does not reveal backdoors, and retraining does not remove them (§9.1/§9.3/§9.4). This is the
  highest-confidence, most-replicated result and the reason detection must be a *fail-closed layer under
  provenance*, not a standalone gate.
- **Bottom line:** a **well-motivated evidence-and-quarantine control** with modest, mostly non-adaptive empirical
  backing and one adaptive-methodology anchor (`A37117`). It is **not** a cleanliness certificate and **not**
  prevention. Every deployment claim **requires production validation**, and an **adaptive, detector-aware red-team
  plus a per-dataset benign-FPR measurement** are prerequisites before operational reliance.

## When NOT to use this pattern

- **As a substitute for provenance/attestation.** Provenance is the primary supply-chain control (retraining does
  not remove backdoors — `A40295`, `A39809`, `A40855`; §15); detection complements it. If you can attest an
  artifact's origin and integrity, do that first and add detection on top — do not rely on detection to make an
  un-attested artifact trustworthy *(reviewer synthesis)*.
- **As the sole gate or a cleanliness certificate.** It is a heuristic layer that is repeatedly bypassed
  (`A39480`, `A39935`, `A36964`) and blind to dormant/adaptive backdoors (§17). A negative screen is not proof of
  absence.
- **When you only inspect the artifact pre-fine-tuning.** Dormant backdoors are invisible there (`A39480`,
  `A39593`); without a post-finetuning screen the pattern gives false assurance.
- **When you would trust a single classical detector or a trigger-inversion lock.** Each named one is bypassed
  (`A39935`, `A36964`, `A39809`) or defeated adaptively (`A37117`).
- **When you cannot measure a per-dataset benign-FPR** — an un-tuned detector either misses backdoors or
  quarantines benign artifacts (`A40897` ~21.95%; `A37389`).
- **When "detection" would auto-authorize promotion on a single score** — verifier/detector scores and
  explanations are game-able (`A40584`, `A40409`, `A38340`); keep the promote decision human-gated for
  high-consequence artifacts.
- **When you treat purification as remediation.** Purification is a layer with catastrophic failure modes
  (`A38345`) and utility cost (`A38121`); "purified" is "re-screen", not "clean".
