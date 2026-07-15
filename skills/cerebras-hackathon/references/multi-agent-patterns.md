# Multi-agent + verifier patterns (the Track-1 answer key)

Cerebras' own post *"Lessons learned from building multi-agent workflows"* is effectively the rubric
for Track 1. Use their vocabulary — the judges recognize it. The companion post *"Never Loop Without
Verifiers"* is the centerpiece pattern. **Fast inference is what makes all of this work**: at ~100 tok/s
verify-loops and fan-out are too slow to keep a human/agent in the loop; at ~1,500 tok/s they're cheap.

## The backbone: Orchestrator + Sub-agents ("Head Chef + Line Cooks")

| | Orchestrator | Sub-agent |
|---|---|---|
| Role | Plan, decompose, coordinate | Execute ONE scoped task |
| Tools | `delegate_task` **only** | Read/write, MCPs, anything |
| Context | High-level goals + **summaries** of sub-agent outputs | ONLY its own prompt + a **fresh window** (no history) |

The human talks **only** to the orchestrator. Each sub-agent gets a fresh, tiny context and returns a
**summary**, so the orchestrator never holds raw files/tool-results. Net: effective context goes from
~200K to **25M+**. **This is exactly how you survive the 5K MSL cap** — keep every Gemma-4 call tiny
and isolated. (Quote the "200K → 25M" line to judges; it turns the tight context limit into your
architecture story.)

## The 5 patterns (start at the top; work down only as needed)

1. **Prep Line** — parallel, *independent*. N workers each produce a variation of the same brief;
   orchestrator/human cherry-picks. Easiest (no file conflicts). 5 generations ≈ 1 min vs 5 min (**5×**).
   Great for design/copy/option exploration; "injects taste."
2. **Dinner Rush** — swarm, parallel, *distinct* tasks toward one goal. Hard rule: **tasks must NOT
   share files.** The moment two need the same file → use another pattern.
3. **Courses in Sequence** — phased "waves"; each wave depends on the prior, within-wave runs parallel.
   For big rebuilds/refactors. Needs a dependency tree.
4. **Prep-to-Plate Assembly** — sequential pipeline; each step is bounded, validates, hands the
   workpiece on. **State lives in files/task-queues, NOT conversation history** → survives restarts.
5. **Gordon Ramsay / Verifier** — *a discipline you layer on ALL of the above, always.* Separate the
   **builder** (one at a time, writes) from the **verifiers** (run in parallel: a code/logic reviewer +
   a visual/functional tester). If either flags, the builder gets another pass.

## The verifier loop (your likely centerpiece)

From *"Never Loop Without Verifiers."* The anatomy of one cycle:

1. **Define a concrete end-state** — be specific about what "done" means.
2. **Validate against reality** — *render the artifact and look at it* (vision), compare to target on
   explicit axes (shape, proportions, features, symmetry, spacing…).
3. **Turn failures into the next prompt** — the loop **rewrites its own instructions** from what it saw.
4. **Have a validation environment** — render → screenshot → re-feed.
5. **Make progress inspectable** — log loop #, the prompt used, the screenshot, the comparison, the
   change. (This inspectable trail *is* your "autonomy-trace" panel and your Track-3 production-readiness.)

Why it's possible now: agents finally have **Eyes** (multimodal — inspect their own output instead of
guessing via text), **Hands** (tools), **Memory** (context), **Brain** (reasoning). The flagship demo:
a photo of a dumbbell → a printable STEP file, self-corrected over **~5 iterations at ~1.2 s each, no
human in the loop.** Gemma-4 vision + Cerebras speed is built exactly for this.

Verifier prompt hygiene (steal verbatim):
- "The full suite must still pass / do not modify test files / fix the root cause / stop when green
  with zero edits to tests."
- "Never declare success from a pending capture or from metadata alone / never leave blank output."
- "Do not give me narrative progress logs — only report validated results." (Forces evidence-based done.)

## Proof points that sell the pitch (cite these)

- Figma site-copy task: single-agent = **36.5 min/run, 12 interventions, 100% failure**;
  multi-agent = **5.2 min, 2 interventions, first-try success.**
- Sequential verifier loop **reduced manual interventions by 84.3%.**
- 5 parallel generations ≈ 1 min vs 5 min sequential (**5×**).
- "Near-instant coding models make adding verification **practically free**." ← the whole thesis.

## Failure modes (catalog for judge Q&A — DeepMind judges probe these)

- **Spiralling** — no end-state → "improves" forever, burns tokens. Fix: a verifiable end-state.
- **Cheating** — does what you said, not what you meant (e.g., deletes the failing test, trains on the
  eval). Fix: be *annoyingly specific* about "done" + forbid the shortcuts; mark eval sets "radioactive."
- **Context bloat / compaction drift** — Figma saw a single viewport eat 64–128K tokens; the agent
  compacted and drifted off-goal after ~100K. Fix: fresh-window sub-agents + state-in-files (and your
  5K MSL cap forces this anyway).
- **Wrong-tool fallback** — agent improvises a hacky path instead of the real tool. Fix: tight tool
  scoping + skills/guides.
- **Shared-file collisions** in swarms. Fix: each worker owns a disjoint file set.

## How to instantiate for the hackathon (3 agents, max)

- **Perceiver** — Gemma-4 vision over a frame/screenshot → strict JSON `{objects, state, anomaly,
  next_step}`. Reasoning **off** (fast path).
- **Planner/Actor** — takes the perception, decides the action/answer → strict JSON `{action, args,
  rationale}`.
- **Guardian/Verifier** — independently checks the plan against the goal + policy → strict JSON
  `{pass: bool, reason, fix_prompt}`. On fail, its `fix_prompt` becomes the next loop's input.
  Escalate `reasoning_effort="low"` here only when it's uncertain.

Keep outputs terse, state in files, and show the loop iterating on screen with the tok/s counter.
