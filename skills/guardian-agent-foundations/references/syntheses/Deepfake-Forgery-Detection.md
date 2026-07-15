# Synthesis — Deepfake-Forgery-Detection

Corpus: 13 papers, all AAAI-26 (2026): A37071, A37334, A37421, A37473, A37553, A37865, A37945, A38060, A40886, A40907, A40928, A41234, A41525. Merged from one partial synthesis (chunk 0). Weighting favors experimental quality, reproducibility, threat-model realism, and independent replication over paper count. Throughout, "direct paper finding" marks values reported by the paper's authors; "reviewer synthesis" marks cross-paper inference added during review. Numbers are author-reported unless stated otherwise. Where a value was absent or truncated in the reviewed text it is written "not stated in paper."

---

## 1. Executive summary

This category is **synthetic-media forensics / content-authenticity**, not agent-execution security. The 13 papers cover AI-generated-image (AIGI) detection, face-forgery detection, face anti-spoofing, audio deepfake detection, temporal audio-visual forgery localization, one proactive image-protection method, and one K-12 AI-literacy artifact. Reviewer-synthesis framing: these methods produce an *evidence signal an agent consumes*, not a control on the agent's own tool/skill/MCP surface.

The dominant and most strongly replicated result across the corpus is that **cross-generator / cross-type / cross-dataset generalization is the central failure mode**: detectors trained on one generator family overfit generator-specific surface artifacts and collapse on unseen generators, demonstrated across many papers under their evaluated (non-adaptive) threat models. Two convergent inductive biases recur as fixes — treating the "fake" class as internally structured rather than monolithic, and leaning on frequency-domain cues — arrived at independently across image and audio modalities.

A second cross-cutting result concerns **explanation trust**: MLLM/VLM-generated forensic rationales are empirically unreliable on their own (A38060 measured up to 67.4% of MLLM-identified flaws as incorrect, direct paper finding), motivating a consensus design move to gate/verify explanations against a metric or taxonomy before surfacing them.

The single largest gap, flagged consistently by reviewers, is that **adaptive / anti-forensic robustness is essentially unmeasured** across the entire corpus — the one demonstrated adaptive attack (A41525) is a teaching classifier, not a defense from this set. Every detector here should be read as demonstrated under a non-adaptive, distribution-shift threat model; adaptive-adversary robustness requires production validation and is currently unestablished.

For the Guardian / agent stack, the actionable primitives are: use any single detector as one probabilistic evidence signal (never an authoritative gate); reuse the fast-proposer-plus-confidence-gated-reflective-verifier pattern (A37421, A38060) as a cheap-check-then-deep-check escalation shape; gate explanations before action; and treat stateful detector components (prototype banks, noise-residual models) as governed surfaces with drift/poisoning risk.

---

## 2. Scope and boundaries

- **In scope:** passive detection of synthetic/forged media (image, audio, audio-visual); face anti-spoofing / presentation-attack detection; proactive owner-side image protection; generator/architecture attribution; forensic explanation generation and its verification.
- **Adjacent, not central (reviewer classification):** this is a content-authenticity / provenance area adjacent to agent security, not LLM prompt/tool/MCP security. Findings feed the evidence base an agent consumes, not the agent's own execution surface.
- **Peripheral (reviewer classification):** A41525 (Breakable Machine) is an AI-literacy education resource, not a detection or defense method; it is the corpus's only adaptive, physical-world attacker but contributes pedagogy rather than a deployable control.
- **Modalities:** image (A37071, A37421, A37473, A37553, A37865, A38060, A40886, A41234), face/presentation (A37334, A37473, A37945), audio (A40907), audio-visual (A40928), physical-world classifier (A41525).
- **Deployment phase:** most methods run at inference on already-generated content; a minority act at training time (A37334, A37473, A37553) or pre-distribution (A37865, owner embeds protection before circulation).
- **Cross-modality unification is absent** — image, audio, and audio-visual detectors are siloed (reviewer synthesis).

---

## 3. Dominant threat models

- **Distribution shift reframed as the adversary (non-adaptive).** 12 of 13 papers explicitly adopt a non-adaptive threat model: the "adversary" is the space of generators (unseen models, unseen forgery types, unseen datasets), and robustness is measured as *generalization*, not adversarial evasion (stated for A37071, A37334, A37421, A37473, A37553, A37865, A37945, A38060, A40886, A40907, A40928, A41234). Adversary knowledge is effectively black-box (no detector-internal access) across the detection papers.
- **One adaptive/physical exception, pedagogical.** A41525 is the only paper with an adaptive attacker — a human learner iteratively spoofing a MobileNet-V2 classifier in the physical world (props, lighting, background) guided by CAM saliency and training-data inspection; targeted, effectively gray/white-box. It is an AI-literacy resource, not a detection/defense method.
- **Environmental (non-adversarial) corruption.** OSN JPEG compression and Gaussian noise are modeled by A37553 and A37421, but as distribution shift, not as an anti-forensic attacker.
- **Digital vs physical.** Digital for all synthetic-media detectors; physical for A37945 (physical presentation/spoof artifacts captured as images) and A41525 (physical-world classifier spoofing).
- **Reviewer-synthesis caveat (recurring across nearly every card):** true *adaptive* anti-forensics — an attacker optimizing against the specific detector — is **not evaluated** anywhere in this corpus.

---

## 4. Major attack families

- **Synthetic image generation** (GAN, diffusion, and emerging VAR/autoregressive): A37071, A37421, A37553, A38060, A40886, A41234.
- **Face forgery / deepfakes** (face-swap, reenactment, entire-face synthesis, face editing): A37334, A37473.
- **Audio deepfakes** across speech / sound / singing voice / music (TTS, VC, SVS/SVC, text-to-music): A40907.
- **Temporal audio-visual forgery** — sparse, boundary-ambiguous manipulated segments in talking-face video: A40928.
- **AIGC tampering / inpainting / compositing** of distributed images: A37865.
- **Presentation / spoofing attacks** on face authentication (print, replay, 3D/paper masks, glasses, makeup — 12 unified types): A37945.
- **Physical-world evasion** of a deployed classifier (embodied, not pixel-space): A41525.
- **Post-processing as an anti-forensic-adjacent corruption** (compression, noise): a recurring complication, most directly A37553 (OSN compression erasing high-frequency forgery traces) and A37421 (JPEG/Gaussian). Reviewer synthesis: genuine adaptive anti-forensics is not evaluated in the corpus.

---

## 5. Major defense families

- **Passive detection via generalization-oriented representation learning (dominant family):** internal-inconsistency / discrepancy learning (A37071 dual-branch asymmetric discrepancy); CLIP visual-language residual prototypes (A37473); decision-driven orthogonal decoupling of compression from the decision axis (A37553); diffusion-timestep-ensembled features (A38060); GAN-vs-DM architectural clustering (A40886); real-only representation learning with feature-space pseudo-negatives (A41234); wavelet prompt tuning for type-invariant audio cues (A40907); deformable state-space temporal localization (A40928).
- **Training-time robustness engineering:** RL-scheduled curriculum data augmentation + IRM (A37334).
- **MLLM/VLM-as-verifier with human-readable explanations:** in-the-wild reasoning detector with adaptive compute (A37421); explainable synthetic-image detection with metric-grounded MLLM refinement (A38060); explainable face anti-spoofing MLLM with detect+type+reason+localize (A37945).
- **Proactive / active forensics:** A37865 inverts adversarial fragility — a frequency-aware ℓ∞ perturbation forces SAM from "segment anything" to "segment nothing" so any later edit shows up as anomalous segmentation ("blank canvas"), enabling training-free tamper localization; the corpus's closest analogue to a watermarking/attestation provenance control.
- **Fingerprinting / attribution:** A40886's unsupervised clusters recover the generating architecture family (GAN vs DM) without generator labels.
- **Red-teaming-as-pedagogy:** A41525 (not a deployable control).

---

## 6. Most influential concepts

- **Generalization-as-robustness.** Robustness is reframed as cross-generator / cross-type / cross-dataset generalization rather than adversarial evasion — the organizing concept of the corpus (reviewer synthesis over 12 papers).
- **The "fake" class as internally structured, not monolithic.** Pattern-coexistence duality within a fake image (A37071), GAN-vs-DM architectural sub-clusters (A40886), and residual/real-only representations decoupled from semantics (A37473, A41234) are independent instantiations of the same inductive bias (reviewer synthesis).
- **Real-only modeling.** Learn the manifold of authentic content and treat deviations as fake, with feature-space pseudo-negatives (A41234) — a future-proofing paradigm that does not require enumerating generators.
- **Frequency-domain cues as load-bearing signal** across modalities: high-frequency / wavelet / spectral features recur as the discriminative signal (A37071, A37553, A37865, A38060, A40907, A41234).
- **Orthogonalize the nuisance to the decision axis instead of deleting it** (A37553) — a transferable design principle for handling compression/corruption without destroying forensic signal.
- **Proactive forensics by inverting adversarial fragility** (A37865) — use adversarial perturbation defensively as an owner-controlled tamper tripwire.
- **Fast-verdict + confidence-gated reflective escalation** (A37421, A38060) — cheap check first, deep check when confidence is low; directly transferable to guardrail verifier loops (reviewer synthesis).
- **Explanations must be gated/verified, not trusted** — anchor rationales to a verifiable taxonomy and quantitative scoring rather than accepting fluent MLLM output (A38060, A37421, A37945).

---

## 7. Common datasets and benchmarks

Only datasets explicitly named in the reviewed text are listed; others are marked as unstated to preserve evidence integrity.

- **GenImage** — AIGI detection benchmark used by A37071, A38060, A40886 (A40886 GenImage average AUC 0.9882; A38060 trains one model per GenImage subset).
- **Chameleon** — harder in-the-wild AIGI benchmark; A37071 reports ~57–58% on Chameleon despite GenImage SOTA.
- **Replay-Attack** — face anti-spoofing cross-dataset benchmark; A37945 reports cross-dataset HTER 20.07.
- **A40886** evaluates over 5 datasets against 13 baselines; the specific dataset names are not stated in the reviewed text.
- **A40928** uses two audio-visual benchmarks; names not stated in the reviewed text.
- **A40907** spans speech / sound / singing-voice / music audio types (clean audio only); specific corpus names not stated in the reviewed text.
- **A37421** uses human-curated in-the-wild sources labeled A/B that are anonymized (limits reproducibility).
- Dataset names for A37334, A37473, A37553, A41234 not stated in the reviewed text.

---

## 8. Evaluation metrics

- **AUC** — A40886 (GenImage avg 0.9882).
- **Accuracy (ACC)** — A38060 (98.91% original / 95.89% hard subset); A37945 (intra-dataset 99.41); A37421 (~78.46% OOD accuracy).
- **EER (Equal Error Rate)** — A40907 (single-type ~30–50% on unseen types near chance; all-type co-trained 3.58% average).
- **HTER (Half Total Error Rate)** — A37945 (Replay-Attack cross-dataset 20.07).
- **Explanation-quality proxies** — text-image similarity, BLEU/ROUGE overlap (A38060, A37945, A37421); reviewer caveat: these measure fluency/overlap, not causal fidelity or human ground truth.
- **Localization** — segmentation/region masks (A37865 tamper localization; A40928 temporal boundary localization); specific numeric metrics not stated in the reviewed text.
- Concrete headline numbers were truncated/unverifiable in the reviewed text for A37334, A37865, and parts of A41234 (recorded "not stated in paper").

---

## 9. Strongest replicated findings

- **Cross-generator / cross-type / cross-dataset generalization is the central, replicated failure mode.** Single-source detectors overfit generator-specific surface artifacts and collapse on unseen generators or forgery types (demonstrated under the evaluated threat models of A37071, A37334, A37421, A37473, A37553, A40886, A40907, A41234). A40907 quantifies it starkly: single-type audio countermeasures drop to near-chance EER (~30–50%) on unseen types, versus 3.58% average EER for the all-type co-trained model (direct paper finding).
- **Treating the "fake" class as internally structured improves generalization.** Pattern-coexistence duality (A37071), GAN-vs-DM architectural sub-clusters (A40886), and residual/real-only representations decoupled from semantics (A37473, A41234) are independent instantiations of the same inductive bias (reviewer synthesis over four papers).
- **Frequency-domain cues are load-bearing across modalities.** High-frequency / wavelet / spectral features recur as the discriminative signal: A37071 (multi-scale), A37553 (high-frequency forgery traces), A37865 (Daubechies-8 DWT), A40907 (type-invariant cue concentrated in the HH wavelet band, direct paper finding), A41234 (DFT amplitude), A38060 (Fourier power-spectrum discrepancies across DDIM timesteps).
- **MLLM/VLM-generated forensic explanations are unreliable on their own.** A38060 measured up to 67.4% of MLLM-identified flaws as incorrect (direct paper finding), motivating a metric-grounded refinement gate; A37421 documents "overthinking" on easy fakes; reviewers flag rationale faithfulness (fluency ≠ causal correctness) for A37421, A37945, and A38060. Consensus design move: gate/verify explanations before surfacing them.

---

## 10. Conflicting findings

- **No head-to-head contradictions.** These are parallel detectors, not competing claims about the same measurement.
- **The real tension is setting-dependence of "SOTA."** High headline numbers (A40886 GenImage avg AUC 0.9882; A38060 98.91% original / 95.89% hard; A37945 intra-dataset ACC 99.41) coexist with much weaker absolute performance in harder or more realistic settings (A37071 ~57–58% on Chameleon despite GenImage SOTA; A37553 ~75% mean under OSN compression; A37421 ~78.46% OOD; A37945 Replay-Attack cross-dataset HTER 20.07). Reviewer synthesis: averaged SOTA can mask near-chance behavior on the hardest in-the-wild benchmarks.
- **Defense-vs-defense contrast on compression handling.** A37553 documents that the prior gradient-reversal approach removes overlapping forgery features along with compression features (a documented failure it replaces with orthogonal decoupling) — a within-literature correction rather than a contradiction among these 13.

---

## 11. Defense bypasses

- **No paper demonstrates a bypass of another paper's method.** The only demonstrated attack in the corpus is A41525's physical-world spoofing of a MobileNet-V2 classifier — and that is a teaching classifier, not a defense from this set.
- **Reviewer-identified (untested) bypass surfaces**, the shared blind spot:
  - **A37865:** stripping / denoising / recompressing / regenerating the image could remove the ℓ∞ protective perturbation and defeat the blank-canvas state; tamper localization is also tied to a specific SAM version (a verifier-model change may break it). Not evaluated against these.
  - **A37473** (prototype memory bank) and **A41234** (RPE noise-residual features): reviewer-noted poisoning / normalization blind spots — heavy denoising or recompression that alters noise statistics is an untested plausible failure.
  - **A37421:** confidence-based adaptive-compute gating could be gamed by an adversary crafting high-confidence-but-wrong "impressions"; untested.
  - **A37071:** no evaluation against post-processing (JPEG, blur, adversarial perturbation) crafted to suppress the inter-branch discrepancy.
- **Calibrated takeaway:** every detector here should be treated as demonstrated under a non-adaptive, distribution-shift threat model; adaptive-adversary robustness **requires production validation** and is currently unestablished for the corpus.

---

## 12. Known benchmark limitations

- **Averaged metrics hide per-generator / per-type failure** (A37071 Chameleon; A40886 and A40907 per-type/per-generator breakdowns matter).
- **Borrowed baseline numbers not re-run under identical preprocessing** (A37473, A37553), so cross-method superiority assumes preprocessing parity.
- **Per-subset training inflates the generalization framing:** A38060 trains one model per GenImage subset (not one universal detector), a caveat on its averaged accuracy.
- **Proprietary / anonymized data limits reproducibility:** A37421 human-curated sources A/B are anonymized.
- **Explanation "correctness" measured by text-image similarity or BLEU/ROUGE, not human ground truth** (A38060, A37945, A37421) — measures fluency/overlap, not causal fidelity.
- **Scope narrowing bounds external validity:** A40907 evaluates clean audio only (no channel noise, compression, or partial spoofing, direct paper statement); A40928 uses only two AV benchmarks; several sub-tasks in A37945 are intra-dataset only.
- **Truncated extracted text** left concrete numbers unverifiable in this review for A37334, A37865, and parts of A41234 (recorded "not stated in paper" where absent).
- **Universal gap:** no adaptive-adversary / anti-forensic evaluation in any of the 13 (A41525's attack is pedagogical, not a robustness test of a defense).

---

## 13. Implementation patterns

- **Frozen foundation backbone + lightweight adapter/prompt/head** (dominant build): CLIP ViT (A37473, A38060, A40886), SSL audio front-end + AASIST (A40907), Siglip + Phi-3 with LoRA (A37945), off-the-shelf SAM (A37865), pretrained ViT (A37553), frozen AV backbones (A40928). Parameter-efficient tuning is common — prompt tuning (A40907 reports ~458× fewer trainable parameters than full fine-tuning, direct paper finding); LoRA (A37421, A37945).
- **Dual-branch / complementary-feature fusion:** A37071 (weight-independent dual branches); A37553 (ViT low-freq + CNN high-freq, bidirectional update — ablation shows this fusion is the single most critical component, +7.4); A41234 (restorer + discriminator).
- **Frequency-domain preprocessing (DWT / DFT / wavelet / Fourier):** A37071, A37553, A37865, A38060, A40907, A41234.
- **Fast-verdict + reflective / adaptive-compute escalation** ("cheap check first, deep check when confidence is low"): A37421 (adaptive Heuristic-to-Analytic reasoning), A38060 (MLLM explanation → metric-guided Top-K refinement loop).
- **Stateful memory / prototype banks with decay + replacement:** A37473 (gradient-aware residual prototypes, capacity 64/class, score-decay γ=0.99).
- **Multi-task consolidation (detect + type + reason + localize):** A37945; segment/region localization: A37865, A40928.
- **Two-stage training (align/pretrain then SFT/RL):** A37421 (SFT cold-start → RLVR/GRPO), A37945 (continual pretraining → visual-instruction SFT), A41234 (adversarial-denoising RPE pretraining → discriminator).
- **Released code** for A37071, A37421, A37865, A37945, A38060, A41525; code availability **not stated in the extracted text** for A37334, A37473, A37553, A40886, A40907, A40928, A41234.

---

## 14. Product design implications

- **Use any single detector as one probabilistic evidence signal, never as an authoritative gate.** Every deployment-implications section reaches this conclusion; combine detection with cryptographic provenance (C2PA-style), watermarking, and human review for high-stakes decisions (A37071, A37865).
- **Gate explanations before surfacing them to a user or an action.** MLLM rationale faithfulness is unverified and empirically unreliable (A38060's ≤67.4% incorrect-flaw finding); anchor explanations to a verifiable taxonomy + quantitative scoring, and keep a human in the loop before action.
- **Surface uncertainty, not just a verdict.** Log and display confidence, impression-vs-final disagreement, and localization masks so downstream users can calibrate trust; averaged accuracy masks near-chance behavior on the hardest inputs (Section 10).
- **Proactive/active forensics (A37865) is an attestation/watermarking analogue** worth considering for owner-controlled assets, but its trust rests on the protective perturbation surviving the distribution channel and on pinning the verifier model (SAM) version — production validation required.
- **Face anti-spoofing as one authentication gate with escalation to human review** (A37945) — directly relevant to identity/authz product surfaces, with the caveat that generated reasoning must not be trusted as ground truth.

---

## 15. Architecture implications

- **The verifier-loop pattern generalizes directly to guardrails:** a fast proposer plus a confidence-gated reflective verifier with adaptive compute (A37421, A38060) is the cheap-check-then-deep-check escalation shape a Guardian Agent can reuse.
- **Treat detectors as pluggable, replaceable evidence producers,** not fixed oracles — generalization is empirical and expires as generators evolve (A40886's fixed GAN/DM K=2 assumption is an explicit example of a bias that new architecture families like VAR can break).
- **Stateful detector surfaces need their own governance:** prototype banks (A37473) and noise-residual models (A41234) introduce drift and poisoning risk that must be bounded, logged, and monitored.
- **Frozen-backbone + lightweight-adapter architecture** (Section 13) keeps detectors cheap to retrain and swap as new generators appear — an operational fit for a rapidly shifting threat surface.
- **Cross-modality gaps must be handled at the architecture level:** image, audio, and audio-visual detectors are siloed (reviewer synthesis), so a unified content-authenticity layer must compose per-modality models rather than assume one detector.

---

## 16. Launch and assurance implications

- **Instrument for time-bounded generalization.** Log confidence, impression-vs-final disagreement, prototype turnover, and localization masks as audit records; monitor OOD accuracy / EER drift as new generators appear. Generalization is empirical and expires — treat detection accuracy as a decaying asset with scheduled re-evaluation.
- **Do not claim adaptive-adversary robustness.** No paper in the corpus evaluates anti-forensic / adaptive attacks; any assurance statement must be scoped to the non-adaptive, distribution-shift threat model actually tested, and adaptive robustness flagged as requiring production validation.
- **Pin and version-control verifier models.** Proactive forensics (A37865) is tied to a specific SAM version; treat the verifier model as a governed dependency whose change can silently break tamper localization.
- **Establish a re-benchmarking cadence against the hardest in-the-wild sets, not averaged SOTA.** A37071's ~57–58% on Chameleon versus GenImage SOTA shows headline numbers can mask near-chance behavior; assurance should track worst-case, per-generator performance.
- **Governance for stateful components:** prototype banks and noise-residual models (A37473, A41234) need bounded, logged, monitored update paths to contain drift and poisoning risk before launch.

---

## 17. Open research problems

- **Adaptive / anti-forensic robustness is essentially unmeasured** across the entire corpus — the largest gap for any security (vs accuracy) use.
- **Time-bounded generalization to genuinely new generator paradigms** (e.g., VAR/autoregressive beyond the GAN/DM dichotomy; A40886, A41234) — inductive biases baked for two families may not transfer.
- **Faithful, independently-verifiable explanations** (not fluency-scored) for human-in-the-loop forensic review (A37421, A37945, A38060).
- **Robustness to real distribution channels** — compression, denoising, resizing, screenshotting, regeneration — partially addressed as environmental corruption (A37553, A37421) but never as an adaptive attack; perturbation survivability is untested for A37865.
- **Cross-modality unification** remains absent — image, audio, and audio-visual detectors are siloed (A38060/A40886/A41234 vs A40907 vs A40928).
- **Reliable generator/architecture attribution** is suggested (A40886) but not independently validated.

---

## 18. Recommended foundational papers

Ranked by transferable lesson, evidence quality, and reproducibility (released code where noted).

1. **A37421 (MIRAGE / MIRAGE-R1)** — most transferable architecture lesson: an in-the-wild, domain-bias-controlled benchmark plus a VLM verifier-loop with confidence-gated adaptive compute and corruption-robustness testing; released code.
2. **A38060 (ESIDE)** — strongest evidence on explanation trust: diffusion-timestep detection paired with the quantified finding that standalone MLLM explanations are unreliable (≤67.4% incorrect), motivating a metric-grounded refinement gate; released code + datasets.
3. **A40886 (TriDetect)** — clearest generalization theory (GAN JS-divergence vs DM KL-divergence artifact families) and the "fake-class-as-multimodal" inductive bias; broad eval (5 datasets, 13 baselines), highest reported AUC in the corpus, plus an attribution angle.
4. **A37553 (DDOC)** — most realistic environmental-robustness setting (OSN compression) and a transferable design principle: orthogonalize the nuisance to the decision axis instead of deleting it.
5. **A37945 (FaceShield)** — load-bearing for the identity/authz + physical-presentation-attack angle and the detect-type-reason-localize consolidation pattern; released code.

---

## 19. Recommended frontier papers

Ranked by novelty of paradigm and forward relevance, with maturity caveats.

1. **A41234 (RealNet)** — most future-proofing paradigm: real-only training with feature-space pseudo-negatives, evaluated across GAN/diffusion/VAR and a safety-critical medical distribution shift, at low compute. Frontier direction for detection that does not require enumerating generators.
2. **A37865 (Blank Canvas)** — the only proactive/active-forensic control in the corpus (adversarial-perturbation → SAM tamper localization), a distinct provenance/attestation primitive; evidence preliminary (truncated numbers), verifier-version-dependent, survivability untested.
3. **A40907 (wavelet prompt tuning, audio)** — parameter-efficient all-type audio detection with a stark quantified generalization result (3.58% all-type EER vs ~30–50% single-type); clean-audio-only scope is the caveat.
4. **A40928 (deformable state-space AV localization)** — frontier for temporal audio-visual forgery localization of sparse, boundary-ambiguous segments; limited to two AV benchmarks.

---

## 20. Source map (paper id → one-line relevance)

- **A37071** — AIGI detection via dual-branch asymmetric discrepancy learning; GenImage SOTA but ~57–58% on Chameleon (setting-dependence evidence); released code.
- **A37334** — Face-forgery robustness via RL-scheduled curriculum augmentation + IRM (training-time defense); concrete numbers truncated in review.
- **A37421** — MIRAGE/MIRAGE-R1: in-the-wild VLM reasoning detector with confidence-gated adaptive compute and corruption testing; ~78.46% OOD; released code; anonymized A/B sources.
- **A37473** — Face-forgery detection via CLIP residual prototype bank (capacity 64/class, decay γ=0.99); stateful-surface governance example; borrowed baselines.
- **A37553** — DDOC: decision-driven orthogonal decoupling of compression (OSN robustness); ViT+CNN bidirectional fusion (+7.4 ablation); ~75% mean under OSN compression.
- **A37865** — Blank Canvas: proactive frequency-aware ℓ∞ perturbation forcing SAM to "segment nothing" for training-free tamper localization; attestation analogue; released code; truncated numbers.
- **A37945** — FaceShield: explainable face anti-spoofing MLLM (detect+type+reason+localize, 12 spoof types); intra-dataset ACC 99.41, Replay-Attack cross-dataset HTER 20.07; identity/authz relevance; released code.
- **A38060** — ESIDE: diffusion-timestep-ensembled detection + metric-grounded MLLM refinement; ≤67.4% of MLLM flaws incorrect (explanation-trust evidence); 98.91%/95.89% ACC; per-GenImage-subset training; released code + datasets.
- **A40886** — TriDetect: unsupervised GAN-vs-DM architectural clustering + attribution; GenImage avg AUC 0.9882 (5 datasets, 13 baselines); fixed K=2 assumption is a named bias.
- **A40907** — Wavelet prompt tuning for type-invariant audio deepfake detection; 3.58% all-type EER vs ~30–50% single-type; ~458× fewer trainable params; clean-audio-only scope.
- **A40928** — Deformable state-space temporal localization of sparse audio-visual forgery segments; two AV benchmarks only.
- **A41234** — RealNet: real-only representation learning with feature-space pseudo-negatives; evaluated across GAN/diffusion/VAR + medical shift, low compute (future-proofing paradigm).
- **A41525** — Breakable Machine: K-12 AI-literacy artifact; only adaptive, physical-world attacker (human spoofing MobileNet-V2 via CAM saliency); pedagogy, not a deployable control; released code.
