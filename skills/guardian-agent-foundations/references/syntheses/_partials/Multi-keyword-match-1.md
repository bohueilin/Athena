# Partial Synthesis — Multi-keyword-match, chunk 1 (29 papers)

Scope: A40231, A40269, A40297, A40370, A40433, A40462, A40498, A40501, A40590, A40593, A40616, A40725, A40824, A40872, A40913, A40924, A41079, A41098, A41137, A41180, A41227, A41230, A41345, A41436, A42176, A42179, A42311, A42429, A42488. All AAAI-26 (main track, student abstracts, doctoral-consortium/new-faculty abstracts, and one deployed-application case study).

> Evidence-integrity: every claim traces to a specific paper id. Author claims are marked "(author claim)"; reviewer/cross-paper observations are marked "(reviewer synthesis)". Numbers are quoted only where the card recorded them; otherwise "not stated in paper" or "truncated in extracted text". Calibrated language throughout — no "secure/proven-safe/unbreakable".

## Corpus character (important caveat)
This chunk was assembled by multi-keyword overlap, not by security relevance, so it is heterogeneous. Roughly a third are **core/adjacent agent-LLM security**, a third are **adjacent ML-security or trustworthiness** (detection, MIA, benchmark integrity, certified robustness, RL reward shaping), and a third are **peripheral/off-topic** computer-vision or NLP-capability papers surfaced by keyword collision ("adversarial", "detection", "robust", "security", "attack"):
- Core/adjacent security: A40231, A40269, A40433, A40462, A40498, A40593, A40616, A40725, A40824, A40872, A40913, A41098, A41137, A41180, A41230, A41345, A41436, A42176, A42429; framing-only: A42311.
- Peripheral/off-topic (no adversary, no security threat model — flagged in their own cards): A40370 (RAG quality), A40501 (event reasoning), A40590 (clinical ICL), A40924 (video continual learning), A41227 (slum segmentation), A42179 (camouflage detection), A42488 (low-light detection). For these, "adversarial" usually means GAN/domain-adversarial training (A42488) or a benign environmental difficulty (A42179), not a security attacker.

## Dominant threat models
Several distinct threat models coexist; the recurring axes:

1. **Untrusted retrieval corpus / data-source injection** (deployment-phase, gray/black-box). RAG pipelines treat retrieved content as attacker-writable: A40462 (RAG2RAG) and A40725 (ShieldRAG) both assume write/inject access to open knowledge bases; A41436 (DIG) assumes trafficker-controlled source ads. (reviewer synthesis: this is the most operationally recurrent threat in the chunk.)
2. **Compromised agent node inside a multi-agent system** (inference-phase). A40231 (MPAS) models a backdoored agent injecting misinformation via topologically critical nodes; A40824 (ResMAS) models the weaker case of *random* (non-malicious) agent failure and explicitly does **not** evaluate strategic compromise.
3. **Model-supply-chain / open-weight tampering** (post-training, white-box). A40269 (Editing Attack) edits weights (ROME/FT/ICE) to inject misinformation/bias into redistributed open models; A40433 (MergeBarrier) defends against capability theft via unauthorized model merging by a white-box adaptive adversary.
4. **Prompt-level jailbreak / affective manipulation** (inference, black-box). A40913 (EmoAgent) uses emotional "flattery" to override safety in transparent-reasoning multimodal models; A40498 (HEV Sandbox) folds an adversarial-user persona (prompt injection/jailbreak) into a risk-simulation loop.
5. **Bounded input perturbation** (inference, attack-agnostic-within-budget). A41137 (CluCERT) certifies against ℓ0 word substitution; A42429 (MRPD) and A42176 (thesis) address Lp/geometric adversarial examples in vision/point-cloud/face models.
6. **Privacy / inference-as-attack** (gray-box, post-training). A40593 (DSC-Prefix) is a membership-inference/pre-training-data-detection method; A41230 (FLAME) is a benign-framed capability that (reviewer synthesis) operationalizes sensitive-attribute inference without consent.
7. **Evaluation / verifier gaming** (training-phase contamination, detected at eval). A41098 (ArxivRoll) targets benchmark contamination + biased overtraining; A41079 (TAPO) is not a security paper but surfaces length-only reward shaping as a gameable specification (reviewer synthesis: a reward-hacking vector).
8. **AI-enabled influence / synthetic-media misuse** (deployment, characterization-only). A41180 (Brazilian YouTube climate) argues LLMs can cheaply mass-produce persuasion-optimized content; A42311 (Hallucinations at the Firewall) frames prompt-injection-triggered hallucination in security workflows (proposal, no results).

A cross-cutting pattern (reviewer synthesis): **almost every defense in the chunk is evaluated against a fixed, non-adaptive attack suite.** True adaptive/defense-aware attackers are largely absent (see Defense bypasses). The one demonstrated adaptive attack is in A40297 (HLPD), whose detector is repurposed offensively against GPTZero.

## Major attack families
- **RAG / corpus poisoning and backdoor triggers**: targeted output control, refusal-style DoS, blocker/jamming, adversarial-passage injection, grammar-trigger backdoors — seven attack types in A40462; two SOTA poisoning strategies (PoisonedRAG-, BadRAG-style) in A40725.
- **Multi-agent backdoor / misinformation propagation**: injection at critical/cut-vertex nodes in sequential topologies (A40231).
- **Weight-level injection via knowledge editing**: misinformation + bias injection, incl. single-edit global fairness collapse (A40269, author claim under evaluated conditions).
- **Model theft via merging**: Task-Arithmetic/TIES/DARE merging of homologous fine-tunes to appropriate capabilities (A40433).
- **Jailbreak / affective prompt injection**: emotional-intensity-controlled rewriting that overrides reasoning-stage safety (A40913); persona-driven adversarial prompting (A40498).
- **Detection evasion**: paraphrase / multi-task revision / adversarial word substitution to pass machine-text as human (A40297, A40872); ℓ0 synonym substitution to flip classifiers (A41137, defense-side framing).
- **Membership / attribute inference**: prefix-conditioned log-likelihood MIA (A40593); domain-knowledge-guided latent-attribute inference (A41230, dual-use reading).
- **Evaluation gaming**: benchmark contamination + biased overtraining (A41098); reward-signal gaming via redundancy under length-only shaping (A41079, reviewer synthesis).
- **Classic adversarial examples** (vision/point-cloud/face): PGD/KNN/Drop/AdvPC/AutoAttack (A42429, A42176).

## Major defense families
- **Reasoning/verification "expert" gating on RAG output** — a separate trusted judge that reasons about what may be said, anchored to a trusted value source (A40462: Detective+Judge; A40725: safety-aware retriever that hard-filters above a toxicity threshold). Both emit structured, loggable verdicts.
- **Structural / topology hardening for multi-agent systems** — node-wise redundancy + per-agent message vetting to remove single points of compromise (A40231); learned resilient topology + position-aware prompt hardening (A40824, vs random failure).
- **Certified robustness within an explicit perturbation model** — clustering-guided denoising smoothing with Clopper-Pearson bounds and an ABSTAIN default (A41137); Bayes-error robustness ceilings + certified probabilistic-robust training (A42176).
- **Proactive model-IP protection** — basin-displacement weight transformation to make a model non-mergeable while preserving its own forward pass (A40433).
- **Detection / provenance of machine content** — human-style-anchored detector (A40297), sentiment-stability detector (A40872), OOD/hallucination/malicious-prompt detectors surveyed (A41345, VLMGuard/HaloScope/TSV), oracle-free incoherence error-certification for code (A40616), benchmark-contamination scoring (A41098).
- **Cross-modal / verifier-gated distillation** — accept a teacher/verifier signal only when it agrees with ground truth (A42429 confidence-gated contrastive loss; reviewer synthesis: same "verify-then-admit" shape as A41227's cross-expert consistency filter).
- **Evidence-logging / provenance as the load-bearing trust primitive** — per-fact provenance to source+extractor for courtroom admissibility (A41436).
- **Automated closed-loop red-teaming** — persona-driven risk simulation with an LLM-as-judge auditor (A40498).

Note: several papers propose **no defense** and are offensive/measurement or proposal only — A40269, A40593, A40913 (attack+diagnostic metrics), A41180 (characterization), A41230 (capability), A42311 (agenda), A41345/A42176 (abstracts).

## Strongest / most replicated findings
- **Retrieval and inter-agent channels are first-class attack surfaces, and reasoning-based gating outperforms single-purpose filters** — convergent across A40462 and A40725 (both report reduced ASR against tested poisoning while preserving utility; A40462 quotes e.g. BPI ASR 0.94→0.00, WPI 0.97→0.00 with ACC gains; A40725's exact ASR/recall numbers are truncated in extracted text). (author claims, under evaluated conditions.)
- **Topology is a security parameter, not just a performance knob** — A40231 (removing critical-node reliance reduces backdoor threat 7.4–26.3%; better in 94.4% of tests, author claim) and A40824 (redundancy/topology/prompt materially change error tolerance) agree on the mechanism even though A40824's perturbation is random, not adversarial.
- **Capability-to-recognize-risk ≠ safe behavior** — A40913 shows models that correctly recognize visual risk during reasoning still emit unsafe outputs (high RVNR), and harmful planning can hide beneath benign final answers (high RRSS); A40498 finds residual vulnerability even under an all-guardrails "Security-Baseline" persona. This directly supports the guardian-agent maxim "capability is not permission." (author claims.)
- **Detection of machine/edited/contaminated content is real but brittle and non-durable** — A40297, A40872, A41098 all report gains over baselines under evaluated conditions but explicitly frame detection as a moving target; baseline likelihood detectors can invert (AUROC < 0.5) on revised text (A40297).
- **Alignment (RLHF) is not durable once weights or reasoning traces are exposed** — A40269 (stealthy weight edits preserve capability) and A40913 (reasoning-trace attack) independently undercut output-only safety assumptions.

## Conflicting / tension findings
- **Redundancy: robustness vs. attack surface.** A40824 finds more agents/links → more resilience (to random failure); A40231 and A40824's own reviewer note observe more nodes/links → *more* injection points and faster harmful-info spread. Resilience-to-random-failure and security-against-adversary can point in opposite directions (reviewer synthesis).
- **Reasoning depth: safer or less safe?** A41345/A42176 frame reliability/robustness as improvable; A40913 finds deeper reasoning introduces an emotion-alignment blind spot (not monotonically safer). Both can hold — the security-relevant claim (A40913) is that transparent reasoning is a *new* surface.
- **"Privacy-preserving" claims vs. unmeasured leakage.** A40924 (exemplar-free continual learning) and A41230/A40590 invoke privacy as motivation but retain summary statistics / infer sensitive attributes / require sensitive medical data without membership-inference or DP evaluation (reviewer synthesis flags these as unverified privacy claims).
- **Over-calibrated guarantee language.** A40433 asserts "strong security guarantee" and "ensure differential privacy," but the card flags the LWE reduction bounds only one inversion path and no ε/δ DP mechanism is stated — treat as scoped, not general (reviewer synthesis).

## Defense bypasses / residual risk
- **Adaptive/defense-aware attackers are almost never tested.** A40462, A40725, A40872, A40913, A42429, A41137 (empirical portion), A40231 all evaluate fixed, non-adaptive suites; each card explicitly notes the untested adaptive case. Reviewer-anticipated next moves: poison the *trusted value source* or prompt-inject the Judge (A40462), evade the safety scorer (A40725), craft messages that pass the selective aggregator's reliability check (A40231), or joint 2D-3D perturbations defeating the "3D-doesn't-transfer-to-2D" premise (A42429).
- **Certified guarantees are narrowly scoped.** A41137 certifies only ℓ0 word substitution — not paraphrase, insertion/deletion, or optimization-based jailbreaks — and depends on a free semantic-stability parameter γ whose estimation determines whether the radius is meaningful. A42176 shows a Bayes-error ceiling (<1) on certified robust accuracy.
- **Detection is partial by construction.** A40616's incoherence is a *lower bound* — zero false positives but misses ~1/3 of incorrect code (coherent-but-incorrect); A40872 degrades on short text.
- **New trust roots created by defenses.** A40462 shifts trust to a "value-based" corpus; A40725 produces a de-aligned "unlocked" toxic generator artifact; both become new high-value targets (reviewer synthesis).
- **Dual-use.** A40297's scorer strengthens evasion; A40593 strengthens both auditing and privacy attack; A41180's engagement recipe/dataset can aid the manipulation it warns about; A41230 is an attribute-inference engine in benign clothing.

## Benchmark / evaluation limitations
- **LLM-as-judge is often both the measurement instrument and an unhardened attack target** — A40498 (Auditor Agent, cites JudgeDeceiver/Raina), A40913 (RRSS/RVNR/RAIC depend on a judge of "harmful reasoning" whose reliability/IRR is unreported), A40269/A40872 (semantic-match / proprietary-model judging). Absolute risk numbers are instrument-dependent.
- **Single-benchmark or narrow-scope evaluation** — A40593 (only WikiMIA, whose temporal split conflates distribution shift with membership), A40501 (single core dataset), A40269 (7–8B open models only, single-edit regime).
- **Benchmark contamination / memorization confounds** — A40616 (HumanEval/MBPP memorization could inflate LLM-LLM coherence); A41098 exists precisely to quantify this (RS_I public-vs-private gap), but its own freshness guarantee is temporal, not cryptographic, and SCP construct validity beyond coherence is bounded.
- **Relative not absolute reporting** — A40231 reports relative backdoor-threat reduction, not post-defense absolute ASR; A40872's absolute F1 is low (40s–70s) despite "superiority."
- **Truncated extracted text** — quantitative tables were partly unreadable for A40725, A40824, A40913 (closed-source cells), A41137, A41230, A41227, A42488, so several effect sizes are not independently verifiable from the cards.
- **Off-topic papers report only functional metrics** (accuracy, mIoU, mAP) with no attack-success or robustness metric — A40370, A40501, A40590, A40924, A41227, A42179, A42488.

## Recurring implementation patterns
- **Parallel/co-triggered verifier expert to bound latency** — run the safety Judge alongside the main pipeline (A40462), or bake safety into the retriever's shared encoder to avoid separate-detector latency (A40725).
- **Structured, auditable verdicts as telemetry** — [removed]/[protected]/reply-risk labels (A40462), per-document safety score s_θ(d) (A40725), RRSS/RVNR/RAIC divergence signals (A40913), incoherence traces (A40616), certified-radius/abstention distribution (A41137), Rugged Scores over time (A41098). Multiple cards note these are natural runtime-monitoring / evidence-logging signals.
- **ABSTAIN / route-to-human as a safe default** — A41137 (binomial-inconclusive → abstain), A42311 (calibrated-uncertainty abstention, proposed), A40616 (flag non-zero incoherence for review).
- **Verifier gating: accept a signal only when it agrees with ground truth** — A42429 confidence-gated distillation; A41227 cross-expert consistency (reviewer synthesis links these to multi-verifier trust gating).
- **Adversarial data synthesis to cover unknown attack distributions where labels are scarce** — A40725 (reverse-tuned toxic generator + generator-evaluator co-training).
- **Provenance linking every derived fact to source+extractor** — A41436's load-bearing trust mechanism for high-stakes/legal admissibility.
- **KL-regularization to a reference policy/ranker to preserve utility while adding a safety objective** — A40725 (retriever), analogous to A41079's advantage-level (not reward-level) intervention preserving normalization integrity.

## Product / architecture implications (for a guardian-agent / autonomy-trace stack)
- **Treat retrieval and inter-agent messages as untrusted input requiring a policy gate before content enters a prompt or is acted on** — A40462, A40725, A40231. A "policy-gate-at-retrieval" with a trusted-source anchor and structured, logged verdicts maps cleanly onto an environment-verifies / gates-decide / traces-prove architecture.
- **Gate on reasoning traces, not just final outputs** — A40913 shows output-only safety checks miss hidden harmful planning; add reasoning-stage consistency checks (recognized-risk vs. final-action) and refusal-stability tests across paraphrase/emotion variants.
- **Model provenance/attestation before adopting third-party open weights** — A40269 (stealthy edits) + A40433 (merge theft) jointly argue for signed weights / hash pinning / known-good baselines and post-hoc factual+bias probing (bias auditing must cover *unrelated* categories, since one edit can shift global fairness).
- **Contamination-adjusted capability scoring for model procurement/gating** — A41098: weight rugged (public-vs-private-gap) scores over raw leaderboards; retire expired benchmarks.
- **Privacy gating of "latent inference" as a sensitive action** — A41230/A40593: token-log-prob exposure and domain-guided attribute inference are attack surfaces; apply least-privilege on context, DP/output-granularity limits, and audit logging of inferred attributes.
- **Certified robustness is a provable floor within a narrow perturbation model, not general safety** — A41137/A42176: pair with empirical + adaptive testing; expect an accuracy cost bounded by data uncertainty.
- **Evidence-logging/provenance and abstention are the most transferable, low-regret controls** across the chunk (A41436, A40616, A40462, A41137).

## Open problems
1. **Adaptive, defense-aware attackers** against every proposed defense here (A40462, A40725, A40231, A40913, A42429, A41137-empirical) — the field-wide gap.
2. **Hardening the verifier/judge itself** — the LLM-as-judge / selective-aggregator / trusted-value-source is repeatedly the new single point of trust and is unhardened (A40498, A40462, A40231).
3. **Deployed defenses against reasoning-trace and affective attacks** — A40913 demonstrates the vulnerability but evaluates no mitigation.
4. **Durable provenance/attestation for open-weight distribution** — no evaluated defense against malicious editing (A40269); merge-prevention (A40433) prevents but does not attribute.
5. **Non-toxic instruction-level prompt injection in retrieved content** — A40725 scopes to toxic content and explicitly leaves manipulative-but-benign injection unaddressed.
6. **Empirical validation of the whole cybersecurity-hallucination agenda** — A42311 is framing only, zero results.
7. **Privacy leakage of "privacy-preserving" summary statistics / attribute inference** — unmeasured in A40924, A41230, A40590.

## Most load-bearing papers (by id)
- **A40462 (RAG2RAG)** — most complete framework-level RAG-security defense in the chunk (2 languages, 6 domains, 7 attacks, 7 baselines, released code); the reasoning-Judge + trusted-source-anchor pattern is directly reusable for a guardian gate.
- **A40725 (ShieldRAG)** — complementary "bake safety into the retriever" defense with adversarial data synthesis; broad eval (7 datasets/5 LLMs/2 attacks), though quantitative results truncated and adaptive robustness under-tested.
- **A40913 (EmoAgent)** — strongest evidence that safety must cover the reasoning trace, not just outputs (RRSS/RVNR/RAIC); the clearest "capability ≠ permission" datapoint.
- **A40231 (MPAS)** — establishes communication topology as a multi-agent security parameter with quantified (relative) backdoor-threat reduction and released code.
- **A40269 (Editing Attack)** — the load-bearing open-weight-supply-chain threat (stealthy misinformation/bias injection, single-edit global fairness collapse); motivates provenance/attestation controls.
- **A41137 (CluCERT)** — the chunk's rigorous certified-robustness contribution (formal bounds + ABSTAIN), important precisely because it shows how narrow provable guarantees are.
(Runner-up for eval integrity: **A41098 (ArxivRoll)** — treats evaluation integrity as a first-class, gameable security property.)
