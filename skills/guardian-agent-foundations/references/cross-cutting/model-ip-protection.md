# Cross-Cutting Chapter — Model Intellectual-Property Protection

*Source synthesis: `references/syntheses/Model-IP-Protection.md` (22 AAAI-26 research cards,
one merged partial synthesis; two cards — A39623, A40030 — flagged off-topic and carrying no
security weight). This chapter is a cross-paper reading organized by IP-protection **thread**, not a
per-paper list. It exists to surface the arguments that become visible only when the papers are read
against each other.*

---

## Evidence-integrity contract (non-negotiable)

- Every numeric value is **author-reported under that paper's own evaluated threat model** unless
  explicitly marked otherwise. The source synthesis flagged that several under-attack tables were
  truncated in the extracted PDFs (A38094, A40910, A40921, A41092, A40851); those magnitudes are
  recorded as author-stated and are **not independently transcribed** here.
- No titles, authors, venues, datasets, or metrics are invented. Where the synthesis recorded a value
  as absent, this chapter writes **"not stated in paper"** rather than supplying one. Headline
  fidelity/bit-accuracy numbers for the image and text watermarking papers (A37103, A37412, A38094,
  A40892, A40901, A40921, A40546, A41092) were truncated/unverifiable in the reviewed text and are
  **not stated in paper**.
- Claims are labeled **(direct)** when they are a finding of the cited paper(s) as recorded in the
  synthesis, and **(reviewer synthesis)** when they are cross-paper judgments — carried over from the
  source synthesis or made in this chapter. Cross-paper judgments are not assertions of any single
  paper.
- Language is calibrated: "demonstrated under the evaluated threat model", "reduced removal success
  against the tested attacks", "not evaluated against", "requires production validation". No absolutes
  ("secure", "unbreakable", "proven safe", "tamper-proof") appear.

## Reading key — the CPVER mapping

Every implication is tagged to the Guardian-Agent enforcement primitives (`worldview.md` §2–§6,
`glossary.md`). The organizing conclusion of this entire corpus is a CPVER statement: **a recovered
watermark or fingerprint is [E] Evidence, not [P] Permission and not prevention** (reviewer synthesis
over nearly every card; each card states the mark supports post-hoc attribution/governance/legal
action but does not itself stop misuse).

- **[C] Capability** — what a model/asset *can produce or reveal*: generated outputs, embeddings,
  log-probs, the intrinsic activation signature. A watermark bit or fingerprint response is a
  capability signal that must be *verified* before it is trusted as evidence.
- **[P] Permission** — what an actor is *authorized* to do: API access control, query-rate/monitoring,
  serving-path control, and **secret-key custody** (the recurring permission surface in this corpus —
  A40546, A40561, A40909, A41092 all depend on a governed key).
- **[V] Verification** — *independent, adversary-aware checking* of an ownership claim before it is
  trusted: trusted-verifier prompting (A40909), similarity+ECC instead of exact match (A40909),
  statistical/p-value tests (A40575, A40728), and — mostly *absent* in this corpus — forgery/collision
  testing.
- **[E] Evidence** — *tamper-evident, independent attribution records*: the recovered mark, the
  intrinsic fingerprint, the provenance registry, the log-prob detection statistic. This is what the
  corpus actually produces.
- **[R] Residual-risk** — what remains after a mark is embedded. In this corpus the residual risk is
  dominated by **two systematically-untested gaps**: (1) scheme-aware **adaptive** removal, and
  (2) **forgery/spoofing** of an owner's mark to frame them. "Robust" here means *robust against the
  tested, non-adaptive attacks* — the residual against an adaptive or forging adversary is largely
  **unknown**.

The single most replicated meta-finding (reviewer synthesis, source §3, §12): **nearly every
watermarking paper evaluates against fixed, off-the-shelf distortions rather than a scheme-aware
optimizing adversary, and forgery/spoofing is named as a gap almost everywhere and evaluated almost
nowhere.** That finding is why the [R] tag appears on nearly every thread below.

---

## Thread 1 — Model extraction (functionality stealing)

**Well-established.** Extraction — training a surrogate that copies a victim's function via queries —
is treated as a first-class threat, and the corpus's central design principle for surviving it is
concrete: **the ownership mark must be in-distribution and coupled to the primary task, not an
out-of-distribution trigger set.** A39992 (DeepTracer) is the load-bearing entry: it is
extraction-robust classifier watermarking evaluated against **hard-label and data-free stealing plus
adaptive and detection attacks**, and its central claim — that OOD watermark triggers activate
disjoint neurons and are *forgotten* by a stolen model whereas in-distribution coupling makes the
watermark inseparable from the copied functionality — is supported by author neuron-activation
analysis (direct). This is one of only two genuinely adaptive threat models in the corpus.

**Emerging.** Extraction on non-classifier surfaces: A40728 (RegionMarker) marks Embedding-as-a-Service
(EaaS) APIs against **copy, paraphrase, and dimension-perturbation** extraction, verified by a KS-test
(direct). Extraction as an *enabler* of watermark laundering: A39041 (box-free image-to-image removal)
shows a black-box query API can be used to train a **watermark-free surrogate** (direct) — extraction
and removal are the same operation here (cross-links Thread 9).

**Contested / bounded.** DeepTracer's adaptive evaluation is the exception, not the norm; the rest of
the extraction-adjacent evidence is non-adaptive beyond the specific attack families each paper
enumerates (A40728 tests three families; whether a *combined* or scheme-aware attacker defeats it is
not evaluated — reviewer synthesis).

**Where defenses fail.** OOD trigger-set watermarks are structurally defeated by extraction (A39992
mechanism, direct). EaaS marks validated against single attack families inherit unknown risk against a
composed attacker (A40728, reviewer synthesis).

**Implication.**
- **[E]/[C]** Design ownership marks for *extraction survival by in-distribution coupling* (A39992),
  not OOD triggers a stolen model discards. The mark is evidence only if it copies with the function.
- **[P]** Extraction is a query-volume behavior: rate-limit, monitor query trajectories, and treat a
  public inference API as an extraction surface (reviewer synthesis, source §14 — marks are
  attribution, access control is the prevention).
- **Launch gate:** an anti-extraction watermark evaluated only on OOD triggers or a single stealing
  method carries **[R] unknown** residual risk against data-free / hard-label / adaptive extraction;
  require the A39992 evaluation bar (adaptive + detection) before crediting extraction robustness.

## Thread 2 — Weight theft (white-box adversary owns the model)

**Well-established (as the strongest threat model, and as a critique of weight-embedded marks).** The
corpus's most adversarially-realistic entry, **A40909 (iSeal)**, models an adversary with **full
white-box weight access** who performs **collusion-based fingerprint unlearning** and
**output-manipulation to evade exact-match verification**, in an explicit litigation setting (direct).
Its argument is a direct critique of the rest of the corpus: **weight-embedded fingerprints are
removable under white-box access, and exact-match verification is evadable** — so ownership evidence
should bind to an *external* secret (a key-generated encoder + Reed–Solomon code) and verify by
**similarity + error-correction**, not weight inspection or exact match (direct). A37429 (GSPure)
corroborates the white-box-removal reality on a different asset class: given the *distributed* 3DGS
asset, it clusters and prunes low-contribution, viewpoint-inconsistent watermark Gaussians (Thread 9).

**Emerging.** Externalizing the secret entirely: intrinsic, no-embedding fingerprints (A40843
StyleSentinel, A40851 OFA) sidestep weight-embedding by reading an *inherent* signature, so there is
no embedded mark for a white-box adversary to unlearn (direct — though their claim that embedded marks
are removable is argued, not benchmarked head-to-head here).

**Contested.** *Where the secret should live* is the corpus's sharpest paradigm tension (source §10):
weight-embedded fingerprints (relied on implicitly by several watermarking papers) vs. iSeal's
external-secret position vs. intrinsic fingerprints. No head-to-head benchmark resolves it (reviewer
synthesis).

**Where defenses fail.** Any scheme whose ownership secret lives *in the weights* is, per iSeal's
threat model, removable by a white-box adversary and evadable by output manipulation against
exact-match verification (A40909, direct). Steganographic hiding inside a distributed asset is
clusterable/prunable (A37429, direct).

**Implication.**
- **[E]/[V]** Bind tamper-evident model identity to an **external secret**, verify by
  **similarity + ECC under a trusted verifier**, and assume the adversary controls inference
  end-to-end (A40909 template, source §15). Do not rely on exact-match ownership tests.
- **[P]** The external secret / key is a **governed credential** — custody and rotation are part of
  the trust boundary (A40909, A40561, A40546, A41092; source §15).
- **[R]** A weight-embedded fingerprint carries **known** removal risk under white-box access
  (A40909) — treat "the attacker doesn't have our weights" as a non-durable assumption for
  open-weight or exfiltration-exposed models.
- **Launch gate:** for any litigation- or attribution-grade ownership claim on a model an adversary
  could obtain, require an external-secret + similarity/ECC scheme evaluated against
  unlearning/output-manipulation (the A40909 bar), not weight inspection.

## Thread 3 — API imitation / surrogate training

**Well-established.** Black-box query APIs are a demonstrated laundering channel: **A39041** shows a
box-free image-to-image API can be driven to produce a **watermark-free surrogate** (author-reported
~100% removal; enables surrogate training) (direct). **A40728 (RegionMarker)** documents that prior
EaaS embedding watermarks each fell to a *single* imitation/extraction family — **EmbMarker, WARDEN,
EspeW defeated by paraphrasing; WET defeated by dimension-perturbation** — motivating its
comprehensive-coverage design (direct). The transferable reading: an exposed generative/embedding API
is an imitation surface, and single-family robustness is insufficient (reviewer synthesis).

**Emerging.** Grey-box detection of imitation and unauthorized training via **log-prob access**:
A37038 uses code membership inference as a copyright/training-data auditor; A40575 (SPECTRA) detects a
pre-publication text watermark from grey-box log-probs (Thread 6). These give an attribution signal
*without* white-box access, but are gated by logit/API availability (direct).

**Contested / bounded.** RegionMarker's coverage is against the three studied families; a scheme-aware
attacker composing families or optimizing against the region-marking scheme itself is not evaluated
(reviewer synthesis). A39041's proposed query-screener defense is **not rigorously benchmarked** per
its card (direct) — so the *defense* side of API imitation is weaker than the *attack* side.

**Where defenses fail.** Watermarks that survive one imitation family but not a composed one (A40728's
documented prior schemes). Any grey-box detector is defeated by **closed APIs that withhold log-probs**
— the corpus's most-cited coverage gap for auditing (A37038, A40575, A40546; source §17).

**Implication.**
- **[P]** Treat the inference/embedding API as the primary imitation control point: monitor and
  rate-limit paraphrase/dimension-probing query patterns; provenance-mark embedding APIs because those
  embeddings feed downstream RAG/agent memory (A40728 as a **supply-chain control**, source §14).
- **[V]** Where log-probs are available, grey-box statistical detection (A37038, A40575) provides an
  attribution signal — but this is verification of a *claim*, not prevention.
- **[R]** Closed-API auditing without logit access is **unsolved** in this corpus (source §17); an
  imitation claim against a log-prob-withholding API is **[R] unestablished**.
- **Launch gate:** do not credit an anti-imitation watermark that was validated against a single
  extraction/paraphrase family; require multi-family coverage (A40728) and state closed-API detection
  as production-validation-pending.

## Thread 4 — Watermarking (the dominant defense family)

**Well-established.** Watermarking is the corpus's largest defense cluster, spanning image
in-generation/latent (A37412, A38094, A40892, A40921), image post-hoc / encoder–noise–decoder (A37103,
A40901), audio latent+inversion (A40561), LLM-text decode-time logit-biasing (A40546, A41092), EaaS
embeddings (A40728), and tabular/GBDT (A39199). Two findings replicate across sub-modalities:

1. **Latent-space / in-generation embedding preserves output quality better than post-hoc marking** —
   recurring across A37412, A38094, A40561, A40892, A40921 (each author-reported on its own datasets;
   the convergence is reviewer synthesis, source §9).
2. **Placement in the generative trajectory is a robustness lever** — A38094: an early-latent (x_T)
   structure mark **survives regeneration**, while a late mark **survives geometric/valuemetric
   transforms** (direct). This makes robustness a placement decision, not only an encoder-strength
   decision.

**Emerging.** Error-correcting coded text watermarks — A40546 (rank-mod-k) and A41092 (extended (8,4,4)
Hamming + anchor synchronization) — carry a payload robustly at decode time; A40921 targets robustness
to **community fine-tunes / LoRA** via free-generation self-augmented training; A40892 uses PCA-energy
redundancy allocation with VAE-prior initialization (direct).

**Contested.** *Embedded marks vs. intrinsic fingerprints* (Thread 5): A40843/A40851 argue embedded
signals are removable/purifiable and favor no-embedding fingerprints; the watermarking majority argues
robust embedding is achievable. The synthesis records these as targeting *different* deployment
constraints (already-published content vs. provider-controlled generation), not a resolved contest
(source §10).

**Where defenses fail.** Every watermarking paper here is evaluated **non-adaptively** — against fixed,
off-the-shelf distortions/edits, not a scheme-aware optimizer (A37103, A37412, A38094, A40546, A40561,
A40892, A40901, A40921, A41092, A39199; source §3). Separable/"inactive" marks are removable (Threads
9). Decode-time text watermarks require **serving-path control** (A40546, A41092) — outside that
control the mark cannot be applied.

**Implication.**
- **[E]** Present any single watermark as **one probabilistic evidence signal scoped to a non-adaptive
  threat model** — never as prevention or as a guarantee (source §14, §16).
- **[C]/[P]** For decode-time text watermarking to tag agent-generated output for downstream
  attribution (A40546, A41092), you must own the serving path and custody the **secret key as a
  credential** (source §15).
- **[R]** "Robust" for every watermark here = *robust against the tested, non-adaptive attacks*; the
  adaptive-removal and forgery residuals are **unknown** (source §12).
- **Launch gate:** scope every robustness claim to the exact non-adaptive attack catalog tested; a
  watermark ships as an evidence layer, never as the sole IP control, and never with an unqualified
  "robust."

## Thread 5 — Fingerprinting (intrinsic vs. embedded ownership signatures)

**Well-established.** Fingerprinting — verifying ownership from a signature rather than an inserted
mark — splits into two paradigms in this corpus. **Intrinsic / no-embedding fingerprints** read an
inherent property: A40843 (StyleSentinel) fits an SVDD one-class hypersphere over a style signature to
detect LoRA/DreamBooth **style theft**; A40851 (OFA) does **passive image-to-model attribution** with
no embedding (direct). **External-secret fingerprints** encrypt the ownership signal outside the
weights: A40909 (iSeal) generates the fingerprint from a key-generated encoder and verifies by
similarity+ECC (direct; Thread 2).

**Emerging.** Fingerprinting as *retroactive* protection — the intrinsic paradigm's distinctive value
is protecting content/models that were **already published without a pre-embedded mark** (A40843,
A40851), a case embedded watermarking cannot serve (reviewer synthesis, source §19).

**Contested.** The intrinsic camp's core claim — that embedded signals are **removable/purifiable and
therefore require pre-publication embedding** — is *argued* by A40843/A40851 but **not benchmarked
head-to-head** against the watermarking majority within this corpus (direct claim, reviewer-flagged as
un-adjudicated; source §10, §19).

**Where defenses fail.** Passive/intrinsic verification's under-attack robustness is largely
**reviewer-unverified** here (A40851's under-attack numbers were truncated; source §12). An intrinsic
signature that an adaptive adversary can purify or mimic would yield false negatives — not evaluated
(reviewer synthesis).

**Implication.**
- **[E]/[V]** Choose the fingerprint paradigm by deployment constraint: intrinsic/no-embedding for
  **retroactive** protection of already-published assets (A40843, A40851); external-secret for
  **litigation-grade** model identity under a white-box adversary (A40909). They are not
  interchangeable (source §10).
- **[R]** Intrinsic-fingerprint robustness to adaptive mimicry/purification is **unestablished** in
  this corpus (A40851 truncated; A40843 argued not benchmarked) — treat as production-validation-pending.
- **Launch gate:** a fingerprint scheme's *false-negative under adaptive purification* and
  *false-positive across owners* must both be measured before it gates an attribution or takedown
  decision (Thread 8).

## Thread 6 — Ownership verification (the access model of the proof)

**Well-established.** Verification-access assumptions vary sharply and are an **architectural
decision**, not a detail (source §10, §15). Three postures recur:

- **Owner-white-box (model + key required to reconstruct the mark).** A40546 (LLM-text) and A40561
  (audio latent+inversion, ChaCha20 key) need the verifier to hold the model and key — a deployment
  burden and a third-party-replication limit (direct; source §12).
- **Grey-box log-prob detection.** A40575 (SPECTRA) verifies a pre-publication text watermark from
  log-probs at **+5B-token scale, <0.001% corpus fraction**, using a **decision-relevant p-value**;
  A37038 uses grey-box code MIA (direct). More deployable, but gated by logit access.
- **Passive / trusted-verifier.** A40851 (OFA) is fully passive (no embedding, no key). A40909 (iSeal)
  keeps verification prompts under a **trusted verifier** and uses **similarity+ECC instead of exact
  match** — specifically to prevent an adversary from evading or overclaiming (direct).

A distinct, strongly-supported verification finding: **standard membership inference collapses to
near-random at scale** — A40575 reports prior MIA at **ROC-AUC ~0.50–0.56 at +5B tokens**, motivating
pre-publication watermarking over passive MIA for training-data provenance (direct).

**Emerging.** Statistical verification with an explicit decision threshold — KS-test / p-value
(A40728, A40575) — moves ownership verification toward a quantified confidence claim rather than a
binary match (direct).

**Contested.** No head-to-head comparison of the three access postures exists in the corpus (source
§10, reviewer synthesis). Owner-white-box schemes trade deployability for not exposing the key;
grey-box schemes trade deployability for a **closed-API blind spot** (Thread 3).

**Where defenses fail.** **Exact-match verification is evadable** by output manipulation (A40909,
direct) — the corpus's clearest verification-mechanism failure. Grey-box verification fails on **closed
APIs** (A37038, A40575, A40546). Passive verification's adaptive robustness is unverified (A40851).

**Implication.**
- **[V]** Prefer **similarity + error-correction under a trusted verifier** over exact match (A40909),
  and quantify verification with a **p-value / statistical test** at a stated threshold (A40575,
  A40728) so the ownership claim carries a calibrated confidence.
- **[P]** Verification-access is a permission/deployment decision: model+key custody (A40546, A40561)
  vs. trusted-third-party (A40909) vs. grey-box log-prob (A40575). Pin and version-control the verifier
  model and key as governed dependencies (source §16).
- **[R]** Passive MIA is **near-random at scale** (A40575) — do not use it as a standalone provenance
  proof; prefer pre-publication watermarking where the training pipeline is controllable.
- **Launch gate:** state the verification-access assumption (white-box / grey-box / passive) next to
  every ownership claim; an exact-match verifier carries **[R] known** evasion risk (A40909) and should
  not gate a litigation-grade decision.

## Thread 7 — Tamper resistance (surviving removal, unlearning, and adaptation)

**Well-established.** Tamper resistance in this corpus means surviving *removal, unlearning, fine-tuning,
and output manipulation* — and the strongest evidence is a **critique** of naive tamper resistance:
A40909 (iSeal) demonstrates that weight-embedded fingerprints are removable under **collusion-based
unlearning** and that exact-match verification is evadable by **output manipulation** (direct). The
constructive answers in the corpus are (1) **external secret + error-correcting codes** — A40909
(key-generated encoder + Reed–Solomon), A41092 (extended (8,4,4) Hamming + anchor synchronization),
A40561 (ChaCha20 key custody) — and (2) **in-distribution task-coupling** so the mark cannot be
separated from the copied function without losing the function (A39992; direct).

**Emerging.** Robustness to **downstream adaptation** as an explicit tamper axis: A40921 targets
community fine-tunes / LoRA that break prior watermark modules, via free-generation self-augmented
training; A39199 targets post-deployment fine-tuning of tabular GBDTs (direct). These treat the
victim's own legitimate fine-tuning as a tamper vector.

**Contested.** Whether error-correction *alone* confers tamper resistance. ECC (A40909, A41092)
recovers a mark under bounded corruption, but the synthesis records that forgery resistance for the
coded text schemes is **untested/not fully verified** (A41092; source §20) — ECC addresses corruption,
not an adversary who *forges* a valid codeword (reviewer synthesis).

**Where defenses fail.** Separable/encapsulated marks are removable (Thread 9 — A37429, A39041):
steganographic hiding is **not a security boundary** (source §6, reviewer synthesis). OOD trigger
watermarks are unlearned by extraction (A39992). Exact-match verification is tamper-evadable (A40909).
ECC-coded schemes' resistance to *forgery* (as opposed to noise) is unverified (A41092).

**Implication.**
- **[E]/[V]** For tamper-evident identity, combine an **external secret**, **error-correction**, and a
  **trusted verifier** (A40909), and design the mark to be **in-distribution / task-coupled** so
  removal costs functionality (A39992). Do not treat hiding/encapsulation as tamper resistance
  (A37429, A39041).
- **[P]** Custody the ECC/encryption key as a credential; key rotation is part of tamper resistance
  (A40561, A40909, A41092; source §15).
- **[R]** ECC recovers from *corruption*, not *forgery*; a coded scheme with untested forgery
  resistance carries **[R] unknown** residual against an adversary who mints a valid codeword (A41092).
- **Launch gate:** a tamper-resistance claim must state which adversary it survives — non-adaptive
  distortion (most of the corpus), collusion unlearning + output manipulation (A40909 bar), or
  extraction (A39992 bar) — and must not conflate corruption-robustness (ECC) with forgery-resistance.

## Thread 8 — False-positive / false-negative risk (collision, forgery, over-refusal)

**Well-established (as a gap).** This is the corpus's most systematically **under-measured** property.
**Forgery / spoofing of an owner's mark** — framing an owner by producing their mark — is named as an
unaddressed gap across A38094, A40546, A41092, and partially A40909, and is **almost never evaluated**
(direct where each paper flags it; the pattern is reviewer synthesis, source §4, §12, §17).
**False-attribution / cross-owner collision rates at scale** are likewise rarely quantified (raised for
A38094, A40892, A40901, A40921, A41092; A40892 explicitly does not quantify false-attribution) (direct
flags; reviewer synthesis on the pattern).

**Emerging.** Where a *decision threshold* exists, false-positive control becomes measurable: A40575's
**decision-relevant p-value at <0.001% corpus fraction** and A40728's **KS-test** turn verification
into a calibrated statistic with a stated error rate (direct). This is the corpus's most promising
handle on false-positive risk, but it is present in only a few papers.

**Contested.** Nothing is directly contested here — the field agrees the gap exists; what varies is
whether a paper *acknowledges* it. The absence of forgery/collision numbers is a **claim-strength**
limitation, not a contradiction (reviewer synthesis).

**Where defenses fail.** Any attribution decision made from a mark without a measured collision rate
risks **false positives** (framing the wrong owner); any mark evaluated only against removal (not
forgery) risks an adversary **manufacturing a false positive** to frame a competitor. Over-strong
policy enforcement produces the inverse failure — A40910's naive fine-tuning for copyright awareness
causes **over-refusal** (direct), the false-positive analog on the guardrail side (cross-links the
copyright-policy thread).

**Implication.**
- **[V]** Before a mark gates an **attribution, takedown, or litigation** decision, measure both error
  directions: **cross-owner collision (false positive)** and **detection under adaptive removal (false
  negative)**; prefer schemes that expose a **thresholded p-value** (A40575, A40728).
- **[R]** Forgery/spoofing resistance is **unestablished** across the corpus (A38094, A40546, A41092,
  A40909) — an unqualified "this output is watermarked, therefore owned by X" carries **[R] known,
  unquantified** false-positive risk.
- **[C]/[P]** Watch the inverse (over-refusal) failure when hardening copyright policy (A40910):
  over-blocking drives operational bypass (precision is the enterprise metric, `worldview.md` §7).
- **Launch gate (hard):** do **not** launch an attribution claim on a mark whose **forgery/spoofing**
  and **cross-owner collision** rates are unmeasured (source §16); require both before the mark
  influences any adverse decision about a party.

## Thread 9 — Watermark removal & laundering (the corpus's demonstrated bypasses)

**Well-established.** The corpus contains **red-team demonstrations that hiding/encapsulation is not a
security boundary**, and they are the highest-confidence removal results:

- **A37429 (GSPure)** — a **white-box** attack that breaks three scene-hiding 3DGS watermarks
  (**GS-Hider, Splats-in-Splats, SecureGS**) by clustering and pruning low-contribution,
  viewpoint-inconsistent watermark Gaussians — author-reported **up to 16.34 dB watermark-PSNR
  reduction with <1 dB scene loss** (direct; Mip-NeRF360 only).
- **A39041 (box-free removal)** — a **black-box query-API** attack breaking two box-free image-to-image
  watermarks (referred to as VWu, VZhang) with author-reported **~100% removal success (PSNR up to
  34.69 dB)**, and it **enables watermark-free surrogate training** — removal *is* laundering here
  (direct).
- **A40728** documents prior EaaS watermarks laundered by a single attack family each (EmbMarker/
  WARDEN/EspeW by paraphrase; WET by dimension-perturbation) (direct; Thread 3).

The unifying mechanism (reviewer synthesis, source §6, §9): **a separable / "inactive" mark is a
removable mark.** A37429 (watermark Gaussians have low, viewpoint-inconsistent contribution →
clusterable) and A39041 (additive-separable mark + inducing the generator toward near-identity →
recoverable) reach this independently from different asset classes.

**Emerging.** *Laundering-via-regeneration/purification* and *surrogate distillation* as the general
attack shape — regeneration of generative-output watermarks is named as an open robustness problem
post-A37429/A39041 (source §17). Extraction-survival design (A39992, in-distribution coupling) is the
constructive counter (Thread 1).

**Contested / bounded.** The removal results are demonstrated against **other** schemes under the
bypasser's own evaluation (source §11). Whether these specific attacks generalize to marks *not* in
their test set is not established. Critically, **the corpus's own defenses are, with few exceptions
(A39992 adaptive; A40909 adversarial threat model), tested only non-adaptively** — so their resistance
to a *scheme-aware* remover is **unestablished** (source §11, reviewer synthesis).

**Where defenses fail.** Steganographic hiding in a distributed asset (A37429). Additive-separable
marks and box-free encapsulation (A39041). Single-family EaaS marks (A40728). Any watermark whose
removal robustness was only shown against fixed distortions inherits **[R] unknown** against an adaptive
remover.

**Implication.**
- **[R]** Assume **separable/encapsulated marks are removable** (A37429, A39041); architectures must
  **not** treat steganographic hiding as a security boundary (source §15).
- **[E]/[C]** Prefer marks that resist removal by construction — **in-distribution task-coupling**
  (A39992) — over hiding; and pair marks with **provenance registries and access control** so a
  laundered output is still traceable upstream (source §14).
- **[V]** Re-benchmark any watermark against **scheme-aware adaptive removal** before trust: the
  demonstrated bypasses all defeated prior schemes that had only non-adaptive evidence (A37429, A39041,
  A40728; source §16).
- **Launch gate:** a removal-robustness claim tested only against fixed distortions carries **[R]
  unknown** residual against adaptive laundering and surrogate distillation; require scheme-aware
  adaptive removal in the pre-ship suite, and never present a hiding-based watermark as a security
  boundary.

---

## Cross-thread reading — how the threads compound

The threads are not independent; the corpus's transferable value is where they **compose** (reviewer
synthesis):

- **Model extraction × watermark laundering** → the *same* query-API operation both steals the function
  and strips the mark (A39041 trains a watermark-free surrogate). Only **in-distribution task-coupling**
  (A39992) makes the mark survive; hiding does not (A37429). **[E]/[R]**
- **Weight theft × ownership verification × tamper resistance** → a white-box adversary unlearns a
  weight-embedded fingerprint *and* evades exact-match verification (A40909). The only corpus answer is
  **external secret + similarity/ECC + trusted verifier** — a single design that addresses all three
  threads at once. **[E]/[V]/[P]**
- **Watermarking × false-positive risk** → every watermark is non-adaptive evidence, yet forgery and
  cross-owner collision are unmeasured (A38094, A40546, A40892, A41092). A mark you can *forge* is a
  false-positive weapon, not just a weak positive. **[R]**
- **API imitation × verification-access** → grey-box log-prob detection (A37038, A40575) is the most
  deployable verification, but it dies on the **closed API** an imitator is most likely to expose —
  the coverage gap is structural. **[P]/[R]**
- **Copyright-policy channel (adjacent, most agent-relevant)** → A40910 (CopyGuard) shows an LVLM's
  refusal guardrail is bypassed when infringing content enters as **multimodal/RAG context**
  (author-reported **11/12 LVLMs fail**), embedded notices are ignored, and naive fine-tuning causes
  over-refusal (direct). This is the corpus's transferable **agent** pattern: enforce policy at
  **ingestion of retrieved/user-supplied context** (a tool-augmented gate — notice identifier → source
  verifier → query-risk analyzer/rewriter → status reminder), not at the surface prompt. **[P]/[V]**

## Consolidated launch-gate checklist (reviewer synthesis, grounded in the cards)

1. **Evidence-not-prevention gate (all threads).** Present every mark/fingerprint as **one
   probabilistic [E] evidence signal**, paired with access control, query monitoring, and a provenance
   registry — never as prevention (source §14; nearly every card). **[E]/[P]**
2. **Non-adaptive-scope gate (Threads 4, 9).** Scope every robustness claim to the exact non-adaptive
   attack catalog tested; a scheme with only fixed-distortion evidence carries **[R] unknown**
   adaptive-removal risk. Re-benchmark against scheme-aware adaptive attacks before trust (A37429,
   A39041, A40728). **[R]/[V]**
3. **Forgery/collision gate (Thread 8, hard).** Do not launch an attribution/takedown/litigation claim
   on a mark whose **forgery-spoofing** and **cross-owner collision** rates are unmeasured (A38094,
   A40546, A41092, A40909); prefer a thresholded **p-value** verifier (A40575, A40728). **[V]/[R]**
4. **External-secret + trusted-verifier gate (Threads 2, 6, 7).** For any model an adversary could
   obtain, bind ownership evidence to an **external secret**, verify by **similarity+ECC under a
   trusted verifier**, and reject exact-match verification (A40909). **[E]/[V]**
5. **Key-custody gate (Threads 4, 6, 7).** Treat every decode-time / encryption / external-secret key
   as a **governed credential** — custody, versioning, rotation (A40546, A40561, A40909, A41092).
   **[P]**
6. **Extraction-survival gate (Thread 1).** Anti-stealing marks must use **in-distribution
   task-coupling**, evaluated against adaptive + detection attacks (A39992 bar), not OOD triggers a
   stolen model forgets. **[E]/[C]**
7. **Verification-access gate (Threads 3, 6).** State the access posture (white-box / grey-box /
   passive) next to every ownership claim; grey-box detection is **[R] unestablished** on closed APIs
   (A37038, A40575); passive MIA is near-random at scale (A40575) and cannot stand alone. **[P]/[R]**
8. **Context-boundary policy gate (cross-thread, agent-relevant).** For agent/RAG systems, enforce
   copyright/safety policy at **ingestion of retrieved/user-supplied context** via a tool-augmented
   gate, not at the surface prompt; watch for over-refusal (A40910). **[P]/[V]**
9. **Production-scale gate (Thread 6).** Training-data provenance results validated at continued-
   pretraining scale (A40575: +5B tokens, continued-pretraining not from-scratch) require full-scale
   validation before assurance claims. **[R]**

---

*Closing evidence-integrity note.* Every metric in this chapter is reported as it appears in the source
synthesis's research cards, labeled author-reported where the card so labels it; several under-attack
tables were flagged truncated in the synthesis (A38094, A40910, A40921, A41092, A40851) and are
therefore not independently transcribed. No titles, authors, venues, datasets, or numbers were
invented; where a card recorded a value as absent, this chapter writes "not stated in paper" rather
than asserting one. Cross-paper judgments are marked *(reviewer synthesis)*; all other claims trace to
the cited paper id under its own evaluated threat model. Two source papers (A39623, A40030) were flagged
off-topic and carry no weight here. This chapter draws only on
`references/syntheses/Model-IP-Protection.md`; claims requiring the primary PDFs (e.g. exact fidelity/
bit-accuracy table cells recorded as "not stated in paper") are **[R] source-validation-pending**.
