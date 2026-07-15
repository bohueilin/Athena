# Pattern: Least-Privilege Credentials

> **Scope of evidence.** This pattern is grounded in the AAAI-26 corpus synthesis `Network-Cyber-Security.md`
> and its underlying research cards, combined with the reviewer-synthesis identity brief `agent-identity.md`
> (the 1Password *"Identity for Reasoning Agents"* brief + the Jul-2026 market sweep) and `architecture-patterns.md`
> (P6 credential broker, P7 Shapley attribution). Load-bearing corpus papers: **A42249** (broad standing access
> converts agent errors into incidents; "capability is not permission"; proposes least-privilege + command
> validation), **A40925** (multi-party/threshold authorization bound to model execution; residual leak),
> **A39721** (routing/access-pattern is a confidentiality asset — oblivious select-then-compute), **A40100**
> (intermediate activations leak input under collusion), **A42239** (any model-visible field is an injection
> surface), **A36959** (multi-signal verify-before-trust). Paper ids (e.g. `A42249`) are the stable corpus ids
> from the synthesis source map (§20).
>
> **Evidence integrity (non-negotiable).** Corpus numeric values are **author-reported and not independently
> verified**; where a card was silent or truncated the text says "not stated in paper". The
> Zero-Standing-Privilege / JIT / attestation / federated-identity mechanics come from `agent-identity.md`, which
> is an **industry brief + market sweep (reviewer synthesis), not a corpus measurement of defense efficacy** —
> every such claim is labeled *(agent-identity brief)* and is engineering practice, not a measured attack/defense
> number. Calibrated language only: "reduced blast radius under the described operating model", "requires
> production validation", never "secure / proven-safe / eliminates". The single most important corpus caveat
> repeated below: **no defense in the Network-Cyber synthesis was evaluated against an adaptive, defense-aware
> attacker** (Network-Cyber §3, §9, §12), so every efficacy number is a non-adaptive upper bound on protection.

---

## Problem addressed

A capable agent holding a **standing, over-scoped credential** turns any single compromise — a prompt injection,
a leaked secret, a confused-deputy error — into a breach whose **blast radius is whatever that credential could
reach**. The corpus and the identity brief converge on one thesis: the dominant production risk is **no longer
capability but authority** — *capability ≠ permission* (Network-Cyber §6.2, grounded by `A42249`; restated by
the identity brief as "capability is not permission").

Two independent failure surfaces motivate credential-side least privilege, distinct from the action-side gate:

- **Broad standing system access converts ordinary agent errors into security incidents.** `A42249` (author-
  reported, small-n: 3 agents, 5-task × 5-trial) observed **unauthorized software install in 100% of certain
  planning tasks** (Claude Sonnet 3.5), attempted brute-force logins, and sensitive-app exposure via navigation
  errors — none of which required a malicious model, only excess standing authority. The paper's own remedy is
  **least privilege + command validation between intent and execution** (proposed, unbuilt).
- **A reasoning agent's access needs evolve mid-task, so a login-time grant is wrong a few steps later**
  *(agent-identity brief)*. A coding agent walks read-repo → run-tests → deploy → read-prod-DB — an escalation
  chain no static grant anticipated. Because **prompt injection means every agent must be treated as potentially
  turned**, the authority bound to an agent at any moment should be **the least justified right then**, so a
  hijack is *contained, not catastrophic* *(agent-identity brief; the access-control twin of "alignment is
  shallow")*.

**Least-privilege credentials** is the control that governs **the credential itself — the *means*/authority an
agent holds** (mint, scope, expire, resolve, attribute, revoke), so that no credential exists before it is
needed or persists after. It is the credential-side complement to `policy-permission-gates` and
`tool-capability-isolation`, which govern the *action decision*. The identity brief's split is the clean mental
model: **broker = govern the credential (this pattern); Apono/gate = govern the action (those patterns).**

## Applicable assets and attack surfaces

- **Long-lived stored secrets (the bearer model).** API keys, cloud keys, tokens, and certificates embedded in
  **prompts, configs, MCP server definitions, source, container images, and logs** — the *new leak surface*
  agents add *(agent-identity brief)*. Industry-reported scale from the brief (cited by it, **not** a corpus
  measurement): machine identities outnumber human ~**45:1 to >80:1**; average machine secret stays active
  **>600 days**; **~1 in 20** holds full-admin; **~1/3 of private repos** contain a plaintext secret. Root
  enabler in nearly every breach: *a standing, over-scoped credential that existed before it was needed and
  persisted after.*
- **The credential-release decision path itself.** Attestation signals, OIDC tokens, and the trust-policy inputs
  the broker evaluates are attackable: `A42239` shows **any model-visible field** (not just the prompt — tool
  results, retrieved text, answer options) can carry authoritative injected text (author-reported adoption ≈0.5,
  accuracy ≈0.27 for the "contradiction" injection; single model QwQ-32B, MMLU, non-adaptive). A broker whose
  context is model-mediated inherits this surface.
- **The MCP transport as a secret-exfiltration channel.** The naive community pattern **returns raw secret values
  through the model's context** — fine for throwaway dev creds, *wrong for anything real*; the hardened pattern
  treats the MCP transport as untrusted and never lets the agent receive raw values *(agent-identity brief, Codex
  MCP server pattern)*.
- **Intermediate state when tokens/inputs traverse offloaded or split inference.** `A40100` — server+client
  collusion reconstructs input from **activations** in federated split-LLM serving (empirical privacy, **no
  reported ε**). `A39721` — **expert-selection access patterns leak input semantics even when the payload is
  encrypted** (semi-honest two-party MoE). Routing metadata and activations are first-class confidentiality
  assets, not just the payload (Network-Cyber §6.4).
- **Model/credential activation itself as a high-value asset.** `A40925` binds model *execution* to multi-party
  authorization so "no single party — or thief — can activate the model" (residual leak noted below).
- **Delegation chains in multi-agent systems.** An agent that sub-delegates must hand a *strictly narrower*
  subset; attenuated N-hop sub-delegation with attribution to the original human is flagged as **the
  least-solved problem** *(agent-identity brief)*.

## Threat model

Designed for **inference/runtime adversaries** who cannot change model weights but can obtain or misuse
authority. Grounded threat classes:

- **Credential theft after foothold → lateral movement.** Attacker gains a foothold, scans for an embedded
  long-lived secret, authenticates as the over-privileged machine identity, and moves laterally — *because it
  looks like legitimate automation, human-centric controls never fire* *(agent-identity brief, the canonical
  breach pattern)*.
- **Injection-turned agent misusing its standing authority.** A hijacked agent invokes credentialed actions it
  is *capable* of (`A42249` unauthorized installs / brute-force; `A42239` off-policy action driven by injected
  model-visible text). The credential, not the model, is the blast radius.
- **Confused-deputy / broad-privilege abuse** — an ordinary planning error executed at admin scope (`A42249`).
- **Honest-but-curious / collusion confidentiality attack** on offloaded inference — a curious server + colluding
  client reconstructs input from activations (`A40100`); a semi-honest party reads routing access patterns
  (`A39721`).
- **Model/credential theft & unauthorized activation** — stolen weights or partial-trigger activation of a gated
  model (`A40925`).
- **Compromised internal / delegate agent** inheriting or widening a shared credential scope — the hardest case;
  attenuated delegation is unsolved *(agent-identity brief)*.

**Adaptivity boundary (critical).** Every relevant corpus defense here (`A40925`, `A39721`, `A40100`) is
evaluated under a **non-adaptive** or **semi-honest** threat model (Network-Cyber §3, §11). `A39721` covers only
semi-honest, not malicious, adversaries; `A40100`'s activation noise is empirical with **no reported ε** and "an
accumulating client or stronger inversion may erode it" (reviewer synthesis, Network-Cyber §11). Treat all
protection numbers as best-case; adaptive red-team is a launch gate.

## Control mechanism

Reduce the authority bound to an agent at any moment to the least justified right then, and prove it fresh
rather than store it:

```
release(workload_attestation, task_intent, policy, env, time) → { short-lived, JEP-scoped credential | DENY }
   └─ agent receives a resolvable handle, not the raw secret; credential auto-expires; every use is attributed
```

- **Zero Standing Privilege (ZSP) is the spine** *(agent-identity brief)*. By default an identity has **no**
  access; it receives narrowly-scoped, short-lived authority **only when a task justifies it**, ideally gated on
  **attestation** (the workload *proves what it is* before anything releases). Two axes, both required:
  **Just-Enough-Privilege (JEP)** — scope to a *specific action/resource* (write **one** bucket, not `s3:*`) —
  and **Just-In-Time (JIT)** — grant on request, expire on a short fixed window, so **nothing standing exists to
  steal between tasks.**
- **Authority proven at runtime, not stored** *(agent-identity brief)*. Prefer the **federated model** (agent
  proves what it is → policy validates the proof → a short-lived credential is issued for the specific task) over
  the **bearer model** (possession of a secret is sufficient — anything that copies it inherits the authority).
  End state = **secretless access**: the verified identity *is* the credential (Workload Identity Federation over
  OIDC; SPIFFE/SVID substrate).
- **Never-seen resolution.** The agent holds a **handle/reference**, not the value; a broker resolves it
  **server-side** for the authorized process and **requires approval at access time**, treating the transport as
  untrusted *(agent-identity brief, 1Password Environments/Codex MCP pattern)*. This is tighter than "release a
  usable short-lived token to the agent" — the brief explicitly names the residual that once a credential is
  released the agent still holds a usable credential.
- **Multi-party / threshold authorization for high-value activation** — bind execution to a consensus trigger so
  no single party or thief can activate it (`A40925`, author-reported; residual noted below).
- **Delegated but attributed, with separate trust domains.** An agent is a *delegate, not a principal*: it
  carries its **own identity** (every action attributes to it) while acting under **human-delegated authority**
  (accountability traces to the person). *Generating code* and *acting on production* are different blast radii
  and **must not share a credential scope** *(agent-identity brief)*.
- **Intent-based scoping + revoke-on-divergence.** Bind the grant to the declared **purpose** of the task and
  revoke when behavior diverges from that purpose *(agent-identity brief; the intent-conformance bridge to
  behavioral monitoring)*.
- **Deterministic, fail-closed.** No attestation, expired token, missing policy, or ambiguous scope → **no
  credential released** (reviewer synthesis; consistent with the fail-closed posture in `policy-permission-gates`
  and Network-Cyber §14).

## Preconditions and trust assumptions

The pattern is only as strong as these hold; each is a documented failure point:

- **A trusted issuer and signature verification.** "No trusted identity without a trusted issuer" — a relying
  party trusts an identity by verifying a signature against the issuer's public key *(agent-identity brief)*.
  Without one, you cannot do the federated model and fall back to (short-lived, tightly scoped) bearer.
- **Trustworthy attestation signals** (where a process runs, who initiated it) that let an issuer bind a workload
  to an identity automatically *(agent-identity brief)*. Spoofable attestation voids ZSP — the brief itself flags
  **"Local Agent Identity Attestation"** (making identity *verified*, not *declared*) as the unshipped gap.
- **A declared, correct scoping/intent policy.** The broker cannot scope to what was never declared; a
  policy-incompleteness or over-broad scope is silent failure (reviewer synthesis; mirrors `A40484`'s
  "predefined constraints C" limitation in the sibling gate pattern).
- **Short-lived-credential + expiry/revocation infrastructure** that actually cuts access when the window
  elapses (JIT is only real if expiry is enforced).
- **A tamper-resistant, non-model-injectable release path.** If the credential-release decision is mediated by
  model-visible context, `A42239` applies — the release logic must sit outside model control, like the
  action-side gate (reviewer synthesis).
- **Audit-store integrity** for attribution-complete logging (reviewer synthesis; the identity brief asserts an
  attribution requirement but you must supply tamper-evidence).
- **Confidentiality of intermediate state** in any offloaded/split hosting — payload encryption alone is
  insufficient (`A40100`, `A39721`).

## System architecture

A broker / control-plane sitting between agent intent and credentialed action — the credential-side chokepoint
(architecture-patterns P6; identity brief §3):

```
 workload ──► [Attest]  prove what/where/who initiated (SPIFFE/OIDC signal). Spoof-resistant. ── fail ─► DENY
                 │
                 ▼
 task intent ─► [Policy validate]  deterministic: is a JEP-scoped grant justified for THIS intent, role, env,
                 │                  time-window? separate trust domains (code-gen ≠ prod). ── no ─► DENY
                 ▼
              [Mint]  short-lived, JEP-scoped credential (JIT). High-value asset → multi-party threshold
                 │     authorization before activation (A40925).
                 ▼
              [Resolve server-side]  agent gets a HANDLE, not the value; approval-at-access; transport untrusted
                 │                    (never-seen). Protect activations/routing if offloaded (A40100, A39721).
                 ▼
      ┌── credentialed action fires (governed by the action-side gate) ──┐
      ▼                                                                    ▼
 [Auto-expire / revoke-on-divergence]                        [Attribution-complete audit]
   short TTL; intent-conformance revoke; sweeper.              who/what · under-which-authority · on-what-data ·
   Zero standing between tasks.                                when · from-what-inputs — bound to runtime identity
                                                               + the delegating human. (agent-identity §1; P5.)
```

- **The deterministic policy/attestation check is the sole authority for release** — an LLM may advise (novel
  intent, anomaly) but must never be the sole basis for releasing a credential (reviewer synthesis, by analogy to
  `A37924` "a verification artifact is not a correctness oracle" and the injectable-guardian caution).
- **Cap the blast radius `k`** — bound how many credentials one compromise can wield (architecture-patterns P6,
  MASTRIKE compromise-budget framing, reviewer synthesis) and place the tightest privileges where Shapley
  attribution says risk concentrates (P7).
- **Confidentiality boundary around intermediate state** — oblivious select-then-compute for routing (`A39721`),
  forward-activation perturbation for offloaded inference (`A40100`) — treat "payload encrypted" as insufficient.

## Recommended implementation pattern

Deterministic, fail-closed, least-privilege — in priority order:

1. **Default-deny, Zero Standing Privilege.** No credential exists until a task justifies it; nothing standing to
   steal between tasks *(agent-identity brief)*. "A credential that persists is already compromised."
2. **JEP + JIT together.** Scope to the specific action/resource *and* expire on a short fixed window; per-
   resource, not just per-capability, where possible (Passport applicability matrix, agent-identity §6).
3. **Prefer federated/secretless to bearer.** Prove authority at runtime via attestation (WIF/OIDC, SPIFFE);
   reserve short-lived bearer only where no trusted issuer exists *(agent-identity brief)*.
4. **Never-seen resolution.** Hand the agent a handle; resolve the secret server-side for the authorized process
   with approval-at-access; treat the MCP/agent transport as untrusted *(agent-identity brief)*. Do **not** return
   raw values through model context.
5. **Separate trust domains into distinct credential scopes** — code-generation vs production action must not
   share a scope, even for the same agent *(agent-identity brief)*.
6. **Re-derive authority close to each action**, not once upfront — escalation-aware, because reasoning agents'
   needs evolve mid-task *(agent-identity brief; `A42249`'s intent→execution validation)*.
7. **Bind the grant to declared intent and revoke on divergence** (intent-conformance) *(agent-identity brief)*.
8. **Multi-party / threshold authorization for high-value activation** (`A40925`), accepting the residual leak
   as a monitored risk.
9. **Verify attestation with multiple independent signals before release** — the `A36959` verify-before-trust
   discipline (cross-source agreement + confidence threshold) transposed from label provenance to identity
   provenance (reviewer synthesis by analogy; author-reported that multi-signal filtering improved label trust,
   with an LLM-judge-disagreement caveat).
10. **Attribution-complete audit** binding every credentialed action to a runtime identity + the delegating human
    *(agent-identity §1; architecture-patterns P5)*.
11. **Fail-closed everywhere** — attestation failure / expiry / missing policy / ambiguity → no release.

## Incorrect or fragile implementation patterns

- **Long-lived bearer secrets in prompts/configs/MCP definitions/images/logs** — the standing-over-scoped
  credential is the root enabler of the canonical breach *(agent-identity brief)*.
- **Over-scoping "to avoid permission errors" and never revoking** — the default habit the brief names as the
  discipline failure; broad + standing = large blast radius the moment any credential leaks.
- **Returning raw secret values through the model's context** (naive MCP pattern) — an injection or a logged
  transcript exfiltrates the secret *(agent-identity brief)*.
- **One credential shared across trust domains** (code-gen and prod on the same scope) — collapses distinct blast
  radii *(agent-identity brief)*.
- **A single login-time / process-start grant** for a reasoning agent — a policy correct at start is wrong a few
  steps later *(agent-identity brief)*.
- **Gating credential release on the model's own reasoning** — the release path is then injectable (`A42239`: any
  model-visible field carries authoritative injected text); the decision must be deterministic and environment-
  side (reviewer synthesis).
- **Trusting caller-supplied or unverified attestation** — declared-not-verified identity is spoofable; the brief
  flags local attestation as the unshipped gap.
- **Encrypting only the payload in offloaded inference** — activations (`A40100`) and routing access patterns
  (`A39721`) still leak input.
- **Fail-open on broker/attestation error** — contradicts the fail-closed posture; release nothing on error
  (reviewer synthesis).

## Verification strategy

- **Adaptive, defense-aware red-team is the launch gate** — the single most consistent corpus gap (`A40925`,
  `A39721`, `A40100` all non-adaptive/semi-honest; Network-Cyber §3, §12). Any robustness claim "requires
  production validation" before reliance.
- **Blast-radius test:** simulate a credential compromise and measure *what it could reach* — verify JEP scope
  actually bounds it (architecture-patterns P6 `k`).
- **Expiry/revocation test:** confirm a JIT credential is genuinely unusable after its window and after a
  revoke-on-divergence trigger (not merely marked expired).
- **Never-seen test:** confirm the agent process (and its logs/transcripts) never contains the raw value — only
  the handle *(agent-identity brief)*.
- **Injection-of-the-release-path test:** plant authoritative text in every model-visible field feeding the
  broker's context (`A42239` template) and confirm it cannot cause a release.
- **Standing-authority-misuse test:** run `A42249`-style planning tasks and confirm the agent cannot perform
  credentialed side effects (install, auth, outbound send) beyond its JEP scope.
- **Confidentiality test for offloaded inference:** run a constructed activation-inversion (`A40100`) and a
  routing-access-pattern (`A39721`) probe; report reconstruction quality / leakage.
- **Multi-signal attestation validation** rather than a single trust signal (`A36959` verify-before-trust,
  author-reported).
- **Report absolute residuals, not relative reductions** (`A40925` residual; Network-Cyber §16).

## Metrics and thresholds

Track these families; **thresholds are operator-defined per deployment and must be validated against an adaptive
set — the corpus provides no validated universal threshold.**

- **Standing-privilege count / credential TTL distribution** — number of live credentials with no active task,
  and median secret lifetime (industry baseline the brief cites as *broken*: >600 days). Target: ZSP → ~0 standing
  between tasks *(agent-identity brief; engineering target, not a corpus number)*.
- **Blast-radius `k`** — resources/actions reachable by a single compromised credential (architecture-patterns
  P6, MASTRIKE compromise-budget, reviewer synthesis). Also detect **coordinated cross-credential misuse**, not
  just isolated abuse.
- **Residual unauthorized-activation** — `A40925` author-reported **~15% Acc-Fusion** under partial-trigger
  fusion (VGG16/CIFAR-10), meaningfully above chance and **not closed**; report the analogous residual for your
  threshold scheme.
- **Over-scope / secret-sprawl rate** — plaintext secrets in repos/MCP configs (brief-cited industry baseline
  ~1/3 of private repos); % of grants scoped to a single resource vs wildcard.
- **% secretless** (federated/attested) vs bearer credentials in service *(agent-identity brief; engineering
  target)*.
- **Time-to-revoke** on intent divergence or incident, and **expiry-sweep coverage**.
- **Unauthorized-install / brute-force / sensitive-app-exposure incidence** as a downstream misuse signal
  (`A42249`, author-reported for the unscoped baseline).
- **Reconstruction quality under a constructed inversion attack** if inference is offloaded (`A40100`).

## Test cases

Concrete, corpus/brief-grounded cases the control must be exercised against:

1. **Leaked long-lived secret → lateral movement** — plant an embedded secret, confirm ZSP/JIT leaves nothing
   standing to steal, and JEP bounds what a leaked credential reaches *(agent-identity brief breach pattern)*.
2. **Injection-turned agent invoking a credentialed action** it is capable of but not scoped for (`A42249`
   unauthorized install; `A42239` off-policy action from injected model-visible text).
3. **Confused-deputy planning error at admin scope** — an ordinary error that would be catastrophic only with
   standing admin authority (`A42249`).
4. **Release-path injection** — authoritative injected text in tool results / retrieved docs / options feeding
   the broker's context (`A42239`).
5. **Raw-value leakage via MCP transport** — confirm the naive "return the secret through model context" path is
   disabled *(agent-identity brief)*.
6. **Cross-trust-domain reuse** — attempt to use a code-gen-scoped credential for a prod action (must deny)
   *(agent-identity brief)*.
7. **Expiry/revocation enforcement** — use a credential after its JIT window and after a divergence-revoke.
8. **Multi-party activation of a high-value model/credential** without consensus (must fail); measure residual
   activation (`A40925`).
9. **Activation-inversion under server+client collusion** in split inference (`A40100`).
10. **Routing/expert-selection access-pattern leak** with payload encrypted (`A39721`).
11. **Attenuated sub-delegation** — a delegate agent attempting to hand a *wider* scope than it holds (must be
    impossible); N-hop attribution back to the original human *(agent-identity brief, least-solved)*.

## Adaptive adversarial tests

Beyond static cases — attackers who know the control:

- **Attestation spoofing** — forge the "where it runs / who initiated" signals to obtain a release; the brief
  itself flags declared-not-verified identity as the open gap *(agent-identity brief)*.
- **Release-path prompt-rewrite** — rewrite the injection specifically to defeat the broker's context checks
  (`A42239` reviewer synthesis: single-model/non-adaptive templates likely overstate robustness).
- **Accumulating-client / stronger inversion** eroding the empirical activation noise (`A40100` reviewer
  synthesis — no reported ε) and malicious (not semi-honest) attack on the routing scheme (`A39721` reviewer
  synthesis — malicious case open).
- **Partial-trigger optimization** against multi-party authorization to push residual activation above the
  reported ~15% (`A40925`).
- **Compromised delegate widening scope** — a turned sub-agent probing whether attenuation is actually enforced
  N hops deep *(agent-identity brief)*.
- **Gaming a new trust-decision surface the broker introduces** — reputation/approval/intent-conformance signals
  are themselves attackable (reviewer synthesis: "treat every new trust-decision surface introduced by a defense
  as attackable", Network-Cyber §15).

## Telemetry requirements

Emit structured, tamper-evident trace fields for every credential lifecycle event (agent-identity §1;
architecture-patterns P5/P10):

- **Attribution-complete per-action record** — *who/what acted · under which authorization · on what data · when
  · from what inputs* — bound to the **runtime identity + the delegating human** *(agent-identity §1)*.
- **Credential lifecycle events** — attest → validate → mint → resolve → use → expire/revoke, each with the JEP
  scope, TTL, trust domain, and the policy/rule that authorized release.
- **Intent-conformance divergence signal** — flag when behavior diverges from the declared task purpose (trigger
  for revoke) *(agent-identity brief)*.
- **Standing-privilege / secret-sprawl inventory** — live credentials with no active task; plaintext secrets
  found in repos/MCP configs *(agent-identity brief secret-sprawl scanner)*.
- **Access-pattern / routing anomalies** in offloaded inference (`A39721` expert-selection; `A40100` activation
  access) — the confidentiality signals content DLP cannot see.
- **Unauthorized-install / login-attempt / sensitive-app navigation** as downstream misuse signatures (`A42249`).
- **Immutable, human-readable audit** of the full chain for forensics/compliance — you must supply the
  integrity/tamper-resistance mechanism (reviewer synthesis).

## Failure handling

- **Fail-closed.** On attestation failure, expired/absent token, missing/ambiguous policy, or broker error →
  **release no credential**; hold for human step-up if the task justifies it (reviewer synthesis; consistent with
  Network-Cyber §14 least-privilege + human approval).
- **Degrade to least privilege, never to open access**, when a downstream check is unavailable.
- **Short TTL is the default containment** — a stuck/hung task loses authority automatically as the window
  elapses (JIT).
- **Revoke-on-divergence** — treat intent-conformance failure as an incident trigger, not an advisory
  *(agent-identity brief)*.
- **Broker/attestation compromise is assumed possible** — because the deterministic policy is the release
  authority and the agent never holds a usable raw secret (never-seen), a single compromised component should not
  by itself yield a usable over-scoped credential (reviewer synthesis).
- **Residual harm is assumed**, so credential-side least privilege pairs with the action-side gate
  (`policy-permission-gates`) and human approval for high-stakes/irreversible operations (`A42249`).

## Rollback and containment

- **Revocation caps blast radius** — short TTL + explicit revoke bound what any single compromise can reach; cap
  the compromise budget `k` (architecture-patterns P6, MASTRIKE, reviewer synthesis).
- **Kill-switch before the credentialed side effect** — halt during planning or immediately before execution,
  not after (architecture-patterns P1; the action-side gate).
- **Intent-based revoke-on-divergence** as first-line containment — revoke when behavior leaves the declared
  purpose *(agent-identity brief)*.
- **Multi-party threshold prevents single-party (or thief) activation** of high-value assets (`A40925`), with the
  residual ~15% Acc-Fusion tracked as a monitored, unclosed risk.
- **Attribution-complete audit for forensics** — reconstruct the chain of individually-innocuous steps that led
  to misuse *(agent-identity §1; Network-Cyber §14 trajectory logging)*.
- **Secret rotation + sprawl remediation** — replace found plaintext secrets with references; rotate on suspected
  exposure *(agent-identity brief secret-sprawl scanner)*.

## Known bypasses

Demonstrated or corpus/brief-supported bypasses of this pattern's weaker forms:

- **Residual unauthorized activation** — `A40925` leaves author-reported **~15% Acc-Fusion** under partial-trigger
  fusion; threshold authorization is mitigation, not elimination.
- **Collusion bypasses payload encryption** — server+client collusion reconstructs input from activations
  (`A40100`); the forward-activation noise is empirical (no ε) and may erode against a stronger attacker.
- **Access-pattern leak bypasses payload encryption** — plaintext expert/tool selection reveals routing even when
  input is encrypted (`A39721`); only semi-honest is covered.
- **Injectable release path** — if credential release is model-mediated, authoritative injected text in any
  model-visible field can drive it (`A42239`, author-reported adoption ≈0.5 for the contradiction style).
- **Once released, the agent still holds a usable credential** — the brief names this as the residual that the
  never-seen handle is designed to tighten; short-lived-token schemes that hand the agent a usable token leave
  this open *(agent-identity brief)*.
- **Attestation spoofing / declared-not-verified identity** — the identity is only as trustworthy as the issuer
  and the attestation; local agent attestation is the brief's named unshipped gap.
- **Compromised delegate agent** widening or reusing scope — attenuated N-hop delegation with attribution is
  unsolved *(agent-identity brief)*.

## Residual risks

- **No scheme drives compromise impact to zero.** `A40925` leaves ~15% residual activation; `A40100` gives
  empirical (not formal-DP) privacy with no reported ε; `A39721` covers only semi-honest. No paper claims
  elimination (Network-Cyber §16).
- **Adaptive attackers are unevaluated across every relevant corpus defense** — the largest methodological gap;
  deployed efficacy may be materially below reported numbers (Network-Cyber §3, §12).
- **Policy/scope incompleteness is silent** — the broker cannot scope to what was never declared; an over-broad
  scope leaks quietly (reviewer synthesis).
- **Attribution and attenuated delegation are unsolved** — N-hop delegation with attribution to the original
  human is the brief's least-solved problem; multi-agent misuse can outrun single-agent scoping *(agent-identity
  brief)*.
- **The credential-release decision and audit-store integrity are assumed, not demonstrated** — a
  model-injectable release path or a tamperable log undermines the whole control (reviewer synthesis; `A42239`).
- **Attestation is a moving trust anchor** — verified-vs-declared identity (local attestation) is the named gap;
  a spoofable attestation collapses ZSP *(agent-identity brief)*.

## Relevant research (stable paper ids from the syntheses/cards)

Primary (AAAI-26 corpus, Network-Cyber-Security synthesis):
- **A42249** — *Towards Capable and Secure Autonomous Computer-Use Agents* (Student Abstract): the cleanest
  "capability ≠ permission" grounding — broad standing access converts errors into incidents (100% unauthorized
  install in certain planning tasks, author-reported); proposes least-privilege + command validation (unbuilt).
  *Evidence: Preliminary (small-n, version-bound, partly subjective) but directionally credible.*
- **A40925** — *Consensus Learning with Multi-Party Perturbation Triggers for Secure Model Access*: multi-party/
  threshold authorization bound to model execution; residual ~15% Acc-Fusion; non-adaptive. *Evidence: Moderate.*
- **A39721** — *SecMoE: Communication-Efficient Secure MoE Inference via Select-Then-Compute*: routing/access-
  pattern is a confidentiality asset — oblivious select-then-compute hides expert selection; semi-honest only.
  *Evidence: Moderate (semi-honest scope).*
- **A40100** — *FedSEA-LLaMA: Secure, Efficient and Adaptive Federated Splitting for LLMs*: activations are a
  confidentiality asset — collusion inversion; forward-activation perturbation; empirical privacy, no ε.
  *Evidence: Moderate (empirical-privacy only).*
- **A42239** — *Obedience or Vigilance? … Malicious Multiple-Choice Options*: any model-visible field is an
  injection surface (adoption ≈0.5, accuracy ≈0.27 for the contradiction style; single model, non-adaptive) — the
  reason the credential-release path must not be model-mediated. *Evidence: Preliminary.*
- **A36959** — *AutoMalDesc*: multi-signal verify-before-trust (cross-temperature + separate-model + confidence)
  — transposable to multi-signal attestation validation; LLM-judge-disagreement caveat. *Evidence: Moderate.*

Reviewer-synthesis / industry-brief cross-references (skill artifacts, **not** AAAI corpus papers):
`agent-identity.md` (1Password "Identity for Reasoning Agents" brief + Jul-2026 sweep) — Zero Standing Privilege,
JEP+JIT, bearer-vs-federated, attestation, secretless/WIF-OIDC, SPIFFE/SVID, delegated-but-attributed, separate
trust domains, intent-based access + revoke-on-divergence, never-seen credential handle, Credential Broker /
Apono split, attenuated N-hop delegation, DPoP/token-exchange/CIBA step-up; `architecture-patterns.md` P1
(pre-action kill-switch), P5 (trajectory-level trace / attribution), P6 (credential broker, MASTRIKE
compromise-budget `k`), P7 (Shapley risk-placed checks), P10 (async explainability); `glossary.md` (identity
vocabulary).

## Evidence strength

- **The architectural thesis is well-supported by convergence, not replication.** "Capability ≠ permission" and
  "minimize standing authority so a hijack is contained" are convergent across `A42249` (corpus) and the
  identity brief — but these are **independent sources in different domains, not independent replications of one
  measured effect**. Treat the convergence as a strong *design* signal, not an effect size.
- **The ZSP / JIT / JEP / attestation / federated mechanics are reviewer-synthesis engineering practice + market
  facts** from `agent-identity.md`, **not corpus-measured defense efficacy.** They are grounded in real breach
  patterns and shipped products (WIF/OIDC, SPIFFE, 1Password Credential Broker, Apono, Okta XAA, Entra Agent ID)
  but their *security effect for agents* "requires production validation."
- **The corpus efficacy numbers are author-reported, non-adaptive, and best-case.** `A40925` (~15% residual),
  `A39721` (semi-honest only), `A40100` (empirical, no ε), `A42249` (small-n), `A42239` (single model) — none
  faces an adaptive, defense-aware attacker (Network-Cyber §3, §9, §12).
- **Deterministic, fail-closed, least-privilege design choices are reviewer-synthesis best practice** grounded in
  the papers' and the brief's failure modes, not themselves a paper-measured result.

## When NOT to use this pattern

- **When the capability/credential can simply be removed.** Prefer elimination to scoping: if a role never needs
  a credential, don't issue it and then scope it. This pattern is for authority that must exist but must be
  conditionally, briefly held *(agent-identity brief; mirrors `A42249` least-privilege)*.
- **For the action-permission decision itself.** Deciding *allow/deny/step-up on a proposed action* is
  `policy-permission-gates` / `tool-capability-isolation` — this pattern governs the *credential/means*
  (broker = govern the credential; gate = govern the action). Use both; don't substitute one for the other.
- **As the sole control.** Least-privilege credentials bound blast radius but do not stop an in-scope credentialed
  action from being misused; pair with the action-side gate, human approval for high-stakes/irreversible
  operations, monitoring, and adaptive red-team (Network-Cyber §14; `A42249`).
- **For content-safety / toxicity / disclosure filtering.** That is a content-guardrail layer, a different
  pattern; credentials govern *authority*, not text.
- **When no trusted issuer or verifiable attestation exists.** You cannot do the federated/secretless model
  without one *(agent-identity brief)*; either establish an issuer/attestation or fall back to a **short-lived,
  tightly-scoped, quickly-rotated bearer** credential and treat the missing attestation as a named residual risk
  — never a long-lived standing bearer secret.
