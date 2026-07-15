# Demo video (≤60s) + Track-2 virality playbook

The brief: **≤60s**, must **show Cerebras speed**, *recommends* a side-by-side vs a GPU provider, focus
on the project, hide anything sensitive on screen. For Track 2 you also post on X tagging **@Cerebras
+ @googlegemma** and win on **organic impressions**.

## True apples-to-apples WSE vs GPU (the most defensible speed claim)

`gemma-4-31b` (the *exact* hackathon model) is also served on **GPU** backends — DeepInfra ($0.07/$0.34),
OpenRouter (incl. a free tier `google/gemma-4-31b-it:free`), Together, Fireworks. So you can run the **same
model on both** and the delta *is* the hardware: Cerebras ~1,500–1,850 tok/s vs GPU ~75–200 tok/s (Artificial
Analysis) = ~10–25×. Far stronger than Gemma-vs-Gemini (which conflates model + hardware).
- Cited published WSE-vs-GPU: **Llama-4-Maverick 2,522 vs 1,038 (Blackwell B200)**, **GPT-OSS-120B 2,700 vs
  900**, **Llama-3.1-405B 969 vs ~50**. TTFT: WSE wins (SRAM < HBM latency), consistent across batch sizes.
- **Honesty (judges will probe):** WSE wins on tok/s + TTFT + end-to-end latency **at low batch** — the
  real-time-agent regime. GPUs win on **energy-per-token and cost at scale** (CS-2 ~250 tok/s/kW vs GPU ~607;
  H100 cheaper $/token at batch 8+). Claim the speed/latency win; don't claim energy/cost.

## The side-by-side latency race (your money shot — for ALL tracks)

- **Cerebras framing is two metrics:** *output tokens/sec* (a tall Cerebras bar over the GPU bar) **and**
  *end-to-end response time* (Cerebras tiny vs everyone). Mirror that structure.
- **Most credible = literal split-screen**, same prompt, two panes, **wall-clock + tok/s visible**, let
  the Cerebras side **finish while the other is still streaming.** You may use **Gemini** as the slow
  baseline (allowed); Gemma-4-on-Cerebras stays primary.
- **Race a LOOP, not one call.** The visceral win is N iterations / N parallel agents / a verify-retry
  finishing in the time the baseline does *one*. That makes "200× memory bandwidth" *felt*, not explained.
- **Expose real `time_info`/tok/s on screen** — to Cerebras engineers a live counter reads as credible.
- ⚠️ **Pre-record it.** Network round-trip can dwarf inference on bad wifi; don't let the hero shot ride
  on live judging wifi. Keep reasoning **off** for the speed shot unless the task needs it.

## ≤60s video anatomy (payoff-first)

1. **0–2s HOOK (result first, on-screen text, sound-off safe):** the single most impressive frame +
   a provocation. Not "here's our project." Instead: *"GPU on the left. Cerebras on the right. Watch the
   right side finish thinking before the left finishes loading."*
2. **2–10s STAKES:** one line of what it does in the real world ("It's watching my desk and reacting in
   real time").
3. **10–35s SPEED-REVEAL:** the split-screen race with the live counter — the highest-leverage 5 seconds.
4. **35–52s "IT'S REAL" BEAT:** the loop acting on something physical — hold an object to the camera and
   it responds *before you finish*, a light flips, the agent calls your next step early.
5. **52–60s PAYOFF LINE + soft CTA:** "Gemma-4 on Cerebras. The brain runs faster than the world moves."

## X/Twitter mechanics (2026) — what actually drives organic reach

- **First 30 minutes of engagement velocity** decides amplification (~10+ engagements triggers the boost).
  Line up the team + friendly accounts to reply/quote immediately.
- **Replies are weighted ~27× more than likes** → the **caption must provoke a reply**, not admiration.
  End with reply-bait: *"What would you point this at?"* / *"GPU users — how long do your agent loops take?"*
- **First 0–3 seconds decide watch-through** → lead with the payoff, never the setup.
- **Sound-off by default** → bold high-contrast captions/overlays (can lift completion ~40%).
- **Native upload** (video into X, not a YouTube link) gets far more reach.
- **Post weekday US morning (~9–11am ET)** to ride the AI-Twitter waking window. Reply to every early
  comment yourselves.
- Tags (@Cerebras, @googlegemma) + 1–2 hashtags go in the **post**, not burned into the video.

## 4 shareable concepts, ranked purely for impressions

- **A. "The Latency Race"** (highest EV) — split-screen, identical task, stopwatch + tok/s, Cerebras
  finishes while the GPU still loads. Universally legible, screenshot-able, debate-baiting. Your money
  shot regardless of build.
- **B. "It reacts before I finish."** — webcam watches a physical task; the agent calls the next step
  *before* you complete the current one. The eerie "it's ahead of me" feeling sells real-time as visceral.
- **C. "I gave AI eyes and one second to think."** — POV phone walking a real space, instant narration /
  state-tracking overlay, hard cut each time it nails something. Kinetic, sound-off friendly.
- **D. "Three AIs arguing in real time"** — three Gemma-4 agents debate a decision live, text flying at
  1,500 tok/s, "impossible at GPU speed." Ties to Track-1 multi-agent; very screenshot-able.

## Discord submission (per track, separate post)

Lead with the 60s video, then: one-line category+wedge (no metaphor-only descriptions), the speed number
(15× / ~1,500 tok/s), the architecture one-liner (orchestrator + fresh-context sub-agents + verifier;
"effective context 200K→25M"), and a link to `docs/ARCHITECTURE.md`. Track 2 also goes to X.
