# Pattern: Content Provenance

> **Scope of evidence.** Grounded in two AAAI-26 corpus syntheses: `Deepfake-Forgery-Detection` (13 papers) and
> `Model-IP-Protection` (22 papers). Paper ids (e.g. `A38060`, `A40909`) are the stable corpus ids from those
> syntheses' source maps. Every recommendation traces to at least one card.
>
> **Relationship to `signed-provenance.md`.** That sibling pattern specifies the *cryptographic-bind sub-control*
> — external secret + trusted verifier + similarity/ECC, deterministic verify-or-fail-closed. **This** pattern is
> the broader **multi-signal content-authenticity playbook**: how a Guardian agent decides, at the ingestion
> boundary, whether a piece of media/content is authentic, synthetic, or tampered, and where it came from, by
> **composing** passive detection, proactive forensics, watermarks, fingerprints, and (via signed-provenance)
> cryptographic credentials into **one fail-closed evidence signal**. The two overlap deliberately on `A40909`,
> `A40910`, `A37865`, `A37429`, `A39041`; where the crypto-bind mechanics matter, this pattern defers to
> `signed-provenance.md` rather than restating them.
>
> **Evidence-integrity conventions (non-negotiable).** Numeric values are **author-reported** unless labeled
> *reviewer synthesis*, and are **not independently verified**. Where a card was silent or truncated, values are
> written "not stated in paper". No absolutes ("secure", "authentic-proof", "unforgeable") are used; findings
> hold "under the evaluated (largely non-adaptive) threat model" and "against the tested attacks". *Direct paper
> finding* and *reviewer synthesis* are distinguished throughout.
>
> **The load-bearing calibration for this pattern.** Both syntheses classify their methods identically: they
> **"produce an *evidence signal an agent consumes*, not a control on the agent's own tool/skill/MCP surface"**
> (Deepfake §1) and are an **"*evidence-and-attribution* discipline, not an agent-execution-security one"** that
> "does not by itself prevent misuse" (Model-IP §1). Therefore content provenance is a **detection/attribution
> layer, never a prevention gate**. Two replicated absences bound every claim: **adaptive / anti-forensic
> robustness is essentially unmeasured** across the entire Deepfake corpus (§17, the single largest gap) and
> near-universally untested in Model-IP except `A40909` and `A39992` (§11); and **cross-generator generalization
> is a decaying asset** — detectors trained on one generator family collapse on unseen ones (Deepfake §9). Treat
> every accuracy number as a non-adaptive, time-bounded upper bound that **requires production validation**.

---

## Problem addressed

A Guardian agent (or a governance layer, a downstream model, a human reviewer) ingests content it did not create —
an uploaded image, a retrieved document, an audio clip, a video segment, a model output — and must answer three
questions before acting on it: **is this authentic or synthetic? has it been tampered with? where did it come
from?** Getting this wrong feeds forged or manipulated media into a decision the agent then executes.

The corpus establishes that **no single provenance signal answers these questions authoritatively**:

- **Passive synthetic-media detectors are probabilistic evidence, never a gate.** The Deepfake synthesis's
  headline product implication is to "use any single detector as **one probabilistic evidence signal, never as
  an authoritative gate**" (§14). Detection generalization is the corpus's central, replicated failure mode:
  single-source detectors overfit generator-specific surface artifacts and collapse on unseen generators
  (Deepfake §9, demonstrated across `A37071`, `A37334`, `A37421`, `A37473`, `A37553`, `A40886`, `A40907`,
  `A41234`). `A40907` quantifies it starkly: single-type audio detectors drop to **near-chance EER ~30–50%** on
  unseen types versus **3.58%** average EER for the all-type co-trained model (direct paper finding). Averaged
  SOTA hides this: `A37071` reports GenImage SOTA yet only **~57–58%** on the harder in-the-wild Chameleon
  benchmark (direct paper finding).
- **Machine-generated forensic explanations are empirically unreliable on their own.** `A38060` (ESIDE) measured
  **up to 67.4%** of MLLM-identified forensic flaws as *incorrect* (direct paper finding); `A37421` documents
  "overthinking" on easy fakes. A fluent rationale is not a correct one.
- **Embedded watermarks are removable when the mark is separable.** `A37429` (GSPure) strips three 3D-Gaussian-
  Splatting watermarks white-box (author-reported up to **16.34 dB** watermark-PSNR reduction, **<1 dB** scene
  loss); `A39041` removes two box-free image-to-image watermarks with author-reported **~100%** removal. The
  replicated lesson: **"a separable / 'inactive' mark is a removable mark"** — hiding is not a security boundary
  (Model-IP §6, reviewer synthesis over two red-team papers).
- **Provenance/policy checks placed at the surface prompt are bypassed via the context channel.** `A40910`
  (CopyGuard): refusal behavior that blocks direct requests does not generalize when infringing content arrives
  as multimodal/RAG context — **11/12 LVLMs fail** (author-reported).

**Content provenance** is the control that turns these weak, individually-defeatable signals into a usable
decision: a **fail-closed, deny-by-default evidence layer** that runs at the **ingestion boundary**, composes
multiple provenance signals (cryptographic credential where available, watermark, passive detector, fingerprint,
proactive tamper-tripwire), **gates machine explanations before surfacing them**, **surfaces uncertainty rather
than a bare verdict**, and **defers to human review** on ambiguity. Its honest scope, inherited from both
corpora: it establishes **attributable, tamper-evident evidence for a trust decision** — it does **not** prevent
misuse, and its accuracy **decays as generators evolve**.

## Applicable assets and attack surfaces

- **Ingested media the agent will act on** — image, audio, text, video/audio-visual, tabular. This is the primary
  surface: content the agent did not create and must not trust on presentation alone (detection targets across
  `A37071`, `A37421`, `A37473`, `A37553`, `A37865`, `A38060`, `A40886`, `A41234` (image); `A37334`, `A37473`,
  `A37945` (face/presentation); `A40907` (audio); `A40928` (audio-visual)).
- **The retrieval / RAG / upload ingestion boundary** — where untrusted external content enters agent context.
  `A40910` shows the provenance/policy check must sit **here, not at the surface prompt** (11/12 LVLMs fail via
  the context channel). Embedding APIs are part of this surface — `A40728` (RegionMarker) marks the embedding
  API because embeddings feed RAG and agent memory (Model-IP §14 supply-chain control).
- **Identity / authentication surfaces** — face anti-spoofing / presentation-attack detection (`A37945`
  FaceShield: 12 unified spoof types — print, replay, 3D/paper masks, glasses, makeup) is a content-provenance
  gate on *who* is presenting, with escalation to human review (Deepfake §14).
- **Owner-controlled assets published into a hostile channel** — the proactive-forensics surface. `A37865`
  (Blank Canvas) applies an owner-side protective perturbation *before circulation* so later edits show up as
  anomalous segmentation; this is the corpus's closest analogue to an attestation/tamper-tripwire control.
- **Model outputs the agent emits** — decode-time watermarking tags agent-generated text for downstream
  attribution (`A40546`, `A41092`), a provenance signal *this* agent produces for the *next* consumer.
- **The detector / verifier itself as a stateful, versioned asset.** Prototype banks (`A37473`, capacity 64/class,
  decay γ=0.99) and noise-residual models (`A41234`) are governed surfaces with drift/poisoning risk (Deepfake
  §15). Proactive-forensics verification is tied to a **specific SAM version** (`A37865`) — a verifier-model
  change can silently break tamper localization.
- **The provenance decision record** — the evidence emitted into a registry/audit for downstream reliance and
  legal/governance action (Model-IP §14; see `tamper-evident-traces.md` / `signed-provenance.md`).

## Threat model

- **Primary (non-adaptive, the corpus's actual coverage): distribution shift as the adversary.** 12 of 13
  Deepfake papers explicitly adopt a non-adaptive threat model where the "adversary" is the space of generators —
  unseen models, unseen forgery types, unseen datasets — and robustness is measured as *generalization*, not
  adversarial evasion (Deepfake §3). Adversary knowledge is effectively black-box on the detector. This is what
  the evidence covers; read every detection number accordingly.
- **Watermark/credential stripping (Model-IP).** Removal/purification of an embedded mark — white-box (`A37429`,
  up to 16.34 dB reduction) and black-box (`A39041`, ~100% removal); regeneration/re-diffusion stripping, where
  placement in the generative trajectory is a robustness lever (`A38094`: early-latent marks survive regeneration,
  late marks survive geometric transforms); model extraction dropping the mark (`A39992`: OOD triggers are
  forgotten by stolen models, only in-distribution task-coupled marks survive).
- **Context-channel bypass (most agent-relevant).** Provenance/guardrail bypass through retrieved or uploaded
  content — `A40910`, 11/12 LVLMs fail when content arrives as multimodal/RAG context; embedded notices ignored.
- **Explanation-trust exploitation.** An adversary (or merely a hard input) inducing a confident-but-wrong
  machine rationale — `A38060`'s ≤67.4% incorrect-flaw finding and `A37421`'s "overthinking" show the rationale
  channel is itself unreliable; reviewer synthesis (Deepfake §11) notes `A37421`'s confidence-gated adaptive
  compute "could be gamed by an adversary crafting high-confidence-but-wrong impressions" (untested).
- **Presentation / physical-world spoofing.** `A37945` targets 12 physical presentation-attack types; `A41525`
  (Breakable Machine) is the corpus's *only* adaptive, physical-world attacker — a human iteratively spoofing a
  MobileNet-V2 classifier via CAM saliency and training-data inspection — but it is an AI-literacy artifact, not
  a defense or a robustness test of any method here.
- **The one adaptive model to design against (Model-IP).** `A40909` (iSeal): adversary **controls inference
  end-to-end**, has **white-box weights**, performs **collusion-based fingerprint unlearning**, and applies
  **output-manipulation to evade exact match** — the most adversarially realistic threat model in either corpus.
- **Environmental (non-adversarial) corruption modeled but not as an attacker.** OSN JPEG compression and
  Gaussian noise (`A37553`, `A37421`) are treated as distribution shift, not anti-forensics.
- **Explicitly out of scope for the corpus evidence — the implementer MUST add these (replicated absences):**
  - *Adaptive / anti-forensic attacks* optimizing against the specific detector — **unmeasured across the entire
    Deepfake corpus** (§17) and untested in Model-IP except `A40909`, `A39992`. This is the defining gap.
  - *Watermark/credential forgery or owner-mark spoofing* to manufacture a false origin or frame a victim —
    "repeatedly named and almost never evaluated" (Model-IP §4, §17: `A38094`, `A40546`, `A41092`, partially
    `A40909`).
  - *False-attribution / cross-owner collision at scale* — rarely quantified (Model-IP §12: `A38094`, `A40892`,
    `A40901`, `A40921`, `A41092`).
- **Trust-boundary assumptions to reject.** (1) That a fluent verdict/explanation implies a correct one
  (`A38060`). (2) That presence of a mark implies integrity — separable marks are removable (`A37429`,
  `A39041`). (3) That absence of a provenance signal is benign — fail closed on absence. (4) That a surface-prompt
  check covers the ingestion channel (`A40910`). (5) That a detector's accuracy is stable over time — it decays
  as new generators appear (`A40886`'s fixed GAN/DM K=2 assumption is a named bias that new families like VAR can
  break; Deepfake §15, §17).

## Control mechanism

A **deterministic, fail-closed provenance decision at the ingestion boundary**, composing multiple signals and
gating machine reasoning — the agent trusts content only when provenance clears, and defers to human review on
ambiguity:

1. **Intercept at ingestion, not at the surface prompt.** Every externally-sourced artifact (upload, RAG
   retrieval, embedding-API result) passes a provenance gate *before* it enters agent context — `A40910`'s
   transferable pattern: a tool-augmented pipeline (notice identifier → source verifier → query-risk
   analyzer/rewriter → status reminder). Surface-prompt checks miss the actual bypass channel.
2. **Check the strongest available signal first: a cryptographic content credential.** If a signed provenance
   credential is present, verify it deterministically (external secret, trusted verifier, similarity + ECC, *not*
   exact match) — defer to `signed-provenance.md` / `A40909`. A verified credential is the highest-confidence
   signal; absence or failure does **not** end the decision (fail closed, continue to weaker signals).
3. **Check embedded/intrinsic marks where the asset class supports them.** Watermark recovery (`A38094`, `A40892`,
   `A40901`, `A40921`, `A40561`, `A40546`, `A41092`), intrinsic fingerprint/attribution for already-published
   content (`A40843` StyleSentinel SVDD hypersphere; `A40851` OFA passive attribution; `A40886` GAN-vs-DM
   architecture clustering). Treat a *recovered* mark as evidence and a *missing* mark as **removed-or-absent,
   never as authentic** (corollary of `A37429`/`A39041`).
4. **Run passive detection as a probabilistic signal with a verifier loop.** Use the reusable
   **fast-verdict + confidence-gated reflective escalation** shape: a cheap proposer, then a deeper reflective
   verifier only when confidence is low (`A37421` adaptive Heuristic-to-Analytic reasoning; `A38060` metric-guided
   Top-K refinement). Prefer real-only / generalization-oriented detectors (`A41234` real-only with feature-space
   pseudo-negatives; `A40886`) that do not require enumerating generators. Output a **calibrated confidence, not
   a bare verdict**.
5. **Gate every machine explanation before surfacing it.** Anchor rationales to a verifiable taxonomy and
   quantitative scoring; never present an MLLM's fluent explanation as ground truth (`A38060` ≤67.4% incorrect
   flaws; consensus across `A38060`, `A37421`, `A37945`). Keep a human in the loop before consequential action.
6. **Compose and decide deterministically, fail-closed, outside the model's control plane.** Aggregate the
   signals; on a verified credential admit-as-evidence; on ambiguity, disagreement, low confidence, or any
   absent/invalid signal → **deny / flag / defer to human**. Never treat unverified content as authentic.
7. **Emit the decision as evidence into a provenance registry**, paired with access control and monitoring —
   *evidence, not prevention* (Model-IP §14). Surface uncertainty (confidence, impression-vs-final disagreement,
   localization masks) downstream (Deepfake §14).

## Preconditions and trust assumptions

- **This is a layer, not the sole control, and not a prevention mechanism.** Every deployment-implications
  section in both corpora ends here: combine content provenance with access control, query monitoring, provenance
  registries, and human review; do not rely on it to stop misuse (Model-IP §14; Deepfake §14). If the goal is to
  *block* an action, use a permission gate / human-approval control (`policy-permission-gates.md`,
  `human-approval-consequential-actions.md`), not provenance.
- **Detection accuracy is a decaying asset.** Generalization is empirical and expires as generators evolve
  (Deepfake §15, §17; `A40886`'s K=2 bias). Preconditions: a scheduled re-benchmarking cadence against the
  *hardest in-the-wild sets* (not averaged SOTA — `A37071`'s ~57–58% Chameleon vs GenImage SOTA), and detectors
  built as **pluggable, replaceable evidence producers**, not fixed oracles.
- **The verifier/detector model and any key are pinned, versioned, governed dependencies.** `A37865` ties tamper
  localization to a specific SAM version — a verifier-model change can silently break verification; treat it as a
  breaking change. Cryptographic-credential key custody follows `signed-provenance.md` (`A40909`, `A40561`
  ChaCha20, `A40546`, `A41092`).
- **Stateful detector components have their own governance.** Prototype banks (`A37473`, capacity 64/class, decay
  γ=0.99) and noise-residual models (`A41234`) carry drift and poisoning risk that must be **bounded, logged, and
  monitored** (Deepfake §15, §16).
- **Machine explanations are untrusted until gated.** Rationale faithfulness is empirically unverified (`A38060`
  ≤67.4% incorrect); anchor to a taxonomy + quantitative score and keep human-in-the-loop before action (Deepfake
  §14).
- **The right control depends on whether you control creation.** For *owner-controlled, pre-publication* assets,
  proactive forensics (`A37865`) or signing (`signed-provenance.md`) apply. For *already-published / third-party*
  content, only *passive detection* and *intrinsic fingerprinting* (`A40843`, `A40851`) apply — you cannot assume
  an embedded mark.
- **Cross-modality is siloed.** Image, audio, and audio-visual detectors are separate (Deepfake §2, reviewer
  synthesis); a unified provenance layer must **compose per-modality models**, not assume one universal detector.
- **All robustness is non-adaptive unless proven otherwise.** No absolutes; scope every claim to the tested,
  non-adaptive threat model, and require a forgery + adaptive red-team before operational reliance.

## System architecture

Provenance is evaluated at every ingestion boundary the content crosses; the decision runs outside the model's
control plane and emits evidence, never a prevention verdict.

```
  EXTERNAL / UNTRUSTED CONTENT                         (upload, RAG retrieval, embedding-API result,
  ┌───────────────────────────┐                        presented face, model output)
  │ image / audio / text /    │                                     │
  │ video / face / embedding  │                                     v
  └───────────────────────────┘         ┌──────────────────────────────────────────────────────┐
                                         │  INGESTION / PROVENANCE GATE   ← env-side, NOT the     │
                                         │  (A40910: notice identifier →   surface prompt         │
                                         │   source verifier → query-risk                         │
                                         │   analyzer/rewriter → reminder)                        │
                                         └──────────────────────────────────────────────────────┘
                                                              │
             ┌────────────────────────────────────────────────┼────────────────────────────────────────┐
             v (signal 1)                     v (signal 2)     v (signal 3)              v (signal 4)
   ┌───────────────────────┐      ┌──────────────────────┐  ┌────────────────────┐  ┌────────────────────┐
   │ Crypto credential     │      │ Watermark / intrinsic│  │ Passive detector   │  │ Proactive tripwire │
   │ (signed-provenance.md;│      │ fingerprint          │  │ w/ verifier loop   │  │ (owner assets)     │
   │  A40909 sim+ECC,      │      │ (A38094,A40843,A40851│  │ (A37421 fast→deep, │  │ A37865 SAM tamper- │
   │  NOT exact match)     │      │  A40886 attribution) │  │  A38060, A41234,   │  │ localization       │
   │                       │      │  recovered=evidence, │  │  A40907)           │  │ (SAM version PINNED)│
   │                       │      │  missing=NOT authentic│ │  → CONFIDENCE      │  │                    │
   └───────────────────────┘      └──────────────────────┘  └────────────────────┘  └────────────────────┘
             │                              │                        │                        │
             └──────────────────────────────┴───────────┬────────────┴────────────────────────┘
                                                         v
                                     ┌───────────────────────────────────────┐
                                     │ EXPLANATION GATE (A38060 ≤67.4% wrong; │  never surface a
                                     │  anchor to taxonomy + quant score)     │  fluent rationale as truth
                                     └───────────────────────────────────────┘
                                                         │
                                     ┌───────────────────────────────────────┐
                                     │ COMPOSE + DECIDE  (deterministic,      │  outside model control plane
                                     │  fail-closed, surface uncertainty)     │
                                     └───────────────────────────────────────┘
                                                         │
              verified credential                ambiguous / low-conf /            absent / invalid /
              or cleared signals                  signal disagreement               removed mark
                     │                                   │                                  │
                     v (admit as EVIDENCE)               v (defer)                          v (FAIL CLOSED)
        provenance registry + audit          human review / quarantine        deny / flag  (deny-by-default)
        (evidence, NOT prevention)           (A40910 status-reminder path)
```

Overlays: (a) for the **RAG/embedding supply chain**, mark the embedding API so agent memory carries provenance
(`A40728`); (b) for **model-asset marks**, design for extraction survival via in-distribution task-coupling, not
an OOD trigger set a stolen model forgets (`A39992`); (c) run detectors on a **frozen-backbone + lightweight-
adapter** architecture (CLIP/ViT/SSL front-ends with LoRA/prompt tuning — Deepfake §13) so they stay cheap to
retrain and swap as generators evolve.

## Recommended implementation pattern

Deterministic, fail-closed, least-privilege, composition-of-signals:

- **Enforce at ingestion, externalized into tools.** Put the check where untrusted content enters (RAG upload,
  embedding result), not on the surface prompt; externalize into a verifier + risk-analyzer + query-rewrite
  pipeline (`A40910`).
- **Compose signals in strength order; fail closed on each miss.** Cryptographic credential (strongest, defer to
  `signed-provenance.md` / `A40909`) → watermark/intrinsic fingerprint (`A38094`, `A40843`, `A40851`, `A40886`) →
  passive detector (`A41234`, `A40886`, `A40907`, verifier loop) → proactive tripwire for owner assets
  (`A37865`). A missing or stripped signal is **absent, not authentic**.
- **Use the fast-verdict + confidence-gated reflective verifier loop.** Cheap check first, deep check only on low
  confidence (`A37421`, `A38060`) — the reusable escalation shape for a Guardian verifier (Deepfake §15).
- **Prefer generalization-oriented, real-only detectors** that do not require enumerating generators (`A41234`
  real-only + feature-space pseudo-negatives, evaluated across GAN/diffusion/VAR + a medical distribution shift;
  `A40886` unsupervised architecture clustering) — the future-proofing paradigm for a shifting threat surface.
- **Co-train across types/generators where possible.** `A40907` shows all-type co-training drops audio EER to
  3.58% versus near-chance ~30–50% for single-type — treat single-source detectors as fragile by default.
- **Gate machine explanations against a taxonomy + quantitative score; keep human-in-the-loop.** Never surface an
  MLLM rationale as ground truth (`A38060` ≤67.4% incorrect; `A37421`, `A37945`).
- **Output calibrated confidence and surface disagreement, not a bare verdict** — log impression-vs-final
  disagreement and localization masks so downstream reliance is calibrated (Deepfake §14).
- **For owner-controlled assets, apply proactive forensics before circulation** (`A37865` tamper-tripwire), and
  **pin the verifier model version** (its SAM dependency is a governed dependency).
- **For content the agent emits, tag it** (decode-time watermark `A40546`, `A41092`) so the next consumer has a
  provenance signal — requires serving-path control and key custody (treat key as a credential).
- **Handle compression/corruption without destroying signal** — orthogonalize the nuisance to the decision axis
  rather than deleting it (`A37553`'s transferable design principle; ~75% mean under OSN compression).
- **Present the result as one evidence signal**, combined with access control, monitoring, and (for high-stakes
  synthetic-media decisions) cryptographic provenance + watermarking + human review (Deepfake §14 explicitly:
  "combine detection with cryptographic provenance (C2PA-style), watermarking, and human review").

## Incorrect or fragile implementation patterns

- **Using a single passive detector as an authoritative gate.** It is probabilistic evidence; generalization
  collapses on unseen generators (`A40907` near-chance on unseen types; `A37071` ~57–58% on Chameleon) — Deepfake
  §14 forbids it explicitly.
- **Trusting a machine-generated forensic explanation as ground truth** (`A38060` ≤67.4% incorrect flaws;
  `A37421` overthinking). Surfacing an ungated rationale to a user or an action.
- **Treating a missing watermark/credential as "authentic".** Separable marks are removable (`A37429`,
  `A39041`); a stripped mark yields an *unsigned/unmarked* artifact that must fail closed, not pass.
- **Checking provenance only at the surface prompt.** Misses the real bypass channel (`A40910`, 11/12 LVLMs fail
  via context).
- **Trusting averaged SOTA accuracy.** It masks near-chance behavior on the hardest in-the-wild sets (Deepfake
  §10; `A37071` Chameleon).
- **Assuming a detector's accuracy is stable over time.** Generalization decays as new generator families appear
  (`A40886` fixed K=2 bias broken by VAR; Deepfake §17).
- **Treating steganographic hiding as the security boundary** (`A37429`, `A39041`).
- **Expecting an OOD watermark trigger to survive model extraction** (`A39992`: forgotten by the stolen model).
- **Using passive membership inference as training-data provenance at scale** (`A40575`: prior MIA ROC-AUC
  ~0.50–0.56, near-random at +5B tokens).
- **Leaving stateful detector state (prototype bank, noise-residual model) ungoverned** (`A37473`, `A41234`
  drift/poisoning risk).
- **Leaving the verifier/detector model un-pinned** (`A37865`: a version change silently breaks verification).
- **Claiming adaptive-adversary or forgery robustness** — untested across the corpus (Deepfake §17; Model-IP §11).

## Verification strategy

- **Prove the decision is deterministic and fail-closed.** For every content class, assert that absent, invalid,
  stripped, and ambiguous signals produce deny/flag/defer *regardless of the model's own output*, and that the
  decision runs outside the model's control plane (`A40910` reject path; corollary of the removal red-team).
- **Test the ingestion channel, not just the prompt.** Inject provenance-bearing and adversarial content via
  RAG/upload and confirm the gate actually checks it (`A40910`).
- **Benchmark against the hardest in-the-wild sets, not averaged SOTA.** `A37071`'s Chameleon ~57–58% versus its
  GenImage SOTA is the cautionary case; track worst-case, per-generator, per-type performance (Deepfake §16).
- **Test cross-generator / cross-type / cross-dataset generalization explicitly** — the corpus's central failure
  mode (Deepfake §9). Report per-generator breakdowns; `A40907`'s single-type ~30–50% vs all-type 3.58% is the
  template.
- **Test environmental corruption robustness** — compression, resize, noise (`A37553` OSN compression; `A37421`
  JPEG/Gaussian).
- **Run the removal / purification red-team** (`A37429`, `A39041`) and confirm a stripped-mark artifact fails
  closed as unmarked, not as authentic.
- **Gate-check explanations against ground truth, not fluency proxies.** Do not accept BLEU/ROUGE/text-image
  similarity as correctness — they measure overlap, not causal fidelity (Deepfake §12); `A38060`'s ≤67.4%
  incorrect-flaw measurement is the reason.
- **Validate stateful-component governance** — bounded prototype turnover / noise-residual updates, logged and
  monitored (`A37473`, `A41234`).
- **Verify the verifier-version change path** is controlled and flagged, not silent (`A37865`).
- **For cryptographic-credential and model-asset marks, follow `signed-provenance.md`'s verification suite**
  (forgery evaluation, cross-owner collision, extraction survival, similarity+ECC boundary; `A40909`, `A39992`,
  `A40728`, `A40575`).
- **Independent validation on the target stack** — most results are single-paper, single-model-family, or
  truncated (`A38094` SD/DDIM; `A40892` SD v2.1; `A37429` Mip-NeRF360; `A38060` trains one model per GenImage
  subset).

## Metrics and thresholds

Author-reported baselines are labeled; **target values are engineering targets requiring production validation,
not paper-derived guarantees.** Do not publish a single-number "authentic" threshold.

- **Cross-generator / cross-type generalization gap** — the load-bearing metric. `A40907`: single-type audio EER
  ~30–50% (near chance) vs **3.58%** all-type co-trained (direct paper finding). Measure the gap on *your* unseen
  generators, not on the training family.
- **Worst-case in-the-wild accuracy, not averaged SOTA.** `A37071`: GenImage SOTA vs **~57–58%** on Chameleon
  (direct paper finding); `A37421`: **~78.46%** OOD accuracy; `A38060`: **98.91%** original / **95.89%** hard
  subset (direct paper findings; per-GenImage-subset training caveat). Track the hard-subset number.
- **Explanation-error rate** — `A38060`: **up to 67.4%** of MLLM flaws incorrect (direct paper finding). *Target:
  gate so this never reaches an action ungated*; treat any ungated-rationale path as unmeasured risk.
- **Face-presentation metrics** — `A37945`: intra-dataset ACC **99.41**, Replay-Attack **cross-dataset HTER
  20.07** (direct paper findings) — the cross-dataset HTER is the operationally honest number.
- **Detection AUC under attribution** — `A40886`: GenImage average AUC **0.9882** (5 datasets, 13 baselines,
  direct paper finding); note the fixed K=2 GAN/DM assumption as a named bias.
- **Removal robustness (offensive baselines)** — watermark-PSNR reduction (`A37429` up to **16.34 dB**, <1 dB
  scene loss); removal success (`A39041` **~100%**) — use to size how easily an embedded mark is stripped in your
  setting; the answer motivates fail-closed handling of the resulting unmarked artifact.
- **Context-channel bypass rate** — `A40910`: **11/12** LVLMs fail without the ingestion gate (direct paper
  finding) — the baseline the gate must beat.
- **Membership-inference near-random baseline** — `A40575`: prior MIA ROC-AUC **~0.50–0.56** at +5B tokens (the
  floor to beat for training-data provenance).
- **Forged / cross-owner-collision accept rate** — *target near 0*, **but untested in the corpus** (Model-IP §12,
  §17); a "0" here is a target, not a demonstrated property.
- **Localization** — tamper masks (`A37865`), temporal AV boundaries (`A40928`); specific numeric metrics **not
  stated in paper** in the reviewed text.
- Headline numbers were **not stated in paper** / truncated for `A37334`, `A37865`, parts of `A41234`, and most
  Model-IP watermark fidelity/bit-accuracy tables — do not invent them.

## Test cases

1. **Unseen-generator content → detector confidence drops; decision defers, not accepts** (`A40907`, `A37071`
   generalization collapse).
2. **Hard in-the-wild input where averaged SOTA masks near-chance behavior → worst-case path exercised** (`A37071`
   Chameleon).
3. **Fluent-but-wrong machine explanation → explanation gate blocks it from the action** (`A38060` ≤67.4%
   incorrect).
4. **Stripped / removed watermark → artifact treated as unmarked and fails closed, not authentic** (`A37429`,
   `A39041`).
5. **Provenance-bearing content injected via RAG/upload → gate checks it at ingestion, not the surface prompt**
   (`A40910`).
6. **Environmental corruption within budget (OSN compression, resize, noise) → detection holds or defers, does
   not silently flip** (`A37553`, `A37421`).
7. **Face presentation attack (print/replay/mask/glasses/makeup) → detected or escalated to human** (`A37945`,
   12 types).
8. **Owner-asset tamper after proactive protection → localized as anomalous; verifier version pinned** (`A37865`).
9. **Signal disagreement (credential says A, detector says B) → surface uncertainty and defer, do not collapse to
   a verdict** (Deepfake §14).
10. **Cryptographic-credential path** — absent/invalid/forged/benign-transform cases per `signed-provenance.md`
    (`A40909`).
11. **Cross-owner collision** — distinct owners/keys produce no false cross-attribution (`A38094`, `A40892`,
    `A40901`, `A40921`, `A41092`) — *flag: untested in corpus*.
12. **Model-extraction survival** — a model-asset mark survives distillation via in-distribution coupling
    (`A39992`).

## Adaptive adversarial tests

The single largest gap in the Deepfake corpus is the near-total absence of adaptive / anti-forensic evaluation
(§17), and in Model-IP adaptive+forgery robustness is untested except `A40909`/`A39992` (§11). The implementer
must add what the papers did not — and must label all pre-adaptive results as "against the tested attacks under
the evaluated non-adaptive threat model":

- **Adaptive anti-forensics.** An attacker optimizing perturbations against *your specific detector* to suppress
  its discriminative signal — e.g. against `A37071`'s inter-branch discrepancy, `A37473`'s prototype bank, or
  `A41234`'s noise-residual features (all reviewer-noted untested blind spots, Deepfake §11). Use `A41525`'s
  iterative-spoofing methodology as a conceptual template (adapted from its physical-world MobileNet-V2 attack).
- **Explanation-gaming.** Craft high-confidence-but-wrong inputs to defeat `A37421`'s confidence-gated adaptive
  compute (reviewer-flagged as a plausible untested bypass, Deepfake §11).
- **Adaptive watermark removal / purification** beyond fixed transforms — scheme-aware stripping, denoising,
  recompression, regeneration (`A37429`, `A39041`, `A38094` demonstrate single non-adaptive removals; adapt them;
  `A37865`'s protective-perturbation survivability is explicitly untested).
- **Owner-mark / credential forgery** to manufacture a false origin or frame a victim — the corpus's most-named,
  least-tested attack (Model-IP §17: `A38094`, `A40546`, `A41092`, `A40909` partial). Treat a suite that omits
  this as *no coverage*.
- **Adaptive context-channel bypass** with obfuscated or split payloads — `A40910`'s CopyGuard is *not* stress-
  tested against these (Model-IP §17).
- **Emulate `A40909`'s adversary** for the cryptographic-credential path (white-box weights, collusion unlearning,
  output-manipulation to evade exact match).
- **Adaptive extraction** using `A39992`'s adaptive + detection-attack methodology.
- **Poisoning of stateful detector state** — prototype-bank / noise-residual poisoning via crafted inputs
  (reviewer-noted, `A37473`, `A41234`).

## Telemetry requirements

- **Append-only provenance-decision audit** — ordered `(artifact hash, per-signal results, composed decision,
  confidence, detector/verifier model + version, key id where applicable)` records for forensic replay (reviewer
  synthesis; mirrors the immutable-audit discipline in `tamper-evident-traces.md`).
- **Confidence and disagreement, not just verdicts** — log detector confidence, impression-vs-final disagreement,
  and cross-signal disagreement so downstream reliance is calibrated (Deepfake §14, §16).
- **Localization artifacts** — tamper masks (`A37865`), temporal AV boundaries (`A40928`) attached to the record.
- **Generalization-drift monitoring** — OOD accuracy / EER over time as new generators appear; detection accuracy
  is a decaying asset requiring scheduled re-evaluation (Deepfake §16).
- **Detector/verifier model + version as a governed dependency** — log it so a version change is visible, not
  silent (`A37865`).
- **Stateful-component telemetry** — prototype turnover, noise-residual update events, bounded and monitored for
  drift/poisoning (`A37473`, `A41234`).
- **Ingestion-gate outcomes** — what was verified, failed, rewritten, or deferred at the context boundary
  (`A40910`).
- **Explanation-gate outcomes** — which rationales were surfaced vs blocked, and against what taxonomy/score
  (`A38060`).
- **Key usage / rotation / revocation** for any credential or decode-time watermark path (defer to
  `signed-provenance.md`; `A40561`, `A40546`, `A41092`, `A40909`).
- **Registry writes for every attribution decision**, so downstream reliance and any legal/governance action is
  auditable (Model-IP §14).

## Failure handling

- **Fail closed.** On absent, invalid, unverifiable, stripped, or low-confidence signals, verifier error, or
  timeout → **deny / flag / defer to human**; never fall through to "authentic" (deny-by-default; `A40910` reject
  path; corollary of the removal red-team).
- **Defer to human review as a first-class action** for out-of-distribution, ambiguous, or signal-disagreement
  cases (`A40910` status-reminder / query-rewrite path; Deepfake §14 human-in-the-loop before action).
- **Surface uncertainty, do not collapse it to a verdict** — return confidence and disagreement, especially when
  averaged accuracy could mask near-chance behavior on a hard input (Deepfake §14).
- **Never surface an ungated machine explanation as ground truth** (`A38060`).
- **On generalization drift** (rising OOD error as a new generator appears), lower the auto-accept threshold and
  route more to human review until the detector is re-benchmarked/retrained (Deepfake §16, reviewer synthesis).
- **Assume residual harm and keep compensating controls active** — content provenance is evidence, not
  prevention; pair with access control, permission gates, and monitoring (Model-IP §14; Deepfake §14).

## Rollback and containment

- **Detector/verifier model is pinned and its rollout staged** so a version change is a controlled migration, not
  a silent break (`A37865`).
- **Swap the detector as a pluggable evidence producer** when a new generator family degrades it — the frozen-
  backbone + lightweight-adapter architecture keeps retrain/swap cheap (Deepfake §13, §15). Roll back to the
  prior detector version if a swap regresses on the hard-set benchmark.
- **Bound, log, and be able to reset stateful detector state** — prototype banks / noise-residual models can be
  quarantined and rebuilt if drift or poisoning is detected (`A37473`, `A41234`).
- **Quarantine artifacts that fail or are deferred by provenance** rather than silently dropping or admitting
  them; the registry enables re-flagging on a later signal or a revoked credential.
- **For the cryptographic-credential path, key rotation/revocation is the containment lever** — defer to
  `signed-provenance.md`; a compromised signing key produces valid credentials until revoked (`A40909`, `A40561`,
  `A40546`, `A41092`).
- **Residual containment gap:** adaptive removal (`A37429`, `A39041`) and generalization decay reduce, they do not
  eliminate, the reliability of any embedded/passive component — containment lowers blast radius, it does not
  restore a guarantee (reviewer synthesis).

## Known bypasses

Demonstrated (within papers, mostly under non-adaptive threat models) and reviewer-identified:

- **Cross-generator generalization collapse** — single-source detectors near-chance on unseen types (`A40907`
  ~30–50% EER; `A37071` ~57–58% Chameleon).
- **Averaged-SOTA masking of near-chance behavior** on the hardest in-the-wild sets (Deepfake §10).
- **Unreliable machine explanations** — `A38060` (≤67.4% incorrect flaws); `A37421` overthinking.
- **Watermark removal / purification** — `A37429` (three 3DGS schemes, white-box, up to 16.34 dB reduction),
  `A39041` (two schemes, black-box, ~100% removal). Steganographic hiding is **not** a boundary.
- **Regeneration stripping** — `A38094` (placement-dependent survival; the wrong placement is stripped by the
  matching transform).
- **Context-channel bypass** — `A40910` (11/12 LVLMs fail via multimodal/RAG context; embedded notices ignored).
- **Membership-inference collapse at scale** — `A40575` (prior MIA ROC-AUC ~0.50–0.56, near-random).
- **Physical-world classifier spoofing** — `A41525` (adaptive human spoofing of MobileNet-V2 via CAM saliency);
  the only demonstrated adaptive attack in the Deepfake corpus, though against a teaching classifier.
- **Reviewer-identified untested bypass surfaces (the shared blind spot):** `A37865` protective-perturbation
  stripping / SAM-version drift; `A37473`/`A41234` prototype-bank / noise-residual poisoning under denoising/
  recompression; `A37421` explanation-gaming; `A37071` no evaluation against discrepancy-suppressing post-
  processing (Deepfake §11).
- **Forgery / owner-mark spoofing** — largely **untested**; the biggest unquantified bypass class (Model-IP §17).
- **Adaptive, scheme-aware / anti-forensic attackers are essentially untested** against these controls except
  `A40909` and `A39992` — a replicated absence across both syntheses and the largest unquantified bypass surface.

## Residual risks

- **Adaptive / anti-forensic robustness is unestablished** — the single largest gap in the Deepfake corpus (§17);
  untested in Model-IP except `A40909`/`A39992`. Every detection number is a non-adaptive upper bound.
- **Content provenance is evidence, not prevention** — it supports a trust decision, attribution, and governance/
  legal action; it does not stop misuse (Model-IP §14; Deepfake §14).
- **Detection accuracy decays over time** — generalization to genuinely new generator paradigms (VAR/
  autoregressive beyond GAN/DM) is time-bounded (`A40886`, `A41234`); the control expires without re-benchmarking.
- **Machine-explanation faithfulness is unverified** — fluency ≠ causal correctness (`A38060` ≤67.4% incorrect;
  Deepfake §12).
- **Forgery / spoofing and cross-owner-collision resistance is unquantified** for the mark/credential signals
  (Model-IP §17, §12) — attribution decisions carry unmeasured framing/false-attribution risk.
- **Stateful detector components carry drift/poisoning risk** that is reviewer-flagged and largely untested
  (`A37473`, `A41234`).
- **Verifier/detector model is a single point of trust** — its version drift breaks verification (`A37865`), its
  compromise removes the signal.
- **Cross-modality generalization is siloed** — image, audio, audio-visual, text, tabular, embedding methods are
  separate; a unified layer must compose per-modality mechanisms and inherits each one's limits (Deepfake §2;
  Model-IP §17).
- **Single-dataset / single-family concentration and truncated numbers** limit external validity (`A37429`
  Mip-NeRF360; `A38094` SD/DDIM; `A40892` SD v2.1; `A38060` per-GenImage-subset training; numbers **not stated in
  paper** for `A37334`, `A37865`, parts of `A41234`) — production validation required.

## Relevant research (stable paper ids from the syntheses/cards)

**Passive detection as a probabilistic evidence signal (Deepfake corpus — the center of this pattern):**
- **A37071** — AIGI detection via dual-branch asymmetric discrepancy; GenImage SOTA but ~57–58% on Chameleon
  (the setting-dependence / averaged-SOTA caution); released code.
- **A37421** — MIRAGE/MIRAGE-R1: in-the-wild VLM reasoning detector with **confidence-gated adaptive compute**
  (fast-verdict → reflective escalation); ~78.46% OOD; documents "overthinking"; released code; anonymized A/B
  sources.
- **A38060** — ESIDE: diffusion-timestep-ensembled detection + **metric-grounded MLLM explanation refinement**;
  the load-bearing **explanation-trust** finding (**≤67.4%** of MLLM flaws incorrect); 98.91%/95.89% ACC;
  per-GenImage-subset training; released code + datasets.
- **A40886** — TriDetect: unsupervised **GAN-vs-DM architectural clustering + attribution**; GenImage avg AUC
  **0.9882** (5 datasets, 13 baselines); fixed **K=2** assumption is a named, expiring bias.
- **A41234** — RealNet: **real-only** representation learning with feature-space pseudo-negatives; across GAN/
  diffusion/VAR + a medical distribution shift, low compute — the **future-proofing** detection paradigm.
- **A40907** — Wavelet prompt tuning for **type-invariant audio** deepfake detection; **3.58%** all-type EER vs
  ~30–50% single-type (the starkest generalization result); ~458× fewer trainable params; clean-audio-only scope.
- **A40928** — Deformable state-space **temporal audio-visual** forgery localization of sparse segments; two AV
  benchmarks only.
- **A37945** — FaceShield: explainable **face anti-spoofing** MLLM (detect+type+reason+localize, 12 spoof types);
  intra-dataset ACC 99.41, Replay-Attack cross-dataset HTER 20.07; identity/authz relevance; released code.
- **A37473** — Face-forgery detection via CLIP residual **prototype bank** (capacity 64/class, decay γ=0.99) — a
  stateful-surface governance example; borrowed baselines.
- **A37553** — DDOC: **decision-driven orthogonal decoupling** of OSN compression (orthogonalize nuisance to the
  decision axis); ViT+CNN bidirectional fusion (+7.4 ablation); ~75% mean under OSN compression.
- **A37334** — Face-forgery robustness via RL-scheduled curriculum augmentation + IRM (training-time); concrete
  numbers **not stated in paper** in the reviewed text.

**Proactive forensics / tamper-tripwire (owner-side, pre-publication):**
- **A37865** — Blank Canvas: proactive frequency-aware ℓ∞ perturbation forcing SAM to "segment nothing" for
  **training-free tamper localization**; the corpus's closest attestation analogue; tied to a **specific SAM
  version** (verifier-version dependency); perturbation survivability untested; released code; truncated numbers.

**Ingestion-boundary enforcement (most agent-relevant — Model-IP corpus):**
- **A40910** — CopyGuard / LVLM copyright: guardrail bypass via the multimodal/RAG **context channel**
  (author-reported **11/12** LVLMs fail); tool-augmented ingestion-time gate (notice identifier → source verifier
  → query-risk analyzer/rewriter → status reminder). *Enforce provenance where content enters, not at the prompt.*

**Cryptographic credential & mark/fingerprint signals (composed via `signed-provenance.md`):**
- **A40909** — iSeal: encrypted external-secret ownership fingerprint (similarity + ECC, not exact match); the
  **only litigation-grade adaptive** threat model in either corpus. *The crypto-credential signal.*
- **A40843 / A40851** — StyleSentinel (SVDD-hypersphere style fingerprint) / OFA (passive image-to-model
  attribution): **intrinsic, no-embedding fingerprints** for already-published content the agent cannot re-sign.
- **A38094 / A40892 / A40901 / A40921 / A40561 / A40546 / A41092** — generative-output watermarking family
  (in-generation, post-hoc, audio, decode-time text); recovered marks are evidence, missing marks are not
  authenticity; non-adaptive robustness; forgery/collision largely unquantified; several headline numbers **not
  stated in paper**.
- **A40728** — RegionMarker: EaaS **embedding-API** watermark (RAG/agent-memory supply-chain provenance); prior
  EaaS schemes each broken by one attack family.

**Removal red-team (why missing ≠ authentic; why fail-closed):**
- **A37429** — GSPure: white-box removal of three 3DGS watermarks (up to **16.34 dB** reduction, <1 dB scene
  loss); Mip-NeRF360 only.
- **A39041** — Box-free image-to-image removal (black-box, **~100%** removal, PSNR up to 34.69 dB); enables
  watermark-free surrogate; proposed query-screener defense not rigorously benchmarked.

**Extraction survival & training-data provenance:**
- **A39992** — DeepTracer: extraction-robust watermarking with **adaptive + detection** attacks; the
  **in-distribution, task-coupled** principle (OOD triggers forgotten by stolen models).
- **A40575** — SPECTRA: pre-publication text watermark via grey-box log-probs (+5B tokens, <0.001% corpus);
  documents prior MIA collapsing to ROC-AUC ~0.50–0.56.
- **A37038** — Code membership inference as a training-data/copyright auditor; grey-box log-prob access.

**Adaptive-attacker exemplar (pedagogy, not a deployable control):**
- **A41525** — Breakable Machine: K-12 AI-literacy artifact; the corpus's **only adaptive, physical-world
  attacker** (human spoofing MobileNet-V2 via CAM saliency); a red-team *methodology template*, not a defense.

**Excluded (off-topic; carry no security weight):** `A39623` (Shapley/FANOVA GP explainability) and `A40030`
(VeriFlow NN formal verification) are flagged miscategorized in the Model-IP synthesis and are **not** used here.

## Evidence strength

- **The design principle** — treat any single provenance signal as **probabilistic evidence, never an
  authoritative gate**; **compose** signals; **enforce at ingestion, not the surface prompt**; **gate machine
  explanations**; **surface uncertainty**; **fail closed on absence/ambiguity**; and **treat detection accuracy
  as a decaying asset** — is **convergent across independent papers and both syntheses** (Deepfake §14 explicitly
  recommends combining detection with cryptographic provenance + watermarking + human review; `A40910`, `A38060`,
  `A40907`, `A37071`, `A37429`/`A39041` each support a facet). This is *convergence across independent studies,
  not independent replication of one effect size*. Reviewer assessment: **moderate** confidence in the
  principle's direction.
- **The composition itself is a reviewer-synthesis extrapolation.** No single paper implements the full multi-
  signal ingestion gate specified here; it is assembled from the corpus's individual primitives plus its
  convergent cautions and **requires production validation**.
- **Specific numbers** (3.58% vs ~30–50% EER; ~57–58% Chameleon; ≤67.4% incorrect flaws; 99.41 ACC / 20.07 HTER;
  0.9882 AUC; 16.34 dB; ~100% removal; 11/12 LVLM failure; ~0.50–0.56 MIA ROC-AUC) are **author-reported,
  non-adaptive** (except `A40909`, `A39992`, and `A41525`'s attack), often single-model / single-family /
  truncated, and **not independently verified**. Many watermark fidelity/bit-accuracy numbers are **not stated in
  paper** in the reviewed text.
- **Adaptive-adversary and forgery/spoofing resistance are the load-bearing gaps** — unmeasured across the
  Deepfake corpus and near-universally untested in Model-IP; any "robust" or "0 forged-accept" claim is a target,
  not a demonstrated property.
- **Bottom line:** a **well-motivated content-authenticity evidence layer** with modest, mostly non-adaptive,
  time-bounded empirical backing and one strong adaptive anchor (`A40909`, via the crypto-credential signal). It
  is **not** a prevention mechanism and its accuracy **decays**. Every deployment claim **requires production
  validation**, and an **adaptive red-team plus a forgery red-team plus a generalization-drift re-benchmarking
  cadence** are prerequisites before operational reliance.

## When NOT to use this pattern

- **When you need prevention, not evidence.** Content provenance establishes a trust decision and attribution — it
  does not stop misuse (Model-IP §14; Deepfake §14). To *block* an action, use a permission gate / human approval
  (`policy-permission-gates.md`, `human-approval-consequential-actions.md`).
- **As a single-detector hard gate.** Every deployment-implications section forbids using one detector as an
  authoritative gate (Deepfake §14); a single signal is defeatable and its accuracy decays.
- **When you would trust a machine-generated explanation as ground truth** (`A38060` ≤67.4% incorrect) — gate it
  or do not surface it.
- **When you cannot maintain a re-benchmarking cadence.** Generalization expires as generators evolve (`A40886`,
  Deepfake §17); a static detector silently degrades. If you cannot re-evaluate against the hardest in-the-wild
  sets, do not claim durable accuracy.
- **When you would make an attribution, identity, or litigation claim without a forgery / cross-owner-collision
  evaluation** — the corpus's near-universal omission (Model-IP §17; `A38094`, `A40546`, `A41092`, `A40909`
  partial) means false-attribution/framing risk is unmeasured.
- **For the cryptographic-bind sub-problem specifically** (external-secret signing, key custody, similarity/ECC
  verification) — use `signed-provenance.md` directly rather than this broader playbook.
- **When you would claim adaptive-adversary or anti-forensic robustness** — untested across the corpus (Deepfake
  §17; Model-IP §11); scope every claim to the tested, non-adaptive threat model.
