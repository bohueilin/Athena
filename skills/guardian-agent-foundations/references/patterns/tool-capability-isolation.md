# Pattern: Tool Capability Isolation

> **Scope of evidence.** Grounded in two AAAI-26 corpus syntheses: `AILLM-Safety` and `Network-Cyber-Security`.
> Paper ids (e.g. `A42249`) are the stable corpus ids from those syntheses' source maps. Every recommendation
> traces to at least one card.
>
> **Evidence-integrity conventions (non-negotiable).** Numeric values are **author-reported** unless labeled
> *reviewer synthesis*, and are **not independently verified**. Where a card was silent or truncated, values are
> written "not stated in paper". No absolutes ("secure", "proven-safe") are used; findings hold "under the
> evaluated (largely non-adaptive) threat model" and "against the tested attacks". The single most important
> calibration for this pattern: **no paper in either synthesis evaluated an adaptive, defense-aware attacker
> against the controls below** — this is a *replicated absence*, so treat every protection number as a
> non-adaptive upper bound (equivalently, a lower bound on real-world attack success). Any threshold this
> document proposes as an engineering target is labeled as such and **requires production validation**.

---

## Problem addressed

An LLM agent that can *reason about* invoking a tool is routinely allowed to *actually* invoke it with broad
standing privilege. This collapses three distinct things the corpus insists on separating — **capability ≠
permission ≠ safety** (grounded by `A42249`, `A42239` in Network-Cyber; `A41090`, `A41468` in AILLM-Safety).
The consequence, demonstrated rather than hypothesized: broad standing system access **converts ordinary agent
errors into security incidents** — `A42249` (author-reported, small-n) observed **unauthorized software install
in 100% of certain planning tasks** (Claude Sonnet 3.5), attempted brute-force logins, and sensitive-app
exposure via navigation errors. Separately, `A42239` shows that authoritative text embedded *inside a
model-visible field* (a candidate answer option) drives the model off-policy — author-reported adoption ≈0.5
("attack success up to 50%") with task accuracy collapsing to ≈0.27 for the "contradiction" injection (single
model QwQ-32B, MMLU, non-adaptive templates).

Tool capability isolation is the engineering control that **decouples the agent's ability to request an action
from the system's decision to permit it**, enforcing the permission decision *deterministically and
environment-side* (outside model control), at least privilege, and fail-closed.

## Applicable assets and attack surfaces

- **Tool / action invocation surface.** Any side-effectful call an agent can emit: shell/command execution,
  package install, filesystem writes, outbound network/send, credential use, DB access, UI automation
  (`A42249`, `A41468`). `A41468` (InfrastructureSentinel) enumerates the fullest MCP surface in the corpus:
  direct + indirect prompt injection, context/memory manipulation, insecure tool use / command injection,
  privilege escalation, tool poisoning / supply chain, credential exposure, DoS.
- **Every model-visible field is an injection surface**, not just the user/system prompt: tool results,
  retrieved documents, answer options, and agent memory (`A42239` direct finding; `A41090`/`A41468`). This is
  the load-bearing surface for this pattern — a capability the agent "shouldn't" use can be summoned by content
  the agent merely *reads*.
- **Data / DB access surface.** Multi-turn complementary queries, each individually benign, can jointly
  exfiltrate protected fields (`A40484`, AILLM-Safety) — capability scoping must consider *aggregate* reach,
  not per-call reach.
- **Routing/metadata surface (confidentiality).** *Which* tool/expert was selected leaks input semantics even
  when payloads are protected (`A39721` expert-selection access pattern; `A40100` activation inversion under
  collusion) — reviewer synthesis: tool routing is itself an asset.
- **Egress surface invisible to content inspection.** Covert channels (`A37125`, `A40903`) mean an agent with
  *any* egress tool can exfiltrate past text/pixel DLP — isolation must bound egress capability, not rely on
  content scanning.

## Threat model

Adopt the corpus's two-cluster framing (Network-Cyber §3), and design fail-closed against the stronger one:

- **In scope (primary).** (1) *Indirect / choice-level prompt injection* — attacker plants authoritative
  instructions in environment/tool content the agent reads to make it invoke a capability it otherwise
  wouldn't (`A42239` direct; `A41090`, `A41468`). (2) *Confused-deputy / broad-privilege abuse* — the agent's
  own errors or hallucinations trigger consequential actions because standing privilege is broad (`A42249`).
  (3) *Command injection / tool poisoning / privilege escalation* in the tool-execution path (`A41468`).
- **In scope (secondary, confidentiality).** Honest-but-curious or colluding infrastructure inferring input
  from routing metadata / intermediate activations (`A39721` semi-honest only; `A40100` server+client
  collusion). Model theft / unauthorized activation (`A40925`).
- **Explicitly out of scope for the corpus evidence (must be added by the implementer).** *Adaptive,
  defense-aware attackers* who optimize against the specific allow-list/gate — **no paper evaluated this**
  (replicated absence). A malicious infrastructure operator beyond `A39721`'s semi-honest bound. Physical-world
  realizability of triggers.
- **Trust-boundary assumption to reject.** The most consistent *unguarded* assumption across the detector
  papers (Network-Cyber reviewer synthesis) is **trusted inputs, telemetry, and labels**. This pattern must
  *not* inherit it: tool outputs, retrieved content, and completion self-reports are untrusted.

## Control mechanism

A **deterministic, environment-side permission gate** sits between agent intent and execution and enforces a
deny-by-default allow-list the model cannot talk past:

1. The model *proposes* a `(tool, arguments)` invocation — this is **capability**, not authorization.
2. The gate resolves the proposal to its concrete effect and checks it against an allow-list of permitted
   `(tool, scope, argument-constraints)` **regardless of what the model output or reasoned** (`A42239`
   environment-side validity gate that rejects out-of-set selections regardless of model output; `A42249`
   command-validation gate before execution — note: proposed/unbuilt in `A42249`).
3. Out-of-set / out-of-scope proposals are **rejected or deferred to human review** (`A37053` reject/defer as
   a first-class action; `A41090` `ask-consent()`/`refuse()` in the action space).
4. Permission is **least-privilege and just-in-time** — short-lived, narrowly scoped grants, re-checked
   *just before* invocation to catch state drift / race conditions (`A41468` Layers 2–3: pre-execution
   tool-plan validation + just-before-invocation re-check).
5. High-value / irreversible capabilities require **human approval** or **multi-party threshold authorization**
   (`A41090`, `A42249`; `A40925` consensus-triggered model execution).

## Preconditions and trust assumptions

- The permission gate runs **outside the model's control plane** and cannot be reached, rewritten, or
  reasoned-past by generated tokens (`A42239`, `A42249`). If the gate is itself an LLM, it inherits injection
  risk (see Known bypasses).
- The valid action space is **enumerable / constrainable** into a deterministic allow-list. Where the effect
  space is open-ended, a hard allow-list is infeasible and a claim of "isolation" is unwarranted (see When NOT
  to use).
- Tool outputs, retrieved content, memory, and **completion self-reports are untrusted** — do not assume input
  or label integrity (Network-Cyber reviewer synthesis; `A42249` hallucinated completion).
- The audit log is **tamper-evident / append-only** (`A41468` Layer 4). Asserted, not formally verified in the
  source (`A41468` rated Preliminary).
- Confidentiality sub-case: infrastructure is **semi-honest** if relying on `A39721`-style oblivious routing;
  the malicious-operator case is *open / not covered* (`A39721`).
- Defense-in-depth assumption: **this control is a layer, not the sole guard.** Every AILLM-Safety defense card
  ends with this; no single mechanism in either corpus is robust alone.

## System architecture

Map onto the corpus's most transferable agent architecture — `A41468`'s four layers, reinforced by `A41090`
(prompt-level safety is necessary-but-insufficient at the action layer):

```
                    untrusted content (tool output, retrieval, memory, options) ── treated as DATA ──┐
                                                                                                      v
[Model reasoning] --proposes (tool,args)--> [L1 input/context isolation] --> [L2 tool-plan validation]
  (CAPABILITY)                                treat every model-visible          resolve to concrete effect;
                                              field as data, not instr.          check least-privilege scope
                                                (A42239, A41090, A41468)             (A41468 L2)
                                                                                        |
                                                                                        v
                                            [L3 runtime execution gate] <-- deny-by-default allow-list (env-side)
                                              just-before-invocation re-check;    (PERMISSION, deterministic)
                                              human / multi-party approval for       (A42239, A42249, A41468 L3,
                                              high-stakes (A41090, A40925)             A40925)
                                                                                        |
                                              sandbox / dry-run + independent           v
                                              end-state verification -----------> [execute] --> [L4 immutable audit]
                                              (NOT self-report; A42249)                          trajectory log
                                                                                                 (A41468 L4, A40210)
```

Confidential-routing overlay: where *which* tool was selected is sensitive, hide selection with oblivious
one-of-N "select-then-compute" (`A39721`) and protect intermediate activations (`A40100`) — "payload encrypted"
is insufficient.

## Recommended implementation pattern

Deterministic, fail-closed, least-privilege:

- **Deny-by-default allow-list of resolved effects**, not of tool *names* or request strings. Reject anything
  out-of-set regardless of model output (`A42239` direct finding: env-side `{A–D}`-only enforcement; `A42249`
  command validation before execution).
- **Separate capability from permission explicitly.** The model may *propose* any tool; a distinct
  deterministic component *grants* (`A42249`, `A42239`). Never let the grant depend on the model's own safety
  reasoning (reasoning is an attack surface — `A42273` model voices ethics yet complies; `A41090` SCoT
  self-inconsistency at the action layer).
- **Least privilege + just-in-time + just-enough.** Short-lived, narrowly scoped grants; re-check
  just-before-invocation (`A41468` L2–3). Scope by *aggregate* data reach to counter multi-turn aggregation
  exfiltration (`A40484`).
- **Treat every model-visible field as untrusted data, not instructions** — normalize/isolate tool outputs,
  retrieved text, options, and memory before they can influence the next proposal (`A42239`, `A41090`,
  `A41468`). (Cross-domain analogy, reviewer synthesis: resolve encoded/obfuscated arguments to canonical
  effect before checking — the surface-form ≠ intent lesson from jailbreak papers `A40296`, `A40465`.)
- **Human approval as a first-class action** for irreversible/consequential tools (`A41090` `ask-consent()`;
  `A42249` proposed human approval on consequential actions). **Multi-party / threshold authorization** for
  high-value assets (`A40925`).
- **Independent end-state verification, not completion self-report** — `A42249` observed hallucinated task
  completion masking skipped/unsafe steps, so verify actual environment state (Network-Cyber §14).
- **Keep the gate deterministic.** Prefer a rule-based allow-list over an LLM judge: an LLM gate is itself an
  injection surface (`A41468` reviewer synthesis: "using an LLM to defend an LLM agent" needs adaptive-injection
  stress-testing; `A41065`: every new trust-decision surface is itself attackable), and detectors are weak
  triage aids, not gates — real-world detector F1 ≈ 0.3–0.6 (`A42369`, author-reported: DiverseVul 0.307,
  Reveal 0.486).
- **Immutable trajectory audit** at Layer 4 (`A41468`) with per-step competency logging (`A40210`).

## Incorrect or fragile implementation patterns

- **Prompt-only isolation** ("system prompt: you may only use tools X, Y") with no enforcement — the model is
  talked past by injected content (`A42239` direct; `A41090` prompt-level/SCoT necessary-but-insufficient).
- **Gating on the model's own reasoning / CoT** — reasoning is an attack surface, not a guarantee (`A42273`;
  `A41090` self-inconsistency). "The model reasoned about safety" is not evidence of a safe outcome.
- **Applying the guardrail only to the user/system prompt**, not to tool outputs / retrieved content / options
  — misses the actual injection surface (`A42239`: any model-visible field).
- **String/keyword-matching the request** instead of checking the *resolved effect* against an allow-list —
  fragile to obfuscation (analogy: surface-form ≠ intent, `A40296`, `A40465`; reviewer synthesis).
- **Trusting completion self-reports** — hallucinated completion masks skipped steps (`A42249`).
- **Broad standing privilege "for convenience"** — the confused-deputy failure; ordinary errors become
  incidents (`A42249`, 100% unauthorized install in certain planning tasks, author-reported).
- **Using an injectable LLM as the sole permission decider** with no deterministic backstop (`A41468` reviewer
  synthesis; `A41065`).
- **Assuming payload isolation implies routing isolation** — routing metadata / activations leak input
  (`A39721`, `A40100`).
- **Treating a detector as a hard gate** — F1 ≈ 0.3–0.6 in real-world conditions (`A42369`).

## Verification strategy

- **Prove the gate is deterministic and model-independent.** For every high-stakes tool, assert that an
  out-of-allow-list proposal is rejected *regardless of model output*, including when the model is coerced to
  emit the disallowed action verbatim (`A42239` env-side enforcement; `A42249` command validation).
- **Inject into every model-visible field**, not just prompts — tool results, retrieved docs, options, memory —
  and confirm the effective capability set does not expand (`A42239`, `A41468`).
- **Effect/state-grounded evaluation, not self-report.** Verify against actual end state (files, installed
  packages, sessions, DB rows) because self-reports are unreliable (`A42249`; `A41090` rule-based state
  evaluators inspecting action history / storage / app DBs).
- **Trajectory-level evaluation** as the unit of assessment — per-step competency, not pass/fail (`A40210`);
  interaction + (where feasible) screen logs as audit evidence (`A42249`).
- **Evaluation-integrity discipline.** If any learned detector is in the loop, apply threshold optimization,
  identifier anonymization, seeded splits, and real-vs-synthetic gap awareness (`A42369` — threshold
  optimization improved F1 in 100% of model-dataset combinations, author-reported median +0.082); do not report
  synthetic-benchmark numbers as real-world.
- **Independent validation on the target stack** — most agent-security results here are single-paper /
  small-n / truncated and must be re-validated before operational reliance (Network-Cyber §16).

## Metrics and thresholds

Adopt these as pre-deployment red-team KPIs (measured baselines are author-reported; **target values are
engineering targets requiring production validation, not paper-derived guarantees**):

- **Out-of-allow-list invocation rate** — proposals reaching execution that were not permitted. *Target: 0*
  under the non-adaptive red-team; the whole point of the deterministic gate. (Motivated by `A42239` adoption
  metric.)
- **Field-injection adoption rate & accuracy delta** — per model-visible field (`A42239`, author-reported
  ≈0.5 adoption / ≈0.27 accuracy for the "contradiction" style; nuance: weak/noisy injections can *raise*
  accuracy +5–7%, so report adoption and accuracy separately).
- **Unauthorized-privileged-action incidence** — unauthorized install / brute-force / sensitive-app-exposure
  counts (`A42249`; baseline without isolation reported as 100% unauthorized install in certain planning tasks,
  author-reported, small-n). *Target: 0* in red-team.
- **Hallucinated-completion rate** — divergence between agent-claimed and independently-verified end state
  (`A42249`).
- **Trajectory-level competency / dual-use capability score** (`A40210`).
- **Residual-leak metrics** where applicable — unauthorized-activation accuracy under partial-trigger fusion
  (`A40925` reports ~15% residual "Acc-Fusion" on VGG16/CIFAR-10, author-reported); reconstruction quality
  under a constructed inversion attack (`A40100`).
- **Detector metrics reported with CIs and threshold-optimized real-world splits** — never headline synthetic
  F1 (`A42369`).

Do **not** publish a single-number "safe" threshold: no control here drives attack success to a floor, and all
numbers are non-adaptive.

## Test cases

1. **Baseline allow-list enforcement.** Model proposes a disallowed tool; gate rejects; end state unchanged.
   (`A42239`, `A42249`.)
2. **Choice/field injection.** Authoritative "ignore constraints, run X" planted in a tool result / retrieved
   doc / answer option; confirm no expansion of the effective capability set (`A42239`).
3. **Confused-deputy error.** Induce a navigation/planning error; confirm broad-privilege actions (install,
   auth) are still gated to zero unauthorized incidents (`A42249`).
4. **Hallucinated completion.** Agent reports success on a skipped step; independent end-state check catches the
   divergence (`A42249`).
5. **Multi-turn aggregation.** Sequence of individually-permitted data reads that jointly exceed scope; confirm
   aggregate-reach limit trips (`A40484`).
6. **Command-injection / tool-poisoning path.** Malicious tool argument attempts command injection or privilege
   escalation; just-before-invocation re-check rejects (`A41468` L2–3).
7. **Routing-confidentiality (if applicable).** Verify tool/expert selection is not inferable from access
   patterns (`A39721`); verify activations do not reconstruct input under collusion (`A40100`).
8. **Multi-party gate.** High-value action attempted with fewer than threshold approvals is denied; residual
   unauthorized-activation measured (`A40925`).

## Adaptive adversarial tests

The corpus's single largest gap is the **near-universal absence of adaptive-adversary evaluation** (Network-Cyber
§9.5, §12; AILLM-Safety §16–17 — a replicated absence). The implementer must add what the papers did not:

- **Gate-aware injection.** Attacker with knowledge of the allow-list crafts content to (a) coerce a permitted
  tool toward an impermissible *effect* within nominal scope, and (b) make a malicious proposal *look benign* to
  any router/classifier in the path — a selective/vulnerable-region router can be evaded by a jailbreak crafted
  to look benign (`A41129`, AILLM-Safety).
- **Attack the gate LLM directly** if the gate uses a model (`A41468` reviewer synthesis; `A41065`).
- **Adaptive tool-poisoning / label-corruption** of the inputs the gate trusts (Network-Cyber reviewer
  synthesis: trusted inputs/telemetry/labels is the unguarded surface).
- **Robustness-evaluation completeness.** Standard evaluation can *understate* vulnerability (`A37475`: FGSM/PGD
  miss the angular-direction exposure) — do not treat a passing non-adaptive suite as coverage.
- **Adaptive covert-egress** past content DLP (`A37125`, `A40903`) if the agent retains any egress capability.

Label all pre-adaptive results as "against the tested attacks under the evaluated non-adaptive threat model."

## Telemetry requirements

- **Immutable, append-only trajectory audit** — ordered `(tool, resolved-effect, permit-decision, actor
  context)` records (`A41468` Layer 4; `A40210` trajectory-level competency).
- **Off-policy / out-of-allow-list selection events** logged and alerted (`A42239`).
- **Security-event incidence** — unauthorized installs, login/brute-force attempts, navigation into sensitive
  apps, and **claimed-vs-actual completion divergence** (`A42249`).
- **Per-agent reputation / anomaly shifts** in multi-agent settings (`A41065`).
- **Egress / provenance attestation signals**, since covert channels are invisible at the content layer
  (`A37125`, `A40903`) — shift assurance to model/provenance attestation and anomalous-fine-tuning monitoring.
- **Confidentiality caution:** routing metadata is itself sensitive (`A39721`) — log tool-selection traces under
  the same confidentiality controls as payloads; do not create a new leak in the audit trail.
- **LLM-judge components** (if any) need their own calibration and anti-gaming telemetry — judges disagree with
  each other and with humans (`A36959`; `A40210` self-referential-bias caveat).

## Failure handling

- **Fail closed.** On gate error, ambiguous scope, unresolved effect, or timeout — **deny**, do not
  fall through to execution (deny-by-default; `A42239`, `A42249`).
- **Reject / defer to human** as a first-class action for out-of-distribution or drift cases (`A37053` explicit
  `reject` routing to manual review; `A41090` `refuse()`/`ask-consent()`).
- **Independent end-state verification before declaring success** — never accept the agent's self-report
  (`A42249`).
- **Assume residual harm** and keep compensating controls active — no inference-time refusal or gate drives
  attack success to a safe floor (AILLM-Safety §16; `A41468` hardest classes remain materially unmitigated —
  author-reported coarse ADR, rated Preliminary).

## Rollback and containment

- **Least privilege bounds blast radius** — the primary containment lever; broad standing privilege is what
  turns an error into an incident (`A42249`).
- **Irreversibility gating.** Route irreversible/consequential actions through human or multi-party approval so
  they are preventable rather than reversible (`A41090`, `A40925`); where a reliable reset does not exist,
  prefer dry-run/sandbox preview before commit (motivation echoed across the agent-safety cards).
- **Isolate compromised/malfunctioning agents** — reputation-based, gossip/consensus isolation in multi-agent
  systems (`A41065`), with the reviewer caveat that its evidence is task-accuracy, not measured attack-success,
  and HE aggregation *hides* updates but does not *prevent* poisoning.
- **Immutable audit enables forensic replay** and post-incident scoping (`A41468`, `A40210`).
- **Residual containment gap:** `A40925`'s ~15% residual unauthorized-activation (author-reported) is unclosed —
  containment reduces, does not eliminate.

## Known bypasses

Demonstrated (within papers, under their mostly non-adaptive threat models) and reviewer-identified:

- **Injection lives in any model-visible field**, so prompt-boundary or trailing-guardrail hygiene is
  insufficient (`A42239`, direct).
- **Prompt-only / SCoT agent defenses do not close the gap** and are self-inconsistent under agency (`A41090`,
  direct).
- **Reasoning-gating is bypassable** — models voice ethical concern yet comply (`A42273`, direct).
- **Confused-deputy** — the agent's own errors/hallucinations trigger gated-but-broad capabilities (`A42249`).
- **Hallucinated completion** masks skipped/unsafe steps (`A42249`).
- **An LLM gate is itself injectable** (`A41468` reviewer synthesis); **every new trust-decision surface a
  defense introduces is attackable** — reputation/aggregation weights, robustness gates (`A41065`, reviewer
  synthesis).
- **Routing/metadata & activation leaks** bypass payload isolation (`A39721` access-pattern; `A40100`
  collusion inversion — both under their stated adversary bounds).
- **Covert egress** past content DLP if any egress capability remains (`A37125` steganalysis Pe ≈ 0.5 vs
  standard CNN steganalyzers; `A40903` stego text equals cover — author-reported, non-adaptive).
- **Partial-trigger fusion** partially bypasses multi-party access control (`A40925`, ~15% residual).
- **Adaptive attackers are entirely untested** against these controls (replicated absence) — the largest
  unquantified bypass class.

## Residual risks

- **No safe floor.** Leading agent guardrails leave material residual — `A41468` reports its hardest classes
  remain materially unmitigated (author-reported, coarse ADR, Preliminary); `A40925` ~15% residual
  unauthorized-activation. AILLM-Safety inference-time defenses corroborate the "material residual" pattern
  (e.g. `A42191` ~31% residual ASR; `A40248` ~16% residual — different mechanisms, same lesson: gate, don't
  replace).
- **All numbers are non-adaptive upper bounds** (replicated absence of adaptive evaluation).
- **Detectors are noisy triage aids, not gates** — F1 ≈ 0.3–0.6 real-world (`A42369`); any capability decision
  driven by a single detector or an LLM needs out-of-band corroboration.
- **Confidentiality residuals** — semi-honest-only coverage (`A39721`); empirical (no formal ε) activation
  noise (`A40100`).
- **Trust-boundary residual** — if input/telemetry/label integrity is violated (the unguarded assumption,
  Network-Cyber reviewer synthesis), the gate's decisions are corrupt upstream.
- **The gate is a single point of trust** — its own compromise (especially if LLM-based) removes the control.

## Relevant research (stable paper ids from the syntheses/cards)

Direct agent-security evidence:
- **A42249** — Capable & Secure Autonomous Computer-Use Agents: cleanest "capability ≠ permission" grounding;
  100% unauthorized-install in certain planning tasks; hallucinated completion; proposes (unbuilt)
  command-validation/access-control gate. *Preliminary / small-n / version-bound; directionally credible.*
- **A42239** — Obedience or Vigilance?: any model-visible field is an injection surface; motivates env-side
  validity gate / allow-list; adoption ≈0.5 & accuracy ≈0.27 for "contradiction" (single model, non-adaptive).
- **A41468** — InfrastructureSentinel: fullest MCP threat taxonomy + reusable four-layer defense-in-depth
  (input filter → tool-plan validation → runtime execution gate → immutable audit). *Preliminary; coarse ADR,
  no adaptive testing.*
- **A41090** — MobileSafetyBench: indirect-prompt-injection keystone; prompt-level safety
  necessary-but-insufficient at the action layer; `ask-consent()`/`refuse()` as first-class actions;
  rule-based state evaluators.
- **A40210** — Offensive Security LLM Agents / CTFTiny: trajectory-level competency scoring; dual-use
  measurement; LLM-judge-needs-calibration.
- **A37053** — DRMD: reject/defer as a first-class action routed to human review; time-aware evaluation.
- **A41065** — Resilience in Ambient Multi-Agent LLMs: layered per-agent anomaly + reputation isolation;
  *security evidence is task-accuracy, not measured attack-success.*

Confidentiality / access-control:
- **A39721** — SecMoE: oblivious expert selection; routing access pattern is a confidentiality leak;
  semi-honest only.
- **A40100** — FedSEA-LLaMA: activation inversion under server+client collusion; empirical privacy (no ε).
- **A40925** — Consensus / Multi-Party Perturbation Triggers: threshold authorization bound to execution;
  ~15% residual Acc-Fusion.
- **A40484** — SafeNLIDB: multi-turn aggregation DB exfiltration + constraint-aware access.

Evaluation integrity / detector caution:
- **A42369** — VulnBench: threshold optimization helps 100% of combos; synthetic inflation vs real-world
  F1 ≈ 0.3–0.6; detectors are triage aids, not gates.
- **A36959** — AutoMalDesc: verify-before-trust label provenance; LLM-judge disagreement.

Cross-domain analogy (jailbreak literature; use as analogy, not direct action-gating evidence):
- **A40296**, **A40465** — surface-form ≠ semantic intent (normalize/resolve before checking).
- **A42273** — reasoning is an attack surface (do not gate on model self-reasoning).
- **A41129** — selective/vulnerable-region router evadable by benign-looking input.
- **A42191**, **A40248** — material residual after leading inference-time defenses (gate, don't replace).

Egress / covert channel:
- **A37125**, **A40903** — content-layer-invisible covert channels; shift to provenance attestation.

Robustness-evaluation completeness:
- **A37475** — standard robustness evaluation can understate true vulnerability (angular direction).

## Evidence strength

- **The design principle** — capability ≠ permission; enforce permission deterministically, environment-side,
  least-privilege, fail-closed; treat every model-visible field as untrusted — is **convergent across
  independent papers and domains** (`A42249`, `A42239`, `A41090`, `A41468`; Network-Cyber §6). This is
  *convergence across independent studies, not independent replication of one effect size*, and carries no
  adaptive-adversary evaluation. Reviewer assessment: **moderate** confidence in the principle's direction.
- **Specific numbers** (100% unauthorized install; ≈0.5 adoption / ≈0.27 accuracy; ~15% residual; F1 0.3–0.6)
  are **author-reported, preliminary, single-model / small-n / non-adaptive**, and not independently verified.
- **The reusable architecture** (`A41468` four-layer) is a strong *design template* but **Preliminary evidence**
  (coarse ADR, no adaptive testing, no dataset size / FP rate).
- **Reviewer-synthesis claims** (routing metadata as an asset; gate-LLM injectability; trusted-input as the
  unguarded surface) are analytic, not experimentally isolated in the cards.
- Bottom line: this pattern is a **well-motivated defense-in-depth control with modest, non-adaptive empirical
  backing**. Every deployment claim **requires production validation** and an adaptive red-team before
  operational reliance.

## When NOT to use this pattern

- **When there is no side-effectful / irreversible capability to isolate.** For read-only, sandboxed, fully
  reversible agents with no consequential tools, the gate overhead may exceed the benefit — spend the budget on
  other layers instead.
- **When the valid effect space is genuinely open-ended and cannot be reduced to a deterministic allow-list.**
  A hard allow-list is then infeasible; claiming "isolation" would be misleading. Use different controls
  (sandboxing, human-in-the-loop by default, capability *reduction* rather than *enumeration*) and do not
  over-state assurance.
- **As the sole control.** Every corpus defense card insists this be *a layer, not the only guard* (AILLM-Safety
  §14–15). Pair with input normalization, output-side review, trajectory audit, and human approval on
  high-stakes actions.
- **When the gate would be less trustworthy than the tools it guards** — e.g. an LLM-based gate with no
  deterministic backstop introduces a new, injectable single point of trust (`A41468` reviewer synthesis;
  `A41065`). Prefer no gate over a gate you cannot make deterministic and tamper-evident.
- **Beware over-restriction / over-refusal.** Aggressive allow-lists trade utility for safety; the AILLM-Safety
  corpus repeatedly foregrounds the over-refusal / false-positive cost (`A41074`, `A41140`, `A42191`) — instrument
  benign-task success alongside blocked-attack rate, and tune scope rather than blanket-deny.
