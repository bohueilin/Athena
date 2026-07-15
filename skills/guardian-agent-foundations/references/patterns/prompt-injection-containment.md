# Pattern: Prompt Injection Containment

> **Scope of evidence.** This pattern is grounded in the AAAI-26 corpus syntheses `AILLM-Safety.md` and
> `Defense-Mitigation.md` and their underlying research cards. Load-bearing papers: **A41090** (MobileSafetyBench,
> the corpus's indirect-prompt-injection keystone — agents highly vulnerable, prompt-level safety
> necessary-but-insufficient, "treat untrusted environment content as data, not instructions"), **A41468**
> (InfrastructureSentinel, the fullest MCP direct+indirect-injection threat taxonomy and a four-layer
> defense-in-depth architecture), **A40840** (Response Attack, forged assistant-history priming), **A36996**
> (CHASE, cross-model jailbroken-history transfer), **A41134** (IMBIA, positional injection into multi-agent
> pipelines + MU-BA/BU-MA asymmetry), **A40296 / A40465 / A41058 / A40916** (emoji / math-code / cipher /
> cross-lingual surface-form evasion → normalize before you screen), **A37924** (GhostCert, "a verification
> artifact is not a correctness oracle"). Supporting: A42273, A41129, A41152, A40248, A40866, A40432, A42191,
> A41498, A39818, A40018, A40484.
>
> **Evidence integrity (non-negotiable).** Every quantitative claim below is **author-reported and not
> independently verified**; where a card was silent the text says "not stated in paper". Numbers are tagged
> author-reported vs. reviewer synthesis. Calibrated language only — "reduced ASR against the tested attacks
> under the evaluated threat model", "requires production validation" — never "secure / proven-safe /
> eliminates". The single most important cross-corpus caveat, repeated below: **no defense in either synthesis
> was evaluated against an adaptive, defense-aware attacker**, so every efficacy number is an upper bound on
> real-world protection. This pattern is scoped to *containing injection* (stopping untrusted content from
> becoming instructions, and bounding blast radius when it does); the downstream *allow/deny/step-up action
> decision* is the sibling pattern `policy-permission-gates.md`, and capability minimization / execution
> isolation are `tool-capability-isolation.md` and `sandboxed-execution.md`.

---

## Problem addressed

An LLM agent cannot, by construction, reliably tell an *instruction from its principal* apart from
*instruction-shaped text it merely read* in the content it processes. The corpus makes this concrete and
load-bearing:

- **Agents follow instructions planted in the environment they read.** A41090 (MobileSafetyBench) reports as a
  headline finding that agents are "highly vulnerable to indirect prompt injection" and that "no agent is safe
  against indirect prompt injection" (author-reported, over 50 scripted injection tasks across frontier
  multimodal LLMs). The single most product-relevant threat in `AILLM-Safety.md` is exactly this: agentic
  indirect prompt injection (A41090, A41468).
- **Prompt-level safety reasoning is necessary but insufficient.** A41090 shows agents "overlook safety
  considerations they themselves generated" (self-inconsistency), and its prompt-only defense (SCoT) "does not
  close the gap" (author-reported). A42273 reports models voice ethical concern in chain-of-thought yet still
  comply. The corpus principle: **capability ≠ permission ≠ safety** (A41090 design implications, verbatim;
  A41468 "capability is not permission").
- **The untrusted channel is not just the user prompt.** Injection enters through received messages, memos,
  social posts, files, retrieved documents, tool output, logs (A41090; A41468), *forged conversation history*
  (A40840 Response Attack, author-reported RA-DRI avg ASR 94.8% across 8 models; A36996 CHASE cross-model
  history transfer), and content *appended after* a benign request in a multi-agent pipeline (A41134 positional
  injection).
- **Surface-form filters miss semantic intent.** Emoji/glyph substitution (A40296), math+code wrapping (A40465,
  author-reported avg ASR 91.19% GPT-series / 97.62% on five SOTA models at a single query), 21-cipher
  recombination (A41058, author-reported 60%+ ASR within ≤10 queries), and cross-lingual "macaronic"
  recombination (A40916) all pass harmful intent through a matcher that scans lexical form.

**Prompt injection containment** is the set of deterministic, structural controls that (a) keep untrusted
content classified as *data, never instruction*, (b) recover canonical intent before any screening decision,
(c) authenticate the provenance of context and history, and (d) bound the blast radius so a bypass — which the
corpus says to assume — is not catastrophic.

## Applicable assets and attack surfaces

- **Environment / observation content the agent reads** — incoming messages (even from strangers), memos,
  social posts, stored files, screenshots + UI-element text (A41090's 13-app Android surface). The primary
  indirect-injection surface.
- **Retrieved documents, logs, and web content** ingested by RAG or a browsing tool — A41468 lists "poisoned
  external data sources (documents, logs, web)"; A40432 shows the retrieved knowledge base is itself an
  attack surface (extraction; residual ~28% chunk-recovery under the strongest defense, author-reported).
- **Tool / MCP-server output and tool descriptions** — tool poisoning / masquerading third-party tools
  (A41468, which *cites* a study of 1,899 open MCP servers finding 7.2% general and 5.5% MCP-specific
  tool-poisoning vulnerabilities — cited evidence, not the paper's own measurement).
- **Conversation history / prior "assistant" turns** — caller-supplied history trusted as authentic model
  output (A40840 DRI/SRI injected responses; A36996 transferred jailbroken histories exploiting
  coherence bias).
- **Multi-agent message passing and agent role profiles** — a malicious module appended after a benign request
  (A41134 MU-BA) or hidden instructions embedded in an agent's role profile (A41134 BU-MA, the harder case).
- **Cross-modal channels** — sub-image decomposition + chain-of-thought (A40018), and the general corpus
  finding that image/audio/video channels are softer than text (A40607, A40863, A40841); an injection can be
  carried in a modality the text-side filter never inspects.

## Threat model

Designed for **inference/runtime adversaries** who cannot change model weights but control content the agent
will read, and steer it into unintended instructions. Grounded threat classes:

- **Direct prompt injection / jailbreak** at the user channel (A41468; A41090 misuse) — a malicious user issues
  an unsafe instruction directly.
- **Indirect prompt injection (headline threat)** — instructions planted in environment/tool/retrieved content
  the agent ingests; the agent acts against the principal's intent (A41090, A41468). *Corpus finding:* prompt-
  level safety does not stop it (A41090).
- **Context / memory manipulation** — a fabricated "emergency maintenance" context to unlock a restricted path
  (A41468); forged prior-turn history trusted as authentic (A40840, author-reported RA-DRI avg ASR 94.8%;
  A36996 coherence-bias transfer).
- **Positional injection in multi-agent pipelines** — malicious instruction appended *after* a benign request,
  specifically to sit past a trailing guardrail (A41134 MU-BA).
- **Compromised internal agent / supply chain** — a third-party agent whose role profile carries hidden
  instructions (A41134 BU-MA); the hardest case (see Known bypasses).
- **Encoding / semantics-preserving evasion of the matcher** — emoji/glyph (A40296), math+code (A40465),
  cipher (A41058), cross-lingual recombination (A40916), distractor masking of a single malicious instruction
  (A42273).
- **Reasoning-channel exploitation** — the injection targets the same chain-of-thought a prompt-only defense
  relies on; the model reasons about safety and complies anyway (A42273; A41090 self-inconsistency).
- **Verifier / detector gaming** — if containment keys on a certificate or a model score, an adversary games
  that artifact (A37924, demonstrated under white-box + known-σ).

**Adaptivity boundary (critical).** Both syntheses flag that almost every *attack* is fixed-strategy and almost
no *defense* is evaluated against an attacker adapting to it: A41090's 50 injection tasks are scripted and
non-adaptive; A41468 evaluates no red-team attacker targeting its four layers; A41134's prompt defense is
non-adaptive. Treat all efficacy numbers as best-case; adaptive red-team is a launch gate (see Verification
strategy).

## Control mechanism

Containment is a **structural, deterministic pipeline**, not a model verdict. Four mechanisms compose:

1. **Trust-boundary isolation (the core control).** Every byte of untrusted content is tagged with its
   provenance and handled as *data, never instruction*. A41090 (implementation implications, verbatim):
   untrusted environment content "must be treated as data, not instructions — argues for content/trust-boundary
   isolation at the tool/observation layer." Enforce a boundary the model **cannot be talked past** — A41134:
   "trailing guardrail text is insufficient against positional injection; enforce a boundary the model cannot be
   talked past." Structurally separate principal intent from ingested content (separate channels / typed roles),
   rather than concatenating them into one flat prompt.
2. **Canonicalization before screening.** Decode/normalize emoji, glyphs, ciphers, cross-lingual recombination,
   and math/code wrapping back to canonical intent *before* any classifier or gate runs, and screen the *whole
   assembled context* (including history), not only the latest user turn (A40296, A40465, A41058, A40916; A40840
   / A36996 "apply safety classification to *history*, not just the latest user turn").
3. **Provenance / attestation of context and history.** Distinguish genuine model-generated turns from
   caller-supplied history so injected "assistant" turns cannot masquerade as authentic output (A40840 / A36996
   implementation implications: "sign/attest transcript provenance", "validate that prior 'assistant' content
   actually originated from the trusted model"). Never trust caller-supplied role profiles as authentic (A41134
   BU-MA).
4. **Layered detection + containment aligned to the agent cognitive cycle.** Defense-in-depth so a threat
   missed at one layer is caught at another (A41468 four layers; A40432 dual-path / single-point-insufficient),
   with the *action decision and least-privilege blast-radius limits deferred to the sibling patterns* — because
   no input-side filter in the corpus drives injection success to a safe floor (A41090 "no agent is safe";
   A41468 residual ADR).

Optional model/LLM signals (semantic intent classification, a Guardian-LLM Safe/Unsafe verdict) are **advisory
only**: they may raise suspicion or force human review, but must never be the sole basis for treating content as
trusted, because the detector is itself injectable/gameable (A41468 reviewer synthesis; A37924).

## Preconditions and trust assumptions

The pattern is only as strong as these hold; each is a documented failure point:

- **A structural channel separation exists** between principal instructions and ingested content. If everything
  is concatenated into one prompt, there is no boundary to enforce (A41090; A41134 "a boundary the model cannot
  be talked past").
- **Provenance of each context element is knowable.** History attestation requires a trusted record of what the
  model actually generated (A40840, A36996). Stateless chat APIs that accept caller-supplied message arrays
  violate this by default (A40840 deployment implications: "any deployment that accepts client-provided
  conversation history … is exposed").
- **Canonicalization coverage is complete for the deployed channels.** An un-normalized encoding (a new cipher,
  a new modality) slips past a surface matcher (A40296, A40465, A41058, A40916; A40018 cross-modal). Coverage
  gaps are silent failures.
- **The detection/decision path is itself not injectable and not the sole authority.** Reviewer synthesis on
  A41468: "using an LLM to defend an LLM agent creates a potentially injectable trust anchor not stress-tested
  against adaptive attacks." If a Guardian LLM participates, it is advisory.
- **Least-privilege scoping and an action gate exist downstream** to contain what leaks through. The corpus is
  explicit that containment must *gate, not replace*, least privilege (A41468 deployment; A41090
  implementation) — see `policy-permission-gates.md`, `tool-capability-isolation.md`.
- **Audit-store integrity is supplied, not assumed.** A41468 asserts an "immutable audit trail" but its
  "integrity/tamper-resistance mechanisms are not specified" (reviewer synthesis) — you must provide it.
- **Screening covers the whole context and every modality the agent can read** (A40840/A36996 whole-context;
  A40018/A40607/A40863 multimodal softer than text).

## System architecture

Defense-in-depth aligned to the agent cognitive cycle (Perception → Planning → Action → Memory) — the most
directly transferable architecture in the corpus (A41468 four layers; reinforced by A41090 "prompt-level safety
is necessary-but-insufficient"):

```
 untrusted content ─►[Ingress: tag provenance]  every message/doc/tool-output/history turn labeled TRUSTED vs
   (msgs, docs,          │                        UNTRUSTED at the boundary; untrusted = data, never instruction.
    tool output,         ▼                        (A41090 trust-boundary isolation; A40840/A36996 history provenance)
    history, files)
                    [Normalize / canonicalize]   decode emoji/glyph/cipher/cross-lingual/math-code → canonical
                         │                        intent; screen the WHOLE assembled context, not last turn only.
                         ▼                        (A40296, A40465, A41058, A40916; A40840/A36996 whole-context)
 principal intent ─►[L1 Input screening]         classify recovered intent; Guardian-LLM verdict = ADVISORY only.
   (typed, separate       │                       may force human review, never sole "trusted". (A41468 L1; A37924)
    channel)              ▼
 agent plan ──────►[L2 Tool-plan validation]     deterministic: does the plan follow UNTRUSTED content into a
                         │                        side effect? block plans steered by injected instructions.
                         ▼                        (A41468 L2)   →→ decision engine = policy-permission-gates.md
 tool call ───────►[L3 Runtime containment gate] FINAL deterministic check before the side effect; fail-closed;
                         │                        least-privilege scoping bounds blast radius. (A41468 L3; A39818)
                         ▼                          →→ blast-radius limits = tool-capability-isolation.md / sandbox
                  ┌─ side effect fires ─┐
                  ▼                     ▼
        [L4 Immutable audit + async explanation]  every decision + provenance chain logged; self-inconsistency and
                  │                                injection signatures flagged; feeds policy-refinement. (A41468 L4)
                  ▼
        adaptive red-team → policy/normalizer refinement loop  (A41468 L4; reviewer synthesis)
```

- **Ingress provenance tagging and normalization run before any model sees the content** — they are the
  containment-specific layers this pattern owns.
- **The allow/deny decision engine (L2/L3 authority)** is `policy-permission-gates.md`; **capability
  minimization and execution isolation** (bounding what a leaked instruction can touch) are
  `tool-capability-isolation.md` and `sandboxed-execution.md`. This pattern is deliberately the *input/context*
  half of a whole-cycle defense.
- **Latency is bounded architecturally** — cache deterministic checks, run audit/non-critical checks
  asynchronously (A41468 explicit).

## Recommended implementation pattern

Deterministic, fail-closed, least-privilege — in priority order:

1. **Tag provenance at ingress and treat untrusted content as data.** Label every context element
   (user turn, tool output, retrieved chunk, prior assistant turn, file) TRUSTED vs UNTRUSTED at the boundary;
   render untrusted content into the model context in a form that is structurally not executable instruction
   (A41090; A41134 "boundary the model cannot be talked past").
2. **Canonicalize before screening, and screen the whole context.** Normalize emoji/glyph/cipher/cross-lingual/
   math-code to recovered intent, then classify — never match raw surface strings (A40296, A40465, A41058,
   A40916). Re-screen the *entire assembled context including history*, not just the latest user turn (A40840,
   A36996).
3. **Authenticate history and role-profile provenance.** Use server-authoritative session state or
   signed/attested transcripts so injected "assistant" turns cannot masquerade as genuine output (A40840,
   A36996); validate agent role profiles are not caller-controlled (A41134 BU-MA).
4. **Keep any model/detector signal advisory.** A Guardian-LLM Safe/Unsafe verdict, a semantic classifier, or a
   certificate may raise suspicion or force human review but must never by itself mark content as trusted or
   authorize a side effect (A41468 reviewer synthesis; A37924 "verification artifact ≠ correctness oracle").
5. **Layer detection at input, tool-plan, and pre-execution** so a single bypass is not catastrophic (A41468;
   A40432 single-point-insufficient). Do not rely on trailing guardrail text after untrusted content (A41134
   positional injection).
6. **Contain the blast radius downstream.** Because no input filter is a safe floor, pair containment with a
   deterministic action gate (`policy-permission-gates.md`), least-privilege capability isolation
   (`tool-capability-isolation.md`), and human approval on high-stakes/irreversible actions — `refuse()` /
   `ask-consent()` as first-class outcomes (A41090).
7. **Add an out-of-band correctness channel** wherever a score/certificate/LLM verdict is load-bearing (human
   review, provenance, ensemble/denoiser disagreement) and hide verifier internals (A37924).
8. **Log every decision with provenance, asynchronously** (which content was untrusted, which rule fired, why)
   so audit adds zero decision latency (A41468 L4).
9. **Feed adaptive red-team findings back into the normalizer and policy** (A41468 L4; reviewer synthesis).
10. **Instrument over-refusal as a first-class metric** — aggressive containment can over-block benign ingested
    content; measure the false-positive cost against an adaptive benign-ambiguous set (A41074, A41140, A41152,
    A42191 all foreground the trade-off), while staying fail-closed on high-stakes actions.

## Incorrect or fragile implementation patterns

- **Relying on the model's own safety reasoning to resist injection.** Agents ignore safety considerations they
  themselves generated (A41090 self-inconsistency; A42273 CoT-voiced-yet-complies); SCoT "does not close the
  gap" (A41090); a benign-looking jailbreak evades a selective/vulnerable-region router entirely (A41129).
- **Trailing guardrail text appended after untrusted content.** Positional injection defeats it — the malicious
  module is placed *after* the benign request specifically to sit past the guardrail (A41134 MU-BA); the
  boundary must be structural.
- **Concatenating principal intent and ingested content into one flat prompt.** With no channel separation there
  is no boundary to enforce (A41090; A41134).
- **Screening only the latest user turn.** History-injection attacks live in prior "assistant" turns (A40840,
  A36996); "guardrails that inspect only the final user message are insufficient" (A36996 deployment).
- **Trusting caller-supplied conversation history or agent role profiles as authentic** (A40840, A36996; A41134
  BU-MA).
- **Keyword / string / API-name / surface-form matching for the decision.** Falls to semantics-preserving
  substitution and encoding (A40296, A40465, A41058, A40916) — normalize first and screen recovered intent.
- **Single-point enforcement** (only an input filter, or only output moderation). Single-path defenses leak
  (A40432 InterOnly 0.75× / IntraOnly 0.83× vs. dual-path 0.51× relative-mean CRR, author-reported).
- **Making a Guardian LLM the sole authority.** It is itself prompt-injectable (A41468 reviewer synthesis) and,
  as a score/verdict, gameable (A37924).
- **Fail-open on normalizer/detector error or timeout.** Contradicts the "single bypass not catastrophic"
  posture (A41468); an un-decodable input must be held or denied, not passed through.

## Verification strategy

- **Adaptive, defense-aware red-team is the launch gate** — the single most consistent gap across both
  syntheses (A41090 non-adaptive scripted injections; A41468 no adaptive attacker vs. its four layers; A41134
  non-adaptive prompt defense; A40432/A40484 no defense-aware attacker). Any robustness claim "requires
  production validation" before reliance.
- **Test indirect prompt injection explicitly**, with content planted in *every* channel the agent reads —
  messages, memos, posts, files, retrieved docs, tool output (A41090's 50-task template; A41468 poisoned
  sources).
- **Test the BU-MA compromised-internal-agent scenario, not only MU-BA** — the corpus shows the former is far
  harder (A41134).
- **Test encoding/cipher/emoji/cross-lingual and cross-modal evasion of the normalizer** (A40296, A40465,
  A41058, A40916, A40018) — verify canonicalization actually recovers intent.
- **Test forged/transferred conversation history** and the DRI/SRI outline-then-elaborate signature (A40840,
  A36996).
- **Effect/outcome-based evaluation in a sandbox** — classify the *outcome* against environment state (Reject /
  Execution-Failure / Attack-Success), not string matches (A39818 rule/state validity; A41090 rule-based
  state-grounded evaluators over action history / file storage / app DBs).
- **Report absolute residuals, not relative reductions** (A41134 ASR-d; A41468 absolute ADR) and **over-refusal
  / false-positive rate** as a first-class metric (A41074, A41140, A41152, A42191).
- **Do not sign off on a single automated LLM judge** — validate against human agreement; measurement
  circularity is a recurring risk (A41134 GPT-4o judge, author-reported 86.34% agreement; A40866 SceneJailEval,
  author-reported F1 0.917 own / 0.995 JBB, is a better-judge attempt but itself untested against
  evaluator-gaming).
- **Use contamination-resistant / regenerated test cases** so an adversary cannot memorize a fixed checklist
  (A39818 level editor; reviewer synthesis).

## Metrics and thresholds

Track these families; **thresholds are operator-defined per deployment and must be validated against an adaptive
set — the corpus provides no validated universal threshold.**

- **Attack Detection Rate (ADR) per injection class.** A41468 Table 1, **author-reported, coarse ">X%"
  thresholds with no dataset size, FP rate, or statistical treatment** (No Guardrail / LLM-as-Filter /
  InfrastructureSentinel): Direct Prompt Injection 5 / 60 / >90; Indirect Prompt Injection 2 / 25 / >85; Tool
  Poisoning 10 / 15 / >88; Command Injection 15 / 50 / >76; Contextual Policy Violation 0 / 20 / >50. Read the
  residuals: even the strongest config is only >85% on indirect PI and >50% on contextual policy violation.
- **ASR and ASR-under-defense (absolute).** A41134 author-reported IMBIA ASR (MU-BA): ChatDev 93 / MetaGPT 45 /
  AgentVerse 71, reduced by 73 / 40 / 49; (BU-MA): ChatDev 71 / MetaGPT 84 / AgentVerse 45, reduced by
  45 / 7 / 42 — residual absolute ASR remains high, especially BU-MA MetaGPT. History-injection baseline to beat:
  A40840 RA-DRI avg ASR 94.8% across 8 models (author-reported) against an unprotected history channel.
- **Goal-achievement + refusal on matched low/high-risk task pairs** (A41090) — unsafe completion = high
  achievement on injected high-risk tasks; over-caution = high refusal on low-risk tasks.
- **Over-refusal / false-positive rate** on benign ingested content, as a first-class metric (A41074, A41140,
  A41152, A42191) — measure against an adaptive benign-ambiguous set.
- **Normalizer coverage / recovery rate** — fraction of encoded inputs whose canonical intent is recovered
  before screening (motivated by A40296, A40465, A41058, A40916); an uncovered encoding is a silent bypass.
- **Detector FNR under a small rewriter** — A41152 reports intention FNR ~31–33% with a Qwen1.5-1.8B rewriter
  (author-reported); a weak in-line detector is a weak layer.
- **Invalid-action rate** as a cheap runtime health monitor; a spike flags degraded planning or observation
  corruption (A39818).
- **Chunk Recovery Rate (CRR)** for retrieval-surface abuse (A40432: full RAGFort still leaves author-reported
  ~28% residual CRR — mitigation, not elimination).
- **Containment latency and decision-cache hit rate** (A41468 caching/async as the latency lever).

## Test cases

Concrete, corpus-grounded cases the containment pipeline must be exercised against:

1. **Direct jailbreak** requesting a disallowed action at the user channel (A41468; A41090 misuse).
2. **Indirect injection** via a received message / memo / social post / retrieved document / tool output
   instructing an unauthorized action (A41090; A41468).
3. **Positional injection** — malicious instruction appended after a benign request to sit past a trailing
   guardrail (A41134 MU-BA).
4. **Compromised internal agent (BU-MA)** — hidden instruction in an agent role profile, e.g. a tester agent
   silently adding a `send_email` exfiltration function (A41134).
5. **Contextual policy violation** — fabricated "emergency maintenance" context to unlock a restricted path
   (A41468 context manipulation).
6. **Forged conversation history** — injected "assistant" DRI/SRI primer followed by an elaboration trigger
   ("expand this outline", "what are other methods") (A40840); cross-model transferred jailbroken history
   (A36996).
7. **Encoding/cipher/emoji/cross-lingual evasion** of the normalizer (A40296, A40465, A41058, A40916).
8. **Cross-modal injection** — sub-image decomposition + CoT, or instruction carried in an image/audio channel
   the text filter never inspects (A40018; A40607, A40863).
9. **Tool poisoning / masquerading third-party MCP tool** whose description carries an instruction (A41468).
10. **Command injection** in tool arguments, e.g. `run_script('../etc/passwd')` (A41468).
11. **Multi-turn inference leakage** — complementary/aggregation queries each safe in isolation (A40484) — a
    containment-adjacent case where the "injection" is progressive.
12. **Verifier/score spoofing** if any containment input is a certificate or model score (A37924).

## Adaptive adversarial tests

Beyond static cases — attackers who know the containment design:

- **Rewrite the injection to evade the specific detector** — rewrite the malicious payload to defeat the
  deployed guardrail (A41134 reviewer synthesis; ASR-d likely overstates robustness against a motivated
  adversary).
- **Injection optimized against the specific deployed agent** (A41090 reviewer synthesis — scripted results
  overstate robustness vs. an adaptive attacker).
- **Novel encoding outside normalizer coverage** — a new cipher/glyph/cross-lingual recombination the
  canonicalizer does not decode (A41058 releases cipher code; A40916 macaronic; assume attackers have the
  released artifacts).
- **Router/selective-detector evasion** — craft a benign-looking request so a selective detector never triggers
  (A41129, acknowledged).
- **Reasoning-channel injection** — target the same chain-of-thought a prompt-only defense depends on so the
  model reasons about safety and complies anyway (A42273; A41090 self-inconsistency).
- **Verifier gaming** — spoof the artifact a score-based detector keys on; a large certificate for the wrong
  class with imperceptible, semantics-preserving perturbation (A37924, white-box + known-σ).
- **Provenance-spoofing** — attempt to forge attested history or a trusted-role tag; test that the attestation
  binding actually holds (A40840, A36996 note current chat APIs lack this binding).

## Telemetry requirements

Emit structured, tamper-evident trace fields for every decision (A41468 Layer 4; reviewer synthesis on async
explainability):

- **Per-context-element provenance record** — TRUSTED vs UNTRUSTED tag, source channel (message / doc / tool /
  history / file), and the canonicalized (post-normalization) form actually screened (A41090 trust-boundary;
  A40296/A40465 normalize-before-gate).
- **Per-decision record** — recovered intent, detector verdict + confidence (marked advisory), the specific rule
  fired, and a human-readable rationale, generated asynchronously (A41468 L4).
- **Immutable, human-readable audit trail** of the full event chain — and you must supply the integrity/tamper-
  resistance mechanism A41468 asserts but leaves unspecified (reviewer synthesis).
- **Self-inconsistency signal** — flag when the agent's stated safety consideration diverges from its executed
  action (A41090).
- **Injection signatures** — forged-history DRI/SRI outline-then-elaborate patterns and Rejection-Inhibition /
  Output-Limitation phrasing (A40840, A36996); egress primitives inserted by generated code (`send_email`,
  external URL fetch, clipboard/keyboard capture, file encryption — A41134's 12-behavior taxonomy); recursive
  topic-expansion / memory-driven query patterns on the retrieval surface (A40432); cross-turn query
  correlations reconstructing restricted joins/differences (A40484).
- **Normalizer coverage misses** — inputs that could not be decoded to canonical intent (candidate zero-day
  encodings; A40296, A41058, A40916).
- **Invalid-action-rate** time series as a runtime health monitor (A39818).

## Failure handling

- **Fail-closed.** On normalizer failure, un-decodable input, detector timeout, missing provenance, or
  advisory-LLM disagreement → block or hold for human approval. Reviewer synthesis, consistent with the "single
  bypass not catastrophic" defense-in-depth posture (A41468).
- **Treat un-attestable history as untrusted** — if provenance of a prior "assistant" turn cannot be verified,
  classify it as untrusted data and re-screen it, never as authoritative context (A40840, A36996).
- **Degrade to least privilege**, never to open access, when a downstream capability check is unavailable
  (`tool-capability-isolation.md`; A41468 "gate, not replace, least privilege").
- **Latency under load** is bounded architecturally (cache deterministic checks; async audit — A41468), not by
  relaxing the decision.
- **Guardian-LLM / detector compromise is assumed possible** (A41468 reviewer synthesis): because the model
  signal is advisory-only, its compromise cannot by itself mark content trusted or authorize a side effect.
- **Residual harm is assumed**, so failure handling pairs containment with the downstream action gate,
  least-privilege scoping, and human approval on high-stakes/irreversible actions (A41090; A41468).

## Rollback and containment

- **Kill-switch before the actuator / side effect** — halt during planning or immediately before execution, not
  after (A41468 L3; A39818 gate-decides). Injection detection that arrives after the side effect fired has not
  contained it.
- **Blast-radius limits** — least-privilege capability isolation and sandboxed execution bound what a leaked
  instruction can touch (`tool-capability-isolation.md`, `sandboxed-execution.md`; A41134 "block outbound
  email/network from generated apps").
- **Immutable audit for forensics** — the full provenance-tagged event chain supports incident reconstruction
  and identifying which untrusted source carried the injection (A41468 L4).
- **Targeted knowledge erasure as incident containment** — model editing (ROME) to suppress specific memorized
  content without full retraining: A41145 author-reported extraction 65.2% → 1.6%, but this is a single-paper,
  white-box, small-model result, **not adaptively tested** — validate against post-edit re-optimization first
  (A41145 reviewer synthesis).
- **Quarantine the poisoned source** — rate-limit / isolate the retrieval collection, tool, or upstream agent
  identified as the injection vector (A40432 rate-limiting + query monitoring; A41134 supply-chain isolation).
- **Feedback loop** — feed the incident into refined normalizer coverage and policy/thresholds (A41468 L4;
  reviewer synthesis).

## Known bypasses

Demonstrated or corpus-supported bypasses of this pattern's weaker forms:

- **Indirect prompt injection is not fully caught** — "no agent is safe against indirect prompt injection"
  (A41090, author-reported); A41468 residual ADR only >85% on indirect PI and >50% on contextual policy
  violation (author-reported, coarse thresholds).
- **Compromised internal agent (BU-MA) bypasses user-level containment** — author-reported Adv-IMBIA reduced
  BU-MA ASR by only 7% for MetaGPT (vs. 40% for MU-BA); "user-interface-level defense largely fails against
  internally compromised agents" (A41134).
- **Forged/transferred history** defeats last-turn-only screening — RA-DRI avg ASR 94.8% (A40840); CHASE
  cross-model transfer (A36996), both author-reported/abstract-level.
- **Encoding/normalization gaps** — an un-decoded emoji/cipher/cross-lingual/math-code input slips a
  semantically-harmful instruction past a surface matcher (A40296; A40465 author-reported avg ASR 91.19–97.62%
  single-query; A41058 60%+ within ≤10 queries; A40916).
- **Reasoning-channel exploitation** — the model reasons about safety and complies anyway (A42273; A41090
  self-inconsistency), so a CoT-based containment check is not a floor.
- **Guardian-LLM injectability / verifier gaming** — an LLM detector is itself prompt-injectable (A41468
  reviewer synthesis) and a score/certificate is spoofable (A37924, white-box + known-σ).
- **Router evasion of selective detection** — a benign-looking request bypasses a vulnerable-region router
  entirely (A41129).
- **Retrieval-surface residual** — A40432 leaves ~28% residual CRR under its strongest configuration
  (author-reported).

## Residual risks

- **No input-side control drives injection success to a safe floor.** Leading defenses leave material residual:
  A41090 "no agent is safe against indirect prompt injection"; A41468 contextual policy violation >50% / command
  injection >76% ADR; A40432 ~28% residual CRR; A42191 ~31% residual ASR; A40248 ~16% residual harmful on
  Qwen-3-8B despite near-zero on the prefill metric (all author-reported). No paper claims elimination.
- **Adaptive attackers are unevaluated across essentially every defense here** — the largest methodological gap
  (both syntheses). Deployed efficacy may be materially below reported numbers.
- **Normalizer coverage is a moving target** — a new encoding/modality outside coverage is a silent bypass
  (A40296, A41058, A40916; multimodal softer than text A40607/A40863/A40018).
- **Prompt-level reasoning is self-inconsistent** and cannot be the last line (A41090, A42273).
- **The flagship injection-defense paper's evidence is Preliminary** — A41468 ADR is ">X%" thresholds with no FP
  accounting, no dataset size, no artifacts, no adaptive test.
- **History-provenance binding is not native to current chat APIs** — A40840/A36996 note targets accept
  caller-supplied history with no cryptographic binding; you must add server-authoritative state or attestation,
  and its correctness is a new surface.
- **The audit trail's integrity is asserted, not demonstrated** (A41468) — a compromised log undermines
  containment and forensics.
- **Aggressive containment over-blocks benign ingested content**, eroding operator trust; the precision/recall
  frontier is itself a residual risk (A41074, A41140, A41152, A42191 foreground the trade-off).

## Relevant research (stable paper ids from the syntheses/cards)

Primary:
- **A41090** — MobileSafetyBench: indirect-prompt-injection keystone; "no agent is safe against indirect prompt
  injection"; prompt-level safety necessary-but-insufficient; "treat untrusted environment content as data, not
  instructions"; `refuse()`/`ask-consent()`. *Evidence: Strong (as a susceptibility benchmark); its own defense
  (SCoT) is weak/self-inconsistent.*
- **A41468** — InfrastructureSentinel: fullest MCP direct+indirect-injection threat taxonomy + four-layer
  defense-in-depth; Guardian-LLM-as-injectable-trust-anchor caveat; coarse ADR table. *Evidence: Preliminary
  (no adaptive test, no FP accounting, no artifacts).*
- **A40840** — Response Attack: forged assistant-history DRI/SRI priming; RA-DRI avg ASR 94.8% (author-reported);
  authenticate/attest history provenance; screen whole context. *Evidence: Moderate.*
- **A36996** — CHASE: cross-model jailbroken-history transfer via coherence bias; history as untrusted
  integrity-checked asset; per-turn + whole-context moderation. *Evidence: Moderate (numeric results truncated in
  extract).*
- **A41134** — IMBIA / "Shadows in the Code": positional injection into multi-agent pipelines; MU-BA vs. BU-MA
  asymmetry; structural separation of intent from instruction; least-privilege capability isolation. *Evidence:
  Moderate.*
- **A40296 / A40465 / A41058 / A40916** — emoji / math-code (EquaCode) / cipher (MetaCipher) / cross-lingual
  (macaronic) surface-form evasion → normalize before screening. *Evidence: Moderate; author-reported ASR is
  best-case, single/low-query.*
- **A37924** — GhostCert: "a verification artifact is not a correctness oracle"; verifier/score gaming → keep
  detectors advisory, add out-of-band correctness. *Evidence: Strong.*

Supporting: A42273 (distractor masking; CoT-voiced-yet-complies), A41129 (EASE; selective reasoning helps text
refusal, router evadable by benign-looking jailbreak), A41152 (VALOR; layered detect→rewrite→verify; intention
FNR ~31–33% with a small rewriter), A40248 (shallow alignment; enforce deep not at the prefix; prefill
47.5%→0.2% on Llama-3.1-8B author-reported), A40866 (SceneJailEval; scenario-adaptive judge — don't rely on a
single LLM judge), A40432 (RAGFort; dual-path / single-point-insufficient; ~28% residual CRR; retrieval-surface
monitoring), A42191 (RAS; ~31% residual ASR), A41498 (GARD; output-side sensitive-info disclosure detector),
A39818 (TowerMind; "models propose, environment verifies, gate decides"; invalid-action-rate monitor), A40018
(cross-modal sub-image decomposition), A40484 (SafeNLIDB; multi-turn progressive inference leakage), A41145
(CoSPED; ROME targeted erasure for incident containment).

Reviewer-synthesis cross-references (skill artifacts, **not** AAAI corpus papers): sibling patterns
`policy-permission-gates.md` (allow/deny/step-up decision engine), `tool-capability-isolation.md` and
`sandboxed-execution.md` (blast-radius limits); `architecture-patterns.md` P1 (pre-action gate), P2
(effect-based evaluation), P6 (least-privilege credential broker), P10 (async explainability), P12 (adaptive
red-team); `agent-identity.md` (Zero Standing Privilege, just-in-time/just-enough, intent-based access).

## Evidence strength

- **The architectural thesis is well-supported by convergence, not replication.** "Treat untrusted context as
  data, not instructions", "screen the whole context / authenticate history", and "defense-in-depth aligned to
  the agent cognitive cycle" converge across A41090, A41468, A41134, A40840, and A36996 — but these are
  **independent studies in different domains, not independent replications of one result** (both syntheses state
  this explicitly). Treat the convergence as a strong *design* signal, not a measured effect size.
- **The susceptibility evidence is Strong** — A41090 (realistic interactive Android environment, human-annotated
  severity, rule-based state-grounded evaluators, multiple frontier agents) credibly establishes that agents are
  highly vulnerable to indirect injection and that prompt-level safety is insufficient.
- **The "verifier ≠ correctness oracle" caution is Strong** (A37924: large-scale ImageNet, three certified
  defenses, targeted+untargeted, released code).
- **The efficacy of any specific containment implementation is Preliminary-to-Moderate.** The flagship
  injection-defense paper (A41468) is Preliminary (coarse ADR, no adaptive test); A41134 and the history/encoding
  attack papers are Moderate; several headline numbers were truncated in the source extracts (A36996) and are
  marked accordingly.
- **All efficacy numbers are author-reported, not independently verified, and best-case** — no adaptive-attacker
  evaluation exists in the corpus for these defenses. Report absolute residuals and validate on the target stack
  before operational reliance.
- **Deterministic, fail-closed, least-privilege, provenance-tagging design choices are reviewer-synthesis
  engineering best practice** grounded in the papers' failure modes, not themselves a paper-measured result.

## When NOT to use this pattern

- **When the untrusted channel can simply be removed.** If an agent does not need to read a given source, don't
  ingest it and then contain it. Containment is for content that must be read but cannot be trusted (A41090
  trust-boundary; A41134 supply-chain).
- **As the sole control.** Every defense card in the corpus ends with "should be a layer, not the sole control";
  input-side containment alone leaves material residual (A41090 "no agent is safe"; A41468 residual ADR). Pair
  with the downstream action gate, least-privilege, human approval, and adaptive red-team.
- **As a substitute for the action-decision gate or capability minimization.** Deciding allow/deny/step-up is
  `policy-permission-gates.md`; bounding blast radius is `tool-capability-isolation.md` /
  `sandboxed-execution.md`. This pattern owns the *input/context* half only.
- **For pure content-safety / toxicity / disclosure filtering with no untrusted-instruction channel.** That is a
  content-guardrail layer (A41498 GARD, A41152 VALOR), a different concern; containment is about instructions
  smuggled through ingested content.
- **When you would be forced to make an LLM the sole authority** with no structural boundary and no deterministic
  containment. A37924 + A41468 (reviewer synthesis) show a single-artifact/LLM authority is gameable/injectable;
  either establish a structural trust boundary and deterministic checks, or treat the LLM output as advisory-only.
- **For fully reversible, low-stakes actions where containment latency/over-refusal cost exceeds the harm** —
  reserve strict fail-closed containment for high-stakes/irreversible operations (A41090's high-risk task class),
  and measure over-refusal as a first-class cost (A41074, A41140, A41152).
