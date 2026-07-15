# Multi-keyword-match — Authoritative Synthesis

> Scope of evidence: this synthesis merges the two available partials — chunk 0 (40 papers) and chunk 1 (29
> papers), 69 AAAI-26 papers in total — into one authoritative view. This category was assembled by
> **multi-keyword overlap** ("adversarial", "robustness", "attack", "agents", "privacy", "federated",
> "detection", "contrastive", "fusion"), **not** by security relevance. Its most important structural fact,
> stated by both partials, is that it is a mixed bag: only a minority of papers model a real adversary, and a
> large fraction are benign methods surfaced by token collision. That heterogeneity is a finding, not a
> defect, and it is called out explicitly below so downstream readers do not over-weight the bucket.
>
> Weighting favors experimental quality, reproducibility, threat-model realism, and independent replication
> over paper count. Because these are 69 distinct, self-contained studies, cross-paper "agreements" are
> **convergent themes across independent teams/domains**, not independent replications of one effect size.
>
> Evidence-integrity conventions: numeric values are author-reported unless labeled "reviewer synthesis." A
> value absent from a card is written "not stated in paper"; a value the extraction pipeline cut is written
> "truncated in extracted text." Calibrated language is used throughout — findings hold "under the evaluated
> threat model" and "against the tested attacks," never "secure/proven-safe/unbreakable." Direct paper
> findings are distinguished from reviewer synthesis at every step. Where a paper has no recorded title/acronym
> in the partials, it is described by role only and never given an invented name.

---

## 1. Executive summary

This category is dominated by adjacent ML-security and outright peripheral work; genuine agent/LLM-security
content is a minority. Both partials independently sort the 69 papers into three tiers: a **small core** of
agent/LLM-security papers, a **larger adjacent tier** (adversarial-ML, extraction/inversion, poisoning,
certified robustness, RAG security, multi-agent robustness), and a **large peripheral tier** whose
"adversarial/robust/privacy" vocabulary is non-security (GAN training, domain adaptation, federated graph
learning with asserted-but-untested privacy, generic detection/segmentation).

The single most load-bearing agent-security artifact in the whole bucket is **A40189 (TAPA)** — the only
paper that instantiates the full "models propose → environments verify → gates decide → traces prove" loop
(LLM proposes symbolic programs, shadow-simulation verifies before live replacement, a degradation threshold
plus backup meta-policies decide/rollback, an Alert primitive routes to human approval, and a provenance
chain logs every adaptation). The strongest *convergent* security lessons, each supported by multiple
independent teams, are: (1) **retrieval and inter-agent channels are first-class attack surfaces, and
reasoning-based gating beats single-purpose filters** (A40462 RAG2RAG, A40725 ShieldRAG, A40231 MPAS, plus
A37023 DRIFTBENCH and A38606 CREAT on the ingestion boundary); (2) **capability to recognize risk is not safe
behavior, and safety must cover the reasoning trace, not just the final output** (A40913 EmoAgent, A40498 HEV
Sandbox) — a direct datapoint for "capability is not permission"; (3) **released models, embeddings, prompts,
and templates are extractable indexes of their private inputs** (A36972 SIDE, A37345 CLIP-FTI, A40004 Inv2A,
A39192 TabGeoFlow, A40593 DSC-Prefix); and (4) **alignment is not durable once weights or reasoning traces
are exposed** (A40269 Editing Attack, A40913).

The dominant, field-wide methodological caveat — carried by essentially every defense card in both chunks —
is that **defenses are almost never evaluated against adaptive, defense-aware attackers.** The one
demonstrated adaptive attack (A40297 HLPD, a detector repurposed offensively) is offensive, not defensive.
Consequently every defense number below is an **upper bound on real-world protection under non-adaptive
conditions.** A second field-wide caveat: the **verifier/judge/trusted-source is repeatedly the new single
point of trust and is left unhardened** (A40462, A40725, A40231, A40498, A40913, A39184). For the
Origin/Guardian stack the highest-value, lowest-regret transferable controls are: a policy gate at
retrieval/inter-agent boundaries with a trusted-source anchor and **structured, logged verdicts**; reasoning-
trace (not output-only) safety checks; model **provenance/attestation** before adopting third-party open
weights; and **abstention / route-to-human** as a safe default.

---

## 2. Scope and boundaries

**In scope (as filed under "Multi-keyword-match"):** LLM prompt/output inversion; RAG and multi-agent
security; open-weight supply-chain tampering and model-merge theft; jailbreak/affective prompt injection;
data/evidence/profile/graph poisoning; membership/attribute inference; adversarial examples (vision, point
cloud, face, CLIP, SNN, multimodal, physical); certified robustness; robust/Byzantine federated and
multi-agent aggregation; confidential computation (FHE); steganography/covert channels; watermarking/
provenance/anti-misuse; machine-text and tamper/forgery detection; benchmark-contamination integrity; plus a
large peripheral set (GAN training, domain adaptation, federated graph learning, trajectory/KG/recommendation
representation learning, forensics, segmentation, camouflage/low-light detection, capability benchmarks).

**Boundaries and caveats:**
- **The bucket is keyword-matched, not curated.** Both partials estimate roughly one third core/adjacent
  security and roughly one third-to-half peripheral. Do not treat "N papers in this category" as N
  security results.
- **"Robustness" is overloaded** across the bucket — it means adversarial robustness in some papers, but
  natural-corruption/non-IID robustness (A38163, A38124, A39573), GAN-training stability (A38544, A39342), or
  domain adaptation (A38870, A42488) in others. Conflating these is the bucket's most common reporting hazard
  (reviewer synthesis).
- **"Privacy-preserving" is asserted far more often than tested.** A cluster of federated-graph papers
  (A38124, A39546, A39573, A40118, A39812) and continual-learning/inference papers (A40924, A41230, A40590)
  invoke privacy from pure data-locality or motivation, with **no** membership-inference/gradient-inversion/DP
  evaluation.
- **No cross-paper benchmark overlap and no independent replication.** Convergent themes are cross-team
  agreement, not replicated effect sizes.
- **Truncated extracted text** limits verification for several cards (A40725, A40824, A40913, A41137, A41230,
  A41227, A42488, and various result tables in chunk 0). Where numbers were cut they are marked accordingly
  and are not independently verifiable from the cards.

---

## 3. Dominant threat models

The bucket spans the full white-box → black-box range. The recurring, security-relevant threat models are:

1. **Untrusted retrieval corpus / ingestion-boundary injection** (deployment-phase; gray/black-box). RAG and
   fact-checking pipelines treat retrieved content as attacker-writable: A40462 (RAG2RAG) and A40725
   (ShieldRAG) assume write/inject access to open knowledge bases; A37023 (DRIFTBENCH) models GenAI-driven
   claim diversity plus adversarial evidence contamination of a retrieval-augmented verifier; A38606 (CREAT)
   poisons individual interaction histories under a stealth constraint; A41436 (DIG) assumes trafficker-
   controlled source ads. Reviewer synthesis: this is the most operationally recurrent threat in the bucket.
2. **Compromised / faulty agent node inside a multi-agent system** (inference-phase). A40231 (MPAS) models a
   backdoored agent injecting misinformation at topologically critical nodes; A39344 (DeMABAR) models adaptive
   reward-corruption and Byzantine messaging (α<1/2) in decentralized bandits; A40824 (ResMAS) models the
   weaker case of *random* (non-malicious) agent failure and explicitly does **not** evaluate strategic
   compromise.
3. **Model-supply-chain / open-weight tampering & theft** (post-training; white-box). A40269 (Editing Attack)
   edits weights (ROME/FT/ICE) to inject misinformation/bias into redistributed open models; A40433
   (MergeBarrier) defends against capability theft via unauthorized model merging by a white-box adaptive
   adversary.
4. **Extraction / inversion / membership inference** (white-box or output-only). A36972 (SIDE) extracts
   training images from even *unconditional* diffusion models; A37345 (CLIP-FTI) inverts a leaked
   face-recognition template into an impersonation-capable face under black-box transfer; A40004 (Inv2A)
   recovers hidden user/system prompts from LLM *text outputs*; A39192 (TabGeoFlow) runs shadow MIA against
   tabular synthesizers; A40593 (DSC-Prefix) is a prefix-conditioned pre-training-data-detection MIA; A41230
   (FLAME) operationalizes sensitive-attribute inference (dual-use reading).
5. **Prompt-level jailbreak / affective manipulation** (inference; black-box). A40913 (EmoAgent) uses
   emotional "flattery" to override safety in transparent-reasoning multimodal models; A40498 (HEV Sandbox)
   folds an adversarial-user persona into a risk-simulation loop; A36989 (AMA) crafts benign-looking prompts
   that pass NSFW text filters yet drive identity-preserving T2I models to emit identity-bound NSFW content.
6. **Bounded input perturbation / adversarial examples** (inference; attack-agnostic-within-budget). Digital:
   A37434 (3D point clouds), A37452 (CLIP test-time), A39335 (multimodal), A39833 (SNNs), A39856 (universal
   CNN perturbations), A41137 (CluCERT, ℓ0 word substitution), A42429 (MRPD), A42176 (Lp/geometric thesis).
   Physical: A38085 (vehicle camouflage that fools detectors *and* humans).
7. **Confidentiality against an untrusted host** (honest-but-curious). A39670 (ReBoot) performs fully-encrypted
   non-interactive MLP training under CKKS; the adversary is a compute host without the secret key.
8. **Federated / distributed-training adversaries.** A39184 (LSHFed) models poisoning (label-flip, gradient
   noise), gradient-inference, and role-election takeover with up to 50% collusive clients.
9. **Evaluation / verifier gaming** (training-phase contamination, detected at eval). A41098 (ArxivRoll)
   targets benchmark contamination + biased overtraining; A41079 (TAPO, reviewer synthesis) surfaces
   length-only reward shaping as a gameable specification.
10. **Operating-environment adversary (agent defends).** A40189 (TAPA) faces evolving/adversarial environments
    (DDoS botnets, swarm disturbances) and re-synthesizes symbolic programs online.
11. **AI-enabled influence / synthetic-media misuse** (deployment; characterization-only). A41180 (Brazilian
    YouTube climate) argues LLMs can cheaply mass-produce persuasion-optimized content; A42311 (Hallucinations
    at the Firewall) frames prompt-injection-triggered hallucination in security workflows (proposal only).

**Recurring gap (reviewer synthesis):** a large sub-group *invokes* threat vocabulary but models **no adversary
at all** — the "privacy" of federated-graph papers (A38124, A39546, A39573, A40118, A39812) is pure
data-locality, asserted and never tested with an inversion/MIA attacker; the "adversarial/robust" of A38544,
A39342, A38870, A42488 refers to GAN dynamics or domain adaptation.

---

## 4. Major attack families

- **Training-data reconstruction / model inversion / membership inference:** A36972 (diffusion extraction via
  surrogate conditioning), A37345 (FR template inversion, 1-shot black-box transfer), A39192 (shadow MIA on
  tabular synthesis), A40004 (prompt inversion from outputs), A40593 (prefix-conditioned MIA), A41230
  (domain-guided latent-attribute inference).
- **RAG / corpus poisoning and backdoor triggers:** A40462 (seven attack types — targeted control, refusal DoS,
  blocker/jamming, adversarial-passage injection, grammar-trigger backdoors), A40725 (PoisonedRAG-/BadRAG-style
  strategies), A37023 (adversarial evidence contamination).
- **Multi-agent backdoor / misinformation propagation:** A40231 (injection at critical/cut-vertex nodes in
  sequential topologies), and as the poisoning family A39184.
- **Weight-level / supply-chain injection and theft:** A40269 (knowledge-editing misinformation + single-edit
  global fairness collapse), A40433 (Task-Arithmetic/TIES/DARE model-merge theft, the defended threat).
- **Jailbreak / affective / filter-evasion prompt injection:** A40913 (emotion-intensity-controlled rewriting
  overriding reasoning-stage safety), A40498 (persona-driven adversarial prompting), A36989 (attribute-
  misbinding NSFW prompts; author-reported +5.28% filter-bypass over baseline sets).
- **Data / evidence / profile / graph poisoning:** A37023 (retrieval), A38606 (stealthy profile pollution,
  adaptive RL), A39451 (graph-structure poisoning via Metattack/PGD), A39363 (label noise, framed as
  data-quality), A39184 (label-flip / gradient-noise FL poisoning).
- **Detection evasion / machine-text laundering:** A40297 (human-style paraphrase — a demonstrated adaptive
  attack against GPTZero), A40872 (multi-task revision), A41137 (ℓ0 synonym substitution, defense-side framing).
- **Adversarial examples (digital + physical):** A37434, A37452, A39335, A39833, A39856, A42429, A42176
  (digital); A38085 (physical, human-stealthy camouflage).
- **Byzantine / corruption in multi-agent learning:** A39344 (reward corruption + Byzantine messaging).
- **Covert channel / exfiltration:** A37327 (robust neural-network steganography hiding secrets in AI-generated
  images).
- **Impersonation / forgery / provenance manipulation:** A37345 (biometric impersonation), A38268 (signature
  reuse/forgery, the defended threat), A36995 (image tampering, the detected threat).
- **Evaluation gaming:** A41098 (benchmark contamination + biased overtraining), A41079 (redundancy under
  length-only reward, reviewer synthesis).

---

## 5. Major defense families

- **Reasoning/verification "expert" gating on RAG / inter-agent output** — a separate trusted judge that reasons
  about what may be said, anchored to a trusted value source, emitting structured loggable verdicts: A40462
  (Detective+Judge), A40725 (safety-aware retriever hard-filtering above a toxicity threshold).
- **Guardian-pattern runtime enforcement (the standout):** A40189 (TAPA) — propose → shadow-simulation verify →
  degradation-threshold gate → backup-meta-policy rollback → human-approval Alert → provenance chain. Reviewer
  synthesis: the only paper in the bucket instantiating the full propose/verify/gate/prove loop, decoupling LLM
  capability from live authority.
- **Structural / topology hardening for multi-agent systems** — node-wise redundancy + per-agent message vetting
  (A40231); learned resilient topology + position-aware prompt hardening (A40824, vs random failure).
- **Robust aggregation / Byzantine tolerance** — trimmed-mean per-arm filtering (A39344); Hamming-distance
  outlier filtering + reputation-weighted role election + secure-aggregation-style masking + LSH-hash gradient
  verification (A39184).
- **Certified robustness within an explicit perturbation model** — clustering-guided denoised smoothing with
  Clopper-Pearson bounds and an ABSTAIN default (A41137); Bayes-error robustness ceilings + certified
  probabilistic-robust training (A42176).
- **Robust representation / robust optimization (evasion)** — fixed simplex-ETF head for inter-class separation
  (A37434), test-time orthogonal-diverse counterattack over CLIP (A37452), vagueness-calibrated gradient
  modulation (A39335), temporal-ensemble adversarial training (A39833), information-bottleneck clean/noise
  disentanglement (A39363), acyclic-aggregation GNN blocking perturbation propagation (A39451).
- **Proactive model-IP protection** — basin-displacement weight transformation to make a model non-mergeable
  while preserving its own forward pass (A40433); targeted protective perturbation redirecting unauthorized
  diffusion fine-tuning with a traceable target-concept signature (A37507).
- **Confidential computation / crypto** — CKKS FHE end-to-end encrypted training (A39670).
- **Detection / provenance / runtime monitoring** — human-style-anchored machine-text detector (A40297),
  sentiment-stability detector (A40872), directional-sensitivity clean/adversarial discriminator (A37452),
  OOD/hallucination/malicious-prompt detectors surveyed (A41345: VLMGuard/HaloScope/TSV), oracle-free
  incoherence certification for code (A40616), benchmark-contamination scoring (A41098), LLM Graph-of-Thought
  alert reduction + attack-path narratives (A36994), unsupervised per-agent failure attribution (A36993),
  weakly-supervised tamper localization (A36995), generative signature watermark with one-time-use (A38268).
- **Verifier-gated distillation / cross-expert consistency** — accept a teacher/verifier signal only when it
  agrees with ground truth (A42429 confidence-gated contrastive loss; A41227 cross-expert consistency).
- **Automated closed-loop red-teaming** — persona-driven risk simulation with an LLM-as-judge auditor (A40498).
- **Evidence-logging / provenance as the trust primitive** — per-fact provenance to source+extractor for legal
  admissibility (A41436).

Note: several papers propose **no defense** and are offensive/measurement/proposal only — A40269, A40593,
A40913, A41180, A41230, A42311, A41345, A42176 (abstract), and the extraction/inversion attacks in chunk 0.

---

## 6. Most influential concepts

- **"Models propose, environments verify, gates decide, traces prove."** Fully instantiated only by A40189
  (TAPA); it is the reference architecture the rest of the bucket only partially approximates.
- **"Capability is not permission."** A40913 (models recognize visual risk in reasoning yet emit unsafe output;
  harmful planning hides beneath benign final answers) and A40498 (residual vulnerability under an
  all-guardrails persona) are the bucket's clearest datapoints.
- **A released model/artifact is an extractable index of its private inputs.** Convergent across A36972, A37345,
  A40004, A39192, A40593 — "no obvious conditioning/observation channel" does not remove extraction risk.
- **Topology is a security parameter, not just a performance knob** (A40231, A40824) — but resilience-to-random-
  failure and security-against-adversary can point in opposite directions.
- **Alignment is not durable once weights or reasoning traces are exposed** (A40269, A40913) — output-only
  safety assumptions are undercut.
- **A verification artifact is not a correctness oracle / certified ≠ general safety** (A41137, A42176) — provable
  guarantees are narrowly scoped to one perturbation model with a bounded accuracy cost.
- **Reasoning-based gating beats single-purpose filters, and single-granularity filters are bypassable** (A40462,
  A40725 vs. A36989/A38606/A40004's partial output-perturbation defense).
- **Evidence-logging / provenance and ABSTAIN / route-to-human** are the most transferable, low-regret controls
  in the bucket (A41436, A40616, A40462, A41137, A42311, A40189).
- **Empirical adversarial robustness correlates with representation-space geometry** (A37434 reports Pearson
  r=0.96 between robustness and feature-space disentanglement, author-reported; echoed by A37452/A39363/A39451/
  A39833).

---

## 7. Common datasets and benchmarks

There is **no shared benchmark across the bucket** — a direct consequence of keyword (not topic) assembly.
New/contributed benchmarks and their caveats:

- **DRIFTBENCH (A37023):** 16k instances, human-validated at 98.6% (κ=0.872 for real variants); built with
  specific generators (GPT-4o, FLUX.1) and live web retrieval — risking generator artifacts and
  non-determinism.
- **ArxivRoll / Rugged Scores (A41098):** benchmark-contamination scoring with a public-vs-private gap (RS_I);
  freshness guarantee is temporal, not cryptographic.
- **DBS-style self-made benchmarks:** CREAT's setup (A38606) and DAWN's single benchmark (A39812) depend on
  surrogate-transfer assumptions / limited external validity.
- **RAG-security corpora:** A40462 evaluates across 2 languages, 6 domains, 7 attacks, 7 baselines (released
  code); A40725 across 7 datasets / 5 LLMs / 2 attacks (quantitative results truncated).
- **WikiMIA (A40593):** the temporal split conflates distribution shift with membership.
- **Standard adversarial-ML datasets** appear singly (ImageNet/CIFAR-class, ModelNet/point-cloud, face-
  recognition sets, HumanEval/MBPP for A40616 — flagged for memorization confounds).
- **Off-topic / peripheral papers** report only functional benchmarks (RAG QA, event reasoning, clinical ICL,
  video continual learning, slum/camouflage/low-light detection) with **no** attack-success or robustness
  metric — A40370, A40501, A40590, A40924, A41227, A42179, A42488.

Reviewer synthesis: benchmark contributions here are valuable but **generator-coupled and single-team**; none
is independently replicated, and several are the paper's own construction, so external validity is unestablished.

---

## 8. Evaluation metrics

- **Attack Success Rate (ASR)** is the most common security metric: e.g. A40462 quotes BPI ASR 0.94→0.00 and WPI
  0.97→0.00 with ACC gains (author claim, under evaluated conditions); A40725's exact ASR/recall is truncated in
  extracted text; A40231 reports *relative* backdoor-threat reduction (7.4–26.3%; better in 94.4% of tests,
  author claim) rather than post-defense absolute ASR.
- **Certified radius / abstention rate** (A41137), **Bayes-error robustness ceiling** (A42176) — provable-floor
  metrics scoped to one perturbation model.
- **Detection AUROC / F1** (A40297 — can invert below 0.5 on revised text; A40872 — absolute F1 in the 40s–70s
  despite reported "superiority"; A41098 Rugged Scores).
- **Extraction/inversion fidelity:** TokenF1/BLEU (A40004 — surface-overlap metrics that under-measure semantic-
  but-non-verbatim recovery), reconstruction similarity (A36972, A37345), DCR ~50% + single black-box MIA as a
  privacy signal (A39192 — a metric the paper itself flags as contested).
- **Reasoning-safety divergence signals:** RRSS / RVNR / RAIC (A40913) — depend on an LLM judge of "harmful
  reasoning" whose reliability / inter-rater agreement is unreported.
- **Robustness-vs-geometry correlation:** Pearson r=0.96 (A37434, author-reported).
- **Byzantine-tolerance regret bounds** (A39344), **collusion threshold** up to 50% (A39184).
- **Off-topic functional metrics only:** accuracy, mIoU, mAP, perplexity (A40370, A40501, A40590, A40924,
  A41227, A42179, A42488) — no security metric.

Reviewer synthesis: **LLM-as-judge is repeatedly both the measurement instrument and an unhardened attack
target** (A40498, A40913, A40269, A40872, A40188), so absolute risk numbers are instrument-dependent and not
directly comparable across papers.

---

## 9. Strongest replicated findings

Read these as **convergent themes across independent teams**, not replicated effect sizes.

- **Retrieval and inter-agent channels are first-class attack surfaces, and reasoning-based gating outperforms
  single-purpose filters** — convergent across A40462 and A40725 (both report reduced ASR against tested
  poisoning while preserving utility), reinforced by A37023 and A38606 on the ingestion boundary. (Author claims,
  under evaluated conditions.)
- **Capability to recognize risk ≠ safe behavior; safety must cover the reasoning trace** — A40913 (high RVNR/RRSS)
  and A40498 (residual vulnerability under an all-guardrails persona) agree. Directly supports "capability is not
  permission."
- **A released model/embedding/prompt/template leaks its private inputs** — A36972 (even *unconditional* diffusion
  leaks via surrogate conditioning), A40004 (prompts leak from *outputs alone*), A37345 (face templates invert to
  impersonation surrogates), A39192/A40593 (synthesis/pretraining-data detectable). Convergent: absence of an
  obvious channel does not remove extraction risk.
- **Alignment is not durable once weights or reasoning traces are exposed** — A40269 (stealthy weight edits
  preserve capability) and A40913 (reasoning-trace attack) independently undercut output-only safety.
- **Single-granularity / single-stage filters are bypassable** — input-only text filters (A36989), aggregate
  distribution-shift detectors (A38606), and lightweight output perturbations (A40004 reports "limited
  protection") each fail when the adversary transforms benign-looking inputs downstream or edits at finer
  granularity.
- **Robust aggregation tolerates a bounded malicious fraction but degrades past a threshold** — A39184 (up to 50%
  collusive, author-reported) and A39344 (α<1/2 Byzantine, with regret bounds) agree.
- **Topology is a security parameter** — A40231 and A40824 agree on the mechanism even though A40824's
  perturbation is random, not adversarial.
- **Empirical adversarial robustness tracks representation-space geometry** — A37434 (r=0.96) with A37452/A39363/
  A39451/A39833 independently improving robustness by shaping/decorrelating representations (each single-team).

---

## 10. Conflicting findings

- **Redundancy: robustness vs. attack surface.** A40824 finds more agents/links → more resilience (to random
  failure); A40231 (and A40824's own reviewer note) find more nodes/links → *more* injection points and faster
  harmful-info spread. Resilience-to-random-failure and security-against-adversary can point opposite directions
  (reviewer synthesis).
- **Reasoning depth: safer or less safe?** A41345/A42176 frame reliability/robustness as improvable with more
  reasoning; A40913 finds deeper reasoning introduces an emotion-alignment blind spot. Both can hold — A40913's
  security-relevant claim is that transparent reasoning is a *new* surface.
- **Privacy metric adequacy.** A39192 relies on DCR (~50%) plus a single black-box MIA to claim empirical
  privacy while itself citing work arguing such similarity-based metrics are inadequate — an unresolved internal
  tension the paper acknowledges.
- **"Robustness" is an overloaded word** — adversarial (A37434/A37452/A39335/A39363/A39451/A39833/A39344/A38085/
  A39856/A41137/A42429/A42176) vs. natural-corruption/non-IID (A38163/A38124/A39573) vs. GAN stability (A38544/
  A39342) vs. domain adaptation (A38870/A42488). Not contradictory results, but a naming collision that invites
  misreading (reviewer synthesis).
- **"Privacy-preserving" claimed vs. tested.** A39184/A39670 argue confidentiality with mechanisms and
  (respectively) honest-majority / RLWE-hardness assumptions; A38124/A39546/A39573/A40118/A39812/A40924/A41230/
  A40590 assert privacy from data-locality or motivation with **no** attacker-side evaluation. Opposite ends of an
  evidence spectrum inside one keyword bucket.
- **Over-calibrated guarantee language.** A40433 asserts "strong security guarantee" and "ensure differential
  privacy," but the card flags that the LWE reduction bounds only one inversion path and no ε/δ DP mechanism is
  stated — treat as scoped, not general (reviewer synthesis).

---

## 11. Defense bypasses

- **Adaptive/defense-aware attackers are almost never tested — the field-wide gap.** A40462, A40725, A40872,
  A40913, A42429, A41137 (empirical portion), A40231, A37452, A37434, A39335, A39833, A39451, A38606, A39184 all
  evaluate fixed, non-adaptive suites; each card notes the untested adaptive case. Reviewer-anticipated next
  moves: poison the *trusted value source* or prompt-inject the Judge (A40462); evade the safety scorer (A40725);
  craft messages that pass the selective aggregator's reliability check (A40231); joint 2D-3D perturbations
  defeating the "3D-doesn't-transfer-to-2D" premise (A42429). A39833 explicitly reports divergent per-attack
  rankings "suggesting gradient obfuscation" and mitigates with worst-case-over-attacks reporting, but still
  lacks a defense-adaptive attack.
- **New trust roots created by defenses.** A40462 shifts trust to a "value-based" corpus; A40725 produces a
  de-aligned "unlocked" toxic generator artifact; A39184 depends on a trusted Verifier that seeds the benchmark
  bit string; A40189 trusts the LLM synthesizer + RAG provenance store + shadow-sim fidelity; A39812's
  server-broadcast prototype graphs are an unauthenticated steering channel. Each concentrates trust in a
  component whose compromise is unmodeled (reviewer synthesis).
- **Certified guarantees are narrowly scoped.** A41137 certifies only ℓ0 word substitution (not paraphrase,
  insertion/deletion, or optimization-based jailbreaks) and depends on a free semantic-stability parameter γ;
  A42176 shows a Bayes-error ceiling (<1) on certified robust accuracy.
- **Detection is partial by construction.** A40616's incoherence is a *lower bound* (zero false positives but
  misses ~1/3 of incorrect code); A40872 degrades on short text; A37327's steganography evades *pretrained*
  SRNet/SiaStegNet but not a steganalyzer retrained on its own stego (the realistic worst case).
- **Honest-but-curious ≠ malicious.** A39670 provides confidentiality but no integrity/verifiability against a
  result-tampering host, and does not address the CKKS approximate-decryption (IND-CPA^D) caveat on released
  values.
- **Filter/protection scoped to one stage.** A36989 adapts to text filters only (not output MLP/image filters);
  A37507 protects only pre-scrape images and is untested against purification/adaptive fine-tuners; A39451
  defends structure attacks, not feature attacks; A40725 scopes to toxic content and leaves manipulative-but-
  benign injection unaddressed.
- **Dual-use.** A40297's scorer strengthens evasion; A40593 strengthens both auditing and privacy attack;
  A41180's engagement recipe/dataset can aid the manipulation it warns about; A41230 is an attribute-inference
  engine in benign clothing.

---

## 12. Known benchmark limitations

- **LLM-as-judge is often both the measurement instrument and an unhardened attack target** — A40498 (cites
  JudgeDeceiver/Raina), A40913 (RRSS/RVNR/RAIC judge reliability/IRR unreported), A40269/A40872 (semantic-match /
  proprietary-model judging), A40188 (LLM-as-a-Judge reward is a reward-hacking target). Absolute risk numbers
  are instrument-dependent.
- **Single-benchmark or narrow-scope evaluation** — A40593 (only WikiMIA, temporal split confounds membership),
  A40501 (single core dataset), A40269 (7–8B open models, single-edit regime), A39344 (single-laptop synthetic,
  K≤20), A39184 (10-client topology), A40004 (single 7B model, white-box), A38870 (N=10 cohort), A40189 (single
  77.7%-uptime operating point).
- **Benchmark contamination / memorization confounds** — A40616 (HumanEval/MBPP memorization could inflate
  LLM-LLM coherence); A41098 exists to quantify this but its freshness guarantee is temporal, not cryptographic,
  and SCP construct validity beyond coherence is bounded.
- **Generator-coupled / self-made benchmarks** — DRIFTBENCH (A37023, GPT-4o/FLUX.1 + live retrieval), CREAT
  (A38606, surrogate-transfer), DAWN (A39812, single DBS).
- **Judge/metric fragility & surface-overlap under-measurement** — ABSS (A36989) and DRIFTBENCH's reasoning
  scoring (A37023) use gameable MLLM/VQA judges; A40004's TokenF1/BLEU miss semantic recovery.
- **Relative not absolute reporting** — A40231 (relative backdoor-threat reduction, no post-defense absolute
  ASR); A40872 (low absolute F1 despite reported superiority).
- **Truncated extracted text** — quantitative tables were partly unreadable for A40725, A40824, A40913
  (closed-source cells), A41137, A41230, A41227, A42488, and several chunk-0 result tables; effect sizes there
  are not independently verifiable from the cards. This is a corpus-extraction limitation, not a paper defect.
- **Off-topic papers report only functional metrics** — A40370, A40501, A40590, A40924, A41227, A42179, A42488.

---

## 13. Implementation patterns

Directly reusable for a guardian-agent / autonomy-trace stack:

- **Shadow/sandbox-before-live + rollback + provenance logging** (A40189) — the canonical propose→verify→gate→
  prove implementation.
- **Parallel/co-triggered verifier expert to bound latency** — run the safety Judge alongside the main pipeline
  (A40462), or bake safety into the retriever's shared encoder to avoid a separate-detector hop (A40725).
- **Structured, auditable verdicts as telemetry** — [removed]/[protected]/reply-risk labels (A40462); per-document
  safety score s_θ(d) (A40725); RRSS/RVNR/RAIC divergence signals (A40913); incoherence traces (A40616); certified-
  radius/abstention distribution (A41137); Rugged Scores over time (A41098). Multiple cards note these are natural
  runtime-monitoring / evidence-logging signals.
- **ABSTAIN / route-to-human as a safe default** — A41137 (binomial-inconclusive → abstain), A42311 (calibrated-
  uncertainty abstention, proposed), A40616 (flag non-zero incoherence for review), A40189 (Alert primitive).
- **Verifier gating: accept a signal only when it agrees with ground truth** — A42429 confidence-gated
  distillation; A41227 cross-expert consistency.
- **Selective / trust-weighted aggregation** — reputation election (A39184), trimmed mean (A39344), attention/
  affinity weighting (A38124/A39573/A39812) — with the caveat that the weighting itself becomes an attack surface
  whenever client-reported metrics are unauthenticated (reviewer synthesis; explicit in A39573/A39812 cards).
- **Adversarial data synthesis to cover unknown attack distributions where labels are scarce** — A40725
  (reverse-tuned toxic generator + generator-evaluator co-training).
- **Provenance linking every derived fact to source+extractor** — A41436's load-bearing trust mechanism for
  high-stakes/legal admissibility; per-agent responsibility attribution over logs (A36993); graph-grounded LLM
  incident narratives (A36994).
- **KL-regularization to a reference policy/ranker** to add a safety objective while preserving utility — A40725
  (retriever), analogous to A41079's advantage-level (not reward-level) intervention.
- **Foundation-model reuse as the operative surface** — frozen SAM as a pseudo-label teacher (A36995); frozen
  CLIP/DINOv2 as offensive or defensive backbones (A37345 offensive, A37452 defensive, A38085 attack surrogate,
  A38163 semantic prior); the forward LLM reused as an inversion decoder (A40004). Reviewer synthesis: shared
  foundation models make attacks *transfer* across systems.

---

## 14. Product design implications

- **Treat model outputs, embeddings, prompts, and templates as confidential assets with access control +
  logging**, not innocuous features — open-weights + secret system prompt on one interface is an inversion risk
  (A40004); leaked FR templates are irreversible identity exposure (A37345); released generative models are
  extractable training-data indexes (A36972, A39192).
- **Gate on reasoning traces, not just final outputs** — output-only safety checks miss hidden harmful planning
  (A40913); add reasoning-stage consistency checks (recognized-risk vs. final-action) and refusal-stability tests
  across paraphrase/emotion variants.
- **Harden the ingestion/retrieval boundary** — treat retrieved evidence, interaction history, and inter-agent
  messages as untrusted, attacker-influenceable input; add near-dup/AI-generated-evidence detection, cross-source
  corroboration, and finer-than-aggregate anomaly monitoring (A37023, A38606, A40462, A40725).
- **Privacy-gate "latent inference" as a sensitive action** — token-log-prob exposure and domain-guided attribute
  inference are attack surfaces (A40593, A41230); apply least-privilege on context, output-granularity limits, and
  audit logging of inferred attributes.
- **Do not treat data-locality as a privacy guarantee** — surface an explicit "privacy claimed vs. privacy
  tested" distinction in any federated/collaborative feature (A38124, A39546, A39573, A40118, A39812).
- **Persistent agent profiles are an unprotected asset** — A40188 concentrates LLM-inferred user data (incl.
  demographics) with no access control/minimization; add minimization + access control before shipping a
  personalized web agent.
- **Evidence-logging/provenance and abstention are the most transferable, low-regret product controls** across
  the bucket (A41436, A40616, A40462, A41137, A40189).

---

## 15. Architecture implications

- **Adopt the propose→verify→gate→prove loop** exemplified by TAPA (A40189): sandbox candidate agent actions,
  keep instant-rollback backups, route high-stakes cases to human approval, and log a tamper-relevant provenance
  chain — but **add** integrity/authenticity controls on the RAG/knowledge and synthesized code that TAPA leaves
  trusted.
- **Place a policy gate at retrieval and inter-agent boundaries** with a trusted-source anchor and structured,
  logged verdicts (A40462, A40725, A40231) — this maps cleanly onto an environment-verifies / gates-decide /
  traces-prove architecture.
- **Treat communication topology as a security parameter** — remove single points of compromise via node
  redundancy + per-agent message vetting, but account for the redundancy↔attack-surface tension (A40231, A40824).
- **Harden the verifier/judge itself** — the LLM-as-judge / selective-aggregator / trusted-value-source is
  repeatedly the new single point of trust; authenticate client/agent contributions and bound the malicious
  fraction for any aggregation step (A39184, A39344, A40498, A40462, A40231).
- **Require model provenance/attestation before adopting third-party open weights** — signed weights / hash
  pinning / known-good baselines + post-hoc factual and (broad-category) bias probing, because one edit can shift
  global fairness and merging can steal capability (A40269, A40433).
- **Pair certified robustness with empirical + adaptive testing** — certified robustness is a provable floor
  within a narrow perturbation model with an accuracy cost bounded by data uncertainty, not general safety
  (A41137, A42176).
- **Confidential computation (HE) is viable for small models** as a TEE/DP complement, but pair with integrity/
  verifiable-computation and treat approximate-decryption leakage seriously (A39670).
- **Physical-AI perception needs adversarial hardening + runtime anomaly detection, not human spot-checks**,
  because attacks can be human-stealthy (A38085) and empirical robustness is non-certified (A37434, A38163,
  A39833).

---

## 16. Launch and assurance implications

- **Every defense number here is an upper bound.** Before launch, re-test each control against an adaptive,
  defense-aware attacker — the field-wide gap flagged by essentially every card. Do not ship a control on the
  strength of non-adaptive ASR alone.
- **Contamination-adjust capability scoring for model procurement/gating** — weight rugged (public-vs-private-gap)
  scores over raw leaderboards and retire expired benchmarks (A41098).
- **Provenance/attestation is a launch gate for third-party weights** — no evaluated defense exists against
  malicious knowledge-editing (A40269); merge-prevention (A40433) prevents but does not attribute, so add
  attribution/audit separately.
- **Instrument structured verdicts, certified-radius/abstention distributions, and invalid-action / incoherence
  rates as runtime health monitors** (A40462, A40725, A41137, A40616, A41098, A40189).
- **Bias auditing must cover *unrelated* categories** — a single weight edit can shift global fairness (A40269).
- **Assurance language must stay calibrated** — treat "strong security guarantee"/"ensures DP" style claims as
  scoped-not-general absent an explicit mechanism and threat model (A40433); require production validation before
  any confidentiality/robustness guarantee is externally asserted.
- **Judge-dependent metrics are not release-grade on their own** — harden or cross-check any LLM-as-judge before
  using its scores in a go/no-go decision (A40498, A40913, A40188).

---

## 17. Open research problems

1. **Adaptive, defense-aware attackers** against every proposed defense here (A40462, A40725, A40231, A40913,
   A42429, A41137-empirical, A37452, A37434, A39335, A39833, A39451, A37327, A38606, A39184) — the dominant
   field-wide methodological gap.
2. **Hardening the verifier/judge/aggregator itself** — repeatedly the new single point of trust and left
   unhardened (A40498, A40462, A40231, A39184).
3. **No demonstrated defense against LLM prompt inversion** — A40004 states it "fails to find a really valid
   schema to overcome LMI"; perturbation defenses are largely bypassed (author-stated open problem).
4. **Deployed defenses against reasoning-trace and affective attacks** — A40913 demonstrates the vulnerability
   but evaluates no mitigation.
5. **Durable provenance/attestation for open-weight distribution** — no evaluated defense against malicious
   editing (A40269); merge-prevention (A40433) prevents but does not attribute; A38268 enforces one-time-use via
   watermark+metadata matching (not cryptographic non-repudiation) and assumes a trusted metadata store.
6. **Non-toxic, instruction-level prompt injection in retrieved content** — A40725 scopes to toxic content and
   explicitly leaves manipulative-but-benign injection unaddressed.
7. **Attribution/accountability under adversarial logs** — A36993 (multi-agent failure localization) and A36994
   (SOC attack-path tracing) are reliability tools, not yet robust to log tampering / blame-shifting / evasion of
   the LLM reasoner (reviewer synthesis, echoed in both cards).
8. **Federated agent-orchestration security** — A39812 tests only scale/heterogeneity "resilience," leaving
   update-inversion, subspace poisoning (its PR step amplifies rare directions), and server-prototype
   manipulation untested.
9. **Privacy leakage of "privacy-preserving" summary statistics / attribute inference** — unmeasured in A40924,
   A41230, A40590, and the data-locality federated-graph cluster (A38124, A39546, A39573, A40118).
10. **Persistent agent profiles as an unprotected asset** — A40188 defers privacy/minimization to future work.
11. **Empirical validation of the cybersecurity-hallucination agenda** — A42311 is framing only, zero results.

---

## 18. Recommended foundational papers

The strongest, most transferable, best-evidenced core-security papers (independent replication is absent, so
"foundational" here means highest experimental quality + threat-model realism + reusable design):

- **A40189 (TAPA)** — the only full runtime-enforcement loop (shadow-sim verify → threshold gate → backup
  rollback → human-approval Alert → provenance chain) for LLM-moderated autonomous agents in adversarial
  environments. The reference architecture for a guardian stack.
- **A40462 (RAG2RAG)** — most complete framework-level RAG-security defense (2 languages, 6 domains, 7 attacks,
  7 baselines, released code); reasoning-Judge + trusted-source-anchor pattern is directly reusable.
- **A40913 (EmoAgent)** — strongest evidence that safety must cover the reasoning trace, not just outputs; the
  clearest "capability ≠ permission" datapoint in the bucket.
- **A40269 (Editing Attack)** — the load-bearing open-weight-supply-chain threat (stealthy misinformation/bias
  injection, single-edit global fairness collapse); motivates provenance/attestation controls.
- **A40004 (Inv2A / language-model inversion)** — grounds "prompt confidentiality is an unmet security property";
  hidden prompts recoverable from outputs, with an explicit (partial) defense evaluation showing perturbations
  are largely bypassed.
- **A41137 (CluCERT)** — the bucket's rigorous certified-robustness contribution (formal bounds + ABSTAIN),
  important precisely because it shows how narrow provable guarantees are.

---

## 19. Recommended frontier papers

Higher-risk / earlier-stage but pointing where the field is going:

- **A40725 (ShieldRAG)** — "bake safety into the retriever" + adversarial data synthesis; broad eval, though
  quantitative results are truncated and adaptive robustness under-tested.
- **A40231 (MPAS)** — establishes communication topology as a multi-agent security parameter with quantified
  (relative) backdoor-threat reduction and released code.
- **A37023 (DRIFTBENCH)** — strongest RAG-security *benchmark* here (16k human-validated instances) for
  GenAI-diversity + adversarial evidence contamination against retrieval-augmented verification.
- **A38606 (CREAT)** — realistic, adaptive, stealth-constrained memory/history poisoning that evades single-
  granularity detectors; the transferable meta-lesson for agent-memory poisoning.
- **A41098 (ArxivRoll)** — treats evaluation integrity as a first-class, gameable security property (contamination-
  adjusted capability scoring).
- **A40498 (HEV Sandbox)** — automated closed-loop red-teaming with a persona-driven risk simulator and LLM-as-
  judge auditor; a reusable red-team harness pattern (whose judge itself needs hardening).
- **A36972 (SIDE)** — reframes generative-model memorization: any conditioning (explicit or surrogate) amplifies
  extraction, refuting "unconditional = safe."
- **A39184 (LSHFed)** — most concrete distributed-training security design (poisoning-robust + privacy-respecting +
  communication-efficient aggregation, up to 50% collusion) under a trusted-verifier/honest-majority assumption.
- **A40433 (MergeBarrier)** — proactive model-IP protection via non-mergeability; scope its guarantee language
  carefully.

---

## 20. Source map (paper id → one-line relevance)

**Chunk 0 (40 papers):**
- **A36972 (SIDE)** — training-data extraction from even *unconditional* diffusion models via surrogate
  conditioning; refutes "unconditional = safe." Core (extraction).
- **A36989 (AMA / ABSS metric)** — attribute-misbinding prompts pass NSFW text filters to drive identity-bound
  NSFW T2I output; input-filter evasion. Core (guardrail bypass).
- **A36993** — unsupervised per-agent failure attribution over multi-agent logs; reliability tool, not adversarial-
  log-robust. Trace-console relevance.
- **A36994** — LLM Graph-of-Thought SOC alert reduction + attack-path narratives; reliability tool. Trace-console
  relevance.
- **A36995** — weakly-supervised image-tamper localization (frozen SAM pseudo-labels); forensics, detected threat
  = tampering. Adjacent.
- **A37005** — biometric/device-identity representation via contrastive learning; identity surface. Adjacent.
- **A37023 (DRIFTBENCH)** — 16k human-validated benchmark for GenAI-diversity + adversarial evidence contamination
  of retrieval-augmented fact-checking. Core (RAG security).
- **A37327** — robust neural-network steganography hiding secrets in AI-generated images; evades pretrained (not
  retrained) steganalyzers. Adjacent (covert channel).
- **A37345 (CLIP-FTI)** — inverts a leaked face-recognition template into an impersonation-capable face (1-shot
  black-box transfer). Core (inversion/identity).
- **A37434** — 3D point-cloud adversarial robustness via a fixed simplex-ETF head; reports r=0.96 robustness↔
  feature-disentanglement. Adjacent (evasion defense).
- **A37452** — test-time orthogonal-diverse counterattack over CLIP + directional-sensitivity detector. Adjacent
  (evasion defense).
- **A37507** — targeted protective perturbation redirecting unauthorized diffusion fine-tuning, with a traceable
  target-concept signature. Adjacent (anti-misuse).
- **A38085** — physical vehicle camouflage fooling detectors *and* humans (human-stealthy). Adjacent (physical
  adversarial).
- **A38124** — federated graph learning; "privacy" = data-locality, asserted and untested with an attacker.
  Peripheral.
- **A38163** — semantic-prior robustness (natural-corruption sense, foundation-model semantic prior). Peripheral/
  adjacent.
- **A38268** — generative signature watermark binding metadata + one-time-use; defended threat = signature reuse/
  forgery; not cryptographic non-repudiation. Adjacent (provenance).
- **A38470** — network-science robustness with "dual agents" = RL policies; "agents" is non-security. Peripheral.
- **A38526** — trajectory/representation learning; non-security. Peripheral.
- **A38544** — GAN training; "adversarial" = GAN dynamics. Peripheral.
- **A38606 (CREAT)** — stealthy, adaptive interaction-history poisoning to promote a target item while evading
  distribution-shift detectors. Core (memory poisoning).
- **A38653** — KG/recommendation representation learning; non-security. Peripheral.
- **A38870** — domain adaptation; "adversarial/robust" = domain-adversarial. Peripheral.
- **A39184 (LSHFed)** — poisoning-robust + privacy-respecting + comms-efficient federated aggregation, up to 50%
  collusion, under a trusted-verifier assumption. Adjacent (FL security).
- **A39192 (TabGeoFlow)** — black-box shadow membership inference against tabular synthesizers; DCR/MIA privacy
  signal flagged as contested. Adjacent (MIA).
- **A39335** — multimodal adversarial robustness via vagueness-calibrated gradient modulation. Adjacent (evasion
  defense).
- **A39342** — GAN training; "adversarial" = GAN dynamics. Peripheral.
- **A39344 (DeMABAR)** — decentralized bandits robust to adaptive reward-corruption + Byzantine messaging (α<1/2),
  trimmed-mean per-arm filtering, regret bounds. Adjacent (Byzantine).
- **A39363** — adversarial robustness via information-bottleneck clean/noise disentanglement (label-noise framing).
  Adjacent (evasion defense).
- **A39451** — acyclic-aggregation GNN resisting graph-structure poisoning (Metattack/PGD); defends structure, not
  features. Adjacent (graph poisoning).
- **A39546** — federated graph learning; privacy asserted from locality, untested. Peripheral.
- **A39573** — federated graph learning with affinity-weighted aggregation; privacy asserted, weighting is an
  unauthenticated surface. Peripheral.
- **A39617** — federated graph learning; non-adversarial. Peripheral.
- **A39670 (ReBoot)** — CKKS FHE end-to-end encrypted MLP training vs. an honest-but-curious host; no integrity,
  IND-CPA^D caveat unaddressed. Adjacent (confidential compute).
- **A39812 (DAWN)** — federated LLM multi-agent workflow synthesis; tests scale/heterogeneity "resilience" only;
  server-prototype channel unauthenticated. Core-adjacent (agent orchestration).
- **A39833** — SNN adversarial robustness via temporal-ensemble adversarial training; reports gradient-obfuscation
  signal, worst-case-over-attacks reporting, no adaptive attack. Adjacent (evasion defense).
- **A39856** — universal adversarial perturbations on CNNs. Adjacent (evasion).
- **A40004 (Inv2A)** — recovers hidden user/system prompts from LLM *text outputs*; explicit partial defense eval
  shows perturbations largely bypassed. Core (prompt inversion).
- **A40118** — federated graph learning; privacy asserted from locality, untested. Peripheral.
- **A40188** — personalized web agent; concentrates LLM-inferred user data (incl. demographics) with no access
  control/minimization; attack-surface catalog. Core-adjacent (agent privacy).
- **A40189 (TAPA)** — LLM-guided programmatic-agent adaptation with shadow-sim verify → threshold gate → backup
  rollback → human-approval Alert → provenance chain. Core (runtime enforcement); the bucket's standout.

**Chunk 1 (29 papers):**
- **A40231 (MPAS)** — multi-agent backdoor at topologically critical nodes + node-redundancy/message-vetting
  defense; topology as a security parameter (released code). Core (multi-agent security).
- **A40269 (Editing Attack)** — knowledge-editing weight tampering injecting misinformation/bias; single-edit
  global fairness collapse; no evaluated defense. Core (supply-chain).
- **A40297 (HLPD)** — human-style-anchored machine-text detector, repurposed as a *demonstrated adaptive attack*
  against GPTZero; baseline likelihood detectors can invert (AUROC<0.5). Adjacent (detection, dual-use).
- **A40370** — RAG quality method; no adversary/security threat model. Peripheral.
- **A40433 (MergeBarrier)** — basin-displacement weight transform to block unauthorized model merging; guarantee
  language scoped-not-general. Core-adjacent (model-IP).
- **A40462 (RAG2RAG)** — reasoning Detective+Judge gate on RAG output anchored to a trusted source; most complete
  RAG-security framework here (released code). Core (RAG security).
- **A40498 (HEV Sandbox)** — automated closed-loop red-teaming with adversarial-user persona + LLM-as-judge
  auditor; residual vulnerability under all-guardrails persona. Core (red-teaming).
- **A40501** — event-reasoning capability; non-security. Peripheral.
- **A40590** — clinical in-context learning; "privacy" invoked but requires sensitive data, no MIA/DP eval.
  Peripheral.
- **A40593 (DSC-Prefix)** — prefix-conditioned log-likelihood membership-inference / pretraining-data detection
  (WikiMIA only); dual-use. Adjacent (MIA).
- **A40616** — oracle-free incoherence error-certification for LLM code; lower bound (misses ~1/3 incorrect code),
  memorization confounds. Adjacent (verification).
- **A40725 (ShieldRAG)** — safety-aware retriever hard-filtering above a toxicity threshold + adversarial data
  synthesis; scopes to toxic content only; results truncated. Core (RAG security).
- **A40824 (ResMAS)** — resilient multi-agent topology + position-aware prompt hardening vs. *random* (not
  strategic) agent failure. Core-adjacent (multi-agent robustness).
- **A40872** — sentiment-stability machine-text detector; low absolute F1, degrades on short text. Adjacent
  (detection).
- **A40913 (EmoAgent)** — affective jailbreak overriding reasoning-stage safety in transparent-reasoning
  multimodal models (RRSS/RVNR/RAIC); "capability ≠ permission" evidence. Core (jailbreak).
- **A40924** — video/exemplar-free continual learning; retains summary statistics, privacy unmeasured. Peripheral.
- **A41079 (TAPO)** — RL length-only reward shaping surfaced as a gameable specification (reward-hacking vector,
  reviewer synthesis); advantage-level intervention. Adjacent (reward integrity).
- **A41098 (ArxivRoll)** — benchmark-contamination + biased-overtraining scoring (Rugged Scores); temporal-not-
  cryptographic freshness. Adjacent (eval integrity).
- **A41137 (CluCERT)** — certified ℓ0 word-substitution robustness with Clopper-Pearson bounds + ABSTAIN; narrow
  perturbation model. Adjacent (certified robustness).
- **A41180** — Brazilian-YouTube climate study; argues LLMs can mass-produce persuasion-optimized content;
  characterization + dual-use dataset. Adjacent (influence).
- **A41227** — slum segmentation with cross-expert consistency filter; non-security, but the consistency-gating
  pattern is reusable. Peripheral.
- **A41230 (FLAME)** — domain-guided latent sensitive-attribute inference; benign-framed but an attribute-inference
  engine (dual-use). Adjacent (privacy attack).
- **A41345** — survey of OOD/hallucination/malicious-prompt detectors (VLMGuard/HaloScope/TSV); abstract, no new
  results. Adjacent (detection survey).
- **A41436 (DIG)** — per-fact provenance to source+extractor for courtroom admissibility; trafficker-controlled
  source ads threat. Adjacent (provenance).
- **A42176** — thesis on certified/probabilistic robustness (Lp/geometric); Bayes-error robustness ceiling.
  Adjacent (certified robustness).
- **A42179** — camouflage detection; "adversarial" = environmental difficulty, non-security. Peripheral.
- **A42311 (Hallucinations at the Firewall)** — frames prompt-injection-triggered hallucination in security
  workflows + calibrated-uncertainty abstention; proposal only, zero results. Core-adjacent (agenda).
- **A42429 (MRPD)** — Lp/geometric adversarial examples in vision/point-cloud/face with confidence-gated
  contrastive distillation; non-adaptive eval. Adjacent (evasion defense).
- **A42488** — low-light detection with domain-adversarial training; "adversarial" = domain-adversarial,
  non-security. Peripheral.
