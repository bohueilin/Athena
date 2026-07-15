# Architecture Patterns for Origin Physical AI

The build playbook. Each pattern is a reusable design primitive extracted from the corpus, with its source and
its concrete application to a Guardian Agent / autonomy trace console / credential broker for embodied AI.

## P1 — Pre-action safety gate (intercept before the actuator fires)
**Source:** Any-Depth Alignment (2510.18081); RedCodeAgent sandbox.
Halt *during* generation / *before* execution, not after. Any-Depth Alignment explicitly suggests inserting a
"Safety Token" check immediately before a tool/action is executed. For embodied AI this is the **kill-switch
before the motor command**. Two cheap implementations:
- **Linear probe (ADA-LP)** — a lightweight classifier on injected Safety-Token hidden states; single forward
  pass, ~25 ms, 2–3 MB, KV-cache reuse → *constant time* regardless of trajectory length (vs. external guardrails
  whose latency/memory grow linearly: ~500 ms / 938 MB at 10K tokens). Critical for long-horizon embodied
  trajectories.
- **Rethinking (ADA-RK)** — fork the stream, inject the assistant header, generate a short lookahead; if a
  refusal appears, halt.
The model becomes *its own* guardrail; survives subsequent fine-tuning where surface alignment is erased.

## P2 — Effect/execution-based evaluation (judge what actually happens)
**Source:** RedCodeAgent (2510.02609); BlueCodeAgent (2510.18131); Agent ForgingGround Verifiable Attack Judge.
Never gate on string/API-name matching — it falls to semantics-preserving substitution. Instead:
- Run the planned action in a **sandbox / isolated Docker / dry-run** and classify the *outcome* against
  environment state: **Reject / Execution-Failure / Attack-Success** (or Task✓/✗ × Attack✓/✗).
- The judge should be **deterministic and rule-based** where possible → reproducible, replayable, benchmarkable.
For physical AI, the "sandbox" is a **simulation / digital twin / dream-environment** (see P3): predict the
consequence of an actuator command before it touches the real world. **Prove a risk before vetoing it** — this is
how you avoid over-conservatism (P8).

## P3 — Dream-environment / experience-model dry-run
**Source:** DreamGym (2511.03773).
A **reasoning-based experience model** predicts `(next_state, reward)` in an *abstract textual state space* via
chain-of-thought, conditioned on history + retrieved past experiences — a token-efficient world-model surrogate.
Motivation is explicitly *safety*: avoid **irreversible real-world actions** and the lack of a **reliable reset
mechanism** — the embodied-AI safety case. Uses:
- Predict the effect of a tool/actuator call *before* executing it (consequence preview for P2).
- Red-team an agent's policy in synthetic space with **zero physical risk**, then sim-to-real warm-start.
- The abstract textual state + CoT rationale per step is a natural feed for the **autonomy trace console** (human-
  readable predicted states).

## P4 — Constitution distillation (red-team findings → auditable rules)
**Source:** BlueCodeAgent (2510.18131); Constitutional AI lineage; Guardset-X.
Convert discovered attacks into human-readable, retrievable **constitutions** (normative rules). At runtime,
retrieve top-k similar constitutions for the current input and use them to guide a context-aware decision. This
operationalizes abstract concepts ("what is a malicious / biased / unsafe instruction") that a bare safety prompt
can't. Two tiers:
- **Principled-level defense** — retrieve + summarize constitutions (the policy layer).
- **Nuanced-level analysis** — dynamic sandbox validation fused with the constitution (the proof layer, P2).
Constitutions are exactly the **auditable, explainable policy** an autonomy trace console should surface.

## P5 — Trajectory-level (not step-level) monitoring
**Source:** MASTRIKE (2510→2606.12918); DevOps-Gym (2601.20882); Shadow AI.
The hard, valuable competency is reasoning over **whole multi-stage, multi-agent execution traces**, because:
- Collusive attacks distribute themselves so each step looks individually benign (MASTRIKE) → only
  trajectory-level + **cross-agent consistency checks** catch them.
- End-to-end multi-stage pipelines fail at *context propagation* — partial completion has no value (DevOps-Gym:
  0% end-to-end), a safety-critical property for physical pipelines.
Maintain a **continuous operational record**: ordered, contextual sequence of process/network/file/tool actions
with host + user context, reasoned over for *how actions connect* (behavioral-sequence reasoning), not signature
matching. **This is the literal "autonomy trace."**

## P6 — Least-privilege credential broker
**Source:** MASTRIKE compromise-budget `k`; TrustGen §10.6 (principle of least privilege); the "delegated
authority" risk surface.
- Broker every tool/capability as a **gated, swappable, logged, policy-checked service** (MCP-wrapped — ARMs and
  MABENCH both wrap tools/attacks as MCP servers; mirrors a broker architecture).
- **Cap the blast radius** of any single compromise (bound `k` — how many credentials one compromise can wield).
- Detect **coordinated cross-credential misuse**, not just isolated abuse.
- Use **Shapley attribution** (P7) to decide *where* to place the strongest checks and tightest privileges.
- **The full theory of this pattern is in `agent-identity.md`:** Zero Standing Privilege (just-enough + just-in-
  time), prove authority at runtime via **attestation/federation** (not stored bearer secrets), **secretless**
  access (WIF/OIDC), agent-as-delegate (own identity + delegated authority + attribution), **separate trust
  domains**, **intent-based access** (revoke on divergence from declared purpose), and **attenuated delegation
  chains**. Maps to the 1Password Credential Broker (govern the credential) + Apono (govern the action).

## P7 — Shapley-based risk attribution
**Source:** MASTRIKE (2606.12918).
Quantify each agent's/credential's **marginal contribution to degrading system robustness** (agent-level Shapley
value), plus the **pairwise interaction index** for *synergistic collusion* (when compromising two together
exceeds the sum). Findings: contributions are **sparse and task-dependent** — only a few agents matter and which
ones varies by task; high individual importance ≠ high coalition synergy. Use to prioritize where to harden,
rather than blanket-blocking everything.

## P8 — Optimize the precision/recall frontier (anti-over-blocking)
**Source:** VirtueGuard-Code; Any-Depth Alignment; BlueCodeAgent; TrustGen (exaggerated safety).
Over-blocking erodes operator trust until the tool is bypassed (→ blind spots). Tactics:
- **Prove before you veto** (P2 dynamic validation suppresses false positives — BlueCodeAgent: FP 54→42).
- Measure **exaggerated safety / over-refusal** as a first-class metric, alongside recall.
- Prefer **specialized small models** (P9) for predictable high-precision inline decisions.
- Track F1 / Precision / Recall / FPR / Accuracy per guard and per policy group (PolicyGuard dashboard model).

## P9 — Specialized small security models inline
**Source:** VirtueGuard-Code; PolicyGuard's lightweight runtime model.
Purpose-built, small models for the inline path → low latency, predictable under load, easy edge deployment.
Reserve large models for offline red-teaming / judging. Evaluate the runtime path in **its original language**
(no translation blind spots — PolicyGuard).

## P10 — Async zero-latency explainability
**Source:** PolicyGuard.
Every allow/block decision ships with a detailed rationale — *which policy, which regulation, why* — generated
**asynchronously so it adds zero latency** to the decision. Write it to the trace. The dashboard is the **single
source of truth**: queries, violations, policy groups, users, API keys, latency.

## P11 — Dynamic, contamination-resistant checks
**Source:** TrustGen (Metadata Curator / Test Case Builder / Contextual Variator); SoSBench evolutionary
synthesis; ARMs ε-greedy diversity.
Don't ship a fixed checklist an adversary can memorize and evade. **Regenerate/vary** checks (paraphrase,
mutate) to neutralize prompt-sensitivity and resist contamination/evasion; use **memory + ε-greedy exploration +
a diversity score** to avoid mode collapse in the red-team.

## P12 — Continuous adaptive red-team in the loop (Red validates Blue)
**Source:** Agent ForgingGround / VirtueRed; RedCodeAgent; ARMs; MASTRIKE.
The defensive layer is only credible if an **automated, adaptive, memory-driven red-team** continuously attacks
it — before/during/after deployment, CI/CD-integrated, grounded in real regulations, with a deterministic
verifiable judge. Reusable red-team template: **LLM agent + retrieval memory (penalty-weighted toward short
attacks) + tool/strategy library + sandbox-or-judge feedback + structured failure diagnosis.** Generate
adversarial scenarios from a *policy/regulation* (policy-based) as well as from datasets (instance-based).

## P13 — Discovery before enforcement
**Source:** Shadow AI.
"You can't govern what you can't see." Before any enforcement, build an **inventory** of every agent, the devices
it runs on, and its behavior — at the system/endpoint level, **without relying on domain allowlists** (works for
unknown/self-hosted endpoints). Surface "which agents, on how many devices, which policy triggered the flag,"
with the full action trajectory pullable on demand. This is the foundation the autonomy trace console sits on.

---

## Putting it together — a reference Origin safety loop

```
            ┌──────────────────────── RED (validate) ───────────────────────┐
            │  P12 adaptive red-team → P11 dynamic checks → P2 verifiable    │
            │  judge → feeds findings as P4 constitutions                    │
            └───────────────────────────────────────────────────────────────┘
                                       │ hardens
                                       ▼
 perceive → plan → [P1 pre-action gate] → [P3 dream-env dry-run → P2 effect check]
                          │ proof                         │
                          ▼                               ▼
              [P6 credential broker: least privilege,  [P10 async explanation]
               P7 Shapley-placed checks, cap blast k]      │
                          │                                ▼
                          └────────────► [P5 trajectory-level trace = autonomy console]
                                          P13 discovery underneath · P8 precision-tuned · P9 small inline model
```
Discover (P13) → Monitor (P5/P10) → Govern (P1/P2/P4/P6), validated by Red (P12), grounded in regulation.
