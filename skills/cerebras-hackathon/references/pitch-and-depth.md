# Pitch, depth & naming

## "Why is Cerebras fast?" — the 30-second judge answer

The whole thesis is one inversion: **GPUs are memory-bound; Cerebras removed the memory wall.**

1. **The model lives on-chip in SRAM** — no fetching weights from far-away DRAM. 48 KB SRAM next to
   *each* of ~900,000 cores (50% of every core is memory). Result: **~21 PB/s on-chip memory bandwidth,
   ~200× a GPU** in the same silicon area. One-liner: *"the model isn't loaded from memory — it **is** the
   memory."*
2. **Wafer-scale = one chip, not a cluster** — WSE-3 is one whole 300mm wafer (46,225 mm², ~57× a top
   GPU die), 4T transistors, 900K cores, a 2D-mesh fabric with single-cycle latency between neighbors and
   **214 Pb/s** fabric bandwidth. No inter-chip network → no per-token synchronization/network tax.
3. **Result, proven:** open models at **1,000–3,000 tok/s** vs **50–100 tok/s** on GPUs. Citable
   head-to-head: **Kimi K2.6 = 981 tok/s vs Gemini 3.5 Flash 181 (5.4×)**, e2e 5.6s vs 17.5s; voice
   TTFT 452ms (first frontier model under the 500ms "conversation" bar). **Gemma-4 ≈ 1,500–1,850 tok/s
   vs ~100 for Haiku = 15×** at comparable intelligence.
4. **The "they said it was impossible" hook (manufacturing):** tiny defect-tolerant cores + a self-healing
   mesh route around dead cores; ~93% of cores stay active, a defect kills <0.0001% of the wafer.

**Script:** *"GPUs spend most of their time waiting on memory — the model lives in DRAM far from compute.
Cerebras prints the whole processor on one wafer and puts the model in SRAM next to 900,000 cores, so
there's no memory wall and no chip-to-chip network. That's ~200× the memory bandwidth and Gemma-4 at 15×
a comparable GPU model. For an agent that has to see, reason, and act in a loop, that's the difference
between a slideshow and real time."*

## The economics-of-speed argument (sound like an insider)

Speed/cost change **what's buildable**, not just UX.
- Reasoning costs **~6× the tokens** and **7–11× longer** for only **~10–20% accuracy** — and **~47% of
  real prompts are "simple"** (no reasoning needed). So **most agent steps should run reasoning-off/fast**;
  turning reasoning off bills **~85% cheaper** and agents run far longer before context compaction.
- "Classify fast, escalate intelligently": cheap fast pass on everything; spend reasoning only on the
  suspicious few — and fast inference makes the escalation "feel like part of the product, not a queue."
- The buildability unlock: at ~1,500 tok/s, **verification + parallel exploration become "practically
  free,"** so you can add QA/retry/verify steps that are "too time-costly" on GPUs. *Fast inference
  converts the agent loop from precious to disposable — which is what makes multi-agent architectures
  actually work.* Frame the demo as: *"because Gemma-4 on Cerebras is fast, we run [N agents / a verify
  loop / retries] that would be impossible at 100 tok/s."*

## Physical-AI framing (Track 1 innovation bonus, no robot required)

- 2026 definition of Physical AI = *"AI that perceives, reasons, and acts in the physical world"* — a
  closed perception→reason→act loop. NVIDIA Cosmos explicitly includes **"vision agents"** alongside
  robots/AVs.
- The defensible claim: robotics research (SCOPE, AC²-VLA, Lite-VLA, 2025–26) converged on **once the
  model is smart enough, perception/inference *latency* — not intelligence — is the dominant bottleneck;
  LLM-in-the-loop control fails on latency spikes/oscillation.** So: *Gemma-4 + Cerebras closes the
  see→reason→act loop fast enough to actually control the real world — the thing GPU latency makes
  impossible.* Cerebras itself markets Gemma-4 for "computer use and robotics."
- **CAN claim:** "the same loop that drives a robot"; "robot-ready / VLA-shaped cognition"; "swap the
  webcam for a robot's eyes and the actuator for its arm — nothing else changes." **CANNOT claim:** that
  you have/ran a robot or did real manipulation. Honesty beats a hollow robot claim with track-1 judges.

## Sovereign-AI angle (closing slide for enterprise/government)

- Thesis line: *"Sovereignty is the foundation. Capacity is the prerequisite. Speed is the differentiator."*
- The non-obvious point judges like: *"higher output speed lets institutions spend more of the response
  budget on reasoning, verification, and tool use while still meeting real-world SLAs"* — i.e. **speed buys
  safety/verification headroom**, which dovetails with the guardian/verifier wedge.
- Proof points: ~15× faster inference, >10× faster training; live deployments — UAE/G42 **JAIS** (Arabic,
  ~2,000 tok/s), US DOE **Genesis Mission**, India's **8-exaflop** national supercomputer.
- Deploy as: *"a hospital/ministry/factory could run this vision agent in-country, in the local language,
  fast enough to keep a human in the loop, on infrastructure they control."*

## Judge biases to exploit (Cerebras + DeepMind engineers)

- **Always show tok/s.** A demo without a visible latency win is dead on arrival.
- **Use their multi-agent vocabulary** (orchestrator/sub-agents, the 5 patterns, "200K→25M"). The
  *Lessons learned* post is the Track-1 answer key.
- **Verification is the differentiator** — show a builder + independent verifier with a *visual* check.
  DeepMind judges probe "spiralling" (never ends) and "cheating" (games the goal) — pre-bake answers.
- **"This feels like a product, not a hackathon project"** is the phrase that wins. Polish + one real
  end-to-end workflow beats breadth. Recorded demos beat live ~9/10.
- Pre-bake the **"why not a tiny local model?"** rebuttal: small local models aren't smart enough for the
  reasoning/verification; Cerebras gives *frontier intelligence AT real-time speed* (the SCOPE finding).

## Naming (from the hackathon-prep retro — naming is a product decision)

The wedge to signal: **verified, real-time, multi-agent action — a guardian/second-opinion on every move,
fast enough for the real world.** Avoid generic/overloaded metaphors (the "Passport" mistake). Run finalists
through the hackathon-prep rubric (distinctiveness, ownability, wedge-signal, say-ability, serious-infra).

Working directions (verify availability before committing):
- **Quorum** *(lead)* — "no agent acts alone; every action is ratified by a quorum." Signals multi-agent +
  consensus + governance. Note collisions (Quorum.us, ConsenSys Quorum) — fine for a hackathon, check for
  a real product.
- **Lockstep** — builder + guardian move in lockstep, in real time. Signals coordination + safety.
- **Vigil** — a guardian that never blinks because it's finally fast enough. Safety/watchfulness, short.
- **Tribunal** — a panel that ratifies agent actions; evocative, heavier.

Whatever the master engine is called, give each track submission a clear sub-name (e.g. the embodied build
vs the enterprise AI-SOC build) so each Discord post reads as its own product.
