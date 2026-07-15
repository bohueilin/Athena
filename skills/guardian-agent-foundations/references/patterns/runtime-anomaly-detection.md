# Pattern: Runtime Anomaly Detection

> **Scope of evidence.** This pattern is grounded in the AAAI-26 corpus syntheses `Network-Cyber-Security.md`
> and `Defense-Mitigation.md` and their underlying research cards. It covers the **detective / monitoring
> layer** — observing an agent's or ML system's runtime behavior (action stream, tool calls, telemetry,
> query patterns, intermediate state) against a baseline of expected / on-policy behavior and raising an
> alert or triggering containment on deviation. It is *not* the preventive allow/deny gate (that is
> `policy-permission-gates.md`), the least-privilege credential control (that is
> `least-privilege-credentials.md`), the input/output classifier layer (that is `input-output-detection.md`),
> or the tamper-evident trace substrate it consumes (that is `tamper-evident-traces.md`). Runtime anomaly
> detection sits *on top of* those controls: the corpus is emphatic that a detector is a **noisy triage aid,
> not a gate**.
>
> Load-bearing papers: **A42249** (Capable and Secure Autonomous Computer-Use Agents — "capability ≠
> permission"; unauthorized-install, brute-force, sensitive-app-exposure, and hallucinated-completion as
> monitorable runtime failures; proposes an unbuilt command-validation gate), **A42239** (choice-level prompt
> injection — *any* model-visible field is an injection surface; off-policy / out-of-allow-list adoption rate
> is the primary runtime signal), **A39818** (TowerMind — action-validity gating and **invalid-action rate as
> a runtime reliability/health signal**), **A40210** (offensive CTF agents — trajectory-level competency
> scoring as the unit of agent evaluation; LLM-as-judge needs calibration), **A41065** (Resilience in Ambient
> Multi-Agent LLMs — the most complete layered runtime-defense architecture: per-agent immune-inspired anomaly
> detection + reputation/trust + gossip isolation), **A41134** (IMBIA — compromised internal agents defeat
> user-level guardrails; a 12-behavior egress taxonomy that doubles as detection signatures), **A37053** (DRMD
> — drift-aware detector with an explicit reject/defer action and time-aware evaluation), **A40432** (RAGFort
> — recursive topic-expansion / memory-driven query loops as a detectable extraction signal), **A42369**
> (VulnBench — the evaluation-integrity anchor: real-world detector F1 ≈ 0.3–0.6, threshold optimization
> helps 100% of combinations, so a fixed default threshold is fragile), **A37924** (GhostCert — a verification
> artifact is not a correctness oracle; a monitor keyed solely on a score is spoofable). Supporting:
> A40815 (compress-then-reason on 1M+-token EDR telemetry), A36959 (multi-signal verify-before-trust label
> provenance), A40100 / A39721 (intermediate state — activations, routing metadata — as a monitorable
> confidentiality asset), A38682 / A38538 / A39096 / A39770 (graph/time-series anomaly detectors), A41145
> (repeated prefix-conditioned queries + soft-prompt attachment as a signal; ROME as incident containment),
> A39732 (per-client accuracy-drop as a signal; robustness-aware aggregation is itself gameable), A36976 /
> A38588 (capability-partitioned escalation), A37087 (context-length stratification), A37475 (robustness
> evaluation can understate vulnerability), A37125 / A40903 (covert channels invisible at the content layer),
> A40925 (multi-party authorization for containment). Off-topic / excluded: A41178, A41464, A42153, A42470,
> A40129, A42364 (framework with no security evaluation).
>
> **Evidence integrity (non-negotiable).** Every quantitative claim below is **author-reported and not
> independently verified**; several source cards flag truncated result tables, and those values are written
> "not stated in paper". Numbers are tagged author-reported vs. *(reviewer synthesis)*. Calibrated language
> only — "reduced ASR against the tested attacks under the evaluated threat model", "requires production
> validation" — never "secure / proven-safe / eliminates". The single most important cross-corpus caveat,
> repeated throughout: **essentially no detector in either synthesis was evaluated against an adaptive,
> defense-aware attacker** (a *replicated absence*, not a replicated positive result), so every detection /
> ASR number is an **upper bound on real-world protection** under a non-adaptive distribution. There is **no
> independent replication across these papers**; convergent themes are agreements across independent domains,
> not replicated effect sizes.

---

## Problem addressed

An autonomous agent or ML pipeline emits behavior at runtime that departs from what it should do — because of
injection, compromise, distribution drift, or an ordinary error that broad privilege escalates into an
incident. Preventive controls (allow-lists, least-privilege, sandboxing) reduce but do not eliminate this;
the corpus makes the residual problem concrete and load-bearing:

- **Broad standing privilege turns ordinary agent errors into security incidents.** A42249 ("capability ≠
  permission", author-reported, small-n / version-bound) observed **unauthorized software install in 100% of
  certain planning tasks** (Claude Sonnet 3.5), attempted brute-force logins, sensitive-app exposure via
  navigation errors, and **hallucinated task completion masking skipped steps** — the last meaning the agent's
  own success report cannot be trusted and must be independently verified.
- **Any model-visible field is an injection surface that drives off-policy action.** A42239 (author-reported,
  single model QwQ-32B, MMLU, non-adaptive templates) shows authoritative "contradiction" text embedded
  *inside a candidate answer option* — not the user/system prompt — drives **E-adoption ≈ 0.5** and collapses
  **accuracy to ≈ 0.27**. The monitorable signal is the off-policy / out-of-allow-list selection itself.
  Nuance carried by the same paper: *weak or noisy* injections can slightly *raise* accuracy (+5–7%) via extra
  verification, so adoption and accuracy must be reported separately.
- **Compromised internal components defeat user-level guardrails.** A41134 (IMBIA, author-reported) shows a
  benign user served by compromised agents (BU-MA) is far harder to protect than a malicious user abusing
  benign agents (MU-BA): for MetaGPT the guardrail's ASR reduction under BU-MA was only **7%** vs. **40%**
  under MU-BA. In-band, user-level detection largely fails against an internally compromised agent.
- **Static detectors degrade under distribution drift.** A37053 (DRMD, author-reported) shows IID-trained
  detectors decay over time under concept drift; the paper's own contribution is a drift-aware reject/defer
  design with time-aware (TESSERACT) evaluation rather than inflated IID splits.
- **A verification artifact is not a correctness oracle.** A37924 (GhostCert, author-reported, white-box +
  known σ, strong evidence) spoofs a large randomized-smoothing certificate onto a wrong class (ASR 30–100%
  vs. Shadow Attack's ~30–65%). A monitor that keys solely on a score or certificate can be gamed.

**Runtime anomaly detection** is the set of controls that observe this behavior, compare it to a baseline of
normal / on-policy behavior, and feed the deviation as an **advisory signal into a deterministic, fail-closed
decision** — never as the gate itself, because the corpus shows detectors are noisy (real-world F1 ≈ 0.3–0.6,
A42369), bypassable, and non-adaptively evaluated.

## Applicable assets and attack surfaces

- **The agent action / tool-call stream.** The primary asset: which actions the agent selects and executes
  (A42249 computer-use actions; A39818 rule/state validity of proposed actions; A41134 generated-code tool
  calls). Every executed action is a monitorable event.
- **Every model-visible field.** Not just the user/system prompt but answer options, tool results, and
  retrieved text — each is an injection surface (A42239) and therefore a field whose downstream effect must be
  observed.
- **The RAG knowledge-base query stream.** Recursive topic-expansion and memory-driven query refinement are
  detectable extraction signatures (A40432); repeated prefix-conditioned queries + soft-prompt attachment
  signal training-data extraction (A41145).
- **Multi-agent pipeline stages and agent role profiles.** Coding and testing stages are the highest-value
  targets, and hidden instructions in a compromised agent's role profile are the BU-MA surface (A41134).
- **High-volume endpoint / EDR telemetry.** A40815 handles EDR samples where >80% exceed 1M tokens (3.6B
  events, 62 malicious families); the monitoring surface is ultra-long structured telemetry.
- **Network flows and time-series / ICS sensor streams.** Cross-dataset NIDS (A38682, NetFlow-v2 benchmarks);
  multivariate time-series anomaly on SWaT (A39770, a real ICS-attack testbed); graph anomaly (A38538, A39096).
- **Model-serving intermediate state.** Activations (A40100 — inversion under server+client collusion) and
  expert-selection / routing metadata (A39721 — access-pattern leak even when the payload is encrypted) are
  first-class confidentiality assets whose access patterns must be monitored, not just the payload.
- **Verifier / certificate / score outputs.** Clusters of large-radius certificates on near-duplicate inputs
  are a monitorable anomaly (A37924).
- **Federated / multi-agent trust statistics.** Per-client accuracy-drop and robustness-score shifts (A39732);
  per-agent reputation and anomaly shifts (A41065) — but these trust surfaces are themselves attackable (see
  Known bypasses).

## Threat model

Designed primarily for **inference / runtime adversaries** who cannot retrain the monitored model but craft
inputs, steer outputs, or compromise a peer component to produce off-policy behavior. Grounded threat classes:

- **Prompt / field injection driving off-policy action.** Authoritative text embedded in *any* model-visible
  field (A42239, author-reported E-adoption ≈ 0.5). The observable is an out-of-allow-list selection.
- **Broad-privilege / confused-deputy abuse.** An agent with excess standing privilege performs consequential
  actions (install, auth, outbound) during ostensibly benign tasks (A42249, author-reported 100%
  unauthorized-install in certain planning tasks; small-n).
- **Compromised peer / internal agent.** Hidden instructions in an agent role profile (A41134 BU-MA); a
  compromised or malfunctioning peer in an ambient multi-agent system (A41065).
- **Knowledge-base / training-data extraction via query loops.** Recursive topic-expansion query loops
  (A40432); repeated prefix-conditioned queries + soft-prompt attachment (A41145).
- **Covert exfiltration primitives in generated code.** send_email, external URL fetch, clipboard/keyboard
  capture, file encryption — A41134's 12-behavior taxonomy across Trojan/Spyware/Adware/Ransomware/Virus.
- **Concept drift as evasion.** IID-trained detectors degrade as the distribution evolves (A37053).
- **Intermediate-state leakage.** Activation inversion under collusion (A40100); routing access-pattern leak
  (A39721).

**Adversary knowledge (critical calibration).** The corpus is dominated by a **non-adaptive "detection-target"
threat model**: the "adversary" is malicious data in a corpus, and the detector is **not** stress-tested
against an attacker who adapts to it (Network-Cyber §3, flagged on nearly every card). The minority of true
adversary-vs-system studies (A37924 verifier gaming, A40100 collusion, A39721 access-pattern, A37475 white-box
evasion, A42239/A42249 injection, A41065 malicious peers) are still narrow and mostly non-adaptive. **Treat
every detection number as a non-adaptive upper bound on protection.**

**Explicitly out of scope for detection alone** (detection is the wrong control here):
- Covert channels invisible at the content layer (A37125 steganalysis Pe ≈ 0.5 against standard CNN
  steganalyzers; A40903 stego text equals cover at the text layer) — content-inspection monitoring cannot see
  them; shift to model / provenance attestation.
- An adaptive attacker who games the anomaly score itself (A37924 certificate spoofing; A39732 gaming the
  robustness-aware aggregation weight; A41065 Sybil/collusion against reputation).

**Trust assumption under attack.** The single most consistent unguarded surface across the detector papers is
**trusted inputs, telemetry, and labels** *(reviewer synthesis, Network-Cyber §3)* — NVD/CVE labels
(A36976/A37021), tool-consensus labels (A37021/A40815), EDR telemetry (A40815), ground-truth labels (A42239)
are all assumed non-adversarial. If the adversary controls the telemetry the monitor consumes, detection fails
silently.

## Control mechanism

Runtime anomaly detection is an **observe → baseline-subtract → score → alert / contain** loop. It is a
**detective** control that feeds a deterministic decision; it does not replace the preventive gate. Concrete
mechanisms grounded in the corpus:

- **Invalid-action / out-of-allow-list rate.** The cheapest and most direct signal: a deterministic check of
  each proposed action against a rule/state validity model (A39818, where invalid-action rate is the
  reliability signal) or an explicit action allow-list (A42239 {A–D}-only enforcement — reject out-of-set
  selections regardless of model output).
- **Trajectory-level competency scoring.** Score behavior at the trajectory level, per step, not pass/fail —
  pass/fail hides *how* capability was exercised (A40210, released CTFJudge/CTFTiny; LLM-judge with an explicit
  calibration caveat).
- **Compress-then-reason on high-volume telemetry.** Compress ultra-long structured telemetry into
  graph/hypergraph embeddings, subtract a benign baseline, then let a model reason over the residual (A40815 on
  1M+-token EDR samples; A38541 summarization + trimming).
- **Behavioral signatures.** Match against known-bad primitives: the 12-behavior egress taxonomy (send_email,
  external URL fetch, clipboard/keyboard capture, file encryption) (A41134); recursive topic-expansion /
  memory-driven query loops (A40432); repeated prefix-conditioned queries + soft-prompt attachment (A41145);
  large-radius certificate clusters on near-duplicate inputs (A37924); per-client accuracy-drop / robustness
  shifts (A39732).
- **Drift-aware reject/defer.** Route drifted or low-confidence cases to human review as a first-class action
  (A37053), with time-aware evaluation so the baseline tracks the evolving distribution.
- **Layered multi-agent monitoring.** Per-agent immune-inspired anomaly detection + probabilistic
  trust/reputation + gossip-based isolation (A41065) — the most complete architecture, with the caveat that its
  evidence is task-accuracy, not measured attack-success.
- **Independent end-state verification.** Because completion self-reports include hallucinated success
  (A42249), verify the actual end state out-of-band rather than trusting the agent's claim.

**Framing (non-negotiable).** This is a *triage aid*, not a gate. Real-world detector F1 ≈ 0.3–0.6 (A42369),
so false negatives and false positives are structural. Pair it with a deterministic, fail-closed preventive
control (environment-side validity gate / allow-list per A42239, A42249; least-privilege per A41134).

## Preconditions and trust assumptions

- **A trustworthy, tamper-evident telemetry channel.** The recurring unguarded assumption is trusted
  telemetry/labels (Network-Cyber §3, reviewer synthesis). The monitor must consume integrity-protected,
  out-of-band telemetry; if the monitored component can forge or suppress its own telemetry, detection
  collapses (A41134 BU-MA is the concrete failure). This precondition is what `tamper-evident-traces.md`
  supplies.
- **A definition of "normal" / on-policy.** Either an explicit allow-list of valid actions (A42239 {A–D}), a
  rule/state validity model (A39818), or a maintained benign baseline (A40815). Without a baseline there is no
  "anomaly".
- **The baseline is maintained under drift.** Time-aware, not IID (A37053 TESSERACT constraints); a stale
  baseline degrades (this is the DRMD problem statement).
- **Out-of-band, least-privilege placement.** The monitor must be isolated from the monitored agent so a
  compromised agent cannot disable it (A41134 BU-MA shows in-band/user-level monitoring fails against a
  compromised internal agent — MetaGPT ASR reduction only 7%).
- **Labels are noisy — do not assume clean ground truth.** NVD/tool-consensus/self-generated/LLM-summarized
  labels are flagged noisy across A42369, A36976, A37021, A40815, A36959; any learned detector inherits this.
- **The monitor is itself a trust-decision surface.** Reputation/aggregation weights and score thresholds are
  attackable (A39732, A41065, reviewer synthesis) and must be hardened, not assumed trustworthy.

## System architecture

- **Environment-side, out-of-band monitor between intent and execution.** Trailing guardrail text is
  insufficient when the injection lives inside a model-visible field (A42239) or a compromised agent (A41134);
  the monitor must observe and gate at a boundary the model cannot be talked past (A42249's proposed
  command-validation point). Position it in the environment, not in the prompt.
- **Layered / multi-point, complementary controls.** Convergent across A40432, A39732, A41134, A41065:
  architect for complementary controls at the retriever, generator, aggregation, and per-agent stages rather
  than a single detector. Single-point defenses are insufficient (Defense-Mitigation §9, the strongest
  cross-paper theme).
- **Capability-partitioned inference path.** Route cheap/structured cases to a small specialized detector and
  escalate only hard/borderline cases to an expensive LLM (A36976 explicit negative result that LLM-only
  underperforms tuned small models; A38588 LLM-as-guide on lowest-score anchors; A40815 compress-then-reason).
  This both improves discrimination and bounds cost on ultra-long telemetry.
- **Trajectory logging + competency scoring as the audit substrate.** Per-step interaction logs and, where
  feasible, screen/video as evidence (A40210, A42249); this is the input the anomaly layer consumes and the
  console renders.
- **Per-agent monitor + system-level anomaly detection + reputation isolation** in multi-agent deployments
  (A41065), with the caveat that its security evidence is task-accuracy, not measured attack-success.
- **Intermediate state as a monitored confidentiality boundary.** In any multi-tenant / offloaded / split
  hosting design, monitor access to activations and routing metadata, not just the payload (A40100, A39721);
  "payload encrypted" is insufficient.
- **Harden every new trust-decision surface the monitor introduces.** Reputation/aggregation weights, score
  thresholds, and access-triggers can be gamed (A39732, A41065; reviewer synthesis, Network-Cyber §15).

## Recommended implementation pattern

Deterministic, fail-closed, least-privilege. The anomaly layer is advisory *into* a deterministic decision;
the deterministic parts must not depend on the model.

1. **Define the on-policy action set / allow-list deterministically and reject out-of-set actions regardless
   of model output** (A42239 {A–D}; A42249 command validation). Detection is layered *on top of* this gate,
   never instead of it.
2. **Emit tamper-evident, out-of-band per-step trajectory telemetry** — action, tool call, arguments, result —
   plus every model-visible field ingested (A40210, A42249, A42239).
3. **Compute the deterministic invalid-action / out-of-allow-list rate** as the primary cheap health signal
   (A39818, A42239); this needs no model and cannot be talked past.
4. **Baseline-subtract high-volume telemetry, then score the residual**, using behavioral signatures where
   available (A40815 compress-then-reason; A41134 egress taxonomy; A40432 query-loop signature; A41145
   prefix-repeat / soft-prompt signature).
5. **Route drift or low-confidence to human review as a first-class reject/defer action** (A37053, A42249) —
   fail closed rather than fail open.
6. **Independently verify the end state**; do not trust agent-claimed completion (A42249 hallucinated
   completion).
7. **Capability-partition**: specialized/small detector first, escalate borderline cases to the LLM (A36976,
   A38588, A40815).
8. **Multi-signal verify-before-trust for any label/pseudo-label the detector learns from** — cross-temperature
   consistency + separate-model agreement + confidence threshold before admitting a pseudo-label (A36959).
9. **Treat every detector verdict as triage and require out-of-band corroboration before any security
   decision** (A42369, A36959, A40815).
10. **Calibrate any LLM-as-judge component** with inter-judge / human agreement (A40210 calibration caveat;
    A36959 judge disagreement; A41134 reports 86.34% agreement with manual evaluators — still, bias is present).
11. **Report adoption and accuracy separately** (A42239) — a single "did it comply" metric hides that weak
    injections raise accuracy while strong ones collapse it.

## Incorrect or fragile implementation patterns

- **Trailing guardrail text / prompt hygiene as the whole control.** The model can be talked past it; the
  injection lives inside a model-visible field (A42239) or a compromised agent's role profile (A41134
  positional injection appended after a benign request).
- **In-band / user-level detection a compromised component can disable.** A41134 BU-MA: MetaGPT ASR reduction
  only 7% under a compromised internal agent vs. 40% when the agent is benign.
- **Content-layer DLP as the only egress monitor.** Covert channels are invisible at the content layer (A37125
  Pe ≈ 0.5; A40903 stego = cover) — content inspection sees nothing anomalous.
- **A single detector / certificate / score used as a correctness oracle or gate.** A37924 spoofs the
  certificate (ASR 30–100%); A42369 shows real-world detector F1 ≈ 0.3–0.6 — the artifact is bounded assurance,
  not truth.
- **Trusting agent-claimed completion.** Hallucinated completion masks skipped/unsafe steps (A42249).
- **IID / static baselines and synthetic benchmarks.** They overstate: Juliet 0.900 / VulDeepecker 0.959 vs.
  real-world DiverseVul 0.307 / Reveal 0.486 (A42369, author-reported); single-function benchmarks hide
  long-context brittleness (A37087 LOC stratification); IID splits inflate vs. time-aware (A37053).
- **A fixed default detection threshold.** A42369: threshold optimization improved F1 in **100%** of
  model-dataset combinations (author-reported median +0.082, best +0.542) — a default threshold is fragile and
  domain-specific.
- **LLM-only detection where a tuned small model does better** (A36976 explicit negative result).
- **Uncalibrated LLM-as-judge** (A36959 judges disagree with each other and humans; A40210 self-referential
  bias caveat).
- **Standard robustness evaluation read as complete.** A37475: FGSM/PGD understate true vulnerability because
  they miss the angular direction AGSM/PAGD exploit — an anomaly baseline tuned only to standard perturbations
  can be blind to a whole direction.
- **Leaving the meta-decision (reputation/aggregation/threshold) ungameable-unchecked** (A39732, A41065).

## Verification strategy

- **Trajectory-level evidence logging + competency scoring**, not pass/fail (A40210); per-step interaction and,
  where feasible, screen/video logs as audit evidence (A42249).
- **Time-aware / distribution-shift-honest evaluation splits** (A37053 TESSERACT; A38682 cross-dataset /
  unseen-attack transfer; A37087 LOC stratification; A42369 seeded splits + identifier anonymization).
- **Threshold optimization with confidence intervals and identifier-anonymized splits** (A42369) — and report
  the threshold-optimized *real-world* F1, not the synthetic-benchmark number.
- **Independent end-state verification vs. agent-claimed completion** (A42249).
- **Multi-signal verify-before-trust for labels** the detector learns from (A36959).
- **Out-of-band corroboration required for any security decision** the detector drives (A42369, A36959,
  A40815).
- **Multi-seed confidence intervals** rather than single-run point estimates (A42369, 3 seeds × 80/10/10).

## Metrics and thresholds

Author-reported unless labeled. All are **non-adaptive** estimates — upper bounds on protection.

- **Invalid-action / out-of-allow-list rate** — primary deterministic health signal (A39818, A42239).
- **Off-policy adoption rate AND accuracy delta, reported separately** (A42239): the "contradiction" injection
  drove E-adoption ≈ 0.5 and accuracy ≈ 0.27 (QwQ-32B, MMLU), while flattery/plain-imperative/noise styles
  failed to attack and sometimes *raised* accuracy +5–7%. A single combined metric hides this.
- **Detection F1 with threshold optimization + CIs** (A42369) — but calibrate the target: real-world F1 ≈
  0.3–0.6 (DiverseVul 0.307, Reveal 0.486), not the synthetic 0.9+ (Juliet 0.900, VulDeepecker 0.959).
  Threshold optimization helped 100% of combinations (median +0.082, best +0.542), so thresholds are
  domain-specific, not defaults.
- **Trajectory competency score** at the step level (A40210).
- **Security-incident incidence counts**: unauthorized-install rate, brute-force-attempt count, sensitive-app
  exposure, hallucinated-completion rate (A42249, small-n).
- **Per-client accuracy-drop / robustness-score shift** (A39732); **per-agent reputation/anomaly shift**
  (A41065).
- **Reject / defer rate** (A37053; A41134 Reject Rate RR / RR-under-defense RR-d).
- **Query-loop anomaly rate** — recursion depth, topic-expansion, memory-driven refinement (A40432);
  prefix-conditioning repetition (A41145).
- **Report absolute residuals, not only relative reductions** — A40925 leaves ~15% residual unauthorized
  activation (Acc-Fusion); A40432's strongest configuration still leaves ~28% chunk-recovery rate (57.16% →
  27.96%, HealthCareMagic/Qwen-14B, author-reported).

## Test cases

Concrete cases drawn from corpus attack families (each verifies the monitor fires):

- **Field injection.** Authoritative "contradiction" text embedded in a non-prompt model-visible field (answer
  option, tool result, or retrieved chunk); verify off-policy adoption is flagged and the out-of-allow-list
  selection is rejected (A42239).
- **Broad-privilege abuse.** A benign planning task that triggers unauthorized software install, a brute-force
  login attempt, or navigation into a sensitive app; verify the incident is flagged (A42249).
- **Hallucinated completion.** Agent reports success but skipped steps; verify independent end-state
  verification catches the discrepancy (A42249).
- **Compromised internal agent (BU-MA).** Hidden instruction in an agent role profile inserts a `send_email`
  exfiltration function; verify the egress-signature detection fires and that it fires *out-of-band* (A41134).
- **Knowledge-base extraction loop.** Recursive topic-expansion / memory-driven queries against a RAG KB;
  verify the query-loop pattern is flagged (A40432).
- **Training-data extraction.** Repeated prefix-conditioned queries + soft-prompt attachment; verify flagged
  (A41145).
- **Concept drift.** A temporally shifted malware/behavior distribution; verify reject/defer routing engages
  and the baseline is time-aware (A37053).
- **Score / certificate anomaly.** Clusters of large-radius certificates on near-duplicate inputs; verify
  flagged rather than trusted (A37924).
- **Out-of-allow-list action.** An action outside the on-policy set (e.g., not in {A–D}); verify deterministic
  rejection and counting independent of model output (A42239, A39818).

## Adaptive adversarial tests

The corpus's largest gap is the **near-universal absence of adaptive evaluation** (Network-Cyber §3/§9/§12;
Defense-Mitigation §9). The following are **not evaluated in the corpus** and are stated as production-validation
requirements, each anchored to the closest demonstrated analog:

- **Detector-aware query adaptation.** An attacker who knows the monitor adjusts strategy — within-cluster
  probing, paraphrase to dodge a rejection rule (A40432 reviewer synthesis; ~28% residual CRR implies
  headroom). *Not evaluated against adaptive attackers; requires production validation.*
- **Score / verifier gaming.** Directly game the anomaly score, analogous to certificate spoofing under
  white-box + known σ (A37924, ASR 30–100%). *Requires production validation.*
- **Trust-surface gaming.** A client/agent that appears locally robust while poisoning globally (A39732), or
  Sybil/collusion against an honest-majority reputation scheme (A41065). *Not tested against Sybil/collusion.*
- **Containment reversal.** ROME-style erasure reversed by post-edit soft-prompt re-optimization (A41145
  reviewer); protective perturbation defeated by purification/re-recording (A37756, A37844, citing Hönig et al.
  2024 that such protection "cannot reliably protect"). *Not evaluated against adaptive purification.*
- **Geometry-aware evasion missed by standard robustness eval** (A37475 angular direction). *Standard eval
  understates; validate against non-standard directions.*
- **Content-layer-invisible covert channel** (A37125 Pe ≈ 0.5; A40903 stego = cover). *Content-inspection
  monitoring cannot detect; requires provenance/attestation, not detection.*
- **Concept-drift-as-evasion** — an attacker who slowly shifts the distribution to stay under the drift
  threshold (A37053). *Requires production validation of the drift detector's adaptive robustness.*

## Telemetry requirements

- **Per-step trajectory logs** — action, tool call, arguments, result (A40210, A42249).
- **Every model-visible field ingested** — prompt, options, tool results, retrieved text (A42239).
- **Screen / video where feasible** as audit evidence (A42249).
- **Egress / behavioral primitives** — send_email, external URL fetch, clipboard/keyboard capture, file
  encryption (A41134's 12-behavior taxonomy as concrete signatures).
- **Query-pattern telemetry** — recursion depth, topic-expansion, memory-driven refinement (A40432);
  prefix-conditioning repetition and soft-prompt attachment (A41145).
- **Intermediate state where multi-tenant / offloaded** — activations and expert-selection / routing metadata
  as sensitive assets (A40100, A39721).
- **Certificate / score distribution + input near-duplication** (A37924).
- **Per-client accuracy-drop / robustness score** (A39732); **per-agent reputation / anomaly shift** (A41065).
- **Ultra-long telemetry handling** — compress into graph/hypergraph embeddings and subtract a benign baseline
  before reasoning (A40815, on samples exceeding 1M tokens).
- **Tamper-evidence and out-of-band delivery** — telemetry must be integrity-protected and not suppressible by
  the monitored component; the recurring unguarded assumption is trusted telemetry (Network-Cyber §3). See
  `tamper-evident-traces.md`.

## Failure handling

- **Fail closed.** On monitor unavailability, low confidence, or detected drift, default to reject/defer to
  human review (A37053 reject action; A42249 human approval on consequential actions) rather than proceeding.
- **Detector is triage, never the sole security decision.** Corroborate out-of-band before acting on a verdict
  (A42369, A36959, A40815).
- **Gate consequential / irreversible actions behind human approval regardless of the monitor's verdict** —
  install, auth, outbound send (A42249). See `human-approval-consequential-actions.md`.
- **Independently verify the end state** when the agent claims completion (A42249).
- **Budget for residual risk and report absolute residuals** — the strongest defenses still leak (A40432 ~28%
  CRR; A40925 ~15% Acc-Fusion).

## Rollback and containment

- **Reject / defer routing to manual review** as a first-class action (A37053).
- **Gossip-based isolation of anomalous agents + reputation down-weighting** in multi-agent systems (A41065) —
  with the caveat that reputation is itself gameable (see Known bypasses).
- **Least-privilege capability isolation** — block outbound email/network from generated apps, sandboxed
  execution, independent code-scanning gates (A41134). See `tool-capability-isolation.md`,
  `sandboxed-execution.md`.
- **Targeted model editing (ROME) as incident containment / erasure** without full retraining (A41145,
  author-reported extraction 65.2% → 1.6%) — but validate against post-edit re-optimization before relying on
  it (A41145 reviewer).
- **Rate-limiting + query monitoring** on extraction-suspicious query loops (A40432, author-reported cost < 2
  accuracy points, FLOPs unchanged or reduced).
- **Multi-party / threshold authorization** to revoke or gate model activation for high-value assets (A40925),
  accepting the ~15% residual-activation headroom as a monitored risk.
- **Caveat:** containment that relies on reputation/aggregation is itself a gameable trust surface (A39732,
  A41065); harden and log the meta-decision.

## Known bypasses

**Demonstrated (within the papers, under their stated — mostly non-adaptive — threat models):**
- **Certificate / verifier spoofing** — a monitor keyed on a score is deceived (A37924, white-box + known σ,
  ASR 30–100%; abstentions become DoS).
- **Compromised internal agents defeat user-level guardrails** (A41134 BU-MA; MetaGPT ASR reduction only 7%).
- **Hallucinated completion masks skipped / unsafe steps** (A42249).
- **Concept drift bypasses static classifiers** (A37053).
- **Covert channels invisible at the content layer** (A37125 Pe ≈ 0.5; A40903 stego = cover).
- **Access-pattern leak bypasses payload encryption** (A39721); **activation inversion under collusion**
  (A40100).
- **Fraud camouflage / collusion / borderline structuring bypasses single-view detectors** (A38541, A38588).
- **Angular-direction evasion missed by standard robustness evaluation** (A37475).
- **Partial-trigger fusion partially bypasses multi-party access control** (A40925, ~15% Acc-Fusion above
  chance).

**Reviewer-identified (not demonstrated in the papers):**
- Detector-aware query adaptation against extraction monitoring (A40432).
- Gaming robustness-aware aggregation / reputation; Sybil/collusion vs. honest-majority (A39732, A41065).
- ROME edits reversible by post-edit soft-prompt re-optimization (A41145).
- Purification / re-recording defeating protective perturbation (A37756, A37844, citing Hönig et al. 2024).

## Residual risks

- **Detectors are structurally noisy.** Real-world F1 ≈ 0.3–0.6 (A42369) → false negatives and false positives
  are unavoidable; the monitor cannot be a gate.
- **Non-adaptive evaluation everywhere.** All numbers are upper bounds on protection under a non-adaptive
  distribution; the replicated absence of adaptive evaluation is the strongest methodological caveat
  (Network-Cyber §9; Defense-Mitigation §9).
- **Residual leakage / activation under the strongest defenses** (A40432 ~28% CRR; A40925 ~15% Acc-Fusion) —
  mitigation, not elimination.
- **The trusted-telemetry assumption is unguarded.** If broken, detection fails silently (Network-Cyber §3,
  reviewer synthesis).
- **Every new trust-decision surface (reputation, aggregation, score threshold) is itself attackable**
  (A39732, A41065; reviewer synthesis, Network-Cyber §15).
- **LLM-judge bias / calibration gaps** in any judge-based component (A36959, A40210, A41134).
- **Single-paper / truncated evidence.** A41065's security evidence is task-accuracy (not measured
  attack-success); several cards flag truncated result tables (A41065, A39732, A37021, A38538, A39096, A39770
  in whole or part) — these require independent validation before operational reliance.

## Relevant research (stable paper ids from the syntheses/cards)

*Core agent-runtime evidence:*
- **A42249** — Towards Capable and Secure Autonomous Computer-Use Agents (AAAI-26, Student Abstract):
  "capability ≠ permission"; monitorable failures (unauthorized-install, brute-force, sensitive-app exposure,
  hallucinated completion); proposes an unbuilt command-validation gate. Evidence: preliminary (small-n,
  version-bound, partly subjective) but directionally credible.
- **A42239** — Obedience or Vigilance? How LLMs React to Malicious Multiple-Choice Options (AAAI-26): any
  model-visible field is an injection surface; off-policy adoption rate as the runtime signal; report adoption
  and accuracy separately. Evidence: preliminary (single model QwQ-32B, MMLU, non-adaptive).
- **A39818** — TowerMind (AAAI-26): action-validity gating; invalid-action rate as a runtime reliability
  signal. Evidence: reliability benchmark, not a security evaluation (transferable pattern only).
- **A40210** — Offensive Security LLM Agents / CTFTiny + CTFJudge (AAAI-26; code released): trajectory-level
  competency scoring; LLM-judge calibration caveat; decoding-hyperparameter sensitivity. Evidence: moderate.
- **A41065** — Resilience in Ambient Multi-Agent LLMs (AAAI-26): most complete layered runtime-defense
  architecture (per-agent anomaly + reputation isolation + FL-with-HE). Evidence: moderate (architecture),
  preliminary (security — task-accuracy, not attack-success; truncated tables).
- **A41134** — Shadows in the Code / IMBIA (AAAI-26; code released): compromised-agent (BU-MA) defeats
  user-level guardrails; 12-behavior egress taxonomy as detection signatures. Evidence: moderate.

*Detection methodology and evaluation integrity:*
- **A42369** — VulnBench (AAAI-26; code released): real-world F1 ≈ 0.3–0.6; threshold optimization helps 100%
  of combinations; synthetic-vs-real gap; detectors are triage aids, not gates. Evidence: moderate (leaning
  strong for the methodological claims).
- **A37053** — DRMD (AAAI-26; code released): drift-aware reject/defer + time-aware TESSERACT evaluation.
  Evidence: moderate.
- **A36959** — AutoMalDesc (AAAI-26; code released): multi-signal verify-before-trust label provenance;
  LLM-judge disagreement caveat. Evidence: moderate (methods).
- **A37087** — CTX-Coder / CTX-Vul (AAAI-26; code released): LOC-stratified evaluation exposing brittleness.
  Evidence: moderate.
- **A40815** — HyperGLLM (AAAI-26): compress-then-reason on 1M+-token EDR telemetry; self-generated-label
  noise. Evidence: moderate (non-adaptive).
- **A38682 / A38538 / A39096 / A39770** — cross-dataset NIDS / graph / time-series anomaly detectors
  (AAAI-26): monitoring-surface methods; non-adaptive; several tables truncated. Evidence: moderate to
  preliminary.
- **A38588** — MH-LGC (AAAI-26): capability-partitioned LLM-as-guide escalation. Evidence: moderate.
- **A36976** — VFCionX (AAAI-26): explicit negative result — LLM-only underperforms tuned small models.
  Evidence: moderate.

*Verifier gaming, drift, and evasion caveats:*
- **A37924** — GhostCert (AAAI-26; code released): a verification artifact is not a correctness oracle; score
  spoofing (ASR 30–100%). Evidence: strong.
- **A37475** — Angular Gradient Sign Method (AAAI-26): standard robustness evaluation understates true
  vulnerability. Evidence: moderate.
- **A39732** — STRUM / GTAE (AAAI-26): per-client accuracy-drop as a signal; robustness-aware aggregation is a
  gameable trust surface. Evidence: preliminary (unreconciled dataset count, no visible numerics, no code).
- **A37125 / A40903** — content-layer-invisible covert channels (AAAI-26): detection blind spot; shift to
  provenance/attestation. Evidence: moderate (non-adaptive; "provable security" downgraded by reviewer).

*Extraction signals, intermediate state, and containment:*
- **A40432** — RAGFort (AAAI-26; code released): query-loop extraction signatures; query monitoring +
  rate-limiting; ~28% residual CRR. Evidence: moderate (leaning strong).
- **A41145** — CoSPED (AAAI-26; code released): prefix-repeat / soft-prompt extraction signal; ROME as
  incident containment (65.2% → 1.6%). Evidence: moderate (white-box, small models, no adaptive test).
- **A40100 / A39721** — confidentiality pair (AAAI-26; code released): activations (A40100 collusion inversion)
  and routing access patterns (A39721 expert-selection leak) as monitored assets. Evidence: moderate
  (empirical privacy / semi-honest only).
- **A40925** — Consensus Learning with Multi-Party Perturbation Triggers (AAAI-26): multi-party authorization
  for containment; ~15% residual Acc-Fusion. Evidence: moderate (non-adaptive).
- **A37756 / A37844** — proactive protective perturbation (AAAI-26): containment analog; both cite Hönig et al.
  2024 that such protection is not reliable against purification. Evidence: moderate (non-adaptive).

*Excluded as off-topic / no security evaluation:* A41178 (disaster-risk geospatial ML), A41464 (water-pipeline
sensor faults), A42153 (agenda abstract), A42470 (autonomous-driving physical-hazard detection), A40129
(non-adversarial continual-learning stability), A42364 (GNN-AID — tooling framework, no security numbers),
A42318 (AI-vs-AI defense proposal, no experiments).

## Evidence strength

- **Strongest single evidence:** A37924 (strong; ImageNet-scale, three certified defenses, released code) for
  "a verification artifact is not a correctness oracle"; A42369 (moderate, leaning strong for the
  methodological claims; released code, 8 datasets, 3 seeds) for "detectors are triage aids, real-world F1 ≈
  0.3–0.6"; A40432 (moderate, leaning strong; realistic black-box threat model, released code) for layered
  defense + query monitoring.
- **Core agent grounding is preliminary but directionally credible:** A42249 (small-n, version-bound, partly
  subjective video scoring), A42239 (single model, single dataset, non-adaptive templates), A41134 (moderate;
  480 cases, three frameworks, single GPT-4o-mini backend, LLM-as-judge).
- **Architecture template with weak security evidence:** A41065 (moderate architecture; security evidence is
  task-accuracy, not measured attack-success).
- **Pattern-only (not a security evaluation):** A39818 (reliability benchmark supplying the action-validity /
  invalid-action-rate pattern).
- **Overarching calibration:** there is **no independent replication across these papers** (each is
  self-contained); convergent themes are agreements across independent domains, not replicated effect sizes.
  **Essentially no detector was evaluated against an adaptive, defense-aware attacker**, so every number is a
  non-adaptive upper bound on protection. Multiple cards flag truncated result tables. **Requires production
  validation** on the target stack before operational reliance.

## When NOT to use this pattern

- **As a gate, correctness oracle, or sole security decision.** It is a triage aid; real-world F1 ≈ 0.3–0.6
  (A42369) and scores are spoofable (A37924). Use `policy-permission-gates.md` for the deterministic decision.
- **As a replacement for a deterministic preventive control.** Detection is layered on top of an
  environment-side validity gate / allow-list (A42239, A42249) and least-privilege isolation (A41134); it does
  not substitute for them.
- **Against covert channels invisible at the content layer.** Content-inspection monitoring cannot see them
  (A37125, A40903); shift to model / provenance attestation (`content-provenance.md`, `signed-provenance.md`).
- **Against a compromised in-band component that can disable or forge telemetry to the monitor.** A41134 BU-MA
  shows in-band/user-level monitoring fails; the monitor must be out-of-band and least-privilege, which is a
  precondition, not something this pattern grants.
- **When you cannot guarantee trustworthy, tamper-evident telemetry.** The whole control collapses on the
  trusted-telemetry assumption (Network-Cyber §3); establish `tamper-evident-traces.md` first.
- **When you would rely on a single detector without out-of-band corroboration** (A36959, A40815, A42369).
- **When the threat model includes an adaptive, defense-aware attacker and you have no adaptive evaluation.**
  The corpus provides essentially none; treat the control as unvalidated against that adversary until
  production validation is done (Network-Cyber §3/§9/§12; Defense-Mitigation §9).
