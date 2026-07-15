# Quality Review — Lens: Security Architect

**Scope reviewed.** Syntheses: `AILLM-Safety.md`, `Adversarial-ML-Attacks.md`, `Privacy-Protection.md`,
`Multi-keyword-match.md`, `Network-Cyber-Security.md`, `Model-IP-Protection.md`, `Deepfake-Forgery-Detection.md`,
`Defense-Mitigation.md`. Patterns read in full for the control-enforcement lens:
`policy-permission-gates.md`, `human-approval-consequential-actions.md`, `least-privilege-credentials.md`,
`tool-capability-isolation.md`, `kill-switches.md`, plus `sandboxed-execution.md`,
`prompt-injection-containment.md`, `retrieval-authorization.md` (skimmed). Plus `ontology.md`,
`source-index/relevance-triage.md`.

**Lens question.** Do the control playbooks specify (a) *where* the enforcement point sits, (b) *fail-closed*
behavior, (c) *trust assumptions*, and (d) *where the actor can influence the enforcement point itself*?

**Headline.** On this lens the base is genuinely strong — stronger than most production security docs. Enforcement
points are named at the correct architectural layer, fail-closed is a first-class section in every control, trust
assumptions are enumerated *and* labeled as failure points, and "the defense's own decision surface is attackable"
is treated head-on (gate-LLM injectability, release-path injection, summary-poisoning, trigger suppression/DoS).
The findings below are real seams, not a verdict that the work is weak. Most are *cross-pattern* gaps that no single
playbook owns — which is exactly the class an adversarial architect review exists to catch.

---

## 1. Findings

### F1 — SEVERITY: major — Root-of-trust is a dangling forward-reference; no playbook owns identity/attestation
**Where.** `human-approval-consequential-actions.md` (Preconditions, "Authenticated approver identity … the corpus
does not evaluate approver-identity spoofing; treat it as an assumed-secure dependency to be covered by the
agent-identity / credential controls"); `kill-switches.md` (Preconditions, "Authenticated, rate-limited trigger
authority … the corpus does not evaluate trigger-authority spoofing — treat it as an assumed-secure dependency
covered by the agent-identity / credential controls"); `least-privilege-credentials.md` (Preconditions,
"Trustworthy attestation signals … Spoofable attestation voids ZSP — the brief itself flags **'Local Agent Identity
Attestation'** … as the unshipped gap").

**Exact problem.** Three separate enforcement playbooks each bottom out their authentication precondition by
*forwarding it to "the agent-identity / credential controls."* But the credential playbook, the supposed owner,
names local attestation as **the unshipped gap** — and offers a fallback (short-lived scoped bearer) only for
*itself*; the approval gate and the kill switch are simply told to "assume secure." Every enforcement point in the
set presumes an authenticated principal, and the primitive that authenticates the principal is (a) unbuilt and
(b) un-owned. An architect reading these five patterns cannot find the answer to "how is the approver / the
trigger-puller / the workload actually authenticated, and what is the fail-closed behavior when attestation is
unavailable?" This is the single load-bearing assumption under the whole enforcement stack, and it is a citation to
a component that does not exist.

**Fix.** Add an `identity-attestation-root-of-trust` playbook (or a shared section the three consumers cite by
name) that: (1) names the authenticating authority and issuer/signature-verification chain explicitly (the
`agent-identity.md` "no trusted identity without a trusted issuer" material already exists — promote it to a
pattern); (2) defines fail-closed behavior *for each consumer* when attestation is unavailable (credentials already
has "fall back to short-lived scoped bearer"; approval and kill-switch currently have **none** — they need "deny /
hold for out-of-band human step-up," not "assume secure"); (3) replaces the three independent "assumed-secure"
forward-references with one concrete mechanism so the gap is owned in exactly one place.

### F2 — SEVERITY: major — Audit is explicitly off the fail-closed path, so consequential actions fire before their evidence record is durable
**Where.** `policy-permission-gates.md` — System architecture ("L4 Immutable audit + async explanation … generated
async → zero added latency"), Telemetry ("generated **asynchronously** so it adds zero decision latency"),
Recommended pattern item 8. `human-approval-consequential-actions.md` — Control mechanism step 5 emits an immutable
audit record, but Failure handling enumerates fail-closed triggers (gate/summarizer unavailable, approval timeout,
provenance unestablished, normalization ambiguous, aggregate crosses tier, classifier uncertain) and **audit-write
failure is not among them.**

**Exact problem.** The patterns correctly make audit the "Evidence" leg of CPVER and repeatedly stress "a check that
passed is not itself proof the check was sound." But by moving audit *off* the decision latency path for
performance, the design lets an `ALLOW` fire — and the irreversible side effect execute — *before* the decision
record is durably committed. For the exact class these gates exist to protect (funds transfer, deletion, access-
control change, actuation), an action that executes before its audit is durable is a non-repudiation and forensic
gap: an attacker who can stall or crash the (async, best-effort) audit subsystem gets consequential actions with no
guaranteed record. Async audit is fine for reversible/low-stakes actions; it is wrong for the high-consequence
branch the gate is built for.

**Fix.** Tier the audit durability guarantee to the action's risk tier (the patterns already tier the *gate* this
way). For consequential/irreversible actions, require **write-ahead / synchronous durable commit of the decision
record before actuation** (audit-commit is a precondition of the side effect, and audit-write failure is a
fail-closed trigger → deny/hold). Keep async audit only for the reversible/low-stakes path. State this explicitly in
`policy-permission-gates.md` L4 and add "audit-write failure → deny" to `human-approval` Failure handling.

### F3 — SEVERITY: major — "Fail-closed = deny/halt" is assumed universally, but for embodied actuators the null action is not necessarily the safe action
**Where.** `policy-permission-gates.md` Failure handling ("Degrade to least privilege, never to open access");
`human-approval-consequential-actions.md` Failure handling ("→ deny the action. Never fail-open");
`kill-switches.md` Control mechanism / Failure handling ("the *enforcement* default is **halt** (fail-closed toward
containment)"; dead-man default "the agent halts if it cannot confirm the supervisory channel"). All three list
**physical actuation / actuator command** as an in-scope asset.

**Exact problem.** For digital side effects the equation *fail-closed = don't-do-it* is correct (not sending funds
is safe). For an embodied system in motion it is not: cutting power to a robot arm holding a load, "halting" a
process driving a vehicle mid-maneuver, or freezing an actuator mid-trajectory can be the *dangerous* action.
Across the whole enforcement set, "fail-closed" is uniformly rendered as deny/no-op/terminate-the-process, with no
notion of a defined *safe state* for an actuator. This is not a niche edge case — this knowledge base explicitly
exists to ground the **Origin Physical AI safety stack**, and `sandboxed-execution.md` / `kill-switches.md` both
enumerate actuator commands as the target surface. The one control that is closest (kill-switch dead-man/heartbeat)
still says "halts the agent," inheriting the same unsafe assumption.

**Fix.** Introduce a "safe-state" abstraction for embodied/latency-critical actuators and redefine fail-closed for
that class as *"transition to a declared per-actuator safe state"* (controlled stop, hold-position, reduce-to-safe-
velocity, or attested hand-back to a human/hardware interlock) — **not** deny/terminate. Make "a declared safe state
exists and is reachable without the agent's cooperation" a precondition in `kill-switches.md`,
`policy-permission-gates.md`, and `human-approval` (its "When NOT to use → latency-critical loops" note already
hints at this but stops short). This also resolves the latent contradiction where `policy-permission-gates` routes
ambiguous high-stakes actions to `STEP_UP`→human while `human-approval` says a human is a design mismatch for
real-time control — both need to point at a deterministic safe-state fallback for the physical case.

### F4 — SEVERITY: major — Multi-agent (agent→agent) delegated-authority has no enforcement point, though the corpus calls it the hardest case
**Where.** The compromised-internal-agent (BU-MA) finding is cited as defeating user-level gates across
`policy-permission-gates.md` ("Adv-IMBIA reduced BU-MA ASR for MetaGPT by only 7%"), `tool-capability-isolation.md`,
and `kill-switches.md`; `least-privilege-credentials.md` calls "attenuated N-hop sub-delegation with attribution …
**the least-solved problem**." Yet every enforcement point in every playbook is placed at the **agent→tool /
agent→external** boundary. There is no pattern in `patterns/` for inter-agent message authorization or attenuated
delegation.

**Exact problem.** The playbooks correctly *diagnose* that a compromised peer/sub-agent, acting through a
legitimately-scoped credential and emitting an in-scope-but-malicious action or a widened sub-delegation, sits
*inside* the boundary every named gate guards — so none of them fire. But they leave the reader with a diagnosis and
no prescription: where do you place the enforcement point for the message one agent sends to another, or for a
delegation that must only ever *narrow*? "Treat every model-visible field as untrusted data" (tool-capability-
isolation) covers peer *content* but not peer-conferred *authority*. This is the exact surface the corpus flags as
least-solved and highest-consequence, and it has no playbook.

**Fix.** Add an `inter-agent-authorization` / `attenuated-delegation` pattern that places a deterministic gate at
the orchestrator / message-bus chokepoint (out-of-band from the agents, per the kill-switch's own "enforce below the
agent" principle): deny-by-default on peer-emitted actions, structural enforcement that a sub-delegated scope is a
strict subset of the delegator's, N-hop attribution back to the originating human, and peer messages classified as
untrusted for *authority* as well as content. Cross-reference A41134 (BU-MA), A40231 (MPAS inter-agent message
injection at topologically critical nodes, already cited in `retrieval-authorization.md`), and the
`agent-identity.md` attenuated-delegation material.

### F5 — SEVERITY: minor — Fail-closed covers *detected* ambiguity but not *undetected* canonicalization incompleteness — the named live bypass
**Where.** `policy-permission-gates.md` — Recommended pattern item 3 ("Canonicalize … Gate on recovered intent")
runs in parallel with Verification item ("Effect/outcome-based evaluation in a sandbox") without ranking which is
authoritative; Failure handling fails-closed on "missing/ambiguous context"; Known bypasses admits "if
canonicalization is incomplete … slips a semantically-harmful action past a surface matcher." Same shape in
`human-approval-consequential-actions.md` (Failure handling "Normalization ambiguous → escalate"; Recommended item 2
"normalize before you gate") and `tool-capability-isolation.md`.

**Exact problem.** The encoding attack space (emoji/glyph A40296, math+code A40465, 21-cipher A41058, cross-lingual
A40916) is open-ended, so a canonicalizer can *confidently return a benign-looking canonical form that is wrong*.
That is the actual bypass the patterns disclose — and you cannot fail-closed on a failure the canonicalizer does not
detect. The fail-closed rules only fire on *detected* ambiguity. Meanwhile "gate on recovered intent" and "gate on
sandboxed effect" are presented as peers, so a reader may legitimately implement intent-recovery as the sole
pre-execution signal for an irreversible action that *cannot* be dry-run (a transfer can't be simulated), where
incomplete canonicalization is the only thing standing between the actor and the effect.

**Fix.** State the signal ranking explicitly: canonicalization is **advisory**; for irreversible / un-simulatable
actions the authoritative pre-execution signal is effect-based/sandbox resolution where possible, and where it is
not possible, **default-deny on any argument class the canonicalizer cannot certify as fully normalized** (treat
"unable to certify canonical" as the fail-closed trigger, not just "detected ambiguity"). Add the "un-simulatable
irreversible action" as a named hard case in `policy-permission-gates.md`.

### F6 — SEVERITY: minor — "Immutable / tamper-evident audit" is a precondition in five patterns but its mechanism is un-owned (correctly disclosed, not yet prescribed)
**Where.** `policy-permission-gates.md`, `human-approval`, `least-privilege-credentials.md`,
`tool-capability-isolation.md`, and `kill-switches.md` all list an immutable/tamper-evident audit store as a
precondition and each honestly notes "you must supply the integrity/tamper-resistance mechanism A41468 asserts but
leaves unspecified." A dedicated `tamper-evident-traces.md` / `secure-logging.md` exists in `patterns/`.

**Exact problem.** This is disclosed well (not a hidden gap) but the same unspecified dependency is repeated five
times without any of the five action-enforcement playbooks pointing at the concrete mechanism. Since dedicated
trace/logging patterns exist, the enforcement patterns should *cite them as the owner* rather than each re-flagging
the hole — otherwise a reader concludes the mechanism is universally missing rather than located elsewhere.

**Fix.** Have all five enforcement patterns cross-reference `tamper-evident-traces.md` as the owning control for the
audit-integrity precondition, and confirm that pattern actually specifies a mechanism (append-only + hash-chain /
signed segments + external anchoring) with its own fail-closed and threat model. Ties directly into F2 (durability)
and F1 (the log's own root-of-trust).

---

## 2. Done well (specific)

- **Fail-closed is a first-class, enumerated section in every enforcement control — not a slogan.** Each pattern has
  a dedicated "Failure handling" section that lists the concrete triggers (gate error, timeout, missing/ambiguous
  context, provenance-unestablished, policy-engine/LLM disagreement) and the resulting action (deny / STEP_UP /
  degrade-to-least-privilege). `kill-switches.md` goes further and handles **both** failure directions — miss
  (trigger suppressed) *and* weaponization (abstention-as-DoS, A37924) — which is a subtlety most real playbooks
  omit.

- **"The enforcement point itself is attackable" is treated head-on — this is my exact lens and it is covered
  unusually thoroughly.** The set consistently refuses to trust its own decision surface: gate-LLM injectability
  ("using an LLM to defend an LLM agent creates an injectable trust anchor"), release-path injection ("any
  model-visible field is an injection surface," A42239, so credential release must be environment-side),
  approval-**summary** poisoning as a distinct surface (A41108 STACK / A41144 MFA extended to the human-reviewer
  channel), trigger suppression *and* forgery (kill-switch), and the generalized principle "**treat every new
  trust-decision surface a defense introduces as attackable**." Actor-influence-on-the-enforcement-point is exactly
  where these docs are strongest.

- **Enforcement points are placed at the architecturally correct layer, with the capability/permission split kept
  clean.** "Enforce at the last controllable point before the side effect" (A41468 L3), deterministic +
  environment-side + not-model-injectable, "capability ≠ permission ≠ safety" as the spine, the credential-side
  (broker: govern the *means*) vs action-side (gate: govern the *action*) division, and the kill-switch's
  "enforce *below* the agent, out-of-band" for the compromised-agent case. Trust assumptions are not only listed but
  each is explicitly labeled "a documented failure point," and adaptive-attacker evaluation is named as a *launch
  gate* rather than a nice-to-have — the calibration an architect wants.

---

## 3. Biggest risk from my seat

Every enforcement point in the stack is well-built but presumes an authenticated principal, and the primitive that
authenticates that principal (approver identity / workload attestation / trigger authority) is punted by three
separate playbooks to "the agent-identity/credential controls," which in turn names local attestation as *the
unshipped gap* — so the entire control plane's root of trust is a citation to a component that does not yet exist and
that no pattern owns (F1).
