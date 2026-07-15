# Defense-Mitigation — Partial Synthesis (chunk 0 of 9 papers)

Papers: A37002, A37924, A39732, A39818, A40129, A40432, A41134, A41145, A42364
Scope note: this synthesis covers ONLY these nine cards. All numeric values are author-reported unless
labeled reviewer synthesis; where a card states a value was truncated from the extracted text, that is
flagged as "not stated in extracted text." Calibrated language is used throughout — findings hold "under
the evaluated threat model" and "against the tested attacks," not in general.

---

## Dominant threat models

This chunk is heterogeneous: three cards are core LLM/agent-system security, three are adversarial-ML in
adjacent modalities, and three are peripheral (a benchmark, a non-adversarial stability method, and a
tooling framework). The security-relevant threat models cluster as:

- **Proactive protection of one's own media against generative misuse.** In A37002 (VoiceCloak) the
  "defender" is the protected speaker who perturbs their reference audio; the adversary is an external
  cloner who runs open-source diffusion voice-conversion at inference. Gray-box on the defender side
  (exact cloning model unknown; transfer sought via WavLM feature space).
- **Adversary who attacks the verification/defense layer itself.** A37924 (GhostCert) is an attack paper
  filed here: a white-box adversary (with knowledge of the smoothing noise level σ) spoofs randomized-
  smoothing certificates so a wrong class receives a large "ghost" robustness radius. Adaptive with
  respect to the certification mechanism.
- **Semi-trusted participants in a distributed LLM system.** A39732 (STRUM/GTAE) models malicious
  federated clients in text-attributed federated graph learning who jointly perturb graph structure and
  node text; gray/white-box at the client via a local surrogate.
- **Black-box extraction of a proprietary asset via the query API.** A40432 (RAGFort) defends a
  proprietary RAG knowledge base against agent-based extraction attacks (RAG-Thief, Worm-Attack) that
  aggregate crafted-query responses to reconstruct the knowledge base and clone the service.
- **Malicious injection into multi-agent pipelines.** A41134 (IMBIA/Shadows in the Code) models two
  scenarios: a malicious user exploiting benign agents (MU-BA, positional prompt injection appended after
  a benign request) and a benign user served by compromised agents (BU-MA, hidden instructions in agent
  profiles) in end-to-end software-generation frameworks.
- **White-box training-data extraction.** A41145 (CoSPED) models a white-box adversary who attaches a
  trainable soft prompt to a frozen open-weight LLM to regenerate memorized suffixes.

Peripheral / non-adversarial threat framings (reviewer-flagged as outside the agent-security core):
A40129 (PDFK) treats "optimization dynamics itself" as the adversary (catastrophic forgetting), not a real
attacker; A39818 (TowerMind) is a capability/reliability benchmark with no attacker/defender model (its
"hallucination" = rule-invalid actions, "misleading information" = deceptive map features); A42364
(GNN-AID) is a tooling framework that packages attacks/defenses but posits no single threat model.

Knowledge assumptions span the full range: white-box (A37924, A41145), gray/white-box at a federation
client (A39732), gray/black-box prompt-level (A41134), gray-box transfer (A37002), and black-box query
API (A40432) — a useful reminder that "defense" results are only as strong as the assumed adversary access.

---

## Major attack families

- **Adversarial perturbation / evasion.** Central to A37924 (region-masked l2 perturbations via GradCAM/
  attention + SAM segmentation, optimized with PGD over noisy batches), A39732 (influence-guided edge
  flips + embedding-space gradient-guided synonym substitution), and — used *defensively* — A37002
  (four-term perturbation of reference audio).
- **Verifier gaming / certificate spoofing.** A37924's core contribution: coaxing a probabilistic
  certified defense into issuing a large deceptive certificate (author-reported ASR 30–100% vs. Shadow
  Attack's 30–65%), with abstentions recorded as denial-of-service.
- **Prompt injection into agent pipelines.** A41134's IMBIA appends a tripartite malicious prompt after a
  benign request (MU-BA) or embeds it in agent role profiles (BU-MA) to make generated software carry
  concealed malicious behavior (5 malware families, 12 behaviors).
- **Model / knowledge-base extraction.** A40432 (black-box KB reconstruction via intra-class deepening +
  inter-class topic expansion) and A41145 (targeted training-data reconstruction via consistency-driven
  soft-prompt tuning).
- **Data poisoning + multimodal compounding.** A39732's GTAE couples structural poisoning (edge flips)
  with text perturbation to transfer across backbones.
- **Cross-agent / supply-chain compromise.** A41134's BU-MA scenario treats third-party agents as an
  untrusted supply chain whose compromise propagates down the pipeline (e.g., a tester agent silently
  adds a `send_email` exfiltration function).

---

## Major defense families

- **Proactive input-side cloaking.** A37002: imperceptible perturbation of the protected media targeting
  the generative process (denoising trajectory, cross-attention conditioning, U-Net feature hierarchy)
  rather than a single encoder subnetwork.
- **Adversarial training + robustness-aware aggregation.** A39732 (STRUM): local modality-aware
  adversarial training plus a federated aggregation weight that up-weights clients showing smaller
  accuracy drops under local adversarial evaluation.
- **Retrieval isolation + output filtering (dual-path).** A40432 (RAGFort): inter-class isolation via
  HDBSCAN pseudo-labels + supervised-contrastive reindexing of the retriever, combined with intra-class
  cascade generation (draft model + stronger reference/verifier applying a sensitivity-aware rejection rule).
- **Prompt-level guardrailing.** A41134 (Adv-IMBIA): adversarial guardrail prompts embedded in agent
  profiles (MU-BA) or at the user interface (BU-MA) instructing agents to check requirements against
  explicit security guidelines and refuse/halt.
- **Model editing / knowledge erasure.** A41145: ROME rank-one model editing to suppress memorized
  content (author-reported extraction 65.2% → 1.6%).
- **Sharpness-aware stabilization (non-security).** A40129 (PDFK): EMA teacher + one-step worst-case KL
  perturbation and a flattening loss to enlarge the "fragility radius" against update-induced forgetting.
- **Action-validity gating (transferable pattern).** A39818: rule/state validity checks before executing
  a proposed agent action.
- **Unified attack/defense/interpretability tooling.** A42364 (GNN-AID): base Attacker/Defender/Explainer
  classes with MLOps, GUI, and experiment tracking (no efficacy evaluation).

---

## Strongest replicated findings

1. **Single-point defenses are insufficient; layered / multi-point defense is required.** This is the
   strongest cross-paper theme, replicated across independent domains: A40432 shows single-path RAG
   protection still leaks >40% of chunks under RAG-Thief while the joint dual-path defense reaches the
   lowest chunk-recovery rate (author-reported relative-mean CRR 0.51× vs. 0.87–0.91× for single-path
   baselines); A39732 argues single-modality FL defenses (DP, crypto, anomaly detection) fail when text
   and structure are jointly perturbable; A41134 finds risk and effective defense are stage-dependent
   (coding/testing stages are the highest-value targets).
2. **A verification artifact is not a correctness oracle.** A37924 demonstrates (under a white-box,
   known-σ threat model) that a large certified radius can be spoofed with imperceptible, semantics-
   preserving perturbations — the formal certificate is not invalidated, but its use as a label-
   correctness signal is. Reviewer synthesis: this generalizes the "models propose / verifiers verify /
   gate decides" caution — a gate keyed solely on a certificate can be deceived.
3. **Defenses are near-universally NOT evaluated against adaptive, defense-aware attackers.** Every
   security card in this chunk carries this caveat explicitly (A37002 purification/re-recording untested;
   A39732 no adaptive attacker vs. STRUM; A40432 no defense-aware extraction; A41134 non-adaptive prompt
   defense; A41145 ROME not tested against post-edit soft-prompt re-optimization). This is the strongest
   *methodological* finding of the chunk and the most important calibration for any product claim.

---

## Conflicting findings

- **Few direct contradictions** because the papers span different modalities and domains; conflicts are
  mostly *internal* or *design-tension* rather than head-to-head.
- **Mutually conflicting prior RAG defenses.** A40432 reports that the two existing single-path defenses
  conflict by construction: inter-class distance-thresholding forces focus on few chunks while intra-class
  summarization requires aggregating across many chunks — motivating a design that reconciles both.
- **Certificate resistance is not uniform.** A37924 notes the diffusion-denoiser certification (DensePure)
  is the *most resistant* of the three defenses tested even though it, too, is spoofable — a nuance
  against a flat "certificates are broken" reading.
- **Internal inconsistency (evidence-integrity flag).** A39732's own text reports "five real-world
  datasets" (abstract) vs. "three real-world TAG-FGL benchmarks" (contributions) — unreconciled in the
  extracted text, which lowers confidence in its empirical section as extracted.

---

## Defense bypasses (demonstrated or reviewer-identified)

- **Certificate spoofing bypasses certified defenses** (A37924, demonstrated under white-box + known σ).
- **Compromised internal agents (BU-MA) bypass user-level guardrails** (A41134, demonstrated): Adv-IMBIA
  is markedly weaker in BU-MA than MU-BA — author-reported ASR reduction of only 7% for MetaGPT under
  BU-MA, i.e., user-interface-level defense largely fails against internally compromised agents.
- **Residual leakage persists under the strongest defense evaluated.** A40432's full RAGFort still leaves
  an author-reported ~28% chunk-recovery rate in the shown cell (57.16% → 27.96%) — substantial
  mitigation, not elimination.
- **Reviewer-identified, not yet demonstrated:** proactive audio perturbation is historically vulnerable
  to adversarial purification / denoising / resampling / re-recording (A37002); ROME editing may be
  reversible by a defense-aware attacker who re-tunes the soft prompt post-edit (A41145); robustness-aware
  aggregation is a new trust-decision surface that a client could game by appearing locally robust while
  poisoning globally (A39732).

---

## Benchmark / evaluation limitations

- **Truncated results in extracted text** limit verification for several cards: numeric defense-success
  and quality-degradation values not visible for A37002; no numeric attack/defense values visible for
  A39732; per-model scores not visible for A39818.
- **LLM-as-judge bias.** A41134 uses GPT-4o as an automated evaluator (author-reported 86.34% agreement
  with manual evaluators), and reports ASR reductions as *relative* percentages — residual absolute ASR
  can remain high (reviewer synthesis).
- **Narrow model / modality scope.** A41145 uses small open-weight models (GPT-Neo 1.3B, Pythia 1.4B)
  under white-box access — does not bound black-box or production-scale risk; A37924 is vision/ImageNet
  only; A40129 is image-classification only; A41134 uses a single backend (GPT-4o-mini).
- **Benchmark contamination.** A39818 mitigates via an author-editable level editor, but its five built-in
  levels remain contamination-exposed once public.
- **No security evaluation at all** in A42364 (framework/demo): no threat model, no quantitative attack/
  defense numbers, no adaptive testing — efficacy of its bundled defenses is unestablished here.

---

## Recurring implementation patterns

- **"Propose → verify → gate."** Recurs as: action-validity gating before execution (A39818), draft-model
  proposal filtered by a stronger reference/verifier via a rejection rule (A40432's cascade), and guardrail
  agents checking generated code against explicit security guidelines before emission (A41134).
- **Representation/embedding-space objectives as a cross-model transfer proxy.** WavLM feature space in
  A37002; embedding-gradient text perturbation in A39732; supervised-contrastive reindexing in A40432;
  soft-prompt embedding steering in A41145.
- **Margin / minimal-flip-radius / worst-case-perturbation mathematics reused across offense, defense, and
  non-adversarial stability.** Explicitly cross-linked by the cards: A37924 (spoofing radius), A37002
  (output-discrepancy maximization through the diffusion graph), A40129 (fragility radius
  `r=|γ|/‖∇γ‖`, SAM-like min-max flattening). Reviewer synthesis: the same geometry underpins attack,
  protection, and stability — the *setting*, not the math, determines whether it is "security."
- **Dual / two-part defense architectures.** A40432 (inter-class + intra-class), A39732 (input-level +
  system-level aggregation), A40129 (temporal EMA + spatial flattening).
- **Model editing as targeted incident-containment / erasure.** A41145's ROME path suppresses specific
  memorized content without full retraining.
- **Base-class abstractions for a living attack/defense catalog.** A42364's Attacker/Defender/Explainer
  subclassing pattern.

---

## Product / architecture implications (for the Origin / Guardian-Agent stack)

- **Treat the RAG knowledge base as a protected IP asset.** A40432 argues for retrieval isolation + output
  filtering combined with rate-limiting and query monitoring for extraction-style query patterns
  (recursive topic expansion, memory-driven query refinement are detectable signals). Author-reported cost
  is <2 accuracy points with FLOPs unchanged or reduced — practical for deployment, but a mitigation, not
  a guarantee (residual leakage remains).
- **Do not trust agent self-policing in multi-agent pipelines.** A41134 (reviewer synthesis, aligned with
  author findings) argues for cryptographic agent provenance/attestation, least-privilege capability
  isolation for tool-calling code (e.g., blocking outbound email/network from generated apps), sandboxed
  execution, and independent code-scanning gates — because BU-MA (compromised internal agent) defeats
  user-level guardrails. The paper's 12-behavior taxonomy (send_email, external fetch, clipboard/keyboard
  capture, file encryption) doubles as concrete egress/detection signatures.
- **Certificates and scores are bounded assurances, not correctness oracles.** A37924 implies safety-
  critical gates should add out-of-band correctness signals (human review, provenance, ensemble
  disagreement), hide the noise level σ, and rate-limit — rather than gate solely on a certified radius.
- **Do not expose white-box internals or user-attachable soft prompts on models trained on sensitive/
  copyrighted corpora.** A41145 recommends combining deduplication, DP training, and post-hoc knowledge
  editing, treating any one alone as insufficient; model editing offers an incident-containment/erasure
  path without full retraining.
- **Voice/identity cloaking is an opt-in complement, not a guarantee.** A37002 positions perturbation as a
  pre-publication mitigation to be paired with reactive deepfake/anti-spoofing detection and voiceprint
  liveness; identity-authentication systems should not treat cloaked-audio availability as protection
  against impersonation.
- **A unified attack-sim + defense + trace-interpretability + experiment-tracking console is a transferable
  blueprint.** A42364's design pattern maps directly onto an autonomy-trace/Guardian console (attack
  simulation, guardrail modules, trace interpretability, reproducible MLOps behind one API/GUI) — though
  the framework certifies no defense itself.
- **Invalid-action rate is a cheap runtime health monitor.** A39818's executability gating and invalid-
  action-rate signal transfer directly to production agent action-guards ("verify each proposed action
  against environment state/rules before executing").

---

## Open problems

- **Adaptive, defense-aware attackers** remain unevaluated across essentially every defense here — the
  single largest gap (A37002, A39732, A40432, A41134, A41145).
- **Robustness of proactive perturbations** to purification, denoising, resampling, compression, and
  physical re-recording (A37002; physical channel not evaluated).
- **Closing residual leakage** in extraction defenses (A40432 ~28% residual CRR; durability of A41145's
  ROME edits under re-optimization).
- **Defending internally-compromised agents from the user level** (A41134 BU-MA) — the paper shows this is
  hard; cryptographic provenance and capability isolation are proposed but not tested here.
- **Hardening new trust-decision surfaces** introduced by defenses themselves — e.g., gaming of
  robustness-aware federated aggregation weights (A39732).
- **Correctness signals for certified pipelines** beyond the certified radius (A37924).
- **Generalization gaps:** small-model → production scale (A41145), single → multiple LLM backends
  (A41134), vision → other modalities (A37924), and reconciling/verifying truncated empirical sections
  (A37002, A39732, A39818).

---

## Most load-bearing papers (by id)

1. **A40432 (RAGFort)** — strongest and most directly agent/LLM-system-security-relevant: realistic
   black-box threat model, evaluation against two agent-based extraction attacks, three domains and three
   LLMs, quantified CRR reductions with utility/efficiency preservation, ablations, and released code.
   Evidence: moderate (leaning strong).
2. **A41134 (IMBIA / Shadows in the Code)** — core multi-agent-pipeline threat model (prompt injection +
   compromised-agent supply chain) with a defined 480-case benchmark across three real frameworks and
   quantified attack/defense results, including the important MU-BA vs. BU-MA defense asymmetry.
   Evidence: moderate.
3. **A37924 (GhostCert / Certified but Fooled)** — the strongest-evaluated paper in the chunk (large-scale
   ImageNet, three certified defenses, targeted + untargeted, budget sweeps, released code) and the source
   of the load-bearing "certificate ≠ correctness / verifier gaming" insight. Evidence: strong.
4. **A41145 (CoSPED)** — training-data-extraction risk plus a quantified, utility-aware model-editing
   defense (author-reported 65.2% → 1.6%), directly relevant to memorization/privacy asset leakage.
   Evidence: moderate.
5. **A39732 (STRUM / GTAE)** — the multimodal (structure + text) federated-GraphLLM threat/defense framing,
   relevant to multi-tenant RAG-over-graph systems, though its evidence is preliminary (unreconciled
   dataset count, no visible numerics, no adaptive-attacker evaluation, no code link).

Peripheral in this chunk: A37002 (domain-specific proactive audio cloaking; moderate), A40129
(non-adversarial continual-learning stability; security-flavored naming but benign setting), A39818
(capability/reliability benchmark; transferable action-gating pattern only), and A42364 (GNN tooling
framework; no security evaluation — architectural inspiration only).
