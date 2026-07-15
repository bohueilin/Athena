# Synthesis — Model-IP-Protection

Corpus: 22 papers, all AAAI-26 (2026): A37038, A37103, A37412, A37429, A38094, A39041, A39199, A39623, A39992, A40030, A40546, A40561, A40575, A40728, A40843, A40851, A40892, A40901, A40909, A40910, A40921, A41092. Merged from one partial synthesis (chunk 0). Weighting favors experimental quality, reproducibility, threat-model realism, and independent replication over paper count. Throughout, "direct paper finding" marks values reported by the paper's authors; "reviewer synthesis" marks cross-paper inference added during review. Numbers are author-reported unless stated otherwise. Where a value was absent or truncated in the reviewed text it is written "not stated in paper." Two papers (A39623, A40030) are miscategorized and off-topic for model-IP / agent security; they are flagged as such and carry no security weight.

---

## 1. Executive summary

This category is **model- and content-IP provenance**: watermarking generative outputs and models, fingerprinting ownership, detecting unauthorized training/extraction, and gating copyright policy. It is largely an *evidence-and-attribution* discipline, not an agent-execution-security one — the recovered mark or fingerprint supports post-hoc attribution, governance, and legal action; it does not by itself prevent misuse (nearly every card states this).

The single most replicated cross-cutting property is a **weak, non-adaptive threat model**: nearly every watermarking paper (A37103, A37412, A38094, A40546, A40561, A40892, A40901, A40921, A41092, and the tabular A39199) explicitly evaluates against fixed, off-the-shelf distortions/edits rather than an adversary who knows the scheme and optimizes against it. "Robust" throughout this corpus should be read as "robust against the tested, non-adaptive attacks." Forgery/spoofing of an owner's mark is repeatedly named as a gap and almost never evaluated.

A minority of papers adopt materially stronger, more realistic threat models and carry disproportionate weight: **A40909 (iSeal)** — white-box weights, collusion-based fingerprint unlearning, and output-manipulation evasion in a litigation setting; **A40910 (CopyGuard / LVLM copyright)** — guardrail bypass through the multimodal/RAG context channel (author-reported 11/12 LVLMs fail); **A39992 (DeepTracer)** — extraction-robust watermarking evaluated against adaptive and detection attacks; and the two red-team removal papers **A37429 (GSPure)** and **A39041 (box-free)**, which demonstrate that steganographic hiding / black-box encapsulation is not a security boundary.

For a Guardian / agent stack the actionable primitives are: treat watermarks and fingerprints as **evidence, not prevention**, and pair them with access control, query monitoring, and provenance registries; adopt CopyGuard's **ingestion-time policy gate on retrieved/user-supplied context** as the transferable agent pattern; follow iSeal's **external-secret + trusted-verifier + similarity/ECC** template for tamper-evident model identity; and treat any decode-time output watermark's secret key as a credential requiring custody.

---

## 2. Scope and boundaries

- **In scope:** generative-output watermarking (image, audio, text, tabular, embeddings), model/asset fingerprinting and ownership verification, extraction/stealing detection, membership-inference / training-data provenance, and copyright policy gating for multimodal models.
- **Modalities and targets:** image generation (A37103, A37412, A38094, A40892, A40901, A40921), 3D Gaussian-Splatting assets (A37429), image-to-image models (A39041), audio (A40561), LLM text (A40546, A40575, A41092), embedding/EaaS APIs (A40728), tabular GBDT models (A39199), style/LoRA image models (A40843), image-to-model attribution (A40851), classifier models under extraction (A39992), code models (A37038), and LVLM copyright behavior (A40910).
- **Deployment phase:** in-generation / latent-time marking (A37412, A38094, A40561, A40892, A40921), post-hoc marking (A37103, A40901), decode-time logit biasing (A40546, A41092), pre-publication marking (A40575), and verification-time-only intrinsic fingerprints (A40843, A40851, A40909).
- **Adjacent, not central (reviewer classification):** this is content-authenticity / provenance work; only A40910 sits squarely on the agent execution surface (context-channel guardrail). The rest feed the evidence base an agent or governance layer consumes.
- **Off-topic / miscategorized (reviewer classification):** A39623 (Shapley attribution for FANOVA Gaussian Processes — explainable-AI) and A40030 (VeriFlow — normalizing-flow neural-network formal verification) are neither IP-protection nor agent-security papers; they are methodologically sound for their actual domains but carry no weight here.

---

## 3. Dominant threat models

- **Defender-embeds-a-mark, adversary-applies-generic-transforms-to-strip-it, evaluated NON-adaptively (dominant).** This is the single most replicated posture, stated individually by A37103, A37412, A38094, A40546, A40561, A40892, A40901, A40921, A41092, and A39199. Adversary knowledge is effectively black-box on the mark; attacks are fixed, off-the-shelf distortions/edits, not scheme-aware optimization.
- **Adversary controls end-to-end inference / litigation setting (strongest).** A40909 (iSeal): white-box weight access, collusion-based fingerprint unlearning, and output-manipulation to evade exact match — the most adversarially realistic threat model in the corpus.
- **Model extraction / stealing.** A39992 (DeepTracer: classifier stealing including hard-label and data-free, with adaptive + detection attacks), A40728 (RegionMarker: EaaS embedding-API extraction via copy/paraphrase/dimension-perturbation), A39041 (box-free image-to-image query API enabling watermark-free surrogate training).
- **Red-team / watermark-removal attackers.** A37429 (GSPure, white-box on the distributed 3DGS asset), A39041 (black-box query API). These are the corpus's demonstrated bypasses.
- **Training-data / unauthorized-training provenance.** A37038 (code membership inference as a copyright auditor), A40575 (SPECTRA: pre-publication text watermark detected via grey-box log-probs at 5B-token scale).
- **Guardrail bypass via the context/retrieval channel (most agent-relevant).** A40910: the safety behavior that refuses direct infringing requests does not generalize when copyrighted content enters as multimodal / RAG context.
- **No adversary (off-topic).** A39623 and A40030 have no IP/security threat model.

Knowledge assumptions cluster as: black-box on the mark for generative-output watermarking; white-box on the asset/model for the removal attacks (A37429) and iSeal's adversary (A40909); grey-box log-prob access for the membership-inference / data-provenance methods (A37038, A40575).

---

## 4. Major attack families

- **Watermark removal / purification (central adversarial action).** Demonstrated offensively in A37429 (author-reported up to 16.34 dB watermark-PSNR reduction with <1 dB scene loss) and A39041 (author-reported ~100% removal success, PSNR up to 34.69 dB). Named as the threat every watermarking paper defends against.
- **Model extraction / theft / surrogate training.** A39992, A40728, A39041 (removal enables watermark-free surrogate).
- **Membership inference.** A37038 uses it offensively as a copyright auditor; A40575 documents that standard MIA collapses to near-random (author-reported ROC-AUC ~0.50–0.56 at +5B tokens) at scale, motivating its watermark.
- **Unauthorized adaptation / style mimicry.** A40843 (LoRA/DreamBooth style theft), A39199 (post-deployment fine-tuning), A40921 (community fine-tunes / LoRA breaking prior watermark modules).
- **Guardrail / policy bypass via modality/context channel.** A40910 (author-reported 11/12 LVLMs fail to respect copyright when infringing content arrives as multimodal context).
- **Watermark forgery / spoofing.** Raised as an unaddressed gap in nearly every watermark/fingerprint paper (A38094, A40546, A41092, partially A40909); almost never evaluated.

---

## 5. Major defense families

- **Watermarking (dominant).** Image in-generation/latent (A37412, A38094, A40892, A40921); image post-hoc / encoder-noise-decoder (A37103, A40901); audio latent + inversion (A40561); LLM-text logit-biasing (A40546, A41092); EaaS embedding (A40728); tabular/GBDT in-place (A39199); training-data via paraphrase-scoring (A40575).
- **Fingerprinting.** Intrinsic / no-embedding (A40843 style hypersphere; A40851 passive image-to-model attribution); encrypted external-secret model fingerprint (A40909).
- **Detection / membership inference.** A37038 (code MIA), A40575 (grey-box log-prob detection).
- **Policy gating / tool-augmented guardrail.** A40910 (CopyGuard: notice identifier, source verifier, query-risk analyzer/rewriter, status reminder).
- **Crypto-provenance + error correction.** A40909 (key-generated encoder + Reed–Solomon), A41092 (extended (8,4,4) Hamming + anchor synchronization), A40561 (ChaCha20 key custody).
- **Certified robustness / formal verification (off-topic).** A40030 — methodologically sound but out of category.

---

## 6. Most influential concepts

- **Watermarks and fingerprints are evidence mechanisms, not prevention** — the organizing conclusion across the corpus (reviewer synthesis over nearly every card); the recovered mark supports attribution/governance/legal action and must be combined with access control and monitoring.
- **A separable / "inactive" mark is a removable mark.** A37429 (watermark Gaussians have low, viewpoint-inconsistent contribution → clusterable and prunable) and A39041 (additive-separable mark plus inducing the generator toward near-identity → recoverable) independently show hiding/encapsulation is not a security boundary (reviewer synthesis).
- **For extraction survival, the mark must be in-distribution and coupled to the primary task.** A39992's central claim: OOD watermark triggers activate disjoint neurons and are forgotten by stolen models, whereas in-distribution coupling makes the watermark inseparable from copied functionality (supported by author neuron-activation analysis).
- **Latent-space / in-generation embedding preserves quality better than post-hoc marking** — recurring across A37412, A38094, A40561, A40892, A40921.
- **Watermark placement in the generative trajectory is a robustness lever** — A38094: early-latent marks survive regeneration, late marks survive geometric/valuemetric transforms.
- **Where the secret should live is a security decision.** A40909 argues weight-embedded fingerprints are removable under white-box access and exact-match verification is evadable, motivating an external key/encoder plus similarity+ECC verification — a direct critique of weight-embedding fingerprinting.
- **Enforce policy where untrusted content enters context, not only at the surface prompt** (A40910) — the transferable agent-security concept in the corpus.

---

## 7. Common datasets and benchmarks

Only datasets/benchmarks explicitly named in the reviewed text are listed; others are marked unstated to preserve evidence integrity. Many under-attack tables were truncated in the reviewed text and are recorded as author-stated rather than reviewer-verified.

- **Mip-NeRF360** — 3D Gaussian-Splatting scenes; the sole evaluation setting for A37429 (single-dataset concentration).
- **Stable Diffusion / DDIM** — generation backbones for A38094 (single model-family scope).
- **Stable Diffusion v2.1** — sole generator for A40892.
- Specific corpus/benchmark names are **not stated in paper** for A37038, A37103, A37412, A39041, A39199, A40546, A40561, A40575 (beyond the stated +5B-token / <0.001%-corpus scale), A40728, A40843, A40851, A40901, A40909, A40910, A40921, A41092 in the reviewed text.
- A39623 and A40030 evaluate on their own (off-topic) XAI / verification benchmarks; not relevant here.

---

## 8. Evaluation metrics

- **Watermark-PSNR / scene-PSNR (removal quality)** — A37429 (author-reported up to 16.34 dB watermark-PSNR reduction, <1 dB scene loss); A39041 (author-reported PSNR up to 34.69 dB).
- **Removal success rate** — A39041 (author-reported ~100%).
- **Detection ROC-AUC** — A40575 documents prior MIA at ~0.50–0.56 (near-random) at +5B tokens (author-reported), motivating its watermark.
- **p-value / statistical-test verification** — A40728 and A40575 (KS-test / p-value); A40575's decision-relevant p-value at <0.001% corpus fraction.
- **One-class / similarity verification** — A40843 (SVDD hypersphere), A40909 (similarity + error-correction instead of exact match), A40851 (passive attribution).
- **Perceptual-quality metrics** for embedded marks (e.g., PSNR/SSIM-style fidelity) recur across the image watermarking papers; specific headline numbers were truncated/unverifiable in the reviewed text for A37103, A37412, A38094, A40892, A40901, A40921 and are recorded as **not stated in paper**.
- **Bit-accuracy / message-recovery under transforms** for text and coded watermarks (A40546 rank-mod-k, A41092 Hamming-coded); specific numbers **not stated in paper** in the reviewed text.

---

## 9. Strongest replicated findings

1. **Latent-space / in-generation embedding preserves quality better than post-hoc marking** — recurring across A37412, A38094, A40561, A40892, A40921 (each author-reported on its own datasets; reviewer synthesis on the convergence).
2. **A separable / "inactive" mark is a removable mark** — A37429 and A39041 independently demonstrate that hiding/encapsulation is not a security boundary (reviewer synthesis over two red-team papers).
3. **For extraction-survival, the mark must be in-distribution and coupled to the primary task** — A39992's central claim, supported by author neuron-activation analysis.
4. **Non-adaptive robustness is near-universal; adaptive and forgery robustness are near-universally untested** — reviewer synthesis across the whole corpus; several papers state it themselves as future work (A37103, A38094, A41092).
5. **Watermark placement in the generative trajectory is a robustness lever** — A38094 (early-latent survives regeneration; late survives geometric/valuemetric transforms).
6. **Standard membership inference collapses to near-random at scale** — A40575 (author-reported ROC-AUC ~0.50–0.56 at +5B tokens), motivating pre-publication watermarking over passive MIA for training-data provenance.

---

## 10. Conflicting findings

- **Embedded marks vs. intrinsic fingerprints (paradigm tension, not direct contradiction).** A40843 (StyleSentinel) and A40851 (OFA) argue embedded signals are removable/purifiable and require pre-publication embedding, favoring intrinsic, no-embedding fingerprints; the watermarking majority argues robust embedding is achievable. They target different deployment constraints — retroactive protection of already-published content vs. provider-controlled generation.
- **Where the secret should live.** A40909 (iSeal) argues weight-embedded fingerprints are removable under full white-box access and that exact-match verification is evadable, motivating an external key/encoder plus similarity+ECC verification — a direct critique of the weight-embedding fingerprint approaches other papers rely on.
- **Verification-access assumptions differ sharply.** A40546 and A40561 require the verifier to hold the model (+key) to reconstruct the mark (owner-white-box); A40575 and A40728 use grey-box log-probs / suspect-model outputs; A40851 is fully passive. No head-to-head comparison exists within the corpus (reviewer synthesis).
- **No shared-measurement contradictions.** These are largely parallel methods on different targets; the tensions above are about paradigm and deployment assumptions, not competing numbers on one benchmark.

---

## 11. Defense bypasses

- **A37429 (GSPure)** breaks three scene-hiding 3DGS watermarks — GS-Hider, Splats-in-Splats, SecureGS (author-reported), via white-box clustering/pruning of low-contribution, viewpoint-inconsistent watermark Gaussians.
- **A39041** breaks two box-free image-to-image watermarks (referred to as VWu, VZhang) with author-reported ~100% removal; it also enables watermark-free surrogate training. A query-screener defense is proposed but, per the card, not rigorously benchmarked.
- **A40910** shows LVLM refusal guardrails bypassed through the multimodal-context / RAG channel; embedded notices are ignored; naive fine-tuning for copyright awareness causes over-refusal (author-reported).
- **A40728** documents prior EaaS watermarks broken by single attack families — trigger-word methods (EmbMarker, WARDEN, EspeW) defeated by paraphrasing; WET defeated by dimension-perturbation — motivating comprehensive coverage.
- **A40575** documents that prior membership-inference collapses to near-random at scale (author-reported), a bypass of passive MIA as a provenance signal.
- **Calibrated takeaway:** demonstrated bypasses are all against *other* schemes, under the bypasser's own evaluation. The corpus's own defenses are, with few exceptions (A39992's adaptive evaluation, iSeal's adversarial threat model), tested only against non-adaptive attacks; their adaptive and forgery robustness **requires production validation** and is currently unestablished.

---

## 12. Known benchmark limitations

- **Non-adaptive attack catalogs; no forgery / collision / false-attribution analysis** — flagged in almost every card (A38094, A40546, A40561, A40728, A40843, A40892, A40901, A40921, A41092). Read "robust" as "against the tested, non-adaptive attacks."
- **Single-dataset / single-model-family concentration** — A37429 (Mip-NeRF360 only), A38094 (SD/DDIM), A40892 (SD v2.1 only).
- **Owner-white-box / model+key verification requirement** limits third-party replication (A40546, A40561, A40909).
- **Continued-pretraining, not from-scratch** — A40575 (author-flagged; full-scale validation is open).
- **Truncated extracted text** left several robustness-under-attack tables reviewer-unverified (explicitly noted for A38094, A40910, A40921, A41092, A40851); treat under-attack numbers as author-stated.
- **Category noise** — A39623 and A40030 are off-topic; their evidence is insufficient from a security/IP lens despite being methodologically sound for their actual (XAI / NN-verification) domains.
- **False-attribution / cross-owner collision rates at scale are rarely quantified** (raised for A38094, A40892, A40901, A40921, A41092).

---

## 13. Implementation patterns

- **Encoder–noise/distortion-simulation–decoder pipelines** with a distortion layer at train time (A37103, A37412, A40901, A40921).
- **Decode-time / inference-time logit biasing with a secret hash key** (A40546 rank-mod-k; A41092 anchor + Hamming); both require control of the serving path.
- **Initial-latent embedding + inversion recovery** (A40561; A38094's structure watermark at x_T).
- **Redundancy / perceptual-masking-guided embedding strength** (A40892 PCA-energy allocation; A40901 gradient-guided per-pixel strength).
- **Secret-key custody + error-correcting codes** (A40561 ChaCha20; A40909 key-generated encoder + Reed–Solomon; A41092 (8,4,4) Hamming).
- **Statistical / one-class verification** (A40728 and A40575 KS-test / p-value; A40843 SVDD hypersphere; A40575 side-balanced, score-matched sampling to avoid a training-independent signature).
- **Distribution-alignment / self-augmented training to close the train/test gap** (A40892 VAE-prior init; A40921 free-generation self-augmented training).
- **In-distribution, task-coupled trigger design for extraction survival** (A39992).
- **Tool-augmented policy pipeline at the context boundary** (A40910: notice identifier → source verifier → query-risk analyzer/rewriter → status reminder).

---

## 14. Product design implications

- **Treat watermarks and fingerprints as evidence, not prevention.** Almost every card states the recovered mark supports post-hoc attribution/governance/legal action and must be combined with access control, query monitoring, and provenance registries — not relied on to stop misuse.
- **Ingestion-time policy gates on retrieved/user-supplied context are the transferable agent pattern** (A40910 / CopyGuard): enforce copyright/safety policy where untrusted content enters context (RAG ingestion, uploaded images), not only on the surface prompt; externalize the checks into tools (verifier + risk analyzer + query rewrite).
- **Provenance on embedding APIs is a supply-chain control** (A40728): embeddings feed RAG/agent memory, so marking the embedding API guards the data agents consume.
- **Decode-time output watermarking can tag agent-generated text for downstream attribution** (A40546, A41092), but requires control of the serving path and secret-key custody — treat the key as a credential.
- **Training-data / dataset provenance auditing** for the AI data supply chain (copyright, benchmark contamination) is viable via grey-box log-prob access (A37038, A40575), subject to logit/API access.
- **Do not overclaim.** Present any single mark or fingerprint as one probabilistic evidence signal scoped to a non-adaptive threat model; adaptive robustness and forgery resistance are unestablished across the corpus.

---

## 15. Architecture implications

- **Tamper-evident model identity should bind ownership evidence to an external secret, not weights** (A40909 / iSeal template): use similarity + error-correction instead of exact match, keep verification prompts under a trusted verifier to prevent overclaim, and assume the adversary controls inference end-to-end.
- **Verification-access is an architectural decision.** Model+key detection (A40546, A40561) is a deployment burden; external-secret + trusted-third-party verification (A40909) or grey-box-log-prob detection (A40575) are more deployable and, per iSeal, more robust to a full-access adversary.
- **Put policy enforcement at the context/tool boundary** (A40910): a Guardian layer should gate retrieved and uploaded content at ingestion, compose external verifier/risk-analyzer tools, and avoid relying on surface-prompt refusal alone.
- **Treat secret keys as governed credentials** for any decode-time or key-custody scheme (A40546, A40561, A40909, A41092) — key custody and rotation are part of the trust boundary.
- **Design marks for extraction survival by in-distribution coupling** (A39992) when protecting against model stealing, rather than OOD trigger sets that a stolen model forgets.
- **Assume separable/encapsulated marks are removable** (A37429, A39041): architectures must not treat steganographic hiding as a security boundary.

---

## 16. Launch and assurance implications

- **Scope every robustness claim to the non-adaptive threat model actually tested.** No absolutes; state "reduced removal success against the tested, non-adaptive attacks" and flag adaptive/forgery robustness as requiring production validation.
- **Require forgery / spoofing evaluation before trusting a mark in adversarial or litigation settings.** Framing an owner by spoofing their mark is repeatedly named and almost never evaluated; do not launch attribution claims without it (A38094, A40546, A41092, A40909).
- **Instrument false-attribution / cross-owner collision rates at scale** before relying on a mark for attribution decisions (raised for A38094, A40892, A40901, A40921, A41092).
- **Pin and version-control verifier models and keys.** External-secret and trusted-verifier schemes (A40909, A40546, A40561, A41092) depend on custody of a key and, in some cases, a specific verifier — treat these as governed dependencies.
- **Validate at production scale for training-data provenance.** A40575's +5B-token result is continued-pretraining, not from-scratch (author-flagged); full-scale validation is open before assurance claims.
- **Re-benchmark against scheme-aware adaptive attacks**, since demonstrated bypasses (A37429, A39041, A40728, A40575) show that prior schemes fell to single adaptive attack families.

---

## 17. Open research problems

- **Adaptive- and forgery-resistant provenance is largely unsolved / untested** across the corpus (spoofing an owner's mark to frame them is repeatedly named but not evaluated).
- **False-attribution / cross-owner collision rates at scale** are rarely quantified (A38094, A40892, A40901, A40921, A41092).
- **Robustness to regeneration/purification** for generative-output watermarks and to scheme-aware adaptive attacks (post-A40728, post-A37429/A39041).
- **Closed-API auditing without logit access** (A37038, A40575, A40546 are all gated by grey-box/logit access).
- **Enforcement at the context/tool boundary against adaptive bypass** — A40910's CopyGuard is not stress-tested against obfuscated content or split payloads.
- **Cross-modal / cross-model-family generalization** of both marks and detectors (image, audio, text, tabular, embedding, and 3DGS methods are siloed).

---

## 18. Recommended foundational papers

Ranked by transferable lesson, evidence quality, threat-model realism, and reproducibility.

1. **A40909 (iSeal)** — strongest evidence in the corpus and the only genuinely adaptive, litigation-grade LLM ownership-verification threat model (white-box weights, collusion unlearning, output-manipulation evasion); the external-secret + trusted-verifier + similarity/ECC template directly informs model-identity/attestation design.
2. **A40910 (CopyGuard / LVLM copyright)** — most directly agent-security-relevant: demonstrates guardrail bypass via the RAG/multimodal-context channel (author-reported 11/12 LVLMs fail) and offers a tool-augmented ingestion-time gate as the transferable agent pattern.
3. **A39992 (DeepTracer)** — extraction-robust watermarking with adaptive + detection evaluation; supplies the reusable "in-distribution, task-coupled" design principle backed by neuron-activation analysis.
4. **A40575 (SPECTRA)** — the strongest training-data-provenance entry: realistic copyright-enforcement framing, meaningful scale (+5B tokens, <0.001% corpus fraction), a decision-relevant p-value metric, and the documented collapse of prior MIA at scale.
5. **A37429 (GSPure) and A39041 (box-free removal)** — the load-bearing red-team demonstrations that steganographic hiding / black-box encapsulation are not security boundaries; the cautionary counterweight to the watermarking majority.

---

## 19. Recommended frontier papers

Ranked by novelty of paradigm and forward relevance, with maturity caveats.

1. **A40843 (StyleSentinel) and A40851 (OFA)** — intrinsic, no-embedding fingerprinting for retroactive protection of already-published content; a paradigm alternative to embedded marks, but their claim that embedded signals are removable is argued rather than benchmarked head-to-head here.
2. **A40728 (RegionMarker)** — provenance for EaaS embedding APIs, a supply-chain control for the data agents/RAG consume; demonstrates comprehensive coverage against copy/paraphrase/dimension-perturbation, though still non-adaptive beyond the studied families.
3. **A38094 (trajectory-placement watermarking)** — establishes watermark placement in the generative trajectory as a robustness lever; single model-family (SD/DDIM) scope is the caveat.
4. **A40546 / A41092 (coded LLM-text watermarking)** — decode-time logit-biasing with error-correcting codes for downstream attribution of agent-generated text; both require serving-path control and key custody, and forgery resistance is untested.

---

## 20. Source map (paper id → one-line relevance)

- **A37038** — Code membership inference used as a training-data / copyright auditor; grey-box log-prob access; closed-API auditing without logits is the open gap.
- **A37103** — Post-hoc image watermark via encoder–noise–decoder pipeline; non-adaptive robustness only (states adaptive robustness as future work); headline numbers not stated in paper in the reviewed text.
- **A37412** — In-generation/latent image watermark; latent embedding preserves quality vs post-hoc; non-adaptive threat model.
- **A37429** — GSPure: white-box removal attack breaking three scene-hiding 3DGS watermarks (GS-Hider, Splats-in-Splats, SecureGS); author-reported up to 16.34 dB watermark-PSNR reduction, <1 dB scene loss; Mip-NeRF360 only.
- **A38094** — In-generation structure watermark at x_T; trajectory placement as a robustness lever (early survives regeneration, late survives geometric/valuemetric transforms); SD/DDIM single-family scope.
- **A39041** — Box-free image-to-image watermark removal attack (black-box query API) breaking two prior schemes with author-reported ~100% removal (PSNR up to 34.69 dB); enables watermark-free surrogate training; proposed query-screener defense not rigorously benchmarked.
- **A39199** — Tabular/GBDT in-place watermark; post-deployment fine-tuning threat; non-adaptive evaluation.
- **A39623** — Off-topic (miscategorized): Shapley attribution for FANOVA Gaussian Processes (explainable-AI); no IP/security relevance.
- **A39992** — DeepTracer: extraction-robust classifier watermarking (hard-label / data-free stealing) with adaptive + detection attacks; supplies the in-distribution task-coupling principle via neuron-activation analysis.
- **A40030** — Off-topic (miscategorized): VeriFlow normalizing-flow neural-network formal verification; sound for its domain, no IP/security relevance.
- **A40546** — LLM-text logit-biasing watermark (rank-mod-k); owner-white-box (model+key) verification; forgery resistance untested.
- **A40561** — Audio latent + inversion watermark with ChaCha20 secret-key custody; owner-white-box verification; non-adaptive attacks only.
- **A40575** — SPECTRA: pre-publication text watermark detected via grey-box log-probs at +5B-token scale (<0.001% corpus fraction), decision-relevant p-value; documents prior MIA collapsing to ROC-AUC ~0.50–0.56; continued-pretraining, not from-scratch.
- **A40728** — RegionMarker: EaaS embedding-API watermark robust to copy/paraphrase/dimension-perturbation extraction; documents prior EaaS schemes (EmbMarker, WARDEN, EspeW, WET) each broken by one attack family; KS-test verification.
- **A40843** — StyleSentinel: intrinsic, no-embedding style fingerprint (SVDD hypersphere) against LoRA/DreamBooth style theft; argues embedded marks are removable.
- **A40851** — OFA: passive image-to-model attribution fingerprint; fully passive verification (no embedding); under-attack numbers reviewer-unverified.
- **A40892** — In-generation image watermark with PCA-energy redundancy allocation and VAE-prior init; SD v2.1 only; false-attribution rates not quantified.
- **A40901** — Post-hoc image watermark with gradient-guided per-pixel embedding strength; non-adaptive attacks; forgery/collision analysis absent.
- **A40909** — iSeal: encrypted external-secret LLM ownership fingerprint (key-generated encoder + Reed–Solomon; similarity+ECC verification); litigation-grade adaptive threat model (white-box weights, collusion unlearning, output-manipulation evasion); strongest entry.
- **A40910** — CopyGuard / LVLM copyright: guardrail bypass via the multimodal/RAG context channel (author-reported 11/12 LVLMs fail); tool-augmented ingestion-time gate (notice identifier, source verifier, query-risk analyzer/rewriter, status reminder); most agent-relevant.
- **A40921** — In-generation image watermark robust to community fine-tunes / LoRA via free-generation self-augmented training; under-attack numbers reviewer-unverified.
- **A41092** — LLM-text logit-biasing watermark with extended (8,4,4) Hamming coding + anchor synchronization; requires serving-path control and key custody; forgery resistance and under-attack numbers not fully verified in the reviewed text.
