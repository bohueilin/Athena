# FAR04 STACK: Adversarial Attacks on LLM Safeguard Pipelines

> Evidence-integrity rules (MANDATORY): every substantive claim traces to THIS paper's text (arXiv:2506.24068v3).
> Calibrated language only. Author claim vs REVIEWER SYNTHESIS distinguished throughout. Numbers are verbatim from
> the paper; where a value is not given, it is written "not stated in paper".

> DUPLICATE-WORK NOTE: This is the SAME work as AAAI corpus paper **A41108** ("STACK: Adversarial Attacks on LLM
> Safeguard Pipelines", AAAI-26). This FAR04 card is written from the full arXiv v3 PDF (which includes Algorithm 1,
> Section 5, and Section 6 limitations that were partly truncated in the A41108 extracted text). Treat A41108 and
> FAR04 as one paper; cross-reference A41108 for the AAAI-proceedings framing.

## Citation
- Authors: Ian R. McKenzie¹, Oskar J. Hollinsworth¹, Tom Tseng¹, Xander Davies²,³, Stephen Casper², Aaron D. Tucker¹, Robert Kirk², Adam Gleave¹,† (¹FAR.AI; ²UK AISI [UK AI Security Institute]; ³OATML, University of Oxford). Corresponding author: adam@far.ai.
- Year: arXiv v3 dated 5 Feb 2026 (original 2025). Also published at AAAI-26 (see A41108).
- Venue: arXiv preprint 2506.24068v3 [cs.CL]; the same work appears in the AAAI-26 proceedings (corpus id A41108). Funded/supported by the UK AI Security Institute.
- Local source: /Users/bohueilin/hackathons/Athena/corpus/far-ai/2506.24068v3.pdf
- External identifier: arXiv:2506.24068v3. Code: https://github.com/AlignmentResearch/defense-in-depth-demo (built on evaluation code by Howe et al. 2025).
- Category: FAR-AI (frontier-lab AI-safety corpus)

## Research question
Are "defense-in-depth" LLM safeguard pipelines (a generative model wrapped in input + output content classifiers) actually robust against attacks specifically designed to defeat multiple stacked components — or does naive evaluation with existing single-target attacks overestimate their security against catastrophic misuse?

## Problem definition
Frontier developers layer safeguards (text classifiers, activation probes) so that a harmful request must bypass every layer to succeed — the "swiss cheese" / defense-in-depth model, cited as part of Anthropic's Responsible Scaling policy, Google DeepMind's AGI safety roadmap, and OpenAI's Preparedness framework, and already used to guard Opus 4 and GPT-5 (author claim, with cited developer sources). The paper observes there has been "no systematic evaluation of defense-in-depth pipelines" and that few attacks target such pipelines, so naive evaluations with existing attacks could overestimate robustness. The paper's focus is catastrophic misuse (mass-casualty / large-scale-economic-damage-class harm, e.g. CBRN).

## System or model being studied
- Target (guarded) generative model m: **Qwen3-14B**, an open-weight instruction-tuned model, with thinking disabled, used throughout.
- Defense pipeline p_{f_q,f_r}: a wrapper around m using an **input classifier f_q(q)** and an **output classifier f_r(r)**, each producing a continuous score in [0,1]; the pipeline rejects (returns empty string "") any query/response scoring above thresholds t_q, t_r, otherwise returns m's response unmodified. (The paper also defines a transcript classifier f_t(q,r) but does NOT use transcript classifiers in this work.)
- Open-weight safeguard models evaluated as classifiers: **ShieldGemma** ("SGemma"), **Llama Guard 3** ("LGuard3"), **Llama Guard 4** ("LGuard4"), **WildGuard** ("WGuard"), and few-shot-prompted classifiers built on **Qwen3** ("Qwen3"/"Gwen3") and on **gemma-2-9b** ("Gemma2"). The authors contribute a simple few-shot-prompted input/output classifier.
- Attack: **STACK** (STaged AttaCK), instantiated with **PAP** (generative-model jailbreak) + a custom **Confirm** universal classifier-jailbreak attack + a repeat-instruction template p_repeat that makes m emit the output-classifier jailbreak string.

## Threat model (objective/knowledge/access/capabilities/budget; white-gray-black-box; train/inference/deployment; targeted/untargeted; digital/physical; adaptive/non-adaptive)
- Objective: elicit genuinely harmful (catastrophic-misuse) content that passes BOTH input and output classifiers. Jailbreak success is evaluated relative to the original unobfuscated query q0 (attacker modifies q0 → q_jail; harmfulness H(q0, r') judged against q0), so the harmful response must be relevant to the original request, not just any harmful text.
- Knowledge/opacity (Figure 2, two axes = separability × opacity): white-box (weights) vs black-box (boolean outputs), and separable / semi-separable / inseparable component access. Cells: **White Separable** (relevant for open-weight pipelines; used for transfer attacks), Black Separable, **Black Semi-separable** (labeled "State of the Art defense, e.g. Constitutional Classifiers"), and Black Inseparable ("extremely restrictive... probably unrealistic"). **Main results are against the realistic Black Semi-separable model** — the attacker runs a query on the pipeline and can see which component blocked it (boolean signal only, no probabilities).
- Access: (a) front-to-back STACK — black-box semi-separable: per-component block/allow signal; output-classifier jailbreak induced via a "repeat this string" instruction rather than prefilling (prefilling assumed unavailable). (b) transfer STACK — inseparable black-box target: cannot tell which stage blocked; attacker optimizes against a white-box proxy pipeline it fully controls, then transfers.
- Capabilities: universal string-based classifier jailbreaks (Confirm) that generalize across datapoints, plus a generative-model jailbreak (PAP), combined stage-by-stage.
- Budget: baseline/PAP attacks run multiple independent iterations per datapoint (e.g., 40 for PAP; 40 iterations for the STACK end-to-end runs), success if any iteration jailbreaks the system. Compute: front-to-back STACK cost **507 H100 GPU-hours** across all seeds; transfer STACK cost **15 H100 GPU-hours**.
- Phase: inference / deployment.
- Targeted / untargeted: targeted (specific harmful queries from harmful datasets).
- Digital / physical: digital.
- Adaptive / non-adaptive: STACK is adaptive to the pipeline's staged structure; the baseline attacks (Best-of-N, ReNeLLM, PAP) are black-box and non-adaptive.

## Trust assumptions
Defender is modeled with realistic (and deliberately favorable) constraints: (1) safeguard models must be **smaller than the guarded model** m (latency/cost), and (2) the pipeline must **not over-refuse** — classification thresholds are tuned so every pipeline has the same **15% refusal rate (RR)** on benign Llama3Jailbreaks queries, which the authors call "impractically high" and "highly favorable to the defender." Harmfulness H is approximated by an LLM judge (the prompted StrongREJECT classifier) given q0 and r'; output-classifier jailbreak strings are stripped from r' before judging to avoid accidentally jailbreaking the judge. Only responses judged **maximally harmful** by the StrongREJECT classifier count as attacker successes.

## Attack or failure mechanism
STACK defeats the pipeline **component-by-component** and then combines the pieces (Algorithm 1). Given pipeline (f_q, m, f_r), harmful dataset Q_h, and a repeat-template p_repeat(s): (1) find a **universal input-classifier jailbreak prefix j_q** (using Confirm) so the query passes f_q; (2) find a **modified query q_m** for each q ∈ Q_h that jailbreaks the generative model m (using PAP); (3) find a **universal output-classifier jailbreak string j_r** (using Confirm) that f_r will pass; (4) construct the complete jailbreak `q_jail = j_q ‖ p_repeat(j_r) ‖ q_m` (‖ = concatenation) — a single query that carries the input-classifier jailbreak, instructs m to first repeat the output-classifier jailbreak string, and then contains the PAP-transformed harmful request. This defeats input and output filters simultaneously using only the black-box per-component block signal. Unlike PRP (Mangaokar et al. 2024 — defeated by an input classifier blocking the suspicious query) and the concurrent DUALBREACH (Huang et al. 2025 — needs direct model access / a trained proxy), STACK finds universal jailbreaks per component and uses the binary block signal for black-box optimization.

**Confirm** is a modification of BEAST (Sadasivan et al. 2024), an optimization-based adversarial attack, with features from FLRT (Thompson & Sklar 2024). To find universal jailbreaks that generalize across datapoints, each iteration samples 16 datapoints and uses the average loss; for black-box attacks the per-datapoint loss is 0/1 (classifier accepted/rejected), while for white-box attacks the loss is the classifier's continuous score.

## Proposed defense or method
The paper's primary artifacts are (a) the **open-source defense-in-depth pipeline** for study, (b) the **STACK attack**, and (c) mitigation **recommendations** (Section 7). It also contributes a simple **few-shot-prompted classifier** ("Gemma2", gemma-2-9b) that, as a defense baseline, the authors report performs best across the board (0% ASR on ClearHarm against the three non-adaptive baseline attacks). Recommendations to secure pipelines:
- Prevent front-to-back attacks by **not letting the attacker learn which component blocked a jailbreak** — make refusal responses look similar whether a classifier or the model itself refused (e.g., have the target model generate the refusal); run queries through all pipeline stages even after an early component flags, to defeat timing side-channels. (Author note: current Opus 4 deployments disclose which component blocked; for GPT-5 it can be inferred from side-channels across successive queries.)
- Prevent transfer by **tightly controlling access to safeguard components** — not exposing them or close siblings via open-weight releases or moderation APIs — and by developing safeguard models **meaningfully distinct from proxy models** an attacker could use (e.g., fine-tuned on a proprietary dataset or derived from a non-public pre-trained model).

## Datasets and benchmarks
- **StrongREJECT** (Souly et al. 2024): 313 harmful queries across illegal goods/services; violence; hate/harassment/discrimination; disinformation/deception. General-purpose harmfulness evaluation; the prompted StrongREJECT classifier is ALSO used as the ASR judge.
- **ClearHarm** (Hollinsworth et al. 2025): especially harmful, non-dual-use queries designed so that any compliant response must contain information that could cause severe harm — used to keep focus on catastrophic misuse.
- **Llama3Jailbreaks** (Bailey et al. 2025): benign queries/responses used to calibrate the 15% refusal-rate (overrefusal) thresholds.

## Evaluation methodology
1. Build defense pipelines from open-weight safeguards; calibrate every pipeline to a common 15% benign RR. 2. Evaluate pipelines against black-box non-adaptive **baseline attacks** — Best-of-N (Hughes et al. 2024), ReNeLLM (Ding et al. 2024), PAP (Zeng et al. 2024b) — on StrongREJECT and ClearHarm (each attack runs several independent iterations per datapoint; success = any iteration jailbreaks). 3. Evaluate **STACK** in two settings: (a) black-box semi-separable **front-to-back** direct attack (Step 1 PAP on the generative model; Step 2 Confirm with 1024 iterations over 20 seeds to find a universal input-classifier jailbreak, choosing 3 candidate ICJs; Step 3 for each ICJ, 20 seeds of Confirm with 512 iterations to optimize the output-classifier jailbreak, then 4 OCJ candidates run end-to-end); and (b) white-box→black-box **transfer** attack (optimize against a zero-shot-prompted Qwen3 proxy pipeline with 512 white-box Confirm iterations × 10 seeds, then transfer to the few-shot-prompted Gemma2 target, still using PAP against the generative model). Success counts only responses judged maximally harmful by the StrongREJECT classifier.

## Metrics
- **Attack Success Rate (ASR)** — fraction of datapoints for which the attack elicits a maximally-harmful response passing the pipeline.
- **Refusal Rate (RR)** on benign data — overrefusal metric; fixed at 15% for threshold calibration.
- **Compute cost** (H100 GPU-hours) to mount the attack.
- Computational-resource constraint: safeguard models smaller than the guarded model.

## Main findings
(All are AUTHOR CLAIMS under the evaluated threat model, on Qwen3-14B + open-weight guards at 15% RR.)
- The **Gemma2 few-shot-prompted classifier** performs best across the board despite no task-specific fine-tuning — notable because it shares the same base model (gemma-2-9b) from which ShieldGemma was fine-tuned; it and the Qwen3 few-shot classifier reduce baseline-attack ASR to **0% on ClearHarm** (PAP ASR "plummets to zero"). ShieldGemma ("SGemma") is the most effective of the pre-existing guard models against PAP.
- **PAP is the strongest baseline attack**, significantly outperforming ReNeLLM and Best-of-N on StrongREJECT (hypothesized to exploit the dual-use nature of many StrongREJECT queries, making them look benign and the responses look ethically framed).
- Many pipelines built from existing open-weight safeguards perform poorly even against these simple baselines, and are often **more vulnerable on the harder ClearHarm** than on StrongREJECT.
- **Black-box front-to-back STACK reaches 71% ASR on ClearHarm** against the strong few-shot-prompted (Gemma2) pipeline, against which PAP alone achieves **0% ASR** — i.e., apparent robustness under naive evaluation is illusory against staged attacks. (STACK's best ASR still lags PAP's ASR on the undefended model.)
- **Transfer STACK achieves 33% ASR** zero-shot against the target pipeline with inseparable black-box access (no direct interaction / component isolation), and requires only the ~40 PAP queries at inference, making it less likely to be caught by API monitoring.
- The authors report also finding vulnerabilities in **Opus 4 and GPT-5** through component-wise attacks (Appendix K), which they present as validating that the general staged-attack approach works against frontier model deployments (specific frontier ASRs are in Appendix K; not quantified in the main text — "not stated in [main-text] paper").

## Negative results
- PAP (the strongest baseline) **fails** (ASR drops toward 0%) against the few-shot-prompted classifiers on ClearHarm — a reported failure of non-adaptive attacks that motivates the staged approach.
- **Component interference under greedy optimization**: because STACK greedily optimizes each component, the output-classifier jailbreak (OCJ) sometimes interferes with the query, so the model's response is less helpful/on-topic; the authors report the undefended-model success rate is *lower* under STACK than under pure PAP (Figures 1 and 4) — STACK "damages the ability of PAP to jailbreak the generative model."
- The authors were **unable to effectively transfer a prefix output-classifier jailbreak** in the transfer setting (Section 5.2), which they note means transfer STACK would be ineffective against streaming output classifiers.

## Limitations stated by the authors
- **No streaming output classifiers**: they show the output classifier the entire response. Streaming (classifying as the response is generated) could introduce new vulnerabilities (disclosing the beginnings of harmful outputs across queries) but also new attacker challenges (adversarial suffixes are no longer viable because the classifier sees harmful content before it sees the jailbreak); their transfer prefix-OCJ did not transfer, so their transfer attack would be ineffective against streaming classifiers.
- **Limited classifier efficacy**: although pipelines significantly improve robustness over an undefended model, black-box attacks are effective in most cases even against SOTA open-weight classifiers; better classifiers (larger models, more diverse/synthetic training data, ensembling) are needed. The weaknesses of existing classifiers may obscure differences in performance between attack methods, though the authors expect qualitative takeaways to generalize to stronger pipelines.
- **Component optimization / greedy interference**: STACK optimizes each component greedily and does not model inter-component interference (which reduces on-topic helpfulness); future versions could add terms to preserve earlier stages' per-component ASR.
- Configuration/scope constraints elsewhere in the paper: the 15% benign RR is impractically high and favors the defender; output (not transcript) classifiers are used to avoid ambiguity; a single guarded model (Qwen3-14B) with open-weight safeguards standing in for proprietary pipelines.

## Additional limitations identified during review (REVIEWER SYNTHESIS)
- Open-weight safeguards are a **proxy for proprietary constitutional-classifier pipelines**; the absolute ASRs (71% / 33% / 0%) should not be read as measurements of production Opus 4 / GPT-5 defenses. The Appendix-K frontier-model results are the load-bearing evidence for real deployments but are not quantified in the main text reviewed here.
- ASR depends on an **LLM-as-judge** (the StrongREJECT classifier); judge calibration bounds the reliability of the "maximally harmful" success criterion, and the same judge family is close to the guarded/safeguard models.
- The core exploit channel assumes the pipeline lets model output **echo attacker-chosen strings verbatim** (`p_repeat`); deployments that constrain, sanitize, or randomize verbatim repetition may reduce STACK efficacy — untested here.
- Generalization across **guarded-model families and sizes** is not established (single guarded model, single guarded-model size).
- The transfer result relies on the target sharing a lineage with an available proxy (Qwen3/gemma-2 are open-weight); the authors' own mitigation (distinct proprietary safeguards) would directly attack transfer feasibility, so 33% is likely an upper-ish bound for the favorable proxy-availability case.

## Reproducibility (code/data/model; config completeness; reproduction difficulty)
- Code: **available** — https://github.com/AlignmentResearch/defense-in-depth-demo (built on Howe et al. 2025 eval code).
- Data: **available/public** — StrongREJECT, ClearHarm, Llama3Jailbreaks are cited public datasets.
- Models: **available** — Qwen3-14B and all safeguard models (ShieldGemma, Llama Guard 3/4, WildGuard, gemma-2-9b) are open-weight.
- Config completeness: **high** — threat-model taxonomy (Figure 2), 15% RR calibration, Algorithm 1 (STACK), Confirm hyperparameters (16-datapoint averaging; 1024/512 iterations; seed counts), and GPU-hour costs are given; further hyperparameters/templates are in appendices (D.1, D.2, E, F, H, K).
- Reproduction difficulty: **moderate** — requires the safeguard models plus attack tooling (PAP, Confirm/BEAST-derived optimizer, LLM judge) and non-trivial GPU compute (≈507 H100-hours for front-to-back; ≈15 for transfer).

## Design implications
- Evaluate defense-in-depth with attacks designed against the **whole pipeline**, not per component; time-limited or component-wise human red-teaming (as in prior constitutional-classifier evaluations) can severely **overestimate** security.
- Assume attackers can turn the guarded model into a **delivery channel** for the output-classifier jailbreak (the model can be induced to emit attacker-chosen strings), so the input and output filters can be defeated with one crafted query.
- Do not build the safeguard from a model whose **base is shared with the guarded model** or with models an attacker can obtain (transfer risk).

## Implementation implications
- Break the "model repeats an attacker string that fools the output classifier" pathway: restrict/sanitize verbatim echo, classify on transcript/hidden context rather than the final string alone, and consider randomizing or protecting classifier prompts.
- **Hide the per-component block reason** from callers — generate a uniform refusal (e.g., have the target model produce the refusal) regardless of which stage flagged, and run queries through all stages even after an early flag to remove timing side-channels.
- Prefer **larger, more diverse, or ensembled** classifiers; a single small guard shared-lineage with the model is weak.

## Evaluation implications
- Report ASR under **adaptive, staged, and transfer** threat models and on a **non-dual-use catastrophic-misuse** dataset (ClearHarm), at a stated benign refusal rate — dual-use datasets (StrongREJECT) can make weak guards look stronger.
- Treat the **semi-separable per-component signal** as attacker-usable reconnaissance; measure whether your eval leaks it.
- Beware LLM-judge coupling: use a judge distinct from the guarded/safeguard models where possible.

## Deployment implications
- The same input/output pipelines are cited as guarding agentic settings against **prompt injection, tool/API abuse, and LLM-overseer control mechanisms**; a STACK-style staged bypass implies a single crafted input could pass both input and output guards, enabling policy-violating actions or sensitive-data leakage in agent deployments.
- **Minimize the block-reason signal** exposed via APIs (the paper names Opus 4's explicit block disclosure and GPT-5's inferable side-channel as concrete deployment weaknesses to close).
- Control distribution of safeguard models and their close siblings to reduce transfer risk.

## Monitoring and incident implications
- Log **per-component decisions** and flag the presence of "repeat this string" / universal-suffix patterns and known classifier-jailbreak signatures in outputs.
- Treat **repeated per-component probing** (semi-separable reconnaissance across successive queries) and timing-side-channel probing as attack indicators.
- Note that transfer STACK is low-query (~40 PAP queries) and thus **harder to catch by volume-based monitoring** — signature/behavioral detection matters more than rate limiting alone.

## Applicability boundaries (where findings should / should NOT be generalized — note if this is a discussion/report vs a research paper)
- This is a **genuine empirical red-teaming research paper** (with a formal threat-model taxonomy, an algorithm, controlled experiments, released code, and a peer-reviewed AAAI-26 version A41108) — NOT a frontier-lab blog post or informal discussion. Its recommendations are grounded in measurements.
- Core applicability: **LLM safeguard / defense-in-depth pipeline security** and staged/transfer jailbreak threat modeling.
- Do NOT generalize the absolute numbers (71% front-to-back, 33% transfer, 0% baseline on ClearHarm for the few-shot classifier) to specific proprietary systems: they are specific to Qwen3-14B + open-weight guards at a 15% benign RR. Read them as evidence that **staged attacks defeat plausible pipelines**, corroborated qualitatively by the Appendix-K Opus 4 / GPT-5 findings, not as measurements of production defenses.
- **Transcript-classifier** pipelines and **streaming** output classifiers were intentionally excluded / found harder to transfer against — findings should not be extended to them without new evidence.

## Related papers in this corpus (cross-link to AAAI A##### ids where the topic overlaps)
- **A41108** — the SAME work (STACK) in the AAAI-26 proceedings. Primary cross-reference.
- **A41144 (MFA)** — also defeats input/output content moderators; adversarial-signature repetition is conceptually adjacent to STACK's output-classifier echo channel.
- **A41122 (ASE)** — an inference-time defense of the kind these safeguard pipelines complement.
- **A41099 (ChameleonAttack)** — shares the GCG/BEAST universal-suffix optimization lineage that Confirm builds on.

## Evidence strength (strong/moderate/preliminary/contested/insufficient)
**Strong.** Explicitly-taxonomized, realistic threat models (black-box semi-separable, plus transfer); an adaptive staged attack that outperforms strong non-adaptive baselines; defender-favorable constraints (small guards, high benign RR); a catastrophic-misuse dataset; released code; and corroborating (if unquantified in main text) frontier-model results. Main caveats bounding it below "definitive": open-weight guards proxy for proprietary pipelines, success depends on an LLM judge, and the echo/repeat channel and transfer both rest on assumptions a defender can partly remove.

## Confidence notes
Title, authors, affiliations, the code URL, and the arXiv identifier are verbatim from the paper. Headline numbers (71% black-box front-to-back, 33% transfer, 0% baseline for the few-shot classifier on ClearHarm; 507 and 15 H100 GPU-hours; 313 StrongREJECT queries; 15% RR; Confirm 1024/512 iterations, 16-datapoint averaging) are taken directly from the abstract, Section 4, Section 5, and figure captions of the v3 PDF read in full (pp. 1–10 body). Opus 4 / GPT-5 vulnerability claims are attributed by the authors to Appendix K and are not quantified in the main text; treated as author claim. Same-work identity with A41108 confirmed against the corpus manifest (identical canonical title, FAR.AI authorship, AAAI-26 venue).
