# Agent Identity & Credential Brokering

**Source:** 1Password research brief *"Identity for Reasoning Agents"* (AGI House **Agent Identity Build Day**,
2026-06-27, Hillsborough; speakers Dawn Song, Keith Enright (CSO Harvey AI, ex-Google CPO), HD Moore (Metasploit)).
This is the **identity/credential half** of the Guardian-Agent thesis — it complements the Virtue AI corpus
(which is mostly about *behavioral* guardrails) with the *access-control* model. It is also the direct
theoretical foundation for the **Passport** product ([[passport-demo-app]], [[origin-pitch-framing]]).

## The one-sentence thesis

> The hard problem of agent engineering is **no longer capability**. In production the dominant risk is that a
> *capable agent holding standing, over-scoped credentials does something wrong, and the blast radius is whatever
> those credentials could reach.*

The question every agent build must answer (memorize — it's the on-stage question, and it's Passport's pitch):

> **When your agent acts, is it acting as itself, or as you? Where does its authority come from, and who answers
> for what it does?**

This is the access-control restatement of Virtue AI's "the risk moved from *what a model says* to *what an agent
does*" (`worldview.md`) and Passport's "**capability is not permission**."

## 1. Why agents make machine identity harder

- **Machine identity** = a credential authenticating a *non-human* actor (service, workload, script, container,
  agent) via **keys / tokens / certificates**, not password + MFA. Machines can't do an SMS prompt or fingerprint,
  so trust rests on **cryptographic material + where/how the workload runs**.
- **Scale stats worth quoting:** machine identities outnumber human ones **~45:1 to >80:1**; the average machine
  secret stays active **>600 days**; **~1 in 20** machine identities holds **full-admin**; **~1/3 of private
  repos** contain a plaintext secret. Agents add a *new leak surface* — secrets scattered into **prompts, configs,
  and MCP server definitions**.
- **How a credential becomes a breach** (the pattern behind most breaches): attacker gains a foothold → **scans
  for an embedded long-lived secret** (source, images, logs, config) → authenticates as the over-privileged
  machine identity → **moves laterally and escalates.** It works because it *looks like legitimate automation*, so
  human-centric controls never fire. Root enabler in nearly every case: **a standing, over-scoped credential that
  existed before it was needed and persisted after.**
- **Why reasoning changes the problem:** a conventional workload is *set-and-forget* (fixed function → static
  policy fits). A **reasoning agent's access needs evolve** as it interprets state and chooses its next action — so
  a policy correct at process start is wrong a few steps later. *"The minimum"* (Zero Trust) becomes a **moving
  target over the life of a single process.** Agent access looks like a *human's* evolving, context-dependent
  needs, but must be granted **to a machine, at machine speed, with no human in the loop.** Canonical example: a
  coding agent goes read-repo → run tests → deploy → read prod DB to debug — *an escalation chain no static grant
  anticipated.*
- **Prompt injection ⇒ treat every agent as potentially turned.** So the authority bound to an agent **at any
  moment should be the least justified right then**, so a hijack is *contained, not catastrophic.* (This is the
  access-control twin of Virtue AI's "alignment is shallow" — don't trust the agent; bound it externally.)
- **Why attribution is hard:** agent harm emerges from a **chain of individually-innocuous steps** (a conversation
  that walks the agent into retrieving sensitive data or invoking an out-of-scope tool). Reconstructing it needs
  **structured logging that ties every action to a runtime identity**: *who/what acted, under which authorization,
  on what data, when, from what inputs.* 1Password's framing: **"the gap is not governance intent but execution
  control."** (Same unit of analysis as Virtue AI's trajectory-level monitoring — see `architecture-patterns.md`
  P5.)

## 2. The three principles for agent access (the heart)

Each maps to one part of the on-stage question.

### Principle 1 — Minimize standing access  *(answers "what can it reach")*
Least privilege has **two axes**, and agents need both:
- **Just-enough-privilege (JEP)** — scope a grant to a *specific action or resource* (write **one** bucket, not
  `s3:*`), so a compromised identity can't reach beyond its job.
- **Just-in-time (JIT)** — grant access *only on request* and *expire it* after a short fixed window, so there's
  **nothing standing to steal between tasks.**
- Together = **Zero Standing Privilege (ZSP):** by default an identity has **no** access; it receives
  narrowly-scoped, short-lived authority **only when a task justifies it.** Provisioning is ideally gated on
  **attestation** (the workload *proves it is what it claims* before anything releases).
- The failure it prevents: **broad + standing = large blast radius** the moment any credential leaks.
- Discipline runs against the default habit (over-scope "to avoid permission errors," never revoke). Mantra:
  **"a credential that persists is already compromised."**

### Principle 2 — Authority is proven at runtime, not stored  *(answers "where authority comes from")*
- An identity is a set of **attributes bound to a trusted issuer**; a relying party trusts it by **verifying a
  signature against the issuer's public key** — exactly like a browser validating a TLS cert. **No trusted
  identity without a trusted issuer.**
- **Bearer model** (the dangerous one): the agent *holds a secret*; **possession is sufficient** — anything that
  copies the secret inherits the authority. This is why long-lived keys are so dangerous.
- **Federated model** (the goal): the agent **proves what it is**, a **policy validates that proof**, and a
  **short-lived credential is issued for the specific task.** **Attestation** (signals like *where a process runs*
  and *who initiated it*) lets an issuer bind a workload to an identity **automatically and in real time**; each
  *fresh attestation re-derives access* rather than relying on a standing grant.
- End state = **secretless access**: the **verified identity *is* the credential.** Deployed version =
  **Workload Identity Federation (WIF) over OIDC** (GitHub Actions, AWS, GCP, Azure).
- **Two disciplines, kept separate:** governing the **entity** (the *who*) = **machine identity management**;
  securing the **credential** (the *means*) = **secrets management**. A runtime answer needs both.

### Principle 3 — An agent acts on delegated authority and must stay accountable  *(answers "who answers for it")*
- An agent is a **delegate, not a principal.** It carries its **own identity** (so every action attributes to
  *it*) while acting under **authority a human delegated** (so accountability traces back to that **person**).
- Because needs evolve mid-task, a single login-time grant won't do: **authority is re-evaluated continuously, as
  close to each action as possible, constrained each time to what's justified at that moment** — Zero Trust applied
  **in real time, not at the front door.** This is also the prompt-injection containment story.
- **Separate trust domains that look similar but aren't:** *generating code* and *acting on production* are
  different blast radii and **must not share a credential scope** — even for the same agent.
- **Accountability needs an audit trail where identity is inseparable from action**, so a chain of steps can be
  reconstructed after the fact.
- **Direction of travel: intent-based access** — **bind a grant to the declared *purpose* of a task, and revoke
  it when the agent's behavior diverges from that purpose.** Monitoring behavior against stated intent is
  *unsettled* — explicitly flagged as a good thing to push on. (This is where agent identity meets Virtue AI's
  behavioral monitoring — the **intent-conformance monitor** is the bridge.)

## 3. The 1Password stack (concrete primitives, "use today" → "frontier beta")

- **Environments + runtime injection** (GA): define secrets in 1Password not `.env`; pull at runtime via the CLI
  (`op run --environment`), SDKs (Go/Python/JS), or a **Service Account** (headless/CI). Locally the env mounts as
  a **virtual file via a UNIX pipe — never written to disk, untrackable by Git** → the "committed .env" failure
  mode disappears. *Default for any project needing an API key.*
- **Desktop authentication for the SDKs** (GA): a tool authenticates through the desktop app's **biometric/password
  prompt** under a **time-bound session** (expires on inactivity/lock). The **human-in-the-loop counterpart to
  service accounts** — use whenever a person should approve a sensitive action.
- **Codex MCP server pattern** (now): **the agent acts on secrets without seeing them.** The official Environments
  MCP server **treats the MCP transport as untrusted** — the agent can create environments and manage *variable
  names* but **never receives raw values**; 1Password mounts them for the authorized process and **requires user
  approval at access time.** (The naive community MCP pattern returns values through the model's context — fine for
  throwaway dev creds, *wrong for anything real.*)
- **Credential Broker** (private beta): a workload presents a **signed OIDC token** → 1Password **validates it
  against a trust policy** → **only the one approved credential is released**, short-lived, with **full attribution**
  (repo/branch/workflow/commit). A compromised pipeline exposes **one credential, not the vault.** *Agent support
  is on the roadmap* — "exactly the gap your prototypes can probe."
- **Apono** (just acquired): where the Credential Broker governs **the credential**, Apono governs **what the
  verified identity can then *do*** in the target system, and **for how long** — JIT, time-bound access into AWS /
  Azure / GCP / K8s / Snowflake / Databricks / 200+ tools, **zero standing privilege + intent-based scoping for
  agents.** Useful split: **broker = govern the credential; Apono = govern the action.**

## 4. Project archetypes (what a credible agent-identity build looks like)

- **Agents with a wallet:** budget-bound procurement agent (payment credential **brokered at runtime**, every txn
  checked vs budget+allowlist before executing); **per-transaction card issuance** (credential scoped to **one**
  transaction, expires after — JIT issuance vs a reusable card).
- **Agents that run the stack:** CI agent on **workload identity** (OIDC, one short-lived credential not a stored
  cloud key); **JIT incident responder** (time-bound scoped access on alert, auto-revokes); **escalation-aware
  deploy agent** (access **re-derived** QA→staging→prod, each step a *fresh policy check* — the reasoning/escalation
  problem head-on).
- **Personal chief of staff:** human-approved inbox/calendar operator routing each sensitive action through the
  **native desktop approval prompt**; access is the signed-in user's, time-bound, revocable.
- **Orgs of agents (delegation chains):** **attenuated sub-delegation** (agent A grants agent B a *strictly
  narrower* subset; an action N hops deep still attributes to the original human) — flagged as **the least-solved
  problem on the list** and most relevant to multi-agent systems; **brokered agent marketplace** (task-scoped,
  expiring credentials with attribution).
- **Platform/infra:** **agent-identity control plane** (issue/scope/monitor/revoke across providers);
  **intent-conformance monitor** (takes the declared task, watches tool calls, **halts on divergence**);
  **attribution-complete audit layer** (bind every tool call to a runtime identity + the delegating human);
  **secret-sprawl scanner** (find plaintext secrets in repos/MCP configs, replace with references).

## 5. How this connects to the rest of the skill

- **Same risk thesis as Virtue AI** (`worldview.md`): capability ≠ the problem; *what the agent does with its
  authority* is. This brief supplies the **identity/credential mechanics** the Virtue corpus assumes.
- **Credential broker pattern** (`architecture-patterns.md` P6) gets its theory here: ZSP, JEP+JIT, attestation,
  federated/secretless, delegated-but-attributed, separate trust domains.
- **Prompt-injection containment** (`threat-models.md`): "minimal current-task grant bounds a hijack" is the
  access-control mitigation that pairs with the behavioral defenses.
- **Trajectory-level monitoring** (P5) ≡ the brief's **attribution** requirement and **intent-conformance**
  direction — both say *bind every action to a runtime identity and reason over the chain.*
- **Compromise budget** (MASTRIKE, `papers.md`) ≡ the brief's **blast radius** — cap what a single compromise can
  reach.

See `glossary.md` for the new vocabulary, and the **Passport applicability matrix** below.

## 6. Passport applicability matrix (already-have vs gaps)

Passport ([[passport-demo-app]]) already implements much of this brief; the brief names the frontier it should
push into. (Grounded in the Passport engine: capability catalog, fail-closed `ToolRouter`, grant TTL/scope,
approval packets, SHA-256 audit chain, revoke; plus the production credential-broker functions in the Origin repo:
`agent-token-mint`, `credential-broker` 10-step pipeline, Rule-of-Two/lethal-trifecta, SIWE, expiry-sweeper.)

| Brief principle | Passport today | Gap / frontier to build |
|---|---|---|
| **JEP** (scope to action/resource) | ✅ scoped `allowed_capabilities`, `denied_capabilities`, GLOBAL_FORBIDDEN, fail-closed router | per-resource (not just per-capability) scoping; explicit blast-radius tiers |
| **JIT / ZSP** (no standing, expire) | ✅ grant TTL + expiry-sweeper + default-deny | re-derive access **per action/step**, not one upfront task grant |
| **Attestation / federated / secretless** | ⚠️ opaque grant-bound agent token (no raw secret) + SIWE wallet proof-of-control | true **attestation** of *what the agent is* (Workload Identity Federation / OIDC) before grant |
| **Delegated + attributed** | ✅ agent has own `agent_id`, acts under user-delegated grant, audit ties identity→action | **attenuated sub-delegation** chains (A→B narrower, N-hop attribution to original human) |
| **Continuous re-evaluation** | ⚠️ per-commit approval gates; reads granted upfront | re-check authority **close to each action**, escalation-aware |
| **Separate trust domains** | ⚠️ one grant per task | model code-gen vs prod-action as **distinct credential scopes** |
| **Intent-based access** | ✅ `IntentParser` scopes grant to normalized intent | **intent-conformance monitor**: watch tool calls vs declared purpose, **revoke on divergence** |
| **Attribution-complete audit** | ✅ SHA-256 hash-chain, redaction, every call audited | export as the **autonomy-trace** with runtime-identity + delegating-human on every event |
| **Brokered, never-seen secrets** | ✅ MockSecretBroker + OnePasswordSecretBroker (handle-only, server-side resolve) | wire the real **1Password Credential Broker** (OIDC trust policy) when agent support ships |

**Strategic read:** Passport already *unifies* what 1Password splits across **Credential Broker (govern the
credential)** and **Apono (govern the action)** — the broker handle + the `ToolRouter` policy chokepoint. That
unification, plus the **intent-conformance monitor** and **attenuated delegation chains** (the brief's
least-solved problem), are Passport's strongest differentiators to build next.

## 7. 2026 UPDATE — the identity market caught up (Jul 2026 sweep)

The brief's "frontier / roadmap" items **shipped** in 2026. What Passport must now track — and where the gaps it can
own still are:

**1Password** rebuilt itself as an **agent-credentialing platform**:
- **Unified Access** GA (**Mar 17 2026**) — discover/secure/audit human+machine+agent identities; partners span
  Anthropic, OpenAI, Cursor, GitHub, Vercel, Perplexity. (Primarily discovery+vaulting; per-action authz lives
  elsewhere.)
- **Credential Broker** private beta (**Jun 15 2026**) — verifies trusted identity signals, delivers approved
  creds/tokens on demand (not copied across environments), logs every request/delivery. First flow: GitHub Actions
  workload identity; agents on the roadmap. **The exact product Passport's broker prototypes.** *Gap it leaves:* the
  **human step-up (approval) leg** and cross-service delegation are still roadmap, and **the agent still holds a
  usable credential once released** (Passport's never-seen handle is tighter).
- **Apono acquired** (**Jun 15 2026**) — JIT, intent-based access into AWS/Azure/GCP/K8s/Snowflake/Databricks/200+,
  **auto-revoke on task completion / behavior drift**. Confirms the **broker=credential + Apono=action** split
  Passport already unifies.
- **AI Agent Identity Kit** (May 2026) — short-lived scoped creds in one SDK call; **`spiffe://` workload URIs**,
  **RFC 8693 token exchange** (swap user token → narrower agent token), **RFC 9449 DPoP** (sender-constrain against
  theft); three models: **Human-Delegated / Machine-Bound / Fully-Autonomous**. *Still unshipped:* **Local Agent
  Identity Attestation** — i.e. the layer that makes agent identity *verified*, not *declared*, is the same gap in
  Passport's applicability matrix.

**The IdPs shipped GA agent-identity planes:**
- **Okta Cross App Access (XAA)** — OAuth extension (**ID-JAG**, Identity Assertion JWT Authorization Grant),
  **adopted as an official MCP authorization extension**; replaces static keys + invisible consent with IdP-mediated,
  policy-governed, auditable token issuance; 25+ partners (Anthropic, Cursor, Slack, Atlassian, Figma…); GA Aug 2026.
  **Auth0 for AI Agents** GA Oct 2025 (token vault, FGA, async authz). *Gap:* enterprise app-to-app within an IdP
  domain; **consumer walk-up + cross-IdP delegation chains out of scope.**
- **Microsoft Entra Agent ID** GA Apr 2026 — credential-less service principals from "agent blueprints," Conditional
  Access for agents, lifecycle governance. *Strongest inside the MS graph.*
- **WorkOS `auth.md`** (May 2026) — an open **agent-registration** protocol (a well-known Markdown file a service
  publishes so agents self-register for scoped creds); + "Agent Verified" (platform attests user identity at
  registration) + FGA for multi-agent delegation chains.
- **Aembit** "Blended Identity" GA Apr 2026 — evaluates **agent workload identity + human session together** in one
  request-time policy decision; short-lived task-scoped creds via secretless token exchange.
- **Teleport Agentic Identity Framework** (Jan 2026) — one **short-lived X.509** identity for human/machine/agent,
  **MCP-level enforcement down to individual tool invocations**, propagates originating-user identity to the tool
  ("the tool sees the agent, not you").

**Substrate + standards:**
- **SPIFFE/SPIRE** = de-facto agent workload-identity substrate (SVID on startup via attestation, hourly rotation);
  Google's new agent identity is SPIFFE-based. *Gap everyone names:* SPIFFE answers "**who is this workload**," not
  "**why is it acting**" — intent, per-task delegation, human step-up sit above it.
- **IETF cluster** (none WG-consensus yet): `draft-oauth-ai-agents-on-behalf-of-user` (agent authz-code grant +
  explicit user consent), `draft-mcguinness-oauth-actor-profile` (RFC 8693 `act` claim), `draft-liu-*` (**delegation_
  chain** claim for end-to-end auditability — RFC 8693 alone is only point-to-point), `draft-niyikiza-oauth-
  attenuating-agent-tokens` (**Biscuit/macaroon** attenuation), **AIP** `draft-prakash-aip`.
- **OpenID Foundation**: **AuthZEN** WG drafts for the agent era — **AARP** (Access Request & Approval Profile = a
  **standardized human step-up/approval flow**) and **COAZ** (MCP tool authorization). AIIM CG on agent identity.
- **MCP auth hardening** across three spec revs: 2025-06-18 (servers = OAuth Resource Servers, RFC 8707 resource
  indicators) → 2025-11 (S256-only PKCE, resource param required) → **2026-07-28** (six authz SEPs incl. **SEP-2350
  scope accumulation during step-up auth**, Client ID Metadata Documents over Dynamic Client Registration).
- **The walk-up / human-step-up problem** — the converging answer is **CIBA** (OIDC Client-Initiated Backchannel
  Auth: agent triggers an out-of-band push to the human's phone; poll/ping/push modes). Shipped as Auth0
  "Asynchronous Authorization," Okta guidance, Yubico+IBM+Auth0 phishing-resistant HITL. **Remaining gaps:** no
  risk-tiering standard for *which* actions need step-up (AuthZEN AARP is the draft), **no standard for attaching the
  approval artifact to the downstream token chain**, and revocation semantics.
- **Attenuated capability tokens** resurging: DeepMind **DCTs** (macaroon-based), **IBCTs** (invocation-bound; identity
  + attenuation + provenance in an append-only chain), startups **Tenuo** (Rust "warrants" — offline-verifiable) and
  **Keycard** (per-agent verifiable identity via runtime attestation + RFC 8693; independent / on-behalf-of /
  impersonation-under-policy patterns; every token traceable/revocable).

**Market structure:** **Astrix → Cisco** (NHI visibility folding into a platform; standalone sales ended Jun 30
2026). Aembit's line — **"visibility is not enforcement"** — names the gap the discovery-only tools leave.

### Where this leaves Passport (updated differentiators)
The commodity layers are now GA (issue a scoped short-lived token, SPIFFE workload ID, DPoP, token exchange). The
**open problems Passport should own** — each backed by the sweep as *explicitly unsolved*:
1. **Human step-up bound into the token chain** — CIBA/AARP deliver the *approval*, but **no standard attaches the
   approval artifact to the downstream delegation token**. Passport's approval packet + hash-chain can be that bind.
   (This is also the local-first **passkey/Touch-ID step-up** already built into the Origin console.)
2. **Attenuated N-hop sub-delegation with attribution to the original human** — everyone points at Biscuit/macaroons/
   IBCTs; nobody has shipped the auditable chain. The brief's "least-solved problem," still open in 2026.
3. **Intent-conformance monitoring / revoke-on-drift** — Apono claims it; "depth unproven." Passport's `IntentParser`
   + trajectory audit is the natural home.
4. **Tamper-evident, portable audit** — no signed agent audit-log standard exists (`landscape-2026.md` §7). Passport's
   SHA-256 chain + delegating-human attribution is a candidate reference format (OTel GenAI spans + signed chain +
   delegation-token refs).
