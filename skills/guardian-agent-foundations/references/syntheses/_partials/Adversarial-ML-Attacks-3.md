# Adversarial-ML-Attacks — Partial Synthesis (chunk 3 of category, 32 papers)

Scope: paper ids A40881, A40891, A40893, A40894, A40895, A40897, A40898, A40902,
A40904, A40905, A40908, A40912, A40915, A40964, A41080, A41099, A41108, A41121,
A41122, A41141, A41144, A41146, A41164, A41170, A41213, A41250, A41404, A42145,
A42217, A42292, A42327, A42439. All are AAAI-26 papers (mix of full papers,
student abstracts, one doctoral-consortium abstract, and one abstract reprint).

Evidence-integrity note: every claim below traces to a specific paper's card;
numbers are the authors' reported values under their evaluated threat models, not
independently verified. "Reviewer synthesis" marks cross-paper judgments that no
single paper makes. Two papers (A40964, A41213) are filed under this category but
are **not** ML-security papers (see Off-topic below); one (A41404) is an abstract
reprint with no methods/metrics.

## Dominant threat models

Several distinct threat clusters recur; the chunk is roughly half attack papers
and half defense papers.

- **Training-time / supply-chain backdoors and poisoning** (the largest cluster):
  a data-poisoning or outsourced-training adversary implants a hidden
  trigger→behavior mapping into a model a victim later downloads and deploys.
  Knowledge is usually gray/black on the final model; activation is at inference.
  Papers: A40891 (MLLM visual backdoor via Fine-Tuning-as-a-Service), A40894
  (All-to-X image backdoor), A40897 (generative-LLM backdoor), A40902 (NLP
  backdoor), A40904 (vision-DNN backdoor), A41080 (NLP/LLM backdoor), A41121
  (open-vocabulary-detector backdoor via prompt tuning), A40908 (split-federated
  poisoning), A42327 (vertical-federated Byzantine poisoning).
- **Agent / MCP tool-layer attacks** (core agent-security): the agent trusts
  third-party tool metadata as ground-truth capability specification. A40895
  (MCPTox — tool-description poisoning that rides a *legitimate* high-privilege
  tool: a confused-deputy pattern), A40898 (MPMA — persuasive metadata biases
  tool *selection* for economic gain). Both are metadata-only, no execution of
  the poisoned tool.
- **LLM/VLM safeguard-pipeline bypass** (core): defense-in-depth stacks
  (input+output classifiers, alignment, system prompt) are attacked as a *whole*.
  A41108 (STACK, staged black-box semi-separable bypass), A41144 (MFA, cross-model
  reward-hacking + moderator-evasion + vision-encoder attack). A41122 (ASE) is the
  in-model inference-time defense these attacks would have to overcome; A41099
  (ChameleonAttack) is a semantics-preserving text attack on financial LLMs/agents.
- **Physical / multimodal perception attacks** (core-to-adjacent): A40881
  (Phantom Menace — laser/EMI/ultrasound sensor injection into VLA robots),
  A42439 (PhysPatch — physically-realizable transferable patch steering
  MLLM-based autonomous-driving perception), A41121 (detector backdoor motivated
  by physical stickers), A41164 (SEAR — AR + multimodal-LLM social engineering).
- **Model-IP / provenance and privacy** (adjacent): watermarking/ownership under
  extraction+removal (A40905 CFW, A40915 NeuralMark, A41146 3DGS watermark
  removal); membership inference (A40912 IMIA); anti-personalization "cloaks" for
  faces/IP (A41170 critique, A41250 VCPro, A41404 face-recognition defense).
- **Foundational robustness theory / architecture** (adjacent): A42217 (feature
  compression as root cause of fragility), A42292 (evolutionary NAS defense),
  A42145 (RL falsification of AV control loops).

## Major attack families

- **Backdoor / trigger insertion**, evolving from fixed-word/patch triggers to
  syntactic, style, dynamic/implicit, multi-target, and multi-modal triggers.
  A40894 shows *distributed* (All-to-X) target mappings that mimic natural error;
  A41121 shows backdoors injected purely via **parameter-efficient prompt tuning**
  (no base-weight retraining). A41080/A40897 note trigger diversification is the
  central detection challenge.
- **Corpus / RAG poisoning**: A40893 (Joint-GCG) jointly optimizes retriever+
  generator gradients (Cross-Vocabulary Projection, Gradient-Tokenization
  Alignment, Adaptive Weighted Fusion) so a single stealthy document both survives
  retrieval and overrides generation.
- **Tool-metadata attacks (MCP)**: A40895 (Trigger Condition + Malicious Action +
  Plausible Justification → hijack a legitimate tool), A40898 (advertising-style
  rewrites + genetic-algorithm stealth optimization to win tool selection).
- **Staged / multi-facet jailbreaks against full stacks**: A41108 finds *universal*
  per-component jailbreaks and chains them (incl. inducing the model to repeat an
  output-classifier jailbreak string); A41144 combines reward-hacking (dual-answer
  meta-task), an optimized "adversarial signature" for moderators, and a
  vision-encoder pixel-space system-prompt injection that transfers across models.
- **Optimization-based / semantics-preserving text attacks**: GCG-lineage suffix
  optimization recurs (A41099 relaxes discrete token search to a continuous
  simplex + T5 "translation" for fluency; shared lineage with A41108/A41144).
- **Physical-signal and physical-patch attacks**: A40881 (8 sensor attacks: laser
  blinding, light projection, EM color strip, ultrasound blur, voice DoS/spoofing);
  A42439 (~1%-area patch, joint location+shape+content optimization, EoT, CLIP
  surrogate ensemble transfer).
- **Membership inference / privacy**: A40912 uses the *number of iterations* to
  craft an adversarial example as a universal membership signal (works even on
  hard-label-only APIs).
- **Watermark/provenance removal & model extraction**: A40905 (extraction then a
  purpose-built remover WRK), A41146 (black-box detector-free 3DGS watermark
  removal via convolutional-feature-variance flattening + evolutionary pruning),
  A40915's threat set (forging + overwriting + fine-tuning + pruning).
- **Purification of protective perturbations**: A41170 treats simple filtering /
  diffusion purification (DiffPure, GrIDPure) as the attack that strips
  anti-personalization "cloaks."
- **Federated poisoning**: A40908 (five vectors — label/data/smashed/weight/
  multi-vector in SFL), A42327 (in-distribution embedding cluster-swap in VFL that
  evades numeric-anomaly detectors).

## Major defense families

- **Backdoor detection at inference (black-box)**: A40891 (Trap-on-Text:
  text-perturbation Semantic-Consistency + Confidence-Drift-Gap), A40897
  (ConfGuard: token-confidence "sequence-lock" run detector, top-1 prob only,
  stop-generation on trip).
- **Backdoor removal / model purification (pre-deployment)**: A40902 (BeDKD:
  directional-mapping module + adversarial knowledge distillation, small clean+
  poisoned data), A40904 (CL-Guard: LRP neuron attribution + dual-network sparse
  training), A41080 (attention-head-similarity detection + head-wise alignment,
  trigger-agnostic, no clean twin model needed).
- **Distributed-training robustness with recovery**: A40908 (HealSplit:
  topology-aware detection + GAN recovery + adversarial multi-teacher distillation
  for split-federated learning).
- **Inference-time model-level defense**: A41122 (ASE: CoT self-generated
  adversarial-scenario reasoning before answering, threat-agnostic, low
  over-refusal). A41108 also contributes a few-shot-prompted input/output
  classifier baseline that beats ShieldGemma on non-adaptive attacks.
- **Model-IP / ownership**: A40905 (CFW: synthetic OOD watermark class + measurable
  Representation Entanglement, resilient to extraction+removal), A40915 (NeuralMark:
  SHAKE-256 hash-as-filter with a forging-probability bound < 1/2^128 at n=256).
- **Architecture / robustness by design**: A42292 (ResNet-GA: genetic search over
  residual-block channel widths with adversarial examples in fitness).
- **Protective adversarial perturbation ("cloaks")**: A41250 (VCPro:
  mask-localized, frequency-domain-imperceptible perturbation) and the class A41170
  critiques; A41404 (per-sample "artificial immune system" purification for face
  recognition — abstract reprint only, unverifiable here).

## Strongest replicated findings (reviewer synthesis across cards)

- **Metadata and descriptions are an injection surface as dangerous as content/
  output.** A40895 and A40898 independently show that trusting tool names/
  descriptions lets an attacker hijack legitimate tools (A40895, peak ASR 72.8%
  on o1-mini) or bias tool selection (A40898, DPMA 100% ASR in most settings).
  A40895 further shows porting indirect-prompt-injection payloads (which lack a
  Trigger Condition) to the description vector yields near-0% ASR — tool poisoning
  is a *distinct* vector.
- **Evaluating stacked defenses per-component overstates security; whole-pipeline
  adaptive attacks defeat them.** A41108 (0% baseline ASR but 71% black-box / 33%
  transfer STACK ASR on the same few-shot pipeline) and A41144 (58.5% overall /
  52.8% commercial ASR, 72.92% with all three facets) both make this point, and
  both exploit the same "model repeats an attacker-chosen string past the output
  classifier" channel — an independently replicated concrete weakness.
- **More capable / better-instruction-following models are often *more*
  susceptible** to metadata/instruction-following attacks (A40895 explicit; A41144
  notes failures cluster on models with *weak* instruction-following).
- **Backdoor activation leaves intrinsic behavioral/representational signatures**
  usable for detection: modality-attention shift + confidence stability (A40891),
  token-confidence sequence-lock (A40897), abnormal attention-head similarity
  (A41080, 99th-pct cosine gap e.g. BadNets 0.9921 vs 0.9149). These are
  convergent evidence that overfit backdoors are detectable — but all are
  evadable heuristics (see bypasses).
- **Shared vision backbones create systemic ("monoculture") transfer risk.** A41144
  (one adversarial image transfers, avg 59.58% image ASR) and A42439 (CLIP-
  surrogate-ensemble transfer to 12 commercial/reasoning MLLMs) independently show
  perturbations crafted on shared encoders transfer to black-box deployed models.
- **Removable in-artifact protection (watermarks, protective perturbations) is not
  a security guarantee.** A41146 (3DGS watermark removal), A41170 (all four
  anti-DreamBooth defenses fail after purification), and A40905's WRK (>=88.79% WSR
  reduction against prior watermarks) all show that capability to render/modify the
  artifact implies capability to strip the mark.

## Conflicting / tension findings

- **"Robust against SOTA defenses" almost always means non-adaptive defenses.**
  A40894 claims A2X backdoors survive six SOTA defenses, but explicitly against
  their *standard* (non-adaptive) form; A42327 evades three classical VFL
  detectors but not the cross-view-consistency defense it advocates (unbuilt).
  Contrast with A40905/A40915, which *do* build purpose-built adaptive
  removers/forgers and evaluate against them — a more demanding bar. This is a
  methodological split, not a factual contradiction, but it makes cross-paper
  "robustness" claims non-comparable.
- **Protective perturbations: usability vs durability.** A41250 (VCPro) advances
  imperceptibility by concentrating perturbation in high-frequency/masked regions;
  A41170 shows high-frequency-concentrated perturbations are exactly what low-pass
  purification removes. VCPro is explicitly *not* tested against purification, so
  its real-world durability is contested by its companion paper.
- **Over-manipulation backfire (A40898).** Counter to the "more persuasion = more
  selection" premise, in a malicious-majority ecosystem several LLMs revert to a
  plain benign tool — an internal negative result the authors flag as speculative.
- **Detection thresholds vs availability.** A40897's stop-generation and threshold
  L are dataset-dependent (L≈9 CQA vs ≈14 UC/SIQA) and some cells show non-trivial
  FPR (up to ~21.95% Shakespeare-style) — effectiveness and false-refusal are in
  tension, unlike the "negligible FPR" headline.

## Defense bypasses (explicitly demonstrated or clearly implied)

- **Output-classifier repetition channel**: both A41108 and A41144 defeat output
  moderators by making the model emit an attacker-chosen jailbreak/"signature"
  string; both recommend constraining verbatim echo / classifying on hidden
  context, untested here.
- **Purification strips protective cloaks**: A41170 shows bilateral+guided
  filtering and DiffPure/GrIDPure defeat Anti-DreamBooth, HF-ADB, SimAC, DisDiff;
  by extension threatens A41250 (VCPro) and the general A41404 class.
- **Adaptive removers beat prior watermarks**: A40905's WRK reduces prior black-box
  watermarks' WSR by >=88.79%; A41146 removes 3DGS marks without ever seeing the
  detector.
- **In-distribution poisoning evades numeric-anomaly detectors**: A42327's
  embedding cluster-swap keeps detection <=1.5% under gradient-norm clipping and
  AE-reconstruction detection while collapsing MNIST accuracy to ~42-46%.
- **Reviewer-flagged, not-yet-evaluated adaptive bypasses**: nearly every detection
  defense (A40891 TSC/CDG, A40897 sequence-lock, A41080 attention-similarity,
  A40908 topology score, A40902/A40904 output-divergence assumption) rests on an
  evadable signature that a defense-aware attacker could suppress; none of these
  papers evaluate such an attacker (recurring gap).

## Benchmark / evaluation limitations (recurring)

- **Non-adaptive attack suites dominate**: A40894, A40897, A40902, A40904, A41080,
  A42292 evaluate against standard attacks with no defense-aware adaptive
  adversary; A40895/A40898 use deliberately generic (non-optimized) payloads.
- **LLM-as-judge scoring**: A41108 (StrongREJECT classifier), A41144, A42439
  (GPT-4o judge), A40898 (LLM-as-judge stealth) all depend on an LLM judge whose
  calibration bounds reliability; A42439 reports no inter-judge/human agreement.
- **Truncated results in extracted text**: many cards flag that headline tables
  were partly truncated (A40881, A40894, A40904, A40908, A41080, A41121, A41146,
  A41170, A41213, A41250) — magnitudes are author-reported, not fully transcribed.
- **Narrow scope / small models**: several backdoor and privacy results are
  vision-classifier-only (A40894, A40904, A40912) or <=7-8B LLM (A40897, A41080);
  student abstracts use toy datasets (A42327 MNIST/FashionMNIST/UCI-HAR; A42292
  CIFAR-10/Mini-ImageNet; A42217 synthetic).
- **Physical realizability asserted, measured digitally**: A42439 ("physically
  realizable" but quantitatively evaluated on digitally-patched nuScenes frames);
  A41121 (physical-sticker motivation, digital eval); A40881 does validate on a
  real Franka arm but on limited tasks.
- **Single-run / no variance**: A41122 (ASE, explicitly no repeated runs due to API
  cost), A42292, A42327 report no CIs/seeds.
- **No defense evaluated in attack papers**: A40893, A40895, A40898, A40912, A41099,
  A41121, A41144, A41146, A41164, A42327 propose no defense, so residual risk after
  mitigation is unknown.

## Recurring implementation patterns

- **Perturb-and-compare / behavioral-signature detection** for backdoors that needs
  only I/O or top-1 probabilities (A40891, A40897) — deployable client-side against
  untrusted providers.
- **Attribution-guided surgical purification** (neuron- or head-level) rather than
  layer reinitialization (A40904 LRP neurons; A41080 attention heads), using a
  small trusted clean set as a security asset (A40902, A40904, A41080).
- **GCG / multi-token gradient optimization lineage** shared across A40893, A41099,
  A41108, A41144 — universal suffix/signature optimization is the common attack
  primitive; A41144 reports 3-5x speedup over GCG, A41099 relaxes to continuous
  space.
- **Ensemble-surrogate transfer** to reach black-box/commercial targets: CLIP
  encoder ensembles (A41144, A42439), open-source RAG components (A40893),
  open-weight safeguards as proxies (A41108).
- **Semantic-region reasoning via a foundation model** to place/optimize attacks:
  GPT-4o for MCP-payload/description generation (A40895, A40898), patch placement
  (A42439), CLIP+role-based RAG for victim profiling (A41164).
- **Detect-then-repair (self-healing) rather than reject-only** in training-integrity
  defenses (A40908 GAN recovery; A40902 punish-distillation).
- **Cryptographic entanglement of mark and parameters** for provenance (A40915
  hash-as-filter; A40905 representation-entanglement metric).

## Product / architecture implications (for a Guardian-Agent / autonomy-console stack)

- **Bind actions to verified user intent, not to tool identity.** A40895's
  confused-deputy result (poisoned tool never executes; a legitimate high-privilege
  tool carries out the malicious action) means permission models keyed to "which
  tool ran" are bypassable. Add a pre-execution gate that verifies each planned
  tool call against the original request, sanitizes/normalizes tool descriptions at
  registration, sandboxes unverified servers, and requires human approval for
  credential-reading actions (e.g., SSH keys) regardless of requester.
- **Treat tool metadata and inbound text/images as untrusted input.** Tool
  descriptions (A40895/A40898), RAG corpora (A40893), financial news/social text
  (A41099/A41164), and camera images (A42439/A40881) are all attacker-influenceable
  channels; a fluent/expert/persuasive surface is not evidence of benignity.
- **Do not rely on model-level safety alignment or a single guard family.** A40895
  (<3% refusal even on Claude-3.7-Sonnet), A41108 (shared base between guard and
  guarded model is a weakness), A41144 (cross-moderator transfer) all argue for
  independent, non-monoculture, whole-pipeline enforcement; break the verbatim-echo
  channel that lets a model smuggle strings past output classifiers.
- **Cross-sensor / cross-source corroboration for perception-driven actions.**
  A42439 and A40881 argue a single MLLM/VLA perception output must not authorize
  safety-critical actuation; corroborate against map/LiDAR/redundant detectors and
  keep a hard safety envelope with human-in-the-loop.
- **Provenance must be cryptographic and out-of-band, not an in-artifact mark.**
  A41146/A41170/A40905 show removable marks fail; pair artifact watermarking with
  signed manifests / registry attestation and access control.
- **Runtime signals worth logging**: token-confidence-run events (A40897),
  attention-head-similarity stats (A41080), per-component block decisions +
  "repeat this string"/universal-suffix patterns (A41108/A41144), appended
  moderator-evasion signatures, tool-selection decisions with the descriptions that
  drove them (A40898), cross-view embedding-alignment stability (A42327), and the
  image regions that drove a perception output (A42439). These are candidate
  telemetry for the autonomy-trace console.
- **Supply-chain sanitization gate before deployment**: attention-similarity /
  neuron-attribution screening (A41080, A40904), model re-distillation on a small
  clean set (A40902), and adapter/prompt-tuning provenance checks (A41121) before
  promoting third-party checkpoints/adapters.

## Open problems

- **Adaptive, defense-aware attackers are almost universally untested** against the
  detection/purification defenses here (A40891, A40897, A40902, A40904, A41080,
  A40908, A42292) — the single largest evidence gap.
- **Purification-robust, imperceptible protective perturbations** remain unsolved
  (A41170 open challenge; A41250 untested against purification).
- **Whole-pipeline mitigation of staged/repetition-channel bypasses** (A41108,
  A41144 both recommend but do not build/validate fixes).
- **VFL/SFL defenses that verify semantic cross-view consistency** rather than
  numeric anomalies (A42327 advocates, does not build; A40908 assumes topological
  separability an adaptive attacker could target).
- **Runtime detection/containment of physical attacks** on VLA/AD stacks (A40881
  provides only training-time hardening; A42439/A42145 provide no deployed
  mitigation).
- **Standardized, adaptive benchmarks**: multi-target/All-to-All backdoors (A40894),
  tool-poisoning with automated adaptive payloads (A40895 future work), CAPTCHA
  attacker↔defender co-evolution (A41141), counter-example quality metrics for AV
  falsification (A42145).
- **Reward designs that separate helpfulness and safety** to close the reward-
  hacking jailbreak pathway (A41144 structural recommendation).
- **Dual-use exposure** of released offensive toolkits/datasets (A41164 AR social
  engineering; A40895/A40898 MCP attacks) — a governance open problem.

## Most load-bearing papers (by security relevance x evidence strength)

1. **A40895 (MCPTox)** — strongest, most directly agent-relevant: first large-scale
   (45 live MCP servers, 353 tools, 1348 cases, 20 agents) evidence that tool-
   description poisoning is a distinct confused-deputy vector defeating permission
   models and model-level alignment. Anchors the "capability is not permission /
   verify intent" architecture argument.
2. **A41108 (STACK)** — rigorous, explicitly-taxonomized threat model showing
   defense-in-depth pipelines that look robust (0% baseline) collapse under staged
   adaptive attacks (71% black-box, 33% transfer). Released code; defines the
   evaluation standard for guard stacks.
3. **A41144 (MFA)** — broad (17 open+commercial VLMs, real moderators) demonstration
   that alignment + system prompt + input/output moderation are *jointly*
   bypassable, plus a reward-hacking mechanistic account and the monoculture-
   transfer finding. Independently replicates A41108's output-repetition channel.
4. **A42439 (PhysPatch)** — strongest physical-perception evidence: transferable
   ~1%-area patch steers 12 commercial/reasoning MLLM-AD stacks (ASR ~10-40%),
   grounding the cross-sensor-verification and untrusted-perception-channel
   requirements for physical-AI agents.
5. **A41170 (Fragile by Design)** — load-bearing *cautionary* result: an entire
   class of protective-perturbation privacy defenses fails under trivial
   purification, forcing purification-aware evaluation and cryptographic-provenance-
   over-cloak design. Directly critiques A41250 and the A41404 class.
6. **A40905 (CFW/WRK)** — model-IP anchor: demonstrates the *sequential* (extract-
   then-remove) threat, that prior removal evals gave a "false sense of security,"
   and sets the bar of building a purpose-built adaptive remover — the methodological
   contrast that exposes the non-adaptive-evaluation weakness pervading the chunk.

## Off-topic / low-evidence flags

- **A40964 (Dominance Pruning in Adversarial FOND Planning)** — automated-planning /
  heuristic-search paper; "adversarial" = worst-case game-theoretic non-determinism,
  not ML-security. Strong in its own field, but tagged insufficient here (no
  attacker-vs-model threat model). Do not cite as agent-security evidence.
- **A41213 (ALERT)** — clinical-NLP depression detection using adversarial *training*
  as a regularizer; no attacker, attack surface, or security defense. Category label
  is a keyword-filing artifact.
- **A41404 (Artificial Immune System face recognition)** — AAAI-26 *abstract reprint*
  of a 2024 IJCV article; no methods/datasets/metrics in the corpus text, so
  SOTA-surpassing claims are unverifiable — evidence_strength insufficient.
- **A42145 (RL falsifying AV)** — doctoral-consortium in-progress abstract, no
  quantitative results; preliminary, adjacent.
