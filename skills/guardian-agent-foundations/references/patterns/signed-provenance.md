# Pattern: Signed Provenance

> **Scope of evidence.** Grounded in two AAAI-26 corpus syntheses: `Model-IP-Protection` and
> `Deepfake-Forgery-Detection`. Paper ids (e.g. `A40909`) are the stable corpus ids from those syntheses'
> source maps. Every recommendation traces to at least one card.
>
> **Evidence-integrity conventions (non-negotiable).** Numeric values are **author-reported** unless labeled
> *reviewer synthesis*, and are **not independently verified**. Where a card was silent or truncated, values are
> written "not stated in paper". No absolutes ("secure", "tamper-proof", "unforgeable") are used; findings hold
> "under the evaluated (largely non-adaptive) threat model" and "against the tested attacks".
>
> **The load-bearing calibration for this pattern.** *No paper in either synthesis implements a full detached
> cryptographic-signature / PKI content-credential ("C2PA-style") scheme.* The closest studied primitive is
> `A40909` (iSeal): an **external-secret + trusted-verifier + similarity/error-correcting-code** ownership
> fingerprint, and it is also the only entry evaluated against an adaptive, litigation-grade adversary. "Signed
> provenance" as specified below is therefore a **reviewer-synthesis extrapolation** built from `A40909`'s
> crypto-provenance template plus the corpus's convergent cautions — not a benchmarked artifact. Two further
> replicated absences bound every claim here: **forgery / owner-mark spoofing is named repeatedly and almost
> never evaluated** (`A38094`, `A40546`, `A41092`, partially `A40909`), and **adaptive, scheme-aware robustness
> is untested** everywhere except `A40909` and `A39992`. Treat every protection number as a non-adaptive upper
> bound; treat every threshold as an engineering target that **requires production validation**.

---

## Problem addressed

A consumer — a Guardian agent, a governance layer, a downstream model, a court — needs to answer two questions
about an artifact (generated content, a model, an embedding, a dataset, or an agent's own output): **where did
this come from, and has it been altered since?** The Model-IP corpus is, in its own framing, an
*evidence-and-attribution* discipline: the recovered mark or fingerprint "supports post-hoc attribution,
governance, and legal action; it does not by itself prevent misuse" — a conclusion stated on nearly every card
(reviewer synthesis over the whole Model-IP corpus). Deepfake-Forgery is the same shape: its detectors "produce
an *evidence signal an agent consumes*, not a control on the agent's own tool/skill/MCP surface".

The corpus's two dominant provenance mechanisms are each individually weak as an authoritative origin claim:

- **Embedded watermarks** are removable when the mark is *separable*. `A37429` (GSPure) strips three
  scene-hiding 3D-Gaussian-Splatting watermarks white-box (author-reported up to **16.34 dB** watermark-PSNR
  reduction with **<1 dB** scene loss); `A39041` removes two box-free image-to-image watermarks with
  author-reported **~100%** removal success (PSNR up to 34.69 dB) and then trains a watermark-free surrogate.
  The reviewer-synthesis lesson repeated across both: **"a separable / 'inactive' mark is a removable mark;"
  hiding / encapsulation is not a security boundary.**
- **Passive detectors** are probabilistic evidence, never an authoritative gate — the Deepfake synthesis's
  headline product implication, reinforced by `A38060`'s finding that **up to 67.4%** of MLLM-identified
  forensic flaws were incorrect (direct paper finding), and by averaged SOTA masking near-chance behavior on the
  hardest sets.

**Signed provenance** is the control that answers those two questions *deterministically* by binding an
artifact's origin claim to an **external secret held by a trusted signer**, and verifying it under a **trusted
verifier** using **similarity + error-correcting codes rather than exact match**, **failing closed** when the
signature is absent, invalid, or unverifiable. It is grounded most directly in `A40909` (iSeal — key-generated
encoder + Reed–Solomon, similarity+ECC verification, adversary-controls-inference threat model) and in the
Deepfake synthesis's explicit recommendation to "combine detection with **cryptographic provenance
(C2PA-style)**, watermarking, and human review for high-stakes decisions." Its honest scope, inherited from the
corpus: it establishes **attributable, tamper-evident evidence** — it does **not** prevent misuse.

## Applicable assets and attack surfaces

- **Generative outputs** (image, audio, text, tabular, 3DGS) — the artifacts over which a provenance claim is
  asserted and the surface where removal/purification attacks land (`A37103`, `A37412`, `A38094`, `A40561`,
  `A40892`, `A40901`, `A40921`, `A39199`; attacked by `A37429`, `A39041`).
- **Models / weights** — ownership identity. `A40909` is load-bearing here: it argues **weight-embedded**
  fingerprints are removable under white-box access and that exact-match verification is evadable, motivating an
  **external** secret. The place the secret lives is itself a security decision.
- **Embedding / EaaS APIs** — a supply-chain surface, because embeddings feed RAG and agent memory. `A40728`
  (RegionMarker) marks the embedding API so the data agents consume carries provenance; prior EaaS schemes
  (EmbMarker, WARDEN, EspeW, WET) were each broken by a single attack family (paraphrase, dimension-perturbation).
- **Agent-generated content** — decode-time tagging for downstream attribution (`A40546` rank-mod-k; `A41092`
  extended (8,4,4) Hamming + anchor synchronization), which requires **control of the serving path** and
  **secret-key custody** (the key is a credential, not a config value).
- **Training data / datasets** — provenance auditing of the AI data supply chain via grey-box log-probs
  (`A37038` code membership inference as a copyright auditor; `A40575` SPECTRA pre-publication text watermark).
- **The verification path itself** — the trusted verifier's **model and key are assets**. `A40909` keeps
  verification under a trusted verifier to prevent overclaim; `A37865` (Deepfake) ties its tamper-localization
  to a **specific SAM version**, so a verifier-model change can silently break verification.
- **The secret key** — the single most sensitive asset. Key-custody schemes: `A40561` (ChaCha20), `A40909`
  (key-generated encoder), `A41092`, `A40546`.
- **The context-ingestion boundary** — where untrusted retrieved/uploaded content enters an agent. `A40910`
  (CopyGuard) shows the guardrail must sit at ingestion, not the surface prompt (author-reported **11/12** LVLMs
  fail to respect copyright when infringing content arrives as multimodal/RAG context).

## Threat model

- **In scope (primary — mark/signature stripping).** (1) *Removal / purification* of an embedded provenance
  mark — demonstrated white-box (`A37429`, up to 16.34 dB reduction) and black-box (`A39041`, ~100% removal).
  (2) *Regeneration / re-diffusion stripping* — `A38094` shows placement in the generative trajectory is a
  robustness lever (early-latent marks survive regeneration; late marks survive geometric/valuemetric
  transforms), which conversely means a mark placed wrong is stripped by the corresponding transform.
  (3) *Model extraction / distillation* dropping the mark — `A39992` (DeepTracer): OOD watermark triggers
  activate disjoint neurons and are **forgotten by stolen models**; only in-distribution, task-coupled marks
  survive.
- **In scope (context channel — most agent-relevant).** *Provenance/guardrail bypass through retrieved or
  uploaded content* — `A40910`: refusal behavior that blocks direct requests does not generalize when the
  content arrives as context (11/12 LVLMs fail); embedded notices are ignored.
- **In scope (training-data provenance evasion).** Passive membership inference **collapses to near-random at
  scale** — `A40575` documents prior MIA at author-reported ROC-AUC **~0.50–0.56** at +5B tokens, motivating a
  pre-publication watermark over passive attribution.
- **The strongest adaptive case to design against (the one model to emulate).** `A40909` (iSeal): the adversary
  **controls inference end-to-end**, has **white-box weight access**, performs **collusion-based fingerprint
  unlearning**, and applies **output-manipulation to evade exact match**. This is the most adversarially
  realistic threat model in either corpus and the template a serious signed-provenance deployment should target.
- **Knowledge assumptions cluster** as: black-box on the mark for generative-output watermarking; white-box on
  the asset for the removal attacks (`A37429`) and iSeal's adversary (`A40909`); grey-box log-prob access for
  the data-provenance methods (`A37038`, `A40575`).
- **Explicitly out of scope for the corpus evidence (the implementer MUST add these).**
  - *Signature forgery / owner-mark spoofing* to frame a victim or manufacture a false origin — repeatedly named
    as a gap and **almost never evaluated** (`A38094`, `A40546`, `A41092`, partially `A40909`). This is the
    defining untested risk of the whole pattern.
  - *False-attribution / cross-owner collision at scale* — rarely quantified (`A38094`, `A40892`, `A40901`,
    `A40921`, `A41092`).
  - *Adaptive, scheme-aware attacks in general* — untested across the corpus except `A40909` and `A39992`.
- **Trust-boundary assumptions to reject.** (1) That **presence** of an embedded mark implies integrity — a
  separable/inactive mark is removable (`A37429`, `A39041`). (2) That **absence** of a signature can be treated
  as benign — the control must fail closed on absence (reviewer synthesis; the corollary of hiding-is-not-a-
  boundary). (3) That **exact-match** verification is safe — it is evadable by output manipulation (`A40909`).

## Control mechanism

A **deterministic verify-or-fail-closed provenance check**, with the secret held outside the model:

1. **Sign at creation / pre-publication.** A trusted signer binds a provenance manifest (content hash, origin,
   author, timestamp, model id) to an **external secret** and emits a signature protected by an
   **error-correcting code**, applied **before the artifact circulates** (`A40909` key-generated encoder +
   Reed–Solomon; `A41092` extended (8,4,4) Hamming + anchor synchronization; `A40561` ChaCha20 key custody;
   proactive owner-side application before circulation is the design of `A37865` and `A40575`).
2. **Verify under a trusted verifier using similarity + ECC, not exact match.** `A40909`'s central design
   choice: exact match is evadable and weight-embedded secrets are removable, so verify with **similarity +
   error correction** and keep the verifier trusted to prevent overclaim. Benign channel transforms stay within
   the error budget; forgeries and tampering fall outside it (the intended property — *forgery resistance itself
   is untested, see Residual risks*).
3. **Decide deterministically, environment-side, fail-closed.** The verification decision runs **outside the
   model's control plane**. Absent, invalid, or unverifiable signature ⇒ **deny / flag / defer to human** —
   never treat as authentic (deny-by-default; corollary of the removal red-team and of `A40910`'s reject path).
4. **Check provenance where untrusted content enters context, not at the surface prompt.** `A40910`'s
   transferable agent pattern: a tool-augmented ingestion gate (notice identifier → source verifier → query-risk
   analyzer/rewriter → status reminder) verifies retrieved/uploaded artifacts at ingestion.
5. **Emit the result as evidence into a provenance registry**, paired with access control and query monitoring —
   *evidence, not prevention* (whole Model-IP corpus).

## Preconditions and trust assumptions

- **The secret lives outside the model/weights and is under custody.** `A40909` directly critiques
  weight-embedded fingerprints as removable under white-box access; key-custody is a first-class requirement
  (`A40561` ChaCha20, `A40546`, `A41092`). Treat the signing key as a governed credential with rotation and
  revocation — its compromise is a total bypass (see Rollback).
- **A trusted verifier / trusted third party exists, and its model + key are pinned and version-controlled.**
  `A40909` keeps verification under a trusted verifier; `A37865` shows a verifier-model version change (its SAM
  dependency) can silently break verification — treat the verifier model as a governed dependency.
- **Signing happens at creation / pre-publication.** Retroactive protection of already-published content is a
  *different* problem the corpus solves with **intrinsic, no-embedding fingerprinting** (`A40843` StyleSentinel
  SVDD hypersphere; `A40851` OFA passive attribution), not with signing.
- **The verification-access model is chosen deliberately.** The corpus offers four postures with sharply
  different deployment burdens (reviewer synthesis over §10/§15 of Model-IP): external-secret + trusted-third-
  party (`A40909`, the most deployable and the most robust to a full-access adversary); model+key owner-white-box
  (`A40546`, `A40561`, a heavier burden); grey-box log-prob (`A40575`); fully passive (`A40851`).
- **ECC parameters and the similarity threshold are tuned** to tolerate the benign channel (compression, resize,
  paraphrase) without admitting forgeries — but **forgery resistance is untested in the corpus**, so this
  boundary must be validated in production, not assumed.
- **Presence of a mark does not imply integrity; absence does not imply benign.** Fail closed on absence
  (`A37429`, `A39041` corollary).
- **This is a layer, not the sole control.** Every Model-IP card ends here: combine with access control, query
  monitoring, and provenance registries; do not rely on the mark to stop misuse.

## System architecture

Signing happens once, at the source; verification happens at every trust boundary the artifact crosses.

```
  CREATE / PRE-PUBLICATION                         DISTRIBUTION CHANNEL
  ┌───────────────────────────┐    (compression, resize, paraphrase, re-hosting,
  │ Trusted signer            │     regeneration, extraction — benign + adversarial)
  │  manifest = {hash, origin,│                         │
  │   author, ts, model id}   │                         v
  │  sign(manifest, EXTERNAL  │        ┌───────────────────────────────────────┐
  │   secret) + ECC           │──────► │ untrusted artifact + (maybe) signature │
  │  (A40909 RS, A41092 Hamm.,│        └───────────────────────────────────────┘
  │   A40561 ChaCha20;                                  │
  │   proactive/pre-pub                                 v
  │   A37865, A40575)         │        [ INGESTION / VERIFICATION GATE ]  ← env-side, outside model control
  └───────────────────────────┘          verify at the context boundary,
        secret key = credential            not the surface prompt (A40910)
        (custody + rotation)                          │
                                                       v
                                   ┌──────────────────────────────────────┐
                                   │ Trusted verifier                     │  model+key PINNED/versioned
                                   │  similarity + ECC  (NOT exact match) │  (A40909 trusted verifier;
                                   │  (A40909)                            │   A37865 verifier-version dep.)
                                   └──────────────────────────────────────┘
                                                       │
                          absent / invalid / unverifiable / forged
                                                       │
                        ┌──────────────────────────────┴───────────────┐
                        v (FAIL CLOSED)                                  v (verified)
                 deny / flag / defer to human                    admit as EVIDENCE →
                 (deny-by-default; A40910 reject)                provenance registry + audit
                                                                 (evidence, NOT prevention)
```

Overlays: (a) for the **RAG/embedding supply chain**, mark the embedding API so agent memory carries provenance
(`A40728`); (b) if the **signed asset is a model**, design the mark for **extraction survival** via
in-distribution, task-coupled coupling rather than an OOD trigger set a stolen model forgets (`A39992`).

## Recommended implementation pattern

Deterministic, fail-closed, least-privilege, key-custodial:

- **Bind to an external secret, verify with similarity + ECC, never exact match.** `A40909`'s template is the
  strongest evidence in the corpus and the only adaptively-evaluated one: external key/encoder + Reed–Solomon,
  similarity-based verification, verifier kept trusted to prevent overclaim.
- **Sign proactively, at creation / pre-publication.** Apply provenance before the artifact circulates
  (`A37865` owner-embeds-before-circulation; `A40575` pre-publication watermark). Do not rely on post-hoc
  detection of an unsigned artifact.
- **Fail closed on absent/invalid/unverifiable signature.** Absence is *not* evidence of authenticity (corollary
  of `A37429`/`A39041`: hiding is not a boundary; a stripped mark yields an unsigned artifact).
- **Do not treat steganographic hiding as the security boundary.** Assume any separable/encapsulated mark is
  removable (`A37429`, `A39041`); the security must come from the cryptographic bind + fail-closed verification,
  not from the mark being hard to find.
- **Verify at the context/ingestion boundary.** Externalize the check into tools (verifier + risk analyzer +
  query rewrite) and run it where untrusted content enters, not on the surface prompt (`A40910`).
- **Treat the secret key as a governed credential.** Custody, rotation, revocation, and least-privilege access
  to the signing path (`A40561`, `A40546`, `A41092`, `A40909`); a decode-time watermark additionally requires
  **serving-path control** (`A40546`, `A41092`).
- **If the asset is a model, couple the mark to the primary task, in-distribution** so it survives extraction
  (`A39992`); an OOD trigger set is forgotten by a stolen model.
- **Mark the embedding API** if agents consume its outputs — a supply-chain provenance control for RAG/memory
  (`A40728`).
- **Pin and version-control the verifier model and key.** Treat a verifier-version change as a breaking change
  (`A37865`).
- **Present the result as one evidence signal**, combined with access control and monitoring — and, for
  synthetic-media provenance, combined with detection and human review (`A40909`; Deepfake §14 "combine with
  cryptographic provenance (C2PA-style), watermarking, and human review").

## Incorrect or fragile implementation patterns

- **Relying on a hidden/steganographic mark as the boundary.** Separable marks are removable — `A37429`
  (three 3DGS schemes broken white-box), `A39041` (~100% black-box removal).
- **Weight-embedded fingerprint + exact-match verification.** Removable under white-box access and evadable by
  output manipulation (`A40909`, direct critique).
- **Treating an embedded generative-output watermark as tamper-proof provenance.** Regeneration and purification
  strip it (`A38094` trajectory dependence; `A37429`, `A39041` removal).
- **Failing open on a missing signature** (treating "no signature found" as "authentic / unmodified"). This
  inverts the control; unsigned must be untrusted.
- **Verifying only at the surface prompt, not at ingestion.** Misses the actual bypass channel (`A40910`,
  11/12 LVLMs fail via context).
- **Using a passive detector as an authoritative provenance gate.** Detectors are probabilistic evidence; MLLM
  explanations are empirically unreliable (`A38060` ≤67.4% incorrect flaws) and averaged SOTA masks near-chance
  behavior on hard sets (Deepfake §10).
- **Expecting an OOD trigger set to survive model theft** (`A39992`: forgotten by the stolen model).
- **Using passive membership inference as training-data provenance at scale** (`A40575`: prior MIA ROC-AUC
  ~0.50–0.56, near-random).
- **Leaving the verifier model un-pinned** (`A37865`: a version change silently breaks verification).
- **Putting the signing key in the serving path without custody/rotation** (`A40546`, `A40561`, `A41092`).

## Verification strategy

- **Prove verification is deterministic and fail-closed.** For every artifact class, assert that absent,
  invalid, corrupted, and (constructed) forged signatures are rejected *regardless of the model's output*, and
  that the decision runs outside the model's control plane (`A40909`; `A40910` reject path).
- **Test the similarity + ECC boundary explicitly** (`A40909`, `A41092`): benign channel transforms
  (compression, resize, paraphrase) within the designed error budget must still verify; tampering and forgeries
  outside it must fail. Report the two directions separately.
- **Run the removal / purification red-team** (`A37429`, `A39041`) and confirm a stripped artifact verifies as
  *unsigned* and fails closed — not as authentic.
- **Test regeneration stripping** and placement robustness (`A38094`).
- **For model assets, test extraction/distillation survival** via behavior/neuron-activation analysis
  (`A39992`).
- **REQUIRE a forgery / owner-mark spoofing evaluation before trusting any attribution claim.** This is the
  corpus's near-universal omission (`A38094`, `A40546`, `A41092`, `A40909` partial) and the single most
  important thing to add — do not launch attribution decisions without it.
- **Measure false-attribution / cross-owner collision at scale** with distinct keys/owners (`A38094`, `A40892`,
  `A40901`, `A40921`, `A41092`).
- **Validate training-data provenance at production scale** — `A40575`'s +5B-token result is
  continued-pretraining, not from-scratch (author-flagged); the p-value decision was demonstrated at <0.001%
  corpus fraction.
- **Inject provenance-bearing content through the ingestion channel** and confirm the gate actually checks it
  (`A40910`).
- **Independent validation on the target stack** — most results here are single-paper, truncated, or
  single-model-family (`A38094` SD/DDIM; `A40892` SD v2.1 only; `A37429` Mip-NeRF360 only).

## Metrics and thresholds

Author-reported baselines are labeled; **target values are engineering targets requiring production validation,
not paper-derived guarantees.**

- **Forged / absent-signature accept rate.** *Target: 0* under the red-team. This is the whole point of
  fail-closed verification. **Caveat: forgery resistance is untested in the corpus** (`A38094`, `A40546`,
  `A41092`, `A40909` partial) — a "0" here is a target, not a demonstrated property.
- **Removal / purification robustness (offensive baselines).** Watermark-PSNR reduction (`A37429`,
  author-reported up to **16.34 dB**, <1 dB scene loss); removal success rate (`A39041`, author-reported
  **~100%**). Use these to size how easily an embedded mark is stripped in your setting; the answer motivates
  fail-closed handling of the resulting unsigned artifact.
- **Cross-owner collision / false-attribution rate at scale.** Rarely quantified in the corpus (`A38094`,
  `A40892`, `A40901`, `A40921`, `A41092`); *target: near 0*, measured before any attribution decision.
- **Extraction-survival** of a model-asset mark (`A39992`).
- **Training-data provenance decision p-value** at low corpus fraction (`A40575`: decision-relevant p-value at
  <0.001% corpus; prior MIA ROC-AUC ~0.50–0.56 as the near-random baseline to beat).
- **Context-channel bypass rate** at ingestion (`A40910`: baseline 11/12 LVLMs fail without the gate).
- **Verification true-accept under benign transforms** (similarity+ECC pass rate; `A40909`, `A41092` — specific
  headline numbers **not stated in paper** in the reviewed text).

Do **not** publish a single-number "secure" threshold: every number here is author-reported and non-adaptive
except `A40909` and `A39992`, and forgery resistance is unquantified.

## Test cases

1. **Absent signature → fail closed.** Unsigned artifact is denied/flagged/deferred, never admitted as
   authentic (deny-by-default corollary of `A37429`/`A39041`).
2. **Invalid / corrupted signature → fail closed; ECC recovers only within the designed error budget**
   (`A40909`, `A41092`).
3. **Forged signature / spoofed owner mark → reject.** *(Flag: the untested frontier — construct the best
   forgery you can; `A40909` only partially evaluates this.)*
4. **Benign channel transform within budget → still verifies** via similarity+ECC (`A40909`), e.g. compression,
   resize, paraphrase.
5. **Removal / purification attack → stripped artifact verifies as unsigned and fails closed** (`A37429`,
   `A39041`).
6. **Regeneration stripping → placement robustness holds or fails closed** (`A38094`).
7. **Ingestion-channel provenance check** — provenance-bearing content injected via RAG/upload is verified at
   the boundary, not the surface prompt (`A40910`).
8. **Model-extraction survival** — mark survives distillation/stealing via in-distribution coupling (`A39992`).
9. **Cross-owner collision** — two owners with distinct keys; confirm no false cross-attribution (`A38094`,
   `A40892`, `A40901`, `A40921`, `A41092`).
10. **Verifier-version change → controlled and flagged, not a silent break** (`A37865`).

## Adaptive adversarial tests

The corpus's single largest gap is the near-universal absence of adaptive, scheme-aware evaluation — a
*replicated absence* across both syntheses (Model-IP §11/§17; Deepfake §11/§17). The implementer must add what
the papers did not:

- **Emulate `A40909`'s adversary — the one adaptive model in the corpus.** Adversary controls inference
  end-to-end, has white-box weights, performs **collusion-based fingerprint unlearning**, and applies
  **output-manipulation to evade exact match**. Run this against your verifier and confirm similarity+ECC (not
  exact match) still holds.
- **Signature forgery / owner-mark spoofing** to manufacture a false origin or frame a victim — the corpus's
  most-named, least-tested attack (`A38094`, `A40546`, `A41092`). Treat a passing suite that omits this as *no
  coverage*.
- **Adaptive removal / purification** beyond the fixed transforms — scheme-aware stripping and regeneration
  (`A37429`, `A39041`, `A38094` demonstrate single non-adaptive removals; adapt them).
- **Adaptive context-channel bypass** with obfuscated or split payloads — `A40910`'s CopyGuard is *not*
  stress-tested against these (Model-IP §17).
- **Adaptive extraction** using `A39992`'s adaptive + detection-attack methodology as the template.
- **Key-compromise scenario** — assume the signing key leaks; measure blast radius and revocation latency
  (reviewer synthesis; key-custody papers `A40561`, `A40546`, `A41092`, `A40909`).

Label all pre-adaptive results as "against the tested attacks under the evaluated non-adaptive threat model."

## Telemetry requirements

- **Append-only provenance/verification audit** — ordered `(artifact hash, signature-status, verifier model +
  version, key id, decision)` records for forensic replay (reviewer synthesis; mirrors the immutable-audit
  discipline the Guardian stack applies elsewhere).
- **Verification-failure / absent-signature events** logged and alerted (fail-closed decisions are
  security-relevant signal).
- **Key usage, rotation, and revocation events** — the signing key is a credential; its custody trail is part of
  the trust boundary (`A40561`, `A40546`, `A41092`, `A40909`).
- **Verifier model + version as a governed dependency** — log it so a version change is visible, not silent
  (`A37865`).
- **Cross-owner collision / near-duplicate alerts** and false-attribution monitoring at scale (`A38094`,
  `A40892`, `A40901`, `A40921`, `A41092`).
- **Ingestion-boundary provenance-check outcomes** — what was verified, what failed, what was rewritten/deferred
  (`A40910`).
- **Registry writes** for every attribution decision, so downstream reliance is auditable.
- **Detection-vs-provenance disagreement**, where a passive detector runs alongside — surface uncertainty, do
  not collapse it to a verdict (Deepfake §14 "surface uncertainty, not just a verdict").

## Failure handling

- **Fail closed.** On absent, invalid, unverifiable signature, verifier error, or timeout → **deny / flag /
  defer to human**; never fall through to "authentic" (deny-by-default; `A40910` reject path; corollary of the
  removal red-team).
- **Reject / defer to human review as a first-class action** for out-of-distribution or ambiguous cases
  (`A40910` status-reminder / query-rewrite path).
- **Never treat unsigned as authentic, and never accept self-asserted provenance** without verifier
  confirmation.
- **Assume residual harm and keep compensating controls active** — signed provenance is evidence, not
  prevention; pair it with access control and query monitoring (whole Model-IP corpus).

## Rollback and containment

- **Key rotation and revocation are the primary containment lever.** A compromised signing key can produce
  *valid* signatures, so the registry must support revocation and the signing path must support rapid rotation
  (`A40561`, `A40546`, `A41092`, `A40909` key custody). This is the reviewer-synthesis containment story — the
  corpus does not benchmark key-compromise recovery.
- **The provenance registry enables revocation and forensic replay** — quarantine or re-flag artifacts signed
  with a revoked key.
- **Quarantine artifacts that fail verification** rather than silently dropping or admitting them.
- **Pin the verifier model and stage its rollout** so a verifier change is a controlled migration, not a silent
  break (`A37865`).
- **Residual containment gap:** a leaked signing key is a **total bypass until revoked** — containment reduces,
  it does not eliminate (reviewer synthesis). Adaptive removal (`A37429`, `A39041`) similarly reduces, not
  eliminates, the reliability of any embedded component.

## Known bypasses

Demonstrated (within papers, mostly under non-adaptive threat models) and reviewer-identified:

- **Removal / purification of embedded marks** — `A37429` (three 3DGS schemes, white-box, up to 16.34 dB
  reduction), `A39041` (two schemes, black-box, ~100% removal). Steganographic hiding is **not** a boundary.
- **Regeneration stripping** — `A38094` (placement-dependent survival; the wrong placement is stripped by the
  matching transform).
- **Context-channel bypass** — `A40910` (11/12 LVLMs fail via multimodal/RAG context; embedded notices ignored).
- **Membership-inference collapse at scale** — `A40575` (prior MIA ROC-AUC ~0.50–0.56, near-random).
- **Exact-match verification evasion + weight-embedded-fingerprint removal** under white-box access — `A40909`
  (the reason to use external-secret + similarity/ECC instead).
- **EaaS watermark removal by a single attack family** — `A40728` documents trigger-word schemes broken by
  paraphrasing and WET broken by dimension-perturbation.
- **Forgery / owner-mark spoofing** — largely **untested**; the biggest unquantified bypass class, named in
  `A38094`, `A40546`, `A41092`, partially `A40909`.
- **Signing-key compromise** — a leaked key forges valid signatures (reviewer synthesis; key-custody papers).
- **Verifier-version drift** silently breaks verification (`A37865`).
- **Adaptive, scheme-aware attackers are essentially untested** against these controls except `A40909` and
  `A39992` — a replicated absence and the largest unquantified bypass surface.

## Residual risks

- **Forgery / spoofing resistance is unestablished** — the defining residual of this pattern. The corpus names
  it repeatedly and almost never measures it (`A38094`, `A40546`, `A41092`, `A40909` partial).
- **Signed provenance is evidence, not prevention** — it supports attribution/governance/legal action; it does
  not stop misuse (whole Model-IP corpus).
- **All robustness numbers are non-adaptive upper bounds** except `A40909` (adaptive, litigation-grade) and
  `A39992` (adaptive + detection). Read "robust" as "against the tested, non-adaptive attacks."
- **Key custody is a single point of trust** — a leaked signing key is a total bypass until revoked.
- **The trusted verifier is a single point of trust** — its version drift breaks verification (`A37865`) and its
  compromise removes the control (reviewer synthesis).
- **False-attribution / cross-owner collision at scale is rarely quantified** (`A38094`, `A40892`, `A40901`,
  `A40921`, `A41092`) — attribution decisions carry unmeasured collision risk.
- **Retroactive coverage gap** — unsigned legacy content is unprotected; intrinsic fingerprinting (`A40843`,
  `A40851`) is a separate control for that case.
- **Cross-modal / cross-model-family generalization is siloed** (image, audio, text, tabular, embedding, 3DGS
  methods are separate) — a unified provenance layer must compose per-modality mechanisms, not assume one.
- **Single-dataset / single-family concentration** limits external validity (`A37429` Mip-NeRF360; `A38094`
  SD/DDIM; `A40892` SD v2.1) — production validation required.

## Relevant research (stable paper ids from the syntheses/cards)

**Crypto-provenance / verification (the core template):**
- **A40909** — iSeal: encrypted external-secret LLM ownership fingerprint (key-generated encoder + Reed–Solomon;
  **similarity + ECC**, not exact match). The **strongest and only litigation-grade adaptive** threat model
  (white-box weights, collusion unlearning, output-manipulation evasion). *The template this pattern is built
  on.*
- **A40561** — Audio latent + inversion watermark with **ChaCha20** secret-key custody; owner-white-box
  verification; non-adaptive attacks only.
- **A41092** — LLM-text logit-biasing watermark with **extended (8,4,4) Hamming coding + anchor synchronization**;
  requires serving-path control and key custody; forgery resistance and under-attack numbers not fully verified
  in the reviewed text.
- **A40546** — LLM-text logit-biasing watermark (rank-mod-k); owner-white-box (model+key) verification; forgery
  resistance untested. *Decode-time tagging of agent output; key = credential.*

**Ingestion-boundary enforcement (most agent-relevant):**
- **A40910** — CopyGuard / LVLM copyright: guardrail bypass via the multimodal/RAG **context channel**
  (author-reported 11/12 LVLMs fail); tool-augmented ingestion-time gate (notice identifier → source verifier →
  query-risk analyzer/rewriter → status reminder). *Verify provenance where content enters, not at the prompt.*

**Extraction survival & supply chain:**
- **A39992** — DeepTracer: extraction-robust watermarking (hard-label / data-free stealing) with **adaptive +
  detection** attacks; the **in-distribution, task-coupled** design principle (OOD triggers are forgotten by
  stolen models), backed by neuron-activation analysis.
- **A40728** — RegionMarker: EaaS embedding-API watermark robust to copy/paraphrase/dimension-perturbation;
  documents prior EaaS schemes each broken by one attack family. *Provenance for the RAG/agent-memory supply
  chain.*

**Training-data provenance:**
- **A40575** — SPECTRA: pre-publication text watermark detected via grey-box log-probs at +5B-token scale
  (<0.001% corpus fraction), decision-relevant p-value; documents prior MIA collapsing to ROC-AUC ~0.50–0.56;
  continued-pretraining (not from-scratch) caveat.
- **A37038** — Code membership inference as a training-data / copyright auditor; grey-box log-prob access;
  closed-API auditing without logits is the open gap.

**Removal red-team (why hiding is not a boundary; why fail-closed):**
- **A37429** — GSPure: white-box removal breaking three scene-hiding 3DGS watermarks (author-reported up to
  16.34 dB watermark-PSNR reduction, <1 dB scene loss); Mip-NeRF360 only.
- **A39041** — Box-free image-to-image watermark removal (black-box query API) with author-reported ~100%
  removal (PSNR up to 34.69 dB); enables watermark-free surrogate training; proposed query-screener defense not
  rigorously benchmarked.

**Robustness levers & embedded-mark caveats:**
- **A38094** — In-generation structure watermark; **placement in the generative trajectory is a robustness
  lever** (early survives regeneration; late survives geometric/valuemetric transforms); SD/DDIM single-family
  scope; forgery/collision not evaluated.
- **A40892 / A40901 / A40921 / A37103 / A37412 / A39199** — generative-output watermarking family (in-generation,
  post-hoc, tabular); non-adaptive robustness; false-attribution/collision rates largely unquantified; several
  headline numbers **not stated in paper** in the reviewed text.

**Intrinsic-fingerprint alternative (retroactive coverage):**
- **A40843** — StyleSentinel: intrinsic, no-embedding style fingerprint (SVDD hypersphere); argues embedded
  marks are removable.
- **A40851** — OFA: passive image-to-model attribution; fully passive verification; under-attack numbers
  reviewer-unverified.

**Proactive / attestation analogue and verifier-pinning (Deepfake corpus):**
- **A37865** — Blank Canvas: proactive owner-side protection applied **before circulation**; the corpus's
  closest analogue to an attestation/provenance control; tamper-localization is **tied to a specific SAM
  version** (verifier-version dependency); perturbation survivability untested; released code.
- **A38060** — ESIDE: quantifies that standalone MLLM forensic explanations are unreliable (**≤67.4%** incorrect
  flaws) — evidence that detectors/explanations must be gated, not trusted as authoritative provenance.
- **A37421** — MIRAGE: fast-verdict + confidence-gated reflective verifier (cheap-check-then-deep-check),
  reusable as an escalation shape around a provenance check. *Deepfake §14 recommends combining detection with
  cryptographic provenance (C2PA-style) + watermarking + human review — the reviewer-synthesis basis for signed
  provenance as the deterministic layer.*

**Excluded (off-topic; carry no security weight):** `A39623` (Shapley/FANOVA GP explainability) and `A40030`
(VeriFlow NN formal verification) are flagged miscategorized in the Model-IP synthesis and are **not** used here.

## Evidence strength

- **The design principle** — bind provenance to an **external secret**, verify under a **trusted verifier** with
  **similarity + ECC (not exact match)**, **fail closed** on absent/invalid signatures, **verify at ingestion**,
  and **do not treat hiding as a boundary** — is **convergent across independent papers** (`A40909`, `A40910`,
  `A37429`/`A39041`) and echoed by the Deepfake synthesis's explicit C2PA-style recommendation. This is
  *convergence across independent studies, not independent replication of one effect size*. Reviewer assessment:
  **moderate** confidence in the principle's direction.
- **Critical scoping caveat.** No paper implements a full **detached cryptographic-signature / PKI
  content-credential** scheme. `A40909` is the closest studied primitive (external-secret crypto-provenance with
  ECC) and the only one with an adaptive threat model; the rest of "signed provenance" as specified is a
  **reviewer-synthesis extrapolation** and **requires production validation**.
- **Specific numbers** (16.34 dB reduction; ~100% removal; ROC-AUC 0.50–0.56; 11/12 LVLM failure; ≤67.4%
  incorrect flaws) are **author-reported, non-adaptive** (except `A40909`, `A39992`), often single-model /
  single-family / truncated, and **not independently verified**. Many watermark headline numbers are **not
  stated in paper** in the reviewed text.
- **Forgery / spoofing resistance is untested** across the corpus — the load-bearing gap; any "unforgeable" or
  "0 forged-accept" claim is a target, not a demonstrated property.
- **Bottom line:** a **well-motivated attribution-and-tamper-evidence control** with modest, mostly non-adaptive
  empirical backing and one strong adaptive anchor (`A40909`). It is **not** a prevention mechanism. Every
  deployment claim **requires production validation**, and a **forgery red-team plus an adaptive red-team** are
  prerequisites before operational reliance.

## When NOT to use this pattern

- **When you need prevention, not attribution.** Signed provenance is evidence — it does not stop misuse (whole
  Model-IP corpus). If the goal is to block an action, use a permission gate / human approval, not provenance.
- **When you cannot control creation / signing** (already-published or third-party content). Signing is a
  pre-publication act; for retroactive coverage use **intrinsic fingerprinting** (`A40843`, `A40851`) and do not
  claim signed provenance.
- **When you cannot custody a key or operate a trusted verifier.** The scheme's trust collapses to the weakest
  of the two; without key custody and a pinned verifier, a "signed" claim is not meaningfully stronger than an
  embedded mark (`A40909`, `A37865`). Do not over-state assurance.
- **As the sole control or a hard gate.** It is a *layer* — pair with access control, query monitoring, human
  review, and (for synthetic media) detection (whole Model-IP corpus; Deepfake §14).
- **When you rely on an embedded mark surviving regeneration / distillation** and cannot couple it
  in-distribution — embedded marks are removable (`A37429`, `A39041`, `A38094`) and OOD marks are forgotten by
  stolen models (`A39992`).
- **When you would make an attribution or litigation claim without a forgery / cross-owner-collision
  evaluation.** The corpus's near-universal omission (`A38094`, `A40546`, `A41092`, `A40909`) means the false-
  attribution / framing risk is unmeasured; do not build irreversible decisions on top of it.
