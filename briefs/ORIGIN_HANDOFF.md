# Origin — what it is, and the mission (handoff for a new conversation)

> A self-contained orientation for anyone (human or agent) picking up Origin cold. For live status,
> read `Origin_Status.md` (the single source of truth) next. Keep this private repo private.

## The one line
**Origin is the reference check for AI agents before they get production permission** — and, on the same
architecture, the verified-environment / evidence layer for any autonomous actor.

> **Model proposes. Environment verifies. Gate decides. Trace proves. — Capability is not permission.**

## The problem
Enterprises cannot safely grant an AI agent production access on the strength of a model's *capability*, a
vendor's claim, or a one-time security review. They need an actionable, independent answer to: *what was
tested, under which policy, against which tools; where is the agent over-granted; has anything changed
since; and can a third party verify the result?* Today that's spreadsheets, ad-hoc logs, and "trust us."

## What Origin does (the wedge)
A buyer describes their agent + its least-privilege policy and runs it through a **deterministic gym**.
Origin returns a **Verified Readiness Level** (L0–L4), a per-decision breakdown of exactly where the
policy **over-grants**, and a signed, config-bound **Origin Attestation** they can re-verify offline —
one that **automatically voids** when the agent's model, tools, context, harness, or environment change.
The self-serve flow is `/reference-check`; anyone can re-verify an attestation at `/verify`.

## Why it's defensible (the moat)
The bet: a **deterministic verifier** that gates a proposed plan and emits **tamper-evident, signed,
reproducible evidence** is the *same product* whether the actor is a software agent, a factory/robot
brain, or a CV model reconstructing a room — **one evidence spine, many domain verifiers.** The
environment (verifier) is the moat, not the model. The deterministic oracle is the only label authority —
**never an LLM grading an LLM.** Two compounding assets: (1) a **self-hardening gym** — every over-grant a
customer surfaces becomes an oracle-labeled, versioned case, so the battery gets harder to game over time;
(2) a **verified-trace data factory** — the gym produces oracle-labeled behavior traces that train tiny
policies which beat hand-written ones. Neither is cloneable without the same oracle discipline *and* the
accumulated corpus.

## What exists today (all gated + pushed; honest state)
- **Public trust layer** (`github.com/bohueilin/Origin`, the live site): the buyer `/reference-check`,
  `/verify` (offline re-check), `/security` (run the verifiers live), `/trust`, `/proof`, `/brief`, and a
  `/labs` hub. The evidence SDK (`packages/verifier-core` + `packages/evidence`): canonical JSON,
  isomorphic SHA-256, hash-chained ScoreReceipts, ES256 attestations (Sigil), Merkle batches, the Crucible
  config-bound credential, the IAM + support gyms.
- **Janus** (`apps/janus`): the agent credential broker + autonomy trace console (identity → authority →
  verified action → trace → containment); a fail-closed money path.
- **Verifier hardening** (`services/{chronos,cobra}`): red-team → patch → measure against reward-hacking.
- **Labs / physical actor:** `/simulation` (multi-robot warehouse, 2D + 3D, oracle-gated, signed) and
  `/operations` (a verified fleet-ops SLA console).
- **The private moat** (`github.com/bohueilin/origin-factory`, private): the Factory Algorithm — a
  fail-closed factory verifier + repair loop + a distilled TRM student (robust multi-seed win), the
  evidence-adapter unification, the site-to-gym floor pipeline, a spatial **reconstruction verifier**, and
  the YC materials.
- **The knowledge base** (`github.com/bohueilin/Athena`, private): `guardian-agent-foundations` (432-paper
  AAAI-26 agent-security corpus + 28 control playbooks) + these briefs. It grounds design + security
  reviews in cited evidence.

## The honesty discipline (this is the brand, not a caveat)
Results are **"reproducible under this verifier,"** never "safe" or "certified." Synthetic is labeled
synthetic; projected is labeled projected. "Tamper-evident" means alteration is *detectable*, not
impossible. Origin *contains* prompt injection; it does not claim to *prevent* it. A machine `honesty-lint`
gate enforces this on every served page. **Every number must be reproducible by an artifact in the repo.**

## The go-to-market ladder
Wedge: **self-serve agent reference check.** Then: an **embedded verification API** GRC platforms (Vanta/
Credo) ship inside their stack; a **deterministic underwriting signal** an agent-liability insurer prices
on; and — the vision — **physical / robot readiness** on the same spine. Certification-as-a-market:
config-bound reference checks re-run on every change (recurring), priced on scope/volume/monitoring —
**never on the level earned** (the level is a deterministic result, not something you can buy).

## The mission (the future)
Every enterprise is about to deploy agents — and soon humanoids — that touch money, data, production, and
physical safety. The blocker isn't capability; it's **trust, governance, and liability**, and there is no
standard for "this actor earned the right to do X, here's the signed, independently-verifiable receipt."
**Origin intends to be that standard** — the verification + evidence layer beneath every autonomous
system, so that *capability is never mistaken for permission.*

## Naming (mythology + product)
**Janus** (Roman god of gates/transitions) — the gate/credential broker. **Chronos** (Greek Titan of time)
— the reward-hack-discovery service. **Athena** (Greek goddess of wisdom/strategy) — the private knowledge
base. **Atlas** — incidental. Product names (non-mythic): **Origin**, **Crucible** (the test environment),
**Origin Attestation** (the signed receipt; internal crypto primitive: Sigil), **Verified Readiness Level**
(the L0–L4 ladder; internal field: `rsl_level`), **Cobra**, **Foundry**.

## Read next, in order
1. `Origin_Status.md` (SSOT — current state, roadmap, constraints). 2. `Origin/README.md` +
`PROJECT_OVERVIEW.md` + `REPO_STRUCTURE.md`. 3. `origin-factory/docs/yc/{YC_ANSWERS,BUILD_STATUS}.md`
(the private moat + YC story). 4. `~/hackathons/SECURITY_AUDIT_CPVER_2026-07-14.md` (the security posture).
5. Non-negotiables: deterministic-oracle-only, honesty rails, never commit `.env*`, never deploy without
authorization, keep the Factory Algorithm out of the public repo.
