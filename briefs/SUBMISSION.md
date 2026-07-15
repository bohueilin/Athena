# Origin Physical AI × Passport — Submission Kit

Pitch assets in this folder:
- `Origin-Passport.pptx` — the 2-slide deck (editable; updated to the live narrative).
- `Origin-Passport.pdf` + `Origin-slide1-physical.jpg` / `Passport-slide2-agent-identity.jpg` — renders.
- `Dawn-Song-Prep.pdf` — conversation cheat-sheet.

---

## 1. Description

**One line:** *Passport is the control plane for delegated agent autonomy — the identity, permission, and accountability layer that lets you safely hand real work to AI agents.*

AI agents now hold credentials like a machine but act with the autonomy of a user. In production the dominant risk isn't a wrong answer — it's a **capable agent holding standing, over-scoped access doing real damage**, where the blast radius is whatever those credentials can reach. The question every team must answer: **when your agent acts, is it acting as itself, or as you?**

Passport answers it. The agent *proposes* a plan; Passport issues a **scoped, time-boxed, revocable grant** and decides what the agent may actually do. **Capability is not permission.** Every action is bound to an identity, judged against the declared intent, gated on human approval when it's sensitive, brokered without ever exposing a secret, written to a tamper-evident audit, and killable in one tap.

**Live and proven** (origin-physical-ai.pages.dev/passport): an **intent-conformance monitor** that contains a prompt-injection attack in real time; **attenuated delegation chains** where authority only narrows and every hop still answers to you; an **access ledger** with an instant kill-switch; and a **real, approval-gated agent payment** — the agent can buy one capped item *with your approval* but can never spend freely. Secrets stay in **1Password** (handle-only); work runs **Daytona**-isolated; **zero standing privilege** by default.

Passport is the **digital half of Origin Physical AI**: Origin licenses what a *robot* may do on your floor (a deterministic readiness license — finish / escalate / refuse); Passport licenses what a *software agent* may do on your accounts. **One control plane, two worlds — identity-bound, policy-governed, auditable, revocable.**

---

## 2. Tech Stack

**Frontend** — React 19 · TypeScript (strict) · Vite 8 · hand-written CSS design system · three.js (multi-robot sim) · viem (wallet)

**Hosting & deploy** — Cloudflare Pages (static, multi-entry) · Wrangler CLI

**Backend / BaaS** — InsForge: Auth (email + Google OAuth), Postgres, **edge functions (Deno Subhosting)**, storage, secrets, scheduled jobs · standalone Hono API server (voice structuring, model proxies, evidence)

**Agent identity & secrets** — **1Password** (Credential Broker · `@1password/sdk` · server-side JIT `op://` resolution · opaque scoped leases · vault pinning · bounded delegation) · custom credential-broker pipeline (fail-closed, Rule-of-Two / lethal-trifecta, agent-token mint)

**Sandbox isolation** — **Daytona** (isolated execution sandboxes for agent work; reference-monitor kill-switch)

**Payments (real)** — **Snaplii** (live agent payments — DoorDash gift cards via Snaplii Cash; server-brokered `quote → human-approve → purchase`; per-buy + session caps; one-shot durable nonce; HMAC-signed, mode-bound tokens; idempotency; fail-closed)

**Wallet / web3** — SIWE (Sign-In-With-Ethereum, EIP-4361) ownership proof via `viem` ecrecover

**Security primitives** — `node:crypto` (HMAC, timing-safe compare, one-shot nonce) · SHA-256 tamper-evident hash-chain audit · fail-closed capability authorization · runtime intent-conformance monitor

**AI / models** — Claude (Opus / Sonnet / Haiku), GPT-4o / GPT-5.x, Gemini, GLM, Qwen, Llama, Gemma, MiniMax — via providers Anthropic · OpenAI · Google · **Nebius** · **GMI Cloud**. Deterministic **BFS oracle** for grading (never a model judging itself).

**Robotics proving ground** — **HUD** (RL environments / proving-ground harness) · Python "robot brain" (plan → verify → repair → RL)

**Voice** — Vapi / VoiceCursor (spoken intent input)

**Quality** — Vitest (211 tests) · Playwright (e2e) · ESLint · TypeScript strict · deterministic, seedable simulation

---

## 3. Repository URL

**https://github.com/bohueilin/physical-ai-demo-test**

- **Live product:** https://origin-physical-ai.pages.dev
- **Passport (agent identity) live demo:** https://origin-physical-ai.pages.dev/passport
- Reference repo (original Passport + 1Password broker + research skill): https://github.com/bohueilin/autonomy-trace-console

> Note: the latest work is on branch `hud-factorydad-1` and is deployed live, but may not yet be pushed to GitHub `main` — push the branch so reviewers see the current code.

---

## 4. 10-second video prompt — "Origin Physical AI"

> **Punchy line:** *"A driver's license for robots."* (alt: *"Capability is not permission."*)

**Use with:** Sora / Veo 3 / Kling / Runway Gen-3. Aspect 16:9 (or 9:16 for social), 10s, cinematic, 24fps.

**Full prompt (paste this):**

> Cinematic 10-second product film, premium and restrained — "instrument-grade calm," like an Apple x aviation-safety ad. A modern warehouse/clinic floor, soft natural light, shallow depth of field. A sleek humanoid robot works calmly **alongside real people**.
>
> **0–3s:** Slow dolly-in on the robot mid-task near a human worker; a faint holographic grid maps the floor; the robot's-eye view overlays three glowing path options. Calm, confident.
> **3–6s:** The decisive beat — three crisp verdict labels snap into frame around the robot, color-coded: **FINISH** (emerald), **ESCALATE** (amber), **REFUSE** (red). The robot pauses at a human-occupied cell; the path flips to amber **ESCALATE**; it stops and looks to the person. Show restraint, not power.
> **6–9s:** A clean "**Robot Safety License · RSL L3**" card materializes and stamps with a soft seal; micro-text "FAR 0.00 · deterministic oracle." Hairline UI, mono numerals.
> **9–10s:** Cut to black. The line types on in a tight grotesk: **"A driver's license for robots."** then the wordmark **ORIGIN — Physical AI** with a small blue→mint gradient mark.
>
> **Style:** near-monochrome palette (warm off-white, deep ink) with semantic green/amber/red used sparingly; glassy holographic overlays; slow, deliberate camera; no lens flares, no cliché sci-fi neon, no glitch. **Mood:** trustworthy, quiet authority, the calm of a thing that knows exactly what it's allowed to do.
> **Sound:** a single warm sub-bass swell, one soft "verified" chime on the license stamp, near-silence otherwise. **VO (optional, calm, low):** "Robots are arriving. Origin decides what they're allowed to do."
> **Negative:** no chaotic action, no humans in danger, no text walls, no clutter, no cartoonish robots, no aggressive music.

*Alt punchy lines:* "Capability is not permission." · "Every robot earns its license before it acts near people." · "Is it ready to move near people — on this floor, doing this job?"
