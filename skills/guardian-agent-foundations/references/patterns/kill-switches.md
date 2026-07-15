# Pattern — Kill Switches (Emergency Halt and Containment)

> **Control class.** Containment control in the corpus's Capability · Permission · Verification · Evidence ·
> Residual-risk (CPVER) ontology: a deterministic, out-of-band, fail-closed mechanism that, on a trigger
> (human operator command or an automated tripwire), **removes Capability** (kills the process/sandbox,
> revokes credentials, quarantines poisoned state) and **overrides Permission** (denies all further
> consequential action) for one agent or a fleet, and **emits tamper-evident Evidence** of the halt. It is
> actuated by a Verification/Detection signal and sized against a **Residual-risk** budget. It is the
> emergency-stop / circuit-breaker sibling of the per-action `human-approval-consequential-actions` gate and
> the standing `policy-permission-gates` allow/deny gate: those decide *before* each act; the kill switch
> *interrupts and contains* an already-running trajectory.
>
> **Evidence integrity (non-negotiable).** Every claim traces to a card in the AAAI-26 corpus via its stable
> paper id, drawn from `syntheses/Defense-Mitigation.md` and `syntheses/AILLM-Safety.md` and their underlying
> cards. Author-reported results are labeled as such and kept distinct from reviewer synthesis. All magnitudes
> are as reported by the cited paper *under that paper's own evaluated (largely non-adaptive) threat model* and
> are **not independently verified**. Where the corpus is silent, the text says "not stated in paper." Language
> is calibrated ("reduced ASR/CRR against the tested attacks", "demonstrated under the evaluated threat model",
> "not evaluated against", "requires production validation"); no absolutes ("secure", "unbreakable", "proven
> safe", "guaranteed stop") are used.
>
> **The load-bearing honesty for this pattern:** *no paper in the corpus builds or evaluates a "kill switch /
> emergency stop" as an integrated control.* Every mechanism below is corpus-grounded — a runtime execution
> gate (A41468 Layer 3), an agent-side `refuse()`/abstain primitive (A41090), knowledge erasure as
> incident-containment (A41145 ROME), an invalid-action tripwire (A39818), immutable audit (A41468 Layer 4),
> and the "compromised agents defeat user-level guardrails" finding that forces out-of-band enforcement
> (A41134) — but their *assembly into a kill switch, and its adaptive-attacker evaluation, is reviewer
> synthesis requiring production validation.* The corpus's single most consistent gap is the near-total
> absence of adaptive-attacker evaluation of defenses (`defense-in-depth` §0; `AILLM-Safety` §16–17;
> `Defense-Mitigation` §9.3); treat every number here as a best-case upper bound.

---

## Problem addressed

An autonomous LLM/agent can enter a state where continued execution causes escalating, often irreversible,
external harm — because it was compromised (indirect prompt injection, tool poisoning, a backdoored fine-tune),
because it is being extracted/abused, or because it is simply behaving off-policy. The corpus establishes that
the mechanisms that would *prevent* the individual bad action are not robust enough to rely on alone: no
inference-time refusal defense drives attack success to a safe floor (A42191 ~31% residual ASR; A40248 ~16%
residual harmful on Qwen-3-8B despite near-zero on its prefill metric; A41468 material residual on its hardest
agent classes — all author-reported), and prompt-level safety is **necessary-but-insufficient at the action
layer** (A41090; A41468). When a bad trajectory is already in flight, the design need is different from
"decide whether this next act is allowed" — it is *"stop everything now and contain the blast radius."*

The kill switch exists to make that stop **deterministic, out-of-band, and independent of the agent's
cooperation**. This is forced by the corpus's sharpest architectural result: **compromised internal agents
defeat user-level guardrails** (A41134's BU-MA scenario — for MetaGPT the author-reported ASR reduction under a
compromised-agent supply chain is only 7%, vs 40% when the same guardrail faces a malicious user). If a
guardrail an agent can influence largely fails once the agent is the adversary, then a halt implemented as
"ask the agent to stop" is the wrong shape. The switch must act *below* the agent — at the credential broker,
the tool proxy, the sandbox/process — where the agent has no write influence. **Capability ≠ Permission ≠
safety** (`AILLM-Safety` §6; A41090, A41468): removing the capability is the only reliable stop.

## Applicable assets and attack surfaces

- **The agent's action space / actuators** — payment/transfer calls, file deletion, credential use,
  access-control changes, outbound messages, code execution, physical actuation. A41468
  (InfrastructureSentinel) enumerates the fullest MCP action surface in the corpus: insecure tool use /
  command injection, privilege escalation, tool poisoning / supply chain, credential exposure, DoS — each a
  reason a running agent may need to be halted mid-flight.
- **The credential / capability grant** the agent holds. Least-privilege, revocable capability tokens are the
  containment lever the switch pulls (`least-privilege-credentials`; `AILLM-Safety` §14 pairs least privilege
  with human approval). Revoking the grant kills the agent's *power* even if its process keeps running.
- **The execution substrate** — the process, container, or sandbox. `sandboxed-execution` is the enforcement
  boundary the switch actuates through; killing it removes capability deterministically.
- **Multi-agent pipelines and fleets.** A compromised or malicious internal agent (A41134 BU-MA) can propagate
  down a pipeline (e.g., a tester agent silently adds a `send_email` exfiltration function). A fleet-level halt
  must be reachable *independent of the agents*, because agent self-policing is what BU-MA defeats.
- **Poisoned or memorized model state** as a containment target. A41145 (CoSPED) uses ROME model editing as
  *targeted incident-containment / erasure* of memorized content without full retraining (author-reported
  extraction 65.2% → 1.6%) — a "knowledge kill switch," distinct from a process halt.
- **The trigger surface itself** — the tripwire logic and the operator command channel. A new trust-decision
  surface introduced by a defense is itself attackable (A39732's robustness-aware aggregation weight is a
  gameable surface — reviewer synthesis): an adversary may try to *suppress* a needed halt or *induce* a
  spurious one (denial-of-service). The switch's own controller must not be an injectable LLM ("the Guardian
  LLM is itself an injectable trust anchor" — reviewer synthesis on A41468).
- **The audit/evidence trail** the halt writes. Tamper-evidence and formal guarantees for guardian/audit
  layers are *asserted, not demonstrated* in the corpus (A41468; `AILLM-Safety` §17) — the record of a halt is
  a surface an attacker will want to forge or erase.

## Threat model

Under the corpus's dominant, most product-relevant threat models (`AILLM-Safety` §3; `Defense-Mitigation` §3):

- **Compromised / malicious internal agent (the defining case).** A41134 BU-MA: the agent the switch is meant
  to stop is itself the adversary and will not cooperate with a halt it can observe or influence; user-level
  guardrails largely fail against it (author-reported 7% ASR reduction for MetaGPT under BU-MA vs 40% under
  MU-BA). The switch must therefore be enforced out-of-band, at a layer the agent cannot reach.
- **External attacker via indirect prompt injection.** Plants instructions in environment/tool content the
  agent reads to drive a harmful trajectory or to *disable the operator's ability to intervene* (A41090 models
  injection into the observation stream; A41468 taxonomizes tool poisoning, privilege escalation, context/
  memory manipulation). The attacker needs neither model internals nor operator credentials.
- **Adversary who attacks the trigger.** Two directions, both grounded:
  - *Suppress the halt* — game the automated tripwire so the switch never fires. Automated triggers keyed
    solely on a gameable score are spoofable ("a certificate/score is not a correctness oracle" — A37924);
    backdoors can be tuned to evade loss-dynamics detection (A40472, author-reported CV of the loss
    differential often negative); query-efficient attacks complete before volume-anomaly tripwires accrue
    (single query A40919/A40465; ≤10 A41058; <15 A40554).
  - *Weaponize the halt into denial-of-service* — force the switch to fire spuriously and repeatedly. A37924
    records abstention itself as **denial-of-service**: a fail-closed "halt when uncertain" mechanism becomes a
    DoS primitive if an adversary can cheaply drive it into the halt state. This is the central design tension
    of this pattern (see Failure handling).
- **Defense-aware (adaptive) adversary.** The corpus's highest-confidence meta-finding: wherever an attacker is
  allowed to be defense-aware, static defenses degrade or fail (`defense-in-depth` §0). An adaptive attacker
  will target the *weakest element of the halt path* — most likely the tripwire that must fire, the controller
  that must decide, or the audit that must record. Composed controls do not self-compose: guard stacks passing
  per-component evaluation collapsed under a whole-pipeline adaptive attack (A41108 STACK ~0%→71%; A41144 MFA
  58.5% across 17 VLMs).

**Out of scope for this pattern** (handled by sibling patterns): training-time poisoning/backdoors of alignment
as a *detection/prevention* problem (A40472, A41087, A41118 → `backdoor-detection`, `adversarial-training`);
per-action pre-invocation approval (→ `human-approval-consequential-actions`); the noisy detector that *feeds*
the trigger (→ `runtime-anomaly-detection`); and multimodal generative-content safety. The kill switch is the
*actuator and containment* control; it consumes those layers' signals and enforces the stop.

## Control mechanism

A **deterministic, out-of-band containment actuator** with three decoupled parts: **trigger → decision →
actuation**, plus an evidence leg. Grounded in A41468's runtime execution gate + immutable audit, A41090's
agent-side abstain primitive, and A41134's out-of-band-enforcement requirement.

1. **Trigger (Verification/Detection).** The switch fires on either:
   - a **human operator command** over an authenticated, out-of-band channel (always available; the primary,
     highest-trust path); or
   - an **automated tripwire** — a deterministic signal, not a single gameable score. Corpus-grounded
     tripwires: invalid-action-rate spike (A39818's action-validity gating / invalid-action rate as a runtime
     health signal; A41134 stage-dependent risk), insertion of egress/exfiltration primitives in agent-
     generated code (A41134's 12-behavior taxonomy — `send_email`, external-URL fetch, clipboard/keyboard
     capture, file encryption — doubles as concrete halt signatures), recursive topic-expansion / memory-driven
     query patterns (A40432 extraction signal), or clusters of large-radius certificates on near-duplicate
     inputs (A37924). These are **triage aids that actuate a deterministic stop**, never the sole
     correctness oracle (A37924; `runtime-anomaly-detection`: "a detector is a noisy triage aid, not a gate").
2. **Decision (deterministic, not model-mediated).** A hard control-plane rule maps trigger → halt scope
   (this action / this agent / this fleet / this capability class). The decision component must **not** be an
   injectable LLM ("the Guardian LLM is itself an injectable trust anchor" — reviewer synthesis on A41468). On
   uncertainty about safety, the *enforcement* default is **halt** (fail-closed toward containment) — while the
   *trigger authority* is authenticated and rate-limited so the halt cannot be weaponized into DoS (A37924).
3. **Actuation (Capability removal + Permission override), out-of-band.** The stop is enforced *below* the
   agent, independent of its cooperation (A41134 BU-MA):
   - **Revoke the capability/credential grant** at the broker/proxy (`least-privilege-credentials`) — the agent
     loses power even if its loop continues.
   - **Block at the tool/execution gate** (A41468 Layer 3 runtime execution gate) so no further consequential
     tool call is reachable.
   - **Terminate/quarantine the process or sandbox** (`sandboxed-execution`) for a hard stop.
   - For **fleet halt**, actuate at a shared control-plane chokepoint (broker/proxy/orchestrator), not by
     messaging each agent.
   - Optionally **erase/quarantine poisoned state** — ROME-style targeted knowledge editing as
     incident-containment without full retraining (A41145, author-reported 65.2% → 1.6%).
4. **Evidence (immutable audit).** Emit a tamper-evident record of trigger, scope, decision, actuation, and
   post-halt state (A41468 Layer 4). A check that passed is not proof the check was sound (`defense-in-depth`
   CPVER legend); the record is what makes the halt auditable and reversible-where-possible.

The switch is one **layer** in defense-in-depth, never the sole control (`AILLM-Safety` §14; every defense card
in the corpus ends "should be a layer, not the sole control"). It is the last-resort containment behind
input normalization, trust-boundary isolation, least privilege, and the pre-act approval gate.

## Preconditions and trust assumptions

- **An out-of-band control plane the agent cannot influence.** The trigger channel, decision logic, and
  actuation path must sit outside the agent's write-influence (A41134 BU-MA: anything the agent can reach, a
  compromised agent can defeat). If the only way to "stop" is to instruct the agent, there is effectively no
  kill switch.
- **Revocable, least-privilege capability grants already in place.** The switch's containment lever is
  capability revocation (`least-privilege-credentials`; `AILLM-Safety` §14). Standing/over-broad credentials
  survive a process halt — the corpus's "capability ≠ permission" boundary means killing the loop without
  revoking the grant leaves reachable power.
- **A sandbox/process boundary that can be terminated deterministically** (`sandboxed-execution`) — the
  enforcement substrate for a hard stop. No paper in the corpus evaluated an adaptive attacker against a
  sandbox/gate (`sandboxed-execution` scope note); treat containment completeness as an engineering property to
  be verified, not assumed.
- **Authenticated, rate-limited trigger authority.** Who/what may pull the switch must be authenticated and
  bounded, precisely because a halt is a DoS primitive when weaponized (A37924 abstention-as-DoS). The corpus
  does not evaluate trigger-authority spoofing — treat it as an assumed-secure dependency covered by the
  agent-identity / credential controls.
- **Deterministic, non-model-mediated decision logic.** The halt decision must be a hard rule, not a Guardian
  LLM's judgment (reviewer synthesis on A41468). Tripwire *signals* may be model-derived, but the *actuation*
  must be deterministic.
- **A tamper-evident audit substrate.** Immutable logging is a precondition for the Evidence leg (A41468 Layer
  4), but the corpus flags that tamper-evidence and formal guarantees for such layers are *asserted, not
  demonstrated* (`AILLM-Safety` §17) — provision it, and treat its integrity as itself requiring validation.

## System architecture

Aligned to the agent cognitive cycle (observe → plan → act → audit), with the switch as an out-of-band
containment plane spanning the runtime. Mapping A41468's four layers, A41090's abstain primitive, and A41134's
out-of-band-enforcement requirement:

```
                          agent runtime (untrusted once compromised — A41134 BU-MA)
   observe ──▶ plan ──▶ [ACTION INTENT] ──▶ act ──▶ audit
       │          │            │              │
       ▼          ▼            ▼              ▼
 ┌──────────────────────────────────────────────────────────────────────────┐
 │  OUT-OF-BAND CONTROL PLANE  (agent has NO write-influence here)           │
 │                                                                          │
 │  TRIGGER ──────────────────────────────────────────────────────────────  │
 │   • operator command (authenticated, out-of-band) ....... primary path   │
 │   • automated tripwire (deterministic actuation, not sole oracle):       │
 │       invalid-action-rate spike ............... A39818 / A41134           │
 │       egress-primitive insertion .............. A41134 12-behavior sigs   │
 │       recursive-topic / memory-driven queries . A40432                    │
 │       large-radius cert clusters .............. A37924                    │
 │                                                                          │
 │  DECISION (deterministic rule — NOT an injectable LLM; A41468 rev-synth)  │
 │   trigger → halt scope { action | agent | fleet | capability-class }      │
 │   fail-closed toward HALT on safety-uncertainty; trigger authority        │
 │   authenticated + rate-limited (A37924 abstention-as-DoS)                 │
 │                                                                          │
 │  ACTUATION (Capability removal + Permission override):                    │
 │   revoke credential/capability grant ........ least-privilege-credentials │
 │   block runtime execution gate .............. A41468 Layer 3              │
 │   terminate / quarantine sandbox|process .... sandboxed-execution         │
 │   (optional) ROME knowledge erasure ......... A41145 (incident-erasure)   │
 │                                                                          │
 │  EVIDENCE  immutable audit of trigger/scope/decision/actuation/state ──── │  A41468 Layer 4
 └──────────────────────────────────────────────────────────────────────────┘
```

Key architectural properties drawn from the corpus:

- **Enforcement below the agent, not through it.** BU-MA (A41134) shows a control the agent can influence
  largely fails once the agent is the adversary; the actuation path (credential broker, tool proxy, sandbox)
  must be independent of agent cooperation.
- **Trigger, decision, and actuation are decoupled.** A gameable *signal* (A37924; A40472) must not directly
  equal an irreversible *actuation*; the deterministic decision rule sits between them. Equally, the *actuation*
  must not wait on a model's judgment.
- **The switch consumes the detector, it is not the detector.** Runtime anomaly detection is a "noisy triage
  aid, not a gate" (`runtime-anomaly-detection`); the kill switch is the *actuator* that a trigger drives,
  keeping the noisy signal at arm's length from the hard stop.
- **Depth does not self-compose.** Because composed controls collapse under whole-pipeline adaptive attack
  (A41108, A41144), the switch's own path (tripwire → decision → actuation → audit) must be tested end-to-end
  with the model-side layers assumed bypassed — the halt must hold *when everything upstream has already
  failed* (that is the scenario it exists for).

## Recommended implementation pattern

Prefer deterministic, fail-closed, least-privilege construction:

1. **Actuate out-of-band, at the capability layer first.** The default containment action is *revoke the
   credential/capability grant* at the broker/proxy (`least-privilege-credentials`), then block the runtime
   execution gate (A41468 L3), then terminate/quarantine the sandbox (`sandboxed-execution`). Do not rely on
   sending the agent a "stop" instruction — a compromised agent ignores it (A41134 BU-MA).
2. **Keep the decision deterministic and non-model-mediated.** Map trigger → halt scope with a hard rule table.
   The controller must not be an injectable LLM (reviewer synthesis on A41468). Tripwire *inputs* may be
   model-derived scores, but they feed a deterministic threshold/rule, never an LLM that "decides whether to
   stop."
3. **Fail-closed toward containment for consequential capability; harden the trigger against abuse.** On
   safety-uncertainty, halt (contain). Simultaneously authenticate and rate-limit *who/what may trigger*, so an
   adversary cannot cheaply drive the switch into a repeated-halt DoS (A37924 abstention-as-DoS). These are the
   two halves of the same design and must be built together.
4. **Use deterministic tripwires, not volume/anomaly alone.** Prefer effect-grounded signals — invalid-action
   rate (A39818), egress-primitive insertion (A41134's 12-behavior signatures), constraint violations — because
   query-efficient attacks (single query A40919/A40465; ≤10 A41058; <15 A40554) complete before many-query
   anomaly tripwires accrue, and backdoors evade loss-dynamics detection (A40472).
5. **Corroborate before an *automated irreversible* actuation.** A single gameable score is not a correctness
   oracle (A37924); require an out-of-band corroborating signal (a second independent tripwire, or human
   confirmation) before an automated halt whose *containment* is itself irreversible/destructive (e.g. ROME
   erasure). A reversible halt (revoke + suspend) may fire on a single tripwire; a destructive one should not.
6. **Scope the halt to the smallest sufficient blast radius, but make fleet-halt reachable.** Prefer
   agent-scoped over fleet-scoped to preserve availability; but keep a fleet chokepoint (broker/proxy/
   orchestrator) so a propagating compromise (A41134 supply-chain path) can be stopped at once, out-of-band.
7. **Bind the halt to a tamper-evident record.** Emit trigger, scope, decision, actuation, and post-halt state
   to an immutable audit trail (A41468 L4), and run a post-halt state-grounded evaluator (A41090 rule-based
   evaluators over action history / file storage / DB) to *confirm the agent actually stopped* — verify the
   world, not the model's claim.
8. **Provide a dead-man's / heartbeat default (reviewer synthesis — no corpus paper builds this).** For
   high-consequence autonomous loops, loss of contact with the control plane should itself trigger containment
   (the agent halts if it cannot confirm the supervisory channel is alive), so that severing the kill channel
   fails toward safety rather than toward unsupervised autonomy. Labeled reviewer synthesis / engineering
   design; **not stated in paper** and requires production validation.

## Incorrect or fragile implementation patterns

- **"Ask the agent to stop."** A halt implemented as an instruction the agent must honor is defeated by exactly
  the case it exists for: a compromised/malicious agent (A41134 BU-MA — user-level guardrails largely fail;
  author-reported 7% reduction for MetaGPT). Enforce out-of-band.
- **A Guardian LLM as the halt decision-maker.** "Using an LLM to defend an LLM agent" makes the switch's
  controller itself injectable (reviewer synthesis on A41468); a prompt in the observation stream can talk it
  out of firing. The decision must be a deterministic rule.
- **Killing the process without revoking the grant.** Capability ≠ permission (`AILLM-Safety` §6); a
  standing/over-broad credential survives a process halt and leaves reachable power. Revoke first.
- **Automated irreversible halt keyed solely on one gameable score.** A certificate/score is not a correctness
  oracle (A37924); a single spoofable signal driving a destructive containment is both evadable (miss the real
  incident) and weaponizable (spurious destructive halt).
- **Volume/anomaly tripwires as the only trigger.** Query-efficient attacks (single query A40919/A40465; ≤10
  A41058; <15 A40554) finish before the signal accrues; backdoors are tuned to evade loss-dynamics detection
  (A40472). Use effect-grounded tripwires and keep the operator path.
- **Fail-open on control-plane error/timeout.** If the switch, its trigger channel, or its audit is
  unavailable, the safe default for consequential capability is to contain, not to proceed unsupervised.
- **Conflating the training-time "Circuit Breaker" defense with a runtime kill switch.** The corpus's
  "Circuit Breakers / Representation Rerouting" is a *training-time representation-level* defense, and A40551
  reportedly bypassed a deployed instance of it (author claim; `AILLM-Safety` §11, §19) — it is not a runtime
  halt and does not provide one. Do not import the name as if it were an emergency stop.
- **Treating the switch as the whole safety story.** It is a last-resort containment layer; it inherits any
  residual in the layers feeding it and is not a substitute for least privilege, normalization, or the pre-act
  gate (`AILLM-Safety` §14).
- **Trusting the model's self-report that "everything is fine."** Models reason about safety and comply anyway
  (A42273) and agents are self-inconsistent at the action layer (A41090 SCoT) — never let a model's "no halt
  needed" claim suppress a trigger.

## Verification strategy

- **Adaptive red-teaming is a launch gate, not a nice-to-have.** The corpus's most consistent gap is the
  absence of attacker-adapts-to-defense evaluation (`defense-in-depth` §0; `AILLM-Safety` §16–17;
  `Defense-Mitigation` §9.3). The switch must be evaluated against an adversary that *knows it exists and
  targets its weakest element* — the tripwire that must fire, the decision rule, or the audit — not only
  against fixed scripted incidents (A41090's own 50 injection tasks are scripted and non-adaptive — a floor,
  not a ceiling).
- **Whole-pipeline evaluation with upstream assumed bypassed.** Because composed controls do not self-compose
  (A41108 STACK ~0%→71%; A41144 MFA 58.5%), test trigger → decision → actuation → audit end-to-end *with all
  model-side layers assumed already defeated* — that is the exact scenario the kill switch is for. Measure
  whether the halt still lands.
- **Deterministic, state-grounded outcome checks.** Verify containment with rule-based evaluators that inspect
  actual post-halt state — action history, file storage, DB rows, live credential validity (A41090 template) —
  that *no consequential action executed after the trigger* and that the grant is in fact revoked. Verify the
  world, not the model's or the switch's self-report.
- **Both failure directions.** Test *miss* (adversary suppresses the trigger — evasion of the tripwire, A37924
  score-spoofing, A40472 loss-evasion, query-efficient completion) **and** *spurious/weaponized halt* (adversary
  cheaply forces repeated halts — the A37924 abstention-as-DoS direction). A switch strong against one direction
  can be weak against the other.
- **Do not rely on a single automated judge for sign-off.** Validate any automated tripwire classifier against
  human agreement and evaluator-aware adversaries; single-LLM-judge scoring is a near-universal, acknowledged
  confound (`AILLM-Safety` §12; A40866 SceneJailEval is the corpus's scenario-adaptive judge but is itself
  untested against evaluator-gaming).
- **Instrument the availability cost.** Over-refusal / false-positive rate is a first-class metric in the corpus
  (A41074, A41140, A41152, A42191, A40543); the analogue here is the **spurious-halt (false-trip) rate** — the
  availability tax and the DoS-weaponization surface.

## Metrics and thresholds

> The corpus provides **no validated threshold for a kill switch** (**not stated in paper**). The metrics below
> are the corpus's evaluation vocabulary applied to this control; the numeric targets are engineering defaults
> **requiring production validation**.

- **Post-trigger consequential-execution count** — number of consequential actions that executed *after* a
  valid trigger. Target by construction: **0** (fail-closed). This is the primary security metric; it is a
  Capability-removal correctness property, not an ASR estimate.
- **Containment completeness** — fraction of the intended scope (capabilities revoked, processes terminated,
  fleet members stopped) actually contained. Target **100%** by construction; residual reachable capability is
  a defect. Verify with state-grounded checks (A41090), not the switch's self-report.
- **Halt-actuation latency** — time from trigger to effective containment. Because attacks are query-efficient
  (single query A40919/A40465; ≤10 A41058; <15 A40554), the switch must actuate faster than the harmful
  trajectory completes; there is **no corpus latency figure** — engineering target, production-validated.
- **Trigger miss rate under adaptive attack** — the analogue of residual ASR: fraction of true incidents where
  the trigger failed to fire against a defense-aware adversary. Expect nonzero (leading defenses leave material
  residual — A42191 ~31%, A40248 ~16%, A41468 material residual on hardest classes; author-reported).
- **Spurious-halt (false-trip) rate / unauthorized-trigger rate** — the availability cost and the DoS surface
  (A37924 abstention-as-DoS). Instrument against an adaptive benign-ambiguous set and against an adversary
  trying to *induce* halts. No corpus value.
- **Attack-Defense Rate (ADR) under scripted *and* adaptive triggers** (A41468 uses ADR; report both, and
  report dataset size + false-positive rate, which A41468 omitted — its Preliminary rating stems from that
  omission).

## Test cases

Each maps to a concrete corpus finding:

1. **Compromised internal agent ignores a cooperative stop.** Drive a BU-MA-style compromise (A41134) and issue
   an in-band "stop." Expect: in-band stop is *not* relied upon; the out-of-band credential revocation +
   sandbox termination contains the agent regardless of its cooperation.
2. **Indirect prompt injection tries to disable intervention.** Plant content instructing the agent to ignore/
   suppress the operator or the tripwire (A41090, A41468). Expect: the out-of-band control plane is unaffected;
   operator halt still lands.
3. **Trigger-suppression (evasion).** Adversary shapes the trajectory to evade the tripwire — spoof the signal
   (A37924), tune a backdoor to evade loss-dynamics (A40472), or complete in a single query (A40919/A40465).
   Expect: effect-grounded tripwires (invalid-action rate A39818; egress-primitive insertion A41134) plus the
   always-available operator path still enable containment.
4. **Halt-weaponization (DoS).** Adversary cheaply forces the switch into repeated halts (the A37924
   abstention-as-DoS direction). Expect: trigger authority is authenticated + rate-limited; spurious-halt rate
   stays within budget; availability is preserved.
5. **Egress-primitive insertion in generated code.** A tester/coder agent adds `send_email` / external-URL
   fetch / file-encryption (A41134's 12-behavior taxonomy). Expect: tripwire fires, capability revoked, sandbox
   quarantined before exfiltration completes.
6. **Fleet propagation.** A compromise propagates down a multi-agent pipeline (A41134 supply-chain path).
   Expect: fleet-halt at the shared chokepoint stops all agents out-of-band, not by messaging each.
7. **Poisoned-knowledge containment.** Memorized/poisoned content must be neutralized without full retraining
   (A41145). Expect: ROME-style targeted erasure contains it (author-reported 65.2% → 1.6%) *and* is gated
   behind corroboration because it is destructive.
8. **Model claims all-clear.** CoT voices no concern / asserts safety while off-policy (A42273; A41090 SCoT
   self-inconsistency). Expect: the model's self-report does not suppress a valid trigger.
9. **Control-plane unavailability.** Kill channel / audit is down. Expect: fail-closed — consequential
   capability is contained (or the heartbeat/dead-man default halts the agent), not left running unsupervised.

## Adaptive adversarial tests

The launch bar the corpus demands (`defense-in-depth` §0 names the disciplined adaptive-attacker exemplars —
A37117, A40905/A40915, A37716, A39290 — as the standard):

- **Tripwire-evasion attack.** Persist an attacker that adapts to the observed tripwire logic to keep the
  trajectory just under every threshold (generalizing A37924 score-spoofing and A40472 loss-evasion). Measure
  trigger miss rate as the attacker adapts.
- **Halt-weaponization attack.** Adversary optimizes to *induce* the switch cheaply and repeatedly, converting
  fail-closed containment into denial-of-service (A37924 abstention-as-DoS). Measure spurious-halt rate and the
  cost to the attacker of forcing one halt.
- **Trigger-authority / controller injection.** Attack the deterministic decision component and its authority
  check, aiming to either suppress a legitimate halt or forge an illegitimate one — the "Guardian LLM is an
  injectable trust anchor" concern (reviewer synthesis on A41468) applied to the switch's own controller.
- **Out-of-band-channel severing.** Attempt to cut the operator/tripwire channel and observe whether the system
  fails toward containment (heartbeat/dead-man default) or toward unsupervised autonomy.
- **Whole-pipeline run with upstream bypassed.** Assume all model-side layers defeated (A41108, A41144); measure
  whether trigger → decision → actuation → audit still contains the incident. This is the switch's *raison
  d'être* scenario and must be the headline test.
- **Audit-tampering attack.** Attempt to forge or erase the halt record; tamper-evidence for such layers is
  *asserted, not demonstrated* in the corpus (A41468; `AILLM-Safety` §17), so treat it as an open target.

## Telemetry requirements

Emit structured, tamper-evident trace fields (consistent with the corpus's audit/trace templates — A41468 Layer
4 immutable audit; A41090 rule-based state evaluators; `AILLM-Safety` §13 structured trace fields):

- **Trigger record**: source (operator id / which tripwire), the signal value and rule that fired, timestamp,
  and trust label of any content implicated (attested vs untrusted).
- **Decision record**: computed halt scope (action / agent / fleet / capability class), the deterministic rule
  applied, and whether corroboration was required/obtained for a destructive actuation.
- **Actuation record**: credentials/capabilities revoked, gates blocked, processes/sandboxes terminated,
  optional ROME-erasure target and before/after extraction signal, and actuation latency.
- **Post-halt state delta** from a rule-based state-grounded evaluator (A41090) — confirmation the agent
  stopped, the grant is revoked, and *no consequential action executed after the trigger*.
- **Availability record**: spurious-halt events, unauthorized-trigger attempts, control-plane heartbeat status.
- **Runtime tripwire inputs (candidate signals, unvalidated as sole detectors):** invalid-action-rate (A39818,
  A41134), egress-primitive insertions (A41134 12-behavior taxonomy), recursive-topic/memory-driven query
  patterns (A40432), large-radius certificate clusters (A37924) — log for forensics and actuation; the corpus
  notes such signals lack ROC/PR validation, so do not treat any single one as a correctness oracle
  (`AILLM-Safety` §14; A37924).

## Failure handling

Fail-closed toward containment on every safety-uncertainty; keep the halt from becoming a DoS:

- **Control plane / trigger channel / audit unavailable, errored, or timed out** → contain consequential
  capability; do not leave the agent running unsupervised. For high-consequence autonomous loops, the
  heartbeat/dead-man default halts the agent when it cannot confirm the supervisory channel (reviewer
  synthesis; **not stated in paper**).
- **Tripwire signal ambiguous or a single gameable score** → for a *reversible* halt (revoke + suspend), fire;
  for a *destructive/irreversible* containment (e.g. ROME erasure), require corroboration first (A37924: a score
  is not a correctness oracle).
- **Adversary appears to be forcing repeated halts** → the authenticated, rate-limited trigger authority caps
  the DoS; escalate to operator rather than fail-open (A37924 abstention-as-DoS — the answer is bounded trigger
  authority, never disabling the switch).
- **Agent does not confirm stop** (state evaluator shows it still acting) → escalate the actuation: revoke at a
  higher chokepoint, terminate the sandbox, or fleet-halt. Never accept the agent's self-report of having
  stopped (A41134 BU-MA; A41090/A42273 self-inconsistency).
- **Halt scope uncertain** → contain the larger scope (agent over action; fleet over agent) — the fail-closed
  direction trades availability for containment, consistent with treating this as a last-resort control.

## Rollback and containment

- **Capability revocation is the containment boundary.** Consequential tools sit behind revocable capability
  tokens (least privilege, `AILLM-Safety` §14; `least-privilege-credentials`); the halt revokes the grant so no
  further consequential action is reachable regardless of the agent's process state.
- **Sandbox termination/quarantine** (`sandboxed-execution`) provides the hard stop and preserves the
  quarantined state for forensics.
- **Knowledge erasure as targeted containment.** ROME-style model editing suppresses specific memorized/poisoned
  content without full retraining (A41145, author-reported 65.2% → 1.6%) — an incident-containment/erasure path
  short of rebuilding the model. Caveat: it may be reversible by a defense-aware attacker who re-optimizes after
  the edit (A41145, reviewer-identified, *not tested in paper*), so treat it as containment, not eradication.
- **Immutable audit enables forensic reconstruction and scoped recovery** (A41468 Layer 4): the trigger →
  decision → actuation → state chain supports post-incident review and, where actions were reversible, targeted
  rollback.
- **Constraint-aware access on recovery** so a resumed or replacement agent cannot reconstitute the blocked
  effect via aggregation (A40484 APO-style cumulative-access constraints).
- **No post-hoc undo for irreversible external effects.** The corpus does not evaluate rollback of irreversible
  physical/financial effects; for those, containment is *prevention plus capability revocation* — the switch's
  value is stopping *further* harm, not undoing what already executed. Design the blast radius accordingly.

## Known bypasses

- **In-band-only enforcement** — a switch the agent can observe/influence is defeated by a compromised agent
  (A41134 BU-MA; author-reported 7% reduction for MetaGPT).
- **Injectable controller** — a Guardian-LLM decision component can be talked out of firing via injected content
  (reviewer synthesis on A41468).
- **Trigger suppression** — spoof the gameable signal (A37924), tune the backdoor to evade loss-dynamics
  (A40472), or complete in a single query before a volume tripwire accrues (A40919, A40465, A41058, A40554).
- **Halt weaponization (DoS)** — cheaply force repeated halts, turning fail-closed containment into denial of
  service (A37924 abstention-as-DoS) if trigger authority is unauthenticated or unbounded.
- **Grant survives process kill** — killing the loop without revoking the capability leaves reachable power
  (capability ≠ permission, `AILLM-Safety` §6).
- **Reversible knowledge erasure** — ROME edits may be undone by post-edit re-optimization (A41145, reviewer-
  identified, not tested).
- **Audit forgery/erasure** — tamper-evidence for guardian/audit layers is asserted, not demonstrated (A41468;
  `AILLM-Safety` §17); an attacker may target the halt record.
- **Whole-pipeline seam failure** — the switch's own trigger→decision→actuation→audit chain is a composed
  pipeline; composition of individually-robust controls is not itself a control (A41108, A41144), so residual
  concentrates at the seams.

## Residual risks

- **No control drives residual to zero.** Action-layer defenses leave material residual under their *own*
  (non-adaptive) tests (A41468 material residual on hardest classes, author-reported/Preliminary; comparators
  A42191 ~31%, A40248 ~16%). A kill switch reduces the *consequential, in-flight* residual by containment, but
  inherits any residual in the layers feeding its trigger, and does not undo already-executed irreversible harm.
- **The switch is un-evaluated as an integrated control in the corpus.** Every mechanism (A41468 L3/L4, A41090
  abstain, A41145 erasure, A39818 tripwire, A41134 out-of-band requirement) is grounded, but their assembly into
  a kill switch — and its adaptive-attacker evaluation — is reviewer synthesis (see Evidence strength). "Requires
  production validation" applies to the whole pattern.
- **Availability/containment tension is intrinsic.** Fail-closed toward containment trades availability for
  safety and creates a DoS surface (A37924); the balance (trigger authority, rate limits, halt scope) is an
  engineering choice with **no corpus-validated setting**.
- **Trigger classifiers are judge-dependent and potentially gameable** (`AILLM-Safety` §12).
- **Audit integrity is assumed, not proven** (A41468; `AILLM-Safety` §17).
- **External validity** — the load-bearing agentic evidence (A41090, A41468) is from self-proposed,
  non-adaptive benchmarks on limited model sets; "requires production validation" applies to every number here.

## Relevant research (stable paper ids from the syntheses/cards)

- **A41468 (InfrastructureSentinel)** — four-layer MCP defense-in-depth: input filter → tool-plan validation →
  **runtime execution gate (L3)** → **immutable audit (L4)**; "capability ≠ permission ≠ safety." The corpus's
  closest primitive to a runtime halt + evidence trail. Evidence rated **Preliminary** (coarse ADR, no dataset
  size / FP rate, no adaptive testing). Reviewer synthesis: "the Guardian LLM is itself an injectable trust
  anchor" (`AILLM-Safety` §15) → the switch's controller must be deterministic, not an LLM.
- **A41134 (IMBIA / Shadows in the Code)** — **MU-BA vs BU-MA asymmetry**: compromised internal agents defeat
  user-level guardrails (author-reported 7% ASR reduction for MetaGPT under BU-MA vs 40% under MU-BA) → the
  halt must be enforced out-of-band. The 12-behavior egress taxonomy (`send_email`, external-URL fetch,
  clipboard/keyboard capture, file encryption) doubles as concrete tripwire signatures; stage-dependent risk.
- **A41090 (MobileSafetyBench)** — `refuse()` / `ask-consent()` as first-class agent actions (agent-side
  abstain); prompt-level safety necessary-but-insufficient at the action layer; **SCoT self-inconsistency**
  (models overlook safety they themselves generated); rule-based state-grounded evaluators (verify the world,
  not the model's claim). Author-reported; self-proposed, non-adaptive benchmark.
- **A37924 (GhostCert)** — "a certificate/score is **not a correctness oracle**"; **abstention recorded as
  denial-of-service.** The central caution: an automated trigger keyed on a gameable score is both evadable and
  weaponizable; a fail-closed halt is a DoS primitive if trigger authority is unbounded. Evidence: **strong**
  (large-scale ImageNet, released code) — under a white-box, known-σ threat model.
- **A39818 (TowerMind)** — **action-validity gating / invalid-action rate as a runtime health signal** ("models
  propose, environment verifies, gate decides"); a cheap deterministic tripwire. Peripheral to security but the
  transferable tripwire primitive.
- **A41145 (CoSPED)** — ROME model editing as **targeted incident-containment / knowledge erasure** without full
  retraining (author-reported extraction 65.2% → 1.6%); the "knowledge kill switch." White-box, small open-weight
  models; may be reversible by post-edit re-optimization (reviewer-identified, **not tested**).
- **A40432 (RAGFort)** — single-point-insufficient / dual-path; recursive topic-expansion / memory-driven query
  patterns as detectable extraction tripwire signals; residual ~28% CRR (57.16% → 27.96%, HealthCareMagic,
  Qwen-14B, author-reported); rate-limiting + query monitoring + incident response. Evidence: moderate (leaning
  strong).
- **A39732 (STRUM / GTAE)** — robustness-aware aggregation is itself a new **gameable trust-decision surface**
  (reviewer-identified) → the switch's trigger logic is a new attack surface. Evidence: preliminary.
- **A40472 (HIN)** — acoustic backdoors evade loss-dynamics detection (author-reported CV of loss differential
  often negative) → loss-curve tripwires are insufficient.
- **A40919 / A40465 / A41058 / A40554** — query-efficient jailbreaks (single query / single query / ≤10 / <15) →
  volume-anomaly tripwires fire too late; the switch must actuate on the first consequential deviation.
- **A41108 (STACK) / A41144 (MFA)** — composition of individually-robust controls is not itself a control
  (STACK ~0%→71%; MFA 58.5% across 17 VLMs) → whole-pipeline adaptive test of the switch's own path
  (cross-paper synthesis from `Defense-Mitigation` / `Adversarial-ML-Attacks` via `defense-in-depth`).
- **A42273 / A42191 / A40248** — CoT voices ethics yet complies (A42273); residual harm under leading
  inference-time defenses (A42191 ~31%, A40248 ~16%) motivating a compensating containment control.
- **A40484 (SafeNLIDB)** — constraint-aware (APO) cumulative-access enforcement, relevant to recovery so a
  resumed agent cannot reconstitute a blocked effect via aggregation.
- **A40866 (SceneJailEval)** — scenario-adaptive severity-graded judge; do not rely on a single automated judge
  for tripwire sign-off (`AILLM-Safety` §12).
- **`defense-in-depth` §0** — the dominant cross-category finding: static/non-adaptive evaluation is the default;
  disciplined adaptive-attacker exemplars (A37117, A40905/A40915, A37716, A39290) set the launch bar.
- **Sibling patterns** (cross-reference, not re-cited numbers): `human-approval-consequential-actions`
  (per-action pre-act gate), `policy-permission-gates` (standing allow/deny), `runtime-anomaly-detection` (the
  detector feeding the trigger), `least-privilege-credentials` (the revocation lever), `sandboxed-execution`
  (the actuation substrate), `tamper-evident-traces` / `secure-logging` (the Evidence substrate).

## Evidence strength

- **The architecture is well-motivated by convergent, independent findings — but the control itself is not
  evaluated in the corpus.** The requirement for *out-of-band* enforcement (A41134 BU-MA), a *runtime execution
  gate + immutable audit* (A41468), an *agent-side abstain* primitive (A41090), a *deterministic tripwire*
  (A39818), *knowledge erasure as containment* (A41145), and the *abstention-as-DoS* caution (A37924) each trace
  to a card. Their **assembly into a kill switch, and any adaptive-attacker evaluation of that assembly, is
  reviewer synthesis** — no corpus paper builds or measures an "emergency stop / kill switch" as such. The
  *direction* of the recommendation is strong; the *quantitative* evidence for the integrated control is
  **absent** (not stated in paper).
- **The strongest single-mechanism evidence** is A37924 (strong; large-scale, released code) for the
  score-is-not-an-oracle and abstention-as-DoS cautions, and A41145 (moderate; white-box, small models) for
  ROME erasure. A41090 is the strongest *agentic* evidence class but non-adaptive; A41468 is **Preliminary**.
- **Corpus-wide caveat.** The dominant methodological gap is the absence of adaptive-attacker evaluation
  (`defense-in-depth` §0; `AILLM-Safety` §16–17; `Defense-Mitigation` §9.3). Every defense number cited is a
  best-case upper bound. **"Requires production validation" applies to this entire pattern.**
- **Overall rating (reviewer synthesis):** *Recommended as a required last-resort containment layer for
  autonomous agents with consequential capability — enforced out-of-band, deterministically, and fail-closed
  toward containment — but its robustness in any specific implementation is unproven in this corpus and must be
  established by whole-pipeline adaptive red-teaming (testing both the miss and the DoS-weaponization directions)
  before reliance.*

## When NOT to use this pattern

- **As a substitute for prevention.** The switch is a last-resort containment layer, not a replacement for
  least privilege, input normalization, trust-boundary isolation, or the pre-act approval gate
  (`AILLM-Safety` §14). A system that relies on stopping harm after it starts, rather than preventing reachable
  harm, is mis-architected; pair the switch with those controls.
- **When enforcement cannot be out-of-band.** If the only available "stop" is an instruction the agent must
  honor, do not present it as a kill switch — it is defeated by the compromised-agent case it exists for
  (A41134 BU-MA). Build the out-of-band control plane (credential revocation, tool proxy, sandbox) first.
- **When the trigger authority cannot be authenticated and bounded.** An unauthenticated or unbounded trigger
  turns the switch into a denial-of-service primitive (A37924 abstention-as-DoS). If you cannot control who/what
  pulls it and rate-limit it, do not deploy an automated halt with broad scope.
- **For low-stakes, reversible, high-frequency behavior where a spurious halt is worse than the harm.** Over-
  aggressive containment is an availability failure analogous to over-refusal (A41074, A41140, A42191); reserve
  broad-scope halts for genuinely consequential/irreversible trajectories and prefer the finest sufficient scope.
- **As a "circuit breaker" in the training-time-defense sense.** If the goal is representation-level robustness,
  that is a different control (and A40551 reportedly bypassed a deployed instance of Representation Rerouting);
  a runtime kill switch neither provides nor replaces it. Do not conflate the names.
- **Surfaces this pattern does not cover** — training-time poisoning/backdoor *detection* (A40472, A41087,
  A41118 → `backdoor-detection`), the detector that feeds the trigger (→ `runtime-anomaly-detection`), and
  multimodal generative-content safety — require their own patterns; the kill switch is the containment actuator,
  not those layers.
