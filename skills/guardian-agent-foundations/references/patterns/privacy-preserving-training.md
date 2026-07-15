# Pattern: Privacy-Preserving Training

> **Scope of evidence.** This pattern is grounded in the AAAI-26 corpus synthesis `Privacy-Protection.md`
> and its underlying research cards, cross-referenced with `architecture-patterns.md` (P5 trajectory trace,
> P6 credential/egress broker), `agent-identity.md` (artifact-as-secret / egress control), and the sibling
> patterns `least-privilege-credentials.md` and `context-and-memory-isolation.md`. Load-bearing corpus papers:
> **A39510** (tight hidden-state DP-SGD analysis — the "accounted DP done right" anchor), **A39051** (DP that
> *guarantees* original-constraint feasibility — DP coexisting with hard safety invariants), **A37854** (DP
> dataset distillation exploiting post-processing immunity), **A38016** (DP synthetic-image generation +
> noise-tolerance pre-training), **A40117** (subspace-restricted DP fine-tuning for LLMs), **A40852**
> (crypto-assisted two-server DP training), **A40132** (secret-sharing MPC training), **A40889** (verifiable,
> robust FL aggregation), **A40045** (federated LLM fine-tune + auditable targeted unlearning), **A37743** and
> **A39333** (the load-bearing attack evidence: noise-perturbed / DP gradients are reconstructable), **A39212**
> (decompose-then-protect for split-inference reconstruction), **A41120 / A40047 / A39373** (the
> deletion-verification / unlearning-residue evidence), and **A39307 / A39338** (privacy-by-data-locality
> asserted but *unevaluated* — the anti-pattern). Paper ids (e.g. `A39510`) are the stable corpus ids from the
> synthesis source map (Privacy-Protection §20).
>
> **Evidence integrity (non-negotiable).** Every numeric value below is **author-reported and not independently
> verified**; several cards flag truncated/OCR-approximate result tables, recorded here as author-stated. Where a
> card was silent the text says "not stated in paper". Formal DP/MPC guarantees are cited as **guarantees on the
> specific released artifact under the stated trust model**, not as executed-attack robustness — the synthesis'
> single most repeated caveat is that **formal-guarantee-without-an-executed-attack is pervasive** and **almost
> no defense here faces an adaptive, defense-aware attacker** (Privacy-Protection §11, §12). Calibrated language
> only: "reduced reconstruction/membership success against the tested, non-adaptive attacks", "requires
> production validation", never "secure / proven-safe / unbreakable / eliminates". Reviewer-synthesis inferences
> (engineering practice added during review) are labeled *(reviewer synthesis)* and are design guidance, not a
> paper-measured result.

---

## Problem addressed

A model that trains or fine-tunes on sensitive data becomes a **leakage vector for that data** — through the
gradients exchanged during training, the intermediate representations it transmits, the checkpoints it
publishes, and the finished weights it serves. For a Guardian / agent stack this is the control that protects
**`training_data` / `user_data` confidentiality across the model lifecycle**: any component that fine-tunes on
user conversations, builds a personalization model, distills a private corpus, learns on-device, or
collaboratively trains across silos.

The corpus's organizing conclusion, independently converged from both review chunks, is blunt:
**approximate/heuristic privacy mechanisms leave an adversarially recoverable residue, and "by-construction"
evidence understates it** (Privacy-Protection §6, §9). Two training-time forms dominate:

- **Heuristic additive noise on gradients is invertible.** Two methodologically independent attack papers
  reconstruct client images from noise-perturbed / DP-protected gradients: `A37743` (GGSS-R, a frozen diffusion
  prior steering DDIM sampling, requiring *no* distributional alignment with the target) and `A39333` (Venom,
  an **analytic, noise-prior-free** reconstruction — author-reported ImageNet LPIPS 0.340 vs 0.632 and ASR 45%
  vs 2% against the prior SOTA at ε=10, δ=10⁻⁵). Convergent implication: **plain additive gradient noise is not
  a privacy boundary.**
- **"We only share gradients/digests/submodels" is data-minimization, not a privacy guarantee.** `A39307`
  (FedAI) and `A39338` (FedLAGC) assert privacy from architecture with **no threat model, no attack, and no
  accounting** — and gradient sharing is precisely the documented leakage vector above. Their own cards grade
  the privacy dimension as *Preliminary / Insufficient*.

The load-bearing thesis is therefore: **model-derived training artifacts — gradients, submodels, smashed
representations, distilled sets, checkpoints — are first-class secrets, not opaque tokens** (Privacy-Protection
§6). The defense is to prefer **accounted DP and/or secure computation over heuristic noise**, to **log the
privacy dial as configuration-of-record**, to **put egress control on every transmitted artifact**, and to
**verify deletion at the representation level** rather than trusting behavioral parity. This pattern governs the
*training/telemetry path*; it is the data-confidentiality complement to the runtime action-side controls
(`policy-permission-gates`, `least-privilege-credentials`).

## Applicable assets and attack surfaces

- **Per-client / per-step gradients on the training path.** The primary leak surface. Under a static additive-
  noise defense, `A37743` reconstructs the source image with a generic diffusion prior; `A39333` reconstructs
  it analytically from **DP-protected** gradients intercepted **before aggregation**, exploiting the final
  fully-connected layer's gradient identity (∇W_j = δ_j·x). Both cards state the attack is **out of scope for
  cryptographic secure aggregation** — i.e. secure aggregation is the gap they leave open.
- **Intermediate / "smashed" representations in split or offloaded training-and-inference.** `A39212`
  (InfoDecom) treats data-reconstruction from smashed data as a first-class threat, worst when the client-side
  "bottom" model is shallow (few nonlinearities filter little). The reconstructable asset is the whole input,
  not one attribute.
- **Published intermediate checkpoints.** `A39510`'s tighter hidden-state RDP bound holds **only if intermediate
  iterates are not released**; checkpoint publishing, federated round exposure, or early-stopping artifacts void
  it and force fallback to looser composition accounting.
- **Released artifacts derived from private data** — distilled datasets (`A37854`: standard distillation offers
  no formal guarantee and is MIA-vulnerable), DP-synthetic data (`A38016`), and the finished fine-tuned model
  (`A40117`: membership-inference / model-inversion / reconstruction on the served model).
- **Shared submodels, masks, and gradient-drift correction vectors.** `A39338` increases what crosses the FL
  boundary (submodels + accumulated drift) with no privacy analysis; its own card flags these as sensitive
  artifacts needing secure aggregation / DP the paper does not provide.
- **Structural digests / kernel features / prototypes.** `A39307` uploads centrality-weighted random-walk path
  digests and a cross-client attribute-inference operator that is itself a **dual-use inference primitive**; the
  synthesis repeatedly flags un-accounted shared *structure* (graphs, masses, digests) as the un-analyzed leak
  (Privacy-Protection §12, §17).
- **The unlearning / deletion channel (the training-data lifecycle tail).** Post-training removal is part of
  privacy-preserving training: `A40045` emits an auditable unlearning event but uses **proxy forgetting metrics,
  not an executed adversary**; `A41120` (PrivUB) shows deployment operations (fine-tuning more than
  quantization) **reactivate** forgotten data; `A39373` shows black-box forget metrics are gameable while the
  encoder retains the forget set.
- **Privatized outputs that feed a system with hard invariants.** `A39051`: naïve symmetric DP noise can push a
  privatized solution **outside the original feasible region** — a safety-constraint violation, not just a
  utility loss.

## Threat model

Designed for **training-time and release-time confidentiality adversaries** who observe or intercept
training artifacts, or who probe/fine-tune the released model. Grounded threat classes:

- **Honest-but-curious / semi-honest counterparty (the single most common model in-corpus).** A server, cloud
  host, or compute peer that follows the protocol but tries to infer private inputs: honest-but-curious FL
  server or eavesdropper reading per-client gradients (`A37743`, `A39333`), honest-but-curious split-inference
  server running DRAs with surrogate knowledge (`A39212`), single semi-honest server in a non-colluding pair
  (`A40852`), honest-majority passive coalition t < n/2 (`A40132`). **Malicious/active/colluding adversaries are
  almost universally out of scope** and several papers state this explicitly (`A40852`, `A40132`, `A40889`).
- **Gradient-interception → training-data reconstruction.** Attacker with model weights + a leaked gradient
  reconstructs the source example (`A37743`, `A39333`). `A39333`'s own card notes it needs the architecture and
  the exposed last-linear-layer structure, and targets **pre-aggregation** updates.
- **Membership / record-level inference on the released model or distilled/synthetic artifact** (`A39510`,
  `A37854`, `A38016`, `A40117` — the risk their DP guarantee is meant to bound; MIA used as the empirical
  probe).
- **Post-deletion / unlearning adversary** — probes or fine-tunes a model *after* a forgetting operation
  (`A41120`, `A40047`, `A39373`); a benign single black-box query can detect the former-membership imprint
  (`A40047`).
- **Byzantine / poisoning data-providers on the aggregation path** — model-poisoning (IPM, ALIE) and norm/
  scaling attacks that defeat cosine-similarity robust aggregation (`A40889`, tested to 80% malicious data-
  providers).
- **Constraint-violation via privatization** — a privatized output rendered infeasible w.r.t. a safety
  constraint by symmetric noise (`A39051`).

**Adaptivity boundary (critical).** Every corpus *defense* relevant here argues privacy from a formal
(ε,δ)/µ-GDP/RDP/FSInfo guarantee or a semi-honest crypto proof and runs **no executed attack** against its own
pipeline (`A39510`, `A39051`, `A37854`, `A38016`, `A40117`, `A40852`, `A40132`, `A40838`) — Privacy-Protection
§12 lists this as the pervasive gap. Every corpus *attack* is evaluated against a **static, non-adaptive**
defense (`A37743`, `A39333` both note the defender does not adapt to the diffusion-denoising attack). Treat all
efficacy numbers as a **non-adaptive best case**; an adaptive, defense-aware red-team is a launch gate.

## Control mechanism

Protect the training-data confidentiality of every artifact that crosses a trust boundary, proving the
protection with accounting rather than asserting it by construction:

```
train(private_data, ε_budget, trust_model) →
  { accounted-DP model | secure-aggregate/MPC-trained model | DENY-to-release }
     └─ every transmitted artifact (gradient/submodel/smashed-rep/distilled-set) is egress-controlled;
        the privacy dial (ε/δ/µ/D/FSInfo/f) is logged as config-of-record;
        release is fail-closed on budget exhaustion, accounting error, or a failed acceptance test
```

- **Prefer accounted DP over heuristic noise; the accounting is the load-bearing property.** Heuristic additive
  gradient noise is invertible (`A37743`, `A39333`); the defense-side papers agree in spirit — the *accounted*
  guarantee, not the perturbation, is what carries (`A37854`, `A39510`). Use RDP/GDP/f-DP composition
  (`A39510`, `A37854`) and treat the ε-budget as a governed, exhaustible resource.
- **Release only the final model when claiming the tight hidden-state bound.** `A39510`'s improved RDP holds for
  smooth non-convex losses **only if intermediate iterates are withheld**; publishing checkpoints reverts you to
  looser composition accounting *(A39510, operational caveat)*.
- **Restrict noise/computation to task-relevant structure *before* adding it**, to escape the noise∝dimension
  curse and keep formal DP affordable: subspace-restricted DP fine-tuning (`A40117`, noise only in the top-k
  task subspace, remainder is post-processing), and decompose-then-protect (`A39212`, strip redundant/task-
  irrelevant information first, then calibrate noise to a target FSInfo level).
- **Exploit post-processing immunity as a budget lever.** Route as much computation as possible through already-
  private (DP-generated) data so it costs **zero additional budget** (`A37854`; `A39051`: "solving the private
  LP does not weaken privacy").
- **Use bounded / one-sided / direction-controlled noise where an output feeds a hard invariant.** `A39051`'s
  matrix-variate **truncated-Laplace one-sided tightening** *guarantees* the private solution stays inside the
  original feasible region (author-reported zero constraint violation vs up to 51% for a symmetric-noise
  baseline at ε=0.25) — the canonical "DP must coexist with a safety constraint" mechanism.
- **Never send raw per-client gradients over an untrusted channel; use secure aggregation / secure computation.**
  Both gradient-inversion cards leave secure aggregation explicitly out of scope — it is the missing control
  (`A37743`, `A39333`). Where mutually-distrusting parties train together, secret-sharing MPC (`A40132`,
  semi-honest honest-majority) or crypto-assisted two-server DP (`A40852`, non-colluding) removes the trusted-
  aggregator assumption — **contingent on the trust model holding**.
- **Make aggregation robust *and verifiable*, and normalize norms before trust scoring.** `A40889`: encrypted
  utility scoring with client-side decryption (the aggregator never sees plaintext scores), commitment-based
  verifiable selection, and **gradient-norm normalization before cosine-similarity** trust scoring to close the
  scaling-attack surface that collapses cosine-only defenses.
- **Pre-condition for noise tolerance on public data (free under accounting).** `A38016`: adversarial model
  perturbation on the *public* pre-training set transfers noise tolerance into DP-SGD fine-tuning, recovering
  utility with no privacy-budget cost (author-reported ~20.18% lower FID, ~5.45% higher accuracy at
  ε ∈ {1,5,10}).
- **Verify deletion at the representation level and treat re-training as a reactivation hazard.** Behavioral
  parity is gameable (`A39373`); pair "delete my data" with a residual-information probe or relearning attack,
  emit an auditable unlearning event (`A40045`), and re-audit after any fine-tune (`A41120`).
- **Deterministic, fail-closed release.** Budget exhaustion, an accounting error, a failed acceptance test, an
  un-satisfiable trust assumption (e.g. collusion detected), or an un-accounted shared artifact → **do not
  release the model/artifact** *(reviewer synthesis; consistent with Privacy-Protection §13 "treat budget-
  accounting error or exhaustion as an incident boundary")*.

## Preconditions and trust assumptions

The pattern is only as strong as these hold; each is a documented failure point:

- **A correct, complete privacy accountant.** The (ε,δ)/µ-GDP/RDP guarantee is only as strong as its accounting;
  it must cover **every shared object**, not just the headline artifact — the synthesis names un-accounted
  structural graphs (`A39311`), mass values (`A39582`), and digests (`A39307`) as silent voids
  (Privacy-Protection §12, §17). A budget-accounting error is a privacy incident *(A37854 card)*.
- **The "final-model-only" release assumption actually holds** for the tight hidden-state bound (`A39510`) — no
  intermediate-checkpoint leak.
- **Correct sensitivity bounding (per-sample gradient clipping) and calibrated noise.** The Gaussian mechanism's
  guarantee depends on the clip threshold C and σ being set and enforced (`A39510`, `A37854`, `A40117`).
- **Public pre-training / auxiliary data is genuinely independent of the private set.** `A37854` and `A38016`
  route "free" post-processing steps through public data; if that data is not actually independent, those steps
  are **not** private. `A40117`'s zero-budget subspace transfer assumes the projection captures *general* task
  geometry, not private sample-specific information — a central, not-formally-proven assumption.
- **The trust model of the secure-computation scheme genuinely holds.** MPC guarantees collapse under collusion
  or a dishonest majority (`A40132` t < n/2; `A40852` and `A40889` non-colluding two-party/anytrust) — deploy
  only with independently-operated, vetted parties, and treat any collusion evidence as a confidentiality
  incident.
- **Secure aggregation / egress control on the gradient path**, since plain additive noise is bypassable
  (`A37743`, `A39333`).
- **A representation-level deletion acceptance test exists** — behavioral forget metrics are necessary-but-
  insufficient (`A39373`, `A41120`).
- **Audit-store integrity** for the privacy-config and unlearning-event records *(reviewer synthesis; the cards
  assert an audit requirement but you must supply tamper-evidence)*.

## System architecture

A DP / secure-aggregation boundary on the training-and-telemetry path, with an egress-controlled artifact
channel and an accountant as the release authority (architecture-patterns P5/P6; Privacy-Protection §15):

```
 private data ─► [Clip + calibrate]  per-sample gradient clipping (C); noise σ calibrated to the target ε.
                    │                  Restrict noise to a task subspace / after redundancy removal to keep it
                    │                  affordable (A40117 subspace; A39212 decompose-then-protect). ── error ─► DENY
                    ▼
                 [Accounted DP  OR  Secure computation]
                    │   RDP/GDP/f-DP composition, final-model-only release (A39510, A37854);   OR
                    │   secret-share / secure-aggregate so raw per-client gradients never leave (A40132, A40852,
                    │   A40889 encrypted scoring + norm-normalization + verifiable selection). ── budget-exhaust ─► DENY
                    ▼
                 [Egress control on EVERY transmitted artifact]  gradient/submodel/smashed-rep/digest/distilled
                    │   set treated as a first-class secret; no raw per-client gradient over an untrusted channel
                    │   (A37743, A39333); no un-accounted shared structure (A39307, A39338). ── un-accounted ─► DENY
                    ▼
                 [Release gate]  formal guarantee stated for the SPECIFIC artifact + representation-level
                    │            acceptance test (deletion / residual-info probe) passed (A39373, A41120). ── fail ─► DENY
                    ▼
        ┌── model / distilled set / synthetic data released ──┐
        ▼                                                       ▼
 [Privacy-config of record]                          [Auditable evidence record]
   ε/δ/µ · clip C · noise σ · diameter D · FSInfo ·    per privacy-relevant op: training run, budget consumed,
   fixed-point f · trust model · non-collusion set.    unlearning event (which client / forget set / when),
   Budget-exhaust = incident boundary.                 verifiable-selection commitments (A40045, A40889, P5).
```

- **The accountant + the trust-model check are the release authority** — a model may be *trained*, but whether
  its artifacts may *leave the boundary* is a deterministic decision on budget, accounting completeness, and the
  acceptance test, never on model self-report *(reviewer synthesis; mirrors the fail-closed posture of the
  sibling gate patterns)*.
- **Two axes are independent and both required:** *how private is the artifact* (the DP/crypto mechanism) and
  *may this artifact cross this boundary* (egress control). A perfectly DP-trained model still must not ship raw
  per-client gradients (`A37743`, `A39333`).
- **Confidentiality boundary around intermediate state** for any split/offloaded training — decompose-then-
  protect the smashed representation (`A39212`), do not assume "payload encrypted" suffices.

## Recommended implementation pattern

Deterministic, fail-closed, least-privilege — in priority order:

1. **Prefer accounted DP or secure computation to heuristic noise.** Track ε via RDP/GDP/f-DP composition and
   treat the budget as governed and exhaustible; heuristic additive gradient noise is a documented leak
   (`A37743`, `A39333`; the accounting is load-bearing per `A37854`, `A39510`).
2. **Clip per-sample gradients and calibrate noise to the target ε**; expose C and σ as governed configuration
   (`A39510`, `A37854`, `A40117`).
3. **Release only the final model** when claiming the tight hidden-state bound; do not publish intermediate
   checkpoints (`A39510`).
4. **Restrict noise to task-relevant structure before adding it** — subspace projection (`A40117`) or
   redundancy removal / information decomposition (`A39212`) — to buy formal privacy at deployable utility.
5. **Route computation through already-private data for free** via post-processing immunity (`A37854`; `A39051`).
6. **Use bounded, one-sided noise where an output feeds a hard invariant** so privatization cannot violate a
   safety constraint (`A39051` truncated-Laplace tightening).
7. **Never transmit raw per-client gradients over an untrusted channel**; use secure aggregation / secret-sharing
   MPC / crypto-assisted DP (`A40132`, `A40852`) and **normalize update norms before cosine trust scoring** with
   verifiable, encrypted selection (`A40889`).
8. **Pre-condition for noise tolerance on public data** (adversarial model perturbation), keeping all robustness
   augmentation strictly on public data so it never touches the accountant (`A38016`).
9. **Account for every shared object**, not just the headline artifact — digests, structures, masses, submodels,
   correction vectors (`A39307`, `A39338`, `A39311`, `A39582`).
10. **Verify deletion at the representation level** (residual-information probe or relearning attack), emit an
    auditable unlearning event, and **re-audit after any fine-tune** (`A39373`, `A40047`, `A41120`, `A40045`).
11. **Log the privacy dial as configuration-of-record** — ε/δ/µ, clip C, noise σ, domain diameter D, FSInfo
    level, fixed-point precision f, trust model, and the non-collusion set (Privacy-Protection §13).
12. **Fail closed everywhere** — budget exhaustion, accounting error, failed acceptance test, un-accounted
    artifact, or collusion evidence → do not release *(reviewer synthesis)*.

## Incorrect or fragile implementation patterns

- **Plain additive gradient noise as "the" privacy control.** Reconstructable by a generic diffusion prior
  (`A37743`) and analytically, noise-prior-free, from DP-protected gradients (`A39333`). Additive noise without
  clipping+accounting is **not even a DP mechanism** (`A37743` card).
- **"We only share gradients / digests / submodels, so it's private."** Data-locality asserted with no threat
  model, no attack, no accounting (`A39307` FedAI, `A39338` FedLAGC) — contested as security evidence precisely
  because gradient/digest sharing is the leak (`A37743`, `A39333`). Its own cards grade the privacy dimension
  *Insufficient*.
- **Transmitting raw per-client gradients over an untrusted channel** — recoverable if intercepted before
  aggregation (`A39333`); secure aggregation is the missing control both attack papers name.
- **Publishing intermediate checkpoints while claiming the tight hidden-state DP bound** — voids `A39510`'s
  guarantee; realized privacy reverts to looser composition.
- **Un-accounted shared structure** — sharing prototypes/graphs/masses/digests outside the ε-budget leaves a
  silent leak the headline (ε,δ) does not cover (`A39311`, `A39582`, `A39307`; Privacy-Protection §12).
- **Symmetric DP noise on an output that must satisfy a hard constraint** — can render the private solution
  infeasible; use one-sided tightening instead (`A39051`).
- **Cosine-similarity robust aggregation without norm normalization** — collapses below ~20% accuracy under
  large-factor scaling attacks (`A40889`).
- **Treating a distilled or synthetic dataset as automatically private** — standard distillation has no formal
  guarantee and is MIA-vulnerable; a formal DP mechanism with documented (ε,δ)/µ is required (`A37854`).
- **Certifying deletion on behavioral parity alone** — black-box forget metrics are gameable while the encoder
  retains the forget set (`A39373`: recoverable >82% vs ≤41% for a true retrain); and fine-tuning after
  unlearning reactivates forgotten data (`A41120`).
- **Assuming the public/auxiliary corpus is independent when it is not** — the "free" post-processing steps then
  spend un-accounted privacy (`A37854`, `A38016`, `A40117`).
- **Excessive robustness perturbation** — `A38016` reports AMP magnitude > 0.5 impairs convergence; the lever
  has a usable range.
- **Fail-open on accountant / crypto error** — contradicts the fail-closed posture; release nothing on error
  *(reviewer synthesis)*.

## Verification strategy

- **Adaptive, defense-aware red-team is the launch gate** — the single most consistent corpus gap: every
  relevant defense is formal-guarantee-only or non-adaptive (Privacy-Protection §11, §12). Any robustness claim
  "requires production validation" before reliance.
- **Executed-attack corroboration of every formal-DP/crypto claim.** Pair the (ε,δ) bound with a
  membership-inference *and* a reconstruction attack — `A39510` validates with MIA trend analysis across knobs;
  most others run none. The cautionary example is elsewhere in the corpus (`A42453`, embedding schemes marketed
  "privacy-preserving" that invert under test).
- **Gradient-inversion red-team as a training-path baseline.** Run a generative-prior inversion (`A37743`) and
  an analytic noise-prior-free inversion (`A39333`) against your gradient-protection scheme; report residual
  reconstruction quality (MSE/PSNR/LPIPS) per architecture and per noise level.
- **Architecture-vulnerability audit before deployment.** Estimate `A37743`'s Reconstruction-Vulnerability
  metric RV = max_x ‖∇_x ∇_W F‖_F (via random orthogonal projections) to rank a candidate architecture's
  intrinsic gradient-leakage susceptibility; a rising RV after an architecture change is a leakage-risk signal.
- **Representation-level deletion acceptance test** — a residual-information probe (feature MI / head-retraining
  recoverability, `A39373`) or a relearning attack — is necessary before certifying right-to-be-forgotten;
  behavioral MIA/accuracy parity is necessary-but-insufficient. Re-audit after any fine-tune (`A41120`).
- **Accounting-completeness audit** — confirm every shared object (digests, structures, submodels, correction
  vectors) is inside the ε-budget, not just the headline artifact (`A39307`, `A39338`, `A39311`).
- **Trust-model validation** — verify the non-collusion / honest-majority assumption operationally (independent
  operators) before relying on the MPC/two-server guarantee (`A40132`, `A40852`, `A40889`).
- **Report absolute residuals, not relative reductions** (Privacy-Protection §16).

## Metrics and thresholds

Track these families; **thresholds are operator-defined per deployment and must be validated against an
adaptive set — the corpus provides no validated universal threshold, and formal-guarantee-without-executed-attack
is pervasive (Privacy-Protection §12).**

- **The privacy dial as configuration-of-record** — ε and δ (`A39510`, `A39051`, `A37854`, `A38016`, `A40117`,
  `A40838`), µ-GDP (`A37854`), domain diameter D (`A39510`, swept over {20,60,100}), FSInfo level (`A39212`),
  fixed-point precision f (`A40132`, f ≥ 16 approaches plaintext; f = 13 collapses to ~52–55% vs ~92%). Log the
  chosen operating point per released artifact.
- **Cumulative privacy-budget consumption** across training runs and re-solves; budget exhaustion is an
  **incident boundary** (`A37854`, `A39051`, `A40117`).
- **Reconstruction quality under a constructed inversion** — MSE/PSNR/LPIPS and ASR at a fixed operating point.
  Corpus reference points (author-reported): `A39333` ImageNet LPIPS 0.340 (attack) vs 0.632 (prior SOTA), ASR
  45% vs 2% at ε=10, δ=10⁻⁵; `A37743` best-guidance ablation MSE 7.7215e−5, PSNR 41.1230, LPIPS 2.0519e−7.
- **Membership-inference AUC/accuracy** on the released model / distilled / synthetic artifact as the empirical
  privacy oracle (`A39510` MIA-estimated ε̂ across batch size and diameter; `A37854`, `A38016`, `A40117`).
- **Reconstruction-Vulnerability (RV)** per candidate architecture (`A37743`) — a pre-deployment leakage-risk
  ranking.
- **Deletion residual** — representation-level recoverability of the forget set (`A39373`: >82% recoverable vs
  ≤41% for a true retrain is the gap a gamed metric hides); reactivation after fine-tuning (`A41120`).
- **Robust-aggregation main-task accuracy under attack** — direction (IPM/ALIE) *and* norm/scaling
  manipulations across adversary fractions well beyond 50% (`A40889`: baselines drop <20% under scaling; MartDE
  author-reported >75% under ALIE and at 80% malicious over-scaling).
- **Utility cost of the privacy dial** — accuracy/FID vs ε (`A38016` ~20.18% lower FID / ~5.45% higher accuracy;
  `A37854` +11.6%; `A40045` +27.43% federated vs best local baseline), and constraint-violation rate for
  constrained-optimization outputs (`A39051` zero vs up to 51%).
- **Secure-computation cost** — runtime under the trust model (`A40852` 642.78 s vs 173,960.9 s author-reported;
  `A40132` communication/time by RMFE parameter).

## Test cases

Concrete, corpus-grounded cases the control must be exercised against:

1. **Diffusion-prior gradient inversion under a static additive-noise defense** — confirm the scheme is not
   plain additive noise, and measure residual reconstruction with a generic prior (`A37743`).
2. **Analytic noise-prior-free reconstruction from DP-protected gradients** intercepted **before aggregation** —
   confirm secure aggregation prevents per-client recovery; measure LPIPS/ASR if not (`A39333`).
3. **Data-reconstruction from a shallow split-inference bottom model** — confirm decompose-then-protect raises
   reconstruction MSE at equal utility (`A39212`).
4. **Checkpoint-leak invalidation** — publish an intermediate iterate and confirm the realized guarantee reverts
   to composition accounting (`A39510`).
5. **Un-accounted shared structure** — attempt to ship a digest / prototype / correction vector outside the
   ε-budget (must be blocked or accounted) (`A39307`, `A39338`, `A39311`).
6. **Data-locality-only "privacy" claim** — assert the FedAI/FedLAGC posture and run a gradient-inversion probe
   to demonstrate it is not a guarantee (`A39307`, `A39338`).
7. **Constraint violation via symmetric noise** — feed a privatized output into a hard-constraint system and
   confirm one-sided tightening keeps it feasible (`A39051`).
8. **Scaling / norm poisoning of aggregation** — large-factor scaling attack; confirm norm-normalization + cosine
   holds where cosine-only collapses (`A40889`).
9. **Distilled/synthetic dataset without a formal mechanism** — run MIA on models trained from it; confirm the
   formal DP mechanism is required for a defensible claim (`A37854`).
10. **Gamed deletion metric** — apply a cosmetic output change that satisfies black-box forget metrics; confirm
    the representation-level probe still recovers the forget set (`A39373`).
11. **Reactivation by re-fine-tuning** — fine-tune an unlearned model and confirm re-audit detects restored
    forgotten data (`A41120`, `A40047`).
12. **Collusion / dishonest-majority** — exceed the trust threshold (colluding two servers / > t parties) and
    confirm the MPC guarantee is documented to collapse (`A40852`, `A40132`, `A40889`).

## Adaptive adversarial tests

Beyond static cases — attackers who know the control (the corpus's largest methodological gap; treat these as
launch gates):

- **Adaptive defender-aware inversion** — an attacker who co-designs against the *specific* noise/subspace/
  frequency-removal pipeline, not the fixed additive noise the attack papers assumed (`A37743`, `A39333`,
  `A39212` all evaluated non-adaptive/semi-adaptive defenders).
- **Leakage through un-noised directions** — probe whether the orthogonal complement of `A40117`'s task subspace
  concentrates recoverable private signal (the card flags this as un-tested).
- **Pipeline-aware / LiRA-style calibrated MIA** tuned to the DP-distillation or DP-synthesis mechanism, rather
  than a standard fixed MIA (`A37854`, `A38016` cards recommend this).
- **In-range poisoning that evades the anomaly filter** — craft updates with valid in-range squared-similarity
  scores to slip past `A40889`'s zᵢ>1 threshold.
- **Collusion optimization** — a colluding server pair or > t coalition against the two-server / honest-majority
  schemes (`A40852`, `A40132`, `A40889`); the semi-honest proof gives no guarantee here.
- **Relearning / decoding-aware deletion attacks** — fine-tune-to-restore and alternative-decoding probes
  against an unlearned model (`A41120`, `A40047`; and the corpus's decoding-aware unlearning attacks generally).
- **Auxiliary-data-strengthened analytic inversion** — improve `A39333` with a better auxiliary prior against a
  fixed ε to push ASR above the reported 45%.

## Telemetry requirements

Emit structured, tamper-evident records for every privacy-relevant training operation (architecture-patterns
P5/P10):

- **Privacy-config of record, per released artifact** — ε/δ/µ, clip C, noise σ, domain diameter D, FSInfo
  level, fixed-point f, the trust model, and the non-collusion / honest-majority set (Privacy-Protection §13).
- **Cumulative budget-accounting state** — budget consumed per training run and re-solve; flag exhaustion as an
  incident boundary (`A37854`, `A40117`).
- **Artifact-egress log** — which artifacts (gradients/submodels/smashed reps/digests/distilled sets) crossed
  which boundary, and under which protection; flag any raw per-client gradient over an untrusted channel
  (`A37743`, `A39333`) and any un-accounted shared structure (`A39307`, `A39338`).
- **Auditable unlearning / deletion event** — which client, which forget set, when the unlearning operator was
  applied, and the acceptance-test verdict (`A40045`, `A40896`); schedule a **post-deletion re-audit** with an
  adversarial membership probe (`A41120`, `A40047`).
- **Verifiable-selection commitments** for robust aggregation — commitment-bound scores/prices enabling
  after-the-fact audit of declared-vs-evaluated contribution and selection fairness (`A40889`).
- **RV / architecture-vulnerability snapshot** before deployment and on architecture change (`A37743`).
- **MIA-based ε̂ audit signal** tracked over training epochs / knobs as an empirical leakage trend (`A39510`).
- **Trust-assumption monitors** — collusion / protocol-deviation / honest-majority-violation signals; treat any
  collusion evidence as a confidentiality incident (`A40852`, `A40132`, `A40889`).
- **Immutable, human-readable audit** of the full chain for forensics/compliance — you must supply the tamper-
  evidence mechanism *(reviewer synthesis)*.

## Failure handling

- **Fail-closed on the release path.** Budget exhaustion, accounting error, a failed representation-level
  acceptance test, an un-accounted shared artifact, or collusion evidence → **do not release** the model /
  distilled set / synthetic data; hold for review *(reviewer synthesis; Privacy-Protection §13 treats budget
  exhaustion as an incident boundary)*.
- **Degrade to a stronger guarantee, never to open sharing** — if a subspace/decomposition step is unavailable,
  fall back to full-space accounted DP (more noise), not to heuristic noise or raw sharing.
- **On intermediate-checkpoint leak, downgrade the claimed guarantee** to composition-based (looser) accounting
  for the realized privacy, and disclose it (`A39510`).
- **On a failed deletion acceptance test, re-unlearn or roll back** — do not certify removal; the encoder may
  still hold the forget set (`A39373`), and a later fine-tune can reactivate it (`A41120`).
- **On collusion / dishonest-majority evidence, treat confidentiality as breached** — the MPC/two-server
  guarantee is documented to collapse past its threshold (`A40852`, `A40132`, `A40889`); contain and rotate.
- **Residual leakage is assumed**, so training-data confidentiality pairs with runtime controls
  (`least-privilege-credentials`, `context-and-memory-isolation`) and human approval for high-stakes model
  releases *(reviewer synthesis)*.

## Rollback and containment

- **The privacy dial and the release gate bound the blast radius** — a stricter ε / larger noise / more
  aggressive redundancy removal (`A39212`) and a fail-closed release gate cap what a released artifact can leak.
- **Secure aggregation / egress control is the primary containment for the gradient path** — because
  reconstruction from an intercepted per-client gradient leaves no in-band runtime signal, **prevention
  (isolation / secure aggregation), not detection, is the control** (`A39333` card).
- **Deletion is risk reduction, not guaranteed erasure** — pair "delete my data" with residual-risk disclosure,
  a representation-level acceptance test, and post-deletion re-audit; treat deployment-phase re-fine-tuning as a
  reactivation hazard (`A41120`, `A40047`, `A40343`, `A40045`).
- **Auditable evidence for forensics** — the privacy-config record, budget-accounting trail, unlearning events,
  and verifiable-selection commitments reconstruct what was released under which guarantee (`A40045`, `A40889`;
  architecture-patterns P5).
- **Rotate / re-train on suspected exposure** — if an intermediate checkpoint or raw gradient leaked, the
  realized guarantee is weaker than claimed; re-train under the corrected trust model and re-issue the config of
  record *(reviewer synthesis)*.

## Known bypasses

Demonstrated or corpus-supported bypasses of this pattern's weaker forms:

- **Heuristic / additive gradient noise → reconstructed** by a generic diffusion prior (`A37743`) and
  **analytically, noise-prior-free**, from DP-protected gradients before aggregation (`A39333`, author-reported
  ASR 45% at ε=10, δ=10⁻⁵).
- **Data-locality-only "privacy" → no guarantee at all** — `A39307` / `A39338` share gradients/digests/submodels
  with no accounting; the shared surface is exactly the inversion target.
- **Un-accounted shared structure → silent leak** outside the headline (ε,δ) — structural graphs, masses,
  digests (`A39311`, `A39582`, `A39307`).
- **Intermediate-checkpoint publication → tighter DP bound voided** (`A39510`).
- **Symmetric DP noise on a constrained output → infeasibility** (a safety-constraint violation), which one-sided
  tightening avoids (`A39051`).
- **Cosine-only robust aggregation → collapses under norm/scaling attack** (baselines <20% accuracy;
  norm-normalization is the credited fix) (`A40889`).
- **Behavioral-parity "deletion" → gamed** while the encoder retains the forget set (`A39373`); **fine-tuning
  after unlearning → reactivates** forgotten data (`A41120`); a **single benign black-box query → detects** the
  former-membership imprint (`A40047`).
- **Non-independent public/auxiliary data → the "free" post-processing steps spend un-accounted privacy**
  (`A37854`, `A38016`, `A40117`).

Calibrated takeaway: the demonstrated bypasses are all against **static, non-adaptive** deployments of *other*
schemes under the bypasser's own evaluation. The corpus's own defenses are, with almost no exception, tested
only against non-adaptive attacks or via formal guarantee alone; their adaptive robustness **requires production
validation** (Privacy-Protection §11, §12).

## Residual risks

- **No scheme drives leakage to zero.** `A37743`'s own theory proves exact reconstruction is impossible **but
  noise only raises, never eliminates, the reconstruction-error lower bound** — noise has value and is
  insufficient alone. Every defense here reports a residual, and none claims elimination (Privacy-Protection
  §16).
- **Adaptive attackers are unevaluated across essentially every relevant corpus defense** — the largest
  methodological gap; deployed efficacy may be materially below the reported non-adaptive numbers
  (Privacy-Protection §11, §12).
- **Formal guarantees are only as strong as their accounting and trust boundary** — voided by a leaked
  checkpoint (`A39510`), a colluding majority (`A40852`, `A40132`, `A40889`), or an un-accounted shared artifact
  (`A39311`, `A39582`, `A39307`).
- **Deletion is approximate and reactivatable** — right-to-be-forgotten is risk reduction, not certified
  erasure; behavioral parity is gameable and fine-tuning reactivates (`A39373`, `A41120`, `A40047`, `A40045`).
- **Metric-based privacy is not (ε,δ)-DP** — `A39212`'s FSInfo bound depends on the metric's fidelity to
  perceptual privacy, and MSE is a known-imperfect proxy.
- **Scale and modality are asserted, not shown** — crypto-ML/MPC results are MNIST/~2000-sample/small-NN
  (`A40132`, `A40852`); DP-synthesis is low-resolution (`A38016`); DP fine-tuning centers on encoder LLMs
  (`A40117`). Scaling behavior "requires production validation" (Privacy-Protection §16).
- **The accountant and audit-store integrity are assumed, not demonstrated** — a budget-accounting error or a
  tamperable log undermines the whole control *(reviewer synthesis)*.

## Relevant research (stable paper ids from the syntheses/cards)

Primary (AAAI-26 corpus, Privacy-Protection synthesis):
- **A39510** — *An Improved Privacy and Utility Analysis of DP-SGD with Bounded Domain and Smooth Losses*: tight
  hidden-state RDP + utility bounds for smooth non-convex losses (DPSGD-GC / DPSGD-DC); load-bearing caveat — the
  tighter guarantee dies if intermediate checkpoints leak. Code: DPSGD-DC. *Evidence: Strong (theory);
  empirical realism Moderate (single MIA family).*
- **A39051** — *Differentially Private Linear Programming*: truncated-Laplace one-sided tightening that
  *guarantees* original-constraint feasibility (author-reported zero violation vs up to 51% at ε=0.25; 65%
  sub-optimality reduction); the canonical "DP + hard safety constraint" mechanism. Central DP, synthetic only.
  *Evidence: Strong (narrow scope).*
- **A37854** — *DP-GenG: DP Dataset Distillation Guided by DP-Generated Data*: µ-GDP accounting + post-processing
  immunity as a budget lever; +11.6% utility; image-domain, non-adaptive MIA. *Evidence: Moderate.*
- **A38016** — *RPGen: Robust and Differentially Private Synthetic Image Generation*: DP-SGD fine-tuning +
  adversarial model perturbation (noise-tolerance pre-training on public data, free under accounting); ~20.18%
  lower FID / ~5.45% higher accuracy at ε ∈ {1,5,10}; low-res, no executed attack. *Evidence: Moderate.*
- **A40117** — *DP-SFT: Differentially Private Subspace Fine-Tuning for LLMs*: restrict DP noise to a top-k task
  subspace (remainder is post-processing); near-non-private accuracy; encoder LLMs; no executed attack;
  un-noised orthogonal directions untested. Code: DP-SFT. *Evidence: Moderate.*
- **A40852** — *Efficient, Secure, DP Deep Learning in the Two-Server Model (CRYPTDP / 2PC-zCDP)*: crypto-assisted
  DP training with a bounded comparison-only activation; 642.78 s vs 173,960.9 s (author-reported); semi-honest,
  non-colluding two-server, ~2000-sample scale. *Evidence: Moderate.*
- **A40132** — *Scalable Privacy-Preserving NN Training over Z₂ᵏ via RMFE Packing*: secret-sharing MPC training,
  semi-honest honest-majority (t < n/2), UC framework, MNIST FCN/CNN; fixed-point f ≥ 16 to retain accuracy.
  *Evidence: Moderate.*
- **A40889** — *MartDE: Privacy-Preserving, Cost-Efficient Evaluation for Data Marketplaces*: encrypted utility
  scoring with client-side decryption, commitment-based verifiable selection, norm-normalization before cosine
  trust scoring; anytrust non-collusion; robust to 80% malicious data-providers under over-scaling where cosine
  defenses collapse <20%. *Evidence: Moderate.*
- **A40045** — *Oblivionis: Learning and Unlearning for Federated LLMs*: LoRA-based federated fine-tune + targeted
  unlearning with an auditable evidence record; +27.43% utility vs best local baseline; proxy forgetting metrics
  (no adversarial verification), honest-only. Code: Oblivionis. *Evidence: Moderate.*
- **A37743** — *Enhanced Privacy Leakage from Noise-Perturbed Gradients via Gradient-Guided Conditional Diffusion*
  (GGSS-R): diffusion-prior inversion of noise-perturbed gradients requiring no distributional alignment;
  contributes the reusable Reconstruction-Vulnerability metric RV = max_x‖∇_x∇_W F‖_F; theory shows noise raises
  but does not eliminate the error lower bound; non-adaptive static-noise defense; secure aggregation out of
  scope. Code: GGSS-R. *Evidence: Moderate.*
- **A39333** — *Venom: Liquid Diffusion-Guided Gradient Inversion for Breaking DP in FL*: **analytic,
  noise-prior-free** reconstruction from DP-protected pre-aggregation gradients (author-reported ImageNet LPIPS
  0.340 vs 0.632, ASR 45% vs 2% at ε=10, δ=10⁻⁵); exploits last-FC-layer structure; secure aggregation out of
  scope. *Evidence: Moderate.*
- **A39212** — *InfoDecom: Decomposing Information for Defending Against Privacy Leakage in Split Inference*:
  decompose-then-protect (frequency removal + information-bottleneck) then FSInfo/Fisher-calibrated noise;
  honest-but-curious server with surrogate knowledge; metric (not (ε,δ)-DP) guarantee, vision-only, MSE-as-privacy
  caveat. Code: InfoDecom. *Evidence: Moderate.*
- **A41120** — *PrivUB*: standardized unlearning-attack benchmark (author-stated 11 datasets × 10 models × 10
  techniques × 21 attacks/defenses) showing unlearning introduces new attack surfaces and that fine-tuning
  reactivates forgotten data more than quantization; reframes "forgetting" claims. *Evidence: Moderate (meta-
  result; per-cell metrics truncated in extraction).*
- **A40047** — *FMIA*: single-query, benign-user, black-box former-membership inference on unlearned models — the
  sharpest low-assumption counter to "deletion = unrecoverable". *Evidence: Preliminary–Moderate (cells
  truncated).*
- **A39373** — *IDI*: black-box unlearning metrics are gameable (Head Distillation leaves the encoder retaining
  the forget set — recoverable >82% vs ≤41% for a true retrain); supplies a representation-level acceptance-test
  metric. *Evidence: Moderate.*
- **A39307** — *FedAI* / **A39338** — *FedLAGC*: federated-by-architecture data minimization asserted as privacy
  with **no threat model, attack, or accounting** — the anti-pattern; gradient/digest/submodel sharing is the
  documented leak. *Evidence: Insufficient for the privacy framing (Preliminary).*

Secondary / supporting (same synthesis): **A40838** (DP synthetic in-context demonstrations, single-budget
composition, formal-only), **A40206** (adversarial obfuscation of only the sensitive attribute in VFL; surrogate
attacker acknowledged weaker than a real one), **A39311 / A39582** (ε-DP / LDP with the un-accounted-shared-object
caveat), **A40343** (relearning restores forgotten knowledge unless erasure reaches knowledge-dense layers).

Reviewer-synthesis cross-references (skill artifacts, **not** AAAI corpus papers): `architecture-patterns.md`
P5 (trajectory-level trace / attribution), P6 (credential/egress broker, compromise-budget framing);
`agent-identity.md` (artifact-as-secret / egress control); sibling patterns `least-privilege-credentials.md`,
`context-and-memory-isolation.md`; Privacy-Protection synthesis §6, §9, §11–§17.

## Evidence strength

- **The architectural thesis is well-supported by cross-chunk convergence, not by replication of one measured
  effect.** "Heuristic gradient noise is bypassable" is independently demonstrated by two methodologically
  distinct attacks (`A37743` diffusion-prior, `A39333` analytic) — a strong *design* signal. "Approximate
  deletion leaves reactivatable residue" is supported by ≥7 papers (`A39373`, `A40047`, `A40343`, `A41120`,
  `A40818`, `A40870`, and the standardized `A41120` harness). Treat these as robust cross-paper conclusions, not
  as a single effect size.
- **The corpus efficacy numbers are author-reported, non-adaptive, and best-case.** The defenses argue privacy
  from a formal (ε,δ)/µ-GDP/RDP/FSInfo guarantee or a semi-honest crypto proof and, with the partial exception of
  `A39510` (MIA trend validation), **run no executed attack against their own pipeline** (Privacy-Protection
  §12). Several cards flag truncated / OCR-approximate tables; specific per-cell numbers are author-stated, not
  reviewer-verified.
- **The trust models are narrow.** Honest-but-curious / semi-honest / honest-majority / anytrust-non-collusion
  dominate; malicious, active, and colluding adversaries are almost universally out of scope and often stated so
  (`A40852`, `A40132`, `A40889`).
- **The deterministic, fail-closed, least-privilege, egress-control, and log-the-dial choices are reviewer-
  synthesis engineering practice** grounded in the papers' failure modes and the synthesis' §13–§16 implications
  — not themselves a paper-measured defense result. Their security effect for an agent stack "requires production
  validation."

## When NOT to use this pattern

- **When the training data need not be exposed at all — prefer elimination to protection.** If a model does not
  need to train/fine-tune on sensitive data, don't ingest it and then privatize it. This pattern is for data that
  *must* participate in training but must not leak *(reviewer synthesis; the data-side analogue of least
  privilege)*.
- **For runtime agent-security threats.** Prompt injection, tool/skill abuse, credential misuse, and confused-
  deputy actions are governed by `prompt-injection-containment`, `tool-capability-isolation`,
  `least-privilege-credentials`, and `policy-permission-gates` — not by training-data DP/MPC. Every corpus card
  here marks agent-runtime relevance as *adjacent*, not core.
- **For inference-time prompt/context confidentiality** — protecting a user's prompt or retrieved context from a
  provider model is a redact/anonymize/route-locally control (a different pattern family); this pattern protects
  the *training* artifact.
- **As the sole control.** Accounted DP / secure computation bounds leakage but does not eliminate it (`A37743`
  proves a non-zero residual), does not stop an adaptive attacker (unevaluated corpus-wide), and does not by
  itself certify deletion (`A39373`). Pair with secure aggregation / egress control, a representation-level
  deletion acceptance test, adaptive red-team, and the runtime controls.
- **When you cannot account for every shared artifact or cannot guarantee the trust model.** If shared structure
  is un-accounted (`A39307`) or the non-collusion / honest-majority assumption cannot be operationally enforced
  (`A40852`, `A40132`, `A40889`), the formal guarantee does not hold — establish the accounting/trust anchor
  first, or treat the gap as a named, disclosed residual risk rather than claiming privacy.
- **When "privacy-preserving" is asserted from data locality alone.** Data minimization by architecture is not a
  guarantee (`A39307`, `A39338`); do not adopt it as this pattern — it is the anti-pattern this pattern exists to
  replace.
