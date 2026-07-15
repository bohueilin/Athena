# Adversarial-ML-Attacks — Partial Synthesis (chunk 1 of 40 papers)

Scope: AAAI-26 "Adversarial-ML-Attacks" corpus, papers A38095–A39603 (this chunk only).
Evidence-integrity: every claim traces to a paper's research card; author findings vs. reviewer
synthesis are distinguished; calibrated language only ("reduced ASR against the tested attacks",
"demonstrated under the evaluated threat model", "not evaluated against"). Numbers appear only where
a card states them.

## Chunk composition (important caveat)
This chunk is heterogeneous and partly mislabeled. Roughly three groups:
1. **Core adversarial-ML** (majority): evasion / adversarial examples, data poisoning, backdoors,
   membership-inference & reconstruction privacy attacks, and their defenses — mostly on vision,
   graph, and (a few) LLM/VLM systems.
2. **Adjacent-but-real security** framed with game theory: audit-mechanism design (A38722),
   network-formation robustness (A38730), layered cyber-defense via Gittins indices (A38761).
3. **Corpus mislabels** where "adversarial" means a GAN/training technique, not a threat actor:
   recommendation (A38469, A38489), image compression (A38515), continual-learning concept
   separation (A39438), VLM hallucination mitigation (A39336), DP synthetic data (A39382), and an
   adversarial-RL self-play method for error diagnosis (A38785). These carry little-to-no
   attack/defense evidence and are flagged per-card as `insufficient`/peripheral. Downstream users
   must not cite them as adversarial-robustness evidence.

Direct agent/LLM relevance is the minority; most core papers are vision/graph/tabular ML. Their
value to a Guardian-Agent stack is **architectural/transferable** (see Product implications), not
drop-in numbers.

## Dominant threat models
- **Inference-time evasion of perception models** is the single most common threat: an attacker adds
  bounded or unrestricted perturbations to inputs so a classifier/detector/depth-estimator/ReID model
  outputs the wrong thing. Knowledge ranges white-box (A38137, A38320, A38340), gray/black-box
  transfer (A38325, A38422), to strict hard-label/decision-only black-box (A38127) and joint
  transfer+query black-box (A38416). Physical-world deployment (printed patches, whole-vehicle
  textures) is a recurring sub-threat for embodied/AD perception (A38095, A38137, A38320).
- **Training-time / supply-chain poisoning** is the second axis: data poisoning of a training set
  (A39301, A39318, A39428, A38328, A39290), backdoors planted before the victim ever sees a
  downstream task (A39480 dormant CLIP backdoor, A39593 graph-foundation-model backdoor, A39577
  time-series backdoor), and poisoning of federated updates (A38328, A39290, A39560). The unifying
  assumption is *misplaced trust in externally-sourced models or data* (model hubs, public datasets,
  crowd labels, federated clients).
- **Privacy inference** is a distinct third axis: membership inference (A38134, A38576, A39276,
  A39449), attribute inference and gradient leakage in federated settings (A39500), and prompt/hidden-
  state reconstruction in split LLM inference (A38853). The recurring insight is that *legitimate
  access is the attack surface* — dual-view unlearning verification (A38134), released open weights
  (A38576, A39276), transmitted activations (A38853).
- **Strategic / game-theoretic adversaries** (A38722, A38730, A38761): agents who game a committed
  policy and coordinate on the worst-case equilibrium, rather than perturbing an ML model.

## Major attack families
- **Adversarial examples / evasion.** Diffusion-generated naturalistic patches (A38095 via
  collaborative LLM agents, A38137 Diff-NAT), object-localized unrestricted UAEs (A38325 ObjectAdv),
  3D disparity-consistent physical camouflage against stereo depth (A38320), ensemble CNN↔ViT transfer
  (A38422 NAMEA), query-efficient hard-label ℓ2 attacks with proved O(1/T²) convergence (A38127), and
  a dual attack that fools a ViT *and* forges a coherent-but-false explanation (A38340 A-SAGE).
- **Data poisoning.** Targeted label-flipping whose minimum flip-count is NP-Complete to measure
  (A39301); "deferred" poisoning via input-Hessian singularization that leaves clean accuracy intact
  but makes the deployed model fragile (A39318); adversarial *missingness* — steering estimates by
  selectively hiding existing entries, bypassing insertion/perturbation defenses entirely (A39428);
  boundary-adaptive (A38328) and subnet-concentrated "pill" (A39290) model-poisoning that hide inside
  robust-aggregation trust regions.
- **Backdoors.** Finetuning-activated *dormant* backdoors in distributed CLIP checkpoints (A39480),
  pretraining-time label-free persistent backdoors in graph foundation models (A39593), and
  temporally-decoupled backdoors in time-series forecasting (A39577). Common design goal:
  dormant/undetectable before deployment, lethal after the victim's own adaptation.
- **Privacy/inference attacks.** Dual-view unlearning membership amplification (A38134),
  amplification-via-unlearning MIA on graph pretrained models (A38576), distillation-based reference-
  model MIA on LLM recommenders (A39449), and hidden-state inversion recovering prompts in split LLM
  inference (A38853).

## Major defense families
- **Adversarial / robust training.** Metric-aware AT for ReID (A38392 DDDefense), selective
  budget-constrained non-zero-sum AT for humanoid control (A38949 SA2RT), semantic-aware margin +
  hyperspherical energy for CLIP zero-shot robustness (A39603 TIMA), edge self-adversarial GCL
  augmentation (A39085), and curvature-minimizing training proposed against A39318.
- **Input intervention / purification / detection.** Diffusion reconstruction-error purification of
  poisoned SD training images (A38345 UDAP, "verify by reconstruction"); RL red-mask input masking +
  retraining to break VLM backdoor attention coupling (A38121 SRD); disentangle-and-discard of
  adversarial-vulnerable features in cross-modal hashing (A38659 DRFGD).
- **Aggregation / distributed integrity.** Semi-verified, dimension-free Byzantine-robust mean
  estimation using a small trusted anchor set (A39560).
- **Configuration-as-defense.** Hyperparameter/implicit-regularization tuning to jointly resist
  transfer- and query-based black-box attacks (A38416).
- **Privacy defenses.** Direction-preserving stochastic scaling of transmitted activations (A38853),
  dual-stochastic VAE + gradient-reversal attribute unlearning for federated recommenders (A39500),
  DP-SGD synthetic-data generation (A39382).
- **Mechanism / policy design.** Optimal audit-rate policies against strategic misreporting (A38722);
  Gittins-index layered-defense allocation against adaptive attackers (A38761).

## Strongest replicated findings
- **"Hiding the signal is not a security boundary."** Decision-only/hard-label APIs remain attackable
  with improving query efficiency (A38127); model smoothness helps query robustness but *hurts*
  transfer robustness — a proven no-free-lunch tension (A38416); ensembling heterogeneous
  architectures does not by itself confer transfer robustness (A38422). (Reviewer synthesis: three
  independent papers converge on "obscurity ≠ robustness.")
- **Aggregate-statistics FL defenses are evadable by structured attacks** that stay inside the trusted
  region — via boundary-adaptive perturbation (A38328) or subnet-concentrated poison (A39290). Two
  independent constructions reach the same conclusion against overlapping defense sets (both name
  FLTrust, Multi-Krum, DnC, etc.).
- **Publishing a model/dataset creates a real privacy/integrity surface.** Released pretrained
  encoders leak membership even when generalization is strong (A38576); open weights enable white-box
  MIA (A39276, A39449); distributed checkpoints can carry dormant backdoors (A39480). (Reviewer
  synthesis across privacy + backdoor papers.)
- **Cross-corpus membership-inference evaluations are confounded.** A39276 shows, with theory
  (Δ_N = O(T/N) similarity-gap decay, slope 0.99±0.02, R²=0.997) and rigorous significance testing,
  that prior "near-perfect" CLIP MIA collapses to near-chance (CSA AUC 94%→51%) under strictly
  in-distribution evaluation — a strong, well-supported result with broad methodological implications
  for privacy auditing.

## Conflicting / tension findings
- **Robustness–generalization / robustness–utility trade-off** is repeatedly non-trivial and
  sometimes contested: A38416 proves a smoothness dichotomy (LR↓ helps transfer +64%, LR↑ helps query
  +28%, mutually exclusive); A39603 argues the CLIP robustness/generalization trade-off *can* be
  jointly improved (contra prior LAAT-style expansion); defenses routinely cost clean accuracy
  (A38121 up to ~15% CIDEr; A39318's own defense 0.81→0.71 ACC).
- **Purification is contested.** A38345 UDAP beats DiffPure/GridPure on most attacks but fails
  catastrophically on the MIST attack (FDFR 0.87 vs DiffPure 0.11) — its own table contradicts the
  broad "robust to diverse attacks" framing. Purification is a layer, not a gate.
- **"Adversarial" as technique vs. threat.** Multiple papers (A38469, A38489, A38515, A38785, A39336,
  A39438, A39382) use adversarial/GAN machinery constructively; their "robustness" is to benign noise
  or unintended behavior, not to an attacker — a labeling conflict flagged in every affected card.

## Defense bypasses (explicitly demonstrated)
- **Robust FL aggregation bypassed** in >90% of tested cases across 9 rules (A39290) and across
  hard/semi-soft/soft boundary families (A38328); A39290's own authored adaptive defense (cosine+
  distance) is reported insufficient.
- **Seven backdoor detectors bypassed** (Neural Cleanse, STRIP, GangSweep, TND-DL/DF, CBD, CleanCLIP)
  by A39480's dormant backdoor, because they inspect the pre-finetuning model where the payload is
  absent.
- **Classical poisoning defenses inapplicable** to adversarial missingness (A39428): nothing is
  inserted or perturbed, so sanitization/outlier-detection do not trigger; MICE (most robust imputer)
  still failed on two datasets.
- **Explanation-based oversight spoofable** (A38340): attention/LRP maps can be steered to a coherent
  but false rationale, defeating explanation-based human review.
- **DP/verification-access as attack surface** (A38134): the legitimate before/after unlearning
  comparison amplifies retained-data membership leakage.

## Benchmark / evaluation limitations (recurring)
- **Non-adaptive-attacker evaluation dominates.** Nearly every defense (A38121, A38345, A38392,
  A38416, A38659, A39085, A39500, A39603) is tested only against fixed/pre-existing attacks; almost
  none test an attacker aware of the specific defense. A38785 and A38949 (learned/adaptive training
  adversaries) and A39290 (authored adaptive defense) are the partial exceptions.
- **Truncated/held-back numbers.** Many cards note key tables in appendices/extended versions absent
  from the read PDF (A38095, A38328, A38722, A38761, A38853, A39290, A39301, A39428, A39500, A39560,
  A39577, A39593, A39603) — headline claims often exceed what is independently verifiable in-source.
- **Metric artifacts.** Cross-corpus MIA inflation (A39276); quality-thresholded transfer ASR
  inflates evasion success (A38325); MIA papers omit TPR@low-FPR and variance (A39449); naturalness
  judged by small perceptibility counts or an LLM judge, not human studies (A38095, A38137, A38785).
- **Narrow scope.** Vision-classifier/single-backbone/single-dataset evaluation is common
  (A38416/A38422 ImageNet-only; A39318 CNN-only; A39480 CLIP-only; A38949 single robot). Physical-
  world quantitative robustness is frequently asserted with truncated tables (A38095, A38137, A38320).

## Recurring implementation patterns
- **Diffusion models as the attacker's generative prior** (A38095, A38137, A38325, A38345 defensive
  inverse) — search a smooth natural-image manifold for natural-yet-adversarial inputs.
- **Bi-level / simulate-the-victim optimization**: simulate the victim's future finetuning
  (A39480), differentiable proxies of imputation/CCA (A39428), pill/subnet inner-outer loops
  (A39290), bi-adversarial self-meta (A38392), inner attack / outer robust loops (A38949, A39085).
- **Weaponizing benign mechanisms**: unlearning re-induces memorization for MIA (A38576) / amplifies
  membership leakage (A38134); PGD reused constructively to separate concepts (A39438) and steer
  training latents; adversarial self-play to build a stronger detector (A38785).
- **Verify-by-reconstruction / anomaly signals**: DDIM reconstruction error as poison detector
  (A38345); eigenvalue inflation as Byzantine signal (A39560); logit-margin drift as adversarial
  signal (A39603); attention-coupling/SFS as backdoor-activation signal (A38121).
- **Small trusted anchor set** to defeat majority-adversary settings (A39560 clean auxiliary set;
  FLTrust-style root data referenced across FL papers).

## Product / architecture implications (Guardian-Agent lens)
- **Treat model outputs, explanations, and hidden states as capability, not verification.** A38340
  (explanations spoofable) and A38853 (activations invertible to prompts) directly support the
  "traces/verification must come from independent verifiers, not the model's own outputs" principle.
  Gate oversight on cross-checked, tamper-evident evidence.
- **Model/dataset supply chain is a first-class attack surface.** A39480, A39593, A39318 show a clean-
  looking artifact can weaponize only after the victim's own adaptation → provenance/attestation and
  *post-finetuning* red-teaming belong in model onboarding, not just pre-finetuning scanning.
- **Perception for physical AI needs cross-modal/temporal verification.** A38095, A38137, A38320
  (single-modality perception is evadable, even by natural-looking or disparity-consistent physical
  artifacts) argue for multi-sensor voting and consistency checks before an action gate trusts "no
  obstacle."
- **Defense-in-depth over single filters.** FL aggregation (A38328/A39290), purification (A38345
  MIST failure), and imputation (A39428 MICE failure) each show a single filter is bypassable — pair
  with identity/authentication of clients, source-influence caps, query monitoring, and runtime drift
  detection.
- **API hygiene reduces attacker leverage.** Hide confidence/logits where possible (A38095, A38127,
  A38449 logit-dependent distillation), rate-limit and monitor query trajectories (A38127, A38416),
  and log split-point/randomization state for activation transmission (A38853).
- **Policy/mechanism design against strategic agents.** A38722 (committed audit policy → truthful
  equilibrium; design to the worst-case equilibrium) and A38761 (model the attacker as *optimal and
  adaptive*, not greedy) map onto PolicyGuard/runtime-enforcement design for coordinating agents.

## Open problems
- **Adaptive-attacker robustness is largely untested** for the defenses here — the biggest evidence
  gap across the chunk.
- **No formal privacy guarantees** for most privacy defenses (A38853 uses heuristic Rouge thresholds;
  A39500 has no DP guarantee); DP where present (A39382) is asserted via budget without empirical
  attack testing.
- **Detection of dormant/process-activated backdoors** and of omission-based poisoning has no
  effective defense in-chunk (A39480, A39593, A39428).
- **Transfer to LLM/agent stacks** is mostly by analogy — poisoning-robustness theory is linear-only
  (A39301), backdoor/evasion results are vision/graph-specific; agentic prompt/tool/skill-injection is
  essentially absent from this chunk.
- **Scaling and multi-target generality**: single-target backdoors (A39577), single robot/backbone
  (A38949, A39480), moderate-dimensional-only guarantees (A39382, A39560).

## Most load-bearing papers (this chunk)
- **A38127** (hard-label query-efficient attack) — strongest evidence in-chunk (proved O(1/T²) rate +
  broad wins over 13 baselines + released code); anchors the "decision-only exposure is not a
  boundary" lesson.
- **A39276** (Rethinking MIA for CLIP) — strong theory+stats debunking of cross-corpus MIA inflation;
  the reference for how to audit foundation-model privacy honestly (distribution-matched probes,
  TPR@low-FPR, significance testing).
- **A39480** (Dormant Backdoor) — cleanest demonstration that pre-deployment inspection is blind to
  finetuning-activated supply-chain backdoors; directly motivates provenance + post-finetuning
  screening.
- **A38340** (A-SAGE) — explanations/attention as manipulable evidence; the sharpest in-chunk support
  for "capability output ≠ verification" in guardian/oversight design.
- **A39290** (Poisoning with a Pill) + **A38328** (boundary-adaptive) — together the strongest signal
  that aggregate-statistics robust FL is bypassable; argues for identity/subnet-aware defense-in-depth.
- **A38345** (UDAP) — best example of "verify-by-reconstruction" *and* an honest failure mode (MIST),
  making the case that purification is a layer, never a trusted gate.
