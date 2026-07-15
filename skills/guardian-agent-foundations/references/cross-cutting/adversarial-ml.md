# Cross-Cutting Chapter — Adversarial Machine Learning

*Source synthesis: `references/syntheses/Adversarial-ML-Attacks.md` (152 AAAI-26 research cards,
4 merged partial syntheses). This chapter is a cross-paper reading organized by adversarial
**thread**, not a per-paper list. It exists to surface the arguments that only become visible when
the papers are read against each other.*

---

## Evidence-integrity contract (non-negotiable)

- Every numeric value is **author-reported under that paper's own evaluated threat model** unless
  explicitly marked otherwise. Many result tables were flagged truncated in the extracted PDFs; those
  magnitudes are not independently transcribed.
- No titles, authors, venues, datasets, or metrics are invented here. Where the source synthesis
  recorded that a value was absent from a card, this chapter writes **"not stated in paper"** rather
  than supplying one.
- Claims are labeled **(direct)** when they are a finding of the cited paper(s) as recorded in the
  synthesis, and **(reviewer synthesis)** when they are cross-paper judgments — either carried over
  from the source synthesis or made in this chapter. Cross-paper judgments are not assertions of any
  single paper.
- Language is calibrated: "demonstrated under the evaluated threat model", "reduced ASR against the
  tested attacks", "not evaluated against", "requires production validation". No absolutes
  ("secure", "unbreakable", "proven safe") appear.

## Reading key — the CPVER mapping

Every implication is tagged to the Guardian-Agent enforcement primitives (`worldview.md` §2–§6,
`glossary.md`). The recurring corpus slogan — **"capability is not permission; obscurity is not
robustness"** — is exactly this decomposition:

- **[C] Capability** — what a model/agent *can do or produce*: raw outputs, reasoning tokens, tool
  executions, hidden states. The corpus's load-bearing warning is that capability is *not*
  permission and *not* evidence.
- **[P] Permission** — what an action is *authorized* to do: access control, intent-binding,
  least-privilege, capability-gating. Tool identity is not permission (A40895).
- **[V] Verification** — *independent, adversary-aware checking* of an output or action before it is
  trusted: sandbox execution, cross-source corroboration, whole-pipeline adaptive red-teaming.
  Model self-explanations are not verification (A38340).
- **[E] Evidence** — *tamper-evident, independent records*: provenance, attestation, hashes, the
  autonomy trace. Model outputs, explanations, and hidden states are capability, **not** evidence
  (A38853).
- **[R] Residual-risk** — what remains unmitigated after a control fires, dominated in this corpus by
  the **untested adaptive-attacker gap**: the residual risk of essentially every defense here is
  *unknown* because the defense was evaluated non-adaptively.

The single most replicated meta-finding across all four chunks (reviewer synthesis): **static,
non-adaptive defense evaluation dominates the field, and wherever the attacker is allowed to be
defense-aware, the defense degrades or fails.** That finding is the reason the [R] tag appears on
nearly every thread below.

---

## Thread 1 — Evasion (inference-time adversarial examples)

**Well-established.** Bounded and unrestricted input perturbations reliably force
classifier/detector/depth/ReID errors across white-box, transfer, and strict decision-only settings
(direct: A38137, A38320, A38340, A37903, A37955; transfer family A37420/A37436/A37651/A37664/A37695/
A37912/A38013/A38325/A38422). The strongest single-attack evidence is A38127 — a hard-label,
query-efficient ℓ2 attack with **proved O(1/T²) convergence, 13 baselines, released code** — which
anchors the cross-corpus principle that *decision-only API exposure is not a security boundary*
(author-reported). Evasion also generalizes beyond misclassification to **false-positive creation**
("ghost" objects, A37955) and to **dual attacks that spoof the output and forge a coherent-but-false
explanation** (A38340, A-SAGE).

**Emerging.** Naturalistic/diffusion-generated perturbations built by collaborative LLM agents
(A38095, A38137), object-localized unrestricted UAEs (A38325), and semantics-preserving *text*
attacks on financial LLMs/agents (A41099 ChameleonAttack, A41164). These move evasion from pixel
noise toward payloads that are fluent and plausible at the surface.

**Contested.** Whether hiding the confidence signal helps. A38416 *proves* a smoothness dichotomy —
transfer-robustness and query-robustness are mutually exclusive (LR↓ +64% transfer / LR↑ +28% query,
author-reported) — so API-hardening choices trade one evasion class for another; there is no single
setting that suppresses both. Several "black-box" evasion claims are internally contradicted
(A37388 needs logits + embedding-space gradients; A37651/A37664/A37695/A38015 are black-box on the
victim but white/gray-box on a public surrogate) — treat headline "black-box" labels skeptically
(reviewer synthesis, §12).

**Where defenses fail.** Explanation-based human oversight is spoofable (A38340 steers attention/LRP
maps to a false-but-coherent rationale). Purification is a layer, not a gate: UDAP (A38345) beats
DiffPure/GridPure on most attacks yet **fails catastrophically on MIST (FDFR 0.87 vs 0.11)** — its
own table contradicts a "robust to diverse attacks" framing (direct). Ensembling heterogeneous
architectures does *not* by itself confer transfer robustness (A38422, direct).

**Implication.**
- Do not gate oversight on the model's own explanation or attention map — those are **[C] capability**,
  not **[V] verification** and not **[E] evidence** (A38340, A38853). Cross-check against an independent
  signal.
- **[P]** API hygiene helps but cannot be complete: hiding confidence/logits (A38127, A38095) and
  rate-limiting query trajectories raises attacker cost, but A38416's dichotomy means you are choosing
  *which* evasion class to harden against, not eliminating evasion. **[R]** the untraded class remains.
- **Launch gate:** any "robust to adversarial examples" claim must state whether the evaluation was
  adaptive; if the paper only evaded fixed pre-existing defenses (the corpus default), treat the
  robustness number as **non-adaptive** and the residual risk as **[R] unknown**. Purification may ship
  as a layer but never as the sole safety gate (A38345).

## Thread 2 — Poisoning (training-time / supply-chain data manipulation)

**Well-established.** Training-time / supply-chain injection is the corpus's *largest* threat cluster
(direct, §3): the adversary controls training data, labels, a reused component, or the pre-release
model, and the victim later trusts it. Poisoning succeeds at very low budget while preserving clean
accuracy — GCB (A39935) reports **≤1% clean-accuracy drop at ≤0.5% poison** (author-reported) — which
is precisely what defeats accuracy-only QA. Agentic structure does not confer immunity: Fact2Fiction
(A40353) defeats decomposition-based RAG fact-checking by **mirroring the system's own task
decomposition, effective at ~0.1% poison** (author-reported); Joint-GCG (A40893) jointly optimizes
retriever + generator so one document both survives retrieval and overrides generation.

**Emerging.** (1) **Adversarial *missingness*** (A39428): the attacker hides existing entries rather
than inserting/perturbing, so sanitization and outlier detection never trigger — even MICE, the most
robust imputer tested, still failed on two datasets (direct). (2) **Dataset-distillation as a
poisoning primitive** — sub-minute, model-agnostic (A37119); clean-label physical backdoors via
distillation (A37349). (3) **Deferred poisoning** via input-Hessian singularization that leaves
clean accuracy intact until a trigger condition (A39318).

**Contested.** Whether classical poisoning defenses generalize. A39428 shows omission-based poisoning
is *outside the design assumption* of insertion/perturbation defenses; label-flipping's minimum
flip-count is NP-Complete to compute and the theory is linear-only (A39301). These are scope
boundaries, not contradictions (reviewer synthesis).

**Where defenses fail.** Sanitization/outlier detection assume the poison is an inserted anomaly;
missingness and in-distribution constructions defeat that assumption (A39428). Detection calibrated
on one distribution misses poison expressed under shift (see Thread 9).

**Implication.**
- **[E] Provenance/attestation is the primary control, not adaptation.** Require crypto-provenance and
  hashes for datasets, labels, reused components, and retrieval corpora, so a discovered poison is
  traceable and a clean checkpoint is restorable (reviewer synthesis, §15–16).
- **[P] Treat every retrieval corpus and third-party dataset as attacker-writable.** Trust-score and
  isolate open-web KBs before they enter a reasoning model (A40353, A40893, A40726, A40876).
- **[V]** Sanitization is necessary but insufficient — pair it with source-influence caps and
  post-ingestion adaptive red-teaming; a single filter is bypassable (A39428).
- **Launch gate:** a poisoning defense that was only tested against insertion/perturbation attacks has
  **[R] unknown** residual risk against omission and in-distribution poisoning; require both classes in
  the pre-ship suite.

## Thread 3 — Backdoors (trigger insertion; the single largest attack family)

**Well-established.** Backdoors are the largest family (direct, §4) and have evolved far past fixed
word/patch triggers: clean-label (A37349, A39935, A39747), syntactic/style/dynamic (A40894 All-to-X
distributed targets, A40897, A41080), multi-target via proxy-space partitioning (A38015),
parameter-efficient prompt-tuning injection with **no base-weight retraining** (A41121), and physical/3D
triggers (A40842 LiDAR, A40855 6DoF-pose, A38056 UV-fluorescence). Two independently replicated,
high-confidence sub-findings:

1. **Retraining/fine-tuning does not reliably remove implanted behavior.** P-Trojan (A40295) is
   engineered so ordinary *clean* fine-tuning **reinforces** it (theory + **>99% persistence**,
   author-reported); A39809 re-injects after retraining and evades BIRD/SHINE; A40855's residual
   pose-offset persists through clean fine-tuning (an honest negative from the authors) (direct).
2. **Backdoors preserve clean accuracy — and even plausible rationales and correct answers — defeating
   accuracy-only QA.** A39935 (≤1% drop at ≤0.5% poison), A40409 (interpretable rationale preserved),
   A40486 (answers correct while reasoning inflates **~17× on MATH-500**), A40867 (clean capability in
   shallow layers) (direct, author-reported).

**Emerging.** *Dormant-until-finetune* backdoors that are **invisible pre-finetuning**: A39480 (CLIP)
evades **7 detectors** — Neural Cleanse, STRIP, GangSweep, TND-DL/DF, CBD, CleanCLIP — precisely
because they inspect the pre-finetuning model where the payload is absent (direct). A39593 (graph
foundation model) and A39577 (time-series) corroborate the dormant-at-pretraining pattern. Detection
signals are also emerging: attention-head cosine similarity with **no clean-twin model required**
(A41080, e.g. BadNets 0.9921 vs 0.9149 author-reported), token-confidence sequence-lock (A40897),
deep-layer attention-hijacking as the mechanism behind test-time purification (A40867 PurMM).

**Contested.** Whether purification/removal is trustworthy. UDAP's MIST failure (A38345), the need for
a small trusted clean set in most surgical purifiers (A40902, A40904, A41080), and the fact that
several detectors are dataset-dependent (A40897 reports FPR up to ~21.95% on Shakespeare-style,
author-reported) mean removal is a *risk-reduction layer*, not a gate (reviewer synthesis).

**Where defenses fail.** Pre-finetuning inspection is structurally blind to dormant backdoors
(A39480). Backdoor detectors that inspect the *wrong* model state, or that assume a single backdoor,
miss the payload — A38015 shows multiple coexisting backdoors. Retraining-based cleanup is defeated by
gradient-aligned persistence (A40295).

**Implication.**
- **[E] Provenance over adaptation.** Retraining does not remove backdoors and accuracy does not reveal
  them, so treat weight/adapter provenance as the control (A39809, A40295, A40855). Add **post-finetuning**
  red-teaming to model onboarding because pre-finetuning inspection is blind (A39480, A39593). Scan for
  *multiple coexisting* backdoors, not one (A38015).
- **[V] Supply-chain sanitization gate** before promoting third-party checkpoints/adapters:
  attention-similarity / neuron-attribution screening (A41080, A40904), re-distillation on a small
  clean set (A40902), adapter/prompt-tuning provenance checks (A41121).
- **[C] Monitor the right signal, not output accuracy.** Instrument deep-layer attention concentration
  (A40867), attention-head-similarity stats (A41080), token-confidence-run events (A40897), and
  reasoning-token telemetry (A40486) — because the malicious behavior is invisible in the accuracy
  metric (reviewer synthesis, §14).
- **Launch gate:** a checkpoint that passed pre-finetuning scanning still carries **[R] unknown**
  dormant-backdoor risk; require post-finetuning screening and forensic hash logging before promotion.

## Thread 4 — Transferability

**Well-established.** Surrogate-then-transfer (craft offline on a surrogate, no victim queries) is the
*default* black-box recipe across the corpus (direct: A37420/A37436/A37651/A37664/A37695/A37912/A38013/
A40176/A40849/A40877/A40878/A39997/A41144/A42439). Two independently converged mechanistic claims:

1. **Loss-landscape geometry drives transfer.** Flat minima (A36964, **80.1% cross-dataset ASR, 73.2%
   post-defense**, author-reported), path flatness (A37912), and manifold-tangent projection (A38013)
   arrive at the same conclusion from attack and geometry sides (direct).
2. **Shared vision backbones create systemic monoculture transfer risk.** MFA (A41144) shows one image
   transfers across 17 open+commercial VLMs (**avg 59.58% image ASR**, author-reported); PhysPatch
   (A42439) shows a CLIP-ensemble surrogate transfers to **12 commercial/reasoning MLLM-AD stacks**
   (direct). A shared base between a guard model and the guarded model is itself a weakness (A41108).

**Emerging.** Transfer as a *membership/IP* vector, not only an evasion vector: out-of-domain surrogate
of a proprietary graph-VFL server model (A40878), near-100% watermark overwrite that transfers across
white/gray/black-box (A39997), and iteration-count-to-craft-an-AE as a *universal* membership signal
even on hard-label APIs (A40912).

**Contested.** What confers transfer robustness. A38416 proves transfer- and query-robustness are
**mutually exclusive** under model smoothness (a no-free-lunch tension); A38422 shows ensembling
heterogeneous architectures does *not* by itself confer transfer robustness. Transfer-ASR metrics are
also confounded — A38325's card notes quality-thresholded transfer ASR *inflates* apparent success
(reviewer synthesis, §8).

**Where defenses fail.** Defenses tuned on one architecture/backbone inherit the monoculture: a
perturbation crafted on a shared encoder (CLIP) transfers to black-box commercial models (A41144,
A42439), and guard stacks sharing a base with the guarded model are jointly bypassable (A41108).

**Implication.**
- **[P] Break the monoculture.** Independent, non-monoculture, whole-pipeline enforcement — the guard
  should not share a base with the guarded model (A41108); perception should not rely on a single
  shared encoder (A42439) (reviewer synthesis, §14–15).
- **[V] Cross-source corroboration** where transfer is the threat: multi-sensor voting for perception
  (A42439, A40881), and heterogeneous-provenance checks rather than a single surrogate-shaped detector.
- **[E]** Weight/backbone secrecy is fragile evidence: near-100% overwrite (A39997) and out-of-domain
  surrogates (A40878) mean "the attacker doesn't have our weights" is not a durable assumption; bound
  any single party's influence rather than relying on model secrecy (reviewer synthesis, §15).
- **Launch gate:** treat any defense validated on a single backbone/architecture as carrying **[R]**
  monoculture-transfer residual risk; require cross-backbone transfer testing before shipping.

## Thread 5 — Physical-world attacks

**Well-established (as attacks; under-defended).** Physical-signal and physical-perception attacks are
demonstrated across LiDAR, camera, and sensor injection. The strongest-evidence physical result is
CP-FREEZER (A37082): a latency-inflation attack that inflates cooperative-perception latency
**>90× (>3 s/frame), reaching 100% on a real physical vehicle testbed under the evaluated setup**
(author-reported) — and it shows that *integrity* defenses are structurally useless when the detection
output never arrives. Phantom Menace (A40881) validates **8 sensor-injection attacks** (laser blinding,
light projection, EM color strip, ultrasound blur, voice DoS/spoof) on a **real Franka arm** (direct).

**Emerging.** Transferable, small-footprint physical patches on driving stacks — PhysPatch (A42439),
a **~1%-area** patch steering 12 commercial/reasoning MLLM-AD stacks — and 3D disparity-consistent
camouflage against stereo depth (A38320), sparse cooperative 3D point-cloud attacks (A37903), and
false-positive "ghost vehicle" creation on 3D detection (A37955).

**Contested / caveated.** *Physical realizability is frequently asserted but measured digitally.*
PhysPatch (A42439) is framed "physically realizable" but evaluated on **digitally-patched nuScenes
frames**; A41121's physical-sticker motivation has a digital evaluation; A37479/A37955/A38056 are
argued by citation/summary. A40881 does validate on real hardware but on **limited tasks** (direct,
§12). True over-the-air physical realizability remains under-demonstrated (A40842, A40855, A40867)
(reviewer synthesis, §17).

**Where defenses fail.** Single-modality perception is evadable even by natural-looking or
disparity-consistent artifacts (A42439, A40881, A38095, A38137, A38320). Integrity checks assume the
signal arrives — availability attacks defeat that assumption (A37082). Runtime detection/containment of
physical attacks on VLA/AD stacks is largely absent: A40881 provides only training-time hardening;
A42439/A42145 provide no deployed mitigation (direct, §17).

**Implication.**
- **[V] Cross-sensor / cross-source corroboration before any safety-critical actuation gate.** Require
  multi-sensor voting, sensor-health monitoring, and confidence-*plus*-consistency (not
  confidence-alone) gating (A42439, A40881, A38095, A38137, A38320) (reviewer synthesis, §15).
- **[P] Gate actuation before the actuator fires** (`worldview.md` §3 — for embodied AI the action
  level is primary). Availability is a defended SLA, not an assumption: bound worst-case per-message
  compute and isolate per-sender cost in perception fusion (A37082) (reviewer synthesis, §14).
- **Launch gate:** a "physically realizable" claim evaluated only on digitally-patched frames has
  **[R] production-validation-pending** residual risk (A42439, A41121); require over-the-air validation
  before relying on the mitigation. And no perception defense should be credited with availability
  guarantees unless it was tested under a latency/DoS adversary (A37082).

## Thread 6 — Adaptive attackers (the corpus's central methodological axis)

**Well-established (as a gap).** This is the corpus's most replicated meta-finding (reviewer synthesis,
§9): **non-adaptive defense evaluation systematically overstates security.** Attack papers evade only
fixed pre-existing defenses; defense papers concede adaptive robustness is unproven. Concretely,
whenever an attacker was allowed to be defense-aware, the defense degraded or fell:

- **Whole-pipeline guard-stack collapse.** STACK (A41108) moves a per-component-robust guard stack from
  **0% → 71% black-box** (33% transfer) and MFA (A41144) from **0% → 58.5%** (52.8% commercial, up to
  72.92% with all three facets) — both exploiting the *same* concrete channel: inducing the model to
  emit an attacker-chosen string past the output classifier (direct, author-reported, independently
  replicated).
- **Robust FL aggregation bypassed.** ShadeEdit (A40787) evades **8 aggregators at ~99.5% avg ASR**;
  Pill (A39290) bypasses **>90% across 9 rules** — and its own authored adaptive defense is reported
  *insufficient* (direct).
- **Confused-deputy at the tool layer.** MCPTox (A40895) hijacks a legitimate high-privilege tool via a
  poisoned *description* (**peak 72.8% ASR on o1-mini**, **<3% refusal even on Claude-3.7-Sonnet**,
  author-reported) — defeating permission models keyed to tool identity *and* model-level alignment.

**Emerging (the gold standard).** A small set of papers model the adaptive attacker honestly and are
the methodological bar the rest should meet: A37117 candidly reports its naive design is broken by an
adaptive trigger-inversion attacker, then fortifies with randomized smoothing (reversed-accuracy
9.25% ≈ clean 9.47%); A40905/A40915 *build* purpose-built adaptive removers/forgers rather than testing
only against standard defenses; A37716 offers attack-agnostic certification; A38949/A38785 use learned
adversaries (direct, §11).

**Contested.** Little is genuinely contested here — the field agrees the gap exists; what varies is
whether authors *acknowledge* it. Several defense papers (A39778, A40859 capability-isolation) report
strong ASR reduction but explicitly flag that an attacker *shaping the shared component* was not
evaluated — a claim-strength tension, not a contradiction (reviewer synthesis, §10).

**Where defenses fail.** Everywhere the evaluation was static. The corpus contains **no defense offering
certified robustness against an unbounded adaptive adversary** (direct, §17).

**Implication.**
- **[R] This is the primary residual-risk tag.** Treat any "robust against SOTA defenses" claim as
  *non-adaptive* — and therefore of **unknown residual risk** — unless the paper built a purpose-built
  adaptive attacker (the A40905/A40915/A37117 bar) (reviewer synthesis, §16).
- **[V] Require adaptive, defense-aware red-teaming before shipping any defense**, integrated into
  CI/CD; a credible safety product validates its own guardrails continuously (`worldview.md` §4, §9).
  Break the specific verbatim-echo channel that smuggles strings past output classifiers (A41108, A41144).
- **[P] Bind actions to verified user intent, not tool identity.** A pre-execution gate must verify each
  planned tool call against the original request; require human approval for high-privilege actions
  (e.g. credential/SSH-key reads) regardless of which tool requests them (A40895) (reviewer synthesis, §14).
- **Launch gate (hard):** no defense ships on a non-adaptive evaluation. If the adaptive attacker was
  not built, the launch record must state residual risk is **[R] unknown**, not "robust."

## Thread 7 — Certified vs empirical robustness

**Well-established.** The corpus is overwhelmingly *empirical*; formal guarantees are rare and narrow.
Only a handful of results carry formal or broadly-validated support:

- **CertMask (A37716)** — attack-agnostic patch certificate at **O(n) vs PatchCleanser's O(n²)**, up to
  **+13.4% certified accuracy** (author-reported), with formal necessary/sufficient coverage
  conditions — **bounded by a *known* single patch-size assumption** (direct).
- **A37117** — randomized-smoothing-fortified capability lock, **ℓ2-certified within the modeled radius**
  (direct).
- **NeuralMark (A40915)** — SHAKE-256 hash-as-filter watermark with a **forging-probability bound
  < 1/2^128 at n=256** (author-reported).
- **AntiDote (A40570)** — open-weight LLM tamper-resistance (**10 models 0.6B–27B × a 52-attack suite;
  up to 27.4% more robust / 78% harmful-score reduction / <0.5% utility loss**, author-reported) —
  **explicitly framed as risk-reduction, a proxy for an intractable min-max, not a proof** (direct).

**Emerging.** Certification is being pushed toward attack-agnostic and capability-gated forms (A37716,
A37117), but always inside a narrow modeled threat: known single patch size (A37716), ℓ2 radius
(A37117), single embedding round (A37010).

**Contested / bounded.** The gap between a certificate and deployment safety. Every certificate here
holds *only within its modeled radius/assumption*; **no defense in the corpus offers certified
robustness against an adaptive adversary, and no privacy defense offers a formal DP guarantee** —
all privacy defenses are empirical (A39752, A40447, A40876, A40877, A38853) and require production
validation (direct, §16–17). Where DP is asserted (A39382) it is via budget without empirical attack
testing.

**Where defenses fail.** Outside the modeled assumption: an unknown or multiple patch size defeats the
A37716 coverage condition; a non-ℓ2 trigger falls outside A37117's radius; multi-round embedding
defeats single-round watermark bounds (A37010, near-100% overwrite in A39997).

**Implication.**
- **[E] Do not present empirical robustness as a guarantee.** In the launch record, a certificate is
  **[E] evidence only within its stated radius/assumption**; empirical results are risk-reduction, not
  proof. AntiDote's self-framing (reduction, not proof) is the correct standard (A40570) (reviewer
  synthesis, §16).
- **[R]** Outside the certified radius the residual risk is **unknown**; state the assumption explicitly
  (patch size, norm ball, embedding rounds) next to every certified number.
- **Launch gate:** a certified claim may gate launch *only* for inputs inside its modeled assumption;
  everything outside inherits the empirical/adaptive residual-risk gate from Thread 6. No privacy
  control ships as "guaranteed" absent a formal DP argument the corpus does not currently supply.

## Thread 8 — Robustness–accuracy (and robustness–generalization) tradeoffs

**Well-established.** Robustness routinely costs clean utility, and one tradeoff is *proven*: A38416
establishes a smoothness **dichotomy** in which transfer-robustness and query-robustness are mutually
exclusive (LR↓ +64% transfer / LR↑ +28% query, author-reported) — a genuine no-free-lunch result, not
a tuning artifact (direct). Empirical utility costs recur: A38121 (SRD) up to **~15% CIDEr** drop;
A39318 clean accuracy **0.81 → 0.71**; A37117 authorized accuracy **86.2% → 73.9%**; A42327's
in-distribution cluster-swap keeps detection ≤1.5% *while collapsing MNIST accuracy to ~42–46%*
(all author-reported).

**Emerging / contested.** Whether the robustness–generalization tradeoff is fundamental. A39603 (TIMA)
argues the CLIP robustness/generalization tradeoff **can** be jointly improved (contra prior
LAAT-style expansion) — a direct counter-position to the "tradeoff is inevitable" reading. A38416's
dichotomy and A39603's joint-improvement claim are the two poles; the corpus does not resolve them
(reviewer synthesis, §10). Many attack papers additionally report only a **single operating point**,
so the true frontier shape is often unobservable (direct, §10).

**Where defenses fail.** Defenses whose only evaluation is a single operating point hide the tradeoff:
a strong ASR-reduction number at an undisclosed utility cost is not a shippable operating point.
Purification and imputation impose accuracy costs that can exceed their security benefit on specific
attacks (A38345 MIST, A39428 MICE).

**Implication.**
- **[C]/[P]** Precision is the dominant enterprise metric (`worldview.md` §7): over-blocking →
  alert fatigue → operators bypass the guardrail → blind spots. A robustness gain that inflates
  benign false-positives (A40897 up to ~21.95% FPR on one style; A37389's *missing* benign-FPR flagged
  as undercutting a prompt-firewall) can *reduce* net security by driving bypass.
- **[V]** Require the *frontier*, not a point: a defense must report clean utility **and** benign-FPR at
  the proposed operating point (A38121, A39318, A37117) before it can be verified as shippable.
- **Launch gate:** reject robustness numbers reported at a single operating point with no utility /
  benign-FPR disclosure; the residual risk is **[R]** an unmeasured utility collapse (A42327) or an
  over-refusal that causes operational bypass.

## Thread 9 — Distribution shift

*(Scope note, reviewer synthesis: this corpus has no dedicated covariate-/label-shift generalization
line the way an OOD-robustness corpus would. "Shift" appears here as the **axis along which other
attacks become invisible to detectors calibrated in-distribution** — chiefly cross-dataset transfer,
the pretraining→finetuning activation gap, and evaluation-distribution confounds. That cross-paper
observation is the thread.)*

**Well-established.** Detectors and metrics calibrated on one distribution miss threats expressed under
shift:

- **Cross-dataset shift hides backdoors.** A36964's flat-minima code-model backdoor **evades AC,
  Spectral Signature, ONION, KillBadCode, EliBadCode under cross-dataset shift** (80.1% cross-dataset
  ASR, author-reported) (direct).
- **The pretraining→finetuning gap is a distribution shift that hides dormant backdoors.** A39480
  (CLIP), A39593 (graph FM), A39577 (time-series), A40295 (LLM), A40855 (6DoF-pose): the payload is
  absent at pretraining and *activated* by the victim's own downstream fine-tuning, defeating
  pre-finetuning inspection (direct). (Cross-links Threads 2–3.)
- **Evaluation-distribution confounds inflate results.** A39276 shows with theory (Δ_N = O(T/N),
  slope 0.99±0.02, R²=0.997) and significance testing that prior "near-perfect" CLIP membership
  inference **collapses to near-chance (CSA AUC 94% → 51%) under strictly in-distribution
  evaluation** — a strong, well-supported methodological result (direct).

**Emerging.** Shift-aware defenses: manifold/OOD-likelihood detect-and-correct for adversarial inputs
(A40301), Mahalanobis + spectral fusion (A40366), and FL backdoor defenses under **domain skew**
(A39778, share-only-low-capacity-module isolation). Whether temporal/architectural redundancy is
robustness under shift is contested — A37479 argues SNN multi-timestep structure is *not* inherent
robustness; A37770 argues CTDG memory *dilutes* isolated perturbations yet still shows ~29% avg
degradation. Same property cuts both ways (reviewer synthesis, §10).

**Contested / out of scope.** Non-adversarial OOD stressors are explicitly flagged as *not* robustness
evidence: A37792 (camera-glass fracture) has "no true adversary" and A37272/A37318/A37488/A37967 are
GAN/domain-adversarial *training* techniques with no threat actor — **do not cite these as robustness
evidence** (direct, §2).

**Where defenses fail.** Any detector, MIA benchmark, or QA metric validated in-distribution carries
**[R]** unmeasured risk under cross-dataset / cross-domain / post-finetuning shift (A36964, A39480,
A39276). Pre-finetuning inspection is structurally blind to the shift that activates the payload
(A39480).

**Implication.**
- **[V] Post-finetuning, cross-distribution red-teaming** is mandatory for onboarding: pre-finetuning
  screening does not observe the activated behavior (A39480, A39593) (reviewer synthesis, §15).
- **[V] Evaluate detectors and MIA/QA metrics under the deployment distribution, not a convenient
  one.** In-distribution-only evaluation is a known result-inflator (A39276); cross-corpus numbers
  should be treated skeptically until distribution-matched.
- **[E]** Distinguish adversarial shift from benign OOD in the trace: benign-OOD stressors (A37792) are
  reliability data, not security evidence — do not let them stand in for adaptive robustness.
- **Launch gate:** a detector or metric validated only in-distribution has **[R] unknown** residual risk
  under shift; require deployment-distribution and post-finetuning evaluation before it gates anything.

---

## Cross-thread reading — how the threads compound

The threads are not independent; the corpus's transferable value is where they **compose** (reviewer
synthesis):

- **Poisoning × distribution shift × backdoors** → *dormant-until-finetune* payloads that are invisible
  pre-finetuning (A39480, A39593, A40295). Provenance **[E]** + post-finetuning adaptive red-team **[V]**,
  not accuracy QA, is the only cross-thread control.
- **Transferability × physical-world × evasion** → a ~1%-area patch crafted on a shared encoder steers
  12 commercial MLLM-AD stacks (A42439). Only cross-sensor **[V]** verification and monoculture-breaking
  **[P]** address it.
- **Adaptive attacker × compositional guard stacks** → per-component-robust pipelines collapse
  (0%→71% / 0%→58.5%) via one shared output-repetition channel (A41108, A41144). Whole-pipeline
  adaptive evaluation **[V]** is the only detector.
- **Confused-deputy (tool metadata) × permission model** → MCPTox (A40895) never executes the poisoned
  tool; a trusted high-privilege tool does the harm. Intent-binding **[P]**, not tool-identity
  permission, is the control.
- **Availability × integrity** → CP-FREEZER (A37082) shows integrity defenses are useless when the
  detection output never arrives. Availability must be a defended SLA **[P]**, instrumented in the trace
  **[E]**.

## Consolidated launch-gate checklist (reviewer synthesis, grounded in the cards)

1. **Adaptive-attacker gate (from Thread 6, applies to all).** No defense ships on a non-adaptive
   evaluation. Absent a purpose-built adaptive attacker, the launch record states residual risk is
   **[R] unknown** — never "robust" (A41108, A41144, A40787, A39290; bar set by A40905/A40915/A37117).
2. **Provenance/attestation gate (Threads 2–3).** Crypto-provenance + hashes for weights, adapters,
   datasets, labels, retrieval corpora; **post-finetuning** screening because pre-finetuning inspection
   is blind (A39480); scan for *multiple* backdoors (A38015). **[E]**
3. **Intent-binding gate (Thread 6).** Verify each planned tool call against the original request;
   human approval for high-privilege/credential actions regardless of requesting tool (A40895). **[P]**
4. **Cross-source verification gate (Threads 4–5).** Multi-sensor voting + consistency (not
   confidence-alone) before safety-critical actuation; independent, non-monoculture guard pipeline
   (A42439, A40881, A41108, A41144). **[V]**
5. **Right-signal telemetry gate (Threads 1,3,6).** Instrument reasoning-token length, deep-layer
   attention concentration, confidence-run and output-repetition events — because backdoors/DoS
   preserve accuracy (A40486, A40867, A41080, A40897, A40445). **[E]/[C]**
6. **Certification-scope gate (Thread 7).** A certified number gates launch only inside its stated
   assumption (patch size, ℓ2 radius, embedding rounds); everything outside inherits the empirical
   residual-risk gate (A37716, A37117, A40915, A40570). **[E]/[R]**
7. **Utility/benign-FPR gate (Thread 8).** Reject robustness reported at a single operating point with
   no clean-utility / benign-FPR disclosure; over-refusal is a first-class failure that causes bypass
   (A38416, A40897, A37389, A42327). **[C]/[P]**
8. **Distribution-match gate (Thread 9).** Detectors and MIA/QA metrics validated only in-distribution
   carry unknown residual risk under shift; require deployment-distribution + post-finetuning evaluation
   (A39276, A36964, A39480). **[V]/[R]**

---

*Closing evidence-integrity note.* Every metric in this chapter is reported as it appears in the source
synthesis's research cards, labeled author-reported where the card so labels it; several headline
numbers sit in table regions the synthesis marked truncated and are therefore not independently
verified. No titles, authors, venues, datasets, or numbers were invented; where a card recorded that a
value was absent, this chapter does not assert one. Cross-paper judgments are marked *(reviewer
synthesis)*; all other claims trace to the cited paper id under its own evaluated threat model. This
chapter draws only on `references/syntheses/Adversarial-ML-Attacks.md`; claims requiring the primary
PDFs (e.g. exact table cells) are **[R] production-/source-validation-pending**.
