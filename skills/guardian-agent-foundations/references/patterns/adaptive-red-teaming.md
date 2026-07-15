# Pattern: Adaptive Red Teaming

> **Scope of evidence.** This pattern is grounded in the AAAI-26 corpus syntheses `AILLM-Safety.md` and
> `Adversarial-ML-Attacks.md` and their underlying research cards. It is the **assurance / verification meta-control**
> that validates every other pattern in this directory: the process of evaluating a deployed defense with an
> attacker that *adapts to that specific defense*, as a fail-closed launch gate and a continuously-maintained
> program — *not* a runtime enforcement mechanism (those are `policy-permission-gates.md`,
> `prompt-injection-containment.md`, `input-output-detection.md`, `tool-capability-isolation.md`, etc.). Its
> subject is the evaluation methodology, not a classifier or a gate.
>
> **The load-bearing thesis.** Both syntheses converge, independently, on one methodological finding rated their
> highest-confidence meta-result: **static, non-adaptive defense evaluation dominates the field, and wherever an
> attacker is allowed to be defense-aware, the defense degrades or fails** (Adversarial §1, §9.1; AILLM §1, §16,
> §17 — "the near-total absence of adaptive-attacker evaluation of defenses"). Nearly every attack paper evades
> only *fixed pre-existing* defenses, and nearly every defense paper *concedes* an adaptive adversary was not
> tested. Adaptive red teaming is the control that closes this gap.
>
> Load-bearing papers: **A41108** (STACK — staged whole-pipeline guard-stack bypass, ~0%→71% ASR black-box /
> 33% transfer, author-reported, released code; the guard-stack *evaluation standard*), **A41144** (MFA —
> independently replicates STACK's output-repetition channel across 17 open+commercial VLMs, 58.5% overall
> author-reported), **A40905** (CFW/WRK — *builds a purpose-built adaptive remover* rather than testing only
> standard defenses; "sets the methodological bar", Adversarial §11/§18), **A37117** (Authority Backdoor —
> honestly reports its naive design is *broken by an adaptive trigger-inversion attacker*, then fortifies with
> randomized smoothing; the cleanest adaptive-attack methodology, reversed-accuracy 9.25% ≈ clean 9.47%
> author-reported), **A39290** (Pill — authors an adaptive defense and honestly reports it insufficient, >90%
> bypass across 9 rules), **A37350** (EigenShield — the one AILLM defense evaluated in standard + *adaptive* + OOD
> settings, with honest asymptotic-guarantee caveats), **A40551** (SOM — reported bypass of a *deployed*
> representation defense, Circuit-Breakers/RR), **A40866** (SceneJailEval — the corpus's best-judge attempt,
> itself untested against evaluator-gaming), **A40584** (Process-Reward-Models score invalid steps high, 0.973 —
> your scorer is gameable), **A41118 / A40855 / A40898** (exemplar *honest negative results*). Coverage anchors:
> **A40895/A40898** (MCP tool poisoning), **A40353/A40893** (RAG poisoning), **A40840/A36996** (history
> injection), **A41090/A41468** (agentic indirect injection), **A40445/A40486/A40833** (reasoning-DoS),
> **A39480/A40295** (post-finetuning / persistent backdoors), **A40881/A42439** (physical/sensor).
> Supporting: A40787, A38328, A42327, A37118, A39997, A37010, A41146, A41170, A39428, A38340, A38127, A40554,
> A41058, A40465, A40919, A37203, A38761, A38949, A38785, A37716, A40915, A38015, A40894, A41141, A41164.
>
> **Evidence integrity (non-negotiable).** Every quantitative claim below is **author-reported and not
> independently verified**; several headline numbers sat in table regions the source extracts marked truncated and
> are flagged. Where a card was silent the text says "not stated in paper". Numbers are tagged author-reported
> vs. *(reviewer synthesis)*. Calibrated language only — "reduced ASR against the tested attacks under the
> evaluated threat model", "requires production validation" — never "secure / proven-safe / eliminates". Adaptive
> red teaming *reduces the risk of shipping a silently-broken defense*; it does **not** prove a system safe, and
> no defense in either corpus offers certified robustness against an unbounded adaptive adversary (Adversarial §1).

---

## Problem addressed

A defense that passes its own evaluation is routinely broken the moment the attacker is allowed to see it. This is
the corpus's single most-replicated finding, and it is a methodology problem, not a defense problem:

- **Per-component-robust stacks collapse under a whole-pipeline adaptive attack.** STACK (A41108) drives a
  few-shot guard pipeline that passes per-component evaluation from ~0% to **71% ASR black-box** (33% transfer,
  author-reported); MFA (A41144) independently drives a jailbreak past alignment + system prompt + input/output
  moderation to **58.5% overall** (author-reported, 17 VLMs, real moderators). Both exploit the *same* channel —
  inducing the model to emit an attacker-chosen string past the output classifier (Adversarial §9.9, "an
  independently replicated concrete weakness"). Neither weakness is visible without a *whole-pipeline, defense-aware*
  test.
- **Defenses evaluated only against fixed prior attacks miss the attacker who targets *them*.** Robust FL
  aggregation is bypassed by structured poison inside the trusted region — A40787 (ShadeEdit) evades 8 aggregators
  at ~99.5% avg ASR; A39290 (Pill) bypasses >90% across 9 rules *and its own authors' adaptive defense is
  insufficient*; A38328 (boundary-adaptive); A42327 keeps detection ≤1.5% while collapsing accuracy (all
  author-reported). Backdoor detectors are bypassed because they inspect the wrong artifact — A39480's dormant
  backdoor evades 7 detectors (Neural Cleanse, STRIP, GangSweep, TND-DL/DF, CBD, CleanCLIP) by hiding in the
  *pre-finetuning* model. Watermark defenses fall to purpose-built removers (A40905 WRK reduces WSR ≥88.79%;
  A39997 near-100% overwrite; A37010 BER 0.50%→38.17%; A41146). Anti-personalization "cloaks" fall to trivial
  purification (A41170, "Fragile by Design"). Explanation-based oversight is spoofable (A38340). All author-reported.
- **The evaluation itself is gameable.** ASR is almost always scored by a single automated LLM judge with no
  reported human agreement, sometimes *circular* — an attack optimizing against the very detector class it is
  scored with (A40916; AILLM §12). Process-Reward-Model scorers rate logically-invalid steps high (A40584, an
  impossible constraint scored 0.973 author-reported). A "better judge" (A40866, SceneJailEval, F1 0.917 own /
  0.995 JBB author-reported) is itself LLM-agent-based and untested against evaluator-gaming. A red-team that
  trusts a gameable oracle measures nothing.

**Adaptive red teaming** is the engineering control that treats *defense-aware, adaptive adversarial evaluation on
absolute residuals with a trustworthy oracle* as a **fail-closed launch gate and a continuously-maintained
program** — so that a defense's reported efficacy is an estimate of real protection, not a best-case artifact of a
static test.

## Applicable assets and attack surfaces

Adaptive red teaming is applied *to* the defended system's controls, and must cover every surface the corpus shows
is attackable. The assets under test:

- **Guard / moderation stacks** (input + output classifiers, alignment, system prompt) as *one pipeline* —
  A41108/A41144 show per-component tests miss the joint bypass and the output-repetition channel.
- **Representation-level / activation-space defenses** — A40858 (ActMan) minimizes the very MMD signal A40887/
  A40607/A40553 rely on; A40551 reports bypassing a deployed Circuit-Breakers/RR defense; A41119/A41148 defeat
  single refusal-direction hardening. The residual stream is a shared surface for defense *and* attack (AILLM §11,
  §17 "the representation-monitor vs. activation-attack collision").
- **Agent / tool / MCP layer** — tool-description poisoning as a confused-deputy vector (A40895 MCPTox, peak
  72.8% on o1-mini, <3% refusal even on Claude-3.7-Sonnet; 45 servers / 353 tools / 1348 cases / 20 agents,
  author-reported), selection-biasing metadata (A40898 MPMA, DPMA 100% ASR in most settings), inter-agent
  message-bus MITM (A40224 MAST), indirect prompt injection in environment/tool content (A41090
  MobileSafetyBench; A41468 InfrastructureSentinel enumerating the fullest MCP threat surface).
- **RAG / retrieval corpora** — decomposition-mirroring poisoning at ~0.1% poison (A40353 Fact2Fiction, evading
  paraphrase / K-means / perplexity filtering), joint retriever+generator poisoning (A40893 Joint-GCG).
- **Conversation history / memory** — forged prior "assistant" turns (A40840 Response Attack, RA-DRI avg ASR
  94.8% across 8 models; A36996 CHASE cross-model transfer, author-reported).
- **Reasoning / availability** — accuracy-preserving reasoning-DoS (A40445; A40486 ~17× on MATH-500; A40833 on
  o3 via indirect injection) that content/accuracy monitors never see.
- **Supply chain (training / fine-tuning / preference data)** — backdoors that survive or are *reinforced by*
  clean fine-tuning (A40295 P-Trojan >99% persistence; A39809; A40855 residual pose offset), dormant until the
  victim's own fine-tuning (A39480, A39593), and preference-data poisoning (A41087 min-cost label-flip; A41118
  AdvBDGen ~3% poison). Requires *post-finetuning* red-teaming (Adversarial §15) and scanning for *multiple
  coexisting* backdoors (A38015), not one.
- **Multimodal & physical channels** — image/audio/video (A40607, A40863, A40841 video omission >90% HOR,
  A41086 embedded image text), and physical/sensor actuation (A40881 Phantom Menace, 8 sensor-injection attacks
  validated on a real Franka arm; A42439 PhysPatch, ~1%-area patch on 12 commercial/reasoning MLLM-AD stacks).
- **The over-refusal / benign frontier** — the defense's false-positive behavior is an asset to red-team too:
  aggressive controls over-block benign content (A40897 FPR up to ~21.95%; A41074/A41140/A41152/A42191/A40543
  foreground the trade-off, author-reported).
- **The red-team's own oracle** — the judge/verifier is an asset that must itself be adversarially validated
  (A40584 gameable PRM; A40866 untested against gaming; A40916 measurement circularity).

## Threat model

Adaptive red teaming defends against the **meta-threat of a false assurance signal**: a defense that reports high
efficacy under a static test but fails against a real, defense-aware adversary. The adversary classes the program
must model, drawn from the corpus:

- **Defense-aware, whole-system attacker.** Knows the deployed defense's design and configuration and stages a
  chained attack against the *specific* pipeline (A41108 STACK, A41144 MFA — both release code; assume attackers
  have it). This is the class static per-component evaluation structurally cannot catch.
- **Learned / online-adaptive attacker.** RL / policy-driven strategy selection that adapts per-query: A40554
  (MAJIC, Markov + Q-learning, >90% ASR at <15 queries), A41058 (MetaCipher, multi-agent RL, 60%+ within ≤10
  queries), A37203 (CognitiveAttack, SFT+PPO rewriter, 30-model breadth, ASR 60.1% vs PAP 31.6%), A40919
  (Reason2Attack), A41118 (AdvBDGen adaptive backdoor), A40176 (MARL adaptive agent-selection) — all
  author-reported. Query-efficiency means "many-query anomaly detection" is not a substitute for adaptive
  evaluation (AILLM §9.5).
- **Purpose-built breaker of a specific defense.** An attacker constructed *against the exact defended artifact*,
  not a generic attack — the A40905/A40915 methodological bar (build the adaptive remover/forger), A37117's
  adaptive trigger-inversion attacker, A40551's bypass of a deployed representation defense.
- **Oracle-gaming attacker.** Optimizes output to fool the judge/verifier the red-team scores with (A40916
  circularity; A40584 PRM 0.973 on an invalid step; A40866 untested against gaming; A38340 spoofed explanation).
- **Coverage-gap attacker.** Uses a surface, modality, encoding, or lifecycle phase the red-team did not exercise
  — a novel cipher/glyph outside normalizer coverage (A41058, A40916), a modality the suite skipped (A40841,
  A41086, A40863), or a *post-finetuning* dormant backdoor a pre-finetuning scan cannot see (A39480, A40295).
- **Snapshot-drift attacker.** Exploits that a commercial model or a defense config changed since the last
  red-team run (commercial-model version drift, A40445/A40726/A40833/A40877); yesterday's pass is not today's.

**Out of the red-team's power (be honest):** it *reduces* the chance of shipping a broken defense; it cannot prove
robustness against an unbounded adaptive adversary. Only narrow formal results exist (A37716 attack-agnostic
certified patch robustness bounded by a *known* patch size; A37117 randomized-smoothing ℓ2 radius; A40915 forging
bound < 1/2^128 at n=256), each within a narrow threat model — none certified against an unbounded adaptive adversary
(Adversarial §1). Treat every red-team pass as "no break found under the tested adaptive attacks", never "safe".

## Control mechanism

Adaptive red teaming is a **deterministic, fail-closed assurance loop** with six composed mechanisms:

1. **Enumerate the defense and its surfaces, then make the attacker defense-aware.** Give the red-team the
   deployed defense's design and configuration and require it to target *that* system, not a generic guard — the
   whole-pipeline methodology of A41108/A41144, the purpose-built-breaker bar of A40905/A37117. A generic,
   defense-blind attack that passes proves nothing (Adversarial §9.1).
2. **Include learned/adaptive and co-evolutionary attackers, not only fixed suites.** RL/online-adaptive attackers
   (A40554, A41058, A37203, A40919, A41118) and attacker↔defender co-evolution (A38761 Gittins-index optimal
   adaptive attacker; A38949/A38785 learned adversaries; A41141 CAPTCHA co-evolution as an open benchmark).
3. **Score on a trustworthy, non-gameable oracle — never a single LLM judge alone.** Validate the judge against
   human agreement; use effect/state-based evaluators where an action is guarded (A41090 rule-based state
   evaluators inspecting action history / storage / app DBs); assume the judge is injectable and gameable
   (A40584, A40866, A40916). Multi-judge + human agreement, not measurement circularity.
4. **Report absolute residuals and over-refusal, not relative reductions.** The output is *residual* ASR under the
   adaptive attack (A42191 51.86→31.27%, i.e. ~31% residual; A40248 ~16.4% residual on Qwen-3-8B; A41468 hardest
   classes >50% / >76% miss — all author-reported) *and* the false-positive/over-refusal rate against an adaptive
   benign-ambiguous set (A41074, A41140, A41152, A40897, A40543).
5. **Gate the launch fail-closed on the result.** No defense ships without an adaptive, defense-aware red-team;
   a residual above the operator's budget, an unvalidated oracle, or a coverage gap → do not ship, or ship only
   with compensating controls (least privilege + human approval + audit), because residual harm is assumed
   (A41090, A41468; AILLM §16 "adaptive red-teaming is a launch gate, not a nice-to-have").
6. **Run continuously and feed findings back.** Attackers adapt and models/configs drift; the suite is a
   maintained, versioned regression corpus that grows with every new attack and every incident (Adversarial §16;
   AILLM §16), with the harness itself contained because the tooling is dual-use (A41164, A40895/A40898, A41058).

The runtime enforcement this program *validates* lives in the sibling patterns; adaptive red teaming owns the
*evaluation methodology and the launch gate* only.

## Preconditions and trust assumptions

The pattern is only meaningful where these hold; each is a documented failure point:

- **The red-team is genuinely defense-aware.** It must know the deployed defense's design and config and target it
  specifically. A defense-blind or generic attack systematically overstates robustness (Adversarial §9.1; the
  whole-pipeline requirement of A41108/A41144).
- **The scoring oracle is trustworthy and validated against human agreement.** A single automated LLM judge, a
  reward/verifier score, or a circular self-scoring setup is not a valid oracle (A40584 0.973 on an invalid step;
  A40866 untested against gaming; A40916 circularity; AILLM §12). Without a trusted oracle, "0% ASR" is unfounded.
- **Coverage spans every deployed surface, modality, and lifecycle phase.** An un-exercised encoding (A41058,
  A40916), modality (A40841, A41086, A40863), agent/tool path (A40895, A41468), or *post-finetuning* phase
  (A39480, A40295, A38015 multiple backdoors) is a silent bypass the red-team never sees. Coverage is a moving
  target (Adversarial §17 calls for standardized *adaptive* benchmarks — A40894, A40895, A42327 — that do not
  yet exist).
- **Results are absolute and include over-refusal.** Relative-only or best-case "up to X%" reporting hides
  residual harm (Adversarial §8; AILLM §8 "best-case over settings, not worst-case"); the benign frontier must be
  measured against an adaptive benign-ambiguous set (A41074, A41140, A41152, A40897).
- **The harness is contained and least-privileged.** Red-team tooling and released attack corpora are dual-use
  (A41164 AR social engineering; A40895/A40898 MCP attacks; A41058/A41086/A41119 released code) — a governance
  and containment concern (Adversarial §16; AILLM §12, §16), so the harness runs in a sandbox with access control
  (`sandboxed-execution.md`, `tool-capability-isolation.md`).
- **Findings feed back before launch, and the suite is versioned.** A red-team whose results are not acted on, or
  that is a one-time artifact, does not close the gap (Adversarial §16; AILLM §16). Commercial-model/config drift
  makes a stale pass invalid (A40445, A40726, A40833, A40877).
- **A residual/over-refusal budget is defined per deployment.** The corpus provides *no validated universal
  threshold* and many headline tables were truncated in extraction; thresholds are operator-defined and must be
  validated on the target system (reviewer synthesis, consistent with Adversarial §12, AILLM §12).

## System architecture

Adaptive red teaming is a program wrapped around the defended system and its release process — a fail-closed gate
feeding a maintained regression corpus and a feedback loop into the defenses:

```
 defended system ─┐
 + DEFENSE CONFIG  │        the attacker is given the design/config → defense-AWARE, not generic
 (all layers)      ▼                                                   (A41108/A41144 whole-pipeline; A40905/A37117 breaker)
        [1] Enumerate assets & surfaces  ── guard stack, rep-space, MCP/tool, RAG, history, reasoning,
                  │                            supply-chain (post-finetune), multimodal, physical, over-refusal frontier
                  ▼
        [2] Defense-aware attack generation ── released suites (assume attacker has them) + learned/RL/online-adaptive
                  │                              (A40554,A41058,A37203) + purpose-built breaker per defense (A40905,A37117)
                  ▼                              + co-evolution (A38761,A38949,A41141)
        [3] Execute in CONTAINED sandbox  ── dual-use tooling isolated & access-controlled
                  │                            (sandboxed-execution.md, tool-capability-isolation.md)
                  ▼
        [4] Trustworthy scoring  ── multi-judge + HUMAN agreement + effect/state-based evaluators (A41090);
                  │                   assume the judge is gameable/injectable (A40584,A40866,A40916)
                  ▼
        [5] Report ABSOLUTE residual ASR + over-refusal ── not relative reductions
                  │                                          (A42191,A40248,A41468 residuals; A41074/A40897 FP)
                  ▼
        [6] LAUNCH GATE (fail-closed) ── residual>budget | oracle unvalidated | coverage gap → DO NOT SHIP,
                  │                        or ship only w/ compensating controls (human-approval + least-privilege + audit)
       ┌──────────┴───────────┐
       ▼                      ▼
  feedback → defenses    versioned regression corpus  ── every finding + incident becomes a permanent case
  (all sibling patterns)  + tamper-evident trace          (Adversarial §16; AILLM §16; tamper-evident-traces.md)
       └──────────► re-run continuously (config/model drift invalidates stale passes: A40445/A40833) ◄──────────┘
```

- **The attacker is inside the loop, not outside it.** The defining architectural choice: the red-team receives
  the defense config and adapts to it (Adversarial §9.1). Everything downstream depends on this.
- **The oracle is a first-class, adversarially-validated component**, never an afterthought — its compromise
  silently invalidates the whole program (A40584, A40866, A40916).
- **The gate is deterministic and fail-closed**; the red-team supplies evidence, the release process makes the
  ship/no-ship decision on absolute residuals against a defined budget.
- **The harness is contained** because it *is* offensive tooling (`sandboxed-execution.md`; dual-use, Adversarial
  §16).

## Recommended implementation pattern

Deterministic, fail-closed, least-privilege — in priority order:

1. **Make the attacker defense-aware and whole-system.** Hand the red-team the deployed defense design/config and
   require it to target the *specific* pipeline end-to-end — reproduce the STACK/MFA whole-pipeline methodology
   including the output-repetition channel (A41108, A41144, both release code). Reject any "robust vs SOTA
   defenses" claim that used a generic, defense-blind attack (Adversarial §9.1, §16).
2. **Build a purpose-built breaker for each defense, and report honest negatives.** Emulate the A40905/A40915 bar
   (construct the adaptive remover/forger) and the A37117 discipline (report that the naive design is broken, then
   fortify). Treat honest negative results as first-class deliverables (A41118 latent-adversarial-training
   mitigates its own backdoor; A40855 residual offset persists; A40898 over-manipulation backfire; A39290 the
   authors' own adaptive defense is insufficient) — a red-team that never reports a break is a broken red-team.
3. **Include learned / online-adaptive / co-evolutionary attackers.** RL and policy-driven strategy selection
   (A40554, A41058, A37203, A40919, A41118) and attacker↔defender co-evolution (A38761, A38949, A38785, A41141),
   because low-query adaptive attacks defeat many-query anomaly detection (A40554 >90% at <15 queries; A41058 60%+
   within ≤10 — author-reported).
4. **Validate the oracle before you trust any ASR.** Use a multi-signal judge with *human agreement*, and
   effect/state-based evaluators where an action is guarded (A41090 rule-based state evaluators). Never sign off on
   a single automated LLM judge; guard against measurement circularity (A40916) and verifier gaming (A40584 0.973;
   A40866 untested against gaming). Log the judge provenance as advisory, never ground truth.
5. **Cover every surface, modality, and lifecycle phase — especially post-finetuning.** Red-team the guard stack,
   representation-space defenses, MCP/tool layer (A40895, A40898, A41468), RAG (A40353, A40893), history (A40840,
   A36996), reasoning-DoS (A40445, A40486, A40833), multimodal (A40841, A41086, A40863), and physical/sensor
   (A40881, A42439). Add *post-finetuning* red-teaming to onboarding — dormant backdoors are invisible
   pre-finetuning (A39480, A39593) — and scan for *multiple* coexisting backdoors, not one (A38015).
6. **Report absolute residuals and over-refusal, not relative deltas.** Publish residual ASR under the adaptive
   attack (A42191 ~31%, A40248 ~16%, A41468 >50%/>76% on hardest classes — author-reported) and the
   false-positive rate against an adaptive benign-ambiguous set (A41074, A41140, A41152, A40897, A40543).
7. **Gate the launch fail-closed on a defined budget.** No adaptive red-team, an unvalidated oracle, a coverage
   gap, or residual above budget → do not ship, or ship only with compensating controls (human approval + least
   privilege + immutable audit), because residual harm is assumed (A41090, A41468).
8. **Contain and access-control the harness.** Run offensive tooling in a sandbox (`sandboxed-execution.md`,
   `tool-capability-isolation.md`); treat attack corpora as dual-use assets with restricted distribution
   (Adversarial §16; AILLM §16).
9. **Make it continuous and versioned.** Every finding and every production incident becomes a permanent
   regression case; re-run on model/config drift (A40445, A40726, A40833, A40877). Log runs into a tamper-evident
   trace (`tamper-evident-traces.md`).
10. **Feed findings back into the defenses.** The output is not a report; it is patched controls in the sibling
    patterns plus a hardened suite (Adversarial §16; AILLM §16). Adaptive red teaming is a maintained control, not
    an audit event.

## Incorrect or fragile implementation patterns

- **Non-adaptive / defense-blind evaluation presented as robustness.** The corpus's central cautionary result:
  attacks evade only fixed defenses and defenses concede adaptive robustness is untested (Adversarial §9.1;
  AILLM §17). "Robust against SOTA defenses" with a generic attack is *non-adaptive* and overstates security.
- **Per-component testing of a stacked defense.** Misses the whole-pipeline joint bypass and the output-repetition
  channel (A41108 0%→71%; A41144 58.5%, author-reported).
- **Testing against fixed prior attacks instead of an attacker who targets your defense.** FL aggregators (A40787,
  A39290, A38328, A42327), backdoor detectors (A39480), and watermarks (A40905, A39997, A37010, A41146) all pass
  standard tests and fall to purpose-built adaptive attacks.
- **Trusting a single automated LLM judge / a reward or verifier score.** Gameable (A40584 0.973 on an invalid
  step), injectable (A41468 reviewer synthesis, AILLM §15), circular (A40916), untested against gaming (A40866).
- **Reporting relative reductions or best-case "up to X%".** Hides material residual harm (A42191 ~31%, A40248
  ~16%, A41468 >50%); the corpus repeatedly flags "up to X%" as best-case, not worst-case (Adversarial §8; AILLM §8).
- **Pre-finetuning-only supply-chain scanning.** Dormant backdoors are invisible until the victim's own
  fine-tuning (A39480, A39593); clean fine-tuning can *reinforce* a backdoor (A40295 >99% persistence). Scanning
  once, for one backdoor, misses coexisting implants (A38015).
- **Ignoring over-refusal.** A defense tuned to pass ASR while over-blocking benign content is unusable or is
  tuned down into a wider attack window (A40897 up to ~21.95%; A41074/A41140/A41152/A42191/A40543).
- **A one-time red-team.** Attackers adapt and configs/models drift (A40445, A40726, A40833, A40877); a stale
  pass is not a current guarantee.
- **An uncontained harness / careless corpus release.** Offensive tooling is dual-use (A41164, A40895/A40898,
  A41058/A41086/A41119); leaking it lowers the attacker's barrier (Adversarial §16; AILLM §16).
- **Presenting a red-team pass as proof of safety.** No corpus defense is certified against an unbounded adaptive adversary
  (Adversarial §1); a pass means "no break found under the tested attacks", nothing stronger.

## Verification strategy

Verifying the *red-team program itself is adequate* (meta-verification):

- **Reproduce known adaptive breaks as a calibration harness.** Confirm your program *rediscovers* the STACK/MFA
  whole-pipeline bypass on a deliberately-stacked guard (A41108, A41144, both release code), the A40551 bypass of a
  representation defense, and the A39480 dormant-backdoor evasion of standard detectors. A program that cannot
  rediscover published breaks will not find novel ones.
- **Require a purpose-built breaker per defense.** Verify each defense was attacked by an adversary constructed
  *against it* (the A40905/A40915/A37117 bar), not only against fixed prior defenses (Adversarial §11, §18).
- **Adversarially validate the oracle.** Confirm the judge is not gameable or circular — test it against
  evaluator-gaming (A40866 gap), verifier-gaming (A40584), and a self-scoring circularity check (A40916); require
  human-agreement statistics.
- **Audit coverage against the surface inventory.** Verify every deployed surface/modality/lifecycle phase in
  "Applicable assets" has at least one adaptive case, and that *post-finetuning* and *multiple-backdoor* cases
  exist (A39480, A38015). Track and close coverage gaps as findings.
- **Report absolute residuals and over-refusal, with human-agreement-validated scoring** (A42191, A40248, A41468
  residuals; A41074/A40897 over-refusal). Effect/state-based evaluation where an action is guarded (A41090).
- **Demand honest negatives.** A program with no reported breaks is presumptively non-adaptive; the exemplar
  discipline is A37117 (report the naive design is broken, then fortify), A41118/A40855/A40898/A39290 (report the
  limitation).
- **Re-run on drift.** Verify the suite re-executes on model/config change (A40445, A40726, A40833, A40877), not
  only at first launch.

## Metrics and thresholds

Track these families; **thresholds are operator-defined per deployment and must be validated on the target system
— the corpus provides no validated universal threshold, and several headline tables were truncated in the source
extracts.** All figures below are author-reported best-case, cited as *bars to beat*, not targets to certify.

- **Residual ASR under the *adaptive* attack (absolute, whole-pipeline).** The bar comes from the breaks: A41108
  STACK ~0%→**71%** black-box / 33% transfer; A41144 MFA **58.5%** overall / 52.8% commercial / 72.92% all-facets;
  A40787 ShadeEdit ~**99.5%** across 8 aggregators; A39290 Pill >**90%** across 9 rules; A40895 MCPTox peak
  **72.8%** on o1-mini; residual floors A42191 **~31%**, A40248 **~16%**, A41468 hardest classes >**50%** /
  >**76%** (all author-reported). A program that reports only per-component or non-adaptive ASR is not measuring
  the real threat.
- **Over-refusal / false-positive rate (first-class), against an adaptive benign-ambiguous set.** A40897 FPR up
  to **~21.95%**; A41074 low benign over-refusal with a large ASR drop (e.g. Qwen2.5-0.5B 91.0→4.0 on MalwareGen);
  A42191 refusal 41.31→62.76% alongside ASR 51.86→31.27% (all author-reported, non-adaptive).
- **Query-budget-to-break.** A low budget defeats query-volume anomaly detection: A40554 >90% at **<15 queries**;
  A41058 60%+ within **≤10 queries**; A40465/A40919 single query (author-reported). Report the budget at which
  each attack succeeds.
- **Coverage ratio** — fraction of deployed surfaces / modalities / lifecycle phases with at least one adaptive
  case (motivated by the coverage-gap threat; Adversarial §17 notes standardized adaptive benchmarks do not yet
  exist for A40894/A40895/A42327). An uncovered surface is an unmeasured bypass.
- **Oracle quality vs human agreement** — judge F1/accuracy *paired with* human-agreement statistics (A40866 F1
  0.917 own / 0.995 JBB author-reported, but itself untested against gaming); never a judge score alone.
- **Persistence-through-lifecycle** — backdoor survival across clean fine-tuning (A40295 >99%; A39809; A40855) and
  dormancy-until-finetune (A39480) as an onboarding gate metric.
- **Regression-suite growth and re-run cadence** — number of permanent cases added per incident; time-to-re-run on
  model/config drift (A40445, A40726, A40833).

## Test cases

Concrete, corpus-grounded adaptive cases the program must include:

1. **Whole-pipeline staged jailbreak** against the deployed guard stack, incl. the output-repetition channel
   (A41108 STACK; A41144 MFA).
2. **Purpose-built breaker of a representation-space defense** — minimize the exact monitored signal (A40858
   ActMan vs MMD monitors), ablate the refusal manifold / hydra circuit (A40551, A41119, A41148).
3. **MCP / tool-layer confused-deputy** — poisoned tool description hijacking a legitimate high-privilege tool
   (A40895 MCPTox), selection-biasing metadata (A40898 MPMA), inter-agent bus MITM (A40224 MAST).
4. **Agentic indirect prompt injection** planted in environment/tool content the agent reads (A41090
   MobileSafetyBench; A41468 InfrastructureSentinel threat classes).
5. **RAG corpus poisoning** at low poison fraction, evading paraphrase/clustering/perplexity filters (A40353
   Fact2Fiction ~0.1%; A40893 Joint-GCG).
6. **History / memory injection** — forged prior "assistant" turns (A40840 RA-DRI avg ASR 94.8%; A36996 CHASE
   cross-model transfer).
7. **Accuracy-preserving reasoning-DoS** that keeps the answer correct while inflating cost (A40445; A40486 ~17×
   on MATH-500; A40833 on o3 via indirect injection).
8. **Post-finetuning dormant / persistent backdoor** — a payload invisible pre-finetuning and surviving or
   reinforced by clean fine-tuning (A39480 evades 7 detectors; A40295 >99% persistence; A38015 multiple backdoors).
9. **Preference / alignment-data poisoning** — min-cost label-flipping and adaptive stealthy backdoors (A41087;
   A41118 ~3% poison, with the honest LAT-mitigation negative).
10. **Physical / sensor attack** where the system actuates on perception (A40881 sensor injection on a real arm;
    A42439 physical patch on MLLM-AD stacks).
11. **Surface-form / encoding evasion outside normalizer coverage** — emoji/math-code/cipher/cross-lingual
    (A40296, A40465, A41058, A40916).
12. **Oracle-gaming / measurement-circularity probe** — output crafted to fool the scoring judge/verifier (A40584
    PRM, A40866 gap, A40916 circularity, A38340 spoofed explanation).
13. **Benign-ambiguous over-refusal probe** — content the defense should *not* block, to measure FP cost (A41074,
    A41140, A41152, A40897, A40543).

## Adaptive adversarial tests

This whole pattern *is* the adaptive-test discipline; this section raises the bar beyond the standard suite to the
attacker who adapts to *your patched, deployed* defense:

- **Attacker with your exact defense config in hand.** Stage the attack against the specific deployed stack, not a
  generic guard — the STACK/MFA methodology optimized against *your* classifiers (A41108, A41144, released code;
  assume attackers have them).
- **Online-adaptive, low-query strategy selection.** RL/Markov strategy sequencing that adapts per response
  (A40554 >90% at <15 queries; A41058 ≤10 queries; A37203 rewriter) — so detection cannot rely on query-volume
  anomaly.
- **Purpose-built breaker re-targeted after each patch.** When you fortify a defense, rebuild the breaker against
  the fortified version (the A37117 loop: broken → fortify → re-attack; A40905 adaptive remover; A39290 authors'
  own adaptive defense still insufficient).
- **Co-evolutionary attacker↔defender.** Model an optimal, adaptive adversary that best-responds to your policy
  (A38761 Gittins-index; A38949/A38785 learned adversaries; A41141 CAPTCHA co-evolution) rather than a fixed
  attack set.
- **Oracle-adaptive attacker.** Craft output that fools your specific judge/verifier (A40916 circularity, A40584
  PRM 0.973, A40866 untested against gaming) — verify the break survives a human-agreement re-score.
- **Coverage-frontier attacker.** Probe exactly the surface/modality/encoding/lifecycle phase your suite does not
  yet cover (novel cipher outside normalizer coverage A41058/A40916; skipped modality A40841/A41086; post-finetune
  dormant backdoor A39480) — each hit becomes a new permanent regression case.
- **Drift attacker.** Re-attack after a model or config change to confirm the prior pass still holds (A40445,
  A40726, A40833, A40877).

## Telemetry requirements

Emit structured, tamper-evident trace fields for every red-team run and finding (integrity mechanism =
`tamper-evident-traces.md`; consistent with A41468 immutable audit; A40866/A36960 structured trace fields):

- **Per-attempt record** — attack id/version, *target defense id + config/version*, whether the attacker was
  defense-aware, seed, query budget consumed, oracle score + human label + verdict, and the **absolute** outcome
  (A41108/A41144 whole-pipeline; A40554/A41058 query budget).
- **Oracle-provenance record** — which judge/verifier produced each score, flagged advisory and gameable, with
  human-agreement statistics (A40584, A40866, A40916) — never logged as ground truth.
- **Residual and over-refusal ledger** — absolute residual ASR and FP rate per surface (A42191, A40248, A41468
  residuals; A41074/A40897 FP), against the benign-ambiguous set.
- **Coverage ledger** — which surfaces / modalities / lifecycle phases were exercised and which are *gaps*
  (Adversarial §17 missing adaptive benchmarks); coverage misses are candidate zero-days.
- **Honest-negative and limitation log** — reported breaks and known-insufficient defenses (A37117, A41118,
  A40855, A40898, A39290) as first-class, not suppressed.
- **Lifecycle / persistence record** — pre- vs post-finetuning results and backdoor survival across clean
  fine-tuning (A39480, A40295, A40855, A38015).
- **Regression and drift record** — permanent cases added per incident, and re-run outcomes on model/config change
  (A40445, A40726, A40833, A40877).
- **Harness-containment record** — that offensive tooling ran sandboxed and corpora access was controlled
  (dual-use; Adversarial §16).

## Failure handling

- **Fail-closed at the launch gate.** No adaptive/defense-aware red-team, an unvalidated oracle, a coverage gap, or
  residual above the defined budget → do not ship, or ship only with compensating controls (human approval + least
  privilege + immutable audit), because residual harm is assumed (A41090, A41468; AILLM §16).
- **Treat an un-exercised surface as unsafe**, not as passing — a coverage gap is a silent bypass (A41058/A40916
  encodings; A40841/A41086 modalities; A39480 post-finetune). Route the affected capability to least privilege /
  human review until a case exists.
- **Treat an unvalidated or gamed oracle as a hard stop.** If the judge is circular, gameable, or lacks
  human-agreement validation, its "0% ASR" is void (A40584, A40866, A40916) — block sign-off, not the finding.
- **Do not relax the standard to pass.** Latency/cost pressure is handled by scoping the suite, sampling, and
  caching — never by dropping the adaptive attacker or reverting to a single automated judge (reviewer synthesis,
  consistent with Adversarial §9.1).
- **Assume material residual harm even on a pass.** Leading defenses leave residual (A42191 ~31%, A40248 ~16%,
  A41468 >50% — author-reported); pair the pass with least-privilege scoping and human approval on high-stakes /
  irreversible actions (A41090, A41468).
- **Contain a harness compromise.** Because the tooling is offensive and dual-use (A41164, A40895/A40898, A41058),
  a leak or misuse of the harness/corpus is an incident in its own right (Adversarial §16; `sandboxed-execution.md`).

## Rollback and containment

- **Roll the *defense* back or tighten it when the red-team finds a break** — the finding gates the release before
  the side effect ships, not after (A41108/A41144 breaks caught pre-launch; A41468 runtime gate downstream). A
  break found post-launch triggers rollback of the affected control to least privilege / deny on high-stakes
  actions (`policy-permission-gates.md`, `tool-capability-isolation.md`).
- **Quarantine the bypass class** — when an adaptive bypass is found (a new encoding, a repetition-channel variant,
  a monoculture-transfer input, a dormant backdoor), disable/tighten the affected path and route to human review
  until the defense is patched and a regression case exists (Adversarial §16 refinement loop).
- **Add every finding and incident as a permanent regression case** — the suite grows monotonically; a fixed break
  must never silently regress (Adversarial §16; AILLM §16).
- **Contain the offensive tooling and corpora** — sandbox the harness and access-control the attack corpora
  (dual-use; Adversarial §16; AILLM §16), so containment of the *red-team* is part of containment of the *system*.
- **Blast-radius limits downstream compensate for residual** — least-privilege capability isolation, sandboxed
  execution, and human approval bound what a not-yet-found bypass can trigger (`tool-capability-isolation.md`,
  `sandboxed-execution.md`, `human-approval-consequential-actions.md`; A41090/A41468 gate-not-replace).
- **Immutable, tamper-evident trace for forensics** — the per-attempt record and oracle provenance support
  reconstructing which defense was bypassed and how (`tamper-evident-traces.md`; A41468 immutable audit).

## Known bypasses

Bypasses of the red-team control *itself* — ways a program silently fails to protect (all supporting evidence
author-reported unless noted):

- **Defense-blindness.** The attacker was never given the defense config, so a generic attack "passes" while the
  real defense-aware attack (A41108, A41144, A40551) would break it — the corpus's core failure mode
  (Adversarial §9.1).
- **Per-component scoping.** Testing layers in isolation misses the whole-pipeline joint bypass and the
  output-repetition channel (A41108, A41144).
- **A gamed or circular oracle.** The judge is fooled (A40584 0.973; A40866 untested against gaming) or optimizes
  against the very detector class it scores with (A40916), producing a false "0% ASR".
- **Coverage gaps.** A surface/modality/encoding/lifecycle phase was never red-teamed — post-finetuning dormant
  backdoors (A39480, A40295), skipped modalities (A40841, A41086, A40863), novel encodings (A41058, A40916),
  MCP/tool paths (A40895, A41468).
- **Fixed-prior-defense testing.** Evaluating against standard defenses rather than an attacker built for *your*
  defense (A40787, A39290, A40905, A39997, A41146, A41170 all pass standard tests and fall to purpose-built
  adaptive attacks).
- **Relative-only / best-case reporting.** "Up to X%" or relative reductions hide residual harm (A42191 ~31%,
  A40248 ~16%, A41468 >50%; Adversarial §8, AILLM §8).
- **Snapshot drift.** A stale pass on a since-changed model/config (A40445, A40726, A40833, A40877).
- **One-time / non-continuous execution.** No feedback loop or regression corpus, so fixed breaks regress and new
  attacks are never added (Adversarial §16; AILLM §16).
- **Harness / corpus leakage.** Dual-use tooling escaping containment becomes an attacker asset (A41164,
  A40895/A40898, A41058/A41086/A41119; Adversarial §16).

## Residual risks

- **A pass is not a proof.** No defense in either corpus is certified against an unbounded adaptive adversary (Adversarial
  §1); only narrow formal results exist within narrow threat models (A37716 known-patch-size; A37117 ℓ2 radius;
  A40915 forging bound < 1/2^128 at n=256). A red-team pass means "no break found under the tested adaptive
  attacks", nothing stronger — "requires production validation" applies to every headline number.
- **Coverage is an unbounded moving target.** Standardized *adaptive* benchmarks do not yet exist for whole
  attack classes (Adversarial §17: multi-target backdoors A40894, automated tool-poisoning payloads A40895,
  VFL/SFL consistency A42327; A41141 co-evolution open). An un-imagined surface is unmeasured.
- **The oracle bounds the program.** LLM judges and reward/verifier scorers are gameable and injectable (A40584,
  A40866, A40916, A41468 reviewer synthesis / AILLM §15); human-agreement validation reduces but does not
  eliminate this.
- **Adaptive attackers evolve faster than suites.** Learned/RL, low-query, co-evolutionary attacks (A40554,
  A41058, A37203, A38761) mean today's pass can be tomorrow's break; continuous re-run mitigates but does not
  close the gap.
- **Residual harm persists after a pass.** Leading defenses leave material residual (A42191 ~31%, A40248 ~16%,
  A41468 >50% — author-reported); compensating controls, not the red-team, contain it.
- **Dual-use exposure.** The program's own tooling and corpora lower the attacker's barrier if leaked (A41164,
  A40895/A40898, A41058; Adversarial §16, AILLM §16) — a governance and containment residual.
- **Self-proposed, in-distribution scoring inflates confidence.** Benchmarks used for both tuning and headline
  scoring risk evaluation overfitting (AILLM §12; A40836/A40399/A40866 self-proposed sets) — a red-team can
  overfit its own suite.

## Relevant research (stable paper ids from the syntheses/cards)

Primary (methodology and the load-bearing meta-finding):
- **A41108** — STACK: staged whole-pipeline guard-stack bypass, ~0%→71% black-box / 33% transfer (author-reported);
  the guard-stack *evaluation standard*; released code. *Evidence: Strong (as an evaluation methodology).*
- **A41144** — MFA: independently replicates STACK's output-repetition channel across 17 open+commercial VLMs with
  real moderators, 58.5% overall (author-reported). *Evidence: Strong (independent replication).*
- **A40905** — CFW/WRK: *builds a purpose-built adaptive remover* rather than testing only standard defenses;
  reduces prior watermark WSR ≥88.79% (author-reported); sets the adaptive-evaluation methodological bar
  (Adversarial §11, §18). *Evidence: Strong (as a methodology exemplar).*
- **A37117** — Authority Backdoor: honestly reports its naive design is broken by an adaptive trigger-inversion
  attacker, then fortifies with randomized smoothing (reversed-accuracy 9.25% ≈ clean 9.47%, author-reported); the
  cleanest adaptive-attack discipline in the corpus. *Evidence: Strong (as a methodology exemplar).*
- **A39290** — Pill: authors an adaptive defense and reports it *insufficient*, >90% bypass across 9 FL rules
  (author-reported); models the honest-negative discipline. *Evidence: Strong (as a methodology exemplar).*
- **A37350** — EigenShield: the one AILLM defense evaluated in standard + *adaptive* + OOD settings with honest
  asymptotic-guarantee caveats (author-reported). *Evidence: Strong relative to the corpus; still author-reported.*
- **A40551** — SOM refusal-manifold suppression: reports bypassing a *deployed* representation defense
  (Circuit-Breakers/RR) (author claim). *Evidence: Moderate–Strong (as an adaptive bypass).*
- **A40866** — SceneJailEval: the corpus's best-judge attempt (F1 0.917 own / 0.995 JBB author-reported), itself
  LLM-agent-based and *untested against evaluator-gaming*. *Evidence: Moderate (oracle-validation cautionary).*
- **A40584** — Process Reward Models score logically invalid steps high (0.973 author-reported) → the scorer is
  gameable. *Evidence: Moderate–Strong.*
- **A41118 / A40855 / A40898** — exemplar *honest negative results* (LAT mitigates its own backdoor at ~3% poison;
  residual pose offset persists; over-manipulation backfire). *Evidence: Moderate (methodology discipline).*

Coverage anchors (surfaces the program must red-team):
- **A40895 / A40898** — MCP tool-description poisoning (peak 72.8% on o1-mini; DPMA 100% ASR in most settings,
  author-reported). *Evidence: Strong (A40895, largest-scale) / Moderate (A40898).*
- **A40353 / A40893** — agentic-RAG poisoning at ~0.1% (Fact2Fiction evades paraphrase/clustering/perplexity) /
  joint retriever+generator (Joint-GCG). *Evidence: Strong (A40353) / Moderate.*
- **A40840 / A36996** — history injection (RA-DRI avg ASR 94.8% / cross-model transfer, author-reported;
  A36996 numbers truncated). *Evidence: Moderate.*
- **A41090 / A41468** — agentic indirect prompt injection (MobileSafetyBench rule-based state evaluators;
  InfrastructureSentinel MCP threat taxonomy, ADR coarse/no adaptive testing). *Evidence: Strong (A41090) /
  Preliminary (A41468).*
- **A40445 / A40486 / A40833** — accuracy-preserving reasoning-DoS (~17× on MATH-500; o3 via indirect injection,
  author-reported). *Evidence: Moderate.*
- **A39480 / A40295** — post-finetuning dormant backdoor evading 7 detectors / clean-fine-tuning-reinforced
  backdoor >99% persistence (author-reported). *Evidence: Strong.*
- **A40881 / A42439** — physical/sensor attacks (8 sensor-injection on a real Franka arm; ~1% patch on 12
  commercial MLLM-AD stacks, author-reported). *Evidence: Moderate–Strong (A40881 real-testbed) / Moderate.*

Supporting: A40787 (ShadeEdit, 8 aggregators ~99.5%), A38328 (boundary-adaptive FL), A42327 (in-distribution
cluster-swap, detection ≤1.5%), A37118 (HogVul, +26.05% ASR vs LM vuln detectors), A39997 / A37010 / A41146
(watermark overwrite/removal), A41170 (purification defeats protective cloaks → purification-aware evaluation),
A39428 (adversarial missingness bypasses insertion/perturbation defenses), A38340 (spoofable explanations),
A38127 (hard-label O(1/T²) — hiding the signal is not a boundary), A40554 / A41058 / A40465 / A40919 / A37203
(learned/online-adaptive, low-query attackers), A38761 / A38949 / A38785 (co-evolutionary / learned adversaries),
A37716 / A40915 (narrow formal certification — bounds, not adaptive proof), A38015 (scan for *multiple* backdoors),
A40894 / A41141 (open need for standardized adaptive benchmarks), A41164 (dual-use offensive tooling).

Reviewer-synthesis cross-references (skill artifacts, **not** AAAI corpus papers): this pattern is the launch gate
and continuous-assurance loop for every sibling defense — `input-output-detection.md`,
`prompt-injection-containment.md`, `policy-permission-gates.md`, `retrieval-authorization.md`,
`context-and-memory-isolation.md`, `backdoor-detection.md`, `adversarial-training.md`, `signed-provenance.md`,
`watermarking-fingerprinting.md`, `model-extraction-defenses.md`, `differential-privacy.md` — validated by adaptive
red teaming and hardened from its findings. Its harness runs in `sandboxed-execution.md` /
`tool-capability-isolation.md`; results are logged in `tamper-evident-traces.md`; residuals are compensated by
`human-approval-consequential-actions.md` and `least-privilege-credentials.md`.

## Evidence strength

- **The core thesis is Strong and independently replicated.** "Non-adaptive evaluation systematically overstates
  security; defense-aware attackers degrade or defeat defenses" is the highest-confidence meta-finding of *both*
  syntheses (Adversarial §1, §9.1; AILLM §1, §16, §17), converged on independently across vision, graph, FL,
  watermark, and LLM/agent domains, and concretely demonstrated by the STACK↔MFA independent replication of the
  same whole-pipeline channel (A41108, A41144).
- **The methodology exemplars are Strong-as-exemplars.** A37117 (broken-then-fortified), A40905/A40915
  (purpose-built breaker), A39290 (honest-negative authored defense), and A37350 (standard + adaptive + OOD) are
  the corpus's demonstrated bar for how to red-team adaptively — but each is a single study, author-reported.
- **The specific "how to run the program" prescriptions are reviewer-synthesis engineering practice**, grounded in
  the papers' demonstrated failure modes (defense-blindness, per-component scoping, gamed oracles, coverage gaps,
  relative-only reporting), not a paper-measured effect size.
- **Every efficacy and residual number is author-reported, best-case, and not independently verified**, and several
  headline tables were truncated in the source extracts (flagged throughout). No number here is a target to
  certify; each is a bar the adaptive attacker demonstrated.
- **The control reduces risk; it does not confer a guarantee.** No corpus defense is certified against an
  unbounded adaptive adversary (Adversarial §1); a red-team pass is calibrated as "no break found under the tested
  adaptive attacks", and requires continuous production validation.

## When NOT to use this pattern

- **As a runtime enforcement mechanism.** Adaptive red teaming is *assurance/verification*, not a live gate;
  it does not block a request in production. The runtime controls it validates are `policy-permission-gates.md`,
  `prompt-injection-containment.md`, `input-output-detection.md`, `tool-capability-isolation.md`. Do not deploy
  a red-team *in place of* a defense.
- **As a substitute for building the layered controls.** Every defense card in both syntheses ends with "should be
  a layer, not the sole control"; red-teaming an absent or single-layer defense just confirms it is broken. Build
  defense-in-depth first (Adversarial §15; AILLM §14–15), then red-team it.
- **As a one-time audit event.** A single pass is invalidated by attacker adaptation and model/config drift
  (A40554, A40445, A40726, A40833, A40877); if you cannot maintain it continuously, do not present its result as a
  standing guarantee.
- **With a single automated LLM judge as the only oracle.** If you cannot validate the oracle against human
  agreement and evaluator-gaming, the program's numbers are unfounded (A40584, A40866, A40916) — fix the oracle
  before relying on the red-team.
- **Without harness containment for offensive tooling.** If the harness and dual-use corpora cannot be sandboxed
  and access-controlled (A41164, A40895/A40898, A41058), the program adds attacker-usable capability; contain
  first (`sandboxed-execution.md`; Adversarial §16, AILLM §16).
- **For a fully reversible, low-stakes action where adaptive-RT cost exceeds the harm** — reserve the full
  fail-closed launch gate for high-stakes/irreversible surfaces (A41090 high-risk task class); scope the suite to
  risk, but never drop the *adaptive* attacker for the surfaces that matter.
