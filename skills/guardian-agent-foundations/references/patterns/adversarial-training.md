# Pattern: Adversarial Training

> **Scope of evidence.** This pattern is grounded in the AAAI-26 corpus synthesis
> `syntheses/Adversarial-ML-Attacks.md` (esp. §5 "Major defense families → Adversarial / robust
> training", §9–§10 trade-offs, §12 benchmark limitations, §14–§16 product/architecture/assurance
> implications) and its underlying research cards under `research-cards/Adversarial-ML-Attacks/`.
> Load-bearing corpus papers, by role: **A38416** (Tuning for Two Adversaries — hyperparameter-
> induced robustness; the *proven* transfer-vs-query smoothness dichotomy; released code);
> **A38949** (SA2RT — selective, budget-constrained, non-zero-sum adversarial training for a real
> humanoid controller; a **learned** in-loop adversary excluded at deployment); **A39954** (AT-Field
> — game-theoretic sample re-grouping to fix AT non-convergence; marginal AutoAttack gains);
> **A38392** (DDDefense — metric-aware bi-adversarial self-meta training for person-ReID / open-set
> metric learning; released code); **A40054** (VARMAT — vulnerability-aware multimodal AT; the
> weakest-modality bound; released code); **A37396** (CBA-FAPT — few-shot adversarial *prompt*
> tuning with internal cross-modal attribution consistency); **A39603** (TIMA — CLIP zero-shot AT
> that *contests* the robustness-generalization trade-off; AutoAttack + unseen radii); **A39085**
> (EDA-GCL — edge self-adversarial augmentation for unsupervised graph contrastive learning);
> **A41122** (ASE — inference-time CoT "adversarial scenario extrapolation" for LLMs; **not**
> training-time, included to bound scope). Cautionary / red-team anchors: **A39318** (Deferred
> Poisoning — standard AT reported "not entirely effective"; curvature-minimizing training helps at a
> clean-accuracy cost); **A41144 / A42439** (shared-backbone monoculture transfer). Backdoor/
> poisoning threats that adversarial training does **not** address (provenance is the control there):
> **A39809, A40295, A40855, A39935, A39480**. Paper ids (e.g. `A38416`) are the stable corpus ids
> from the synthesis source map (§20).
>
> **Evidence integrity (non-negotiable).** Every numeric value below is **author-reported and not
> independently verified**; several headline tables are flagged **truncated** in the extracted PDFs
> (A38416, A39603, A40054, A37396) so magnitudes are not fully transcribed. Values are **non-adaptive**
> (standard, off-the-shelf attacks) unless explicitly noted: only **A38949** uses a learned in-loop
> adversary, and **A39603 / A39954 / A40054** evaluate with AutoAttack (a strong, parameter-free,
> *partly* adaptive ensemble) — none of the papers here evaluates an attacker that adapts to the
> *specific defense mechanism*. Calibrated language only: "reduced robust-accuracy loss against the
> tested attacks", "demonstrated under the evaluated threat model", "requires production validation" —
> never "secure / robust / proven-safe / unbreakable". Items marked *(reviewer synthesis)* are
> cross-paper inference or engineering practice from the synthesis, **not** a measured defense number
> from a single paper. Two corpus caveats dominate this pattern and are repeated throughout:
> **(1) adversarial training *shifts* the residual-risk surface, it does not remove vulnerability**
> (A38416 proves a no-free-lunch dichotomy; every defense here reports residual robust-accuracy loss),
> and **(2) non-adaptive evaluation systematically overstates security** — the corpus's single most
> replicated meta-finding (Adversarial-ML-Attacks §9.1, §12).

---

## Problem addressed

Machine-learning components that an agent depends on — perception classifiers, CLIP/VLM encoders,
metric-learning identity matchers, multimodal fusion models, and learned controllers — misclassify
under small, often imperceptible, input perturbations crafted at inference time. The corpus documents
this evasion surface across white-box gradient attacks (A39603, A37396, A38392, A40054), query- and
transfer-based black-box attacks (A38416), physical patches on driving/robot perception
(A42439, A40881), and structure perturbation on graphs (A39085 external study). CLIP zero-shot
accuracy can drop up to ~90% under perturbation (A39603, author-reported problem framing).

**Adversarial training (AT)** is the training-time control: include adversarially-perturbed inputs —
or a co-trained adversary — in the training loop so the learned model tolerates perturbation at
deployment. The corpus positions AT as **one risk-reduction layer for the evasion surface only**,
with two hard boundaries the pattern must state up front:

- **AT is scoped to inference-time evasion of ML/perception components.** It is *not* a control for
  prompt injection, tool-metadata poisoning, backdoors/data-poisoning, memory poisoning, or
  reasoning-DoS. Those need provenance/attestation (A39809, A40295, A40855), tool-layer intent
  binding (A40895), or availability SLAs (A37082, A40833) — separate patterns. Adversarial training
  does **not** remove an implanted backdoor: A39809 survives retraining, A40295 is *reinforced* by
  clean fine-tuning, A40855's residual offset persists — clean or adversarial retraining is the wrong
  tool for that class (Adversarial-ML-Attacks §9.3).
- **AT reduces, never eliminates, the residual risk.** A38416 *proves* (Proposition 1 + a curvature
  bound) that model smoothness improves query-robustness while *harming* transfer-robustness — a
  genuine no-free-lunch dichotomy, not a tuning artifact (§10). Every defense in this pattern reports
  a residual robust-accuracy loss and a clean-accuracy cost. The organizing thesis *(reviewer
  synthesis over §14–§16)*: **treat a hardened model's output as a lower-risk signal, not a trusted
  gate.** Consequential actions must still pass an independent, fail-closed confidence-plus-consistency
  and cross-source-corroboration check (§15).

## Applicable assets and attack surfaces

- **Perception classifiers (the canonical surface).** DNN image classifiers under black-box query and
  transfer evasion (A38416, CIFAR-10/ImageNet, ResNet family). This is the MLaaS query-API surface an
  agent's vision tools sit behind.
- **Vision-language / CLIP-style encoders.** Zero-shot classification robustness (A39603, CLIP-B/32),
  parameter-efficient prompt-tuned adapters (A37396). These are the perception/foundation-model
  components agents rely on for image understanding; a shared CLIP backbone is a **monoculture** surface
  (perturbations transfer across models built on it — A41144, A42439, §6).
- **Metric-learning / identity-authorization models.** Person-ReID and other embedding-retrieval
  matchers used as identity signals (A38392, Market-1501/DukeMTMC). Only the *feature encoder* is
  deployed; the classifier head used in training is discarded — so robustness must live on the encoder
  (A38392's core finding).
- **Multimodal fusion models.** Feature-space perturbation across modalities (A40054, HighMMT on
  CMU-MOSEI/UR-FUNNY/AV-MNIST). The **most vulnerable modality bounds** system robustness (A40054).
- **Learned controllers (physical AI).** RL humanoid/locomotion policies whose state/action inputs
  carry sensor-estimation and actuator error (A38949, Unitree G1). Perturbation set spans observation
  space (B_s) and action space (B_a).
- **Graph / relational encoders.** Unsupervised graph contrastive representations under structural
  noise and poisoning (A39085; external study uses Metattack + random edge noise).
- **The training pipeline and training data themselves** are part of the surface. AT presupposes clean
  training data; A39318 (deferred poisoning) shows a poisoner can pre-singularize the input-Hessian so
  the model ships abnormally fragile and standard AT is "not entirely effective." Training-data
  provenance is a precondition, not an afterthought (§15).
- **Out of scope for AT (state this explicitly).** LLM prompt/jailbreak resistance via weight-level
  adversarial training is **not demonstrated in this corpus.** The nearest artifact, A41122 (ASE), is
  an *inference-time* CoT procedure, not training — do not present it as adversarial training.

## Threat model

From Adversarial-ML-Attacks §3 (threat model 2, "inference-time evasion of perception models") and the
per-card threat sections. Cluster by adversary posture:

- **Inference-time evasion, white-box (strongest, most common eval).** Adversary has model access and
  crafts ℓp-bounded gradient perturbations: PGD/CW/BIM/AutoAttack against CLIP (A39603, ε ∈ {1,2,4,8}/255
  incl. radii *larger than training*), attribution-shifting visual PGD (A37396), metric-PGD toward the
  farthest-negative identity (A38392, ε ∈ {8,10}/255, 16 iters), feature-space Frobenius-bounded
  multimodal perturbation (A40054), and standard ℓ∞ suites for classifiers (A39954: FGSM/BIM/PGD-10/50/
  C&W/APGD/AutoAttack).
- **Inference-time evasion, black-box (transfer + query).** Surrogate-then-transfer, or query-budget
  oracle probing (A38416: SquareAttack score-based, HopSkipJump decision-based). No target internals;
  attacker builds a surrogate and/or queries the rate-limited API.
- **Learned / co-adaptive adversary in the training loop (A38949).** A budget-constrained RL adversary
  that *selects* which sparse timesteps to perturb and generates bounded state/action perturbations;
  co-optimized with the victim in a non-zero-sum game. This models sensor/actuator-error cascades, and
  is the closest the corpus comes to an adaptive adversary — but the adversary is *the defender's own
  training tool*, removed at deployment; it is **not** an external deployment-time attacker.
- **Structural / poisoning-adjacent (graph).** Metattack (gray/white-box structure poisoning) and
  random edge-noise, evaluated as external robustness for A39085; poisoning is separated into
  train-time vs test-time perturbation.
- **Adaptivity — the decisive caveat.** Every card's evaluation is **non-adaptive to the specific
  defense**. AutoAttack (A39603, A39954, A40054) is a strong ensemble but is not tuned to the ASAM/
  SC-MHE margin, the sample-matching cache, or the vulnerability-aware regularizer. A38416's attacks
  are standard and could be re-tuned to the induced smoothness. A38949's SAP/PAP settings are the
  authors' own. Assume a defense-aware adversary is *not* covered by any headline number (§9.1, §12).

Design consequence: model the deployment-time adversary as a **defense-aware evader with surrogate
access and a query budget**, and assume AT shifts — not closes — the boundary the adversary must cross.

## Control mechanism

A layered training-time control. No layer is a gate; the runtime layer (5) is the fail-closed backstop.

1. **Adversarial-example training / fine-tuning (the base control).** Generate perturbed inputs (PGD
   or fast-AT single-step) during training and optimize a min-max objective so the model is correct on
   both clean and perturbed inputs. Instantiated by A39603 (PGD adversarial fine-tuning of CLIP),
   A37396 (adversarial prompt tuning), A38392 (metric adversarial training), A40054 / A39954 (fast-AT).
2. **Adversary *placement* over adversary *volume* (A38949).** Do not perturb uniformly. A learned,
   budget-constrained **selective** adversary that concentrates perturbations on the few most-vulnerable
   states (SAP) beats both uniform domain randomization and full-time ("persistent") attack, which
   over-conservatizes the model (robust overfitting). Use a **non-zero-sum** objective (maximize
   V^adv − V^m, not R^adv = −R^m) to avoid the weak-adversary dilemma.
3. **Vulnerability-aware budget allocation (A40054).** Probe per-modality (or per-component)
   vulnerability = ‖∇_x L‖_F · ‖x‖_F (one forward+backward, attack-agnostic) and preferentially harden
   the weakest modality — because the weakest modality bounds system robustness.
4. **Robustness-preserving regularizers instead of blind perturbation (A37396, A39603, A40054).**
   Regularize the *internal decision basis*: cross-modal attribution consistency between clean and
   adversarial inputs (A37396), a semantic-aware margin that preserves pretrained geometry (A39603
   ASAM+SC-MHE, which lets robustness and generalization improve *jointly*), or the gradient-norm
   component only — never feature magnitude directly, which overfits (A40054).
5. **Runtime fail-closed gate around the hardened model (the load-bearing layer).** *(reviewer
   synthesis over §14–§15.)* Because AT only shifts residual risk, the deployed system must **not** act
   on the model's output alone for a consequential decision. Gate on **confidence-plus-consistency**
   (not confidence alone), **cross-sensor/cross-source corroboration** (A42439, A40881, §15), and
   deterministic thresholds; deny/degrade on disagreement.

Verification of the *training control* is **deterministic**: robust accuracy under a fixed attack suite
must exceed a pre-registered threshold on a held-out set (A39603, A39954, A38392, A40054), with the
clean-accuracy delta reported at the same operating point.

## Preconditions and trust assumptions

- **Defender controls training and the training configuration.** AT is a train-time defense; the
  defender chooses hyperparameters/perturbation budget (A38416 treats the training config itself as the
  robustness lever; A38949/A39954/A40054/A38392 all own the training loop). An attacker who controls
  training data or hyperparameters defeats the premise.
- **Training data is clean / provenance-attested.** AT assumes the clean-loss term is trustworthy.
  A39318 breaks this: a deferred-poisoning adversary who perturbs training samples (ε = 3/255) leaves a
  model that passes train/validation checks yet is abnormally fragile, and standard AT (PGD-AT, SAM,
  Smoothing, TRADES) is reported "not entirely effective." **Pair AT with data provenance** (§15) — it
  is a precondition, not an add-on.
- **A meaningful perturbation model is known.** Robustness is bounded to the trained threat: A38949's
  policy is hardened to bounded sim perturbations within (ε_s, ε_a) and a budget N_a, *not* to
  contact/dynamics disturbances (author-stated out of scope) or attacks outside the trained bounds.
  A39603 explicitly trains at ε = 1/255 and tests *unseen* larger radii — robustness to unseen strength
  is a claim to validate, not assume.
- **The deployed component is the one that was hardened (A38392).** Adversarial training can distribute
  robustness onto a head that is discarded at deployment; for metric/retrieval systems, robustness must
  be verified on the *feature encoder* that actually ships. Verify robustness on the deployment
  artifact, not a training-only proxy.
- **A learned adversary, if used, is training-only and cleanly excludable (A38949, least privilege).**
  The SAP is an offensive tool; it must **never** be present in the inference path. Keep the adversary
  module separable so it is stripped for deployment — shipping it is an added attack surface.
- **Fail-closed, least-privilege framing** *(reviewer synthesis, consistent with §15):* expose the
  minimum output granularity a client needs (hide logits/confidence where feasible — A38416/A38127,
  because richer outputs aid query attacks), and never let a hardened-but-uncertified model authorize a
  consequential action on its own.

## System architecture

```
        ┌────────────────────────── DEFENDER / TRAINING TRUST ZONE ──────────────────────────┐
 clean, provenance-       [ vulnerability probe ]        [ learned adversary (TRAINING ONLY) ]
 attested training data   ‖∇_xL‖_F·‖x‖_F per component    selective, budget-constrained SAP
   (A39318 precondition)   → weakest-modality first        non-zero-sum V^adv−V^m  (A38949)
          │                 (A40054)                        ── MUST be excluded at deployment ──
          ▼                     │                                   │  (least privilege)
   [ ADVERSARIAL-TRAINING LOOP (min–max) ]  ◄─ perturbations / attacked states ─┘
     • PGD / fast-AT inner max (A39603, A39954, A40054, A37396, A38392)
     • robustness-preserving regularizer: attribution-consistency (A37396),
       semantic-margin + geometry preservation (A39603), gradient-norm only (A40054)
     • sample re-grouping for convergence (A39954);  metric AT + FNES (A38392)
          │  robust checkpoint (verify robustness ON THE DEPLOYED ARTIFACT — A38392)
          ▼
┌──────────────────────────────── DEPLOYMENT (adversary excluded) ───────────────────────────┐
 input ─►  [ hardened model ]  ─►  output + confidence/margin
                    │
                    ▼
          [ RUNTIME FAIL-CLOSED GATE ]   ← the load-bearing layer (reviewer synthesis, §15)
            • confidence-PLUS-consistency (not confidence alone)   (§15)
            • cross-sensor / cross-source corroboration            (A42439, A40881)
            • margin / attribution-drift anomaly check             (A39603, A37396)
            • deny / degrade / escalate on disagreement (deterministic)
                    │  telemetry
                    ▼
        [ autonomy-trace console: margin, robust-acc SLA, query-trajectory, drift ]
```

Key architectural decisions: **the learned adversary is a training asset, never a deployment
component** (A38949, least privilege); **robustness is verified on the deployed artifact** (A38392's
encoder-vs-head lesson); **the runtime gate — not the model — is the security boundary** *(reviewer
synthesis, §15)*; and **AT is one layer of defense-in-depth** paired with query monitoring/rate
limiting (A38416 deployment note: hyperparameter tuning only *shifts* query-attack success), data
provenance (A39318), and cross-source corroboration for any perception-driven actuation (§15).

## Recommended implementation pattern

- **Choose adversary placement, not volume (A38949).** For learned controllers/policies, co-train a
  **selective, budget-constrained** adversary (constrained-optimization with a Lagrange-relaxed attack
  budget N_a; best regime near λ ≈ 10⁻¹ in their setup) using a **non-zero-sum** objective; alternate
  outer/inner optimization; **initialize the victim from a pre-trained policy**; keep separate value
  networks. Strip the adversary before deployment. Rationale: uniform domain randomization is
  insufficient (a DR-trained policy scored 94.4% under DR but **0%** under a learned selective attack,
  A38949 Table 1) and persistent full-time attack induces robust overfitting.
- **Regularize the internal decision basis, not just outputs.** For CLIP/VLM adapters, add
  cross-modal *attribution-consistency* loss (clean-vs-adversarial forward-attention + backward-gradient
  maps) on top of the min-max objective (A37396 CBA-FAPT), or a **semantic-aware adaptive margin plus
  hyperspherical-energy with a semantic-consistency regularizer** that preserves pretrained geometry
  (A39603 TIMA ASAM+SC-MHE) — this is the corpus's evidence that robustness and generalization can be
  improved *jointly* rather than traded off.
- **Probe and harden the weakest component first (A40054).** Compute per-modality/per-component
  vulnerability ‖∇_x L‖_F · ‖x‖_F (one forward+backward, attack-agnostic) and allocate the robustness
  budget there. **Regularize the gradient norm only** (L_Reg = β·Σ_m ‖∇_{x_m}L‖_F); do **not** directly
  regularize feature magnitude — the authors report it overfits and harms expressive capacity.
- **Fix AT convergence explicitly (A39954).** Fast/standard AT can enter cyclic non-convergence
  (cross-batch "none-potential games"), more common in AT than standard training. Layer a lightweight
  matched-clean loss — cache normalized clean features every K steps (e.g. K=100), match each
  adversarial example to its most-similar clean sample, add L = (1−λ)·L_base(X_adv,y) +
  λ·L_base(X_match,y_match). Report **Best AND Last checkpoints** (A39954) — Last exposes robust
  overfitting.
- **For metric/identity models, adversarially train the deployed encoder (A38392).** Use metric
  adversarial training (attack the embedding toward the farthest-negative identity), soften hard labels
  (FNES), add a clean-vs-adversarial feature discriminator for adversarial-clean *invariance*, and treat
  training-data imbalance as a robustness lever (balance under-represented identities). Verify robustness
  on the encoder, not the training-only classifier. **Do not import classification input-purification
  defenses** — A38392 reports they give near-0% robustness for ReID.
- **Tune the training configuration as an attack-agnostic lever (A38416), but jointly.** Learning rate,
  weight decay, momentum regulate smoothness. Because smoothness helps query-robustness but hurts
  transfer-robustness, use **multi-objective search (NSGA-II)** to find a joint operating point rather
  than optimizing one attack family — optimizing for one *masks a regression in the other*.
- **Report the operating point honestly.** Always report clean-accuracy delta at the same point as
  robust accuracy (A38416/A39603/A38392 trade-off framing), and test **unseen, larger** perturbation
  radii and a strong ensemble (AutoAttack), not only the training ε (A39603).
- **Wrap the hardened model in a fail-closed runtime gate** *(reviewer synthesis, §15):*
  confidence-plus-consistency, cross-sensor corroboration, and margin/attribution-drift monitoring;
  deny/degrade on disagreement. AT hardens the model; the gate contains what AT missed.

## Incorrect or fragile implementation patterns

- **Treating AT as a guarantee or a gate.** A38416 proves you cannot maximize transfer- and
  query-robustness simultaneously; the residual is real. A hardened model that authorizes a consequential
  action on its own output is a fragile design — the runtime gate is mandatory *(reviewer synthesis,
  §15)*.
- **Uniform / full-time adversarial perturbation.** A38949: persistent full-time attack (PAP) induces a
  large state-distribution shift and degrades performance in normal conditions (robust overfitting), and
  can be *worse* than domain randomization; a pure zero-sum objective yields a weak, non-improving
  adversary. Placement + budget + non-zero-sum beats volume.
- **Domain randomization treated as robustness.** A38949 Table 1: a DR-trained policy passed DR eval at
  94.4% but collapsed to **0%** under a learned selective attack. Randomization-only robustness tests
  overstate security.
- **Hardening a training-only head instead of the deployed component.** A38392: standard AT distributes
  robustness onto a classifier that ReID discards at test time, so robustness is lost at deployment.
  Verify on the artifact that ships.
- **Directly regularizing feature magnitude.** A40054 reports this overfits and harms expressive
  capacity; regularize the gradient component only.
- **Uniform robustness budget across modalities.** A40054: the weakest modality bounds system robustness,
  so uniform treatment wastes budget and leaves the exploitable modality under-hardened.
- **Ignoring AT convergence / reporting only the Best checkpoint.** A39954: cross-batch cyclic dynamics
  leave residual vulnerability; Last-checkpoint reporting exposes robust overfitting that Best hides.
- **Assuming AT cleans poisoned training data.** A39318: standard AT (PGD-AT/SAM/Smoothing/TRADES) is
  "not entirely effective" against deferred (Hessian-singularizing) poisoning; AT is not a poisoning
  defense — provenance is (§15, A39809/A40295/A40855 for backdoors).
- **Adversarially training on a shared/monoculture backbone and assuming isolation.** A41144/A42439:
  perturbations crafted on a shared CLIP encoder transfer to black-box commercial models — AT on the
  shared backbone is a *systemic* rather than isolated control (§6).
- **Presenting inference-time "adversarial reasoning" as adversarial training.** A41122 (ASE) is an
  inference-time CoT procedure with no fine-tuning; it does not harden weights. Do not conflate the two;
  its single-run, no-CI evaluation and weaker small-model regime are its own caveats.

## Verification strategy

Every scheme verifies with a **deterministic threshold on robust accuracy under a fixed attack suite**,
on a held-out set, with the clean-accuracy cost reported at the same operating point:

- **A39603 (CLIP):** robust accuracy under PGD/CW/**AutoAttack**/BIM at multiple radii **including
  unseen larger ε** (2,4,8/255 vs training 1/255), across 14 datasets, plus clean zero-shot accuracy and
  semantic-preservation checks. Require the model to hold robustness at *unseen* strength.
- **A39954 (classifier):** robust accuracy under FGSM/BIM/PGD-10/50/C&W/APGD/**AutoAttack**; **AutoAttack
  RA is the most reliable indicator**; report **Best and Last** checkpoints.
- **A38392 (metric/ReID):** white-box metric attacks (FNA/SMA/IFGSM) at ε ∈ {8,10}/255, plus
  **cross-domain** transfer (Market↔Duke) for unseen identities, plus **per-identity robustness
  variance** — average accuracy alone hides biased robustness.
- **A40054 (multimodal):** per-modality single-modality probing to show heterogeneity, then robust
  accuracy gains across datasets under fast-AT + AutoAttack.
- **A38416 (black-box):** report **both** transfer *and* query attack results — optimizing/evaluating
  one alone can mask a regression in the other.
- **A38949 (controller):** evaluate under a **learned, targeted** adversary (not just DR), and over
  **long horizons** (failures accumulated over ~65 s before a fall) — short episodes miss drift.

Cross-cutting requirements *(reviewer synthesis, §15–§16)*: verify robustness on the **deployed
artifact** (A38392); include a **strong ensemble (AutoAttack)** and **unseen radii** (A39603); report
the **clean-accuracy delta** at the operating point (A38416/A39603/A38392); and — because none of these
is adaptive-robust — treat every threshold as scoped to the tested, non-adaptive attack set.

## Metrics and thresholds

All values **author-reported**, on the paper's own datasets, **non-adaptive to the specific defense**
unless noted, not independently verified; several tables are flagged truncated.

- **Robust accuracy (RA) under a fixed suite** — the primary metric; want RA high, clean-accuracy cost
  bounded. A39954 (CIFAR-10, Best): Clean 83.07, PGD-10 57.37, C&W 51.54, **AutoAttack 48.58** — a
  **marginal ~0.25–0.5 point** gain over the strongest baselines (TDAT 48.33, FGSM-LAW 48.12); no
  variance/CIs reported. Read this as a caution: AT deltas can be within noise.
- **Robustness improvement (relative)** — A40054: {**12.73%, 22.21%, 11.19%**} robust-accuracy gain on
  CMU-MOSEI / UR-FUNNY / AV-MNIST integrated with fast-AT (absolute/AutoAttack tables truncated).
- **Metric-attack robustness** — A38392 (ResNet50/Market, FNA 8/255, paired ReID metrics): Ours
  **31.99/55.17** vs Adv-train 8.57/18.14, DAS 12.70/24.85; input-purification baselines **near 0%**;
  clean **68.50/88.21**. Absolute robustness stays **modest under strong attack** — improved, not solved.
- **Transfer vs query trade-off (proven)** — A38416: **up to +64%** transfer-robustness by *decreasing*
  LR; **up to +28%** query-robustness by *increasing* LR — **mutually exclusive** (per-cell robust-acc
  tables truncated). Best-case relative gains; clean-accuracy cost of the extremes not summarized.
- **Learned-adversary controller** — A38949: DR-trained policy 94.4% (DR) → **0%** (learned selective
  attack); SAP-trained 97.4% (DR) / 95.7% (SAP); real-robot **~+40%** terrain-traversal success,
  **~32%** trajectory-tracking-error reduction; SAP attack ratio rises with difficulty (Flat 13.6% →
  Dance 30.2%). Single platform.
- **Motivation / diagnostic signals** — A39603: margin↔semantic-similarity Pearson r = **−0.685**
  (ρ = −0.651, p ≪ 0.001) — logit margin is a measurable adversarial-drift signal. A41080 (adjacent):
  attention-head-similarity separates clean/backdoor (BadNets 0.9921 vs 0.9149) — a runtime signal, not
  an AT metric.
- **Poisoning caveat** — A39318: standard AT variants "not entirely effective" vs deferred poisoning;
  curvature-minimizing training scores best on their robustness metrics but at **ACC 0.71 vs clean 0.81**
  — a concrete clean-accuracy cost.
- **Inference-time (not AT, scope bound)** — A41122 (ASE): outright-rejection **≤4%**, adversarial-Q&A
  **92–99%**, bias **4–10× lower** — single-run, no CIs (API cost), adaptive eval qualitative only.

**No threshold here is "safe."** Each is scoped to the tested, non-adaptive attacks; AutoAttack
(A39603/A39954/A40054) and the learned adversary (A38949) are the strongest bars, and none covers a
defense-aware adversary (§9.1, §12).

## Test cases

At minimum, exercise the attack suite each paper demonstrates, plus clean-accuracy regression, unseen
strength, deployment-artifact, and false-robustness checks:

1. **White-box gradient suite:** FGSM, BIM, PGD-10/50, C&W, APGD, **AutoAttack** on the deployed model —
   verify RA exceeds the pre-registered threshold and record Best *and* Last checkpoints (A39954).
2. **Unseen-strength / unseen-attack:** evaluate at perturbation radii **larger than training**
   (A39603, ε 2/4/8/255 vs 1/255) and with attacks not used in training — verify robustness does not
   collapse out-of-training-distribution.
3. **Black-box transfer + query jointly:** surrogate-transfer *and* score/decision query attacks
   (SquareAttack, HopSkipJump) — verify a gain on one did not regress the other (A38416).
4. **Metric / open-set attacks (identity models):** FNA/SMA/IFGSM at multiple budgets, **cross-domain**
   transfer to unseen identities, and **per-identity robustness variance** — verify no long-tail of
   under-protected identities (A38392).
5. **Per-modality vulnerability probe (multimodal):** single-modality attacks to confirm the weakest
   modality is hardened, not just the average (A40054).
6. **Learned / targeted adversary (controllers):** evaluate under a budget-constrained *learned* attack
   (not only domain randomization) and over **long horizons** — a DR-only test can hide a 0% collapse
   (A38949 Table 1); watch cumulative tracking-error drift.
7. **Deployment-artifact check:** verify robustness on the component that actually ships (encoder, not a
   training-only head) — A38392.
8. **Clean-accuracy / utility regression:** measure the clean-accuracy delta at the robust operating
   point (A38416/A39603/A38392) and confirm it is within the utility budget.
9. **Convergence / robust-overfitting check:** compare Best vs Last checkpoint RA and monitor
   training-loss oscillation (A39954).
10. **Poisoned-data control:** confirm training data provenance; run a deferred-poisoning probe
    (A39318) — AT does not clean poisoned data, so this must be caught upstream.

## Adaptive adversarial tests

This is the corpus's single biggest gap (§9.1, §12) and where you must go **beyond** every headline
number — mark all of these **"requires production validation"**:

- **Defense-aware smoothness re-tuning (A38416).** An attacker who knows the tuned smoothness re-tunes
  the surrogate or shifts query budget accordingly — the reported +64%/+28% gains may not hold. Not
  evaluated.
- **Regularizer-aware attacks (A37396, A39603, A40054).** Craft perturbations that jointly evade the
  attribution-consistency loss (A37396), the ASAM/SC-MHE margin (A39603), or the vulnerability-aware
  gradient-norm regularizer (A40054). None of these papers evaluates an attacker adapted to its own
  mechanism.
- **Cache/matching-aware attacks (A39954).** Exploit the deterministic feature-cache/sample-matching
  (updated only every K steps) to evade the convergence fix. Not evaluated.
- **Component-aware metric attacks (A38392).** An attacker aware of FNES / self-meta / the clean-vs-adv
  discriminator; robustness to a defense-aware attacker is unestablished.
- **Out-of-bound / interaction perturbations (A38949).** Perturbations larger than the trained (ε_s, ε_a)
  budget, different noise models, physical spoofing, and contact/dynamics disturbances (author-stated
  out of scope). The 0%/40%/32% figures are scoped to the platform and trained bounds.
- **Deferred / Hessian-singularizing poisoning (A39318).** Poison the training data so AT trains a
  fragile model that passes clean/validation checks — an adaptive attack *on the training pipeline
  itself*.
- **Monoculture transfer (A41144, A42439).** Craft on a shared CLIP-family backbone and transfer to the
  hardened model — AT on a shared backbone is a systemic surface, not an isolated one.

## Telemetry requirements

For the autonomy-trace console *(reviewer synthesis grounded in §15–§16 runtime-telemetry candidates)*:

- **Robustness SLA / operating point.** Log the last-verified robust accuracy per attack, the clean-
  accuracy delta, and the pinned operating point (A38416/A39603) so a regression (from retraining,
  fine-tuning, or drift) is detectable.
- **Runtime margin / drift signals.** Per-request logit **margin** (A39603 — margin correlates with
  semantic similarity and shifts under perturbation), **attribution-map divergence** from expected
  (A37396 diagnostic), and **per-modality gradient-norm / feature-magnitude** disproportion (A40054
  vulnerability indicator) — these are the observable "an input may be perturbed" signals.
- **Query-boundary telemetry (the live black-box detection surface).** Query volume/rate per account and
  **boundary-search / binary-search / random-search probing patterns** (A38416 monitoring note; A38127) —
  AT only *shifts* query-attack success, so the query boundary must be watched independently.
- **Controller health drift.** For learned policies, cumulative tracking-error / per-joint drift and
  stability metrics over long horizons, plus flags for known high-risk regimes the adversary targeted
  (terrain transitions, high-dynamic phases) — A38949 shows drift precedes a fall by tens of seconds.
- **Runtime-gate decisions.** Every deny/degrade/escalate with the corroboration inputs that drove it,
  for audit.
- **Training-data provenance and checkpoint lineage.** Hashes of training data and the robust checkpoint,
  so a poisoning-induced fragility (A39318) or a robustness regression is traceable to a source and a
  clean checkpoint is restorable.

## Failure handling

- **Fail-closed at the runtime gate** *(reviewer synthesis, §15):* on low confidence-plus-consistency,
  cross-source disagreement, or a margin/attribution-drift trip, **deny / degrade / escalate rather than
  act** — the deterministic, least-privilege default. AT hardens the model; the gate contains what AT
  missed.
- **Treat a hardened-model output as a lower-risk signal, never sufficient evidence** for a consequential
  action (A38392 deployment note: do not treat a ReID match/non-match as high-assurance identity without
  corroboration). Every defense here reports residual robust-accuracy loss.
- **Robustness is conditional and can regress.** A38416's gains are relative and can invert under an
  adaptive attacker; A39954's Last checkpoint can differ from Best (robust overfitting). A retrain,
  fine-tune, or data-distribution shift can silently regress the operating point — the robustness SLA
  telemetry must alarm on it.
- **Never single-signal.** Because every AT number is scoped to a non-adaptive threat model, a failed or
  ambiguous robustness check degrades to corroborating evidence (query telemetry, cross-sensor votes,
  provenance), not a definitive verdict (§15 defense-in-depth).
- **The learned adversary must never leak into production.** If a deployment build is found to include
  the training-time SAP/attack module (A38949), treat it as a live incident — it is an attack tool with
  privileged model access.

## Rollback and containment

- **Roll back to a pinned robust checkpoint.** Version training data, hyperparameters, and the robust
  checkpoint (A38416 treats config as the lever; §16 evidence-logging/rollback). On a demonstrated break
  or a robustness-SLA regression, revert to the last checkpoint that passed the verification suite.
- **Contain at the runtime gate and query boundary.** Tighten the fail-closed gate (raise the
  corroboration requirement, degrade to a more conservative policy) and throttle/block anomalous query
  trajectories (A38416/A38127) while re-hardening.
- **Re-harden with the adaptive attack that broke you.** Because AT is empirical, a break becomes a new
  training signal: add the successful attack to the inner-max suite and retrain (the A38949/A39603
  posture of training against the strongest available adversary), then re-verify Best *and* Last.
- **Accept the irreversibility of a successful evasion.** AT does not undo an action already taken on a
  misclassified input — containment limits *future* exposure and preserves the trace for forensics; it
  does not reverse the consequence. This is why the fail-closed action gate, not AT, is the last line.
- **Quarantine poisoned training data.** If fragility traces to poisoned data (A39318), remove the source
  from the provenance-attested set and retrain — AT alone will not clean it.

## Known bypasses

From Adversarial-ML-Attacks §10–§12 (all author-reported; against the AT paradigm or specific schemes,
under each paper's own evaluation):

- **The proven smoothness dichotomy (A38416).** Whatever you tune for, the opposite black-box family gets
  *easier*: decreasing LR raises transfer-robustness but *lowers* query-robustness, and vice-versa — a
  bypass by construction (§10). There is no single smoothness that closes both.
- **Domain-randomization / uniform-AT collapse (A38949).** A learned selective attack drove a DR-trained
  policy from 94.4% to **0%** — randomization-hardened models are bypassable by targeted, budget-aware
  perturbation.
- **Standard AT vs deferred poisoning (A39318).** PGD-AT, SAM, Smoothing, and TRADES are reported "not
  entirely effective" against a model pre-poisoned to have singular input-Hessian — AT does not recover
  robustness a poisoner removed.
- **Monoculture transfer (A41144, A42439).** Perturbations crafted on a shared CLIP-family backbone
  transfer to black-box commercial/reasoning models (A42439: CLIP-ensemble surrogate → 12 commercial
  MLLMs; A41144: one image, avg 59.58% image ASR) — AT on the shared backbone does not isolate it.
- **Marginal-gain / robust-overfitting bypass (A39954).** AutoAttack RA improvements are within ~0.25–0.5
  point of baselines with no variance reported, and Last-checkpoint robustness can differ from Best — the
  "gain" may not survive an honest operating point.
- **Adaptive-attack gap (whole pattern).** No paper here evaluates an attacker adapted to its specific
  defense mechanism (§9.1, §12). Every headline number is therefore an *upper bound* on real robustness;
  a defense-aware adversary is an open bypass for all of them.

**Calibrated takeaway (§9.1, §12):** the demonstrated bypasses are partly against the AT paradigm itself
(the dichotomy, DR collapse, deferred poisoning) and partly reflect the untested adaptive-attack surface;
AT's adaptive and defense-aware robustness **requires production validation** and is currently
unestablished.

## Residual risks

- **Adaptive / defense-aware robustness is unestablished** — the largest residual risk; every number is
  non-adaptive to the specific mechanism (§9.1, §12).
- **The robustness–utility trade-off is real and sometimes proven** (A38416 dichotomy; A39318 ACC
  0.71→0.81 clean cost; A38392 modest absolute robustness; A38121-class ~15% utility drops for adjacent
  robustness interventions, §10). A shippable operating point must disclose the utility cost, not just the
  ASR-reduction number.
- **Scope confinement to evasion of ML components.** AT does nothing for backdoors/poisoning (A39809,
  A40295, A40855, A39318), prompt/tool injection (A40895), memory poisoning, or reasoning-DoS (A40833) —
  those residual risks are entirely uncovered by this pattern.
- **Bounded threat model.** Robustness is confined to the trained perturbation model and strength
  (A38949 out-of-bound / contact disturbances; A39603 unseen radii are a *claim to validate*).
- **Deployment-artifact mismatch** (A38392): robustness can live on a discarded head; verify on what
  ships.
- **Single-backbone / single-dataset concentration** across nearly the whole pattern (A38416 CIFAR-10/
  ImageNet CNNs; A39603 CLIP-B/32 only; A39954 ResNet-18; A40054 single HighMMT; A38392 two datasets/CNN
  only; A38949 single robot) — generalization of every headline number is unestablished (§12).
- **Empirical, not certified** — none of these AT methods offers certified robustness; the corpus's only
  certified defenses (A37716 CertMask patch, A37117 smoothing) are *not* general adversarial training and
  are bounded to narrow threat models (§5, §17).
- **Monoculture systemic risk** (A41144, A42439) when hardening a shared backbone.

## Relevant research (stable paper ids from the syntheses/cards)

Core (training-time adversarial / robust training):

- **A38416** — Tuning for Two Adversaries: hyperparameter-induced robustness as an attack-agnostic lever;
  *proves* the transfer-vs-query smoothness dichotomy (up to +64% / +28%, mutually exclusive); NSGA-II
  joint optimization; released code. *The no-free-lunch anchor: AT shifts, does not close, the boundary.*
- **A38949** — SA2RT: selective, budget-constrained, **non-zero-sum** adversarial training for a real
  humanoid controller with a **learned** in-loop adversary removed at deployment. *Placement over volume;
  DR is insufficient (94.4%→0% under a learned attack); the corpus's nearest adaptive-adversary AT.*
- **A39954** — AT-Field: game-theoretic sample re-grouping to restore AT convergence; marginal AutoAttack
  gains, no variance, no code. *AT convergence is security-relevant; report Best AND Last.*
- **A38392** — DDDefense: metric-aware bi-adversarial self-meta training for person-ReID / open-set
  metric learning; released code. *Harden the deployed encoder, not the discarded head; classification
  defenses do not transfer; data imbalance is a robustness lever.*
- **A40054** — VARMAT: vulnerability-aware multimodal AT; released code. *The weakest modality bounds
  system robustness; regularize gradient norm only.*
- **A37396** — CBA-FAPT: few-shot adversarial *prompt* tuning with cross-modal attribution-consistency.
  *Regularize the internal decision basis, not just outputs; parameter-efficient.*
- **A39603** — TIMA: CLIP zero-shot AT (ASAM + SC-MHE) that **contests** the robustness-generalization
  trade-off; AutoAttack + unseen radii; code in supplement. *Evidence the trade-off can be jointly
  improved by preserving pretrained geometry.*
- **A39085** — EDA-GCL: edge self-adversarial augmentation for unsupervised graph contrastive learning;
  low-cost O(Md) internal min-max; external Metattack/random-noise robustness study; released code.

Cautionary / red-team anchors:

- **A39318** — Deferred Poisoning (DPA): standard AT (PGD-AT/SAM/Smoothing/TRADES) "not entirely
  effective"; curvature-minimizing training helps at a clean-accuracy cost (0.71 vs 0.81). *AT is not a
  poisoning defense; provenance is.*
- **A41144 (MFA) / A42439 (PhysPatch)** — shared-backbone monoculture transfer to black-box commercial
  models. *AT on a shared encoder is systemic, not isolated.*
- **A39809 / A40295 / A40855 / A39935 / A39480** — backdoors survive/are reinforced by retraining and
  preserve clean accuracy. *AT does not remove implanted behavior — the out-of-scope boundary.*

Scope-bounding (NOT adversarial training — do not conflate):

- **A41122 (ASE)** — inference-time CoT "adversarial scenario extrapolation" for LLMs; no fine-tuning;
  single-run, no CIs. *The nearest LLM-side artifact, included to mark the scope boundary: the corpus has
  no evidence for weight-level adversarial training against LLM jailbreaks.*

Adjacent robustness/geometry context: **A38121** (SRD input masking, ~15% CIDEr utility cost — an
adjacent robustness intervention, not AT); **A37117** (capability-gated + certified smoothing, adjacent
certified defense); **A37716** (CertMask certified patch, adjacent). *(reviewer synthesis: certified
defenses are a separate, narrower class than general AT.)*

## Evidence strength

- **A38416 — Moderate (with a proven core).** Theory (Proposition 1 + curvature bound) plus extensive
  CIFAR-10/ImageNet experiments across three deployment scenarios and two data distributions, released
  code; the smoothness dichotomy is a genuine proven result. Tempered by non-adaptive standard attacks,
  vision-only scope, best-case "up to X%" reporting, and truncated per-cell tables.
- **A38949 — Moderate.** Consistent multi-metric simulation plus real-robot demonstrations, clear
  ablations (perturbation level, λ, task-wise attack ratio), and a **learned** in-loop adversary — the
  strongest adversary posture in the pattern. Tempered by single platform, no external/adaptive
  deployment-time adversary, an inherited (not independently proven) monotonicity guarantee, and missing
  camera-ready hyperparameters.
- **A39603 — Moderate.** Broad (14 datasets, four attacks incl. AutoAttack, unseen radii, SOTA
  baselines, motivating correlation analysis) and *contests* the trade-off; tempered by empirical
  (non-certified) robustness, single backbone/source, no mechanism-adaptive attack, truncated tables.
- **A40054 — Moderate.** Clear weakest-modality insight, lightweight attack-agnostic probe, multi-dataset
  relative gains, released code; tempered by single backbone, feature-space-only threat model,
  relative-gain reporting with truncated absolute/AutoAttack tables, no adaptive attack.
- **A38392 — Moderate.** Well-motivated ReID-specific defense with a validated core hypothesis
  (robustness-on-classifier), broad comparison, ablations, cross-domain tests, released code; tempered by
  two-dataset/CNN-only scope, no adaptive attacker, modest absolute robustness under strong attack.
- **A37396 — Moderate.** Conventional, credible PGD threat model, breadth (11 datasets, three
  generalization settings), comparison to prior SOTA; tempered by no adaptive-attack evaluation, heuristic
  attribution proxies, no stated artifact release.
- **A39954 — Moderate (marginal effect).** Sound theory plus 9 baselines and AutoAttack, but absolute
  gains are ~0.25–0.5 point with no variance, ResNet-18 only, no code, no mechanism-adaptive attack.
- **A39318 — Moderate (red team / cautionary).** Concrete demonstration that standard AT is insufficient
  against deferred poisoning, with a curvature-minimizing counter at a stated clean-accuracy cost; CIFAR-
  scale, surrogate-transfer black-box.
- **A41122 — Preliminary (out-of-scope for AT).** Broad benchmark comparison but single-run, no CIs,
  qualitative adaptive analysis, weaker on small models — and it is inference-time, not training.

Cross-cutting: **all numbers are author-reported and non-adaptive to the specific defense; the strongest
bars are AutoAttack (A39603/A39954/A40054) and the learned adversary (A38949), and none establishes
adaptive/defense-aware robustness (§9.1, §12).** Reviewer-synthesis items in this pattern (the runtime
fail-closed gate, cross-source corroboration, layering strategy, telemetry) are **engineering practice,
not measured defense efficacy**, and require production validation.

## When NOT to use this pattern

- **When the threat is not inference-time evasion of an ML component.** For prompt/tool injection
  (A40895), backdoors/data-poisoning (A39809, A40295, A40855, A39318), memory poisoning, or reasoning-DoS
  (A40833), adversarial training is the wrong control — use provenance/attestation, tool-layer intent
  binding, or availability SLAs. AT does **not** remove an implanted backdoor.
- **As a gate or a guarantee.** AT reduces residual risk under the tested attacks; A38416 proves you
  cannot close both black-box families. Never let a hardened model authorize a consequential action on
  its own output — pair it with a fail-closed runtime gate.
- **When you cannot afford the utility cost.** The robustness–accuracy trade-off is real and sometimes
  proven (A38416; A39318 ACC 0.71 vs 0.81). If the clean-accuracy budget is tight and the operating point
  is not disclosable, do not ship AT as if it were free.
- **When training data is not provenance-attested.** AT assumes a trustworthy clean-loss term; a deferred
  poisoner defeats it (A39318). Establish data provenance first.
- **When the deployed artifact differs from the trained one.** For metric/retrieval systems, verify on the
  encoder, not a training-only head (A38392); if you cannot, AT's robustness may not deploy.
- **When you need certified robustness.** These are all empirical methods; use the narrower certified
  defenses (A37716 patch, A37117 smoothing) within their bounded threat models instead — and do not
  present empirical AT as certified.
- **For LLM jailbreak resistance via weight-level training.** The corpus provides **no** evidence for
  this; A41122 (ASE) is inference-time reasoning, not adversarial training. Do not claim AT hardens an LLM
  against jailbreaks.
- **On a shared/monoculture backbone assumed to be isolated.** AT on a shared CLIP-family encoder is a
  systemic control (perturbations transfer — A41144, A42439); if isolation is the requirement, add
  capability isolation / independent-backbone diversity, not AT alone.
- **For cross-modal or cross-task reuse without revalidation.** Robustness does not compose across
  modalities (A37388, A37396, A37436, A37442) and methods are siloed across vision/metric/multimodal/
  graph/RL (§12); re-establish the threat model and metrics before reusing an AT recipe on a new
  component.
