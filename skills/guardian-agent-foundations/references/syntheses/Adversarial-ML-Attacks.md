# Adversarial-ML-Attacks — Authoritative Synthesis

Merged from 4 partial syntheses covering 152 AAAI-26 research cards filed under the
"Adversarial-ML-Attacks" corpus folder. Weighting reflects experimental quality,
reproducibility, threat-model realism, and independent (cross-paper) replication — not
paper count.

**Evidence-integrity contract.** Every numeric value below is **author-reported** under
that paper's own evaluated threat model unless explicitly marked otherwise; many result
tables were truncated in the extracted PDFs and are flagged where that matters. No titles,
authors, venues, datasets, metrics, attack-success or defense numbers were invented. Where a
value was absent from a card it is written "not stated in paper." Claims labeled *(reviewer
synthesis)* are cross-paper judgments made by the partial-synthesis authors or this merge, not
assertions of any single paper. Language is calibrated ("demonstrated under the evaluated
threat model", "reduced ASR against the tested attacks", "not evaluated against", "requires
production validation"); no absolutes ("secure", "unbreakable", "proven safe") are used.

---

## 1. Executive summary

This corpus is dominated by **classical ML robustness research** (vision, graph, tabular,
federated, audio, physical-perception), with a **minority — but the highest-value minority —
sitting squarely in agent/LLM-runtime security**. The single most robust, repeatedly
replicated finding across all four chunks is methodological: **static, non-adaptive defense
evaluation dominates the field, and wherever an attacker is allowed to be defense-aware, the
defense degrades or fails.** Nearly every attack paper demonstrates evasion only against fixed
pre-existing defenses, and nearly every defense paper concedes that an adaptive adversary was
not tested.

The findings most transferable to a Guardian-Agent / autonomy-trace stack, ranked by evidence
strength and threat-model realism:

- **Metadata and tool descriptions are an injection surface as dangerous as content.**
  MCPTox (A40895) shows tool-description poisoning is a *distinct* confused-deputy vector: the
  poisoned tool never executes; a legitimate high-privilege tool carries out the malicious
  action, defeating permission models keyed to tool identity and defeating model-level
  alignment (peak ASR 72.8% on o1-mini; <3% refusal even on Claude-3.7-Sonnet, author-reported).
- **Defense-in-depth guard stacks that look robust per-component collapse under whole-pipeline
  adaptive attacks.** STACK (A41108) and MFA (A41144) independently move a few-shot guard
  pipeline from ~0% baseline ASR to 71% / 58.5% (author-reported) and both exploit the same
  concrete channel — inducing the model to emit an attacker-chosen string past the output
  classifier.
- **Agentic structure is not self-protective.** Fact2Fiction (A40353) defeats decomposition-
  based RAG fact-checking by mirroring the system's own task decomposition (effective at ~0.1%
  poison, author-reported); MAST (A40224) reframes the inter-agent message bus as a MITM
  surface.
- **Retraining/fine-tuning does not remove implanted behavior; provenance is the control.**
  P-Trojan (A40295) is engineered so ordinary clean fine-tuning *reinforces* it (>99%
  persistence, author-reported); A39809, A40855 corroborate.
- **Reasoning/inference compute is a first-class availability surface.** Three papers (A40445,
  A40486, A40833 — the last on o3 via indirect prompt injection) inflate reasoning length while
  keeping answers correct, invisible to accuracy-only monitoring.
- **Availability of hard-real-time perception pipelines is under-defended.** CP-FREEZER
  (A37082) inflates cooperative-perception latency >90× on a real vehicle testbed (author-
  reported) and shows integrity defenses are structurally useless when detection outputs never
  arrive.

The corpus contains only two `strong`-graded *defense* results with formal or broadly-validated
support — CertMask (A37716, attack-agnostic O(n) certified patch robustness, bounded by a known
patch-size assumption) and AntiDote (A40570, tamper-resistance for open-weight LLMs, explicitly
framed as risk-reduction, not proof). **No defense in the corpus offers certified robustness
against an adaptive adversary, and no privacy defense offers a formal DP guarantee.**

## 2. Scope and boundaries

- **In scope (this synthesis's focus):** adversarial examples / evasion, data poisoning,
  backdoors, membership-inference / reconstruction / inversion privacy attacks, availability /
  resource-exhaustion attacks, agent/tool/RAG-layer attacks, watermark/provenance attacks, and
  the corresponding defenses — across vision, graph, tabular, audio, federated, physical-sensor,
  and LLM/VLM/agent systems.
- **Direct agent/LLM relevance is the minority.** Genuinely agent-central papers concentrate in
  chunks 2–3: MCP tool poisoning (A40895, A40898), guard-stack bypass (A41108, A41144),
  agentic-RAG poisoning (A40353, A40893), inter-agent tampering (A40224), persistent LLM
  backdoors (A40295, A40409, A40486), reasoning-DoS (A40445, A40486, A40833), MLLM backdoor
  purification (A40867), open-weight tamper-resistance (A40570), RAG confidentiality (A40726,
  A40876), and physical VLA/MLLM-AD attacks (A40881, A42439). Chunks 0–1 are largely
  vision/graph/federated ML whose value is architectural/transferable, not drop-in.
- **Explicitly out of scope / mislabeled (do not cite as robustness evidence).** The corpus
  folder is keyword-filtered, so "adversarial" sometimes means GAN/domain-adversarial *training*
  with no threat actor: A37272, A37318, A37488, A37967 (chunk 0); A38469, A38489, A38515,
  A38785, A39336, A39438, A39382 (chunk 1). Non-ML-security or unverifiable: A40964 (adversarial
  FOND planning), A41213 (clinical-NLP with adversarial regularizer), A41404 (abstract reprint,
  no methods/metrics), A42145 (doctoral-consortium in-progress AV-falsification abstract).
- **Data-integrity caveat on identifiers.** Chunk 2 flags that the corpus manifest's arXiv IDs
  are frequently mis-extracted citation IDs (flagged on A39668, A39725, A39747, A39803, A40176,
  A40224, A40272, A40295, A40301). Trust the internal Axxxxx card ids, not manifest arXiv IDs,
  for those.

## 3. Dominant threat models

Grouped by adversary capability, as stated across the corpus:

1. **Training-time / supply-chain injection (largest cluster).** Adversary controls training
   data, a reused component, labels, or the pre-release model; the victim later trusts and
   deploys it. Spans poison-only black-box supply chain (A36961, A36964, A37119, A37770, A38056),
   clean-label / hidden-trigger gray-box (A37349, A39935, A39747), backdoors dormant until the
   victim's own downstream fine-tuning (A39480 CLIP, A39593 graph-FM, A39577 time-series, A40295
   LLM, A40855 6DoF-pose), and MLLM/LVLM fine-tune backdoors (A38015, A40867, A40891).
2. **Inference-time evasion of perception models.** Bounded/unrestricted input perturbations
   cause a classifier/detector/depth/ReID model to err. Knowledge ranges white-box (A38137,
   A38320, A38340, A37082, A37396, A37903, A37479, A37955) through gray/black-box transfer
   (A37420, A37436, A37651, A37664, A37695, A37912, A38013, A38325, A38422) to strict
   hard-label/decision-only black-box (A38127) and physical-world (A38095, A38320, A37647,
   A42439, A40881).
3. **Federated-learning insider / malicious participant.** Poisoned updates that hide inside
   robust-aggregation trust regions: A38328 (boundary-adaptive), A39290 ("pill"/subnet), A39560
   (Byzantine mean estimation defense), A39725/A39778/A40051/A40787/A40859/A40878/A40908/A42327.
4. **Privacy inference / reconstruction.** Membership inference (A38134, A38576, A39276, A39449,
   A40587, A40726, A40846, A40912), attribute/gradient/geo inference (A39500, A39752, A40447,
   A40877), embedding inversion (A40876), split-LLM hidden-state inversion recovering prompts
   (A38853), and unlearning-induced leakage (A39725). Recurring insight: *legitimate access is
   the attack surface.*
5. **Availability / economic-DoS on reasoning LLMs (emerging).** Inflate compute/latency while
   preserving output correctness: A40445 (repetitive generation), A40486 (triggered CoT
   verbosity), A40833 (poly-base reasoning extension via indirect injection). Perception-side
   availability: A37082, A37479.
6. **Agent / MCP tool-layer and multi-agent subversion.** Agent trusts third-party tool metadata
   as capability ground-truth (A40895, A40898); inter-agent message-bus tampering (A40224);
   decomposition-mirroring RAG poisoning (A40353); MARL observation perturbation (A40176).
7. **LLM/VLM safeguard-pipeline bypass.** The whole defense-in-depth stack (input+output
   classifiers, alignment, system prompt) attacked jointly: A41108, A41144, A41099.
8. **Model-IP / provenance and watermark manipulation.** Extraction-then-removal (A40905),
   overwrite/forge (A37010, A39997, A40915, A41146), machine-unlearning reversal (A37426).
9. **Strategic / game-theoretic adversaries.** Agents who game a committed policy rather than
   perturb a model (A38722 audit-mechanism design, A38730 network-formation, A38761 layered
   cyber-defense via Gittins indices).
10. **Worst-case / adaptive adversaries in the loop.** Genuinely modeled in only a handful:
    A37117 (adaptive trigger-inversion vs a model lock), A37716 (attack-agnostic certification),
    A39290 (authored adaptive defense), A38949/A38785 (learned/adaptive training adversaries).

## 4. Major attack families

- **Backdoor / trigger insertion (the single largest family).** Evolving from fixed word/patch
  triggers to clean-label (A37349, A39935, A39747), syntactic/style/dynamic (A40894 All-to-X
  distributed targets, A40897, A41080), multi-target via proxy-space partitioning (A38015),
  parameter-efficient prompt-tuning injection with no base-weight retraining (A41121), physical/3D
  triggers (A40842 LiDAR, A40855 6DoF-pose, A38056 UV-fluorescence, A37349), fine-tune-persistent
  (A40295, A40409 rationalization, A40486 CoT-overthinking, A40867), dormant-until-finetune
  (A39480, A39593, A39577), and DRL component/post-training (A39809).
- **Adversarial examples / evasion.** Universal perturbations (A37015 theory, A37442 multi-image,
  A37647 physical patch), transfer attacks (A37420, A37436, A37651, A37664, A37695, A37912,
  A38013, A38422, A38325), diffusion-generated naturalistic patches (A38095 via collaborative LLM
  agents, A38137), 3D disparity-consistent camouflage (A38320), sparse/cooperative 3D (A37903),
  false-positive *creation* ("ghost" objects, A37955), spoof-plus-fake-explanation dual attacks
  (A38340), and semantics-preserving text attacks on financial LLMs/agents (A41099).
- **Corpus / RAG poisoning.** Joint retriever+generator gradient optimization so one document
  both survives retrieval and overrides generation (A40893 Joint-GCG); decomposition-aware
  sub-claim poisoning of agentic fact-checkers (A40353).
- **Tool-metadata / MCP attacks.** Confused-deputy hijack of a legitimate high-privilege tool via
  poisoned description (A40895); advertising-style + genetic-algorithm-stealth rewrites that bias
  tool *selection* (A40898).
- **Staged / multi-facet jailbreaks against full guard stacks.** Chained per-component universal
  jailbreaks (A41108); combined reward-hacking + moderator-evasion signature + vision-encoder
  pixel-space system-prompt injection (A41144).
- **Data / graph / FL poisoning.** NP-Complete-to-measure label-flipping (A39301), deferred
  input-Hessian singularization (A39318), adversarial *missingness* that hides existing entries
  and bypasses insertion/perturbation defenses (A39428), node/edge injection (A39604, A39668),
  robust-aggregation-evading model poisoning (A38328, A39290, A40787), VFL cluster-swap (A42327).
- **Availability / resource exhaustion.** Latency-inflation on cooperative perception (A37082),
  latency-as-attacker-resource for SNNs (A37479), reasoning/output-length DoS (A40445, A40486,
  A40833).
- **Privacy / membership inference / inversion.** Iteration-count-to-craft-an-AE as a universal
  membership signal even on hard-label APIs (A40912), gradient-norm+robustness MIA (A40587),
  cross-modal image-membership from text (A40726), embedding inversion (A40876), split-LLM
  hidden-state inversion (A38853), unlearning-amplified MIA (A38134, A38576, A39725).
- **Watermark / provenance removal & model extraction.** Multi-embedding overwrite (A37010,
  A39997 near-100% overwrite ASR author-reported), extraction-then-purpose-built-remover (A40905),
  detector-free 3DGS watermark removal (A41146), unlearning reversal via relearning (A37426),
  out-of-domain surrogate of a proprietary server model (A40878).
- **Physical-signal / sensor attacks.** 8 sensor-injection attacks (laser blinding, light
  projection, EM color strip, ultrasound blur, voice DoS/spoof) on VLA robots validated on a real
  Franka arm (A40881); ~1%-area transferable patch on MLLM-AD perception (A42439).

## 5. Major defense families

- **Certified / provable robustness (rare, high-value).** CertMask (A37716) — attack-agnostic
  patch certificate at O(n) vs PatchCleanser's O(n²), up to +13.4% certified accuracy
  (author-reported), bounded by a *known* patch-size assumption. A37117 — randomized-smoothing-
  fortified model lock, ℓ2-certified within the modeled radius. NeuralMark (A40915) — SHAKE-256
  hash-as-filter with a forging-probability bound < 1/2^128 at n=256 (author-reported).
- **Adversarial / robust training.** Metric-aware ReID AT (A38392), budget-constrained non-zero-sum
  AT for humanoid control (A38949), semantic-margin + hyperspherical energy for CLIP zero-shot
  robustness (A39603), game-theoretic sample re-grouping (A39954), per-modality vulnerability-aware
  AT (A40054), cross-modal attribution-consistency regularization (A37396), edge self-adversarial
  GCL (A39085), curvature-minimizing training (proposed vs A39318).
- **Backdoor / adversarial-input detection (mostly heuristic, black-box).** Token-confidence
  sequence-lock (A40897 ConfGuard, top-1 prob only), text-perturbation semantic-consistency +
  confidence-drift (A40891), attention-head-similarity (A41080), embedding-stability probe for
  adversarial text (A39803), manifold OOD-likelihood (A40301), Mahalanobis+spectral fusion
  (A40366), density-based poisoned-sample detection during contrastive pre-training (A37141 DIFT),
  SAE + causal-feature identification for reward hacking (A40584), middle-layer gradient-norm MIA
  signal (A40587).
- **Purification / backdoor removal.** Test-time token zeroing on hijacked deep-layer attention
  (A40867 PurMM), server-side multi-teacher distillation (A40051), LoRA distillation-unlearning
  (A40366), directional-mapping + adversarial KD (A40902 BeDKD), LRP-neuron dual-network sparse
  training (A40904 CL-Guard), diffusion reconstruction-error purification (A38345 UDAP),
  MLLM-verifier patch localization + SAM masks + inpainting (A37474 SATED), RL red-mask input
  masking (A38121 SRD), attention-head alignment with no clean-twin model (A41080).
- **Inference-time model-level defense.** ASE (A41122) — CoT self-generated adversarial-scenario
  reasoning before answering, threat-agnostic, low over-refusal (single-run, no CIs, author-
  reported). APD (A37389) — β-VAE + graph-spectral prompt disentanglement firewall (preliminary).
- **Distributed-training robustness.** Semi-verified dimension-free Byzantine-robust mean
  estimation with a small trusted anchor set (A39560); topology-aware detection + GAN recovery +
  adversarial multi-teacher distillation (A40908 HealSplit); capability isolation — share only a
  low-capacity style module (A39778) or defend on observable interface artifacts (A40859).
- **Tamper-resistance / capability-gating.** AntiDote (A40570) — bi-level tamper-resistance for
  open-weight LLMs against malicious fine-tuning (10 models 0.6B–27B × 52-attack suite; up to
  27.4% more robust / 78% harmful-score reduction / <0.5% utility loss, author-reported;
  explicitly a proxy for an intractable min-max, not a guarantee). A37117 — utility gated on a
  hardware-derived credential; leaked weights degrade to near-random. ROVER (A37426) —
  request-router + gradient-sink for relearning-resistant unlearning.
- **Model-IP / provenance.** CFW (A40905) — synthetic OOD watermark class + representation-
  entanglement, resilient to extraction+removal; AIS-simulated-overwrite watermark fine-tuning
  (A37010); provenance-weighted robust-recommendation metric (A40854).
- **Privacy-preserving transformations (all empirical, no formal DP).** On-device sensor
  perturbation (A39752), client-side prompt desensitization (A40447), MI-optimized embedding
  obfuscation (A40876), pre-sharing image perturbation vs VLM geolocation (A40877), direction-
  preserving activation scaling (A38853), reversible adversarial audio (A37140 IO-RAE).
- **Architecture / mechanism design.** Evolutionary NAS with adversarial-example fitness (A42292),
  optimal audit-rate policy vs strategic misreporting (A38722), Gittins-index layered defense
  modeling an *optimal, adaptive* attacker (A38761).

## 6. Most influential concepts

- **"Capability is not permission" / "obscurity ≠ robustness."** Recurs from multiple angles:
  tool identity is not authorization (A40895); decision-only/hard-label API exposure is not a
  boundary (A38127, A40912); weight secrecy is fragile (A39997 near-100% overwrite across
  white/gray/black-box, A40878 out-of-domain surrogate); explanations/attention are not
  verification (A38340 spoofable rationale); model outputs and hidden states are capability, not
  evidence (A38853 activations invert to prompts).
- **Provenance/attestation over adaptation as the primary supply-chain control**, because
  retraining does not remove backdoors (A39809, A40295, A40855) and accuracy metrics do not reveal
  them (A39935, A40409, A40486, A40867).
- **Adaptive-attacker evaluation as the missing methodological axis** — the corpus's most
  replicated meta-finding.
- **Availability as a safety property** for hard-real-time and reasoning pipelines (A37082,
  A37479, A40445, A40486, A40833).
- **Monoculture / shared-backbone transfer risk** — perturbations crafted on shared encoders
  (CLIP) transfer to black-box commercial models (A41144, A42439); shared base between guard and
  guarded model is a weakness (A41108).
- **Loss-landscape geometry as the transferability mechanism** — flat minima (A36964), path
  flatness (A37912), manifold-tangent projection (A38013), algorithm-stability bounds (A37015).
- **The unlearning / "right-to-be-forgotten" interface as a dual-use attack surface** — leaky,
  abusable for anti-forensic revocation, and causing collateral forgetting (A39725, A39747,
  A40272, A38134).
- **Confused-deputy pattern** — MCPTox (A40895) is the concrete agent-security instantiation:
  the poisoned artifact never acts; a trusted high-privilege component does.

## 7. Common datasets and benchmarks

Reported per-card (not exhaustive; many tables truncated):

- **Vision classification:** ImageNet (A38416, A38422, A37651, A37664, A37912, A38013), CIFAR-10
  and Mini-ImageNet (A42292), MNIST / FashionMNIST / UCI-HAR (A42327 student-abstract scale).
- **Physical / driving perception:** nuScenes (A42439, digitally-patched frames), cooperative-
  perception V2V testbeds and a real vehicle (A37082), a real Franka arm (A40881).
- **Reasoning LLMs:** MATH-500 (A40486, reasoning length inflated ~17×, author-reported).
- **NLP backdoor / detection:** CQA, UC, SIQA, Shakespeare-style style-transfer (A40897 threshold
  and FPR studies).
- **VLM / MLLM:** LLaVA-1.5 (A40272, ~6–8 concepts), HighMMT (A40054 single backbone), CLIP as
  shared encoder/target across many (A39480, A39276, A39603, A41144, A42439).
- **MCP agent ecosystem:** 45 live MCP servers / 353 tools / 1348 cases / 20 agents (A40895).
- **Guard-stack / jailbreak:** ShieldGemma referenced as a baseline (A41108); 17 open+commercial
  VLMs with real moderators (A41144). Several jailbreak papers use "AdvPromptGen"/"Novel Attack"
  test sets that A37389's card flags as undescribed.

**No single standard benchmark spans the corpus.** Agent-security attacks (MCP, RAG, multi-agent,
reasoning-DoS) largely introduce their own bespoke evaluation harnesses, limiting cross-paper
comparability *(reviewer synthesis)*.

## 8. Evaluation metrics

- **Attack success rate (ASR)** — the dominant metric; definitions vary (per-target, per-sample,
  quality-thresholded transfer ASR which A38325's card notes *inflates* success).
- **Certified accuracy** and certified radius (A37716, A37117).
- **Clean-accuracy drop / benign accuracy** as the stealth check for backdoors (A39935 ≤1% drop
  at ≤0.5% poison, author-reported; A39318 defense 0.81→0.71).
- **Membership-inference metrics:** AUC (A39276 CSA 94%→51% under in-distribution eval);
  the field is criticized for omitting **TPR@low-FPR** and variance (A39449, A39276).
- **Watermarking:** bit error rate BER (A37010 0.50%→38.17%), watermark success rate WSR (A40905
  ≥88.79% reduction), forging-probability bound (A40915).
- **Availability:** latency per frame / ×-inflation (A37082 >90×, >3 s/frame), reasoning-token
  length (A40445, A40486, A40833) — flagged as a *proxy* for wall-clock energy (A40445).
- **Robustness–utility trade-off points:** PSNR/SSIM (A37010), CIDEr (A38121 up to ~15% drop),
  FDFR (A38345 MIST 0.87 vs DiffPure 0.11), authorized accuracy (A37117 86.2%→73.9%).
- **False-positive rate / over-refusal:** A40897 (up to ~21.95% on Shakespeare-style), A41122
  (low over-refusal). A37389's card flags a *missing* benign-FPR as undercutting a prompt-firewall.
- **LLM-as-judge scores** (StrongREJECT, GPT-4o/GPT-4o-mini) recur but bound reliability (see §12).

## 9. Strongest replicated findings

Ranked by cross-paper independence and evidence quality:

1. **Non-adaptive defense evaluation is the field's dominant weakness; defense-aware attackers
   degrade or defeat defenses.** Converged on by essentially every chunk — attack papers evade
   only fixed defenses, defense papers concede adaptive robustness is unproven. Highest-confidence
   meta-finding.
2. **"Hiding the signal is not a security boundary."** Decision-only APIs remain attackable with
   improving query efficiency (A38127, proved O(1/T²), 13 baselines, released code — strongest
   single-attack evidence in chunk 1); model smoothness helps query robustness but *hurts*
   transfer robustness, a proven no-free-lunch tension (A38416, LR↓ +64% transfer / LR↑ +28%
   query, mutually exclusive); ensembling heterogeneous architectures does not by itself confer
   transfer robustness (A38422). Weight secrecy is fragile (A39997, A40878).
3. **Fine-tuning / retraining does not reliably remove implanted behavior.** A40295 (clean
   fine-tuning *reinforces* a gradient-aligned backdoor; forgetting-mitigation *amplifies*
   persistence), A39809 (component re-injects after retraining), A40855 (residual pose-offset
   persists). Direct control implication: provenance/attestation, not adaptation.
4. **Backdoors preserve clean accuracy — and even plausible rationales and correct answers —
   defeating accuracy-only QA.** A39935 (≤1% drop at ≤0.5% poison), A40409 (rationale preserved),
   A40486 (answers correct while reasoning inflates ~17× on MATH-500), A40867 (clean capability
   in shallow layers). All author-reported.
5. **Aggregate-statistics FL defenses are evadable by structured attacks inside the trusted
   region.** Two independent constructions — boundary-adaptive (A38328) and subnet-concentrated
   "pill" (A39290, >90% bypass across 9 rules) — reach the same conclusion against overlapping
   defense sets (FLTrust, Multi-Krum, DnC, Median, Trimmed-Mean, etc.).
6. **Publishing a model/dataset creates a real privacy/integrity surface.** Released encoders
   leak membership even under strong generalization (A38576); open weights enable white-box MIA
   (A39276, A39449); distributed checkpoints carry dormant backdoors (A39480). *(reviewer
   synthesis across privacy + backdoor papers.)*
7. **Cross-corpus membership-inference evaluations are confounded.** A39276 shows with theory
   (Δ_N = O(T/N), slope 0.99±0.02, R²=0.997) and significance testing that prior "near-perfect"
   CLIP MIA collapses to near-chance (CSA AUC 94%→51%) under strictly in-distribution evaluation —
   a strong, well-supported methodological result.
8. **Metadata/descriptions are an injection surface as dangerous as content.** A40895 (tool
   hijack, peak 72.8% on o1-mini) and A40898 (selection bias, DPMA 100% ASR in most settings)
   independently; A40895 further shows porting content-style indirect-injection payloads (lacking
   a Trigger Condition) to the description vector yields near-0% ASR — tool poisoning is a
   *distinct* vector.
9. **Whole-pipeline adaptive attacks defeat stacked guards that pass per-component evaluation.**
   A41108 (0%→71% black-box) and A41144 (0%→58.5%) both exploit the model-repeats-a-string channel
   past the output classifier — an independently replicated concrete weakness.
10. **Shared vision backbones create systemic monoculture transfer risk.** A41144 (one image
    transfers, avg 59.58% image ASR) and A42439 (CLIP-ensemble surrogate transfers to 12
    commercial/reasoning MLLMs) independently. All author-reported.
11. **Availability is a first-class, under-defended property.** A37082 (>90× latency, 100% on a
    physical testbed under the evaluated setup) plus the reasoning-DoS trio (A40445, A40486,
    A40833).
12. **Transferable backdoors/AEs generalize across architectures via loss-landscape geometry.**
    A36964 (flat-minima triggers, 80.1% cross-dataset ASR, 73.2% post-defense, author-reported)
    and A37912 (path flatness) converge from attack and geometry sides.

## 10. Conflicting findings

- **Robustness–utility / robustness–generalization trade-off: universal but contested.** A38416
  proves a smoothness *dichotomy* (transfer- and query-robustness mutually exclusive); A39603
  argues the CLIP robustness/generalization trade-off *can* be jointly improved (contra prior
  LAAT-style expansion). Many defenses simply cost clean accuracy (A38121 up to ~15% CIDEr; A39318
  0.81→0.71; A37117 86.2%→73.9%). Several attack papers report only a single operating point.
- **Purification is contested — a layer, not a gate.** UDAP (A38345) beats DiffPure/GridPure on
  most attacks but fails catastrophically on MIST (FDFR 0.87 vs 0.11) — its own table contradicts
  the "robust to diverse attacks" framing.
- **Protective perturbations: usability vs durability.** VCPro (A41250) concentrates perturbation
  in high-frequency/masked regions for imperceptibility; its companion A41170 shows high-frequency
  perturbations are exactly what low-pass purification removes — VCPro is not tested against
  purification, so its durability is contested by A41170.
- **Temporal redundancy: robustness or liability?** A37479 argues SNN multi-timestep structure is
  *not* inherent robustness (early-stopping/warm-up shortcuts); A37770 argues CTDG memory *dilutes*
  isolated perturbations yet still achieves ~29% avg degradation. Same property cuts both ways.
- **Capability isolation "works" vs "untested against adaptive attackers."** A39778 and A40859
  report strong ASR reduction from architectural isolation, but both flag that an attacker shaping
  the shared component / enlarging intra-cluster distance was not evaluated — claim-strength
  tension, not contradiction.
- **Unlearning as reliable removal vs leaky/abusable.** A40272 argues precise behavioral forgetting
  is achievable; A39725/A39747 argue the unlearning event itself leaks membership and can be
  abused. *(reviewer synthesis: not contradictory — different objectives — but jointly: "delete"
  is security-sensitive and behavioral non-recall is not proof of removal.)*
- **Verifier/reward signals: trustworthy vs game-able.** A40584 shows Process Reward Models assign
  high scores to logically invalid steps via stylistic confounders (an impossible constraint scored
  0.973, author-reported) — cautioning against best-of-N / judge pipelines that trust verifier
  scores.
- **DP as privacy defense: partial only.** A40846 reports DP yields only a slight ASR decrease
  against relative-metric MIA; A40587's threat is untested against DP-SGD. No paper here validates
  a strong privacy guarantee.
- **Over-manipulation backfire.** A40898 finds that in a malicious-majority tool ecosystem, several
  LLMs revert to a plain benign tool — an internal negative result the authors flag as speculative.

## 11. Defense bypasses

Explicitly demonstrated (attacks defeating named, evaluated defenses; all author-reported):

- **Backdoor detectors bypassed.** A39480's dormant backdoor evades 7 detectors (Neural Cleanse,
  STRIP, GangSweep, TND-DL/DF, CBD, CleanCLIP) because they inspect the pre-finetuning model where
  the payload is absent. A39935 (GCB) resists STRIP, Neural Cleanse, Fine-Pruning, ABL ("most, not
  all", author hedge). A36964 evades AC, Spectral Signature, ONION, KillBadCode, EliBadCode under
  cross-dataset shift. A39809 survives retraining-based defenses; InfrectroRL evades BIRD and SHINE.
  A40855 survives clean fine-tuning (honest negative: residual offset persists).
- **Robust FL aggregation bypassed.** A40787 (ShadeEdit) evades 8 aggregators (FedAvg, Multi-Krum,
  Median, Trimmed-Mean, CRFL, RFLBAT, FLAME, SFed variants) at ~99.5% avg ASR — counterfactual
  edits partly reversible by clean fine-tuning, **bias edits persist**. A39290 bypasses >90% across
  9 rules (its own authored cosine+distance adaptive defense is reported insufficient). A38328
  across hard/semi-soft/soft boundary families. A42327's in-distribution cluster-swap keeps
  detection ≤1.5% under gradient-norm clipping + AE-reconstruction while collapsing MNIST accuracy
  to ~42–46%.
- **Guard-stack / moderator bypass.** A41108 (STACK) 0%→71% black-box / 33% transfer, incl.
  inducing the model to repeat an output-classifier jailbreak string. A41144 (MFA) 58.5% overall /
  52.8% commercial / 72.92% with all three facets, replicating the output-repetition channel.
  A40224 (MAST) evades a three-criteria LLM "Tamper Defender" via similarity constraints.
- **Agentic-RAG defenses bypassed.** A40353 (Fact2Fiction) evades paraphrasing, K-means clustering
  detection, and perplexity filtering.
- **Verifier / gate evasion.** A37118 (HogVul) raises false-negative rate of LM vulnerability
  detectors (26.05% avg ASR gain) — confused-deputy risk if an agent trusts the gate.
- **Watermark / provenance removal.** A40905's WRK reduces prior black-box watermarks' WSR by
  ≥88.79%; A41146 removes 3DGS marks without ever seeing the detector; A37010 shows MBRS/HiDDeN
  offer ~no protection against a single re-embedding (BER 0.50%→38.17%, several ≈ random); A39997
  near-100% overwrite across white/gray/black-box.
- **Protective-cloak purification.** A41170 shows DiffPure/GrIDPure + bilateral/guided filtering
  defeat Anti-DreamBooth, HF-ADB, SimAC, DisDiff — by extension threatening A41250 and the A41404
  class.
- **Classical poisoning defenses inapplicable.** A39428 (adversarial missingness) — nothing is
  inserted/perturbed, so sanitization/outlier detection do not trigger; even MICE (most robust
  imputer) still failed on two datasets.
- **Explanation-based oversight spoofable.** A38340 (A-SAGE) steers attention/LRP maps to a
  coherent-but-false rationale, defeating explanation-based human review.
- **Reasoning-purification brittle.** A40833 argues pattern-matching purification and perplexity
  filtering are brittle (conceptual, not a full defender-vs-attacker study).

**Candid adaptive-attack treatments (the methodological gold standard here):** A37117 honestly
reports its naive design is broken by an adaptive trigger-inversion attacker, then fortifies with
randomized smoothing (reversed-accuracy 9.25% ≈ clean 9.47%). A40905/A40915 *build* purpose-built
adaptive removers/forgers rather than testing only against standard defenses.

## 12. Known benchmark limitations

- **Non-adaptive attack suites dominate** — the single most common gap, present in the large
  majority of both attack and defense papers across all four chunks. Exceptions: A37117, A37716,
  A39290 (authored adaptive defense), A38949/A38785 (learned adversaries).
- **Truncated result tables.** Many cards flag that headline tables were partly truncated in the
  extracted PDFs; magnitudes are author-reported, not fully transcribed (non-exhaustive: A36961,
  A36964, A37119, A37442, A37647, A37716, A38015, A38095, A38328, A38853, A39290, A39301, A39428,
  A39500, A39560, A39577, A39593, A39603, A39604, A39668, A40176, A40224, A40295, A40301, A40584,
  A40587, A40846, A40854, A40878, A40881, A40894, A40904, A40908, A41080, A41121, A41146, A41170,
  A41250).
- **LLM-as-judge dependence.** A41108 (StrongREJECT), A41144, A42439 (GPT-4o, no inter-judge/human
  agreement reported), A40898 (LLM-as-judge stealth), A37420 (GPT-4o-mini, bias unaudited), A37116
  (unspecified promptable LLM backend) — judge calibration bounds reliability.
- **Narrow scope / small scale.** Vision-classifier/single-backbone/single-dataset is common
  (A38416/A38422 ImageNet-only; A39318 CNN-only; A39480 CLIP-only; A38949 single robot; A40054
  single HighMMT; A40272 single LLaVA-1.5 + ~6–8 concepts; A40587 capped at 6B; A39997 3 systems /
  speech). Student abstracts use toy datasets (A42327, A42292, A42217 synthetic).
- **Imperceptibility asserted, not measured.** Multiple papers assert ℓ∞/perceptual stealth with
  no human study, LPIPS/SSIM, or ε disclosed (A36961, A37388, A37420, A37442, A37647); A37664 uses
  a visible ε=32/255 yet frames it as an AE.
- **Physical realizability asserted, measured digitally.** A42439 ("physically realizable" but
  evaluated on digitally-patched nuScenes frames), A41121 (physical-sticker motivation, digital
  eval), A37479/A37955/A38056 argued by citation/summary. A40881 does validate on a real Franka arm
  but on limited tasks.
- **Proxy metrics.** Output length as an energy/latency proxy without wall-clock energy (A40445);
  behavioral non-recall as an unlearning proxy without MIA/relearning audits (A40272); MIA papers
  omitting TPR@low-FPR and variance (A39449).
- **Commercial-model version drift** makes results snapshot-dependent (A40445, A40726, A40833,
  A40877).
- **Single-run / no variance** (A41122 explicitly no repeated runs due to API cost; A42292, A42327
  no CIs/seeds).
- **No defense proposed in many attack papers** → residual risk after mitigation unknown (A40893,
  A40895, A40898, A40912, A41099, A41121, A41144, A41146, A41164, A42327).
- **Internal contradictions in "black-box" claims.** A37388 claims black-box but needs logits and
  text-embedding-space gradients; A37651/A37664/A37695/A38015 are "black-box on the victim" but
  white/gray on a surrogate or public encoder. Treat headline "black-box" labels skeptically.

## 13. Implementation patterns

Method-level patterns recurring across the corpus:

- **Surrogate-then-transfer offline construction** (no victim queries) — the default black-box
  recipe (A37420, A37436, A37651, A37664, A37695, A37912, A38013, A40176, A40849, A40877, A40878,
  A39997, A41144, A42439). Exception: A39604 deliberately avoids surrogates (gradient-free
  evolutionary search on non-differentiable LLM features).
- **GCG / multi-token discrete gradient optimization lineage** — shared across A40893, A40295,
  A40445, A41099, A41108, A41144 (A41099 relaxes to a continuous simplex + T5 for fluency; A41144
  reports 3–5× speedup over GCG).
- **Bi-level / simulate-the-victim optimization with a differentiable proxy** — A40570 (adversarial
  hypernetwork generating LoRA attack patches), A39480 (simulate future finetuning), A39747
  (inject↔unlearn with PCGrad), A39668 (teacher/student distillation), A39290 (pill/subnet
  inner-outer), A38392/A38949/A39085 (inner attack / outer robust).
- **Diffusion models as the attacker's generative prior** (A38095, A38137, A38325) and as the
  defensive inverse (A38345, A37474).
- **LoRA-based injection or purification** — parameter-efficient for both sides (A40272, A40366,
  A40570, A40787, A40867, A41121).
- **Representation/attention-level analysis as the detection signal** — A39803 (masking-induced
  embedding sensitivity), A40301 (manifold OOD), A40366 (Mahalanobis+spectral), A40867 (hierarchical
  attention hijacking), A40584 (SAE features), A40587 (middle-layer gradient norms), A40891/A40897
  (confidence stability / token-confidence run), A41080 (attention-head cosine similarity, e.g.
  BadNets 0.9921 vs 0.9149).
- **Perturb-and-compare behavioral-signature detection** needing only I/O or top-1 probabilities
  (A40891, A40897) — deployable client-side against untrusted providers.
- **Attribution-guided surgical purification** (neuron/head-level rather than layer
  reinitialization) using a small trusted clean set as a security asset (A40902, A40904, A41080).
- **Small trusted anchor set** to defeat majority-adversary settings (A39560; FLTrust-style root
  data across FL papers).
- **Foundation-model-as-component** — as verifier (A37474), risk scorer (A37116), decoy-text
  generator (A37140), payload/description generator (A40895, A40898), patch placer (A42439),
  victim profiler (A41164). Each *inherits the component's own attack surface* (prompt injection,
  hallucination) — flagged explicitly in A37474.
- **Detect-then-repair (self-healing) rather than reject-only** (A40908 GAN recovery, A40902
  punish-distillation).
- **Multi-round planning for stealthy agentic attacks** — A40224 (MCTS → step-level DPO), A40353
  (Planner/Executor mirroring the victim).
- **Cryptographic entanglement of mark and parameters** for provenance (A40915 hash-as-filter,
  A40905 representation-entanglement metric).
- **Optimization-geometry exploitation** — flat minima (A36964), path flatness (A37912),
  manifold-tangent projection (A38013), algorithm-stability bounds (A37015).

## 14. Product design implications

For a Guardian-Agent / autonomy-trace-console product *(reviewer synthesis, grounded in cards)*:

- **Bind actions to verified user intent, not to tool identity.** A40895's confused-deputy result
  means permission models keyed to "which tool ran" are bypassable. Add a pre-execution gate that
  verifies each planned tool call against the original request; require human approval for
  credential-reading actions (e.g., SSH keys) regardless of requester.
- **Treat all tool metadata and inbound text/images as untrusted input.** Tool descriptions
  (A40895/A40898), RAG corpora (A40893/A40353), financial news / social text (A41099/A41164),
  camera images (A42439/A40881) are attacker-influenceable; fluent/expert/persuasive surface is
  not evidence of benignity.
- **Do not rely on model-level safety alignment or a single guard family.** A40895 (<3% refusal
  even on Claude-3.7-Sonnet), A41108 (shared base between guard and guarded model is a weakness),
  A41144 (cross-moderator transfer) argue for independent, non-monoculture, whole-pipeline
  enforcement — and break the verbatim-echo channel that smuggles strings past output classifiers.
- **Monitor the right signal, not output accuracy.** Backdoors preserve accuracy and rationales
  (A39935, A40409, A40486, A40867); DoS preserves correctness while inflating reasoning tokens
  (A40445, A40486, A40833). Instrument per-request output-length/entropy and reasoning-token
  telemetry, deep-layer attention concentration, Mahalanobis/manifold scores, and confidence-run
  events — not just pass/fail.
- **Treat model outputs, explanations, and hidden states as capability, not verification.** A38340
  (spoofable explanations) and A38853 (invertible activations) support gating oversight on
  independent, cross-checked, tamper-evident evidence.
- **The "delete/forget" capability is security-sensitive.** Retain forensic snapshots *before*
  honoring unlearning/delete requests (A39747); behavioral non-recall is not proof of removal
  (A40272); the unlearning event can leak membership (A39725).
- **Availability/timeliness is a defended SLA, not an assumption.** Bound worst-case per-message
  compute, isolate per-sender cost in multi-agent fusion, and enforce reasoning-token ceilings
  independent of prompt-controlled instructions (A37082, A40445, A40486, A40833).

## 15. Architecture implications

- **Provenance & attestation as the primary supply-chain control.** Retraining/fine-tuning does not
  remove backdoors (A39809, A40295, A40855) and accuracy does not reveal them; require
  crypto-provenance/attestation for weights, reused components, datasets, labels, and retrieval
  corpora, and add *post-finetuning* red-teaming to model onboarding (dormant backdoors are invisible
  pre-finetuning — A39480, A39593, A39318). Scan for *multiple coexisting* backdoors, not one (A38015).
- **Authenticated, integrity-checked agent-to-agent channels.** A40224's MITM premise is directly
  negated by message signing / mutual auth; content-only trust on an inter-agent bus is unsafe.
- **Retrieval-corpus trust scoring, provenance, and isolation for RAG.** Treat open-web KBs as
  attacker-writable (A40353, A40726, A40876); minimize/sanitize exposed justifications
  (transparency–security trade-off, A40353); sanitize retrieved context *before* it enters a
  reasoning model (indirect-injection DoS, A40833).
- **Isolate trust domains before joint attention.** A37442 shows one poisoned image corrupts
  co-presented clean images (order-invariant) — per-image sanitization is insufficient for agents
  doing RAG/browsing over image galleries.
- **Cross-sensor / cross-source corroboration for perception-driven actuation.** A42439, A40881,
  A38095, A38137, A38320 show single-modality perception is evadable (even by natural-looking or
  disparity-consistent physical artifacts); require multi-sensor voting, sensor-health monitoring,
  and confidence-plus-consistency (not confidence-alone) gating before a safety-critical action gate.
- **Defense-in-depth over single filters, with identity/source caps.** FL aggregation (A38328,
  A39290), purification (A38345 MIST failure), and imputation (A39428 MICE failure) each show a
  single filter is bypassable — pair with client authentication, source-influence caps, query
  monitoring, and runtime drift detection. Bound any single party's influence rather than relying on
  server-model secrecy (A40878).
- **Capability-gating enforced in weights / least privilege.** A37117 gates utility on a
  hardware-derived credential with a certified robustness layer (leaked weights → near-random);
  A39778/A40859 share only low-capacity modules — concrete blast-radius-limitation patterns.
- **API hygiene.** Hide confidence/logits where possible (A38127, A38095), rate-limit and monitor
  query trajectories (A38127, A38416, A40587, A40726, A40846, A39997 against try-and-test loops),
  and log split-point/randomization state for activation transmission (A38853).
- **Cryptographic, out-of-band provenance over in-artifact marks.** Removable marks fail (A41146,
  A41170, A40905); pair artifact watermarking with signed manifests / registry attestation and
  access control.

## 16. Launch and assurance implications

- **Require adaptive, defense-aware red-teaming before shipping any defense.** The corpus's central
  lesson: non-adaptive evaluation systematically overstates security. Treat any "robust against SOTA
  defenses" claim as *non-adaptive* unless the paper built a purpose-built adaptive attacker (the
  A40905/A40915/A37117 bar).
- **Do not present empirical robustness as a guarantee.** Only CertMask (A37716) and the smoothing/
  hash bounds (A37117, A40915) offer formal guarantees, each within a *narrow* threat model
  (known-single-patch-size, ℓ2-radius, single embedding round). AntiDote (A40570) is explicitly
  framed as risk-reduction, not proof. No privacy defense here offers a formal DP guarantee — all
  are empirical (A39752, A40447, A40876, A40877, A38853) and require production validation.
- **Supply-chain sanitization gate before promoting third-party artifacts.** Attention-similarity /
  neuron-attribution screening (A41080, A40904), re-distillation on a small clean set (A40902), and
  adapter/prompt-tuning provenance checks (A41121) before promoting third-party checkpoints/adapters
  — and post-finetuning screening because pre-finetuning inspection is blind (A39480).
- **Evidence-logging / rollback as the incident story for every poisoning class.** Log training-data/
  dataset/backbone provenance and hashes so a discovered backdoor is traceable and a clean checkpoint
  is restorable.
- **Runtime telemetry candidates for the autonomy-trace console** (each from a card): token-confidence-
  run events (A40897), attention-head-similarity stats (A41080), per-component block decisions +
  "repeat this string" / universal-suffix patterns (A41108/A41144), tool-selection decisions with the
  descriptions that drove them (A40898), full inter-agent transcripts with per-message provenance
  (A40224), retrieval-evidence provenance + injection-cluster patterns (A40353), reasoning-token
  telemetry for DoS (A40445/A40486/A40833), and the image regions that drove a perception output
  (A42439).
- **Dual-use / governance exposure.** Released offensive toolkits and datasets (A41164 AR social
  engineering; A40895/A40898 MCP attacks) are a governance open problem for anyone publishing agent
  red-team tooling.

## 17. Open research problems

- **Adaptive-attacker robustness** for essentially every defense here — the largest evidence gap;
  residual risk is unknown for every defense in the corpus.
- **Certification beyond narrow threat models** — unknown/multiple patch sizes (A37716), non-ℓ2
  triggers (A37117), multi-round embeddings (A37010); no defense offers certified robustness against
  an **unbounded** adaptive adversary — one permitted to exceed the certified threat model (larger radius,
  a different norm, or a different surface). Within its stated bound, certification *is* a worst-case,
  attack-agnostic guarantee (e.g. CertMask/A37117); the open problem is guarantees beyond that bound.
- **Formal privacy guarantees** — most privacy defenses are heuristic (A38853 Rouge thresholds, A39500
  no DP guarantee); where DP exists (A39382) it is asserted via budget without empirical attack testing.
- **Detection of dormant / process-activated backdoors and omission-based poisoning** — no effective
  in-corpus defense (A39480, A39593, A39428).
- **Verifiable unlearning** — behavioral non-recall is not proof of removal; relearning/extraction
  audits are absent (A40272) while the unlearning interface is simultaneously leaky and abusable
  (A39725, A39747).
- **Loss-landscape-geometry-aware defenses** against transferable/flat-minima backdoors and AEs
  (A36964's own call, echoed by A37912/A38013).
- **Multimodal / generative-LLM robustness with defined metrics and benign-FPR budgets** (A37388/A37389
  gaps); robustness does not compose from single-modality robustness (A37388, A37396, A37436, A37442).
- **Whole-pipeline mitigation of staged / repetition-channel guard bypasses** — A41108 and A41144
  recommend but do not build/validate fixes; reward designs that *separate* helpfulness and safety to
  close the reward-hacking jailbreak pathway (A41144).
- **Verifier / reward-model robustness** and its interaction with agentic best-of-N / judge pipelines
  (A40584).
- **Runtime detection/containment of physical attacks** on VLA/AD stacks (A40881 provides only
  training-time hardening; A42439/A42145 provide no deployed mitigation); true over-the-air physical
  realizability remains under-demonstrated (A40842, A40855, A40867).
- **Purification-robust, imperceptible protective perturbations** remain unsolved (A41170 open;
  A41250 untested against purification).
- **Standardized, adaptive benchmarks** for multi-target/All-to-All backdoors (A40894), automated
  adaptive tool-poisoning payloads (A40895), VFL/SFL semantic cross-view consistency (A42327, A40908),
  and distilled-dataset / condensed-artifact integrity as a new axis (A37119, A37349).
- **Scaling to frontier-scale and genuinely black-box production models** (A40587, A40570); transfer to
  LLM/agent stacks is mostly by analogy — agentic prompt/tool/skill-injection is under-represented in
  chunks 0–1.

## 18. Recommended foundational papers

Best evidence quality, reproducibility, or reusable formal/methodological contribution
(read for the underlying principle):

- **A38127** — hard-label query-efficient attack with proved O(1/T²) convergence, 13 baselines,
  released code; the anchor for "decision-only exposure is not a boundary."
- **A39276** — how to audit foundation-model membership-inference honestly (distribution-matched
  probes, TPR@low-FPR, significance testing); debunks cross-corpus MIA inflation with strong theory.
- **A37716 (CertMask)** — the corpus's cleanest `strong` defense: attack-agnostic O(n) certified
  patch robustness with formal necessary/sufficient coverage conditions (bounded by known patch size).
- **A37082 (CP-FREEZER)** — strongest-evidence attack: physical-testbed availability/latency threat
  for collaborative pipelines; shows integrity defenses fail when detection outputs never arrive.
- **A38416** — the proven smoothness dichotomy (transfer- vs query-robustness mutually exclusive);
  the canonical "no free lunch" reference for API-hardening decisions.
- **A38345 (UDAP)** — best "verify-by-reconstruction" example *and* an honest failure mode (MIST),
  establishing purification as a layer, never a trusted gate.
- **A38340 (A-SAGE)** — sharpest support for "capability output ≠ verification" in oversight design
  (explanations/attention are manipulable evidence).
- **A40905 (CFW/WRK)** — sets the methodological bar of building a purpose-built adaptive remover;
  exposes the non-adaptive-evaluation weakness pervading the corpus.

## 19. Recommended frontier papers

Highest agent/LLM-runtime relevance for a Guardian-Agent stack (read for the concrete threat):

- **A40895 (MCPTox)** — largest-scale evidence (45 live MCP servers, 353 tools, 1348 cases, 20
  agents) that tool-description poisoning is a distinct confused-deputy vector defeating permission
  models and alignment. Anchors "verify intent, capability ≠ permission."
- **A41108 (STACK)** — rigorous, taxonomized demonstration that per-component-robust guard stacks
  collapse under staged adaptive attacks (0%→71% black-box); released code; sets the guard-stack
  evaluation standard.
- **A41144 (MFA)** — 17 open+commercial VLMs, real moderators; alignment + system prompt + I/O
  moderation are *jointly* bypassable; independently replicates A41108's output-repetition channel
  plus the monoculture-transfer finding.
- **A40353 (Fact2Fiction)** — black-box, decomposition-aware poisoning of agentic fact-checking/RAG
  effective at ~0.1% poison; establishes that agentic decomposition is not self-protective.
- **A40295 (P-Trojan)** — pre-release LLM backdoor engineered so ordinary clean fine-tuning
  *reinforces* it (theory + >99% persistence, author-reported); the core supply-chain safety-bypass
  result.
- **A40224 (MAST)** — reframes the inter-agent message bus as a first-class MITM attack surface
  (MCTS+DPO stealth planning); motivates authenticated agent-to-agent channels.
- **A40570 (AntiDote)** — the strongest agent-relevant *defense*: tamper-resistance for open-weight
  LLMs (10 models 0.6B–27B × 52-attack suite); calibrated as reduction, not proof.
- **A40833 (ExtendAttack)** — black-box reasoning-DoS on o3 that preserves answer accuracy via
  indirect prompt injection; the clean DoS × injection intersection for LRM serving.
- **A40867 (PurMM)** — deployable no-retraining test-time MLLM backdoor purification grounded in a
  hierarchical deep-layer attention-hijacking mechanism; a runtime-enforcement primitive.
- **A42439 (PhysPatch)** — transferable ~1%-area patch steering 12 commercial/reasoning MLLM-AD
  stacks; grounds cross-sensor-verification and untrusted-perception requirements for physical AI.
- **A41170 (Fragile by Design)** — load-bearing cautionary result: a whole class of protective-
  perturbation privacy defenses fails under trivial purification; forces purification-aware
  evaluation and provenance-over-cloak design.

## 20. Source map (paper id → one-line relevance)

Author-reported; "insufficient/off-topic" = mislabeled or non-ML-security, do not cite as robustness
evidence.

- **A36961** — poison-only black-box audio speaker-recognition backdoor (truncated tables).
- **A36964** — flat-minima code-model backdoor transferring cross-dataset (80.1% ASR); geometry insight.
- **A36999** — hypergraph pivotality poisoning (backdoor transferability sub-theme).
- **A37010** — multi-embedding overwrite defeats forensic watermarks (BER 0.50%→38.17%); AIS defense.
- **A37015** — universal-adversarial-perturbation theory via algorithm-stability bounds.
- **A37082 (CP-FREEZER)** — availability/latency attack, >90× inflation on a physical CP testbed; `strong`.
- **A37116** — attacker-centric LLM-assisted OSS/CI supply-chain risk scoring; agent-tooling transferable.
- **A37117 (Authority Backdoor)** — capability-gated-in-weights + certified robustness; cleanest adaptive-attack methodology.
- **A37118 (HogVul)** — evades LM vulnerability detectors (26.05% ASR gain); verifier-gaming lesson.
- **A37119** — dataset-distillation as a sub-minute, model-agnostic poisoning primitive.
- **A37140 (IO-RAE)** — reversible adversarial audio for privacy (empirical, no guarantee).
- **A37141 (DIFT)** — density-based poisoned-sample detection during contrastive pre-training.
- **A37272** — cross-view geo-localization; GAN-adversarial training, no threat model — insufficient.
- **A37318** — video-diffusion distillation; adversarial = training technique — insufficient.
- **A37349** — clean-label physical backdoor via dataset distillation (gray-box).
- **A37388** — multimodal cross-modal-synergy attack; "black-box" claim internally contradicted.
- **A37389 (APD)** — β-VAE + graph-spectral prompt-injection firewall; preliminary (no benign-FPR).
- **A37396 (CBA-FAPT)** — cross-modal internal-attribution-consistency adversarial training.
- **A37420** — VLM transfer evasion (GPT-4o-mini judge, bias unaudited; 2-dataset scope).
- **A37426 (ROVER)** — relearning reverses machine-unlearning; gradient-sink defense.
- **A37436** — video-MLLM transfer attack via asymmetric PCGrad gradient projection.
- **A37442 (LAMP)** — one poisoned image corrupts co-presented clean images in multi-image MLLMs.
- **A37474 (SATED)** — training-free MLLM-verifier patch localization; flags inherited verifier attack surface.
- **A37479** — SNN latency-aware attack; argues temporal redundancy is not inherent robustness.
- **A37488** — diffusion sampling guidance; adversarial = training technique — insufficient.
- **A37615 (OTI)** — model-free dual-use image-attackability diagnostic.
- **A37647** — physical query-only printable patch on deployed LVLMs (strict black-box).
- **A37651** — targeted transfer attack (image-classification-only, surrogate-reliant).
- **A37664** — continual-learning-durable AEs via frozen CLIP; ε=32/255 (visible).
- **A37695** — video-foundation-model transfer attack (truncated tables).
- **A37716 (CertMask)** — attack-agnostic O(n) certified patch defense; `strong` (known patch size).
- **A37770** — temporal-graph link-prediction poisoning; CTDG memory dilutes perturbations (~29% degradation).
- **A37792** — camera-glass fracture as OOD/robustness stressor (no true adversary).
- **A37903** — sparse cooperative 3D point-cloud attack (Schur-complement convexity test).
- **A37912** — path-flatness transferable image attack (geometry mechanism).
- **A37955** — physical false-positive "ghost vehicle" creation on 3D detection.
- **A37967** — fair multi-view clustering; adversarial = training technique — insufficient.
- **A38013** — transferable image attack via manifold-tangent projection.
- **A38015 (MTAttack)** — multi-target LVLM instruction-tuning backdoor via proxy-space partitioning.
- **A38056** — UV-fluorescence conditionally-visible traffic-sign backdoor (no persistent artifact).
- **A38095** — diffusion naturalistic patches via collaborative LLM agents (physical, truncated tables).
- **A38121 (SRD)** — RL red-mask input masking to break VLM backdoor attention coupling (~15% CIDEr cost).
- **A38127** — hard-label query-efficient ℓ2 attack, proved O(1/T²), released code; strongest chunk-1 evidence.
- **A38134** — dual-view unlearning-verification amplifies membership leakage.
- **A38137 (Diff-NAT)** — diffusion naturalistic physical patch.
- **A38320** — 3D disparity-consistent physical camouflage vs stereo depth.
- **A38325 (ObjectAdv)** — object-localized unrestricted UAEs (quality-thresholded ASR inflation caveat).
- **A38328** — boundary-adaptive FL model poisoning inside robust-aggregation trust region.
- **A38340 (A-SAGE)** — spoofs a ViT and forges a coherent-but-false explanation.
- **A38345 (UDAP)** — DDIM reconstruction-error poison purification; honest MIST failure (FDFR 0.87).
- **A38392 (DDDefense)** — metric-aware bi-adversarial self-meta AT for ReID.
- **A38416** — proven transfer-vs-query smoothness dichotomy (LR↓ +64% / LR↑ +28%).
- **A38422 (NAMEA)** — ensemble CNN↔ViT transfer; ensembling alone doesn't confer transfer robustness.
- **A38469** — recommendation with adversarial/GAN machinery — insufficient/off-topic.
- **A38489** — recommendation with adversarial/GAN machinery — insufficient/off-topic.
- **A38515** — image compression, adversarial = technique — insufficient/off-topic.
- **A38576** — unlearning-amplified MIA on graph pretrained encoders.
- **A38659 (DRFGD)** — disentangle-and-discard adversarial-vulnerable features in cross-modal hashing.
- **A38722** — committed audit-rate policy → truthful equilibrium; strategic-agent mechanism design.
- **A38730** — robust network-formation game (strategic adversary).
- **A38761** — Gittins-index layered cyber-defense modeling an optimal, adaptive attacker.
- **A38785** — adversarial-RL self-play for error diagnosis — insufficient/off-topic (constructive).
- **A38853** — split-LLM hidden-state inversion recovering prompts; direction-preserving scaling defense.
- **A38949 (SA2RT)** — budget-constrained non-zero-sum AT for humanoid control (learned adversary).
- **A39085** — edge self-adversarial graph contrastive-learning augmentation.
- **A39276** — rethinking CLIP MIA; cross-corpus inflation collapses to chance under in-distribution eval.
- **A39290 (Pill)** — subnet-concentrated FL poison bypasses >90% across 9 rules; authored defense insufficient.
- **A39301** — targeted label-flipping; minimum flip-count NP-Complete; linear-only theory.
- **A39318** — deferred poisoning via input-Hessian singularization (clean accuracy intact).
- **A39336** — VLM hallucination mitigation, adversarial = technique — insufficient/off-topic.
- **A39382** — DP-SGD synthetic data; adversarial = GAN — peripheral (DP asserted, not attack-tested).
- **A39428** — adversarial *missingness* bypasses insertion/perturbation defenses (MICE still fails).
- **A39438** — continual-learning concept separation via PGD — insufficient/off-topic (constructive).
- **A39449** — distillation-reference-model MIA on LLM recommenders (omits TPR@low-FPR).
- **A39480 (Dormant Backdoor)** — finetuning-activated CLIP backdoor bypassing 7 detectors.
- **A39500** — federated attribute/gradient leakage; dual-stochastic-VAE unlearning defense (no DP).
- **A39560** — semi-verified dimension-free Byzantine-robust mean estimation (trusted anchor set).
- **A39577** — temporally-decoupled time-series forecasting backdoor (single target).
- **A39593** — pretraining-time label-free persistent graph-foundation-model backdoor.
- **A39603 (TIMA)** — semantic-margin + hyperspherical-energy CLIP zero-shot robustness (contests trade-off).
- **A39604** — gradient-free evolutionary node-injection on LLM-enhanced GNNs (surrogate-free).
- **A39668 (MetaDist)** — graph edge-perturbation poisoning transferring vs robust GNNs (non-adaptive).
- **A39725** — unlearning-induced MIA + reconstruction (retaliation via leakage).
- **A39747** — anti-forensic backdoor revocation via unlearning (inject↔unlearn PCGrad).
- **A39752** — real-time on-device sensor perturbation for privacy (empirical).
- **A39778** — FL backdoor under domain skew; share-only-low-capacity-module isolation defense.
- **A39803** — embedding-stability probe for adversarial text (adaptive robustness unproven).
- **A39809 (TrojanentRL/InfrectroRL)** — DRL component/post-training backdoor surviving retraining; evades BIRD/SHINE.
- **A39935 (GCB)** — clean-label backdoor ≤1% acc drop at ≤0.5% poison; resists STRIP/NC/Fine-Pruning/ABL.
- **A39954 (AT-Field)** — game-theoretic sample-re-grouping AT (single ResNet-18, marginal AutoAttack deltas).
- **A39997** — neural-audio watermark overwrite; near-100% overwrite across white/gray/black-box.
- **A40051** — server-side multi-teacher distillation vs federated graph backdoor.
- **A40054 (VARMAT)** — per-modality vulnerability-aware AT (single HighMMT backbone).
- **A40176** — MARL observation-perturbation adaptive single-agent-selection attack.
- **A40224 (MAST)** — inter-agent message-bus MITM tampering (MCTS+DPO); evades LLM Tamper Defender.
- **A40272 (AUVIC)** — adversarial unlearning of a visual concept; collateral forgetting (single LLaVA-1.5).
- **A40295 (P-Trojan)** — pre-release LLM backdoor reinforced by clean fine-tuning (>99% persistence).
- **A40301** — embedding-manifold OOD detect-and-correct for adversarial inputs.
- **A40353 (Fact2Fiction)** — decomposition-aware agentic-RAG poisoning at ~0.1% poison; `strong`.
- **A40366** — Mahalanobis+spectral detector + LoRA distillation-unlearning purification.
- **A40409** — rationalization-model backdoor preserving interpretable rationale.
- **A40445** — repetitive-generation reasoning-DoS (output length as energy proxy).
- **A40447** — client-side prompt desensitization (GCG-lineage; empirical).
- **A40486** — triggered CoT-overthinking backdoor; answers correct, reasoning ~17× on MATH-500.
- **A40570 (AntiDote)** — open-weight LLM tamper-resistance (10 models × 52 attacks); reduction not proof.
- **A40584** — Process Reward Models score invalid steps high (0.973); SAE causal-feature defense.
- **A40587 (OR-MIA)** — white-box gradient-norm+robustness MIA (capped 6B; untested vs DP-SGD).
- **A40726** — black-box cross-modal image-membership inference on multimodal RAG.
- **A40787 (ShadeEdit)** — federated knowledge-edit evading 8 aggregators (~99.5% ASR); bias edits persist.
- **A40833 (ExtendAttack)** — black-box reasoning-DoS on o3 via indirect prompt injection; preserves accuracy.
- **A40842** — physical LiDAR-trigger backdoor.
- **A40846** — relative-metric MIA on hybrid recommenders (DP only slight ASR decrease).
- **A40849** — audio ASR/ASV/KWS transfer-evasion booster (multi-shuffle gradient fusion).
- **A40854** — provenance-weighted robust-recommendation metric vs citation shilling.
- **A40855 (6DAttack)** — 6DoF-pose backdoor surviving clean fine-tuning (residual offset persists).
- **A40859** — vertical-FL backdoor with label knowledge; interface-artifact-only defense.
- **A40867 (PurMM)** — test-time MLLM backdoor purification via deep-layer attention-hijacking finding.
- **A40876** — RAG embedding inversion (up to ~5% tokens recoverable); MI-optimized obfuscation defense.
- **A40877** — pre-sharing image perturbation vs VLM geolocation (empirical).
- **A40878 (GVFL)** — out-of-domain surrogate of a proprietary graph-VFL server model; reward gaming.
- **A40881 (Phantom Menace)** — 8 sensor-injection attacks on VLA robots; real Franka-arm validation.
- **A40891 (Trap-on-Text)** — text-perturbation semantic-consistency + confidence-drift MLLM backdoor detection.
- **A40893 (Joint-GCG)** — joint retriever+generator RAG poisoning (one document survives + overrides).
- **A40894 (A2X)** — All-to-X distributed-target backdoor mimicking natural error (non-adaptive defenses).
- **A40895 (MCPTox)** — tool-description poisoning confused-deputy vector; peak 72.8% on o1-mini; `strong`.
- **A40897 (ConfGuard)** — token-confidence sequence-lock backdoor detection (dataset-dependent FPR up to ~21.95%).
- **A40898 (MPMA)** — persuasive tool-metadata biases selection (DPMA 100% ASR); over-manipulation backfire.
- **A40902 (BeDKD)** — directional-mapping + adversarial-KD NLP backdoor removal (small clean set).
- **A40904 (CL-Guard)** — LRP-neuron dual-network sparse training backdoor purification.
- **A40905 (CFW/WRK)** — extraction-then-removal watermark threat + purpose-built adaptive remover.
- **A40908 (HealSplit)** — topology-aware detection + GAN recovery for split-federated poisoning.
- **A40912 (IMIA)** — iteration-count-to-craft-an-AE as universal membership signal (hard-label APIs).
- **A40915 (NeuralMark)** — SHAKE-256 hash-as-filter watermark, forging bound < 1/2^128 at n=256.
- **A40964** — dominance pruning in adversarial FOND planning — off-topic (not ML-security).
- **A41080** — attention-head-similarity backdoor detection, trigger-agnostic, no clean twin (BadNets 0.9921 vs 0.9149).
- **A41099 (ChameleonAttack)** — semantics-preserving text attack on financial LLMs/agents (continuous relaxation + T5).
- **A41108 (STACK)** — staged whole-pipeline guard-stack bypass (0%→71% black-box); released code.
- **A41121** — open-vocabulary-detector backdoor via prompt tuning only (physical motivation, digital eval).
- **A41122 (ASE)** — inference-time CoT adversarial-scenario reasoning defense (single-run, no CIs).
- **A41141** — CAPTCHA attacker↔defender co-evolution (benchmark open problem).
- **A41144 (MFA)** — multi-facet jailbreak of 17 VLMs (58.5% ASR); replicates output-repetition channel.
- **A41146** — detector-free 3DGS watermark removal via feature-variance flattening + evolutionary pruning.
- **A41164 (SEAR)** — AR + multimodal-LLM social engineering (dual-use governance concern).
- **A41170 (Fragile by Design)** — anti-personalization cloaks fail under purification; critiques A41250/A41404.
- **A41213 (ALERT)** — clinical-NLP with adversarial regularizer — off-topic (no attacker).
- **A41250 (VCPro)** — mask-localized frequency-domain protective perturbation (untested vs purification).
- **A41404** — face-recognition "artificial immune system" purification — abstract reprint, unverifiable.
- **A42145** — RL falsification of AV control loops — doctoral-consortium abstract, preliminary.
- **A42217** — feature compression as the root cause of adversarial fragility (synthetic).
- **A42292 (ResNet-GA)** — evolutionary NAS over residual-block widths with adversarial-example fitness.
- **A42327** — in-distribution VFL embedding cluster-swap evading numeric-anomaly detectors (≤1.5% detection).
- **A42439 (PhysPatch)** — transferable ~1%-area patch on 12 commercial/reasoning MLLM-AD stacks; physical-perception anchor.

---
*Evidence-integrity closing note:* Every metric above is reported as it appears in the corresponding
research card, labeled author-reported where the card so labels it; several headline numbers sit in
table regions marked truncated in the extracted text and are therefore not independently verified. No
titles, authors, venues, datasets, or numbers were invented; where a card stated a value was absent it
is not asserted here. Cross-paper judgments are marked *(reviewer synthesis)*; all other claims trace to
the cited paper id under its own evaluated threat model.
