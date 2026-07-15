---
name: cerebras-hackathon
description: >-
  Playbook + hard facts for the Cerebras × Google DeepMind "Gemma 4" 24-hour
  hackathon (gemma-4-31b on Cerebras Inference). Use when building, scoping,
  pitching, or demoing a project for this event — multi-agent, multimodal,
  enterprise, or a viral X/Twitter speed demo. Covers the exact model/API facts
  and gotchas, the multi-agent + verifier-loop patterns the judges wrote the
  rubric around, the "why Cerebras is fast" depth story for judge Q&A, the 60s
  demo-video + virality playbook, and three ready-to-build project blueprints
  (one per prize track) unified by one master engine. Trigger on anything about
  Gemma 4, gemma-4-31b, Cerebras inference, the three tracks (Multiverse Agents /
  People's Choice / Enterprise Impact), the latency side-by-side, or "we must win
  this hackathon."
metadata:
  type: reference
---

# Cerebras × Gemma 4 Hackathon — Winning Playbook

A 24-hour, fully-remote (Discord) hackathon. **June 28 10:00 AM PT → June 29 10:00 AM PT.**
Model: **`gemma-4-31b` only**, on the Cerebras Inference API. Three prize tracks. The single
job of every submission is to **make Cerebras inference speed visible and essential** — not a
nice-to-have, but the reason the product can exist at all.

> **The one sentence that wins all three tracks (memorize it):**
> *A multi-agent system where a fast Gemma-4 orchestrator fans out parallel sub-agents that **see**
> (images/screenshots/frames), and a separate **verifier/guardian** agent checks their work in a
> tight loop — and we prove on-screen, side-by-side, that this only works because Cerebras runs
> Gemma-4 at ~1,500 tok/s (15× a comparable GPU model).*

This skill has four reference files — read the one you need:
- **[references/api-cheatsheet.md](references/api-cheatsheet.md)** — exact model/API facts, limits, code patterns, and the gotchas that will kill a naive build.
- **[references/multi-agent-patterns.md](references/multi-agent-patterns.md)** — the orchestrator/worker + 5 named patterns + the verifier loop the judges literally wrote the Track-1 rubric around.
- **[references/demo-and-viral-playbook.md](references/demo-and-viral-playbook.md)** — the ≤60s video anatomy, the side-by-side latency race, and the X/Twitter virality mechanics for Track 2.
- **[references/pitch-and-depth.md](references/pitch-and-depth.md)** — "why Cerebras is fast" 30-sec answer, the economics-of-speed argument, the sovereign-AI angle, judge biases, and naming.

---

## The tracks (and what each judge actually rewards)

| Track | Prize | The judge is scoring… | Your wedge |
|---|---|---|---|
| **1 — Multiverse Agents** (multi-agent + multimodal) | $2K | Agent collaboration · multimodal use of Gemma-4 · **speed in action** · innovation (**physical AI / robotics / embodied / IoT bonus**) | Real-time embodied see→reason→act→verify loop |
| **2 — People's Choice** (most organic X impressions) | $2K | Organic reach · engagement · content quality · authenticity. Must post ≤60s video on X tagging **@Cerebras + @googlegemma** | The visceral **latency race** + "it reacts before I finish" clip |
| **3 — Enterprise Impact** | $1K | Business impact (search, multimodal RAG, **incident response, cybersecurity**, support, KM) · production-readiness · technical excellence · AI differentiation | Real-time multimodal **AI-SOC** with a guardian + audit trail |

You may submit to **all three** (separate Discord post per track). The smart play is **one engine,
three skins** — build the core loop once, re-point its inputs, cut the same footage three ways.

---

## The master concept: one engine, three submissions

**The engine ("Quorum" — working name, see naming in pitch-and-depth):** a real-time, multimodal,
multi-agent **perceive → reason → act → verify** loop on Gemma-4 + Cerebras, where a **Guardian/Verifier
agent runs on *every* cycle** — because Cerebras is the first thing fast enough to make per-step
verification free. *No agent acts alone; every action is ratified in real time.*

This fuses the hackathon's core thesis (*"fast inference makes verification & multi-agent loops
practically free"* — Cerebras' own words) with a genuine, defensible wedge: **safety/verification as a
first-class, real-time citizen.**

- **Track 1 → point the engine at the physical world.** Webcam/phone = eyes. Agents: **Perceiver**
  (Gemma-4 vision on frames) + **Planner** + **Guardian/Verifier**. Framed as *robot-ready embodied
  cognition* ("swap the webcam for a robot's eyes and the actuator for its arm — nothing else changes").
  Hits multi-agent + multimodal + the physical-AI innovation bonus.
- **Track 3 → point the same engine at the enterprise.** Inputs become dashboards/logs/alert
  screenshots/CCTV. **Classify fast (reasoning off), escalate intelligently (reasoning on for the
  suspicious few), Guardian verifies before any automated action**, full **autonomy-trace audit log**.
  Hits incident-response/cybersecurity + production-readiness + governance.
- **Track 2 → the footage.** The split-screen latency race + "it reacts before I finish" — the engine
  is inherently the most shareable thing you have.

> If you only build ONE thing: build the **Track-1 embodied loop**. It is the hero, it generates the
> Track-2 video for free, and it re-skins into Track-3 with new inputs + an audit panel.

---

## The non-negotiables (every submission, every track)

1. **Show the tok/s, live.** Put the API's `time_info` / tokens-sec / TTFT on screen. To Cerebras
   engineers this is free credibility; a demo without a visible speed win is dead on arrival.
2. **Side-by-side vs a GPU baseline.** The brief *recommends* it; you may call **Gemini** as the slow
   baseline. Same prompt, two panes, wall-clock visible, Cerebras finishes while the other still
   streams. **Pre-record this** — never let it ride on live wifi during judging.
3. **Make the loop the star, not a single call.** A single fast response is "nice." N iterations / N
   parallel agents / a verify-retry completing in the time the baseline does *one* call is the visceral
   "speed = capability" proof. That's the whole Cerebras thesis.
4. **Structured outputs (`strict: true`) for every agent hand-off.** Typed JSON contracts are what keep
   a multi-agent loop from dissolving into garbage. (See api-cheatsheet.)
5. **Respect the real ceiling:** **5K MSL / 32K MCL**, **100 RPM / 100K TPM**. Architect for tiny
   per-call contexts (orchestrator + fresh-context sub-agents). This is also your best depth story.
6. **Terse outputs.** Continuous webcam→VLM is only "real-time" if you cap resolution, throttle frames,
   and force short structured outputs. Unbounded prose erases the speed advantage.
7. **Be honest about hardware.** No robot? Don't claim one. "We built the robot-ready *brain*; here's
   why GPU latency would break it" beats a hollow robot claim with track-1 judges who know hardware.

---

## 24-hour build order (de-risked)

1. **First 30 min: confirm access.** Verify your key actually serves `gemma-4-31b` with **image input**.
   Wire a **fallback model** (Llama/Qwen/Kimi on Cerebras) behind a flag so a key problem can't sink you.
2. **Hour 1: the speed proof.** Build the side-by-side (Cerebras vs Gemini) with live `time_info`. This
   is your demo spine; get it working before anything else and **record a clean take early.**
3. **Hours 2–6: the core loop.** Perceiver (image→structured JSON) → Planner → Guardian/Verifier.
   **3 agents max** — 5+ is un-debuggable in 24h and the latency stacks. State in files/queues, not
   conversation history. Each agent = a system prompt + a strict schema.
4. **Hours 6–12: pick your hero surface** (webcam embodied for Track 1). Make the loop *visibly* fix /
   react / catch in sub-second passes on screen. Add the **inspectable autonomy-trace** panel (loop #,
   prompt used, what it saw, verdict) — this satisfies the "make progress inspectable" rule AND doubles
   as Track-3 production-readiness.
5. **Hours 12–18: re-skin for Track 3.** New inputs (dashboards/logs), an audit log, the "classify
   fast / escalate intelligently" framing. Mostly prompt + input changes on the same engine.
6. **Hours 18–22: cut the videos.** One ≤60s hero (Track 1), one viral cut (Track 2, latency-race +
   reaction beat), one enterprise cut (Track 3). See demo-and-viral-playbook.
7. **Hours 22–24: write the Discord posts + architecture diagram**, post Track-2 video to X tagging
   **@Cerebras + @googlegemma** in the **US-morning** window, and have the team ready to reply in the
   first 30 min (reply velocity drives X reach).

---

## Top gotchas (full list in api-cheatsheet)

- ⚠️ **Predicted Outputs and Multi-LoRA are NOT available to you** (wrong models / private-preview
  dedicated-endpoint only). Don't design around them. Raw speed already makes full re-emits feel instant.
- ⚠️ **`reasoning_effort` low = medium = high on Gemma-4 today** (no graduated depth); `none` keeps it
  off. No raw/hidden chain-of-thought (only `reasoning_format: "parsed"`).
- ⚠️ **Images: Chat Completions endpoint only**, PNG/JPEG, **≤5 images & ≤10 MB/request**, ~256–280
  tokens each. Base64 data URI always works; hosted URLs per the FAQ (verify live early).
- ⚠️ **Gemma-4 is weak at** small text, charts (dashed vs solid / color-only), spatial coordinates,
  counting, rotated/fisheye images. Don't build a demo whose success hinges on these.
- ⚠️ **Image-borne prompt injection is real** — text inside an image enters context. Treat transcribed
  image text as untrusted. (This is also a *great* Track-3 security demo / guardian angle.)
- ⚠️ **Network round-trip can dwarf inference time** on bad wifi. Pre-record the speed shots.

---

## See also
- [references/api-cheatsheet.md](references/api-cheatsheet.md) · [references/multi-agent-patterns.md](references/multi-agent-patterns.md) · [references/demo-and-viral-playbook.md](references/demo-and-viral-playbook.md) · [references/pitch-and-depth.md](references/pitch-and-depth.md)
- Related skills: **hackathon-prep** (naming + architecture-depth lessons), **guardian-agent-foundations** (the verifier/guardian/agent-security IP this build leans on).
