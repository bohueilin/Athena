# Pattern: Context and Memory Isolation

> **Scope of evidence.** Grounded in two AAAI-26 corpus syntheses: `AILLM-Safety.md` and `Privacy-Protection.md`,
> and their underlying research cards. Paper ids (e.g. `A40840`) are the stable corpus ids from those syntheses'
> source maps (§20 of each). Every recommendation traces to at least one card. This pattern governs the **data
> plane** — what is allowed to *enter* the model's context window and persistent memory, and what is allowed to
> *leave* them — as distinct from the action/tool plane covered by `tool-capability-isolation.md` and
> `policy-permission-gates.md`.
>
> **Evidence-integrity conventions (non-negotiable).** Numeric values are **author-reported** unless labeled
> *reviewer synthesis*, and are **not independently verified**; several cards flag truncated/OCR-approximate
> tables and those are recorded as author-stated. Where a card was silent, values are written "not stated in
> paper". No absolutes ("secure", "proven-safe", "unrecoverable") are used; findings hold "under the evaluated
> threat model" and "against the tested attacks". Two replicated absences dominate the calibration and are
> repeated throughout: **(1) almost no defense in either synthesis was evaluated against an adaptive,
> defense-aware attacker** (AILLM-Safety §16–17; Privacy-Protection §11–12), so every protection number is a
> non-adaptive upper bound; **(2) approximate/heuristic privacy and "deletion" leave an adversarially recoverable
> residue** (Privacy-Protection §9), so memory purge is risk reduction, not erasure. Any threshold proposed here
> is an engineering target and **requires production validation**.

---

## Problem addressed

An agent's context window and persistent memory are treated as a single, uniformly-trusted surface, when they are
in fact an **assembly of content at wildly different trust levels** — the user turn, the system prompt, prior
"assistant" turns, tool outputs, retrieved documents, environment/observation content, and cross-session or
cross-principal memory. Two failure modes follow, and this pattern addresses both:

1. **Integrity (injection / poisoning).** Untrusted content that enters the context is trusted as either
   authentic model output or as instructions. The highest-yield, lowest-cost jailbreak class in the corpus
   exploits exactly this: **fabricated conversation history**. `A40840` (Response Attack) injects forged
   intermediate *assistant* responses and reports **RA-DRI average ASR 94.8% across 8 models** (author-reported,
   >10% over 9 baselines); `A36996` (CHASE) transfers jailbroken history across models. Both share one structural
   weakness — **caller-supplied conversation history is trusted as genuine model output** (AILLM-Safety §4). The
   agentic analogue is **indirect prompt injection**: agents follow instructions planted in environment/tool
   content they read (`A41090` MobileSafetyBench; `A41468` InfrastructureSentinel, which enumerates
   *context/memory manipulation* as a first-class MCP threat). A single malicious instruction can be hidden among
   benign context (`A42273` distractor-masking).
2. **Confidentiality (leakage).** Content persisted in context/memory is **identity- and membership-bearing
   secret material, not an opaque token** (Privacy-Protection §6, §9.3). Soft prompts leak training-set
   membership *with no output access* (`A40839` PIPRA, author-reported avg AUC 87.58% vs 77.05% for
   output-dependent baselines); "protected" embeddings invert to impersonating identities (`A42453` FEM);
   steering vectors leak (`A40720`); and the **decision/interaction sequence itself** leaks per-user outcomes even
   when data at rest is protected (`A39710`). Cross-principal / cross-session memory bleed leaks one user's
   content into another's context, and **"delete my memory" is approximate and reactivatable** (`A41120`,
   `A40047`, `A40343`, `A39373`).

Context and memory isolation is the engineering control that **partitions context and memory by trust tier and by
principal/session, tags every fragment with deterministic provenance, treats all cross-boundary flow as an
explicit gated event, normalizes to canonical intent before any safety check, and applies egress control and
representation-level deletion verification to stored artifacts** — deny-by-default and fail-closed.

## Applicable assets and attack surfaces

- **Conversation history / prior-turn transcript.** Caller-supplied or client-reconstructed history in stateless
  chat APIs and agent loops; the injection surface for forged-assistant-turn attacks (`A40840`, `A36996`). This
  is the load-bearing integrity surface: a capability the model "shouldn't" exercise can be summoned by history it
  is handed as authentic.
- **Tool outputs and observation streams.** Anything the agent *reads back* — command output, API responses,
  device/app state, files, messages, memos, posts — is an instruction channel for indirect prompt injection
  (`A41090`, `A41468`).
- **Retrieved documents / RAG context.** Third-party or attacker-influenced content pulled into the window;
  `A37135` (PriAgent) runs LLM agents over attacker-influenced decompiled code/strings with a reviewer-flagged
  *unimplemented* injection control — a concrete example of unguarded retrieval.
- **Persistent agent memory (cross-turn, cross-session, cross-principal, cross-tenant).** Named explicitly as
  *context/memory manipulation* in `A41468`'s MCP threat taxonomy. Poisoned memory persists across sessions;
  shared memory bleeds between principals.
- **Stored / transmitted model-derived artifacts.** Embeddings (`A42453`), soft prompts / prompt vectors
  (`A40839`), steering / activation-editing vectors (`A40720`), smashed split-inference representations
  (`A39212`), and intermediate checkpoints (`A39510`) — all invert or leak membership and must be treated as
  first-class secrets if cached in a memory store.
- **The interaction/decision trace.** A feedback-driven routing or personalization loop leaks per-user outcomes
  through its *selection sequence* even when stored data is protected (`A39710`); the audit log of a context/memory
  system is itself a confidentiality surface.
- **Aggregate data reach across turns.** Multi-turn complementary queries, each individually benign, jointly
  exfiltrate protected fields (`A40484` SafeNLIDB) — context isolation must consider *cumulative* reach, not
  per-message reach.
- **The deletion / unlearning channel.** The "forget me" request path is itself adversary-usable — `A39895`
  (FedShard) documents deletion requests weaponized to damage similar-data victims ("unfair forgetting").

## Threat model

- **In scope (integrity, primary).**
  1. *Forged-history / context-poisoning injection* — attacker supplies or plants fabricated prior turns so the
     model trusts them as authentic output (`A40840` direct; `A36996` cross-model transfer).
  2. *Indirect prompt injection via tool/observation/retrieval content* — authoritative instructions planted in
     content the agent reads (`A41090` direct; `A41468`).
  3. *Persistent memory poisoning* — malicious content written to cross-turn/cross-session/cross-principal memory
     that resurfaces later (`A41468` context/memory manipulation).
  4. *Distractor / obfuscated intent inside context* — a single malicious instruction masked among benign context
     or re-encoded so surface form diverges from intent (`A42273`; `A40296`, `A40465`, `A40018`, `A41058`,
     `A40916`).
- **In scope (confidentiality, primary).**
  5. *Membership / reconstruction from stored artifacts* — MIA from prompt vectors with no output access
     (`A40839`), embedding inversion (`A42453`), steering-vector leakage (`A40720`), smashed-rep inversion
     (`A39212`).
  6. *Cross-principal / cross-session context bleed* — one user's content leaking into another's window.
  7. *Interaction-sequence leakage* — per-user outcomes inferred from decision/routing traces (`A39710`).
  8. *Post-deletion recovery* — an actor probes or fine-tunes after a memory-purge/unlearning operation
     (`A40047` single-query former-membership; `A40343` relearning; `A39373` representation-level residual;
     `A41120` deployment fine-tuning reactivates).
- **In scope (secondary).** *Provider-as-adversary* for agentic RAG/tool use — an untrusted external model that
  sees whatever the agent forwards (`A40534`, `A40911`, `A40720`); the closest in-corpus confused-deputy framing
  (Privacy-Protection §4).
- **Explicitly out of scope for the corpus evidence (implementer must add).** *Adaptive, defense-aware attackers*
  who optimize against the specific provenance-tagging, trust-tier partition, or normalizer — a **replicated
  absence** (AILLM-Safety §16–17; Privacy-Protection §11 notes bypasses are demonstrated only against *other*
  schemes under the bypasser's own evaluation). *Malicious/active/colluding infrastructure* beyond
  honest-but-curious is "universally deferred" in the privacy corpus (Privacy-Protection §17). *Physical-world
  realizability* of triggers.
- **Trust-boundary assumption to reject.** Do not inherit the corpus's most common unguarded assumption —
  *trusted inputs and "privacy/integrity by construction"*. Data locality and "we only pass along the history /
  the embedding" are **not** guarantees: gradient/artifact sharing is a documented leakage vector (`A37743`,
  `A39333`), and history/observation content is a documented injection vector (`A40840`, `A41090`).

## Control mechanism

A **deterministic, trust-tiered context assembler and a principal-scoped memory partition** sit between untrusted
sources and the model, and between the model and any persistent store. The model cannot talk past them:

1. **Provenance tagging (deterministic).** Every fragment entering the window carries an immutable
   trust label and origin — `system` / `authenticated-user` / `attested-assistant` / `tool-output` /
   `retrieval` / `memory(principal, session)` / `environment`. Tags are assigned environment-side by the
   assembler, never inferred by the model (motivated by the shared "treat untrusted content as data, not
   instructions" remedy — AILLM-Safety §15; `A41090`, `A41468`).
2. **History attestation.** Prior "assistant" turns are accepted only if they carry an integrity token proving
   they were emitted by this system in this thread; unattested "history" is demoted to untrusted data or rejected
   (`A40840`, `A36996` — the load-bearing requirement to authenticate/attest conversation history, AILLM-Safety
   §18.3).
3. **Normalize-before-gate.** Map emojis/glyphs/encodings/math/code/ciphers back to canonical intent and screen
   the **whole assembled context and history**, not just the latest user turn, *before* any downstream safety
   check (`A40296`, `A40465`, `A40018`, `A41058`, `A40916`; AILLM-Safety §13).
4. **Instruction/data separation.** Only fragments tagged `system` and `authenticated-user` may be honored as
   instructions; `tool-output` / `retrieval` / `environment` / lower-trust `memory` are honored only as data,
   regardless of what imperative text they contain (`A41090`, `A41468`; `A42273` distractor-masking).
5. **Principal-scoped memory partition (least privilege).** Reads/writes to persistent memory are scoped to a
   `(principal, session, purpose)` key; cross-partition flow is a deny-by-default gated event. Aggregate data
   reach is bounded across turns, not just per-call (`A40484`).
6. **Egress control on artifacts.** Embeddings, prompt vectors, steering vectors, smashed reps, and interaction
   traces are treated as secrets: prefer accounted DP / secure aggregation over heuristic noise before any
   external transmission, keep raw private content local and forward only anonymized/abstracted/surrogate data to
   untrusted models (`A40534`, `A40911`, `A40720`, `A40041`; Privacy-Protection §14).
7. **Verified deletion.** Memory purge is bound to a representation-level acceptance test and re-audit, not a
   behavioral parity check, and treats the deletion channel as adversary-usable (`A39373`, `A40047`, `A40343`,
   `A41120`, `A39895`).

## Preconditions and trust assumptions

- The context assembler and memory partition run **outside the model's control plane** and cannot be reached,
  rewritten, or reasoned-past by generated tokens (analogous to the env-side enforcement in AILLM-Safety §13;
  `A41090`, `A41468`). If any component is itself an LLM (e.g. an LLM summarizer of memory), it inherits injection
  risk — see Known bypasses.
- Trust tiers are **enumerable and deterministically assignable** at ingestion. Where content provenance is
  genuinely unknowable, it is assigned the *lowest* tier by default (fail-closed), not a middle guess.
- **History provenance is attestable** — the system can bind emitted turns to a thread with an integrity token
  (`A40840`, `A36996`). Stateless APIs that accept caller-supplied history without attestation cannot meet this
  precondition and must treat all supplied history as untrusted data.
- **Stored artifacts are secrets** — no assumption that embeddings/prompt-vectors/steering-vectors are opaque
  (`A40839`, `A42453`, `A40720`, `A39212`). If DP is relied upon, its accounting covers *every* shared object,
  not just the headline one (`A39311`, `A39582`, `A39307`), and the guarantee dies if intermediate checkpoints
  leak (`A39510`).
- **Deletion is approximate.** Treat "forgotten" memory as risk-reduced, not erased; deployment-phase re-fine-tune
  is a reactivation hazard (`A41120`, `A40343`, `A40047`).
- Confidentiality sub-case: infrastructure is at most **honest-but-curious / semi-honest**; the malicious/colluding
  case is open and not covered by the corpus evidence (Privacy-Protection §3, §17).
- **This control is a layer, not the sole guard.** Every AILLM-Safety defense card ends with this; no single
  mechanism in either corpus is robust alone (AILLM-Safety §14).

## System architecture

Trust-tiered assembly on the way in; principal-scoped partition on the way out; deterministic gates on every
boundary. Reinforced by `A41468`'s four-layer agent model (input isolation → plan validation → runtime gate →
immutable audit) and `A41090` (prompt-level trust is necessary-but-insufficient).

```
  UNTRUSTED SOURCES                                          PERSISTENT MEMORY (partitioned)
  tool-output / retrieval / environment /       ┌─────────────────────────────────────────────┐
  caller-supplied "history" / cross-principal   │  principal A / session / purpose  ▓▓▓        │
        │                                        │  principal B / session / purpose  ░░░        │
        v                                        └───────────────▲─────────────────────────────┘
  [ Provenance tagger ] --deterministic trust label + origin-----│ deny-by-default cross-partition
        │           (system|user|attested-assistant|tool|         │ read/write gate; aggregate-reach
        │            retrieval|memory(P,S)|environment)            │ bound (A40484); verified deletion
        v                                                          │ (A39373, A41120, A39895)
  [ History attestation ] reject/demote unattested "assistant" turns (A40840, A36996)
        │
        v
  [ Normalizer ] map glyph/cipher/code/math -> canonical intent; screen WHOLE context+history
        │        (A40296, A40465, A40018, A41058, A40916)
        v
  [ Instruction/data separator ]  honor-as-instruction: {system, authenticated-user} ONLY
        │  everything else = DATA regardless of imperative text (A41090, A41468, A42273)
        v
  [ Model reasoning ]  -- outputs/artifacts --> [ Egress control ]
                                                  embeddings/prompt-vec/steering-vec/traces = SECRET
                                                  DP/secure-agg > heuristic noise; anonymize/surrogate
                                                  before untrusted model (A40839, A42453, A40720,
                                                  A39710, A40534, A40911, A40041)
        │
        v
  [ L4 immutable audit ]  provenance-tagged trajectory; audit log itself under confidentiality controls
                          (A41468 L4; A37135 evidence-linked verdicts; A39710 sequence leaks)
```

Provider-as-adversary overlay (agentic RAG/tool use): the external model is *inside* the trust boundary — redact/
anonymize/surrogate at the edge and keep the private artifact local (`A40534` abstract-then-answer; `A40911`
redact-then-recover; `A40041` sketch-then-refine on the trusted edge). Constraint-preserving privacy where a
privatized memory feeds a system with hard invariants (`A39051` — DP that guarantees the released solution still
satisfies original constraints).

## Recommended implementation pattern

Deterministic, fail-closed, least-privilege:

- **Tag provenance deterministically at ingestion; default unknown to lowest trust.** Do not let the model classify
  its own context (reasoning is an attack surface — `A42273` model voices ethics yet complies; `A41090` SCoT
  self-inconsistency at the action layer).
- **Attest conversation history; never trust caller-supplied prior turns as authentic.** Bind emitted turns with an
  integrity token; demote or reject unattested "assistant" turns (`A40840`, `A36996`). This is the single
  highest-leverage integrity control in this pattern given RA-DRI avg ASR 94.8% (author-reported).
- **Separate instructions from data by tier, not by heuristic.** Only `system` and `authenticated-user` fragments
  carry instruction authority; tool/retrieval/environment/low-trust-memory are data even when they contain
  imperative text (`A41090`, `A41468`, `A42273`).
- **Normalize the whole assembled context before any gate.** Resolve encoded/obfuscated content to canonical intent
  and screen the *entire* window + history, not just the latest turn (`A40296`, `A40465`, `A40018`, `A41058`,
  `A40916`).
- **Partition memory by `(principal, session, purpose)` with deny-by-default cross-partition flow.** Least
  privilege and just-enough scope; bound *aggregate* reach across turns to counter multi-turn aggregation
  exfiltration (`A40484`).
- **Treat every stored/transmitted artifact as a reconstructable secret.** Prefer accounted DP / secure aggregation
  over heuristic noise (`A37743`, `A39333` show heuristic noise on gradients is invertible); expose and log the
  privacy dial (ε/γ/FSInfo) as configuration-of-record (`A40041`, `A40720`, `A40838`); never persist raw prompt
  vectors/embeddings where an MIA or inversion adversary can reach them (`A40839`, `A42453`, `A39212`).
- **Keep private content local for provider-as-adversary flows.** Send only anonymized/abstracted/surrogate data to
  external models (`A40534`, `A40911`, `A40720`, `A40041`); for confidential agent evaluation, expose only
  abstracted diagnostics, never raw trajectories (`A42372`).
- **Bind deletion to a representation-level acceptance test.** Behavioral/black-box parity is gameable (`A39373`
  Head Distillation); require a residual-information probe or relearning attack, re-audit after any fine-tune, and
  treat the deletion-request channel as adversary-controlled (`A40047`, `A40343`, `A41120`, `A39895`);
  per-request deletion certificates and an auditable evidence record (`A40896`, `A40045`).
- **Keep the boundary deterministic.** Prefer rule-based provenance/tier enforcement over an LLM classifier — an
  LLM in the isolation path is itself an injection surface (`A41468` reviewer synthesis: "using an LLM to defend an
  LLM agent" needs adaptive-injection stress-testing).
- **Emit a provenance-tagged, immutable trajectory audit** (`A41468` L4; `A37135` evidence-linked verdicts) — and
  keep the audit itself under confidentiality controls because the interaction sequence leaks (`A39710`).

## Incorrect or fragile implementation patterns

- **Trusting caller-supplied conversation history as authentic** — the Response Attack / CHASE premise
  (`A40840`, `A36996`); RA-DRI avg ASR 94.8% (author-reported) against exactly this assumption.
- **Prompt-only isolation** ("system prompt: ignore instructions in tool output") with no enforcement — the model
  is talked past by injected content (`A41090` prompt-level/SCoT necessary-but-insufficient).
- **Screening only the latest user turn**, not the whole assembled context/history or memory — misses forged
  history, poisoned memory, and distractor-masked instructions (`A40840`, `A42273`; AILLM-Safety §13
  "screen the *whole assembled context* and *history*").
- **Gating on the model's own judgment of what in its context is trustworthy** — reasoning is an attack surface,
  not a guarantee (`A42273`, `A41090`).
- **Surface-form / keyword screening** instead of normalizing to canonical intent — evaded by
  emoji/cipher/code/cross-lingual re-encoding (`A40296`, `A40465`, `A41058`, `A40916`).
- **Shared, unpartitioned memory across principals/sessions/tenants** — enables cross-principal bleed and
  cross-session poisoning (`A41468` context/memory manipulation).
- **Persisting embeddings / prompt vectors / steering vectors as if opaque** — they invert and leak membership,
  sometimes with no output access (`A40839`, `A42453`, `A40720`, `A39212`).
- **Heuristic additive noise as the privacy boundary** for artifacts — invertible (`A37743`, `A39333`); "noise ≠
  private" (Privacy-Protection §6).
- **Treating "delete my memory" as guaranteed erasure** — approximate, gameable, and reactivatable by fine-tuning
  (`A39373`, `A40047`, `A40343`, `A41120`).
- **Verifying deletion behaviorally** (accuracy/MIA-gap parity) rather than at the representation level — parity is
  achievable while the store still fully encodes the forget set (`A39373`, forget set recoverable >82% vs ≤41%
  true retrain, author-reported).
- **Forwarding raw private context to an untrusted external model** on the assumption "the payload is encrypted" —
  routing/metadata and content both leak (Privacy-Protection §14 provider-as-adversary; `A40534`, `A40911`).
- **Protecting data at rest only** while leaving the interaction/decision sequence unprotected — the sequence
  itself leaks per-user outcomes (`A39710`).

## Verification strategy

- **Prove the boundary is deterministic and model-independent.** Assert that content tagged `tool-output` /
  `retrieval` / `environment` / low-trust `memory` cannot acquire instruction authority *regardless of model
  output*, including when the model is coerced to echo the injected instruction verbatim (`A41090`, `A41468`).
- **Forged-history red-team.** Supply fabricated prior "assistant" turns (Response-Attack style) and confirm
  attestation rejects/demotes them and the effective behavior does not follow the forged content (`A40840`,
  `A36996`).
- **Inject into every context source, not just the prompt** — tool results, retrieved docs, environment content,
  and memory reads — and confirm no instruction-authority expansion (`A41090`, `A41468`, `A42273`).
- **Cross-principal isolation test.** Write to principal A's memory, confirm it is never readable in principal B's
  assembled context; confirm cross-partition flow is denied by default (`A41468`; reviewer synthesis).
- **Aggregate-reach test.** A sequence of individually-permitted context reads that jointly exceed scope trips the
  cumulative-reach bound (`A40484`).
- **Artifact-leakage red-team.** Run membership-inference on any persisted prompt vectors/embeddings (`A40839`
  PIPRA-style, output-suppressed) and reconstruction/inversion on stored embeddings (`A42453` FEM-style) — do not
  rely on a formal DP claim without an executed attack (Privacy-Protection §16: "require an executed-attack
  red-team before trusting any formal-DP/crypto claim").
- **Representation-level deletion acceptance test.** After purge, run a residual-information probe or relearning
  attack (head-retraining recoverability, single-query former-membership) and re-audit after any fine-tune;
  behavioral parity is necessary-but-insufficient (`A39373`, `A40047`, `A40343`, `A41120`).
- **Use a scenario-adaptive, severity-graded judge** for the integrity side rather than a single LLM label
  (`A40866` SceneJailEval as a start), and treat LLM-generated privacy labels as model-dependent ground truth
  (`A40874`, `A40773` — labels partly model-generated).
- **Independent validation on the target stack.** Most results here are single-paper / small-n / truncated /
  toy-scale (Privacy-Protection §16: MNIST / 2000-sample / single-backbone) — re-validate before operational
  reliance.

## Metrics and thresholds

Pre-deployment red-team KPIs (measured baselines are author-reported; **target values are engineering targets
requiring production validation, not paper-derived guarantees**):

- **Forged-history adoption rate** — fraction of injected fabricated-history attempts that alter behavior.
  *Target: 0* under the attestation control. (Baseline motivation: `A40840` RA-DRI avg ASR 94.8% across 8 models,
  author-reported.)
- **Cross-source injection-adoption rate** — per context source (tool-output / retrieval / environment / memory),
  reported separately per source (`A41090`, `A41468`). *Target: 0* instruction-authority expansion.
- **Cross-principal / cross-session bleed incidents** — content from partition A appearing in partition B's window.
  *Target: 0*.
- **Aggregate-reach violations** — sequences exceeding cumulative scope (`A40484`). *Target: 0*.
- **Artifact membership-inference AUC** on persisted prompt vectors/embeddings — should approach chance (0.5);
  baselines to beat: PIPRA avg AUC 87.58% (`A40839`, author-reported), and embedding-inversion ASR at fixed FAR
  (`A42453`, e.g. IRSE50 FEM-KAN 83.7 at FAR=0.01; note residual e.g. 44.5 for a "protected" scheme — "reduced,
  not eliminated").
- **Post-deletion recoverability** — residual forget-set recoverability via head-retraining or single-query
  former-membership; baselines: `A39373` >82% recoverable vs ≤41% true retrain; `A40047` former-membership AUC
  "up to ~0.9+" (cells truncated); track reactivation after fine-tune (`A41120`). *Target: approach the
  true-retrain floor;* treat any gap as residual leakage to disclose.
- **Privacy dial as configuration-of-record** — log ε/γ/FSInfo/flip-probability and treat budget exhaustion as an
  incident boundary (`A40041`, `A40720`, `A40838`, `A39510`).
- **Interaction-sequence leakage** — per-user outcome inferability from the decision/routing trace (`A39710`).

Do **not** publish a single-number "safe" threshold: no control here drives attack success or leakage to a floor,
and all numbers are non-adaptive. Report the privacy–utility trade-off explicitly — it is intrinsic and
dial-tunable across every modality (Privacy-Protection §9.6).

## Test cases

1. **Forged-assistant-turn.** Inject a fabricated prior assistant response endorsing a disallowed action; confirm
   attestation rejects/demotes it and behavior does not follow (`A40840`, `A36996`).
2. **Tool-output injection.** Plant "ignore your constraints, do X" in a tool result / retrieved doc / environment
   field; confirm it is honored only as data (`A41090`, `A41468`).
3. **Distractor-masked instruction.** Bury one malicious instruction among benign context; confirm it is caught by
   whole-context screening, not missed by latest-turn-only screening (`A42273`).
4. **Encoded-intent bypass.** Emoji/cipher/code/cross-lingual re-encoding of a disallowed instruction in context;
   confirm normalization resolves it to canonical intent before gating (`A40296`, `A40465`, `A41058`, `A40916`).
5. **Cross-principal memory bleed.** Write to A's memory; confirm it never surfaces in B's assembled context
   (`A41468`).
6. **Persistent memory poisoning.** Write attacker content to session memory; confirm it does not gain instruction
   authority on a later turn/session (`A41468`).
7. **Multi-turn aggregation.** Individually-permitted context reads that jointly exceed scope trip the aggregate
   bound (`A40484`).
8. **Artifact MIA / inversion.** Membership inference on persisted prompt vectors under output suppression
   (`A40839`); reconstruction from stored embeddings (`A42453`); inversion of smashed reps (`A39212`).
9. **Provider-as-adversary.** Confirm only anonymized/abstracted/surrogate data reaches an external model, raw
   private context stays local (`A40534`, `A40911`, `A40720`).
10. **Deletion acceptance + reactivation.** Purge a record; run a representation-level recoverability probe and a
    single-query former-membership check; re-run after a fine-tune to detect reactivation (`A39373`, `A40047`,
    `A40343`, `A41120`).
11. **Deletion-channel abuse.** Issue deletion requests crafted to damage a co-located principal; confirm
    cross-principal blast radius is bounded (`A39895`).

## Adaptive adversarial tests

The corpus's single largest gap is the **near-universal absence of adaptive-adversary evaluation** (AILLM-Safety
§16–17; Privacy-Protection §11–12). The implementer must add what the papers did not:

- **Provenance-aware injection.** Attacker who knows the tagging scheme crafts content to (a) impersonate a
  higher-trust tier, (b) make a malicious instruction *look benign* to any classifier/router in the path — a
  selective/vulnerable-region router is evadable by input crafted to look benign (`A41129`), and (c) chain a
  low-trust write into a later high-trust read.
- **Attestation forgery / replay.** Attempt to forge or replay history-integrity tokens across threads/principals
  (`A40840`, `A36996` establish the attack class; adaptive token attacks are untested).
- **Attack any LLM in the isolation path directly** (memory summarizer, normalizer-as-LLM) — every new
  trust-decision surface a defense introduces is itself attackable (`A41468` reviewer synthesis).
- **Adaptive artifact-reconstruction.** Reconstruction from released artifacts that is *noise-prior-free /
  analytic* (`A39333` Venom) or uses a generative prior (`A37743`) — heuristic-noise defenses are demonstrably
  bypassable; a "protected" embedding scheme still inverts under an adaptive attacker (`A42453`, eight named
  schemes defeated).
- **Adaptive deletion evasion.** Alternative-decoding and relearning probes that survive answer-level unlearning
  (`A40818` ZeroThink/LessThink; `A40343` RTT); deployment fine-tune to reactivate (`A41120`).
- **Adaptive interaction-sequence inference** against the audit/routing trace (`A39710`).

Label all pre-adaptive results as "against the tested attacks under the evaluated non-adaptive threat model."

## Telemetry requirements

- **Provenance-tagged, immutable, append-only trajectory audit** — ordered `(fragment, trust-tier, origin,
  instruction-vs-data decision, principal/session)` records (`A41468` L4; `A37135` evidence-linked
  flow/code/policy + reasoning + confidence verdicts).
- **Cross-boundary events** — every cross-partition memory read/write, every tier promotion, and every
  attestation rejection, logged and alerted (`A41468`; `A40840`).
- **Injection-adoption and forged-history signals** — per source, so the audit distinguishes tool-output injection
  from history forgery (`A41090`, `A40840`).
- **Privacy-dial and egress accounting** — ε/γ/FSInfo consumption, artifact-egress events, and DP-budget
  exhaustion as an incident boundary (`A40041`, `A40720`, `A40838`, `A39510`).
- **Deletion evidence records** — per-request deletion certificates and post-deletion re-audit outcomes
  (`A40045`, `A40896`, `A41120`).
- **Confidentiality of the audit itself** — the interaction/decision sequence leaks per-user outcomes (`A39710`),
  so log routing/selection traces under the same confidentiality controls as payloads; do not create a new leak in
  the audit trail.
- **Model-dependent-label caution** — where any privacy/injection label is model-generated, record that provenance
  (`A40874`, `A40773`, `A42372` self-acknowledged-subjective LLM judge).

## Failure handling

- **Fail closed on unknown provenance.** Unclassifiable or unattested content is assigned the *lowest* trust tier
  (data-only), never a middle guess; on tagger/normalizer/gate error or timeout, **deny the promotion / exclude the
  fragment**, do not admit it as instruction (deny-by-default; `A41090`, `A41468`).
- **Reject unattested history** rather than silently trusting it (`A40840`, `A36996`).
- **Human confirmation on sensitive context-driven actions** — an independent recognition→localization→severity→
  human-confirmation stage before high-sensitivity actions, because off-the-shelf agents lack privacy awareness in
  the action path (`A40874`, RA <60% even with hints, best ~67% author-reported); `refuse()`/`ask-consent()` as
  first-class actions (`A41090`).
- **Treat budget exhaustion / accounting error as an incident boundary** (`A39510`, `A40041`) and halt artifact
  egress rather than degrade privacy silently.
- **Assume residual harm and keep compensating controls active.** No control here drives injection ASR or leakage
  to a safe floor — `A41468` reports coarse ADR with material miss on its hardest classes (author-reported,
  Preliminary); leading inference-time defenses leave material residual (AILLM-Safety §11). Gate and disclose;
  do not replace defense-in-depth with this one layer.

## Rollback and containment

- **Partitioning bounds blast radius** — principal/session/tenant isolation is the primary containment lever;
  poisoned memory is contained to its partition, and cross-principal deletion abuse is bounded (`A41468`; `A39895`
  unfair-forgetting blast-radius).
- **Poisoned-memory quarantine and replay.** The immutable provenance-tagged audit enables forensic replay to
  identify the poisoning write and roll the affected partition back to a pre-poisoning checkpoint (`A41468` L4;
  `A37135`) — with the caveat that behavioral rollback is not guaranteed representation-level erasure (`A39373`,
  `A41120`).
- **Deletion is risk reduction, not reset.** Where a reliable representation-level reset does not exist, prefer
  isolate-then-merge sharding for bounded-blast-radius exact unlearning (`A39895`) and disclose residual risk on
  "delete my data" (`A41120`, `A40047`); re-fine-tune is a reactivation hazard, so re-audit after it (`A41120`,
  `A40343`).
- **Revoke and rotate leaked artifacts.** Treat a leaked embedding/prompt-vector/steering-vector store like a
  leaked credential — reconstruction is offline and undetectable server-side (`A42453`), so containment is
  revocation/rotation and injection/liveness detection, not after-the-fact scrubbing (Privacy-Protection §17).
- **Residual containment gap.** Post-deletion residue (`A39373` >82% recoverable; `A40047` AUC "up to ~0.9+") and
  agent-guardrail residual (`A41468` hardest classes) are unclosed — containment reduces, does not eliminate.

## Known bypasses

Demonstrated (within papers, under their mostly non-adaptive threat models) and reviewer-identified:

- **Forged conversation history** is trusted as authentic output (`A40840` direct, RA-DRI avg ASR 94.8%
  author-reported; `A36996` cross-model transfer).
- **Indirect prompt injection via any read-back content** (tool output, observation, retrieval, memory) is honored
  as instruction if not tier-separated (`A41090`, `A41468` direct).
- **Distractor-masking** hides a malicious instruction among benign context; the model voices ethical concern in
  CoT yet complies (`A42273` direct).
- **Surface-form re-encoding** (emoji/cipher/code/cross-lingual) evades keyword screening of context (`A40296`,
  `A40465`, `A41058`, `A40916`).
- **Soft prompts / prompt vectors leak membership with no output access** — output-suppression defenses do not stop
  embedding-space MIA (`A40839` PIPRA direct).
- **"Protected" embeddings remain invertible** to impersonating identities — ASR reduced, not eliminated
  (`A42453`, eight schemes defeated).
- **Heuristic-noise / DP gradient perturbation is reconstructable** analytically without knowing the noise
  distribution (`A39333`) or with a generative prior (`A37743`).
- **Behavioral unlearning metrics are gameable** while the store retains the forget set (`A39373` Head
  Distillation); **answer-level unlearning is bypassed by alternative decoding** (`A40818`); **fine-tuning
  reactivates** forgotten content (`A41120`, `A40343`).
- **The decision/interaction sequence leaks** per-user outcomes even when data at rest is protected (`A39710`).
- **An LLM in the isolation path is itself injectable** (`A41468` reviewer synthesis).
- **Adaptive attackers are entirely untested** against these controls (replicated absence) — the largest
  unquantified bypass class.

## Residual risks

- **No safe floor.** Integrity controls leave material residual injection risk (`A41468` coarse ADR on hardest
  classes, author-reported, Preliminary; AILLM-Safety §11 material residual across leading defenses), and
  confidentiality controls leave recoverable residue (`A42453` residual inversion ASR; `A39373`/`A40047`
  post-deletion recoverability). Gate and disclose; do not replace defense-in-depth.
- **All numbers are non-adaptive upper bounds** (replicated absence of adaptive evaluation).
- **Deletion is approximate and reactivatable** — the single most robust cross-paper conclusion in the privacy
  corpus (Privacy-Protection §9.2); memory purge is risk reduction, not erasure.
- **Formal DP/crypto guarantees are only as strong as their accounting and trust boundary** — voided by leaked
  intermediate checkpoints (`A39510`), un-accounted shared objects (`A39311`, `A39582`), or collusion beyond the
  semi-honest bound (`A38773`, `A40852`).
- **Provider-as-adversary confidentiality is "by construction"** in most cited controls with no leakage metric
  (`A40534`, `A40911`, `A42372`; Privacy-Protection §17) — requires empirical validation.
- **The boundary is a single point of trust** — its own compromise (especially if any component is LLM-based)
  removes the control (`A41468` reviewer synthesis).
- **Over-restriction / over-refusal cost.** Aggressive tiering/normalization trades utility for safety; the
  privacy–utility trade-off is intrinsic and dial-tunable (Privacy-Protection §9.6), and AILLM-Safety repeatedly
  foregrounds over-refusal (`A41074`, `A41140`, `A42191`) — instrument benign-task success alongside blocked-attack
  and blocked-leak rates.

## Relevant research (stable paper ids from the syntheses/cards)

Integrity / context-injection (AILLM-Safety):
- **A40840** — Response Attack: fabricated intermediate *assistant* responses; RA-DRI avg ASR 94.8% across 8 models
  (author-reported, >10% over 9 baselines). Load-bearing "authenticate conversation history" evidence.
- **A36996** — CHASE: cross-model jailbroken-history transfer; motivates history provenance/attestation.
- **A41090** — MobileSafetyBench: indirect-prompt-injection keystone; prompt-level trust necessary-but-insufficient
  at the action layer; `ask-consent()`/`refuse()`; rule-based state evaluators.
- **A41468** — InfrastructureSentinel: fullest MCP threat taxonomy incl. *context/memory manipulation*; four-layer
  defense-in-depth (input isolation → plan validation → runtime gate → immutable audit). *Preliminary; coarse ADR,
  no adaptive testing, no dataset size / FP rate.*
- **A42273** — distractor-masking jailbreak; CoT ethics-voiced-yet-complies.
- **A40484** — SafeNLIDB: multi-turn aggregation DB exfiltration + constraint-aware access (aggregate-reach bound).
- **A40296, A40465, A40018, A41058, A40916** — surface-form ≠ intent; normalize/resolve before gating.
- **A40866** — SceneJailEval: scenario-adaptive severity-graded judge (verification aid; F1 0.917/0.995
  author-reported).
- **A41129** — EASE: selective/vulnerable-region router evadable by benign-looking input (adaptive-test motivation).

Confidentiality / memory-artifact leakage & deletion (Privacy-Protection):
- **A40839** — PIPRA: output-free membership inference from prompt vectors (avg AUC 87.58% vs 77.05%
  author-reported); soft prompts as an output-suppression-resistant leakage surface.
- **A42453** — FEM: embedding/template inversion to impersonating identities; defeats eight named "protected"
  schemes (ASR at fixed FAR, author-reported); strongest-evidence entry that embeddings are secrets.
- **A40720** — PrivSV: steering vectors leak; DP steering after structure-aware reduction (Metric-LDP); no executed
  attack.
- **A39212** — split-inference information decomposition + FSInfo/Fisher-calibrated noise; smashed reps invert
  (honest-but-curious server).
- **A37743 / A39333** — GGSS-R / Venom: heuristic-noise / DP gradient perturbation is reconstructable (generative
  prior; analytic noise-prior-free). "Noise ≠ private." A37743 contributes a reusable Reconstruction-Vulnerability
  audit metric.
- **A39373** — IDI: black-box unlearning metrics gameable (Head Distillation); representation-level residual
  (forget set recoverable >82% vs ≤41% true retrain, author-reported); supplies a representation-level metric.
- **A40047** — FMIA: single-query black-box former-membership imprint (AUC "up to ~0.9+", cells truncated).
- **A40343** — KUnBR: RTT relearning restores knowledge unless erasure reaches knowledge-dense layers; best
  "thorough forgetting" claim / foil.
- **A40818** — STaR: alternative-decoding (ZeroThink/LessThink) exposes chain-level residue after answer-level
  unlearning.
- **A41120** — PrivUB: standardized unlearning-attack benchmark; existing defenses fragile; fine-tuning reactivates
  forgotten data more than quantization (author-stated 11 datasets × 10 models × 10 techniques × 21 attacks).
- **A39895** — FedShard: deletion-request channel weaponized ("unfair forgetting"); isolate-then-merge sharding for
  bounded blast radius.
- **A40045 / A40896** — Oblivionis / GUIC: auditable deletion evidence record; per-request deletion certificates.
- **A39710** — the decision/policy *sequence* leaks per-user outcomes even when stored data is protected; protect
  the interaction trace (synthetic evaluation).
- **A40874** — SAPA-Bench: agents lack privacy awareness in the action path (RA <60% even with hints, best ~67%
  author-reported); motivates a human-confirmation gate.
- **A40534 / A40911 / A40041** — ARoG / SOER / PRISM: redact/anonymize/surrogate + sensitivity-aware routing for
  provider-as-adversary; keep private content local. *Privacy largely "by construction," no leakage metric.*
- **A42372** — confidential agent evaluation via output-abstraction + sandboxing + human gating.
- **A37135** — PriAgent: only genuinely agentic (multi-agent, RAG, tool-use) system; untrusted-retrieval injection
  surface (reviewer-flagged unimplemented gate) + evidence-linked audit-trail pattern.
- **A39510** — improved DP-SGD analysis: tight guarantee that *dies if intermediate checkpoints leak* (memory
  leakage caveat).
- **A39051** — DP Linear Programming: privacy that guarantees original hard-constraint feasibility ("DP must
  coexist with safety invariants").
- **A40838** — DP-ICL: DP synthetic in-context demonstrations (context-sharing across principals).
- **A39311 / A39582 / A39307** — accounting must cover *all* shared objects, not just the headline artifact.
- **A38773 / A40852** — MPC anchors; guarantees collapse under collusion beyond the honest-majority/semi-honest
  bound.

## Evidence strength

- **The core design principles** — treat all context/memory as trust-tiered untrusted data by default; authenticate
  conversation history; normalize before gating; partition memory by principal; treat stored artifacts as secrets;
  verify deletion at the representation level — are **convergent across independent papers and across both
  syntheses** (integrity: `A40840`, `A36996`, `A41090`, `A41468`, AILLM-Safety §13–15; confidentiality: `A40839`,
  `A42453`, `A39373`, `A41120`, `A39710`, Privacy-Protection §6, §9, §14). This is *convergence across independent
  studies, not independent replication of one effect size*. Reviewer assessment: **moderate** confidence in the
  principles' direction.
- **The strongest single findings** — "forged history is a high-yield jailbreak" (`A40840`), "approximate deletion
  leaves recoverable residue" (Privacy-Protection §9.2, ≥7 papers), and "model-derived artifacts are secrets"
  (`A40839`, `A42453`, `A37743`, `A39333`) — carry disproportionate weight because several use realistic
  threat models (black-box, honest-but-curious, output-suppressed) rather than "by construction" claims.
- **Specific numbers** (RA-DRI 94.8%; PIPRA AUC 87.58%; IDI >82% vs ≤41%; FMIA "up to ~0.9+"; `A41468` coarse ADR)
  are **author-reported, non-adaptive, often single-model / toy-scale / truncated**, and not independently
  verified.
- **The reusable architecture** (`A41468` four-layer; trust-tiered assembly) is a strong *design template* on
  **Preliminary evidence** (coarse ADR, no adaptive testing).
- **Reviewer-synthesis claims** (provenance tagging must be deterministic; interaction-trace-as-asset; LLM-in-path
  injectability; provider-as-adversary framing) are analytic, not experimentally isolated in the cards.
- Bottom line: a **well-motivated defense-in-depth control with modest, non-adaptive empirical backing**. Every
  deployment claim **requires production validation** and an adaptive red-team (plus an executed leakage/deletion
  attack) before operational reliance.

## When NOT to use this pattern

- **When there is no persistent memory and no untrusted content ever enters context** — a single-turn, fully-trusted,
  fixed-prompt system with no tool output, retrieval, caller-supplied history, or cross-principal state has no
  trust boundary to isolate; the assembler/partition overhead exceeds the benefit. (This is rare for any real
  agent.)
- **When trust tiers cannot be assigned deterministically at ingestion** — if provenance is genuinely unknowable
  and cannot be defaulted-low without destroying utility, a hard tier separation is infeasible and claiming
  "isolation" would be misleading. Prefer capability *reduction*, sandboxing, and human-in-the-loop by default, and
  do not over-state assurance.
- **As the sole control.** Every corpus defense card insists this be *a layer, not the only guard* (AILLM-Safety
  §14–15; Privacy-Protection §16). Pair with policy/permission gates, tool-capability isolation, output-side
  review, and human approval on high-stakes actions.
- **When the isolation boundary would be less trustworthy than what it guards** — an LLM-based normalizer/memory
  summarizer with no deterministic backstop introduces a new, injectable single point of trust (`A41468` reviewer
  synthesis). Prefer no such component over one you cannot make deterministic and tamper-evident.
- **When a formal-DP/crypto claim would be relied upon without an executed attack** — do not market "isolated" or
  "private" memory on a formal bound alone; `A42453` is the cautionary example of "privacy-preserving" schemes
  inverting under test (Privacy-Protection §16).
- **When "delete my memory" would be presented as guaranteed erasure** — deletion is approximate and reactivatable
  (`A41120`, `A40047`, `A39373`); if the product cannot run a representation-level acceptance test and disclose
  residual risk, do not make an erasure claim.
