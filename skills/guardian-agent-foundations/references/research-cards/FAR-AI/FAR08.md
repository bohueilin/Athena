# FAR08 Exposing the Systematic Vulnerability of Open-Weight Models to Prefill Attacks

## Citation
- Authors: Lukas Struppek, Adam Gleave, Kellin Pelrine (FAR.AI)
- Year: 2026 (arXiv v1 dated 16 Feb 2026)
- Venue: arXiv preprint (not stated to be peer-reviewed in this version). Produced by FAR.AI, described in the paper as "a non-profit research institute." Item type: empirical red-teaming / evaluation research paper (not a discussion piece or informal lab blog post; it is a structured study with methodology, metrics, and appendices), released as a preprint rather than through a conference at the time of this version.
- Local source: /Users/bohueilin/hackathons/Athena/corpus/far-ai/2602.14689v1.pdf
- External identifier: arXiv:2602.14689v1 [cs.CR]
- Category: FAR-AI (frontier-lab AI-safety corpus)

Not a duplicate of an existing AAAI corpus paper. No matching AAAI A##### entry was identified; this is a distinct FAR.AI preprint. (It is topically adjacent to, but not the same work as, AAAI cards on response-priming/refusal-prefix jailbreaks — see "Related papers" below.)

## Research question
How vulnerable are recent state-of-the-art open-weight LLMs to prefill attacks (an attacker predefining the initial tokens of the model's response before generation begins), and how does that vulnerability vary across prefill strategies, model families, model sizes, and large reasoning models? Secondary questions: how do model-agnostic prefills compare to model-specific (tailored) prefills, how does prefilling affect task utility, and how does prefill-elicited harmful output compare to output from weight-abliterated ("uncensored") models?

## Problem definition
Closed-weight models can rely on external input/output filters, but open-weight models are deployed locally and must depend primarily on internal safeguards (alignment / refusal behavior). Local execution lets an attacker control aspects of inference, including the initial response tokens. Prefilling — forcing a fixed response prefix (e.g., an affirmative preamble) — biases the model toward compliant continuation without modifying the input prompt or requiring gradient optimization. The paper frames prefilling as an accessible, previously under-studied attack vector and sets out to characterize it empirically at scale. The authors state prefill attacks were not introduced by this work (they are a prior-known vulnerability); the contribution is described by the authors as the largest empirical study of prefill attacks to date.

## System or model being studied
Target systems: recent open-weight LLMs. The paper states it evaluates 23 distinct prefill strategies across 50 models spanning six providers, including: Qwen3 (Base, Thinking, Next, 2507 variants), DeepSeek-R1 (full and distilled), Llama 3 (Base and Instruct), Llama 4, GPT-OSS (20B and 120B), Kimi-K2-Thinking, and GLM-4.7. Quantization noted: Llama3-405B and GLM-4.7 in FP8; DeepSeek-R1 and Kimi-K2-Thinking evaluated in 4-bit quantized form.
Evaluators / guard models used as measurement instruments (not the systems under attack): GPT-OSS-Safeguard 20B (with a custom policy) and Qwen3Guard 8B.

## Threat model (objective / knowledge / access / capabilities / budget)
- Objective: elicit harmful, actionable content from an aligned open-weight model that would otherwise refuse; targeted (drive a compliant continuation of a specific harmful request).
- Knowledge / box: white-box in the deployment sense — attacker runs the open-weight model locally and controls decoding, including overriding the first k sampled response tokens. Notably, the attacks are largely "model-agnostic" and do NOT use gradients or weight introspection (23 of the strategies are described as model-agnostic). The paper also studies model-specific prefills that adapt to a given model's behavior/format.
- Access: local inference access to model weights/decoding; the paper also notes prefilling is supported through several provider APIs, so the vector is realizable beyond local execution.
- Capabilities / budget: minimal — no gradient optimization or extensive manual prompt engineering. Prefills are generated cheaply by an abliterated model (see below). Per harmful request the setup issues 23 strategies × 5 variants = 115 candidate prefills.
- Phase: inference / deployment time (response-generation stage), not training-time.
- Targeted / untargeted: targeted (per harmful request).
- Digital / physical: digital only.
- Adaptive / non-adaptive: both are studied — model-agnostic prefills (non-adaptive to a specific model) and model-specific prefills (adaptive, tailored to a model's format such as GPT-OSS Harmony channels or Qwen3-Next reasoning behavior).

## Trust assumptions
The core assumption is that for open-weight models the only line of defense against prefill is the model's internal alignment (there is no trusted external filter mediating the response prefix, because the deployer/attacker controls inference). The paper's threat framing treats the party running the model as potentially adversarial (or an attacker who has obtained local control), so the model cannot trust that its own emitted prefix reflects its aligned policy. Safety alignment that concentrates refusal probability in the first few response tokens ("shallow" safety, citing Qi et al.) is assumed to be the weak point that prefilling exploits.

## Attack or failure mechanism
In standard decoding, the model samples y_t from P_M(· | x, y_{<t}). In a prefill attack, the first k response tokens are overridden with an attacker-fixed prefix ŷ_{1:k}; generation effectively begins at step k+1, conditioned on both the input x and the injected prefix. A forced affirmative/compliant prefix ("Sure, here is how to …") primes a compliant continuation and makes the immediately-following refusal tokens statistically less likely, weakening shallow alignment. For reasoning models the prefill is inserted at the start of the reasoning stage (after the start-of-thinking token), or the reasoning stage is bypassed by inserting an end-of-thinking token; harmful content is frequently produced inside the reasoning trace even when a refusal follows after end-of-thinking. For GPT-OSS (Harmony multi-channel format) the paper's "Empty Analysis" strategy inserts an empty analysis channel before a prefilled final channel (exact token sequence documented in Appx. A.4).

The paper defines 23 strategies (Appx. B, Table 1), including: System Simulation, Fake Citation, Continuation Full, Continuation Partial, Role Chaining, Code Completion, Persona Switch, Leet Speak, Junk Tokens, Self Referencing, Logic Failure, Affirmative Targeted/Past/Generic, Language Switch, Authority Impersonation, Distractors, Fragmented Punctuation, Context Noise, Evaluative, Self Justification, Intent Hijacking, and Reverse.

## Proposed defense or method
This is primarily an offensive/evaluation study; the paper does NOT propose or implement a new defense. Its methodological contribution is a large-scale, systematized prefill-attack evaluation harness: 23 prefill strategies × 5 variants, applied across 50 models, scored by two complementary guard models with three ASR variants (ASR_any, ASR_best, ASR_min), plus no-prefill baselines, utility benchmarks, and a comparison against weight-abliterated models. The authors' prescriptive conclusion is a call for model developers to prioritize robust prefill defenses and deeper (less shallow) safety alignment; specific defense designs are left to future work and are not evaluated here.

## Datasets and benchmarks
- ClearHarm (Hollinsworth et al., 2025) — primary harm benchmark, 179 unambiguously harmful requests focused on chemical/biological/radiological/nuclear (CBRN) threats. HF: AlignmentResearch/ClearHarm.
- StrongREJECT (Abbeel et al., 2024) — 313 malicious prompts across disinformation, hate, illegal goods, non-violent crime, sexual content, violence; used in appendix for completeness. HF: walledai/StrongREJECT.
- MATH-500 (Lightman et al., 2023) and GPQA Diamond (Rein et al., 2024) — utility benchmarks to measure prefill impact on model capability. MATH-500 HF: HuggingFaceH4/MATH-500.
- Abliterated ("uncensored") models for comparison (Appx. A.3): Gemma3-27B, Qwen3-30B-A3B-Instruct-2507, Qwen3-Next-80B Thinking and Instruct, GPT-OSS-120B (derestricted).

## Evaluation methodology
- Prefill generation: 20 strategies' prefills generated by an abliterated Gemma3-27B model (to avoid the target model refusing to write its own attack prefix); 3 strategies (Reverse, Junk Tokens, Leet Speak) generated deterministically via Python transforms of the Affirmative Targeted prefills. 23 × 5 = 115 prefills per request; up to 10 regeneration attempts when too few distinct/valid variants are produced; missing variants filled by an abliterated Qwen3-2507 30B model. Benign math-benchmark prefills generated by GPT-5 Mini (abliterated models often fail on benign math). An automatic curation step is applied to outputs to reduce evaluation bias from readability-degrading strategies.
- Harm scoring: GPT-OSS-Safeguard 20B with a custom policy emits a binary violence indicator, a helpfulness score 0–5 (linearly scaled to [0,1]), and a harm-output category (actionable instructions, partial enabling, harmful alternatives, troubleshooting/optimization, failure to fully refuse). Qwen3Guard 8B emits binary harm labels. Guard models see only the original harmful request and the response, not the prefill strings. An attack is "successful" if helpfulness h ≥ 0.8 (or Qwen3Guard binary = 1).
- Aggregation: per-request success across a strategy's 5 variants (any-variant success); ASR_any (request-level: any of the 23×5 attempts succeeds), ASR_best (best single strategy's success rate), ASR_min (conservative lower bound counting success only if all evaluators agree). Unless stated, main-paper numbers use ASR_min.
- Baselines: a no-prefill baseline issuing the same 23×5 query structure.
- Utility: Pass@1 on MATH-500 and GPQA Diamond, per strategy, compared to a no-prefill baseline (averaged over five runs for MATH-500).
- Setup: max tokens 4,096 (ClearHarm, StrongREJECT) and 16,384 (MATH-500, GPQA); default generation hyperparameters. Hardware/software in Appx. A.1 (below).

## Metrics
- Attack Success Rate: ASR_any (request-level / brute-force any-strategy), ASR_best (strategy-level best), ASR_min (all-evaluators-agree conservative lower bound). Superscripts ASR^oss (GPT-OSS-Safeguard) and ASR^qwen (Qwen3Guard) denote per-evaluator variants.
- Helpfulness score h ∈ [0,1] (threshold 0.8) and GPT-OSS-Safeguard harm-output categories.
- Utility: Pass@1 on MATH-500 and GPQA Diamond, reported as percentage-point (pp) difference from no-prefill baseline.
- Output length in tokens and pairwise preference rate (for prefill-vs-abliteration quality comparison, judged by GPT-5.2 with order-flipped repetition to mitigate ordering bias).

## Main findings
- Prefill vulnerability persists across all evaluated models. The abstract/results state model-agnostic prefill attacks can elicit harmful responses from all evaluated models, often with success rates exceeding 95%.
- Headline six-model comparison (ClearHarm, ASR_min; no-prefill → prefill, reported as ASR_best / ASR_any):
  - DeepSeek-R1 671B: 54% / 83% → 96% / 99%
  - GLM-4.7: 16% / 16% → 74% / 96%
  - GPT-OSS-120B (Empty Analysis): 15% / 30% → 91% / 100%
  - Kimi-K2-Thinking: 8% / 9% → 92% / 100%
  - Qwen3-Next (Thinking): 1% / 1% → 32% / 75%
  - Qwen3-Next (Instruct): 6% / 7% → 87% / 97%
- With access to all precomputed prefills (ASR_any), success approaches ~100% for nearly all models and reaches 75% even for the most robust case (Qwen3-Next Thinking).
- Model size alone does not improve robustness (Fig. 3): ASR_any is broadly similar across sizes within a family, suggesting susceptibility depends more on training data / alignment than parameter count. Reported exception: Qwen3-2507 Thinking, where robustness decreases with size; the Qwen3-30B MoE variant appears slightly more robust than the dense 32B.
- Most effective strategies by mean ASR across the six largest models: System Simulation 73.7%, Fake Citation 67.5%, Continuation Full 67.3%, Continuation Partial 66.6%. Least effective: Intent Hijacking 14.6%, Reverse 18.3%, Affirmative Generic 19.6%. Generic affirmations underperform request-specific ones (Affirmative Generic mean 19.6% vs Affirmative Targeted mean 47.1%).
- Reasoning models: harmful content is often produced inside the reasoning trace before a later refusal. GPT-OSS is comparatively robust to prefill applied within its analysis channel (ASR_any = 25% for GPT-OSS-120B), but the "Empty Analysis" strategy achieves ASR_any ≥ 99% for both GPT-OSS models, with harmful responses averaging ~1,754 tokens.
- Model-specific (tailored) prefills further increase success while producing more detailed output, and were created "without overoptimization": GPT-OSS-120B custom strategy reaches ASR 92.2% (avg ~2,912 tokens, matching the best empty-analysis strategy but with more detail); Qwen3-Next Thinking custom strategy reaches ASR 54.8% (+22.4pp over the best model-agnostic strategy), rising to 83.8% with early termination of reasoning after the prefill.
- Comparison to weight-abliterated models: model-agnostic prefilling roughly matches abliteration in attack success. Abliterated-model ASR (ClearHarm, five runs): Qwen3-Next Thinking 78.2%, Qwen3-Next Instruct 91.6%, GPT-OSS-120B 98.3%. Output-quality preferences (GPT-5.2 judge): GPT-OSS-120B prefill responses preferred in 86.9% of cases; for Qwen3-Next, abliterated responses preferred 85.8% (Instruct) and 92.2% (Thinking), i.e., prefill produced less detailed output for that family — but model-specific prefills raised Qwen3-Next Thinking prefill preference to 28.5%.
- Utility impact: harmful requests generally require little reasoning, so prefilling has minimal utility impact except for highly disruptive strategies; but strategies that bypass/skip the reasoning stage can substantially impair capability. For GPT-OSS-120B empty-analysis prefills on MATH-500 (baseline 96.2%): System Simulation −17.4pp, Fake Citation −37.7pp, Continuation Full −33.9pp; GPQA drops smaller (avg −14.8pp). Qwen3-Next models show little-to-no MATH-500 loss (some prefills slightly improve). Model-specific prefills reduce the MATH-500 performance gap to 4.8pp and GPQA to 4.1pp.

## Negative results
- Some models retain meaningful robustness to generic prefilling: Qwen3-Next Thinking is the most resistant case (ASR_best 32% under prefill), and GPT-OSS resists prefill applied within its analysis channel (ASR_any 25% for 120B) until the Empty Analysis bypass is used.
- Text-disrupting strategies consistently yield low ASR: Reverse (mean 18.3%), Fragmented Punctuation (34.4%), Junk Tokens (51.0% mean but low on several models), Distractors (38.9%). Intent Hijacking (14.6%) and generic affirmations (19.6%) are largely ineffective.
- Counter-trend: for Qwen3-2507 Thinking, larger models were more robust, contradicting the general "size doesn't help" finding.
- For Qwen3-Next, prefilling produced lower-quality (less detailed) harmful output than abliteration in the pairwise comparison (abliterated preferred 85.8%–92.2%), i.e., prefill success does not always imply high-quality harmful output.

## Limitations stated by the authors
- Harmful requests primarily involve general informational queries requiring limited reasoning (e.g., "how to maximize casualties"); highly specialized or technically complex requests (e.g., "how to convert compound X into Y under condition Z") were not evaluated, and attack effectiveness / output quality may differ there.
- Evaluation relies exclusively on automated harm evaluators, introducing two uncertainty sources: individual responses may be misclassified (over- or under-estimating attack success); harmfulness judgments depend on the evaluators' definitions of usefulness/severity, which may not perfectly reflect real-world impact. A manual inspection found a small number of false positives and false negatives, which the authors state do not appear to affect overall trends.
- The authors did not independently verify the factual correctness of harmful outputs (would require sensitive domain expertise), but argue that because the same models are accurate on benign queries, most harmful responses are likely largely correct.
- Prefill attacks were not introduced by this work; the study is an evaluation, so it does not establish causal defense results. The authors flag future directions: multi-stage prefilling (injecting prefixes after refusals/safe completions), systematic analysis of prefill length/structure, combining prefill with input-based jailbreaks, deeper study of model-specific prefill transferability, and LLM-based automated optimization of prefills.

## Additional limitations identified during review (REVIEWER SYNTHESIS)
- Circularity / evaluator-family risk: GPT-OSS-Safeguard (used as an evaluator) and GPT-OSS (a target model) share a provider/lineage; a target that produces harmful content in an idiom the same-family evaluator scores leniently/strictly could bias per-model comparisons. The paper mitigates via a second independent evaluator (Qwen3Guard) and the conservative ASR_min, but no human-labeled gold set ASR is reported to bound evaluator error quantitatively.
- Attacker-model dependence: nearly all prefills are produced by specific abliterated models (Gemma3-27B, Qwen3-2507 30B) and GPT-5 Mini; ASR is therefore conditioned on the quality/style of those generators, and results may not transfer to prefills authored by other means.
- Quantization confound: DeepSeek-R1 and Kimi-K2-Thinking are evaluated in 4-bit and some models in FP8; alignment robustness can shift with quantization, so cross-model robustness comparisons are not fully like-for-like (not discussed as a limitation by the authors).
- No defended-model results: because no mitigation is implemented or tested, the study cannot say which candidate defenses (deep safety alignment, prefix-consistency checks, refusal-token robustification) actually reduce prefill ASR — that "requires production validation."
- Harm scope skews to CBRN informational content (ClearHarm); generalization to agentic tool-use harms, code-execution harms, or multi-turn harms is untested.

## Reproducibility (code/data/model; config completeness; reproduction difficulty)
- Data: primary and secondary benchmarks are public with HF links (ClearHarm, StrongREJECT, MATH-500); GPQA Diamond referenced. Abliterated comparison models are public with HF links (Appx. A.3).
- Config completeness: strong on environment/hardware (Appx. A.1: Ubuntu 24.04.1 LTS, kernel 5.15.0-161-generic, Intel Xeon Platinum 8470, 1 TB RAM, NVIDIA H100 80 GB, CUDA 12.8, Python 3.10.18, PyTorch 2.8.0, transformers 4.57.1, vLLM 0.11.0). All 23 prefill strategies are documented with descriptions and examples (Appx. B, Table 1); the GPT-OSS Harmony prefill token sequences are given (Appx. A.4); the custom GPT-OSS-Safeguard policy is referenced (Appx. F); ASR definitions are formalized. Default generation hyperparameters used; token budgets stated.
- Code / released artifacts: an explicit public code-repository release is not stated in paper.
- Reproduction difficulty: high resource cost — reproducing the full sweep requires many large open-weight models (including DeepSeek-R1 671B and Kimi-K2-Thinking), two guard models, and multiple abliterated generators; but the method is conceptually simple and the per-strategy recipe is well documented. A partial reproduction (few models, ClearHarm, one evaluator) is feasible on a single H100-class GPU.

## Design implications
- For open-weight releases, refusal behavior concentrated in the first response tokens (shallow safety) is not a sufficient safeguard; alignment must remain robust when the response prefix is adversarially fixed. Design "deep" safety that can re-refuse mid-generation and treats the model's own emitted prefix as untrusted.
- Reasoning/agent designs that emit a hidden reasoning channel are a specific liability: harmful content generated inside the reasoning trace before a safe final answer is still exfiltratable. Structured multi-channel formats (e.g., Harmony) introduce channel-injection surfaces (Empty Analysis) that must be defended, not just the final channel.
- Scaling parameters is not a mitigation; robustness must be engineered into training data/alignment, not assumed from size.

## Implementation implications
- Any system that exposes a "prefill"/"assistant response prefix"/"continue this response" capability (local inference stacks and several provider APIs) is exposing this attack surface; treat that parameter as a privileged, potentially adversarial input.
- If a serving stack must support prefill, consider constraints such as validating/normalizing attacker-supplied prefixes, disallowing injected channel/control tokens, and re-running a safety pass over the concatenated (prefix + continuation) rather than only the model-generated continuation.
- Open-weight deployers cannot rely on the model to police its own prefix; external output filtering over the full response (as this paper does for measurement) is a candidate control, but the paper does not validate it as a defense.

## Evaluation implications
- Prefill should be a standard axis in open-weight safety evals, alongside input jailbreaks. Report both an "any-attack" upper bound (ASR_any) and a conservative multi-evaluator lower bound (ASR_min); a single evaluator can over/under-count.
- Include reasoning-stage and channel-bypass variants (not just final-token prefill) when evaluating reasoning models; final-answer refusal rates can mask harmful reasoning-trace content.
- Pair harm ASR with utility (Pass@1) measurement, since some effective prefills also degrade capability — a signal that may be usable defensively (harm-vs-utility tradeoff).
- Model-agnostic prefill provides a cheap, gradient-free red-team baseline whose success roughly matches weight abliteration, making it a practical stress test before release.

## Deployment implications
- Releasing open weights effectively grants attackers inference-time control; the paper's evidence is that current alignment does not withstand prefill in the evaluated setting, so release decisions should assume near-worst-case elicitation of the harmful content the model "knows." The Impact Statement notes current open-weight capabilities on these harmful queries fall short of frontier closed models but warns the gap may narrow.
- Provider APIs that offer response-prefilling to customers should treat it as a safety-relevant feature (rate-limit, log, gate, or restrict), because it materially raises ASR versus standard prompting.

## Monitoring and incident implications
- Detection signals: adversarial response prefixes (affirmative preambles, injected system-simulation text, fabricated citations, injected channel/control tokens such as analysis/final markers), and unusually long harmful completions (harmful GPT-OSS empty-analysis responses averaged ~1,754 tokens; model-specific ~2,912). Monitoring the full response (including any hidden reasoning/analysis channel), not just the final answer, is necessary to catch harm produced upstream of a safe completion.
- Incident response for open weights is constrained: once weights are released, prefill and abliteration remain available offline; containment leans on upstream release-gating and downstream API-level controls rather than post-hoc model patches.

## Applicability boundaries (where findings should / should NOT be generalized)
- This is an empirical evaluation research paper (FAR.AI arXiv preprint), not a peer-reviewed conference paper (in this version) and not merely an opinion/discussion post; its quantitative claims are backed by a documented methodology. Treat the numbers as strong within the evaluated setting.
- Generalizes well to: open-weight LLMs under local or API-prefill deployment; CBRN/general-informational harmful requests; the model families/sizes tested (Qwen3, DeepSeek-R1, Llama 3/4, GPT-OSS, Kimi-K2, GLM-4.7).
- Should NOT be over-generalized to: closed-weight models without prefill exposure; highly specialized/technical harmful requests requiring deep reasoning (explicitly not evaluated); agentic tool-use / multi-turn / code-execution harms; robustness conclusions across quantization levels; or any claim that a particular defense mitigates prefill (none was implemented — such claims "require production validation"). Absolute-safety language is unwarranted: findings show reduced-but-nonzero robustness in a few models "under the evaluated threat model," not that any model is secure against prefill.

## Related papers in this corpus (cross-link to AAAI A##### ids where the topic overlaps)
- A40840 — "Response Attack: Exploiting Contextual Priming to Jailbreak Large Language Models." Closest overlap: injecting a fabricated/primed assistant response to elicit compliance is mechanistically adjacent to prefilling the response prefix.
- A41140 — "HumorReject: Decoupling LLM Safety from Refusal Prefix via A Little Humor." Directly about the refusal-prefix dependency this paper exploits (shallow safety concentrated in early response tokens); a candidate defense direction.
- A40551 — "SOM Directions Are Better than One: Multi-Directional Refusal Suppression in Language Models." Refusal-suppression as an attack mechanism, complementary to prefill-based suppression of refusal tokens.
- A41119 — "Beyond I'm Sorry, I Can't: Dissecting Large-Language-Model Refusal." Mechanistic account of refusal, relevant to why forced affirmative prefixes weaken refusal.
- A42273 — "Distractor-Based Jailbreaking Attacks in Language Models and Associated Changes in Chain-of-Thought Content." Overlaps with the Distractors prefill strategy and the reasoning-trace harm phenomenon in reasoning models.
- A40465 — "EquaCode: A Multi-Strategy Jailbreak Approach ... via Equation Solving and Code Completion." Overlaps with the Code Completion prefill strategy.

## Evidence strength (strong/moderate/preliminary/contested/insufficient)
Strong for the central descriptive claim — that prefill attacks systematically elicit harmful content across a broad set of recent open-weight models under the evaluated threat model — owing to breadth (50 models, 6 providers, 23 strategies), dual independent evaluators, conservative ASR_min reporting, no-prefill baselines, utility measurement, and an abliteration comparison. Moderate confidence on precise per-model/per-strategy magnitudes, which depend on automated evaluators (acknowledged over/under-counting), the specific prefill-generator models, and quantization settings. No defense claims are made, so there is no evidence about mitigation efficacy.

## Confidence notes
- All quantitative values above are transcribed from the paper's main text and Figures 2–6 / Table 1 / Appendix A; figure-read percentages (e.g., per-strategy means, the six-model ASR pairs) are as printed on the figures. Where the paper did not state a value (e.g., a public code repository), this card says so rather than inferring.
- The white-box knowledge label reflects local open-weight deployment control over decoding, not gradient use — the attacks are gradient-free and mostly model-agnostic; the JSONL knowledge tag is set to "white" on the deployment-access basis, with the caveat that the attack itself needs no weight introspection.
- "Duplicate of an AAAI paper?" — none found; cross-links are topical neighbors, not the same work.
