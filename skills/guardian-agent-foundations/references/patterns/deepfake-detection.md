# Pattern: Deepfake Detection

> **Scope of evidence.** Grounded in the AAAI-26 corpus synthesis `Deepfake-Forgery-Detection` (13 papers:
> A37071, A37334, A37421, A37473, A37553, A37865, A37945, A38060, A40886, A40907, A40928, A41234, A41525) and
> its per-paper research cards. Paper ids (e.g. `A38060`) are the stable corpus ids from that synthesis' source
> map. Every recommendation traces to at least one card.
>
> **Evidence-integrity conventions (non-negotiable).** Numeric values are **author-reported** unless labeled
> *reviewer synthesis*, and are **not independently verified**. Where a card was silent or truncated, values are
> written "not stated in paper". No absolutes ("secure", "unbreakable", "proven-safe") are used; findings hold
> "under the evaluated (largely non-adaptive) threat model" and "against the tested attacks". Direct paper
> findings are distinguished from reviewer synthesis throughout.
>
> **The load-bearing calibration for this pattern (read before designing anything).** This corpus is
> **synthetic-media forensics / content-authenticity, not agent-execution security.** Its own framing: these
> detectors "produce an *evidence signal an agent consumes*, not a control on the agent's own tool/skill/MCP
> surface." Three replicated cautions bound every claim below. (1) **Cross-generator / cross-type / cross-dataset
> generalization is the central, replicated failure mode** — single-source detectors overfit generator-specific
> artifacts and collapse on unseen generators (A37071, A37334, A37421, A37473, A37553, A40886, A40907, A41234).
> (2) **Adaptive / anti-forensic robustness is essentially unmeasured across the entire corpus** — the only
> demonstrated adaptive attacker (A41525) is a K-12 teaching classifier, not a defense from this set. Every
> detector here is demonstrated under a **non-adaptive, distribution-shift threat model**; adaptive-adversary
> robustness **requires production validation** and is currently unestablished. (3) **MLLM/VLM-generated forensic
> explanations are empirically unreliable on their own** — A38060 measured up to **67.4%** of MLLM-identified
> flaws as incorrect (direct paper finding). Treat every accuracy number as a non-adaptive upper bound; treat
> every threshold as an engineering target that requires production validation; treat a "not-flagged-as-fake"
> verdict as **"not proven authentic," never as "authentic."**

---

## Problem addressed

A consumer — a Guardian agent, a governance layer, a content-moderation pipeline, an identity/authentication
gate, a downstream model, or a human reviewer — receives a piece of media (an image, an audio clip, a video, a
face presented to a biometric check) and must answer: **is this artifact genuine, or is it synthetic / forged /
spoofed?** Getting this wrong lets manipulated media flow into decisions it should never reach: a spoofed face
authenticates as a real person (A37945), an AI-generated image passes as evidence (A37071, A37421, A38060,
A40886, A41234), a cloned voice authorizes an action (A40907), a tampered talking-face video is trusted as a
record (A40928, A37865).

The corpus establishes that a passive deepfake detector is a **probabilistic evidence signal, never an
authoritative gate.** Two findings make this non-negotiable:

- **Generalization is benchmark-dependent and expires.** Averaged SOTA masks near-chance behavior on the
  hardest in-the-wild inputs: A37071 (DADL) is GenImage-SOTA (author-reported ACC_M 92.52) yet drops to
  **~57–58%** on the harder Chameleon benchmark (57.29 / 58.13 / 57.81 across three training sources, direct
  paper finding); A40907 shows single-type audio countermeasures fall to **~30–50% EER (near chance)** on unseen
  audio types versus **3.58% average EER** when co-trained on all types (direct paper finding); A37945 reports
  intra-dataset ACC 99.41 but cross-dataset Replay-Attack **HTER 20.07** (direct paper finding). Generalization
  is empirical, per-generator, and **time-bounded** — a decaying asset (reviewer synthesis over the corpus).
- **Explanations cannot be trusted as ground truth.** A38060's ≤67.4% incorrect-flaw finding, plus A37421's
  documented "overthinking" on easy fakes, mean a fluent forensic rationale is not a verified one; explanation
  faithfulness (fluency ≠ causal correctness) is flagged for A37421, A37945, A38060.

**Deepfake detection**, as an engineering control, is therefore the discipline of turning one or more
probabilistic per-modality detectors into a **deterministic, fail-closed evidence layer**: a detector proposes a
score and (optionally) a localization / explanation; a deterministic wrapper thresholds it, routes uncertain or
out-of-distribution or unverifiable inputs to a **fail-closed default (block / require cryptographic provenance /
escalate to human review)** rather than to "authentic", gates any explanation before it is surfaced, and logs
everything for time-bounded assurance. Its honest scope, inherited from the corpus: it establishes
**probabilistic authenticity evidence** — it does **not** guarantee authenticity and does **not** withstand an
adaptive anti-forensic adversary on current evidence.

## Applicable assets and attack surfaces

- **AI-generated still images (image authenticity).** The dominant surface: GAN, diffusion, and emerging
  autoregressive/VAR outputs entering an agent, moderation queue, or evidence pipeline (A37071, A37421, A37553,
  A38060, A40886, A41234). Attack lands as an unseen-generator image the detector must classify.
- **Face media (forgery + presentation attack).** Two sub-surfaces: (a) *face forgery* — face-swap,
  reenactment, entire-face synthesis, face editing (A37473, A37334); (b) *face anti-spoofing / presentation
  attack* on an authentication gate — print, replay, 3D/paper masks, glasses, makeup, unified as 12 spoof types
  (A37945). This is the surface most directly coupled to **identity/authorization** decisions.
- **Audio (voice / sound / singing / music authenticity).** TTS, voice conversion, singing-voice synthesis,
  text-to-music (A40907). Relevant wherever a voice authorizes an action or a clip is treated as a record;
  A40907's scope is **clean audio only** (channel noise, compression, partial spoofing explicitly excluded).
- **Audio-visual video (temporal forgery localization).** Sparse, boundary-ambiguous manipulated segments in
  talking-face video — the surface where "which segment was tampered" matters, not just a video-level verdict
  (A40928).
- **Owner-protected assets (proactive provenance).** A distinct, owner-side surface: an image the owner
  perturbs *before distribution* so later tampering is localizable by an off-the-shelf verifier (A37865). The
  protective perturbation and the verifier model are themselves assets.
- **The stateful components of the detector itself (governed surfaces).** Prototype / memory banks (A37473:
  capacity 64/class, score-decay γ=0.99, Top-K=64) and noise-residual models (A41234: frozen RPE restorer →
  64-dim CRR) introduce **drift and poisoning risk** and must be governed, bounded, logged, and monitored
  (reviewer synthesis; the cards flag both as untested poisoning/normalization blind spots).
- **The verifier / backbone model as a pinned dependency.** A37865 ties tamper localization to a **specific SAM
  version**; a verifier-model change can silently break verification. Any frozen-backbone detector (CLIP ViT in
  A37473/A38060/A40886, SSL front-ends in A40907, Siglip+Phi-3 in A37945, SAM in A37865) is a governed
  dependency.
- **The explanation channel.** MLLM/VLM rationales (A37421, A37945, A38060) are a surface where an unverified,
  possibly-wrong narrative can be surfaced to a human or an action — must be gated (A38060: ≤67.4% incorrect).

## Threat model

Stated in the corpus's own terms, then extended with the gaps an implementer **must** add.

- **In scope (primary — distribution shift reframed as the adversary, non-adaptive).** 12 of 13 papers adopt a
  non-adaptive threat model in which the "adversary" is the space of generators: unseen generative models,
  unseen forgery types, unseen datasets. Robustness is measured as **generalization**, not adversarial evasion
  (A37071, A37334, A37421, A37473, A37553, A37865, A37945, A38060, A40886, A40907, A40928, A41234). Adversary
  knowledge is effectively **black-box** on the detector across the detection papers (no detector-internal
  access assumed).
- **In scope (environmental, non-adversarial corruption).** OSN JPEG compression and Gaussian noise degrade
  high-frequency forgery traces — modeled by A37553 (OSN compression erasing high-frequency traces) and A37421
  (JPEG/Gaussian robustness), but as **distribution shift, not as an anti-forensic attacker**.
- **In scope (identity / physical presentation).** A37945 covers physical presentation/spoof artifacts (print,
  replay, masks, makeup) captured as images — the digital-image manifestation of a physical spoof.
- **The one adaptive / physical exception, pedagogical.** A41525 (Breakable Machine) is the only paper with an
  adaptive attacker: a human learner iteratively spoofing a MobileNet-V2 classifier in the physical world
  (props, lighting, background) guided by CAM saliency and training-data inspection — targeted, effectively
  gray/white-box. It is an **AI-literacy resource that teaches classifier evasion, not a detection or defense
  method** (direct card statement).
- **Explicitly OUT of scope for the corpus evidence — the implementer MUST treat these as unestablished and add
  their own validation:**
  - **Adaptive / anti-forensic evasion** — an attacker optimizing against the *specific* detector
    (perturbation-suppressing post-processing, adversarial examples targeting the discrepancy signal,
    recompression/regeneration to strip cues). **Not evaluated anywhere in the corpus** (reviewer synthesis
    across nearly every card; explicitly noted for A37071, A37334, A37421, A37473, A37553, A37865, A37945,
    A38060, A40886, A40907, A40928, A41234).
  - **Perturbation removal against proactive forensics** — stripping/denoising/recompressing/regenerating an
    A37865-protected image to remove the ℓ∞ perturbation and defeat the "blank canvas" state; and
    verifier-model (SAM) version drift. Not evaluated.
  - **Poisoning / normalization of stateful detector state** — attacker-influenced training data corrupting the
    A37473 prototype bank, or heavy denoising/recompression altering the noise statistics A41234 depends on.
    Named as plausible blind spots, untested.
  - **Confidence gaming** — crafting high-confidence-but-wrong "impressions" to defeat A37421's confidence-gated
    adaptive-compute escalation. Named, untested.
- **Trust-boundary assumptions to reject.** (1) That a **"not-flagged-as-fake" verdict means authentic** — it
  means "not proven authentic"; the dangerous failure is the false negative and the control must fail closed on
  it. (2) That **averaged SOTA accuracy transfers to the hardest inputs** — A37071 Chameleon ~57–58% and A40907
  single-type near-chance EER refute this. (3) That a **fluent MLLM explanation is a correct one** (A38060
  ≤67.4% incorrect). (4) That **a detector validated on today's generators holds tomorrow** — A40886's fixed
  GAN/DM K=2 worldview is an explicit example of a bias a new family (VAR) can break.

## Control mechanism

A **deterministic verdict-and-route wrapper around one or more probabilistic detectors**, designed fail-closed
and least-privilege. The detector is stochastic; the control around it is deterministic.

1. **Per-modality detection (evidence production).** Route each artifact to the modality-appropriate detector —
   image (A37071/A37553/A38060/A40886/A41234), face-forgery (A37473/A37334), face-anti-spoofing
   (A37945), audio (A40907), audio-visual temporal localization (A40928). Cross-modality is **absent** in the
   corpus (image/audio/AV detectors are siloed, reviewer synthesis), so a unified layer must **compose
   per-modality models**, never assume one universal detector.
2. **Deterministic thresholding to a three-state verdict, not a boolean.** Map the detector's continuous score
   to `{authentic-evidence, likely-synthetic, unverified}` using pinned, versioned thresholds. `unverified`
   covers low-confidence, out-of-validated-distribution, missing-provenance, or stale-model conditions.
3. **Fail-closed routing.** `likely-synthetic` and `unverified` **both** route to the safe default —
   block / require cryptographic provenance (C2PA-style) / escalate to human review — and **never** to
   "authentic / trusted". Only `authentic-evidence` *with* corroborating provenance may pass automatically for a
   high-stakes decision (A37071, A37865 deployment implications: "combine detection with cryptographic
   provenance, watermarking, and human review for high-stakes decisions").
4. **Confidence-gated reflective escalation (cheap check → deep check).** Reuse the fast-proposer +
   confidence-gated reflective-verifier shape (A37421 adaptive Heuristic-to-Analytic reasoning; A38060 MLLM
   explanation → metric-guided Top-K refinement): a cheap detector runs first; a more expensive
   reflective/verifier stage engages **only when the fast verdict's confidence is low**. This allocates compute
   by difficulty (A37421 direct finding) — but the confidence signal must be calibrated and guarded (see
   Known bypasses).
5. **Gate explanations before surfacing.** Any MLLM/VLM rationale must pass a metric-grounded taxonomy check
   (A38060's flaw-taxonomy + quantitative-rating refinement) before it reaches a human or an action; surface it
   as *unverified supporting detail*, never as the basis for the verdict (A38060 ≤67.4% incorrect; A37421 /
   A37945 faithfulness caveats).
6. **Surface uncertainty, not just a verdict.** Emit and log the confidence score, impression-vs-final
   disagreement (A37421), localization masks (A37865, A40928, A37945), and prototype/cluster diagnostics
   (A37473, A40886) so downstream consumers can calibrate trust (synthesis product-design implication).
7. **(Optional, owner-controlled) proactive provenance.** For owned assets, embed an A37865-style protective
   perturbation pre-distribution so later tampering is localizable by a **pinned** verifier model — an
   attestation/watermarking analogue whose trust rests on perturbation survivability and verifier-version
   pinning (both untested; require production validation).

The detector is a **pluggable, replaceable evidence producer**, not a fixed oracle (synthesis architecture
implication) — generalization expires and detectors must be swapped as generators evolve.

## Preconditions and trust assumptions

- **A trusted classification/labeling foundation for training.** A37421 assumes trustworthy human annotation
  (29 trained annotators, three-way + platform-label unanimity, 11,559 high-confidence images) and that
  distilled reasoning traces are adequate supervision; A37473 trusts training face corpus/labels; A38060 trusts
  the flaw taxonomy. Poisoned or mislabeled training data undermines all of these (reviewer synthesis:
  gradient-magnitude prototype selection in A37473 "assumes clean gradients; behavior under label noise is
  untested").
- **A pinned, version-controlled backbone / verifier model.** Frozen CLIP ViT (A37473, A38060, A40886), SSL
  front-ends (A40907), Siglip+Phi-3 (A37945), off-the-shelf SAM (A37865) — each is a governed dependency whose
  version change can silently alter behavior (A37865 explicitly ties localization to a specific SAM version).
- **A validated in-distribution envelope.** Every accuracy number is conditioned on inputs resembling the
  evaluation distribution. A38060 **trains one model per GenImage subset** (not one universal detector) — its
  averages assume the deploying team recreates that per-subset structure. A40907 assumes **clean audio**. Inputs
  outside the validated envelope must be treated as `unverified`, not scored optimistically.
- **A calibrated confidence signal (for the escalation gate).** A37421/A38060's cheap-then-deep escalation
  requires that "low confidence" reliably tracks "hard/uncertain"; A37421's card explicitly flags that this
  gate "could be manipulated (adversary crafts high-confidence wrong impressions); untested." Calibration must
  be validated in production.
- **Non-adaptive adversary (the assumption you are inheriting, and must flag).** Every detection number assumes
  the adversary is *not* optimizing against this specific detector. This is the single largest inherited
  assumption; it must be stated in any assurance claim and never silently relied upon.
- **Owner control of the distribution channel (proactive path only).** A37865 assumes the owner can embed and
  distribute the protected image intact and that the invisible perturbation survives to the point of inspection
  — untested against real channels (JPEG, resize, screenshot, regeneration).
- **Detection is one signal among several.** The trust model assumes deepfake detection is **combined with**
  cryptographic provenance, watermarking/signed-provenance, and human review for high-stakes decisions — never
  the sole authority (A37071, A37865; cross-references the `signed-provenance` pattern).

## System architecture

A composed, per-modality evidence layer feeding a deterministic policy gate.

```
                         ┌────────────────────────────────────────────────┐
   media artifact  ──▶   │  MODALITY ROUTER (deterministic)                │
   (+ provenance          │  image | face-forgery | face-antispoof | audio │
    metadata if any)      │  | audio-visual  → pick composed detector(s)   │
                         └───────────────┬────────────────────────────────┘
                                         ▼
        ┌────────────────── PER-MODALITY DETECTOR (evidence producer, pluggable) ──────────────────┐
        │  FAST PROPOSER  (cheap check)                                                             │
        │    image: dual-branch discrepancy (A37071) / freq-decoupled (A37553) / real-only (A41234) │
        │    face:  CLIP residual prototypes (A37473)   antispoof: FAS-MLLM (A37945)                │
        │    audio: wavelet-prompt SSL+AASIST (A40907)  AV: deformable state-space TFL (A40928)     │
        │    img (ensemble): diffusion-timestep ensemble (A38060) / GAN-vs-DM cluster (A40886)      │
        │              │  score + calibrated confidence                                             │
        │              ▼                                                                             │
        │  CONFIDENCE GATE  ── high-confidence ─▶ emit verdict                                        │
        │              │ low-confidence                                                              │
        │              ▼                                                                             │
        │  REFLECTIVE VERIFIER (deep check, A37421 HA-R / A38060 metric-guided refinement)           │
        │              │  refined verdict + (optional) localization mask + gated explanation         │
        └──────────────┼────────────────────────────────────────────────────────────────────────── ┘
                       ▼
        ┌────────────── DETERMINISTIC POLICY GATE (fail-closed) ─────────────────────────────────┐
        │  threshold → {authentic-evidence | likely-synthetic | unverified}  (pinned thresholds) │
        │  EXPLANATION GATE: metric-grounded taxonomy check before any rationale is surfaced      │
        │  authentic-evidence + corroborating provenance ─▶ pass (auto)                           │
        │  likely-synthetic ─▶ BLOCK / flag                                                       │
        │  unverified / OOD / stale-model / missing-provenance ─▶ REQUIRE PROVENANCE or HUMAN     │
        └───────────────┬────────────────────────────────────────────────────────────────────────┘
                        ▼
        ┌──────────────────── GOVERNANCE & TELEMETRY ───────────────────────────────────────────┐
        │  pin verifier/backbone version (A37865 SAM)   bound+log+monitor stateful state         │
        │  (prototype bank A37473: cap 64/cls, γ=0.99; RPE noise model A41234)                    │
        │  log: confidence, impression-vs-final (A37421), localization masks, per-generator drift │
        │  re-benchmark cadence vs hardest sets (A37071 Chameleon), not averaged SOTA             │
        └────────────────────────────────────────────────────────────────────────────────────────┘
```

Architectural commitments (synthesis architecture implications):

- **Detectors are pluggable evidence producers, not fixed oracles.** Frozen-backbone + lightweight adapter /
  prompt / head is the dominant, operationally-favorable build (CLIP ViT, SSL+AASIST, Siglip+Phi-3 w/ LoRA,
  off-the-shelf SAM) — cheap to retrain and swap as generators evolve. A40907 reports prompt tuning uses
  **~458× fewer trainable parameters** than full fine-tuning (direct paper finding).
- **The verifier-loop generalizes to guardrails.** Fast proposer + confidence-gated reflective verifier (A37421,
  A38060) is the reusable cheap-check-then-deep-check escalation shape.
- **Stateful surfaces get their own governance plane** (prototype banks A37473; noise-residual models A41234) —
  bounded, logged, monitored update paths.
- **Cross-modality is composed, never assumed unified** — image/audio/AV are siloed.

## Recommended implementation pattern

1. **Treat every detector output as a probabilistic evidence signal feeding a fail-closed gate — never an
   authoritative allow.** Default the gate so that anything not positively established as authentic (with
   corroborating provenance) routes to block or human review. The false negative (a fake accepted as real) is
   the dangerous failure; design against it (A37071, A37421, A37553, A37945, A38060 deployment implications).
2. **Compose per-modality detectors; do not build or assume a universal one.** Pick per modality (image / face /
   audio / AV). Where the corpus offers convergent inductive biases, prefer generalization-oriented ones:
   internal-inconsistency/discrepancy (A37071), orthogonal decoupling of compression from the decision axis
   (A37553), real-only representation with feature-space pseudo-negatives (A41234), architectural clustering +
   attribution (A40886), wavelet/frequency prompts for type-invariance (A40907).
3. **Lean on frequency-domain cues where the corpus shows they are load-bearing.** High-frequency / wavelet /
   spectral features recur as the discriminative signal across modalities (A37071 multi-scale, A37553
   high-frequency traces, A37865 Daubechies-8 DWT, A38060 Fourier power-spectrum across DDIM timesteps, A40907
   HH wavelet band, A41234 DFT amplitude). A37553's ablation: high-/low-frequency bidirectional fusion is the
   **single most critical component (+7.4 accuracy when present, direct paper finding)**.
4. **Use confidence-gated reflective escalation, and calibrate the gate.** Cheap detector first; engage the
   expensive reflective verifier only on low confidence (A37421: adaptive HA-R reaches best OOD acc 78.46% by
   choosing when to think deeply; A38060: metric-guided refinement loop). Validate calibration and guard against
   confidence gaming.
5. **Gate MLLM/VLM explanations behind a metric-grounded taxonomy check before surfacing.** Anchor rationales to
   a verifiable flaw taxonomy + quantitative rating (A38060), and label them *unverified supporting detail*.
   Keep a human in the loop before consequential action (A38060 ≤67.4% incorrect; A37945 faithfulness caveat).
6. **Prefer real-only / future-proofing paradigms where enumerating generators is infeasible.** A41234 learns
   the real manifold and treats deviations as fake via feature-space pseudo-negatives — evaluated across
   GAN/diffusion/VAR and a medical distribution shift at low compute (direct paper claim: +4.51% accuracy /
   +3.93% AP over prior SOTA). This does not require collecting new generator samples for every family.
7. **For owned assets, consider proactive provenance as a complementary signal.** A37865 embeds a frequency-aware
   ℓ∞ perturbation pre-distribution so tampering shows up as anomalous SAM segmentation (training-free
   localization). Treat it as *complementary*, pin the verifier (SAM) version, and validate perturbation
   survivability through your real distribution pipeline.
8. **Govern stateful detector state explicitly.** For prototype banks (A37473), bound memory (e.g., the paper's
   64/class), log prototype turnover, and validate that stored prototypes are not attacker-controllable; for
   noise-residual models (A41234), monitor for preprocessing that suppresses the cues.
9. **Pin and version every backbone/verifier model** and record the version on every verdict (A37865 SAM
   dependency).
10. **Instrument for time-bounded generalization from day one** (see Telemetry) — detection accuracy is a
    decaying asset; schedule re-evaluation against the hardest in-the-wild sets, not averaged SOTA (A37071
    Chameleon).

## Incorrect or fragile implementation patterns

- **Treating a "not-detected-as-fake" verdict as "authentic / safe to pass."** This inverts the fail-closed
  requirement; the corpus's uniform deployment guidance is "use as a triage/evidence layer feeding human or
  policy gates, not as final authority" (A37071, A37334, A37421, A37473, A37553, A37945, A38060).
- **Trusting averaged SOTA accuracy as the operating guarantee.** A37071 is GenImage-SOTA yet ~57–58% on
  Chameleon; A40907 single-type CMs hit near-chance EER on unseen types; A37945 intra-dataset 99.41 but
  Replay-Attack HTER 20.07. Averaged numbers hide per-generator/per-type near-chance behavior (synthesis
  Section 10, direct paper findings).
- **Deploying a single-source / single-generator detector and assuming it transfers.** Cross-generator collapse
  is the corpus's central replicated failure mode (A37071, A37334, A37421, A37473, A37553, A40886, A40907,
  A41234).
- **Surfacing an MLLM/VLM forensic rationale as ground truth (or as the basis of the verdict).** A38060
  measured ≤67.4% of MLLM flaws incorrect; A37421 documents "overthinking" on easy fakes. Fluency ≠ causal
  correctness (A37421, A37945, A38060).
- **Building one "universal" detector across modalities.** Image, audio, and AV detectors are siloed in the
  corpus; a monolithic cross-modality assumption has no support (reviewer synthesis).
- **Claiming adaptive-adversary or anti-forensic robustness.** No paper evaluates it; A41525's attack is
  pedagogical. Any such claim is unsupported by this corpus.
- **Letting the verifier/backbone model version float.** A37865's localization is tied to a specific SAM
  version; an unpinned backbone can silently change behavior.
- **Leaving stateful detector state ungoverned.** An unbounded, unlogged, attacker-influenceable prototype bank
  (A37473) or a noise-residual model whose cues are silently normalized away (A41234) is a drift/poisoning
  surface.
- **Assuming environmental corruption robustness equals adaptive robustness.** A37553/A37421 handle compression
  and noise *as distribution shift*; neither is an adaptive anti-forensic attacker (reviewer synthesis).
- **Deleting the nuisance signal instead of orthogonalizing it.** A37553 documents that the prior
  gradient-reversal approach removes informative forgery features along with compression features — orthogonal
  decoupling (preserve the signal, null its influence on the decision axis) is the corrected pattern.
- **Discarding high-frequency channels because compression degrades them.** A37553's ablation shows the
  high-/low-frequency bidirectional fusion is the most critical component (+7.4).

## Verification strategy

- **Cross-generator / cross-type / cross-dataset holdout is the primary verification protocol** (train on one
  family, test on held-out families) — the corpus's core evaluation (A37071, A37334, A37421, A37473, A37553,
  A40886, A40907, A41234).
- **Report per-generator / per-type / per-benchmark breakdowns, not just averages** — averaged SOTA masks
  near-chance behavior (A37071 Chameleon; A40886 per-generator AUC; A40907 per-type EER). Verification must
  surface worst-case, not mean.
- **Include hard-sample and in-the-wild benchmarks explicitly** (A38060 GenHard hard-sample test set; A37071
  Chameleon; A37421 in-the-wild composite-pipeline + post-processed data with domain-bias-free construction —
  real and fake sourced from the same channels to avoid inflated accuracy).
- **Test environmental corruption robustness** (JPEG compression, Gaussian noise, OSN recompression) as
  distribution shift, reporting accuracy under corruption without corruption-specific training where the method
  claims robustness (A37421, A37553).
- **For explanations, audit correctness independently** — but note the corpus proxies (text-image similarity,
  BLEU/ROUGE) measure fluency/overlap, not causal fidelity (A38060, A37945, A37421). A38060's 30.1%–67.4%
  per-subset pruning rate of MLLM-generated flaws is the cautionary baseline; treat similarity scores as
  necessary-not-sufficient.
- **For localization methods, report region/segment-level metrics** (A37865 tamper masks via Otsu thresholds;
  A40928 mAP/mAR across IoU/proposal thresholds; A37945 AP@40/AP@50) at strict thresholds where boundary
  quality matters (A40928 IoU 0.95).
- **Recompute borrowed baselines under identical preprocessing where feasible** — several papers cite prior
  numbers rather than re-running them (A37473, A37553), so cross-method superiority assumes preprocessing
  parity.
- **Verify calibration of the confidence gate** used for reflective escalation (A37421) before relying on it to
  allocate compute or gate escalation.
- **Drive the full fail-closed gate end-to-end**, not just the detector: confirm that low-confidence, OOD,
  stale-model, and missing-provenance inputs all route to the safe default (block/provenance/human), never to
  "authentic."

## Metrics and thresholds

All values below are **author-reported under non-adaptive, distribution-shift conditions** and are reference
anchors, **not guarantees**; production thresholds require validation on the deploying team's own hardest sets.

- **Image detection accuracy / AUC (reference anchors):** A38060 (ESIDE) 98.91% original / 95.89% hard-sample
  average accuracy, **per-GenImage-subset training** (caveat: not one universal detector); A40886 (TriDetect)
  GenImage average **AUC 0.9882** vs next-best 0.9815, AIGCDetectBenchmark 0.9971 / 0.9869; A37071 (DADL)
  GenImage ACC_M 92.52 **but Chameleon ~57–58%**; A41234 (RealNet) +4.51% accuracy / +3.93% AP over prior SOTA
  across GAN/diffusion/VAR. A40886 baseline LGrad ~0.57 avg AUC illustrates cross-generator collapse.
- **Compression-robust image accuracy:** A37553 (DDOC) mean **~75.4% / 75.5%** under OSN compression vs ODDN
  71.4% — note **~25% residual error** in this realistic open-world setting.
- **Face forgery cross-dataset AUC:** A37473 (ResProto-FD) frame-level AUC CDF 83.8 / DFD 91.4 / DFDC 79.5 /
  Avg 84.9 (trained on FF++ c23).
- **Face anti-spoofing (identity gate):** A37945 (FaceShield) intra-dataset ACC 99.41 / HTER 0.53; cross-dataset
  S&P→W HTER 5.71; **Replay-Attack cross-dataset HTER 20.07** (the uneven-generalization warning); CASIA-MFSD
  ACC 90.59 / HTER 6.37; localization AP@40 97.78 / AP@50 95.60. **Report HTER alongside ACC** for FAS.
- **Audio EER:** A40907 (WPT-XLSR-AASIST, all-type co-trained) average **EER 3.58%** vs single-type CMs
  **~30–50% (near chance)** on unseen types — the starkest quantified generalization gap in the corpus.
- **Audio-visual temporal localization:** A40928 (DeformTrace) LAV-DF best average mAP 75.3 / average mAR 92.9;
  report across IoU 0.5/0.75/0.95 (boundary quality worst at strict IoU).
- **Explanation-quality proxies (fluency, NOT correctness):** text-image similarity, BLEU-1..4, ROUGE-L, METEOR
  (A38060, A37945, A37421). A38060 MLLM incorrect-flaw rate **up to 67.4%** is the load-bearing negative anchor.
- **Threshold guidance (engineering, requires production validation):** set the `authentic-evidence` threshold
  conservatively (favor false positives → human review over false negatives → fake accepted); define an
  explicit `unverified` band for scores near the decision boundary and route it fail-closed; set an
  OOD/staleness trigger that forces `unverified` when input falls outside the validated envelope or the
  backbone/verifier version has changed. **Truncated / not-stated numbers:** concrete headline metrics were
  truncated in the reviewed text for A37334, A37865, and parts of A41234 (recorded "not stated in paper").

## Test cases

Grounded in the corpus's own evaluation designs. Each should be run before deployment and on a recurring cadence.

1. **Cross-generator holdout (image).** Train on one generator family, test on held-out families spanning GAN,
   diffusion, and VAR/autoregressive (A41234's GAN→diffusion→VAR protocol; A40886's GAN-vs-DM). Pass criterion:
   worst-family accuracy above the deploying team's floor, not just the average.
2. **Hard-sample subset (image).** Evaluate on a deliberately harder in-the-wild set (A38060 GenHard; A37071
   Chameleon; A37421 in-the-wild composite-pipeline). Expect a large drop vs easy sets (A37071 ~57–58% on
   Chameleon); confirm the gate routes low-confidence hard samples to `unverified`.
3. **Compression / noise robustness (image).** Apply JPEG compression, Gaussian noise, and OSN recompression
   without corruption-specific training (A37421, A37553). Verify accuracy degradation is bounded and that severe
   degradation triggers `unverified`.
4. **Cross-type audio holdout.** Train on one audio type (speech), test on sound / singing / music (A40907).
   Expect single-type near-chance EER on unseen types; confirm the co-trained/all-type model or the fail-closed
   route handles it.
5. **Cross-dataset face forgery + anti-spoofing.** Leave-one-dataset-out (A37473: FF++→CDF/DFD/DFDC; A37945:
   intra + cross-dataset including the weak Replay-Attack transfer). Confirm uneven cross-domain HTER is
   surfaced, not hidden by intra-dataset numbers.
6. **Temporal AV localization boundary quality.** Score mAP/mAR at strict IoU (0.95) on AV benchmarks (A40928);
   confirm segment boundaries are actionable, not smoothed.
7. **Proactive-provenance benign-reencoding false-positive test.** For A37865-protected assets, verify benign
   re-encodings (resize, JPEG) do **not** produce spurious tamper localizations, and that the pinned SAM version
   reproduces the blank-canvas state.
8. **Explanation-gate correctness audit.** Sample MLLM/VLM rationales and measure the incorrect-flaw rate
   against the taxonomy (A38060's 30.1%–67.4% pruning baseline); confirm the gate rejects unverified rationales
   before surfacing.
9. **Confidence-calibration test.** Verify that "low confidence" tracks "hard/uncertain" so the reflective
   escalation gate (A37421) allocates compute correctly and cannot be trivially bypassed by confident-but-wrong
   inputs.
10. **Fail-closed routing test.** Feed OOD inputs, missing-provenance inputs, and stale-backbone conditions;
    confirm every one routes to block/provenance/human, never to "authentic."

## Adaptive adversarial tests

**Corpus status: essentially absent — this is the single largest gap, and the implementer must add these
tests.** No detection paper evaluates an adaptive anti-forensic attacker; the only adaptive attacker in the
corpus (A41525) is a K-12 human spoofing a MobileNet-V2 classifier in the physical world via CAM saliency and
training-data inspection — pedagogy, not a robustness test of any defense here. Treat the following as
**required production validation**, and treat all results as unestablished until run:

- **Anti-forensic post-processing against image detectors.** Apply adversarial perturbations, blur,
  recompression, and regeneration crafted to suppress the specific discriminative signal (e.g., A37071's
  inter-branch discrepancy; A41234's noise residuals; A37553's high-frequency cues). A37071's card explicitly
  flags "no evaluation against post-processing crafted to suppress the inter-branch discrepancy."
- **Perturbation removal against proactive provenance (A37865).** Strip / denoise / recompress / regenerate the
  protected image and measure whether the ℓ∞ perturbation survives and the blank-canvas tamper signal persists.
  Also test **verifier-model (SAM) version drift** and cross-model transfer. All untested in the paper.
- **Prototype-bank poisoning (A37473).** Introduce attacker-influenced or label-noisy training samples and
  measure prototype drift and its effect on cross-forgery AUC; the card flags the bank as an untested
  poisoning/drift surface and gradient-magnitude selection as untested under label noise.
- **Noise-statistic normalization against real-only detectors (A41234).** Apply heavy denoising/recompression
  that normalizes the noise statistics RealNet depends on and measure detection collapse (named blind spot).
- **Confidence gaming against the escalation gate (A37421).** Craft high-confidence-but-wrong "impressions" and
  measure whether the reflective-verifier escalation is bypassed (named, untested).
- **Physical / embodied spoofing of any deployed classifier (A41525 as the intuition source).** For
  face-anti-spoofing or physical-presentation gates (A37945), test props, lighting, and background manipulation
  guided by saliency — the one concrete adaptive-attack shape the corpus demonstrates, albeit pedagogically.
- **Reporting discipline:** any assurance statement must scope results to the non-adaptive threat model actually
  tested and explicitly flag adaptive robustness as **requiring production validation** (synthesis launch/assurance
  implication).

## Telemetry requirements

Log as tamper-evident audit records (cross-reference `tamper-evident-traces` / `signed-provenance`):

- **Verdict and calibrated confidence score** per artifact and per detector (all papers; A37071's inter-branch
  distance is a continuous confidence signal for thresholding and logging).
- **Impression-vs-final disagreement and reflection triggers** (A37421) — a drift/attack signal; log when the
  reflective verifier overturns the fast verdict.
- **Localization masks / segment boundaries** as evidence artifacts (A37865 SAM anomaly maps + Otsu thresholds;
  A40928 tampered segments + video-level score; A37945 attack-localization AP outputs).
- **Explanation-gate outcome** — the metric-grounded refinement pass/fail and the incorrect-flaw rate (A38060),
  so surfaced rationales are auditable and the ≤67.4% baseline is monitored.
- **Per-generator / per-type / per-dataset accuracy drift** as new generators appear — monitor OOD accuracy
  (A37421), EER drift (A40907), and cross-dataset HTER (A37945) as retraining triggers.
- **Prototype-bank / stateful-state health** — prototype turnover and per-dataset AUC drift (A37473); treat
  sudden prototype-bank instability as a data-quality/drift signal.
- **Cluster / attribution assignment** where available (A40886 GAN-vs-DM family) — logged as forensic aid, with
  the caveat that attribution reliability is not independently validated.
- **Backbone / verifier model version and key parameters** on every verdict (A37865: SAM version, perturbation
  parameters, Otsu thresholds per protected asset), so a version change is visible in the audit trail.
- **Input-distribution / OOD flags** — record when an input falls outside the validated envelope (A38060
  per-subset scope; A40907 clean-audio scope) and was routed `unverified`.
- **Decision provenance** — which detector(s) ran, whether corroborating cryptographic provenance was present,
  and the final gate route (auto-pass / block / provenance-required / human-escalated).

## Failure handling

- **Fail closed on the false negative.** The dangerous failure is a fake accepted as authentic. Any
  `likely-synthetic` **or** `unverified` (low-confidence, OOD, stale-model, missing-provenance) verdict routes
  to the safe default — block / require cryptographic provenance / escalate to human review — never to
  "authentic" (uniform corpus deployment guidance).
- **Escalate on low confidence, do not auto-decide.** Engage the reflective verifier (A37421/A38060) on low
  confidence; if confidence remains low after reflection, escalate to human review rather than emitting a
  verdict.
- **Reject unverified explanations.** If an MLLM/VLM rationale fails the metric-grounded taxonomy gate (A38060),
  drop it or mark it `unverified supporting detail`; never let it drive the verdict or reach an action
  unreviewed.
- **On backbone/verifier version mismatch, force `unverified`.** If the running backbone/verifier version does
  not match the validated one (A37865 SAM), stop trusting scores and route to human/provenance until
  re-validated.
- **On stateful-state instability, freeze and fall back.** Sudden prototype-bank turnover (A37473) or noise-cue
  suppression (A41234) → freeze the stateful component, fall back to a governed baseline detector or human
  review, and raise a drift alert.
- **On out-of-envelope input, do not extrapolate.** Inputs outside the validated distribution (unseen modality,
  clean-audio assumption violated, per-subset scope exceeded) are `unverified` by construction.
- **Preserve evidence on every failure.** Retain the artifact, scores, masks, gated explanation, model version,
  and gate route as audit records for review and incident response (A37421, A37945 monitoring implications).

## Rollback and containment

- **Detectors are pluggable and replaceable** — swap a degraded/bypassed detector for a governed baseline
  without touching the deterministic gate (synthesis architecture implication: detectors are evidence
  producers, not fixed oracles).
- **Pin and roll back the verifier/backbone version deterministically.** Because behavior is tied to a specific
  backbone/verifier version (A37865 SAM), keep the validated version pinned; on a regression, roll back to it
  and force `unverified` for anything scored under the suspect version until re-validated.
- **Bound, log, and reversibly reset stateful state.** Prototype banks (A37473: capacity 64/class, γ=0.99
  decay) and noise-residual models (A41234) must have bounded, logged, monitored update paths and a clean-reset
  to a known-good snapshot on suspected poisoning/drift.
- **Contain to human review, not to silent allow.** The containment posture is to widen the fail-closed net
  (route more to human/provenance), never to relax it toward auto-pass.
- **Quarantine affected decisions.** When a bypass or drift is confirmed, re-open decisions that relied on the
  affected detector/version using the retained audit trail; because detection is one signal among several
  (A37071, A37865), corroborate with cryptographic provenance where available.
- **Disable proactive-provenance trust on channel change.** If the distribution pipeline changes such that
  A37865 perturbation survivability is in doubt, stop treating protected-asset localization as authoritative
  until re-validated end-to-end.

## Known bypasses

From synthesis Section 11 (defense bypasses) and per-card reviewer-identified surfaces. **No paper demonstrates
a bypass of another paper's method**; the only *demonstrated* attack in the corpus is A41525's physical-world
spoofing of a MobileNet-V2 teaching classifier. The following are **reviewer-identified, untested** bypass
surfaces — plausible, not benchmarked:

- **Perturbation stripping (A37865).** Denoising / recompressing / regenerating a protected image could remove
  the ℓ∞ protective perturbation and defeat the blank-canvas state; localization is also tied to a specific SAM
  version (a verifier-model change may break it). Not evaluated against these.
- **Prototype poisoning / drift (A37473)** and **noise-statistic normalization (A41234).** Attacker-influenced
  training data could corrupt the prototype bank; heavy denoising/recompression that alters noise statistics
  could suppress the residual cues RealNet relies on. Untested plausible failures.
- **Confidence gaming (A37421).** Confidence-based adaptive-compute gating could be gamed by an adversary
  crafting high-confidence-but-wrong "impressions." Untested.
- **Post-processing to suppress the discriminative signal (A37071).** No evaluation against JPEG/blur/adversarial
  perturbation crafted to suppress the inter-branch discrepancy.
- **Physical / embodied spoofing (A41525).** A human can iteratively spoof a deployed classifier in the physical
  world via saliency + training-data inspection — the corpus's one concrete adaptive attack, demonstrated
  against a teaching classifier and directly relevant to physical-presentation gates (A37945).
- **Distribution-channel corruption (A37553, A37421 as the closest analogues).** OSN compression already erases
  high-frequency forgery traces as environmental corruption; a motivated adversary could weaponize
  recompression — but genuine adaptive anti-forensics is not evaluated anywhere.
- **Calibrated takeaway:** every detector here is demonstrated under a **non-adaptive, distribution-shift threat
  model**; adaptive-adversary robustness **requires production validation** and is currently unestablished for
  the corpus.

## Residual risks

- **False negatives on unseen generators / hard in-the-wild inputs.** Cross-generator collapse is the central
  replicated failure mode; averaged SOTA masks near-chance behavior (A37071 Chameleon ~57–58%; A40907
  single-type near-chance EER). A residual false-negative rate persists and must be caught by fail-closed
  routing + provenance + human review.
- **Time-bounded generalization.** Detection accuracy is a **decaying asset** — inductive biases baked for
  today's families may not transfer (A40886's fixed GAN/DM K=2 worldview vs emerging VAR; A41234). Requires a
  re-benchmarking cadence.
- **Explanation unfaithfulness.** MLLM/VLM rationales are empirically unreliable (A38060 ≤67.4% incorrect) and
  scored by fluency/overlap proxies, not causal fidelity (A37421, A37945). A gated explanation is still not a
  verified one.
- **Environmental fragility.** ~25% residual error under OSN compression (A37553); clean-audio-only validity
  (A40907); real distribution channels (resize, screenshot, regeneration) largely untested (A37865).
- **Stateful-surface drift/poisoning.** Prototype banks (A37473) and noise-residual models (A41234) carry
  untested drift/poisoning risk.
- **Cross-modality gaps.** Image/audio/AV detectors are siloed; a composed layer inherits the weakest per-modality
  detector and has no unified cross-modality validation.
- **Adaptive-adversary risk (the dominant residual).** Unmeasured across the corpus; any deployment against a
  motivated evader carries unquantified risk until production validation is done.
- **Attribution unreliability.** Generator/architecture attribution (A40886) is suggested but not independently
  validated — do not make consequential attribution claims on it.

## Relevant research (stable paper ids from the syntheses/cards)

- **A37071** — DADL: AIGI detection via dual-branch asymmetric discrepancy (Pattern-Coexistence Hypothesis,
  SHAP bimodal validation); GenImage SOTA (ACC_M 92.52) but ~57–58% on Chameleon (setting-dependence evidence);
  released code.
- **A37334** — CRDA: face-forgery generalization via RL-scheduled curriculum augmentation + IRM (training-time
  defense); concrete numbers truncated ("not stated in paper").
- **A37421** — MIRAGE / MIRAGE-R1: in-the-wild VLM reasoning detector with confidence-gated adaptive-compute
  reflective verifier; OOD acc 78.46% (adaptive HA-R); JPEG/Gaussian robustness; released code; anonymized A/B
  sources.
- **A37473** — ResProto-FD: CLIP visual-language residual prototype bank (capacity 64/class, decay γ=0.99,
  Top-K=64, λ=0.3); cross-dataset AUC Avg 84.9; stateful-surface governance example.
- **A37553** — DDOC: decision-driven orthogonal decoupling of OSN compression; ViT+CNN bidirectional
  high-/low-frequency fusion (+7.4 ablation, most critical component); ~75% mean under OSN compression.
- **A37865** — Blank Canvas: proactive frequency-aware ℓ∞ perturbation (Daubechies-8 DWT + Canny + SSIM) forcing
  SAM to "segment nothing" for training-free tamper localization; attestation analogue; released code;
  quantitative results truncated.
- **A37945** — FaceShield: explainable face anti-spoofing MLLM (detect + type + reason + localize, 12 spoof
  types); intra-dataset ACC 99.41 / HTER 0.53, Replay-Attack cross-dataset HTER 20.07; identity/authz relevance;
  released code.
- **A38060** — ESIDE: diffusion-timestep-ensembled detection + metric-grounded MLLM refinement gate; ≤67.4% of
  MLLM flaws incorrect (explanation-trust evidence); 98.91% / 95.89% ACC; **per-GenImage-subset training**;
  released code + datasets (GenHard, GenExplain); arXiv:2503.06201.
- **A40886** — TriDetect: unsupervised GAN-vs-DM architectural clustering (JS vs KL divergence) + attribution;
  GenImage avg AUC 0.9882 (5 datasets, 13 baselines); fixed K=2 assumption is a named bias.
- **A40907** — WPT-SSL: wavelet prompt tuning for type-invariant all-type audio deepfake detection; 3.58%
  all-type EER vs ~30–50% single-type; ~458× fewer trainable params; clean-audio-only scope.
- **A40928** — DeformTrace: deformable state-space temporal localization of sparse audio-visual forgery
  segments; LAV-DF avg mAP 75.3 / mAR 92.9; two AV benchmarks only.
- **A41234** — RealNet: real-only representation learning with feature-space pseudo-negatives; evaluated across
  GAN/diffusion/VAR + medical distribution shift, low compute (+4.51% acc / +3.93% AP); future-proofing
  paradigm.
- **A41525** — Breakable Machine: K-12 AI-literacy artifact; the only adaptive, physical-world attacker (human
  spoofing MobileNet-V2 via CAM saliency); pedagogy, not a deployable control; released code.

## Evidence strength

- **Moderate overall for detection (accuracy), weak-to-absent for security (adaptive robustness).** The corpus
  provides broad, released-code, multi-generator cross-dataset evaluation (A37071, A37421, A37865, A37945,
  A38060, A41525 have released code; A38060 also released datasets), supporting the generalization claims under
  the evaluated non-adaptive threat model. Reviewer-assessed per-paper evidence is "moderate" for most detection
  papers and "preliminary" for the proactive control (A37865, quantitative results truncated) and the
  pedagogical artifact (A41525).
- **Strong, replicated (direct paper findings across multiple papers):** cross-generator/type/dataset
  generalization collapse (A37071, A37334, A37421, A37473, A37553, A40886, A40907, A41234); frequency-domain
  cues as load-bearing signal across modalities (A37071, A37553, A37865, A38060, A40907, A41234); MLLM
  explanation unreliability (A38060 ≤67.4%, direct finding).
- **Weakest / unestablished:** adaptive / anti-forensic robustness (unmeasured across all 13); explanation
  causal faithfulness (proxied by fluency/overlap only); real-distribution-channel survivability (A37865);
  attribution reliability (A40886).
- **Reviewer-synthesis vs direct findings** are separated throughout; numbers are author-reported and not
  independently verified; truncated/absent values are marked "not stated in paper" (A37334, A37865, parts of
  A41234).

## When NOT to use this pattern

- **As an authoritative allow gate.** Never use a deepfake detector to *auto-approve* content, an identity, or
  an action as genuine. It is a probabilistic evidence signal feeding a fail-closed gate; the uniform corpus
  guidance is "not as final authority" (A37071, A37334, A37421, A37473, A37553, A37945, A38060). For an
  authoritative origin claim, use cryptographic provenance / signed-provenance (`signed-provenance` pattern) —
  the corpus explicitly recommends combining detection with C2PA-style provenance for high-stakes decisions.
- **Against a motivated adaptive / anti-forensic adversary, on current evidence.** No paper validates this; do
  not deploy as the sole defense where the attacker can optimize against the specific detector. Add production
  adaptive-adversarial validation first.
- **As a control on the agent's own execution surface.** This is content-authenticity, **not** agent-execution
  security. For prompt/tool/skill/MCP injection, memory poisoning, or delegated-authority abuse, use the
  agent-security patterns (`prompt-injection-containment`, `context-and-memory-isolation`,
  `policy-permission-gates`, `least-privilege-credentials`), not deepfake detection.
- **As a cross-modality universal detector.** The corpus offers no unified cross-modality detector; compose
  per-modality models, or do not claim coverage of a modality you have not validated.
- **Where averaged accuracy is treated as the operating guarantee.** If you cannot report and act on per-generator /
  per-type / hardest-benchmark worst-case behavior (A37071 Chameleon; A40907 per-type EER), the pattern's
  fail-closed premise cannot be honored.
- **Where the backbone/verifier version or stateful state cannot be governed.** If you cannot pin the
  backbone/verifier version (A37865 SAM) or bound/log/monitor the prototype bank (A37473) / noise-residual model
  (A41234), the drift/poisoning residual risk is unmanaged.
- **For proactive provenance on assets you do not control end-to-end.** A37865 requires owner control of the
  pre-distribution embedding and an intact distribution channel; do not use it for already-published or
  third-party assets, or where perturbation survivability through your channel is unvalidated.
