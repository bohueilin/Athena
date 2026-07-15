# Adversarial-ML-Attacks — Partial Synthesis (chunk 0, 40 papers)

Scope: paper ids A36961, A36964, A36999, A37010, A37015, A37082, A37116, A37117, A37118, A37119, A37140, A37141, A37272, A37318, A37349, A37388, A37389, A37396, A37420, A37426, A37436, A37442, A37474, A37479, A37488, A37615, A37647, A37651, A37664, A37695, A37716, A37770, A37792, A37903, A37912, A37955, A37967, A38013, A38015, A38056. All are AAAI-26 papers pulled from the "Adversarial-ML-Attacks" corpus folder.

Reviewer caveat up front (synthesis, not a paper claim): this chunk is dominated by **classical ML robustness / vision / poisoning research**, not agent/LLM-runtime security. Four papers are mis-filed by keyword — "adversarial" means GAN/domain-adversarial training, with **no threat model at all**: A37272 (cross-view geo-localization), A37318 (video-diffusion distillation), A37488 (diffusion sampling guidance), A37967 (fair multi-view clustering). They are tagged `insufficient` and should not be cited as attacks or defenses. Two more (A37272/A37318) explicitly self-flag the mis-fit.

---

## Dominant threat models

Across the security-relevant papers, the recurring threat models are (grouped by adversary knowledge, as stated in each paper):

- **Poison-only, black-box supply-chain** (attacker touches only training data / a distributed artifact, no model access): A36961 (audio speaker-rec), A36964 (code models, cross-dataset), A37119 (distilled datasets, no raw data), A37141 (contrastive encoders — the defender's assumed adversary), A37770 (temporal graphs, train-set-only), A38056 (traffic-sign fluorescence backdoor). A37349 (clean-label physical backdoor) is the **gray-box** variant (attacker knows architecture, cannot relabel). A38015 (multi-target LVLM backdoor) is gray-box via access to the **public visual encoder** only.
- **Black-box transfer evasion** (craft on a surrogate, transfer to an unseen victim, no victim queries): A37015 (UAP theory), A37420/A37436 (VLM/video-MLLM), A37442 (multi-image MLLM), A37651/A37664/A37695 (targeted / continual-learning / video-foundation-model transfer), A37912/A38013 (transferable image attacks). A37388 claims black-box but the card flags an **internal contradiction** (it needs logits and text-embedding-space access → effectively gray/white).
- **Query-only / API black-box at inference**: A37118 (evade LM vulnerability detectors), A37647 (physical, query-only patch on deployed LVLMs).
- **White-box inference-time** (gradient access to the victim): A37082 (cooperative-perception latency), A37396 (PGD, defense-training), A37903 (point-cloud), A37479 (SNN), A37955 (physical FP creation on 3D detection).
- **Worst-case / adaptive**: only A37117 (adaptive attacker who reverse-engineers a model lock) and A37716 (attack-agnostic certified defense) genuinely model an adaptive/unrestricted adversary in the optimization or certification loop.
- **Prompt-channel adversary against an LLM**: A37389 only (jailbreak / prompt-injection text).

Only three papers sit squarely in **agent/LLM security** as the guardian-agent skill defines it: A37389 (prompt-injection/jailbreak defense), A38015 (LVLM instruction-tuning backdoor supply chain), A37116 (OSS/tool supply-chain risk scoring). A37118, A37442, A37647 are adjacent (an LLM/LM used as a gate, or an LVLM agent ingesting untrusted images).

## Major attack families (this chunk)

1. **Backdoor / data poisoning** (the single largest family): A36961, A36964, A37119, A37349, A37770 (poisoning of link prediction), A38015, A38056; defender-side counterparts A37141 (detect during CL training), A37116 (score supply-chain risk), A37117 (backdoor mechanics repurposed as a *lock*). Recurring sub-themes: **transferability across datasets/architectures** (A36964's flat-minima insight; A36999 hypergraph pivotality), **clean-label / hidden-trigger** stealth (A37349), **dataset-distillation as a poisoning primitive** (A37119, A37349), **multi-target** binding via proxy-space partitioning (A38015), and **conditionally-visible physical triggers** (A38056 fluorescence; leaves no persistent artifact).
2. **Adversarial examples / evasion** (vision-heavy): universal perturbations (A37015 theory, A37442 multi-image, A37647 physical patch), transfer attacks (A37420, A37436, A37651, A37664, A37695, A37912, A38013), sparse/cooperative 3D (A37903), SNN-specific latency-aware (A37479), false-positive **creation** attacks (A37955 "ghost" vehicles), and multimodal cross-modal-synergy (A37388).
3. **Availability / latency ("sponge") attacks**: A37082 (CP-FREEZER) — inflates NMS's O(M²) cost via crafted V2V features to blow past a 1.5 s time-to-collision deadline. A37479 reframes latency as an **attacker resource** (compress attack cost under a frame budget).
4. **Provenance / watermark / model-IP attacks**: A37010 (multi-embedding overwrite of forensic watermarks), A37117 (adaptive attacker vs. a model lock), A37426 (relearning/fine-tuning attack that reverses machine-unlearning).
5. **Verifier / gate evasion**: A37118 (semantics-preserving code perturbation flips an LM vulnerability detector's verdict → confused-deputy risk if an agent trusts it).
6. **Physical-world / sensor**: A37349, A37647, A37903, A37955, A38056 (crafted), plus A37792 (naturally-occurring camera-glass fracture reframed as an OOD/robustness stressor, no true adversary).

## Major defense families (this chunk)

- **In-training / data-side detection**: A37141 (DIFT — density-based poisoned-sample detection *during* contrastive pre-training, ~10 clean anchors/class, theoretically bounded density-collapse signature); A37116 (attacker-centric, LLM-assisted OSS supply-chain risk scoring — governance/CI/binary-concealment dimensions).
- **Certified / provable robustness**: A37716 (CertMask — attack-agnostic patch certificate at O(n) vs PatchCleanser's O(n²), up to +13.4% certified accuracy, bounded by a *known* patch-size assumption); A37117 (randomized-smoothing-fortified model lock, ℓ2-certified within the modeled radius).
- **Robust optimization / adversarial training**: A37396 (CBA-FAPT — regularize *internal cross-modal attribution* consistency, not just outputs); A37010 (AIS — simulate the overwrite attack during watermark fine-tuning).
- **Input-side filtering / purification**: A37389 (APD — β-VAE + graph-spectral prompt disentanglement, "detect-then-sanitize" firewall); A37474 (SATED — training-free MLLM-as-verifier patch localization + SAM masks + diffusion inpainting, with a **false-positive-aware** evaluation framework).
- **Provenance / capability-gating**: A37117 ("capability is not permission" — model utility gated on a hardware-derived trigger; leaked weights degrade to near-random); A37426 (ROVER — request-router + gradient-sink to make unlearning resistant to relearning).
- **Privacy-by-perturbation**: A37140 (IO-RAE — reversible adversarial audio; obfuscate content to ASR, losslessly recover for authorized parties).
- **Diagnostics**: A37615 (OTI — model-free, dual-use image-attackability screen).

## Strongest / best-supported findings

- **Availability is a first-class, under-defended property.** A37082 shows a single compromised participant inflates cooperative-perception latency **>90×** (>3 s/frame, 100% success on a real vehicle testbed under the evaluated setup), and that existing *integrity* defenses are structurally useless because they require detection outputs that never arrive. Strong evidence within its threat model (four CP models, multi-hardware, physical testbed, code released).
- **Certified patch defense can be made linear-cost.** A37716 provides formal necessary/sufficient coverage conditions and an attack-agnostic certificate; graded `strong` within the single-known-size-patch threat model.
- **"Distilled/condensed ≠ safe."** Two independent papers (A37119 digital, no-raw-data; A37349 clean-label physical) demonstrate dataset distillation as a *poisoning primitive*; A37119 reports a sub-minute, model-agnostic injection. Replicated conceptual finding across settings.
- **Transferable backdoors/AEs generalize across architectures via loss-landscape geometry.** A36964 (flat-minima triggers transfer cross-dataset; 80.1% cross-dataset ASR, 73.2% post-defense as reported) and A37912 (path-flatness) converge on the same mechanism from attack and geometry sides.
- **Label consistency + no-visible-trigger is not an integrity check.** A37349 (clean-label) and A38056 (invisible-until-UV) both defeat human/inspection-based auditing under their evaluated conditions.
- **Multimodal robustness does not compose from single-modality robustness.** A37388, A37396, A37436, A37442 independently find cross-modal coupling (joint image+text or cross-image attention) is the exploitable/hardenable surface.

## Conflicting / tension findings

- **"Black-box" claims vary wildly in strength.** A37647 is a genuinely strict query-only black box (no shared encoder). A37388 *claims* black-box but requires logits and text-embedding-space gradients (card flags contradiction). A37651/A37664/A37695/A38015 are "black-box on the victim" but **white/gray on a surrogate or the public encoder** — the pipeline is not black-box. Treat headline "black-box" labels skeptically; the tags below record the *victim* knowledge and note surrogate reliance.
- **Robustness–utility / robustness–imperceptibility trade-offs are universal but differently reported.** A37117 (σ↑ → certified robustness↑ but authorized accuracy 86.2%→73.9%), A37010 (λA↑ → MEA robustness↑ but PSNR/SSIM↓), A37119/A37349 (α trade-off between backdoor retention and benign accuracy). No paper escapes the trade-off; several report only a single operating point.
- **Temporal redundancy: robustness or liability?** A37479 argues SNN multi-timestep structure is *not* inherent robustness (early-stopping + membrane warm-up shortcuts). A37770 argues CTDG memory *dilutes* isolated perturbations (harder to poison) — yet still achieves ~29% avg degradation. Same "temporal aggregation" property cuts both ways depending on attack design.

## Defense bypasses / evasion demonstrated

- A36964 evades AC, Spectral Signature, ONION, KillBadCode, EliBadCode (code-specific + generic backdoor defenses) under cross-dataset shift, as reported.
- A37118 raises false-negative rate of deployed LM vulnerability detectors via coordinated lexical+syntax perturbation (26.05% avg ASR gain over baselines) — a **verifier-gaming** result directly relevant to agent code-review gates.
- A37010 shows standard robust watermarking (MBRS, HiDDeN) offers essentially no protection against a single re-embedding (avg BER 0.50% → 38.17%, several methods ≈ random).
- A37117 **honestly reports its own naive design is broken** by an adaptive trigger-inversion attacker, then fortifies with randomized smoothing (reversed-accuracy 9.25% ≈ clean 9.47% in the tested setting) — the most methodologically candid adaptive-attack treatment in the chunk.
- A37426 shows standard fine-tuning fully reverses machine-unlearning ("no resistance"), motivating gradient-isolation defenses.
- A38015 reports continued effectiveness against "mainstream backdoor defenses" (specific table truncated in the extract).

## Benchmark / evaluation limitations (recurring)

- **No adaptive-defense evaluation** is the single most common gap. The overwhelming majority of attack papers (A36961, A36964, A36999, A37119, A37388, A37420, A37436, A37442, A37647, A37651, A37664, A37695, A37770, A37903, A37912, A38013, A38015, A38056) evaluate only against *static/existing* defenses; an attacker- or defense-aware adaptive opponent is untested. A37117 and A37716 are the exceptions.
- **Truncated result tables** in the extracted text prevent independent verification of many headline numbers (A36961, A36964, A37119, A37141, A37442, A37647, A37695, A37716 "Table ??", A38015). Numbers are recorded as author-claimed, not verified.
- **Imperceptibility asserted, not measured**: multiple papers assert ℓ∞/perceptual stealth with no human study, LPIPS/SSIM, or ε disclosed (A36961, A37388, A37420, A37442, A37647). A37664 uses ε=32/255 (visible) yet frames it as an AE.
- **Narrow scope**: image-classification-only (A37015, A37651, A37664, A37912, A38013), two datasets / few models (A37420, A37436), single target string (A37647), 200 images (A37436). Physical claims often argued via citation, not demonstrated (A37479), or only summarized (A37647, A37955, A38056).
- **Undefined metrics / datasets**: A37388's per-task score is undefined (clean rows already 0.31–0.53); A37389's key test sets ("AdvPromptGen", "Novel Attack") are undescribed and results are figure-only with **no benign false-positive rate** — undercutting a prompt-firewall's central usability claim.
- **LLM-as-judge dependence**: A37420 (GPT-4o-mini correctness judge, bias unaudited); A37116 (unspecified LLM backend, itself promptable).

## Recurring implementation patterns

- **Surrogate-then-transfer** offline attack construction (no victim queries) — the default black-box recipe (A37420, A37436, A37651, A37664, A37695, A37912, A38013).
- **Gradient-conflict / multi-task resolution** when fusing modalities or objectives: A37436 (asymmetric PCGrad-style projection, treat text gradient as anchor), A37396 (cross-modal attribution alignment), A37903 (Schur-complement convexity test for cooperative point subsets).
- **Optimization-geometry exploitation**: flat minima (A36964), path flatness (A37912), manifold-tangent projection (A38013), algorithm-stability bounds (A37015).
- **Proxy/prototype-space partitioning** to avoid inter-trigger interference (A38015) — a genuinely new mechanism.
- **MLLM/foundation-model-as-component**: as verifier (A37474 SATED), as decoy-text generator (A37140), as risk scorer (A37116), as semantic anchor for durable AEs (A37664 uses frozen CLIP). Each *inherits the component's own attack surface* (prompt injection, hallucination) — flagged explicitly in A37474.
- **Data-distillation / trajectory-matching as an attack objective** (A37119, A37349).
- **Provenance / hash-pinning / attested-build** as the recommended mitigation for every supply-chain poisoning paper (A36961, A36964, A37119, A37349, A37770, A38015, A38056).

## Product / architecture implications (for the Origin/Guardian stack)

- **Supply chain of *agent tooling* is the most transferable lesson.** A37116 (attacker-centric OSS/CI risk scoring incl. social-engineering and unpinned-Action surfaces) and A38015 (one poisoned instruction-tuning pass → many independent trigger→behavior bindings via a public visual encoder) map directly onto securing MCP/skill/plugin registries and any encoder/model an agent auto-installs or fine-tunes on. Treat third-party corpora, distilled datasets, and public encoders as untrusted; require crypto-provenance/attestation and poisoned-sample scanning that tests for *multiple* coexisting backdoors, not one.
- **"Capability is not permission," enforced in weights.** A37117 demonstrates conditional utility gated on a hardware-derived credential with a *certified* robustness layer — a concrete instantiation of capability-gating and blast-radius limitation for leaked model weights (relevant to model-access-control / credential-broker framing).
- **Don't trust an ML/LLM gate as a hard security boundary.** A37118 (evadable vulnerability detectors) and A37474 (MLLM-verifier inherits prompt-injection/hallucination risk) argue for defense-in-depth: pair any LM/MLLM gate with execution/dynamic checks, human approval for high-risk actions, and rate-limiting/query-monitoring to raise query-based-search cost.
- **Availability is a safety property.** A37082/A37479 show any super-linear pipeline stage or hard real-time deadline is an attack surface; bound worst-case per-message compute, isolate per-sender cost in multi-agent fusion, and treat timeliness SLAs as defended, not assumed.
- **Cross-image / cross-modal attention is an untrusted-influence channel.** A37442 (one poisoned image corrupts co-presented clean images, order-invariant) → for agents browsing the web / doing RAG over image galleries, per-image sanitization is insufficient; isolate trust domains before joint attention.
- **Physical perception for embodied agents**: query-only printable patches (A37647), naturalistic ghost-object creation (A37955), conditionally-visible triggers (A38056), and sensor-fault OOD (A37792) all argue for cross-sensor corroboration, sensor-health monitoring, and confidence-plus-consistency (not confidence-alone) gating.
- **Evidence-logging / rollback** recurs as the incident story for every poisoning paper: log training-data/dataset/backbone provenance and hashes so a discovered backdoor is traceable and a clean checkpoint is restorable.

## Open problems (as stated or clearly implied)

- **Loss-landscape-geometry-aware defenses** against transferable/flat-minima backdoors and AEs (A36964's own call; echoed by A37912/A38013).
- **Adaptive-attacker-hardened** versions of nearly every defense here (A37141 density-evasion, A37389 VAE/graph-evasion, A37426 threshold-boundary evasion, A37474 semantics-coherent patches, A37716 unknown/multiple patch sizes).
- **Certification beyond narrow threat models**: known-single-patch-size (A37716), ℓ2-bounded triggers (A37117), single embedding round (A37010).
- **Multimodal / generative-LLM robustness** with defined metrics and benign-FPR budgets (A37388/A37389 gaps).
- **Durable / update-surviving adversarial inputs** (A37664 shows AEs can persist across continual-learning updates — retraining is not an implicit defense).
- **Distilled-dataset / condensed-artifact integrity** as a new benchmark axis (A37119, A37349).

## Most load-bearing papers (by id)

- **A38015 (MTAttack)** — most agent-security-relevant *attack*: realistic gray-box LVLM instruction-tuning supply-chain backdoor, multi-target via proxy-space partitioning, preserved clean-task fidelity; `moderate` evidence (truncated tables, no proxy-space-aware adaptive defense).
- **A37116 (OSS supply-chain risk framework)** — attacker-centric, LLM-assisted risk scoring incl. social-engineering/CI surfaces; directly transferable to agent tool/skill/plugin supply-chain hardening; `moderate` (case-study-validated, no labeled benchmark).
- **A37117 (Authority Backdoor)** — the chunk's cleanest adaptive-attack methodology and a concrete "capability-gated-in-weights + certified robustness" pattern for model-access-control; `moderate`.
- **A37082 (CP-FREEZER)** — strongest-evidence attack in the chunk and the clearest availability/latency threat for multi-agent/collaborative pipelines; `strong` (within its white-box CP threat model).
- **A37716 (CertMask)** — the only `strong` *defense*: attack-agnostic, O(n) certified patch robustness with formal proofs; a reusable runtime-guarantee pattern (bounded by known-patch-size).
- **A37442 (LAMP)** — defines the multi-image-MLLM cross-image "contagion" attack surface directly relevant to web-browsing / RAG agents; `moderate` (truncated experimental tables).

Honorable mention: **A37118 (HogVul)** for the verifier-gaming / confused-deputy lesson on trusting an LM security gate, and **A37389 (APD)** as the only direct prompt-injection/jailbreak defense (but `preliminary` — undescribed datasets, no benign-FPR, no adaptive test).

---
Evidence-integrity note: every metric above is reported as it appears in the corresponding research card, labeled author-claim where the card so labels it; several headline numbers sit in table regions marked truncated in the extracted text and are therefore not independently verified. No titles, datasets, or numbers were invented; where a card said a value was absent, it is not asserted here.
