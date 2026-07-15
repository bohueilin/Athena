# Pattern: Watermarking and Fingerprinting

> **Scope of evidence.** This pattern is grounded in the AAAI-26 corpus synthesis
> `syntheses/Model-IP-Protection.md` and its underlying research cards under
> `research-cards/Model-IP-Protection/`. It covers the *marking-and-verification* primitive: embedding a
> recoverable ownership/provenance signal into a model, its outputs, or its training data (watermarking),
> or deriving an intrinsic identifying signal without embedding (fingerprinting), and later verifying it
> against a suspect artifact. Load-bearing corpus papers, by role:
> **A40909** (iSeal — external-secret LLM ownership fingerprint; key-generated encoder + Reed-Solomon +
> similarity verification; trusted judge; the only *adaptive*, litigation-grade threat model);
> **A39992** (DeepTracer — extraction-survivable black-box classifier watermark; in-distribution,
> task-coupled trigger; adaptive + detection evaluation);
> **A38094** (OptMark — dual-placement diffusion-image watermark; trajectory placement as a robustness
> lever; TPR@FPR=1e-6); **A40561** (Anchor Watermark — latent-diffusion audio; ChaCha20 key custody +
> inversion/Soft-DTW recovery); **A40546** (WaterMod — decode-time LLM-text logit watermark; rank-mod-k;
> zero-bit + multi-bit); **A41092** (ARGH-Mark — LLM-text logit watermark; anchor sync + extended
> (8,4,4) Hamming); **A40728** (RegionMarker — EaaS embedding-API watermark; secret PCA + LSH regions;
> KS-test verification); **A39199** (robust GBDT/tabular watermark; in-place vs prunable-additive);
> **A40575** (SPECTRA — pre-publication training-data watermark; grey-box log-prob ratio test);
> **A37038** (SynPrune — syntax-aware code membership-inference auditor; grey-box logits);
> **A40843** (StyleSentinel — intrinsic style fingerprint; SVDD one-class; no embedding) and
> **A40851** (OFA — passive image-to-model attribution fingerprint; synthesis-free);
> **A40910** (CopyGuard — ingestion-time copyright policy gate on retrieved/uploaded context; the
> transferable agent pattern); **A37429** (GSPure — RED TEAM: white-box prune/cluster removal of
> scene-hiding 3DGS watermarks) and **A39041** (box-free removal — RED TEAM: query-based reverse
> engineering strips a black-box-encapsulated watermark). Image encoder-noise-decoder / in-generation
> siblings with largely truncated numbers: **A37103, A37412, A40892, A40901, A40921**. Paper ids (e.g.
> `A40909`) are the stable corpus ids from the synthesis source map (§20).
>
> **Evidence integrity (non-negotiable).** Every numeric value below is **author-reported and not
> independently verified**; where a card was silent or truncated the text says "not stated in paper".
> Values are **non-adaptive** unless the paper is explicitly noted as adaptive — only **A39992**'s
> adaptive/detection evaluation and **A40909**'s verification-time adversary rise above the non-adaptive
> bar; **A40728** is *semi*-adaptive (watermark-aware removal attacks, but not optimized against its
> secret-region design) and **A40843** is *partially* adaptive (permits attacker preprocessing but shows
> no fingerprint-aware evader). Calibrated language only: "reduced removal/evasion success against the
> tested, non-adaptive attacks", "requires production validation", never "secure / proven-safe /
> unbreakable". Items marked *(reviewer synthesis)* are cross-paper inference or engineering practice from
> the synthesis, **not a measured defense number from a single paper**. The single most important corpus
> caveat, repeated throughout: **watermarks and fingerprints are evidence, not prevention**
> (Model-IP-Protection §14), and **adaptive robustness and forgery/spoofing resistance are
> near-universally untested** across this corpus (§12).

---

## Problem addressed

You need to establish *provenance* — to later prove that a model, a generated artifact, or a training
corpus originated from (or was produced/used by) a specific owner — under conditions where the artifact
circulates outside your control. The corpus attacks this from three angles, all reducible to one
primitive (embed/derive a recoverable signal, then verify it against a deterministic threshold):

- **Output watermarking** — mark a model's *outputs* so any generated image (A38094, A37103, A37412,
  A40892, A40901, A40921), audio (A40561), text (A40546, A41092), or embedding vector (A40728) can be
  attributed after the fact.
- **Model fingerprinting** — bind ownership evidence to the *model itself*, either by injecting an
  external-secret fingerprint (A40909 iSeal) or by reading an *intrinsic*, non-embedded signal the model
  leaves (A40843 style hypersphere; A40851 passive image-to-model attribution).
- **Training-data / dataset provenance** — mark or audit *data* so unauthorized use in training is later
  detectable (A40575 SPECTRA pre-publication text watermark; A37038 SynPrune code membership inference).
- **Extraction-survivable ownership** — design the watermark so a *stolen/extracted* copy inevitably
  carries it (A39992 DeepTracer). (The stealing threat itself is the sibling pattern
  `model-extraction-defenses.md`; here the focus is the mark's survival property.)

The organizing thesis (Model-IP-Protection §14, §6, *reviewer synthesis* over nearly every card):
**a recovered mark or fingerprint is one probabilistic evidence signal supporting post-hoc attribution,
governance, and legal action — it does not by itself prevent misuse, copying, or reproduction.** Every
watermarking card in the corpus restates this. Treat the mark as evidence to be corroborated by access
control, query monitoring, and a provenance registry; never as a barrier.

A second decisive framing distinction (Model-IP-Protection §5, A40910): most of this corpus protects the
*owner's* IP by marking assets, but **A40910 (CopyGuard) inverts the problem** — it prevents a model from
*reproducing someone else's* copyrighted content that arrives through the retrieval/upload channel. That
is a content-compliance *policy gate*, the one directly agent-relevant control in the corpus, and it is
treated here as a distinct sub-pattern (see Control mechanism §5).

## Applicable assets and attack surfaces

- **Generated media / model outputs** — the primary output-watermarking surface: diffusion images
  (A38094, A40892, A40901, A40921, A37103, A37412), image-to-image outputs (A39041 is the removal attack
  on this surface), latent-diffusion audio (A40561), autoregressive LLM text (A40546, A41092), and EaaS
  embedding vectors (A40728). Richer/higher-fidelity outputs carry more payload but also give a remover
  more to work with *(reviewer synthesis)*.
- **Model weights and served inference** — the fingerprinting surface. Weight-embedded fingerprints are
  removable under white-box access (A40909's explicit critique); an *external* secret (key-generated
  encoder) survives weight access (A40909). Intrinsic fingerprints (A40851, A40843) read a signal the
  model emits without any embedding.
- **Distributed model files / assets** — high-value assets shipped in the clear, e.g. 3D Gaussian
  Splatting scenes (A37429 is the white-box purification attack), and tabular GBDT models (A39199). Once
  distributed, an embedded mark is subject to offline removal with no query-side telemetry (A37429).
- **Training / evaluation corpora** — the data-provenance surface: text watermarked before publication
  (A40575) and code audited for pretraining membership (A37038). This is the data-supply-chain surface an
  agent's models are built on.
- **The retrieval / upload / RAG context channel** — the *policy-gate* surface (A40910): copyrighted
  content entering a multimodal model as retrieved or uploaded context bypasses surface-prompt refusal.
  Directly relevant to any agent that ingests external content.
- **The verification secret itself** — the ChaCha20 key (A40561), the secret PCA projection + trigger
  regions (A40728), the key-generated encoder + RSC parameters (A40909), the decode-time hash key /
  RNG seed and anchor pattern (A40546, A41092), the watermark key set (A39992), the scoring model +
  retained originals (A40575), and the one-class hypersphere / carriers (A40843, A38094). These are
  **credentials** and are part of the trust boundary (§15).

## Threat model

From Model-IP-Protection §3–§4. Cluster by adversary posture:

- **Defender embeds a mark; adversary applies generic, off-the-shelf transforms to strip it; evaluated
  NON-adaptively (dominant).** The single most replicated posture — stated by A37103, A37412, A38094,
  A40546, A40561, A40892, A40901, A40921, A41092, and A39199. Adversary knowledge is effectively
  black-box on the mark; attacks are fixed distortions/edits (JPEG, blur, crop, rotate, resample,
  pitch-shift, MP3, paraphrase, token insert/delete/replace, VAE regeneration), not scheme-aware
  optimization. **Read "robust" throughout as "robust against the tested, non-adaptive attacks."**
- **Adversary controls end-to-end inference / litigation setting (strongest, safest to assume).**
  A40909 (iSeal): white-box weight read/modify, collusion-based fingerprint unlearning (fine-tune away
  disclosed prompt-response pairs), and output/response manipulation to evade exact match. This is the
  most adversarially realistic threat model in the corpus and the one to design against.
- **Semi-adaptive / watermark-aware removal.** A40728 (RegionMarker): CSE cluster-and-remove,
  paraphrasing (NLLB translation + gpt-4o-mini rewriting), and dimension-perturbation (shift / removal /
  permutation) — watermark-aware but not optimized against the secret-region design.
- **White-box asset purification.** A37429 (GSPure): the adversary holds the distributed 3DGS file,
  renders arbitrary views, and clusters/prunes low-contribution watermark primitives — no query telemetry
  is available. A39199's threat: post-deployment fine-tuning + pruning of a redistributed GBDT.
- **Black-box query reverse-engineering.** A39041: identity-inducing queries to a wrapped image-to-image
  API expose the hiding network, strip the (additive-separable) mark, leak the private clean output, and
  enable a watermark-free surrogate.
- **Grey-box log-prob adversary/auditor (for data provenance).** A40575 and A37038 require token
  log-probabilities from the suspect model; weights/architecture not needed. A40575 does *not* model an
  adversary who strips the watermark from training data.
- **Guardrail bypass via the context channel (most agent-relevant).** A40910: the refusal that holds for
  a direct infringing request does *not* generalize when the copyrighted content arrives as retrieved /
  uploaded multimodal context; models ignore copyright notices (author-reported 11/12 LVLMs fail).
- **Watermark forgery / spoofing (the near-universal gap).** Fabricating an owner's mark to *frame* them,
  or overclaiming ownership of another's model, is repeatedly named (A40909 partially defends overclaim;
  A38094, A40546, A41092, A40901 name it) and **almost never evaluated** (§4, §12).

Knowledge assumptions cluster as: black-box on the mark for generative-output watermarking; white-box on
the asset/model for the removal attacks (A37429) and iSeal's adversary (A40909); grey-box log-prob access
for the data-provenance methods (A40575, A37038). **Design consequence:** assume the adversary eventually
controls inference end-to-end and knows the scheme (A40909's posture); every other case is weaker.

## Control mechanism

A layered evidence control; no single layer is sufficient. Verification is **deterministic** in every
scheme (a threshold on a secret-conditioned statistic), which is what makes the control fail-closed and
auditable.

1. **Output watermark (attribution of generated content).** Embed a recoverable message and verify by a
   deterministic detection statistic:
   - *Generative-trajectory placement* (A38094 OptMark): a **structure** watermark at the initial latent
     `x_T` (survives regeneration) plus a **detail** watermark at a late timestep `t_d∈[200,300]` (survives
     geometric/valuemetric transforms); decode via a frozen encoder + carrier dot-product; verify by bit
     accuracy → TPR at a fixed low FPR (1e-6). *Placement in the trajectory is the robustness lever.*
   - *Latent embedding + inversion recovery* (A40561 Anchor): encrypt bits with a secret key, map into the
     Gaussian initial latent, recover by DDIM inversion refined against an unguided **anchor trajectory**
     via Soft-DTW; verify by bit accuracy > τ → TPR@FPR.
   - *Decode-time logit biasing* (A40546 WaterMod: rank-mod-k residue partition + entropy gate;
     A41092 ARGH-Mark: RG-balanced partition + periodic anchors + extended (8,4,4) Hamming); verify by a
     z-score / match-rate over green-token counts against a binomial null.
   - *Secret-region semantic watermark for EaaS* (A40728 RegionMarker): secret PCA projection → LSH region
     partition → per-region embedding-as-watermark; verify by a **KS-test p-value < 0.05**.
2. **Model fingerprint (ownership under a white-box adversary).** Bind evidence to a secret held *outside
   the weights* — a key-generated encoder — fine-tune to reconstruct **Reed-Solomon-encoded** targets, and
   verify by **similarity + error-correction, not exact match**, with prompts queried only by a trusted
   judge (A40909 iSeal). Removal by weight access alone cannot erase an external secret; similarity+ECC
   survives output manipulation; judge-only prompts prevent overclaim.
3. **Intrinsic (no-embedding) fingerprint (retroactive protection).** Where you cannot pre-embed (content
   already published), verify a *leaked* intrinsic signal: a one-class **SVDD hypersphere** around an
   artist's style embeddings (A40843 StyleSentinel), or a passive **image-to-model** attribution head over
   architecture-dependent spectral fingerprints (A40851 OFA). Verification is a similarity/boundary test at
   an operating threshold.
4. **Training-data provenance (grey-box).** Watermark text **before publication** by paraphrasing and
   score-matched sampling so no distribution shift is introduced, then verify by a **log-prob ratio test**
   (A40575 SPECTRA); or audit code pretraining membership by AST-pruning syntactically-forced tokens and
   thresholding a syntax-pruned membership score (A37038 SynPrune).
5. **Ingestion-time policy gate (agent content-compliance — A40910 CopyGuard).** At the point untrusted
   content enters context, run a tool-augmented pipeline: **copyright-notice identifier → source/status
   verifier → query-risk analyzer that rewrites risky queries toward transformative use → status reminder
   injected to the model.** This is the transferable agent pattern — enforce policy where content enters,
   not only at the surface prompt.
6. **Extraction-survival design (when the copy will be stolen).** Make the ownership watermark
   **in-distribution and task-coupled** so a stolen model that copies functionality inevitably copies the
   mark (A39992 DeepTracer). Verify by accuracy on a secret key set > τ (a 20% threshold is cited for
   hard-label ownership confirmation). See `model-extraction-defenses.md` for the full extraction layer.

## Preconditions and trust assumptions

- **Owner controls the marking point and holds the secret.** Output watermarks require control of the
  generation/serving path — inference-time optimization (A38094), the initial-latent embed (A40561), the
  decoding loop's logits (A40546, A41092), or the embedding API (A40728). This is **first-party provider**
  territory, not post-hoc marking of arbitrary third-party artifacts (A38094, A40546 explicitly). Data
  watermarks require marking **before publication** (A40575). Fingerprint injection happens during
  training/fine-tuning (A40909, A39992, A39199).
- **A trusted verifier / registration authority exists for the strongest scheme.** iSeal (A40909) requires
  a trusted judge + registration authority with black-box API access to suspect and registered models;
  verification prompts are queried **only** by the judge to prevent overclaim. Its guarantees collapse if
  the authority or key custody is compromised — that is out of the evaluated model.
- **Verification-access is a deployment-defining assumption, and it differs sharply by scheme (§10, §15):**
  - *Owner-white-box (model + key):* A40546 and A41092 reconstruct the green list by re-running the model
    with the key; A40561 runs inversion + anchor optimization against candidate anchors with the owner's
    model. Heavy deployment burden; not a black-box third-party detector.
  - *Trusted-judge black-box:* A40909 needs only API access to the suspect, plus the external secret.
  - *Grey-box log-probs:* A40575, A37038 need token probabilities from the suspect; closed APIs that
    withhold them defeat these methods (mitigated only via a court-appointed arbiter with access).
  - *Fully passive:* A40851 needs only the suspect image.
- **Secrecy assumptions are load-bearing and mostly un-leakage-analyzed.** A40728's security rests entirely
  on the attacker being unable to recover the PCA matrix / trigger regions; A40561 on the ChaCha20 key;
  A40546/A41092 on the hash key/seed and anchor pattern; A40909 on the key/encoder; A39992/A39199 on the
  watermark key set. None of these papers provide a partial-key-leakage analysis.
- **Structural assumptions the marks depend on.** A39992 assumes coupling the watermark within the primary
  task distribution forces a stolen model to learn it (validated by neuron-activation heatmaps).
  A40843/A40851 assume an intrinsic signal (style / architecture spectral fingerprint) persists and is
  distinctive. A40561 assumes CFG and unguided diffusion trajectories stay statistically close (K-S test
  at most steps). If the assumption fails, the mark fails.
- **Fail-closed, least-privilege framing** *(reviewer synthesis, consistent with A40909's
  end-to-end-inference posture):* expose the minimum output granularity clients need; treat every
  verification secret as a governed credential with custody and rotation (§15); route verification through
  a trusted party where possible; and treat a positive verification as evidence for governance/legal
  review, not an automatic enforcement trigger.

## System architecture

```
        ┌──────────────────────── OWNER / PROVIDER TRUST ZONE ─────────────────────────┐
        │                                                                              │
 model  │  [ MARKING POINT ]                         [ SECRET-CUSTODY STORE ]          │
 / data │   • output watermark: trajectory (A38094), init-latent (A40561),  ◄──credential:
 / gen  │     decode-time logits (A40546/A41092), EaaS region (A40728)       ChaCha20 key (A40561),
        │   • model fingerprint: external-secret encoder + RSC (A40909)       PCA+regions (A40728),
        │   • intrinsic fingerprint: NONE embedded — learn hypersphere/       hash key+anchor (A40546/
        │     attribution head from owned artifacts (A40843/A40851)           A41092), key-gen encoder+
        │   • data watermark: pre-publication paraphrase+score-match (A40575)  RSC (A40909), key set
        │   • extraction-coupled trigger (A39992)                             (A39992/A39199)
        │           │                                                    rotate + version (§15,§16)     │
        │           ▼                                                                                    │
        │   [ served model / published artifact / released dataset ]                                    │
        │           │                                                                                    │
        │   ── for RAG/agent ingestion of EXTERNAL content: ──►  [ INGESTION POLICY GATE (A40910) ]      │
        │        notice-identifier → source verifier → query-risk analyzer/rewriter → status reminder    │
        │           │  telemetry                                                                          │
        │           ▼                                                                                     │
        │   [ provenance registry + verification audit trail ]  (issued marks, key-custody events)       │
        └───────────┼─────────────────────────────────────────────────────────────────────────────────┘
                    │
  ── suspect artifact / model / dataset appears in the wild ──
                    ▼
      [ VERIFIER ]   (prefer a TRUSTED JUDGE, offline, black-box — A40909)
        • deterministic threshold test:
            bit-acc/TPR@FPR (A38094,A40561) · z-score/match-rate (A40546,A41092) ·
            KS p<0.05 (A40728) · similarity J(·)>ω + RSC (A40909) · one-class boundary (A40843) ·
            log-prob ratio p-value (A40575) · WSR>τ (A39992) · syntax-pruned AUROC>ε (A37038)
        • MANDATORY benign / independently-owned control must FAIL the test  (false-attribution bound)
                    ▼
      [ governance / legal review ]   ← evidence, not automated enforcement (§14)
```

Key architectural decisions (§15): **put verification logic — thresholds, error-correction, key custody —
in a trusted third party, not the deployed model** (A40909); **choose the verification-access model
deliberately** — owner-white-box detection (A40546, A40561) is heavier than trusted-judge black-box
(A40909) or grey-box log-prob (A40575); **treat every secret key as a governed credential** with custody
and rotation (A40546, A40561, A40909, A41092); and **put the policy gate where untrusted content enters
context** (A40910), not only at the surface prompt.

## Recommended implementation pattern

- **Place output watermarks in the generative trajectory, not at the pixel/surface level (A38094).** Use a
  dual mark — early-latent structure component for regeneration robustness plus a late-timestep detail
  component (`t_d∈[200,300]`) for transform robustness. Shape the mark to match low- and high-order moments
  of benign noise (mean/variance/kurtosis/skewness regularizers) for imperceptibility, and use the adjoint
  method for O(1)-memory optimization through the ODE solver. Verify by TPR at a *fixed low FPR* (1e-6),
  reported with paired quality metrics (FID/CLIP).
- **For latent-diffusion media, embed in the initial latent and recover by anchor-aligned inversion
  (A40561).** Encrypt bits with a secret stream cipher (ChaCha20), map them into the Gaussian initial
  latent via distribution-preserving sampling (generation unchanged, low FAD/IS bias), and at verification
  reduce inversion error by optimizing the inverted trajectory toward an unguided-diffusion anchor
  trajectory with Soft-DTW. Report **TPR@FPR and bit accuracy** across a distortion suite, and note that
  **FPR grows with the number of anchors N** — bound N or accept higher verification cost.
- **For LLM text, bias logits at decode time with a coded, synchronization-aware scheme (A40546, A41092).**
  Partition the probability-sorted vocabulary by a residue class (rank mod k) so a high-probability token
  always survives (A40546), or use an RG-balanced ±δ partition (A41092, δ=5.0). Add **error-correcting
  codes** — extended (8,4,4) Hamming (A41092) or per-position majority vote (A40546) — and **periodic
  anchors** to resist insertion/deletion desynchronization (A41092). Keep payloads in the reliable regime
  (**≤32 bits, longer generations L≥384** for A41092). Detection needs the model + secret key; treat that
  as a deployment constraint.
- **For embedding APIs (EaaS), use secret-projection semantic regions (A40728).** Project through a *secret*
  PCA matrix (uniform region occupancy defeats cluster-and-remove), partition via LSH into `2^d` regions,
  select `R=α·2^d` trigger regions, and use the **in-region text embedding itself** as the per-region
  watermark (defeats dimension-perturbation). Verify with a conservative KS-test (**p<0.05**, combined
  across watermark levels). Evaluate against removal **and** paraphrasing **and** dimension-perturbation
  *jointly* — defeating any single family defeats the defense.
- **Bind model ownership to an external secret and verify tolerantly (A40909).** Use a key-generated
  encoder (secret lives outside the weights), fine-tune to reconstruct Reed-Solomon-encoded targets, and
  verify by **similarity J(·) > ω with RSC error correction, never exact match**. Do **not** publicly
  disclose any verification prompt-response pair (that enables collusion unlearning). Route all
  verification through the trusted judge.
- **When you cannot pre-embed, use an intrinsic fingerprint with an operating-point policy (A40843,
  A40851).** Learn a one-class boundary (SVDD hypersphere) around owned artifacts, augmenting a sparse
  portfolio while preserving the protected attribute (A40843's semantic self-reconstruction); or train a
  passive attribution head (A40851). Always attach a **calibrated threshold / ROC operating point and a
  false-accept analysis** — a one-class boundary can misclassify superficially similar non-members.
- **For training-data provenance, watermark before publication with no distribution shift (A40575).**
  Generate paraphrases, score each with a separate pre-cutoff scoring model (Min-K%++), and use
  **score-matched, side-balanced sampling** (weights `exp(-α|r-1|)`, α=100) so the watermark plants no
  training-independent signature (which would cause false positives). Verify by the grey-box ratio test
  (no non-member set needed). For code, **AST-prune syntactically-forced tokens** before the membership
  score (A37038). Prefer a **decision-relevant p-value separation** over AUROC for enforcement claims.
- **Design extraction-survivable ownership marks in-distribution and task-coupled (A39992).** Select source
  classes spanning the primary feature space, assign the least-likely target label under a benign model
  (false-positive control), couple with an intra/inter-class centroid loss, and filter key samples by the
  **victim-pass / surrogate-pass / benign-fail** rule.
- **For non-differentiable tree models, embed in place, not by appending trees (A39199).** In-place split/leaf
  updates entangle the mark with structure; appended trees are prunable. Duplicate watermark samples so
  their gradients dominate, and keep the watermark ratio out of the observed high-variance low-ratio regime.
- **Gate ingested content at the boundary (A40910).** Compose external tools — notice identifier, source/
  status verifier, query-risk analyzer that rewrites toward transformative use, and a status reminder —
  rather than relying on the model's surface-prompt refusal or on a static blocklist (so it adapts as
  copyright status changes).

## Incorrect or fragile implementation patterns

- **Separable / "inactive" / steganographic marks — a separable mark is a removable mark (§6).** A37429:
  watermark Gaussians with low, viewpoint-inconsistent contribution are clusterable and prunable
  (author-reported up to **16.34 dB** watermark-PSNR reduction with **< 1 dB** scene loss), breaking three
  scene-hiding 3DGS schemes. A39041: an additive-separable mark behind a black-box wrapper is exposed by
  identity-inducing queries (author-reported **~100% removal**, PSNR up to **34.69 dB**), additionally
  leaking the private clean output. **Do not treat steganographic hiding or black-box encapsulation as a
  security boundary.**
- **Weight-embedded fingerprint + exact-match verification (A40909's explicit critique).** A fingerprint
  living only in weights is removable under white-box access, and exact-match verification is evadable by
  output manipulation. Bind to an external secret; verify by similarity + ECC.
- **Publicly disclosing verification prompt-response pairs (A40909).** Disclosure enables collusion-based
  unlearning (fine-tune away the disclosed records) and reverse engineering, invalidating future claims.
- **Pixel-level / post-hoc surface marks for generative media.** A38094: pixel-level watermarks are
  provably removable by generative regeneration; a detail mark placed too near the final image behaves like
  a pixel mark (artifacts + regeneration-fragile). Latent/in-generation embedding preserves quality and
  survives regeneration (recurring across A37412, A38094, A40561, A40892, A40921).
- **Out-of-distribution trigger watermarks for extraction survival (A39992).** OOD watermark tasks activate
  disjoint neuron regions; a stolen model never exercises them and **forgets the mark**. Couple the trigger
  in-distribution.
- **Single-attack-family robustness for EaaS (A40728).** Prior schemes each fell to one family
  (EmbMarker/WARDEN/EspeW to paraphrasing; WET to dimension-perturbation). An attacker who defeats any one
  attack defeats the defense.
- **Surface-token / trigger-word semantics (A40728, A40546).** Semantically empty trigger words are removed
  by paraphrasing; random green/red splits that exclude the top token erode fluency.
- **Additive tree watermarks (A39199).** Appended low-contribution trees are prunable; naive label flips
  wash out under later fine-tuning or harm accuracy without gradient-dominance duplication.
- **Relying on passive membership inference at scale (A40575).** Standard MIA collapses to near-random
  (author-reported ROC-AUC **~0.50–0.56 at +5B tokens**) — not a dependable provenance signal on its own;
  and planting a *consistent-high-score* watermark creates a training-independent false-positive signature.
- **Enforcing copyright policy only at the surface prompt (A40910).** Refusal that holds for direct requests
  does not generalize to retrieved/uploaded context; embedded notices are ignored (11/12 LVLMs). Naive
  fine-tuning for awareness over-refuses legitimate/transformative tasks — gate at ingestion instead.
- **Presenting any mark or fingerprint as prevention (§14).** The mark does not stop the theft, copy, or
  reproduction; it only supports post-hoc attribution.

## Verification strategy

Every scheme verifies with a **deterministic threshold on a secret-conditioned statistic**, run by the
owner or (preferably) a trusted third party against the suspect artifact. Cross-cutting requirement:
**always run a benign / independently-owned artifact through verification and require it to FAIL** — this
is the only false-attribution bound most schemes provide.

- **A38094 (diffusion image):** decode the message via the frozen encoder + carriers; declare a match by
  bit accuracy → **TPR at a fixed FPR = 1e-6** across geometric/valuemetric/editing/regeneration attacks;
  report paired FID/CLIP.
- **A40561 (audio):** run inversion + anchor-trajectory Soft-DTW optimization, recover bits, declare
  attribution when **bit accuracy > τ**; report **TPR@FPR**; for N anchors, take argmax bit-match and note
  **FPR(τ,N)** grows with N.
- **A40546 / A41092 (LLM text):** reconstruct the green list with the model + secret key; compute a
  **z-score over green-token counts** (binomial null, ε=0.5 for k=2 / p0=1/k) or an anchor-guided
  **match-rate** with per-bucket majority vote + Hamming correction.
- **A40728 (EaaS):** build backdoor (in-watermark-region) and benign corpora, compare cosine/L2 distance
  distributions to the region watermark, declare infringement if the **KS p-value < 0.05** (combined
  conservatively across watermark levels).
- **A40909 (LLM fingerprint):** the **trusted judge** queries the suspect API, decodes with Reed-Solomon,
  and matches by **similarity J(·) > ω**; prompts are judge-only to prevent overclaim.
- **A40843 / A40851 (intrinsic fingerprint):** attribute iff the artifact's style vector falls **inside the
  one-class hypersphere** (A40843) or the pairwise attribution head clears an **AUC/OSCR operating point**
  (A40851) — always at a calibrated threshold with a stated false-accept rate.
- **A40575 (training data):** compute Min-K%++ score ratios under target vs scoring model; test whether the
  mean ratio drops after training; report the **member/non-member p-value gap** (no non-member set needed).
- **A37038 (code):** AST-prune syntactically-forced tokens, compute the syntax-pruned membership probability
  SPP(x), threshold at ε; report **AUROC** across models × member/non-member ratios × function lengths.
- **A39992 / A39199 (model ownership):** query the suspect on the secret key set; flag if **WSR / forced-
  prediction rate > τ** (20% cited for hard-label in A39992); benign-fail filtering / low-impact candidate
  selection is the false-positive control.

## Metrics and thresholds

All values **author-reported**, on each paper's own datasets, **non-adaptive unless noted**, not
independently verified. No threshold is "safe" — each is scoped to the tested attack set.

- **TPR @ fixed low FPR** — A38094 reports at FPR=1e-6 across four attack families (headline SOTA-robustness
  claim; per-attack numbers largely **not stated in paper** in the reviewed text). A40561: author-reported
  **avg TPR 98% / Bit Acc 99%** across ten distortions; **100% TPR** on clean audio; worst case (high
  pitch-shift) ~**93% TPR / ~85% Bit Acc**; strongest baseline (GROOT) reported far lower (avg TPR 16% /
  Bit Acc 19%). Non-adaptive.
- **Detection AUROC / z-score (text)** — A40546: multi-bit vs MPAC, author-reported **AUROC 98.29 vs 48.40**
  on MBPP+ code, +26.94% GSM8K accuracy, +27.18% pass@1; near-perfect detection under generic rewriting
  (non-adaptive). A41092: match rate and bit accuracy **> 99.9%** in most clean configs (e.g. C4/OPT-1.3B
  8-bit **99.90** vs CyclicShift 97.00 / ECC 99.00 / CTWL 83.00); 32-bit at L=200 falls to **~96.0%**;
  robustness-under-attack numbers largely truncated → **not stated in paper**.
- **KS p-value < 0.05** for EaaS infringement; utility ~**92–94%** accuracy preserved (dropping to ~**87.9%**
  under CSE) — A40728. Semi-adaptive.
- **Fingerprint Success Rate (FSR)** — A40909: author-reported **100% FSR on 12 LLMs against >10 attacks**
  (incl. collusion unlearning + response manipulation), while baselines drop to **0%** under those attacks.
  **Adaptive verification-time evaluation.** "100%" is scoped to the evaluated attacks.
- **Attribution AUC / OSCR (image fingerprint)** — A40851: author-reported attribution AUC **94.05%**
  (DMDetection) and **83.05%** (AIGCBenchmark, notably lower — uneven generalization); OSCR **85.08%**
  (GenImage), **88.48%** (OSMA); closed-set accuracy **98.67%** (OSMA). Non-adaptive; no removal/forgery
  testing. A40843: one-sample verification claimed superior to baselines; specific metric values **not
  stated in the extracted text**.
- **p-value separation (training data)** — A40575: author-reported **≥ 9 orders of magnitude** member/
  non-member gap at **< 0.001% corpus fraction** and **+5B-token** continued pretraining (> 3 orders better
  than STAMP's ≤ 3); motivating baseline MIA collapse to ROC-AUC **~0.50–0.56** at 5B tokens.
  Continued-pretraining, not from-scratch.
- **AUROC (code membership)** — A37038: author-reported **+15.4% average AUROC** over baselines across
  4 models × 3 ratios (Python only, grey-box).
- **WSR / ΔAcc (extraction-coupled watermark)** — A39992: near-100% WSR on stolen models; stays above the
  **20%** hard-label ownership threshold; two-stage filtering drove stolen WSR **94.61% → 95.86% → 98.75%**
  and benign WSR to **0%**; ΔAcc −0.06 (FMNIST) / +0.28 (CIFAR-10) / −0.95 (CIFAR-100). Adaptive+detection.
- **Watermark rate / ΔAccuracy (GBDT)** — A39199: many settings reach **1.000** watermark rate with low
  accuracy loss, but **high variance at low watermark ratios** (|W|/|Dtrain| ≤ 0.01). Non-adaptive.
- **Attacker-side benchmarks you must defend against** — A37429: up to **16.34 dB** watermark-PSNR reduction
  with **< 1 dB** scene loss; A39041: **~100% removal** / PSNR up to **34.69 dB**.

## Test cases

Exercise the removal/edit suite the corpus demonstrates, plus a mandatory false-positive control and a
utility regression, for whichever sub-pattern you deploy:

1. **Image-watermark transforms (A38094):** geometric (flip, 40° rotation, 60% resize, 60% center crop),
   valuemetric (color jitter, Gaussian blur, contrast, 50% JPEG, saturation), editing (meme, random erase,
   text overlay, InstructPix2Pix), and regeneration (VAE / diffusion) — verify TPR@FPR=1e-6 and paired
   FID/CLIP hold.
2. **Audio-watermark distortions (A40561):** 32 kHz resample, 100 Hz high-pass, 1000 Hz low-pass, 10%
   amplitude scale, 9 kbps MP3, 8-bps recount, 15-sample median filter, 5 dB Gaussian noise, 60% crop,
   0.5-semitone pitch shift (the hardest) — verify TPR@FPR and Bit Acc; sweep intensity.
3. **Text-watermark edits (A40546, A41092):** strong paraphrasing/rewriting (A40546); token
   insertion/deletion/replacement at varying proportions (A41092) — verify z-score/match-rate; sweep
   payload bits (A41092: confirm the ≤32-bit / L≥384 reliable regime).
4. **EaaS attacks, jointly (A40728):** CSE cluster-and-remove; paraphrasing (NLLB + gpt-4o-mini);
   dimension-shift / reduction / permutation — verify KS p<0.05 under *each and their stacking* (stacking is
   the corpus gap).
5. **White-box asset purification (A37429) and model removal (A39992, A39199):** prune/cluster low-
   contribution watermark primitives; fine-tune, prune, quantize, transfer-learn — verify the mark survives
   within usable-accuracy ranges.
6. **Query reverse-engineering (A39041):** craft near-identity queries against a wrapped generator; verify
   the watermark and clean output are not both recoverable.
7. **Fingerprint verification-time attacks (A40909):** collusion unlearning of disclosed records; output/
   response manipulation; overclaim attempts — verify FSR holds and non-owners cannot overclaim.
8. **Training-data provenance (A40575, A37038):** verify the ratio-test p-value gap / SynPrune AUROC on
   watermarked-and-trained vs untrained models; include structured/conversational text (A40575's weak spot).
9. **Ingestion policy gate (A40910):** book excerpts, news, lyrics, code docs × repetition/extraction/
   paraphrase/translation × with/without notice (textual and image-embedded) — verify the gate rewrites or
   refuses; watch for over-refusal of transformative use.
10. **MANDATORY false-attribution control:** run an independently-owned / benign artifact through
    verification and require it to **FAIL** (A39992 benign-fail; A40728 benign corpus; A40575 score-matched
    sampling; A40843/A40851 base-rate/FPR).
11. **Utility regression:** measure generated-output quality, embedding accuracy, or model ΔAcc to confirm
    the mark does not degrade the service (A38094 FID/CLIP; A40561 FAD/IS t-test; A40728 task ACC/F1;
    A39992/A39199 ΔAcc).
12. **Key-secrecy handling:** confirm keys/projections/encoders/anchors are never returned to clients and
    live only in the custody store.

## Adaptive adversarial tests

This is the corpus's single biggest gap (§12) and where you must go **beyond** what the papers validated —
mark all of these **"requires production validation"**:

- **Scheme-aware watermark removal.** An adversary who knows the *placement* and optimizes against it:
  targeted denoising at the known detail timestep `t_d` or optimization-based erasure of a diffusion mark
  (A38094 does not evaluate this); regeneration/diffusion-purification of audio (A40561 tests only signal
  distortions); key-aware or top-2-parity-targeting attacks on text watermarks (A40546, A41092 test only
  generic rewriting / fixed edits).
- **Anchor / synchronization attacks (A41092).** The authors themselves note the anchor "remains
  susceptible to adversarial manipulations" — test anchor imitation, anchor stripping, and paraphrase/
  back-translation loops (strongest against token-level marks, not reported).
- **RegionMarker-aware attacker (A40728).** Jointly attack regions *and* dimensions; estimate the provider's
  PCA basis from many queries; stack paraphrase → dimension-shift → CSE (the stated gap).
- **Query-screener evasion (A39041).** Vary query statistics to defeat the near-identity screener (proposed
  but not rigorously benchmarked).
- **iSeal-aware distillation / heavy fine-tuning / output-distribution shaping (A40909).** "100% FSR" is
  scoped to the evaluated attacks; a stronger adaptive adversary aware of the RSC/similarity design is not
  exhaustively bounded.
- **Fingerprint-aware evasion for intrinsic marks (A40843, A40851).** Style-mixing / multi-artist LoRA /
  targeted style perturbation to fall outside the hypersphere (A40843's threat model permits attacker
  preprocessing but shows no such evader); laundering (recompression, resize, print-scan) or deliberate
  spoofing of another model's spectral fingerprint (A40851 untested, amplitude-spectrum known fragile).
- **Training-data watermark removal (A40575).** Deduplicate, re-paraphrase, or filter scraped text before
  training (explicitly not modeled); MIA-aware training / canary suppression for code (A37038).
- **GBDT adaptive erasure (A39199).** Dedicated watermark-removal / distillation / overwriting (only generic
  fine-tuning is tested).
- **Adaptive bypass of the ingestion gate (A40910).** Obfuscated content, adversarial images, split payloads
  across turns against the notice-identifier / query-rewriter (CopyGuard is not stress-tested this way).
- **Forgery / spoofing (the universal gap).** Attempt to fabricate an owner's mark to *frame* them, or to
  overclaim ownership. Repeatedly named, almost never evaluated (§4, §12). **Do not launch attribution
  claims in adversarial/litigation settings without it** (A38094, A40546, A41092, A40901, A40909).

## Telemetry requirements

- **Query-boundary telemetry (the only live detection surface for query-driven attacks).** Per-account
  query volume/rate, input-distribution monitoring, and near-identity query detection (A39041's screener
  signature), anomalous embedding-query patterns (A40728). Extraction/reverse-engineering is query-driven,
  so this is where it is observable *(reviewer synthesis over A39041, A40728)*. Note the **asymmetry**:
  offline asset purification (A37429) and offline dataset scraping (A40575) leave **no query telemetry** —
  detection must shift to verification of suspect artifacts and to registries.
- **Verification audit trail.** Record key-custody events, judge queries, RSC-decoded matches, the threshold
  decision, and the benign-control result for each verification (A40909 monitoring implications; A37038 and
  A40575 treat results as audit records feeding governance).
- **Provenance registry.** Issued marks/keys/anchors, embedding-time parameters (α, λ, δ, timesteps, region
  sets), payload↔owner/instance bindings (multi-bit tenant IDs from A38094 48-bit, A40546/A41092 multi-bit),
  and scheme versions — so a later suspect is checked against the right secret and a broken scheme can be
  identified and rotated.
- **Ingestion-gate telemetry (A40910).** Log content source, notice status, and the gate's decision/rewrite
  for every ingested item, for auditability and incident review.
- **Utility/quality baselines** logged alongside (FID/CLIP, FAD/IS, task ACC, ΔAcc), so a defensive re-mark
  can be shown not to have degraded the service, and a marked artifact can be distinguished from a benign one.

## Failure handling

- **Treat every verification output as probabilistic evidence, not an enforcement trigger.** Route a
  positive verification to governance/legal review; do not auto-act (A37038, A40575, A40909 deployment
  implications; §14).
- **Never single-signal.** Because every mark is scoped to a non-adaptive threat model, a failed or
  ambiguous verification should degrade to corroborating evidence (registry, query telemetry, key-custody
  records), not a definitive verdict. Combine watermark evidence with access-control logs.
- **Conditional-on-usability protection is a first-class failure mode (A39992).** Extraction-watermark
  robustness holds only while the stolen model stays usably accurate; an accuracy-sacrificing adversary
  weakens verification. Similarly A39199 degrades at low watermark ratios — treat low-ratio verdicts as
  low-confidence.
- **Fail-closed at the ingestion gate (A40910).** On an unresolved copyright-status lookup or an unparseable
  notice, **rewrite toward transformative use or refuse**, rather than reproducing the content — the
  deterministic, least-privilege default. Watch the opposite failure (over-refusal of fair use) and tune the
  query-risk analyzer, not a blunt blocklist.
- **Fail-closed at the query boundary** *(reviewer synthesis):* on a near-identity-query trip or quota
  exhaustion, throttle/deny rather than continue serving.
- **Verification-cost failures.** Owner-white-box schemes (A40561's per-anchor Soft-DTW optimization; A40546/
  A41092's model re-run) are compute-bearing; on verifier overload, queue and degrade gracefully rather than
  skip the benign-control check.

## Rollback and containment

- **Rotate the secret, re-mark going forward.** Keys/projections/encoders/anchors are governed credentials
  (§15); on suspected compromise or a demonstrated break (as A37429, A39041, and the A40728-documented prior
  schemes were broken), **revoke the key, rotate to a fresh secret, and re-embed for future artifacts.**
  Version the registry so old and new marks are both verifiable (§16: pin and version keys + verifier).
- **Retire and replace a broken scheme.** When a scheme is shown vulnerable (steganographic-hiding or
  additive-separable marks per A37429/A39041; single-family EaaS marks per A40728; passive weight-embedded
  exact-match fingerprints per A40909), migrate the *design*, not just the key.
- **Contain query-driven attacks at the boundary.** Throttle or block offending accounts/query patterns
  (A39041, A40728).
- **Accept the irreversibility of provenance failures.** Marking and verification are **post-hoc** — an
  already-extracted surrogate, an already-purified 3DGS asset (A37429, offline, no telemetry), or an
  already-published-then-scraped dataset (A40575 protects only content watermarked *before* release) cannot
  be "rolled back". Containment limits *future* loss and preserves *attribution* evidence; it does not undo
  the copy or reproduction (§14).

## Known bypasses

From Model-IP-Protection §11 (all author-reported, against *other* schemes, under the bypasser's own
evaluation):

- **A37429 (GSPure)** breaks three scene-hiding 3DGS watermarks — GS-Hider, Splats-in-Splats, SecureGS — via
  white-box clustering/pruning of low-contribution, viewpoint-inconsistent watermark Gaussians (up to
  **16.34 dB** watermark-PSNR reduction, **< 1 dB** scene loss). Single dataset (Mip-NeRF360), non-adaptive
  victims.
- **A39041** breaks two box-free image-to-image watermarks (VWu, VZhang) with **~100% removal** (PSNR up to
  **34.69 dB**) via identity-inducing queries, and enables watermark-free surrogate training; its proposed
  query-screener defense is not rigorously benchmarked.
- **A40728** documents prior EaaS watermarks each broken by a single family: EmbMarker, WARDEN, EspeW by
  paraphrasing; WET by dimension-perturbation.
- **A40575** documents that prior membership inference collapses to near-random at scale (ROC-AUC
  **~0.50–0.56 at +5B tokens**) — a bypass of passive MIA as a provenance signal.
- **A40909** documents the failure classes it defends against: passive-fingerprint forgery/overclaim,
  weight-embedded fingerprint removal under white-box access, and exact-match evasion by output manipulation.
- **A40910** demonstrates the LVLM refusal guardrail bypassed through the multimodal/RAG context channel
  (author-reported **11/12** LVLMs fail; embedded notices ignored).

**Calibrated takeaway (§11):** the demonstrated bypasses are against *other* schemes; the corpus's own
defenses are, with the exceptions of A39992 (adaptive/detection) and A40909 (adaptive verification-time),
tested only non-adaptively — their adaptive and forgery robustness **requires production validation** and is
currently unestablished.

## Residual risks

- **Adaptive and forgery/spoofing robustness is unestablished** across the corpus (§12) — the largest
  residual risk for any attribution claim. Spoofing an owner's mark to frame them is near-universally
  untested (§4).
- **A separable mark remains removable** (A37429, A39041): any scheme whose mark is statistically separable
  from the primary content/functionality is at risk under a white-box or reverse-engineering adversary.
- **Conditional-on-usability / low-signal protection** (A39992 accuracy-sacrificing attacker; A39199 low
  watermark-ratio high variance; A40851 uneven cross-benchmark AUC 83–94%).
- **Secrecy / trusted-authority compromise is out of the evaluated model.** The whole guarantee rests on key
  custody and (for A40909) the trusted judge/authority; partial-key-leakage is un-analyzed across A40728,
  A40561, A40546, A40909, A41092, A39992, A39199.
- **Verification-access constraints.** Owner-white-box detection (A40546, A40561) is a deployment burden;
  grey-box log-prob dependence (A40575, A37038) cuts both ways — closed APIs that withhold probabilities
  resist auditing, yet exposing log-probs also aids extraction *(reviewer synthesis)*. FPR grows with anchor
  count (A40561).
- **Scope / generalization limits.** Pre-publication-only for data (A40575); Python-only for the code auditor
  (A37038); structured/conversational text weak (A40575); continued-pretraining not from-scratch (A40575);
  single-dataset / single-model-family concentration (A37429 Mip-NeRF360; A38094/A40892 SD family). Methods
  are **siloed across modalities** — do not reuse a mark cross-modally without revalidation (§17).
- **False-attribution / cross-owner collision rates at scale are rarely quantified** (§12; raised for A38094,
  A40892, A40901, A40921, A41092) — a one-class boundary (A40843) or a similarity threshold (A40851, A40909)
  can misfire on superficially similar non-members.
- **The ingestion gate is heuristic (A40910).** Compliance scoring (ROUGE/similarity/refusal) may mislabel
  borderline fair-use; the source verifier's coverage/latency/error modes are uncharacterized; legal ground
  truth is jurisdiction-dependent.
- **Evidence, not prevention (§14):** none of these stop the copy, extraction, or reproduction itself.

## Relevant research (stable paper ids from the syntheses/cards)

Output watermarking (generative media / text / embeddings):

- **A38094** — OptMark: dual-placement diffusion-image watermark; trajectory placement (early-latent survives
  regeneration, late survives transforms) as a robustness lever; 48-bit; TPR@FPR=1e-6; adjoint O(1)-memory.
  Non-adaptive, SD/DDIM single-family.
- **A40561** — Anchor Watermark: latent-diffusion audio; ChaCha20 key custody; initial-latent embed +
  inversion/Soft-DTW recovery; TPR@FPR + FAD/IS quality; owner-white-box, non-adaptive; FPR grows with N.
- **A40546** — WaterMod: decode-time LLM-text logit watermark; rank-mod-k residue partition + entropy gate;
  zero-bit + multi-bit; z-score/AUROC. Detection needs model+key; non-adaptive; forgery untested.
- **A41092** — ARGH-Mark: LLM-text logit watermark; RG-balanced partition + periodic anchors + extended
  (8,4,4) Hamming; match-rate/bit-acc; linear-time detection. ≤32-bit / L≥384 reliable regime; non-adaptive.
- **A40728** — RegionMarker: EaaS embedding-API watermark; secret PCA projection + LSH semantic regions +
  embedding-as-watermark; KS-test verification; comprehensive attack-family coverage. Semi-adaptive.
- **A37103 / A37412 / A40892 / A40901 / A40921** — image encoder-noise-decoder / in-generation watermarks
  (latent embedding preserves quality; PCA-energy / gradient-guided strength; LoRA-robust self-augmentation);
  headline numbers largely **not stated in paper** / reviewer-unverified; non-adaptive; forgery/collision
  analysis absent.
- **A39199** — robust GBDT/tabular watermark; in-place split/leaf updates (vs prunable additive trees) +
  gradient-dominance duplication; high variance at low watermark ratio; non-adaptive.

Model fingerprinting (ownership / attribution):

- **A40909** — iSeal: external-secret LLM ownership fingerprint (key-generated encoder + Reed-Solomon +
  similarity verification; trusted judge); litigation-grade **adaptive** threat model (white-box weights,
  collusion unlearning, output manipulation). *Strongest entry in the corpus.*
- **A40843** — StyleSentinel: intrinsic, no-embedding style fingerprint (SVDD one-class hypersphere) against
  LoRA/DreamBooth style theft; one-sample verification; retroactive protection. Partially adaptive.
- **A40851** — OFA: passive, synthesis-free image-to-model attribution fingerprint; AUC/OSCR at an operating
  threshold; non-adaptive, amplitude-spectrum fragile.
- **A39992** — DeepTracer: extraction-survivable black-box classifier watermark; in-distribution,
  task-coupled trigger; adaptive + detection evaluation. (Extraction detail in `model-extraction-defenses.md`.)

Training-data / dataset provenance:

- **A40575** — SPECTRA: pre-publication text watermark (paraphrase + score-matched sampling); grey-box
  Min-K%++ log-prob ratio test; ≥9-orders p-value gap at <0.001% corpus; documents MIA collapse at scale.
- **A37038** — SynPrune: syntax-aware code membership-inference auditor (AST-prune forced tokens); grey-box
  logits; Python-only; +15.4% AUROC.

Agent content-compliance policy gate:

- **A40910** — CopyGuard: ingestion-time copyright policy gate on retrieved/uploaded multimodal context
  (notice identifier → source verifier → query-risk analyzer/rewriter → status reminder); the transferable
  agent pattern; guardrail bypass demonstrated (11/12 LVLMs). Non-adaptive on CopyGuard itself.

Red team (load-bearing bypass demonstrations):

- **A37429** — GSPure: white-box prune/cluster removal of scene-hiding 3DGS watermarks; a separable mark is a
  removable mark.
- **A39041** — box-free image-to-image watermark removal via query reverse engineering; black-box
  encapsulation is not a security boundary; enables watermark-free surrogate.

Off-topic / miscategorized (carry no weight here): **A39623** (Shapley/FANOVA-GP explainable-AI), **A40030**
(VeriFlow normalizing-flow NN verification).

## Evidence strength

- **A40909 — Strong** (for its class): realistic adversarial litigation threat model with *adaptive*
  verification-time attacks (collusion unlearning, response manipulation), theoretical error-correction /
  cryptographic analysis, 12 LLMs; tempered by reliance on a trusted judge/authority and key secrecy, and
  "100% FSR" scoped to the evaluated attacks.
- **A39992 — Moderate**: broad multi-dataset/multi-attack evaluation including hard-label/data-free stealing,
  removal, and adaptive/detection attacks, with released code; tempered by conditional-on-usability
  protection, one non-best case (JBDA/FMNIST), and no formal false-positive bound.
- **A38094 / A40561 / A40546 / A41092 — Moderate**: comprehensive multi-attack robustness with proper
  TPR@FPR (A38094, A40561) or multi-domain AUROC/match-rate (A40546, A41092) and paired quality metrics;
  each tempered by **non-adaptive** attacks only, single-modality/family scope, owner-white-box or
  serving-path detection requirements, and **no forgery/spoofing analysis**.
- **A40728 — Moderate**: comprehensive attack-matrix evaluation (removal + two paraphrasing + two
  dimension-perturbation) with joint utility/detection reporting; tempered by no adaptive/stacked-attack
  evaluation and dependence on secret-projection secrecy without leakage analysis.
- **A40575 — Moderate**: meaningful scale (+5B tokens, <0.001% corpus), decision-relevant p-value metric;
  tempered by continued-pretraining (not from-scratch), no adaptive removal adversary, grey-box requirement,
  weak on structured text.
- **A40843 / A40851 — Moderate**: realistic, timely threats (LoRA/DreamBooth mimicry; in-the-wild
  attribution) with multi-dataset/real-platform (A40843) or multi-benchmark + released-code (A40851)
  evaluation; tempered by **no fingerprint-aware adaptive adversary**, truncated/absent FPR-base-rate
  analysis, and dependence on the "signal is distinctive and persistent" assumption.
- **A40910 — Moderate**: large structured benchmark (50k pairs, 12 LVLMs), clear compliance gap, working
  model-agnostic defense; tempered by heuristic compliance scoring, no adaptive-bypass evaluation of
  CopyGuard, unclear artifact release.
- **A37038 — Moderate**: principled cheaper detector, new authentic benchmark, ablations (+15.4% AUROC);
  tempered by Python-only scope, logit dependence, fuzzy MIA signal at scale, no adaptive-vendor test.
- **A39199 — Preliminary-to-Moderate**: first robust GBDT watermark with released code; narrow threat model
  (generic fine-tuning only), high variance at low ratios, no adaptive/false-positive-collision evaluation.
- **A39041 / A37429 — Moderate (red team)**: realistic removal attacks with strong author-reported results;
  the load-bearing evidence that hiding/encapsulation is not a boundary.

Cross-cutting: **all numbers are author-reported and non-adaptive unless noted; forgery/spoofing and strong
adaptive robustness are untested across the corpus (§12).** Reviewer-synthesis items in this pattern
(layering strategy, query-boundary/ingestion telemetry, fail-closed defaults, credential custody) are
**engineering practice, not measured defense efficacy**, and require production validation.

## When NOT to use this pattern

- **When you need to *prevent* copying, extraction, or reproduction.** The corpus delivers
  attribution/evidence, not prevention (§14). If prevention is the requirement, watermarking/fingerprinting
  is a supplement to access control and monitoring, not a solution.
- **When you cannot control the marking point or hold a secret.** Output watermarks need control of
  generation/serving (A38094, A40546, A40561, A41092, A40728); data watermarks need pre-publication marking
  (A40575); fingerprint injection needs training-time access (A40909, A39992, A39199). For already-published
  content with no owned model, only intrinsic fingerprinting applies (A40843, A40851) — and only where the
  intrinsic signal is distinctive and persistent.
- **When the adversary has white-box asset access and the mark is separable.** A separable/steganographic
  mark is removable (A37429, A39041); do not rely on hidden-signal watermarking for high-value assets
  distributed in the clear (3DGS, model files) — combine with access control, licensing/attestation, and
  signed provenance (see `signed-provenance.md`).
- **When you must audit a closed API with no logit access.** A40575 and A37038 depend on grey-box log-probs;
  without them (and without a court-appointed arbiter with access) they do not apply.
- **When forgery/spoofing or framing is the primary concern.** Spoofing an owner's mark is near-universally
  untested (§12); do not deploy this pattern as-is where an adversary framing another party is the threat,
  without adding and validating a forgery-resistance layer.
- **For cross-modal reuse without revalidation.** Methods are siloed across image/audio/text/tabular/
  embedding/3DGS (§17); do not reuse a text watermark for images, or a classifier watermark for an LLM,
  without re-establishing the threat model, metrics, and thresholds.
- **As a substitute for runtime agent-execution security.** Watermarking/fingerprinting is provenance and
  attribution; it does not gate tool use, isolate context, or authorize actions. The one exception that
  *does* sit on the agent surface — the ingestion policy gate (A40910) — is a content-compliance control,
  not model-IP marking; use that sub-pattern where the risk is a model reproducing *others'* copyrighted
  content, and pair it with the runtime patterns (prompt-injection containment, retrieval-authorization,
  policy-permission gates).
