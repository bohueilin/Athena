# Pattern: Input / Output Detection

> **Scope of evidence.** This pattern is grounded in the AAAI-26 corpus syntheses `AILLM-Safety.md` and
> `Adversarial-ML-Attacks.md` and their underlying research cards. It covers the **ML-detector / classifier /
> judge layer** — the input-side moderation, jailbreak, toxicity, and adversarial-input detectors and the
> output-side content, disclosure, and harm detectors that screen what enters and leaves a model — *not* the
> structural trust boundary (that is `prompt-injection-containment.md`), the allow/deny decision engine (that is
> `policy-permission-gates.md`), or training-time backdoor detection (that is `backdoor-detection.md`).
>
> Load-bearing papers: **A41108** (STACK — staged whole-pipeline bypass drives a per-component-robust input+output
> guard stack from ~0% to 71% ASR black-box, author-reported, by inducing the model to emit an attacker-chosen
> string past the output classifier), **A41144** (MFA — 17 open+commercial VLMs with real moderators; alignment +
> system prompt + I/O moderation jointly bypassed, 58.5% overall author-reported; **independently replicates the
> output-repetition channel** and adds shared-encoder monoculture transfer), **A41498** (GARD — taxonomy-grounded
> financial sensitive-information I/O detector, OWASP-LLM #2), **A41152** (VALOR — layered detect → rewrite →
> post-hoc verify), **A40866** (SceneJailEval — scenario-adaptive severity-graded judge), **A40920**
> (T2I-RiskyPrompt — reason-driven detector), **A37350** (EigenShield — embedding-layer input filter, one of the
> few defenses evaluated in an adaptive setting), **A36960** (source-aware audio-toxicity classifier),
> **A40296 / A40465 / A41058 / A40916** (surface-form evasion → normalize before you detect), **A40840 / A36996**
> (detect over the whole context/history, not the last turn), **A40841 / A41086** (multimodal detector coverage
> gaps), **A40584** (verifier/reward scores are gameable), **A40897** (detector false-positive cost),
> **A41074 / A42191 / A41140** (over-refusal as a first-class metric; material residual ASR after detection).
> Supporting: A40301, A40366, A40891, A40607, A40863, A41099, A40353, A38127, A38340, A38853, A40445, A40486,
> A40833, A40248, A40399, A40543, A40018, A41468, A41090.
>
> **Evidence integrity (non-negotiable).** Every quantitative claim below is **author-reported and not
> independently verified**; several headline numbers sat in table regions the source extracts marked truncated
> and are flagged. Where a card was silent the text says "not stated in paper". Numbers are tagged author-reported
> vs. *(reviewer synthesis)*. Calibrated language only — "reduced ASR against the tested attacks under the
> evaluated threat model", "requires production validation" — never "secure / proven-safe / eliminates". The
> single most important cross-corpus caveat, repeated below: **no detector in either synthesis was evaluated
> against an adaptive, defense-aware attacker except A37350 (partially)**, so every efficacy number is an upper
> bound on real-world protection, and the two strongest agent-relevant results (A41108, A41144) are *attacks that
> break stacked detectors*, not defenses.

---

## Problem addressed

A model cannot be trusted to police its own inputs and outputs, so deployments bolt on **detectors**: input-side
classifiers (moderation, jailbreak, toxicity, adversarial-input / OOD probes) and output-side classifiers
(content moderation, PII/secret disclosure, harmful-generation checks). The corpus makes three problems concrete
and load-bearing:

- **A stack of detectors that each pass per-component evaluation collapses under a whole-pipeline adaptive
  attack.** This is the corpus's single most important — and *independently replicated* — finding for this
  pattern. STACK (A41108) moves a few-shot guard pipeline from ~0% baseline ASR to **71% black-box** (33%
  transfer, author-reported); MFA (A41144) independently moves a jailbreak past alignment + system prompt + input
  and output moderation to **58.5% overall / 52.8% commercial / 72.92% with all three facets** (author-reported,
  17 VLMs, real moderators). Both exploit the *same concrete channel*: inducing the model to emit an
  attacker-chosen string **past the output classifier** (Adversarial-ML §9.9, "an independently replicated
  concrete weakness").
- **Surface-form detectors miss semantic intent.** Emoji/glyph substitution (A40296 — the model *recognizes* the
  intent yet complies), math+code wrapping (A40465, author-reported avg ASR 91.19% GPT-series / 97.62% on five
  SOTA models at a single query), 21-cipher recombination (A41058, author-reported 60%+ ASR within ≤10 queries),
  and cross-lingual "macaronic" recombination (A40916) all pass harmful intent through a detector that scans
  lexical form. Semantics-preserving perturbation defeats text detectors on financial LLMs/agents too
  (A41099, ChameleonAttack).
- **Accuracy-preserving and modality-shifted attacks are invisible to the obvious detector signal.** Reasoning-DoS
  keeps the *answer correct* while inflating reasoning ~17× on MATH-500 (A40486) or via indirect injection on o3
  (A40833) — an accuracy-only or content-only monitor sees nothing. Video summarizers omit clearly-visible harm
  (A40841, author-reported Harmfulness-Omission-Rate >90% in most cells) and embedded NSFW text in generated
  images evades OCR+toxicity pipelines (A41086, author-reported OCR+Detoxify detects only ~90.83% on FLUX, 49.66%
  on SDXL). Multimodal channels are repeatedly softer than text (A40607, A40863).

**Input/output detection** is the set of controls that build, layer, normalize-before, and evaluate these
detectors correctly, while treating every detector verdict as an **advisory signal into a deterministic,
fail-closed decision** — never as the gate itself, because the corpus shows detectors are bypassable, gameable,
and non-adaptively evaluated.

## Applicable assets and attack surfaces

- **The input channel (user prompt + assembled context).** Screened by moderation/jailbreak/toxicity classifiers
  (A41108/A41144 input moderation layer), embedding-layer filters (A37350 EigenShield, RMT causal-subspace
  projection), and manifold/OOD adversarial-input probes (A40301 embedding-manifold detect-and-correct; A40366
  Mahalanobis+spectral). The *whole assembled context and conversation history* is the asset, not just the latest
  turn (A40840, A36996).
- **The output channel (model generation).** Screened by output content moderators, sensitive-information/PII
  disclosure detectors (A41498 GARD, OWASP-LLM #2), and — critically — the surface the STACK/MFA output-repetition
  channel targets (A41108, A41144). The output classifier is where the strongest replicated bypass lands.
- **Reasoning / intermediate content.** Reasoning-token length and chain-of-thought are an availability and
  stealth surface (A40445 repetitive-generation, A40486 CoT-overthinking backdoor, A40833 reasoning-DoS on o3);
  a Process-Reward-Model verifier over reasoning steps is itself gameable (A40584, an impossible constraint scored
  0.973, author-reported).
- **Multimodal inputs and outputs.** Image (A40018 sub-image decomposition, A40607, A40863, A40920 T2I risk,
  A41086 embedded-image-text, A41152 T2I output image check), audio (A36960 toxicity source/category, A40607),
  and video (A40841 frame-sampling coverage + encoder-vs-fusion probe). Frame sampling / token compression are
  *safety-coverage decisions, not efficiency afterthoughts* (A40841).
- **The detector itself as an asset.** An LLM judge/detector inherits its own attack surface — prompt injection
  and evaluator-gaming (A40866 is LLM-agent-based and untested against evaluator-gaming; A41468 reviewer synthesis:
  "using an LLM to defend an LLM agent creates a potentially injectable trust anchor"; A37474-class verifiers
  inherit the component's attack surface). The detector's own false-positive/over-refusal behavior is an asset to
  protect (A40897 dataset-dependent FPR up to ~21.95%; A41074/A41140/A41152/A42191/A40399/A40543).

## Threat model

Designed for **inference/runtime adversaries** who cannot change model weights but craft inputs, or steer
outputs, to slip past the detector layer. Grounded threat classes:

- **Whole-pipeline adaptive jailbreak of a stacked guard.** The attacker treats the input classifier, model
  alignment, system prompt, and output classifier as one system and stages a chained attack (A41108 STACK,
  author-reported 0%→71% black-box; A41144 MFA, 58.5% author-reported). The load-bearing sub-threat is the
  **output-repetition channel** — inducing the model to reproduce an attacker-chosen string so it passes the
  output classifier (both papers, independently).
- **Surface-form / encoding evasion of the detector.** Emoji (A40296), math+code (A40465), cipher (A41058),
  cross-lingual recombination (A40916), semantics-preserving text perturbation (A41099) — the harmful intent is
  preserved but the lexical form the detector scans is changed.
- **Whole-context / history evasion.** The malicious content lives in a prior "assistant" turn or elsewhere in
  the assembled context, so a detector that inspects only the latest user turn misses it (A40840 forged history,
  author-reported RA-DRI avg ASR 94.8% across 8 models; A36996 cross-model transferred history).
- **Modality-shift evasion.** The payload is carried in a channel the deployed detector does not inspect — a
  sub-image (A40018), continuous MLLM space transferred to a text suffix (A40863), audio paralinguistics (A36960,
  A40607), embedded text rendered inside a generated image (A41086), or a video frame the sampler skipped (A40841).
- **Accuracy-preserving stealth.** Reasoning-DoS and reasoning-overthinking backdoors keep answers correct while
  inflating cost, invisible to accuracy/content-only detection (A40445, A40486, A40486's ~17× on MATH-500,
  A40833 on o3 via indirect injection — all author-reported).
- **Detector / verifier gaming.** The attacker games the artifact the detector keys on — a reward/verifier score
  (A40584 PRM scores logically invalid steps high, 0.973 author-reported), a spoofable explanation/attention map
  (A38340 A-SAGE forges a coherent-but-false rationale), or model outputs/hidden states treated as evidence
  (A38853 activations invert to prompts — outputs are capability, not verification).
- **Known-detector bypass.** The attacker knows the detector family and defeats it directly — Fact2Fiction
  (A40353) evades paraphrasing, K-means clustering detection, and perplexity filtering; hiding the confidence
  signal is not a boundary (A38127, hard-label query-efficient attack, proved O(1/T²)).
- **Monoculture transfer.** A detector sharing an encoder/backbone with the guarded model (or with other
  deployments) inherits transferable adversarial inputs (A41108 shared base between guard and guarded model is a
  weakness; A41144 avg 59.58% image ASR transferring across moderators, author-reported).

**Adaptivity boundary (critical).** Both syntheses' most consistent meta-finding is that **defenses are almost
never evaluated against an attacker adapting to them** (Adversarial §9.1; AILLM §17). Of the detectors here only
A37350 (EigenShield) reports a standard + *adaptive* + OOD evaluation; A41074, A42191, A41152, A41498, A40866,
A40920 are non-adaptively evaluated (author caveats). Treat every efficacy number as best-case; adaptive
red-teaming is a launch gate (see Verification strategy).

## Control mechanism

Detection is a **set of advisory signals feeding a deterministic, fail-closed decision** — not a verdict that is
itself the gate. Five mechanisms compose:

1. **Normalize / canonicalize before you detect.** Decode emoji/glyph/cipher/cross-lingual/math-code back to
   canonical intent, and screen the *whole assembled context including history*, before any classifier runs
   (A40296, A40465, A41058, A40916; A40840/A36996 "screen history, not just the latest user turn"). A detector
   applied to un-normalized surface form is defeated by construction.
2. **Screen both directions, independently, over every modality.** An input classifier and an output classifier
   are *both* required (A41108/A41144 show either alone is insufficient), and coverage must extend to image/audio/
   video (A40018, A40607, A40841, A41086, A36960) — including the standalone-encoder signal when fusion suppresses
   harm (A40841 encoder-vs-fusion probe). Frame sampling and token compression are coverage decisions (A40841).
3. **Break the output-repetition channel.** Because the one independently-replicated stacked-guard bypass is
   inducing the model to emit an attacker-chosen string past the output classifier (A41108, A41144), the output
   detector must not be defeatable by verbatim echo — e.g. detect on recovered intent and on structural
   repetition of classifier-triggering fragments, not only on the raw output string.
4. **Use independent, non-monoculture detectors, and keep their output advisory.** Do not share the guarded
   model's encoder/backbone with the guard (A41108 shared-base weakness); avoid a single detector family that
   transfers across deployments (A41144 monoculture). Treat every score/verdict — including an LLM judge — as an
   *advisory input to a deterministic decision*, never the sole authority, because detectors are injectable
   (A41468 reviewer synthesis), gameable (A40584, A38340, A38853), and evaluator-gamable (A40866).
5. **Detect the right signal, not just pass/fail content.** Instrument reasoning-token length/entropy
   (A40445, A40486, A40833), confidence-drift / token-confidence runs (A40891, A40897), and manifold/Mahalanobis
   OOD scores (A40301, A40366) — because accuracy- and content-only detection misses accuracy-preserving and
   representation-shifted attacks.

The allow/deny/step-up **decision** these signals feed is `policy-permission-gates.md`; the structural
"untrusted content is data, not instruction" boundary is `prompt-injection-containment.md`; blast-radius limits
are `tool-capability-isolation.md` / `sandboxed-execution.md`. This pattern owns the *detector layer* only.

## Preconditions and trust assumptions

The pattern is only as strong as these hold; each is a documented failure point:

- **Canonicalization coverage is complete for every deployed channel and modality.** An un-normalized encoding or
  an un-inspected modality is a silent bypass (A40296, A40465, A41058, A40916 text; A40018, A40607, A40863,
  A41086, A40841 multimodal). Coverage is a moving target, not a one-time task.
- **The output classifier cannot be defeated by verbatim echo.** If it keys on the raw output string, the
  replicated repetition channel defeats it (A41108, A41144). You must assume the model can be induced to emit
  arbitrary attacker-chosen strings.
- **Detector and guarded model do not share the same encoder/backbone.** Shared base is a demonstrated weakness
  (A41108); a monoculture detector transfers (A41144).
- **The detector's verdict is not the sole authority and is not itself an un-defended trust anchor.** An LLM
  judge is prompt-injectable (A41468 reviewer synthesis) and evaluator-gamable (A40866 untested against gaming);
  a score/verifier is gameable (A40584, A38340). A deterministic gate downstream must make the actual decision.
- **A false-positive / over-refusal budget is defined and measured.** Aggressive detection over-blocks benign
  content (A40897 FPR up to ~21.95% author-reported; A41074/A41140/A41152/A42191/A40399/A40543 all foreground the
  trade-off). Without a measured budget, the detector is either evaded or unusable.
- **Detection runs over the whole assembled context and history**, from a trusted record — last-turn-only
  screening is bypassed by history injection (A40840, A36996).
- **Residual harm after detection is assumed and handled downstream.** No detector here drives ASR to a safe
  floor (A42191 ~31% residual, A40248 ~16% residual, A41468 >50% miss on hardest class — all author-reported);
  least-privilege scoping and human approval on high-stakes actions must be present (A41090; A41468).

## System architecture

Detectors sit as advisory layers around the model, feeding a deterministic decision — an input-side gate and an
output-side gate, both fail-closed, aligned to the agent cognitive cycle (A41468 layered detect → gate → verify;
A41152 detect → rewrite → post-hoc verify; A41090 prompt-level detection necessary-but-insufficient):

```
 raw input ──►[Normalize / canonicalize]   decode emoji/glyph/cipher/cross-lingual/math-code → canonical intent;
 (+history,        │                         assemble WHOLE context+history before screening.
  multimodal)      ▼                         (A40296,A40465,A41058,A40916; A40840/A36996 whole-context)
             [Input detectors]              moderation + jailbreak + toxicity + OOD/manifold + per-modality;
                  │                          INDEPENDENT backbone from the guarded model. verdicts = ADVISORY.
                  ▼                          (A37350 embedding filter; A40301/A40366 OOD; A36960 audio; A40920 T2I)
             [Input gate: fail-closed]  ───► deterministic allow/hold/deny on advisory scores + rules.
                  │                            decision engine = policy-permission-gates.md
                  ▼
              ┌ model / agent ┐             reasoning-token & confidence telemetry emitted here
              └───────┬───────┘              (A40445/A40486/A40833 length; A40891/A40897 confidence)
                      ▼
             [Output detectors]             content moderation + disclosure/PII (A41498) + per-modality harm
                  │                          (A40841 video, A41086 image-text, A41152 T2I image check);
                  ▼                          MUST resist verbatim-echo (A41108/A41144 repetition channel).
             [Output gate: fail-closed] ───► deterministic block/rewrite/hold; over-refusal budget measured.
                  │                            (A41152 rewrite; A41074/A42191/A40399 FP trade-off)
                  ▼
        [Tamper-evident trace + async judge]  every detector verdict+score+rule logged with provenance;
                  │                             scenario-adaptive severity judge advisory only (A40866).
                  ▼                             integrity mechanism = tamper-evident-traces.md
        adaptive red-team → detector/normalizer refinement loop  (Adversarial §16; AILLM §16)
```

- **Normalization and input detection run before the model sees content; output detection and the echo-resistant
  check run before any side effect fires.** A detector verdict that arrives after the effect has not contained
  anything.
- **The two gates are deterministic** (`policy-permission-gates.md`); the detectors only supply advisory scores.
- **Latency is bounded architecturally** — cache deterministic checks, run the async severity judge and audit off
  the critical path (A41468 caching/async).

## Recommended implementation pattern

Deterministic, fail-closed, least-privilege — in priority order:

1. **Canonicalize, then detect on recovered intent.** Normalize emoji/glyph/cipher/cross-lingual/math-code and
   assemble the whole context+history before any classifier; never match raw surface strings (A40296, A40465,
   A41058, A40916; A40840, A36996). Track normalizer coverage as a metric; an un-decodable input is held, not
   passed.
2. **Deploy independent input AND output detectors.** Both directions are required (A41108/A41144). Give the
   detectors a *different* backbone/encoder from the guarded model (A41108 shared-base weakness) and avoid a
   single family that transfers across deployments (A41144 monoculture).
3. **Make the output detector echo-resistant.** Detect on recovered intent and on structural repetition of
   classifier-triggering fragments — not only on the raw output string — to close the independently-replicated
   repetition channel (A41108, A41144).
4. **Cover every modality the system reads or emits.** Input: image/audio/video and embedded-image text (A40018,
   A36960, A40607, A40920, A41086). Output: post-hoc image safety check (A41152), video harm/omission check with
   the standalone-encoder signal as a backstop when fusion suppresses harm (A40841). Treat frame sampling / token
   compression as coverage settings (A40841).
5. **Keep every detector/judge verdict advisory into a deterministic gate.** A moderation score, an LLM judge
   (A40866), a reward/verifier score (A40584), or an explanation (A38340) may raise suspicion, force a rewrite,
   or force human review — but the deterministic gate makes the decision (`policy-permission-gates.md`). Never let
   an injectable LLM be the sole authority (A41468 reviewer synthesis).
6. **Detect the right signal, not just content pass/fail.** Emit and threshold reasoning-token length/entropy
   (A40445, A40486, A40833), token-confidence runs / confidence-drift (A40891, A40897), and manifold/Mahalanobis
   OOD scores (A40301, A40366) — these catch accuracy-preserving and representation-shifted attacks that content
   moderation misses.
7. **Prefer rewrite/hold over hard-reject where it lowers over-refusal without weakening the gate** (A41152
   detect→rewrite→verify; A40543 filter only harmful relations; A40399 "Educational Refusal" quality tier) — but
   stay fail-closed on high-stakes/irreversible actions.
8. **Instrument over-refusal / false-positive rate as a first-class metric** against an adaptive benign-ambiguous
   set (A41074, A41140, A41152, A42191, A40897, A40543) — an unusable detector is turned off.
9. **Log every verdict with its score, rule, and the canonicalized form screened, asynchronously**, into a
   tamper-evident trace (`tamper-evident-traces.md`; A40866/A36960 structured trace fields; A41468 L4).
10. **Feed adaptive red-team findings back into normalizer coverage and detector thresholds** (Adversarial §16;
    AILLM §16) — detection is a maintained control, not a fixed asset.

## Incorrect or fragile implementation patterns

- **A stack of per-component-validated input+output classifiers presented as robust.** It collapses under a
  staged whole-pipeline adaptive attack — the corpus's strongest cautionary result (A41108 0%→71% black-box;
  A41144 58.5%, both author-reported).
- **An output classifier that keys on the raw output string.** Defeated by the independently-replicated
  repetition channel — the model is induced to echo an attacker-chosen string past it (A41108, A41144).
- **Surface-form / keyword / regex detection.** Falls to emoji/math-code/cipher/cross-lingual/semantics-preserving
  substitution (A40296, A40465, A41058, A40916, A41099) — normalize first and detect recovered intent.
- **Screening only the latest user turn / only text.** History-injection lives in prior turns (A40840, A36996)
  and payloads hide in image/audio/video (A40018, A40607, A40841, A41086, A40863).
- **Accuracy- or content-only monitoring.** Misses reasoning-DoS and overthinking backdoors that keep answers
  correct (A40445, A40486, A40833) and video/image harm the fused model omits (A40841, A41086).
- **Making an LLM judge the sole authority.** It is prompt-injectable (A41468 reviewer synthesis) and
  evaluator-gamable (A40866 untested against gaming); a reward/verifier score is gameable (A40584, 0.973 on an
  invalid step); an explanation/attention map is spoofable (A38340).
- **Sharing the guarded model's encoder/backbone with the detector.** Shared base is a demonstrated weakness
  (A41108); a monoculture detector transfers across deployments (A41144).
- **Suppressing/hiding the output or the confidence signal and calling it a boundary.** Decision-only exposure is
  still attackable with improving query efficiency (A38127, proved O(1/T²)).
- **Ignoring over-refusal.** Unmeasured false-positive cost (A40897 up to ~21.95%) makes the detector either
  bypass-tuned or switched off (A41074, A41140, A41152, A42191).
- **Fail-open on detector error/timeout or on an un-decodable input.** Contradicts the defense-in-depth posture;
  an input the normalizer cannot decode must be held or denied, not passed (reviewer synthesis, consistent with
  A41468).

## Verification strategy

- **Adaptive, defense-aware red-team is the launch gate** — the single most consistent gap across both syntheses
  (Adversarial §9.1, §16; AILLM §16, §17). Any robustness claim "requires production validation" first. Note that
  only A37350 (EigenShield) in this set reports an adaptive + OOD evaluation; A41074, A42191, A41152, A41498,
  A40866, A40920 are non-adaptive (author caveats).
- **Run the whole-pipeline staged attack, not per-component tests.** Reproduce the STACK/MFA methodology: chain an
  attack across input classifier + alignment + system prompt + output classifier, and specifically test the
  **output-repetition channel** (induce the model to echo an attacker-chosen string past the output classifier) —
  A41108, A41144, both release code.
- **Test surface-form / encoding evasion of the normalizer** (A40296, A40465, A41058, A40916, A41099) — verify
  canonicalization actually recovers the intent the detector then screens.
- **Test whole-context / history and per-modality evasion** (A40840, A36996; A40018, A40607, A40863, A41086,
  A40841) — verify the detector inspects prior turns and every modality, including the standalone-encoder signal
  where fusion suppresses harm (A40841).
- **Test detector/verifier gaming** — reward/verifier score gaming (A40584), spoofed explanations (A38340),
  known-detector bypass via paraphrase/clustering/perplexity evasion (A40353).
- **Report absolute residuals, not relative reductions, and over-refusal as a first-class metric** (A42191
  absolute residual ASR; A41074/A41140/A41152/A40897 over-refusal). Effect/outcome-based evaluation against
  environment state where the detector guards an action (A41090 rule-based state-grounded evaluators).
- **Do not sign off on a single automated LLM judge.** Validate against human agreement; measurement circularity
  (a detector optimizing against the class it scores with) is a recurring risk (A40916, A40920); A40866
  (SceneJailEval, author-reported F1 0.917 own / 0.995 JBB) is a better-judge attempt but itself untested against
  evaluator-gaming.

## Metrics and thresholds

Track these families; **thresholds are operator-defined per deployment and must be validated against an adaptive
set — the corpus provides no validated universal threshold, and several headline tables were truncated in the
source extracts.**

- **ASR-under-defense (absolute), whole-pipeline.** The bar to beat comes from the attacks: A41108 STACK
  ~0%→**71%** black-box / 33% transfer (author-reported); A41144 MFA **58.5%** overall / 52.8% commercial /
  72.92% all-facets / avg 59.58% image transfer (author-reported). A detector stack that reports only
  per-component ASR is not measuring the real threat.
- **Detector detection rate / recall + false-negative rate.** A41498 GARD recall **0.98** — but on a largely
  synthetic set with only 115 SME-validated real samples (author-reported, non-adaptive). A41152 intention **FNR
  ~31–33%** with a Qwen1.5-1.8B rewriter (author-reported) — a weak in-line detector is a weak layer. A41086
  embedded-image-text: OCR+Detoxify detects only **~90.83% FLUX / 49.66% SDXL** (author-reported).
- **False-positive / over-refusal rate (first-class).** A40897 ConfGuard dataset-dependent FPR **up to ~21.95%**
  (author-reported); A41074 reports low benign over-refusal with a large ASR drop (e.g. Qwen2.5-0.5B 91.0→4.0 on
  MalwareGen, author-reported, non-adaptive); A42191 refusal 41.31→62.76% alongside ASR 51.86→31.27%
  (author-reported). Measure against an adaptive benign-ambiguous set.
- **Judge/detector quality.** F1 (A40866, 0.917/0.995 author-reported), accuracy (A40920 T2I-RiskyPrompt **91.8%**
  author-reported), recall/FNR/FPR (A41152, A41498) — but with human-agreement validation, not a single LLM judge.
- **Normalizer coverage / recovery rate** — fraction of encoded inputs whose canonical intent is recovered before
  detection (motivated by A40296, A40465, A41058, A40916); an uncovered encoding is a silent bypass.
- **Accuracy-preserving-stealth signals** — reasoning-token length / ×-inflation (A40486 ~17× on MATH-500,
  A40445, A40833 — all author-reported, flagged as a *proxy* for wall-clock energy), token-confidence-run and
  confidence-drift events (A40891, A40897), manifold/Mahalanobis OOD scores (A40301, A40366).
- **Detector latency and decision-cache hit rate** (A41468 caching/async as the latency lever).

## Test cases

Concrete, corpus-grounded cases the detector layer must be exercised against:

1. **Whole-pipeline staged jailbreak** chaining input classifier + alignment + system prompt + output classifier
   (A41108 STACK; A41144 MFA).
2. **Output-repetition bypass** — induce the model to emit an attacker-chosen string that passes the output
   classifier verbatim (A41108, A41144 — the independently-replicated channel).
3. **Surface-form evasion** — emoji (A40296), math+code single-query (A40465), 21-cipher within ≤10 queries
   (A41058), cross-lingual macaronic (A40916), semantics-preserving financial-text perturbation (A41099).
4. **Whole-context / history injection** — malicious content in a prior "assistant" turn (A40840 RA-DRI), a
   cross-model transferred jailbroken history (A36996).
5. **Modality-shift evasion** — sub-image decomposition + CoT (A40018), continuous MLLM space → text suffix
   (A40863), audio paralinguistics (A36960, A40607), embedded NSFW text in a generated image (A41086), harmful
   video frame the sampler skipped (A40841).
6. **Accuracy-preserving stealth** — reasoning-DoS / overthinking backdoor that keeps the answer correct while
   inflating reasoning (A40445, A40486, A40833).
7. **Detector/verifier gaming** — a reward/verifier score inflated on an invalid step (A40584), a spoofed
   coherent-but-false explanation (A38340), model outputs/activations treated as evidence (A38853).
8. **Known-detector bypass** — paraphrase / K-means-clustering / perplexity-filter evasion (A40353); hidden
   confidence signal exploited (A38127).
9. **Output disclosure** — a benign-looking prompt that elicits sensitive-information disclosure the output
   detector must catch (A41498 GARD, OWASP-LLM #2).
10. **Benign-ambiguous over-refusal probe** — content the detector should *not* block, to measure false-positive
    cost (A41074, A41140, A41152, A40897, A40399, A40543).

## Adaptive adversarial tests

Beyond static cases — attackers who know the detector design:

- **Stage the attack against the specific deployed stack** — the STACK/MFA methodology optimized against *your*
  input+output classifiers, not a generic guard (A41108, A41144, both release code — assume attackers have them).
- **Novel encoding outside normalizer coverage** — a new cipher/glyph/cross-lingual recombination the
  canonicalizer does not decode (A41058 releases cipher code; A40916 macaronic).
- **Query-efficient adaptive jailbreak** — low-query, online-adaptive strategy selection defeats many-query
  anomaly detection (A40554 >90% at <15 queries, A41058 60%+ within ≤10 — author-reported), so detection cannot
  rely on query-volume anomaly alone.
- **Detector-optimized adversarial input** — an adversarial example crafted against the detector's encoder,
  exploiting shared-backbone/monoculture transfer (A41108 shared base; A41144 transfer).
- **Evaluator-gaming the judge** — craft output that fools the LLM judge scoring it (A40866 untested against
  gaming; A40916/A40920 measurement circularity).
- **Reward/verifier gaming** — produce reasoning that scores high on a Process-Reward-Model while being invalid
  (A40584, 0.973 author-reported).
- **Repetition-channel variants** — re-encode the attacker's target string so it still passes an echo-resistant
  output detector (adaptive follow-on to A41108/A41144; reviewer synthesis).

## Telemetry requirements

Emit structured, tamper-evident trace fields for every detector decision (integrity mechanism =
`tamper-evident-traces.md`; A41468 L4; A40866/A36960 structured trace fields):

- **Per-detector verdict record** — detector id/version, the canonicalized (post-normalization) form screened,
  score + threshold, verdict, and whether it was advisory or gating (A40296/A40465 normalize-before-detect;
  A40866/A36960 structured fields including toxicity source/category).
- **Whole-pipeline outcome** — per-component block decisions plus the joint outcome, and any "repeat this string"
  / universal-suffix signature (A41108, A41144 output-repetition channel).
- **Normalizer coverage misses** — inputs that could not be decoded to canonical intent (candidate zero-day
  encodings; A40296, A41058, A40916).
- **Accuracy-preserving-stealth signals** — reasoning-token length/×-inflation time series (A40445, A40486,
  A40833), token-confidence-run / confidence-drift events (A40891, A40897), manifold/Mahalanobis OOD scores
  (A40301, A40366).
- **Per-modality coverage record** — which modalities were inspected and the standalone-encoder-vs-fusion
  divergence where measured (A40841 encoder-vs-fusion; A41086 OCR miss; A40018/A40607/A40863).
- **Over-refusal / false-positive events** — blocked-benign flags for the FP budget (A40897, A41074, A41140,
  A41152).
- **Judge/verifier provenance** — which judge/reward model produced an advisory score, flagged as gameable
  (A40866, A40584), never logged as ground truth.

## Failure handling

- **Fail-closed.** On detector timeout/error, an un-decodable (normalizer-miss) input, missing history
  provenance, or advisory-judge disagreement → block or hold for human approval (`human-approval-consequential-
  actions.md`). Reviewer synthesis, consistent with the defense-in-depth posture (A41468).
- **Treat an un-inspected modality or un-decoded encoding as unsafe**, not as passing — coverage gaps are silent
  bypasses (A40296, A41058, A40916; A40018, A40607, A40841, A41086).
- **Keep the decision on the deterministic gate, not the detector.** If the detector layer degrades, the gate
  degrades to least privilege / deny on high-stakes actions, never to open access (`policy-permission-gates.md`,
  `tool-capability-isolation.md`).
- **Assume the judge/detector can be compromised or gamed** (A40866, A40584, A41468 reviewer synthesis): because
  its verdict is advisory-only, its compromise cannot by itself authorize an output or a side effect.
- **Bound latency architecturally**, not by relaxing the check — cache deterministic checks, run the async
  severity judge and audit off the critical path (A41468).
- **Assume material residual harm.** No detector here reaches a safe floor (A42191 ~31% residual, A40248 ~16%
  residual, A41468 >50% miss on hardest class — author-reported); pair detection with least-privilege scoping and
  human approval on high-stakes/irreversible actions (A41090, A41468).

## Rollback and containment

- **Block before the side effect / before the output is released**, during output detection, not after (A41152
  post-hoc check *before* release; A41468 runtime gate). A verdict that arrives after the output has shipped has
  not contained anything.
- **Rewrite/quarantine over hard-fail where it preserves utility without weakening the gate** — VALOR's
  category-specific rewrite of a flagged prompt/image (A41152), risk-aware filtering of only harmful relations
  (A40543); the gate stays fail-closed on high-stakes actions.
- **Quarantine the bypass class** — when an adaptive bypass is found (a new encoding, a repetition-channel
  variant, a monoculture-transfer input), disable or tighten the affected detector path and route to human review
  until normalizer coverage / thresholds are updated (Adversarial §16 refinement loop).
- **Blast-radius limits downstream** — least-privilege capability isolation and sandboxed execution bound what a
  detected-too-late output can trigger (`tool-capability-isolation.md`, `sandboxed-execution.md`; A41090/A41468
  gate-not-replace least privilege).
- **Immutable, tamper-evident trace for forensics** — the full per-detector verdict chain supports reconstructing
  which layer was bypassed and how (`tamper-evident-traces.md`; A41468 L4).
- **Feedback loop** — feed the incident into refined normalizer coverage, detector thresholds, and the adaptive
  red-team suite (Adversarial §16; AILLM §16).

## Known bypasses

Demonstrated or corpus-supported bypasses of this pattern's weaker forms (all author-reported unless noted):

- **Whole-pipeline staged attack defeats a per-component-robust stack** — A41108 (STACK) 0%→71% black-box / 33%
  transfer; A41144 (MFA) 58.5% overall / 72.92% all-facets. The strongest, independently-replicated result.
- **Output-repetition channel** — inducing the model to echo an attacker-chosen string past the output classifier
  (A41108 and A41144 independently).
- **Surface-form / encoding evasion** — emoji (A40296), math+code 91.19–97.62% single-query (A40465), 21-cipher
  60%+ within ≤10 queries (A41058), cross-lingual macaronic (A40916), semantics-preserving financial text
  (A41099).
- **Whole-context / history injection** past last-turn-only detection — A40840 RA-DRI avg ASR 94.8%; A36996
  cross-model transfer (numeric results truncated in extract).
- **Modality-shift evasion** — A40018 sub-image, A40863 continuous-space, A41086 embedded image text (49.66% SDXL
  detected), A40841 video omission >90%, A36960/A40607 audio.
- **Accuracy-preserving stealth** — reasoning-DoS/overthinking keeps answers correct (A40445, A40486 ~17×, A40833
  on o3), invisible to content/accuracy detection.
- **Detector/verifier gaming** — reward/PRM 0.973 on an invalid step (A40584), spoofed explanation (A38340),
  paraphrase/clustering/perplexity-filter evasion (A40353), hidden confidence signal (A38127).
- **Monoculture / shared-backbone transfer** — adversarial inputs crafted on a shared encoder transfer to the
  guard (A41108 shared base; A41144 avg 59.58% image transfer).
- **Over-refusal as a soft bypass** — a detector tuned down to avoid FP (A40897 up to ~21.95%) leaves a wider
  attack window (reviewer synthesis on the A41074/A42191 trade-off).

## Residual risks

- **No detector drives ASR to a safe floor.** Leading defenses leave material residual: A42191 ~31% residual ASR;
  A40248 ~16% residual harmful on Qwen-3-8B despite near-zero on the prefill metric; A41468 >50% miss on its
  hardest class (all author-reported). The two strongest agent-relevant results here are *attacks* (A41108,
  A41144), not defenses.
- **Adaptive attackers are essentially unevaluated** — only A37350 reports an adaptive setting; the rest are
  best-case, non-adaptive (both syntheses' central gap). Deployed efficacy may be materially below reported
  numbers.
- **Normalizer / modality coverage is a moving target** — a new encoding or an un-inspected modality is a silent
  bypass (A40296, A41058, A40916; A40018, A40607, A40841, A41086).
- **LLM judges and reward/verifier detectors are injectable and gameable** — A41468 (reviewer synthesis) and
  A40866 (untested against evaluator-gaming), A40584 (PRM gaming), A38340 (spoofed explanation).
- **Self-proposed, in-distribution, non-adaptive detector benchmarks** overstate generality — A41498 (0.98 recall
  on a largely synthetic set, 115 real samples), A40866/A40920 self-proposed sets used for both tuning and
  headline SOTA (AILLM §12).
- **Over-refusal erodes operator trust** — the precision/recall frontier is itself a residual risk
  (A41074, A41140, A41152, A42191, A40897, A40399, A40543).
- **Dual-use artifact release** — STACK and MFA (A41108, A41144) and several evasion papers release code/prompts;
  assume attackers have them when threat-modeling (Adversarial §16; AILLM §12).
- **The trace/audit integrity is a supplied assumption** — a compromised log undermines detection forensics
  (`tamper-evident-traces.md`; A41468 asserts but does not specify integrity).

## Relevant research (stable paper ids from the syntheses/cards)

Primary:
- **A41108** — STACK: staged whole-pipeline guard-stack bypass, ~0%→71% black-box / 33% transfer (author-reported);
  the output-repetition channel past the output classifier; shared base between guard and guarded model is a
  weakness; released code. *Evidence: Strong (as an attack / evaluation standard for guard stacks).*
- **A41144** — MFA: multi-facet jailbreak of 17 open+commercial VLMs with real moderators, 58.5% overall
  (author-reported); **independently replicates** the output-repetition channel; monoculture transfer (avg 59.58%
  image ASR). *Evidence: Strong (as an attack); LLM/GPT-4o-judge dependence noted.*
- **A41498** — GARD: taxonomy-grounded financial sensitive-information I/O detector (OWASP-LLM #2); recall 0.98 on
  a largely synthetic set (115 SME-validated real samples). *Evidence: Preliminary (non-adaptive, in-distribution).*
- **A41152** — VALOR: layered detect → LLM-rewrite → post-hoc image verify (T2I); intention FNR ~31–33% with a
  small rewriter. *Evidence: Moderate; non-adaptive.*
- **A40866** — SceneJailEval: scenario-adaptive severity-graded jailbreak judge, F1 0.917 own / 0.995 JBB
  (author-reported); itself LLM-agent-based, untested against evaluator-gaming. *Evidence: Moderate.*
- **A40920** — T2I-RiskyPrompt: reason-driven 3B risk detector, 91.8% accuracy (author-reported); 6/14-category
  taxonomy; concept-erasure coverage gap. *Evidence: Moderate; self-proposed benchmark.*
- **A37350** — EigenShield: RMT causal-subspace embedding-layer input filter; model-agnostic; **one of the few
  detectors evaluated in standard + adaptive + OOD settings**, with honest asymptotic-guarantee caveats.
  *Evidence: Strong (relative to the corpus; still author-reported).*
- **A36960** — source-aware audio-toxicity classifier with structured toxicity source/category trace fields.
  *Evidence: Moderate.*
- **A40296 / A40465 / A41058 / A40916** — emoji / math-code (EquaCode) / cipher (MetaCipher) / cross-lingual
  (macaronic) surface-form evasion → normalize before you detect. *Evidence: Moderate; author-reported ASR is
  best-case, single/low-query.*
- **A40840 / A36996** — Response Attack / CHASE: forged & transferred conversation history → detect over the whole
  context, not the last turn. *Evidence: Moderate (A36996 numbers truncated in extract).*
- **A40841 / A41086** — video omission (>90% HOR) with encoder-vs-fusion probe / embedded-image-text evading
  OCR+Detoxify (90.83% FLUX, 49.66% SDXL) → per-modality coverage. *Evidence: Moderate.*
- **A40584** — Process Reward Models score logically invalid steps high (0.973) → keep verifier/reward scores
  advisory. *Evidence: Moderate–Strong.*
- **A40897** — ConfGuard: token-confidence sequence-lock detector; dataset-dependent FPR up to ~21.95% → measure
  over-refusal. *Evidence: Moderate.*
- **A41074 / A42191 / A41140** — AlignTree / RAS / HumorReject: over-refusal as a first-class metric and material
  residual ASR after detection (A42191 51.86→31.27%). *Evidence: Moderate; non-adaptive.*

Supporting: A40301 (embedding-manifold OOD detect-and-correct), A40366 (Mahalanobis+spectral detector), A40891
(perturb-and-compare confidence-drift, needs only I/O), A40607 / A40863 (multimodal softer than text), A41099
(semantics-preserving financial-text attack), A40353 (Fact2Fiction evades paraphrase/clustering/perplexity
detectors), A38127 (hiding the signal is not a boundary, O(1/T²)), A38340 (spoofable explanations), A38853
(invertible activations — outputs are capability, not verification), A40445 / A40486 / A40833 (reasoning-token
telemetry vs. accuracy-preserving DoS), A40248 (residual harm; enforce safety deep), A40399 (Educational-Refusal
tier; scaling paradox), A40543 (WALKSAFE; reduce over-refusal), A40018 (cross-modal sub-image decomposition),
A40554 (MAJIC; query-efficient adaptive jailbreak — detection cannot rely on query-volume anomaly), A37474
(SATED; an LLM verifier inherits the component's own attack surface),
A41468 / A41090 (detector is one layer; LLM-detector injectable; prompt-level detection necessary-but-insufficient).

Reviewer-synthesis cross-references (skill artifacts, **not** AAAI corpus papers): sibling patterns
`prompt-injection-containment.md` (structural "content is data, not instruction" boundary + canonicalization),
`policy-permission-gates.md` (the deterministic allow/deny/step-up decision the detectors feed),
`tool-capability-isolation.md` / `sandboxed-execution.md` (blast-radius limits downstream),
`human-approval-consequential-actions.md` (escalation on detector uncertainty), `tamper-evident-traces.md`
(trace integrity), `backdoor-detection.md` (training-time trigger detection, out of scope here),
`model-extraction-defenses.md` (query-monitoring for extraction).

## Evidence strength

- **The central cautionary thesis is Strong and independently replicated.** "A stack of per-component-robust
  input+output detectors collapses under a whole-pipeline adaptive attack, via the output-repetition channel" is
  demonstrated by two independent papers (A41108, A41144) that converge on the *same concrete channel* — the
  corpus explicitly calls this "an independently replicated concrete weakness" (Adversarial §9.9). This is
  stronger than mere design convergence.
- **The design principles are well-supported by convergence, not replication.** "Normalize before you detect",
  "detect over the whole context and every modality", "keep detector verdicts advisory into a deterministic
  gate", and "measure over-refusal" converge across many independent studies in different domains (A40296/A40465/
  A41058/A40916; A40840/A36996; A40866/A40584/A38340; A41074/A41140/A41152/A42191) — a strong *design* signal,
  not a measured effect size.
- **Any specific detector's efficacy is Preliminary-to-Moderate.** A41498 is Preliminary (non-adaptive,
  in-distribution, mostly synthetic); A41152, A40866, A40920, A41074, A42191 are Moderate and non-adaptive; A37350
  is the strongest single detector (adaptive + OOD evaluation) but still author-reported. Several headline numbers
  were truncated in the source extracts and are flagged.
- **All efficacy numbers are author-reported, not independently verified, and best-case.** No adaptive-attacker
  evaluation exists for most detectors here; the two strongest agent-relevant results are *attacks*, not defenses.
  Report absolute residuals and validate on the target stack before operational reliance.
- **Deterministic, fail-closed, advisory-only, non-monoculture, normalize-first design choices are
  reviewer-synthesis engineering best practice** grounded in the papers' demonstrated failure modes, not
  themselves a paper-measured result.

## When NOT to use this pattern

- **As the sole control or as the gate itself.** Every defense card in both syntheses ends with "should be a
  layer, not the sole control"; a stacked detector layer is the corpus's most clearly-broken control under
  adaptive attack (A41108, A41144). Pair with the deterministic decision gate (`policy-permission-gates.md`),
  structural containment (`prompt-injection-containment.md`), least privilege (`tool-capability-isolation.md`),
  human approval, and adaptive red-team.
- **As a substitute for structural trust-boundary isolation.** Detecting instruction-shaped text is not the same
  as keeping untrusted content classified as *data, never instruction* — that is `prompt-injection-containment.md`.
  A detector over un-isolated content is fighting the wrong battle (A41090, A41468).
- **When the risky channel/modality can simply be removed or not emitted.** If a system need not read a modality
  or produce a content class, don't ingest/emit it and then detect it — coverage you don't need is attack surface
  you don't need (reviewer synthesis; A40841 frame-sampling as coverage).
- **When you would be forced to make an LLM judge the sole authority** with no deterministic gate behind it — the
  judge is injectable (A41468 reviewer synthesis) and evaluator-gamable (A40866); keep it advisory or don't rely
  on it.
- **For training-time backdoor/trigger detection** — that is `backdoor-detection.md`; runtime I/O content
  detection does not catch dormant, fine-tuning-activated, or accuracy-preserving backdoors (A39480, A40295,
  A40486 from `Adversarial-ML-Attacks.md`).
- **For fully reversible, low-stakes actions where detector latency/over-refusal cost exceeds the harm** — reserve
  strict fail-closed detection for high-stakes/irreversible operations (A41090 high-risk task class), and measure
  over-refusal as a first-class cost (A41074, A41140, A41152, A40897).
