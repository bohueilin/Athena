# Synthesis — Privacy-Protection

Corpus: 73 papers, all AAAI-26 (2026), merged from two partial syntheses (chunk 0 = 40 papers, chunk 1 = 33 papers). Chunk 0: A37135, A37244, A37284, A37472, A37499, A37551, A37735, A37743, A37748, A37854, A37930, A37979, A38004, A38016, A38021, A38130, A38196, A38297, A38773, A39038, A39051, A39210, A39212, A39307, A39311, A39333, A39338, A39373, A39381, A39431, A39496, A39502, A39510, A39524, A39582, A39671, A39681, A39710, A39750, A39895. Chunk 1: A39911, A39975, A40033, A40041, A40045, A40047, A40117, A40132, A40206, A40343, A40398, A40534, A40720, A40773, A40818, A40838, A40839, A40852, A40862, A40868, A40870, A40874, A40889, A40896, A40911, A41120, A42113, A42140, A42151, A42229, A42232, A42372, A42453.

Weighting favors experimental quality, reproducibility, threat-model realism, and independent (cross-chunk) replication over paper count. Throughout, "direct paper finding" marks values reported by the paper's authors; "reviewer synthesis" marks cross-paper inference added during review. Numbers are author-reported unless stated otherwise, and several cards flag truncated/OCR-approximate result tables — those are recorded as author-stated, not reviewer-verified. Where a value was absent or unrecoverable in the reviewed text it is written "not stated in paper." A material fraction of this folder is heterogeneous or miscategorized; §2 separates genuine privacy contributions from category artifacts, and off-topic papers carry no security weight.

---

## 1. Executive summary

This category is **statistical, cryptographic, and mechanistic data-privacy for ML** — differential privacy, secure computation, machine unlearning / right-to-be-forgotten, gradient- and embedding-reconstruction attacks, and provenance/attribution — with only a thin minority sitting on the agent execution surface. It is largely an *evidence-and-mechanism* discipline: the guarantees and mechanisms constrain what a defined counterparty can infer; very few papers model an active, adapting attacker inside an agent trust boundary.

The single most replicated cross-cutting property, independently converged from both chunks, is that **approximate/heuristic privacy mechanisms leave an adversarially recoverable residue, and behavioral or "by-construction" evidence understates it**. Two forms dominate: (a) heuristic additive noise on gradients is invertible (A37743, A39333), and (b) approximate machine unlearning leaves a detectable, often reactivatable imprint (A39373, A40047, A40343, A40818, A40870, A41120). The corollary — replicated across many cards — is that **model-derived artifacts are identity/membership-bearing secrets, not opaque tokens**: gradients and smashed representations (A37743, A39333, A39212), soft prompts (A40839), face embeddings even after "protection" (A42453), and steering vectors (A40720) all invert or leak membership, sometimes with no output access at all.

A minority of papers adopt materially stronger, more realistic threat models and carry disproportionate weight: **A42453 (FEM)** — full paper, realistic black-box embedding-only adversary, multiple FR/PPFR targets plus a commercial API, defeating eight named "privacy-preserving" template schemes; **A41120 (PrivUB)** — a standardized unlearning-attack benchmark showing existing defenses are fragile and that deployment operations (fine-tuning) reactivate forgotten data; **A40047 (FMIA)** — a single-query, benign-user, black-box former-membership imprint; **A39333 (Venom)** and **A37743 (GGSS-R)** — convergent, methodologically independent demonstrations that DP/heuristic-noise gradient perturbation is bypassable; **A39373 (IDI)** — that black-box unlearning metrics are gameable while the encoder retains the forget set; and **A40874 (SAPA-Bench)** — the most agent-core paper, quantifying that off-the-shelf MLLM smartphone agents lack privacy awareness in the action path. On the defense side the formal anchors are **A39510** (tight hidden-state DP-SGD analysis) and **A39051** (DP that provably preserves hard constraints).

For a Guardian / agent stack the actionable primitives are: **treat every transmitted model artifact — gradients, submodels, prototypes, smashed reps, soft prompts, steering vectors, embeddings — as a first-class secret with egress control**; **prefer accounted DP and secure aggregation over heuristic noise, and log the privacy dial (ε/γ/mr/FSInfo/D) as configuration-of-record**; **verify deletion at the representation level and treat "delete my data" as risk reduction, not guaranteed erasure**; and **put an independent privacy/human-approval gate in the agent action path** (A40874), since data-at-rest protection is insufficient when the decision/policy sequence itself leaks (A39710).

---

## 2. Scope and boundaries

**In scope (genuine privacy/security contributions, ~55 of 73):**
- **Differential privacy** — central DP with formal accounting (A39051, A39510, A37854, A38016, A39710, A39311, A39582), local DP and utility recovery (A39582, A39381, A40041, A40862, A40720), subspace/structure-restricted DP (A40117, A40720), DP synthetic data / in-context demonstrations (A38016, A40838), crypto-assisted DP training (A40852).
- **Machine unlearning / right-to-be-forgotten** — mechanisms (A37499, A38196, A39038, A39431, A39750, A39895, A39911, A40045, A40343, A40398, A40818, A40870, A40896), unlearning *evaluation/attacks* (A39373, A40047, A41120), and unlearning *repurposed* for fairness/robustness (A39681).
- **Reconstruction / inversion / inference attacks** — gradient inversion (A37743, A39333), split-inference data-reconstruction (A39212), embedding/template inversion (A42453), prompt-vector membership inference (A40839), attribute inference (A40206, A42113), telemetry reconstruction (A40862).
- **Secure computation** — MPC / secret sharing (A38773, A39210, A40132, A40852), HE / private inference (A40033, A39502, A42229), ZK verifiable inference (A42232).
- **Inference-time / representation & prompt privacy for (M)LLMs** (A40041, A40534, A40773, A40911), model IP / extraction (A39496, A39671), covert-channel confidentiality (A37284), provenance/attribution/auditing (A37135, A37735, A37930, A40868), robust/verifiable FL aggregation (A40889).

**Privacy-motivated but privacy-unevaluated (~4):** federated methods whose "privacy" is data-minimization-by-architecture with no threat model, attack, or accounting — A39307, A39524, A39338, and the informal-synthesis A38021. Gradient/digest sharing is a documented leakage vector (A37743, A39333), so these are contested as security evidence.

**Adjacent / peripheral (flagged by their own cards):** A39975, A40132, A40862, A40868, A42113, A42151, A42140.

**Explicitly off-topic / miscategorized (~8 — carry no privacy/security weight):** pure computer-vision/graphics reconstruction or efficiency papers with no adversary, asset, or threat model — A37244 (driving-VLA token pruning), A37472 (EEG-to-video decoding; the card flags a dual-use privacy *threat*, not a defense), A37551 (video grounding), A37748 (MRI reconstruction), A37979 (slender-structure 3D), A38004 (dynamic-scene NVS; its "noise injection" is a regularizer, explicitly *not* differential privacy), A38130 (semi-transparent surface reconstruction), A38297 (hyperspectral reconstruction). A42140 is a thesis-proposal abstract with no instantiated threat model.

Reviewer synthesis: the folder label alone is not evidence of a privacy mechanism. A recurring trap is conflating "noise injection" (a generalization regularizer, e.g. A38004) or "data locality" (A39338, A39524) with a privacy guarantee; each card had to be read to separate real defenses from category artifacts.

---

## 3. Dominant threat models

Six recur across the genuine-privacy papers; the first three carry the most weight because they are most consistently instantiated.

1. **Honest-but-curious / semi-honest counterparty (the single most common model).** A server, cloud provider, or compute host that follows the protocol but tries to infer private inputs, weights, or attributes. Chunk 0: A39210 (semi-honest 2PC), A39212 (honest-but-curious server running DRAs with surrogate knowledge), A38773 (semi-honest, honest-majority), A39311/A39582 (semi-honest/untrusted server under DP), A39038 (honest server). Chunk 1: A40033, A40132, A40852, A40206 (honest-but-curious VFL server), A42229. Malicious/active/colluding adversaries are almost universally out of scope, and several papers state this explicitly (A40033, A40132, A40852).
2. **Formal, adversary-agnostic worst-case (differential privacy / crypto).** Information-theoretic, adaptive-safe by construction, unbounded auxiliary knowledge, per-record adjacency: A39051, A39510, A37854, A38016, A39710, A39311, A39582, A40117, A40838, A40852, A40862, A40720. These argue privacy from the (ε,δ)/ε/µ-GDP/Metric-LDP guarantee rather than from an executed attack — none of them runs an empirical attack to corroborate the bound (see §12).
3. **Post-deletion / unlearning adversary.** An actor who probes or fine-tunes a model *after* a forgetting operation. Membership-inference as the privacy oracle (A37499, A38196, A39038, A39895, A39510, A38016), single-query black-box former-membership (A40047), white-box relearning via fine-tuning (A40343 "RTT"), decoding-switching + multi-granularity MIA (A40818), gradient-matching reconstruction from θ↔θ_u (A41120), and a standardized taxonomy of such attacks (A41120).
4. **Provider-as-adversary / untrusted third-party model (the closest recurring agent-trust-boundary analogue).** A40534 (third-party LLM sees KG entities), A40720 (provider holds shared steering vector), A40911 (cloud MLLM sees uploaded image), A42232 (untrusted quantum host). Reviewer synthesis: this is a confused-deputy framing for agents calling external models.
5. **Gradient-interception / leaked-artifact adversary.** Honest-but-curious server or eavesdropper reading per-client pre-aggregation updates (A37743, A39333; training path), or an attacker who intercepts a released artifact — soft prompt (A40839), steering vector (A40720), face embedding (A42453, black-box embedding-only). 
6. **Model-confidentiality / IP-theft adversary.** Model extraction from a query API (A39671), unauthorized execution of released weights (A39496). Here the protected asset is `model_weights`/`ip`, not user data.

A seventh, non-adversarial "target under audit / compliance" pattern has no active attacker at all: A37135 (a possibly non-compliant app), A37735 (an infringing model), A37930 (an attributed generator), and the mandated-deletion papers A40045/A40896/A39975.

---

## 4. Major attack families

- **Gradient inversion / training-data reconstruction from FL gradients** (A37743 GGSS-R, A39333 Venom). Both reconstruct client images from noise-perturbed / DP gradients; A39333 does so **analytically without knowing the noise distribution** (author-reported LPIPS 0.340 vs 0.632 and ASR 45% vs 2% for the prior SOTA at ε=10, δ=10⁻⁵), A37743 uses a generic unaligned diffusion prior. The chunk's strongest attack signal (see §9).
- **Model / template inversion & reconstruction** (A42453 FEM: diffusion+KAN face reconstruction from FR/PPFR embeddings; author-reported ASR at FAR=0.01, e.g. IRSE50 FEM-KAN 83.7 vs MAP2V 77.9). A41120 reports white-box gradient-matching reconstruction from θ vs θ_u as the most severe leakage; A39975 uses data-free reconstruction benignly but is inversion-adjacent.
- **Data-reconstruction attacks (DRAs) in split inference** (A39212) — invert smashed intermediate representations back to raw input, worst when the client-side "bottom" model is shallow. A40862 treats a single-message Bayesian DRA as a first-class LDP design axis.
- **Membership / former-membership inference** — pervasive as an *evaluation* probe (A37499, A38196, A39038, A39895, A39510, A38016, A40720, A40818, A41120) and as headline attacks: A40047 (stealthy single-query former-membership on unlearned GNNs, learned dual-encoder + contrastive loss, AUC reported "up to ~0.9+" on some settings, cells truncated); A40839 (output-free MIA from prompt vectors — PIPRA, author-reported avg AUC 87.58% vs 77.05% for output-dependent baselines, 90.37% acc on Caltech101).
- **Relearning / knowledge-recovery on unlearned models** — A40343 (RTT fine-tuning restores forgotten knowledge unless erasure reaches knowledge-dense layers), A40398 (adversarial-prompt reproduction of forgotten code), A40818 (ZeroThink/LessThink alternative decodings expose chain-level residue), A41120 (fine-tuning worsens leakage more than quantization).
- **Attribute inference** — A40206 (adversarial classifier infers sensitive attributes from VFL embeddings), A42113 (speaker re-identification from anonymized child audio via ECAPA-TDNN + EER).
- **Model extraction / stealing** — A39671 (encoder reconstructed offline for free; only a lightweight head needs victim labels; author-reported ~100 queries vs ~5,000 for prior SOTA), and oracle-guided key-recovery against hardware model-locking (A39496).
- **Verifier gaming / evaluation attack** — A39373 (Head Distillation satisfies MIA/JSD unlearning metrics while leaving the encoder identical), A42232 (untrusted host returns a wrong result, detected by ZK proof).
- **Data-poisoning / backdoors weaponizing FL or the unlearning channel** — A39895 (malicious clients issue deletion requests to damage similar-data victims; unfair forgetting is the vulnerability), A39911 (backdoor via a feature party), A40889 (IPM/ALIE/scaling model-poisoning against FL aggregation, tested to 80% malicious data-providers).
- **Deepfake / forgery / evasion** — A40868 (AIGC image detection across 20+ generators), A42151 (deepfake detection, doctoral-consortium summary).

---

## 5. Major defense families

- **Differential privacy (largest formal family).** Central DP with accounting: A39051 (LP with a truncated/one-sided-tightening Laplace mechanism that *guarantees original-constraint feasibility*), A39510 (tight hidden-state RDP for smooth non-convex losses), A37854 (µ-GDP dataset distillation exploiting post-processing immunity), A38016 (DP-SGD synthesis + noise-tolerance pre-training), A39710 (ε-DP + Nash-regret bandits). Structure/subspace-restricted DP to escape the noise∝dimension curse: A40117 (DP-SFT subspace), A40720 (PrivSV, structure-aware reduction then Metric-LDP), A40862 (RNS single-residue LDP). DP in-context/synthetic: A40838. Local DP and utility recovery: A39582, A39381, A40041 (two-layer adaptive LDP prompt routing). ε-DP on prototypes: A39311. Crypto-assisted DP training: A40852 (2PC-zCDP).
- **Machine unlearning (largest overall family).** Representation misdirection to a fixed random anchor (A39911; A40870 RMisU step), causal/bias-pathway disentanglement (A37499 CUPID), peripheral low-confidence forgetting (A38196 PeriUn), federated-graph residual-permeation removal (A39038 PAGE), hyperbolic retain-data-free concept removal (A39431 DIET), few-shot zero-glance synthetic erasure (A39750 GFOES), exact sharded federated unlearning (A39895 FedShard), token-level output redistribution (A40398 PROD), layer knowledge-density + block re-insertion (A40343 KUnBR), influential-neuron-path editing across modalities (A40870 MIP-Editor), inference-time trajectory suppression without weight updates (A40818 STaR), federated LoRA-based targeted unlearning (A40045 Oblivionis), certified graph unlearning with fairness (A40896 GUIC). Plus the *evaluation* (A39373 IDI, A40047, A41120) and *repurposing* (A39681) of unlearning.
- **Secure computation (MPC / HE / ZK).** Private cake-cutting with honest-majority Shamir sharing and oblivious fixed-structure restructuring (A38773), 2PC secret-shared Boolean matmul + k-anonymous supernodes (A39210), RMFE-packed Shamir MPC training over Z_2^k (A40132), HE+MPC transformer inference (A40033 PCFormer, author-reported ~1.9× speedup, semi-honest), CKKS-encrypted argumentative explanation (A42229), ZK proof of quantum inference with parameter hiding (A42232). A39502 is an efficiency method that *assumes* an underlying crypto-PI protocol.
- **Selective / sensitivity-aware / data-minimization protection.** Adversarial obfuscation of only the sensitive attribute (A40206 NashCoder), entity anonymization/abstraction so raw data never reaches the LLM (A40534 ARoG), redact-then-recover surrogate editing (A40911 SOER), context-aware routing keeping high-sensitivity prompts local (A40041 PRISM), split-inference information decomposition then FSInfo/Fisher-calibrated noise (A39212), output-abstraction for confidential agent evaluation (A42372).
- **Inference-time representation steering** — A40773 (Know-Then-Do, mass-mean privacy-direction steering, training-free, LLM→VLM transfer).
- **Provenance / attribution / detection** — A37930 (training-free double-reconstruction loss-ratio attribution), A37735 (memorization/copyright detection via paired learning/unlearning branch divergence), A37135 (LLM multi-agent privacy-compliance auditing), A40868/A42151 (synthetic-media detectors).
- **Model-asset protection & covert channels** — A39496 (hardware logic-locking, "activated accelerator = license"), A37284 (hide sensitive video in a cover, analyze in the steganographic domain).
- **Robust / verifiable FL evaluation** — A40889 MartDE (encrypted scoring with client-side decryption, commitment-based verifiable selection, norm-normalization before cosine-similarity trust scoring, anytrust non-collusion).
- **Federated-by-architecture data minimization (asserted, not evaluated)** — A39307, A39524, A39338.

---

## 6. Most influential concepts

- **Approximate/heuristic privacy leaves recoverable residue; "deletion" ≠ "unrecoverable," "noise" ≠ "private."** The organizing conclusion across both chunks (reviewer synthesis over ~9 papers; see §9). Hiding, cosmetic output changes, and additive noise are not security boundaries.
- **Model-derived artifacts are secrets, not opaque tokens.** Gradients, smashed reps, soft prompts, steering vectors, and even "protected" embeddings invert or leak membership — sometimes with no output access (A40839, A42453, A37743, A39333, A39212, A40720). A direct input to any credential-broker/artifact-sharing design.
- **Deletion must be verified at the representation level, not behaviorally.** Output-only evidence (MIA/accuracy parity) is gameable (A39373 Head Distillation: forget set recoverable to >82% vs ≤41% true retrain); the missing acceptance test is a residual-information probe (feature MI or head-retraining recoverability) or a relearning attack (A40343, A40818, A40047).
- **Formal DP/MPC is adaptive-safe by construction but only as strong as its accounting and trust boundary.** The guarantee is worst-case for the *specific* released artifact and trust model; it is voided by leaked intermediate checkpoints (A39510), a colluding majority (A38773, A40852), or un-accounted shared objects (A39311 structural graphs, A39582 masses, A39307 digests).
- **Selective, sensitivity-aware protection beats blanket DP/HE/MPC on utility.** Protecting only the sensitive part reduces (not eliminates) the utility cost — "no free lunch is reduced, not removed" (A40206, A40041, A40534, A40911).
- **Post-processing immunity is a budget lever.** Route as much computation as possible through already-private (DP-generated) data so it costs zero additional budget (A37854; A39051 "solving the private LP doesn't weaken privacy").
- **The decision/policy sequence is itself a leakage channel.** A bandit's arm-selection sequence leaks per-user outcomes even when stored data is protected (A39710) — protecting data at rest is insufficient for feedback-driven agentic routing.
- **DP must coexist with hard safety constraints.** A39051's one-sided-tightening truncated-Laplace noise *guarantees* the released solution still satisfies the original constraints — the canonical pattern for privacy that cannot violate a safety invariant.
- **Enforce privacy in the agent action path, not only at rest.** A40874's recognition→localization→severity→human-confirmation gate before high-sensitivity actions is the transferable agent-security concept ("capability is not permission").

---

## 7. Common datasets and benchmarks

Only datasets/benchmarks explicitly named in the reviewed text are listed; others are marked unstated to preserve evidence integrity. Many under-attack tables were truncated/OCR-approximate and are recorded as author-stated.

- **PrivUB harness (A41120)** — the one standardized cross-method benchmark in-corpus: author-stated 11 datasets × 10 models × 10 unlearning techniques × 21 attacks/defenses; its own per-cell metric definitions were truncated in the extracted text.
- **Face-recognition targets (A42453)** — IRSE50 and GhostFaceNet backbones plus a commercial API, against eight named protection schemes (DCTDP, HFCF, PartialFace, MinusFace, PolyProtect, MLP-Hash, SlerpFace, Fawkes); reconstruction ASR reported at fixed FAR (e.g. FAR=0.01).
- **R-TOFU** — single unlearning benchmark for A40818 (one model).
- **Caltech101** — one PIPRA MIA setting (A40839, 90.37% acc author-reported).
- **Small-scale crypto-ML settings** — MNIST-scale FCN/CNN (A40132), ~2000-sample setups (A40852), tabular Breast-Cancer MLPs (A42229), 4-qubit MNIST (A42232); 6.7–8B-parameter LLMs for unlearning (A40343, A40398).
- **Vision classifiers / image datasets** dominate the unlearning and DP-image papers; specific corpus names are **not stated in paper** in the reviewed text for the large majority (A37499, A38196, A39038, A39373, A39431, A39750, A39895, A39051, A39510, A39582, A39311, A40117, A40838, A40720, A40041, A40534, A40911, A40206, and others).
- **Synthetic-only or single-dataset** evaluation is flagged for A39051, A39710 (synthetic), A37472 (single dataset), A40818 (one model).
- Off-topic papers (A37244, A37472, A37551, A37748, A37979, A38004, A38130, A38297) evaluate on their own CV/graphics benchmarks; not relevant here.

---

## 8. Evaluation metrics

- **Reconstruction fidelity / perceptual distance** — LPIPS and attack-success-rate (ASR) for gradient inversion (A39333 author-reported LPIPS 0.340 vs 0.632, ASR 45% vs 2% at ε=10, δ=10⁻⁵); PSNR/quality for A37743; A37743's reusable **Reconstruction-Vulnerability (RV)** architecture-audit metric.
- **ASR at fixed FAR** for template/embedding inversion (A42453, e.g. IRSE50 FEM-KAN 83.7 vs MAP2V 77.9 at FAR=0.01; residual ASR e.g. 44.5 on GhostFaceNet for MinusFace — "reduced but not eliminated").
- **Membership-inference AUC/accuracy** as the privacy oracle for unlearning and prompt leakage (A40047 AUC "up to ~0.9+", cells truncated; A40839 avg AUC 87.58% vs 77.05% baseline; A38196/A39038/A39895/A39510/A38016 fixed MIA).
- **MIA-gap / JSD to a retrain oracle, and representation-level recoverability** for unlearning (A39373: >82% forget-test accuracy recoverable via head-retraining on 2% of data vs ≤41% for a true retrain; A40870 best forgetting only ~80–88%; A39431 forget-acc 8.06%; A39750 A_Df=0 — the last two *not* adversarially verified).
- **The privacy dial as configuration-of-record** — ε (A39051/A39510/A39582/A39311/A39710/A40838), local-DP flip probability (A39381), compression ratio γ (A39210), guidance rate mr (A37743), FSInfo level (A39212), bounded-domain diameter D (A39510), Metric-LDP εd² (A40720). Multiple papers report baseline collapse at strong privacy (A39582 baselines go "NA" at ε<1; A39381 reports 30–60% GPL degradation under perturbation).
- **Efficiency / latency** for crypto-ML (A40033 ~1.9× speedup; A40852 642.78 s vs 173,960.9 s author-reported; A39671 ~100 queries vs ~5,000 for prior extraction).
- **Fidelity/faithfulness of crypto approximations** (A42229 IO unfaithfulness 0.0499→0.4454 collapse at MLP-L).
- **Formal-guarantee statements without an executed attack** — feasibility/sub-optimality theorems (A39051), RDP + utility bounds (A39510), perfect security under honest majority (A38773), (ε,δ)/LDP composition (A40117, A40838, A40852, A40720). Treat these as guarantees on the specific released artifact, not empirical robustness.

---

## 9. Strongest replicated findings

Ranked by cross-chunk independence and threat-model realism.

1. **Heuristic additive noise on gradients is not a robust privacy defense.** Independently demonstrated by two methodologically distinct attack papers — A37743 (diffusion-prior inversion of Gaussian/Laplacian-perturbed gradients) and A39333 (analytic, noise-prior-free reconstruction from DP-protected gradients). The defense-side DP papers agree in spirit: A37854 and A39510 argue the *accounted* DP guarantee — not heuristic perturbation — is the load-bearing property, and A37743's own theory shows noise raises the reconstruction-error lower bound (so noise has value but is insufficient alone). Convergent design implication: secure aggregation + clipping-with-DP-accounting + (optionally) compression, red-teamed with a generative-prior attacker.

2. **Approximate unlearning leaves an adversarially detectable, often reactivatable residue; behavioral/black-box metrics understate it.** The corpus's most robust cross-paper conclusion, supported by ≥7 independent papers across both chunks: A39373 (black-box MIA/JSD parity achievable by cosmetic output changes while the encoder fully encodes the forget set), A40047 (single black-box query detects the imprint), A40343 (RTT relearning restores knowledge from unmodified layers), A40818 (chain-level leakage survives answer-level unlearning and alternative decodings), A40870 (best forgetting only ~80–88%, residual remains), A41120 (the θ↔θ_u discrepancy is itself a leak; existing defenses "generally lack robustness"). Reviewer synthesis: papers claiming "complete forgetting" purely behaviorally (A39431, A39750) are, by their own cards, not adversarially verified — a representation-level or relearning probe is the missing acceptance test.

3. **Model-derived artifacts are identity/membership-bearing secrets, not opaque tokens.** Soft prompts leak training-set membership with no output access (A40839); FR/PPFR face embeddings — even "protected" or partial — invert to realistic impersonating faces defeating eight named schemes (A42453, the strongest-evidence entry); steering vectors and pseudo-source reconstructions carry recoverable structure (A40720, A39975); smashed split-inference representations invert (A39212). Convergent with finding 1 (gradients are reconstructable).

4. **Formal DP/MPC guarantees are adaptive-safe by construction but only as strong as their accounting and trust boundary.** A39051 (feasibility + sub-optimality theorems), A39510 (RDP + utility bounds), A38773 (perfect security under honest majority), A39582/A39311/A39710 (ε-DP). Repeated caveat: leaking intermediate checkpoints (A39510), a colluding majority (A38773, A40852), or un-accounted shared artifacts (A39311, A39582) voids the guarantee.

5. **Selective, sensitivity-aware protection preserves utility better than blanket DP/HE/MPC**, and **formal privacy is cheaper when noise/computation is restricted to task-relevant structure.** A40206, A40041, A40534, A40911 (protect only the sensitive part); A40117 (subspace), A40720 (structure-aware compression before DP), A40862 (single-residue reporting), A40852 (bounded MPC-friendly activations). All author-reported near-non-private utility; formal guarantees stated, empirical attacks not run.

6. **The privacy–utility trade-off is intrinsic, dial-tunable, and recurs across every modality** — text (A40041, A40838), embeddings (A40206, A40720), voice (A42113), images (A40911), explanations (A42229), telemetry (A40862), tabular/graph/vision (chunk 0). No paper claims to eliminate it; the dial should be logged as configuration-of-record.

---

## 10. Conflicting findings

- **"Thorough forgetting is achievable" (A40343, A40398, A40870) vs. "unlearning reliably leaves exploitable residue" (A40047, A41120, A40818, A39373).** Not a strict contradiction: the defense papers demonstrate reduced recoverability *under one named attack* (RTT for A40343; adversarial-prompt reproduction for A40398; behavioral forget/retain deltas for A40870), while the attack/benchmark papers show *other* attacks (single-query MIA, gradient reconstruction, alternative-decoding, representation probing) still succeed. Reviewer synthesis: the field lacks a shared adversary, so both statements are true against different, non-overlapping tests — the core open problem (§17).
- **Formal guarantee vs. asserted-by-architecture privacy.** A39051/A39510/A38773/A39311/A39582/A40117/A40852 provide formal DP or MPC; A39307/A39524/A39338 (informally A38021) assert privacy from "we only share gradients/digests/prototypes" with *no* attack or accounting. Since gradient/digest sharing is a documented leakage vector (A37743, A39333), the asserted-privacy papers are contested as security evidence.
- **Whole-model vs. localized editing for unlearning.** A40343 argues gradient-ascent-family methods only touch "cover layers" and must reach knowledge-dense layers; A40870 argues point-wise neuron editing (DEPN/MANU) is *too* local and misses cross-layer/cross-modal flow, requiring path-level editing. Opposite failure diagnoses of prior art, each reconciled only within its own method.
- **Cryptographic confidentiality vs. deployability.** A40033/A40852 report large efficiency gains (~1.9×; two-orders-of-magnitude training-time reduction) yet remain semi-honest-only; A42229/A42232 are honest proofs-of-concept that degrade or stay slow at useful scale (A42229 fidelity collapse; A42232 only noise-free 4-qubit simulation). Same family, opposite maturity signals.
- **"Noise defends" vs "noise fails."** A live tension rather than a strict contradiction: defense papers add noise for privacy; attack papers (A37743, A39333) show noise-only is bypassable; A37743's theory reconciles by showing noise raises but does not eliminate the error bound.
- **Which privacy family to use** — cryptographic MPC (A38773, A39210, A40132, A40852: strong under honest-majority/semi-honest, communication cost, no graceful degradation past the threshold) vs statistical DP (A39311, A39582, A40117: worst-case per-record, composition cost, utility loss) vs metric-privacy (A39212: FSInfo bound, but MSE is a known-imperfect perceptual-privacy proxy). No paper adjudicates; they occupy different trust models.

---

## 11. Defense bypasses

Demonstrated or acknowledged in-corpus.

- **DP / heuristic-noise gradient perturbation → reconstructed** by A37743 (diffusion prior) and A39333 (analytic, noise-prior-free).
- **Black-box unlearning metrics → gamed** by A39373's Head Distillation (encoder unchanged, forget set recoverable).
- **Answer-level unlearning → bypassed by alternative decoding** — ZeroThink/LessThink expose forgotten chain-level content (A40818, the motivating negative result).
- **Deployment operations reactivate "forgotten" knowledge** — fine-tuning (more than quantization) after unlearning increases leakage (A41120); RTT fine-tuning restores knowledge (A40343).
- **Output-suppression defenses do not stop embedding-space attacks** — PIPRA remains effective when output-based MIAs fail under output suppression (A40839).
- **"Protected" embeddings remain invertible** — every PPFR/template-protection scheme tested in A42453 still yields impersonating reconstructions (ASR reduced, not eliminated; e.g. FEM-KAN 44.5 on GhostFaceNet for MinusFace).
- **"Rate-limit + prediction-only" GNN API → bypassed** by encoder-free stealing (A39671), effective even with an extraction defense in place.
- **Cosine-similarity robust FL aggregation collapses under norm/scaling attacks** — most defenses drop below 20% accuracy under large-factor scaling; norm-normalization is credited as the fix (A40889).
- **Single-reconstruction-loss attribution → collapses to near-chance** on SOTA generators like FLUX (A37930's motivating failure of prior work).
- **k-anonymity on supernodes → reviewer-flagged weak** to linkage/auxiliary-information attacks; no ℓ-diversity/DP layer (A39210).
- **Hardware logic-locking → unresolved block-replacement attack** (retrain/replace the protected block rather than recover the key), acknowledged by A39496.
- **Non-adaptive-attacker evaluation likely overstates protection** — flagged for A42113 (only an "ignorant" attacker), A39911 (a single fixed anchor may be trivially reversible by an adaptive party), A40206 (surrogate attacker weaker than a real one).

Calibrated takeaway: demonstrated bypasses are all against *other* schemes under the bypasser's own evaluation. The corpus's own defenses are, with few exceptions (A39671's defense-in-place, A39496's adaptive adversary, A40889's scaling-designed attack, A40818's decoding-aware probe), tested only against non-adaptive attacks; their adaptive robustness **requires production validation**.

---

## 12. Known benchmark limitations

- **Formal-guarantee-without-executed-attack is pervasive.** A39051, A39710, A39582, A40117, A40838, A40720, A40852, A40041, A40534, A40911, A39911 argue privacy via (ε,δ)/LDP composition, Metric-LDP, HE assumptions, or "by construction" (no raw data uploaded) but run *no* empirical membership-inference/reconstruction/linkage attack. Multiple cards independently recommend pairing formal bounds with red-team attacks.
- **Non-adaptive adversaries dominate.** Almost no paper evaluates an attacker specifically optimized against its own pipeline. Notable partial exceptions: A39212 (surrogate-knowledge but not fully adaptive), A40818 (decoding-aware), A40889 (scaling-designed-to-break-cosine), A41120 (adaptive elements), A42372 (iterative resubmission), A39496/A39671 (adaptive / defense-in-place).
- **MIA as sole privacy oracle** — a single, lower-bound-estimator attack family standing in for "privacy" (A37499, A38196, A39038, A39895, A39510).
- **Behavioral forgetting ≠ deletion** — accuracy/MIA-gap metrics miss representation-level residual (A39373, and by extension the unverified-forgetting caveat on A39431/A39750).
- **Scope confinement** — overwhelmingly vision classifiers / image data in chunk 0; unlearning LLM papers use single backbones/synthetic benchmarks (A40818 on R-TOFU, one model); crypto-ML on MNIST-scale (A40132), ~2000 samples (A40852), 4-qubit MNIST (A42232). Scaling behavior is asserted, not shown.
- **LLM-as-judge / model-generated ground truth** — A40874 privacy labels partly GPT-4o-generated; A42372 self-acknowledged-subjective LLM judge; A40773 labels via GPT-4o/Claude auto-labeling; A40911 ground-truth edits are MLLM-generated. Privacy "correctness" is model-dependent.
- **Underspecified accounting** — DP claimed for the headline artifact but not for every shared object (A39311 structural graphs; A39582 mass values; per-round composition for iterative variants not analyzed; A39307 digests).
- **The standardization gap the corpus itself names** — A41120 is motivated by unlearning-attack papers each beating predecessors "under their own tailored conditions," and provides a shared harness; but its own per-cell metric definitions are truncated in the extracted text.
- **OCR / truncation caveats** — many cards flag truncated result tables (A39911, A40045, A40047, A40206, A40852, A40874, A40889, A40911, A41120, A42453 limitations; and several FedShard/GFOES/DP-NCB figures in chunk 0). Treat specific per-cell numbers as author-stated unless a card marks them verbatim.

---

## 13. Implementation patterns

- **Expose and log the privacy dial** (ε/γ/mr/FSInfo/D/εd²) as configuration-of-record; treat budget-accounting error or exhaustion as an incident boundary (A39051, A39510, A39311, A38016, A39710, A40041, A40720, A40838).
- **Post-processing immunity as a budget lever** — route computation through already-private (DP-generated) data so it costs zero additional budget (A37854; A39051).
- **Bounded / one-sided / direction-controlled noise** to preserve hard constraints or valid ranges (A39051 truncated-Laplace tightening for feasibility; A39710 clip-to-[0,1] as safe post-processing).
- **Structure-aware dimensionality reduction *before* adding DP noise**, to escape the noise∝dimension curse (A40117 subspace; A40720 HCC compression; A40862 single-residue reporting; A39212 information decomposition).
- **Decompose-then-protect / coarsen-then-share** — strip redundant/task-irrelevant information before adding noise (A39212), coarsen structure into k-anonymous supernodes (A39210), share *structure* not embeddings/raw prototypes (A39311).
- **Redact/anonymize-then-reconstruct-locally** so the untrusted model never sees raw data (A40534 abstract-then-answer; A40911 surrogate-then-recover; A40041 sketch-then-refine on the trusted edge).
- **Representation misdirection to a random anchor** for forgetting — two independent papers (A39911 collapse-to-c·u; A40870 RMisU to a random unit-sphere target) plus a retain loss to preserve utility.
- **Oblivious restructuring of leaky artifacts** — replace an input-dependent dynamic graph with a fixed graph + cryptographic edge weights so timing/structure leaks nothing (A38773).
- **Isolate-then-merge sharding** for root-path-local, bounded-blast-radius exact unlearning (A39895).
- **Swap non-crypto-friendly ops for low-degree-polynomial/soft approximations** in HE/MPC pipelines (A42229 ReLU→x²+x, hard→soft k-means; A40852 bounded comparison-only activation; A42232 trig via low-degree polynomials) — with a recurring faithfulness/accuracy penalty.
- **Difference/consistency signals over absolute values** — double-reconstruction *ratio* (A37930), learning-vs-unlearning branch *divergence* (A37735), difference-maximizing adversarial graph as a residual-knowledge probe (A39038).
- **Emit an auditable evidence record per privacy-relevant operation** — unlearning events (A40045, A40870), ε-budget consumption (A40041, A40720, A40838), commitment-based verifiable selection (A40889), per-request certificates (A40896), evidence-linked audit verdicts (A37135).
- **Two-non-colluding-parties as the trust anchor** (A40852 two-server; A40889 anytrust) — with the caveat that the guarantee collapses under collusion.

---

## 14. Product design implications

For a guardian / agent-security stack (reviewer synthesis grounded in the cited cards).

- **Treat every transmitted model artifact as a sensitive, reconstructable asset** — gradients, submodels, prototypes, digests, smashed representations, soft prompts, steering vectors, embeddings (A37743, A39333, A39212, A40839, A42453, A40720). Assume reconstructable if intercepted; prefer accounted DP and/or secure aggregation over heuristic noise; never ship raw per-client gradients over untrusted channels.
- **A privacy gate belongs in the agent action path.** A40874 shows off-the-shelf MLLM smartphone agents recognize sensitive actions at RA below 60% even with explicit hints (best Gemini 2.0-flash ~67%); the recommended control is an independent recognition→localization→severity→human-confirmation stage before executing high-sensitivity actions (credentials, financial, precise location, permission grants). This maps directly to a PolicyGuard/ActionGuard-style gate with human approval on sensitive tool calls — "capability is not permission."
- **The decision/policy sequence is itself a leakage channel** (A39710) — a feedback-driven agentic routing/personalization loop can leak per-user outcomes even when stored data is protected. Protect the interaction trace, not only data at rest.
- **"Delete my data" / agent-memory purge is risk reduction, not guaranteed erasure.** Pair it with residual-risk disclosure, representation-level acceptance tests, post-deletion re-audit (adversarial membership probes), and least-privilege on dual-version (θ, θ_u) weight access. Treat deployment-phase re-fine-tuning as a reactivation hazard (A41120, A40047, A40343, A40045, A40896, A39373).
- **Treat the unlearning-request channel as adversary-controlled** and bound the cross-principal blast radius and cost variance (A39895 — unfair forgetting enables poisoning and cascaded departures).
- **Provider-as-adversary is a real deployment pattern for agentic RAG/tool use.** Keep raw private content local and send only anonymized/abstracted/surrogate data to external models (A40534, A40720, A40911, A42232) — the closest in-corpus confused-deputy control.
- **LLM multi-agent tooling over untrusted content is a prompt-injection surface.** A37135 runs LLM agents over attacker-influenced decompiled code/strings without an injection control (reviewer-flagged unimplemented gate); its evidence-linked verdicts (flow/code/policy snippet + reasoning + confidence) are, however, a strong `audit_records` pattern.
- **Confidential agent evaluation via output-abstraction + sandboxing** (A42372) — expose derived diagnostics (scores + failure clusters), never raw trajectories, run untrusted code server-side behind a strict submission contract with human gating.
- **Formal privacy claims in product copy must be validated against executed attacks** before trust — A42453 is the cautionary example (schemes marketed as "privacy-preserving" invert under test).
- **Provenance/attribution are governance building blocks but probabilistic evidence, not proof** — A37930/A37735 outputs should gate/triage, not autonomously certify, and are not robust to adaptive evasion.

---

## 15. Architecture implications

- **Put a DP/secure-aggregation boundary on the training/telemetry path, with accounting for *all* shared artifacts,** not just the headline object (A39311 structural graphs, A39582 masses, A39307 digests). Never treat data locality (A39338, A39524) as a privacy guarantee.
- **Restrict noise/computation to task-relevant structure** to make formal privacy affordable — subspace/compression before DP (A40117, A40720, A40862), decompose-then-protect (A39212). This is the recurring way to get formal guarantees at deployable utility.
- **DP must coexist with hard safety constraints.** Where a privatized output feeds a system with invariants (feasibility, valid ranges, safety envelopes), use constraint-preserving mechanisms (A39051 one-sided-tightening; A39710 clip-to-domain post-processing) rather than symmetric noise that can violate them.
- **Bind deletion to a verifiable, representation-level pipeline** with dual-version (θ, θ_u) access control, per-request certificates (A40896), and re-audit after any output-layer patch (A39373). Behavioral parity alone is not an acceptance signal.
- **Model the untrusted external model as inside the trust boundary** for RAG/tool use: redact/anonymize/surrogate at the edge, keep the private artifact local (A40534, A40911, A40720). For outsourced compute where correctness matters, a verifiable-inference layer (A42232) detects a lying host — at current toy scale.
- **Two-non-colluding-party or honest-majority anchors** (A40852, A40889, A38773) are deployable trust models but collapse under collusion — architect for detection of, or resistance to, a colluding majority before relying on them.
- **Model-asset protection is a distinct axis** — serving APIs are extraction targets even with strict rate limits (A39671: detect embedding-guided, centroid-proximal, information-dense small query sets, not just volume); publicly-released weights can be usage-gated via a hardware root-of-trust (A39496), contingent on a tamper-proof key store and unresolved block-replacement risk.
- **Treat privacy dials and secret keys as governed configuration/credentials** — ε-budgets, LDP flip rates, ChaCha20/CKKS keys, verifiable-selection commitments — with custody, rotation, and incident boundaries (A39051, A40041, A40720, A40889, A42229).

---

## 16. Launch and assurance implications

- **Scope every privacy claim to the threat model actually tested.** No absolutes; state "reduced membership/reconstruction success against the tested, non-adaptive attacks" and flag adaptive robustness and LLM-scale behavior as requiring production validation.
- **Require an executed-attack red-team before trusting any formal-DP/crypto claim** at product scale (A40117, A40838, A40852, A40720, A39051) — the recurring card recommendation; A42453 is the cautionary example of a "privacy-preserving" scheme inverting under test.
- **Require a representation-level deletion acceptance test** (residual-information probe or relearning attack) before certifying right-to-be-forgotten; behavioral MIA/accuracy parity is necessary-but-insufficient (A39373, A40047, A40343). Re-audit after any fine-tune or output-layer patch (A41120, A40343).
- **Pin and version-control verifier models, keys, and budgets.** DP budgets, non-collusion assumptions, and key custody are governed dependencies; budget exhaustion or collusion is an incident boundary (A39510, A38773, A40852, A40889, A40041).
- **Validate at production scale.** Crypto-ML and unlearning-LLM results here are MNIST/2000-sample/4-qubit/single-backbone (A40132, A40852, A42232, A40818) — scaling is asserted, not shown; do not launch assurance claims on toy-scale evidence.
- **Disclose residual risk on "delete my data" and "privacy-preserving" features** — deletion is approximate and reactivatable (A41120, A40047); "protected" embeddings remain invertible offline and undetectably server-side (A42453).
- **Instrument the interaction trace, not only the datastore** — feedback/policy sequences leak (A39710); confidential-agent evaluation should expose only abstracted diagnostics (A42372).

---

## 17. Open research problems

- **A shared, adaptive-adversary evaluation standard for unlearning** that reconciles "thorough forgetting" claims with residual-imprint attacks (implied across A40047/A40343/A40818/A41120/A39373). The field currently lacks a common adversary, so opposite conclusions coexist.
- **Certified / irreversible removal from parameters** — every unlearning paper here is approximate or behavioral; none claims a formal removal proof (A40343/A40398/A40870 explicitly), and generative/LLM/agent-memory settings are essentially unvalidated adversarially.
- **Robust privacy for gradient/artifact exchange beyond heuristic noise** — secure aggregation + accounted DP + generative-prior red-teaming, and defenses that survive noise-prior-free analytic attacks (A37743, A39333). Most FL efficiency work (A39338) ships gradients/submodels with no such protection.
- **Empirical-attack validation of formal-DP/crypto defenses at LLM scale** (A40117, A40838, A40852, A40720) — formal bounds are rarely corroborated by an executed attack.
- **Formal accounting for *all* shared artifacts**, not just the headline object (A39311, A39582, A39307).
- **Malicious/active adversaries, collusion, and malicious-server-holding-caches** — universally deferred (A38773, A39210, A40033, A40132, A40852, A40889, A39038, A39895, A39212).
- **Query-time defenses for invertible biometric/embedding templates** — reconstruction is offline and undetectable server-side, so liveness/injection detection is the only remaining control (A42453).
- **Leakage-quantified metrics for "privacy-by-construction" systems** that currently report none (A40534, A40911, A42372, A39975, A39307, A39524, A39338).
- **HE/MPC faithfulness and latency at useful model sizes** (A42229 fidelity collapse; A42232 toy scale).
- **Black-box / API-only forensic detection** — A37735 memorization detection is white-box-only; litigation-realistic settings are black-box.
- **Adaptive-evasion-robust provenance/attribution** (A37930, A37735) and **surrogate-distillation / block-replacement-robust model locking** (A39496).

---

## 18. Recommended foundational papers

Ranked by transferable lesson, evidence quality, threat-model realism, and (cross-chunk) replication.

1. **A39333 (Venom) and A37743 (GGSS-R)** — jointly the load-bearing "heuristic-noise / DP gradient perturbation is bypassable" evidence; independent methods (analytic noise-prior-free vs diffusion-prior), same conclusion under a realistic honest-but-curious FL server. A37743 also contributes the reusable Reconstruction-Vulnerability (RV) architecture-audit metric.
2. **A41120 (PrivUB)** — the meta-result: a standardized benchmark showing machine unlearning introduces new privacy attack surfaces, that tool-combination boosts attacks, that DL↔LLM leakage transfers, and that fine-tuning reactivates forgotten data more than quantization. Reframes the entire unlearning sub-population's "forgetting" claims.
3. **A40047 (FMIA)** — the sharpest low-assumption counter-evidence to "deletion = unrecoverable": a single black-box query, benign-user posture, detects the imprint across three unlearning methods.
4. **A39373 (IDI)** — reframes how deletion must be evaluated: black-box metrics are gameable (Head Distillation), residual information persists in intermediate layers (forget set recoverable to >82% vs ≤41% true retrain); supplies a representation-level metric. Directly shapes any RTBF/safety-forgetting acceptance test.
5. **A42453 (FEM)** — the strongest-evidence paper in the corpus (full paper, realistic black-box embedding-only threat model, multiple FR/PPFR targets plus a commercial API, ASR at fixed FAR): eight named "protected" embedding schemes remain invertible to impersonating identities. Load-bearing for treating embeddings as secrets.
6. **A40874 (SAPA-Bench)** — the most agent-security-core paper: quantifies that MLLM smartphone agents lack privacy awareness (RA <60% even with hints) and motivates an explicit recognition→localization→severity→human-confirmation gate in the action path.
7. **A39510 (improved DP-SGD analysis)** — the "formal DP done right" anchor: tight hidden-state RDP + utility bounds under only smoothness, with the load-bearing operational caveat that the tighter guarantee dies if intermediate checkpoints leak.
8. **A39051 (DP Linear Programming)** — the strongest formal contribution in-corpus for safety-critical settings: DP that *guarantees* original-constraint feasibility via one-sided-tightening truncated-Laplace noise; the canonical pattern for "DP must coexist with hard safety constraints."

Secondary but agent-relevant: **A37135 (PriAgent)** as the only genuinely *agentic* (multi-agent, RAG, tool-use) system, whose untrusted-decompiled-input injection surface and evidence-linked audit trail transfer directly to guardian-agent design; **A40839 (PIPRA)** for establishing soft prompts as a standalone, output-suppression-resistant leakage surface; **A39671 (On Stealing GNNs)** for a realistic model-extraction threat that defeats the "rate-limit + withhold-embeddings" defense.

---

## 19. Recommended frontier papers

Ranked by novelty of paradigm and forward relevance, with maturity caveats.

1. **A40343 (KUnBR)** — best-articulated *defensive* unlearning result with a real relearning-attack (RTT) robustness axis and joint utility reporting; the strongest "thorough forgetting" claim, valuable precisely as the foil to A41120/A40047. Localizes erasure to knowledge-dense layers; maturity caveat: single named attack, 6.7–8B single-backbone scope.
2. **A40041 (PRISM) and A40534 / A40911 (ARoG / SOER)** — sensitivity-aware routing and redact/surrogate patterns for the provider-as-adversary deployment; the closest in-corpus confused-deputy controls for agents calling external models. Maturity caveat: privacy is largely "by construction" with no leakage metric.
3. **A40720 (PrivSV)** — DP steering vectors after structure-aware reduction (Metric-LDP); treats a shared steering vector as a leakable artifact and privatizes it, an emerging surface as steering/activation-editing enters production. Maturity caveat: formal bound, no executed attack.
4. **A42372 (confidential multi-agent evaluation)** — output-abstraction + sandboxing + human gating for evaluating untrusted agents on confidential data; a reusable governance pattern. Maturity caveat: self-acknowledged-subjective LLM judge.
5. **A40889 (MartDE)** — verifiable, robust FL aggregation (encrypted scoring, commitment-based verifiable selection, norm-normalization before cosine trust scoring) that survives norm/scaling poisoning where cosine defenses collapse. Maturity caveat: anytrust non-collusion assumption.
6. **A42232 (ZK proof of quantum inference)** — verifiable outsourced inference with parameter hiding against an untrusted host; forward-looking for trust-minimized compute. Maturity caveat: noise-free 4-qubit simulation only.

---

## 20. Source map (paper id → one-line relevance)

- **A37135** — PriAgent: only genuinely agentic system (multi-agent, RAG, tool-use) for LLM privacy-compliance auditing over decompiled code + policy; untrusted-input injection surface (reviewer-flagged) + evidence-linked audit-trail pattern.
- **A37244** — Off-topic (miscategorized): driving-VLA token pruning; no adversary/asset/threat model.
- **A37284** — Steganographic covert-channel confidentiality: hide sensitive video in a cover, analyze in the steganographic domain.
- **A37472** — Off-topic: EEG-to-video decoding; card flags a dual-use privacy *threat*, not a defense; single dataset.
- **A37499** — CUPID: unlearning that disentangles causal vs bias pathways; shows standard bias-unlearning erases the shortcut, not the class ("shortcut unlearning").
- **A37551** — Off-topic: video grounding; no privacy threat model.
- **A37735** — Memorization/copyright detection via paired learning-vs-unlearning branch divergence; white-box only.
- **A37743** — GGSS-R: diffusion-prior gradient inversion of noise-perturbed/DP gradients; load-bearing "heuristic noise is bypassable"; contributes the reusable RV architecture-audit metric.
- **A37748** — Off-topic: MRI reconstruction; no adversary.
- **A37854** — µ-GDP dataset distillation exploiting post-processing immunity; argues the accounted DP guarantee is the load-bearing property.
- **A37930** — Training-free double-reconstruction loss-*ratio* image attribution; probabilistic evidence, not proof; not adaptive-evasion robust.
- **A37979** — Off-topic: slender-structure 3D reconstruction; no adversary.
- **A38004** — Off-topic: dynamic-scene novel-view synthesis; its "noise injection" is a regularizer, explicitly *not* differential privacy.
- **A38016** — DP-SGD synthesis + noise-tolerance pre-training; uses fixed MIA as the probe.
- **A38021** — Informal-synthesis paper; asserted privacy with no formal accounting layer.
- **A38130** — Off-topic: semi-transparent surface reconstruction; no adversary.
- **A38196** — PeriUn: forget only low-confidence "peripheral" samples; shows only peripheral samples actually change under the retrain oracle.
- **A38297** — Off-topic: hyperspectral reconstruction; no adversary.
- **A38773** — Private cake-cutting via honest-majority Shamir sharing; oblivious fixed-structure restructuring of leaky dynamic-graph artifacts; perfect security under honest majority only.
- **A39038** — PAGE: federated-graph residual-permeation removal (honest server); difference-maximizing adversarial graph as a residual-knowledge probe.
- **A39051** — DP Linear Programming: truncated/one-sided-tightening Laplace that *guarantees* original-constraint feasibility; strongest formal contribution; canonical "DP + hard safety constraints" pattern.
- **A39210** — 2PC secret-shared secure Boolean matmul + k-anonymous supernodes; semi-honest; k-anonymity reviewer-flagged weak to linkage.
- **A39212** — Split-inference information decomposition (frequency + information-bottleneck) then FSInfo/Fisher-calibrated noise; honest-but-curious-server DRA threat.
- **A39307** — FedAI: federated-by-architecture data minimization; asserted privacy, no attack or accounting.
- **A39311** — SPP-FGC: ε-DP on prototypes/structure; un-accounted structural-graph caveat.
- **A39333** — Venom: analytic, noise-prior-free reconstruction from DP-protected gradients (author-reported LPIPS 0.340 vs 0.632, ASR 45% vs 2% at ε=10, δ=10⁻⁵); load-bearing attack.
- **A39338** — Federated efficiency method; data locality asserted as privacy; ships gradients/submodels with no protection.
- **A39373** — IDI: Head Distillation games black-box unlearning metrics while the encoder retains the forget set (recoverable >82% vs ≤41% retrain); supplies a representation-level metric.
- **A39381** — Utility recovery atop LDP; author-reported 30–60% GPL degradation under perturbation.
- **A39431** — DIET: retain-data-free VLM concept removal via hyperbolic geometry (forget-acc 8.06%); not adversarially verified.
- **A39496** — Hardware logic-locking ("activated accelerator = license"); acknowledges an unresolved block-replacement attack.
- **A39502** — Cryptographic private-inference efficiency method; assumes an underlying crypto-PI protocol.
- **A39510** — Improved DP-SGD analysis: tight hidden-state RDP + utility bounds under smoothness; guarantee dies if intermediate checkpoints leak.
- **A39524** — Federated-by-architecture data minimization; asserted privacy, no attack or accounting.
- **A39582** — LDP method; baselines go "NA" at ε<1; un-accounted mass-value caveat.
- **A39671** — On Stealing GNNs: encoder-free extraction (~100 queries vs ~5,000 prior); defeats the rate-limit + prediction-only defense; realistic model-confidentiality threat.
- **A39681** — Repurposes unlearning for fairness/robustness via influence functions.
- **A39710** — ε-DP + Nash-regret bandits; the arm-selection *sequence* leaks per-user outcomes even when stored data is protected; synthetic evaluation.
- **A39750** — GFOES: few-shot zero-glance unlearning via synthetic erasure samples (A_Df=0); not adversarially verified.
- **A39895** — FedShard: exact sharded federated unlearning (isolate-then-merge); documents DPA poisoning via the unlearning-request channel (unfair forgetting as the vulnerability).
- **A39911** — Backdoor via a feature party suppressed to class-prior by unlearning; representation misdirection to a random anchor; single fixed anchor may be reversible by an adaptive party.
- **A39975** — Benign data-free reconstruction (pseudo-source); inversion-adjacent; peripheral; reports no leakage metric.
- **A40033** — PCFormer: HE+MPC transformer inference (~1.9× speedup); semi-honest only.
- **A40041** — PRISM: two-layer adaptive LDP prompt routing; keeps high-sensitivity prompts local (sketch-then-refine on the trusted edge); sensitivity-aware.
- **A40045** — Oblivionis: federated LoRA targeted unlearning with an auditable evidence record; compliance-driven, no attacker.
- **A40047** — FMIA: stealthy single-query black-box former-membership inference on unlearned GNNs (AUC "up to ~0.9+", cells truncated); sharpest counter to "deletion = unrecoverable."
- **A40117** — DP-SFT: subspace-restricted DP fine-tuning; formal guarantee, no executed attack.
- **A40132** — RMFE-packed Shamir MPC training over Z_2^k; semi-honest honest-majority; MNIST-scale; peripheral.
- **A40206** — NashCoder: adversarial obfuscation of only the sensitive attribute in VFL; surrogate attacker acknowledged weaker than a real one.
- **A40343** — KUnBR: layer knowledge-density + block re-insertion unlearning; RTT relearning restores knowledge unless erasure reaches knowledge-dense layers; best "thorough forgetting" claim / foil.
- **A40398** — PROD: token-level output-distribution redistribution to forget code; adversarial-prompt-reproduction attack.
- **A40534** — ARoG: entity anonymization/abstraction so raw KG data never reaches a third-party LLM; provider-as-adversary.
- **A40720** — PrivSV: DP steering vectors after structure-aware reduction (εd²-LDP, Metric-LDP); provider holds the shared steering vector.
- **A40773** — Know-Then-Do: mass-mean privacy-direction inference-time steering; training-free; LLM→VLM transfer; GPT-4o/Claude auto-labeled dataset.
- **A40818** — STaR: inference-time trajectory suppression without weight updates; ZeroThink/LessThink alternative decodings expose chain-level residue; decoding-switching + multi-granularity MIA.
- **A40838** — DP-ICL: DP synthetic in-context demonstrations with single-budget composition; formal, no executed attack.
- **A40839** — PIPRA: output-free membership inference from prompt vectors (avg AUC 87.58% vs 77.05% output-dependent; 90.37% Caltech101); soft prompts as an output-suppression-resistant leakage surface.
- **A40852** — 2PC-zCDP: crypto-assisted two-server DP training (642.78 s vs 173,960.9 s author-reported); semi-honest, non-colluding two-server.
- **A40862** — RNS-based single-message LDP frequency estimation; single-message Bayesian DRA as a first-class design axis; peripheral.
- **A40868** — AIGC image detection across 20+ unseen generators (mAcc 93.02%/91.56% author-reported); provenance; peripheral.
- **A40870** — MIP-Editor: influential-neuron-path editing across modalities; best forgetting only ~80–88%, residual remains; RMisU random-anchor step.
- **A40874** — SAPA-Bench: MLLM smartphone-agent privacy awareness (RA <60% even with hints; best Gemini 2.0-flash ~67%); motivates an action-path privacy/human-approval gate; most agent-core.
- **A40889** — MartDE: verifiable robust FL aggregation (encrypted scoring, commitment-based selection, norm-normalization before cosine); anytrust non-collusion; cosine defenses collapse <20% under scaling.
- **A40896** — GUIC: certified graph unlearning with fairness and per-request certificates; compliance-driven.
- **A40911** — SOER: redact-then-recover surrogate editing so the cloud MLLM never sees the raw image; provider-as-adversary; MLLM-generated ground truth.
- **A41120** — PrivUB: standardized benchmark showing unlearning introduces new attack surfaces and that existing defenses are fragile (author-stated 11 datasets × 10 models × 10 techniques × 21 attacks); meta-result reframing the unlearning sub-population.
- **A42113** — Speaker re-identification from anonymized child audio (ECAPA-TDNN + EER); only an "ignorant" attacker; peripheral.
- **A42140** — Thesis-proposal abstract; no instantiated threat model.
- **A42151** — Deepfake detection + privacy-by-design synthetic biometrics; doctoral-consortium summary aggregating external numbers; peripheral.
- **A42229** — CKKS-encrypted argumentative explanation; ReLU→x²+x / hard→soft k-means approximations; fidelity collapse at MLP-L (IO unfaithfulness 0.0499→0.4454); toy scale.
- **A42232** — ZK proof of quantum inference with parameter hiding; untrusted quantum host; noise-free 4-qubit simulation only.
- **A42372** — Confidential multi-agent industrial evaluation via output-abstraction (scores + failure clusters, never raw trajectories) + sandboxing + human gating; self-acknowledged-subjective LLM judge.
- **A42453** — FEM: diffusion+KAN face reconstruction from FR/PPFR embeddings (ASR at FAR=0.01, e.g. IRSE50 FEM-KAN 83.7 vs MAP2V 77.9); strongest-evidence paper; defeats eight named "protected" embedding schemes.
