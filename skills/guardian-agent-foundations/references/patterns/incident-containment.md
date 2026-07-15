# Pattern: Incident Containment

> **Scope of evidence.** This pattern is grounded in the AAAI-26 corpus syntheses `Defense-Mitigation.md` and
> `Network-Cyber-Security.md` and their underlying research cards. It covers the **response / blast-radius
> layer** — what a system does *once an incident is detected or suspected*: deterministically halt or reject
> the offending action, isolate / quarantine the affected agent or component, revoke standing capability or
> model activation, rate-limit an abusive query loop, perform targeted erasure of leaked knowledge, and roll
> back to a safe state — all while preserving tamper-evident evidence for forensics. It is **not** the
> detection / monitoring layer that raises the alarm (that is `runtime-anomaly-detection.md` and
> `input-output-detection.md`), the preventive allow/deny gate (that is `policy-permission-gates.md`), the
> static network topology that pre-limits reach (that is `network-segmentation.md`), the standing-credential
> least-privilege configuration (that is `least-privilege-credentials.md`), or the audit substrate the
> response consumes (that is `tamper-evident-traces.md`). Incident containment sits *downstream* of detection
> and *on top of* isolation: it assumes an alert already exists and asks how to bound the damage
> deterministically. The corpus's single most explicit anchor is A41145, whose own card frames ROME model
> editing as "an incident-containment/erasure path without full retraining."
>
> Load-bearing papers: **A41145** (CoSPED — ROME targeted model editing as post-incident knowledge erasure,
> author-reported extraction 65.2% → 1.6%, white-box, small models, **reversible by defense-aware
> re-optimization**), **A41134** (IMBIA / Shadows in the Code — Adv-IMBIA guardrails that **refuse /
> replace / halt** on violation; least-privilege capability isolation and egress control as pre-containment;
> the **MU-BA vs. BU-MA asymmetry** — user-level containment largely fails against a compromised internal
> agent), **A42249** (Capable and Secure Autonomous Computer-Use Agents — "capability ≠ permission";
> human approval on consequential/irreversible actions; **hallucinated completion** means containment success
> cannot be self-reported), **A37053** (DRMD — explicit **reject / defer** as a first-class containment
> action; time-aware evaluation), **A40925** (Consensus Learning — multi-party / threshold authorization bound
> to model execution so no single party or thief can activate it; residual ~15% Acc-Fusion), **A41065**
> (Resilience in Ambient Multi-Agent LLMs — **gossip-based reputation isolation** of anomalous agents; "without
> containment [failures] cascade"; honest-majority / Sybil caveats), **A40432** (RAGFort — **rate-limiting +
> query monitoring** to contain extraction; residual ~28% CRR), **A37924** (GhostCert — a verification
> artifact is not a correctness oracle, so a containment *trigger* keyed solely on a score is spoofable and
> abstention becomes DoS). Supporting: A42239 (any model-visible field is an injection surface; environment-
> side out-of-set rejection), A42369 (VulnBench — detectors are triage aids, real-world F1 ≈ 0.3–0.6, so a
> trigger will over- and under-contain), A40210 (trajectory-level evidence as the forensic-scoping substrate),
> A37756 / A37844 (proactive protective perturbation as a containment analog, defeated by purification —
> Hönig et al. 2024), A37125 / A40903 (covert channels invisible at the content layer — content-DLP
> containment fails), A40100 / A39721 (intermediate state — activations, routing metadata — must be contained,
> not just the payload), A39732 (per-client robustness signal; robustness-aware aggregation is itself a
> gameable containment-trust surface). Off-topic / excluded: A41178, A41464, A42153, A42470 (physical-hazard,
> not adversary), A40129 (non-adversarial continual-learning stability), A42364 (GNN-AID — tooling framework,
> no security evaluation), A42318 (AI-vs-AI defense proposal, no experiments).
>
> **Evidence integrity (non-negotiable).** Every quantitative claim below is **author-reported and not
> independently verified**; several source cards flag truncated result tables, and those values are written
> "not stated in paper." Numbers are tagged author-reported vs. *(reviewer synthesis)*. **No paper in either
> synthesis measures a containment-specific operational metric** — time-to-contain, mean-time-to-recovery,
> measured blast-radius reduction, or rollback latency are all "not stated in paper"; the corpus supplies
> *mechanisms* and *residual-leakage* numbers, not response-time evidence. Calibrated language only —
> "reduced ASR against the tested attacks under the evaluated threat model," "requires production validation" —
> never "secure / proven-safe / eliminates." The single most important cross-corpus caveat, repeated
> throughout: **essentially no defense in either synthesis was evaluated against an adaptive, defense-aware
> attacker** (a *replicated absence*, not a replicated positive result), so every containment-effectiveness
> number is an **upper bound on real-world protection** under a non-adaptive distribution. There is **no
> independent replication across these papers**; convergent themes are agreements across independent domains,
> not replicated effect sizes.

---

## Problem addressed

Preventive controls and detectors reduce but never eliminate incidents: injection lands, a peer agent is
compromised, standing privilege turns an ordinary error into a security event, or extraction succeeds. Once
that happens, the operative question is no longer *did we stop it* but *how do we bound the damage, stop
propagation, and recover to a safe state — deterministically, without trusting the compromised component.*
The corpus makes the residual problem concrete and load-bearing:

- **Broad standing privilege converts an ordinary agent error into an incident.** A42249 ("capability ≠
  permission," author-reported, small-n / version-bound) observed **unauthorized software install in 100% of
  certain planning tasks** (Claude Sonnet 3.5), attempted brute-force logins, and sensitive-app exposure via
  navigation errors during ostensibly benign tasks. If capability is not pre-contained by least privilege, the
  blast radius of any single misstep is the full standing-privilege set.
- **Uncontained failures cascade through a multi-agent system.** A41065 states directly that danger/pathogen
  signals, "without containment[,] cascade through agent interactions" (and, in the federated layer, as client
  drift). Containment is what stops a single compromised agent from becoming a system-wide compromise.
- **Compromised internal components defeat user-level containment.** A41134 (IMBIA, author-reported) shows a
  benign user served by compromised agents (BU-MA) is far harder to contain than a malicious user abusing
  benign agents (MU-BA): for MetaGPT the Adv-IMBIA guardrail's ASR reduction under BU-MA was only **7%** vs.
  **40%** under MU-BA (ChatDev 45% vs. 73%; AgentVerse 42% vs. 49%). In-band, user-level containment largely
  fails against an internally compromised agent — containment must be out-of-band and least-privilege.
- **Containment success cannot be self-reported.** A42249 observed **hallucinated task completion masking
  skipped steps** — the agent claims it recovered / stopped when it did not. Any "incident contained" signal
  from the affected component is untrustworthy; the end state must be independently verified.
- **A containment trigger keyed on a score is spoofable.** A37924 (GhostCert, author-reported, white-box +
  known σ, strong evidence) spoofs a large randomized-smoothing certificate onto a wrong class (ASR 30–100%
  vs. Shadow Attack's ~30–65%), and its abstentions are **recorded as denial-of-service** — i.e., a
  score-driven containment reflex can both *miss* a real incident and *be weaponized into a DoS* by forcing
  abstentions.

**Incident containment** is the set of deterministic, fail-closed, least-privilege response controls that,
given an alert, halt the action, isolate the component, revoke the capability, rate-limit or erase the abused
asset, and roll back to a safe state — reducing blast radius while acknowledging that residual leakage and
already-exfiltrated data are frequently irreversible.

## Applicable assets and attack surfaces

- **The agent action / tool-call stream at the moment of execution.** The primary containment point: the
  consequential action about to run (A42249 computer-use actions such as install / auth / outbound send;
  A42239 the selected option/action). Containment intercepts here, before the irreversible step.
- **Standing capability and credential scope.** The blast radius of any incident equals the agent's standing
  privilege (A42249 "capability ≠ permission"); the tool-calling capabilities of generated code — outbound
  email/network, clipboard/keyboard, file encryption (A41134's 12-behavior egress taxonomy).
- **Multi-agent pipeline peers and role profiles.** A compromised or malfunctioning peer agent (A41065) and
  hidden instructions in a compromised agent's role profile (A41134 BU-MA) are the propagation surface that
  isolation must cut.
- **The model's memorized / leaked knowledge.** Memorized suffixes recoverable via soft-prompt extraction
  (A41145) — the asset targeted-erasure (ROME) contains; a proprietary RAG knowledge base being reconstructed
  by query loops (A40432).
- **Model activation itself, for high-value assets.** Whether the model produces meaningful predictions at all
  can be bound to multi-party consent (A40925), so a stolen model or a single compromised party cannot
  activate it.
- **The query / request channel.** Recursive topic-expansion and memory-driven query refinement (A40432) and
  repeated prefix-conditioned queries + soft-prompt attachment (A41145) are the abusive loops that rate-limiting
  contains.
- **Model-serving intermediate state.** Activations (A40100 — inversion under server+client collusion) and
  expert-selection / routing metadata (A39721 — access-pattern leak even when the payload is encrypted) are
  first-class confidentiality assets whose leak must be contained, not just the payload.
- **The egress boundary.** Covert channels are invisible at the content layer (A37125, A40903), so containment
  of exfiltration must act at the egress/provenance boundary, not via content inspection.
- **The tamper-evident trace.** The evidence substrate that scopes the incident (A40210 trajectory-level
  logging, A42249 per-step + video) — an asset the response must preserve, not destroy.

## Threat model

Designed primarily for the moment **after** an inference/runtime adversary has succeeded (or is suspected of
succeeding). Grounded incident classes the pattern must contain:

- **Injection-driven off-policy action.** Authoritative text in *any* model-visible field — answer option,
  tool result, retrieved text, not just the prompt — drives a consequential action (A42239, author-reported
  E-adoption ≈ 0.5, accuracy ≈ 0.27, QwQ-32B / MMLU). Containment = deterministic rejection of the out-of-set
  action regardless of model output.
- **Broad-privilege / confused-deputy abuse.** An over-privileged agent performs install / auth / outbound
  during a benign task (A42249, author-reported 100% unauthorized-install in certain planning tasks; small-n).
  Containment = least-privilege pre-containment plus human approval on the consequential step.
- **Compromised / malicious peer agent.** Hidden instructions in a role profile (A41134 BU-MA); a compromised
  or malfunctioning peer in an ambient multi-agent system (A41065). Containment = out-of-band isolation /
  reputation down-weighting, because in-band user-level containment fails (A41134 MetaGPT 7%).
- **Knowledge-base / training-data extraction in progress.** Recursive query loops (A40432); prefix-repeat +
  soft-prompt attachment (A41145). Containment = rate-limit, query monitoring, and targeted erasure.
- **Model theft / unauthorized activation.** Stolen weights or one party's leaked secret (A40925). Containment
  = multi-party authorization bound to activation.
- **Covert exfiltration.** send_email, external URL fetch, clipboard/keyboard capture, file encryption
  (A41134's taxonomy); content-layer-invisible covert channels (A37125, A40903). Containment acts at egress /
  capability, not content.
- **Intermediate-state leakage.** Activation inversion under collusion (A40100); routing access-pattern leak
  (A39721).

**Adversary knowledge (critical calibration).** The corpus is dominated by a **non-adaptive** threat model;
the minority of true adversary-vs-system studies (A37924 verifier gaming, A40925 partial-trigger fusion,
A41065 malicious peers, A40100 collusion, A39721 access-pattern, A42239/A42249 injection) are still narrow and
mostly non-adaptive. Critically for *containment*, the two most relevant containment mechanisms are explicitly
**not** tested against an attacker who adapts to them: A41145's ROME defense is "evaluated against the same
(non-adaptive) attack; a defense-aware attacker could re-tune the soft prompt post-edit — robustness not
established," and A41065's reputation isolation has "no adaptive adversary that … Sybil-floods gossip to bias
reputation." **Treat every containment-effectiveness number as a non-adaptive upper bound.**

**Trust assumption under attack.** The single most consistent unguarded surface is **trusted inputs,
telemetry, and labels** *(reviewer synthesis, Network-Cyber §3)*. If the adversary controls the telemetry the
response engine consumes, containment triggers on forged evidence or never triggers at all — and A41134 BU-MA
is the concrete demonstration that a compromised in-band component can defeat in-band containment.

## Control mechanism

Incident containment is a deterministic **halt → isolate → revoke → erase/rate-limit → roll back → verify**
response, driven by an alert but never *depending on the compromised component*. Concrete mechanisms grounded
in the corpus:

- **Halt / reject-defer as a first-class action.** A37053 (DRMD) routes drift / low-confidence to an explicit
  `reject` action for manual review; A41134's Adv-IMBIA instructs agents to "refuse to generate violating
  code, and delete/replace/**halt** on detected violations"; A42249 gates consequential actions behind human
  approval. Fail closed: stop, do not proceed.
- **Least-privilege pre-containment + capability isolation.** A41134 argues for "least-privilege capability
  isolation for tool-calling code (e.g., blocking outbound email/network from generated apps)," sandboxed
  execution, and egress controls — so the blast radius is bounded *before* the incident (A42249 "capability ≠
  permission"). See `tool-capability-isolation.md`, `sandboxed-execution.md`, `least-privilege-credentials.md`.
- **Out-of-band isolation / quarantine of the anomalous component.** A41065's gossip protocol disseminates
  reputation matrices and isolates bad actors ("social immune response"); A41134 BU-MA shows this must be
  out-of-band because user-level isolation fails against a compromised internal agent (MetaGPT ASR reduction
  only 7%).
- **Revocation of activation via multi-party / threshold authorization.** A40925 binds model execution to a
  complete multi-party trigger so "no single party (or an attacker who steals the model or one party's
  secrets) can activate the model"; revoking one party's consent contains a stolen-model incident (residual
  ~15% Acc-Fusion remains — see Residual risks).
- **Rate-limiting + query monitoring to contain an extraction loop.** A40432 pairs its dual-path defense with
  rate-limiting and query monitoring of recursive topic-expansion / memory-driven refinement (author-reported
  cost < 2 accuracy points, FLOPs unchanged or reduced).
- **Targeted erasure / model editing as post-incident knowledge containment.** A41145's ROME editing suppresses
  specific memorized content without full retraining (author-reported extraction 65.2% → 1.6%) — the corpus's
  explicit "incident-containment/erasure path." See `model-extraction-defenses.md`.
- **Independent end-state verification.** Because completion self-reports include hallucinated success
  (A42249), verify the actual post-containment end state out-of-band rather than trusting the agent's claim.

**Framing (non-negotiable).** The *trigger* for containment is a noisy detector (real-world F1 ≈ 0.3–0.6,
A42369) or a spoofable score (A37924), so the trigger will both over- and under-contain; the *action* must be
deterministic and fail-closed, and the decision to declare an incident "contained" must rest on independent
verification, not on the affected component's report.

## Preconditions and trust assumptions

- **An alert / detection signal already exists.** Containment is the response layer; it presupposes
  `runtime-anomaly-detection.md` (or a gate rejection) fired. It does not itself detect.
- **A trustworthy, tamper-evident, out-of-band evidence channel.** The recurring unguarded assumption is
  trusted telemetry/labels (Network-Cyber §3). The response engine must consume integrity-protected telemetry
  the compromised component cannot forge or suppress; if it can (A41134 BU-MA), containment triggers on a lie.
  This is what `tamper-evident-traces.md` supplies.
- **Least privilege is already configured, so blast radius is pre-bounded.** A42249 "capability ≠ permission" —
  containment is dramatically cheaper when standing privilege is minimal; retrofitting containment onto a
  broadly-privileged agent leaves the full privilege set exposed.
- **The response engine is isolated from the monitored/affected component.** In-band containment a compromised
  agent can disable is not containment (A41134 BU-MA; A41065 requires an honest quorum for reputation consensus
  to isolate bad actors).
- **Model-editing / erasure containment requires white-box model access.** A41145's ROME edits internal
  representations; the containment path is unavailable for black-box-only deployments.
- **Multi-party revocation requires the consensus/trigger scheme to be pre-provisioned.** A40925's CTD triggers
  are embedded during training — activation-time revocation is only available if this was designed in.
- **An honest quorum / connected graph for reputation isolation.** A41065's gossip convergence "depends on the
  second-largest eigenvalue of the gossip matrix" and "a quorum of honest agents is implicitly needed."
- **Containment triggers and trust surfaces are themselves attackable.** Reputation/aggregation weights and
  score thresholds can be gamed (A39732, A41065; reviewer synthesis) — harden the meta-decision.

## System architecture

- **Environment-side, out-of-band response engine positioned between intent and execution.** Trailing guardrail
  text is insufficient when the trigger lives inside a model-visible field (A42239) or a compromised agent
  (A41134); the response must intercept at a boundary the model cannot be talked past (A42249's proposed
  command-validation point). Reject out-of-set actions regardless of model output (A42239 {A–D} enforcement).
- **Layered / defense-in-depth containment, not a single choke point.** Convergent across A40432, A39732,
  A41134, A41065: single-point defenses are insufficient (Defense-Mitigation §9, the strongest cross-paper
  theme). Architect complementary containment at the action gate, the capability boundary, the peer-isolation
  layer, and the model-activation layer.
- **Structural separation of user intent from executable instruction.** A41134's positional-injection finding
  (malicious module appended *after* the benign request to evade filters) implies containment cannot rely on
  order/position; enforce a boundary the model cannot be talked past, not trailing text.
- **Pre-containment by least privilege + capability isolation + sandboxing + egress control.** A41134, A42249:
  bound the blast radius before the incident so containment has less to reverse. See `tool-capability-
  isolation.md`, `sandboxed-execution.md`, `network-segmentation.md`.
- **Out-of-band isolation / reputation layer for multi-agent systems.** Per-agent anomaly + probabilistic
  trust + gossip-based reputation isolation (A41065), with the caveat that its security evidence is
  task-accuracy, not measured attack-success, and it assumes an honest majority.
- **Multi-party authorization bound to model activation for high-value assets** (A40925), accepting residual
  ~15% Acc-Fusion as a monitored risk.
- **Intermediate state as a contained confidentiality boundary.** In multi-tenant / offloaded / split hosting,
  contain access to activations and routing metadata, not just the payload (A40100, A39721).
- **Trajectory / tamper-evident trace as the forensic-scoping substrate.** Per-step interaction logs (and, where
  feasible, screen/video) scope what to isolate/revoke/roll back (A40210, A42249); preserve, do not destroy,
  during response. See `tamper-evident-traces.md`.
- **Harden every new trust-decision surface the containment layer introduces.** Reputation/aggregation weights,
  score thresholds, and activation triggers can be gamed (A39732, A41065; reviewer synthesis, Network-Cyber §15).

## Recommended implementation pattern

Deterministic, fail-closed, least-privilege. The trigger may be probabilistic; the response must not be.

1. **Pre-contain by least privilege before anything happens.** Minimize standing capability and isolate
   tool-calling code (block outbound email/network from generated apps, sandbox, egress-control) so the blast
   radius of any single incident is small (A41134, A42249). This is the cheapest containment.
2. **Define the on-policy action set deterministically and reject out-of-set actions on alert** (A42239 {A–D};
   A42249 command validation) — regardless of what the model decided. Fail closed.
3. **Halt / reject-defer to human review as a first-class action** on any detected violation, drift, or
   low-confidence (A37053 reject; A41134 refuse/replace/halt; A42249 human approval on consequential steps) —
   never fail open.
4. **Gate consequential / irreversible actions behind human approval regardless of the trigger's verdict** —
   install, auth, outbound send (A42249). See `human-approval-consequential-actions.md`.
5. **Isolate the affected component out-of-band.** Quarantine and down-weight the anomalous agent via
   reputation isolation (A41065); do it out-of-band because in-band/user-level isolation fails against a
   compromised internal agent (A41134 BU-MA, MetaGPT 7%).
6. **Rate-limit and monitor the abused channel** on an extraction-suspicious query loop (A40432, cost < 2
   accuracy points).
7. **Revoke activation for high-value assets** via multi-party / threshold authorization (A40925).
8. **Perform targeted erasure on confirmed knowledge leakage** — ROME model editing without full retraining
   (A41145, 65.2% → 1.6%) — *but validate against post-edit re-optimization and across the full downstream task
   suite before relying on it* (A41145 reviewer).
9. **Independently verify the post-containment end state**; do not trust agent-claimed completion (A42249
   hallucinated completion).
10. **Preserve the tamper-evident trace throughout** for forensic scoping and audit (A40210, A42249); do not
    let response actions destroy evidence.
11. **Report absolute residuals, not only relative reductions** — the strongest defenses still leak (A40432
    ~28% CRR; A40925 ~15% Acc-Fusion; A41134 residual absolute ASR remains high because reductions are relative).

## Incorrect or fragile implementation patterns

- **Trailing guardrail text / prompt hygiene as the containment boundary.** The model can be talked past it;
  the trigger lives inside a model-visible field (A42239) or a compromised role profile (A41134 positional
  injection appended after a benign request).
- **In-band / user-level containment a compromised component can disable or ignore.** A41134 BU-MA: MetaGPT ASR
  reduction only 7% under a compromised internal agent vs. 40% when benign — user-interface-level defense
  "largely fails against internally compromised agents."
- **Trusting the agent's "incident contained / task complete" self-report.** Hallucinated completion masks
  skipped/unsafe steps (A42249); the end state must be independently verified.
- **A containment reflex keyed solely on a spoofable score or certificate.** A37924 spoofs the certificate (ASR
  30–100%) and turns forced abstentions into DoS — a score-driven auto-contain both misses real incidents and
  is weaponizable.
- **A fixed default detection threshold as the containment trigger.** A42369: threshold optimization improved
  F1 in **100%** of model-dataset combinations (author-reported median +0.082, best +0.542) — a default
  threshold over- or under-contains and is domain-specific.
- **Assuming targeted erasure is permanent.** ROME is evaluated only against the same non-adaptive attack; "a
  defense-aware attacker could re-tune the soft prompt post-edit — robustness not established" (A41145).
- **Assuming reputation isolation or aggregation is unattackable.** No adaptive adversary that Sybil-floods
  gossip to bias reputation is evaluated (A41065); robustness-aware aggregation is itself gameable (A39732);
  honest-majority is unverified against collusion.
- **Homomorphic-encryption aggregation as poisoning containment.** A41065: HE "protects update confidentiality
  but … does not prevent poisoning" — encryption is the wrong containment for a poisoning incident.
- **Content-layer DLP as the exfiltration containment.** Covert channels are invisible at the content layer
  (A37125 Pe ≈ 0.5; A40903 stego = cover) — contain at egress/capability/provenance, not content.
- **Containing only the payload while activations / routing leak.** A40100 (activation inversion under
  collusion), A39721 (routing access-pattern leak) — "payload encrypted" is insufficient.
- **Treating a single detector verdict as sufficient grounds to auto-contain destructively.** Real-world F1 ≈
  0.3–0.6 (A42369); corroborate out-of-band before an irreversible response.

## Verification strategy

- **Independent end-state verification vs. agent-claimed completion** — the primary check that containment
  actually happened (A42249 hallucinated completion).
- **Trajectory-level evidence review**, not pass/fail, to confirm the incident's true scope was isolated
  (A40210 trajectory competency scoring; A42249 per-step + video).
- **Report residual leakage / activation after containment, absolutely.** ER30/ER50 extraction rate before and
  after ROME (A41145 65.2% → 1.6%); Acc-Fusion after multi-party revocation (A40925 ~15%); chunk-recovery rate
  after rate-limiting + dual-path (A40432 ~28%, 57.16% → 27.96% HealthCareMagic/Qwen-14B); ASR-under-defense
  absolute, not only relative (A41134).
- **Time-aware / distribution-shift-honest evaluation** of any drift-triggered containment (A37053 TESSERACT;
  A42369 seeded splits + identifier anonymization) — do not validate on inflated IID.
- **Multi-seed confidence intervals** rather than single-run point estimates (A42369, 3 seeds × 80/10/10).
- **Verify erasure durability against re-optimization** before relying on ROME (A41145 reviewer).
- **Verify isolation holds under an honest quorum only** — test reputation convergence and its failure when the
  malicious fraction rises (A41065).
- **Out-of-band corroboration required before any irreversible containment action** driven by a detector
  (A42369, A36959, A40815).

## Metrics and thresholds

Author-reported unless labeled. All are **non-adaptive** estimates — upper bounds on protection. **No paper
reports a containment-*speed* metric** (time-to-contain, MTTR, rollback latency); those are "not stated in
paper."

- **Residual extraction rate after erasure** — ER30/ER50 exact-match before/after ROME: 65.2% → 1.6% (A41145,
  GPT-Neo 1.3B, white-box, non-adaptive; Pythia baseline 51.7%). Report the *absolute residual* (1.6%), not
  only the drop.
- **Residual unauthorized activation after revocation** — Acc-Fusion ≈ 4.4–15.1 on CIFAR-10 (VGG16 ≈ 15.08),
  meaningfully above chance (A40925). Containment reduces but does not close.
- **Residual chunk-recovery rate after rate-limiting + dual-path** — ~28% (57.16% → 27.96%,
  HealthCareMagic/Qwen-14B); single-module variants still expose > 40% (A40432).
- **ASR reduction under defense, MU-BA vs. BU-MA, reported absolutely** — Adv-IMBIA MU-BA reductions ChatDev
  73% / MetaGPT 40% / AgentVerse 49%; BU-MA ChatDev 45% / MetaGPT **7%** / AgentVerse 42% (A41134). The 7% is
  the load-bearing warning: in-band containment against a compromised internal agent barely works, and
  reductions are relative so residual absolute ASR stays high.
- **Reject / defer rate and reject-rate-under-defense** — RR / RR-d (A41134); explicit reject action rate
  (A37053).
- **Rate-limiting / query-monitoring cost** — author-reported < 2 accuracy points, FLOPs unchanged or reduced
  (A40432) — cheap enough to deploy.
- **Security-incident incidence to contain** — unauthorized-install rate (100% in certain planning tasks),
  brute-force-attempt count, sensitive-app exposure, hallucinated-completion rate (A42249, small-n).
- **Detection F1 as the trigger quality bound** — real-world F1 ≈ 0.3–0.6 (DiverseVul 0.307, Reveal 0.486)
  vs. inflated synthetic 0.9+ (Juliet 0.900, VulDeepecker 0.959); threshold optimization helps 100% of
  combinations (A42369) — so the containment trigger is domain-specific and noisy, never a default.
- **Certificate/score-spoofing rate and abstention→DoS rate** — the trigger's own attack surface (A37924, ASR
  30–100%).

## Test cases

Concrete cases drawn from corpus attack families (each verifies containment fires and bounds the blast radius):

- **Out-of-set action on injection.** Authoritative "contradiction" text in a non-prompt model-visible field
  drives an out-of-allow-list selection; verify deterministic rejection independent of model output (A42239).
- **Consequential-action halt.** A benign planning task attempts unauthorized software install / brute-force
  login / navigation into a sensitive app; verify the action is halted and routed to human approval (A42249).
- **Hallucinated-completion catch.** Agent reports the incident is contained / task complete but skipped steps;
  verify independent end-state verification catches the discrepancy (A42249).
- **Compromised internal agent (BU-MA) isolation.** A hidden role-profile instruction inserts a `send_email`
  exfiltration function; verify out-of-band capability/egress containment fires even though in-band user-level
  containment would not, and that the agent is isolated/down-weighted (A41134, A41065).
- **Cascade stop.** A danger/pathogen signal on one agent; verify reputation isolation prevents propagation to
  peers (A41065 "without containment[,] cascade").
- **Extraction-loop rate-limit.** Recursive topic-expansion / memory-driven queries against a RAG KB; verify
  rate-limiting + query monitoring engage and the loop is throttled (A40432).
- **Confirmed knowledge leak erasure.** Repeated prefix-conditioned queries + soft-prompt attachment confirm
  memorized-suffix leakage; verify targeted ROME erasure drops extraction and utility is retained (A41145).
- **Stolen-model activation revocation.** One party's secret is leaked / the model is exfiltrated; verify
  multi-party authorization prevents meaningful activation and quantify the residual Acc-Fusion (A40925).
- **Score-spoof resilience of the trigger.** Feed near-duplicate inputs producing a large "ghost" certificate;
  verify the containment reflex does not auto-fire on the spoofed score alone and that forced abstentions are
  not weaponizable into DoS (A37924).

## Adaptive adversarial tests

The corpus's largest gap is the **near-universal absence of adaptive evaluation** (Network-Cyber §3/§9/§12;
Defense-Mitigation §9), and it is most acute for the two headline containment mechanisms. The following are
**not evaluated in the corpus** and are stated as production-validation requirements, each anchored to the
closest demonstrated analog:

- **Containment reversal by re-optimization.** An attacker who re-tunes the soft prompt *after* ROME erasure to
  regenerate the suppressed suffixes (A41145 reviewer — "robustness not established"). *Not evaluated against
  post-edit re-optimization; requires production validation.*
- **Trust-surface gaming to evade isolation.** Sybil-flooding gossip to bias reputation and keep a malicious
  agent from being isolated (A41065), or appearing locally robust while poisoning globally to survive
  robustness-aware aggregation (A39732). *Not tested against Sybil/collusion.*
- **Partial-trigger fusion against activation revocation.** Fusing partial triggers to reactivate a revoked
  model (A40925, residual ~15% Acc-Fusion under the *evaluated* fusion attacker; no adaptive white-box
  gradient-search activator evaluated). *Requires validation against a stronger activator.*
- **Score / trigger gaming to force false or missed containment.** Spoof the certificate to suppress the
  trigger, or force abstentions to weaponize the containment reflex into DoS (A37924, white-box + known σ, ASR
  30–100%). *Requires production validation.*
- **Detector-aware evasion of the containment trigger.** An attacker who knows the rate-limit / query-monitor
  thresholds and adapts query strategy — within-cluster probing, paraphrase to dodge the rejection rule (A40432
  reviewer synthesis; ~28% residual CRR implies headroom). *Not evaluated against adaptive attackers.*
- **Purification defeating an erasure/perturbation-style containment analog.** Protective perturbation removed
  by purification / retraining / re-recording (A37756, A37844, both citing Hönig et al. 2024 that such
  protection "cannot reliably protect"). *Not evaluated against adaptive purification.*
- **Concept-drift-as-evasion of a drift-triggered containment.** An attacker who shifts the distribution slowly
  to stay under the reject/defer threshold (A37053). *Requires production validation.*
- **Content-layer-invisible exfiltration during containment.** Covert channel that a content-DLP-based
  containment cannot see (A37125 Pe ≈ 0.5; A40903 stego = cover). *Contain at egress/provenance, not content.*

## Telemetry requirements

- **A tamper-evident, out-of-band per-step trajectory record** — action, tool call, arguments, result — as the
  forensic-scoping substrate for what to isolate/revoke/roll back (A40210, A42249). Preserve during response;
  do not let containment actions destroy it. See `tamper-evident-traces.md`.
- **Every model-visible field ingested** — prompt, options, tool results, retrieved text — so the injection
  source can be scoped (A42239).
- **Egress / behavioral primitives** — send_email, external URL fetch, clipboard/keyboard capture, file
  encryption (A41134's 12-behavior taxonomy) — the signatures that trigger capability/egress containment.
- **Query-pattern telemetry** — recursion depth, topic-expansion, memory-driven refinement (A40432);
  prefix-conditioning repetition + soft-prompt attachment (A41145) — to trigger rate-limiting / erasure.
- **Per-agent reputation / anomaly / trust signal** (A41065 immune signals SS/DAMP/PAMP → MCAV; A39732
  per-client accuracy-drop) — the input to isolation decisions, itself a hardened trust surface.
- **Model-activation authorization state** — which parties have consented; residual activation under partial
  triggers (A40925).
- **Intermediate-state access where multi-tenant / offloaded** — activations and expert-selection / routing
  metadata as sensitive assets (A40100, A39721).
- **Certificate / score distribution + input near-duplication** — to detect a spoofed trigger before
  auto-containing (A37924).
- **A durable record of what was contained** — which action halted, which agent isolated, which capability
  revoked, which knowledge erased — for rollback, audit, and independent end-state verification (A42249).
- **Human-agreement calibration data** for any LLM-as-judge trigger component (A36959, A40210, A41134's 86.34%
  agreement figure).

## Failure handling

- **Fail closed.** On trigger unavailability, low confidence, detected drift, or a suspected spoofed score,
  default to halt / reject-defer to human review (A37053; A42249) — never fail open. A37924's abstention-as-DoS
  is the caveat: fail-closed must not be trivially forced by an attacker, so combine with rate-limiting and
  out-of-band corroboration.
- **Do not trust the compromised component's report** that containment succeeded — independently verify the end
  state (A42249).
- **Corroborate out-of-band before any irreversible containment** (destructive rollback, permanent revocation)
  driven by a noisy detector (F1 ≈ 0.3–0.6, A42369).
- **Escalate consequential/irreversible actions to human approval** regardless of automated verdict (A42249).
  See `human-approval-consequential-actions.md`.
- **Budget for residual risk and report absolute residuals** — the strongest containment still leaks (A40432
  ~28% CRR; A40925 ~15% Acc-Fusion; A41134 residual absolute ASR high).
- **Assume in-band containment can fail against a compromised internal component** (A41134 BU-MA) — the
  fallback is out-of-band isolation and least-privilege pre-containment, not a stronger in-band prompt.

## Rollback and containment

- **Reject / defer routing to manual review** as a first-class, reversible action — the human can subsequently
  approve (A37053, A42249).
- **Targeted model editing (ROME) as reversible-scope erasure** without full retraining (A41145, 65.2% →
  1.6%) — but treat it as *reversible by the attacker too* (post-edit re-optimization not defended) and
  validate against the full downstream task suite before relying on it.
- **Multi-party / threshold re-authorization** to restore activation after revocation, or to keep it revoked
  by withholding one party's consent (A40925) — with the ~15% residual-activation headroom as a monitored risk.
- **Rate-limit relaxation** once an extraction loop is confirmed benign (A40432, low cost < 2 accuracy points
  makes toggling cheap).
- **Gossip-based reputation restoration** for an agent cleared after isolation (A41065) — with the caveat that
  reputation is a gameable trust surface and convergence assumes an honest quorum.
- **Least-privilege capability isolation, sandboxing, and egress control** as the standing containment that
  bounds what any rollback must undo (A41134). See `tool-capability-isolation.md`, `sandboxed-execution.md`.
- **Irreversibility caveat (load-bearing).** Containment reduces blast radius; it does not reverse
  already-exfiltrated data or residual leakage. A40432's strongest configuration still leaked ~28% of chunks
  *before* rate-limiting engaged; A40925 leaves ~15% Acc-Fusion; A37125 / A40903 exfiltration invisible at the
  content layer may complete before any content-based rollback. **No paper demonstrates infrastructure-level
  snapshot/restore or clean rollback of an in-progress exfiltration — that capability is "not stated in
  paper"** and must be supplied and validated on the target stack.
- **Caveat:** containment that relies on reputation/aggregation is itself a gameable trust surface (A39732,
  A41065); harden and log the meta-decision.

## Known bypasses

**Demonstrated (within the papers, under their stated — mostly non-adaptive — threat models):**
- **Compromised internal agents defeat user-level / in-band containment** (A41134 BU-MA; MetaGPT ASR reduction
  only 7% vs. 40% MU-BA).
- **Hallucinated completion masks skipped / unsafe steps** so a self-reported "contained" is false (A42249).
- **Certificate / score spoofing** deceives a score-driven trigger and turns abstention into DoS (A37924,
  white-box + known σ, ASR 30–100%).
- **Partial-trigger fusion partially bypasses multi-party activation revocation** (A40925, ~15% Acc-Fusion
  above chance).
- **Residual leakage persists under the strongest extraction containment** (A40432, ~28% CRR after dual-path +
  rate-limiting; single-module > 40%).
- **Covert channels invisible at the content layer** evade content-DLP containment (A37125 Pe ≈ 0.5; A40903
  stego = cover).
- **Access-pattern leak bypasses payload-only containment** (A39721); **activation inversion under collusion**
  (A40100).

**Reviewer-identified (not demonstrated in the papers):**
- ROME erasure reversible by post-edit soft-prompt re-optimization (A41145 reviewer).
- Sybil-flooding gossip to bias reputation and evade isolation; gaming robustness-aware aggregation
  (A41065, A39732).
- HE aggregation hides updates but does not contain poisoning; honest-majority unverified against collusion
  (A41065).
- Detector-aware query adaptation against extraction rate-limiting (A40432 reviewer synthesis).
- Purification / re-recording defeating protective-perturbation-style containment (A37756, A37844, citing
  Hönig et al. 2024).

## Residual risks

- **Containment reduces blast radius; it does not eliminate it.** Residual leakage/activation persists under the
  strongest defenses evaluated (A40432 ~28% CRR; A40925 ~15% Acc-Fusion; A41145's 1.6% is a residual, not
  zero) — and already-exfiltrated data is irreversible.
- **In-band containment fails against a compromised internal component** (A41134 BU-MA, 7%) — the fallback
  (out-of-band isolation + least privilege) is a precondition, not something this pattern grants.
- **The trigger is noisy and spoofable.** Real-world detector F1 ≈ 0.3–0.6 (A42369) and scores are spoofable
  (A37924) — containment will over- and under-fire, and a score-driven auto-contain is DoS-weaponizable.
- **The two headline containment mechanisms are non-adaptively evaluated and likely reversible** — ROME erasure
  (A41145) and reputation isolation (A41065) both lack adaptive-adversary evaluation.
- **New trust-decision surfaces (reputation, aggregation, activation triggers) are themselves attackable**
  (A39732, A41065; reviewer synthesis, Network-Cyber §15).
- **The trusted-telemetry assumption is unguarded.** If the response engine's evidence is forgeable/suppressible
  by the compromised component, containment triggers on a lie or never fires (Network-Cyber §3).
- **No operational containment-speed evidence.** Time-to-contain, MTTR, rollback latency, and measured
  blast-radius reduction are "not stated in paper" across the corpus — these require production validation.
- **Single-paper / truncated evidence.** A41065's security evidence is task-accuracy (not measured
  attack-success); A40925, A41145 are single-paper, small-model / white-box; several cards flag truncated
  tables — all require independent validation before operational reliance.

## Relevant research (stable paper ids from the syntheses/cards)

*Core containment mechanisms:*
- **A41145** — CoSPED: Consistent Soft Prompt Targeted Data Extraction and Defense (AAAI-26; code released):
  ROME targeted model editing as the corpus's explicit "incident-containment/erasure path without full
  retraining"; author-reported extraction 65.2% → 1.6%; white-box, small models (GPT-Neo 1.3B / Pythia 1.4B),
  **not tested against post-edit re-optimization**. Evidence: moderate.
- **A41134** — Shadows in the Code / IMBIA (AAAI-26; code released): Adv-IMBIA refuse/replace/halt guardrails;
  least-privilege capability isolation + sandboxing + egress control as pre-containment; **MU-BA vs. BU-MA
  asymmetry** (MetaGPT ASR reduction 7% BU-MA vs. 40% MU-BA) — in-band containment fails against compromised
  internal agents; 12-behavior egress taxonomy. Evidence: moderate.
- **A42249** — Towards Capable and Secure Autonomous Computer-Use Agents (AAAI-26, Student Abstract):
  "capability ≠ permission"; human approval on consequential actions; **hallucinated completion** means
  containment cannot be self-reported; proposes an unbuilt command-validation gate. Evidence: preliminary
  (small-n, version-bound, partly subjective) but directionally credible.
- **A37053** — DRMD (AAAI-26; code released): explicit **reject / defer** as a first-class containment action;
  time-aware TESSERACT evaluation. Evidence: moderate.
- **A40925** — Consensus Learning with Multi-Party Perturbation Triggers (AAAI-26): multi-party / threshold
  authorization bound to model activation — revoke a stolen-model incident; residual ~15% Acc-Fusion under
  partial-trigger fusion; non-adaptive. Evidence: moderate.
- **A41065** — Resilience in Ambient Multi-Agent LLMs (AAAI-26): gossip-based reputation isolation of anomalous
  agents ("without containment[,] cascade"); honest-majority / Sybil / HE-does-not-prevent-poisoning caveats.
  Evidence: moderate (architecture), preliminary (security — task-accuracy, not attack-success).
- **A40432** — RAGFort (AAAI-26; code released): rate-limiting + query monitoring to contain extraction loops
  (cost < 2 accuracy points); residual ~28% CRR. Evidence: moderate (leaning strong).

*Trigger integrity, forensic scoping, and calibration:*
- **A37924** — GhostCert (AAAI-26; code released): a verification artifact is not a correctness oracle — a
  score-driven containment trigger is spoofable (ASR 30–100%) and abstention becomes DoS. Evidence: strong.
- **A42369** — VulnBench (AAAI-26; code released): the containment *trigger* is a triage aid, real-world F1 ≈
  0.3–0.6, threshold optimization helps 100% of combinations. Evidence: moderate (leaning strong,
  methodological).
- **A42239** — Obedience or Vigilance? (AAAI-26): any model-visible field is an injection surface;
  environment-side out-of-set rejection as the deterministic containment boundary. Evidence: preliminary
  (single model QwQ-32B, MMLU, non-adaptive).
- **A40210** — Offensive Security LLM Agents / CTFTiny + CTFJudge (AAAI-26; code released): trajectory-level
  evidence as the forensic-scoping substrate; LLM-judge calibration caveat. Evidence: moderate.

*Containment blind spots and gameable surfaces:*
- **A37756 / A37844** — proactive protective perturbation (AAAI-26; A37756 code released): an erasure/perturbation
  containment analog defeated by purification (both cite Hönig et al. 2024). Evidence: moderate (non-adaptive).
- **A37125 / A40903** — content-layer-invisible covert channels (AAAI-26): content-DLP containment fails; shift
  to egress/provenance. Evidence: moderate (non-adaptive; "provable security" downgraded by reviewer).
- **A40100 / A39721** — confidentiality pair (AAAI-26; code released): activations (A40100 collusion inversion)
  and routing access patterns (A39721 expert-selection leak) must be contained, not just the payload. Evidence:
  moderate (empirical privacy / semi-honest only).
- **A39732** — STRUM / GTAE (AAAI-26): robustness-aware aggregation is itself a gameable containment-trust
  surface. Evidence: preliminary (unreconciled dataset count, no visible numerics, no code).

*Cross-cutting theme:*
- **Layered / defense-in-depth containment** is the strongest cross-paper theme (Defense-Mitigation §9),
  convergent across A40432, A39732, A41134, A41065.

*Excluded as off-topic / no security evaluation:* A41178 (disaster-risk geospatial ML), A41464 (water-pipeline
sensor faults), A42153 (agenda abstract), A42470 (autonomous-driving physical-hazard detection), A40129
(non-adversarial continual-learning stability), A42364 (GNN-AID — tooling framework, no security numbers),
A42318 (AI-vs-AI defense proposal, no experiments).

## Evidence strength

- **Strongest single evidence:** A37924 (strong; ImageNet-scale, three certified defenses, released code) for
  "a containment trigger keyed on a score is spoofable and abstention becomes DoS." A42369 (moderate, leaning
  strong for the methodological claims; released code, 8 datasets, 3 seeds) for "the trigger is a noisy triage
  aid, real-world F1 ≈ 0.3–0.6." A40432 (moderate, leaning strong; realistic black-box threat model, released
  code) for rate-limiting/query-monitoring containment with quantified residual (~28% CRR).
- **Core containment mechanisms are moderate / preliminary and non-adaptively evaluated:** A41145 (moderate;
  ROME 65.2% → 1.6%, white-box, small models, no adaptive re-optimization test), A40925 (moderate; multi-party
  revocation, ~15% residual Acc-Fusion, non-adaptive), A41134 (moderate; 480 cases across three frameworks,
  single GPT-4o-mini backend, LLM-as-judge; the BU-MA 7% vs. MU-BA 40% asymmetry is well-supported
  qualitatively).
- **Architecture template with weak security evidence:** A41065 (moderate architecture; security evidence is
  task-accuracy, not measured attack-success; honest-majority / Sybil untested).
- **Agent grounding is preliminary but directionally credible:** A42249 (small-n, version-bound, partly
  subjective video scoring), A42239 (single model, single dataset, non-adaptive templates).
- **Overarching calibration:** there is **no independent replication across these papers** (each is
  self-contained); convergent themes are agreements across independent domains, not replicated effect sizes.
  **Essentially no containment mechanism was evaluated against an adaptive, defense-aware attacker**, so every
  effectiveness number is a non-adaptive upper bound. **No paper reports a containment-speed / MTTR /
  blast-radius-reduction metric** — those are "not stated in paper." **Requires production validation** on the
  target stack before operational reliance.

## When NOT to use this pattern

- **As a substitute for prevention or detection.** Containment is the response layer; it presupposes a
  deterministic preventive gate (`policy-permission-gates.md`), least-privilege configuration
  (`least-privilege-credentials.md`), and a detection signal (`runtime-anomaly-detection.md`). It bounds damage
  after the fact; it does not stop incidents from starting.
- **As an in-band control a compromised component can disable.** A41134 BU-MA shows in-band/user-level
  containment fails against a compromised internal agent (MetaGPT 7%); if you cannot place the response engine
  out-of-band, this pattern does not deliver.
- **When you cannot guarantee trustworthy, tamper-evident, out-of-band telemetry.** The whole control collapses
  on the trusted-telemetry assumption (Network-Cyber §3); establish `tamper-evident-traces.md` first.
- **As auto-destructive response driven by a single noisy or spoofable trigger.** Real-world F1 ≈ 0.3–0.6
  (A42369) and scores are spoofable (A37924, abstention → DoS) — require out-of-band corroboration and human
  approval before irreversible containment (`human-approval-consequential-actions.md`).
- **When you need to reverse already-completed exfiltration.** Residual leakage (A40432 ~28% CRR; A40925 ~15%
  Acc-Fusion) and content-layer-invisible exfiltration (A37125, A40903) may complete before containment; no
  corpus paper demonstrates clean rollback of an in-progress leak.
- **As permanent erasure you can rely on without re-validation.** ROME (A41145) is untested against post-edit
  re-optimization and only validated on small white-box models — validate durability and downstream utility
  first (`model-extraction-defenses.md`).
- **Against covert channels at the content layer.** Content-inspection containment cannot see them (A37125,
  A40903); shift to egress / model / provenance attestation (`content-provenance.md`, `signed-provenance.md`).
- **When the threat model includes an adaptive, defense-aware attacker and you have no adaptive evaluation.**
  The corpus provides essentially none for containment; treat the control as unvalidated against that adversary
  until production validation is done (Network-Cyber §3/§9/§12; Defense-Mitigation §9).
