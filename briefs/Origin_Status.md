# Origin_Status — Single Source of Truth

> **Read this first.** This is the canonical status + roadmap for Origin. Any new conversation
> (Claude, Fable 5, or Codex) should read this file before doing anything else. It **supersedes and
> folds in** the two earlier briefs `Origin-YC-HANDOFF.md` + `Origin-FABLE-KICKOFF.md` (same folder —
> safe to delete; everything relevant is here).
>
> **Where it lives + why:** `briefs/Origin_Status.md` inside the **PRIVATE** repo
> `github.com/bohueilin/Athena` — so it syncs across your machines (e.g. the Mac Mini: `git pull`)
> without ever touching the **public** `github.com/bohueilin/Origin` repo. It holds YC strategy +
> private-algorithm context, the exact category we purged from the public repo. **Never commit this
> file into the public Origin repo** (Athena-private only).
>
> **Snapshot (updated 2026-07-13 by a Fable 5 audit+harden session):** repo PUBLIC, branch `main`,
> HEAD `4a43817`+. ⚠️ **Always `git fetch && git pull --rebase` before working** — the GitHub remote is
> the truth. Tests green (`make gates-all`): **janus 168 · origin-web 428 · @origin/evidence 13 ·
> @origin/verifier-core 23 · cobra 176 · chronos 383** (~1,191). Build + lint clean; CI now also runs the
> evidence-verify gates.
>
> **A full audit + hardening pass landed** — see `~/hackathons/AUDIT_REPORT.md` (private). It shipped:
> the existential public-honesty P0s (fabricated "3% Qwen3-4B" removed, `/foundry` absolutes scoped, the
> `/verify` false-VOID of the flagship TR-A002 proof fixed, `/rsi` contamination caveated), a batch of
> security/legal/product P1s (GA consent, Nebius endpoint guards, `canonical()` digest-collision fix,
> private-IP-leak doc cleanup, `/security`+`/verify` discoverability, honesty-lint extended to meta/og +
> React copy, evidence-verify wired into CI), and — in the **private `origin-factory` repo** — the four
> verifier reward-hacking holes closed with adversarial tests + honestly re-verified metrics.
> **Still with the founder (human decisions):** LICENSE, branch protection, domain registration,
> git-history purge, deploy cutover. (The public IP leak is RESOLVED — §1.3.)
>
> **Moat + product builds (2026-07-13, gated + pushed; see `origin-factory/docs/yc/BUILD_STATUS.md`):**
> the buyer **reference-check flow** (`/reference-check`); the **self-hardening gym** — the sharpest
> moat layer (`verifier-core/gymHardening.mjs` + `public/rsi/gym-hardening.json`, robustness 0→1 as
> customers surface over-grants); a **deterministic underwriting signal** for agent insurance
> (`verifier-core/underwriting.mjs`); a **verification-substrate API** under the GRC stack
> (`src/certify/certifyApi.ts` + `docs/api/origin-certify.openapi.yaml`); the **verified-trace data
> factory** (`origin-factory/trace-factory/`); and the **robust multi-seed** student win
> (5.4%±2.4%, 8/8 seeds). YC answers + strategy: `origin-factory/docs/yc/{YC_ANSWERS,BUILD_STATUS}.md`.
>
> **The physical actor (2026-07-13, gated + pushed):** a **verified warehouse simulation** at
> `/simulation` (`apps/origin-web/src/simulation/`) — multi-robot fulfilment in **2D (canvas) + 3D
> (Three.js)** on Origin's OWN deterministic `warehouse.ts` oracle (finish/escalate/refuse),
> collision-free + people-first by construction; the run drops a signed Sigil re-verified on `/verify`.
> Clean-room from the "Warehouse AI" concept (no code copied; credited in `docs/PRIOR_ART.md`); no
> learned-policy claim. This is the "one evidence spine, two actors" physical half, in-browser. A
> legally-clean **floor-plan ingest pipeline** (`origin-factory/site-to-gym/scripts/ingest_footprints.mjs`
> + `data/external/SOURCES.json`) turns real government footprints (ODbL) into oracle-labeled floors.
>
> **⚠️ Deploy cutover — READY, human-owned (2026-07-14).** We are consolidating onto Origin as the
> single deploy source (replacing `physical-ai-demo-test`). The Pages build is **verified from a clean
> clone** (root `apps/origin-web`, `npm install && npm run build`, output `dist` — resolves the
> `@origin/*` workspace, builds all 17 pages, `functions/` present). `docs/CUTOVER.md` is the exact
> dashboard checklist; `docs/DEPLOY.md` + `CLAUDE.md` now name Origin canonical. The **repoint + env-var
> confirm** is the human step (no agent has Cloudflare creds). Project env vars carry over on a source
> repoint; only the lead function's `LEAD_WEBHOOK_URL`/`RESEND_*` are new. `physical-ai-demo-test` stays
> the rollback until Origin deploys cleanly, then archive it.

---

## 0. The one-liner (memorize)

**Origin is the verified-environment layer for autonomous systems — digital agents *and* physical
robots.** One invariant runs through everything:

> **Model proposes. Environment verifies. Gate decides. Trace proves. — Capability is not permission.**

The company thesis (this is the whole pitch): *a deterministic verifier that gates a proposed plan and
emits tamper-evident, signed, reproducible evidence is the SAME product whether the actor is a software
agent touching an API or a humanoid robot touching a factory floor.* **One evidence spine, two domains.
The environment is the moat, not the model.**

---

## 1. WHERE WE ARE (status)

### 1.1 Repo shape (current, post-restructure)
```
github.com/bohueilin/Origin   PUBLIC · main · HEAD 9bee271 · pushed
  apps/janus/            ← the gate/identity app (RENAMED from apps/passport). 167 tests.
  apps/origin-web/       ← the live marketing/console site + /security + /verify pages. 416 tests.
  apps/chronos-ui/       ← Chronos run-graph UI.
  packages/verifier-core/  ← @origin/verifier-core: the extracted, publishable Verifier SDK
                             (sigil, iamGym, merkleBatch, proofCarryingPolicy, crucible, checkpoint,
                             env-promotion, mcp-adapter, tool-registry, build-trace). 23 tests.
  services/chronos, services/cobra   ← verifier / reward-hacking research (public, kept).
  .github/workflows/{ci.yml, deploy-origin-web.yml}  ← CI gate + human-gated deploy.
```
> **Note:** `apps/origin-web/rlkit/*.mjs` no longer exists — the core evidence lib was extracted to
> `packages/verifier-core/`. If older notes reference `rlkit/…`, translate to `packages/verifier-core/…`.

### 1.2 What is BUILT + shipped (all committed + pushed + tested)
**The digital trust layer (complete):**
- **Janus gate** (`apps/janus`): fail-closed `toolRouter.ts` with an optional Tell+Cordon guard;
  hash-chained `auditLogger.ts`; `SecretBroker` (opaque handles, never secrets).
- **Tell** (measured intent): `engine/tell.ts` + `engine/activationProbe.ts` — declared vs measured vs
  action; white-box TaskTracker-style probe that **abstains at confidence 0 without model activations**.
- **Cordon** (containment): `engine/cordon.ts` — taint → broker refuses the secret → freeze only the
  poisoned sub-tree (blast radius measured). Wired end-to-end in `engine/cordonTell.ts`.
- **Crucible + IAM gym** (certification): `verifier-core/crucible.mjs` + `verifier-core/iamGym.mjs` —
  config-bound "reference check for agents" (`issueIamReferenceCheck`), deterministic-oracle-issued,
  RSL L0→L4, catastrophic over-grant caps the level.
- **Product steals:** `verifier-core/sigil.mjs` (ES256 signed receipt), `janus/…/secrets/leakVsHold.ts`,
  `janus/…/engine/controlRoom.ts` (lineage + pause/approve/freeze), `verifier-core/merkleBatch.mjs`,
  `verifier-core/proofCarryingPolicy.mjs`.
- **Surfaced in the browser** (run the real engines client-side, verified): `ContainmentPanel.tsx`,
  `LeakVsHoldPanel.tsx`, `ControlRoomPanel.tsx` in the Janus app.
- **RL evidence platform:** the 9 pillars (env-as-artifact, reset/step, MCP registry, verified reward,
  replay+cost, checkpoint/resume, curriculum, promotion, ScoreReceipts) in `verifier-core` + origin-web.

**The Week-2 / launch-prep additions (done by the "Fable 5" session ~2026-07-07):**
- ✅ Full **Passport → Janus rename** (`apps/passport` → `apps/janus`).
- ✅ **Isomorphic SHA-256** — the evidence core now hashes in Node *and* the browser (byte-identical),
  which **unblocked the certification browser UI** (the old `node:crypto` blocker is gone).
- ✅ Live **`/security`** page (Sigil sign/verify/tamper, Merkle, proof-carrying policy, IAM check).
- ✅ Public **`/verify`** page (paste a credential → re-verify offline).
- ✅ **Verifier SDK extracted** to `@origin/verifier-core` (a real, publishable package).
- ✅ **CI gate** + **human-gated deploy** workflow + Merkle second-preimage + canonical-undefined fixes.

### 1.3 The IP / repo posture (critical — do not violate)
- The proprietary **Factory Algorithm was purged from the public `Origin` repo history** (force-pushed).
  Origin's own history is clean (verified 2026-07-13). It lives privately in **`origin-factory`** (§3/§4).
- ✅ **RESOLVED (2026-07-13) — the `physical-ai-demo-test` repo is now PRIVATE.** It previously exposed
  the Factory Algorithm (`factoryceo_trm/` with `verifier.py`, `repair_loop.py`, `trm_student.py`) as the
  world-readable live-site deploy repo. `gh repo view` now returns `visibility: PRIVATE`. Note: anyone who
  cloned it while public still has that copy — the moat's durable home is the private `origin-factory`.
- The **live website** deploys from a *different* repo (`physical-ai-demo-test` / `hud-factorydad-1`)
  via Cloudflare Pages. **Pushing Origin does NOT deploy. Never deploy without explicit auth + target.**

### 1.4 Cloud launch-sprint additions (remote `main`, PR #1 merged — AHEAD of some local machines)
A cloud "origin-yc-launch-sprint" agent already shipped (verify locally after `git pull`):
- ✅ **The unification, publicly demonstrated:** a **factory-plan reference check example — "one evidence
  spine, two actors"** on the `/verify` page (`apps/origin-web/src/verify/examples.mjs` + `VerifyPage.tsx`
  + `selftest.mjs`). *This is the YC-winning demo move — an agent action and a factory plan verified by
  the same signed evidence.* (Uses the public evidence format; the private algorithm stays private.)
- ✅ **`/trust` live gated-evidence scoreboard** ("don't take our word for it" — `trust.html` +
  `public/trust/gates-summary.json`).
- ✅ **Property-based tests on the deterministic oracle** (`services/cobra/tests/test_oracle_properties.py`
  — "the moat must never be wrong").
- ✅ **CI hardening:** gate all Python in CI, one green scoreboard, secret-scan (gitleaks), **honesty-lint**.
- ✅ **Unified README narrative + design-partner CTA.**
> Net: the **trust-layer + public demo are further along than §5 assumes** — several §5 items are done.
> The **private Factory-Algorithm gaps (§3.3) are NOT touched by the sprint** and remain the real work.

---

## 2. THE TWO HALVES (the unification thesis = the YC story)

Origin has two halves that are secretly the same product:

1. **Digital trust layer (PUBLIC, built).** Janus + Tell + Cordon + Chronos + Crucible + Sigil. An
   agent proposes a plan → scoped revocable authority → measured intent → contained blast radius →
   signed proof. **Done + tested.**
2. **Physical Factory Algorithm (PRIVATE, the moat).** A verifier gates a robot/factory *plan* the
   exact same way. **Deep + real, lives in private originals; not yet unified with the evidence spine.**

**The world-class move (highest-leverage next build):** make the Factory verifier emit the SAME Origin
ScoreReceipts + Sigils. Then a factory plan and an agent action are the same first-class, tamper-evident,
signed, reproducible artifact — proving *"Origin: the verified-environment layer for any autonomous
actor."* That single demo is the YC differentiator.

---

## 3. THE ORIGIN FACTORY (the algorithm) — design · state · next steps

> The private moat — the **physical** half of "the environment is the moat." **NOT in the public Origin
> repo** (purged). Two components; three locations (see §4). ⚠️ **The PRIVATE algorithm repo does not
> exist yet — creating it is next-step #1.** Scope is honest + bounded: no real robot/PLC/MES/ERP
> control, no unbounded-autonomy claim — a clean verifiable environment + recursive repair + metrics +
> RFT data export. Autonomy claims stay bounded by what the verifier actually gates.

### 3.1 The design — how the algorithm works

**Component A — FactoryCEO-TRM** (`~/hackathons/0620-test/physical-ai-demo-test/factoryceo_trm`):
verifiable autonomous factory operation. Thesis: *"the CEO leaves for two weeks and operations keep
running"* — credible **by design**, because the brain literally cannot emit an infeasible plan.
**Brain decides → verifier gates → humanoid executes** (decision/verification layer, NOT motor control).
```
synthetic scenarios (src/generator.py) → teacher plan (deterministic / Claude / Gemma-via-Fireworks)
  → src/verifier.py         → structured HARD-constraint errors + a scalar soft reward
  → src/repair_loop.py      → recursive verify→repair→re-verify until 0 hard violations & reward plateaus
  → VERIFIED reasoning traces  → distill a tiny TRM student (src/trm_student.py, src/rl_train.py,
                                 distill/grpo.py, HUD env)  — the Sillon/RATP recipe
  → verified plan (= the robot's task queue) → humanoid (isaac/: Isaac Sim/Lab + V-JEPA 2 perception)
```
- **The verifier (`src/verifier.py`) is THE product.** Hard constraints that MUST be zero to execute:
  no machine overlap · no unqualified operator · no missing material · no hallucinated entity. Soft
  reward, tuned so violations dominate and repairs pay off: `HARD_VIOLATION_PENALTY=800`,
  `ON_TIME_BONUS=+200`, `LATENESS=8/hr` (cap 600), `TRUST_PENALTY_LATE=300`, `OVERTIME=150`,
  `EXPEDITE=+50%` material, `SCRAP=60%` of job revenue. Operators are typed `human|robot` — a humanoid
  is just another schedulable resource, so the plan JSON *is* the control stack's task queue.
- **The recursive repair loop (`src/repair_loop.py`)** picks the highest-priority hard error, applies a
  local repair (move / swap / expedite / safety / reject-negative-margin), re-verifies, repeats. Every
  step is logged → the RFT training signal.
- **The TRM student (`src/trm_student.py`)** = a **Tiny Recursive Model** (Samsung SAIL "Less is More:
  Recursive Reasoning with Tiny Networks"): a few-K-param net over a fixed tensor encoding of the
  verifier's error signature, recursively predicting the next repair op — replaces the heuristic once
  trained. **Sillon/RATP thesis (`distill/RECIPE.md`):** narrow domain + synthetic data + domain
  reasoning traces + a **real verifier** ⇒ a small specialized model matches/beats frontier LLMs. *This
  is the Origin thesis in the physical domain — the environment beats the model.*

**Component B — Origin Environment Factory ("site-to-gym", `~/hackathons/Floor design`):**
*"One floor plan becomes a deduplicated robot safety eval set in seconds. Gemma proposes. Origin
verifies."* Floor plan → Gemma-on-Cerebras explodes it into many safety scenarios + adversarial tests →
a **deterministic verifier** assigns **finish / escalate / refuse** → oracle-filtered hazard
augmentation adds refusals + hard negatives → RSI dataset + graph tensors → trained bounded
safety/occupancy/customer policies (`ml/`).

### 3.2 Where we are — algorithm state (HONEST; do not overclaim)

**Proven + defensible (the real core):**
- ✅ **The verifier + recursive repair loop drives HARD violations to ZERO.** Measured across the
  synthetic corpora: **14→0, 281→0, 761→0, 1,400→0** hard violations eliminated (256 grounded records,
  Fireworks teacher). This is the credible "cannot ship an infeasible plan" claim.
- ✅ **Baseline confirms the need:** frontier LLMs one-shot on the raw HUD → reward ≈ **0.0** (they emit
  infeasible/unsafe plans). Safe autonomy needs the verifier gate + repair, not a bigger model.
- ✅ **site-to-gym:** oracle finish/escalate/refuse labels + trained safety/occupancy policies (~4.7k
  oracle-labeled floors; ~98.5% balanced-accuracy safety policy cited previously); RSI dataset + graph
  tensors + a dashboard exist (`outputs/`, `datasets/{floors,rl_episodes,sft_pairs}_v1.jsonl`).
- ✅ **Test coverage:** 9 pytest files in TRM (verifier / repair_loop / student / simulator / safety /
  ruler / seeds_loop / floor_layout / integration).

**Updated 2026-07-13 (origin-factory, re-verified deterministically):**
- ✅ **The four verifier reward-hacking holes are CLOSED** (unbounded quote, negative procurement,
  unchecked duration, repair non-termination). Repair now *provably* returns 0-hard; +6 adversarial
  property tests (12 total). The invariant "the brain cannot ship an infeasible plan" is now true.
- ✅ **The student win is now ROBUST (multi-seed, 2026-07-13).** A trained 2,954-param TRM student
  (`distill/trm-student/trm.pt`, deterministic) beats the hand-written rule policy by **5.4% ± 2.4% fewer
  mean repair steps across 8 training seeds** on a 40-scenario held-out medical-devices battery — **8/8
  seeds win, 100% feasible on every seed, op-acc 0.82**, paired 95% CI [0.35, 1.08] steps (excludes 0).
  Reproduce: `distill/bench_trm_multiseed.py`. (The earlier single-seed 10.8% was a favorable draw; 5.4%
  is the honest, defensible number.) This closes the #1 remaining algorithm proof point.
- ✅ **Dispatch-order RL: +32.5% profit** vs greedy (reproducible; uses the honest dispatch channel, not
  the reward-hack holes). ⚠️ **The GRPO/HUD-reward path is still noisy/early** (~0.04 shaped) — that
  specific "GRPO student beats teacher" story is NOT proven; the repair-step + op-accuracy result above
  is the honest student win.
- ✅ **The unification is REAL** (`evidence-adapter/` emits @origin/verifier-core ScoreReceipts + Sigils
  with a persistent committed issuer key; verifies on the public `/verify`). No robot/PLC/MES/ERP
  integration (explicit scope bound).

### 3.3 Algorithm next steps (the roadmap)

1. ✅ **DONE — PRIVATE algorithm repo exists** (`origin-factory`).
2. **Close the student-win gap — the headline proof point (PARTLY DONE).** A trained TRM student with
   persisted weights now shows a *preliminary* held-out win (~10.8% fewer mean repair steps, op-acc 0.72),
   but it is **single-seed, N=24, median-tie**. **Remaining:** run it **multi-seed with variance/CI** on a
   larger held-out set so it's a robust win; fix or drop the noisy GRPO/HUD-reward path. Never fake it.
3. ✅ **DONE — the Sigil unification is real** (`origin-factory/evidence-adapter/`). Deepen if desired.
4. ✅ **Verifier hardened** (four holes closed + adversarial tests, 2026-07-13). Still open: a **second
   factory domain** so the environment moat visibly generalizes.
5. **The Isaac execution proof:** a short, honest "verified plan → humanoid executes in Isaac Sim" clip
   for the demo (the plan JSON is the task queue).

---

## 4. WHERE EVERYTHING LIVES

| Thing | Location | Notes |
|---|---|---|
| Public trust layer + evidence + showcase | `github.com/bohueilin/Origin` (PUBLIC) · `~/hackathons/Origin` | push ≠ deploy |
| Verifier SDK (publishable) | `packages/verifier-core` (`@origin/verifier-core`) | the certification engine |
| Live website | repo `physical-ai-demo-test` / `hud-factorydad-1` → Cloudflare Pages | never deploy w/o auth+target |
| **PRIVATE algorithm repo (EXISTS)** | **`github.com/bohueilin/origin-factory` (PRIVATE) · `~/hackathons/origin-factory`** | **the moat's real home — has factoryceo-trm + site-to-gym + `evidence-adapter` (the working unification) + `flywheel` (RSI + signed lineage) + `docs/yc/`. 4 verifier holes CLOSED (2026-07-13); metrics re-verified.** |
| FactoryCEO-TRM original | `~/hackathons/0620-test/physical-ai-demo-test/factoryceo_trm` | source copy — ⚠️ lives on the PUBLIC `physical-ai-demo-test` repo (the IP leak, §1.3-note) |
| site-to-gym original | `~/hackathons/Floor design` | source copy of the robot-readiness gym |
| Nested `factory-private/` | inside the public Origin tree (gitignored, own git, NO remote) | a SEPARATE 3rd clean-room `forge`+`platform` effort; candidate to merge into origin-factory or retire |

---

## 5. WHAT TO BUILD NEXT (prioritized roadmap)

> Each item is a clean, testable unit. Keep everything gated (build + lint + tests) and commit per unit
> to the RIGHT repo (public trust-layer → Origin; algorithm → the private repo). Order roughly by
> leverage toward YC.
>
> ⚠️ **RECONCILE WITH §1.4 (the cloud sprint already did some of this):** #2 (the unification) exists as
> a public **/verify factory-plan reference-check example**; #5 (landing/narrative + design-partner CTA)
> is done; the **/verify half of #3** is done (a public offline re-verify page + /trust scoreboard).
> **The still-open, highest-value work is the PRIVATE algorithm side + turning demos into a real
> product + a real partner:**

1. ✅ **DONE — the PRIVATE algorithm repo exists** (`origin-factory`, private, with a remote; FactoryCEO-TRM
   + site-to-gym + the working unification + flywheel + YC docs). This is the home for all algorithm work
   + the thing you grant YC private access to. (Verifier holes closed + metrics re-verified 2026-07-13.)
2. **The unification (the world-class move):** make `factoryceo_trm/verifier.py` emit an Origin
   **ScoreReceipt + Sigil** using the exact `@origin/verifier-core` digest discipline. Apply the RSL
   ladder to factory plans (a catastrophic hard-violation caps the level). Now Crucible issues a
   "reference check" for a factory brain the same way it does for an IAM agent. **This is the demo that
   wins.** (Evidence format is public/shared; the algorithm stays private.)
3. **Turn `/security` + `/verify` into a real BUYER product** (not just a demo): configure/upload an
   agent's IAM policy (or pick a preset) → run the gym → RSL verdict + lift + config-bound credential →
   **download the Sigil** → the `/verify` page re-checks it offline. Add a "book a reference check" CTA.
4. **Run the real Factory pipeline + train/eval the tiny TRM student** (in the private repo): generate
   fresh verified episodes → train `trm_student.py` → a benchmark table (heuristic vs learned-TRM vs
   frontier-teacher baseline, scored by the real verifier). This is the Sillon-thesis proof point.
5. **Landing page + narrative refresh** to the unified one-liner (§0). Single clear CTA.
6. **The 60-second demo video** (see §6).
7. **Design-partner outreach** → ≥1 real (authorized) reference check end-to-end.
8. **YC application + deck.**

---

## 6. WHAT TO BUILD TO WIN Y-COMBINATOR

**What YC is actually buying:** a huge market + a wedge you can show working in 60 seconds + a moat +
evidence someone wants it. Here's the sharp version for Origin.

### 6.1 The winning demo (build this, pre-record it)
**"One evidence spine, two actors."** Split screen:
- Left: an **agent** hit by a prompt injection → Tell blocks it pre-execution → Cordon contains it →
  a **signed Sigil receipt** drops out. (leak-vs-hold as the kicker: standard agent leaks the key,
  vault agent holds.)
- Right: a **factory brain** proposes a plan with a hard violation → the verifier gates it → the repair
  loop fixes it → the **same signed Sigil receipt** drops out.
- Bottom: the public **/verify** page re-checks *both* receipts offline, from the same verifier.
- Punchline: *"Same trust spine. Software agent or humanoid robot. Capability is not permission."*

### 6.2 The one metric that matters
**≥1 design partner running a real, authorized reference check.** Real usage (or a signed LOI/pilot)
beats any amount of polish. Everything in §5 exists to make this possible; prioritize it.

### 6.3 The narrative (wedge → moat → market)
- **Wedge (land):** the signed Trust Receipt + leak-vs-hold + blocked-injection containment. Visceral,
  viral, 60 seconds. This is the top-of-funnel.
- **Moat:** the deterministic verified environment. Digital = the IAM/agent gym; physical = the Factory
  Algorithm (verifier-gated, Sillon thesis). *Nobody else has a real verifier-gated environment for
  BOTH — and the environment beats the model.*
- **Market + revenue:** Certification-as-a-market — config-bound "reference checks for agents/robots,"
  priced on the RSL ladder, **re-certified on every config change** (recurring). IAM/security first,
  then finance-ops, support, data-access, physical readiness.

### 6.4 The depth story (for the interview — rehearse these)
- Why the deterministic oracle is the moat (vs LLM-graded rubrics that can be gamed).
- Why a config-bound credential *voids* on drift (real security, not a static badge).
- Why the tamper-evident hash-chain + Sigil makes evidence independently verifiable (no trust in us).
- Why the environment beats the model (Sillon/TRM: 600M reasoner matches frontier on a narrow task).
- The containment guarantee (Cordon: the secret is never fetched for a tainted agent; blast radius is
  bounded to the poisoned sub-tree).

### 6.5 The YC-ready bar (checklist)
- [ ] Crisp one-liner + a 60s demo a non-expert immediately gets.
- [ ] A product a design partner can actually use (not just a demo) — the §5.3 buyer flow.
- [ ] ≥1 design partner (LOI / pilot / warm "yes I'd use this").
- [ ] A defensible depth story (§6.4), rehearsed.
- [ ] Honest metrics + clean IP (clean-room prior art; private moat; no overclaims).
- [ ] Application + video submitted; private-repo access ready for YC (never public the algorithm).

---

## 7. THE 4-WEEK LAUNCH PLAN (updated for where we are)

- **Week 1 — foundation (LARGELY DONE by Fable):** ✅ Janus rename, ✅ isomorphic sha256, ✅ /security +
  /verify pages, ✅ verifier-core SDK, ✅ CI + human-gated deploy. **Remaining:** create the private
  algorithm repo (§5.1); nail the one-liner + demo storyboard.
- **Week 2 — the certification product + the unification:** the buyer flow (§5.3); the Factory-verifier-
  emits-Sigil unification (§5.2); the TRM benchmark (§5.4). Start design-partner outreach.
- **Week 3 — design partner(s) + real evidence:** ≥1 partner runs a real reference check; a second gym
  domain; tighten the video; harden the honesty story.
- **Week 4 — apply + launch:** YC application + video; grant private algorithm access to YC; rehearse
  the depth story; public launch beat (the viral clip + landing CTA); final IP/security sweep.

---

## 8. SECURITY & HONESTY CONSTRAINTS (non-negotiable — carry into every session)

- **Deterministic oracle is the ONLY label/reward authority.** Never an LLM grading an LLM. (The
  factory `verifier.py` + site-to-gym checks ARE the oracle — never replace them with a model.)
- **No white-box Tell claim without real open-weight activations** (the probe abstains otherwise).
- **Fakes labeled as fakes; "projected" numbers say so; "reproducible under this verifier," never
  "safe"/"correct."** Real customer readiness stays **blocked** until approved real evidence exists.
- **Training stays fail-closed** (`TRAINING_NOT_AUTHORIZED` where present).
- **Clean-room only** — credit inspirations in `docs/PRIOR_ART.md`; copy no all-rights-reserved code;
  never strip MIT attribution; avoid GPL/AGPL.
- **Never commit `.env*`** (except `.env.example`); no secrets in any repo or the bundle. Rotate the old
  0620 keys before broad sharing.
- **Never put the Factory Algorithm in the public Origin repo** — private repo only. For YC, grant
  private access; do NOT merge the algorithm into public Origin.
- **Never deploy the public website without explicit authorization + a named target.**

---

## 9. HOW TO RUN + VERIFY

```bash
cd ~/hackathons/Origin
# Janus (the gate app) — self-contained client demo
cd apps/janus && npm install && npm run dev -- --port 5199 --strictPort   # open /passport.html (or /janus.html)
npx vitest run                                # 167 tests
# Origin-web (site + /security + /verify)
cd ../origin-web && npm install && npm run dev
npx vitest run                                # 416 tests
npm run build                                 # tsc -b && vite build
# The Verifier SDK
cd ../../packages/verifier-core && npx vitest run   # 23 tests
```
- **See the cores in the browser:** origin-web `/security` (Sigil/Merkle/policy/IAM) + `/verify`
  (offline re-check); Janus `/app` → run a scenario → Containment / Leak-vs-hold / Control Room panels.
- **Preview gotcha:** the harness preview may bind to the OLD passport copy at
  `~/hackathons/0619/autonomy-trace-console`. Start the Origin dev server yourself and use its port.

---

## 10. READ ORDER FOR A NEW SESSION + GLOSSARY

**Read order:** (1) this file. (2) `~/hackathons/Origin/{README.md, PROJECT_OVERVIEW.md,
docs/ARCHITECTURE.md, docs/PRIOR_ART.md}`. (3) Trust cores: `apps/janus/src/janus/engine/{tell,cordon,
activationProbe,controlRoom,cordonTell,toolRouter}.ts` + `secrets/{leakVsHold,redact,mockSecretBroker}.ts`.
(4) SDK: `packages/verifier-core/{sigil,iamGym,crucible,merkleBatch,proofCarryingPolicy}.mjs`.
(5) Factory Algorithm: `factoryceo_trm/{README.md, distill/RECIPE.md, src/verifier.py, src/repair_loop.py,
src/trm_student.py}` + `Floor design/README.md`.

**Glossary:** **RSL** = Readiness/Autonomy License ladder L0→L4 (trust + pricing axis; a catastrophic
over-grant caps the level). **ScoreReceipt** = reproducible reward receipt (bundle + trace + pinned
verifier → re-derivable). **Sigil** = ES256-signed, offline-verifiable evidence receipt. **Config-bound
credential** = a Crucible "reference check" that voids if model/tools/context/harness/env changes.
**Catastrophic** = a security-critical over-grant that caps the RSL. **Taint/Cordon** = exposed agent is
tainted; broker refuses its secrets; sub-tree can be frozen (blast radius bounded). **Clean-room** =
reimplement an idea from scratch; credit the source; copy no protected code.

---

*Canonical status. Supersedes `Origin-YC-HANDOFF.md` + `Origin-FABLE-KICKOFF.md`. Grounded in repo
state at HEAD `9bee271` (janus 167, origin-web 416, verifier-core 23; all green). Keep private. Build
honest. Capability is not permission.*
