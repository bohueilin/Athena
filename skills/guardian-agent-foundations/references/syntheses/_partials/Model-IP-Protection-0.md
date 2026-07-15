# Model-IP-Protection — Partial Synthesis (chunk 0 of 22 papers)

Scope note: this partial covers only the 22 papers in this chunk (A37038, A37103, A37412,
A37429, A38094, A39041, A39199, A39623, A39992, A40030, A40546, A40561, A40575, A40728,
A40843, A40851, A40892, A40901, A40909, A40910, A40921, A41092). All are AAAI-26 (2026)
entries. Claims attributed to a paper are the card's rendering of that paper's text; items
labelled "reviewer synthesis" are cross-paper observations, not paper claims. Numeric figures
are author-reported unless stated otherwise. Two papers (A39623, A40030) are miscategorized
and are off-topic for model-IP/agent security (flagged below).

## Dominant threat models

The overwhelmingly dominant posture is **defender-embeds-a-provenance-mark, adversary-applies-generic-transforms-to-strip-it, evaluated NON-adaptively**. Nearly every watermarking paper (A37103, A37412, A38094, A40546, A40561, A40892, A40901, A40921, A41092, and the tabular A39199) explicitly states its evaluated attacks are fixed, off-the-shelf distortions/edits, not an adversary who knows the scheme and optimizes against it. This is the single most replicated cross-cutting property of the chunk (reviewer synthesis, but each card states it individually).

Distinct, stronger threat models appear in a minority:
- **Adversary controls end-to-end inference / litigation setting** — A40909 (iSeal): white-box weight access, collusion-based fingerprint unlearning, output-manipulation to evade exact match. This is the most adversarially realistic threat model in the chunk and the paper is scored "strong."
- **Model-extraction / stealing** — A39992 (DeepTracer, classifier stealing incl. hard-label/data-free, with adaptive+detection attacks), A40728 (RegionMarker, EaaS embedding-API extraction against CSE/paraphrase/dimension-perturbation), A39041 (box-free image-to-image, query-based, enables watermark-free surrogate training).
- **Red-team / watermark-removal attack papers** — A37429 (GSPure, white-box on the distributed 3DGS asset), A39041 (black-box query API). These demonstrate defense bypasses (below).
- **Training-data provenance / unauthorized-training detection** — A37038 (code MIA), A40575 (SPECTRA, pre-publication text watermark detected via grey-box log-probs at 5B-token scale).
- **Guardrail-bypass via the context/retrieval channel** — A40910 (LVLM copyright): the safety behavior that refuses direct infringing requests does not generalize when copyrighted content enters as multimodal/RAG context. This is the most directly agent-relevant threat model in the chunk.
- **Off-topic (no adversary)** — A39623 (Shapley attribution for FANOVA GPs) and A40030 (VeriFlow normalizing-flow NN verification): neither is an IP-protection or agent-security paper; both are miscategorized.

Knowledge assumptions cluster at black-box on the mark for generative-output watermarking; white-box on the asset/model for the removal attacks (A37429) and iSeal's adversary (A40909); grey-box log-prob access for the MIA/data-provenance methods (A37038, A40575).

## Major attack families (studied or defended-against)

- **Watermark removal / purification** — the central adversarial action. Demonstrated offensively in A37429 (up to 16.34 dB watermark-PSNR reduction, <1 dB scene loss, author-reported) and A39041 (100% removal success, PSNR up to 34.69 dB, author-reported). Named as the threat every watermarking paper defends against.
- **Model extraction / theft / surrogate training** — A39992, A40728, A39041 (removal enables watermark-free surrogate).
- **Membership inference** — A37038 uses it offensively (as a copyright auditor); A40575 documents that standard MIA collapses to ~random (ROC-AUC ~0.50–0.56 at +5B tokens, author-reported) motivating its watermark.
- **Unauthorized adaptation / style mimicry** — A40843 (LoRA/DreamBooth style theft), A39199 (post-deployment fine-tuning), A40921 (community fine-tunes/LoRA breaking prior watermark modules).
- **Guardrail / policy bypass via modality/context channel** — A40910 (11/12 LVLMs fail to respect copyright in multimodal context, author-reported).
- **Watermark forgery / spoofing** — raised as an unaddressed gap in nearly every watermark/fingerprint paper (A38094, A40546, A41092, A40909-partially); almost never evaluated.

## Major defense families

- **Watermarking (dominant)**: image in-generation/latent (A37412, A38094, A40892, A40921), image post-hoc/E-N-D (A37103, A40901), audio latent+inversion (A40561), LLM text logit-biasing (A40546, A41092), EaaS embedding (A40728), tabular/GBDT in-place (A39199), training-data via paraphrase-scoring (A40575).
- **Fingerprinting**: intrinsic/no-embedding (A40843 style hypersphere, A40851 passive image-to-model attribution), encrypted external-secret model fingerprint (A40909).
- **Detection / membership inference**: A37038, A40575.
- **Policy gating / tool-augmented guardrail**: A40910 (CopyGuard — notice identifier, source verifier, query-risk analyzer/rewriter, status reminder).
- **Crypto-provenance + error-correction**: A40909 (key-generated encoder + Reed–Solomon), A41092 (extended (8,4,4) Hamming + anchor synchronization).
- **Certified robustness / formal verification (off-topic)**: A40030.

## Strongest replicated findings

1. **Latent-space / in-generation embedding preserves quality better than post-hoc marking** — recurring across A37412, A38094, A40561, A40892, A40921 (each author-reported on its own datasets).
2. **A separable / "inactive" mark is a removable mark** — A37429 (watermark Gaussians have low, viewpoint-inconsistent contribution → clusterable and prunable) and A39041 (additive-separable mark + inducing the generator into near-identity → recoverable). Reviewer synthesis: both independently show that hiding/encapsulation is not a security boundary.
3. **For extraction-survival, the mark must be in-distribution and coupled to the primary task** — A39992's central claim (OOD watermark triggers activate disjoint neurons and are forgotten by stolen models; in-distribution coupling makes the watermark inseparable from copied functionality), supported by neuron-activation analysis.
4. **Non-adaptive robustness is near-universal and adaptive/forgery robustness is near-universally untested** — reviewer synthesis across the whole chunk; several papers state it themselves as future work (A37103, A38094, A41092).
5. **Watermark placement in the generative trajectory is a robustness lever** — A38094: early-latent marks survive regeneration, late marks survive geometric/valuemetric transforms.

## Conflicting / tension findings

- **Embedded marks vs. intrinsic fingerprints (paradigm tension, not direct contradiction)**: A40843 (StyleSentinel) and A40851 (OFA) argue embedded signals are removable/purifiable and require pre-publication embedding, favoring *intrinsic, no-embedding* fingerprints; the watermarking majority argues robust embedding is achievable. They target different deployment constraints (retroactive protection of already-published content vs. provider-controlled generation).
- **Where the secret should live**: A40909 (iSeal) argues weight-embedded fingerprints are removable under full white-box access and that exact-match verification is evadable, motivating an *external* key/encoder plus similarity+ECC verification — a direct critique of the weight-embedding fingerprint approaches other papers rely on.
- **Verification access assumptions differ sharply**: A40546 and A40561 require the verifier to hold the model (+key) to reconstruct the mark (owner-white-box), whereas A40575/A40728 use grey-box log-probs / suspect-model outputs, and A40851 is fully passive. No head-to-head comparison exists within the chunk.

## Documented defense bypasses

- **A37429 GSPure** breaks three scene-hiding 3DGS watermarks (GS-Hider, Splats-in-Splats, SecureGS) — author-reported.
- **A39041** breaks two box-free image-to-image watermarks (VWu, VZhang) with ~100% removal — author-reported; a query-screener defense is proposed but, per the card, not rigorously benchmarked.
- **A40910** shows LVLM refusal guardrails bypassed through the multimodal-context/RAG channel; notices are ignored; naive fine-tuning for awareness causes over-refusal.
- **A40728** documents prior EaaS watermarks broken by a single attack family (trigger-word methods EmbMarker/WARDEN/EspeW by paraphrasing; WET by dimension-perturbation), motivating comprehensive coverage.
- **A40575** documents that prior MIA collapses to random at scale.

## Benchmark / evaluation limitations (recurring)

- **Non-adaptive attack catalogs; no forgery/collision/false-attribution analysis** — flagged in almost every card (A38094, A40546, A40561, A40728, A40843, A40892, A40901, A40921, A41092). "Robust" should be read as "against the tested, non-adaptive attacks."
- **Single-dataset / single-model-family concentration** — A37429 (Mip-NeRF360 only), A38094 (SD/DDIM), A40892 (SD v2.1 only).
- **Owner-white-box / model+key verification requirement** limits third-party replication (A40546, A40561, A40909).
- **Continued-pretraining, not from-scratch** — A40575 (author-flagged; full-scale validation is open).
- **Truncated extracted text** in many cards means several robustness-under-attack tables were not reviewer-verified (explicitly noted for A38094, A40910, A40921, A41092, A40851). Treat under-attack numbers as author-stated.
- **Category noise** — A39623 and A40030 are off-topic; their evidence is "insufficient" from a security/IP lens despite being methodologically sound for their actual (XAI / NN-verification) domains.

## Recurring implementation patterns

- **Encoder–noise/distortion-simulation–decoder pipelines** with a distortion layer at train time (A37103, A37412, A40901, A40921).
- **Decode-time / inference-time logit biasing** with a secret hash key (A40546 rank-mod-k; A41092 anchor + Hamming; both need control of the serving path).
- **Initial-latent embedding + inversion recovery** (A40561, and A38094's structure watermark at x_T).
- **Redundancy/perceptual-masking-guided embedding strength** (A40892 PCA-energy allocation; A40901 gradient-guided per-pixel strength).
- **Secret-key custody + error-correcting codes** (A40561 ChaCha20; A40909 key-generated encoder + Reed–Solomon; A41092 (8,4,4) Hamming).
- **Statistical / one-class verification** (A40728 & A40575 KS-test / p-value; A40843 SVDD hypersphere; A40575 side-balanced score-matched sampling to avoid a training-independent signature).
- **Distribution-alignment / self-augmented training to close the train/test gap** (A40892 VAE-prior init; A40921 free-generation SAT).

## Product / architecture implications (for an autonomy-trace / guardian stack)

- **Treat watermarks and fingerprints as evidence mechanisms, not prevention.** Almost every card states the recovered mark supports post-hoc attribution/governance/legal action and must be combined with access control, query monitoring, and provenance registries — not relied on to stop misuse.
- **Most agent-relevant items in this chunk:**
  - A40910 (CopyGuard) — an **ingestion-time policy gate on retrieved/user-supplied multimodal context** is the transferable pattern: enforce safety policy where untrusted content enters context (RAG ingestion, uploaded images), not only on the surface prompt; externalize policy checks into tools (verifier + risk analyzer + query rewrite).
  - A40909 (iSeal) — template for **tamper-evident model identity/attestation**: bind ownership evidence to an external secret (not weights), use similarity+error-correction instead of exact match, keep verification prompts under a trusted verifier to prevent overclaim, and assume the adversary controls inference end-to-end.
  - A40728 (RegionMarker) — embeddings feed RAG/agent memory; **provenance on embedding APIs** is a supply-chain control for the data agents consume.
  - A40546 / A41092 — **decode-time output watermarking** can tag agent-generated text for downstream attribution; both require control of the serving path and secret-key custody (treat the key as a credential).
  - A37038 / A40575 — **training-data / dataset provenance auditing** for the AI data supply chain (copyright, benchmark-contamination), subject to logit/grey-box access.
- **Verification-access is an architectural decision**: model+key detection is a deployment burden; external-secret + trusted-third-party verification (iSeal) or grey-box-log-prob detection (SPECTRA) are more deployable and, per iSeal, more robust to a full-access adversary.

## Open problems

- **Adaptive- and forgery-resistant provenance is largely unsolved / untested** across the chunk (spoofing an owner's mark to frame them is repeatedly named but not evaluated).
- **False-attribution / cross-owner collision rates** at scale are rarely quantified (raised for A38094, A40892, A40901, A40921, A41092).
- **Robustness to regeneration/purification** for generative-output watermarks and to RegionMarker-/scheme-aware adaptive attacks.
- **Closed-API auditing** without logit access (A37038, A40575, A40546 all gated by it).
- **Enforcement at the context/tool boundary against adaptive bypass** (A40910's CopyGuard is not stress-tested against obfuscated content or split payloads).
- **Cross-modal / cross-model-family generalization** of both marks and detectors.

## Most load-bearing papers in this chunk (by id)

- **A40909 (iSeal)** — strongest evidence in the chunk; the only genuinely adaptive, litigation-grade LLM ownership-verification threat model; directly informs model-identity/attestation design.
- **A40910 (CopyGuard / LVLM copyright)** — most directly agent-security relevant: guardrail bypass via the RAG/multimodal-context channel and a tool-augmented ingestion-time gate.
- **A39992 (DeepTracer)** — extraction-robust watermarking with adaptive+detection evaluation; supplies the reusable "in-distribution coupling" design principle.
- **A40575 (SPECTRA)** — realistic copyright-enforcement framing, meaningful scale (+5B tokens, <0.001% corpus fraction), decision-relevant p-value metric; the strongest training-data-provenance entry.
- **A39041 (box-free removal)** and **A37429 (GSPure)** — the load-bearing red-team demonstrations that black-box encapsulation / steganographic hiding are not security boundaries; the cautionary counterweight to the watermarking majority.
