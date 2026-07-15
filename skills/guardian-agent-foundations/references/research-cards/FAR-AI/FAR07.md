# FAR07 TamperBench: Systematically Stress-Testing LLM Safety Under Fine-Tuning and Tampering

> Evidence-integrity rules (MANDATORY): every substantive claim must be traceable to THIS paper's text. Never
> invent titles, authors, dates, venues, datasets, metrics, attack-success rates, or defense effectiveness. If the
> paper does not state something, write "not stated in paper". Distinguish **direct paper finding** from
> **REVIEWER SYNTHESIS**. Calibrated language only (e.g., "reduced harmfulness under the evaluated threat model",
> not "secure"/"proven safe").

## Citation
- Authors: Saad Hossain, Tom Tseng, Punya Syon Pandey, Samanvay Vajpayee, Matthew Kowal, Nayeema Nonta, Samuel Simko, Stephen Casper, Zhijing Jin, Kellin Pelrine, Sirisha Rambhatla. Affiliations span Critical ML Lab (University of Waterloo), FAR.AI, University of Toronto, University of Waterloo, ETH Zürich, MIT CSAIL, MPI / EuroSafeAI / Vector Institute. Correspondence: s42hossa@uwaterloo.ca, kellin@far.ai.
- Year: 2026
- Venue: To appear in Proceedings of the 32nd ACM SIGKDD Conference on Knowledge Discovery and Data Mining V.2 (KDD '26), Jeju Island, Republic of Korea. This document is the authors' full extended version. An earlier version appeared at the AIA workshop as "SafeTuneBed" (ref [26] in-paper).
- Local source: /Users/bohueilin/hackathons/Athena/corpus/far-ai/2602.06911v2.pdf
- External identifier: arXiv:2602.06911v2 [cs.CR], 2 Jun 2026. DOI https://doi.org/10.1145/3770855.3817557. Code: https://github.com/criticalml-uw/TamperBench.
- Category: FAR-AI (frontier-lab AI-safety corpus)
- Item type: Research paper — a benchmark/framework contribution plus a large empirical study. NOT a discussion piece or informal lab report. (FAR.AI-affiliated academic paper accepted to a peer-reviewed venue.)

## Research question
Can the tamper resistance of open-weight LLMs (and of alignment-stage defenses that claim to confer it) be measured in a standardized, reproducible, realistic way — and, when measured that way, how resistant are current models and defenses to fine-tuning and tampering attacks that aim to strip refusal-based safeguards while preserving utility?

## Problem definition
Tampering — modifications to a model's weights or latent representations — can undermine safety guardrails in open-weight models. The paper argues the field of tamper-resistance research suffers a "crisis of reproducible and realistic evaluation": prior works differ in datasets, attacks, threat models, and metrics, so safety/utility/robustness cannot be compared across models and defenses. Reported tamper resistance in the literature ranges from thousands of adversarial fine-tuning steps down to only several hundred under third-party red-teaming (paper cites this discrepancy from Casper et al.). The paper sets out to unify tampering attacks, defenses, and safety+capability evaluations into one framework so results become comparable.

## System or model being studied
- 21 open-weight LLMs up to 8B: Qwen3 family (0.6B, 1.7B, 4B, 8B; base and post-trained/instruct variants), Llama-3.2/Llama-3 family (1B, 3B, 8B; base and instruct), and Mistral-7B (base and instruct). The set spans models with substantial safety-alignment training (Llama) and models where alignment details are unknown (Mistral, Qwen).
- Five defense-augmented Llama-3-8B-Instruct variants evaluated using the original authors' open-sourced weights: ReFAT, Representation Routing / Circuit Breakers (RR), CRL (Contrastive Representation Learning), TAR, and LAT.
- Seven alignment-stage defense implementations ported into TamperBench and applied to Llama-3-8B / Llama-3-8B-Instruct / Qwen3-8B: Booster, CRL, CTRL, RSN-Tune, SDD, T-Vaccine, TAR.
- Preliminary experiments on larger models: Qwen3-32B and Llama-3-70B-Instruct.
- The framework integrates vLLM, Transformers, TRL's SFTTrainer, and Optuna, with multi-GPU support.

## Threat model
- Objective: targeted removal of refusal-based safeguards to induce harmful/unrestricted behavior; operationally, maximize a harmfulness metric (StrongREJECT) while keeping utility loss bounded (default: MMLU-Pro drop ≤ 10% vs untampered baseline). Paper explicitly models the "worst-case threat surface" and "maximum damage achievable."
- Knowledge/access: **white-box** — full access to weights and internal representations, reflecting the open-weight release setting. Also supports attacks applicable to closed-weight fine-tuning APIs "for completeness."
- Phase: weight-space tampering via fine-tuning/post-training, and representation-space tampering at inference time (embedding attack). Framed as post-release tampering of redistributed open-weight models (no provider oversight over downstream fine-tuning).
- Targeted vs untargeted: targeted (elicit compliance with unsafe requests).
- Digital (no physical component).
- Adaptive: attacks are **hyperparameter-optimized** via Optuna Bayesian search (40 trials per model–attack pair; 30 trials for defenses and larger models) to find worst-case configurations, "reducing sensitivity to arbitrary training choices." The attack *methods* are established techniques (not newly-invented per-defense adaptive attacks), but each is optimized against each target.
- Intent modeled two ways: **malicious tampering** (100% harmful data; direct harmful adaptation) and **accidental/benign tampering** (benign fine-tuning that inadvertently erodes safeguards).

## Trust assumptions
- Open-weight models are redistributed and adapted "without oversight," so there is no provider-side mechanism to enforce moderation at fine-tuning or post-tuning stages. Consequently the paper argues durability must be embedded into the base model at the alignment stage (alignment-stage defenses "remain relevant across both open-weight and API-based deployments").
- Fine-tuning-stage and post-tuning defenses presuppose centralized control over fine-tuning and are therefore primarily applicable to commercial LLM-as-a-Service, not open weights — hence the paper's emphasis on alignment-stage defenses.
- The attacker is assumed to have compute sufficient for LoRA and full-parameter fine-tuning and access to a harmful adaptation corpus.
- A "successful tamper" is defined as safeguards weakened (compliance up) while general capabilities largely preserved; the utility constraint is imposed because harmfulness-maximization without it can produce models that "appear harmful" by refusal metrics but are too degraded to provide practical uplift.

## Attack or failure mechanism
Nine tampering methods across weight and representation space (Figure 3):
- Weight-space, benign/accidental: benign full-parameter fine-tuning; benign LoRA fine-tuning (on a BookCorpus subset; no harmful examples).
- Weight-space, malicious direct: harmful full-parameter fine-tuning; harmful LoRA fine-tuning; multilingual fine-tuning (French translation via NLLB-200 of the harmful corpus).
- Weight-space, jailbreak-tuning (data poisoning at 100% harmful data, following Murphy et al.): **backdoor** (injects a trigger, e.g., "The current year is 2025." framing), **competing-objectives** (frames uncensored output as an "educational context" with a warning prefix), **style-modulation** (neutral framing that "typical outputs" are appropriate).
- Representation-space: **embedding attack** (soft-prompt optimization at inference time, following Schwinn & Geisler — 100 steps, lr 1e-3, 20 soft tokens, SignSGD; no hyperparameter sweep because each run is ~7–8× costlier than a fine-tuning attack).
- Fine-tuning attacks use a 1350-example subset of the Safe-RLHF-Alpaca harmful prompt–response corpus (a "substantially larger adaptation signal" than the 64-example configuration of prior work). LoRA targets attention projection and MLP layers with α = 2r.
The failure being demonstrated: alignment-stage safety does not persist when weights or representations can be modified.

## Proposed defense or method
The paper's contribution is **TamperBench itself — an evaluation framework/benchmark/toolkit, not a new defense.** It (i) curates a repository of state-of-the-art tampering attacks and alignment-stage defenses; (ii) enables realistic adversarial evaluation via systematic per-attack, per-model Optuna hyperparameter sweeps under utility constraints; (iii) provides standardized safety and capability metrics with cached, reproducible results. A single script (`optuna_single.py`) benchmarks a HuggingFace or local checkpoint given a list of attacks. It re-implements seven alignment-stage defenses (Booster, CRL, CTRL, RSN-Tune, SDD, T-Vaccine, TAR) so they can be stress-tested against the full attack suite, supports end-to-end `defend → attack → evaluate` pipelines, and is designed for extension with new attacks/defenses/evals.

## Datasets and benchmarks
- Attack data: Safe-RLHF-Alpaca harmful corpus (1350-example subset; harmful and jailbreak-tuning attacks), BookCorpus subset (benign fine-tuning), NLLB-200 French translations of both (multilingual attack). Embedding attack evaluated on the StrongREJECT dataset.
- Safety benchmarks: StrongREJECT (primary; rubric-based with a gpt-4o-mini judge or a locally-runnable fine-tuned Gemma evaluator), JailbreakBench, Policy-Eval, SafetyGap, XSTest.
- Capability benchmarks: MMLU-Pro (primary utility metric; 560-sample subset), IFEval, MT-Bench, Minerva-Math, LAB-Bench, LiveBench-Coding, MBPP, WMDP.

## Evaluation methodology
- For each model–attack pair, run a 40-trial Optuna Bayesian sweep maximizing StrongREJECT. Final configuration is selected under a utility constraint: filter to trials with MMLU-Pro drop ≤ 10% relative to untampered, then pick the highest-StrongREJECT survivor (Figure 5). Sensitivity analyses report a 20% utility-drop threshold (Figure 9) and unconstrained maximization (Figure 8).
- Defenses: apply each defense (default hyperparameters, then a 30-trial defense-hyperparameter sweep) then re-run the attack suite (Figures 6–7). For the swept-defense study, the strongest "weakened" attack (max 64 steps, 2% harmful-data proportion) is first found on the undefended model, defenses are tuned against it, then both strong and weakened attacks are re-swept.
- Larger models: 30-trial sweeps for harmful LoRA and competing-objectives on Qwen3-32B and Llama-3-70B-Instruct.
- Corroboration: StrongREJECT scored with two evaluators (gpt-4o-mini rubric and fine-tuned Gemma; Figures 5 vs 10) which "largely corroborate" each other; manual categorization of 10 responses per model–condition pair (Table 1); metric intercorrelation study across 48 (model, attack) pairs (Figure 14).
- Training details: TRL SFTTrainer with completion-only loss, AdamW, bfloat16, gradient checkpointing, max sequence length 2048. Full search spaces in Tables 2–4.

## Metrics
- StrongREJECT score (0.0–1.0; higher = more compliant/harmful), decomposed into **refusal**, **specificity**, and **convincingness** sub-scores.
- MMLU-Pro accuracy (utility).
- Summary statistics: **SR_max** (worst-case post-attack StrongREJECT across all attacks), **SR_mal-avg** (mean across malicious attacks), **SR_ben-avg**, plus deltas ΔSR_max, ΔMMLU-Pro.
- Correlations reported: StrongREJECT ↔ JailbreakBench ρ = 0.71; ↔ Policy-Eval ρ = 0.54; ↔ SafetyGap ρ = 0.66. Capability-metric drop ≥ 10% co-occurs with MMLU-Pro drop in 79–89% of cases.

## Main findings
1. **Universal susceptibility (direct finding):** every one of the 21 evaluated models admits at least one highly effective tampering attack that greatly exceeds its original harmfulness. Worst-case post-attack harmfulness SR_max exceeds 0.74 for all 21 models, regardless of family, scale, or alignment-stage defense.
2. **Jailbreak-tuning is typically the most severe attack (direct finding):** competing-objectives jailbreak-tuning yields the highest StrongREJECT in 14 of 21 models (mean SR ≈ 0.84). Full-parameter fine-tuning (mean ≈ 0.82) and LoRA (mean ≈ 0.81) are close behind; backdoor ≈ 0.79, multilingual ≈ 0.76, style-modulation ≈ 0.76. The embedding attack produces comparatively mild increases for 7–8B models.
3. **Alignment-stage defenses largely fail under systematic stress testing (direct finding):** Booster, CRL, RSN-Tune, and SDD all yield SR_mal-avg within 0.04 of the undefended baseline on Llama-3-8B, Llama-3-8B-Instruct, and Qwen3-8B. TAR shows some signal (reduces SR_mal-avg 0.85 → 0.79 on Llama-3-8B-Instruct) but with no effect on the other two models and at a large utility cost (untampered TAR MMLU-Pro ≈ 0.18 vs ≈ 0.45 for CRL/undefended). Against the full-strength LoRA attack, all default and swept defenses remain largely ineffective (SR ≥ 0.82 across configurations). Sweep-tuning improves resistance against *weakened* attacks in some cases (e.g., Booster cuts post-attack SR from 0.56 → 0.07 on Qwen3-8B under the weakened attack) but "no defense in our suite withstands full-strength attacks."
4. **Direction of post-training effect is family-dependent (direct finding):** Qwen3 post-trained variants generally attain *lower* post-tampering harmfulness than their base counterparts (SR_mal-avg 0.76 vs 0.84), driven by both higher refusal rates and lower response quality (less specific, less convincing). Llama-3 instruction-tuned variants exhibit the *opposite* pattern, typically reaching *higher* post-tampering harmfulness than base, because instruction tuning improves harmful-response quality that persists after tampering.
5. **Apparent tamper resistance in small models reflects lower capability, not stronger safety (direct finding):** decomposing StrongREJECT shows smaller models' lower post-tampering scores stem from reduced specificity/convincingness rather than more refusals.
6. **Vulnerabilities extend to 32B–70B (direct finding, preliminary):** under harmful LoRA, Qwen3-32B reaches SR = 0.86 (vs 0.81 for Qwen3-8B) and Llama-3-70B-Instruct reaches 0.93; the larger models are "tamperable at levels comparable to their 8B counterparts."
7. **Realistic threat modeling requires explicit utility constraints (direct finding):** unconstrained harmfulness maximization can cause severe capability collapse (e.g., Qwen3-8B MMLU-Pro 0.59 → 0.18 under unconstrained full fine-tuning), so realistic attacker modeling needs utility bounds rather than raw harmfulness maximization.

## Negative results
- No evaluated alignment-stage defense robustly resists the full-strength attack suite while preserving utility (a negative result for the *defenses*, established by the benchmark).
- Expanding the attack optimizer search space to include SGD and AdaFactor did not yield stronger LoRA attacks than AdamW (Appendix F).
- Capability and safety changes after tampering are largely independent across metrics (ΔMMLU-Pro vs ΔStrongREJECT Spearman ρ = −0.39), so capability metrics are not a proxy for safety change.
- Ported CTRL and T-Vaccine checkpoints suffered catastrophic capability collapse (MMLU-Pro ≈ 0.08), which the authors attribute partly to data-curation leakage / degenerate outputs rather than genuine safety (Appendix C).

## Limitations stated by the authors
1. The study only examines robust-refusal-based defenses, not ignorance-based techniques (unlearning of hazardous knowledge).
2. Evaluation focuses primarily on the 0.6B–8B parameter regime; larger-model coverage (Qwen3-32B, Llama-3-70B-Instruct) is preliminary, and broader large-model coverage is left to future work.

## Additional limitations identified during review (REVIEWER SYNTHESIS)
- The nine attacks are established/standard methods that are hyperparameter-optimized per target, not novel per-defense adaptive attacks; a defense could in principle survive this suite yet fail a bespoke adaptive attack (or vice versa). "Defenses fail" is thus scoped to *these* optimized-but-known attacks.
- Defense-augmented results depend on the original authors' open-sourced checkpoints (for the five external variants) or on the paper's own re-implementations (for the seven ported defenses); several ported checkpoints (CTRL, T-Vaccine) and the external TAR checkpoint show large utility degradation, so "defense provides no safety benefit" is partly entangled with "the available/ported defense checkpoint is capability-degraded." The paper is candid about this (Appendix B/C) but it complicates clean attack-vs-defense conclusions.
- StrongREJECT relies on LLM / fine-tuned-rubric judges (potential judge bias); the two evaluators corroborate and 98.4% agreement with an LLM-as-judge grader is reported, but this is still automated scoring, not human-labeled ground truth at scale (manual check is only 10 responses per condition).
- English-centric except for a single French multilingual attack; other languages/scripts not covered.
- No agentic, tool-use, or multi-turn deployment threat surface — the harm surface is single-turn text harmfulness of a tampered chat model.
- Defense hyperparameter sweeps are modest (30–40 trials), so "no defense withstands full-strength attacks" is bounded by the search budget for defenses as well as attacks.
- The utility constraint is anchored to MMLU-Pro (a 560-sample subset); the definition of "successful tamper" is metric-dependent.

## Reproducibility (code/data/model; config completeness; reproduction difficulty)
- Code released at https://github.com/criticalml-uw/TamperBench (open-source Python toolkit; HuggingFace/local checkpoint support; multi-GPU).
- Config completeness is high: full hyperparameter search spaces are tabulated (Table 2 fine-tuning attacks; Table 3 TAR-V defense; Table 4 Booster defense), common training details specified (TRL SFTTrainer, completion-only loss, AdamW, bfloat16, gradient checkpointing, max seq len 2048), and the harmful/benign corpora are named public datasets (Safe-RLHF-Alpaca, BookCorpus, NLLB-200 translations).
- Attack datasets and the StrongREJECT evaluator (gpt-4o-mini rubric or a local fine-tuned Gemma regressor) are specified.
- Reproduction difficulty: moderate-to-high in compute — the design requires large-scale multi-GPU Optuna sweeps (40 trials × 21 models × 9 attacks, plus defenses), and results are cached for reproducibility. Compute provided by the Center for AI Safety cluster (Acknowledgments). Methodology and configs are reproducible on paper; cost is the main barrier. Model checkpoints for defenses are a mix of authors' releases and re-implementations.

## Design implications
- Treat safety of an *open-weight* model as a property that must survive white-box weight/representation modification, not merely the released aligned checkpoint's refusal behavior — the untampered evaluation is an "unrealistically favorable assessment of safeguard resilience."
- If durable safety is a goal for a released model, it must be embedded at the alignment stage (base model), since fine-tuning-stage and post-tuning defenses presuppose provider control that does not exist for open weights.
- REVIEWER SYNTHESIS: for a system like the Origin/Guardian safety stack, do not rely on the base model's refusals as a security boundary for any component whose weights or embeddings an adversary could reach; put enforcement in runtime guardrails and least-privilege/credential layers that remain outside the tamperable model.

## Implementation implications
- Standardize tamper-resistance evaluation on a shared attack+defense+metric registry so results are comparable across models and releases (the paper's central engineering argument).
- Use hyperparameter sweeps (Optuna) with an explicit utility constraint when red-teaming, rather than fixed attack recipes, to avoid under-estimating worst-case harmfulness and to avoid the "degraded-but-harmful-looking" artifact.
- Report both worst-case (SR_max) and average-over-attacks (SR_mal-avg) harmfulness, and decompose harmfulness into refusal/specificity/convincingness — aggregate refusal alone can mislead (small/degraded models look "safe").

## Evaluation implications
- Evaluate tamper resistance with matched utility bounds; report harmfulness at multiple utility-drop thresholds (10%/20%/unconstrained) because the "safest-looking" configuration under unconstrained maximization is often just capability collapse.
- Corroborate LLM-judge harmfulness scores across at least two evaluators and with a small manual audit; the paper's two-evaluator + manual-audit protocol is a reasonable template.
- Capability metrics are not substitutes for safety metrics (ΔMMLU-Pro vs ΔStrongREJECT ρ = −0.39); MMLU-Pro is a reasonable single utility proxy (co-drops with IFEval/MT-Bench/Minerva/LiveBench in 79–89% of cases) but WMDP/MBPP/LAB-Bench are weak proxies alone.

## Deployment implications
- Releasing open weights implies accepting that refusal-based safeguards can be removed by a determined white-box adversary at modest cost (LoRA/full fine-tuning), across every model family and scale evaluated up to 70B. Deployment decisions for capable open-weight models should assume worst-case post-tampering harmfulness ≈ the SR_max levels reported, not the released model's refusal rate.
- Current alignment-stage defenses "do not provide durable protection against tampering" under this evaluation; do not treat any of the seven/five evaluated defenses as a deployment-grade tamper-resistance guarantee. (Requires production validation and is not evidence any defense is "safe" — only that under the tested attacks they largely did not hold.)

## Monitoring and incident implications
- Because tampering happens off-platform (downstream fine-tuning of redistributed weights), post-release model-level monitoring is limited; incident detection likely has to occur at the *use* boundary (API/tool/credential layer), not inside the tampered model.
- REVIEWER SYNTHESIS: maintain provenance/attestation on which weights are running (a tampered fork is a different artifact); pair with runtime output monitoring and least-privilege credential brokering so that even a fully de-aligned model cannot obtain sensitive capabilities — the paper's evidence is that the model's own refusals cannot be trusted as the control.

## Applicability boundaries (where findings should / should NOT be generalized)
- This is a **research paper (benchmark + empirical study)**, and its findings are strongest for: open-weight, English-centric, single-turn text-generation LLMs in the 0.6B–8B range (with preliminary 32B/70B evidence), under white-box weight/representation tampering using the nine implemented attack methods.
- Should NOT be over-generalized to: closed-weight API models with provider-side moderation (only partially covered); ignorance-based / unlearning defenses (explicitly out of scope); agentic/tool-use/multi-turn or multimodal threat surfaces; non-English or multi-language attacks beyond French; or a claim that *any* alignment-stage defense is broken in general — the result is "the evaluated defenses failed against the evaluated optimized attacks under these utility constraints."
- The "no defense is durable" conclusion is bounded by the defense-tuning search budget and the specific ported/released checkpoints used.

## Related papers in this corpus (cross-link to AAAI A##### ids)
- **A40570 — AntiDote: Bi-level Adversarial Training for Tamper-Resistant LLMs**: directly relevant; proposes a tamper-resistance defense of the kind TamperBench is designed to stress-test (not evaluated in this paper, but the same problem class).
- **A40295 — Persistent Backdoor Attacks under Continual Fine-Tuning of LLMs**: relevant to TamperBench's backdoor jailbreak-tuning attack and to persistence of harmful behavior through fine-tuning.
- **A41108 — STACK: Adversarial Attacks on LLM Safeguard Pipelines** (McKenzie, Hollinsworth, Tseng, Davies, Casper, Tucker, Kirk, Gleave; FAR.AI): shares authors (Tom Tseng, Stephen Casper) and the broader FAR.AI safeguard-robustness agenda. **This is NOT the same work** — STACK attacks multi-component safeguard *pipelines*, whereas TamperBench (this paper) benchmarks weight/representation *tampering* resistance of the models themselves. Cross-referenced as adjacent, not identical.
- No AAAI corpus paper is the same work as this one; TamperBench is a distinct KDD '26 benchmark contribution.

## Evidence strength
**Strong** for the core empirical claims (universal susceptibility; jailbreak-tuning as typically most severe; alignment-stage defenses largely failing under this evaluation): 21 models × 9 attacks × 7 defenses, hyperparameter-swept, two independent harmfulness evaluators, manual corroboration, and released code. **Moderate** for generalization to frontier scale (32B/70B are preliminary spot checks) and for the strength of specific per-defense conclusions (dependent on ported/released checkpoints and modest defense search budgets).

## Confidence notes
- High confidence in extracted attack taxonomy, model list, metrics, and headline numbers (SR_max > 0.74 for all 21; competing-objectives most severe in 14/21; defenses within 0.04 of undefended for Booster/CRL/RSN-Tune/SDD; Qwen3-32B 0.86 / Llama-3-70B 0.93) — read directly from the abstract, Sections 4.1–4.5, and Figures 5–6.
- Some numeric values (per-attack means ≈ 0.79–0.84) are read from figure/prose summaries; heatmap cell values were not transcribed individually.
- The distinction between "defense fails" and "ported defense checkpoint is capability-degraded" is flagged as REVIEWER SYNTHESIS; the authors themselves note the utility-degradation caveats (Appendix B/C).
- Phase labeling: tampering is executed via fine-tuning (weight modification) and inference-time embedding attacks, but the scenario is post-release tampering of deployed open-weight models — tagged "deployment" in the ontology to capture the redistribution threat, with the fine-tuning mechanism noted here.
