# Pattern: Tamper-Evident Traces

> **Scope of evidence.** This pattern is grounded in the AAAI-26 corpus syntheses `Network-Cyber-Security.md`
> and `Defense-Mitigation.md` and their underlying research cards. Load-bearing papers: **A42249** (Capable and
> Secure Autonomous Computer-Use Agents — agent self-reports are untrustworthy: "hallucinated task completion
> masks skipped steps", so *independent end-state verification is required*, and interaction-by-interaction +
> video logs are the audit evidence), **A40210** (CTFTiny / CTFJudge — trajectory-level, per-step evidence
> logging is the unit of agent assessment, LLM-as-judge needs calibration/anti-gaming, and decoding
> hyperparameters make runs non-deterministic), **A37924** (GhostCert — "a verification artifact is not a
> correctness oracle"; a certificate/score/signature can be spoofed, so a signed record attests *provenance,
> not correctness*), **A41134** (IMBIA / Shadows in the Code — a *compromised internal agent* defeats
> user-level controls, so the component that writes the trace may itself be malicious → the corpus
> recommendation is *cryptographic agent provenance/attestation*). The single most important framing is
> **reviewer synthesis** from `Network-Cyber-Security.md` §3: the recurring *implicit* assumption across the
> detector/telemetry papers is **trusted inputs, telemetry, and labels** — data integrity, label provenance,
> and pipeline trust are assumed non-adversarial. Tamper-evident traces exist precisely to remove that
> assumption. Supporting: A42369 (VulnBench — recorded evaluation metrics can be contaminated/leakage-inflated),
> A42364 (GNN-AID — experiment-tracking/interpretability-console blueprint, no security eval), A39818
> (TowerMind — invalid-action rate as a cheap runtime health signal), A41065 (Ambient Multi-Agent — reputation/
> trust is a runtime signal but is itself an attackable trust surface), A39732 (STRUM/GTAE — a
> robustness-aware aggregation weight is a gameable surface; every new trust-decision surface is attackable),
> A40100 / A39721 (offloaded inference leaks input via activations / routing → a trace store carries sensitive
> intermediate state), A41145 (CoSPED — model editing / ROME as targeted erasure → dual-use caution for
> "evidence deletion"), A36959 (verify-before-trust multi-signal label provenance), A40815 (ultra-long
> telemetry, 1M+-token samples → compress-then-reason), A42239 (any model-visible field is an injection
> surface → a re-ingested trace is an injection surface).
>
> **Evidence integrity (non-negotiable).** Every quantitative value below is **author-reported and not
> independently verified**; where a card was silent the text says "not stated in paper". Numbers are tagged
> author-reported vs. reviewer synthesis. **No paper in either synthesis builds, deploys, or measures a
> cryptographic tamper-evident logging system** (hash-chaining, Merkle trees, append-only WORM storage,
> transparency logs, external anchoring). The corpus supplies the *threat motivation*, the *audit-substrate
> framing*, and the *central caution* — it does **not** supply an empirical evaluation of tamper-evident
> traces. Accordingly, the cryptographic construction in this pattern is presented as **standard security
> engineering that requires production validation on the target stack**, not as a corpus-measured result.
> Calibrated language only — "reduces the class of undetectable tampering under the stated threat model",
> "requires production validation" — never "immutable / unforgeable / proven-safe / secure". The strongest
> cross-corpus caveat, repeated below: **no defense in either synthesis was evaluated against an adaptive,
> defense-aware attacker**, so treat every efficacy number as an upper bound. This pattern is scoped to
> *making the record of what an agent did detectably-tamper-resistant and independently corroborated*; the
> upstream *allow/deny/step-up action decision* is `policy-permission-gates.md`, capability minimization and
> execution isolation are `tool-capability-isolation.md` and `sandboxed-execution.md`, injection containment is
> `prompt-injection-containment.md`, and the human sign-off surface is
> `human-approval-consequential-actions.md`. A tamper-evident trace is the evidentiary substrate those controls
> are audited against.

---

## Problem addressed

An autonomy console, a policy gate, and an incident review all depend on **a record of what the agent
actually did**. If that record can be silently altered, omitted, or fabricated — by the agent, by a
compromised peer agent, by an attacker who reached the log, or by an insider — then every downstream control
is auditing a story the adversary controls. The corpus makes three parts of this concrete and load-bearing:

- **The agent's own account of what it did cannot be trusted.** A42249 reports (author-reported, small-n,
  version-bound) that computer-use agents exhibit **hallucinated task completion that masks skipped or unsafe
  steps** — the agent reports success while having done something else, or nothing. The card's direct
  implication: *completion self-reports are not evidence; independent end-state verification is required.* A
  trace built only from the agent's self-narration inherits the agent's unreliability.

- **The component that writes the trace may itself be malicious.** A41134 (IMBIA) shows that a **compromised
  internal agent (BU-MA) defeats user-level guardrails** — author-reported, the defense's ASR reduction under
  BU-MA is only 7% vs. 40% under a malicious-user (MU-BA) scenario — and that a tester agent can silently add
  a `send_email` exfiltration primitive to generated software. If a compromised agent can also author or
  amend the audit log, the log is worthless. The card's recommendation is exactly **cryptographic agent
  provenance/attestation** so the origin of each recorded action is bound to an attested identity.

- **A signature or certificate on the record proves provenance, not correctness.** A37924 (GhostCert)
  demonstrates (under a white-box, known-noise-level threat model) that a **verification artifact is not a
  correctness oracle**: a large certified radius can be assigned to a *wrong* class with imperceptible,
  semantics-preserving perturbation (author-reported spoofing ASR 30–100% vs. ~30–65% for the Shadow-Attack
  baseline). The transferable caution: a tamper-*evident* trace tells you the record was not altered after
  writing; it does **not** tell you the recorded claim was true. Do not gate a correctness decision on the
  mere existence of a signed trace.

Underneath all three sits the reviewer-synthesis framing from `Network-Cyber-Security.md` §3: across the
detector and telemetry papers the recurring *implicit* assumption is **trusted inputs, telemetry, and
labels** — provenance and pipeline trust are assumed non-adversarial. **Tamper-evident traces are the
control that removes that assumption for the audit record itself.** The goal is not confidentiality and not
correctness; it is **integrity + provenance + non-repudiation of the evidence**: given a trace, an
independent reviewer can detect (a) any post-hoc alteration or deletion of an entry, (b) any gap or reorder
in the sequence, and (c) which attested identity authored each entry — and can corroborate the agent's
claims against independently observed end-state, so that "the agent said it succeeded" and "the world
actually changed as claimed" are recorded and reconciled separately.

## Applicable assets and attack surfaces

- **The autonomy / trajectory trace itself** — the per-step record of observations, decisions, tool calls,
  arguments, and outcomes. A40210 establishes the **trajectory (not pass/fail) as the unit of agent
  assessment** and A42249 records **interaction-by-interaction plus video logs as audit evidence**; this
  record is the primary protected asset.

- **Policy-gate decision records** — every allow/deny/step-up decision emitted by `policy-permission-gates.md`
  and every human sign-off from `human-approval-consequential-actions.md`. If these can be back-dated or
  removed, an unauthorized action can be made to look authorized after the fact.

- **Independent end-state observations** — the out-of-band checks that corroborate or contradict the agent's
  self-report (A42249: "independent end-state verification"). These are a distinct, high-value asset because
  they are the only entries not authored by the agent under audit.

- **The execution context needed to attribute or reproduce a run** — model id, decoding hyperparameters,
  seeds, tool/skill versions, prompt/template hashes. A40210 shows runs are **non-deterministic and sensitive
  to decoding hyperparameters**; without this context recorded, an investigator cannot distinguish tampering
  from ordinary non-determinism.

- **Recorded evaluation / benchmark results** — A42369 (VulnBench) shows recorded metrics are inflatable by
  **benchmark contamination, label leakage, and identifier-encoded labels** (author-reported: threshold
  optimization improved F1 in 100% of model-dataset combinations; synthetic Juliet F1 0.900 vs. real-world
  DiverseVul 0.307). A metrics record that omits split provenance and leakage controls is a tamperable claim
  about capability.

- **Runtime health signals** — invalid-action rate (A39818), off-policy/out-of-allow-list selections (A42239),
  divergence between agent-claimed and actual completion (A42249), per-agent reputation shifts (A41065). These
  are both telemetry to protect and the tripwires that reveal tampering.

- **The trace *as re-ingested content*** — a summarizer, an LLM-judge (A40210), or a downstream agent that
  reads the trace. A42239 establishes that **any model-visible field is an injection surface**; a poisoned
  log entry becomes a prompt-injection payload for whatever later reads it. The trace is both evidence and
  attack surface.

- **Sensitive intermediate state captured in the trace** — activations, routing metadata, retrieved content,
  tool payloads. A40100 (activation inversion under server+client collusion) and A39721 (expert-selection
  access-pattern leak) show intermediate state leaks input semantics; a verbose trace store is a
  confidentiality liability, so tamper-evidence must be designed alongside least-privilege read access.

## Threat model

Designed for adversaries who want the **record to lie** — to hide an action that happened, invent one that
didn't, alter arguments/outcomes, or destroy evidence — after or during execution. The agent is treated as
**untrusted-by-default** (A42249 hallucinated completion; A41134 compromised internal agent). Grounded threat
classes:

- **Fabricated success / omission by the acting agent.** The agent reports completion it did not achieve, or
  never records a step it took (A42249, author-reported hallucinated completion; and 100% unauthorized-install
  in certain planning tasks — an action that must appear in the record whether or not the agent narrates it).

- **Compromised or malicious writer.** A peer/tool/sub-agent in the pipeline authors or amends entries to
  cover an exfiltration or unsafe action (A41134 BU-MA; the tester agent silently adding `send_email`). The
  writer's *identity* on each entry is the disputed fact.

- **Post-hoc alteration / deletion / reordering** of entries by anyone who reaches the store — external
  attacker, insider, or the operator. (Standard log-tampering; the corpus does not measure it directly, but
  §3 reviewer synthesis names "trusted telemetry" as the unguarded assumption this threat exploits.)

- **Verifier / signature gaming.** An adversary produces a record that *passes* the integrity check while
  being false — the direct generalization of A37924's certificate spoofing to any artifact a downstream gate
  keys on. "The trace verifies" must not be read as "the trace is true".

- **Evaluation-record contamination.** Recorded metrics are inflated by leakage/contamination so the trace
  overstates capability or safety (A42369).

- **Trust-surface gaming of the logging layer itself.** Any reputation, sampling, or robustness weight the
  trace pipeline introduces becomes a target: A39732 shows a robustness-aware aggregation weight is gameable
  (a client appears locally robust while poisoning globally); A41065's reputation weights are, by reviewer
  synthesis, themselves attackable. The tamper-evidence mechanism is a new trust-decision surface and must be
  threat-modeled as one.

- **Log-as-injection.** A poisoned entry attacks whatever re-reads the trace (A42239).

- **Evidence-erasure tooling misuse.** Targeted-editing/erasure capabilities intended for incident containment
  (A41145 ROME, author-reported extraction 65.2% → 1.6%) are dual-use: the same primitive can destroy
  evidence. Erasure paths are in-scope for the threat model, not just the response plan.

**Out of scope for this pattern (handled by siblings):** stopping the injection that caused the bad action
(`prompt-injection-containment.md`), deciding whether the action is allowed (`policy-permission-gates.md`),
bounding blast radius of execution (`tool-capability-isolation.md`, `sandboxed-execution.md`). Tamper-evident
traces assume those may fail and ensure the *failure is recorded truthfully and detectably*.

**Adaptivity boundary (critical).** Both syntheses flag near-universal absence of adaptive, defense-aware
evaluation. No corpus paper red-teams a logging/attestation layer. Every design target in this pattern is
therefore an **engineering invariant to be validated**, not a corpus-measured efficacy number.

## Control mechanism

Tamper-evidence is a **structural, deterministic property of how the record is written and read**, not a
model verdict and not a confidentiality mechanism. Five composable mechanisms:

1. **Append-only, hash-chained ordering (core control, standard engineering — not corpus-measured).** Each
   entry commits to the cryptographic hash of the previous entry (a linked hash chain; batch entries under a
   Merkle root for efficient inclusion proofs). Any alteration, deletion, or reorder breaks the chain and is
   detectable by recomputation. This is the mechanism that turns "trusted telemetry" (§3 reviewer synthesis,
   the assumption to remove) into *verifiable* telemetry. The corpus motivates it; it does not measure it —
   flagged per Evidence integrity.

2. **Writer attestation / provenance binding (grounded in A41134).** Every entry is signed by an *attested
   writer identity* — a workload/agent identity established out of band (see `agent-identity.md`), not a
   self-asserted name. This directly implements the A41134 recommendation of **cryptographic agent
   provenance/attestation** and defends the BU-MA case: a compromised agent cannot forge another identity's
   signature, and non-repudiably owns what it did write. The signing key is held by the runtime/attestation
   layer, not by the agent's tool-callable surface.

3. **Independent end-state corroboration (grounded in A42249).** For every consequential action, the trace
   records **two separately-authored facts**: the agent's claimed outcome *and* an out-of-band observation of
   the resulting world-state, plus their divergence. A42249's finding — self-reports mask skipped steps — is
   encoded as a first-class schema requirement, not an optional field. Divergence is a monitored signal
   (see Telemetry).

4. **Execution-context capture for attributability (grounded in A40210).** Each run records model id, decoding
   hyperparameters, seeds, tool/skill versions, and prompt/template hashes. Because A40210 shows runs are
   non-deterministic and hyperparameter-sensitive, this context is what lets a reviewer distinguish *tampering*
   from *legitimate non-determinism*; without it, integrity verification is unfalsifiable.

5. **Fail-closed write-gating.** A consequential action **does not proceed** unless its intent entry is durably
   written and chained first (write-ahead), and its outcome + end-state entries are written after. If the trace
   store is unreachable or the chain cannot be extended, the action is *deferred/denied*, not executed
   unlogged — the corpus's "reject/defer as a first-class action" posture (A37053) applied to the evidence
   layer. Availability of the record is a precondition for the action, so an attacker cannot buy invisibility
   by knocking out the logger.

**Sharp boundary (A37924).** These five give **integrity, provenance, ordering, corroboration, and
non-repudiation**. They do **not** give *correctness* of the recorded claim. A verified chain of signed
entries can still record a false-but-consistent story; correctness comes from the independent end-state
check (mechanism 3) and out-of-band signals, never from the signature alone.

## Preconditions and trust assumptions

- **An out-of-band writer-identity / attestation root exists.** Mechanism 2 assumes attested workload/agent
  identities and a signing root the agent's tool surface cannot reach. Grounded in A41134's provenance
  recommendation; see `agent-identity.md`. If identities are self-asserted, provenance is theatre.

- **The trace store enforces append-only at the storage layer, not just the API.** Write-once / WORM
  semantics or an external anchor must be enforced below the application, so that a compromised application
  identity cannot rewrite history. (Standard engineering; not corpus-measured.)

- **At least one corroboration source is independent of the acting agent.** A42249's end-state verification is
  only meaningful if the observer is not the same untrusted component that made the claim. This is the
  honest-independence assumption; if the "verifier" is the agent, the control collapses.

- **Clock / ordering source is trustworthy enough to sequence entries.** Hash-chaining gives *relative* order;
  wall-clock timestamps are advisory and themselves tamperable. Trust ordering from the chain, not from
  timestamps.

- **The verification/attestation layer is itself a trust-decision surface and will be attacked** (A39732,
  A41065 reviewer synthesis). It must be hardened, monitored, and kept minimal; adding it does not remove
  trust, it relocates trust to the signing root and the storage guarantee.

- **No adaptive-adversary validation is inherited from the corpus.** Every efficacy expectation here is a
  design target requiring production red-teaming (both syntheses, §on adaptive evaluation).

- **Confidentiality is a separate, co-required control.** Because traces carry sensitive intermediate state
  (A40100, A39721), tamper-evidence must be deployed *with* least-privilege read access and, where
  appropriate, field-level minimization/encryption — otherwise the integrity control creates a
  confidentiality liability.

## System architecture

A minimal, deterministic evidence pipeline sitting beside the agent runtime and the policy gate:

```
                      ┌─────────────────────────────────────────────┐
   agent runtime ───► │  Trace Recorder (in runtime, least-priv)     │
   (untrusted)        │  - canonicalize entry (stable serialization) │
   policy gate  ───►  │  - attach attested writer identity           │
   human sign-off ──► │  - compute entry hash, link prev-hash        │───► signed, chained
   end-state probe ─► │  - WRITE-AHEAD before consequential action   │      append-only entry
                      └───────────────┬─────────────────────────────┘
                                      │ (fail-closed: no durable+chained write ⇒ defer/deny action)
                                      ▼
                      ┌─────────────────────────────────────────────┐
                      │  Append-only / WORM store  (write-once)      │
                      │  + periodic external anchor (Merkle root)    │  ◄── operator cannot silently rewrite
                      └───────────────┬─────────────────────────────┘
                                      │
             read path (untrusted-on-read, A42239: sanitize before LLM sees it)
                                      ▼
      ┌──────────────┐   ┌───────────────────────┐   ┌─────────────────────────┐
      │ Verifier      │   │ Autonomy/Trace console │   │ Incident review / export │
      │ recompute     │   │ (A42364 blueprint;     │   │ (independent auditor,    │
      │ chain + sigs  │   │  A40210 trajectory view)│   │  inclusion proofs)       │
      └──────────────┘   └───────────────────────┘   └─────────────────────────┘
```

- **Writer separation.** The recorder runs *in the runtime/control plane*, holding the signing key; the agent
  emits *proposed* entries but cannot sign or reach the store directly. This encodes A41134: a compromised
  agent authors content non-repudiably under its own identity but cannot forge another's or rewrite history.

- **Write-ahead + fail-closed coupling to the action.** The intent entry is chained *before* the consequential
  action executes; the store's availability gates the action (mechanism 5). This is the point that stops
  "act now, log never".

- **Append-only store + external anchor.** Write-once storage prevents in-place edits; periodically publishing
  the current Merkle root to an independent location prevents even the operator from silently rewriting the
  whole log (a multi-party integrity posture loosely analogous to A40925's "no single party can act alone" —
  cited as analogy, not as a measured A40925 result). Standard engineering; not corpus-measured.

- **The console is a *reader*, and readers are untrusted-on-read.** A42364 (GNN-AID) is the corpus's
  architectural blueprint for a unified attack/defense/trace-interpretability + experiment-tracking console —
  cited for structure only; the card reports **no security evaluation**. Any LLM summarizer/judge in the read
  path (A40210) must treat entry content as *data, not instructions* (A42239), per
  `prompt-injection-containment.md`.

- **Verifier is deterministic and stateless.** It recomputes hashes and checks signatures/inclusion proofs;
  it renders no model judgment about *correctness* (A37924 boundary).

## Recommended implementation pattern

Deterministic, fail-closed, least-privilege. Concretely:

- **Canonicalize before hashing.** Serialize each entry with a stable, canonical encoding (fixed field order,
  normalized whitespace/encoding) so the hash is reproducible; A40210's non-determinism warning applies to
  serialization too — an unstable encoding makes every re-verification a false tamper alert.

- **Chain every entry; anchor batches.** `entry_hash = H(canonical(entry) ‖ prev_hash)`; publish the periodic
  root externally. Include the writer's attested identity *inside* the hashed payload so provenance is part of
  what is sealed (A41134).

- **Record the A42249 triple for every consequential action:** (i) agent-claimed intent/outcome, (ii)
  independent end-state observation, (iii) divergence flag. Never collapse (i) and (ii) into one field.

- **Seal the decision trail, not just the action.** Chain the policy-gate decision
  (`policy-permission-gates.md`) and human sign-off (`human-approval-consequential-actions.md`) as their own
  attested entries, so "who authorized this" is non-repudiable and cannot be back-filled.

- **Capture execution context on every run** (model id, decoding params, seeds, tool/skill/prompt-template
  hashes) — A40210. This is what makes a disputed run attributable and reproducible.

- **Seal evaluation records with their provenance.** When a trace records a benchmark/eval result, seal the
  split identity, leakage-control status, and identifier-anonymization status alongside the metric (A42369),
  so a recorded "score" cannot be silently detached from the conditions that make it meaningful.

- **Fail closed on write failure.** If the intent entry cannot be durably chained, *defer or deny* the action
  (A37053 reject/defer applied to evidence). Log the deferral itself.

- **Least-privilege on the store.** Writers: append-only, no delete/overwrite. Readers: scoped, audited,
  minimized fields (A40100/A39721 confidentiality). No principal — including the agent and the operator
  application identity — holds delete/rewrite on historical entries.

- **Sanitize on read.** Before any LLM (summarizer, judge, downstream agent) ingests trace content, treat it
  as untrusted data (A42239) via `prompt-injection-containment.md`.

- **Compress high-volume telemetry without breaking the chain.** For ultra-long traces (A40815: 1M+-token
  samples), chain a *hash-committed* raw entry and store a derived summary that references it — never replace
  the sealed raw entry with a lossy summary as the source of truth.

- **Corroborate high-stakes claims with multiple signals before trusting them** (A36959 verify-before-trust:
  cross-signal agreement + threshold before admitting a claim; A40210 LLM-judge needs calibration). A single
  signed entry is provenance; a corroborated entry is closer to evidence.

## Incorrect or fragile implementation patterns

- **Trusting the agent's self-narration as the trace.** Directly refuted by A42249 (hallucinated completion
  masks skipped steps). A log the agent writes about itself, with no independent end-state check, records the
  agent's story, not the facts.

- **Letting the acting agent (or a peer agent) sign or amend history.** A41134 BU-MA: a compromised writer
  neutralizes the record. Signing must live in the control plane, not the agent's tool surface.

- **Gating a correctness decision on "the trace is signed/verified".** The A37924 error transplanted:
  signature ≠ truth. A downstream gate that treats a verifying trace as a correctness certificate can be fed a
  false-but-consistent record.

- **Log-after-act.** Executing the consequential action first and logging as a side effect lets any failure or
  attacker drop the record. The intent entry must be write-ahead and chained *before* the action (mechanism 5).

- **Timestamp-ordered "immutability".** Relying on wall-clock timestamps for ordering/immutability; timestamps
  are tamperable and give no cross-entry binding. Order must come from the hash chain.

- **Application-layer "append-only" over a mutable store.** If the underlying store permits in-place edit/
  delete under the application identity, "append-only" is a convention an attacker with that identity ignores.
  Enforce write-once at the storage layer + external anchor.

- **A verbose trace with broad read access.** Turns the integrity control into a confidentiality breach —
  activations/routing/retrieved payloads leak (A40100, A39721). Integrity without least-privilege read is a
  net regression.

- **Feeding raw trace text straight into an LLM reader.** A poisoned entry injects the summarizer/judge
  (A42239). Un-sanitized read paths re-weaponize the evidence store.

- **Treating a new reputation/robustness/sampling weight in the trace pipeline as trustworthy.** A39732 (and
  A41065 reviewer synthesis): these are gameable surfaces. A "trust score" attached to entries is itself an
  attack target, not a shortcut around verification.

- **Sampling out "boring" entries to save space.** Selective omission is indistinguishable from tampering and
  breaks the chain's completeness guarantee; compress (hash-committed) rather than drop (A40815).

- **Exposing a broad erasure/edit capability for "cleanup".** Erasure tooling (A41145 ROME, dual-use) on the
  evidence store is an evidence-destruction primitive; if legal retention/redaction is required, use a sealed
  redaction that preserves a tombstone + hash of the removed content, never a silent delete.

## Verification strategy

- **Continuous chain + signature verification.** A stateless verifier recomputes `entry_hash` over the chain,
  checks each writer signature against the attestation root, and validates inclusion of each externally
  anchored root. Any break localizes the first altered/missing entry. (Design invariant; not corpus-measured.)

- **Independent-observer reconciliation.** For a sample (and all high-stakes actions), compare the recorded
  agent-claim against the recorded independent end-state and against reality where re-observable (A42249).
  Persistent claim-vs-end-state divergence is a tamper/failure indicator.

- **Non-determinism-aware replay.** Using the sealed execution context (A40210), re-run or re-derive where
  feasible; discrepancies within recorded decoding/seed variance are expected, discrepancies outside it are
  suspect. This separates tampering from legitimate stochasticity.

- **Eval-provenance audit.** For recorded metrics, verify the sealed split/leakage/anonymization provenance
  (A42369) so a "score" cannot be trusted without its conditions.

- **Adaptive red-team of the logging layer (launch gate).** Because no corpus paper red-teams a logging/
  attestation layer, an explicit adaptive exercise is required: attempt omission, reorder, back-dating, writer
  spoofing, chain-forking, external-anchor bypass, and log-as-injection. Treat pre-red-team numbers as upper
  bounds (both syntheses' adaptive-evaluation caveat).

- **Corroboration-before-trust for claims used in decisions** (A36959): require agreement across independent
  signals + a confidence threshold before a recorded claim is admitted as evidence to a gate.

## Metrics and thresholds

*Operational invariants below are engineering targets requiring production validation — not corpus-measured
efficacy. Author-reported corpus numbers are labeled and are motivational, not measurements of this pattern.*

- **Chain-verification pass rate = 100% expected; any single failure is a P1 integrity incident** (a break is
  binary — one altered/missing entry fails the chain). Threshold: 0 unverified/unsigned writes admitted.

- **Unlogged-consequential-action rate → target 0** (fail-closed invariant, mechanism 5). Any consequential
  action without a preceding chained intent entry is a control failure.

- **Claim-vs-end-state divergence rate** (A42249) — track as a first-class metric; a rising divergence rate is
  both a reliability signal and a tamper indicator. Baseline is corpus-motivated by A42249's hallucinated-
  completion finding (qualitative; exact rate "not stated in paper").

- **Writer-attestation coverage = 100% of entries carry a verifiable attested identity** (A41134). Any
  self-asserted/unattested writer is rejected.

- **External-anchor freshness** — max age of the most recent published root below a set bound; a stale anchor
  widens the silent-rewrite window.

- **Invalid-action rate / off-policy-selection rate** as runtime health tripwires (A39818; A42239) — spikes
  correlate with the conditions under which fabricated records appear.

- **Corpus reference numbers (author-reported; motivation, not this pattern's efficacy):** GhostCert
  certificate-spoofing ASR 30–100% (A37924) — why a signature is not correctness; IMBIA BU-MA defense ASR
  reduction 7% vs. 40% MU-BA (A41134) — why the writer must be attested; VulnBench threshold-optimization F1
  gain in 100% of combinations and Juliet 0.900 vs. DiverseVul 0.307 (A42369) — why eval records need sealed
  provenance; CoSPED extraction 65.2% → 1.6% via ROME (A41145) — the dual-use erasure caution. All
  author-reported, non-adaptive, single-study; do not restate as tamper-evidence results.

## Test cases

Functional / integrity (deterministic, must pass):

1. **Alter one field of a sealed entry** → verifier flags the exact entry; chain fails from that point.
2. **Delete an interior entry** → chain break detected at the successor; no silent renumbering possible.
3. **Reorder two entries** → hash linkage mismatch detected.
4. **Forge an entry under another writer's identity** → signature check fails (A41134 attestation).
5. **Unattested/self-asserted writer attempts a write** → rejected; 0% attestation-coverage gap.
6. **Consequential action attempted while trace store is unreachable** → action deferred/denied, deferral
   itself logged (fail-closed, A37053).
7. **Agent reports success but end-state probe shows no change** (A42249 hallucinated completion) → divergence
   flag set; both facts recorded separately.
8. **Log-as-injection:** an entry contains instruction-shaped text; a downstream LLM reader is driven to act
   → with sanitize-on-read (A42239) the reader treats it as data; test fails if the reader obeys it.
9. **Eval record without sealed split/leakage provenance** (A42369) → rejected or flagged non-admissible as
   evidence.
10. **Broad-read exposure of a trace carrying activations/routing** (A40100, A39721) → least-privilege read
    denies; minimized fields only.
11. **Replay within recorded decoding/seed context** (A40210) → discrepancies inside variance accepted,
    outside variance flagged.

## Adaptive adversarial tests

*Required because no corpus paper red-teams a logging/attestation layer; results are the real evidence, and
pre-test numbers are upper bounds (both syntheses' adaptive caveat).*

- **Adaptive omission:** attacker who knows the schema tries to make a real action produce no chained entry
  (race the write-ahead, crash the recorder mid-action, exploit a non-fail-closed path). Success = an
  unlogged consequential action.
- **Adaptive writer-spoofing / key reach:** attempt to obtain or misuse the signing capability from the
  agent's tool surface (A41134 threat: agent should never reach the signer).
- **Chain-forking / anchor-bypass:** maintain a "clean" chain shown to auditors while the real chain diverges;
  defeated only if external anchoring makes the fork detectable — test that it does.
- **False-but-consistent record (A37924 transplanted):** produce a fully verifying trace whose end-state claim
  is false; success unless the independent end-state check (A42249) contradicts it — validates that
  verification ≠ correctness is handled by corroboration, not signatures.
- **Trust-surface gaming (A39732, A41065):** if the pipeline attaches any reputation/robustness/sampling
  weight, attempt to appear trustworthy while poisoning — confirm the weight is not a verification shortcut.
- **Eval-record contamination (A42369):** inject leakage/identifier-encoded labels; confirm sealed provenance
  makes the inflation visible rather than trusted.
- **Evidence-erasure abuse (A41145 dual-use):** attempt to use redaction/cleanup tooling to remove an entry;
  confirm only tombstone+hash redaction is possible, never silent delete.

## Telemetry requirements

Signals to emit (and themselves seal into the chain):

- **Chain-verification status and first-failure locator** — continuous; any failure pages as P1.
- **Per-entry attested writer identity** (A41134) and attestation-coverage gauge.
- **Claim-vs-end-state divergence events and rate** (A42249) — the primary fabricated-success tripwire.
- **Unlogged-consequential-action / write-fail-deferral counters** (fail-closed health, A37053).
- **Invalid-action rate and off-policy/out-of-allow-list selection rate** (A39818; A42239) — correlated with
  fabrication windows.
- **External-anchor freshness / last-published-root age.**
- **Read-path access audit** — who read which fields (A40100/A39721 confidentiality) and any LLM re-ingestion
  events (A42239).
- **Per-agent reputation/anomaly shifts** (A41065) — a *signal*, explicitly not a trust shortcut (reviewer
  synthesis: gameable).
- **Concrete egress/behavior signatures in recorded actions** — A41134's 12-behavior taxonomy (e.g.
  `send_email`, external-URL fetch, clipboard/keyboard capture, file encryption) doubles as detection
  signatures worth flagging in the trace.
- **Execution-context completeness** — fraction of runs with full model/decoding/seed/version capture (A40210);
  gaps make attribution impossible.

## Failure handling

- **Fail closed on the write path.** If an intent entry cannot be durably chained, the consequential action is
  **deferred/denied**, not executed unlogged (A37053 reject/defer). Availability of the record is a
  precondition for the action.
- **Fail loud, don't fail silent, on the read/verify path.** A chain-verification failure is surfaced as an
  integrity incident with the first-failure locator; the console must not render an unverified trace as
  trustworthy (A37924: don't let "it's shown" imply "it's verified/true").
- **Isolate a suspected-compromised writer.** On writer-anomaly (A41065 reputation shift; A41134 BU-MA
  indicators), quarantine that agent identity's future writes for review while preserving its sealed past
  entries as evidence — never delete them.
- **Corroborate before acting on a recorded claim** (A36959): a single divergence/anomaly triggers
  investigation, not automated destructive response, because the anomaly detector is itself fallible and
  gameable.
- **Degrade to more logging, not less, under uncertainty.** If integrity is in question, raise capture
  fidelity and human review; do not sample down (selective omission is indistinguishable from tampering).

## Rollback and containment

- **The trace is append-only; you roll back the *system*, not the record.** Containment removes the
  offending capability/agent (via `tool-capability-isolation.md`, `sandboxed-execution.md`,
  `policy-permission-gates.md`) and quarantines the writer identity — the historical entries stay sealed as
  evidence.
- **Targeted erasure only as tombstoned redaction.** Where legal/privacy retention forces removal of *content*,
  use a redaction that leaves a tombstone + hash of the removed payload so the chain stays intact and the
  removal is itself auditable. The A41145 ROME primitive (author-reported 65.2% → 1.6%) is cited as
  incident-containment *for the model's memorized content*, and as the explicit **dual-use caution**: never
  wire an equivalent silent-delete path into the evidence store.
- **External anchor is the rollback backstop.** If in-store history is suspected rewritten, the last
  independently-published Merkle root bounds what could have been altered and lets an auditor detect the
  divergence (multi-party integrity posture; loose analogy to A40925 "no single party acts alone" — analogy,
  not a measured result).
- **Preserve evidence through incident response.** Containment actions (quarantine, capability revocation,
  key rotation) are themselves recorded as attested entries, so the response is as auditable as the incident.

## Known bypasses

**Reviewer-identified (not demonstrated against a tamper-evident trace in the corpus — no such system is
evaluated there):**

- **False-but-consistent record.** A verifying chain can seal a false claim; the signature attests provenance,
  not truth (A37924, demonstrated for certificates under white-box + known-σ; transplanted here). Mitigated,
  not closed, by independent end-state corroboration (A42249).
- **Compromised-writer content.** Attestation makes a compromised agent *own* what it writes but does not make
  what it writes *true* (A41134 BU-MA). The record is honest about authorship, not about intent.
- **Unlogged action via a non-fail-closed path.** Any execution path that can act before/without a chained
  intent entry defeats the whole control; this is the highest-value bypass and the reason mechanism 5 is
  mandatory.
- **Trust-surface gaming.** A reputation/robustness/sampling weight in the pipeline is gameable (A39732;
  A41065 reviewer synthesis) — an attacker can look trustworthy while poisoning; such weights must never
  substitute for chain/signature verification.
- **Log-as-injection.** A poisoned entry attacks downstream LLM readers (A42239) — a bypass of the *review*,
  not the chain; mitigated by sanitize-on-read.
- **Evidence-erasure via dual-use tooling.** Cleanup/edit capabilities (A41145) can destroy entries if not
  restricted to tombstoned redaction.
- **Confidentiality leak as a side effect.** A verbose sealed trace can leak intermediate state (A40100,
  A39721) even while perfectly tamper-evident — an integrity control that creates a disclosure bypass.
- **Non-determinism as cover.** Without sealed execution context (A40210), an attacker can attribute a planted
  discrepancy to "the model was stochastic".

**Corpus adaptivity caveat:** none of the above has been evaluated against an adaptive attacker targeting a
tamper-evident logging layer — that evaluation is a launch gate, not a corpus deliverable.

## Residual risks

- **Correctness is never established by the trace** (A37924). Tamper-evidence + corroboration narrows, but does
  not eliminate, the gap between "recorded and verified" and "true".
- **Corroboration is only as good as the independent observer** (A42249). Where end-state cannot be
  independently observed, the agent-claim stands uncorroborated.
- **The signing root and storage guarantee are concentrated trust.** Compromise of the attestation key or the
  write-once guarantee undermines everything downstream; this pattern relocates trust, it does not remove it
  (reviewer synthesis, generalizing A39732/A41065's "new trust surface" caution).
- **Insider / operator with storage-layer control** remains the hardest residual; external anchoring bounds
  but does not eliminate silent rewrite, and the anchor destination is its own dependency.
- **Confidentiality vs. completeness tension** (A40100, A39721): the more faithfully you seal, the more
  sensitive state you retain — residual disclosure risk scales with trace fidelity.
- **No adaptive-adversary assurance is inherited** — the dominant residual across both syntheses; all targets
  require production validation.
- **Metric/eval records can still mislead** if provenance sealing is incomplete (A42369).

## Relevant research (stable paper ids from the syntheses/cards)

**Load-bearing (motivation, substrate, and the central caution):**
- **A42249** — Towards Capable and Secure Autonomous Computer-Use Agents (AAAI-26 Student Abstract): hallucinated
  task completion masks skipped steps → *independent end-state verification required*; interaction + video logs
  as audit evidence. Author-reported, small-n, version-bound.
- **A40210** — Offensive Security LLM Agents / CTFTiny + CTFJudge (AAAI-26; code
  github.com/NYU-LLM-CTF/CTFJudge, data github.com/NYU-LLM-CTF/CTFTiny): trajectory-level (not pass/fail)
  evidence as the audit unit; LLM-judge needs calibration/anti-gaming; decoding-hyperparameter sensitivity
  (non-determinism).
- **A37924** — GhostCert / "Certified but Fooled!" (AAAI-26; code github.com/ghostcert): a verification
  artifact is not a correctness oracle; certificate spoofing ASR 30–100% (author-reported, white-box + known-σ).
- **A41134** — IMBIA / Shadows in the Code (AAAI-26; arXiv:2511.18467; code github.com/wxqkk0808/IMBIA):
  compromised internal agent (BU-MA) defeats user-level controls (ASR reduction 7% vs. 40% MU-BA); recommends
  cryptographic agent provenance/attestation; 12-behavior egress taxonomy.
- **`Network-Cyber-Security.md` §3 (reviewer synthesis)** — the implicit "trusted inputs/telemetry/labels"
  assumption this pattern removes.

**Supporting:**
- **A42369** — VulnBench (AAAI-26; code github.com/ijakenorton/VulnBench): recorded metrics inflatable by
  contamination/leakage/identifier-encoded labels → seal eval provenance.
- **A42364** — GNN-AID (AAAI-26; code github.com/ispras/GNN-AID): unified attack/defense/interpretability +
  experiment-tracking console blueprint; **no security evaluation** (architecture only).
- **A39818** — TowerMind (AAAI-26): invalid-action rate as a cheap runtime health signal.
- **A41065** — Resilience in Ambient Multi-Agent LLMs (AAAI-26): reputation/trust runtime signal + gossip
  isolation; reputation weights themselves attackable (reviewer synthesis).
- **A39732** — STRUM/GTAE (AAAI-26): a robustness-aware aggregation weight is a gameable trust surface →
  every new trust-decision surface is attackable. Preliminary evidence.
- **A40100** — FedSEA-LLaMA (AAAI-26; arXiv:2505.15683): offloaded inference leaks input via activations →
  trace stores carry sensitive intermediate state. Empirical privacy only.
- **A39721** — SecMoE (AAAI-26): expert-selection access pattern leaks input → routing metadata in traces is
  sensitive. Semi-honest only.
- **A41145** — CoSPED (AAAI-26; arXiv:2510.11137): ROME model-editing/erasure (65.2% → 1.6%,
  author-reported) — incident-containment primitive and the dual-use evidence-erasure caution.
- **A36959** — AutoMalDesc (AAAI-26; code github.com/CrowdStrike/automaldesc): verify-before-trust multi-signal
  provenance (cross-signal agreement + threshold) — corroborate before admitting a claim as evidence.
- **A40815** — HyperGLLM (AAAI-26): ultra-long telemetry (1M+-token samples) → compress-then-reason without
  dropping sealed raw entries.
- **A42239** — Obedience or Vigilance? (AAAI-26): any model-visible field is an injection surface → a
  re-ingested trace is an injection surface (sanitize-on-read).

**Loose analogy (cited as analogy, not as a measured result):** **A40925** — Consensus Learning with
Multi-Party Perturbation Triggers (AAAI-26): "no single party can act alone" motivates external anchoring /
multi-party integrity; residual ~15% Acc-Fusion (author-reported), non-adaptive.

## Evidence strength

- **Threat motivation: strong (convergent, multi-paper).** That agent self-reports are unreliable (A42249),
  that a compromised writer defeats naive controls (A41134), that signatures ≠ correctness (A37924), and that
  "trusted telemetry" is the unguarded assumption (§3 reviewer synthesis) are consistent across independent
  cards. All author-reported, single-study, non-adaptive — a strong *case for the control*, not a measured
  efficacy.
- **The cryptographic construction (hash-chaining, Merkle/WORM, external anchoring, writer attestation):
  standard security engineering, NOT evaluated in this corpus.** No paper builds or measures a tamper-evident
  agent-logging system. Treat the construction as **requiring production validation on the target stack**.
- **Corroboration + provenance-sealing design: moderate, corpus-consistent** (A42249 end-state verification,
  A41134 attestation, A42369 eval provenance, A36959 verify-before-trust) — directionally supported, not
  benchmarked as a unit.
- **Adaptive-adversary assurance: none inherited.** Both syntheses flag near-universal absence of adaptive,
  defense-aware evaluation; no corpus paper red-teams a logging/attestation layer. Every operational threshold
  here is an engineering target, and adaptive red-team is a launch gate.
- **Calibration:** claims are stated as "reduces the class of undetectable tampering under the stated threat
  model" and "requires production validation" — never "immutable/unforgeable/proven-safe".

## When NOT to use this pattern

- **When there is no consequential or auditable action.** For read-only, reversible, low-stakes agent behavior
  with no compliance or incident-review need, full hash-chained attestation is over-engineering; a plain log
  suffices. The corpus prioritizes this control where actions are consequential (A42249) or multi-agent/
  supply-chain risk exists (A41134).
- **When you cannot supply an independent end-state observer.** Without independence, the corroboration
  mechanism (A42249) collapses and you get provenance theatre; fix the independence gap first, or scope the
  claim to "provenance only".
- **When you have no out-of-band attestation root.** If writer identities are self-asserted, mechanism 2 is
  cosmetic (A41134); stand up `agent-identity.md` first.
- **As a substitute for the upstream controls.** A tamper-evident trace does not stop injection
  (`prompt-injection-containment.md`), does not decide allow/deny (`policy-permission-gates.md`), and does not
  bound blast radius (`tool-capability-isolation.md`, `sandboxed-execution.md`). It records what those controls
  did. Deploying it *instead of* them is a misuse.
- **As a correctness or confidentiality control.** It is neither (A37924 boundary; A40100/A39721 show it can
  *worsen* confidentiality if read access is broad). Use the appropriate sibling control for those goals.
- **When you cannot enforce storage-layer append-only / anchoring.** Application-layer "append-only" over a
  mutable store gives false assurance; if the environment cannot provide write-once + external anchoring,
  document the residual insider/operator-rewrite risk explicitly rather than claim tamper-evidence.
