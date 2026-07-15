# AILLM-Safety — Authoritative Synthesis

> Merged from two partial syntheses covering AAAI-26 papers filed under the corpus label "AILLM-Safety"
> (chunk 0: 40 papers; chunk 1: 23 papers; 63 total). This document supersedes the partials.
>
> **Evidence integrity.** Every claim traces to a paper card. Author-reported results are labelled as such and
> kept distinct from reviewer synthesis. All magnitudes are as-reported by the paper and **not independently
> verified**; where a card was silent or its result table was truncated in the source extract, the value is
> marked "not stated in paper". Language is deliberately calibrated ("reduced ASR against the tested attacks",
> "demonstrated under the evaluated threat model", "not evaluated against", "requires production validation").
> No absolutes ("secure", "unbreakable", "proven safe") are used. Weighting favours experimental quality,
> reproducibility, threat-model realism, and (where available) cross-paper convergence — not paper count.

---

## 1. Executive summary

Across 63 papers, roughly 44 are core LLM/agent-security work; the remainder are privacy/federated-learning-adjacent
(privacy as a motivation, not an evaluated defense) or peripheral vision/representation papers mis-binned by the
lexical collision of "alignment" (safety alignment vs. representation alignment). The security-relevant subset
converges on one mechanistic thesis, supported by multiple independent papers: **safety alignment in current
systems is "shallow"** — concentrated in early response positions, a low-rank/redundant refusal sub-circuit, and
surface lexical form — and this shallowness is the shared root cause behind the strongest attacks. Four independent
autoregressive-LLM papers (A40248 mechanistic account; A40551 refusal-as-manifold; A40840/A36996 history injection)
and their VLM analogue (A40607 "delayed safety awareness"), plus two white-box refusal-dissection papers in the
second chunk (A41119 "hydra"; A41148 harm-detection vs. refusal-execution), all point at the same weakness.

The offensive frontier is **query-efficient, black-box, and channel-shifting**: emoji/glyph substitution (A40296),
math+code wrapping (A40465), cipher/macaronic recombination (A41058, A40916), fabricated conversation history
(A40840, A36996), cognitive-bias persuasion (A37203), and adaptive RL strategy selection (A40554, A41058, A40919)
each defeat token- or surface-level safety at low query budgets. Multimodal channels (image, audio, video, T2I) are
repeatedly shown softer than text. The most product-relevant threat is **agentic indirect prompt injection**
(A41090, A41468): agents follow instructions planted in the environment/tool content they read.

The defensive frontier is **representation-level and inference-time steering** (A37350, A40785, A40607, A40887,
A41074, A42191), **alignment reshaping** (A37106, A40248, A41140, A41129, A40836), and **layered agent guardrails**
(A41468, A41152). None drives attack success to a safe floor; leading inference-time defenses leave material
residual (e.g. A42191 ~31% residual ASR; A41468 >50% miss on its hardest agent class). The single most consistent
methodological gap is the **near-total absence of adaptive-attacker evaluation of defenses**, compounded by
pervasive single-LLM-judge scoring. The actionable conclusion for a guardian stack: **defense-in-depth aligned to
the agent cognitive cycle**, treat untrusted context (history, tool output, environment) as data not instructions,
normalize inputs to canonical intent before gating, and pair model-internal signals with least-privilege and
human-approval on high-stakes actions — because no single control in this corpus is robust alone.

## 2. Scope and boundaries

- **In scope:** black-box and white-box jailbreaks of safety-aligned chat/vision/audio LLMs; training-time
  poisoning and backdoors of alignment; inference-time and post-training defenses; agent/tool/MCP security;
  T2I / multimodal generative-content safety; evaluation benchmarks and judges. All papers are AAAI-26 (several
  are Student Abstracts, flagged as preliminary).
- **Partly in scope (privacy-adjacent):** four federated-learning / source-free-domain-adaptation papers (A37918,
  A40037, A39337, A39939) treat privacy leakage (gradient inversion, membership inference, reconstruction) as a
  *design motivation, not an evaluated defense* — they cite but do not run the attacks, so residual leakage is
  unquantified. One financial disclosure guardrail (A41498) targets OWASP-LLM sensitive-information disclosure.
- **Out of scope / do not cite for security claims:** ~11 chunk-0 vision/representation/clustering papers with no
  adversary and no threat model (A37192, A37696, A38215, A38279, A38298, A38532, A38956, A39003, A39235, A39475,
  A40136), filed here only by folder placement; their own cards warn against security generalization. Four chunk-1
  peripheral papers contribute analogies only, not agent-security results: A40940 (formal reactive-control
  synthesis, no attacker), A41088 (moral-uncertainty calibration, no adversary), A41238 (autonomous-vehicle
  safety-scenario red-teaming; physical AV, not agent/tool security), A41517 (AI-safety curriculum case study).
- **External-validity boundary:** the strongest representation-level results are open-weight / white-box only and
  do not transfer to closed API models without internals access; many benchmarks are self-proposed and used for
  both tuning and headline SOTA.

## 3. Dominant threat models

- **Black-box, inference-time jailbreak of a safety-aligned chat LLM (modal threat).** Prompt-only API access,
  targeted harmful elicitation, single- or few-query budgets. A36996 (history transfer), A37203 (cognitive-bias
  rewriting), A40296 (emoji substitution), A40465 (equation+code wrapping), A40554 (adaptive Markov strategy
  composition), A40840 (fabricated response-history priming), and in chunk 1 A40916 (macaronic), A41058
  (MetaCipher cipher selection), A40919 (Reason2Attack T2I), A41093 (StyleBreak audio), A42273 (distractor).
  Several are explicitly **adaptive** (RL/policy-driven selection).
- **White-box / open-weight attacker or defender.** Requires residual-stream access and a runtime hook:
  A40551 (multi-directional refusal-direction ablation), A40858 (LVLM activation manipulation), A40863 (MLLM
  continuous-space suffix), A41119 (SAE feature ablation), A41148 (DBDI activation steering). Reviewer synthesis
  (A41148 deployment note): for downloadable models this collapses to "the owner attacking their own model", so
  withholding weights (API-only) is itself a material control. Every representation-level *defense* also needs
  internals (A40607, A40785, A40887, A40553, A41074, A42191).
- **Training-/fine-tuning-phase poisoning and backdoors.** A40472 (HIN acoustic backdoors in audio LLMs, partial
  fine-tuning-data write access), A41087 (minimum-cost preference-label flipping against RLHF/DPO reward learning),
  A41118 (AdvBDGen adaptive stealthy alignment-data backdoors) — untrusted annotator / partially-controlled
  crowdsourced preference data.
- **Agentic threat models (most product-relevant).** A41090 (MobileSafetyBench) models both a malicious user and an
  external attacker planting **indirect prompt injection** in environment content the agent reads (messages, memos,
  posts, files). A41468 (InfrastructureSentinel) enumerates the fullest MCP threat surface in the corpus: direct +
  indirect prompt injection, context/memory manipulation, insecure tool use / command injection, privilege
  escalation, tool poisoning / supply chain, credential exposure, DoS.
- **Multimodal expansion of the attack surface.** Image (A40018, A40607, A40836, A40858, A40863), audio (A36960,
  A40472, A41093), video (A40841), and T2I (A40916, A40919, A40920, A41086, A41152) are each shown softer than the
  text channel; VLMs/MLLMs reported more jailbreak-prone than their LLM backbones (A40607, A40863).
- **Privacy leakage / disclosure.** Gradient inversion, membership inference, reconstruction in collaborative ML
  (A37918, A40037, A39337, A39939, treated as motivating risk, largely un-instantiated); sensitive-information
  extraction via crafted prompts / model inversion / extractable memorization (A41498).
- **Emergent (non-adversarial) safety failures.** Cross-modal implicit risk from individually-benign inputs
  (A40836); omission of clearly-visible harmful video content (A40841); persona/role-play pressure (A40399).

**Recurring adaptivity gap:** the large majority of attacks are fixed-strategy / non-adaptive to the specific
deployed defense, and almost no *defense* is evaluated against an attacker adapting to it (see §11, §12, §17).

## 4. Major attack families

- **Context / history manipulation.** Injecting forged prior *assistant* turns exploits coherence bias:
  A36996 (CHASE, cross-model jailbroken-history transfer) and A40840 (Response Attack; author-reported RA-DRI avg
  ASR 94.8% across 8 models, >10% over 9 baselines). Shared structural weakness: **caller-supplied conversation
  history is trusted as authentic model output.**
- **Semantic-channel / representation-shift bypass.** Re-encode harmful intent where safety fires weakly: emojis
  (A40296, tokenization-driven representation gap — models *recognize* intent yet comply), math+code wrapping
  (A40465, author-reported avg ASR 91.19% GPT-series / 97.62% on five SOTA models, single query), cross-modal
  sub-image decomposition + CoT (A40018), MLLM continuous-space→text-suffix transfer (A40863), 21-cipher encryption
  with keyword masking (A41058, author-reported 60%+ ASR within ≤10 queries), cross-lingual character recombination
  (A40916 "macaronic"), distractor-masking of a single malicious instruction (A42273).
- **Persuasion / cognitive-bias framing.** A37203 (CognitiveAttack) trains a red-team rewriter (SFT+PPO) to embed
  *synergistic* cognitive biases; author-reported ASR 60.1% vs. PAP 31.6%, with 73.3% of 30 targets >50% ASR.
- **Learned / reasoning-driven adversaries.** A40919 (Reason2Attack) trains an attacker LLM (SFT + GRPO,
  Frame-Semantics CoT) for fluent adversarial T2I prompts (author-reported ~60% ASR at a single query); A40554
  (MAJIC) uses a Markov chain + Q-learning to order disguise strategies online (author-reported >90% ASR at <15
  queries, including against a strongly-aligned model).
- **Representation / activation attacks (white-box).** A40551 (multi-directional refusal ablation via SOM;
  author-claimed highest ASR on all 8 models incl. a Circuit-Breakers/RR-defended one), A40858 (ActMan,
  attention-shift + MMD activation concealment; author-reported +12.06% relative ASR), A40863 (MLLM continuous
  space), A41119 (sparse SAE refusal sub-circuit ablation; "hydra effect" — dormant features re-activate when
  precursors are suppressed; specific per-stage ASR figures ambiguous in the source extract), A41148 (DBDI —
  decompose refusal into a harm-detection vector and a refusal-execution vector, nullify separately; author-reported
  up to 97.88% ASR on Llama-2).
- **Prefix / mismatched-generalization jailbreaks.** Prefix-injection / assistant-prefilling forcing an affirmative
  opening token, plus nested-encoding attacks (ReNeLLM, CodeAttack, CodeChameleon) — the threat class A41140 is
  built to withstand.
- **Backdoor / poisoning.** A40472 (HIN): emotion/speed acoustic triggers, author-reported >95% ASR at 3%
  poisoning, evading loss-dynamics detection (CV of loss differential often negative). A41087 (minimum-cost
  preference-label flipping). A41118 (dual-discriminator prompt-specific paraphrase backdoors installable at ~3%
  poison, cross-model transfer).
- **Modality-specific attacks.** Audio style perturbation (emotion×age×gender) in A41093; NSFW *text rendered
  inside generated images* in A41086 — a T2I threat OCR+toxicity pipelines miss (author-reported OCR+Detoxify
  detects only ~90.83% on FLUX, 49.66% on SDXL); zero-query black-box video edits (frame-replacement, corner
  picture-in-picture, transparent overlay) in A40841 (author-reported Harmfulness-Omission-Rate >90% in most cells).
- **Multi-turn privacy inference.** A40484: complementary/aggregation queries each safe in isolation jointly
  exfiltrate protected DB fields.
- **Agentic attacks.** Indirect prompt injection into device/agent observation streams (A41090); multi-step MCP
  tool-abuse / command-injection / privilege-escalation chains (A41468).

## 5. Major defense families

- **Training-/post-training alignment reshaping.** A37106 (MOSA — align diffusion-LLM *middle* tokens, exploiting a
  generation-order asymmetry), A40543 (WALKSAFE — subgraph risk via risk-aware random walk + Bi-GRPO, filtering only
  harmful relations to reduce over-refusal), A40484 (SafeNLIDB — synthetic-data + Alternating Preference
  Optimization), A40836 (SRPO — step-wise reasoning-path preference optimization for cross-modal safety), A40248
  (Targeted Learning Completion — training-time completion of undertrained later positions), A41140 (HumorReject —
  relocate safety from a brittle refusal-*prefix* to a distributed humor *style* via a 400-sample ORPO dataset;
  author-reported prefix-injection Safety Rate avg 98.8% Llama3 / 96.6% Mistral), A41129 (EASE — distil selective
  deliberative safety reasoning into SLMs, routing only "vulnerable semantic regions" through CoT; author-reported
  up to 17% ASR reduction vs shallow alignment and up to 90% inference-overhead reduction vs always-on reasoning).
- **Inference-time / decoding-time steering (no weight update).** A37350 (EigenShield — RMT causal-subspace
  projection at the embedding layer, model-agnostic), A40785 (ACD — subtract a learned adversarial-prompt logit
  stream), A40607 (SafetyReminder — mid-generation conditional soft-prompt injection for VLMs), A40887 (DDPO —
  input-dependent defensive embedding injected at the most class-separable layer), A40553 (MirrorShield — contrastive
  "mirror" + attention-entropy RIU detection), A40248 (inference-time contrastive suppression of base-favored
  tokens), A41074 (AlignTree — fuse a linear refusal direction with per-layer RBF-SVMs into a Random-Forest gate;
  author-reported large ASR drops, e.g. Qwen2.5-0.5B 91.0→4.0 on MalwareGen, with low benign over-refusal),
  A42191 (RAS — single contrastive refusal vector at layer 20; author-reported ASR 51.86→31.27%, refusal
  41.31→62.76%). White-box activation access required; A42191 and A41074 are non-adaptive-evaluated.
- **Weight-level targeted mitigation.** A41086 applies LoRA only to localized text-rendering attention layers to
  suppress embedded NSFW text while preserving benign generation — the only defense designed for the open-weight /
  local-deployment case where API filtering is bypassable.
- **Layered detect → rewrite/gate → verify guardrails.** A41152 (VALOR for T2I: word/semantic/value detection →
  category-specific zero-shot LLM rewrite → post-hoc image check), A41468 (InfrastructureSentinel for MCP agents:
  input filter → tool-plan validation → runtime execution gate → immutable audit), A41498 (GARD — taxonomy-grounded
  financial sensitive-information I/O detector).
- **Detection / evaluation layers.** A36960 (source-aware audio-toxicity classifier), A40866 (SceneJailEval —
  scenario-adaptive multi-dimensional jailbreak judge; author-reported F1 0.917 own set / 0.995 JBB), A40399
  (EduGuardBench — persona-jailbreak + pedagogical-harm benchmark, introduces an "Educational Refusal" quality
  tier), A40920 (T2I-RiskyPrompt — reason-driven 3B detector, author-reported 91.8% accuracy), A41090
  (MobileSafetyBench — interactive Android agent-safety benchmark with rule-based state evaluators + SCoT prompting).
- **Poisoning-robustness levers (not full mitigations).** A41087 shows higher reward-model feature dimension
  provably raises label-flip attack cost (Proposition 4); A41118 reports latent-adversarial-training (BEEAR-style)
  is the one defense class that substantially mitigates its backdoor.
- **Privacy-by-design (data minimization).** A37918, A40037, A39337, A39939 share representations/prototypes/models
  instead of raw data; A40037 adds Laplace noise but *no formal (ε,δ) budget*.

**Cross-cutting architectural lesson (multiple defenses):** safety must be enforced deep across all generation
positions and internal representations, not just the refusal prefix / first token (A40248, A40607, A40551, A40836,
A40887, A41140, A41119).

## 6. Most influential concepts

- **Shallow safety alignment.** Safety concentrated in early response positions / a low-rank refusal subspace; the
  unifying mechanistic idea (A40248 gives the gradient-concentration + signal-decay account; corroborated by A40551,
  A40840, A36996, A40607, A41140, A41119, A41148).
- **Refusal as a manifold / redundant "hydra" circuit, not a single switch.** A40551, A41119, A41148 (attack side);
  A41074 (defense side: linear + non-linear features beat linear-only probes).
- **Surface-form ≠ semantic intent.** Safety that scans lexical/surface form is evaded by inputs whose textual form
  diverges from their semantic/visual meaning (A40296, A40465, A41058, A40916, A42273). Reviewer-synthesis remedy:
  gate on *normalized/recovered intent*.
- **Untrusted context as an instruction channel.** Caller-supplied history (A40840, A36996) and environment/tool
  content (A41090, A41468) are trusted as authentic; the trust-boundary-isolation remedy ("treat as data, not
  instructions") recurs across the agentic papers.
- **Reasoning is an attack surface, not a safety guarantee.** Models voice ethical concern in CoT yet still comply
  (A42273); agents "overlook safety considerations they themselves generated" (A41090 SCoT self-inconsistency).
- **Capability ≠ permission ≠ safety.** Empirically grounded by A41468/A41090: prompt-level safety reasoning is
  necessary-but-insufficient; hard policy gating and least privilege on sensitive tools are required.
- **Contrastive difference-of-means "safety/refusal direction"** as a dual-use primitive appearing on both defense
  (A41074, A42191) and attack (A41119, A41148) sides.
- **Multimodal channels are softer than text**, and frame sampling / token compression are *safety-coverage*
  decisions, not efficiency afterthoughts (A40841, A40607, A40863).

## 7. Common datasets and benchmarks

- **Jailbreak evaluation sets / judges:** JailbreakBench ("JBB", used by A40866), HarmBench classifier (attack
  scoring, multiple papers), LlamaGuard-2/3 (agent/text judge, chunk 1), Perspective API and Detoxify (toxicity /
  NSFW scoring, A37350, A40543, A41086), CLIP/NSFW detectors (T2I).
- **Self-proposed benchmarks (introduced by corpus papers, used for both tuning and headline SOTA — treat with
  caution):** RSBench (A40836), EduGuardBench (A40399), SceneJailEval 14-scenario set (A40866), MobileSafetyBench
  interactive Android agent set (A41090), T2I-RiskyPrompt with a 6-category/14-subcategory taxonomy (A40920),
  ToxicBench (A41086), MalwareGen (used by A41074), InfrastructureSentinel MCP threat set (A41468), GARD financial
  SFI dataset (A41498, largely synthetic with 115 SME-validated real samples), A40484 self-generated pattern pool,
  A41058 released cipher-attack code/prompts.
- Model targets are heavily open-weight 7–8B (Llama-2/3, Mistral, Qwen2.5/Qwen-3, Qwen1.5) plus GPT-family and a
  Llama-3.1-405B data point (A40465). Several defenses/attacks use only 1–2 models (external-validity caveat, §12).

*Named exactly as they appear in the paper cards; benchmark contents not independently verified.*

## 8. Evaluation metrics

- **Attack Success Rate (ASR)** — the dominant metric, almost always scored by an automated judge (see §12).
  Variants/refinements: **RA-DRI** (A40840), **Harmfulness-Omission-Rate** (A40841), relative-ASR delta (A40858).
- **Safety Rate / refusal rate** (A41140, A42191) and **over-refusal / benign-refusal / false-positive rate**
  (foregrounded by A41074, A41140, A41152, A42191, A41498, A40543, A40553, A40887, A40248 as the safety/helpfulness
  trade-off).
- **Detector/judge quality:** F1 (A40866), accuracy (A40920), recall / FNR / FPR (A41152 intention FNR; A41498
  recall), and **ADR (attack-defense rate, as reported)** for the MCP guardrail (A41468).
- **Poisoning-specific:** poison fraction at fixed ASR (A40472, A41118 ~3%), CV of loss differential as a detection
  signal (A40472), minimum label-flip cost (A41087).
- **Efficiency framed as a safety property:** query budget to jailbreak (A40554 <15; A41058 ≤10; A40919/A40465
  single query), inference-overhead reduction (A41129 up to 90%).

Recurring caveat: "up to X%" figures are best-case over settings, not worst-case guarantees; human-eval is largely
absent; several headline numbers were truncated in the source extracts and are marked "not stated in paper".

## 9. Strongest replicated findings

Ranked by cross-paper convergence and evidence quality; still author-reported and not independently verified.

1. **Safety alignment is shallow, and this is the shared root cause of many attacks.** Strongest convergence in the
   corpus: A40248 (mechanistic; inference-time contrastive decoding cutting a prefill attack 47.5%→0.2% on
   Llama-3.1-8B-Instruct), A40551 (refusal manifold — ablating several directions beats single-direction), A40840 /
   A36996 (later-position/coherence weakness via history injection), A40607 (VLM "delayed safety awareness"), joined
   in chunk 1 by A41119 and A41148 (refusal is a distributed, redundant, separable circuit) and A41140 (initial-token
   safety trivially defeated by forced affirmative prefixes).
2. **Heterogeneous / non-natural-language and cross-lingual channels reliably evade surface-level safety even when
   the model can recover the harmful intent.** Emojis (A40296), math/code (A40465), sub-image decomposition (A40018),
   audio paralinguistics (A36960, A41093), MLLM continuous space (A40863), cipher/macaronic recombination (A41058,
   A40916), distractors (A42273).
3. **Multimodal channels are softer than text.** VLM/MLLM susceptibility exceeds the text backbone (A40607, A40863,
   A40858); video summarizers omit visible harm (A40841, with a probing control showing the standalone encoder
   detects harm the fused model reports far less); embedded-image text evades OCR+toxicity (A41086).
4. **Agents are highly vulnerable to indirect prompt injection, and prompt-level safety is necessary-but-insufficient
   at the action layer.** A41090 (headline agentic finding + SCoT self-inconsistency); A41468 architects around the
   same premise.
5. **Query-efficient jailbreaks exist**, so detection cannot rely on many-query anomaly signals alone (A40919 ~60%
   single query; A41058 60%+ within ≤10; A40554 >90% at <15; A41093 gains within ~3 iterations).
6. **Judge-model dependence is near-universal** and an acknowledged confound (§12).
7. **Defenses must report over-refusal, not just ASR** (A41074, A41140, A41152, A42191, A41498, A40543 all
   foreground the trade-off; several baselines "buy" safety with large benign-refusal increases).

## 10. Conflicting findings

- **Scale vs. safety.** A40399 reports a "scaling paradox" — mid-sized models can be *most* vulnerable, contradicting
  "bigger = safer". A40465 finds the opposite in one case: the largest model tested (Llama-3.1-405B) resisted best
  (EquaCode ASR 17.88% vs. 81–98% elsewhere). Both are observational on different model sets; not directly comparable.
- **Where safety alignment "lives".** A40248/A40551 (autoregressive LLMs) locate safety in *early* tokens / low-rank
  refusal directions; A37106 (diffusion LLMs) argues the *opposite* — *middle* tokens are most critical and
  structurally shielded from the attacker. Architecture-specific divergence, not a contradiction: it reinforces that
  defenses must be architecture-aware. A37106's own card flags its sequential-generation-bias assumption as possibly
  erodable (decoding-order attacks untested).
- **Deliberative safety reasoning: helpful vs. insufficient.** A41129 (EASE) reports selective safety reasoning
  meaningfully reduces SLM jailbreak ASR; A41090 reports SCoT improves scores but leaves agents unsafe and
  self-inconsistent at the *action* layer. Reviewer synthesis: a scope boundary (text-answer refusal vs. embodied
  tool/action decisions), not a direct contradiction.
- **Model scale vs. teacher quality.** A41129 reports a *smaller* LRM distils better safety reasoning than a larger
  one (with a minimum-competence floor), counter to "bigger teacher is better".
- **Best-defense claims are non-uniform.** A41140 reports HumorReject is not uniformly best: on Llama3 under
  mismatched-generalization it averages 84.0%, below Circuit Breaker's 89.0% (author-reported) — method ranking flips
  by model/attack family.
- **Over-refusal resolution is claimed but unverified.** A40543, A40553, A40887, A40248 all argue prior defenses
  over-refuse and claim to resolve the safety/utility trade-off; none (in the visible extracts) quantify
  false-positive rates against an adaptive benign-ambiguous set, so the claimed resolution is not independently
  verifiable here.

## 11. Defense bypasses

- **Representation-level defenses can be directly gamed.** A40858 (ActMan) *minimizes* MMD divergence of last-token
  activations from a benign baseline — exactly the signal A40887 (DDPO), A40607, and A40553 rely on. The A40887 card
  explicitly flags the collision. More broadly, white-box activation-space defenses (A41074, A42191) and
  activation-space attacks (A41119, A41148) operate on the same residual stream; neither defense paper evaluates the
  corresponding adaptive attack — coexistence is an open collision, not a resolved result.
- **A deployed representation-level defense (Circuit-Breakers / Representation Rerouting) was reportedly led by
  A40551's multi-direction ablation** (author claim) — a reported bypass setting the robustness bar.
- **Single "refusal-direction" hardening** is defeated by attacking harm-detection separately (A41148) and by
  hydra-style feature redundancy (A41119).
- **Refusal-prefix–dependent safety** is defeated by prefix injection / assistant-prefilling (A41140 premise).
- **Token/keyword and alignment-dataset scanning** is bypassed by encoding (A41058), cross-lingual recombination
  (A40916), and OCR-fragile embedded text (A41086). Math/code wrapping (A40465) is noted (A40543 card) as likely to
  resist entity-relation parsing, i.e. to bypass WALKSAFE's graph-surgery premise (untested but a concrete predicted
  gap).
- **Concept-removal / concept-erasure at the weight level** does not remove cross-lingual triggerability (A40916)
  and fails to cover multiple risk types simultaneously without benign-fidelity loss (A40920).
- **Constant-trigger backdoor detectors** miss prompt-specific paraphrase triggers (A41118) — with the honest
  negative result that A41118 is itself substantially mitigated by latent-adversarial-training.
- **Prompt-only agent defenses (SCoT)** do not close the gap and are self-inconsistent under agency (A41090); a
  smaller rewriting LLM raises FNR (A41152: Qwen1.5-1.8B ~31–33% intention FNR); a selective-defense router can be
  evaded by a jailbreak crafted to look benign (A41129).
- **Residual non-elimination.** Even stronger defenses leave material residual ASR: A40248 reports Qwen-3-8B residual
  ~16.4% harmful despite near-zero on the prefill metric; A42191 leaves ~31.27% ASR; A41468's hardest classes are
  only >50% (contextual policy violation) / >76% (command injection) ADR; A40607 loses specific per-attack cells to
  baselines though best on average. No paper claims elimination (calibrated language honored across the corpus).
- **Privacy "defenses" are unbypassed only because unattacked.** A37918/A40037/A39337/A39939 never run the
  gradient-inversion / MIA attacks they cite, so residual leakage is unquantified.

## 12. Known benchmark limitations

- **Single-LLM-judge ASR with no reported human agreement**, sometimes circular (GPT-4 judging GPT-family; an attack
  optimizing against the same NSFW-detector class it scores with, A40916): A36996, A37203, A40296, A40465, A40554,
  A40840, A40858, plus chunk 1 A40919, A41058, A41093, A41148, A42191, A42273. A40866 is the corpus's attempt at a
  better judge but is itself LLM-agent-based and untested against evaluator-gaming.
- **Non-adaptive evaluation is the norm for defenses** (A42191 explicitly; also A41152, A41498, A41468, A40920,
  A41090 scripted 50 injection tasks, plus most chunk-0 defenses) — "up to X%" figures are best-case, not worst-case.
- **Self-proposed benchmarks used for both tuning and headline SOTA** (A40836 RSBench, A40399 own set, A40866 own
  14-scenario set) risk metric-method co-selection / evaluation overfitting; non-adaptive fixed prompt/attack sets
  (A40018, A40399, A40465, A40484) risk contamination after release.
- **Small / narrow model scope.** Several defenses/attacks use 1–2 open 7–8B models (A41140, A41148 partially, A41093
  four 7–8B LAMs, A42191 one 8B model, A42273 two 7–8B reasoning models), limiting generality to frontier/proprietary
  systems.
- **In-distribution / self-built test sets.** A41498's 0.98 recall is on a largely synthetic set with only 115
  SME-validated real samples; A41074 has partial train/eval attack-family overlap.
- **Open-weight / white-box-only external validity.** Representation papers need internals (A40248 paired
  base+aligned logits; A40551/A40607/A40785/A40887/A40553/A41074/A42191 need activations) — none transfer to closed
  API models.
- **Classifier sociolinguistic bias.** Perspective API and similar carry bias (A37350, A40543) that propagates into
  training signal and reported harm reduction.
- **Coarse / truncated reporting.** A41468 reports ">X%" ADR with no dataset size, FP rate, or statistical treatment
  (rated Preliminary). Many headline tables were truncated in extracted text; missing numbers marked "not stated".
- **Dual-use artifact release.** Multiple offensive papers release code/prompts (A41058, A41086 ToxicBench, A41119
  feature indices, A41140 data), lowering the misuse barrier.

## 13. Implementation patterns

Transferable primitives for a guardian / autonomy-trace stack, drawn from the papers:

- **Treat conversation history / prior "assistant" turns as untrusted, integrity-checked context** — sign/attest
  transcript provenance so injected turns can't masquerade as genuine output (A36996, A40840). Directly relevant to
  agent memory and stateless chat APIs.
- **Treat untrusted environment/tool content as data, not instructions** — content/trust-boundary isolation at the
  observation/tool layer, the shared remedy to indirect prompt injection (A41090, A41468).
- **Normalize before you gate** — map emojis/glyphs/encodings/math/code/ciphers back to canonical intent *before*
  the safety check; screen the *whole assembled context* and *history*, not just the latest user turn (A40296,
  A40465, A40018, A41058, A40916).
- **Hook safety at the most class-separable internal layer** — base-vs-aligned logit gap or layer-N last-token
  representation as a cheap harmful-intent signal (A40248, A40887, A40607, A42191) — but assume it can be
  adversarially shaped (A40858, A41148); contrastive difference-of-means "safety direction" is a dual-use primitive.
- **Score reasoning steps, not just final labels** — step-wise branch preference (A40836), position-resolved KL /
  base-favored-token profiles (A40248) as runtime and training diagnostics; but do not treat "the model reasoned
  about safety" as evidence of a safe outcome (A42273, A41090).
- **Layered detect → rewrite/gate → verify pipelines** (A41152, A41468) and **risk-tiered / selective activation of
  expensive reasoning** — "reason/gate only when it matters" (A41129 vulnerable-region routing; A41090 low/high-risk
  task pairs).
- **Rule-based state-grounded evaluators** (A41090 inspects Android action history / file storage / app DBs) and
  **immutable audit trails** (A41468 Layer 4) as evidence-logging templates.
- **Human-approval as a first-class action** — `ask-consent()` / `refuse()` in the agent action space (A41090);
  human-in-the-loop review where detectors fail (A41086, A41498 SME validation).
- **Contrastive paired training data** to shape safe behavior without over-triggering on benign inputs (harmful→safe
  + benign→normal in A41140; single-word-swap NSFW/benign image pairs in A41086).
- **Taxonomy-grounded synthetic-data bootstrapping** where real data cannot be shared (A41498 regulatory taxonomy;
  A40920 platform-policy taxonomy).
- **Emit structured trace fields for audit** — toxicity source/category (A36960), filtered eigen-directions / RbNS
  margins (A37350), RIU/entropy divergence (A40553), removed ERG edges + reconstructed query (A40543), safety-CoT
  rationale (A40836/A40866). Consistent with an autonomy-trace / evidence-logging design.
- **Preference-data provenance and per-annotator flip-rate monitoring** plus latent-adversarial-training in
  post-alignment hardening (A41087, A41118).

## 14. Product design implications

- **Layered defense-in-depth, not a single control.** Every defense card ends with "should be a layer, not the sole
  control." Concretely: input normalization + context/history provenance + representation-level gate + output-side
  screening + scenario-adaptive judge + logging. No single mechanism in this corpus is robust alone.
- **Independent output-side review is essential** where model-internal alignment is the only guard (A40465, A40863):
  a single benign-looking API call can extract harmful procedural content; rate-limiting alone fails against
  single-query attacks (§9.5).
- **Multi-signal moderation over single filters** — semantic/decode-aware plus image-side/output moderation as
  backstops (A41058, A40916, A40920, A41086, A41152); domain-specific disclosure guardrails as a separately
  instrumented I/O layer (A41498).
- **Multimodal inputs are first-class attack surfaces** (image/audio/video); frame sampling and token compression are
  *safety-coverage* decisions (A40841); consider standalone-encoder signals as an auxiliary harm detector when fusion
  suppresses them (A40841).
- **Human approval and least privilege gate high-stakes actions** — because no inference-time refusal defense drives
  ASR to a safe floor, defenses must *gate*, not replace, least-privilege + human-in-the-loop on sensitive tools.
- **Uncertainty/CoT as monitoring signals, not user output** — per-decision entropy/MI (A41088) and CoT n-gram drift
  (A42273) are candidate runtime tripwires but are unvalidated as detectors (no ROC/PR); log reasoning traces for
  forensics while not exposing raw CoT to users.
- **Data minimization is necessary but not sufficient for privacy** — pair prototype/representation sharing with an
  explicit DP accountant and empirical leakage tests (A40037, A39939, A37918).

## 15. Architecture implications

- **Defense-in-depth aligned to the agent cognitive cycle** (input → tool-plan validation → pre-invocation execution
  gate → post-action audit) is the most directly transferable architecture (A41468 four-layer), reinforced by A41090
  that prompt-level safety is necessary-but-insufficient. "Capability ≠ permission ≠ safety" is empirically grounded.
- **Trust-boundary isolation** at the observation/tool layer (treat untrusted content as data) is the shared remedy
  to indirect prompt injection (A41090, A41468).
- **Pre-execution tool-plan validation + just-before-invocation re-check** (A41468 Layers 2–3) target tool poisoning,
  privilege escalation, and state-drift/race conditions that content filters miss; back reasoning with hard policy
  gating rather than trusting the model to honor its own safety notes (A41090).
- **Safety must be enforced across all generation positions and internal layers**, not just the refusal prefix
  (A40248, A40607, A40551, A40836, A40887, A41140) — and safety hooks must be architecture-aware (autoregressive vs.
  diffusion divergence, A40248/A40551 vs. A37106).
- **The Guardian LLM is itself an injectable trust anchor** (reviewer synthesis on A41468): "using an LLM to defend
  an LLM agent" needs adaptive-injection stress-testing and tamper-evident logging that current papers assert but do
  not verify.
- **Open-weight deployment cannot rely on API-side filtering or single-direction refusal hardening** (A41086, A41119,
  A41148); weight-level mitigation + representation monitoring + external gating are implied.
- **Fine-tuning and preference data are supply-chain trust boundaries** — waveform/feature-level provenance and
  poisoning defenses (loss-curve monitoring is insufficient, A40472); annotation provenance logging and
  latent-adversarial-training (A41087, A41118).

## 16. Launch and assurance implications

- **Adaptive red-teaming is a launch gate, not a nice-to-have.** The corpus's most consistent gap is the absence of
  attacker-adapts-to-defense evaluation; any robustness claim requires it before production (A37106, A40248, A40484,
  A40543, A40553, A40607, A40785, A40887, A42191, A41152, A41468, A41498, A41074, A41129). "Requires production
  validation" applies to every headline defense number here.
- **Do not rely on a single automated judge for release sign-off.** Validate against human agreement and
  evaluator-aware adversaries; measurement circularity (attack optimizing against the scoring detector) is a
  recurring risk (A40916, A40920, A40866).
- **Assume residual harm and design compensating controls.** Leading inference-time defenses leave material residual
  ASR (A42191 ~31%; A40248 ~16%; A41468 >50% miss on hardest agent class); pair with least-privilege, human approval,
  and immutable audit for high-stakes actions.
- **Instrument over-refusal / false-positive rates as first-class launch metrics**, against an adaptive
  benign-ambiguous set — not just ASR (A41074, A41140, A41152, A42191, A40543).
- **Cover multimodal and cross-lingual surfaces explicitly**; English-text safety alignment does not transfer to
  audio style, embedded image text, or cross-lingual recombination (A40916, A41093, A41086).
- **Establish supply-chain assurance for fine-tuning and preference data** — provenance, per-annotator flip-rate
  monitoring, latent-adversarial-training, and defenses beyond loss-curve monitoring (A40472, A41087, A41118).
- **Physical-world realizability of multimodal triggers is unproven** — over-the-air replay of acoustic triggers is
  untested (A40472); do not assume lab ASR transfers to deployment.
- **Dual-use release hygiene** — several offensive artifacts are public (A41058, A41086, A41119, A41140); assume
  attackers have them when threat-modeling.

## 17. Open research problems

- **Adaptive-attacker evaluation of defenses** — the single most consistent gap; prerequisite to any robustness claim
  (A37106, A40248, A40484, A40543, A40553, A40607, A40785, A40887, A42191, A41152, A41468, A41498, A41074, A41129).
- **The representation-monitor vs. activation-attack collision** needs head-to-head study (A40887 ↔ A40858;
  A41074/A42191 ↔ A41119/A41148; A40551 ↔ Representation Rerouting).
- **Cross-model / closed-API applicability** of white-box defenses and detectors.
- **Trustworthy, non-gameable judges** — reduce single-LLM-judge dependence; validate against human agreement and
  evaluator-aware adversaries (A40866 is a start).
- **Reconciling reasoning-based defenses with agentic action layers** — where to place hard enforcement vs. model
  reasoning (A41129 helps text refusal; A41090 shows reasoning insufficient for embodied actions).
- **Router/boundary evasion in selective defenses** — a jailbreak crafted to look benign bypasses the
  vulnerable-region router entirely (A41129, acknowledged but unstressed).
- **Tamper-evidence and formal guarantees for guardian/audit layers** — asserted, not demonstrated (A41468 notes
  formal verification and immutable-log integrity as absent).
- **Empirical privacy accounting** for the FL/SFDA cluster — run the cited inversion/MIA attacks; add formal DP
  (A37918, A40037, A39337, A39939).
- **Physical-world realizability** of acoustic/multimodal triggers (over-the-air replay untested, A40472).
- **Over-refusal quantification** under the "resolves safety-utility trade-off" claims, against adaptive
  benign-ambiguous sets.
- **Cross-lingual / multimodal / paralinguistic robustness** — an under-defended surface (A40916, A41093, A41086);
  English-text safety semantics do not transfer.

## 18. Recommended foundational papers

Keystone works establishing core principles a guardian knowledge base should build on. (All AAAI-26; ranked by
mechanistic leverage and evidence quality.)

1. **A40248 (Incomplete Safety Learning / Targeted Learning Completion)** — mechanistic keystone: explains *why*
   shallow alignment emerges (gradient concentration + signal decay) and ties together history-injection, prefill,
   and persona attacks; offers both inference-time and training-time fixes with visible before/after numbers.
2. **A41090 (MobileSafetyBench)** — strongest agent-security evidence class: interactive Android benchmark,
   human-annotated risk severity, rule-based state evaluators, matched low/high-risk tasks; establishes agent
   indirect-prompt-injection susceptibility and that prompt-level safety is necessary-but-insufficient.
3. **A40840 (Response Attack) + A36996 (CHASE)** — jointly establish the load-bearing requirement to
   authenticate/attest conversation history; injected assistant turns are the highest-yield, lowest-cost jailbreak.
4. **A37350 (EigenShield)** — the defense with the strongest, most externally-valid evidence (visible ASR tables,
   LLM+VLM breadth, standard + adaptive + OOD settings, honest asymptotic-guarantee caveats); model-agnostic
   embedding-layer filtering transferable to API-served models.
5. **A41119 (refusal dissection / "hydra effect")** — mechanistic, reproducible white-box account of refusal as a
   redundant sub-circuit; load-bearing for why single-direction hardening is fragile in open-weight settings.
6. **A40866 (SceneJailEval)** — evaluation-layer keystone: scenario-adaptive, severity-graded, audit-friendly
   judging, the piece most reusable as a standardized verifier for the rest of the corpus's attacks/defenses.

## 19. Recommended frontier papers

Cutting-edge attack/defense demonstrations that define the current robustness bar.

1. **A41058 (MetaCipher)** — realistic adaptive black-box multi-agent RL jailbreak with released code and
   query/time-efficiency metrics; strongest offensive evidence that token-level safety is evadable and persistent.
2. **A40551 (SOM multi-directional refusal suppression)** — reframes refusal as a manifold and reports bypassing a
   deployed representation-level defense (RR), setting the robustness bar for representation-level safety.
3. **A41468 (InfrastructureSentinel)** — fullest MCP/agent threat taxonomy plus a directly reusable four-layer
   defense-in-depth architecture (evidence Preliminary: coarse ADR, no adaptive testing).
4. **A37203 (CognitiveAttack)** — best breadth (30 models) and a realistic black-box persuasion threat that generic
   keyword/suffix defenses miss; motivates persuasion/intent-preservation detectors.
5. **A41118 (AdvBDGen)** — adaptive, low-budget (~3%) alignment backdoor with cross-model transfer and an honest
   negative result (latent-adversarial-training mitigates it); anchors the preference-data supply-chain threat.
6. **A41087 (cost-minimized label-flipping)** — the corpus's most rigorous result (convex-duality), quantifying
   minimum poisoning cost of RLHF/DPO alignment and giving a concrete robustness lever (reward-model feature dim).
7. **A37106 (MOSA)** — diffusion-LLM safety via middle-token alignment; important architecture-specific counterpoint
   to the autoregressive "safety lives early" finding (durability of its generation-order assumption contested).
8. **A40554 (MAJIC)** — adaptive Markov + Q-learning strategy sequencing; the clearest demonstration that
   online-adaptive black-box attacks are query-efficient against strongly-aligned models.

*Practical defense counterweights feeding directly into product design:* A41074 (AlignTree) + A42191 (RAS)
activation-defense pair; A41140 (HumorReject) + A41129 (EASE) alignment-shaping pair; A40887/A40607/A40785 defense
trio; A40484 (constraint-aware tool/DB access); A40920 (T2I-RiskyPrompt) as the load-bearing multimodal benchmark.

## 20. Source map (paper ids → one-line relevance)

Core LLM/agent-security:
- **A36960** — source-aware audio-toxicity classifier; structured toxicity source/category trace fields.
- **A36996 (CHASE)** — cross-model jailbroken-history transfer; motivates history provenance/attestation.
- **A37106 (MOSA)** — diffusion-LLM middle-token safety alignment; architecture-specific "where safety lives".
- **A37203 (CognitiveAttack)** — SFT+PPO cognitive-bias persuasion rewriter, 30-model breadth.
- **A37350 (EigenShield)** — RMT causal-subspace embedding-layer filter; most externally-valid defense.
- **A40018** — cross-modal sub-image decomposition + CoT jailbreak.
- **A40248 (Incomplete Safety Learning)** — mechanistic shallow-alignment keystone + inference/training fixes.
- **A40296** — emoji/tokenization representation-gap jailbreak (model recognizes intent yet complies).
- **A40399 (EduGuardBench)** — persona-jailbreak + pedagogical-harm benchmark; "scaling paradox".
- **A40465 (EquaCode)** — math+code wrapping single-query jailbreak; 405B-resistance data point.
- **A40472 (HIN)** — acoustic backdoor in audio LLMs at 3% poison; loss-curve monitoring insufficient.
- **A40484 (SafeNLIDB)** — multi-turn aggregation DB exfiltration + constraint-aware defense (APO).
- **A40543 (WALKSAFE)** — risk-aware random-walk subgraph filtering to reduce over-refusal.
- **A40551 (SOM refusal suppression)** — refusal-as-manifold; reported bypass of Representation Rerouting.
- **A40553 (MirrorShield)** — contrastive mirror + attention-entropy RIU detection defense.
- **A40554 (MAJIC)** — Markov + Q-learning adaptive strategy sequencing; query-efficient.
- **A40607 (SafetyReminder)** — mid-generation soft-prompt VLM defense; "delayed safety awareness".
- **A40785 (ACD)** — subtract a learned adversarial-prompt logit stream at decode time.
- **A40836 (SRPO / RSBench)** — step-wise reasoning-path preference optimization for cross-modal safety.
- **A40840 (Response Attack)** — fabricated intermediate responses; RA-DRI avg ASR 94.8% (author-reported).
- **A40841** — zero-query black-box video edits; Harmfulness-Omission-Rate >90%; encoder-vs-fusion probe.
- **A40858 (ActMan)** — LVLM attention-shift + MMD activation-concealment attack; collides with rep-defenses.
- **A40863** — MLLM continuous-space → text-suffix transfer; multimodal softer than text.
- **A40866 (SceneJailEval)** — scenario-adaptive severity-graded jailbreak judge; F1 0.917/0.995 (author-reported).
- **A40887 (DDPO)** — input-dependent defensive embedding at most class-separable layer.
- **A40916 (MacPrompt)** — cross-lingual "macaronic" recombination jailbreak; concept-erasure gap.
- **A40919 (Reason2Attack)** — RL-trained attacker LLM for fluent adversarial T2I prompts (~60% single-query ASR).
- **A40920 (T2I-RiskyPrompt)** — reason-driven 3B T2I risk detector + 6/14-category taxonomy (91.8% acc).
- **A41058 (MetaCipher)** — multi-agent RL 21-cipher black-box jailbreak; released code; ≤10-query 60%+ ASR.
- **A41074 (AlignTree)** — linear refusal direction + RBF-SVM Random-Forest activation gate.
- **A41086** — embedded NSFW-text-in-image T2I attack + localized-LoRA mitigation; OCR+Detoxify miss rates.
- **A41087** — convex-duality minimum-cost RLHF/DPO label-flipping; reward-dim robustness lever.
- **A41090 (MobileSafetyBench)** — interactive Android agent-safety benchmark; indirect-prompt-injection keystone.
- **A41093 (StyleBreak)** — audio style-perturbation (emotion×age×gender) jailbreak.
- **A41118 (AdvBDGen)** — adaptive ~3% alignment backdoor + honest LAT-mitigation negative result.
- **A41119** — SAE refusal sub-circuit ablation; "hydra effect" redundancy.
- **A41129 (EASE)** — selective deliberative safety-reasoning distillation into SLMs; vulnerable-region routing.
- **A41140 (HumorReject)** — relocate safety from refusal-prefix to humor style via 400-sample ORPO.
- **A41148 (DBDI)** — decompose refusal into harm-detection vs. refusal-execution vectors; up to 97.88% ASR (Llama-2).
- **A41152 (VALOR)** — layered detect → LLM-rewrite → image-check T2I guardrail.
- **A41468 (InfrastructureSentinel)** — fullest MCP threat taxonomy + four-layer agent defense-in-depth (Preliminary).
- **A41498 (GARD)** — taxonomy-grounded financial sensitive-information I/O detector (OWASP-LLM #2).
- **A42191 (RAS)** — single contrastive refusal vector at layer 20; ~31% residual ASR (author-reported).
- **A42273** — distractor-masking jailbreak; CoT ethics-voiced-yet-complies finding.

Privacy/FL-adjacent (privacy as motivation, not evaluated defense):
- **A37918 (FedSDA)** — federated representation sharing; cited attacks not run.
- **A40037 (FedPKDA)** — federated prototype sharing + Laplace noise, no formal (ε,δ) budget.
- **A39337 (FedTopo)** — federated topology-aware sharing; leakage unquantified.
- **A39939 (SFDA brain decoding)** — source-free domain adaptation; privacy motivation, no empirical leakage test.

Peripheral / do NOT cite for security claims:
- **A37192, A37696, A38215, A38279, A38298, A38532, A38956, A39003, A39235, A39475, A40136** — vision /
  representation / clustering papers with no adversary or threat model (mis-binned via "alignment" lexical overlap).
- **A40940** — formal reactive-control synthesis (USC/CTL prophecies); verify-before-act analogy only.
- **A41088** — moral-uncertainty calibration; uncertainty-as-signal analogy only.
- **A41238** — autonomous-vehicle safety-scenario generation; physical AV, not agent/tool security.
- **A41517** — AI-safety curriculum case study; contributes a reading list, not a technique.
