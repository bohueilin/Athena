# Pattern: Network Segmentation

> Engineering-control playbook. Grounds every recommendation in the Guardian-Agent corpus and cites stable
> paper ids. Primary evidence is the AAAI-26 research cards behind the **Network-Cyber-Security** synthesis
> (ids prefixed `A…`), plus the **Defense-Mitigation** card **A41134** where egress/network-primitive evidence
> is most direct. Where the most on-point blast-radius / trust-domain / trajectory-telemetry guidance lives in
> the broader Origin corpus captured in `architecture-patterns.md` and `agent-identity.md`, those are cited by
> the source file and labeled **(reviewer synthesis)** — their numbers were not re-verified here against the
> primary cards, and are treated as lower-confidence.
>
> Evidence-integrity conventions (non-negotiable): numeric values are **author-reported** unless labeled
> "reviewer synthesis." Absent values are written "not stated in paper." Calibrated language only — findings
> hold "under the evaluated threat model" and "against the tested attacks," never "secure / proven-safe."
> Direct paper findings are distinguished from reviewer synthesis. **No paper in this corpus evaluated an
> adaptive, defense-aware attacker against a segmentation boundary** (Network-Cyber-Security §9/§12 flag the
> near-universal absence of adaptive evaluation); treat every containment number below as a **non-adaptive**
> upper bound on real-world protection.
>
> Scope note: the corpus does not contain a paper whose primary contribution is "network segmentation" as a
> named control. This pattern therefore composes segmentation from what the corpus *does* evidence —
> least-privilege boundaries, environment-side fail-closed gates, blast-radius containment, boundary intrusion
> detection, side-channel isolation, and reputation-based quarantine — and states plainly where a
> recommendation is an engineering extrapolation rather than a measured result.

---

## Problem addressed

A flat network — where any agent, tool runtime, sub-agent, or service can reach any other host and any egress
destination by default — converts a single local compromise or a single injected instruction into a
system-wide incident. The corpus makes the underlying failure concrete, even though it does not test
segmentation itself:

- **Broad standing reach turns a mistake into an incident.** A42249 (author-reported) observed Claude Sonnet
  3.5 installing software without consent in **100% of certain planning tasks**, plus attempted brute-force
  logins and sensitive-app exposure via navigation errors, when the agent held broad/unrestricted system
  privileges by default. The card's load-bearing framing is **"capability is not permission."** The network
  analogue: default reachability is standing privilege at the transport layer.
- **A compromised internal peer can reach outward and exfiltrate.** A41134 (IMBIA / "Shadows in the Code",
  Defense-Mitigation) shows a benign-user / compromised-agent (BU-MA) pipeline where a sub-agent silently
  inserts network/exfiltration primitives (a `send_email`-style function) into generated software; its
  author-recommended remedy explicitly includes **egress controls** and **least-privilege capability isolation
  that blocks outbound email/network from generated apps** — a per-workload network boundary. Prompt-level
  guardrails were near-useless here (author-reported Adv-IMBIA reduced MetaGPT ASR by **73% in MU-BA but only
  7% in BU-MA**), so the boundary must be structural, not textual.
- **Capable agents are dual-use and pivot.** A40210 (author-reported) ran offensive CTF agents across binary
  exploitation, web, reverse-engineering, forensics, and crypto; the paper's own safety posture is to run them
  **only inside controlled Linux sandboxes** with **"authorization boundaries, sandboxing, and rate/scope
  limits."** Lateral movement / pivoting is exactly what an unsegmented network permits.
- **Isolation that shares intermediate state leaks across the boundary.** A40100 (FedSEA-LLaMA, author-reported)
  reconstructs input from **forward activations** under server+client collusion in split inference; A39721
  (SecMoE) shows **expert-selection/routing access patterns** leak input semantics even when the payload is
  encrypted. A segment boundary that separates payloads but shares memory, activations, caches, or routing
  metadata is porous.

Network segmentation is the control that partitions the system into trust zones with **default-deny boundaries**
between them, so a compromise, an injection-driven action, or an ordinary error reaches only its own zone rather
than the whole estate — bounding blast radius, lateral movement, and egress.

---

## Applicable assets and attack surfaces

Assets a segmentation boundary is meant to protect (grounded in the corpus):

- **Cross-zone reachability itself** — the ability of one host/agent/tool to open a connection to another. This
  is the primary asset; default reachability is the standing privilege A42249 warns against.
- **Egress / exfiltration channels** — outbound network and messaging from a workload. A41134 enumerates a
  **12-behavior malware taxonomy** (Trojan / Spyware / Adware / Ransomware / Virus families; author-reported)
  whose network-relevant members (`send_email`, external-URL fetch, file encryption/ransomware C2) are the
  concrete egress-signature set a boundary must fence.
- **High-value / privileged zones** — install/package managers, authentication services, system settings
  (A42249 unauthorized installs, brute-force logins), and any credential-issuing or model-execution service.
- **OT / ICS control networks** — A39770 evaluates on **SWaT**, a real ICS-attack testbed (author-reported),
  giving indirect grounding for isolating cyber-physical control segments from IT.
- **Intermediate agent state as a confidentiality asset across the boundary** — not just the payload. A40100
  (activation inversion under collusion) and A39721 (routing access-pattern leak) show a boundary that shares
  activations/routing metadata leaks input semantics through side channels.
- **Blast-radius budget** — how many credentials/capabilities a single compromise can wield (`k`), which a zone
  boundary is meant to cap (`architecture-patterns.md` P6, reviewer synthesis).

Attack surfaces that reach across or drive traffic through a boundary:

- **Any model-visible field**, not only the user/system prompt. A42239 (author-reported) shows authoritative
  text placed *inside a candidate answer option* drives an LLM off-policy — "contradiction" style reached
  **E-adoption ≈0.5 ("up to 50%")** with accuracy collapsing to **≈0.27** (single model QwQ-32B, MMLU,
  temp 0.1). Tool results, retrieved documents, and answer options can all carry an instruction to "connect to
  X" — so the boundary cannot trust the model to choose the destination.
- **Compromised peer/sub-agents** initiating east-west or outbound traffic (A41134 BU-MA; A41065
  malfunctioning/malicious ambient agents).
- **Colluding infrastructure parties** attacking side channels that cross a nominal boundary (A40100
  server+client collusion; A39721 semi-honest routing observation).
- **Covert channels invisible at the content layer** — A37125 (image steganalysis Pe ≈ 0.5 against standard
  CNN steganalyzers) and A40903 (linguistic stego text equals cover) mean a boundary cannot rely on content
  inspection to catch exfiltration; it must be destination/capability-based.

---

## Threat model

Adopt a fail-closed model that assumes an agent's *reasoning can be subverted*, a *peer/sub-agent can be
compromised*, and the enforcement lives only in the boundary — not in the endpoints' cooperation.

- **In-scope adversaries (grounded):**
  - *Injection into any model-visible field* steering an agent to reach a disallowed destination (A42239,
    A42249).
  - *Compromised internal/sub-agent supply chain* that inserts network/exfiltration primitives and initiates
    outbound traffic (A41134 BU-MA, author-reported).
  - *A capable dual-use agent* attempting lateral movement / pivoting from its zone (A40210).
  - *Colluding infrastructure parties* attacking isolation side channels that cross a boundary (A40100;
    A39721).
  - *Coordinated / malfunctioning peer agents* in a multi-agent fabric (A41065).
- **Trust boundary:** the model, its prompt, its tool outputs, agent-generated code, and traffic sourced from
  any zone are **untrusted** until authorized at the boundary. The corpus rule is that the environment/gate —
  not prompt hygiene — enforces the boundary (A42239, A42249). The segmentation control plane (policy engine +
  enforcement points) is the trusted computing base.
- **Assumed-but-fragile in the corpus (call these out as risk):** inputs, telemetry, and labels are treated as
  trusted across the detector papers (Network-Cyber-Security §3, reviewer synthesis). A boundary intrusion
  detector (NIDS) must not be assumed to have ground-truth labels — real-world detection is modest (A42369).
- **Explicitly NOT covered by the corpus evidence:** an **adaptive, defense-aware attacker** who reshapes
  traffic, obfuscates destinations, or splits egress to evade the specific segmentation policy. A41134 states
  its defense was "not tested against an adaptive attacker who rewrites Pm to evade Padv." Every containment
  claim here is therefore a non-adaptive upper bound.

---

## Control mechanism

Network segmentation composes corpus-grounded primitives applied at the transport/zone boundary, in fail-closed
order:

1. **Default-deny zone boundaries (least-privilege reachability).** Partition into trust domains; deny all
   cross-zone and egress traffic by default and allow-list only the specific source→destination→port/protocol
   flows a workload needs. Directly motivated by A42249 ("capability is not permission"; least-privilege /
   just-in-time) and A41134 (least-privilege capability isolation that blocks outbound email/network from
   generated apps). Separating trust domains is the agent-identity principle (`agent-identity.md`, reviewer
   synthesis).
2. **Environment-side connection-admission gate *before* the flow opens.** The boundary admits a flow only if
   it is on the allow-list, **regardless of what the model or workload decided** — the same environment-side,
   allow-list-not-prompt-hygiene principle A42239 (reject out-of-set) and A42249 (command-validation gate
   between intent and execution) establish for actions, applied to connections. This is deterministic and does
   not trust the endpoint to stay in-policy. Reviewer-synthesis reinforcement: a pre-action gate that halts
   *before* the operation fires (`architecture-patterns.md` P1, reviewer synthesis).
3. **Egress control with a signature/destination policy.** Deny-by-default outbound; allow-list destinations;
   instrument the network-relevant members of the A41134 12-behavior taxonomy (`send_email`, external URL
   fetch, ransomware/C2 patterns) as block-and-alert signatures — while accepting that content-layer inspection
   alone misses covert channels (A37125, A40903), so egress must be **destination/capability-based plus
   provenance attestation**, not content matching.
4. **Boundary telemetry and intrusion detection as triage.** Monitor east-west and egress flows with a
   cross-dataset NIDS (A38682 TriFusion-IDS, multimodal graph-tabular-text, evaluated cross-dataset for
   unseen-attack transfer; author-reported), and compress high-volume endpoint/east-west telemetry before
   reasoning (A40815 HyperGLLM, 1M+-token EDR samples). Treat detector outputs as **noisy triage, not gates**
   — real-world detection F1 is modest (A42369; DiverseVul 0.307, Reveal 0.486 author-reported), so a NIDS
   alert should raise scrutiny, not silently authorize a flow.
5. **Side-channel isolation across the boundary.** In multi-tenant / split / offloaded hosting, isolate memory,
   activations, caches, and routing metadata — not just the payload (A40100 activation inversion; A39721
   oblivious select-then-compute as a reusable primitive). "Payload encrypted across the segment" does not
   imply confidentiality.
6. **Blast-radius containment + quarantine.** Bound how many credentials/capabilities one compromised zone can
   wield (`k`; `architecture-patterns.md` P6, reviewer synthesis) and quarantine a misbehaving node — A41065
   (author-reported: task-accuracy evidence, not measured attack-success — reviewer caveat) uses reputation-
   based, gossip-propagated isolation to remove a compromised/malfunctioning agent from the collective.

Layering is deliberate: the corpus's strongest cross-paper theme is that **single-point defenses are
insufficient; layered / multi-point defense is required** (Network-Cyber-Security §15; Defense-Mitigation §9,
convergent across A40432, A41134). Segmentation is one layer, not a complete control.

---

## Preconditions and trust assumptions

- **A real enforcement boundary exists** (firewall / security group / service-mesh policy / VLAN / physical
  air-gap / VM/network namespace) whose enforcement does not depend on the endpoint's cooperation. The
  boundary must be one the model/workload "cannot be talked past" (A42239, A42249).
- **The set of legitimate flows is enumerable** enough to express an allow-list. Well-scoped
  service-to-service topologies are the cleanest fit (analogue of the classify/route-to-fixed-set workflow
  A42239 gates cleanly); genuinely open-ended egress degrades the allow-list toward a leaky deny-list (see
  *When NOT to use*).
- **Isolation covers side channels, not just packets.** Do not assume "different subnet / process-separated"
  implies confidentiality — activations (A40100) and routing/expert-selection metadata (A39721) leak input
  under collusion; shared caches and co-residency are in scope.
- **The NIDS is triage, not an oracle.** Real-world detection F1 is modest (A42369) and detectors drift over
  time (A37053 time-aware TESSERACT splits vs inflated IID; author-reported), so boundary detection must be one
  signal among several and re-evaluated under distribution shift, never the sole authority to permit a flow.
- **Labels/telemetry feeding the boundary detector may be noisy** (Network-Cyber-Security §3; A42369
  identifier-leakage/synthetic-inflation caveats) — do not treat a detector's "benign" as ground truth.
- **Consensus/authorization primitives have residual leakage.** Multi-party model-access control leaves
  residual unauthorized activation (A40925 ~15% Acc-Fusion, author-reported) — a cross-zone authorization gate
  bound to model execution is bounded, not airtight.

---

## System architecture

Fail-closed boundary pipeline (each stage defaults to *deny* on error/ambiguity):

```
 workload / agent / sub-agent wants to open a flow (east-west or egress)
        │  (untrusted: model output, tool results, retrieved text, sub-agent-sourced traffic)
        ▼
 [1] CONNECTION-ADMISSION GATE  ── environment-side allow-list (src→dst→port/proto); deny out-of-set
        │      (A42239 reject-at-gate · A42249 command validation · pre-action gate, arch-patterns P1 RS)
        │  deny → REJECT (fail-closed, logged)
        ▼
 [2] TRUST-ZONE BOUNDARY  ── default-deny between zones; only task-required flows
        │      (A42249 least-privilege/JIT · A41134 block outbound net/email · separate trust domains, RS)
        │  side-channel isolation of memory/activations/routing across the boundary (A40100, A39721)
        ▼
 [3] EGRESS CONTROL  ── deny-by-default outbound; allow-list destinations; A41134 12-behavior egress signatures
        │      (A41134 egress control · covert-channel caveat A37125/A40903 → destination/provenance, not content)
        ▼
 [4] BOUNDARY DETECTION (TRIAGE, not gate)  ── cross-dataset NIDS on east-west/egress flows
        │      (A38682 TriFusion-IDS · A40815 compress-then-reason telemetry · A42369 detectors are triage)
        │  cross-zone high-value access → HUMAN / MULTI-PARTY AUTHORIZATION (A42249, A40925)
        ▼
 [5] TRAJECTORY-LEVEL FLOW LOG  ── continuous ordered record of process/network/file/tool actions
        │      (arch-patterns P5 RS · A40210 trajectory competency · A42249 interaction logs · autonomy trace)
        │
        └──► CONTAINMENT: quarantine/isolate misbehaving zone (A41065), cap blast radius k (arch-patterns P6 RS)
```

Design notes:

- The gate at [1] is **deterministic and environment-side** by construction; it does not ask the model or
  workload to self-police (A42239, A42249; A41134 BU-MA lesson that endpoint guardrails fail against a
  compromised peer).
- [4]'s NIDS output is advisory: it raises scrutiny and can trigger containment, but a green NIDS result never
  *authorizes* a flow that the [1] allow-list would deny (A42369 detectors-as-triage).
- Prefer a **cheap, constant-time inline admission check** at [1] over an external policy service whose
  latency grows with trajectory length (`architecture-patterns.md` P1/P9, reviewer synthesis).

---

## Recommended implementation pattern

1. **Partition into trust zones and default-deny between them.** No standing east-west reachability; allow-list
   only the specific source→destination→port/protocol flows each workload needs. (A42249 least-privilege/JIT;
   A41134 block outbound network/email from workloads; separate trust domains, `agent-identity.md` reviewer
   synthesis.)
2. **Enforce the boundary environment-side, before the flow opens.** Admit a connection only if it is on the
   allow-list, irrespective of what the endpoint/model decided; log every rejection. (A42239 reject-out-of-set;
   A42249 command-validation gate.)
3. **Deny-by-default egress; allow-list destinations.** Instrument the network-relevant A41134 12-behavior
   signatures (`send_email`, external URL fetch, ransomware/C2) as block-and-alert; make egress
   destination/capability-based **plus** provenance attestation, because content DLP misses covert channels
   (A37125, A40903).
4. **Monitor the boundary with a cross-dataset NIDS as triage.** Deploy A38682-style multimodal NIDS evaluated
   for unseen-attack transfer; compress high-volume east-west/EDR telemetry before reasoning (A40815). Never
   let a detector's "benign" verdict authorize a flow (A42369).
5. **Require human / multi-party authorization for cross-zone access to high-value assets** — reaching an
   auth/credential/model-execution service from a lower-trust zone. (A42249 human approval on consequential
   actions; A40925 threshold authorization bound to execution.)
6. **Isolate side channels across the boundary** (memory/activations/caches/routing), not just packets, in any
   multi-tenant / split / offloaded hosting (A40100; A39721 oblivious select-then-compute).
7. **Cap blast radius and enable quarantine.** Bound `k` (credentials/capabilities one compromised zone can
   wield; `architecture-patterns.md` P6, reviewer synthesis) and support reputation-based isolation of a
   misbehaving node (A41065).
8. **Log flows at trajectory granularity.** Keep a continuous ordered record of process/network/file/tool
   actions with host+user context, reasoned over for *how flows connect* (behavioral-sequence, not signature)
   — the literal autonomy trace (`architecture-patterns.md` P5, reviewer synthesis; A40210; A42249).
9. **Layer complementary controls** — admission gate + zone boundary + egress control + NIDS + quarantine —
   because single-point defense leaks (Network-Cyber-Security §15; A40432, A41134 layered-defense theme).

Bias every default toward **deterministic, fail-closed, least-privilege**: on any policy-lookup error,
detector uncertainty, or timeout, **deny/defer** the flow (A37053 reject-as-first-class-action) and route to
review rather than fail open.

---

## Incorrect or fragile implementation patterns

- **Flat network / default-allow east-west "for convenience."** This is the transport-layer form of the A42249
  broad-standing-privilege failure (100% unauthorized-install under broad privilege) and exactly what lets a
  dual-use agent pivot (A40210).
- **Trusting the endpoint/model to choose its own destinations (prompt-only "please don't exfiltrate").**
  A41134 BU-MA is the direct counter-example — endpoint-level guardrails reduced ASR by only **7%** against an
  internally compromised agent (author-reported). Guardrail *text* is not a boundary.
- **Letting the model/agent decide the connection target from a model-visible field.** A42239 shows
  authoritative text inside a candidate option drives off-policy choice (E-adoption ≈0.5); a boundary that
  reads the model's chosen destination instead of enforcing an allow-list can be talked past.
- **Content-inspection egress/DLP as the only outbound control.** Covert channels are invisible at the
  content layer (A37125 steganalysis Pe ≈ 0.5; A40903 stego-equals-cover) — destination/capability policy plus
  provenance attestation is required, not payload matching.
- **Treating a NIDS/detector as an authorization oracle.** Real-world detection F1 ≈ 0.3–0.6 (A42369) and
  detectors drift (A37053); gating flow-permit on detector output alone both under-blocks novel attacks and
  drifts stale.
- **Segmenting packets but sharing memory/activations/caches/routing across the boundary.** Leaks input via
  side channels under collusion (A40100) or access-pattern observation (A39721).
- **A single boundary as the whole defense.** Single-point defense leaks (A40432, A41134); segmentation must be
  layered with an admission gate, egress control, detection, and quarantine.
- **Certifying the boundary on IID/synthetic traffic only.** Synthetic benchmarks vastly overstate real-world
  performance (A42369 Juliet 0.900 vs DiverseVul 0.307, author-reported); a NIDS validated only on in-
  distribution flows will look far stronger than it is.

---

## Verification strategy

- **Assert default-deny at the boundary as the acceptance test.** For every non-allow-listed source→destination
  →port flow, verify the connection is denied and logged — the environment-side allow-list must reject
  out-of-set flows regardless of endpoint intent (A42239, A42249).
- **Distribution-shift-honest evaluation of the NIDS.** Do not certify on IID/synthetic-only traffic — it
  inflates scores (A42369 synthetic-vs-real gap; A37053 time-aware TESSERACT splits; A38682's own cross-dataset
  / unseen-attack protocol is the right posture). Use seeded, leakage-controlled splits (A42369).
- **Cross-zone reachability audit.** Enumerate actually-reachable source→destination pairs and diff against the
  intended allow-list; any unexpected reachable pair is a fail-closed finding (motivated by A42249
  broad-reach → incident).
- **Egress-coverage test.** Attempt each network-relevant A41134 12-behavior primitive (`send_email`, external
  URL fetch, C2/ransomware pattern) from inside a zone and assert block-and-alert.
- **Side-channel probe.** From a co-resident/colluding position, attempt input reconstruction via
  activations/routing across the boundary and assert isolation holds (A40100, A39721).
- **Trajectory-level, not per-flow, review.** Score behavior over whole multi-stage traces — collusive/pivoting
  attacks look benign per individual flow (A40210 competency scoring; `architecture-patterns.md` P5, reviewer
  synthesis).
- **Report absolute residuals, not only relative reductions** (A41134 relative-vs-absolute caveat; A40925
  residual ~15%). Multi-seed with confidence intervals (A42369).

---

## Metrics and thresholds

Corpus-grounded KPIs (targets are engineering choices, **not** corpus-certified; report absolute values and
qualify to the tested attacks under a non-adaptive threat model):

- **Unauthorized cross-zone reachability count → target 0.** Any source→destination pair reachable but not on
  the allow-list is a fail-closed blocker (motivated by A42249 broad-reach → 100% unauthorized-install).
- **Out-of-allow-list / denied-flow attempt rate.** A42239 E-adoption is the loggable analogue; spikes in
  attempted out-of-set connections are incident indicators — the boundary denies them; monitor the attempted
  rate.
- **Egress-block coverage** across the network-relevant A41134 12-behavior set (`send_email`, external URL
  fetch, C2/ransomware).
- **Attack-Success-under-Defense (ASR-d), absolute.** A41134 (author-reported) MU-BA reductions 73/40/49% vs
  BU-MA 45/7/42% show relative reductions can hide high residual attack success — publish absolute ASR-d,
  especially for the compromised-peer (BU-MA) case, which most resembles a lateral-movement scenario.
- **Boundary-NIDS reliability context:** treat real-world detection F1 as ≈ 0.3–0.6 (A42369) — do **not** set a
  flow-permit threshold that assumes oracle-quality detection; report precision/recall on a cross-dataset,
  unseen-attack split (A38682).
- **Blast-radius bound `k`** — number of credentials/capabilities one compromised zone can wield; the
  containment budget to minimize (`architecture-patterns.md` P6, reviewer synthesis).
- **Residual cross-zone authorization leakage** — where a cross-zone gate is bound to model execution, report
  residual unauthorized-activation (A40925 ~15% Acc-Fusion, author-reported).
- **Over-blocking / exaggerated-safety rate** as a first-class metric alongside recall, so a too-tight boundary
  does not silently erode utility until operators punch holes in it (`architecture-patterns.md` P8, reviewer
  synthesis).

All thresholds are **non-adaptive** estimates; qualify every target to "against the tested attacks under the
evaluated threat model."

---

## Test cases

Concrete, corpus-derived cases (each should pass fail-closed):

1. **Denied lateral flow.** A workload in a low-trust zone attempts an east-west connection to a peer not on
   its allow-list → boundary denies and logs; no reachability (least-privilege reachability; A42249 analogue).
2. **Compromised sub-agent egress.** A BU-MA-style pipeline where a sub-agent inserts a `send_email`
   exfiltration primitive attempts outbound → egress control blocks; A41134 12-behavior signature alerts;
   delivery/flow halted (A41134).
3. **Injection-chosen destination.** Authoritative "contradiction" text in a tool result instructs the agent to
   connect to an attacker host → environment-side allow-list rejects the out-of-set destination regardless of
   the model's choice (A42239).
4. **Cross-zone reach to a privileged service.** An agent in a general zone attempts to reach the
   auth/credential/model-execution service → denied unless explicitly allow-listed and, for high-value access,
   gated behind human / multi-party authorization (A42249, A40925).
5. **Lateral movement / pivot by a dual-use agent** confined to its sandbox zone with scope/rate limits; no
   reach to production zones; full flow trajectory logged (A40210).
6. **Side-channel probe across the boundary:** a co-resident/colluding party attempts input reconstruction from
   activations or routing metadata → isolation covers side channels; oblivious routing where applicable
   (A40100, A39721).
7. **Covert-channel egress** invisible to content DLP → destination/capability egress policy blocks it even
   though content inspection sees nothing anomalous (A37125, A40903).
8. **OT/ICS isolation:** an IT-zone host attempts to reach a control-network endpoint → denied at the IT↔OT
   boundary (SWaT-style control network; A39770 indirect grounding).
9. **Unseen-attack traffic** on the boundary NIDS → detector flags as triage (raises scrutiny / triggers
   containment) but does not by itself authorize any flow (A38682 cross-dataset; A42369 triage-not-gate).

---

## Adaptive adversarial tests

The single largest corpus gap is the **absence of adaptive-adversary evaluation** (Network-Cyber-Security
§9/§12; A41134 explicit). This pattern must be red-teamed with a defense-aware attacker before any assurance
claim:

- **Egress reshaping to evade the destination/signature policy** — the exact test A41134 did not run ("rewrites
  Pm to evade Padv"); obfuscate destinations, tunnel over allowed ports/protocols, split egress across
  channels, and mutate `send_email`/URL-fetch primitives.
- **Traffic-shaping / mimicry to evade the boundary NIDS** — craft flows that resemble allow-listed benign
  traffic (analogous to fraud camouflage / borderline structuring near the decision boundary in A38541/A38588).
- **Injection relocated across model-visible fields** to smuggle a target destination — options, tool results,
  retrieved text — cycling styles (A42239 shows style matters; test denied-attempt rate and task accuracy
  separately).
- **Collusion attacks on isolation** — server+client (A40100) and routing-observation (A39721) reconstruction
  across a nominal boundary.
- **Partial-trigger / consensus-gaming** against any cross-zone authorization bound to model execution (A40925
  residual ~15% Acc-Fusion).
- **Compromised-peer (BU-MA) escalation** attempting to reach outward and pivot despite endpoint guardrails
  (A41134).
- **Continuous, memory-driven adaptive red-team in CI/CD**, grounded in policy and validated by a deterministic
  judge (`architecture-patterns.md` P11/P12, reviewer synthesis).

Report results as **absolute** ASR / escape / reachability under the adaptive attacker, not relative reductions.

---

## Telemetry requirements

Log at trajectory granularity as the audit substrate (`architecture-patterns.md` P5, reviewer synthesis; A40210;
A42249; autonomy-trace console):

- **Per-flow admission decision** (allow/deny/defer), the allow-list rule fired, and the requested
  source→destination→port — so a denied out-of-set attempt is attributable (A42239 off-policy selection as
  incident signal).
- **Egress events** matched against the network-relevant A41134 12-behavior taxonomy (`send_email`, external
  URL fetch, C2/ransomware) with destination.
- **Boundary-NIDS alerts** with the cross-dataset context they were scored under (A38682), treated as triage
  signals — never as authorization.
- **Continuous ordered record** of process/network/file/tool actions with host+user context, reasoned over for
  *how flows connect* (behavioral-sequence, not signature) — the literal autonomy trace
  (`architecture-patterns.md` P5, reviewer synthesis).
- **Security-incident tags:** unexpected cross-zone reachability, unauthorized privileged-service access,
  brute-force/login attempts, and navigation/connection into sensitive zones (A42249) — each should trigger
  containment.
- **Per-zone/per-agent reputation & anomaly signals** and quarantine/isolation events in multi-agent settings
  (A41065).
- **Blast-radius indicators:** count of distinct credentials/capabilities a single zone has exercised (`k`;
  `architecture-patterns.md` P6, reviewer synthesis).

Caveat: content-layer telemetry alone can miss covert channels (A37125, A40903) — pair flow logs with
destination/provenance attestation.

---

## Failure handling

Fail-closed everywhere:

- **On policy-lookup error, ambiguity, timeout, or detector uncertainty → deny/defer the flow**, routing to
  human review as a first-class action (A37053 explicit reject/defer; A42249 human approval on consequential
  cross-zone access). Never fail open into default-allow.
- **On a detected egress signature or unauthorized cross-zone attempt → block + alert + halt** before it
  completes (A41134 "before delivery"; A42249 monitorable signals trigger containment).
- **On a NIDS alert → raise scrutiny / trigger containment, but do not use its absence as permission** (A42369
  triage-not-gate).
- **Never silently over-block into uselessness** — measure exaggerated-safety and prefer "prove before you
  veto," so operators do not punch permanent holes in the boundary and create blind spots
  (`architecture-patterns.md` P8, reviewer synthesis).
- **Degrade to a narrower reachability set** rather than widening reachability on failure (least-privilege
  default; A42249/A41134).

---

## Rollback and containment

- **Containment is the design goal of segmentation.** A boundary bounds how far a compromise, injection-driven
  action, or error propagates — the network form of the least-privilege / blast-radius principle (A42249;
  `architecture-patterns.md` P6, reviewer synthesis, "cap the blast radius of any single compromise / bound
  `k`").
- **Quarantine/isolate a misbehaving zone or node.** A41065 (author-reported: task-accuracy evidence, not
  measured attack-success — reviewer caveat) uses reputation-based isolation ("social immune response") +
  gossip-propagated isolation to remove a compromised/malfunctioning agent from the collective; those
  isolation events are natural audit signals and map to dynamically tightening a zone boundary.
- **Cap cross-credential blast radius.** Bound how many credentials/capabilities one compromised zone can wield
  and detect coordinated cross-credential misuse, not just isolated abuse (`architecture-patterns.md` P6,
  reviewer synthesis; ties to the least-privilege-credentials pattern).
- **Trigger containment on the A42249 monitorable signals** (unauthorized privileged access, brute-force,
  navigation/connection into sensitive zones) and on unexpected cross-zone reachability.
- **Tighten, don't loosen, under uncertainty** — shrink the allow-list / raise the boundary rather than open it
  when a zone is suspected compromised.

---

## Known bypasses

Demonstrated in the corpus (under the papers' mostly non-adaptive threat models):

- **Compromised internal peers (BU-MA) bypass endpoint-level guardrails** — Adv-IMBIA reduced MetaGPT ASR by
  only **7%** in BU-MA vs 40% in MU-BA (A41134, author-reported); a boundary that relies on endpoint
  cooperation fails against a compromised peer.
- **Injection inside a model-visible field can select a disallowed destination** — E-adoption ≈0.5 (A42239,
  author-reported) if the boundary reads the model's choice instead of enforcing an allow-list.
- **Side channels bypass packet isolation** — activation-based inversion under collusion (A40100); expert-
  selection/routing access-pattern leak (A39721) — input semantics cross a nominal boundary.
- **Covert channels bypass content-inspection egress/DLP** — steganalysis Pe ≈ 0.5 (A37125); stego text equals
  cover at the text layer (A40903).
- **Concept drift degrades a boundary NIDS over time** — IID-trained detectors decay (A37053, author-reported)
  and synthetic benchmarks overstate real-world detection (A42369).
- **Partial-trigger fusion partially bypasses multi-party access control** — residual ~15% Acc-Fusion (A40925,
  author-reported) — a cross-zone authorization gate bound to model execution is bounded, not airtight.
- **Fraud-camouflage-style boundary evasion** — borderline/near-boundary structuring bypasses single-view
  detectors (A38541, A38588), an analogue for traffic crafted to sit just inside benign.

Reviewer-identified (not demonstrated in these papers): an adaptive attacker who reshapes/tunnels/obfuscates
egress to evade the specific segmentation policy (A41134 explicitly untested); Sybil/collusion against the
honest-majority assumption in reputation-based quarantine (A41065, reviewer caveat).

---

## Residual risks

- **No adaptive-adversary evaluation exists in the corpus for boundary controls** — all containment numbers are
  non-adaptive upper bounds (Network-Cyber-Security §9/§12; A41134). Requires production red-team validation
  before reliance.
- **No paper directly measures network segmentation as a control** — this pattern extrapolates from adjacent
  evidence (least-privilege, egress control, boundary detection, side-channel isolation, quarantine); the
  composition itself is engineering judgment, not a measured result, and needs on-stack validation.
- **Residual leakage/attack-success persists under the best evaluated adjacent defenses** — A40925 ~15%
  Acc-Fusion; A41134 high absolute residual ASR in BU-MA; A40432 (analogous layered defense) leaves
  author-reported ~28% residual in its domain. Budget for residual; pair with monitoring and incident response.
- **Boundary-detector unreliability** — real-world NIDS F1 ≈ 0.3–0.6 (A42369) and drift over time (A37053);
  the boundary cannot rely on detection to permit/deny flows.
- **Confidentiality side channels** may persist even with strong packet isolation (A40100 empirical noise only,
  no reported ε; A39721 semi-honest only — malicious case open).
- **Multi-agent/zone quarantine assumes honest-majority/connectivity** (A41065) — unverified against
  Sybil/collusion; its evidence is task-accuracy, not measured attack-success (reviewer caveat).
- **Over-blocking risk** — a too-tight boundary erodes operator trust and invites permanent hole-punching if
  exaggerated-safety is not measured (`architecture-patterns.md` P8, reviewer synthesis).

---

## Relevant research (stable paper ids from the syntheses/cards)

Primary (AAAI-26 cards behind the Network-Cyber-Security synthesis, plus A41134 from Defense-Mitigation):

- **A42249** — Towards Capable and Secure Autonomous Computer-Use Agents (Student Abstract) — "capability is not
  permission"; least-privilege / just-in-time; command-validation gate; human approval on consequential access.
  Network analogue: default reachability is standing privilege. *Core anchor. Evidence: preliminary / small-n.*
- **A41134** — Shadows in the Code (IMBIA); arXiv:2511.18467; code github.com/wxqkk0808/IMBIA
  (Defense-Mitigation) — egress control + least-privilege capability isolation blocking outbound net/email;
  MU-BA vs BU-MA asymmetry (73% vs 7% reduction); 12-behavior egress taxonomy. *Core anchor for egress/lateral.*
- **A42239** — Obedience or Vigilance? (malicious multiple-choice options) — any model-visible field is an
  injection surface; environment-side allow-list, not endpoint trust, chooses the destination. *Core anchor.
  Evidence: preliminary, single model.*
- **A38682** — TriFusion-IDS: multimodal graph-tabular-text contrastive NIDS, cross-dataset / unseen-attack
  transfer on NetFlow-v2 benchmarks — boundary intrusion detection as triage. *Evidence: moderate; non-adaptive.*
- **A40815** — HyperGLLM: hypergraph-enhanced endpoint threat detection compressing 1M+-token EDR telemetry —
  compress east-west/endpoint telemetry before reasoning. *Evidence: moderate (self-generated-label caveat).*
- **A39770** — State-Derivative-Aware NCDE for multivariate time-series anomaly detection, evaluated on **SWaT**
  (real ICS-attack testbed) — indirect grounding for OT/ICS segment isolation. *Evidence: moderate; non-adaptive.*
- **A37144** — Tree-Based Stochastic Optimization for Urban Network Security Games; arXiv:2511.10072 —
  interdiction/patrol equilibrium; where to place defensive chokepoints/boundaries. *Evidence: moderate;
  synthetic instances only.*
- **A40210** — Offensive Security LLM Agents / CTFTiny + CTFJudge; arXiv:2508.05674 — dual-use pivoting;
  isolated-sandbox + authorization/scope limits; trajectory competency. *Evidence: moderate.*
- **A41065** — Resilience in Ambient Multi-Agent LLMs — reputation-based, gossip-propagated quarantine of a
  misbehaving node. *Evidence: moderate (architecture), preliminary (security — task-accuracy, not attack-success).*
- **A40100** — FedSEA-LLaMA; arXiv:2505.15683 — activations are a confidentiality asset (collusion inversion
  across a boundary).
- **A39721** — SecMoE — routing/expert-selection access-pattern leak; oblivious select-then-compute primitive.
- **A40925** — Consensus Learning with Multi-Party Perturbation Triggers — threshold authorization bound to
  model execution; residual ~15% Acc-Fusion.
- **A42369** — VulnBench; code github.com/ijakenorton/VulnBench — detectors/NIDS are triage, not gates
  (real-world F1 ≈ 0.3–0.6; synthetic inflation vs real-world).
- **A37053** — DRMD; arXiv:2508.18839 — reject/defer as a first-class action; time-aware (TESSERACT) evaluation;
  detector drift.
- **A38541 / A38588** — DGP / MH-LGC — fraud camouflage / borderline structuring as a boundary-evasion analogue.
- **A37125 / A40903** — image / linguistic steganography — covert channels invisible at the content layer
  (egress cannot rely on content inspection).

Broader Origin corpus (reviewer synthesis — source file noted; numbers not re-verified against primary cards):

- **`architecture-patterns.md` P1** — pre-action gate that halts before the operation fires; constant-time
  inline check.
- **`architecture-patterns.md` P5** — continuous operational record of process/network/file/tool actions;
  trajectory-level, behavioral-sequence reasoning (the literal autonomy trace).
- **`architecture-patterns.md` P6** — least-privilege credential broker; cap blast radius / bound `k`; detect
  coordinated cross-credential misuse.
- **`architecture-patterns.md` P8** — anti-over-blocking; measure exaggerated-safety, prove-before-veto.
- **`agent-identity.md`** — separate trust domains; Zero Standing Privilege; intent-based access; attenuated
  delegation chains.

---

## Evidence strength

- **Direction of the pattern: well-supported by analogy, not by a direct segmentation study.** That capable and
  potentially-compromised agents need least-privilege boundaries, environment-side fail-closed gating, egress
  control, boundary detection-as-triage, side-channel isolation, and blast-radius containment is convergent
  across independent studies (A42249, A41134, A42239, A40210, A38682, A40100/A39721, A41065) and reinforced by
  the corpus-wide layered-defense theme (Network-Cyber-Security §15). **No corpus paper studies "network
  segmentation" by name**, so the specific composition is engineering extrapolation.
- **Specific numbers: paper-specific, non-adaptive, and mostly preliminary.** The cleanest agent-security
  anchors (A42249, A42239) are small-n / single-model / version-bound; A41134 is author-reported with an
  LLM-judge (GPT-4o, author-reported 86.34% agreement) and reports relative reductions; A38682/A40815/A39770
  are non-adaptive detectors; A41065's security evidence is task-accuracy, not measured attack-success. The
  blast-radius / trust-domain / autonomy-trace framing comes from `architecture-patterns.md` and
  `agent-identity.md` reviewer synthesis and was not re-verified against primary cards.
- **Critical caveat:** **no paper evaluated an adaptive, defense-aware attacker** against a segmentation
  boundary — a *replicated absence* (Network-Cyber-Security §9/§12; A41134 explicit), the strongest
  methodological finding and the most important calibration. All containment claims must be stated as "reduced
  attack success / contained blast radius against the tested attacks under the evaluated non-adaptive threat
  model," never "secure." **Production validation and adaptive red-teaming are required before operational
  reliance.**

---

## When NOT to use this pattern

- **When the legitimate flow set is genuinely open-ended and cannot be reduced to an allow-list.** The
  environment-side admission gate is strongest for well-scoped service-to-service topologies (A42239 analogue);
  an unbounded egress space degrades the allow-list into a leaky deny-list — combine with least-privilege
  workloads and human/multi-party authorization rather than treating the boundary as sufficient.
- **When confidentiality of intermediate state is the primary requirement and the deployment is multi-tenant /
  split / offloaded.** Packet/zone segmentation does not by itself close activation/routing side channels
  (A40100, A39721) — this needs cryptographic/oblivious techniques, not just a network boundary.
- **As a standalone or "sufficient" control.** Single-point defense leaks (A40432, A41134); a boundary not
  layered with an admission gate, egress control, detection, quarantine, and monitoring is not a complete
  control (Network-Cyber-Security §15).
- **As a detection oracle.** A boundary NIDS is triage — real-world F1 ≈ 0.3–0.6 (A42369) and it drifts
  (A37053); do not permit/deny a flow solely on detector output.
- **Where over-blocking would drive operators to punch permanent holes in the boundary.** If exaggerated-safety
  cannot be measured and tuned, an over-tight boundary can create worse blind spots than it prevents
  (`architecture-patterns.md` P8, reviewer synthesis); invest in prove-before-veto and precision tuning first.
- **When the threat is a subverted endpoint that is itself allow-listed.** Segmentation limits *reach*, not the
  legitimacy of an authorized peer — a compromised but allow-listed node (A41134 BU-MA) still needs
  trajectory-level detection, quarantine, and blast-radius caps, not just a boundary.
