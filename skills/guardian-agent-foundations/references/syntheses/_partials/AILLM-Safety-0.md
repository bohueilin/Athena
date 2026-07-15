# AILLM-Safety — Partial Synthesis (chunk 0, 40 papers)

> Scope: AAAI-26 papers filed under corpus label "AILLM-Safety". EVIDENCE INTEGRITY — every claim traces to a
> paper card; author claims vs. reviewer synthesis are distinguished; magnitudes truncated in source extracts are
> flagged "not stated / not visible in paper". Calibrated language throughout ("reduced ASR against the tested
> attacks", "under the evaluated threat model", "not evaluated against"). Numbers are as-reported by the paper and
> not independently verified.

## 0. Corpus composition (important caveat before any generalization)
This chunk is heavily diluted by mis-binned papers. Of 40:
- **~25 are core LLM/agent-security** papers (jailbreak attacks, safety-alignment defenses, backdoors, eval
  frameworks): A36996, A37106, A37203, A37350, A40018, A40248, A40296, A40399, A40465, A40472, A40484, A40543,
  A40551, A40553, A40554, A40607, A40785, A40836, A40840, A40841, A40858, A40863, A40866, A40887, and (adjacent,
  voice-moderation) A36960.
- **~4 are privacy/federated-learning-adjacent** where privacy is a *design motivation, not an evaluated defense*:
  A37918 (FedSDA), A40037 (FedPKDA), A39337 (FedTopo), A39939 (SFDA brain decoding).
- **~11 are peripheral / off-topic** vision, multimodal-representation, or clustering papers with **no adversary and
  no threat model**, filed here only by folder placement: A37192, A37696, A38215, A38279, A38298, A38532, A38956,
  A39003, A39235, A39475, A40136. Their cards explicitly warn: do NOT cite them for any security claim. The lexical
  overlap of "alignment" (safety alignment vs. representation/semantic alignment) is the likely mis-binning cause.

The security synthesis below draws on the core + privacy-adjacent set only.

## 1. Dominant threat models
- **Black-box, inference-time jailbreak of a safety-aligned chat LLM** is the modal threat: prompt-only API access,
  targeted harmful elicitation, single- or few-query budgets. Seen in A36996 (history transfer), A37203 (cognitive-
  bias rewriting), A40296 (emoji substitution), A40465 (equation+code wrapping), A40554 (adaptive Markov strategy
  composition), A40840 (fabricated response-history priming). This is the most replicated framing.
- **White-box / self-hosted open-weight** attacker or defender: A40551 (representation-level refusal-direction
  ablation), A40858 (LVLM activation manipulation), A40863 (MLLM-mediated suffix crafting via continuous space).
  Also every representation-level *defense* (A40607, A40785, A40887, A40553) requires white-box internals.
- **Training-/fine-tuning-phase poisoning**: A40472 (HIN) — a white-box adversary with partial fine-tuning-data
  write access implants acoustic backdoors in audio LLMs.
- **Multimodal expansion of the attack surface**: image (A40018, A40607, A40836, A40858, A40863), audio
  (A36960, A40472), and video (A40841) are each shown to be softer than the text channel — VLMs/MLLMs are reported
  more jailbreak-prone than their LLM backbones (A40607, A40863).
- **Privacy leakage in collaborative/regulated ML**: gradient inversion, membership inference, reconstruction
  (A37918, A40037, A39337, A39939) — but treated as a *motivating* risk, largely un-instantiated.
- **Emergent (non-adversarial) safety failures**: cross-modal implicit risk from individually-benign inputs (A40836);
  omission of clearly-visible harmful video content (A40841); persona/role-play pressure (A40399).

Recurring **adaptivity gap**: the large majority of attacks are *fixed-strategy / non-adaptive to the specific
deployed defense*; almost no *defense* is evaluated against an attacker adapting to it (see §7).

## 2. Major attack families
- **Context / history manipulation.** Injecting forged prior *assistant* turns exploits the model's coherence bias:
  A36996 (CHASE, cross-model jailbroken-history transfer) and A40840 (Response Attack, fabricated intermediate
  responses; author-reported RA-DRI avg ASR 94.8% across 8 models, >10% over 9 baselines). Both hinge on the same
  structural weakness: **caller-supplied conversation history is trusted as authentic model output**.
- **Semantic-channel / representation-shift bypass.** Re-encode harmful intent into a channel where safety fires
  weakly: emojis (A40296, tokenization-driven representation gap; models *recognize* intent yet comply), math+code
  wrapping (A40465, author-reported avg ASR 91.19% GPT-series / 97.62% on five SOTA models, single query),
  cross-modal sub-image decomposition + CoT (A40018), MLLM continuous-space→text-suffix transfer (A40863).
- **Persuasion / cognitive-bias framing.** A37203 (CognitiveAttack) trains a red-team rewriter (SFT+PPO) to embed
  *synergistic* cognitive biases; author-reported ASR 60.1% vs. PAP 31.6%, with 73.3% of 30 targets >50% ASR.
- **Adaptive strategy sequencing.** A40554 (MAJIC) uses a Markov chain + Q-learning to order disguise strategies
  online; author-reported >90% ASR at <15 queries, including against a strongly-aligned model.
- **Representation / activation attacks (white-box).** A40551 (multi-directional refusal ablation via SOM;
  author-claimed highest ASR on all 8 models incl. a Circuit-Breakers-defended one), A40858 (ActMan, attention-shift
  + MMD activation concealment; author-reported +12.06% relative ASR).
- **Backdoor / poisoning.** A40472 (HIN): emotion/speed acoustic triggers reach author-reported >95% ASR at 3%
  poisoning, evading loss-dynamics detection (CV of loss differential often negative).
- **Multimodal omission / evasion.** A40841: zero-query black-box video edits (frame-replacement, corner
  picture-in-picture, transparent overlay) yield author-reported Harmfulness-Omission-Rate >90% in most cells.
- **Multi-turn privacy inference.** A40484: complementary/aggregation queries each safe in isolation jointly
  exfiltrate protected DB fields.

## 3. Major defense families
- **Training-/post-training alignment.** A37106 (MOSA — align diffusion-LLM *middle* tokens, exploiting a
  generation-order asymmetry), A40543 (WALKSAFE — subgraph risk via risk-aware random walk + Bi-GRPO to filter only
  harmful relations, reducing over-refusal), A40484 (SafeNLIDB — synthetic-data + Alternating Preference
  Optimization), A40836 (SRPO — step-wise reasoning-path preference optimization for cross-modal safety), A40248
  (Targeted Learning Completion — training-time completion of undertrained later positions).
- **Inference-time / decoding-time steering (no weight update).** A37350 (EigenShield — RMT causal-subspace
  projection at the embedding layer, model-agnostic), A40785 (ACD — subtract a learned adversarial-prompt logit
  stream), A40607 (SafetyReminder — mid-generation conditional soft-prompt injection for VLMs), A40887 (DDPO —
  input-dependent defensive embedding injected at the most class-separable layer), A40553 (MirrorShield — contrastive
  "mirror" + attention-entropy RIU detection), A40248 (inference-time contrastive suppression of base-favored tokens).
- **Detection / evaluation layers.** A36960 (source-aware audio-toxicity classifier), A40866 (SceneJailEval —
  scenario-adaptive multi-dimensional jailbreak judge; author-reported F1 0.917 own set / 0.995 JBB), A40399
  (EduGuardBench — persona-jailbreak + pedagogical-harm benchmark, introduces "Educational Refusal" quality tier).
- **Privacy-by-design (data minimization).** A37918, A40037, A39337, A39939 — share representations/prototypes/
  models instead of raw data; A40037 adds Laplace noise but *no formal (ε,δ) budget*.

Cross-cutting architectural lesson (multiple defenses): **safety must be enforced deep across all generation
positions and internal representations, not just the refusal prefix / first token** (A40248, A40607, A40551,
A40836, A40887).

## 4. Strongest replicated findings
- **Safety alignment is "shallow" (concentrated in early response positions / a low-rank refusal subspace), and this
  shallowness is the shared root cause behind many attacks.** A40248 gives a mechanistic account (gradient
  concentration + signal decay in autoregressive training) and reports inference-time contrastive decoding cutting a
  prefill attack 47.5%→0.2% on Llama-3.1-8B-Instruct. A40551 independently shows refusal is a *manifold* (multiple
  related directions), and ablating several beats single-direction ablation. A40840/A36996 exploit the same
  later-position/coherence weakness via history injection. A40607 finds the VLM analogue ("delayed safety awareness").
  This convergence — four independent papers — is the chunk's most robust theme.
- **Heterogeneous / non-natural-language channels reliably evade word- and surface-level safety** even when the model
  can still recover the harmful intent: emojis (A40296), math/code (A40465), sub-image decomposition (A40018), audio
  paralinguistics (A36960), MLLM continuous space (A40863). Implication (reviewer synthesis): safety should operate
  on *normalized/recovered intent*, not surface tokens.
- **Multimodal channels are softer than text.** VLM/MLLM jailbreak susceptibility exceeds the text backbone
  (A40607, A40863, A40858); video summarizers omit visible harm (A40841, with a probing control showing the
  standalone encoder detects harm the fused model reports far less).
- **Judge-model dependence is near-universal.** ASR/harm is scored by an LLM judge (GPT-4o / GPT-4 / HarmBench-cls /
  Perspective API) in nearly every attack and several defenses — a shared, acknowledged confound (see §6).

## 5. Conflicting / tension findings
- **Scale vs. safety.** A40399 reports a "scaling paradox" — mid-sized models can be *most* vulnerable, contradicting
  "bigger = safer". A40465 finds the opposite tendency in one case: the largest model tested (Llama-3.1-405B) resisted
  best (EquaCode ASR 17.88% vs. 81–98% elsewhere), suggesting alignment depth/scale helped there. Both are
  observational on different model sets; not directly comparable.
- **Where safety alignment "lives".** A40248/A40551 (autoregressive LLMs) locate safety in *early* tokens / low-rank
  refusal directions; A37106 (diffusion LLMs) argues the *opposite* — middle tokens are most critical and
  structurally shielded from the attacker. This is an architecture-specific divergence, not a contradiction: it
  reinforces that defenses must be architecture-aware.
- **Diffusion-LLM asymmetry as a durable advantage?** A37106's defense rests entirely on a sequential-generation
  bias its own card flags as possibly erodable (decoding-order attacks untested) — a defender-favorable finding whose
  durability is contested by its own reviewer notes.
- **Over-refusal vs. harm reduction.** A40543, A40553, A40887, A40248 all argue prior defenses over-refuse and claim
  to resolve the safety/utility trade-off; none (in the visible extracts) quantify false-positive rates against an
  adaptive benign-ambiguous set, so the claimed resolution is not independently verifiable here.

## 6. Defense bypasses & residual risk
- **Representation-level defenses can be directly gamed.** A40858 (ActMan) *minimizes* MMD divergence of last-token
  activations from a benign baseline — exactly the signal that A40887 (DDPO) and A40607/A40553 rely on. The A40887
  card explicitly flags this collision: a DDPO-aware activation-manipulation attacker could target its
  feature/injection layer. So the representation-monitoring defense family and the activation-attack family are on a
  collision course, and *neither side tested the other*.
- **Circuit-Breakers / Representation Rerouting was still led by A40551's multi-direction ablation** (author claim) —
  a reported bypass of a deployed representation-level defense.
- **EquaCode (A40465) math/code wrapping is noted (A40543 card) as likely to resist entity-relation parsing**, i.e.,
  to bypass WALKSAFE's graph-surgery premise; untested but a concrete predicted gap.
- **Residual non-elimination:** even the stronger defenses leave material residual ASR — A40248 reports Qwen-3-8B
  residual ~16.4% harmful despite near-zero on the prefill metric; A40607 loses specific per-attack cells to baselines
  though best on average. No paper claims elimination (calibrated language honored across the corpus).
- **Privacy "defenses" are unbypassed only because unattacked.** A37918/A40037/A39337/A39939 never run the
  gradient-inversion / MIA attacks they cite, so residual leakage is unquantified — the shared, load-bearing gap of
  the privacy-adjacent cluster.

## 7. Benchmark / evaluation limitations (recurring)
- **Single LLM-judge ASR** with no reported human agreement (A36996, A37203, A40296, A40465, A40554, A40840, A40858)
  — potential self-preference / calibration bias, sometimes circular (GPT-4 judging GPT-family). A40866 is the
  chunk's attempt at a better judge but is itself LLM-agent-based and untested against evaluator-gaming.
- **Truncated result tables** in the extracted text for most papers — many headline numbers are abstract-level author
  claims not visible in the cards (explicitly flagged for A36996, A37106, A40543, A40554, A40836, A40858, A40887).
- **Self-proposed benchmarks used for both tuning and headline SOTA** (A40836 RSBench; A40399 own set; A40866 own
  14-scenario set), risking metric-method co-selection / evaluation overfitting.
- **Non-adaptive fixed prompt/attack sets** (A40018, A40399, A40465, A40484 self-generated pattern pool) risk
  benchmark contamination after release and overstate robustness.
- **Open-weight / white-box-only scope** limits external validity for the representation papers (A40248 needs paired
  base+aligned logits; A40551/A40607/A40785/A40887/A40553 need internals) — none transfer to closed API models.
- **Perspective API and similar classifiers carry sociolinguistic bias** (A37350, A40543) that propagates into both
  training signal and reported harm reduction.

## 8. Recurring implementation patterns (transferable to a guardian stack)
- **Treat conversation history / prior "assistant" turns as untrusted, integrity-checked context** — sign/attest
  transcript provenance so injected turns can't masquerade as genuine output (A36996, A40840). Directly relevant to
  agent memory and stateless chat APIs.
- **Normalize before you gate**: map emojis/glyphs/encodings/math/code back to canonical intent *before* the safety
  check; screen the *whole assembled context* and *history*, not just the latest user turn (A40296, A40465, A40018).
- **Hook safety at the most class-separable internal layer**; use base-vs-aligned logit gap or layer-N last-token
  representation as a cheap harmful-intent signal (A40248, A40887, A40607) — but assume it can be adversarially
  shaped (A40858).
- **Score reasoning steps, not just final labels**; step-wise positive/negative branch preference (A40836) and
  position-resolved KL / base-favored-token profiles (A40248) as runtime and training diagnostics.
- **Constraint-aware, history-aware verification for tool/data access**: joint reasoning over schema + history +
  current query for DB/tool agents (A40484); scenario-adaptive, severity-graded judging rather than binary allow/block
  (A40866).
- **Emit structured trace fields** for audit: toxicity source/category (A36960), filtered eigen-directions / RbNS
  margins (A37350), RIU/entropy divergence (A40553), removed ERG edges + reconstructed query (A40543), safety-CoT
  rationale (A40836/A40866). Consistent with an autonomy-trace / evidence-logging design.

## 9. Product / architecture implications
- **Layered defense-in-depth, not a single control.** Every defense card ends with "should be a layer, not the sole
  control." Concretely: input normalization + context/history provenance + representation-level gate + output-side
  screening + scenario-adaptive judge + logging. No single mechanism in this chunk is robust alone.
- **Independent output-side review is essential** where model-internal alignment is the only guard (A40465, A40863):
  a single benign-looking API call can extract harmful procedural content; rate-limiting alone fails against
  single-query attacks.
- **Multimodal inputs are first-class attack surfaces** (image/audio/video), and their safety cannot be treated as an
  efficiency/quality afterthought — frame sampling and token compression are *safety-coverage* decisions (A40841).
  Consider using standalone encoder signals as an auxiliary harm detector when fusion suppresses them (A40841).
- **Fine-tuning is a supply-chain trust boundary** for multimodal models: waveform/feature-level provenance and
  poisoning defenses are needed; loss-curve monitoring is insufficient (A40472).
- **Data minimization is necessary but not sufficient** for privacy: pair prototype/representation sharing with an
  explicit DP accountant and empirical leakage tests (A40037, A39939, A37918).

## 10. Open problems
- **Adaptive-attacker evaluation of defenses** is almost entirely missing — the single most consistent gap across
  A37106, A40248, A40484, A40543, A40553, A40607, A40785, A40887. Closing it is prerequisite to any robustness claim.
- **The representation-monitor vs. activation-attack collision** (A40887 ↔ A40858, A40551 ↔ RR) needs head-to-head
  study.
- **Cross-model / closed-API applicability** of white-box defenses and detectors.
- **Trustworthy, non-gameable judges**: reduce single-LLM-judge dependence; validate against human agreement and
  evaluator-aware adversaries (A40866 is a start).
- **Empirical privacy accounting** for the FL/SFDA cluster (run the cited inversion/MIA attacks; add formal DP).
- **Physical-world realizability** of acoustic/multimodal triggers (over-the-air replay untested, A40472).
- **Over-refusal quantification** under the "resolves safety-utility trade-off" claims.

## 11. Most load-bearing papers (by id)
- **A40248 (Incomplete Safety Learning)** — the mechanistic keystone: explains *why* shallow alignment emerges and
  ties together the history-injection, prefill, and persona attacks; offers both an inference-time and a training-time
  fix with visible before/after numbers. Highest leverage for a guardian design.
- **A37350 (EigenShield)** — the defense with the strongest, most externally-valid evidence in the chunk (visible ASR
  tables, LLM+VLM breadth, standard + adaptive + OOD settings, honest asymptotic-guarantee caveats). Model-agnostic
  embedding-layer filtering is directly transferable to API-served frontier models.
- **A40840 (Response Attack)** and **A36996 (CHASE)** — jointly establish the load-bearing architectural requirement:
  authenticate/attest conversation history; injected assistant turns are the highest-yield, lowest-cost jailbreak.
- **A40551 (SOM multi-directional refusal suppression)** — reframes refusal as a manifold and reports bypassing a
  deployed representation-level defense (RR), setting the robustness bar for representation-level safety.
- **A37203 (CognitiveAttack)** — best breadth (30 models) and a realistic black-box persuasion threat that generic
  keyword/suffix defenses miss; motivates persuasion/intent-preservation detectors.
- **A40866 (SceneJailEval)** — the evaluation-layer keystone: scenario-adaptive, severity-graded, audit-friendly
  judging is the piece most reusable as a standardized verifier for the rest of the corpus's attacks/defenses.

_(Runners-up feeding directly into product design: A40887/A40607/A40785 defense trio, A40472 audio-backdoor
supply-chain lesson, A40484 constraint-aware tool/DB access.)_
