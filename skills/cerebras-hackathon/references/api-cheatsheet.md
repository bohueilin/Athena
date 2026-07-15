# Gemma-4 on Cerebras — API cheat-sheet & gotchas

Everything here is hackathon-specific. Where the public model page disagrees with the hackathon FAQ,
**the FAQ wins** (the public numbers do NOT apply during the event).

## Hard facts

- **Model ID:** `gemma-4-31b` (exact). Only Gemma-4 variant hosted. Dense (not MoE), Apache-2.0,
  Google DeepMind's open model. Intelligence Index ≈ **29** (ties Claude Haiku's 30) — a fast, capable
  *junior*, not a frontier reasoner. Treat it accordingly.
- **API:** standard Cerebras Inference, **OpenAI-compatible Chat Completions**, your existing key.
  Base URL `https://api.cerebras.ai/v1`. Use the OpenAI SDK pointed at it, or the `cerebras-cloud-sdk`.
- **Modality:** text + image **IN**, **text-only OUT**. No image generation, no audio, **no native
  video** (judging says "video" but you simulate it by sampling frames as images).
- **Speed:** **~1,500–1,850 tok/s** on Cerebras vs **~100 tok/s** for Claude Haiku = **~15×** at
  comparable quality. GPU baseline Cerebras always quotes: **50–100 tok/s.** Real anchor: the
  "Never Loop" CAD demo produced a full new STEP file in **~1.2 s per loop**.
- **Timing telemetry:** every response has `usage` (prompt/completion/total tokens) **and** a
  `time_info` object. Dedicated endpoints also expose Prometheus metrics (TTFT, TPOT, e2e latency,
  output tok/s, queue time). **Put `time_info` on screen.**

## Hackathon limits — the real ceiling

- **Context: 5K MSL (max sequence/prompt per request) / 32K MCL (max context).** This is the number
  that kills naive designs — NOT the public 65K/131K. Architect for small per-call contexts.
- **Rate: 100 RPM / 100K TPM** (elevated, per-participant; requires the capacity form). Free tier is
  5–30 RPM. Budget your fan-out against 100 RPM.

## Capabilities you SHOULD use

- ✅ **Structured Outputs** with `strict: true` (constrained decoding to a JSON schema). This is the
  backbone of reliable agent hand-offs — every agent returns a typed contract.
- ✅ **Tool Calling + Parallel Tool Calling** (also strict).
- ✅ **Streaming**, sampling controls, prompt caching.
- ✅ **Reasoning** via `reasoning_effort`: `none` (off, default) / `low` / `medium` / `high`.

## Gotchas (each has burned someone)

- ⚠️ **Predicted Outputs: NOT on Gemma-4** (only `gpt-oss-120b`, `zai-glm-4.7`). Don't design around it.
  At ~1,800 tok/s a full re-emit of a small artifact is already sub-second — you don't need it.
- ⚠️ **Multi-LoRA: private preview, dedicated-endpoint only** — not on shared hackathon keys. Get the
  "fleet of specialists off one base model" effect with **distinct system prompts per role** instead.
- ⚠️ **`reasoning_effort` low = medium = high on Gemma-4 today** (no graduated depth). Only
  `reasoning_format: "parsed"` (separate `reasoning` field) is supported — no `raw`/`hidden` CoT.
  Default is **off**; the economics paper says most steps don't need it — keep it off for speed,
  switch on only for the "escalate" path.
- ⚠️ **Images: Chat Completions endpoint only** (the `/completions` endpoint rejects images). PNG/JPEG,
  as `image_url` (base64 data URI guaranteed; hosted URLs per FAQ — verify live). **Max 5 images,
  10 MB total/request.** Each image ≈ **256–280 tokens** (capped; smaller images aren't always cheaper).
  Inspect `usage.prompt_tokens_details.image_tokens`. 5 images ≈ ~1,300 tokens before any text — against
  a 5K MSL ceiling.
- ⚠️ **Vision weak spots:** small/low-res text (enlarge first), rotated/upside-down content, charts
  (dashed-vs-solid, color-only differences), spatial localization/coordinates, exact counting,
  panoramic/fisheye, medical images, CAPTCHAs. Don't hinge a demo on these.
- ⚠️ **Image prompt-injection:** text inside an image enters the prompt and can hijack it
  ("ignore previous instructions"). Treat all transcribed image text as untrusted → also a strong
  Track-3 guardian demo.

## Minimal patterns

Text + image, structured output, with timing (Python, OpenAI-compatible):

```python
from openai import OpenAI
client = OpenAI(base_url="https://api.cerebras.ai/v1", api_key=CEREBRAS_API_KEY)

resp = client.chat.completions.create(
    model="gemma-4-31b",
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "Return the scene as JSON per the schema."},
            {"type": "image_url",
             "image_url": {"url": "data:image/jpeg;base64,<...>"}},  # or a hosted URL
        ],
    }],
    response_format={  # strict structured output = clean agent hand-off
        "type": "json_schema",
        "json_schema": {
            "name": "perception",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "objects":  {"type": "array", "items": {"type": "string"}},
                    "state":    {"type": "string"},
                    "next_step":{"type": "string"},
                },
                "required": ["objects", "state", "next_step"],
                "additionalProperties": False,
            },
        },
    },
    reasoning_effort="none",   # keep off for the fast path; "low" only to escalate
    temperature=0.2,
    max_tokens=300,            # terse outputs preserve the speed advantage
)
print(resp.choices[0].message.content)
print(resp.usage, getattr(resp, "time_info", None))   # tok/s + TTFT for the on-screen counter
```

The **side-by-side**: run the identical task against **Gemini** (`gemini-3.5-flash` or current) in a
second pane and race the wall-clocks. Gemma-4-on-Cerebras must remain the *primary* model.

## Pre-flight (first 30 minutes of the event)

1. Confirm the key serves `gemma-4-31b` **with an image in the message** (not just text).
2. Confirm base64 data-URI images work; test a hosted URL too.
3. Wire a **fallback** Cerebras model behind a flag (Llama/Qwen/Kimi) in case of a Gemma-4 key issue.
4. Sanity-check `time_info` is present so the on-screen counter is real, not faked.
