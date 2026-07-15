# Agent Threat Models

The catalog a Guardian Agent / autonomy trace console / credential broker must defend against, synthesized from
the corpus. Organize by *who* the adversary is, *where* injection enters, and *how* harm propagates.

## Threat-model axes

- **Direct threat model** — a *malicious user/operator* gives harmful instructions directly.
- **Indirect threat model** — a *benign user + external attacker* who injects via the environment, an MCP/tool,
  retrieved content, or perception. **Embodied agents perceive the world, so indirect attacks are first-class.**

Both span the three injection surfaces below (Agent ForgingGround framing):
**Environment Injection · MCP & Tool Injection · Prompt Injection.**

## The threat catalog

### Prompt-layer
- **Direct prompt injection** — adversarial instructions in the user prompt; jailbreaks (GCG, AutoDAN, PAIR, TAP,
  AmpleGCG, AdvPrompter).
- **Indirect prompt injection** — instructions hidden in retrieved docs, web pages, emails, tool outputs.
- **Deep-prefill attack** (Any-Depth Alignment) — a *new* threat: harmful assistant-side prefills from dozens to
  thousands of tokens (avg >3,500) push past front-loaded refusals; ~100% ASR on base models. Mitigation: re-
  assess at *any depth* (mid-stream Safety Tokens), not just at turn start.

### Tool / action / skill-layer
- **Tool abuse / misuse** — coaxing an agent to call a legitimate tool toward harmful effect.
- **Tool / skill injection** — malicious capability smuggled into the agent's toolset; "injection skills"
  (e.g., gmail-forwarding-abuse skill for data exfiltration).
- **MCP injection** — hidden prompt injections / vulnerabilities / data-leakage paths inside MCP servers & their
  source (scanned by MCPGuard).
- **Code substitution** (RedCodeAgent) — semantics-preserving rewrite (`os.remove` → `pathlib.Path.unlink`) that
  defeats blacklist guardrails. **Generalizes to any capability-gate, including a credential broker and physical
  actuation: gate the *effect*, not the API name.**
- **Unauthorized action / privilege escalation** — agent acts beyond its delegated authority.

### Environment / perception-layer (critical for embodied AI)
- **Environment injection / manipulation** — adversarial state planted in the operating environment.
- **Multimodal / perception attacks** (ARMs 5-pattern, 11-strategy taxonomy):
  - *Visual context cloaking* (hide harmful content in email/Slack/news/narrative images)
  - *Typographic transformation* (render prompt as flowchart / numbered-list image to dodge text filters)
  - *Visual multi-turn escalation* (crescendo, actor attack, acronym)
  - *Visual reasoning hijacking* — **multimodal trigger backdoor** (a malicious sign/sticker triggers behavior),
    **many-shot mixup**, **simulated function-call** (a fabricated tool injected so the model "executes" it →
    unauthorized actuation)
  - *Visual perturbation* (photographic distortion, jigsaw scramble, shuffling)
  - **Embodied mapping:** a sticker on a stop sign = trigger backdoor; a fake tool descriptor = simulated
    function-call → rogue actuation. A perception-driven robot guardrail must defend all five patterns.

### Memory / persistence-layer
- **Memory poisoning** — corrupting persistent memory / RAG so future decisions are compromised (BadAgent,
  AgentPoison target long-term memory/RAG).
- **Backdoor attacks** — implanted triggers that flip behavior on a cue (NIST-cited).
- **Specification gaming** — agent satisfies the literal objective while violating intent (NIST-cited).

### Multi-agent / system-layer
- **Cross-agent collusion** (MASTRIKE) — compromised agents *coordinate* to bypass distributed safety checks.
  Distributed attacks look individually benign → **step-level guardrails miss them; you must reason at the
  trajectory/system level with cross-agent consistency checks.**
- **Compromise budget `k`** — the threat model parameterizes how many agent credentials a single compromise can
  wield. **Maps directly to a credential broker: cap blast radius, detect coordinated misuse.** Attack success
  scales monotonically with `k`.
- **Agent-level Shapley attribution** — which agent/credential most degrades system robustness (sparse and
  task-dependent — only a few agents matter, and *which* ones varies by task). Use to place strongest checks /
  least privilege where they matter; high individual importance ≠ high coalition synergy.

## Outcome classes (what "success" means for the attacker)

For code/agents, **a refusal is not enough to call something safe, and a non-refusal isn't automatically
harmful** — judge by *effect*. RedCodeAgent's 3-way verdict is the model:

- **Rejection** — agent refused.
- **Execution Failure** — agent tried but the harmful effect didn't materialize.
- **Attack Success** — the harmful effect actually occurred (verified against environment state).

Agent ForgingGround separates two orthogonal axes: **Task Pass/Fail × Attack Pass/Fail** (a good guardrail = task
succeeds AND attack fails).

## Standard attack vocabulary
- **ASR** (Attack Success Rate), **RR** (Rejection Rate), **PVR** (Policy Violation Rate).
- **Trajectory length** — # tool calls; an efficiency/stealth proxy (shorter = stealthier).
- **Mode collapse** — red-teamer reusing a few templates; defeated by memory + ε-greedy exploration + a
  diversity score.
- **Adaptive / closed-loop red-teaming** — agent + retrieval memory + tool/strategy library + sandbox-or-judge
  feedback, refined by structured failure diagnosis.

## Risk-category catalogs (use to scope coverage)
- **VirtueRed policy domains:** Healthcare, Customer Service, CRM, E-Commerce, Finance, OS, File system, Legal,
  Telecom, Research, Travel, HR, Workflow, Coding, RecSys.
- **MABENCH (multi-agent) examples:** Finance (Card Service Tampering, Payment Manipulation, Account Access
  Hijacking, Contact Channel Hijacking), Engineering (Production Safety Bypass, Sensitive Data Exfiltration,
  Governance Workflow Subversion), CRM (Privacy/Consent Violation, Unauthorized Deal Approval, Financial Fraud).
- **Embodied benchmarks referenced (TrustGen §8.4, §9):** Agent-SafetyBench (349 envs, 8 risk categories, none
  >60% safe), SafeAgentBench (embodied, 750 tasks, 10 hazards — baselines reject only 5%), SafetyDetect (1,000
  anomalous home scenes), AutoTrust (L4 driving trust), V2X cooperative-perception trust.
