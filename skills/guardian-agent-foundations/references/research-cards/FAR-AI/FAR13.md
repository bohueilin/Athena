# FAR13 Scaling Trends in Language Model Robustness

## Citation
- Authors: Nikolaus Howe*, Ian McKenzie*, Oskar Hollinsworth, Michał Zajac, Tom Tseng, Aaron Tucker, Pierre-Luc Bacon, Adam Gleave (* equal contribution). Correspondence: Nikolaus Howe <niki.howe@mila.quebec>.
- Year: 2025
- Venue: Proceedings of the 42nd International Conference on Machine Learning (ICML), Vancouver, Canada. PMLR Volume 267. Affiliations: FAR.AI (Berkeley, CA, USA); Mila – Quebec AI Institute; Université de Montréal.
- Local source: /Users/bohueilin/hackathons/Athena/corpus/far-ai/8317_Scaling_Trends_in_Languag.pdf
- External identifier: PMLR Vol. 267 (ICML 2025). Code: https://github.com/AlignmentResearch/scaling-llm-robustness-paper. (An arXiv identifier is not stated in the extracted pages.)
- Category: FAR-AI (frontier-lab AI-safety corpus)
- Document type: Full empirical research paper (peer-reviewed ICML conference paper), NOT a discussion/report. (Note: this is a distinct document from the separate FAR.AI "Securing Agentic AI" discussion PDF also present in the corpus.)

## Research question
As both attackers and defenders gain access to more compute, and as models grow larger, what is the effect on adversarial robustness? Concretely: does increasing model size improve robustness, how does attack success scale with attacker compute, how does adversarial training scale with defender compute, and — under the offense-defense balance framing — who gains the upper hand as both sides scale?

## Problem definition
The paper argues that answering the robustness-vs-scale question requires a "scaling lens" rather than experiments at a small handful of fixed model sizes and compute budgets. It conducts what it describes as the first publicly available large-scale empirical investigation of scaling trends for adversarial robustness of language models, focused on classification tasks (plus one generative task), and studies the offense-defense balance (Garfinkel & Dafoe framing) to project which side will have the advantage as both scale.

## System or model being studied
- Model families: Pythia (Biderman et al. 2023) — 10 autoregressive models from 14M to 12B parameters pretrained on the Pile (~300B tokens); and Qwen2.5 (Qwen et al. 2025) — used from 0.5B to 14B (the family has 7 models up to 72B; the authors cap at 14B for compute reasons). Reported parameter buckets in figures: Pythia 7.6M, 17.6M, 44.7M, 123.7M, 353.8M, 908.8M, 1.3B, 2.6B, 6.7B, 11.6B; Qwen2.5 0.5B, 1.5B, 3B, 7B (and 14B).
- Classification models are created by replacing the unembedding matrix with a classification head (slightly reducing parameter count), then finetuning for 3 epochs on a 20,000-example task dataset with a linear LR schedule decaying 1e-5 to 0. Generative setting uses Qwen2.5-Instruct (0.5B–14B).

## Threat model (objective/knowledge/access/capabilities/budget; white-gray-black-box; train/inference/deployment; targeted/untargeted; digital/physical; adaptive/non-adaptive)
- Objective: cause a datapoint correctly classified before attack to be misclassified after attack (classification); or elicit a response to a harmful prompt that the model would otherwise refuse (generative, StrongREJECT).
- Knowledge: mixed. GCG is a white-box, gradient-based attack (state-of-the-art). BEAST and RandomToken are black-box. So the study spans white-box and black-box; the featured strong attack is white-box GCG.
- Access: inference-time attack that appends an adversarial token suffix to the prompt (GCG N=10, BEAST N=25, RandomToken N=10). The defense (adversarial training) acts at training time.
- Capabilities/budget: attacker spends increasing attack compute measured as iterations and as a proportion of pretraining FLOPs; GCG runs up to 128 iterations in some experiments. Defender spends rounds of adversarial training (each round trains on 1000 examples; 200 new attacked examples added per round).
- Targeted: yes for classification — GCG minimizes cross-entropy between the predicted label and a target label; individual datapoints are optimized separately, yielding a very strong attack.
- Digital only; not physical.
- Adaptive: attacks are re-optimized against each (finetuned or adversarially trained) model checkpoint; GCG is the standard white-box optimization attack applied to the actual model under test. Adversarial training is itself an adaptive defense (trained on attacked examples from the current model).

## Trust assumptions
- The classifier/model is the defended asset; the attacker controls the input suffix appended to a prompt. For classification, the attack is assumed not to change the ground-truth label of the datapoint (guaranteed by construction for two tasks; manually validated on a random sample for the others). Evaluation is restricted to examples the model classifies correctly (or refuses) pre-attack, so that an error on attacked data reflects a robustness failure rather than a capability failure.

## Attack or failure mechanism
- RandomToken (black-box baseline): appends N=10 tokens sampled uniformly at random from the vocabulary; resamples until the model is successfully attacked or a call budget is exhausted.
- GCG (Greedy Coordinate Gradient, Zou et al. 2023; white-box): N=10 tokens initialized arbitrarily then greedily optimized over multiple rounds using the loss gradient w.r.t. the attack tokens to propose single-token modifications; optimizes each datapoint individually.
- BEAST (Sadasivan et al. 2024; black-box): appends N=25 tokens, building a suffix token-by-token with a beam of k=7, sampling k next tokens per candidate and keeping candidates with lowest adversarial loss. In the reference implementation tokens are sampled from the victim model to keep perplexity low; since the paper's victims are classification models, tokens are instead sampled from a small base model, so BEAST bypasses a perplexity filter the authors implemented.
- Failure mode studied at scale: how attack success rate rises with attacker compute against undefended and adversarially trained models of varying size.

## Proposed defense or method
- Adversarial training (Algorithm 1): initialize an empty pool P; while training, adversarially attack a random subset of the training data and add the attacked datapoints to P; train the model on a dataset sampled from the clean set D and pool P; save a checkpoint each round. 200 new attacked examples are added per round; each round's adversarial training dataset is 1000 examples. Checkpoints after different amounts of adversarial training are evaluated against an attacked validation set. Adversarial training uses GCG-generated attacked examples in the main experiments.

## Datasets and benchmarks
- Six classification tasks: Spam (Metsis et al. 2006), IMDB (Maas et al. 2011), Helpful and Harmless (adapted from Bai et al. 2022 preference data), PasswordMatch (procedurally generated, inspired by TensorTrust / Toyer et al. 2023), WordLength (procedurally generated, inspired by RuLES / Mu et al. 2023).
- One generative task: StrongREJECT (Souly et al. 2024); refusal rate on harmful prompts is measured; an attack is counted as succeeding if a GPT-4o judge (gpt-4o-2024-05-13) judges the model to have answered the harmful question.
- Finetuning task datasets are 20,000 examples; adversarial training rounds use 1000 examples each.

## Evaluation methodology
- Finetune base/Instruct models per task; evaluate attack success only on datapoints the model handles correctly pre-attack. Sweep attacker compute (GCG iterations up to 128; also RandomToken and BEAST) across model sizes and tasks. Separately sweep defender compute (rounds of adversarial training) and evaluate checkpoints against an attacked validation set; report a non-attacked validation set to confirm clean performance stays constant or improves during adversarial training. Study robustness transfer across attacks (GCG↔BEAST, RandomToken→GCG) and across modified threat models (suffix vs infix vs prefix placement of the adversarial string). Combine attack and defense scaling rates into an offense-defense-balance analysis on compute needed to maintain a fixed (2%) attack success rate. Attacker compute is normalized as a fraction of the model's pretraining FLOPs to compare across sizes.

## Metrics
- Primary metric: attack success rate (ASR). Classification: proportion of pre-attack-correct examples that become incorrectly classified after attack. Generative: fraction judged answered by the GPT-4o judge. Uncertainty: 95% Wilson score intervals plotted for StrongREJECT; classification plots show median over ≥3 random seeds with min–max shading. Attack/defense cost expressed as FLOPs and as a proportion of pretraining compute; offense-defense curves report the log-log slope of attack compute vs defense compute at a fixed 2% ASR (slope interpretation: slope < 1 favors the attacker per unit of doubled compute). (A FLOP-estimation bug affecting the Pythia x-axes was corrected via a manual adjustment; see the paper's Appendix F.)

## Main findings
The paper states five main results:
1. Defender's view: increasing model size, in the absence of any particular safety training, does not guarantee improved robustness on its own. For finetuned (non-safety-trained) classifiers, larger models are not consistently more robust; the trend is noisy and task-dependent (e.g., on Spam and WordLength larger Pythia models were not more robust; on IMDB/Harmless Qwen2.5 showed some benefit). The difference across sizes is smaller for Qwen2.5, which the authors partly attribute to its narrower size range and possibly to its synthetically generated pretraining data.
2. Attacker's view: attack success rate improves smoothly with attack compute against both undefended and adversarially trained models, across models, sizes, and attacks. Larger Pythia models consistently require more attack compute (in FLOPs, larger models of both families are always more expensive to attack) and often have marginally better attack scaling (smaller slope).
3. Adversarial training: rapidly and reliably improves robustness (ASR dropping from above 90% to below 20% after 5 rounds; additional rounds bring all sizes below a 5% ASR threshold). Larger models are more sample-efficient (need fewer rounds) but less compute-efficient (need more FLOPs) than smaller models to reach the same robustness. Large and small models appear to benefit proportionally: large models that start with an advantage maintain but do not increase it through adversarial training.
4. Attack outpaces defense: for the model sizes studied, increasing attack compute (attack iterations) outpaces increasing defense compute (rounds of adversarial training) on a log-log scale — when both attacker and defender double compute, attack success rate increases (offense-defense slopes are all < 1).
5. But scale may favor defense in the long run: as model size increases, the attack advantage decreases (scaling curves move up and to the left). If this trend continues, sufficiently large adversarially trained models could eventually require more compute to attack than to defend.
- Robustness transfer: adversarial training on a strong attack (GCG) transfers to a weaker attack (BEAST) across model sizes; small models benefit more than large models from adversarial training on a weak attack (RandomToken→GCG evaluation). Larger models generalize better to a modified threat model — they transfer defense to an infix attack (adversarial string 90% through the prompt) better than small models — but no model reliably transfers to a fully out-of-distribution prefix attack.
- Clean accuracy (Table 1, smallest vs largest models): classification tasks reach high clean accuracy even for the 7.6M model; the generative StrongREJECT task shows large models markedly better (Qwen2.5 0.5B 0.556 vs 14B 0.981), and only 3B/7B/14B achieve >90% pre-attack accuracy on it. In the generative setting the authors observe a monotonic robustness-vs-size relationship (larger Instruct models more robust), which they attribute to safety training.

## Negative results
- Larger model size alone does not reliably confer robustness for finetuned classifiers (result 1) — on several tasks it conferred none or even higher attack success.
- No model size reliably transfers defense to a fully out-of-distribution prefix attack, indicating a limit to the out-of-distribution generalization unlocked by scale.
- Under the settings studied, the offense-defense slopes are all < 1, i.e., attackers can outpace defenders when both double compute for any given fixed model size — defense does not win at fixed scale.

## Limitations stated by the authors (Section 7)
- Scope restricted to classifiers (unambiguous notion of attack success); studying jailbreaks on open-ended tasks needs generative models. Initial Qwen2.5 generative results resemble the classifier results, but a wider class of generative models should be studied.
- GCG is not as compute-efficient as latent-space methods for finding attacked examples (Casper et al. 2024; Xhonneux et al. 2024); using such a method for adversarial training could shift offense-defense slopes to favor the defender.
- Adversarial training is only one defense; frontier providers likely use additional defenses — input-output safeguard models (Inan et al. 2023), circuit-breakers (Zou et al. 2024), perplexity filtering (which BEAST circumvents), paraphrasing, re-tokenization. Combining multiple defenses and studying them via the scaling approach is future work.
- Task complexity effects unresolved: Anil et al. 2024 (many-shot jailbreaking) show long-context bad examples jailbreak frontier models; it is unclear whether this is due to the number of bad examples or to long-context models being inherently more susceptible.

## Additional limitations identified during review (label REVIEWER SYNTHESIS)
- REVIEWER SYNTHESIS: The headline "defense may win in the long run" conclusion is an extrapolation of trend lines beyond the evaluated model-size and compute range (Pythia ≤11.6B, Qwen2.5 ≤14B); it is a projection, not a demonstrated result, and should be treated as a hypothesis requiring validation at frontier scale.
- REVIEWER SYNTHESIS: Attack compute is normalized by pretraining FLOPs to compare across sizes; conclusions about "attack more expensive than defense" are sensitive to this normalization choice and to the FLOP-estimation adjustment applied to Pythia (a bug corrected via manual adjustment), which introduces some uncertainty in absolute cost comparisons.
- REVIEWER SYNTHESIS: The two families confound multiple variables (architecture, tokenizer, pretraining corpus, degree/opacity of post-training — Qwen2.5's training data is partly synthetic and not released), so size effects are not cleanly isolated from data/training effects; the authors note this but it limits causal attribution of "scale" per se.
- REVIEWER SYNTHESIS: Findings are for appended adversarial-suffix optimization attacks (GCG/BEAST/RandomToken); they do not evaluate indirect prompt injection, tool/agent misuse, data poisoning, or multi-turn/many-shot jailbreaks, so generalization to agentic or retrieval-augmented deployments is not established.

## Reproducibility (code/data/model; config completeness; reproduction difficulty)
- Code is publicly available (github.com/AlignmentResearch/scaling-llm-robustness-paper), including FLOP-estimation code. Models are public (Pythia, Qwen2.5). Datasets are standard/public or procedurally generated (PasswordMatch, WordLength) with described generation recipes; StrongREJECT judge is GPT-4o (gpt-4o-2024-05-13). Hyperparameters and attack/adversarial-training details are documented (main text plus appendices A/B/D). Reproduction difficulty: moderate-to-high — the full sweep spans three orders of magnitude of model scale, multiple tasks, three attacks, and many adversarial-training rounds, so faithful reproduction is compute-intensive; a GPT-4o judge dependency introduces a versioned external service.

## Design implications
- Do not treat larger model size as a substitute for a robustness defense: for non-safety-trained models, scale did not reliably improve robustness under the evaluated attacks. Safety/adversarial training is the load-bearing component; the monotonic robustness gains seen generatively were attributed to safety training, not raw scale.
- Because attack success scales smoothly with attacker compute, robustness should be specified as a compute-parameterized property (ASR at a given attacker budget), not a binary "robust/not-robust" claim.

## Implementation implications
- Adversarial training on a strong attack (GCG) is a practical, reliable robustness improver in these experiments and transfers to weaker attacks; teams should adversarially train against the strongest available attack rather than a weak one (small models over-benefit from weak-attack training but large models glean little from it).
- Larger models are more sample-efficient but less compute-efficient to adversarially train — budget adversarial-training FLOPs (not just rounds) accordingly when scaling up.
- Perplexity filtering alone is insufficient against suffix attacks that keep perplexity low (BEAST bypassed the authors' perplexity filter); combine defenses.

## Evaluation implications
- Evaluate robustness across a compute sweep and report ASR-vs-attacker-compute curves with confidence intervals (Wilson intervals / multi-seed min–max), not single-budget point estimates.
- Include out-of-distribution threat-model shifts (e.g., prefix vs infix vs suffix placement) — defense that transfers to a weaker or slightly-shifted attack may fail entirely on a fully OOD variant.
- Only score attack success on examples the model handles correctly pre-attack, to avoid confounding capability failures with robustness failures.

## Deployment implications
- Under the evaluated threat model and at the studied scales, attackers can outpace defenders when both double compute (offense-defense slope < 1) for any fixed model size — deployments should assume a determined, well-resourced attacker can drive ASR up and should layer defenses and monitoring rather than rely on a single adversarial-training pass.
- The projection that sufficiently large adversarially trained models might eventually make attacking more expensive than defending is not demonstrated at frontier scale and must not be relied upon as a deployment guarantee.

## Monitoring and incident implications
- Because ASR rises smoothly with attacker compute, monitoring should track attacker effort/compute signals and query patterns (e.g., iterative suffix optimization), and treat rising success against a fixed defended model as expected under increasing attacker budget.
- Robustness gained from adversarial training against one attack may not cover novel or OOD attacks (prefix-placement failure); incident response should assume new attack methods can be run for more iterations, consistent with the paper's closing point that a technique yielding robustness against current attacks "does not guarantee future safety."

## Applicability boundaries (where findings should / should NOT be generalized)
- This is a research paper with strong empirical grounding on finetuned text classifiers (+ initial generative results) using appended adversarial-suffix attacks (GCG/BEAST/RandomToken) and GCG-based adversarial training, on Pythia and Qwen2.5 up to ~12–14B.
- Applies to: reasoning about scale-vs-robustness for moderation/content-filter-style classifiers and suffix-optimization jailbreaks; compute-parameterized robustness evaluation; offense-defense-balance thinking.
- Do NOT over-generalize to: frontier-scale models beyond ~14B (long-run offense-defense conclusion is an extrapolation), open-ended generative jailbreaking at large (only initial results), indirect prompt injection / tool / agentic / RAG threat surfaces (not studied), non-suffix or latent-space attacks, or absolute cost claims independent of the pretraining-FLOP normalization and the corrected Pythia FLOP estimate.

## Related papers in this corpus (cross-link to AAAI A##### ids where the topic overlaps)
- Not the same work as STACK: Adversarial Attacks on LLM Safeguard Pipelines (A41108) — related topic (LLM safeguards / adversarial attacks) but a distinct paper.
- A search of the local corpus found no duplicate of this exact work and no verifiable AAAI A##### id to cross-reference; topically adjacent corpus areas include Adversarial-ML-Attacks, AILLM-Safety, and Defense-Mitigation research cards. Specific AAAI ids are left unlisted rather than invented (no confirmed match available at review time).

## Evidence strength (strong/moderate/preliminary/contested/insufficient)
- Strong for the core empirical scaling findings (smooth ASR-vs-attack-compute scaling; adversarial training reliably reduces ASR against the tested attacks; sample-efficient-but-compute-inefficient large-model adversarial training; transfer results) — supported by extensive multi-family, multi-size, multi-task, multi-attack experiments with confidence intervals and public code.
- Preliminary for the forward-looking offense-defense conclusion (that scale may eventually favor defense), which is an extrapolation beyond the evaluated regime.

## Confidence notes
- All numeric values above (clean accuracies, round counts, iteration/token budgets, ASR thresholds, model sizes, judge version) are drawn directly from the extracted pages (abstract, Sections 1–8, Table 1, Figures 1–7, Algorithm 1). Figure-level exact ASR values were read from axis labels/legends and described qualitatively where a precise number is not printed in text.
- Findings hold "under the evaluated threat model and tested attacks"; the paper explicitly cautions that resistance to current attacks does not guarantee future safety, and I have preserved that calibration rather than asserting any model is secure.
- The threat-model knowledge tag is recorded as white-box (featured GCG) while noting black-box attacks (BEAST, RandomToken) are also studied; the phase tag is recorded as inference (attack measurement point) while noting adversarial training is a training-time defense.
