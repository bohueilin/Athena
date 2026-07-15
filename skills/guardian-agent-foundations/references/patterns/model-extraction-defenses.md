# Pattern: Model Extraction Defenses

> **Scope of evidence.** This pattern is grounded in the AAAI-26 corpus synthesis
> `syntheses/Model-IP-Protection.md` and its underlying research cards under
> `research-cards/Model-IP-Protection/`. Load-bearing corpus papers, by role:
> **A39992** (DeepTracer — extraction-robust black-box classifier watermark; in-distribution,
> task-coupled trigger; evaluated against adaptive + detection attacks); **A40728** (RegionMarker —
> EaaS embedding-API extraction defense; secret projection + semantic regions; comprehensive
> attack-family coverage); **A40909** (iSeal — external-secret LLM ownership fingerprint under a
> white-box, collusion-unlearning, output-manipulation adversary); **A39041** (box-free removal —
> RED TEAM: query-based reverse engineering strips a black-box-encapsulated watermark and enables a
> watermark-free surrogate); **A37429** (GSPure — RED TEAM: white-box prune/cluster removal of
> scene-hiding 3DGS watermarks); **A40575** (SPECTRA — pre-publication training-data watermark,
> grey-box log-prob verification); **A37038** (SynPrune — code membership-inference provenance
> auditor, grey-box logits). Adjacent/keying primitives: **A40546 / A40561 / A41092** (secret-key
> custody + error-correcting output watermarks), **A38094** (trajectory placement), **A40851 /
> A40843** (intrinsic no-embedding fingerprints), **A39199** (GBDT watermark). Paper ids (e.g.
> `A39992`) are the stable corpus ids from the synthesis source map (§20).
>
> **Evidence integrity (non-negotiable).** Every numeric value below is **author-reported and not
> independently verified**; where a card was silent or truncated the text says "not stated in
> paper". Values are **non-adaptive** unless the paper is explicitly noted as adaptive (only A39992's
> adaptive/detection evaluation and A40909's verification-time adversary qualify). Calibrated
> language only: "reduced removal/stealing success against the tested, non-adaptive attacks",
> "requires production validation", never "secure / proven-safe / unbreakable". Items marked
> *(reviewer synthesis)* are cross-paper inference or engineering practice from the synthesis, **not
> a measured defense number from a single paper**. The single most important corpus caveat, repeated
> throughout: **watermarks and fingerprints are evidence, not prevention** (Model-IP-Protection §14),
> and **adaptive robustness and forgery/spoofing resistance are near-universally untested** across
> this corpus (§12).

---

## Problem addressed

A model deployed behind a query API is copyable. An adversary with only black-box access can
reconstruct a functional surrogate — demonstrated for **classifiers** (A39992: JBDA, Knockoff,
ActiveThief, MExMI, DFME, MAZE, DFMS-HL, including hard-label and data-free stealing), **embedding
APIs / EaaS** (A40728: query, collect embeddings, train a cheaper competing service), and
**image-to-image models** (A39041: query-based reverse engineering that both strips the ownership
watermark and yields a watermark-free surrogate). A white-box holder (insider, or a thief who has
already exfiltrated weights) is stronger still: A40909 assumes the adversary controls end-to-end
inference and can inspect/modify weights; A37429 prunes an embedded watermark out of a distributed
3D asset.

The corpus draws a sharp line between two sub-problems, and it is decisive for what this pattern can
promise:

- **Prevention** (stop the copy from happening) — only lightly covered: query monitoring / screening
  / rate limiting is *named* (A39041's proposed API query-screener; A40728's API boundary; A39992's
  deployment guidance) but not rigorously benchmarked as a defense.
- **Attribution / provenance** (prove a suspect model or dataset was extracted from yours) — the
  corpus's actual contribution: extraction-survivable watermarks (A39992), tamper-evident
  fingerprints (A40909), EaaS provenance (A40728), and training-data provenance (A40575, A37038).

The organizing thesis (Model-IP-Protection §14, *reviewer synthesis* over nearly every card):
**a recovered mark supports post-hoc attribution, governance, and legal action; it does not by
itself prevent misuse.** Treat any single mark or fingerprint as one probabilistic evidence signal,
paired with access control, query monitoring, and a provenance registry — never as a barrier.

## Applicable assets and attack surfaces

- **Query-served model APIs — the primary extraction surface.** Classifier logits/labels (A39992),
  embedding vectors (A40728), generated images (A39041). The richer the output (full softmax /
  log-probs / high-precision embeddings), the higher the achievable surrogate fidelity *(reviewer
  synthesis; the corpus does not measure output-granularity reduction as a defense, but grey-box
  log-prob access is the enabling surface in A39992, A40575, A37038)*.
- **Model weights** — white-box theft and insider replication (A40909 assumes full weight
  read/modify; A37429 operates on the distributed asset).
- **Training / evaluation corpora** — unauthorized use of copyrighted or licensed data (A40575 text;
  A37038 code). This is the data-supply-chain surface an agent's models are built on.
- **The verification secret itself** — the watermark key set (A39992), the secret PCA
  projection/trigger regions (A40728), the key-generated encoder (A40909), and any decode-time
  key (A40546, A40561, A41092). These are **credentials** and are part of the trust boundary
  (§15).
- **Embeddings that feed RAG / agent memory** — marking the embedding API is a supply-chain control
  because embeddings power the retrieval an agent consumes (A40728, §14).

## Threat model

From Model-IP-Protection §3–§4. Cluster by adversary posture:

- **Black-box query extraction (dominant for this pattern).** Adversary knows the task domain, not
  the architecture/training data; queries to build a near-original surrogate; may then apply removal
  transforms. Instantiated by A39992 (seed/substitute/data-free stealing, incl. hard-label &
  many-class), A40728 (CSE cluster-and-remove, paraphrasing via NLLB and gpt-4o-mini,
  dimension-perturbation), A39041 (identity-inducing queries that expose the hiding network).
- **White-box / end-to-end-inference adversary (strongest, safest to assume).** A40909: full weight
  access, collusion-based fingerprint unlearning, output/response manipulation to evade exact match —
  a litigation setting. A37429: white-box prune/cluster removal of low-contribution,
  viewpoint-inconsistent watermark Gaussians.
- **Grey-box log-prob adversary/auditor (for data provenance).** A40575 and A37038 require token
  log-probabilities from the suspect model; weights/architecture not needed.
- **Adaptivity.** The dominant corpus posture is **non-adaptive** — fixed, off-the-shelf attacks,
  not scheme-aware optimization (§3, §12). Only **A39992** (adaptive + detection attacks) and
  **A40909** (adaptive verification-time attacks) rise above this bar. **Forgery / spoofing** of an
  owner's mark (framing another party) is repeatedly named and almost never evaluated (§4, §12).

Design consequence: assume the adversary eventually controls inference end-to-end and knows the
scheme (A40909's posture). Everything else is a weaker case.

## Control mechanism

A layered control; no single layer is sufficient.

1. **Extraction-survivable watermark (attribution).** Make the watermark task **in-distribution and
   coupled to the primary task** so a stolen model that copies functionality inevitably copies the
   mark (A39992). Verification: accuracy on a secret key set exceeds a deterministic threshold.
2. **External-secret fingerprint + tolerant verification (white-box adversary).** Bind ownership
   evidence to a secret held *outside the weights* (key-generated encoder), verify by
   **similarity + error-correction**, not exact match, and keep verification prompts under a trusted
   judge (A40909). Removal by weight access alone cannot erase an external secret; similarity + ECC
   survives output manipulation.
3. **Comprehensive, secret-projection provenance for EaaS (extraction of embedding APIs).** Secret
   dimensionality reduction + semantic regions + embedding-as-watermark, verified by a conservative
   statistical test, robust *jointly* to removal, paraphrasing, and dimension-perturbation (A40728).
4. **Query-boundary prevention layer.** Rate limits, per-account query auditing, and
   anomalous/near-identity query screening at the API (A39041's proposed screener; A40728's API
   boundary; A39992 deployment guidance). *(reviewer synthesis: this is the actual prevention lever;
   it is named but not benchmarked in-corpus — requires production validation.)*
5. **Training-data provenance (grey-box).** Pre-publication watermark + log-prob ratio test (A40575);
   syntax-aware membership inference for code (A37038).

Verification is **deterministic** in every case: WSR > τ (A39992), KS p-value < 0.05 (A40728),
similarity J(·) > ω with Reed-Solomon correction (A40909), a ratio-test p-value gap (A40575),
AUROC threshold ε (A37038).

## Preconditions and trust assumptions

- **Owner controls training and holds the secret.** The watermark is embedded during victim training
  (A39992) or the data is watermarked *before publication* (A40575); the secret key set / projection
  / encoder is owner-held and kept secret (A39992, A40728, A40909).
- **A trusted verifier / registration authority exists** for the strongest scheme. iSeal (A40909)
  requires a trusted judge + registration authority with black-box API access to suspect and
  registered models; verification prompts are queried **only** by the judge to prevent overclaim.
  This is a real trust dependency — its compromise is out of the evaluated model.
- **Grey-box log-prob access** to the suspect model for data provenance (A40575, A37038). Closed APIs
  that withhold token probabilities defeat these methods.
- **Secrecy assumptions are load-bearing.** A40728's security rests entirely on the attacker being
  unable to recover the PCA matrix / trigger regions; A40909's on the key/encoder staying outside the
  thief's reach; A39992's on key-set secrecy. Leakage analysis for partial inference of the secret is
  **not provided** by these papers.
- **A surrogate approximates the real stolen model.** A39992 filters key samples using a surrogate
  trained by simulated stealing; mismatch with an unseen stealing strategy can reduce effectiveness.
- **Fail-closed, least-privilege framing** *(reviewer synthesis, consistent with the corpus's
  "assume end-to-end-inference adversary" posture, A40909):* expose the minimum output granularity a
  client genuinely needs; treat verification secrets as governed credentials with custody and
  rotation (§15).

## System architecture

```
                 ┌────────────────────── OWNER / PROVIDER TRUST ZONE ───────────────────────┐
 training ──►  [ watermark / fingerprint embedding ]        [ secret-key custody store ]
   data         (in-distribution coupled trigger A39992,     (key set A39992; PCA matrix +
                 external-secret encoder A40909, secret       regions A40728; key-gen encoder
                 PCA+regions A40728)                          + RSC params A40909)  ← credential,
                        │                                        rotate + version (§15,§16)
                        ▼
 client ─►  [ QUERY BOUNDARY ]  ─►  served model  ─►  [ output-granularity limiter ]  ─► client
            • rate limit (fail-closed on quota)                 (hard label / reduced
            • per-account query audit                            precision where feasible;
            • near-identity / anomalous-query screen             reviewer synthesis)
              (A39041 screener; A40728; A39992)
                        │  telemetry
                        ▼
            [ extraction telemetry + provenance registry ]  (issued marks, key custody events)
                        │
     ── suspect model / dataset appears in the wild ──
                        ▼
      [ TRUSTED VERIFIER / JUDGE ]  (offline, black-box query to suspect; A40909)
            • deterministic threshold test (WSR>τ / KS p<0.05 / J>ω+RSC / ratio p-value)
            • benign-model false-positive check
                        ▼
            [ governance / legal review ]   ← evidence, not automated enforcement
```

Key architectural decisions (§15): **put verification logic — thresholds, error-correction, key
custody — in the trusted third party, not the deployed model** (A40909); **verification-access is a
design choice** — model+key owner-white-box detection (A40546, A40561) is a heavier deployment
burden than external-secret + trusted-judge (A40909) or grey-box log-prob detection (A40575);
**treat secret keys as governed credentials** with custody and rotation for any key-custody scheme
(A40546, A40561, A40909, A41092).

## Recommended implementation pattern

- **Make the extraction watermark in-distribution and task-coupled (A39992).** Select source classes
  that span the primary feature space (K-Means over class-centroid features from a benign model);
  assign the **least-likely target label under a benign model** to control false positives on
  independently trained models; couple watermark and target-class outputs with an intra/inter-class
  centroid loss so the mark activates the *same neurons the thief must copy*. Filter key samples with
  the deterministic **victim-pass / surrogate-pass / benign-fail** rule, then keep the top-M by
  surrogate target probability. Verify: WSR on the key set > τ (A39992 cites a 20% threshold for
  hard-label ownership confirmation).
- **Bind ownership to an external secret and verify tolerantly (A40909).** Use a key-generated
  encoder (the secret lives outside the weights), fine-tune the model to reconstruct
  **Reed-Solomon-encoded** targets, and verify by **similarity (J(·) > ω) with error correction**,
  never exact match. Do **not** publicly disclose a verification prompt-response pair (that enables
  collusion unlearning). Route all verification queries through the trusted judge.
- **Cover the full attack family matrix for EaaS (A40728).** Project embeddings through a secret
  dimensionality reduction (uniform region occupancy defeats cluster-and-remove), partition into
  semantic regions via LSH (semantic regions survive paraphrasing), and use the in-region text
  embedding itself as the per-region watermark (defeats dimension-perturbation). Verify with a
  conservative KS-test (p < 0.05 → infringement). Evaluate against removal **and** paraphrasing
  **and** dimension-perturbation *jointly* — defeating any single family defeats the defense.
- **Instrument and throttle the query boundary** *(reviewer synthesis, grounded in A39041, A40728,
  A39992 deployment):* per-account query auditing, input-distribution monitoring, near-identity /
  anomalous-query screening, and **fail-closed rate limiting** (deny on quota exhaustion rather than
  serve). Extraction is query-driven, so the boundary is a genuine detection surface.
- **For training-data provenance**, watermark **before publication** (A40575): generate paraphrases,
  score with a separate pre-cutoff scoring model (Min-K%++), and use **score-matched, side-balanced
  sampling** so the watermark introduces no distribution shift (avoiding a training-independent
  false-positive signature); verify with the grey-box ratio test (no non-member set needed). For
  code, prune syntactically-forced tokens before the membership score (A37038).
- **Report utility alongside detection** (A40728) and **use decision-relevant metrics** — p-value
  separation over AUROC for enforcement claims (A40575).

## Incorrect or fragile implementation patterns

- **Out-of-distribution trigger watermarks.** A39992's root-cause finding (supported by
  neuron-activation analysis): OOD watermark tasks activate disjoint neuron regions; a stolen model
  trained on in-distribution-like queries never exercises them and **forgets the mark**. OOD triggers
  are separable and forgettable.
- **Treating black-box encapsulation as a security boundary.** A39041: hiding a generator behind a
  single black-box operation network does **not** protect the watermark — identity-inducing queries
  expose the hiding network and strip the mark (author-reported ~100% removal, PSNR up to 34.69 dB),
  additionally leaking the private clean output and enabling a watermark-free surrogate.
- **Separable / "inactive" / steganographic marks.** A37429: watermark Gaussians with low,
  viewpoint-inconsistent contribution are clusterable and prunable (author-reported up to 16.34 dB
  watermark-PSNR reduction, < 1 dB scene loss). §6 (*reviewer synthesis* over A37429 + A39041):
  **a separable mark is a removable mark.**
- **Weight-embedded fingerprint + exact-match verification.** A40909's explicit critique: a
  fingerprint that lives only in weights is removable under white-box access, and exact-match
  verification is evadable by output manipulation.
- **Publicly disclosing verification prompt-response pairs.** A40909: disclosure enables
  collusion-based unlearning (fine-tune away the disclosed records) and reverse engineering.
- **Single-attack-family robustness for EaaS.** A40728: prior schemes each fell to one family
  (EmbMarker/WARDEN/EspeW to paraphrasing; WET to dimension-perturbation). An attacker who defeats
  any single attack defeats the defense.
- **Surface-token / trigger-word semantics.** A40728: semantically empty trigger words are removed by
  paraphrasing.
- **Relying on passive membership inference at scale.** A40575: standard MIA collapses to near-random
  (author-reported ROC-AUC ~0.50–0.56 at +5B tokens) — not a dependable provenance signal on its own.
- **Presenting a mark as prevention.** §14: the mark does not stop the theft.

## Verification strategy

Every scheme verifies with a **deterministic threshold on a secret-conditioned statistic**, run by
the owner or (preferably) a trusted third party against the suspect model/dataset:

- **A39992:** query the suspect with the secret key set; flag if accuracy (WSR) > τ (20% cited for
  hard-label). Benign-fail filtering during construction is the false-positive control.
- **A40728:** build backdoor (in-watermark-region) and benign corpora, compare cosine/L2 distance
  distributions to the region watermark, declare infringement if the KS p-value < 0.05 (combined
  conservatively across watermark levels).
- **A40909:** trusted judge queries the suspect API, decodes with Reed-Solomon, and matches by
  similarity J(·) > ω; prompts are judge-only to prevent overclaim.
- **A40575:** compute Min-K%++ score ratios under target vs scoring model; test whether the mean
  ratio drops after training; report the member/non-member p-value gap (no non-member dataset
  needed).
- **A37038:** AST-prune syntactically-forced tokens, compute the syntax-pruned membership probability,
  threshold at ε; report AUROC.

Cross-cutting requirements: **externalize verification to a trusted verifier** (A40909, §15);
**always run a benign / independently-trained model through verification** and require it to *fail*
(A39992 benign-fail, A40728 benign corpus, A40575 score-matched sampling) to bound false attribution.

## Metrics and thresholds

All values **author-reported**, on the paper's own datasets, **non-adaptive unless noted**, not
independently verified.

- **Watermark Success Rate (WSR)** — want ≈0 on benign models, high on victim and stolen models.
  A39992 (author-reported): near-100% WSR on stolen models (Knockoff, DFME) including CIFAR-100; WSR
  stays above the **20%** hard-label ownership threshold; two-stage key filtering drove stolen WSR
  94.61% → 95.86% → 98.75% and benign WSR to 0%.
- **Task-fidelity cost (ΔAcc)** — A39992: −0.06 (FMNIST), +0.28 (CIFAR-10), −0.95 (CIFAR-100) for the
  watermarked model.
- **KS p-value < 0.05** for infringement; utility ~92–94% accuracy preserved (dropping to ~87.9%
  under CSE) — A40728.
- **Fingerprint Success Rate (FSR)** — A40909: 100% FSR on 12 LLMs against > 10 attacks (incl.
  collusion unlearning, response manipulation), while baselines drop to 0% under those attacks.
  **Adaptive** verification-time evaluation.
- **p-value separation** — A40575: ≥ 9 orders of magnitude member/non-member gap at < 0.001% corpus
  fraction and +5B-token continued pretraining; motivating collapse of baseline MIA to ROC-AUC
  ~0.50–0.56.
- **AUROC** — A37038: +15.4% average AUROC over baselines across 4 models × 3 ratios (Python code).
- **Attacker-side benchmarks you must defend against** — A39041: ~100% removal / PSNR up to 34.69 dB;
  A37429: up to 16.34 dB watermark-PSNR reduction with < 1 dB scene loss.

No absolute threshold is "safe"; each is scoped to the tested, non-adaptive attack set (except A39992
adaptive/detection and A40909 verification-time).

## Test cases

At minimum, exercise the extraction/removal suite the corpus demonstrates, plus false-positive and
utility regression tests:

1. **Extraction attacks (classifier):** seed-based (JBDA), substitute-data (Knockoff, ActiveThief,
   MExMI), data-free (DFME, MAZE, DFMS-HL), hard-label and many-class — verify WSR survives on the
   stolen model (A39992).
2. **EaaS attacks (jointly):** CSE cluster-and-remove; paraphrasing (translation-based + LLM
   rewriting); dimension-shift/reduction/permutation — verify KS p < 0.05 under *each and their
   stacking* (A40728; stacked attacks are the corpus gap).
3. **Query-based reverse engineering (image-to-image):** craft near-identity queries and attempt to
   strip the mark / train a surrogate — verify the watermark and clean output are not both recoverable
   (A39041).
4. **White-box removal:** fine-tune, prune, quantize, transfer-learn the stolen model; for embedded
   marks, attempt cluster/prune removal — verify WSR stays above τ within usable-accuracy ranges
   (A39992, A37429).
5. **Verification-time attacks (fingerprint):** collusion unlearning of disclosed records; output/
   response manipulation; overclaim attempts — verify FSR holds and non-owners cannot overclaim
   (A40909).
6. **False-positive / false-attribution:** run an independently-trained benign model (and a
   different owner's model) through verification and require it to **fail** (A39992 benign-fail,
   A40728 benign corpus, A40575 score-matched sampling).
7. **Utility regression:** measure ΔAcc / downstream embedding accuracy / generated-output quality to
   confirm the mark does not degrade the service (A39992, A40728).
8. **Key-secrecy handling:** confirm keys/projections are never returned to clients and live only in
   the custody store.

## Adaptive adversarial tests

This is the corpus's single biggest gap (§12) and where you must go **beyond** what the papers
validated — mark all of these **"requires production validation"**:

- **Scheme-aware coupling attacker** who knows the in-distribution coupling mechanism and optimizes
  against it (A39992's own stated caveat — its adaptive/detection attacks may not be the strongest).
- **RegionMarker-aware attacker** who jointly attacks regions *and* dimensions, estimates the
  provider's PCA basis from many queries, or stacks paraphrase → dimension-shift → CSE (A40728's
  stated gap: attacks are not optimized against the secret-region design).
- **Query-screener-evading statistics** — vary query distributions to defeat the near-identity
  screener (A39041's proposed screener is not rigorously benchmarked).
- **iSeal-aware distillation / heavy fine-tuning / output-distribution shaping** vs the RSC/similarity
  design (A40909: "100%" is scoped to the evaluated attacks; a stronger adaptive adversary is not
  exhaustively bounded).
- **Training-data watermark removal** — deduplicate, re-paraphrase, or filter scraped text before
  training (A40575 explicitly does not model a watermark-removal adversary); MIA-aware training /
  canary suppression for code (A37038).
- **Forgery / spoofing** — attempt to fabricate an owner's mark to frame them. Repeatedly named,
  almost never evaluated across the corpus (§4, §12); do **not** launch attribution claims in
  adversarial/litigation settings without it (A38094, A40546, A41092, A40909).

## Telemetry requirements

- **Query-boundary telemetry (the live detection surface).** Per-account query volume and rate,
  input-distribution monitoring, near-identity query detection (A39041's screener signature),
  anomalous embedding-query patterns (A40728). Extraction is query-driven, so this is where it is
  actually observable *(reviewer synthesis over A39041, A39992 deployment, A40728)*.
- **Verification audit trail.** Record key-custody events, judge queries, RSC-decoded matches, and
  the threshold decision for each verification (A40909 monitoring implications; A37038 treats results
  as audit records feeding governance).
- **Provenance registry.** Issued marks/keys, embedding-time parameters, and scheme versions, so a
  later suspect can be checked against the right secret and a broken scheme can be identified and
  rotated.
- **Utility/quality baselines** logged alongside, so a defensive re-mark can be shown not to have
  degraded service.

## Failure handling

- **Fail-closed at the query boundary** *(reviewer synthesis, design principle):* on query-quota
  exhaustion or an anomalous-query trip, **deny/throttle rather than continue serving** — the
  deterministic, least-privilege default.
- **Treat verification output as probabilistic evidence, not an enforcement trigger.** Route a
  positive verification to governance/legal review; do not auto-act (A37038, A40575, A40909
  deployment implications).
- **Conditional protection is a first-class failure mode.** A39992's robustness holds only while the
  stolen model stays usably accurate — an attacker willing to sacrifice accuracy weakens
  verification; never rely on a single signal, and combine watermark evidence with query telemetry
  and access-control logs.
- **Never single-signal.** Because every mark is scoped to a non-adaptive threat model, a failed or
  ambiguous verification should degrade to corroborating evidence (registry, telemetry, key-custody
  records), not a definitive verdict.

## Rollback and containment

- **Rotate the secret, re-mark going forward.** Keys/projections/encoders are governed credentials
  (§15); on suspected compromise or a demonstrated break of the scheme (as A39041, A37429, and
  A40728-documented prior schemes were broken), **revoke the key, rotate to a fresh secret, and
  re-embed for future assets.** Version the registry so old and new marks are both verifiable
  (§16: pin and version keys + verifier).
- **Contain at the boundary.** Throttle or block offending accounts/query patterns via the
  query-boundary layer.
- **Accept the irreversibility of extraction.** Provenance is **post-hoc** (A40728, A40575) — an
  already-extracted surrogate or an already-published-then-scraped dataset cannot be "rolled back";
  A40575's pre-publication-only property means data not watermarked before release is unrecoverable.
  Containment limits *future* loss and preserves *attribution* evidence; it does not undo the copy.

## Known bypasses

From Model-IP-Protection §11 (all author-reported, against *other* schemes, under the bypasser's own
evaluation):

- **A37429 (GSPure)** breaks three scene-hiding 3DGS watermarks — GS-Hider, Splats-in-Splats,
  SecureGS — via white-box clustering/pruning of low-contribution, viewpoint-inconsistent watermark
  Gaussians (up to 16.34 dB watermark-PSNR reduction, < 1 dB scene loss).
- **A39041** breaks two box-free image-to-image watermarks (VWu, VZhang) with ~100% removal
  (PSNR up to 34.69 dB) and enables watermark-free surrogate training; its proposed query-screener
  defense is not rigorously benchmarked.
- **A40728** documents prior EaaS watermarks each broken by a single family: EmbMarker, WARDEN, EspeW
  by paraphrasing; WET by dimension-perturbation.
- **A40575** documents that prior membership inference collapses to near-random at scale — a bypass of
  passive MIA as a provenance signal.
- **A40909** documents the failure classes it defends against: passive-fingerprint forgery/overclaim,
  weight-embedded fingerprint removal under white-box access, and exact-match evasion by output
  manipulation.

**Calibrated takeaway (§11):** the demonstrated bypasses are against *other* schemes; the corpus's
own defenses are, with the exceptions of A39992 (adaptive/detection) and A40909 (adaptive
verification-time), tested only non-adaptively — their adaptive and forgery robustness **requires
production validation** and is currently unestablished.

## Residual risks

- **Adaptive and forgery/spoofing robustness is unestablished** across the corpus (§12) — the largest
  residual risk for any attribution claim.
- **Conditional-on-usability protection** (A39992): an accuracy-sacrificing attacker can weaken
  extraction watermarks.
- **Trusted-authority / key-secrecy compromise** is out of the evaluated model (A40909); the whole
  guarantee rests on the judge/authority and key custody.
- **Grey-box logit dependence cuts both ways** (A40575, A37038): closed APIs that withhold token
  probabilities resist auditing, yet exposing log-probs also *aids extraction* — a genuine
  design tension *(reviewer synthesis)*.
- **Pre-publication-only** for data (A40575); **Python-only** for the code auditor (A37038);
  **continued-pretraining, not from-scratch**, evaluation (A40575) leaves full-scale validation open.
- **Single-dataset / single-model-family concentration** (A37429 Mip-NeRF360 only; A40728 headline on
  SST-2; the image watermarking papers on SD-family) limits generality.
- **False-attribution / cross-owner collision rates at scale are rarely quantified** (§12).
- **Evidence, not prevention** (§14): none of these stop the extraction itself.

## Relevant research (stable paper ids from the syntheses/cards)

Core (extraction / provenance):

- **A39992** — DeepTracer: extraction-robust black-box classifier watermark; in-distribution,
  task-coupled trigger; adaptive + detection evaluation. *The reusable "design the mark to survive
  stealing" primitive.*
- **A40728** — RegionMarker: EaaS embedding-API extraction defense; secret projection + semantic
  regions; comprehensive attack-family coverage.
- **A40909** — iSeal: external-secret LLM ownership fingerprint under a white-box, collusion-unlearning,
  output-manipulation adversary; similarity + Reed-Solomon verification; trusted judge. *Strongest
  threat model in the corpus.*
- **A39041** — RED TEAM: query-based reverse engineering of box-free image-to-image watermarks;
  demonstrates black-box encapsulation is not a security boundary and enables surrogate training.
- **A37429** — RED TEAM: GSPure white-box removal of scene-hiding 3DGS watermarks; a separable mark is
  a removable mark.
- **A40575** — SPECTRA: pre-publication training-data watermark; grey-box log-prob ratio test; documents
  MIA collapse at scale.
- **A37038** — SynPrune: syntax-aware code membership inference as a copyright/provenance auditor
  (grey-box logits).

Adjacent primitives (keying, placement, intrinsic fingerprints):

- **A40546 / A40561 / A41092** — decode-time output watermarks with secret-key custody + error-correcting
  codes (WaterMod rank-mod-k; ChaCha20 audio; extended Hamming). *Key custody is part of the trust
  boundary.*
- **A38094** — trajectory placement as a robustness lever for generative-output marks.
- **A40851 / A40843** — intrinsic, no-embedding fingerprints (passive image-to-model attribution; style
  hypersphere) — a paradigm alternative for retroactive protection.
- **A39199** — robust GBDT watermarking (tabular model IP).

Adjacent-but-out-of-scope: **A40910** (CopyGuard — copyright-policy guardrail bypass via the
RAG/multimodal context channel; a *content-compliance* control, not model extraction).
Off-topic/miscategorized (carry no weight here): **A39623**, **A40030**.

## Evidence strength

- **A40909 — Strong** (for its class): realistic adversarial litigation threat model with *adaptive*
  verification-time attacks, theoretical error-correction/cryptographic analysis, 12 LLMs; tempered by
  reliance on a trusted judge/authority and key secrecy, and "100%" scoped to the evaluated attacks.
- **A39992 — Moderate**: broad multi-dataset/multi-attack evaluation including hard-label/data-free
  stealing, removal, and adaptive/detection attacks, with released code; tempered by
  conditional-on-usability protection, one non-best case (JBDA/FMNIST), and no formal false-positive
  bound.
- **A40728 — Moderate**: comprehensive attack-matrix evaluation (removal + two paraphrasing + two
  dimension-perturbation) with joint utility/detection reporting; tempered by no adaptive/stacked-attack
  evaluation and dependence on secret-projection secrecy without leakage analysis.
- **A40575 — Moderate**: meaningful scale (+5B tokens, < 0.001% corpus), decision-relevant p-value
  metric; tempered by continued-pretraining (not from-scratch), no adaptive removal adversary, grey-box
  requirement, weak on structured text.
- **A37038 — Moderate**: principled, cheaper detector with a new authentic benchmark and ablations;
  tempered by Python-only scope, logit dependence, fuzzy MIA signal at scale, no adaptive-vendor test.
- **A39041 / A37429 — Moderate (red team)**: realistic removal attacks with strong author-reported
  results; the load-bearing evidence that hiding/encapsulation is not a boundary.

Cross-cutting: **all numbers are author-reported and non-adaptive unless noted; forgery/spoofing and
strong adaptive robustness are untested across the corpus (§12).** Reviewer-synthesis items in this
pattern (query-boundary monitoring, output-granularity minimization, the layering strategy) are
**engineering practice, not measured defense efficacy**, and require production validation.

## When NOT to use this pattern

- **When you need to *prevent* extraction outright.** The corpus delivers attribution/evidence, not
  prevention (§14); prevention rests on access control + query throttling, which are named but not
  benchmarked here. If prevention is the requirement, this pattern is a supplement, not a solution.
- **When the adversary will not keep the surrogate usably accurate.** A39992's protection is
  conditional on the stolen model staying accurate; against an accuracy-indifferent adversary the
  extraction watermark weakens.
- **When you cannot hold a secret or run a trusted verifier.** A40909's guarantees collapse without a
  trusted judge/authority and a secret key/encoder held outside the model.
- **When you must audit a closed API with no logit access.** A40575 and A37038 depend on grey-box
  log-probs; without them (and without a court-appointed arbiter that has access) they do not apply.
- **For already-published training data.** A40575 protects only content watermarked *before* release;
  it cannot retroactively protect published data.
- **For cross-modal reuse without revalidation.** Methods are siloed across image/audio/text/tabular/
  embedding/3DGS (§17); do **not** reuse a classifier watermark for an LLM or a generative model
  without re-establishing the threat model and metrics.
- **When the real threat is copyright-policy compliance via the RAG/context channel** — that is
  A40910 (CopyGuard) territory, a content-compliance guardrail, not model extraction; use that
  pattern instead.
- **As a substitute for forgery/spoofing defense.** Spoofing an owner's mark to frame them is
  near-universally untested (§12); do not rely on this pattern where framing/overclaim is the primary
  concern without adding and validating a forgery-resistance layer.
