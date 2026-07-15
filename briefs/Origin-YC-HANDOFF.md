# ORIGIN — YC Launch Handoff (Master Brief)

> **What this is.** A complete, standalone handoff so a fresh session (Claude Fable 5) or Codex can
> pick up Origin cold and drive it to a Y-Combinator-ready startup launch in ~4 weeks. Everything
> below is grounded in the actual repo state as of the handoff, not aspiration.
>
> **Where this file lives + why.** `/Users/bohueilin/hackathons/Origin-YC-HANDOFF.md` — deliberately
> **outside** the public Origin repo. It contains YC strategy + references to the private "factory
> algorithm," which is exactly the category we purged from the public repo. **Do not commit this file
> into `github.com/bohueilin/Origin`.** Keep it private (or move it into the private algorithm repo).
>
> **Repo snapshot at handoff:** `github.com/bohueilin/Origin` · **PUBLIC** · branch `main` · HEAD `9098dae`.
> Tests green: **passport 167**, **rlkit 117**. Builds + lint clean.

---

## 0. TL;DR (memorize this)

**Origin is the trust/evidence layer for AI agents.** One invariant runs through everything:

> **Model proposes. Environment verifies. Gate decides. Trace proves. — Capability is not permission.**

An agent (or robot) can be *capable* of an action without being *permitted* to do it. Origin is the
control plane that (1) issues scoped, revocable authority, (2) measures the agent's real intent before
it acts, (3) contains the blast radius when something goes wrong, and (4) emits tamper-evident,
independently-verifiable proof of everything — issued by a **deterministic oracle**, never an LLM
grading an LLM. On top of that sits the business: **Certification-as-a-market** — a config-bound
"reference check for agents" that a buyer can trust because it was earned against our oracle, not a
self-authored rubric.

**The YC wedge in one line:** *Before you let an agent act on your systems, Origin gives you the
receipt that proves what it's allowed to do, what it actually tried to do, and that it was contained
if it went rogue — cryptographically, reproducibly, and independently verifiable.*

---

## 1. What is Origin (product + thesis)

Origin is a **secure execution + evidence platform for autonomous agents**. Two framings, one spine:

- **For AI agents (digital autonomy):** an agent proposes a plan; Origin issues a scoped, revocable
  grant; a gate authorizes each tool call *before* it runs (fail-closed); the agent's measured intent
  is checked against its declared plan; a taint/containment layer freezes only the poisoned sub-tree;
  and every action lands in a hash-chained, tamper-evident trace.
- **For Physical AI (robot readiness):** the same trust spine — floor/site → a deterministic
  readiness verdict (finish / escalate / refuse) → evidence. *(Note: the physical/robot ML — the
  "factory algorithm" — is private; see §5. The public repo keeps the trust spine + the digital-agent
  product, not the model.)*

**The thesis (put this on the design doc + deck):**
> *An RL environment is a secure execution product: sandbox · verifier · trace · reset · cost ·
> reproducibility.* The environment is the moat, not the model. Whoever owns the verified environment
> owns the trust — and trust is the bottleneck to agent adoption in the enterprise.

**Why now:** the next platform shift isn't smarter agents — it's **agents you can trust to act**.
Identity-bound, policy-governed, user-authorized, auditable, revocable. Enterprises will not grant
standing autonomy to agents without exactly this layer. Origin is that layer.

---

## 2. The naming system — "the Origin forge" (LOCKED)

One hard, short, evocative noun per function. Trademark-checkable, evocative-not-literal.

| Layer / function | Name | What it is |
|---|---|---|
| The environment / gym (creation, the world things are tested in) | **Origin** | existing — the platform |
| The trace / record (time, tamper-evident memory) | **Chronos** | existing |
| Red-team / reward-hack hunting (offense; hardens the verifier) | **Cobra** | existing (research tool, kept public) |
| Identity / authority / governance (the gate) — *formerly "Passport"* | **Janus** | the gate; scoped delegation + authorization chokepoint |
| Measured-intent watcher (declared vs measured vs action) | **Tell** | black-box conformance + white-box activation probe |
| Blast-radius containment / immune system | **Cordon** | taint-tracking + broker refusal + freeze-the-sub-tree |
| Certification / eval-as-credential (the market) | **Crucible** | config-bound "reference check for agents" |
| The signed portable receipt artifact | **Sigil** | ECDSA-signed, offline-verifiable evidence |

> ⚠️ **Naming caveat still open:** the app directory is still `apps/passport` and much UI copy still
> says "Passport." The rename to **Janus** is decided but **not fully executed** in code/copy. This is
> a deliberate next-step task (see §9) — a generic/overloaded name ("Passport") quietly caps a
> hackathon/startup; "Janus" (the two-faced god of gates, thresholds, and transitions) is the chosen
> replacement.

---

## 3. Architecture (layers + repos)

### 3.1 The three planes (one invariant)
```
① INTENT      — humans + agents express what they want (voice / text / a robot site)
                apps/origin-web (readiness)   ·   apps/passport→Janus (agent tasks)
                                │  intent (no authority yet)
② CONTROL     — the moat. propose a plan, then GATE it.
   PLANE        • planner (LLM proposes)         • capability engine: read ≠ commit
                • Janus: identity → scoped grant → authorization chokepoint (fail-closed)
                • Tell: declared vs MEASURED vs action     • Cordon: taint + containment
                                │  authorized action (or deny)
③ EVIDENCE    — tamper-evident. Chronos trace + rlkit ScoreReceipts + Sigil signatures
   PLANE        • deterministic oracle is the ONLY label/reward authority
                • Crucible: config-bound certification issued by the oracle
```

### 3.2 Repos (this is load-bearing — get it right)
- **`github.com/bohueilin/Origin`** — PUBLIC monorepo. The public showcase + the digital-agent
  product + the evidence layer. Branch `main`. **Pushing here does NOT deploy anything.**
- **Live website** deploys from a *different* repo: `physical-ai-demo-test` / branch `hud-factorydad-1`
  via **Cloudflare Pages** (watches GitHub). Origin is not wired to Pages. **Never deploy the public
  site without explicit authorization + a named target.**
- **The factory algorithm (private, see §5)** lives in: the pre-purge bundle backup
  (`origin-backup-<sha>.bundle`), `~/hackathons/Floor design` (site-to-gym half), and
  `~/hackathons/0620-test/physical-ai-demo-test/factoryceo_trm` (TRM half). **A dedicated PRIVATE repo
  is planned but not yet created.**

### 3.3 Apps (in the Origin monorepo)
- **`apps/origin-web`** — the live marketing/console React+Vite site. Multi-entry (index, app, capture,
  auth, passport, foundry, soc, clip, brief, proof, trust). Ships the **rlkit** evidence library
  (`apps/origin-web/rlkit/*.mjs`) + a deterministic warehouse gym + a symbolic BFS oracle. Build:
  `tsc -b && vite build`. **Reward oracle** (`server/env/*`, `foundryHandler.ts`) is kept public — it's
  the deterministic verifier, consistent with the public thesis.
- **`apps/passport`** (→ Janus) — the agent-identity / delegated-autonomy demo (`passport.html`, a
  self-contained client-side React app; no backend needed for the demo). Home of the security cores +
  the surfaced UI panels. Deterministic engine (injected clock), tamper-evident hash-chained
  `AuditLogger`, `SecretBroker` (opaque handles, never secrets), `ToolRouter` (the fail-closed
  authorization chokepoint).
- **`apps/chronos-ui`** — React/React-Flow UI for the Chronos run-graph.

---

## 4. What we've built (complete inventory — all committed + pushed + tested)

### 4a. The evidence layer — `apps/origin-web/rlkit/` (the RL-platform, the moat)
Nine RL-platform pillars, all vitest-gated (part of the 117 rlkit tests):
- `env-evidence.mjs` — the tamper-evident core: canonical JSON + SHA-256 hash chain + sealing digest,
  `ScoreReceipt` reproducibility. **⚠️ Uses Node's `node:crypto` (sync sha256) — Node-side by design.**
- `env-manifest.mjs`, `warehouse-manifest.mjs`, `warehouse-tools.mjs` — env-as-versioned-artifact.
- `origin-env-core.mjs`, `executor.mjs` — OpenEnv-style reset/step/state + executor.
- `tool-registry.mjs`, `mcp-adapter.mjs` — MCP tool registry + rate limit.
- `checkpoint.mjs` — checkpoint/resume (interrupted episode reproduces byte-identical final digest).
- `cost-ledger.mjs` — replay/dispute + cost-per-rollout ledger.
- `curriculum-evidence.mjs` — difficulty-band curriculum.
- `env-promotion.mjs` — environment promotion lifecycle.
- `build-trace.mjs`, `run-episode.mjs` — episode + build-trace helpers.

### 4b. The gate (Janus / `apps/passport`) — identity → authority → trace
- `engine/toolRouter.ts` — the chokepoint. Fail-closed. Now carries an **optional `RouterGuard`** that
  runs Tell + Cordon *before* authorization (additive — existing callers unaffected).
- `engine/auditLogger.ts` — append-only, hash-chained, `static verify()`.
- `engine/session.ts`, `grantManager.ts`, `approvalManager.ts`, `revocationManager.ts`,
  `policyEngine.ts`, `planner.ts`, `intentParser.ts`, `riskClassifier.ts`, `ids.ts` — the spine.
- `secrets/` — `mockSecretBroker.ts` (opaque handles, never returns the secret), `onePasswordSecretBroker.ts`
  (real 1Password SDK broker), `pickBroker.ts`, `redact.ts` (the `MOCK_SECRET_SENTINEL` tracer +
  `assertNoSecret` backstop).

### 4c. The three "beyond-us" cores (the biggest IP upgrades — all built + tested)
1. **Tell** (measured intent) — `engine/tell.ts` + `engine/activationProbe.ts`.
   - Three-way gate: **declared** (predicted plan) vs **measured** (a probe) vs **action**. Blocks a
     goal-hijack *before* the tool runs.
   - Black-box tier: deterministic conformance monitor. White-box tier: a real TaskTracker-style
     activation-delta linear probe (`activationProbe.ts`) that **abstains at confidence 0 when no
     model activations are supplied** — so white-box detection is never claimed on API-only models.
   - Clean-room from Agent Polygraph + SecureDelegate + the TaskTracker paper (see `docs/PRIOR_ART.md`).
2. **Cordon** (blast-radius containment) — `engine/cordon.ts`.
   - Taint-tracking per agent; the broker **refuses to resolve a secret for a tainted agent** (the
     secret is never fetched); `freezeSubtree()` freezes only the poisoned sub-tree + measures blast
     radius. Clean-room from CORDON + QuarantineAI.
3. **Crucible + IAM gym** (certification-as-a-market) — `rlkit/crucible.mjs` + `rlkit/iamGym.mjs`.
   - `crucible.mjs`: config-bound credential (voids if model/tools/context/harness or env change),
     before/after lift, emits a Sigil.
   - `iamGym.mjs`: a **deterministic, fail-closed, least-privilege** IAM/access-control gym (12
     allow/deny/escalate decisions, oracle-labeled; "catastrophic" = a security-critical over-grant
     that caps the RSL level). `issueIamReferenceCheck()` is the product API: run an agent's policy →
     RSL level → a config-bound "reference check for agents" credential + a plain-English summary.
   - Clean-room from Diploma.ai + Bad-agents.

**End-to-end integration:** `engine/cordonTell.ts` drives the REAL ToolRouter + AuditLogger +
Cordon-guarded broker through one continuous injection→containment loop, and the trace re-verifies.

### 4d. Product-surface steals (all engines built + tested)
- **Sigil** — `rlkit/sigil.mjs`. Shareable, browser-signed receipt. ECDSA P-256 / ES256 via Web Crypto;
  signs rlkit's content-address; public key travels inside; optional issuer-thumbprint pin. *(Engine
  done; browser page blocked — see §6.)*
- **Leak-vs-hold** — `secrets/leakVsHold.ts`. Same injection vs two agents: key-in-context leaks, vault
  (broker handle) holds. Runs the real broker + `assertNoSecret` sentinel.
- **Control Room** — `engine/controlRoom.ts`. Live lineage + pause/approve/freeze state machine
  (cascades down the sub-tree; resume never thaws a freeze). Clean-room from Agent Control Room.
- **Merkle batch** — `rlkit/merkleBatch.mjs`. One signed root, O(log N) inclusion proofs,
  beneficiary-bound; second-preimage-safe. Clean-room from APS×1Password.
- **Proof-carrying policy** — `rlkit/proofCarryingPolicy.mjs`. Hash-chained policy versions; every
  decision binds to the policy version in force (no retroactive compliance). Clean-room from ScopeMemory.

### 4e. Surfaced in the live browser UI (built + browser-verified in the passport app)
- **`ContainmentPanel.tsx`** — runs the real Cordon+Tell loop, renders the injection→contained story +
  "✓ trace re-verified" + stats (0 secrets fetched, blast radius 2, 7 trace events).
- **`LeakVsHoldPanel.tsx`** — the side-by-side (standard LEAKED vs vault HELD; "broker prevented the leak").
- **`ControlRoomPanel.tsx`** — interactive lineage + operator buttons (approve/deny/pause/resume/freeze);
  verified the freeze cascade (Assistant+Drafts+Payments → frozen; siblings keep running).

### 4f. Prior-art discipline
`docs/PRIOR_ART.md` credits every absorbed idea clean-room (Cordon, Tell, Crucible+IAM, Sigil,
leak-vs-hold, Merkle, proof-carrying policy, Control Room) with the source + license reality. **No
all-rights-reserved code was copied; no MIT attribution stripped; no GPL/AGPL.**

---

## 5. Repo & IP situation (the factory algorithm) — READ THIS

- On 2026-07-06 the proprietary **factory algorithm** (the TRM planning/scheduling model + its
  training/distillation/RL + the site-to-gym policy training + the business/pitch docs) was **purged
  from the PUBLIC Origin repo history** via `git-filter-repo` + force-push (`bcaa30c`→`09e28bf`).
- **Kept public (deliberate):** the whole digital-agent product + evidence layer + `services/chronos`
  + `services/cobra` (verifier/reward-hacking research) + the deterministic reward oracle + the
  "capability is not permission" thesis docs.
- **The algorithm still lives locally** (nothing lost): the pre-purge **bundle backup**, the
  `~/hackathons/Floor design` repo (site-to-gym half), and
  `~/hackathons/0620-test/physical-ai-demo-test/factoryceo_trm` (TRM half). It is **no longer in
  `~/hackathons/Origin`** (filter-repo rewrote the local tree too).
- **Residual (decided: leave it):** the old pre-purge commit is still fetchable by exact SHA on GitHub
  until GitHub GCs. The user chose **not** to delete/recreate the repo (that wipes stars/activity);
  we wait for GC.
- **The rule going forward:** never put the factory algorithm in the public Origin repo. Its home is a
  **PRIVATE repo (not yet created)**. For YC, grant reviewers access to the private repo — **do not
  merge the algorithm back into public Origin** (that re-exposes it).
- **On going public for YC:** decided *mostly no.* Keep the core algorithm private (it's the moat).
  Make public only what proves it works (evidence, demos, thesis). YC accepts private repo access.

---

## 6. Known gaps / honest limitations (what is NOT done)

1. **rlkit has no browser surface.** `rlkit/env-evidence.mjs` uses `node:crypto` (sync sha256) — it's
   the Node-side evidence core (shared with the CLIs + vitest). So Sigil/Merkle/policy/IAM **cannot run
   in a browser bundle** as-is (`node:crypto` won't resolve; React never mounts). A `/security` browser
   page was attempted and **reverted**. **Fix path (a real next task):** add a browser-safe *synchronous*
   sha256 to `env-evidence.mjs` (isomorphic: `node:crypto` in Node, a pure-JS sha256 in the browser) —
   and prove byte-identical output with a test, because committed digests/traces depend on exact hashes.
   *Alternative:* expose a server endpoint that computes these and the page renders results.
2. **The Janus rename is not executed.** Directory is still `apps/passport`; UI copy still says "Passport."
3. **White-box Tell is a drop-in, not a live claim.** It needs real open-weight model activations to be
   more than an interface; on hosted models it (correctly) abstains.
4. **Certification-as-a-market has the engine, not the product.** No buyer-facing UI, no pricing, no
   billing, no design-partner flow, no real customer evidence (blocked by design until approved).
5. **No real design partners / real customer evidence yet.** The `demo_real_customer_*` fixtures are
   deliberately *authorization-blocked* placeholders.
6. **The private algorithm repo does not exist yet.** (See §5 / §9.)

---

## 7. The comprehensive YC goal (what winning looks like)

**Company one-liner (for the application):**
> *Origin is the trust layer for AI agents: the control plane + evidence layer that lets enterprises
> grant agents scoped, revocable autonomy — and get cryptographic, independently-verifiable proof of
> exactly what each agent was allowed to do, what it actually tried to do, and that it was contained
> if it went rogue.*

**The market / why-now:** every company is about to deploy agents that touch money, data, and
production systems. The blocker is not capability — it's **trust, governance, and liability**. There is
no standard "agent got the right to do X, here's the receipt." Origin is that standard.

**The wedge (land):** the **shareable, signed Trust Receipt** + the **leak-vs-hold** proof + the
**blocked-injection containment** demo. These make the value visceral in 60 seconds and are the viral
top-of-funnel.

**The moat + expansion:** **Certification-as-a-market** — the config-bound "reference check for agents"
issued by our deterministic oracle. This is the recurring-revenue business: agent vendors + enterprises
pay to certify (and re-certify on every config change) that an agent behaves under least-privilege in a
domain (IAM/security first, then finance ops, support, data access). The RSL (Readiness/Autonomy
License) ladder (L0→L4) is the pricing + trust axis.

**What "YC-ready" concretely requires (the bar):**
1. **A crisp, memorable one-liner + a 60-second demo video** that a non-expert immediately gets.
2. **A working product a design partner can actually use** (not just a demo): sign up → run their agent
   through the gym → get a signed reference check → verify it.
3. **≥1 design partner** (LOI, pilot, or at minimum a warm "yes I'd use this") — real usage or real intent.
4. **A defensible technical depth story** judges/investors can interrogate: the deterministic-oracle
   moat, the config-bound credential, the tamper-evident trace, the containment guarantee.
5. **Honest metrics + a clean IP posture** (no overclaims; clean-room prior art; private moat).
6. **The application + video submitted**, with a coherent narrative from wedge → moat → market.

---

## 8. The 4-week launch plan (concrete, week by week)

> Assumes ~1 focused builder + Claude/Codex. Adjust ruthlessly; ship every week.

### Week 1 — Sharpen + de-risk + private-repo
- **Rename Passport → Janus** across `apps/passport` (dir, copy, brand, README) — kill the generic name.
- **Create the PRIVATE algorithm repo** and push the factory algorithm into it from the bundle (unify
  the two halves). Confirm public Origin stays algorithm-free.
- **Fix the rlkit browser gap:** add an isomorphic sync sha256 to `env-evidence.mjs` (+ a byte-identity
  test), so Sigil/Merkle/policy/IAM can render in a browser. This unblocks the whole certification UI.
- **Nail the one-liner + the 60s demo storyboard.** Record a first rough cut of the hero demo
  (blocked-injection containment + signed receipt) — pre-recorded, not live.
- **Landing page pass** on the public site: the wedge (Trust Receipt + leak-vs-hold + containment) as
  the hero; "capability is not permission" thesis; a single clear CTA (book a design-partner call).

### Week 2 — The certification product (make it usable)
- **Build the buyer-facing "reference check" flow** (browser, now unblocked): upload/configure an
  agent's IAM policy (or pick a preset) → run it through the IAM gym → see the RSL verdict + lift +
  the config-bound credential → **download the Sigil** → a public **/verify** page that re-checks a
  pasted credential offline.
- **Wire the Control Room + Tell + Cordon panels into a coherent "Console"** narrative (not scattered).
- **Pricing hypothesis:** per-certification + per-seat + re-cert-on-config-change. Draft it.
- **Start design-partner outreach** (10–20 warm targets: agent-tooling startups, enterprises piloting
  agents, security teams). Use the demo video as the opener.

### Week 3 — Design partner(s) + real evidence
- **Get ≥1 design partner running** their agent (or a representative policy) through the gym. Capture a
  real (authorized) reference check end-to-end. This is the single highest-value YC artifact.
- **Second gym domain** beyond IAM (e.g. finance-ops or data-access least-privilege) to show the
  platform generalizes.
- **Harden the honesty story:** every number reproducible; every claim scoped ("reproducible under this
  verifier," never "safe"); the deterministic-oracle-is-the-only-authority discipline visible.
- **Tighten the video** to the final 60s cut; write the "why Origin, why now, why us" narrative.

### Week 4 — Apply + launch
- **YC application:** company one-liner, the demo video, the wedge→moat→market narrative, traction
  (design partner + usage), the team/why-us, the ask.
- **Grant YC private access** to the algorithm repo if depth is requested (never public it).
- **Polish + dry-run the interview answers** (the depth story from §7.4).
- **Public launch beat:** the hero demo on X/socials (the viral leak-vs-hold + containment clip),
  landing page live, "request a reference check" CTA open.
- **Final IP + security sweep:** no secrets committed, no overclaims, no algorithm in public, clean
  prior-art credits.

---

## 9. Immediate next steps (the first new-session task list)

Do these in order; each is a clean, testable unit. Keep everything gated (build + lint + tests) and
commit per unit.

1. **Rename Passport → Janus** in `apps/passport` (copy + brand + README; optionally the dir). Update
   `docs/PRIOR_ART.md` naming section is already correct.
2. **Isomorphic sha256 in `rlkit/env-evidence.mjs`** — the unblocker. Node path unchanged (identical
   digests); add a pure-JS sync sha256 fallback for the browser; add a test asserting byte-identity
   with `node:crypto` on sample inputs. Confirm all 117 rlkit tests still pass.
3. **Rebuild the `/security` (or `/console`) browser page** in `apps/origin-web` now that rlkit loads
   in the browser: Sigil sign/verify + tamper, Merkle inclusion + tamper, proof-carrying policy chain +
   decision-binding, IAM reference-check (VALID + lift, config-drift VOID, allow-all capped). Wire the
   vite entry + route. Verify live.
4. **Create the private algorithm repo** and migrate the factory algorithm from the bundle.
5. **Certification buyer flow** (the product): the reference-check issuance + the public `/verify` page.
6. **60-second demo video** storyboard + rough cut.

---

## 10. Security & honesty constraints (MUST persist — non-negotiable)

These are load-bearing for both integrity and YC credibility. Carry them into every session.

- **The deterministic oracle is the ONLY label/reward authority.** Never an LLM grading an LLM.
- **No white-box Tell claim without real open-weight model activations.** The probe abstains otherwise.
- **Fakes are labeled as fakes.** Synthetic fixtures say so; projected numbers say "projected."
- **No production / real-customer / compliance / "safe" claims.** Say "reproducible under this verifier,"
  never "correct" or "safe." Real customer readiness stays **blocked** until approved real evidence exists.
- **Training must stay fail-closed** (`TRAINING_NOT_AUTHORIZED`).
- **Clean-room only:** no copying all-rights-reserved code; never strip MIT attribution; avoid GPL/AGPL.
  Credit inspirations in `docs/PRIOR_ART.md`.
- **Never commit `.env*`** except `.env.example`. No secrets in the repo or the bundle.
- **Never put the factory algorithm in the public Origin repo.** Private repo only.
- **Never deploy the public website without explicit authorization + a named target.** Origin push does
  not auto-deploy; the live site is a different repo (Cloudflare Pages).
- **Rotate any live keys** that ever touched disk (the old 0620 keys) before broad sharing.

---

## 11. How to run + verify locally

```bash
# Repo root
cd ~/hackathons/Origin

# Passport (→ Janus) — the security cores + demo. Self-contained client app.
cd apps/passport
npm install
npm run dev -- --port 5199 --strictPort      # open http://localhost:5199/passport.html
npx vitest run                                 # 167 tests
npx tsc -b && npx eslint src --max-warnings=0  # build + lint

# Origin-web — the live site + rlkit evidence layer.
cd ../origin-web
npm install
npm run dev                                    # multi-page (index/app/passport/foundry/soc/...)
npx vitest run rlkit/                          # 117 rlkit tests
npm run build                                  # tsc -b && vite build

# To SEE the security cores in the browser: passport /app → run any scenario → scroll to
# the Containment / Leak-vs-hold / Control Room panels (they run the real engines client-side).
```
> **Preview gotcha:** the harness preview server may bind to the *original* passport copy at
> `~/hackathons/0619/autonomy-trace-console`, not the Origin copy. To verify Origin's UI, start the
> Origin dev server yourself (as above) and point the browser at its port.

---

## 12. Files a new session should read first

**For Claude Fable 5 (new session) — read in this order:**
1. This handoff (you're reading it).
2. `~/hackathons/Origin/README.md` + `PROJECT_OVERVIEW.md` + `docs/ARCHITECTURE.md` +
   `docs/architecture/ORIGIN_TRUST_ARCHITECTURE.md` — the public product + thesis.
3. `~/hackathons/Origin/docs/PRIOR_ART.md` — the naming system + clean-room credits + license reality.
4. The security cores: `apps/passport/src/passport/engine/{tell,cordon,activationProbe,controlRoom,cordonTell,toolRouter}.ts`
   + `apps/passport/src/passport/secrets/{leakVsHold,redact,mockSecretBroker}.ts`.
5. The evidence + market: `apps/origin-web/rlkit/{env-evidence,crucible,iamGym,sigil,merkleBatch,proofCarryingPolicy}.mjs`.
6. The surfaced UI: `apps/passport/src/passport/ui/components/{ContainmentPanel,LeakVsHoldPanel,ControlRoomPanel}.tsx`.

**For Codex (share this):** the same file list, plus emphasize §6 (the rlkit browser gap + fix path)
and §9 (the immediate task list). Codex is good at the mechanical rename (§9.1), the isomorphic-sha256
unblocker (§9.2), and the browser-page rebuild (§9.3).

---

## 13. Glossary (fast reference)

- **RSL** — Readiness/Autonomy License ladder (L0→L4). The trust + pricing axis; a catastrophic
  over-grant caps the level.
- **ScoreReceipt** — a reproducible reward receipt: EnvironmentBundle + recorded action trace + pinned
  verifier → a tamper-evident, re-derivable receipt.
- **Sigil** — an ECDSA-signed, offline-verifiable evidence receipt.
- **Config-bound credential** — a Crucible "reference check" that voids if the agent's model/tools/
  context/harness or the environment changes.
- **Catastrophic (verdict)** — a security-critical over-grant (allowing a forbidden/tainted/high-
  sensitivity action) that caps the RSL level.
- **Taint / Cordon** — an agent exposed to untrusted content is tainted; the broker refuses its secrets
  and its sub-tree can be frozen (blast radius contained).
- **Clean-room** — reimplement an idea from scratch in our stack; credit the source; copy no protected code.

---

*End of handoff. Everything above is grounded in repo state at HEAD `9098dae` (passport 167 tests,
rlkit 117 tests, green). Keep this file private. Build honest. Capability is not permission.*
