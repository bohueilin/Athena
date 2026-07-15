# Interviewing for Agent Security (2026)

How to talk about agent security in an interview — the frameworks interviewers expect, the debates you must hold a
calibrated position on, the numbers to have ready, and how to use **Origin + Passport** as portfolio proof. Sourced
from a Jul 2026 sweep of live postings (Anthropic, OpenAI, GDM, Lakera, Okta, 1Password) + prep guides. Pairs with
`landscape-2026.md` (facts) and `worldview.md`/`agent-identity.md` (the thesis you're demonstrating).

## What "strong candidate" sounds like in 2026 loops

Synthesis across postings + prep guides — five moves that read as senior:
1. **Name the frameworks unprompted, but lead with blast radius.** Don't recite OWASP; open with *"what can this
   agent touch, and what happens when it's manipulated into using that access?"* Frameworks are the shared
   vocabulary; blast-radius thinking is the judgment.
2. **Layered defense where the deterministic layer is the guarantee.** Tool-call allow-lists, capability checks,
   egress control, breaking a lethal-trifecta leg = the floor. Model-level guardrails/classifiers = best-effort
   telemetry, **never the sole gate**. (Backed by 2510.09023 vs 2606.26479, below.)
3. **Red-team methodology is adaptive & iterative.** GDM's agentic-red-team role explicitly wants exploit dev +
   eval-framework/fuzzing fluency. Name **AgentDojo** as the benchmark; describe memory-driven, defense-aware attacks
   (the attacker adapts to the defense), not a static prompt list.
4. **Treat identity/permissions as the top real-world failure class** (OWASP **ASI03**). Advocate scoped, delegated,
   auditable, **revocable** agent credentials — Zero Standing Privilege, JIT, attestation (see `agent-identity.md`).
5. **Hold calibrated positions, not absolutes.** e.g. *"Prompt injection is unsolved and likely unsolvable at the
   model layer, which is why my design assumes compromise and contains blast radius."*

## The framework canon (know cold, cite by code)

- **OWASP LLM Top 10** (LLM01 Prompt Injection … LLM06 Sensitive Info Disclosure, LLM08 Excessive Agency).
- **OWASP Agentic Top 10 2026** — ASI01 Goal Hijack, **ASI03 Identity & Privilege Abuse**, ASI04 Supply Chain,
  ASI06 Memory Poisoning, ASI09 Human-Agent Trust Exploitation, ASI10 Rogue Agents (full list in `landscape-2026.md`).
- **OWASP MCP Top 10** + **Agentic Skills Top 10** — for tool/plugin supply-chain questions.
- **MITRE ATLAS** — adversarial ML tactics/techniques; **MITRE ATT&CK C0062 (GTG-1002)** as the real agent-attacker case.
- **NIST AI RMF** (Govern/Map/Measure/Manage) + **CAISI** agent-security initiative + **CSF AI Profile**
  (Secure/Detect/Thwart).
- **The lethal trifecta** (Willison): *private data + untrusted content + external comms*; **Rule of Two** (≤2 legs).
- **STRIDE-for-agents** — classic threat modeling adapted; expect a live threat-model exercise.

## The four debates — your position (with citations)

**1. "Can prompt injection be solved?"** → *No, not by detection at the model layer.* **The Attacker Moves Second**
(arXiv **2510.09023**): 12 defenses reporting ~0% vuln were bypassed >90% by adaptive attackers; human red-team 100%.
As long as trusted instructions and untrusted data share one channel, detection loses. **Treat injection as an
architectural condition to design around, not a bug to patch.** Never claim a classifier "solves" it.

**2. Guardrail model vs deterministic policy?** → *Deterministic out-of-band enforcement as the floor; classifiers
as signal.* **CaMeL** (arXiv **2503.18813**) — extract control/data flow from the trusted query, capability policy
at each tool call, provable security, 77% AgentDojo utility. **Progent/RTBAS/FIDES/FORGE** (adaptive eval arXiv
**2606.26479**): ASR 25.8%→4.2%, defense-aware attack only 2.6% — the *opposite* of detection defenses. Best answer:
**defense in depth** — deterministic policy mediates actions (guarantee), classifiers add telemetry (best-effort).

**3. Human-in-the-loop approval?** → *A layer whose failure mode (fatigue) must itself be threat-modeled.* Anthropic
disclosed users approve **~93%** of prompts; approval fatigue is now framed as a "clickthrough vulnerability." A PI
that triggers a rubber-stamped approval has bypassed the human control. Design: **risk-tiered escalation** (approve
only irreversible/high-blast-radius actions), batching, and **informative** approvals (show the diff/action, not
"Allow?"). The standard-in-progress is AuthZEN **AARP** (Access Request & Approval Profile).

**4. Agent identity vs user identity?** → *Every agent action is delegated user access; never shared service
accounts or token impersonation.* Distinguish the **user identity** (the human the action runs for, carried as a
delegated subject) from the **agent identity** (the instance calling downstream). Two anti-patterns interviewers
probe: (a) API keys/service accounts that strip user identity ("the agent did it"); (b) impersonation where the
agent reuses the user's token and vanishes from audit. Vocabulary: **OAuth 2.1 + OBO/token exchange (RFC 8693)** for
delegation chains, **DPoP (RFC 9449)** against token theft, **PKCE**, **CAEP** for real-time revocation, **SPIFFE/
WIMSE** for workload identity; emerging **ID-JAG / Okta Cross App Access**, IETF `draft-*-agent` delegation drafts,
**AIP** (Agent Identity Protocol, arXiv 2603.24775). Product-side: **Zero Standing Privilege + JIT** (1Password
Credential Broker + Apono; Okta agent registry + kill switch). See `agent-identity.md` for the full mechanics.

## Numbers to have ready (credibility currency)

- AgentDojo: **73.2%** undefended ASR → **~8.7%** layered; PromptArmor claims **~0%** (arXiv 2507.15219).
- Adaptive attacks bypass **12/12** detection defenses >90% (2510.09023); out-of-band **Progent 4.2% → 2.6%** under
  adaptive attack (2606.26479).
- CAISI red-team: **81% task-hijacking** vs 11% baseline. Anthropic: users approve **~93%** of prompts; cred-exfil
  test **24/25** against model-layer defenses. GTG-1002: model ran **80–90%** of a real espionage op.
- Machine identities outnumber human **~45:1→80:1**; avg machine secret lives **>600 days**; **1 in 20** holds
  full-admin; **~1/3** of private repos contain a plaintext secret (`agent-identity.md`).
- Market: guardian agents **10–15%** of agentic-AI by 2030 (Gartner); ~**65%** of orgs hit an agent incident in 2026.

## The one-liners (memorize)

- **"Capability is not permission."** (Origin/Passport thesis; formalized as *intent-to-execution integrity*, Dawn
  Song group arXiv 2605.16976.)
- **"The risk moved from what a model *says* to what an agent *does*."**
- **"Assume the agent is already compromised; bound what a hijack can reach."** (PI-containment via least privilege.)
- **"Alignment is shallow — refusals collapse at depth, on expert knowledge, under semantic rewrites, and after
  fine-tuning — so the guardrail must be external."** (`worldview.md` §6.)
- **"The weakest layer is the one you built yourself."** (Anthropic containment — argues for deterministic OS/VM
  primitives over custom model defenses.)
- **"Who answers when the agent acts?"** — identity + attribution as the accountability question.

## Using Origin + Passport as portfolio proof

You don't just *know* the theory — you *built* the reference architecture. Map each claim to a shipped piece:
- **"I built a credential broker"** → agent gets a *brokered handle, never the secret*; server-side resolution
  (1Password SDK / MockSecretBroker); grant TTL + scope + fail-closed `ToolRouter`. (ASI03, least privilege.)
- **"I implemented the Rule of Two / lethal trifecta"** → a live gate that blocks the private-data + untrusted +
  external-comms combination. (Meta's Rule of Two, in code.)
- **"I built the autonomy trace"** → SHA-256 hash-chained, per-action audit binding runtime identity + delegating
  human — *the tamper-evident agent audit log the field has no standard for yet* (`landscape-2026.md` §7).
- **"I added human step-up with a passkey"** → WebAuthn/Touch-ID gate before granting *new* agent authority
  (per-action step-up = AuthZEN AARP direction; the CIBA/walk-up problem, solved for the local case).
- **"I use a deterministic judge, not an LLM grading an LLM"** → effect-based verification (Origin's FactoryDad
  readiness oracle), the anti-pattern-avoidance interviewers reward.
- **Honest gaps you're building toward** (shows depth): attenuated **sub-delegation** chains (N-hop attribution),
  **intent-conformance monitoring** (revoke on drift), true **attestation** (WIF/OIDC) vs a declared identity,
  **server-verified** passkey step-up (challenge + signature, not client-only). These are the field's open problems
  too — naming them signals you're at the frontier, not behind it.

## Likely question shapes (rehearse answers)

- *"Design a guardrail for an agent that can spend money / touch prod / read the file system."* → discovery →
  least-privilege broker → pre-action gate on **effect** → deterministic policy + HITL only for irreversible →
  trajectory-level audit → continuous red-team. (This is the `architecture-patterns.md` loop — walk it.)
- *"An agent reads a web page and then emails someone — what could go wrong?"* → indirect prompt injection + lethal
  trifecta; break a leg; treat page content as untrusted data, not instructions.
- *"How do you red-team an agent?"* → adaptive, memory-driven, defense-aware; AgentDojo; effect-based verifiable
  judge; regulation-grounded scenarios; report ASR under *adaptive* not static attack.
- *"How should an agent authenticate to a downstream API?"* → delegated user identity via token exchange, short-lived
  DPoP-bound scoped token, never a shared service account; revocable; audited. (The anti-patterns above.)
- *"Why won't OpenAI/Anthropic just build this in?"* → they build **isolation** on **their** platform; the open,
  defensible layer is **cross-platform policy + delegation identity + portable audit** (`landscape-2026.md` §3).
