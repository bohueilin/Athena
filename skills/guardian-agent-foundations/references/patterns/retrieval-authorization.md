# Pattern: Retrieval Authorization

> **Scope of evidence.** This pattern is grounded in the AAAI-26 corpus syntheses `Multi-keyword-match.md` and
> `Privacy-Protection.md` and their underlying research cards. Load-bearing papers on the **integrity /
> ingestion-injection** dimension: **A40462** (RAG2RAG, reasoning Detective+Judge gate anchored to a trusted
> source), **A40725** (ShieldRAG, safety-aware retriever hard-filtering above a threshold), **A37023**
> (DRIFTBENCH, adversarial evidence contamination of retrieval-augmented verification), **A38606** (CREAT,
> stealthy adaptive interaction-history/memory poisoning), **A40231** (MPAS, inter-agent message injection at
> topologically critical nodes), **A40189** (TAPA, shadow-verify → gate → rollback → human-Alert → provenance),
> **A41436** (DIG, per-fact provenance to source+extractor). Load-bearing on the **confidentiality /
> read-authorization** dimension: **A40188** (web agent concentrates LLM-inferred user data with no access
> control), **A40534 / A40911 / A40041** (keep raw private content off the untrusted model — provider-as-
> adversary), **A39710** (the decision/retrieval *sequence* itself leaks), **A40874** (SAPA-Bench, agents fail to
> recognize sensitive material in the action path), **A37135** (PriAgent, agentic auditing over untrusted
> retrieved input with an unimplemented injection gate), and the extraction findings **A40593 / A41230 / A40839 /
> A42453** (retrieved artifacts, prompts, and embeddings are extractable secrets). Supporting: A40004, A40616,
> A42372, A40206, A40498, A40913, A40773.
>
> **Evidence integrity (non-negotiable).** Every quantitative claim below is **author-reported and not
> independently verified**; where a card was silent the text says "not stated in paper", and where the
> extraction pipeline cut a value it says "truncated in extracted text". Numbers are tagged author-reported vs.
> reviewer synthesis. Calibrated language only — "reduced ASR against the tested attacks under the evaluated
> threat model", "requires production validation" — never "secure / proven-safe / eliminates". Two corpus-wide
> caveats govern this entire pattern: (1) **no defense in either synthesis was evaluated against an adaptive,
> defense-aware attacker**, so every efficacy number is an upper bound on real-world protection; and (2) **the
> corpus contains strong direct evidence for the *integrity* half of this pattern (RAG/inter-agent injection
> defenses) but only *motivating* evidence for the *confidentiality* half (papers showing read-side access
> control is absent, not papers implementing it)** — the document-ACL / least-privilege-retrieval design is
> therefore reviewer synthesis grounded in the papers' failure modes and `agent-identity.md`, and **requires
> production validation**.

---

## Problem addressed

An LLM agent that can *retrieve* — from a RAG corpus, a vector store, long-term memory, a tool that returns
records, or a peer agent's message — will (a) pull whatever the retriever surfaces into its context, and (b)
be steered by that content as if it were trustworthy instruction. The corpus establishes that **retrieval and
inter-agent channels are first-class attack surfaces, and that reasoning-based gating beats single-purpose
filters** (Multi-keyword-match §9, convergent across A40462, A40725, reinforced by A37023 and A38606 on the
ingestion boundary). Two independent, coupled failure surfaces motivate a dedicated authorization boundary at
retrieval time:

- **Integrity / injection: retrieved content is attacker-writable and is treated as instruction.** RAG and
  fact-checking pipelines assume the knowledge base is honest, but A40462 (RAG2RAG) and A40725 (ShieldRAG)
  model write/inject access to open knowledge bases; A37023 (DRIFTBENCH) models GenAI-driven claim diversity
  plus adversarial evidence contamination; A38606 (CREAT) poisons individual interaction histories under a
  stealth constraint that evades aggregate distribution-shift detectors; A40231 (MPAS) injects misinformation
  through inter-agent messages at topologically critical nodes. Reviewer synthesis (Multi-keyword-match §3):
  untrusted-retrieval-corpus / ingestion-boundary injection is the most operationally recurrent threat in the
  bucket.
- **Confidentiality / read-authorization: agents retrieve and re-emit data the requester was never entitled to
  see.** A40188 shows a personalized web agent that concentrates LLM-inferred user data (including
  demographics) with **no access control or minimization**; A40534 / A40911 / A40041 all exist because raw
  private content routinely reaches an untrusted external model that should never have seen it; A39710 shows
  that even when stored data is protected, the *sequence* of retrieval/decision leaks per-user outcomes; and
  A40593 / A41230 / A40839 / A42453 show that what is retrieved (prompts, latent attributes, soft prompts,
  "protected" embeddings) is itself an extractable secret. Reviewer synthesis: current agentic retrieval has
  essentially no read-side least-privilege — this is a design gap the corpus documents but does not solve.

**Retrieval authorization** is the deterministic enforcement point that decides, *before* retrieved content
enters the model's context window and *before* any action derived from it fires, two coupled questions: **may
this principal, for this declared purpose, receive this item at all** (read-authorization / confidentiality),
and **how much may this item be allowed to influence the agent given its provenance and integrity signal**
(ingestion-trust / integrity). Both decisions are keyed on authenticated inputs and a declared policy — not on
the model's own judgment of the content it just read.

## Applicable assets and attack surfaces

- **RAG / knowledge-base retrieval** — the primary surface. Retrieved passages are attacker-writable and
  carry seven-plus distinct attack types in one corpus taxonomy: targeted control, refusal DoS, blocker /
  jamming, adversarial-passage injection, and grammar-trigger backdoors (A40462); PoisonedRAG-/BadRAG-style
  corpus poisoning (A40725); adversarial evidence contamination of retrieval-augmented verification (A37023).
- **Long-term / episodic agent memory and interaction history** — A38606 (CREAT) poisons individual histories
  adaptively under a stealth constraint that defeats single-granularity, distribution-shift detectors; agent
  memory is "an unprotected asset" absent access control (A40188). Memory is a *read* surface (it feeds
  context) and a *write* surface (poisoning) simultaneously.
- **Inter-agent messages / shared blackboards** — A40231 (MPAS) treats a peer agent's message as untrusted,
  injecting at cut-vertex / critical nodes; "topology is a security parameter, not just a performance knob"
  (Multi-keyword-match §6). A message from a peer is retrieval from an untrusted source.
- **Tool / API results returned into context** — records, search results, decompiled code and strings
  (A37135 PriAgent runs LLM agents over attacker-influenced decompiled input), scraped web content. Any tool
  return is retrieved content that may carry an indirect injection.
- **Confidential source documents subject to per-principal access control** — cross-tenant records, above-
  clearance documents, PII, credentials. A40188 (no access control on inferred profiles), A40534 / A40911 /
  A40041 (raw private content must not reach the untrusted model), A42372 (raw trajectories must not be exposed
  to an evaluator). Reviewer synthesis: this is the least-privilege-on-the-corpus surface the corpus motivates
  but does not implement.
- **The retrieval / decision *trace* itself** — A39710 shows a feedback-driven arm-selection (retrieval /
  routing) sequence leaks per-user outcomes even when the datastore is protected; the pattern of *what was
  retrieved* is a side channel.
- **Retrieved model-derived artifacts** — prompts recoverable from outputs (A40004), soft prompts leaking
  membership with no output access (A40839, PIPRA avg AUC 87.58% vs 77.05% author-reported), latent sensitive
  attributes (A41230 FLAME), and "protected" face embeddings that still invert to impersonating identities
  (A42453). Treat any retrieved artifact as a first-class secret with egress control (Privacy-Protection §6).

## Threat model

Designed for **inference/runtime adversaries** who cannot change model weights but can write to, or steer
retrieval from, a corpus/memory/peer channel, or who can query the agent to extract what it retrieves.
Grounded threat classes:

- **Untrusted-corpus / ingestion-boundary injection** — attacker writes poisoned passages into an open
  knowledge base or lets them be scraped in (A40462, A40725, A37023). *Headline corpus finding:* this is the
  most recurrent threat, and single-purpose input filters are bypassable (Multi-keyword-match §3, §9).
- **Stealthy, adaptive memory/history poisoning** — attacker pollutes individual interaction histories with an
  RL policy tuned to stay under an aggregate anomaly detector (A38606 CREAT). Single-granularity detection is
  the documented failure mode.
- **Inter-agent message injection** — a backdoored or compromised peer agent injects misinformation at a
  topologically critical node (A40231 MPAS); harder cases are collusive.
- **Indirect prompt injection via any retrieved content** — instructions planted in documents, records, tool
  returns, or decompiled input that the agent reads and follows (A37135 runs over such input without an
  injection control — reviewer-flagged unimplemented gate).
- **Cross-principal / above-clearance read** — a query (possibly steered by injection) that pulls records the
  requesting principal is not entitled to; the confused-deputy pattern where an agent's broad corpus access is
  borrowed by an attacker (reviewer synthesis grounded in A40188's no-access-control finding and the provider-
  as-adversary framing of A40534 / A40911 / A40041 / A42232 in Privacy-Protection §3).
- **Retrieval-time exfiltration / extraction** — recursive topic-expansion and memory-driven query refinement
  to reconstruct a corpus (analogous to the extraction signals in Multi-keyword-match §14); prefix-conditioned
  membership queries (A40593); attribute inference from retrieved context (A41230); prompt/soft-prompt/embedding
  recovery (A40004, A40839, A42453).
- **Trace/sequence side channel** — inference from the *pattern* of retrievals even when each item is
  access-checked (A39710).
- **Verifier / trusted-source gaming** — poisoning the trusted value source the gate anchors to, or prompt-
  injecting the reasoning Judge (A40462 reviewer-anticipated next move); evading the safety scorer (A40725);
  crafting a peer message that passes the selective aggregator's reliability check (A40231).

**Adaptivity boundary (critical).** Multi-keyword-match §11 and Privacy-Protection §11 both flag that the large
majority of defenses here are evaluated on fixed, non-adaptive attack suites (A40462, A40725, A40231, A38606,
A37023 all note the untested adaptive case). Treat every efficacy number as best-case; adaptive, defense-aware
red-team is a launch gate, not optional (see Verification strategy).

## Control mechanism

Two deterministic decision functions evaluated at the retrieval boundary, both **before** retrieved content
reaches the model context and before any action derived from it fires:

```
read_auth(principal, roles, purpose, item, item_labels, tenant)      → { RETURN | REDACT | DENY }
ingest_trust(item, provenance, integrity_signal, source_trust_tier)  → { EVIDENCE(bounded) | QUARANTINE | ROUTE_TO_VERIFIER }
```

- **Read-authorization is a deterministic access decision over authenticated labels, not an LLM verdict on
  content.** Document-/row-level ACLs, tenant isolation, clearance, and purpose scope decide `RETURN / REDACT /
  DENY`. This is reviewer synthesis grounded in the corpus failure mode (A40188 has none) plus `agent-
  identity.md` (Zero Standing Privilege, just-in-time / just-enough, intent-based access, separate trust
  domains) and `architecture-patterns.md` P6. **Do not let an LLM decide sensitivity as the sole authority:**
  A40874 (SAPA-Bench) reports off-the-shelf MLLM agents recognize sensitive material with recognition accuracy
  **below 60% even with explicit hints** (best Gemini 2.0-flash ~67%, author-reported) — LLM sensitivity
  recognition is an *advisory* signal, never the access decision.
- **Ingestion-trust decides how much a retrieved item may influence the agent, by provenance tier.** Content
  from an authenticated, integrity-verified source may be admitted as evidence with bounded influence; content
  from an open/attacker-writable source is quarantined, or routed to a reasoning verifier before use (A40462
  Detective+Judge anchored to a trusted source; A40725 per-document safety score `s_θ(d)` hard-filtered above a
  threshold). Reasoning-based gating beats single-purpose filters (A40462 vs. the partial output-perturbation
  defenses of A40004/A38606), but the verifier must itself be hardened (see Preconditions).
- **Retrieved content is data, not instructions.** The admitted item is structurally separated from the
  instruction channel so the model cannot be "talked past" — the same structural-boundary requirement the
  action-side patterns depend on (cross-ref `policy-permission-gates.md`; A40231 per-agent message vetting).
- **Provenance is attached, not inferred.** Every returned item carries source + extractor provenance for
  downstream audit and containment (A41436 per-fact provenance to source+extractor; A40189 provenance chain).
- **Fail-closed.** On missing labels, unverifiable provenance, verifier error/timeout, ambiguous purpose, or
  budget exhaustion → `DENY` / `QUARANTINE` (redact-and-continue only for reversible low-stakes reads).
  Reviewer synthesis, consistent with the corpus-wide "single bypass not catastrophic" posture.

## Preconditions and trust assumptions

The gate is only as strong as these hold; each is a documented failure point:

- **Authenticated principal identity, roles, and purpose.** Read-authorization is meaningless without them
  (reviewer synthesis; `agent-identity.md` intent-based access — revoke on divergence from declared purpose).
  Spoofable role or purpose signals void the confidentiality half.
- **Correct, complete item-level access labels.** Every corpus item needs a trustworthy sensitivity/tenant/
  clearance label. A40188's failure is precisely the *absence* of such labels; where labels are missing the
  gate must fail closed, not guess. Label incompleteness is silent leakage (reviewer synthesis; analogous to
  A40484's "does not discover unknown sensitive correlations beyond the constrained set" in
  `policy-permission-gates.md`).
- **A trustworthy source-trust tier / provenance signal.** Ingestion-trust depends on knowing which sources are
  authenticated vs. attacker-writable (A41436 source+extractor provenance; A40189 provenance store). If
  provenance is forgeable, the tiering collapses.
- **A hardened verifier / trusted-source anchor.** The reasoning Judge (A40462), the safety scorer (A40725),
  the selective aggregator (A40231), and the shadow-sim fidelity + provenance store (A40189) are each **a new
  single point of trust that the corpus repeatedly leaves unhardened** (Multi-keyword-match §11 "New trust roots
  created by defenses"). A40462 shifts trust to a "value-based" corpus that can itself be poisoned; the Judge
  can be prompt-injected. If an LLM participates in the decision it must be advisory, not authoritative.
- **LLM-as-judge is both the measurement instrument and an attack target** (Multi-keyword-match §8/§12: A40498,
  A40913; Privacy-Protection §12: A40874 / A42372 / A40773 labels are partly model-generated). Any content-
  sensitivity or content-safety judgment is instrument-dependent and gameable.
- **A structural trust boundary separating retrieved content from executable instruction** (reviewer synthesis;
  A40231 message vetting; the "treat as data, not instructions" requirement carried across both syntheses).
- **Least-privilege corpus scoping already applied** — the agent's *standing* access to the corpus is minimized
  before the gate runs (`agent-identity.md` Zero Standing Privilege; `architecture-patterns.md` P6). The gate
  narrows a per-query view; it does not substitute for not granting broad standing corpus access in the first
  place.
- **Audit-store integrity** — provenance and decision logs must be tamper-resistant; the corpus asserts
  "immutable" provenance/audit but does not specify the integrity mechanism (A40189, A41436) — you must supply
  and verify it (reviewer synthesis).

## System architecture

Defense-in-depth aligned to the retrieval boundary — read-authorization and ingestion-trust are *both*
enforced before content reaches context, and a downstream action derived from retrieved content is still gated
by the action-side pattern (`policy-permission-gates.md`):

```
 query + principal + purpose
        │
        ▼
 [R0  Discovery / inventory]   every corpus, memory store, tool source, peer channel is registered with a
        │                       source-trust tier and item-label schema (architecture-patterns P13; A41436
        ▼                       provenance requires a known source set).
 [R1  Read-authorization]      DETERMINISTIC: per-item ACL / tenant / clearance / purpose check over
        │                       AUTHENTICATED labels → RETURN | REDACT | DENY. Fail-closed on missing labels.
        ▼                       (Reviewer synthesis grounded in A40188; agent-identity.md; P6.)
 [R2  Ingestion-trust gate]    per-item, keyed on provenance/source-trust-tier:
        │                        · authenticated source  → admit as EVIDENCE with bounded influence
        │                        · open/attacker-writable → QUARANTINE or ROUTE_TO_VERIFIER
        ▼                       (A40725 per-doc safety score hard-filter; A40462 Judge anchored to trusted src.)
 [R3  Reasoning verifier]      OPTIONAL, for quarantined/high-stakes items: reasoning judge emits a structured
        │                       verdict (admit / redact / drop + rationale). Advisory to a deterministic
        ▼                       admit/deny; run alongside the pipeline to bound latency (A40462; A40725 in-retriever).
 [R4  Provenance tagging]      each admitted item carries source+extractor provenance into context
        │                       (A41436; A40189 provenance chain).
        ▼
   model context ──► plan ──► [action-side policy gate] ──► side effect
        │                      (policy-permission-gates.md; A40189 shadow-verify→gate→rollback→Alert)
        ▼
 [R5  Immutable retrieval audit + async explanation]  every RETURN/REDACT/DENY/QUARANTINE logged with the
        │                                              policy fired, provenance, and rationale, generated async
        ▼                                              (A40189; A41436; architecture-patterns P10).
   red-team feedback → refine labels, tiers, verifier (P12).
```

- **The deterministic decisions (R1, R2's tier lookup) are the authority.** The reasoning verifier (R3) and any
  LLM sensitivity signal are advisory — they may force `REDACT`/`QUARANTINE`/`ROUTE_TO_VERIFIER` but must never
  be the sole basis for `RETURN`/`EVIDENCE` (rationale: A40874 low recognition accuracy; A40462/A40725 verifier
  is an unhardened trust root).
- **Latency mitigations are architectural**: co-trigger the verifier alongside retrieval (A40462), or bake the
  safety score into the retriever's shared encoder to avoid a separate detector hop (A40725); cache
  deterministic ACL/tier lookups; generate audit/explanation async (P10).

## Recommended implementation pattern

Deterministic, fail-closed, least-privilege — in priority order:

1. **Deny-by-default read-authorization per (principal, purpose, item-label).** Enumerate what each role/purpose
   may retrieve; everything else denies or redacts. This is the least-privilege spine for the confidentiality
   half (reviewer synthesis; A40188 shows the cost of its absence; `agent-identity.md` intent-based access,
   `architecture-patterns.md` P6). **Filter at retrieval time, before ranking returns items to context** — not
   as a post-hoc redaction of an already-assembled prompt.
2. **Tier sources by provenance and gate ingestion on the tier, not on the content's own claims.** Authenticated
   internal sources vs. open/attacker-writable sources get different influence budgets (A40725 per-document
   safety score `s_θ(d)` hard-filtered above a threshold; A40462 anchor to a trusted source). Content that
   asserts its own trustworthiness is exactly the injection pattern.
3. **Route quarantined / high-stakes retrieved content through a reasoning verifier that emits a structured,
   logged verdict** — reasoning-based gating outperforms single-purpose filters (A40462 Detective+Judge; A40725
   safety-aware retriever). Keep the verifier advisory to a deterministic admit/deny and hardened against
   injection of itself.
4. **Treat every retrieved item — including peer-agent messages and tool returns — as untrusted data,
   structurally separated from instructions** (A40231 per-agent message vetting; A37135's missing injection
   gate is the negative example). Never let retrieved text be concatenated into the instruction channel.
5. **Keep raw sensitive content off any untrusted downstream model; send only anonymized / abstracted /
   surrogate representations** — the closest in-corpus confused-deputy control (A40534 entity abstraction so raw
   KG data never reaches a third-party LLM; A40911 redact-then-recover surrogate; A40041 keep high-sensitivity
   prompts on the trusted edge). For confidential evaluation, expose only abstracted diagnostics, never raw
   trajectories (A42372).
6. **Attach source+extractor provenance to every admitted item** so downstream audit, containment, and
   attribution work (A41436 per-fact provenance for admissibility; A40189 provenance chain).
7. **Monitor and rate-limit the retrieval *pattern*, not just single items** — single-granularity detection is
   bypassable (A38606 stealthy adaptive poisoning evades aggregate detectors), and the retrieval sequence itself
   leaks (A39710). Add finer-than-aggregate anomaly monitoring and recursive-expansion / prefix-repetition
   detection.
8. **`REDACT` and `DENY` are first-class outcomes, and step-up-to-human is reserved for high-stakes cross-
   boundary reads** (reviewer synthesis; mirrors `ask-consent()`/`refuse()` in `policy-permission-gates.md`).
9. **Immutable, human-readable retrieval audit per decision** (which policy, which provenance, why), generated
   **asynchronously** so it adds zero retrieval latency (A40189; A41436; P10).
10. **Bound the LLM sensitivity/verifier signal's authority** — advisory-only, and cross-check against
    deterministic labels; A40874's <60% recognition accuracy is the reason it cannot be the access decision.
11. **Instrument over-redaction as a first-class cost** for reversible low-stakes reads ("prove before you
    veto", `architecture-patterns.md` P8) — but stay fail-closed on cross-tenant / above-clearance reads.

## Incorrect or fragile implementation patterns

- **Trusting retrieved content because it was retrieved.** Retrieval does not launder trust; the corpus is
  attacker-writable (A40462, A40725, A37023). Admitting top-k passages directly to context is the core
  vulnerability.
- **Single-purpose / single-granularity filters on ingested content.** A single toxicity/keyword filter is
  bypassable; reasoning-based gating outperforms it (A40462 vs. A40004/A38606 partial defenses), and aggregate
  distribution-shift detectors miss stealthy per-item poisoning (A38606). Scope is also a trap: A40725 filters
  *toxic* content and explicitly leaves manipulative-but-benign injection unaddressed.
- **Post-hoc prompt redaction instead of retrieval-time authorization.** Filtering an already-assembled context
  is racy and leaks; enforce read-authorization *before* items are selected (reviewer synthesis; the least-
  privilege-at-source principle of P6).
- **Letting an LLM decide sensitivity or access as the sole authority.** A40874 reports recognition accuracy
  <60% even with hints — an LLM sensitivity classifier misses sensitive material and cannot be the access
  decision (must be deterministic labels + advisory LLM).
- **Sending raw private content to an untrusted external model / peer.** The provider-as-adversary papers exist
  because this is the default failure (A40534, A40911, A40041); anonymize/abstract/surrogate at the edge.
- **No access control on retrieved profiles / memory.** A40188 concentrates LLM-inferred user data with no
  minimization or access control — a direct negative example. Persistent memory without ACLs is an unprotected
  asset.
- **Anchoring the gate to a trusted value source or verifier that is itself unhardened.** A40462 shifts trust to
  a value-based corpus that can be poisoned; the Judge can be prompt-injected (reviewer-anticipated); A40231's
  selective aggregator can be fed messages crafted to pass its reliability check. A new trust root is a new
  attack surface (Multi-keyword-match §11).
- **Ignoring the retrieval sequence / side channel.** Per-item access checks do not stop leakage from the
  *pattern* of retrievals (A39710).
- **Fail-open on missing labels or verifier timeout.** Contradicts the fail-closed posture; missing labels must
  deny/redact (reviewer synthesis).
- **Treating data-locality as a privacy guarantee.** "We only retrieve locally / only share embeddings" is
  asserted-not-tested privacy; retrieved embeddings and artifacts invert (A42453, A40839, A40593) — Privacy-
  Protection §2/§9 flags data-locality-as-privacy as a recurring trap.

## Verification strategy

- **Adaptive, defense-aware red-team is the launch gate** — the single most consistent gap across both
  syntheses (A40462, A40725, A40231, A38606, A37023 all non-adaptive). Any robustness claim "requires production
  validation" before reliance.
- **Poison the corpus / memory / peer channel and measure post-defense influence**, using the seven-plus attack
  types (targeted control, refusal DoS, blocker/jamming, adversarial-passage injection, grammar-trigger
  backdoors — A40462) and PoisonedRAG/BadRAG-style corpus poisoning (A40725).
- **Test stealthy, adaptive memory poisoning specifically** — CREAT-style RL-tuned per-item pollution that stays
  under an aggregate detector (A38606); verify finer-than-aggregate monitoring catches it.
- **Test the confidentiality half with cross-principal / above-clearance queries**, including queries steered by
  an indirect injection (confused-deputy: the injection tries to make the agent read data the requester cannot
  see). Reviewer synthesis grounded in A40188.
- **Test provider-as-adversary leakage** — confirm raw sensitive content never reaches the untrusted model; only
  abstracted/surrogate representations do (A40534, A40911, A40041, A42372).
- **Test retrieval-time extraction** — recursive topic-expansion, prefix-conditioned membership queries
  (A40593), attribute-inference from retrieved context (A41230), prompt/soft-prompt/embedding recovery (A40004,
  A40839, A42453).
- **Attack the verifier / trusted-source anchor directly** — poison the value source, prompt-inject the Judge,
  craft messages that pass the aggregator's reliability check (A40462, A40231 reviewer-anticipated moves).
- **Report absolute residuals, not relative reductions** — A40231 reports only *relative* backdoor-threat
  reduction with no post-defense absolute ASR (Multi-keyword-match §8/§12); demand absolute post-defense numbers.
- **Do not sign off on a single automated LLM judge** — validate against human agreement; LLM-as-judge is both
  instrument and attack target (A40498, A40913, A40874, A42372). Judge reliability / inter-rater agreement is
  frequently unreported (A40913 RRSS/RVNR/RAIC).
- **Use contamination-resistant / regenerated test cases** so an adversary cannot memorize a fixed corpus-poison
  checklist (`architecture-patterns.md` P11; the generator-coupled, single-team benchmark caveat on A37023).

## Metrics and thresholds

Track these families; **thresholds are operator-defined per deployment and must be validated against an
adaptive set — the corpus provides no validated universal threshold, and several report only relative or
truncated numbers.**

- **Attack Success Rate (ASR) on ingested-content attacks, absolute and post-defense.** A40462 author-reported
  BPI ASR 0.94→0.00 and WPI ASR 0.97→0.00 with accuracy gains, *under the evaluated non-adaptive conditions*;
  A40725's exact ASR/recall are **truncated in extracted text**; A40231 reports only *relative* backdoor-threat
  reduction 7.4–26.3% (better in 94.4% of tests, author-reported) with **no post-defense absolute ASR** — read
  that as a coarse signal, not a floor.
- **Per-document / per-item safety or trust score distribution** (A40725 `s_θ(d)`) as a runtime health monitor;
  a shift in the distribution flags corpus poisoning.
- **Read-authorization decision rates** — RETURN / REDACT / DENY per (role, purpose, source-tier); cross-tenant
  deny rate; and **over-redaction / false-deny rate** as a first-class cost (P8).
- **Retrieval-extraction signatures** — recursive topic-expansion depth, prefix-conditioned query repetition
  (A40593), attribute-inference query patterns (A41230); rate over time, not per-item.
- **Provenance completeness** — fraction of admitted items carrying verified source+extractor provenance (A41436;
  A40189); a drop signals a provenance-tiering gap.
- **Verifier verdict distribution and disagreement rate** with deterministic labels (A40462, A40725); rising
  disagreement flags either poisoning or verifier drift.
- **Retrieval-gate latency and decision-cache hit rate** (A40462 co-triggered verifier; A40725 in-retriever
  scoring as the latency levers).

All numeric values above are **author-reported, non-adaptive, and several are relative or truncated** — do not
treat any as a validated threshold.

## Test cases

Concrete, corpus-grounded cases the gate must be exercised against:

1. **Adversarial-passage injection** into the RAG corpus instructing a target output (A40462 targeted control).
2. **Refusal-DoS / blocker-jamming passages** designed to suppress a legitimate answer (A40462).
3. **Grammar-trigger backdoor passage** that activates on a benign-looking trigger (A40462).
4. **PoisonedRAG/BadRAG-style corpus poisoning** across multiple datasets/LLMs (A40725).
5. **Adversarial evidence contamination** of a retrieval-augmented verifier with GenAI-diverse claims (A37023).
6. **Stealthy adaptive memory/history poisoning** tuned to evade an aggregate distribution-shift detector
   (A38606 CREAT).
7. **Inter-agent message injection at a topologically critical node** (A40231 MPAS).
8. **Indirect prompt injection via a tool return / decompiled input** the agent reads and follows (A37135).
9. **Cross-tenant / above-clearance retrieval** — a query (optionally injection-steered) that tries to pull
   records the requesting principal is not entitled to (reviewer synthesis; A40188 no-access-control baseline).
10. **Provider-as-adversary leakage** — verify raw private content is not sent to an untrusted external model;
    only anonymized/abstracted/surrogate data is (A40534, A40911, A40041).
11. **Retrieval-time extraction** — recursive topic-expansion to reconstruct the corpus; prefix-conditioned
    membership queries (A40593); attribute inference from retrieved context (A41230).
12. **Retrieved-artifact secret recovery** — prompt inversion from outputs (A40004), soft-prompt membership
    (A40839), "protected" embedding inversion (A42453).
13. **Trace/sequence side-channel** — infer a per-user outcome from the pattern of retrievals despite per-item
    access checks (A39710).
14. **Verifier / trusted-source poisoning** — poison the value-source corpus or prompt-inject the reasoning
    Judge (A40462); feed the selective aggregator a message crafted to pass its reliability check (A40231).

## Adaptive adversarial tests

Beyond static cases — attackers who know the gate:

- **Corpus-poison optimized against the deployed retriever/verifier** — craft passages that the safety scorer
  admits and the reasoning Judge rates trustworthy (A40725 scorer evasion; A40462 Judge injection — both
  reviewer-anticipated in Multi-keyword-match §11).
- **Poison the trusted value source itself**, turning the gate's anchor against it (A40462 "value-based" corpus
  is attacker-writable).
- **Stealth-constrained memory poisoning that adapts to the monitor** — extend A38606's adaptive RL against the
  specific finer-than-aggregate detector you deploy.
- **Message crafted to pass the selective aggregator's reliability check** in a multi-agent retrieval channel
  (A40231 reviewer synthesis).
- **Injection-driven confused-deputy read** — an indirect injection whose payload is "retrieve and return
  document X" where X is above the requester's clearance; verify read-authorization denies regardless of the
  injected instruction (reviewer synthesis).
- **Adaptive extraction** — recursive, embedding-guided, information-dense small query sets that defeat a naive
  volume rate-limiter (analogous to the encoder-free extraction that defeats "rate-limit + prediction-only" in
  Privacy-Protection §11, A39671).
- **Gaming a new trust-decision surface the gate introduced** — appear locally compliant per-item while
  achieving the goal across the retrieval sequence (A39710 sequence leakage; reviewer synthesis: "treat every
  new trust-decision surface introduced by a defense as attackable").

## Telemetry requirements

Emit structured, tamper-evident trace fields for every retrieval decision (A40189 provenance chain; A41436
source+extractor provenance; `architecture-patterns.md` P10 async explainability):

- **Per-decision record:** principal + roles + purpose, query, item id + labels (tenant/clearance/sensitivity),
  source-trust tier, decision (RETURN/REDACT/DENY for read-auth; EVIDENCE/QUARANTINE/ROUTE_TO_VERIFIER for
  ingestion-trust), the **specific policy/rule fired, the provenance, and a human-readable rationale**, generated
  asynchronously (A40189; P10).
- **Provenance chain per admitted item** — source + extractor, carried into context and retained for
  containment/attribution (A41436; A40189). Supply and verify the integrity/tamper-resistance mechanism the
  corpus asserts but leaves unspecified (reviewer synthesis).
- **Per-item trust/safety score** (A40725 `s_θ(d)`) and **verifier verdict + rationale** (A40462) as structured,
  loggable signals — natural runtime-monitoring feeds (Multi-keyword-match §13).
- **Extraction/abuse signatures** — recursive topic-expansion depth, prefix-conditioned repetition (A40593),
  attribute-inference query patterns (A41230), cross-turn retrieval correlations (A39710).
- **Poisoning-drift signals** — per-item trust-score distribution shift (A38606-style finer-than-aggregate
  monitoring); provenance-completeness drops.
- **Over-redaction / false-deny rate** time series as a health/usability monitor (P8).

## Failure handling

- **Fail-closed.** On missing/unverifiable labels or provenance, verifier error/timeout, ambiguous purpose, or
  extraction-budget exhaustion → `DENY` (read-auth) / `QUARANTINE` (ingestion-trust); `REDACT`-and-continue only
  for reversible low-stakes reads. Reviewer synthesis, consistent with the corpus "single bypass not
  catastrophic" posture (A40189 backup meta-policies + Alert).
- **Degrade to least privilege, never to open access** — on a downstream check failure, narrow the retrieved
  view, do not widen it (`agent-identity.md` Zero Standing Privilege).
- **Advisory-signal compromise is survivable by design** — because the LLM sensitivity/verifier signal is
  advisory-only, its compromise or a low-recognition-accuracy miss (A40874) cannot by itself produce a
  `RETURN`/`EVIDENCE`.
- **Verifier / trusted-source compromise is assumed possible** (Multi-keyword-match §11 new-trust-root caveat) —
  pair the anchor with independent provenance tiering so anchor compromise alone is not catastrophic.
- **Latency under load is bounded architecturally** — co-triggered verifier (A40462), in-retriever scoring
  (A40725), cached deterministic ACL/tier lookups, async audit (P10) — not by relaxing the decision.
- **Residual leakage/injection is assumed**, so failure handling pairs retrieval-authorization with least-
  privilege corpus scoping, the action-side gate (`policy-permission-gates.md`), and human approval for high-
  stakes cross-boundary reads.

## Rollback and containment

- **Quarantine and provenance-trace the poisoned item** — because every admitted item carries source+extractor
  provenance (A41436; A40189), a discovered poison can be traced to its source and the source's trust tier
  demoted; downstream context assembled from it can be identified and invalidated.
- **Backup meta-policy + human-approval Alert on degradation** — A40189 (TAPA) keeps instant-rollback backups
  and routes high-stakes/degraded cases to human approval; the same rollback-and-Alert applies when the retrieval
  trust signal degrades.
- **Purge/quarantine poisoned memory, treating agent-memory purge as risk reduction, not guaranteed erasure** —
  Privacy-Protection §14: "delete my data" / memory purge is approximate and reactivatable; pair with residual-
  risk disclosure and post-purge re-audit (A41120/A40047/A40343 unlearning-residue findings, cross-synthesis).
- **Revoke the compromised source's read/write access and re-tier it** — cap blast radius via intent-based
  access revocation (`architecture-patterns.md` P6; `agent-identity.md`).
- **Rate-limit + query monitoring as extraction containment** — budget for residual leakage; extraction defenses
  are partial (Privacy-Protection §11, A39671 defeats naive rate-limits) and require the finer-grained signals
  above.
- **Immutable retrieval audit for forensics** — the full decision + provenance chain supports incident
  reconstruction (A40189; A41436), contingent on the audit-store integrity you must supply.
- **Feed incidents into refined labels, source tiers, and verifier** (`architecture-patterns.md` P12 adaptive
  red-team loop).

## Known bypasses

Demonstrated or corpus-supported bypasses of this pattern's weaker forms:

- **Single-purpose / single-granularity ingestion filters are bypassable** — input-only or aggregate detectors
  miss transformed or stealthy poison (A40004 reports "limited protection" from output perturbation; A38606
  evades distribution-shift detection; Multi-keyword-match §9).
- **Scope-limited ingestion filters leave non-toxic injection open** — A40725 scopes to toxic content and
  explicitly leaves manipulative-but-benign injection unaddressed.
- **The trusted value source / reasoning Judge / selective aggregator is a new, unhardened trust root** —
  poison the value source or prompt-inject the Judge (A40462); feed a reliability-check-passing message (A40231)
  (reviewer-anticipated, Multi-keyword-match §11).
- **LLM sensitivity recognition misses sensitive material** — A40874 recognition accuracy <60% even with hints;
  a read-authorization that relies on it under-blocks.
- **Retrieved "protected" artifacts still leak** — soft prompts leak membership with no output access (A40839);
  "protected" embeddings invert to impersonating identities (A42453, ASR reduced not eliminated); prompts
  recover from outputs (A40004). Egress control on retrieved artifacts is partial.
- **The retrieval sequence leaks even under per-item access control** (A39710).
- **Extraction defeats naive rate-limiting** — embedding-guided, information-dense small query sets extract with
  far fewer queries (Privacy-Protection §11, A39671 analogue).
- **Relative-only / truncated efficacy reporting overstates protection** — A40231 (relative reduction, no
  absolute ASR), A40725 (truncated) — real residuals may be materially higher.

## Residual risks

- **No gate drives injection or leakage to a safe floor under adaptive attack.** Every efficacy number here is
  author-reported, non-adaptive, and in some cases relative-only (A40231) or truncated (A40725); A40462's
  0.94→0.00 / 0.97→0.00 holds only under the evaluated non-adaptive conditions. Deployed efficacy may be
  materially below reported numbers.
- **Adaptive, defense-aware attackers are essentially unevaluated across the corpus** — the largest
  methodological gap (both syntheses).
- **The confidentiality / read-authorization half is reviewer synthesis, not a corpus-implemented result.** The
  corpus documents the *absence* of read-side access control (A40188) and its consequences (provider-as-
  adversary leakage), but no paper implements document-ACL-enforced retrieval; this design **requires production
  validation**.
- **Label/tier/policy incompleteness is silent** — the gate cannot enforce what was never labeled or declared
  (reviewer synthesis; analogous to A40484's constrained-set limitation).
- **The verifier / trusted-source anchor is a new single point of trust left unhardened by the source papers**
  (Multi-keyword-match §11) — its compromise is largely unmodeled.
- **Retrieved artifacts remain extractable secrets** — inversion/membership recovery is offline and often
  undetectable server-side (A42453, A40839, A40593); query-time controls are the only remaining lever.
- **The retrieval sequence side channel** persists even with perfect per-item access control (A39710).
- **Memory purge is approximate and reactivatable** — cross-synthesis unlearning-residue evidence (Privacy-
  Protection §9: A41120, A40047, A40343, A39373) means "we removed the poison / the sensitive record" is risk
  reduction, not guaranteed erasure.
- **Benchmarks are generator-coupled and single-team** — A37023 (GPT-4o/FLUX.1 + live retrieval), CREAT (A38606
  surrogate-transfer); none independently replicated, so external validity is unestablished (Multi-keyword-match
  §7/§12).

## Relevant research (stable paper ids from the syntheses/cards)

Primary — integrity / ingestion-injection:
- **A40462** — RAG2RAG: reasoning Detective+Judge gate on RAG output anchored to a trusted source; 2 languages /
  6 domains / 7 attacks / 7 baselines, released code; author-reported BPI ASR 0.94→0.00, WPI 0.97→0.00 under
  non-adaptive conditions. *Evidence: Strong (most complete RAG-security framework in-bucket); adaptive
  robustness untested; the anchor is a new trust root.*
- **A40725** — ShieldRAG: safety-aware retriever hard-filtering above a per-document safety threshold `s_θ(d)` +
  adversarial data synthesis + KL-regularization to a reference ranker; 7 datasets / 5 LLMs / 2 attacks.
  *Evidence: Moderate; quantitative results truncated in extracted text; scoped to toxic content only.*
- **A37023** — DRIFTBENCH: 16k human-validated instances (98.6%, κ=0.872, author-reported) for GenAI-diversity +
  adversarial evidence contamination of retrieval-augmented verification. *Evidence: Moderate (strongest RAG-
  security benchmark here); generator-coupled, non-deterministic.*
- **A38606** — CREAT: stealthy, adaptive, stealth-constrained interaction-history/memory poisoning that evades
  single-granularity distribution-shift detectors (adaptive RL). *Evidence: Moderate; the transferable meta-
  lesson for agent-memory poisoning.*
- **A40231** — MPAS: inter-agent message injection at topologically critical nodes + node-redundancy / per-agent
  message vetting; released code; author-reported *relative* backdoor-threat reduction 7.4–26.3% (no absolute
  ASR). *Evidence: Moderate; relative-only reporting; topology as a security parameter.*
- **A40189** — TAPA: shadow-simulation verify → degradation-threshold gate → backup-meta-policy rollback →
  human-approval Alert → provenance chain; single 77.7%-uptime operating point. *Evidence: Moderate; the only
  full propose→verify→gate→prove loop in-bucket; RAG/knowledge left trusted.*
- **A41436** — DIG: per-fact provenance to source+extractor for admissibility; trafficker-controlled source-ads
  threat. *Evidence: Moderate; the load-bearing provenance/audit pattern.*

Primary — confidentiality / read-authorization:
- **A40188** — personalized web agent that concentrates LLM-inferred user data (incl. demographics) with **no
  access control or minimization**; attack-surface catalog. *Evidence: Moderate; the negative example motivating
  read-side least privilege.*
- **A40534 / A40911 / A40041** — ARoG / SOER / PRISM: keep raw private content off the untrusted model via
  entity abstraction / redact-then-recover surrogate / sensitivity-aware routing to a trusted edge. *Evidence:
  Moderate; privacy largely "by construction", no executed-attack leakage metric.*
- **A39710** — ε-DP + Nash-regret bandits: the arm-selection (retrieval/decision) *sequence* leaks per-user
  outcomes even when stored data is protected; synthetic evaluation. *Evidence: Moderate; establishes the trace
  side channel.*
- **A40874** — SAPA-Bench: MLLM agents recognize sensitive material with RA <60% even with hints (best Gemini
  2.0-flash ~67%, author-reported); motivates a recognition→localization→severity→human-confirmation gate.
  *Evidence: Moderate (as a susceptibility benchmark); privacy labels partly GPT-4o-generated.*
- **A37135** — PriAgent: agentic (multi-agent, RAG, tool-use) privacy-compliance auditing over untrusted
  decompiled input with a **reviewer-flagged unimplemented injection gate**; evidence-linked verdicts
  (flow/code/policy snippet + reasoning + confidence). *Evidence: Moderate; the only genuinely agentic system,
  and the injection-gate gap is instructive.*

Supporting: A40004 (Inv2A, prompt inversion from outputs; perturbation defenses largely bypassed), A40616
(oracle-free incoherence certification; lower bound, misses ~1/3, zero false positives), A40593 (DSC-Prefix,
prefix-conditioned membership inference, WikiMIA only, dual-use), A41230 (FLAME, latent attribute inference,
dual-use), A40839 (PIPRA, soft-prompt membership with no output access), A42453 (FEM, "protected" embeddings
invert), A42372 (confidential evaluation via output-abstraction + sandboxing + human gating), A40206 (NashCoder,
obfuscate only the sensitive attribute), A40498 / A40913 (LLM-as-judge is both instrument and unhardened target),
A40773 (inference-time privacy-direction steering; model-generated labels).

Reviewer-synthesis cross-references (skill artifacts, **not** AAAI corpus papers): `architecture-patterns.md`
P6 (least-privilege credential broker / read-side least privilege), P1/P2 (gate before content reaches context /
effect-based), P10 (async explainability), P11 (contamination-resistant checks), P12 (adaptive red-team), P13
(discovery / source inventory); `agent-identity.md` (Zero Standing Privilege, just-in-time / just-enough,
intent-based access, separate trust domains, attenuated delegation); `policy-permission-gates.md` (the action-
side companion gate that fires on decisions derived from retrieved content).

## Evidence strength

- **The integrity thesis — "retrieval/inter-agent channels are attack surfaces and reasoning-based gating beats
  single-purpose filters" — is well-supported by convergence, not replication.** Convergent across A40462,
  A40725, A37023, A38606, A40231 — but these are **independent studies in different domains, not independent
  replications of one effect size** (both syntheses state this explicitly). Treat the convergence as a strong
  *design* signal, not a measured effect size. Efficacy of any specific implementation is **Moderate at best,
  non-adaptive, and in cases relative-only (A40231) or truncated (A40725)**.
- **The confidentiality / read-authorization thesis is Preliminary as an implemented control.** The corpus
  provides strong *motivating* evidence that read-side access control is absent and its absence is harmful
  (A40188, A40534/A40911/A40041, A39710, A40874), but **no paper implements document-ACL-enforced retrieval**;
  the deny-by-default read-authorization design is reviewer synthesis grounded in these failure modes plus
  `agent-identity.md`, and **requires production validation**.
- **The provenance/audit primitive is Moderate** (A41436 per-fact provenance; A40189 provenance chain) but its
  integrity/tamper-resistance mechanism is asserted, not demonstrated — you must supply it.
- **All efficacy numbers are author-reported, non-adaptive, best-case**, and several are relative or truncated.
  Report absolute post-defense residuals and validate on the target stack before operational reliance.
- **Deterministic, fail-closed, least-privilege design choices are reviewer-synthesis engineering best practice**
  grounded in the papers' failure modes (LLM sensitivity <60% recognition in A40874; unhardened verifier trust
  roots in A40462/A40231; single-granularity bypass in A38606), not themselves a paper-measured result.

## When NOT to use this pattern

- **When the corpus/source can simply be removed from the agent's reach.** Prefer least-privilege elimination to
  gating: if a role never needs a source, don't index it into that agent's retriever and then gate it. The gate
  is for corpora that must be reachable but conditionally (reviewer synthesis; `agent-identity.md` least
  privilege).
- **As the sole control.** Retrieval-authorization gates the *read/ingestion* boundary; a decision derived from
  admitted content must still pass the action-side gate (`policy-permission-gates.md`; A40189 shadow-verify →
  gate). A lone retrieval gate leaves material residual (A40231 relative-only, A40725 truncated).
- **As a substitute for a structural trust boundary.** If retrieved content is not separated from executable
  instruction, a downstream gate can be "talked past" (A40231 message vetting; the "data not instructions"
  requirement across both syntheses).
- **For pure content-safety / toxicity filtering of *model outputs*.** That is an output-guardrail layer, a
  different pattern; retrieval-authorization decides *what may be retrieved and how it may influence the agent*,
  not the toxicity of generated text (A40725 shows toxicity-only scope is itself insufficient for injection).
- **When no per-item access labels or source-trust tiers can be established and you would be forced to make an
  LLM the sole authority on sensitivity/trust.** A40874 (<60% recognition) and the unhardened-verifier caveat
  (A40462, A40231) show why single-artifact/LLM authority is gameable — either establish deterministic labels/
  tiers or treat the LLM signal as advisory-only.
- **For fully reversible, low-stakes reads where redaction/latency cost exceeds the harm** — "prove before you
  veto" (`architecture-patterns.md` P8); reserve hard fail-closed denial for cross-tenant / above-clearance /
  attacker-writable-source reads, and measure over-redaction as a first-class cost.
