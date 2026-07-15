# Cerebras × Gemma 4 Hackathon — Winning Strategy

**Event:** Cerebras × Google DeepMind "Gemma 4" 24h hackathon · June 28 10:00 AM PT → June 29 10:00 AM PT · remote/Discord.
**Model:** `gemma-4-31b` only (multimodal IN: text+images; **text-only OUT**; no video/audio in). OpenAI-compatible Chat Completions. Structured outputs + tool calling (`strict:true`). `reasoning_effort` off by default. `time_info` per request. Limits: **5K MSL / 32K MCL**, **100 RPM / 100K TPM**.
**Differentiator we must make visible:** Cerebras runs Gemma-4 at **~1,500–1,850 tok/s vs ~100 for Claude Haiku = ~15×**.

> Full reference lives in the `cerebras-hackathon` skill (api-cheatsheet, multi-agent-patterns, demo-and-viral-playbook, pitch-and-depth).

---

## The thesis (one sentence)

> **Fast inference makes verification and multi-agent loops practically free** — so we build a real-time
> **perceive → reason → act → verify** loop where a **Guardian/Verifier agent runs on every cycle**, and we
> prove on-screen (split-screen vs Gemini) that this only works because Cerebras runs Gemma-4 at ~1,500 tok/s.

This is Cerebras' *own* published thesis (the "Never Loop Without Verifiers" + "Economics of AI Reasoning"
posts) fused with our existing IP (**Guardian Agents / autonomy-trace / credential broker** from Origin &
Passport). Safety/verification as a **first-class, real-time citizen** is the wedge no one else will pitch.

---

## Master concept: **Quorum** — one engine, three submissions

**Quorum** *(name LOCKED)*: a real-time, multimodal, multi-agent **computer-use** loop on Gemma-4 +
Cerebras. **No agent acts alone; every action is ratified by a verifier quorum, in real time.**
The agent **sees a screen → decides an action → a Guardian ratifies it → it acts → re-screenshots → verifies.**
The screen (a browser, driven by Playwright) is the real-world surface — Cerebras explicitly markets
Gemma-4 for "computer use and robotics," and the *same* see→reason→act→verify loop is what would drive a
robot (robot-ready cognition; we demo it on screens).

Three agents (max — more is un-debuggable in 24h and latency stacks):
- **Perceiver** — Gemma-4 vision over a page **screenshot** → strict JSON `{summary, elements[], state, goal_progress}`. Reasoning **off** (fast path).
- **Planner/Actor** — decides the next computer action → strict JSON `{action: click|type|navigate|scroll|done, target, value, rationale}`.
- **Guardian/Verifier** — independently ratifies the action vs goal + policy (and quarantines injected text) → strict JSON `{approve: bool, reason, fix_prompt}`. On reject, `fix_prompt` becomes the next loop's input. Escalate `reasoning_effort="low"` only when uncertain.

Architecture backbone (the depth story): **orchestrator holds only `delegate_task`; each sub-agent gets a
fresh, tiny context** → respects the 5K MSL cap and pushes "effective context 200K → 25M." Everything streams
with a live **tok/s counter**, and every cycle is written to an **inspectable autonomy-trace** (loop #, what
it saw, the verdict) — which doubles as Track-3 production-readiness.

**Build it ONCE, ship it THREE ways:**

| Track | Point the engine at… | Framing |
|---|---|---|
| 1 (hero) | the **real world via webcam** ("Eyes") | embodied safety co-pilot — *the first AI fast enough to act in the real world* (physical-AI bonus) |
| 2 | the **reaction race** + the live hazard catch | "Cerebras warned 9.7× sooner — the GPU warned after it already happened" |
| 3 | the **enterprise SOC console** (already built) | real-time AI-SOC that *operates the tools*, vetoes a prompt-injection + audit trail |

---

## Track 1 — Multiverse Agents ($2K) · HERO BUILD (the "Eyes" embodied co-pilot)

**Product:** *Quorum Eyes* — a real-time safety co-pilot that watches the physical world through a **webcam**.
A Perceiver (Gemma-4 *vision*) reads the scene and coaches the next step; a **Guardian** raises a real-time
**HAZARD** alert *before* you get hurt ("STOP — fingertips under the blade", "pan's about to ignite"). Two
agents per frame; the "act" is a warning. Live only because Cerebras runs Gemma-4 fast enough to warn in time
— at GPU speed the warning lands *after* the accident. **Robot-ready:** swap the webcam for a robot's camera
and the alert for an actuator-stop — same loop, same contracts (we don't fake hardware).

**Why it scores on every Track-1 axis:**
- *Agent collaboration* — `perceiveScene` + `guardScene` (+ a deterministic HAZARD floor); the Guardian is a
  genuine second agent with veto power, not decoration.
- *Multimodal* — Gemma-4 **vision on a live camera frame** every cycle (the "Screenshot Insight" pattern, on
  the real world).
- *Speed in action* — the **reaction race** makes it visceral: same frame, Cerebras warns in ~0.15s while the
  GPU baseline warns in ~1.5s — *after it already happened.* Speed = capability, not a number.
- *Innovation (the bold/physical-AI bonus)* — embodied perception→reason→act in the real world is 2026's
  defining theme; *real-time safety for embodied AI* (the "Safety Option Layer", HomeSafe-Bench, Viture Helix
  safety glasses) is the hot niche, and our Guardian **is** that layer.

**The defensible claim (pre-baked for judges):** robotics/VLA research (SCOPE, AC²-VLA, 2025–26) found that
once a model is smart enough, **latency — not intelligence — is the bottleneck for any see→act loop**;
LLM-in-the-loop control fails on latency spikes. Cerebras removes that wall — which is the only reason a
Guardian-on-every-frame loop can warn *before* harm. (The browser computer-use loop from the earlier build is
kept as the **Track-3 SOC** surface.)

---

## Track 3 — Enterprise Impact ($1K)

**Product:** *Quorum SOC* — the same engine pointed at security/ops. Ingests **alert dashboards, log
screenshots, CCTV/asset images** → **Perceiver** triages → **classify fast (reasoning off), escalate
intelligently** (reasoning on for the suspicious few) → **Guardian verifies before any automated action** →
**full autonomy-trace audit log**.

**Why it wins the rubric:**
- *Business impact* — incident response / cybersecurity is the use case Cerebras marks "Today," and it has
  its own paper in the corpus ("faster inference lets security AI do more reasoning per second"; MTTR
  hours→minutes; ~95% of Tier-1 triage automatable).
- *Production readiness* — strict typed contracts, fresh-context sub-agents, an audit trail, a guardian gate
  before action. This is governance, not a toy.
- *AI differentiation* — Gemma-4 *reads the screenshot* (multimodal RAG / "Screenshot Insight") and decides
  in <1s; show it side-by-side vs Gemini.
- *Bonus security depth* — demo the **image prompt-injection** guardrail (malicious text embedded in an
  uploaded screenshot) and the Guardian quarantining it. Plays straight to our guardian-agent expertise.
- *Closing slide:* the **sovereign-AI** angle — "run this in-country, in the local language, on infra you
  control; speed buys the verification headroom to stay safe within SLA."

---

## Track 2 — People's Choice ($2K) · the footage

No separate build — **the engine is the most shareable thing we have.** Post a ≤60s native video to X
tagging **@Cerebras + @googlegemma** in the **US-morning** window; line up the team to reply in the first 30
min (reply velocity + replies weighted ~27× drive reach).

**Hero cut (payoff-first):**
1. **0–2s hook:** "GPU on the left. Cerebras on the right. Watch the right finish thinking before the left finishes loading."
2. **10–35s:** the **split-screen latency race** with a live tok/s counter — Cerebras finishes a *whole loop* while Gemini does one call.
3. **35–52s:** "it reacts before I finish" — hold an object to the camera, the agent calls the next step early / the Guardian catches a mistake.
4. **52–60s:** "Gemma-4 on Cerebras. The brain runs faster than the world moves." + reply-bait caption ("What would you point this at?").

⚠️ **Pre-record the speed shots** — network round-trip can dwarf inference on bad wifi.

---

## 24-hour build order (de-risked)

1. **0:00–0:30 — Access.** Confirm the key serves `gemma-4-31b` *with an image*; base64 works; wire a
   fallback Cerebras model (Llama/Qwen/Kimi) behind a flag. Confirm `time_info` is real.
2. **0:30–1:30 — Speed proof.** Split-screen Cerebras-vs-Gemini with live `time_info`. Record a clean take early.
3. **1:30–6:00 — Core loop.** Perceiver → Planner → Guardian, strict JSON each, state in files, terse outputs.
4. **6:00–12:00 — Track-1 hero surface.** Playwright browser driver + the loop visibly operating a real web task, the Guardian catching a wrong action, + the autonomy-trace panel.
5. **12:00–18:00 — Track-3 re-skin.** Point the same loop at an enterprise console (SOC/admin panel) + audit log + the image-injection guardrail beat.
6. **18:00–22:00 — Cut 3 videos** (hero / viral / enterprise).
7. **22:00–24:00 — Discord posts + `docs/ARCHITECTURE.md` + post Track-2 to X**, team replies in first 30 min.

---

## Naming (verify availability before committing)

**Name LOCKED: Quorum** — "no agent acts alone; every action is ratified by a verifier quorum, in real
time." Signals multi-agent + consensus + governance, and it's the wedge in one word. (Minor collisions:
Quorum.us, ConsenSys Quorum — fine for a hackathon; revisit if it becomes a real product.) Tagline options:
*"No agent acts alone."* / *"A second opinion on every move — in real time."* / *"The brain runs faster than
the world moves."*

---

## Top risks → mitigations

- **Gemma-4 access / key issues** → confirm in the first 30 min; fallback model behind a flag.
- **Live wifi tanks the speed shot** → pre-record all latency footage.
- **"Real-time" erased by long outputs** → cap resolution, throttle frames, force terse structured JSON.
- **Scope creep in the agent loop** → 3 agents, period. One clean loop beats a fragile orchestra.
- **Overclaiming a robot** → "we built the robot-ready brain"; never fake hardware.
- **"Why not a tiny local model?"** → not smart enough for the reasoning/verification; Cerebras = frontier
  intelligence at real-time speed (the SCOPE finding).
