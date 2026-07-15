# The Virtue AI Worldview

The conceptual foundation. Every design decision in the Origin Physical AI safety stack should be traceable to
one of these claims.

## 1. The ontological shift (the single most reusable framing)

> Traditional software is **stateless, deterministic, and bounded.**
> Agentic systems are **stateful, probabilistic, and unbounded.**

This contrast (Virtue AI's NIST CAISI comment) drives everything. Because agents carry memory, behave
probabilistically, and can take unbounded real-world actions, you cannot secure them with the static, signature-
based, input/output-level tools built for traditional software (EDR/XDR treat an agent like a generic app).

## 2. Secure agents as complete systems, not at the prompt layer

Risk is no longer "what the model *says*" but "what the model and agents *do*." Guardrails must operate on
**actions, tool calls, and the full decision chain**, not just input/output text. The canonical risk surface to
instrument:

- Tool use & API integrations
- Persistent memory
- Orchestration layers
- Deployment environments
- Multi-agent communication
- **Runtime behavior + delegated authority** ← a credential broker lives here

## 3. The four enforcement levels

A guardrail product is **distinct layers**, not one monolithic filter:

| Level | What it governs | Virtue AI component |
|-------|-----------------|---------------------|
| **Prompt** | Inputs/outputs, jailbreaks, toxicity | PolicyGuard (input/output) |
| **Action** | Tool calls / function calls before they fire | ActionGuard |
| **MCP / Tool** | MCP servers & tool source for hidden injections, leak paths | MCPGuard |
| **Skill** | Agent skills / capabilities | (skill-level scanning) |

For **physical/embodied AI, the action level is primary** — actuation must be gated *before the actuator fires*,
not filtered after generation.

## 4. The Blue / Red two-sided model

Defense is meaningless without continuous offense.

- **AgentSuite-Blue** — runtime security, governance, observability (Shadow AI discovery, ActionGuard, MCPGuard,
  PolicyGuard).
- **AgentSuite-Red / VirtueRed** — automated, adaptive red-teaming + validation (Agent ForgingGround, the
  RedCodeAgent / ARMs / MASTRIKE research line).

A credible safety product **validates its own guardrails by red-teaming them continuously** — before, during, and
after deployment, integrated into CI/CD.

## 5. The discover → monitor → govern triad

Virtue AI's unifying market message (across all three Gartner recognitions): *human oversight alone cannot keep
pace as agents become operational infrastructure; you need AI-native controls to* **discover, monitor, and
govern** *agents end-to-end.*

- **Discover** — "you can't govern what you can't see." Inventory every agent, device, and behavior at the
  system/endpoint level, without relying on domain allowlists. (Shadow AI.) This is the **autonomy trace**
  foundation.
- **Monitor** — reason over *ordered, contextual action trajectories* (how actions connect), not isolated
  signature matches. Maintain a **continuous operational record** so every flag is auditable evidence.
- **Govern** — enforce policy on the decision chain at runtime, with cited explanations, mapped to regulation.

## 6. "Alignment is shallow" — the empirical drumbeat

The defensive case rests on five independent demonstrations that model-internal alignment is brittle, so an
**external** guardrail is mandatory:

- **Shallow at depth** (Any-Depth Alignment, 2510.18081): models refuse at the *start* of a turn but collapse
  once a harmful continuation is underway; deep-prefill attacks (thousands of tokens) hit ~100% ASR on base
  models.
- **Shallow on knowledge** (SoSBench, 2505.21605): models refuse low-knowledge prompts ("how to build a bomb")
  but disclose expert-level scientific hazards at high rates (Deepseek-R1 PVR 0.849).
- **Shallow against rewrites** (RedCodeAgent, 2510.02609): semantics-preserving **code substitution**
  (`os.remove` → `pathlib.Path.unlink`) trivially defeats blacklist guardrails.
- **Shallow across modality** (ARMs, 2510.02677): even constitutionally-aligned Claude-4-Sonnet hits >90% ASR
  under multimodal attack patterns.
- **Erased by fine-tuning** (SoSBench + Any-Depth): domain fine-tuning erodes alignment (BioMistral PVR 0.915);
  surface alignment is wiped by SFT — but a depth-invariant external probe survives.

Corollary themes:
- **Reasoning/CoT is a liability**: visible-thinking models leak more harmful content → monitor the trajectory,
  not just the output.
- **Scaling isn't uniformly safer**: safety only improves with size when alignment *co-scales* with knowledge.
- **Integrate internal + external protection** (TrustGen §10.6): weak/adjustable internal alignment + a fast,
  depth-invariant, operator-controlled external monitor. Any-Depth Alignment dissolves the boundary — the model
  becomes *its own* external guardrail via a linear probe on "Safety Token" activations.

## 7. Precision is the dominant enterprise metric

False positives are the real failure mode: **over-blocking → alert fatigue → operators bypass the tool → blind
spots.** A noisy guardrail gets ignored; an incomplete one lets harm through — either way you lose coverage.
- VirtueGuard-Code optimizes precision (0.896 vs ~0.66 for general models) because false positives slow CI/CD and
  destroy credibility.
- Any-Depth Alignment's headline is near-100% safety **with near-zero over-refusal**.
- "Exaggerated safety" (over-refusal of benign queries) is a first-class measured failure mode (TrustGen).
- **Prove before you veto**: BlueCodeAgent and RedCodeAgent both validate a flagged risk by *executing it in a
  sandbox* before deciding — so the guardrail blocks real risks, not plausible-looking-but-safe ones.

## 8. Specialized > bigger for security

"Your AI can write code. It can't secure it." AI security is a **dedicated discipline / specialized layer**, not
an emergent property of general intelligence. Small, purpose-built security models give lower latency, easier
deployment, and predictable performance under load — essential for **inline runtime enforcement** and CI/CD.
(VirtueGuard-Code, a fraction of frontier size, ranks #1 in F1.)

## 9. Static evaluation is dead; dynamic/adaptive is the standard

Static benchmarks get contaminated and stale; manual jailbreaks get patched. The field has moved to:
- **Dynamic test generation** that regenerates/varies cases to resist contamination (TrustGen Contextual
  Variator; SoSBench evolutionary synthesis).
- **Autonomous red-team agents** with memory + exploration that adapt per-target (RedCodeAgent, ARMs, MASTRIKE).
- **Deterministic verifiable judges** that check *environment state / actual effect*, yielding reproducible,
  replayable results (Agent ForgingGround's Verifiable Attack Judge; RedCodeAgent's sandbox; MABENCH).

A runtime guardrail should likewise **vary its own checks** to resist evasion, and judge by *effect*, not string.

## 10. Compliance is a mapping layer, not a workstream

One enforcement layer should map to 30+ overlapping frameworks (EU AI Act, GDPR, NIST AI RMF, OWASP
LLM/Agentic/MCP Top 10, MITRE ATLAS, ISO/IEC 42001, HIPAA, FINRA, …) so it's **audit-ready by default**. Ground
*harm definitions* in authoritative external standards (regulation-grounded), not ad-hoc labels. See
`regulations.md`.
