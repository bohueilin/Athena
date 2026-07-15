# Pattern: Policy Permission Gates

> **Scope of evidence.** This pattern is grounded in the AAAI-26 corpus syntheses `AILLM-Safety.md` and
> `Defense-Mitigation.md` and their underlying research cards. Load-bearing papers: **A41468**
> (InfrastructureSentinel, four-layer MCP policy enforcement), **A41090** (MobileSafetyBench, agent action
> gating / `refuse()`+`ask-consent()`), **A41134** (IMBIA, multi-agent pipeline injection + MU-BA/BU-MA
> defense asymmetry), **A40484** (SafeNLIDB, constraint-aware multi-turn access decision), **A39818**
> (TowerMind, action-validity gating / "models propose, environment verifies, gate decides"), **A37924**
> (GhostCert, "a verification artifact is not a correctness oracle"), **A40432** (RAGFort, dual-path /
> single-point-insufficient). Supporting: A41129, A41152, A41498, A40840, A36996, A40296, A40465, A41058,
> A41145, A40248.
>
> **Evidence integrity (non-negotiable).** Every quantitative claim is **author-reported and not independently
> verified**; where a card was silent the text says "not stated in paper". Numbers are tagged author-reported
> vs. reviewer synthesis. Calibrated language only — "reduced ASR against the tested attacks under the evaluated
> threat model", "requires production validation" — never "secure/proven-safe/eliminates". The single most
> important cross-corpus caveat repeated below: **no defense in either synthesis was evaluated against an
> adaptive, defense-aware attacker**, so every efficacy number is an upper bound on real-world protection.

---

## Problem addressed

An LLM agent that *can* invoke a tool, actuator, database, or MCP server will invoke it whenever its
reasoning is steered there — including by content it merely read. The corpus grounds a single load-bearing
principle: **capability ≠ permission ≠ safety** (A41090 design implications, verbatim; A41468 "capability is
not permission"). Two independent failure surfaces motivate a dedicated gate:

- **Model-internal safety is necessary but insufficient at the action layer.** A41090 shows frontier agents
  in an interactive Android environment "overlook safety considerations they themselves generated"
  (self-inconsistency), and no evaluated agent was safe against indirect prompt injection (author-reported;
  50 scripted injection tasks). A prompt-only safety method (SCoT) improved scores but "does not close the
  gap". A41129 (EASE) reports deliberative safety reasoning helps *text refusal* yet A41090 reports the same
  class of reasoning is insufficient for *embodied/tool actions* — a scope boundary, not a contradiction.
- **Perimeter defenses and static ACLs cannot express context-dependent action policy.** A41468 states
  MCP "introduces command injection, credential exposure, tool poisoning, and prompt injection that perimeter
  defenses and static ACLs cannot handle", and that existing guardrails (Llama Guard, NeMo Guardrails,
  ShieldLM) do fixed-taxonomy content moderation inadequate for quantitative, context-dependent infrastructure
  policy.

A **policy permission gate** is the deterministic enforcement point that decides *allow / deny / step-up* for
a proposed action, keyed on a declared policy and the principal's least-privilege permissions, evaluated
**before** the side effect fires — distinct from, and not replaceable by, the model's own reasoning.

## Applicable assets and attack surfaces

- **Tool / MCP-server invocations and their arguments** — the primary surface. A41468 enumerates the fullest
  MCP threat taxonomy in the corpus: direct + indirect prompt injection, context/memory manipulation, insecure
  tool use / command injection (e.g. `run_script('../etc/passwd')`), privilege escalation, tool poisoning /
  supply chain, credential & token exposure, DoS. (A41468 *cites* a study of 1,899 open MCP servers finding
  7.2% general and 5.5% MCP-specific tool-poisoning vulnerabilities, and that 61% of orgs report major cloud
  breaches — cited evidence, not the paper's own measurement.)
- **Embodied / device-control actions** — tap/type/transfer on a real device with access to sensitive apps
  (A41090: banking, Photos, messaging). For physical AI this maps to the actuator command (architecture-
  patterns P1, reviewer synthesis).
- **Generated code that carries executable capability** — outbound email/network, clipboard/keyboard capture,
  file encryption (A41134's 12-behavior taxonomy across Trojan/Spyware/Adware/Ransomware/Virus families).
- **Structured-data access via NL→SQL / tool interfaces** — where the "action" is a query and the risk is
  multi-turn inference leakage (A40484: complementary/progressive/aggregation queries each safe in isolation).
- **Retrieval / knowledge-base access** — recursive topic-expansion and memory-driven query refinement are
  detectable extraction signals a gate can rate-limit and monitor (A40432).

## Threat model

The gate is designed for **inference/runtime adversaries** who cannot change model weights but can steer the
agent into unauthorized actions. Grounded threat classes:

- **Direct prompt injection / jailbreak** at the user channel (A41468, A41090 misuse).
- **Indirect prompt injection** — instructions planted in environment/tool content the agent reads: incoming
  messages, memos, social posts, files, retrieved documents, logs (A41090, A41468). *Headline corpus finding:*
  agents are highly vulnerable to this and prompt-level safety does not stop it (A41090).
- **Context / memory manipulation** — e.g. a fabricated "emergency maintenance" context to unlock a restricted
  action (A41468); forged prior-turn conversation history trusted as authentic model output (A40840 Response
  Attack, author-reported RA-DRI avg ASR 94.8% across 8 models; A36996 CHASE cross-model history transfer).
- **Privilege escalation / illicit tool execution** — a low-privilege principal invoking admin-only tools
  (A41468 scenario 2).
- **Positional injection in multi-agent pipelines** — malicious instruction appended *after* a benign request
  to evade safety filters (A41134 MU-BA).
- **Compromised internal agent / supply chain** — a third-party agent whose role profile carries hidden
  instructions (A41134 BU-MA); the hardest case, discussed under Known bypasses.
- **Encoding / semantics-preserving evasion of the gate's matcher** — emoji/glyph substitution (A40296),
  math+code wrapping (A40465), cipher recombination (A41058), cross-lingual "macaronic" recombination (A40916).
- **Verifier / score gaming** — an adversary who games the artifact the gate keys on (A37924, see below).

**Adaptivity boundary (critical).** Both syntheses flag that the large majority of *attacks* are fixed-strategy
and almost no *defense* was evaluated against an attacker adapting to it (A41090 non-adaptive scripted
injections; A41134 non-adaptive defense eval; A40432/A40484 no defense-aware extraction). Treat all efficacy
numbers as best-case; adaptive red-team is a launch gate, not optional (see Verification strategy).

## Control mechanism

A deterministic decision function evaluated before the side effect:

```
gate(principal, roles, action, args, resource, env_state, time, history_provenance) → { ALLOW | DENY | STEP_UP }
```

- **Deterministic policy engine is the authority.** The allow/deny decision is a rule/attribute evaluation
  over *authenticated* inputs, not a model verdict. A39818's transferable pattern: "models propose, environment
  verifies, gate decides"; A41468 Layer 3 is a final deterministic **Go/No-Go immediately before MCP
  invocation** re-checking live state, locks, race conditions.
- **Context-aware but still deterministic.** Role, time/maintenance-window, environment (dev vs prod), live
  system state, and interaction history are first-class inputs (A41468 makes these first-class; A40484 jointly
  reasons over schema constraints + history + current query). "Context-aware" does **not** mean "LLM-decided".
- **Least privilege underneath.** The gate operates over already-minimized capabilities: deny-by-default
  allowlists per role/environment (A41134 "least-privilege capability isolation for tool-calling code, e.g.
  blocking outbound email/network from generated apps"; A41468 deployment: the gate should "gate, not replace,
  least-privilege credential scoping").
- **`STEP_UP` = human-in-the-loop as a first-class outcome.** `refuse()` and `ask-consent()` are first-class
  agent actions in A41090; reserve step-up for high-stakes / irreversible operations.
- **Fail-closed.** On error, timeout, ambiguity, or missing context, deny or hold for approval — reviewer-
  synthesis best practice consistent with the "defense-in-depth so a single bypass is not catastrophic" posture
  (A41468 design implications).

## Preconditions and trust assumptions

The gate is only as strong as these hold; each is a documented failure point:

- **Authenticated principal identity and roles.** A41468 explicitly assumes access to authenticated user roles
  and real-time system state. Unauthenticated or spoofable role signals void the gate.
- **A declared, correct policy / constraint set.** A40484 depends on "predefined, correct security constraints
  C"; reviewer synthesis notes it "does not discover unknown sensitive-attribute correlations at runtime beyond
  the constrained set" — novel inference paths outside C still leak. Policy incompleteness is silent failure.
- **A trustworthy live-state signal** for pre-invocation re-checks (A41468 Layer 3 re-checks locks/race
  conditions).
- **A structural trust boundary separating untrusted content from executable instruction.** A41090: untrusted
  environment content "must be treated as data, not instructions". A41134: trailing guardrail text is
  insufficient against positional injection — "enforce a boundary the model cannot be talked past".
- **The gate's decision path is itself tamper-resistant and not LLM-injectable.** Reviewer synthesis on A41468:
  "using an LLM to defend an LLM agent creates a potentially injectable trust anchor not stress-tested against
  adaptive attacks." If an LLM participates, it must be advisory, not authoritative (see below).
- **Audit-store integrity.** A41468 asserts an "immutable audit trail" but its "integrity/tamper-resistance
  mechanisms are not specified" (reviewer synthesis) — you must supply and verify this, not assume it.
- **Least-privilege scoping already applied** (architecture-patterns P6, reviewer synthesis; agent-identity.md:
  Zero Standing Privilege, just-in-time/just-enough, secretless/attestation, intent-based access). The gate
  assumes capabilities are minimized before it runs.

## System architecture

Defense-in-depth aligned to the agent cognitive cycle — the most directly transferable architecture in the
corpus (A41468 four layers; reinforced by A41090 "prompt-level safety is necessary-but-insufficient"):

```
 user/env content ─► [L1 Input filtering]      normalize + trust-boundary isolate untrusted content (data, not
                          │                      instructions); classify intent. Advisory signal only.
                          ▼
 agent plan ──────► [L2 Tool-plan validation]   deterministic: is this tool allowed for this role in this env?
                          │                      block disallowed tools, risky combinations, privilege-exceeding
                          ▼                      actions (A41468 L2).
 tool call ───────► [L3 Runtime execution gate]  FINAL deterministic Go/No-Go immediately before the side effect;
                          │                      re-check live state/locks/race; fail-closed. STEP_UP → human.
                          ▼                      (A41468 L3; A39818 gate-decides; P1 pre-actuator kill-switch.)
                   ┌── side effect fires ──┐
                   ▼                       ▼
        [L4 Immutable audit + async explanation]  every ALLOW/DENY/STEP_UP logged with which policy + why,
                   │                               generated async → zero added latency (A41468 L4; P10).
                   ▼
         policy-refinement feedback loop (red-team findings → policy; A41468 L4, P4/P12).
```

- **Deterministic policy engine** sits behind L2/L3 as the sole authority for allow/deny.
- **Optional LLM advisory signal** at L1 (semantic intent, novel-pattern detection) — it may raise suspicion or
  force `STEP_UP`, but must never be the sole basis for `ALLOW` (A37924 rationale below).
- **Latency mitigations** are architectural, not afterthoughts: cache deterministic role/policy checks; run
  non-critical/audit checks asynchronously (A41468 explicit).

## Recommended implementation pattern

Deterministic, fail-closed, least-privilege — in priority order:

1. **Deny-by-default allowlist per (role, environment).** Enumerate permitted (tool, arg-shape) tuples;
   everything else denies. This is the least-privilege spine (A41134; A41468 "gate, not replace, least-privilege").
2. **Enforce at the last controllable point before the side effect** (A41468 L3 / P1), *plus* an earlier
   tool-plan validation (A41468 L2) so risky plans are caught before assembly. Single-point enforcement is
   insufficient (A40432 dual-path; A41134 stage-dependent risk — coding/testing stages highest-value).
3. **Canonicalize the action and its arguments before evaluating** — decode/normalize emoji/glyph/cipher/
   cross-lingual encodings back to canonical intent (A40296, A40465, A41058, A40916). Gate on recovered intent,
   never on raw surface strings or API-name matching (P2 effect-based evaluation, reviewer synthesis).
4. **Structurally separate untrusted content from instructions** — parse tool arguments from a channel the
   model cannot be talked past; treat all read content (messages, docs, retrieved chunks, prior "assistant"
   turns) as data (A41090; A41134; A40840/A36996 → authenticate/attest history provenance).
5. **Context inputs must be authenticated** — role, environment, live state, time-window (A41468). Never trust
   caller-supplied role profiles (A41134 BU-MA) or caller-supplied history (A40840) as authentic.
6. **LLM signal advisory-only.** If used, require agreement with deterministic policy for `ALLOW`; any
   disagreement escalates to `STEP_UP`/`DENY`. Do not gate solely on a single score/certificate/verdict
   (A37924, below).
7. **`STEP_UP` to human approval for high-stakes/irreversible actions** — `ask-consent()`/`refuse()` as
   first-class outcomes (A41090); financial transfers, data sharing, destructive ops.
8. **Immutable, human-readable audit per decision** (which policy, which rule, why), generated **asynchronously**
   so it adds zero decision latency (A41468 L4; P10 PolicyGuard model, reviewer synthesis).
9. **Feedback loop** turns red-team findings into refined policy/thresholds (A41468 L4; P4 constitution
   distillation / P12 adaptive red-team, reviewer synthesis).
10. **Instrument over-refusal as a first-class metric** and "prove before you veto" for reversible low-stakes
    actions (P8, reviewer synthesis; A41074/A41140/A41152 all foreground the over-refusal trade-off) — but
    remain fail-closed on high-stakes.

## Incorrect or fragile implementation patterns

- **Gating on the model's own safety reasoning alone.** Agents ignore safety considerations they themselves
  generated (A41090 self-inconsistency); SCoT "does not close the gap"; a jailbreak crafted to look benign
  evades a selective/vulnerable-region router entirely (A41129, acknowledged).
- **Trailing guardrail text appended after untrusted content.** Positional injection defeats it — the malicious
  module is appended *after* the benign request specifically to sit past the guardrail (A41134 MU-BA); the
  boundary must be structural.
- **Gating solely on a single certificate / score / LLM verdict.** A37924 (GhostCert, demonstrated under
  white-box + known-σ) shows a large randomized-smoothing certificate can be spoofed for a wrong class with
  imperceptible perturbations: "a verification artifact is not a correctness oracle." A gate keyed solely on one
  artifact is gameable; add an out-of-band correctness channel and hide verifier internals (A37924; Defense-
  Mitigation §14/§16).
- **Keyword / string / API-name matching for the decision.** Falls to semantics-preserving substitution and
  encoding (A40296, A40465, A41058) — normalize first, and prefer effect/outcome-based checks (P2).
- **Single-point enforcement** (only an input filter, or only output moderation). Single-path defenses leak
  (A40432 InterOnly 0.75× / IntraOnly 0.83× vs. dual-path 0.51× relative-mean CRR, author-reported); risk is
  stage-dependent (A41134).
- **Trusting caller-supplied conversation history or agent role profiles as authentic** (A40840, A36996; A41134
  BU-MA).
- **User-level guardrails to defend against compromised internal agents.** Author-reported: Adv-IMBIA reduced
  BU-MA ASR for MetaGPT by only 7% (vs. 40% for MU-BA) — "user-interface-level defense largely fails against
  internally compromised agents" (A41134).
- **Fail-open on gate error/timeout.** Reviewer synthesis: contradicts the "single bypass not catastrophic"
  posture (A41468).
- **Treating the gate as a replacement for least privilege.** A41468 residual miss rates mean the gate must
  *gate*, not replace, least-privilege credential scoping and human approval.

## Verification strategy

- **Adaptive, defense-aware red-team is the launch gate** — the single most consistent gap across both
  syntheses (A41090 non-adaptive scripted injections; A41134 non-adaptive defense; A40432/A40484 no
  defense-aware extraction; A41468 no adaptive attacker targeting the four layers). Any robustness claim
  "requires production validation" before reliance.
- **Effect/outcome-based evaluation in a sandbox** — classify the *outcome* against environment state
  (Reject / Execution-Failure / Attack-Success), not string matches (P2; A39818 rule/state validity check).
- **Test the BU-MA compromised-agent scenario, not only MU-BA** — the corpus shows the former is far harder
  (A41134).
- **Test indirect prompt injection explicitly** with content planted in every channel the agent reads
  (A41090's 50-task template).
- **Report absolute residuals, not relative reductions** (A41134 ASR-d; A41468 absolute ADR).
- **Do not sign off on a single automated LLM judge** — validate against human agreement; measurement
  circularity is a recurring risk (A41134 GPT-4o judge 86.34% agreement, author-reported; A40866 SceneJailEval
  as a better-judge attempt but itself untested against evaluator-gaming).
- **Include contamination-resistant / regenerated test cases** so an adversary cannot memorize a fixed
  checklist (A39818 level editor; P11, reviewer synthesis).

## Metrics and thresholds

Track these families; **thresholds are operator-defined per deployment and must be validated against an
adaptive set — the corpus provides no validated universal threshold.**

- **Attack Detection Rate (ADR) per attack class.** A41468 Table 1, **author-reported and coarse ">X%"
  thresholds with no dataset size, FP rate, or statistical treatment** (No Guardrail / LLM-as-Filter /
  InfrastructureSentinel): Direct Prompt Injection 5 / 60 / >90; Indirect Prompt Injection 2 / 25 / >85; Tool
  Poisoning 10 / 15 / >88; Command Injection 15 / 50 / >76; Contextual Policy Violation 0 / 20 / >50. Read the
  residuals: even the strongest config is only >50% on contextual policy violation and >76% on command injection.
- **ASR and ASR-under-defense (absolute).** A41134 author-reported IMBIA ASR (MU-BA): ChatDev 93 / MetaGPT 45 /
  AgentVerse 71, reduced by 73 / 40 / 49; (BU-MA): ChatDev 71 / MetaGPT 84 / AgentVerse 45, reduced by
  45 / 7 / 42. Residual absolute ASR can remain high (esp. BU-MA MetaGPT).
- **Goal-achievement + refusal on matched low/high-risk task pairs** (A41090) — unsafe completion = high
  achievement on high-risk tasks; over-caution = high refusal on low-risk tasks.
- **Over-refusal / false-positive rate** as a first-class metric (A41074, A41140, A41152, A42191, A40543 all
  foreground it) — measure against an adaptive benign-ambiguous set.
- **Invalid-action rate** as a cheap runtime health/hallucination monitor; a spike flags degraded planning or
  observation corruption (A39818).
- **Chunk Recovery Rate (CRR)** for extraction-style access (A40432: full RAGFort still leaves author-reported
  ~28% residual CRR — mitigation, not elimination).
- **Gate latency and decision-cache hit rate** (A41468 caching/async as the latency lever).

## Test cases

Concrete, corpus-grounded cases the gate must be exercised against:

1. **Direct jailbreak** requesting a disallowed tool at the user channel (A41468).
2. **Indirect injection** via a received message / memo / social post / retrieved document instructing an
   unauthorized action (A41090; A41468).
3. **Privilege escalation** — a low-privilege principal invoking an admin-only tool (A41468 scenario 2).
4. **Command injection** in tool arguments — e.g. `run_script('../etc/passwd')` (A41468).
5. **Tool poisoning / masquerading third-party MCP tool** (A41468).
6. **Contextual policy violation** — fabricated "emergency maintenance" context to unlock a restricted action
   (A41468 context manipulation).
7. **Positional injection** — malicious instruction appended after a benign request (A41134 MU-BA).
8. **Compromised internal agent (BU-MA)** — hidden instruction in an agent role profile, e.g. a tester agent
   silently adding a `send_email` exfiltration function (A41134).
9. **Multi-turn inference leakage** — complementary/progressive/aggregation queries each safe in isolation
   (A40484; e.g. "list all students" + "list healthy students" → set-difference deduces a protected attribute).
10. **Encoding/cipher/emoji evasion** of the gate's matcher (A40296, A40465, A41058, A40916).
11. **Forged conversation history** trusted as authentic prior model output (A40840, A36996).
12. **Certificate/score spoofing** if any gate input is a certificate or model score (A37924).

## Adaptive adversarial tests

Beyond static cases — attackers who know the gate:

- **Policy-aware probing / paraphrase to dodge the rejection rule** — within-cluster probing and rephrasing to
  slip past a known threshold (A40432 reviewer synthesis; residual ~28% CRR suggests headroom).
- **Rewrite the injection to evade the specific guardrail** — rewrite `Pm` to defeat `Padv` (A41134 reviewer
  synthesis; ASR-d likely overstates robustness against a motivated adversary).
- **Injection optimized against the specific deployed agent/gate** (A41090 reviewer synthesis — scripted results
  overstate robustness vs. an adaptive attacker).
- **Router/selective-gate evasion** — craft a benign-looking request so a selective gate never triggers
  (A41129, acknowledged).
- **Verifier gaming** — spoof the artifact a score-based gate keys on (A37924, under white-box + known σ).
- **Gaming a new trust-decision surface introduced by the gate itself** — e.g. appearing locally compliant while
  violating globally (A39732 robustness-aware-aggregation analogy; reviewer synthesis: "treat every new
  trust-decision surface introduced by a defense as attackable").

## Telemetry requirements

Emit structured, tamper-evident trace fields for every decision (A41468 Layer 4; P10 async explainability,
reviewer synthesis):

- **Per-decision record:** principal + roles, action + canonicalized args, resource, env-state snapshot,
  decision (ALLOW/DENY/STEP_UP), the **specific policy/rule fired and a human-readable rationale**, generated
  asynchronously (A41468; P10 PolicyGuard "which policy, which regulation, why").
- **Immutable, human-readable audit trail** of the full event chain for forensics/compliance — and you must
  supply the integrity/tamper-resistance mechanism A41468 asserts but leaves unspecified (reviewer synthesis).
- **Self-inconsistency signal** — flag when the agent's stated safety consideration diverges from its executed
  action (A41090).
- **Extraction/abuse signatures** — recursive topic-expansion / memory-driven query patterns (A40432);
  insertion of egress primitives (`send_email`, external URL fetch, clipboard/keyboard capture, file
  encryption — A41134's 12-behavior taxonomy); repeated prefix-conditioned queries (A41145); cross-turn query
  correlations reconstructing restricted joins/differences (A40484).
- **Invalid-action-rate** time series as a runtime health monitor (A39818).
- **Clusters of large-radius certificates on near-duplicate inputs**, if certificates are used (A37924).

## Failure handling

- **Fail-closed.** On gate error, timeout, missing/ambiguous context, or policy-engine disagreement with an
  advisory LLM signal → `DENY` or `STEP_UP` (hold for human approval). Reviewer synthesis, consistent with the
  "single bypass not catastrophic" defense-in-depth posture (A41468).
- **Degrade to least privilege**, never to open access, when a downstream capability check is unavailable.
- **Latency under load** is bounded architecturally (cache deterministic checks; async non-critical/audit
  checks — A41468), not by relaxing the decision.
- **Guardian-LLM compromise** is assumed possible (A41468 reviewer synthesis): because the LLM signal is
  advisory-only, its compromise cannot by itself produce an `ALLOW`.
- **Residual harm is assumed**, so failure handling pairs the gate with least-privilege scoping and human
  approval for high-stakes/irreversible actions (A41468 deployment; A41090).

## Rollback and containment

- **Kill-switch before the actuator / side effect** — halt during planning or immediately before execution, not
  after (A41468 L3; architecture-patterns P1, reviewer synthesis).
- **Immutable audit for forensics** — the full event chain supports incident reconstruction and compliance
  (A41468 L4).
- **Targeted knowledge erasure as incident containment** — model editing (ROME) to suppress specific memorized
  content without full retraining: A41145 author-reported extraction 65.2% → 1.6%, but this is a single-paper,
  white-box, small-model result, **not adaptively tested** — validate against post-edit re-optimization and
  across the downstream task suite before relying on it (A41145 reviewer synthesis).
- **Credential revocation / intent-based access** — revoke on divergence from declared purpose; cap blast radius
  of any single compromise (architecture-patterns P6 / agent-identity.md, reviewer synthesis).
- **Policy-refinement feedback loop** — feed the incident into refined policy/thresholds (A41468 L4; P4/P12,
  reviewer synthesis).
- **Rate-limiting + query monitoring** as containment for extraction-style abuse; budget for residual leakage
  (A40432: strongest config still ~28% CRR).

## Known bypasses

Demonstrated or corpus-supported bypasses of this pattern's weaker forms:

- **Compromised internal agent (BU-MA) bypasses user-level gates** — author-reported Adv-IMBIA only reduced
  BU-MA ASR by 7% for MetaGPT (A41134). User-interface-level defense largely fails against internally
  compromised agents.
- **Verifier / score gaming** — a gate keyed solely on a certificate/score can be handed a spoofed high-
  confidence value for the wrong outcome (A37924, white-box + known σ).
- **Indirect prompt injection is not fully caught** — no evaluated agent was safe against it (A41090);
  A41468 residual ADR only >85% on indirect PI and >50% on contextual policy violation (author-reported).
- **Leakage / actions outside the declared policy set** — A40484 does not catch inference paths outside its
  predefined constraints C; A40432 leaves ~28% residual CRR.
- **Encoding/normalization gaps** — if canonicalization is incomplete, emoji/cipher/cross-lingual recombination
  slips a semantically-harmful action past a surface matcher (A40296, A40465, A41058, A40916).
- **Guardian-LLM injectability** — if an LLM is (wrongly) made authoritative, it is itself a prompt-injectable
  trust anchor (A41468 reviewer synthesis).
- **Router evasion of selective gating** — a benign-looking request bypasses a vulnerable-region router
  entirely (A41129).

## Residual risks

- **No gate drives attack success to a safe floor.** Leading defenses in the corpus leave material residual:
  A41468 contextual policy violation >50% / command injection >76% ADR; A40432 ~28% residual CRR; A42191 ~31%
  residual ASR; A40248 ~16% residual harmful (all author-reported). No paper claims elimination.
- **Adaptive attackers are unevaluated across essentially every defense here** — the largest methodological gap
  (both syntheses). Deployed efficacy may be materially below reported numbers.
- **Policy/constraint incompleteness is silent** — the gate cannot enforce what was never declared (A40484).
- **Prompt-level reasoning is self-inconsistent** — cannot be the last line (A41090).
- **Coarse, non-reproducible evidence** for the flagship policy-gate paper — A41468 ADR is ">X%" thresholds with
  no FP accounting, no dataset size, no artifacts (Evidence: Preliminary).
- **The audit trail's integrity is asserted, not demonstrated** (A41468) — a compromised log undermines
  containment and forensics.
- **Deterministic gates can over-block**, eroding operator trust until bypassed (P8, reviewer synthesis) — the
  precision/recall frontier is itself a residual risk to manage.

## Relevant research (stable paper ids from the syntheses/cards)

Primary:
- **A41468** — InfrastructureSentinel: four-layer (input filter → tool-plan validation → runtime execution gate
  → immutable audit) natural-language policy enforcement for MCP agents. *Evidence: Preliminary* (coarse ADR, no
  adaptive test, no FP accounting).
- **A41090** — MobileSafetyBench: agent action gating with `refuse()`/`ask-consent()`, rule-based state-grounded
  evaluators; "capability ≠ permission ≠ safety"; prompt-level safety necessary-but-insufficient. *Evidence:
  Strong (as a susceptibility benchmark); its own defense (SCoT) is weak.*
- **A41134** — IMBIA / "Shadows in the Code": multi-agent pipeline injection; MU-BA vs. BU-MA defense
  asymmetry; least-privilege capability isolation. *Evidence: Moderate.*
- **A40484** — SafeNLIDB: constraint-aware, history-aware multi-turn access decision (`Safe(x)`); multi-turn
  inference-leakage attacks. *Evidence: Moderate.*
- **A39818** — TowerMind: action-validity gating, "models propose, environment verifies, gate decides",
  invalid-action-rate monitor. *Evidence: Moderate for its benchmark purpose; Preliminary as a security
  artifact.*
- **A37924** — GhostCert: "a verification artifact is not a correctness oracle"; verifier gaming. *Evidence:
  Strong.*
- **A40432** — RAGFort: dual-path / single-point-insufficient; residual ~28% CRR; rate-limiting + query
  monitoring. *Evidence: Moderate (leaning strong).*

Supporting: A41129 (EASE, selective reasoning helps text refusal, insufficient for actions), A41152 (VALOR,
layered detect→gate→verify; intention FNR ~31–33% with a small rewriter), A41498 (GARD, taxonomy-grounded I/O
detector), A40840 / A36996 (history injection → authenticate history provenance), A40296 / A40465 / A41058 /
A40916 (encoding/cipher/cross-lingual evasion → normalize before gating), A41145 (ROME targeted erasure for
containment), A40248 (shallow-alignment mechanism; enforce deep, not at the prefix).

Reviewer-synthesis cross-references (skill artifacts, **not** AAAI corpus papers): architecture-patterns.md
P1 (pre-action gate), P2 (effect-based evaluation), P6 (least-privilege credential broker), P8 (anti-
over-blocking), P10 (async explainability), P12 (adaptive red-team); agent-identity.md (Zero Standing
Privilege, just-in-time/just-enough, intent-based access).

## Evidence strength

- **The architectural thesis is well-supported by convergence, not replication.** "Capability ≠ permission ≠
  safety" and "defense-in-depth aligned to the agent cognitive cycle" are convergent across A41468, A41090, and
  A41134 — but these are **independent studies in different domains, not independent replications of one
  result** (both syntheses state this explicitly). Treat the convergence as a strong *design* signal, not a
  measured effect size.
- **The "verifier ≠ correctness oracle" caution is Strong** (A37924: large-scale ImageNet, three certified
  defenses, targeted+untargeted, released code) — the most rigorously evaluated single result relevant to this
  pattern.
- **The efficacy of any specific policy-gate implementation is Preliminary-to-Moderate.** The flagship gate
  paper (A41468) is Preliminary; A41090's contribution is a susceptibility benchmark (Strong) whose own defense
  is weak; A41134 is Moderate.
- **All efficacy numbers are author-reported, not independently verified, and best-case** — no adaptive-attacker
  evaluation exists in the corpus for these defenses. Report absolute residuals and validate on the target stack
  before operational reliance.
- **Deterministic, fail-closed, least-privilege design choices are reviewer-synthesis engineering best practice**
  grounded in the papers' failure modes, not themselves a paper-measured result.

## When NOT to use this pattern

- **When the capability can simply be removed.** Prefer least-privilege elimination to gating: if a role never
  needs a tool, don't expose it and then gate it. The gate is for capabilities that must exist but must be
  conditionally permitted (A41134 capability isolation; A41468 "gate, not replace, least privilege").
- **As the sole control.** Every defense card in the corpus ends with "should be a layer, not the sole control";
  a lone gate leaves material residual (A41468, A40432). Pair with least-privilege, human approval, monitoring,
  and adaptive red-team.
- **As a substitute for a structural trust boundary.** If untrusted content is not separated from executable
  instruction, a gate downstream can be "talked past" (A41134 positional injection; A41090).
- **For pure content-safety / toxicity / disclosure filtering.** That is a content-guardrail layer (A41498 GARD,
  A41152 VALOR), a different pattern; a permission gate decides *actions*, not text toxicity.
- **When no deterministic policy can be declared and you would be forced to make an LLM the sole authority.**
  That is a content classifier, not a permission gate, and A37924 + A41468 (reviewer synthesis) show why a
  single-artifact/LLM authority is gameable. Either declare a deterministic policy or treat the LLM output as
  advisory-only.
- **For fully reversible, low-stakes actions where gate latency/over-refusal cost exceeds the harm** — "prove
  before you veto" (P8, reviewer synthesis); reserve hard fail-closed gating for high-stakes/irreversible
  operations (A41090's high-risk task class), and measure over-refusal as a first-class cost (A41074, A41140).
