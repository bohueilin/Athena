# Pattern: Secure Logging

> **Scope of evidence.** This pattern is grounded in the AAAI-26 corpus syntheses `Network-Cyber-Security.md`
> and `Privacy-Protection.md` and their underlying research cards. Paper ids (e.g. `A42453`) are the stable
> corpus ids from those syntheses' source maps (§20 of each). Every recommendation traces to at least one card.
>
> **What this pattern owns, and what it delegates.** "Secure logging" here is the discipline of producing logs
> and telemetry that (a) **capture the security-relevant events completely and fail-closed**, while (b) **not
> themselves becoming a confidentiality liability, an injection vector, or an over-broad data store**. Its
> center of gravity is the **confidentiality, data-minimization, redaction, access/egress-control, and
> safe-re-ingestion** properties of the log. The *integrity / provenance / non-repudiation / tamper-evidence*
> of the record — hash-chaining, writer attestation, append-only WORM, external anchoring — is the sibling
> control `tamper-evident-traces.md`; the two **compose** (a log should be both un-fakeable *and* not a
> secret-leak), and this file references that boundary rather than restating it. Upstream siblings:
> `differential-privacy.md` (the ε/LDP accounting a privacy-preserving log emits and records),
> `context-and-memory-isolation.md` (a log re-read into a context window is memory ingress),
> `prompt-injection-containment.md` (sanitize-on-read), `retrieval-authorization.md` (read-authorization on the
> log store), `least-privilege-credentials.md` / `policy-permission-gates.md` (who may read/write the store),
> and `human-approval-consequential-actions.md` (the A40874 sensitive-action gate that also governs what a log
> is *allowed* to record about a user).
>
> **Evidence-integrity conventions (non-negotiable).** Numeric values are **author-reported** unless labeled
> *reviewer synthesis*, and are **not independently verified**; several cards flag truncated/OCR-approximate
> tables, recorded here as author-stated, not reviewer-verified. Where a card was silent the text says
> "not stated in paper". Calibrated language only — "reduces recoverable residue against the tested,
> non-adaptive attacks", "requires production validation", "not evaluated against" — never
> "secure/private/unrecoverable/proven-safe". Direct paper findings are distinguished from reviewer synthesis.
>
> **The load-bearing calibration for this pattern.** **No paper in either synthesis builds, deploys, or measures
> a "secure logging" system** (redaction pipeline, field-level minimization, egress-controlled log store, safe
> re-ingestion). What the corpus supplies is (1) the **threat motivation** — that the things a naive agent log
> captures (gradients, activations, smashed representations, soft prompts, steering vectors, embeddings,
> retrieved content, routing metadata, the decision sequence itself) are **adversarially recoverable secrets,
> not opaque tokens** (Privacy-Protection §6, §9); (2) the **unguarded assumption to remove** — the recurring
> *implicit* premise across the detector/telemetry papers is **trusted inputs, telemetry, and labels**
> (Network-Cyber-Security §3, reviewer synthesis); and (3) the **design principles** — minimize/decompose
> before storing, log the privacy dial as configuration-of-record, emit an auditable record per
> privacy-relevant operation, treat any re-ingested field as an injection surface, and keep raw private content
> off untrusted readers. Accordingly the confidentiality/minimization construction here is **standard security
> engineering that requires production validation on the target stack**, not a corpus-measured result. The
> single strongest cross-corpus caveat, repeated throughout: **near-universal absence of adaptive,
> defense-aware evaluation** — treat every efficacy number as an upper bound (lower bound on attack success).

---

## Problem addressed

An autonomy console, a policy gate, an incident review, and a compliance audit all depend on **logs and
telemetry**. But a log is simultaneously the *evidence you need* and *a data store the adversary wants*. The
corpus makes the second half concrete and load-bearing in a way naive logging ignores: the byproducts an agent
runtime most naturally dumps into a log are **not inert strings — they are reconstructable secrets, and the
sequence of decisions is itself a leakage channel**. Four grounded problems:

- **Model-derived artifacts in a log are recoverable identity/membership-bearing secrets, not opaque tokens.**
  This is the single most replicated cross-chunk conclusion in `Privacy-Protection.md` (§6, §9, reviewer
  synthesis over multiple independent papers). Gradients logged for debugging invert to training images
  (A37743 diffusion-prior inversion; A39333 analytic, *noise-prior-free* reconstruction — author-reported LPIPS
  0.340 vs 0.632 and ASR 45% vs 2% for prior SOTA at ε=10, δ=10⁻⁵). Smashed/intermediate split-inference
  representations invert back to raw input (A39212, worst when the client-side model is shallow). Soft prompts
  leak training-set membership **with no output access at all** (A40839 PIPRA — author-reported avg AUC 87.58%
  vs 77.05% for output-dependent baselines). "Protected" face embeddings still invert to impersonating
  identities across **eight named protection schemes** (A42453 FEM — author-reported ASR at FAR=0.01, e.g.
  IRSE50 FEM-KAN 83.7 vs MAP2V 77.9; residual e.g. 44.5 on GhostFaceNet for MinusFace — "reduced, not
  eliminated"). Steering vectors carry recoverable structure (A40720). A log that captures any of these "for
  observability" is a confidentiality breach waiting for a reader.

- **The decision/policy sequence is itself a leakage channel — protecting data at rest is insufficient.**
  A39710 (ε-DP + Nash-regret bandits, synthetic evaluation) shows a feedback-driven agent's **arm-selection
  sequence leaks per-user outcomes even when the stored data is protected**. The reviewer-synthesis
  implication (Privacy-Protection §6, §14): the *interaction trace itself* — the ordered log of what the agent
  chose — must be protected, not only the datastore it reads.

- **The agent cannot be trusted to recognize what is sensitive before it logs it.** A40874 (SAPA-Bench) finds
  off-the-shelf MLLM smartphone agents recognize sensitive actions at recognition-accuracy **below 60% even
  with explicit hints** (author-reported best Gemini 2.0-flash ~67%; note the privacy labels are partly
  GPT-4o-generated, so "sensitivity correctness" is itself model-dependent). Reviewer synthesis: you cannot
  delegate redaction to the agent's own judgment — an independent, deterministic minimization stage must sit in
  the logging path.

- **The log is re-ingested, and any re-ingested field is an injection surface.** A42239 establishes that
  **any model-visible field** — not only the user/system prompt but options, tool results, retrieved text — is
  an injection surface (author-reported E-adoption ≈0.5 and accuracy collapse to ≈0.27 for the "contradiction"
  injection on QwQ-32B/MMLU; with the within-paper nuance that *weak/noisy* injections can slightly *raise*
  accuracy). A summarizer, an LLM-judge (A40210), or a downstream agent that reads the log inherits this: a
  poisoned log entry becomes a prompt-injection payload for whatever later reads it.

Underneath all four sits the reviewer-synthesis framing from `Network-Cyber-Security.md` §3: the recurring
*implicit* assumption across the detector and telemetry papers is **trusted inputs, telemetry, and labels** —
provenance and pipeline trust are assumed non-adversarial. Secure logging removes that assumption on the
**confidentiality and content-safety axis** (what is in the log, who can read it, whether it can be weaponized
on re-ingestion); `tamper-evident-traces.md` removes it on the **integrity axis** (whether the log was
altered). The goal of *this* pattern is a log that is **complete enough for security/audit, minimized enough
not to be a secret store, access- and egress-controlled, and safe to re-read** — deterministically and
fail-closed.

## Applicable assets and attack surfaces

- **The log/telemetry store itself as a confidentiality asset.** Every entry is potential leakage. The primary
  protected asset is not "the log's integrity" (that is `tamper-evident-traces.md`) but **the sensitive content
  a naive log accumulates** and **the read/egress paths out of it**.

- **Model-derived artifacts that get logged.** Gradients (A37743, A39333), smashed/intermediate representations
  (A39212), soft prompts / prompt vectors (A40839), embeddings — even "protected" ones (A42453), steering
  vectors (A40720), and pseudo-source reconstructions (A39975). Each is demonstrated invertible or
  membership-bearing; each is a first-class secret if it lands in a log.

- **Sensitive intermediate execution state.** Activations (A40100 — inversion under server+client collusion;
  empirical privacy only, no reported ε) and expert-selection / routing metadata (A39721 — access-pattern leak
  even when payload is encrypted; semi-honest only). A verbose trace that captures these turns observability
  into a disclosure channel.

- **The decision/policy/interaction sequence.** The ordered record of agent choices leaks per-user outcomes
  (A39710). This is an asset even when each individual entry looks benign, because the *sequence* is the
  secret.

- **Retrieved content and tool payloads written to the log.** RAG results, KG entities, uploaded images, tool
  I/O. The provider-as-adversary cluster (A40534 ARoG, A40911 SOER, A40041 PRISM) treats keeping raw private
  content off the untrusted reader as the control; a log that stores the raw content re-creates the exposure
  the agent was supposed to avoid.

- **"Anonymized" fields that are not actually unrecoverable.** A42113 (speaker re-identification from
  *anonymized* child audio via ECAPA-TDNN + EER, evaluated only against an "ignorant" attacker) is the
  cautionary card: logging an "anonymized" value is not the same as logging a non-recoverable one.

- **Privacy-relevant operational metadata as configuration-of-record.** The privacy dial — ε / LDP flip
  probability / compression ratio γ / FSInfo level / bounded-domain diameter D / Metric-LDP εd² — and its
  consumption (A39051, A39510, A39311, A40041, A40720, A40838). This *should* be logged (as governed config),
  and the log of it is itself an audit asset that must be complete and access-controlled.

- **Security-event telemetry that must be captured (completeness surface).** Off-policy / out-of-allow-list
  selections (A42239); unauthorized installs, brute-force login attempts, sensitive-app exposure via
  navigation errors, and hallucinated-completion divergence (A42249); invalid-action rate and per-agent
  reputation shifts (A41065). Under-capturing these is a *security* failure of the log; over-capturing raw
  detail is a *confidentiality* failure. Secure logging holds both edges.

- **The log as re-ingested content (attack surface, not just asset).** Any summarizer / LLM-judge (A40210) /
  downstream agent that reads the log. A42239: a poisoned entry injects the reader. This is the same
  memory-ingress surface `context-and-memory-isolation.md` governs, arriving via the log.

- **Recorded evaluation / benchmark results.** A42369 (VulnBench) shows recorded metrics are inflatable by
  contamination, label leakage, and identifier-encoded labels (author-reported: threshold optimization
  improved F1 in 100% of model-dataset combinations; synthetic Juliet F1 0.900 vs. real-world DiverseVul
  0.307). A metric logged without its split/leakage provenance is a misleading claim about capability.

- **Egress / DLP blind spots.** A37125 and A40903 (author-reported steganalysis Pe ≈ 0.5; non-adaptive) show
  covert channels invisible at the content/text layer. A log-export or egress path cannot be secured by
  content inspection alone; a channel designed to preserve cover statistics passes DLP.

## Threat model

Designed for adversaries who want to **read secrets out of the log**, **make the log leak by what it stores or
by what it fails to store**, or **weaponize the log on re-ingestion** — as distinct from adversaries who want
the record to *lie* (that is the `tamper-evident-traces.md` threat model). The agent is treated as
**untrusted-by-default and privacy-unaware** (A40874 RA <60%; A42249 hallucinated completion). Grounded threat
classes:

- **Honest-but-curious reader of the log store (the most common corpus threat model, transplanted).** A
  server, cloud host, operator, or over-broadly-scoped principal who follows the protocol but reads logged
  artifacts to infer private inputs, membership, or attributes. This is the semi-honest counterparty that
  dominates `Privacy-Protection.md` §3 (A39210, A39212, A38773, A40033, A40132, A40852, A40206, A42229),
  applied to whoever can read the log.

- **Artifact-reconstruction adversary who intercepts a logged model-derived value.** Gradients (A37743,
  A39333), smashed reps (A39212), soft prompts (A40839), embeddings (A42453), steering vectors (A40720). The
  demonstrated attacks assume only possession of the artifact — logging it *is* handing it over.

- **Sequence-inference adversary.** Reads the ordered decision/policy log and infers per-user outcomes even
  when each field is individually protected (A39710). Reviewer synthesis: this defeats "we redacted the
  payload" if the *ordering itself* is exposed.

- **Provider-as-adversary via the log path.** An external/third-party model or reader receives raw private
  content because the log forwarded it (the confused-deputy framing of A40534, A40911, A40041, A40720). The
  log becomes the leak even though the agent's direct path was protected.

- **Log-as-injection.** A poisoned or attacker-influenced entry attacks a downstream LLM reader / summarizer /
  judge (A42239). A37135 (PriAgent) is the corpus's concrete agentic case: an LLM multi-agent auditor runs over
  attacker-influenced decompiled code/strings **without an injection control** (reviewer-flagged unimplemented
  gate) — the untrusted content flows through the pipeline and would flow through anything that re-reads its
  audit log.

- **Under-capture / evidence-starvation.** The adversary arranges that a security-relevant event (unauthorized
  install, brute-force attempt, off-policy selection, claim-vs-end-state divergence) is *not* logged — because
  logging was best-effort, sampled, or dropped under load. A42249 shows these events occur (author-reported
  100% unauthorized-install in certain planning tasks, small-n) and A42239 shows off-policy selection is the
  tripwire; a log that misses them is a security failure even though it leaked nothing.

- **"Anonymized"-but-recoverable capture.** The log stores a value believed de-identified that a stronger
  attacker re-identifies (A42113 — evaluated only against an "ignorant" attacker, so its own protection is a
  non-adaptive upper bound).

- **Covert-channel egress through the log/export path.** Content-preserving steganographic exfiltration
  (A37125, A40903) hidden in logged/exported fields, invisible to content DLP.

- **Eval-record contamination.** Logged metrics inflated by leakage/contamination so the log overstates
  capability or safety (A42369).

- **Reactivation of "deleted" logged data.** Even after a "delete my data" / log-purge, the residue is
  recoverable: approximate unlearning leaves an adversarially detectable, often reactivatable imprint (A41120
  PrivUB — fine-tuning reactivates forgotten data more than quantization; A40047 FMIA — single black-box query
  detects the imprint; A39373 IDI — behavioral deletion metrics are gameable while the representation retains
  the forget set, forget set recoverable >82% vs ≤41% true retrain). Reviewer synthesis: purging a log entry
  is *risk reduction, not guaranteed erasure*.

**Out of scope for this pattern (handled by siblings):** whether the record was altered/omitted/back-dated
(`tamper-evident-traces.md`); stopping the injection that caused a bad action
(`prompt-injection-containment.md`); deciding whether an action is allowed (`policy-permission-gates.md`);
bounding execution blast radius (`tool-capability-isolation.md`, `sandboxed-execution.md`). Secure logging
assumes those may fail and ensures the *log of the failure is both captured and not itself a new leak/injection*.

**Adaptivity boundary (critical).** Both syntheses flag near-universal absence of adaptive, defense-aware
evaluation. Privacy-Protection §11 is explicit: demonstrated bypasses are against *other* schemes under the
bypasser's own evaluation, and the corpus's own defenses are, with few exceptions, tested only against
non-adaptive attackers — their adaptive robustness **requires production validation**. Every design target in
this pattern is therefore an **engineering invariant to be validated**, not a corpus-measured efficacy number.

## Control mechanism

Secure logging is a **deterministic pipeline that sits between event producers and the log store, and between
the store and every reader** — not a model verdict. Six composable mechanisms, all fail-closed and
least-privilege:

1. **Classify-then-minimize at write time (core control, standard engineering — not corpus-measured).** Before
   any field is stored, a deterministic minimization stage decides *what may be logged at all* and *at what
   fidelity*. Model-derived artifacts (gradients, activations, smashed reps, soft prompts, embeddings, steering
   vectors) and raw private content default to **not logged / logged as a non-invertible reference (hash or
   ID)**, because the corpus demonstrates each is reconstructable (A37743, A39333, A39212, A40839, A42453,
   A40720, A40100). This directly implements the design principle "treat every transmitted model artifact as a
   sensitive, reconstructable asset" (Privacy-Protection §14). The classifier is **deterministic and
   allow-list-shaped**, *not* the agent's own judgment — because A40874 shows the agent recognizes sensitivity
   at <60%.

2. **Redact / decompose / abstract before storing (grounded in the sensitivity-aware cluster).** Where a field
   must be logged but carries sensitive structure, log the **abstracted / anonymized / surrogate** form and
   keep the raw off the store — the redact-then-recover-locally pattern (A40911 SOER, A40534 ARoG, A40041
   PRISM). For statistical/telemetry fields, prefer **decompose-then-protect and structure-restricted noise**
   (A39212 information decomposition; A40862 single-message LDP frequency reporting; A40117/A40720 subspace/
   compression before noise) so the log carries the signal, not the raw. Reviewer-synthesis caveat: A42113
   shows "anonymized" is not "unrecoverable" — abstraction reduces, does not eliminate, recoverability.

3. **Protect the sequence, not only the fields (grounded in A39710).** Because the decision/policy *sequence*
   leaks per-user outcomes, the ordered interaction log for a principal is access-controlled and, where the
   sequence is itself the release, subject to `differential-privacy.md` accounting on the sequence — not merely
   field-level redaction.

4. **Log the privacy dial as configuration-of-record (grounded in the DP cluster).** ε / LDP flip probability /
   γ / FSInfo / D / εd² and their per-operation consumption are recorded as **governed configuration**
   (A39051, A39510, A39311, A40041, A40720, A40838), and an auditable evidence record is emitted per
   privacy-relevant operation — unlearning events, budget consumption, per-request certificates (A40045
   Oblivionis, A40870, A40896 GUIC, A40889 commitment-based verifiable selection). Budget exhaustion or
   accounting error is an incident boundary (Privacy-Protection §13).

5. **Least-privilege, audited read/egress from the store (standard engineering).** Readers are scoped, minimized
   to the fields they need, and every read is itself logged (who read which fields) — the read-authorization
   discipline of `retrieval-authorization.md` applied to the log. Egress cannot be secured by content
   inspection alone (A37125, A40903 covert channels invisible at content layer); egress is gated by
   allow-listed destinations and monitored, not DLP-scanned-and-trusted.

6. **Sanitize on read; treat the log as untrusted data for any LLM reader (grounded in A42239).** Before a
   summarizer / judge / downstream agent ingests a log field, it is handled as **data, not instructions**
   (via `prompt-injection-containment.md` / `context-and-memory-isolation.md`), because any model-visible field
   is an injection surface. Reviewer synthesis (A37135): an agentic auditor over untrusted logged content with
   no injection control is a demonstrated open surface.

**Completeness edge (fail-closed capture).** Security-relevant events — off-policy/out-of-allow-list selection
(A42239), unauthorized install / brute-force / sensitive-app exposure / hallucinated-completion divergence
(A42249), invalid-action rate (A41065) — are **mandatory-capture**: if they cannot be durably written, the
consequential action is deferred/denied rather than executed unlogged (the "reject/defer as a first-class
action" posture of A37053 applied to the security-event log). Secure logging fails **toward more, minimized
capture**, never toward silent under-capture.

**Sharp boundary.** These six give **confidentiality-appropriate content, minimization, sequence protection,
governed privacy accounting, controlled read/egress, and injection-safe re-ingestion**. They do **not** give
*tamper-evidence, provenance, or non-repudiation* of the record — that is `tamper-evident-traces.md`, and a
production log needs both.

## Preconditions and trust assumptions

- **A deterministic sensitivity classifier / field allow-list exists and is not the agent.** Mechanism 1
  assumes an out-of-agent, deterministic rule set for what may be logged and at what fidelity. Grounded in
  A40874 (agent RA <60% even with hints) — self-classification is not a precondition that holds. If
  minimization is delegated to the model, this control is theatre.

- **Model-derived artifacts are treated as secrets by default.** The precondition inverting naive logging: the
  corpus's most replicated finding (Privacy-Protection §9) is that gradients/reps/prompts/embeddings/steering
  vectors invert. The default posture must be *don't log the artifact; log a non-invertible reference* unless a
  reviewed exception exists.

- **A privacy-accounting substrate exists for any log that is also a release.** Mechanisms 3–4 assume the
  DP/LDP accounting of `differential-privacy.md` is available where the log (or the sequence) constitutes a
  release. A "by construction / we only log X" claim with no accounting is contested evidence
  (Privacy-Protection §2, §10: A39307/A39524/A39338 assert privacy from data-locality with no attack or
  accounting — a documented trap).

- **Read/egress access control is enforced below the application, not by convention.** Mechanism 5 assumes the
  store enforces scoped read at the storage/IAM layer; an application-layer "only admins read" over a broadly
  readable store is bypassable by anyone with the application identity. (Standard engineering; not
  corpus-measured.)

- **Every LLM reader in the read path applies injection containment.** Mechanism 6 assumes
  `prompt-injection-containment.md` is in place for summarizers/judges/downstream agents (A42239, A37135). If a
  reader ingests raw log text as instructions, sanitize-on-read is absent and the log is an injection vector.

- **"Anonymized" and "deleted" are risk-reduction, not guarantees.** Preconditions carry the caveats that
  anonymization is defeatable (A42113) and log-purge leaves recoverable residue (A41120, A40047, A39373) —
  so retention/deletion claims must be scoped, not absolute.

- **The minimization/redaction pipeline is itself a trust-decision surface and will be attacked.** Adding a
  classifier/redactor relocates trust to that component; it must be minimal, deterministic, and monitored
  (generalizing the reviewer-synthesis "every new trust surface is attackable" caution, Network-Cyber-Security
  §15).

- **No adaptive-adversary validation is inherited from the corpus.** Every efficacy expectation is a design
  target requiring production red-teaming (both syntheses' adaptive-evaluation caveat; Privacy-Protection §11).

## System architecture

A deterministic write/read pipeline wrapping the log store, sitting beside the agent runtime and composing with
the tamper-evidence layer:

```
  event producers                 ┌──────────────────────────────────────────────┐
  (agent runtime, policy gate, ─► │  Log Ingress (deterministic, least-priv)      │
   tools, end-state probe)        │  1. classify field (allow-list; NOT the agent)│
                                  │  2. minimize/redact/abstract or drop-to-ref    │
                                  │  3. structure-restricted noise where a release │
                                  │  4. attach privacy-dial config-of-record       │──► minimized entry
                                  │  MANDATORY-CAPTURE security events fail-closed  │
                                  └───────────────────┬──────────────────────────┘
                                                      │ (hand off to tamper-evidence
                                                      │  layer: sign+chain — see
                                                      │  tamper-evident-traces.md)
                                                      ▼
                                  ┌──────────────────────────────────────────────┐
                                  │  Log Store (scoped read at storage/IAM layer) │
                                  │  field-level access classes; read is audited  │  ◄── egress: allow-listed
                                  └───────────────────┬──────────────────────────┘        destinations only
                                                      │
        read path (untrusted-on-read, A42239: sanitize before any LLM sees it)
                                                      ▼
      ┌──────────────┐   ┌───────────────────────┐   ┌─────────────────────────┐
      │ Human review  │   │ LLM summarizer / judge │   │ Incident / compliance    │
      │ (scoped read) │   │ (A40210) — data-not-   │   │ export (redacted,        │
      │               │   │  instructions gate     │   │  destination allow-list) │
      └──────────────┘   └───────────────────────┘   └─────────────────────────┘
```

- **Ingress is deterministic and agent-independent.** Classification/minimization is a fixed pipeline, not a
  model decision (A40874). The agent *proposes* content; the ingress stage decides what is stored and at what
  fidelity.

- **Artifact default is drop-to-reference.** Gradients/activations/reps/prompts/embeddings/steering vectors are
  stored as a non-invertible reference (hash/id) unless a reviewed exception applies (Privacy-Protection §9,
  §14). The raw artifact does not enter the store by default.

- **Sequence protection is a store property, not a field property.** The ordered per-principal decision log is
  its own access class (A39710); exposing "just the sequence" is a release subject to accounting.

- **The store enforces field-level read classes at the IAM/storage layer**, and every read is audited (who read
  which fields — Privacy-Protection §14 read-audit; `retrieval-authorization.md`). Egress goes only to
  allow-listed destinations (A37125/A40903: content DLP cannot see a covert channel, so gate destinations, not
  bytes).

- **Every LLM reader is behind a sanitize-on-read gate** (A42239, A37135), the same memory-ingress control as
  `context-and-memory-isolation.md`.

- **Tamper-evidence is a separate, co-required layer.** Signing/chaining/attestation/WORM is
  `tamper-evident-traces.md`; this architecture hands the minimized entry to it. A secure log is minimized *and*
  tamper-evident.

## Recommended implementation pattern

Deterministic, fail-closed, least-privilege. Concretely:

- **Default-deny logging of model-derived artifacts.** Gradients, activations, smashed representations, soft
  prompts, embeddings, steering vectors → **not stored raw**; store a salted hash / opaque id and, if needed
  for debugging, a strictly access-controlled short-TTL sidecar behind an exception review (A37743, A39333,
  A39212, A40839, A42453, A40720, A40100). Rationale is the replicated invertibility finding
  (Privacy-Protection §9), not a per-artifact judgment.

- **Redact/abstract raw private content at ingress; keep raw off the reader.** Log the anonymized/surrogate
  form (A40911, A40534, A40041); never forward raw retrieved content, KG entities, or uploaded media into a log
  that a third-party model or broad reader can reach. Caveat the abstraction as reduction, not elimination
  (A42113).

- **Decompose-then-protect and use structure-restricted noise for telemetry/statistics** rather than logging
  raw values (A39212 information decomposition; A40862 single-residue LDP; A40117/A40720 subspace/compression
  before DP). Prefer bounded/one-sided noise where a logged value feeds a system with hard constraints (A39051
  constraint-preserving; A39710 clip-to-domain).

- **Treat the decision/interaction sequence as a protected release** (A39710): access-class the per-principal
  ordered log; where the sequence is exported/served, apply `differential-privacy.md` accounting to it, not
  only to the fields.

- **Record the privacy dial and per-op privacy evidence as configuration-of-record** (A39051, A39510, A40041,
  A40720, A40838): log ε/LDP-rate/γ/FSInfo/D/εd² and their consumption; emit an auditable record per
  privacy-relevant operation (unlearning event A40045; per-request certificate A40896; verifiable selection
  commitment A40889). Budget exhaustion/accounting error → incident boundary.

- **Mandatory-capture the security events, fail-closed.** Off-policy/out-of-allow-list selection (A42239);
  unauthorized install / brute-force / sensitive-app exposure / hallucinated-completion divergence (A42249);
  invalid-action rate and per-agent reputation shifts (A41065). If these cannot be durably written, defer/deny
  the consequential action (A37053) — never proceed with the security event unlogged.

- **Seal evaluation-record provenance** (A42369): when logging a metric, capture split identity, leakage-control
  status, and identifier-anonymization status alongside it, so a logged "score" cannot be detached from the
  conditions that make it meaningful.

- **Least-privilege, audited read; scoped fields.** Readers get the minimum field set; every read is logged
  (Privacy-Protection §14). No principal — including the agent's tool surface — gets blanket read of artifact/
  sequence classes.

- **Allow-listed egress, not content-scanned egress.** Because covert channels are invisible at the content
  layer (A37125, A40903), gate log export/forwarding by destination allow-list and volume/anomaly monitoring,
  not by DLP content inspection alone.

- **Sanitize on read for every LLM reader.** Summarizer/judge/downstream agent treats log fields as data
  (A42239, A37135) via `prompt-injection-containment.md`.

- **Compress high-volume telemetry without silently dropping security events.** For ultra-long telemetry
  (A40815: 1M+-token EDR samples), compress-then-reason on non-security fields; never sample out
  mandatory-capture security events to save space (that is indistinguishable from evidence-starvation).

- **Corroborate before trusting a logged claim** (A36959 verify-before-trust; A40210 LLM-judge needs
  calibration): a single logged signal is not evidence for a security decision; require cross-signal agreement
  + threshold.

- **Scope retention/deletion honestly.** Log-purge is risk reduction, not erasure (A41120, A40047, A39373);
  pair "delete my data" with residual-risk disclosure and a representation-level acceptance test where the log
  feeds a model; treat re-fine-tune as a reactivation hazard.

## Incorrect or fragile implementation patterns

- **Logging gradients/activations/reps/prompts/embeddings/steering vectors raw "for observability".** Directly
  refuted by the replicated invertibility finding (A37743, A39333, A39212, A40839, A42453, A40720, A40100). A
  debug dump of any of these is a reconstructable-secret store.

- **Delegating redaction to the agent's own sensitivity judgment.** A40874: agents recognize sensitivity at
  <60% even with hints. Minimization must be a deterministic, agent-independent stage.

- **Redacting fields but exposing the decision sequence.** A39710: the ordered sequence leaks per-user outcomes
  even when each field is protected. "We redacted the payload" is insufficient if the sequence is readable.

- **Treating "anonymized" as "unrecoverable".** A42113: anonymized audio re-identifies under a stronger
  attacker (and even that eval used only an "ignorant" attacker — a non-adaptive upper bound). Log abstraction
  with a residual-risk caveat, not a guarantee.

- **Treating "deleted / purged" as "erased".** A41120/A40047/A39373: purge leaves an adversarially detectable,
  reactivatable imprint; behavioral deletion checks are gameable. Silent "delete" claims overstate protection.

- **Content-scanning log egress and trusting it.** A37125/A40903: covert channels are invisible at the content
  layer (Pe ≈ 0.5). DLP over log exports gives false assurance; gate destinations.

- **Feeding raw log text straight into an LLM summarizer/judge/agent.** A42239 (any field is an injection
  surface), A37135 (agentic auditor over untrusted content with no injection control). Un-sanitized read paths
  weaponize the log.

- **"Privacy by construction / we only log digests or gradients."** A39307/A39524/A39338 assert privacy from
  data-locality with no attack or accounting, and gradient/digest sharing is a documented leakage vector
  (A37743, A39333) — so this is contested, not sound (Privacy-Protection §2, §10).

- **Best-effort / sampled logging of security events.** Sampling out "boring" events is indistinguishable from
  evidence-starvation and misses exactly the events A42249/A42239 identify. Security-event capture must be
  fail-closed, not best-effort.

- **Broad read access to the whole log.** Turns any curious reader into the honest-but-curious adversary of
  Privacy-Protection §3; least-privilege field-scoped read is mandatory.

- **Formal/heuristic-noise claim in the log's privacy copy without an executed attack.** Privacy-Protection
  §12: formal-guarantee-without-executed-attack is pervasive; A42453 is the cautionary example of a
  "privacy-preserving" scheme inverting under test. Do not label a log "private" without a red-team.

- **Confusing this with tamper-evidence.** A minimized, access-controlled log that is *still rewritable* is not
  integrity-protected; a hash-chained log that *still stores raw embeddings* is not confidential. The two
  controls do not substitute for each other.

## Verification strategy

- **Ingress minimization audit (deterministic, must pass).** Assert that no default-deny artifact class
  (gradients/activations/reps/prompts/embeddings/steering vectors) reaches the store raw; that raw private
  content is abstracted; that the classifier is agent-independent (A40874). Design invariant; not
  corpus-measured.

- **Reconstruction red-team on whatever *is* logged.** For any artifact or abstracted field retained, run the
  corpus's own attacks against the stored form: gradient inversion (A37743 diffusion prior; A39333 analytic
  noise-prior-free), representation inversion (A39212), embedding inversion (A42453), prompt-vector MIA (A40839),
  re-identification (A42113). If the stored form reconstructs, it is not minimized. Use A37743's
  Reconstruction-Vulnerability (RV) architecture-audit metric where applicable.

- **Sequence-leakage check** (A39710): confirm the per-principal decision sequence is access-classed and, where
  released, accounted; attempt outcome inference from the exposed sequence.

- **Privacy-accounting audit** (Privacy-Protection §12, §15): verify ε/LDP/γ is logged for *all* shared objects,
  not just the headline field (the A39311/A39582/A39307 under-accounting trap); confirm budget exhaustion is an
  enforced incident boundary.

- **Read/egress access-control test.** Verify field-scoped read at the storage/IAM layer, that reads are
  audited, and that egress goes only to allow-listed destinations (A37125/A40903 — content scan is insufficient).

- **Sanitize-on-read test** (A42239, A37135): inject instruction-shaped text into a log field; confirm a
  downstream LLM reader treats it as data.

- **Mandatory-capture / fail-closed test** (A42249, A42239, A37053): confirm security events are durably
  written and that a consequential action is deferred/denied if its security-event entry cannot be written.

- **Retention/deletion acceptance test** (A41120, A40047, A39373): after a purge, run a residual-information /
  former-membership probe; behavioral "it's gone" is necessary-but-insufficient. Re-audit after any re-fine-tune.

- **Eval-provenance audit** (A42369): confirm logged metrics carry split/leakage/anonymization provenance.

- **Adaptive red-team of the logging layer (launch gate).** Because no corpus paper red-teams a secure-logging
  system, an explicit adaptive exercise is required (see Adaptive adversarial tests). Treat pre-red-team
  numbers as upper bounds (both syntheses' adaptive caveat; Privacy-Protection §11).

## Metrics and thresholds

*Operational invariants below are engineering targets requiring production validation — not corpus-measured
efficacy. Author-reported corpus numbers are labeled and are motivational, not measurements of this pattern.*

- **Raw-artifact-in-log rate → target 0.** No gradient/activation/rep/prompt/embedding/steering-vector stored
  raw outside a reviewed, access-controlled, short-TTL exception (Privacy-Protection §9). Any occurrence is a
  P1 confidentiality incident.

- **Reconstruction success on stored forms → target below the residual you have accepted and disclosed.** Treat
  as "reduced, not eliminated" (A42453 residual e.g. 44.5 on GhostFaceNet for MinusFace, author-reported);
  measure with the paper attacks (A37743/A39333/A39212/A40839/A42453) and report the *absolute* residual, not a
  relative reduction (Privacy-Protection §16).

- **Security-event capture completeness = 100% for mandatory-capture events** (A42249, A42239); unlogged
  consequential-action rate → 0 (fail-closed, A37053). Any consequential action without its security-event
  entry is a control failure.

- **Privacy-dial logging coverage = 100% of privacy-relevant operations** carry ε/LDP/γ + consumption
  (A39051, A39510, A40041, A40720, A40838). Budget-exhaustion → enforced incident boundary.

- **Read-audit coverage = 100% of reads logged; field-scope violations → 0** (Privacy-Protection §14;
  `retrieval-authorization.md`).

- **Egress destination-allow-list violations → 0** (A37125/A40903 — content DLP is not a threshold you can
  trust).

- **Sanitize-on-read coverage = 100% of LLM readers** behind the injection gate (A42239, A37135).

- **Retention/deletion residual disclosed, not claimed-zero** (A41120, A40047) — the metric is "residual risk
  disclosed + representation-level probe run", not "0% recoverable".

- **Corpus reference numbers (author-reported; motivation, not this pattern's efficacy):** Venom gradient
  reconstruction ASR 45% vs 2% at ε=10, δ=10⁻⁵ (A39333) — why gradients are not loggable raw; PIPRA soft-prompt
  MIA avg AUC 87.58% vs 77.05% (A40839) — why prompt vectors are secrets; FEM residual ASR e.g. 44.5 on
  GhostFaceNet/MinusFace (A42453) — why "protected" embeddings still leak; SAPA-Bench RA <60%/best ~67%
  (A40874) — why the agent can't self-redact; A42239 E-adoption ≈0.5, accuracy ≈0.27 (QwQ-32B/MMLU) — why
  re-ingested log fields are injection surfaces; VulnBench threshold-opt F1 gain in 100% of combos, Juliet
  0.900 vs DiverseVul 0.307 (A42369) — why eval logs need sealed provenance. All author-reported,
  single-study, non-adaptive; do not restate as secure-logging results.

## Test cases

Functional / confidentiality (deterministic, must pass):

1. **Attempt to log a raw gradient / activation / smashed rep / soft prompt / embedding / steering vector**
   (A37743, A39333, A39212, A40839, A42453, A40720, A40100) → ingress default-deny stores a non-invertible
   reference only; raw-artifact-in-log rate stays 0.
2. **Run the paper reconstruction attack against the stored form** → reconstruction fails, or succeeds only up
   to the disclosed residual; a fully reconstructable stored form fails the test (A42453 "reduced, not
   eliminated" is the calibration).
3. **Log a raw retrieved document / uploaded image, then have a third-party-scoped reader access it** → blocked;
   only the abstracted/surrogate form is readable (A40911, A40534).
4. **Expose only the per-principal decision sequence and attempt outcome inference** (A39710) → sequence is
   access-classed / accounted; naive exposure fails the test.
5. **Log an "anonymized" field and run a stronger re-identification attack** (A42113) → residual re-id is
   measured and disclosed, not assumed zero.
6. **Security event occurs (unauthorized install / off-policy selection) under log-store pressure** (A42249,
   A42239) → event is durably captured or the consequential action is deferred/denied; never proceeds unlogged
   (A37053).
7. **Log-as-injection:** a field contains instruction-shaped text; a downstream summarizer/judge reads it
   (A42239, A37135) → sanitize-on-read makes the reader treat it as data; test fails if the reader obeys it.
8. **Privacy-relevant operation with no logged ε/budget** (A39051, A39510) → rejected/flagged; privacy-dial
   coverage gap detected.
9. **Under-accounted shared object** — headline field DP-logged but a co-shared structure/mass/digest is not
   (A39311, A39582, A39307) → flagged as incomplete accounting.
10. **Log export to a non-allow-listed destination, including a covert-channel-shaped payload** (A37125,
    A40903) → destination gate blocks; content DLP is not relied on.
11. **Eval metric logged without split/leakage/anonymization provenance** (A42369) → flagged non-admissible.
12. **Purge a log entry, then run a former-membership / residual probe** (A41120, A40047, A39373) → residual is
    surfaced and disclosed; behavioral "gone" alone does not pass.

## Adaptive adversarial tests

*Required because no corpus paper red-teams a secure-logging system; results are the real evidence, and
pre-test numbers are upper bounds (both syntheses' adaptive caveat; Privacy-Protection §11 — demonstrated
bypasses are against other schemes under the bypasser's own eval).*

- **Adaptive reconstruction against the stored (minimized/abstracted) form:** an attacker who knows the
  redaction scheme optimizes an inversion against it (generalizing A39333's noise-prior-free analytic attack and
  A42453's scheme-defeating reconstruction). Success = recovering more than the disclosed residual.
- **Sequence-inference under partial field redaction** (A39710): infer per-user outcomes from the exposed
  ordering despite field-level redaction.
- **Anonymization-defeat** (A42113): stronger-than-"ignorant" attacker re-identifies logged "anonymized" fields.
- **Deletion-reactivation** (A41120, A40047, A39373): after purge + a routine re-fine-tune, recover the
  "deleted" data; confirm the retention claim was scoped as risk-reduction, not erasure.
- **Log-as-injection against the reader** (A42239, A37135): craft a log field that drives a downstream
  summarizer/judge/agent off-policy; confirm sanitize-on-read holds.
- **Covert-channel egress** (A37125, A40903): exfiltrate through a logged/exported field invisible to content
  DLP; confirm destination allow-listing + anomaly monitoring catches it where content scanning cannot.
- **Under-accounting exploit** (A39311, A39582, A39307): find a co-shared object the DP accounting missed and
  reconstruct from it.
- **Minimization-pipeline gaming** (reviewer synthesis, "every new trust surface is attackable"): make sensitive
  content classify as non-sensitive so it is logged in full; confirm the deterministic allow-list is not
  content-spoofable.

## Telemetry requirements

Signals to emit (and to protect under this same pattern — the telemetry about the log is itself a log):

- **Raw-artifact-in-log detections** — any default-deny artifact class reaching the store raw (A37743, A39333,
  A39212, A40839, A42453); pages as P1.
- **Reconstruction-audit results** on stored forms (A37743 RV metric; A42453) — periodic, with the absolute
  residual.
- **Security-event capture completeness and unlogged-consequential-action counter** (A42249, A42239, A37053) —
  the fail-closed health signal.
- **Off-policy / out-of-allow-list selection rate** (A42239) and **invalid-action rate / per-agent reputation
  shifts** (A41065) — both the events to capture and the tripwires that a fabrication/leak window is open
  (reputation is a *signal*, explicitly not a trust shortcut — gameable, reviewer synthesis).
- **Claim-vs-end-state divergence** (A42249) — captured as two separately-authored facts (agent claim +
  independent observation), never collapsed.
- **Privacy-dial consumption and budget-exhaustion events** (A39051, A39510, A40041, A40720, A40838).
- **Read-path access audit** — who read which fields (Privacy-Protection §14) and every LLM re-ingestion event
  (A42239).
- **Egress events by destination** (allow-list hits/misses) and volume/anomaly on export (A37125, A40903 —
  because content is not a reliable signal).
- **Per-privacy-operation evidence records** — unlearning events (A40045), per-request certificates (A40896),
  verifiable-selection commitments (A40889).
- **Eval-provenance completeness** — fraction of logged metrics carrying split/leakage/anonymization status
  (A42369).

## Failure handling

- **Fail closed on mandatory-capture.** If a security-relevant event cannot be durably minimized-and-written,
  the consequential action is **deferred/denied**, not executed unlogged (A37053 reject/defer applied to the
  security-event log). Availability of the security-event record is a precondition for the action.

- **Fail closed on minimization, not open.** If the classifier/redactor is unavailable or uncertain about a
  field, **do not log the raw value** — drop to a reference or defer, because the default posture is
  "artifacts are secrets" (Privacy-Protection §9). An uncertain redactor must not emit raw.

- **Fail loud on read/egress violations.** A field-scope violation, a non-allow-listed egress attempt, or a
  detected raw-artifact write is surfaced as an incident, not silently dropped.

- **Isolate a suspected-leaking reader/writer.** On anomaly (excessive artifact-class reads, egress to new
  destinations, reputation shift — A41065), quarantine that principal's future access for review while
  preserving its access-audit history as evidence (hand integrity to `tamper-evident-traces.md`).

- **Corroborate before acting on a logged claim** (A36959; A40210 judge-calibration): a single logged signal or
  a single detector is triage, not a gate — real-world detector F1 ≈ 0.3–0.6 (A42369). Investigate, do not
  auto-destroy.

- **Under uncertainty, degrade to more *minimized* capture, not less capture and not more raw.** Raise
  fidelity of *references and security events*, never raise raw-artifact retention.

- **Budget/accounting failure is an incident boundary** (Privacy-Protection §13): on ε-exhaustion or accounting
  error for a log that is also a release, stop the release path rather than continue un-accounted.

## Rollback and containment

- **Containment removes access/egress and quarantines principals; it does not "un-leak".** A logged secret that
  was read is compromised — treat rotation of the leaked credential/secret and notification as the response
  (via `least-privilege-credentials.md`), because reconstruction is offline and undetectable server-side
  (A42453: "protected" embeddings invert offline; A40047: single-query former-membership). You cannot roll back
  a disclosure.

- **Purge is risk-reduction with a residual, and must be honest about it** (A41120, A40047, A39373). Where
  legal/privacy retention forces removal, run a representation-level acceptance test after the purge and
  disclose the residual; treat any subsequent re-fine-tune as a reactivation hazard (A41120: fine-tuning
  reactivates more than quantization).

- **Tighten the allow-list / minimization rule set, not the after-the-fact scrubbing.** The durable fix for a
  raw-artifact-in-log incident is default-deny at ingress (mechanism 1), not a downstream redactor chasing
  fields that already landed.

- **Revoke and rotate on a confirmed reader compromise.** Rotate signing/read keys and re-scope access; record
  the containment actions themselves as (tamper-evident) log entries so the response is auditable.

- **Preserve the integrity of the evidence trail during containment.** Rollback of the *system* (revoke
  capability, quarantine identity) must not delete the historical security-event log — that is
  `tamper-evident-traces.md`'s append-only guarantee; secure logging must not open a silent-delete path for
  "cleanup".

## Known bypasses

**Reviewer-identified (not demonstrated against a secure-logging system in the corpus — no such system is
evaluated there; each item is a demonstrated attack against a related object, transplanted with calibration):**

- **Reconstruction from any logged model-derived artifact.** Gradients (A37743, A39333), reps (A39212), soft
  prompts (A40839), embeddings even "protected" (A42453), steering vectors (A40720) — all invert; logging them
  raw is the bypass. Mitigated by default-deny, *reduced not eliminated* for any retained abstraction.

- **Sequence inference despite field redaction** (A39710) — the ordering leaks; field-level redaction does not
  close it.

- **Anonymization defeat** (A42113) — "anonymized" logged fields re-identify under a stronger-than-tested
  attacker.

- **Deletion reactivation** (A41120, A40047, A39373) — purge leaves recoverable, reactivatable residue;
  behavioral deletion checks are gameable.

- **Log-as-injection** (A42239, A37135) — a poisoned field attacks the downstream LLM reader; a bypass of the
  *review*, mitigated by sanitize-on-read.

- **Covert-channel egress** (A37125, A40903) — exfiltration through a logged/exported field invisible to
  content DLP; mitigated by destination gating, not content scanning.

- **Under-accounting** (A39311, A39582, A39307) — a co-shared object outside the DP accounting reconstructs the
  "protected" release.

- **Minimization delegated to the agent** (A40874) — the agent mis-classifies sensitive content as safe and
  logs it in full.

- **"Privacy by construction" with no accounting** (A39307/A39524/A39338, contested per Privacy-Protection §2,
  §10) — data-locality asserted as privacy while gradients/digests still ship.

**Corpus adaptivity caveat:** none of the above has been evaluated against an adaptive attacker targeting a
secure-logging layer specifically — that evaluation is a launch gate, not a corpus deliverable (both syntheses;
Privacy-Protection §11).

## Residual risks

- **Disclosure is irreversible; minimization reduces, does not eliminate, recoverability.** A42453 (residual
  ASR non-zero across eight schemes), A40047 (single-query detection), A42113 (anonymization defeatable) — any
  retained abstraction carries a residual that must be measured and disclosed, not claimed zero.

- **The decision sequence remains a leakage channel** (A39710) wherever it is exposed, even under perfect
  field-level redaction.

- **Retention/deletion is approximate and reactivatable** (A41120, A40047, A39373) — "delete my data" on a log
  is risk reduction, not guaranteed erasure, especially where the log feeds a model that is later re-fine-tuned.

- **The minimization/classification pipeline is concentrated new trust** — it can be gamed or misconfigured
  (reviewer synthesis, "every new trust surface is attackable", Network-Cyber-Security §15); it relocates trust,
  it does not remove it.

- **Confidentiality vs. completeness tension.** Mandatory-capture of security events (A42249, A42239) pulls
  toward more logging; minimization pulls toward less — the residual is the boundary between "enough evidence"
  and "too much secret", and it is a judgment, not a solved value.

- **Covert channels remain invisible at the content layer** (A37125, A40903) — destination gating and anomaly
  monitoring bound but do not close covert egress.

- **Formal/heuristic privacy claims are unvalidated against adaptive attackers** (Privacy-Protection §11, §12) —
  no adaptive-adversary assurance is inherited; all thresholds require production red-teaming.

- **This pattern does not provide integrity.** A minimized, access-controlled log that is still rewritable is
  not tamper-evident — the residual "the record was altered" risk lives in, and is only closed by,
  `tamper-evident-traces.md`.

## Relevant research (stable paper ids from the syntheses/cards)

**Load-bearing (the confidentiality-of-logs motivation and the design principles):**
- **A37743** — GGSS-R (Privacy-Protection): diffusion-prior gradient inversion of noise-perturbed/DP gradients;
  reusable Reconstruction-Vulnerability (RV) architecture-audit metric. Load-bearing "logged gradients are
  reconstructable". Author-reported; honest-but-curious FL server; non-adaptive.
- **A39333** — Venom (Privacy-Protection; author-reported LPIPS 0.340 vs 0.632, ASR 45% vs 2% at ε=10, δ=10⁻⁵):
  analytic, *noise-prior-free* gradient reconstruction. Convergent with A37743.
- **A39212** — split-inference information decomposition + FSInfo/Fisher-calibrated noise (Privacy-Protection):
  smashed/intermediate representations invert; honest-but-curious-server DRA — logged reps are secrets, and
  decompose-then-protect is the mitigation.
- **A40839** — PIPRA (Privacy-Protection; author-reported avg AUC 87.58% vs 77.05%, 90.37% Caltech101):
  output-free membership inference from soft prompts — logged prompt vectors are secrets even with no output.
- **A42453** — FEM (Privacy-Protection; strongest-evidence paper; author-reported ASR at FAR=0.01, e.g. 83.7
  vs 77.9; residual e.g. 44.5): "protected" embeddings invert to impersonating identities across eight named
  schemes (DCTDP, HFCF, PartialFace, MinusFace, PolyProtect, MLP-Hash, SlerpFace, Fawkes). "Reduced, not
  eliminated" is the calibration for any logged embedding.
- **A40720** — PrivSV (Privacy-Protection): steering vectors are leakable artifacts (Metric-LDP εd²); formal,
  no executed attack — logged steering vectors are secrets.
- **A40100** — FedSEA-LLaMA (Network-Cyber-Security; arXiv:2505.15683): activations invert under server+client
  collusion; empirical privacy only, no reported ε — logged activations are sensitive.
- **A39721** — SecMoE (Network-Cyber-Security): expert-selection/routing access pattern leaks input even when
  payload is encrypted; semi-honest only — logged routing metadata is sensitive.
- **A39710** — ε-DP + Nash-regret bandits (Privacy-Protection): the decision/policy *sequence* leaks per-user
  outcomes even when data at rest is protected; synthetic evaluation — protect the logged sequence, not only
  fields.
- **A40874** — SAPA-Bench (Privacy-Protection; author-reported RA <60%, best Gemini 2.0-flash ~67%; privacy
  labels partly GPT-4o-generated): agents can't reliably recognize sensitivity — minimization must be
  deterministic and agent-independent; also the action-path human-confirmation gate.
- **A42239** — Obedience or Vigilance? (Network-Cyber-Security; author-reported E-adoption ≈0.5, accuracy ≈0.27,
  QwQ-32B/MMLU): any model-visible field is an injection surface → a re-ingested log field is an injection
  surface (sanitize-on-read). Nuance: weak/noisy injections can raise accuracy.
- **A42249** — Towards Capable and Secure Autonomous Computer-Use Agents (Network-Cyber-Security, Student
  Abstract; author-reported 100% unauthorized-install in certain planning tasks; small-n, version-bound): the
  security events a log must fail-closed capture; hallucinated-completion divergence.
- **`Network-Cyber-Security.md` §3 (reviewer synthesis)** — the implicit "trusted inputs/telemetry/labels"
  assumption this pattern removes on the confidentiality/content-safety axis.

**Supporting:**
- **A40911** — SOER, **A40534** — ARoG, **A40041** — PRISM (Privacy-Protection): keep raw private content off
  the untrusted reader; redact/abstract/route-locally — log the abstracted form.
- **A39051** — DP Linear Programming (Privacy-Protection): constraint-preserving one-sided noise; privacy dial
  as config-of-record; post-processing immunity.
- **A39510** — improved DP-SGD analysis (Privacy-Protection): tight hidden-state RDP; guarantee dies if
  intermediate checkpoints leak → logging checkpoints voids DP.
- **A40838** — DP-ICL, **A40862** — RNS single-message LDP (Privacy-Protection): DP synthetic
  demonstrations / telemetry-frequency reporting with accounting; log the signal, not the raw.
- **A40117** — DP-SFT subspace (Privacy-Protection): structure-restricted noise before storing/releasing.
- **A41120** — PrivUB, **A40047** — FMIA, **A39373** — IDI (Privacy-Protection): purge ≠ erasure; residual is
  detectable/reactivatable; behavioral deletion checks are gameable (>82% vs ≤41% recoverable).
- **A40045** — Oblivionis, **A40896** — GUIC, **A40889** — MartDE (Privacy-Protection): emit an auditable
  evidence record / per-request certificate / verifiable-selection commitment per privacy-relevant operation.
- **A42372** — confidential multi-agent evaluation (Privacy-Protection): expose only abstracted diagnostics
  (scores + failure clusters), never raw trajectories; self-acknowledged-subjective LLM judge.
- **A37135** — PriAgent (Privacy-Protection): agentic auditor over untrusted logged content with a
  reviewer-flagged unimplemented injection gate; evidence-linked audit-trail (`audit_records`) pattern.
- **A42113** — speaker re-identification from anonymized child audio (Privacy-Protection; ECAPA-TDNN + EER,
  "ignorant" attacker only): "anonymized" ≠ unrecoverable.
- **A37125 / A40903** — covert channels invisible at the content layer (Network-Cyber-Security; author-reported
  Pe ≈ 0.5; non-adaptive): content-DLP over log egress is insufficient → gate destinations.
- **A42369** — VulnBench (Network-Cyber-Security; code github.com/ijakenorton/VulnBench): logged metrics
  inflatable by contamination/leakage → seal eval provenance.
- **A40815** — HyperGLLM (Network-Cyber-Security): ultra-long telemetry (1M+-token samples) → compress-then-
  reason without dropping mandatory-capture security events.
- **A37053** — DRMD (Network-Cyber-Security; arXiv:2508.18839): reject/defer as a first-class action → fail-
  closed applied to security-event capture.
- **A36959** — AutoMalDesc (Network-Cyber-Security; code github.com/CrowdStrike/automaldesc): verify-before-
  trust multi-signal provenance — corroborate before admitting a logged claim as evidence; LLM-judge
  disagreement caveat.
- **A40210** — CTFTiny / CTFJudge (Network-Cyber-Security): trajectory-level logging as the unit of assessment;
  LLM-judge needs calibration; decoding-hyperparameter sensitivity (execution-context capture).
- **A41065** — Resilience in Ambient Multi-Agent LLMs (Network-Cyber-Security): per-agent reputation as a
  runtime signal — captured but itself attackable (reviewer synthesis, not a trust shortcut).
- **A39975** — benign data-free reconstruction (Privacy-Protection): inversion-adjacent; reinforces
  "artifacts reconstruct".

**Contested / cautionary (cited as traps, not endorsements):**
- **A39307 / A39524 / A39338** (Privacy-Protection §2, §10) — "privacy by construction / data-locality" with no
  attack or accounting; gradient/digest sharing is a documented leak (A37743, A39333) → do not treat data
  locality as a logging-privacy guarantee.

## Evidence strength

- **Threat motivation (logged artifacts/sequences are recoverable secrets; agent can't self-redact; re-ingested
  fields inject): strong (convergent, multi-paper, cross-chunk).** The "model-derived artifacts are secrets"
  conclusion is `Privacy-Protection.md`'s most replicated cross-chunk finding (§9, ≥5 independent papers:
  A37743, A39333, A39212, A40839, A42453; plus A40720, A40100). The sequence-leak (A39710), agent-unawareness
  (A40874), and injection-surface (A42239, A37135) findings are individually single-study but mutually
  reinforcing. All author-reported, non-adaptive — a strong *case for the control*, not a measured efficacy.

- **The confidentiality/minimization construction (default-deny artifact logging, redaction/abstraction,
  structure-restricted noise, field-scoped read, allow-listed egress, sanitize-on-read): standard security
  engineering, NOT evaluated as a system in this corpus.** No paper builds or measures a secure-logging
  pipeline. Treat the construction as **requiring production validation on the target stack**, and treat any
  retained abstraction's protection as *reduced, not eliminated* (A42453 residual is the calibration).

- **Privacy-accounting and per-operation evidence design: moderate, corpus-consistent** (A39051, A39510, A40045,
  A40896, A40889 — directionally supported, formal-guarantee-without-executed-attack is pervasive
  (Privacy-Protection §12), so pair with red-team).

- **Retention/deletion honesty: strong negative evidence.** That purge ≠ erasure is well supported (A41120,
  A40047, A39373) — the *residual* is the finding, so "delete" claims must be scoped.

- **Adaptive-adversary assurance: none inherited.** Both syntheses flag near-universal absence of adaptive,
  defense-aware evaluation, and Privacy-Protection §11 states demonstrated bypasses are against *other* schemes
  under the bypasser's own eval; no corpus paper red-teams a secure-logging layer. Every operational threshold
  here is an engineering target, and adaptive red-team is a launch gate.

- **Calibration:** claims are stated as "reduces recoverable residue against the tested, non-adaptive attacks"
  and "requires production validation" — never "private/secure/unrecoverable/proven-safe".

## When NOT to use this pattern

- **When the log genuinely contains no sensitive, model-derived, or personal content and no re-ingestion
  reader.** For a purely synthetic, non-personal, human-only-read debug log with no artifacts and no
  compliance need, the full minimization/redaction/egress apparatus is over-engineering — a plain log plus
  `tamper-evident-traces.md` (if integrity matters) suffices. The corpus prioritizes this control where the log
  carries recoverable artifacts (Privacy-Protection §9), a decision sequence (A39710), or is re-read by a model
  (A42239).

- **As a substitute for tamper-evidence.** Secure logging governs *what is in the log and who can read it*, not
  *whether the record was altered*. Deploying it instead of `tamper-evident-traces.md` leaves the record
  rewritable; the two are co-required, not interchangeable.

- **As a substitute for the upstream controls.** It does not stop the injection that caused a bad action
  (`prompt-injection-containment.md`), decide allow/deny (`policy-permission-gates.md`), bound blast radius
  (`tool-capability-isolation.md`, `sandboxed-execution.md`), or authorize reads
  (`retrieval-authorization.md`). It records those safely; using it *in place of* them is a misuse.

- **When you cannot enforce read/egress access control below the application layer.** Application-layer "only
  admins read" over a broadly readable store gives false assurance (Privacy-Protection §3 honest-but-curious
  reader). If the environment cannot provide storage/IAM-layer field-scoped read and destination allow-listing,
  document the residual disclosure risk explicitly rather than claim "secure logging".

- **When "delete = erased" or "anonymized = unrecoverable" must be *guaranteed*.** The corpus shows both are
  approximate (A41120, A40047, A39373; A42113). If a hard, provable-erasure or provable-anonymity guarantee is
  a requirement, this pattern cannot supply it — scope the claim to risk-reduction with a disclosed residual,
  or use a formal-erasure/formal-privacy control (`differential-privacy.md`) with its own validated accounting.

- **When minimization would starve mandatory security-event capture.** If a deployment's constraints force
  dropping security events (A42249, A42239) to satisfy minimization, the balance is wrong: the fail-closed
  completeness edge is non-negotiable, and a design that can only satisfy one edge should be revisited, not
  shipped half-applied.
