# Defense-Mitigation — Authoritative Synthesis

> Scope of evidence: this synthesis merges the single available partial (chunk 0, 9 papers) with the nine
> underlying research cards (A37002, A37924, A39732, A39818, A40129, A40432, A41134, A41145, A42364), all
> AAAI-26 papers. There is no independent replication *across* these papers — each is a distinct, self-contained
> study — so cross-paper agreements below are **convergent themes across independent domains**, not independent
> replications of one result. Weighting favors experimental quality, reproducibility, threat-model realism, and
> agent-security relevance over paper count.
>
> Evidence-integrity conventions: numeric values are author-reported unless labeled "reviewer synthesis." Where a
> card records that a value was truncated from the extracted text, it is written "not stated in paper" (or "not
> visible in extracted text"). Calibrated language is used throughout — findings hold "under the evaluated threat
> model" and "against the tested attacks," never "secure/proven-safe." Direct paper findings are distinguished
> from reviewer synthesis.

---

## 1. Executive summary

This category is heterogeneous. Of nine papers, three are core LLM/agent-system security
(A40432 RAGFort — RAG knowledge-base extraction defense; A41134 IMBIA — multi-agent software-development
security; A37924 GhostCert — red-teaming of certified defenses), one is white-box LLM training-data
extraction plus a model-editing defense (A41145 CoSPED), one is multimodal federated-GraphLLM robustness
(A39732 STRUM/GTAE), one is proactive audio anti-cloning (A37002 VoiceCloak), and three are peripheral to
agent security (A40129 PDFK, a non-adversarial continual-learning stability method; A39818 TowerMind, a
capability/reliability benchmark; A42364 GNN-AID, a GNN tooling framework with no security evaluation).

The strongest, most transferable finding — convergent across independent domains — is that **single-point
defenses are insufficient; layered / multi-point defense is required** (A40432, A39732, A41134). The second
load-bearing insight is that **a verification artifact is not a correctness oracle**: A37924 demonstrates
(under a white-box, known-noise-level threat model) that a large randomized-smoothing certificate can be
spoofed with imperceptible, semantics-preserving perturbations. The most important methodological caveat,
carried explicitly by every security card, is that **these defenses are near-universally NOT evaluated
against adaptive, defense-aware attackers** — so all defense numbers below are upper bounds on real-world
protection.

Only three papers (A40432, A37924, A41145 partially) offer strong-to-moderate evidence with released code,
visible numeric results, and realistic threat models; the rest are moderate, preliminary, or peripheral.
For the Origin / Guardian-Agent stack, the actionable takeaways are: treat RAG knowledge bases as protected
IP assets with dual-path defense plus query monitoring; do not trust agent self-policing in multi-agent
pipelines (compromised internal agents defeat user-level guardrails); treat certificates and scores as
bounded assurances requiring out-of-band correctness signals; and instrument invalid-action rate as a cheap
runtime health monitor.

---

## 2. Scope and boundaries

**In scope (as filed in the corpus "Defense-Mitigation" category):** proactive/reactive defenses and their
red-teaming across RAG systems, multi-agent LLM pipelines, certified-robustness verification, federated
GraphLLMs, LLM training-data extraction, generative-voice-cloning protection, and (peripherally) GNN
tooling, continual-learning stability, and LLM-agent planning benchmarks.

**Boundaries and caveats:**
- **Three papers are peripheral to agent security** and are flagged as such in their own cards: A40129
  (PDFK) treats "optimization dynamics itself" as the adversary (catastrophic forgetting), not a real
  attacker; A39818 (TowerMind) is a capability/reliability benchmark with no attacker/defender model; A42364
  (GNN-AID) is a tooling framework positing no single threat model and reporting no security numbers.
- **Modality spread is wide** (audio, vision/ImageNet, text-attributed graphs, RAG text, code generation,
  LLM memorization), so direct head-to-head comparison is largely impossible; agreements are thematic.
- **Truncated extracted text** limits verification for several cards (A37002, A39732, A39818, A41134/partial
  prompt details) — where numbers were not visible they are marked "not stated in paper."
- **No cross-paper benchmark overlap** and **no independent replication** — do not read convergent themes as
  replicated effect sizes.

---

## 3. Dominant threat models

Knowledge assumptions span the full white-box → black-box range; "defense" strength is only as good as the
assumed adversary access.

- **Proactive protection of one's own media against generative misuse (gray-box transfer).** A37002
  (VoiceCloak): the "defender" is the protected speaker who perturbs their reference audio; the adversary is
  an external cloner running open-source diffusion voice-conversion at inference. Exact cloning model
  unknown; transfer sought via a WavLM feature space.
- **Adversary who attacks the verification/defense layer itself (white-box, known σ).** A37924 (GhostCert):
  a white-box adversary who knows the smoothing noise level σ spoofs randomized-smoothing certificates so a
  wrong class receives a large "ghost" robustness radius; abstentions are recorded as denial-of-service.
- **Semi-trusted participants in a distributed LLM system (gray/white-box at a client).** A39732
  (STRUM/GTAE): malicious federated clients in text-attributed federated graph learning jointly perturb
  graph structure and node text via a local surrogate GCN.
- **Black-box extraction of a proprietary asset via the query API.** A40432 (RAGFort): agent-based
  extraction attacks (RAG-Thief, Worm-Attack) aggregate crafted-query responses to reconstruct a proprietary
  RAG knowledge base and clone the service. Black-box API access only — matches commercial deployments.
- **Malicious injection into multi-agent pipelines (gray/black-box, prompt-level).** A41134 (IMBIA): two
  scenarios — MU-BA (a malicious user exploits benign agents via positional prompt injection appended after
  a benign request) and BU-MA (a benign user is served by compromised agents with hidden instructions in
  their role profiles).
- **White-box training-data extraction.** A41145 (CoSPED): a white-box adversary attaches a trainable soft
  prompt to a frozen open-weight LLM to regenerate memorized suffixes.

**Non-adversarial / no-threat-model framings (peripheral):** A40129 (adversary = catastrophic forgetting,
no attacker), A39818 ("hallucination" = rule-invalid actions; "misleading information" = deceptive map
features; no attacker/defender), A42364 (framework packaging attacks/defenses; threat model "not stated in
paper").

---

## 4. Major attack families

- **Adversarial perturbation / evasion.** Central to A37924 (region-masked l2 perturbations via
  GradCAM/attention saliency fused with SAM segmentation masks, optimized with PGD over noisy batches),
  A39732 (influence-guided edge flips + embedding-space gradient-guided synonym substitution), and — used
  *defensively* — A37002 (four-term perturbation of reference audio).
- **Verifier gaming / certificate spoofing.** A37924's core contribution: coaxing a probabilistic certified
  defense into issuing a large deceptive certificate for the wrong class (author-reported ASR 30–100% vs.
  Shadow Attack's ~30–65%), with abstentions recorded as denial-of-service.
- **Prompt injection into agent pipelines.** A41134's IMBIA appends a tripartite malicious prompt
  (Ts secret-task summary, Td task descriptions, Ci code instructions) after a benign request (MU-BA) or
  embeds it in agent role profiles (BU-MA) so generated software carries concealed malicious behavior
  (5 malware families, 12 behaviors).
- **Model / knowledge-base extraction.** A40432 (black-box KB reconstruction via intra-class deepening +
  inter-class topic expansion, using agent memory loops) and A41145 (targeted training-data reconstruction
  via consistency-driven soft-prompt tuning).
- **Data poisoning + multimodal compounding.** A39732's GTAE couples structural poisoning (degree-budgeted
  edge flips) with l0-sparse text perturbation to transfer across backbones.
- **Cross-agent / supply-chain compromise.** A41134's BU-MA treats third-party agents as an untrusted supply
  chain whose compromise propagates down the pipeline (e.g., a tester agent silently adds a `send_email`
  exfiltration function).

---

## 5. Major defense families

- **Retrieval isolation + output filtering (dual-path).** A40432 (RAGFort): inter-class isolation via
  HDBSCAN pseudo-labels + supervised-contrastive reindexing of the retriever, combined with intra-class
  constrained cascade generation (lightweight draft model + stronger reference/verifier applying a
  sensitivity-aware rejection rule `π = (1−r)·q_t + r·p_t`). Strongest-evidenced defense in the category.
- **Prompt-level guardrailing.** A41134 (Adv-IMBIA): adversarial guardrail prompts embedded in agent
  profiles (Adv-MU-BA) or at the user interface (Adv-BU-MA) instructing agents to check requirements against
  explicit security guidelines and refuse/replace/halt.
- **Adversarial training + robustness-aware aggregation.** A39732 (STRUM): local modality-aware adversarial
  training plus a federated aggregation weight that up-weights clients showing smaller accuracy drops under
  local adversarial evaluation.
- **Model editing / knowledge erasure.** A41145 (CoSPED defense side): ROME rank-one model editing to
  suppress memorized content (author-reported extraction 65.2% → 1.6%).
- **Proactive input-side cloaking.** A37002 (VoiceCloak): imperceptible perturbation of the protected media
  targeting the generative process (denoising trajectory, cross-attention conditioning, U-Net feature
  hierarchy) rather than a single encoder subnetwork.
- **Action-validity gating (transferable pattern, not framed as security).** A39818: rule/state validity
  checks before executing a proposed agent action; invalid-action rate as a reliability signal.
- **Sharpness-aware stabilization (non-security).** A40129 (PDFK): EMA teacher + one-step worst-case KL
  perturbation and a flattening loss to enlarge the "fragility radius" against update-induced forgetting.
- **Unified attack/defense/interpretability tooling (no efficacy evaluation).** A42364 (GNN-AID): base
  Attacker/Defender/Explainer classes with MLOps, GUI, and experiment tracking.

---

## 6. Most influential concepts

1. **"A certificate/score is a bounded-norm assurance, not a correctness oracle."** (A37924) — the single
   most transferable conceptual result; directly informs any "models propose / verifiers verify / gates
   decide" design.
2. **Dual-path / complementary defense.** (A40432) — protecting only one extraction path (inter- or
   intra-class) leaves the other leaking; the two prior single-path defenses even conflict by construction.
3. **MU-BA vs. BU-MA asymmetry.** (A41134) — defending against a malicious *user* via agent-level guardrails
   is far easier than defending a benign user against internally *compromised agents*; user-level defense
   largely fails against BU-MA.
4. **Shared margin / minimal-flip-radius / worst-case-perturbation geometry across offense, defense, and
   stability.** Explicitly cross-linked by the cards: A37924 (spoofing radius), A37002 (output-discrepancy
   maximization through the diffusion graph), A40129 (fragility radius `r_θ = |γ_θ|/‖∇_θ γ_θ‖`, SAM-like
   min-max flattening). Reviewer synthesis: the *setting*, not the math, determines whether it is "security."
5. **Representation/embedding-space objectives as a cross-model transfer proxy.** WavLM feature space
   (A37002); embedding-gradient text perturbation (A39732); supervised-contrastive reindexing (A40432);
   soft-prompt embedding steering (A41145).
6. **Model editing as targeted incident-containment / erasure** without full retraining. (A41145, ROME.)
7. **Invalid-action rate as a runtime reliability/health signal.** (A39818.)

---

## 7. Common datasets and benchmarks

No dataset is shared across papers; each is domain-specific.

- **A40432 (RAGFort):** HealthCareMagic (medical QA), Enron Email, MathQA — each built into an independent
  proprietary KB. Attacks: RAG-Thief, Worm-Attack (Cohen et al. 2024). Baseline defenses: re-ranking,
  summarization, Set Distance Threshold (Zeng et al. 2024a). Generators: Qwen-14B, DeepSeek-R1-8B,
  Gemma-3-27B; Sentence-BERT retriever.
- **A41134 (IMBIA):** 480 test cases = 40 benign tasks (one sampled from each of 40 subcategories of SRDD,
  the Software Requirement Description Dataset from ChatDev, 1,200 tasks total) × 12 malicious behaviors
  across Trojan, Spyware, Adware, Ransomware, and Virus families. Frameworks: ChatDev, MetaGPT, AgentVerse.
  LLM backend: GPT-4o-mini; GPT-4o as automated evaluator.
- **A41145 (CoSPED):** LM Extraction Benchmark (Carlini et al. 2024; from The Pile) — D1 = 15,000 sequences
  (50-token prefix / 50-token suffix), D2 = 16,000 sequences (150-token prefix / 50-token suffix). LAMBADA
  referenced for utility. Models: GPT-Neo 1.3B, Pythia 1.4B.
- **A37924 (GhostCert):** ImageNet; three defended models — Randomized Smoothing + ResNet50, Smoothed
  Ensemble, DensePure (diffusion denoiser + ViT-Large/Patch16-512), at σ = 0.25 and 0.5; compared to Shadow
  Attack (ICLR 2020) and a bounded-distortion Shadow variant. A user study on imperceptibility is referenced
  (protocol/scale not fully visible in extracted text).
- **A40129 (PDFK):** CIFAR-10, CIFAR-100, ImageNet-Subset, Tiny-ImageNet, under Clear and Blurry
  task-boundary protocols, at multiple buffer sizes (CIFAR 200/500/1000; ImageNet-Subset & Tiny-IN
  1000/2000/5000); 10 replay baselines (ER, DER++, DVC, ER-ACE, GSA, OCM, PCR, ER+MKD, ER+SDP, S6MOD).
- **A37002 (VoiceCloak):** VCTK and LibriTTS referenced in the bibliography; exact eval splits/models "not
  stated in paper."
- **A39732 (STRUM/GTAE):** internal inconsistency — abstract says "five real-world datasets," contributions
  say "three real-world TAG-FGL benchmarks" (unreconciled); Open Graph Benchmark referenced; exact set "not
  stated in paper."
- **A39818 (TowerMind):** five built-in TowerMind difficulty levels (self-contained; no external ML
  datasets); comparison table vs. ELF, DeepRTS, Gym-µrts, Mini HoK.
- **A42364 (GNN-AID):** MUTAG shown in the GUI; preloaded datasets included; no benchmark security
  evaluation reported.

---

## 8. Evaluation metrics

- **Attack Success Rate (ASR).** A37924 (untargeted = fraction misclassified; targeted = fraction classified
  as the attacker's target *and* assigned a certificate radius); A41134 (ASR and ASR-under-defense, ASR-d).
- **Spoofing Radius / certified radius, l2 norm, DoS (abstention) rate.** A37924.
- **Chunk Recovery Rate (CRR), absolute and "Relative Mean CRR" (× of undefended); Answer Accuracy; FLOPs.**
  A40432.
- **Extraction rate via k-exact-match (ER30, ER50); token-level accuracy; downstream utility.** A41145.
- **Benign Utility (BU), Utility Under Attack, Reject Rate (RR), RR-under-defense (RR-d), plus
  benign/attacked consistency.** A41134.
- **Classification accuracy / accuracy-drop under attack** (used both as attack-effectiveness measure and,
  in A39732, as the per-client robustness signal for aggregation).
- **Accuracy (%) and K-step Forgetting Rate (KFR); loss-landscape sharpness; fragility radius.** A40129.
- **Defense Success Rate (DSR) claimed but numeric values "not stated in paper"; cosine speaker-similarity,
  PESQ, DTW referenced.** A37002.
- **In-game score (capability) and invalid-action rate ("hallucination").** A39818.
- **Interpretability fidelity; no attack-success/defense-effectiveness numbers reported.** A42364.

Cross-cutting caveat (reviewer synthesis): A41134 reports ASR reductions as *relative* percentages and uses
an LLM-as-judge (GPT-4o, author-reported 86.34% agreement with manual evaluators) — residual absolute ASR
can remain high, and LLM-judge bias is present.

---

## 9. Strongest replicated findings

These are convergent themes across independent domains (not independent replications of one effect size).

1. **Single-point defenses are insufficient; layered / multi-point defense is required** — the strongest
   cross-paper theme.
   - A40432: single-path RAG protection still leaks >40% of chunks under RAG-Thief, while the joint dual-path
     defense reaches the lowest chunk-recovery rate (author-reported relative-mean CRR 0.51× vs. 0.87–0.91×
     for single-path baselines; ablation InterOnly 0.75×, IntraOnly 0.83×, full 0.51×).
   - A39732: argues single-modality FL defenses (DP, cryptography, anomaly detection) fail when text and
     structure are jointly perturbable (author claim; numerics "not stated in paper").
   - A41134: risk and effective defense are stage-dependent; coding and testing stages are the highest-value
     targets, and defense-in-depth across stages outperforms any single intervention point.
2. **A verification artifact is not a correctness oracle** (A37924, demonstrated under white-box + known σ):
   a large certified radius can be spoofed with imperceptible, semantics-preserving perturbations. The
   formal certificate is not invalidated; its use as a *label-correctness signal* is what fails. Reviewer
   synthesis: this generalizes the "gate keyed solely on a certificate can be deceived" caution.
3. **Defenses are near-universally NOT evaluated against adaptive, defense-aware attackers** — carried
   explicitly by every security card (A37002 purification/re-recording untested; A39732 no adaptive attacker
   vs. STRUM; A40432 no defense-aware extraction; A41134 non-adaptive prompt defense; A41145 ROME not tested
   against post-edit soft-prompt re-optimization). This is the strongest *methodological* finding and the
   most important calibration for any product claim.
4. **A model-editing defense can produce a large author-reported extraction-rate drop** (A41145: 65.2% →
   1.6% via ROME) — a single-paper, white-box, small-model result, not yet replicated or adaptively tested.

---

## 10. Conflicting findings

Direct head-to-head contradictions are rare (papers span different modalities); conflicts are mostly
*internal* or *design-tension*.

- **Mutually conflicting prior RAG defenses.** A40432 reports that the two existing single-path defenses
  conflict by construction: inter-class distance-thresholding forces focus on few chunks, while intra-class
  summarization requires aggregating across many chunks — motivating a design that reconciles both.
- **Certificate resistance is not uniform.** A37924 notes the diffusion-denoiser certification (DensePure)
  is the *most resistant* of the three defenses tested even though it, too, is spoofable — a nuance against a
  flat "all certificates are broken" reading.
- **Internal inconsistency (evidence-integrity flag).** A39732's own text reports "five real-world datasets"
  (abstract) vs. "three real-world TAG-FGL benchmarks" (contributions), unreconciled in the extracted text —
  lowering confidence in its empirical section as extracted.
- **Baseline brittleness vs. average accuracy (peripheral).** A40129 shows some baselines are competitive in
  individual cells (e.g., ER+MKD edges CIFAR-10 Clear-1000) yet collapse under Blurry boundaries (e.g., GSA
  to near-random), illustrating that end-of-stream accuracy hides short-horizon instability.

---

## 11. Defense bypasses

**Demonstrated:**
- **Certificate spoofing bypasses certified defenses** (A37924, under white-box + known σ): ghost
  certificates assign a large radius to a wrong class; abstention becomes DoS.
- **Compromised internal agents (BU-MA) bypass user-level guardrails** (A41134): Adv-IMBIA is markedly
  weaker in BU-MA than MU-BA — for MetaGPT the author-reported ASR reduction under BU-MA is only 7% (vs. 40%
  under MU-BA), i.e., user-interface-level defense largely fails against internally compromised agents.
- **Residual leakage persists under the strongest defense evaluated** (A40432): full RAGFort still leaves an
  author-reported ~28% chunk-recovery rate in the shown cell (57.16% → 27.96%, HealthCareMagic, Qwen-14B) —
  substantial mitigation, not elimination; single-module variants still expose >40%.

**Reviewer-identified (not yet demonstrated in the papers):**
- Proactive audio perturbation is historically vulnerable to adversarial purification / denoising /
  resampling / re-recording; no adaptive-attacker or robustness-to-preprocessing evaluation is visible
  (A37002).
- ROME editing may be reversible by a defense-aware attacker who re-tunes the soft prompt post-edit (A41145).
- Robustness-aware aggregation is a new trust-decision surface a client could game by appearing locally
  robust while poisoning globally — a confused-deputy / evaluation-gaming risk (A39732).
- An attacker who knows RAGFort reindexes topics and cascades generation could adjust query strategy
  (within-cluster probing, paraphrase to dodge the rejection rule); residual ~28% CRR suggests headroom
  (A40432, reviewer synthesis).

---

## 12. Known benchmark limitations

- **Truncated results in extracted text** limit verification: numeric defense-success and quality-degradation
  values not visible for A37002; no numeric attack/defense values visible for A39732; per-model scores not
  visible for A39818; some result tables truncated for A37924 and A40432.
- **LLM-as-judge bias.** A41134 uses GPT-4o as an automated evaluator (author-reported 86.34% agreement with
  manual evaluators) and reports ASR reductions as *relative* percentages — residual absolute ASR can remain
  high (reviewer synthesis).
- **Narrow model / modality scope.** A41145 uses small open-weight models (GPT-Neo 1.3B, Pythia 1.4B) under
  white-box access — does not bound black-box or production-scale risk; A37924 is vision/ImageNet only;
  A40129 is image-classification only; A41134 uses a single backend (GPT-4o-mini); A40432 covers three
  domains and three LLMs but no multilingual / very-large / streaming-updated KBs.
- **Benchmark contamination.** A39818 mitigates via an author-editable level editor, but its five built-in
  levels remain contamination-exposed once public.
- **Extraction "success" is exact-match on public-corpus suffixes.** A41145's ER30/ER50 on The Pile may not
  reflect real-world sensitive-PII extraction rates (reviewer synthesis).
- **No security evaluation at all.** A42364 (framework/demo): no threat model, no quantitative attack/defense
  numbers, no adaptive testing — efficacy of its bundled defenses is unestablished; A39818 and A40129 are
  reliability/stability benchmarks, not security benchmarks.

---

## 13. Implementation patterns

- **"Propose → verify → gate."** Action-validity gating before execution (A39818); draft-model proposal
  filtered by a stronger reference/verifier via a rejection rule (A40432's cascade); guardrail agents
  checking generated code against explicit security guidelines before emission (A41134).
- **Dual / two-part defense architectures.** Inter-class + intra-class (A40432); input-level adversarial
  training + system-level robustness-aware aggregation (A39732); temporal EMA + spatial flattening (A40129).
- **Representation/embedding-space objectives as a transfer proxy.** WavLM (A37002); embedding-gradient text
  perturbation (A39732); supervised-contrastive reindexing (A40432); soft-prompt embedding steering (A41145).
- **Region-focused perturbation via saliency + segmentation.** A37924 fuses GradCAM/attention saliency with
  SAM masks to confine PGD perturbations to semantically-coherent regions (imperceptible *and*
  certificate-efficacious).
- **Positional prompt injection appended after a benign request** to evade safety filters (A41134 MU-BA) —
  argues for structural separation of user intent from executable instruction.
- **Model editing as targeted incident-containment / erasure.** ROME suppresses specific memorized content
  without full retraining (A41145).
- **Base-class abstractions for a living attack/defense catalog.** Attacker/Defender/Explainer subclassing
  (A42364).
- **Decoupling protected retriever index from the generator's content pipeline** to preserve answer quality
  while isolating topics (A40432).

---

## 14. Product design implications

For the Origin / Guardian-Agent stack (author findings + reviewer synthesis, labeled).

- **Treat the RAG knowledge base as a protected IP asset.** A40432 argues for retrieval isolation + output
  filtering combined with rate-limiting and query monitoring; recursive topic expansion and memory-driven
  query refinement are detectable extraction signals. Author-reported cost is <2 accuracy points with FLOPs
  unchanged or reduced — practical for deployment, but a mitigation, not a guarantee (residual ~28% CRR
  remains).
- **Do not trust agent self-policing in multi-agent pipelines.** A41134 (author findings + reviewer
  synthesis): because BU-MA (compromised internal agent) defeats user-level guardrails, prefer cryptographic
  agent provenance/attestation, least-privilege capability isolation for tool-calling code (e.g., blocking
  outbound email/network from generated apps), sandboxed execution, and independent code-scanning gates. The
  12-behavior taxonomy (send_email, external URL fetch, clipboard/keyboard capture, file encryption) doubles
  as concrete egress/detection signatures.
- **Certificates and scores are bounded assurances, not correctness oracles.** A37924 implies safety-critical
  gates should add out-of-band correctness signals (human review, provenance, ensemble/denoiser
  disagreement), hide the noise level σ, rate-limit, and prefer denoiser-based certification (most resistant
  here) — rather than gate solely on a certified radius.
- **Do not expose white-box internals or user-attachable soft prompts on models trained on sensitive /
  copyrighted corpora.** A41145 recommends combining deduplication, DP training, and post-hoc knowledge
  editing, treating any one alone as insufficient; ROME offers an incident-containment/erasure path without
  full retraining (but validate against re-optimization and across the downstream task suite first).
- **Voice/identity cloaking is an opt-in complement, not a guarantee.** A37002 positions perturbation as a
  pre-publication mitigation to pair with reactive deepfake/anti-spoofing detection and voiceprint liveness;
  identity-authentication systems should not treat cloaked-audio availability as protection against
  impersonation.
- **Invalid-action rate is a cheap runtime health monitor.** A39818's executability gating and
  invalid-action-rate signal transfer directly to production agent action-guards.

---

## 15. Architecture implications

- **Layered, multi-point defense is the default posture, not defense-in-one-place.** Convergent across
  A40432, A39732, A41134 — architect for complementary controls at retriever, generator, aggregation, and
  per-agent stages.
- **Separate user intent from executable instruction structurally.** A41134's positional-injection finding
  implies trailing guardrail text is insufficient; enforce a boundary the model cannot be talked past.
- **Add an out-of-band correctness channel to any verifier-gated pipeline.** A37924: a gate keyed solely on a
  verification artifact (certificate, score) is spoofable; combine with provenance, human review, or
  ensemble/denoiser disagreement, and hide verifier internals (σ).
- **Treat every new trust-decision surface introduced by a defense as attackable.** A39732's
  robustness-aware aggregation weight is itself a gameable surface (reviewer synthesis) — harden the meta-
  decision, log per-client robustness scores, and combine with server-side integrity checks.
- **A unified attack-sim + defense + trace-interpretability + experiment-tracking console is a transferable
  blueprint.** A42364's Attacker/Defender/Explainer + MLOps/GUI pattern maps onto an autonomy-trace/Guardian
  console — though the framework certifies no defense itself.
- **Decouple protected components from utility-critical paths.** A40432 keeps the query encoder and generator
  input pipeline unchanged while reindexing the retriever — a pattern for adding protection without utility
  regression.

---

## 16. Launch and assurance implications

- **Every defense claim must be qualified to its evaluated threat model and tested attacks.** No paper here
  evaluated an adaptive, defense-aware attacker; launch language must say "reduced ASR/CRR against the tested
  attacks under the evaluated threat model," never "secure" or "proven-safe."
- **Adopt these as pre-deployment red-team KPIs:** CRR against RAG-Thief and Worm-Attack (A40432); ASR and
  absolute ASR-d across MU-BA and BU-MA (A41134); certificate-spoofing ASR / DoS rate (A37924); ER30/ER50
  extraction rate before and after editing (A41145). Report absolute residuals, not only relative reductions.
- **Instrument runtime monitoring signals identified by the papers:** recursive topic-expansion / memory-
  driven query patterns (A40432); insertion of network/exfiltration primitives in generated code (A41134's
  12-behavior taxonomy); clusters of large-radius certificates on near-duplicate inputs (A37924); repeated
  prefix-conditioned queries and soft-prompt attachment (A41145); invalid-action-rate spikes (A39818);
  per-client accuracy-drop / robustness-score shifts (A39732).
- **Budget for residual leakage.** A40432's strongest configuration still leaves ~28% CRR; pair any single
  defense with rate-limiting, query monitoring, and incident-response (e.g., ROME-style targeted erasure per
  A41145).
- **Independent validation is a launch gate.** Framework-provided or single-paper defenses (A42364, and any
  single-study number) must be independently validated on the target stack before operational reliance;
  A42364 explicitly certifies no defense.

---

## 17. Open research problems

- **Adaptive, defense-aware attackers** remain unevaluated across essentially every defense here — the
  single largest gap (A37002, A39732, A40432, A41134, A41145).
- **Robustness of proactive perturbations** to purification, denoising, resampling, compression, and
  physical re-recording (A37002; physical channel "not stated in paper").
- **Closing residual leakage in extraction defenses** (A40432 ~28% residual CRR; durability of A41145's ROME
  edits under defense-aware re-optimization).
- **Defending internally-compromised agents from the user level** (A41134 BU-MA) — shown to be hard;
  cryptographic provenance and capability isolation are proposed but not tested in the paper.
- **Hardening trust-decision surfaces introduced by defenses themselves** — e.g., gaming of robustness-aware
  federated aggregation weights (A39732).
- **Out-of-band correctness signals for certified pipelines** beyond the certified radius (A37924).
- **Generalization gaps:** small-model → production scale (A41145); single → multiple LLM backends (A41134);
  vision → other modalities (A37924); reconciling/verifying truncated or internally-inconsistent empirical
  sections (A37002, A39732, A39818).

---

## 18. Recommended foundational papers

Prioritized for a practitioner building an agent-security defense stack (weighting evidence quality,
reproducibility, and threat-model realism):

1. **A40432 (RAGFort)** — realistic black-box threat model, two agent-based extraction attacks, three
   domains, three LLMs, quantified CRR reductions with utility/efficiency preservation, ablations, released
   code. The clearest "how to defend a deployed LLM asset" template. Evidence: moderate (leaning strong).
2. **A37924 (GhostCert)** — strongest-evaluated paper in the category (large-scale ImageNet, three certified
   defenses incl. a diffusion denoiser, targeted + untargeted, budget sweeps, released code); source of the
   load-bearing "certificate ≠ correctness / verifier gaming" insight. Evidence: strong.
3. **A41134 (IMBIA / Shadows in the Code)** — core multi-agent-pipeline threat model (prompt injection +
   compromised-agent supply chain), a defined 480-case benchmark across three real frameworks, quantified
   attack/defense results, and the important MU-BA vs. BU-MA defense asymmetry. Evidence: moderate.

---

## 19. Recommended frontier papers

Newer or narrower directions worth tracking, with caveats:

1. **A41145 (CoSPED)** — training-data-extraction risk plus a quantified, utility-aware model-editing defense
   (author-reported 65.2% → 1.6%); frontier value is the extraction-mechanism → mitigation bridge, tempered
   by white-box, small-model scope and no adaptive test. Evidence: moderate.
2. **A39732 (STRUM / GTAE)** — the multimodal (structure + text) federated-GraphLLM threat/defense framing,
   relevant to multi-tenant RAG-over-graph systems; preliminary evidence (unreconciled dataset count, no
   visible numerics, no adaptive-attacker evaluation, no code link). Evidence: preliminary.
3. **A37002 (VoiceCloak)** — diffusion-era proactive identity cloaking; mechanism-grounded and topical, but
   numeric results and adaptive/robustness testing were not visible in the extracted text. Evidence:
   moderate, unverifiable from extract.

Peripheral (architectural inspiration or transferable patterns only, not defense evidence): **A39818**
(action-validity gating pattern), **A42364** (unified attack/defense/interpretability console blueprint),
**A40129** (EMA + sharpness-aware stabilization for continually-updated models — non-adversarial).

---

## 20. Source map (paper id → one-line relevance)

- **A37002 — VoiceCloak: A Multi-Dimensional Defense Framework Against Unauthorized Diffusion-Based Voice
  Cloning** (AAAI-26; Hu, Wu, Lu, Luo; arXiv:2505.12332): proactive input-side audio cloaking against
  diffusion voice-cloning; opt-in mitigation, numerics not visible in extract, adaptive/purification
  robustness untested.
- **A37924 — Certified but Fooled! Breaking Certified Defences with Ghost Certificates** (AAAI-26; Vo, Haq,
  Montague, Abraham, Abbasnejad, Ranasinghe; code github.com/ghostcert): white-box, known-σ spoofing of
  randomized-smoothing certificates; source of "certificate ≠ correctness"; strongest evidence in category.
- **A39732 — Towards Robust Text-Attributed Federated Graph Learning: Multimodal Threats and Defense**
  (AAAI-26; Shi, Wan, Huang, Wu, Zhang, Ye): dual-modality (structure+text) attack GTAE + STRUM defense for
  federated GraphLLMs; preliminary (dataset-count inconsistency, no visible numerics, no code link).
- **A39818 — TowerMind: A Tower Defence Game Learning Environment and Benchmark for LLM as Agents** (AAAI-26;
  Wang, Zhou, Zhao, Liu, Ma, Ushaw, Davison): LLM-agent planning/reliability benchmark; peripheral to
  security; contributes the transferable action-validity-gating / invalid-action-rate pattern.
- **A40129 — Perturbing to Preserve: Defending Fragile Knowledge in Online Continual Learning** (AAAI-26;
  Zhou, Gao, Xu; code github.com/colaudiolab/PDFK): non-adversarial continual-learning stability (EMA +
  sharpness-aware flattening); security-flavored naming, benign setting; peripheral.
- **A40432 — RAGFort: Dual-Path Defense Against Proprietary Knowledge Base Extraction in RAG** (AAAI-26; Li,
  Pan, Xiong et al.; arXiv:2511.10128; code github.com/happywinder/RAGFort): black-box RAG KB-extraction
  defense (contrastive reindexing + cascade generation); strongest agent-security-relevant defense; residual
  ~28% CRR.
- **A41134 — Shadows in the Code: Risks and Defenses of LLM-based Multi-Agent Software Development Systems**
  (AAAI-26; Wang, Huang, Liang, Li, Du; arXiv:2511.18467; code github.com/wxqkk0808/IMBIA): IMBIA attack +
  Adv-IMBIA guardrail across ChatDev/MetaGPT/AgentVerse; MU-BA vs. BU-MA asymmetry; core multi-agent threat
  model.
- **A41145 — CoSPED: Consistent Soft Prompt Targeted Data Extraction and Defense** (AAAI-26; Yang, Fok,
  Thing; arXiv:2510.11137): white-box soft-prompt training-data extraction + ROME model-editing defense
  (author-reported 65.2% → 1.6%); small open-weight models; no adaptive test.
- **A42364 — GNN-AID: Graph Neural Network Analysis, Interpretation and Defense** (AAAI-26; Lukianov,
  Drobyshevskiy, Sazonov, Soloviov, Makarov; code github.com/ispras/GNN-AID): unified GNN
  attack/defense/interpretability tooling framework; no security evaluation; architectural-blueprint value
  only.
