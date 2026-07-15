# Glossary — standardized vocabulary

One lexicon so Origin Physical AI talks about safety consistently. Grouped by theme.

## Core framing
- **Stateless / deterministic / bounded** — traditional software. **Stateful / probabilistic / unbounded** —
  agentic systems. The shift that justifies a new safety stack.
- **Secure agents as complete systems** — gate actions and decision chains, not just prompt text.
- **Delegated authority** — the credentials/permissions an agent acts under; the credential-broker's domain.
- **Operational infrastructure** — what agents become at scale → require security/governance/oversight.
- **Discover → Monitor → Govern** — the end-to-end control triad.
- **Guardian Agent** — an AI agent that supervises other AI agents, monitoring/blocking risky actions and
  enforcing policy across platforms (Gartner category).

## Enforcement levels & layers
- **Prompt / Action / MCP-tool / Skill level** — the four enforcement layers.
- **Pre-action gate** — intercept *before* the actuator/tool fires (vs. post-generation filter).
- **Blue side** — defense/observability/enforcement. **Red side** — offense/red-teaming/validation.
- **Principled-level defense** (policy/constitution layer) vs. **nuanced-level analysis** (dynamic-proof layer).

## Alignment & its failure modes
- **Shallow alignment** — refusal front-loaded at turn start / on shallow knowledge / against blacklist strings.
- **Any-depth / depth-invariant alignment** — safety re-asserted at arbitrary generation depth.
- **Safety Tokens** — assistant-header tokens whose hidden states carry a linearly-separable harmfulness signal;
  act as aggregators; enable the "model as its own guardrail" linear probe.
- **Exaggerated safety / over-refusal / over-conservatism** — blocking benign requests; a first-class failure
  mode (erodes trust → bypass → blind spots).
- **Ripple effect / trustworthiness bottleneck** — improving one trust dimension cascades onto others.
- **Alignment co-scaling** — safety only improves with model size when alignment scales *with* knowledge.

## Threats & attacks
- **Direct vs. Indirect threat model** — malicious user vs. benign-user-plus-external-injector.
- **Prompt / Tool / Skill / Environment injection** — the injection surfaces.
- **Indirect prompt injection** — instructions hidden in retrieved/perceived content.
- **Deep-prefill attack** — long harmful assistant prefill that defeats front-loaded refusals.
- **Code substitution** — semantics-preserving rewrite that bypasses blacklists.
- **Memory poisoning / backdoor / specification gaming** — persistence-layer corruption / triggered behavior /
  literal-objective-vs-intent gaming.
- **Visual reasoning hijacking** — multimodal trigger backdoor, many-shot mixup, simulated function-call.
- **Simulated function-call** — a fabricated tool injected so the model "executes" it → unauthorized actuation.
- **Cross-agent collusion** — compromised agents coordinate so each step looks benign.
- **Compromise budget `k`** — how many credentials/agents a single compromise can wield.
- **Mode collapse** — red-teamer reusing a few templates (defeated by memory + ε-greedy + diversity score).

## Metrics & judging
- **ASR** (Attack Success Rate), **RR** (Rejection Rate), **PVR** (Policy Violation Rate).
- **Guard Score** — Virtue AI's headline guardrail quality metric (plotted vs. latency).
- **Verifiable Attack Judge** — deterministic, rule-based outcome check against environment state.
- **LLM-as-Judge with policy spec** — judging grounded in an explicit policy rubric (human-validated).
- **Task Pass/Fail × Attack Pass/Fail** — orthogonal evaluation axes.
- **Reject / Execution-Failure / Attack-Success** — the 3-way effect-based outcome.
- **Trajectory length** — # tool calls; efficiency/stealth proxy.
- **Diversity score** — `1 − cos(embed(x), embed(y))`; resists mode collapse.
- **Group-based reward entropy** — selects "feasible-yet-challenging" tasks (max info gain).

## Architecture nouns
- **Autonomy trace / agent action trajectory** — the ordered, contextual record of an agent's actions.
- **Continuous operational record** — host + user + tool-call sequence kept as auditable evidence.
- **Behavioral-sequence reasoning** — reasoning over how actions connect (vs. signature matching).
- **Constitution** — a red-team-distilled, human-readable normative rule used to guide detection.
- **Credential broker** — gates/logs/policy-checks every capability; caps blast radius; least privilege.
- **Dream-environment / reasoning experience model** — abstract-textual world-model surrogate for safe dry-runs.
- **Sim-to-real (S2R)** — train in synthetic env, warm-start with a little real RL.
- **Policy Lab / Policy Group / Guard** — policy refinement engine / grouping / individual enforcement unit.
- **Regulation-grounded / policy-grounded** — harm definitions anchored in authoritative external standards.
- **Agent-level Shapley value / interaction index** — marginal robustness contribution / synergy of a coalition.

## Agent identity & credential access (see `agent-identity.md`)
- **Machine identity** — a credential authenticating a non-human actor (service/workload/agent) via keys/tokens/
  certs, not password+MFA. Governing *the entity* = **machine identity management**.
- **Secrets management** — securing *the credential/means* (vs governing the entity). A runtime answer needs both.
- **Standing access / standing credential** — access that exists before it's needed and persists after; the root
  enabler of most breaches. "A credential that persists is already compromised."
- **Blast radius** — everything a leaked credential could reach (≡ MASTRIKE's *compromise budget*).
- **Just-enough-privilege (JEP)** — scope a grant to a specific action/resource (write one bucket, not `s3:*`).
- **Just-in-time (JIT)** — grant only on request, expire after a short fixed window.
- **Zero Standing Privilege (ZSP)** — JEP + JIT: default-deny; narrow, short-lived authority only when justified.
- **Attestation** — a workload *proving what it is* (where it runs, who initiated it) so an issuer binds it to an
  identity automatically/in real time; each fresh attestation re-derives access.
- **Bearer model** — possession of a secret = authority (anything copying it inherits it); why long-lived keys are
  dangerous.
- **Federated model** — agent proves what it is → policy validates → short-lived task-specific credential issued.
- **Secretless access** — the verified identity *is* the credential (no stored secret).
- **Workload Identity Federation (WIF) / OIDC** — the deployed federated-model standard (GitHub Actions/AWS/GCP/
  Azure).
- **Trusted issuer** — the authority whose signature a relying party verifies; "no trusted identity without a
  trusted issuer."
- **Delegate vs principal** — an agent is a *delegate*: its own identity (attribution) acting under a human's
  delegated authority (accountability).
- **Attenuated (sub-)delegation** — agent A grants agent B a *strictly narrower* subset; an N-hop action still
  attributes to the original human. ("The least-solved problem.")
- **Intent-based access / intent-conformance** — bind a grant to a task's declared purpose; revoke when behavior
  diverges. The bridge between credential access and behavioral monitoring.
- **Execution control** (vs governance intent) — actually *enforcing* and *logging* runtime identity, not just
  having a policy. "The gap is not governance intent but execution control."
- **Separate trust domains** — code-gen vs prod-action are different blast radii; don't share a credential scope.
- **Credential Broker (1Password)** — validates a signed OIDC token against a trust policy, releases *one* short-
  lived credential with full attribution. **Apono** — governs what the verified identity may then *do* (JIT, time-
  bound, intent-scoped). Broker = govern the credential; Apono = govern the action.
