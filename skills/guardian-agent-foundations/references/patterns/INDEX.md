# Control Playbooks — INDEX

28 engineering control playbooks. Retrieve by defense token (`scripts/search.py defense <token>` for the *papers*; open the pattern here for the *build guidance*). Each pattern carries: threat model · control mechanism · correct-vs-fragile impl · verification · metrics/thresholds · adaptive tests · telemetry · known bypasses · residual risks · relevant paper ids · evidence strength · when NOT to use.

> **Maturity:** these are **research-grounded design guidance, not build-ready specs.** Several runtime controls carry transplanted/analogy figures and un-owned cross-pattern seams — see the Top-8 in `../final-quality-review.md` (#4–8) before lifting any page as a production spec.

| pattern | primary defense | problem addressed |
|---|---|---|
| [`adaptive-red-teaming`](adaptive-red-teaming.md) | `red_teaming` | A defense that passes its own evaluation is routinely broken the moment the attacker is allowed to see it |
| [`adversarial-training`](adversarial-training.md) | `adversarial_training` | Machine-learning components that an agent depends on — perception classifiers, CLIP/VLM encoders, |
| [`backdoor-detection`](backdoor-detection.md) | `detection` | An agent stack ingests third-party artifacts it does not control the provenance of: pre-trained weights, |
| [`content-provenance`](content-provenance.md) | `crypto_provenance` | A Guardian agent (or a governance layer, a downstream model, a human reviewer) ingests content it did not create — |
| [`context-and-memory-isolation`](context-and-memory-isolation.md) | `memory_isolation` | An agent's context window and persistent memory are treated as a single, uniformly-trusted surface, when they are |
| [`deepfake-detection`](deepfake-detection.md) | `detection` | A consumer — a Guardian agent, a governance layer, a content-moderation pipeline, an identity/authentication |
| [`differential-privacy`](differential-privacy.md) | `differential_privacy` | Any artifact a system **derives from sensitive records and then releases** — a trained model, a fine-tuned |
| [`evaluation-holdout-protection`](evaluation-holdout-protection.md) | `holdout` | A Guardian / autonomy-trace stack makes go/no-go decisions from **measurements**: a safety benchmark score, a |
| [`human-approval-consequential-actions`](human-approval-consequential-actions.md) | `human_approval` | Autonomous LLM/agent systems reach a point in their cognitive cycle where they can *execute* an action with real, |
| [`incident-containment`](incident-containment.md) | `incident_containment` | Preventive controls and detectors reduce but never eliminate incidents: injection lands, a peer agent is |
| [`input-output-detection`](input-output-detection.md) | `detection` | A model cannot be trusted to police its own inputs and outputs, so deployments bolt on **detectors**: input-side |
| [`kill-switches`](kill-switches.md) | `kill_switch` | An autonomous LLM/agent can enter a state where continued execution causes escalating, often irreversible, |
| [`least-privilege-credentials`](least-privilege-credentials.md) | `least_privilege` | A capable agent holding a **standing, over-scoped credential** turns any single compromise — a prompt injection, |
| [`model-extraction-defenses`](model-extraction-defenses.md) | `query_monitoring` | A model deployed behind a query API is copyable |
| [`network-segmentation`](network-segmentation.md) | `least_privilege` | A flat network — where any agent, tool runtime, sub-agent, or service can reach any other host and any egress |
| [`policy-permission-gates`](policy-permission-gates.md) | `policy_gating` | An LLM agent that *can* invoke a tool, actuator, database, or MCP server will invoke it whenever its |
| [`privacy-preserving-inference`](privacy-preserving-inference.md) | `trusted_execution` | An agent must run inference over **sensitive input** — a user's prompt (PHI, financial intent), an uploaded image |
| [`privacy-preserving-training`](privacy-preserving-training.md) | `differential_privacy` | A model that trains or fine-tunes on sensitive data becomes a **leakage vector for that data** — through the |
| [`prompt-injection-containment`](prompt-injection-containment.md) | `input_filtering` | An LLM agent cannot, by construction, reliably tell an *instruction from its principal* apart from |
| [`retrieval-authorization`](retrieval-authorization.md) | `retrieval_isolation` | An LLM agent that can *retrieve* — from a RAG corpus, a vector store, long-term memory, a tool that returns |
| [`runtime-anomaly-detection`](runtime-anomaly-detection.md) | `runtime_monitoring` | An autonomous agent or ML pipeline emits behavior at runtime that departs from what it should do — because of |
| [`safe-rollback`](safe-rollback.md) | `rollback` | Autonomous LLM/agent and ML systems are compromised or silently degraded in ways that *no upstream control drives to |
| [`sandboxed-execution`](sandboxed-execution.md) | `sandboxing` | Agents that plan and act — generating code, invoking tools, driving a computer, or emitting actuator commands — |
| [`secure-logging`](secure-logging.md) | `evidence_logging` | An autonomy console, a policy gate, an incident review, and a compliance audit all depend on **logs and |
| [`signed-provenance`](signed-provenance.md) | `crypto_provenance` | A consumer — a Guardian agent, a governance layer, a downstream model, a court — needs to answer two questions |
| [`tamper-evident-traces`](tamper-evident-traces.md) | `tamper_evident_logs` | An autonomy console, a policy gate, and an incident review all depend on **a record of what the agent |
| [`tool-capability-isolation`](tool-capability-isolation.md) | `capability_isolation` | An LLM agent that can *reason about* invoking a tool is routinely allowed to *actually* invoke it with broad |
| [`watermarking-fingerprinting`](watermarking-fingerprinting.md) | `watermarking` | You need to establish *provenance* — to later prove that a model, a generated artifact, or a training |
