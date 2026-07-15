# Partial Synthesis — Deepfake-Forgery-Detection, chunk 0 (13 papers)

Papers: A37071, A37334, A37421, A37473, A37553, A37865, A37945, A38060, A40886, A40907, A40928, A41234, A41525. All AAAI-26 (2026). This chunk is synthetic-media forensics: AI-generated-image (AIGI) detection, face-forgery detection, face anti-spoofing, audio deepfake detection, temporal audio-visual forgery localization, one proactive-protection method, and one K-12 education artifact. Scope note (reviewer synthesis): this is a *content-authenticity / provenance* area adjacent to agent security, not LLM prompt/tool/MCP security. Findings feed the "evidence base" an agent consumes, not the agent's own execution surface.

## Dominant threat models
- **Distribution shift reframed as the adversary, not an adaptive attacker.** 12 of 13 papers explicitly state a *non-adaptive* threat model: the "adversary" is the space of generators (unseen models, unseen forgery types, unseen datasets), and robustness is measured as *generalization*, not adversarial evasion (stated for A37071, A37334, A37421, A37473, A37553, A37865, A37945, A38060, A40886, A40907, A40928, A41234). Adversary knowledge is effectively black-box (no detector-internal access) in all detection papers.
- **The one adaptive/physical exception is pedagogical.** A41525 (Breakable Machine) is the only paper with an adaptive attacker — a human learner iteratively spoofing a MobileNet-V2 classifier in the *physical world* (props, lighting, background) guided by CAM saliency and training-data inspection; targeted, gray/white-box in effect. It is an AI-literacy resource, not a detection/defense method (reviewer classification: peripheral to security).
- **Phase.** Detection runs at inference/deployment on already-generated content (most papers). Training-time defenses: A37334 (RL curriculum augmentation), A37553 (paired-compressed subset), A37473 (prototype bank built at training). Pre-distribution protection: A37865 (owner embeds a protective perturbation before the image circulates).
- **Digital vs physical.** Digital for all synthetic-media detectors. Physical for A37945 (physical presentation/spoof artifacts captured as images) and A41525 (physical-world classifier spoofing). Environmental (non-adversarial) corruption — OSN JPEG compression, Gaussian noise — is modeled by A37553 and A37421 but as distribution shift, not as an anti-forensic attacker.

## Major attack families
- **Synthetic image generation** (GAN, diffusion, and emerging VAR/autoregressive): A37071, A37421, A37553, A38060, A40886, A41234.
- **Face forgery / deepfakes** (face-swap, reenactment, entire-face synthesis, face editing): A37334, A37473.
- **Audio deepfakes** across speech / sound / singing voice / music (TTS, VC, SVS/SVC, text-to-music): A40907.
- **Temporal audio-visual forgery** — sparse, boundary-ambiguous manipulated segments in talking-face video: A40928.
- **AIGC tampering / inpainting / compositing** of distributed images: A37865.
- **Presentation / spoofing attacks** on face authentication (print, replay, 3D/paper masks, glasses, makeup — 12 unified types): A37945.
- **Physical-world evasion** of a deployed classifier (embodied, not pixel-space): A41525.
- **Post-processing as an anti-forensic-adjacent corruption** (compression, noise) is a recurring *complication*, most directly A37553 (OSN compression erasing high-frequency forgery traces) and A37421 (JPEG/Gaussian). Reviewer synthesis across nearly every card: true *adaptive* anti-forensics (an attacker optimizing against the specific detector) is **not evaluated** anywhere in this chunk.

## Major defense families
- **Passive detection via generalization-oriented representation learning** (the dominant family): internal-inconsistency / discrepancy learning (A37071 dual-branch asymmetric discrepancy); CLIP visual-language residual prototypes (A37473); decision-driven orthogonal decoupling of compression from the decision axis (A37553); diffusion-timestep-ensembled features (A38060); GAN-vs-DM architectural clustering (A40886); real-only representation learning with feature-space pseudo-negatives (A41234); wavelet prompt tuning for type-invariant audio cues (A40907); deformable state-space localization (A40928).
- **Training-time robustness engineering:** RL-scheduled curriculum data augmentation + IRM (A37334).
- **MLLM/VLM-as-verifier with human-readable explanations:** in-the-wild reasoning detector with adaptive-compute (A37421); explainable synthetic-image detection with metric-grounded MLLM refinement (A38060); explainable face anti-spoofing MLLM with detect+type+reason+localize (A37945).
- **Proactive / active forensics:** A37865 inverts adversarial fragility — a frequency-aware ℓ∞ perturbation forces SAM from "segment anything" to "segment nothing" so any later edit shows up as an anomalous segmentation ("blank canvas"), enabling training-free tamper localization. This is the closest thing in the chunk to a watermarking/attestation-style provenance control.
- **Fingerprinting / attribution:** A40886's unsupervised clusters recover the generating architecture family (GAN vs DM) without generator labels.
- **Red-teaming-as-pedagogy:** A41525 (not a deployable control).

## Strongest replicated findings
- **Cross-generator / cross-type / cross-dataset generalization is the central, replicated failure mode.** Single-source detectors overfit generator-specific surface artifacts and collapse on unseen generators or forgery types (demonstrated under the evaluated threat models of A37071, A37334, A37421, A37473, A37553, A40886, A40907, A41234). A40907 quantifies it starkly: single-type audio countermeasures drop to near-chance EER (~30–50%) on unseen types, versus 3.58% average EER for the all-type co-trained model (author-reported).
- **Treating the "fake" class as internally structured (non-monolithic) improves generalization.** Pattern-coexistence duality within a fake image (A37071), GAN-vs-DM architectural sub-clusters (A40886), and residual/real-only representations decoupled from semantics (A37473, A41234) are independent instantiations of the same inductive bias.
- **Frequency-domain cues are load-bearing across modalities.** High-frequency / wavelet / spectral features recur as the discriminative signal: A37071 (multi-scale), A37553 (high-frequency forgery traces), A37865 (Daubechies-8 DWT), A40907 (type-invariant cue concentrated in the HH wavelet band, author-reported), A41234 (DFT amplitude), A38060 (Fourier power-spectrum discrepancies across DDIM timesteps).
- **MLLM/VLM-generated forensic explanations are unreliable on their own.** A38060 measured up to 67.4% of MLLM-identified flaws as incorrect (author-reported), motivating a metric-grounded refinement gate; A37421 documents "overthinking" on easy fakes; reviewers flag rationale *faithfulness* (fluency ≠ causal correctness) for A37421, A37945, and A38060. Consensus design move: gate/verify explanations before surfacing them.

## Conflicting findings
- **No head-to-head contradictions** (these are parallel detectors, not competing claims about the same measurement). The real tension is **setting-dependence of "SOTA":** high headline numbers (A40886 GenImage avg AUC 0.9882; A38060 98.91% original / 95.89% hard; A37945 intra-dataset ACC 99.41) coexist with much weaker absolute performance in harder or more realistic settings (A37071 ~57–58% on Chameleon despite GenImage SOTA; A37553 ~75% mean under OSN compression; A37421 ~78.46% OOD; A37945 Replay-Attack cross-dataset HTER 20.07). Reviewer synthesis: averaged SOTA can mask near-chance behavior on the hardest in-the-wild benchmarks.
- **Defense-vs-defense contrast on compression handling:** A37553 documents that the prior gradient-reversal approach *removes overlapping forgery features along with compression features* (a documented failure it replaces with orthogonal decoupling) — a within-literature correction rather than a contradiction among these 13.

## Defense bypasses
- **No paper demonstrates a bypass of another paper's method.** The only *demonstrated* attack in the chunk is A41525's physical-world spoofing of a MobileNet-V2 classifier — and that is a teaching classifier, not a defense from this set.
- **Reviewer-identified (untested) bypass surfaces**, consistently flagged as the shared blind spot:
  - A37865: stripping / denoising / recompressing / regenerating the image could remove the ℓ∞ protective perturbation and defeat the blank-canvas state; the tamper localization is also tied to a specific SAM version (verifier-model change may break it). Not evaluated against these.
  - A37473 (prototype memory bank) and A41234 (RPE noise-residual features): reviewer-noted poisoning / normalization blind spots — heavy denoising or recompression that alters noise statistics is an untested plausible failure.
  - A37421: confidence-based adaptive-compute gating could be gamed by an adversary crafting high-confidence-but-wrong "impressions"; untested.
  - A37071: no evaluation against post-processing (JPEG, blur, adversarial perturbation) crafted to suppress the inter-branch discrepancy.
- Calibrated takeaway: every detector here should be treated as demonstrated under a *non-adaptive, distribution-shift* threat model; adaptive-adversary robustness **requires production validation** and is currently unestablished for the chunk.

## Benchmark / eval limitations
- **Averaged metrics hide per-generator / per-type failure** (A37071 Chameleon; A40886, A40907 per-type/per-generator breakdowns matter).
- **Borrowed baseline numbers not re-run under identical preprocessing** (A37473, A37553), so cross-method superiority assumes preprocessing parity.
- **Per-subset training inflates the generalization framing:** A38060 trains one model per GenImage subset (not one universal detector), a caveat for its averaged accuracy.
- **Proprietary / anonymized data limits reproducibility:** A37421 human-curated sources A/B are anonymized.
- **Explanation "correctness" measured by text-image similarity or BLEU/ROUGE, not human ground truth** (A38060, A37945, A37421) — measures fluency/overlap, not causal fidelity.
- **Scope narrowing bounds external validity:** A40907 evaluates clean audio only (no channel noise, compression, or partial spoofing, author-stated); A40928 uses only two AV benchmarks; several sub-tasks in A37945 are intra-dataset only.
- **Truncated extracted text** left concrete numbers unverifiable in this review for A37334, A37865, and parts of A41234 (recorded as "not stated in paper" where absent).
- **Universal gap: no adaptive-adversary / anti-forensic evaluation** in any of the 13 (A41525's attack is pedagogical, not a robustness test of a defense).

## Recurring implementation patterns
- **Frozen foundation backbone + lightweight adapter/prompt/head** is the dominant build: CLIP ViT (A37473, A38060, A40886), SSL audio front-end + AASIST (A40907), Siglip + Phi-3 with LoRA (A37945), off-the-shelf SAM (A37865), pretrained ViT (A37553), frozen AV backbones (A40928). Parameter-efficient tuning is common (prompt tuning — A40907 reports ~458× fewer trainable parameters than full fine-tuning, author-reported; LoRA — A37421, A37945).
- **Dual-branch / complementary-feature fusion:** A37071 (weight-independent dual branches), A37553 (ViT low-freq + CNN high-freq, bidirectional update — ablation shows this fusion is the single most critical component, +7.4), A41234 (restorer + discriminator).
- **Frequency-domain preprocessing (DWT / DFT / wavelet / Fourier):** A37071, A37553, A37865, A40907, A41234, A38060.
- **Fast-verdict + reflective / adaptive-compute escalation** ("cheap check first, deep check when confidence is low"): A37421 (adaptive Heuristic-to-Analytic reasoning), A38060 (MLLM explanation → metric-guided Top-K refinement loop).
- **Stateful memory / prototype banks with decay + replacement:** A37473 (gradient-aware residual prototypes, capacity 64/class, score-decay γ=0.99).
- **Multi-task consolidation (detect + type + reason + localize):** A37945; segment/region localization: A37865, A40928.
- **Two-stage training (align/pretrain then SFT/RL):** A37421 (SFT cold-start → RLVR/GRPO), A37945 (continual pretraining → visual-instruction SFT), A41234 (adversarial-denoising RPE pretraining → discriminator).
- **Released code** for A37071, A37421, A37865, A37945, A38060, A41525; code availability *not stated in the extracted text* for A37334, A37473, A37553, A40886, A40907, A40928, A41234.

## Product / architecture implications (Guardian / agent stack)
- **Use any single detector as one probabilistic evidence signal, never as an authoritative gate.** Every deployment-implications section reaches this conclusion; combine detection with cryptographic provenance (C2PA-style), watermarking, and human review for high-stakes decisions (A37071, A37865).
- **The verifier-loop pattern generalizes directly to guardrails:** a fast proposer plus a confidence-gated reflective verifier with adaptive compute (A37421, A38060) is the cheap-check-then-deep-check escalation shape a Guardian Agent can reuse.
- **Gate explanations before surfacing them.** MLLM rationale faithfulness is unverified and empirically unreliable (A38060's ≤67.4% incorrect-flaw finding); anchor explanations to a verifiable taxonomy + quantitative scoring, and keep a human in the loop before action.
- **Proactive/active forensics (A37865) is an attestation/watermarking analogue** worth considering for owner-controlled assets, but its trust rests on the protective perturbation surviving the distribution channel and on pinning the verifier model (SAM) version — production validation required.
- **Stateful detector surfaces need their own governance:** prototype banks (A37473) and noise-residual models (A41234) introduce drift and poisoning risk that must be bounded, logged, and monitored.
- **Instrument for time-bounded generalization:** log confidence, impression-vs-final disagreement, prototype turnover, and localization masks as audit records; monitor OOD accuracy / EER drift as new generators appear (generalization is empirical and expires as generators evolve — A40886's fixed GAN/DM K=2 assumption is an explicit example of a bias that new architecture families like VAR can break).
- **Identity/authorization tie-in:** A37945 positions face anti-spoofing as one authentication gate with escalation to human review — directly relevant to identity/authz components, with the caveat that generated reasoning must not be trusted as ground truth.

## Open problems
- **Adaptive / anti-forensic robustness is essentially unmeasured** across the entire chunk — the largest gap for any *security* (vs accuracy) use.
- **Time-bounded generalization to genuinely new generator paradigms** (e.g., VAR/autoregressive beyond the GAN/DM dichotomy; A40886, A41234) — inductive biases baked for two families may not transfer.
- **Faithful, independently-verifiable explanations** (not fluency-scored) for human-in-the-loop forensic review (A37421, A37945, A38060).
- **Robustness to real distribution channels** — compression, denoising, resizing, screenshotting, regeneration — partially addressed as environmental corruption (A37553, A37421) but never as an adaptive attack; perturbation survivability is untested for A37865.
- **Cross-modality unification** remains absent — image, audio, and audio-visual detectors are siloed (A38060/A40886/A41234 vs A40907 vs A40928).
- **Reliable generator/architecture attribution** is suggested (A40886) but not independently validated.

## Most load-bearing papers (this chunk)
1. **A37421 (MIRAGE / MIRAGE-R1)** — the most transferable architecture lesson: an in-the-wild, domain-bias-controlled benchmark plus a VLM verifier-loop with confidence-gated adaptive compute and corruption-robustness testing; released code.
2. **A38060 (ESIDE)** — strongest evidence on explanation-trust: diffusion-timestep detection paired with the quantified finding that standalone MLLM explanations are unreliable (≤67.4% incorrect), motivating a metric-grounded refinement gate; released code + datasets.
3. **A40886 (TriDetect)** — the clearest generalization theory (GAN JS-divergence vs DM KL-divergence artifact families) and the "fake-class-as-multimodal" inductive bias; broad eval (5 datasets, 13 baselines), highest reported AUC in the chunk, plus an attribution angle.
4. **A41234 (RealNet)** — the most future-proofing paradigm: real-only training with feature-space pseudo-negatives, evaluated across GAN/diffusion/VAR and a safety-critical medical distribution shift, at low compute.
5. **A37865 (Blank Canvas)** — the only proactive/active-forensic control in the chunk (adversarial-perturbation → SAM tamper localization), a distinct provenance/attestation primitive despite preliminary (truncated-numbers) evidence.
6. **A37553 (DDOC)** — the most realistic environmental-robustness setting (OSN compression) and a transferable design principle: *orthogonalize the nuisance to the decision axis instead of deleting it*.

(A37945 FaceShield is a close seventh — load-bearing for the identity/authz + physical-presentation-attack angle and the detect-type-reason-localize consolidation pattern.)
