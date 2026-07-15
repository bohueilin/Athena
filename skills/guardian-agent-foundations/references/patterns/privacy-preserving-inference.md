# Pattern: Privacy-Preserving Inference

> **Scope of evidence.** This pattern is grounded in the AAAI-26 corpus synthesis `Privacy-Protection.md` and its
> underlying research cards. It is scoped to **protecting private data *while a model processes it at inference /
> serving time*** — the prompt, image, embedding, KG entity, or activation that crosses a trust boundary to reach a
> (possibly remote, possibly third-party) model, and the model-derived artifacts (embeddings, smashed
> representations, soft prompts, steering vectors) transmitted alongside it. It is **not** about training-time
> privacy (DP-SGD training), nor about right-to-be-forgotten / deletion (machine unlearning) — those are separate
> concerns in the same synthesis and are out of scope here.
>
> Load-bearing papers: **A42453 (FEM)** — the strongest-evidence entry: a realistic black-box, embedding-only
> adversary reconstructs impersonating faces from FR *and* "privacy-preserving" (PPFR) embeddings, defeating eight
> named protection schemes (author-reported ASR at FAR=0.01, e.g. IRSE50 FEM-KAN 83.7 vs MAP2V 77.9; residual
> 44.5 on GhostFaceNet even for MinusFace) → **artifacts transmitted at inference are identity-bearing secrets,
> reconstruction is offline and server-side-undetectable, so a query-time liveness/injection control is the only
> remaining defense**. **A40874 (SAPA-Bench)** — the most agent-core paper: off-the-shelf MLLM smartphone agents
> recognize privacy-sensitive actions at Risk-Awareness < 60% even with explicit hints (author-reported best
> Gemini 2.0-flash RA(EH) ~67%, GPT-4o 55.03), motivating an **independent recognition→localization→severity→
> human-confirmation gate in the action path** ("capability is not permission"). **A40033 (PCFormer)** — the one
> cryptographic secure-inference paper (HE+MPC two-party, semi-honest, author-reported ~1.9× speedup, no reported
> accuracy loss). **A39212 (InfoDecom)** — split-inference data-reconstruction defense by decompose-then-protect
> (FSInfo metric, honest-but-curious server). **A40534 (ARoG) / A40911 (SOER) / A40041 (PRISM)** — the
> provider-as-adversary controls: anonymize / surrogate / route-and-keep-local before a raw datum reaches an
> untrusted model. **A40720 (PrivSV)** and **A40839 (PIPRA)** — a transmitted steering vector / soft prompt is a
> leakable, membership-bearing artifact (PIPRA output-free MIA avg AUC 87.58% vs 77.05%). **A39710 (DP-NCB)** —
> the *decision/policy sequence itself* leaks per-user outcomes even when stored data is protected. **A39051 (DP
> Linear Programming)** — DP output that still satisfies hard safety constraints. Attack anchors **A39333 (Venom)
> / A37743 (GGSS-R)** — heuristic/DP-noise-perturbed artifacts are analytically reconstructable, so *heuristic
> noise is not a boundary*. Crypto/verifiability frontier **A42229 (HE explanations)** and **A42232 (zkQML)**.
>
> **Evidence integrity (non-negotiable).** Every quantitative value below is **author-reported, single-study, and
> non-adaptive unless stated otherwise**; several cards flag truncated/OCR-approximate tables (A40874, A42453,
> A40911, A40839). Where a paper is silent the text says "not stated in paper". Direct paper findings are
> distinguished from reviewer synthesis. **No paper in this corpus builds or measures an end-to-end agentic
> "privacy-preserving-inference" control**: the cryptographic methods are semi-honest and/or toy-scale (A40033
> semi-honest; A42229 fidelity collapse at MLP-L; A42232 noise-free 4-qubit simulation), and the routing/
> redaction/steering methods (A40534, A40911, A40041, A40773) argue privacy **by construction with no executed
> leakage attack**. The composed control here is therefore **standard privacy engineering that requires
> production validation on the target stack**, using the corpus for threat motivation, mechanism selection, and
> the recurring failure caution — not as a measured efficacy result. Calibrated language only: "reduced
> reconstruction/membership success against the tested, non-adaptive attacks", "requires production validation",
> "not evaluated against" — never "secure / private / unbreakable / proven-safe". The dominant cross-corpus
> caveat, repeated below: **almost no defense here was evaluated against an adaptive, defense-aware attacker**
> (§11–12 of the synthesis), so treat every efficacy number as an upper bound.
>
> **Sibling boundary.** This pattern governs *what private data may leave the trust boundary to a model, in what
> protected form, and whether the egress decision requires human sign-off*. The human sign-off surface itself is
> `human-approval-consequential-actions.md`; the allow/deny egress decision is enforced through
> `policy-permission-gates.md`; treating embeddings/steering-vectors/keys as first-class secrets with custody is
> `least-privilege-credentials.md`; authorizing which private records a retrieval/RAG step may fetch is
> `retrieval-authorization.md`; sealing the privacy dial (ε/FSInfo/…) as configuration-of-record is
> `tamper-evident-traces.md`; and sanitizing untrusted model output that re-enters the agent is
> `prompt-injection-containment.md`. Privacy-preserving inference is the data-confidentiality control those
> siblings assume but do not themselves provide.

---

## Problem addressed

An agent must run inference over **sensitive input** — a user's prompt (PHI, financial intent), an uploaded image
(faces, license plates, IDs), a knowledge-graph entity (a person's residence, diagnosis), or a derived artifact
(embedding, activation, steering vector) — and frequently that inference happens on a model the agent does **not**
control: a third-party LLM API, a cloud MLLM, a split/offloaded compute host, or another agent. The problem is that
**the act of inference itself exposes the private data to the party doing the inference and to anyone who
intercepts the transmitted artifacts** — and the corpus makes three parts of this concrete and load-bearing:

- **The artifacts transmitted at inference time are secrets, not opaque tokens.** A42453 (FEM) demonstrates, under
  a *realistic black-box, embedding-only* threat model, that face embeddings — including embeddings from schemes
  explicitly marketed as "privacy-preserving" (DCTDP, HFCF, PartialFace, MinusFace) and transform-protected
  templates (PolyProtect, MLP-Hash, SlerpFace) — invert to realistic impersonating faces that pass real-world FR
  systems and a commercial API (author-reported ASR at FAR=0.01; residual e.g. 44.5 on GhostFaceNet even for the
  strongest scheme). A40839 (PIPRA) shows a soft/prompt vector leaks training-set **membership with no output
  access at all** (author-reported avg AUC 87.58% vs 77.05% for output-dependent baselines; 90.37% on Caltech101),
  *resistant to output-suppression defenses*. A40720 (PrivSV) treats a shared steering vector (>20,000-D for
  Llama-2-7B) as a leakable artifact carrying member/attribute information. A39212 (InfoDecom) shows split-inference
  "smashed" representations invert back to the raw input, worst when the client-side model is shallow. The direct
  implication: **any model-derived object you send to a counterparty must be treated as reconstructable to the
  private input.**

- **Off-the-shelf models cannot be trusted to notice they are handling sensitive data.** A40874 (SAPA-Bench)
  quantifies that MLLM smartphone agents execute privacy-sensitive actions (reading a clipboard password, uploading
  a contact list, entering credentials) with **Risk-Awareness below 60% even when given explicit hints** (author-
  reported; best Gemini 2.0-flash ~67%, GPT-4o RA(EH) 55.03; task-success 17.51–48.12%). The model's own judgment
  is not a control surface — the recognition of sensitivity must be made by an **independent gate**, not delegated
  to the model whose autonomy created the exposure.

- **Protecting data at rest is insufficient — the decision sequence leaks too.** A39710 (DP-NCB) shows that in a
  feedback-driven sequential decision loop (a bandit/personalization/routing loop), the *arm-selection policy
  itself* leaks each user's private outcome, because future choices depend on past outcomes — even when the stored
  rewards are protected. For agentic routing/personalization, the interaction trace is a leakage channel.

Underneath all three sits the synthesis's most-replicated conclusion (reviewer synthesis over ~9 papers): **heuristic
/ approximate protection leaves an adversarially recoverable residue, and "by-construction" or behavioral evidence
understates it.** A39333 (Venom) reconstructs client images from DP-protected gradients *analytically, without
knowing the noise distribution* (author-reported LPIPS 0.340 vs 0.632, ASR 45% vs 2% at ε=10, δ=10⁻⁵); A37743
(GGSS-R) does the same with a generic diffusion prior. The transferable lesson for inference: **additive "hiding"
noise on a transmitted artifact is not a boundary; only accounted DP, secure computation, or not-sending-the-raw-
data is.** The goal of this pattern is therefore: given a private input and a model that may be untrusted,
**minimize what crosses the trust boundary, protect what must cross it with an accounted (not heuristic) mechanism,
gate the egress decision deterministically with human sign-off on high-sensitivity actions, and treat every
transmitted artifact and the decision sequence as reconstructable** — so that "the model computed an answer" does
not imply "the model (or an interceptor) learned the private input."

## Applicable assets and attack surfaces

- **The raw private input at the point of egress** — the prompt, image, document, or KG record about to be
  transmitted to a model. A40041 (PRISM, PHI/PII prompts), A40534 (ARoG, KG entities like residence/diagnosis),
  A40911 (SOER, faces/plates/IDs/passports in images) all treat this as the primary protected asset and the thing
  that must *not* leave the trusted edge in raw form.

- **Model-derived artifacts transmitted for collaborative/offloaded inference** — embeddings (A42453), soft/prompt
  vectors (A40839), steering vectors (A40720), smashed split-inference representations (A39212), and (training-path,
  but the lesson transfers) gradients (A37743, A39333). Each is independently demonstrated to invert or leak
  membership; each is a first-class secret with egress control.

- **The untrusted model / provider inside the trust boundary.** A40534, A40911, A40720, A40041 all model the
  third-party LLM/MLLM as **honest-but-curious (or worse)**: whatever content reaches it may be retained, analyzed,
  or leaked. This is the confused-deputy surface for agents calling external models — the provider is *inside* the
  data trust boundary, not outside it.

- **The agent action path.** A40874: the sequence recognition→localization→severity→execution where a sensitive
  operation (credential entry, contact upload, precise location, permission grant) is executed *without a
  confirmation checkpoint*. The blind spot is explicitly **low/medium-sensitivity actions** (routine-looking
  clipboard reads, contact uploads), which models flag least reliably.

- **The decision / policy sequence** of a feedback-driven loop (A39710) — observable arm/route/tool selections that
  leak per-user outcomes over time even when stored data is protected. A distinct asset because it leaks *through
  behavior*, not through a datastore.

- **The privacy dial and its secret material** — ε / γ / FSInfo / D / εd²-LDP budget (A39051, A39710, A39212,
  A40041, A40720, A40838) and the crypto keys (CKKS/HE keys A42229, ZK proving/verifying keys A42232, secret-share
  material A38773/A40033). The synthesis is explicit (§15): these are **governed configuration/credentials** with
  custody, rotation, and an incident boundary — see `least-privilege-credentials.md`.

- **The commercial/serving inference API as an extraction target.** A39671 (On Stealing GNNs) shows an encoder can
  be reconstructed offline for free with only a lightweight victim-labeled head (author-reported ~100 queries vs
  ~5,000 for prior SOTA), **defeating a rate-limit + prediction-only defense**. The model itself (`model_weights`/
  `ip`) is an asset exposed *through* the inference interface.

- **The model output / explanation as a leakage vector** — A42229 shows argumentative *explanations* carry PII
  (grounds/counterarguments), so the explanation path, not just the prediction, is in scope; A40773 targets the
  model's own tendency to emit privacy-violating content at inference.

## Threat model

Designed for adversaries who want to **learn the private input, or reconstruct it from what the inference exposes** —
the model provider itself, an interceptor of transmitted artifacts, an observer of the decision sequence, or a
querying client extracting the model. The counterparty performing inference is treated as **untrusted-for-
confidentiality by default**. Grounded threat classes (each tagged with its corpus threat model):

- **Honest-but-curious counterparty (the single most common model in the corpus, §3).** A server/provider/host that
  follows the protocol but tries to infer private inputs, weights, or attributes: A40033, A39212, A38773, A39210,
  A40852, A42229 (implied), A40534/A40911/A40041/A40720 (the provider-as-adversary). **Malicious/active/colluding
  adversaries are almost universally out of scope** and several papers state this explicitly (A40033, A40132,
  A40852) — a critical limitation carried into every claim below.

- **Interceptor of a leaked/transmitted artifact.** An attacker who obtains a released embedding (A42453, black-box
  embedding-only), soft prompt (A40839, output-free), steering vector (A40720), or smashed representation (A39212)
  and reconstructs the input or infers membership **offline, with no further access to the serving system** — so
  server-side monitoring cannot detect the reconstruction step (A42453 monitoring implications).

- **Reconstruction from noise-perturbed artifacts.** An adversary who inverts DP/heuristic-noise-protected
  artifacts analytically or with a generative prior (A39333 noise-prior-free; A37743 diffusion prior) — the direct
  refutation of "we added noise, therefore it's private."

- **Formal, adversary-agnostic worst-case (DP / crypto, §3).** Information-theoretic, adaptive-safe *by
  construction*, unbounded auxiliary knowledge, per-record adjacency: A39051, A39710, A39212 (FSInfo metric),
  A40838, A40720 (Metric-LDP), A40041 (ε-LDP). Important calibration: **these argue privacy from the guarantee, and
  none runs an empirical attack to corroborate the bound** (§12); the guarantee is worst-case for the *specific
  released artifact and trust model* only.

- **Model-extraction / IP-theft via the inference API.** A39671 (encoder-free stealing that defeats rate-limit +
  prediction-only); the protected asset is the model, exposed through queries.

- **Untrusted-host result forgery (integrity of outsourced inference).** A42232 (a cloud quantum host returns a
  wrong result the classical client cannot detect) — the confidentiality *and* correctness side of outsourced
  inference.

- **The decision-sequence adversary.** An observer of policy/arm/route selections inferring per-user outcomes over
  time (A39710) — a behavioral, not data-at-rest, leak.

- **Non-adversarial "agent lacks privacy awareness" failure (A40874).** Not an attack: the agent, acting on a
  benign instruction, exposes sensitive data because no gate recognized the action's sensitivity. In scope because
  it is the dominant *inference-time* privacy failure for autonomous agents.

**Explicitly out of scope for this pattern (handled elsewhere):** stopping the injection that *caused* a bad egress
(`prompt-injection-containment.md`); deciding whether a tool call is *allowed at all* (`policy-permission-gates.md`);
authorizing which private records may be *retrieved* (`retrieval-authorization.md`); training-time DP and
deletion/unlearning (separate synthesis families). This pattern assumes those may be imperfect and ensures that
*whatever data does reach a model is minimized and protected, and the egress decision is gated and recorded.*

**Adaptivity boundary (critical).** The synthesis flags a near-universal absence of adaptive, defense-aware
evaluation (§11–12). The demonstrated bypasses (A42453, A39333, A37743, A39671) are against *other* schemes under
the bypasser's own evaluation; the corpus's own defenses (A40033, A39212, A40534, A40911, A40041, A40720, A40773)
are tested only against non-adaptive attacks or *no executed attack*. Every efficacy expectation here is therefore
an **engineering target requiring production red-teaming**, not a corpus-measured number.

## Control mechanism

Privacy-preserving inference is a **deterministic, fail-closed egress discipline** layered with a protection
mechanism chosen by trust model — not a model verdict about its own behavior. Six composable mechanisms, ordered by
the synthesis's own preference (minimize first, protect what remains, verify, gate):

1. **Data minimization at the trusted edge — send abstractions/surrogates, not raw data (grounded in A40534,
   A40911, A40041; §5, §13).** Before any datum reaches an untrusted model, replace it with the least-revealing
   form that still supports the task: anonymize KG entities to opaque IDs plus a *non-identifying abstract concept*
   (A40534 ARoG — "geographic location" instead of "L.A."); replace sensitive image regions with synthetic
   surrogates and recover the intended edit **locally** so the original never uploads (A40911 SOER); or route the
   highest-sensitivity prompts entirely to trusted local compute and send only an abstracted "sketch" to the cloud
   (A40041 PRISM). This is the corpus's closest confused-deputy control and its cheapest-on-utility one
   (§9 "selective, sensitivity-aware protection preserves utility better than blanket DP/HE/MPC").

2. **Accounted formal protection for what must cross — DP with a logged budget, or secure computation (grounded in
   A39051, A39212, A40720, A40838, A40033; §5).** When a raw or derived artifact must leave the boundary, protect
   it with an *accounted* mechanism whose privacy dial is configuration-of-record — differential privacy (ε /
   Metric-LDP εd² / FSInfo), or cryptographic private inference (HE+MPC A40033; secret-sharing A38773/A39210).
   **Prefer accounted DP / secure computation over heuristic additive noise** (A37743, A39333: heuristic/DP-noise
   artifacts are reconstructable; the *accounted* guarantee, not the noise per se, is the load-bearing property —
   A37854, A39510).

3. **Reduce dimensionality/redundancy *before* adding noise (grounded in A39212, A40720; §13, §15).** Additive DP
   noise scales with dimension, so protect only task-relevant structure: strip task-irrelevant information first
   (A39212 InfoDecom decompose-then-protect; frequency-domain removal + information-bottleneck, then FSInfo-
   calibrated noise), or compress a high-dimensional artifact with a structure-aware reducer before the DP
   mechanism (A40720 PrivSV's HCC then Metric-LDP). This is the recurring way to get a formal guarantee at
   deployable utility.

4. **Deterministic, sensitivity-aware egress gate with human confirmation on high-sensitivity actions (grounded in
   A40874; §6, §14).** An **independent** stage — not the acting model — classifies each candidate egress by
   privacy category and severity (A40874's recognition→localization→severity), then a policy gate
   (`policy-permission-gates.md`) *deterministically* routes it: low-sensitivity → allowed protected egress;
   high-sensitivity (credentials, financial, precise location, permission grants) → **human confirmation required**
   (`human-approval-consequential-actions.md`) before anything transmits. A40874's finding that models score RA
   below 60% even with hints is the reason recognition is delegated to a dedicated classifier and the *decision* to
   a deterministic gate, never to the model's discretion.

5. **Protect the decision/policy sequence, not only data at rest (grounded in A39710).** For feedback-driven
   sequential loops, release statistics under accounted DP *at the point of release* (episodic/batched, ε consumed
   per release event) and widen optimism/confidence bounds to absorb the noise — so the observable policy does not
   leak per-user outcomes.

6. **Query-time defense for the irreducible offline-reconstruction residue (grounded in A42453).** Because a leaked
   embedding/template can be inverted *offline and server-side-undetectably*, the only remaining control at the
   serving interface is **input-side liveness / presentation-attack / injection detection** on queries, plus
   treating an artifact-store exposure as a credential-compromise incident (re-enrollment/revocation). This is a
   containment control, not a prevention of the offline attack.

**Sharp boundary.** These mechanisms give **minimization + accounted confidentiality + a gated, recorded egress
decision**. They do **not** give: (a) protection against a *malicious/colluding* counterparty (out of scope for
almost every corpus method); (b) prevention of *offline* reconstruction of an artifact that has already leaked
(A42453 — only query-time detection and incident response remain); (c) any guarantee that survives without an
executed-attack red-team (§12). DP/crypto guarantees are on the *specific released artifact and trust model* — a
colluding majority (A38773, A40852) or a leaked intermediate checkpoint (A39510) voids them.

## Preconditions and trust assumptions

- **A trusted edge / local compute exists to run minimization.** A40911 (surrogate generation + local recovery),
  A40041 (edge SLM retains the raw prompt and refines the cloud sketch), A40534 (KG owner is trusted) all assume a
  trusted party that never ships the raw datum. If there is no trusted edge, mechanisms 1 and 3 collapse — the
  minimization has to happen *before* the untrusted model sees anything.

- **The sensitivity classifier is good enough to route, and mis-classification fails toward *more* protection.**
  A40041's routing depends on NER accuracy; A40874 shows models classify sensitivity poorly. The precondition is a
  dedicated classifier plus a **fail-closed default**: unknown/uncertain sensitivity is treated as high, not low
  (the corpus does not measure routing-error privacy cost — A40041 reviewer caveat — so this must be validated).

- **The privacy dial is chosen, logged, and budget-accounted for *every* released artifact.** A39311/A39582/A39307
  (synthesis §12) show DP claimed for the headline object but *not* for every shared object voids the guarantee.
  ε / FSInfo / εd² / γ and cumulative budget must be sealed as configuration-of-record (`tamper-evident-traces.md`)
  and budget exhaustion treated as an incident boundary (A40720 kε over k epochs; A39710 per-release ε).

- **Keys and secret material have custody separate from the agent's tool surface.** CKKS/HE decryption keys
  (A42229), ZK proving/verifying keys (A42232), secret-share material (A38773, A40033) are credentials — see
  `least-privilege-credentials.md`. The decryption-key holder is a trusted party by assumption (A42229); if the
  agent can reach the key, HE confidentiality is theatre.

- **The trust model of the chosen crypto matches reality.** A40033/A38773/A40852 are **semi-honest / honest-
  majority only** and *collapse under collusion or an active adversary*. Using them assumes the counterparty will
  not deviate from the protocol — an assumption that must be justified, not inherited.

- **Human approvers are available and non-fatigued for high-sensitivity egress** (A40874 gate depends on a real
  confirmation step) — see `human-approval-consequential-actions.md` for the fatigue/decision-quality preconditions.

- **No adaptive-adversary assurance is inherited from the corpus.** Every threshold here is a design target
  requiring production red-teaming (§11–12). "Privacy-preserving" marketing must be validated against an executed
  attack before trust — A42453 is the cautionary example of eight such schemes inverting under test.

## System architecture

A minimal, deterministic egress pipeline between the agent and any model outside the confidentiality boundary:

```
   ┌──────────────────────── TRUSTED BOUNDARY (edge / local) ────────────────────────┐
   │                                                                                  │
   │  agent request ─► ┌───────────────────────────────┐                             │
   │  (raw private     │ 1. Sensitivity Classifier      │  category + severity        │
   │   input)          │    (dedicated; NOT the model   │  (A40874 recog→localize→    │
   │                   │     under audit — A40874)      │   severity)                 │
   │                   └───────────────┬───────────────┘                             │
   │                                   ▼                                              │
   │                   ┌───────────────────────────────┐                             │
   │                   │ 2. Deterministic Egress Gate   │  fail-closed:               │
   │                   │    (policy-permission-gates)   │  unknown ⇒ treat as HIGH    │
   │                   └───┬───────────┬───────────┬────┘                             │
   │            LOW/none   │   MEDIUM  │    HIGH    │ (credentials/financial/          │
   │                       │           │           │  precise-loc/permission)         │
   │                       ▼           ▼           ▼                                  │
   │              ┌────────────┐ ┌───────────┐ ┌──────────────────────┐               │
   │              │ minimize   │ │ minimize  │ │ HUMAN CONFIRMATION    │               │
   │              │ (A40534/   │ │ + accounted│ │ (human-approval-...)  │               │
   │              │  A40911/   │ │ DP / crypto│ │ then local-only OR    │               │
   │              │  A40041)   │ │ (A39212/   │ │ minimized+DP egress   │               │
   │              └─────┬──────┘ │  A40720/   │ └──────────┬───────────┘               │
   │                    │        │  A40033)   │            │                           │
   │                    │        └─────┬──────┘            │                           │
   │                    ▼              ▼                   ▼                           │
   │             ┌────────────────────────────────────────────────┐                   │
   │             │ 3. Budget Accountant + Trace Seal              │  ε/FSInfo/εd²/keys │
   │             │    (log privacy dial; tamper-evident-traces)  │  as config-of-record│
   │             └───────────────────────┬────────────────────────┘                   │
   │  local-only path (raw stays here) ◄─┤ (fail-closed: no protected form ⇒ deny)     │
   └─────────────────────────────────────┼─────────────────────────────────────────────┘
                                         ▼  (only abstraction / surrogate / DP-noised
                                             artifact / ciphertext crosses)
                     ╔═════════════════════════════════════════════════╗
                     ║  UNTRUSTED MODEL / PROVIDER (honest-but-curious) ║
                     ║  - HE+MPC private inference (A40033/A42229)      ║
                     ║  - or plain API over minimized/DP data          ║
                     ║  - ZK proof of result correctness (A42232)      ║
                     ╚═══════════════════════┬═════════════════════════╝
                                             ▼
                         result / sketch / edited-surrogate / proof
                                             │
   ┌─────────────────────────────────────────┼─────────────────────────────────────────┐
   │  4. Local Recovery / Verify (trusted)    ▼   sanitize-on-return (prompt-injection-  │
   │     - refine cloud sketch w/ local ctx (A40041)   containment) before agent acts    │
   │     - recover edit onto original (A40911)                                           │
   │     - verify ZK proof (A42232)                                                      │
   └─────────────────────────────────────────────────────────────────────────────────────┘
```

- **The classifier is separate from the model under audit.** A40874's central finding (RA < 60%) is that the acting
  model is a poor privacy classifier; recognition is delegated to a dedicated stage and the *decision* to a
  deterministic gate.

- **The gate is deterministic and fail-closed.** Sensitivity → route is a fixed policy, not a discretionary model
  choice; unknown/uncertain sensitivity routes to the most protective path (local-only or human-confirmation), never
  the cheapest. This is the corpus's "reject/defer as a first-class action" posture applied to egress.

- **Only a protected form crosses the boundary** — an abstraction (A40534), a surrogate (A40911), a sketch (A40041),
  a DP-noised artifact after dimensionality reduction (A39212, A40720), or ciphertext under HE+MPC (A40033, A42229).
  The raw input and unprotected artifacts never leave.

- **The budget accountant + trace seal** logs the privacy dial and cumulative budget as configuration-of-record and
  denies egress if no valid protected form can be produced (fail-closed) — sealed via `tamper-evident-traces.md`.

- **The return path is untrusted-on-return.** Cloud output/sketch/explanation is treated as data, not instructions,
  and sanitized (`prompt-injection-containment.md`) before the agent acts on it; where correctness matters, a ZK
  proof (A42232) verifies the outsourced computation.

## Recommended implementation pattern

Deterministic, fail-closed, least-privilege — send the minimum, protect the rest with an accounted mechanism, gate
and seal the decision:

- **Minimize before you protect (A40534, A40911, A40041, A39212).** First ask "does the raw datum need to leave at
  all?" Prefer abstraction (opaque ID + non-identifying concept), surrogate substitution with local recovery, or
  local-only handling of the highest-sensitivity content. Only then apply a protection mechanism to what genuinely
  must cross. This ordering is the synthesis's "reduce what must be protected before protecting it" (§13) and its
  utility-preserving finding (§9).

- **Choose the protection mechanism by trust model, and log its dial.** Untrusted-but-honest provider + raw data
  must cross → cryptographic private inference (A40033 HE+MPC for transformer serving; A42229 CKKS for the
  explanation path) or DP on the released artifact. High-dimensional artifact → structure-aware reduction *then* DP
  (A40720 HCC+Metric-LDP; A39212 decompose+FSInfo). Sequential decision loop → episodic DP release (A39710). In
  every case, **expose ε / FSInfo / εd² / γ / cumulative budget as configuration-of-record** and seal it
  (`tamper-evident-traces.md`).

- **Prefer accounted DP / secure computation over heuristic noise (A37743, A39333, A37854, A39510).** Do not ship
  raw per-client artifacts protected only by hand-tuned additive noise — it is analytically/generatively
  reconstructable. Where DP is used, account for **every** shared object, not just the headline one (§12 caveat:
  A39311 structural graphs, A39582 masses, A39307 digests all voided the guarantee by omission).

- **Preserve hard safety constraints through the privacy mechanism (A39051).** When a privatized value feeds a
  system with invariants (valid ranges, feasibility, safety envelopes), use a constraint-preserving mechanism —
  A39051's one-sided-tightening truncated-Laplace *guarantees the released solution still satisfies the original
  constraints*; A39710 clips private means to [0,1] as safe post-processing — rather than symmetric noise that can
  push the output out of a safe region.

- **Gate egress deterministically with human sign-off on high-sensitivity actions (A40874).** Wire a dedicated
  classifier (privacy category + Low/Medium/High severity) into a deterministic policy gate
  (`policy-permission-gates.md`); require human confirmation (`human-approval-consequential-actions.md`) before
  transmitting anything the classifier marks high-sensitivity (credentials, financial, precise location, permission
  grants). Do not rely on the acting model to self-flag — A40874 shows it will not.

- **Fail closed.** If sensitivity is unknown/uncertain → treat as high. If no valid protected form can be produced
  (DP budget exhausted, HE protocol unestablished, key unavailable) → **deny the egress and keep the datum local**;
  never fall back to plaintext transmission. Log the deferral itself.

- **Keep raw content local and recover locally (A40911, A40041).** Reconstruct the intended result/edit on the
  original *inside* the trusted boundary from the untrusted model's output on the surrogate/sketch — the provider
  never receives raw private data.

- **Treat artifact-store exposure as credential compromise (A42453).** Because reconstruction is offline and
  server-side-undetectable, an embedding/template-store leak triggers re-enrollment/revocation, and the serving
  interface must run input-side liveness/presentation-attack/injection detection on queries.

- **Verify outsourced correctness where it matters (A42232).** For compute you cannot trust to be correct, a ZK
  proof of the inference (parameter-hiding) detects a lying host — at the caveat that current evidence is noise-free
  4-qubit simulation with unmeasured proof cost.

- **Sanitize the model's return before acting on it** (`prompt-injection-containment.md`) — the untrusted model's
  output/sketch/explanation is data, not instructions.

## Incorrect or fragile implementation patterns

- **Delegating the sensitivity decision to the acting model.** Directly refuted by A40874 (RA < 60% even with
  explicit hints). "The model will refuse if it's sensitive" is not a control; recognition must be an independent
  stage feeding a deterministic gate.

- **Treating a transmitted embedding / soft prompt / steering vector / smashed representation as opaque.** A42453
  (embeddings, even "protected", invert), A40839 (soft prompts leak membership with no output access, resistant to
  output suppression), A40720 (steering vectors leak), A39212 (smashed reps invert). Sending a derived artifact
  "instead of the raw data" is not minimization unless the artifact itself is accounted-protected.

- **Relying on heuristic additive noise as a boundary.** A39333 (analytic, noise-prior-free reconstruction) and
  A37743 (diffusion-prior reconstruction) invert noise-perturbed artifacts; A37743's own theory shows noise *raises
  but does not eliminate* the reconstruction-error bound. Noise has value only inside an *accounted* DP mechanism.

- **Claiming DP for the headline artifact while shipping un-accounted side objects.** A39311 (structural graphs),
  A39582 (mass values), A39307 (digests) — the guarantee is voided by any unaccounted shared object (§12). Account
  for everything that crosses.

- **Symmetric DP noise on a value that feeds a hard constraint.** Can push the output out of a safe/valid region;
  use constraint-preserving mechanisms (A39051) instead.

- **"Privacy by construction" with no leakage measurement, trusted as a guarantee.** A40534, A40911, A40041, A40773
  all argue privacy structurally with **no executed inference/linkage/re-identification attack** (each card's
  reviewer caveat). Directionally useful, but do not market as a guarantee — pair with an executed attack (§16).

- **Assuming "we only share gradients/digests/prototypes" is private.** A39307/A39524/A39338 assert data-
  minimization-by-architecture with no attack or accounting; since artifact sharing is a documented leakage vector
  (A37743, A39333), this is contested as security evidence (§10). Data locality ≠ privacy.

- **Trusting a semi-honest crypto protocol against a malicious/colluding counterparty.** A40033/A38773/A40852 are
  semi-honest / honest-majority and **collapse under collusion or active deviation** — using them where the
  counterparty may be malicious is a trust-model mismatch.

- **Letting the agent reach the decryption key / secret material.** Collapses HE confidentiality (A42229's trust
  assumption is a *separate* trusted key holder). Keys live outside the agent's tool surface
  (`least-privilege-credentials.md`).

- **Falling back to plaintext when the protected path fails.** Any non-fail-closed egress path (budget exhausted,
  HE unestablished) that silently sends raw data defeats the control. Deny and keep local.

- **Protecting data at rest but exposing the decision sequence.** A39710: an observable feedback-driven policy leaks
  per-user outcomes even with stored rewards protected. Encrypting the datastore is not enough.

- **Rate-limit + prediction-only as an anti-extraction defense.** A39671 defeats exactly this (encoder-free stealing,
  ~100 vs ~5,000 queries). Detect information-dense/centroid-proximal small query sets, not just volume.

- **Treating MSE / a metric bound as perceptual privacy.** A39212 itself flags MSE is a known-imperfect proxy;
  FSInfo is a *metric* guarantee, not (ε,δ)-DP. Complement with perceptual metrics and an executed attack.

## Verification strategy

- **Executed-attack red-team before trusting any formal-DP/crypto/by-construction claim (the recurring §16
  recommendation).** Run membership-inference, attribute-inference, and reconstruction/inversion attacks against the
  actual transmitted artifact and the actual pipeline — do **not** treat a formal ε/FSInfo/εd² bound or a "raw data
  never leaves" argument as evidence on its own. A42453 is the cautionary case: eight "privacy-preserving" schemes
  inverted under an executed attack.

- **Egress-boundary conformance test.** Assert that for every sensitivity class, only the intended protected form
  crosses the boundary — capture the actual bytes transmitted and confirm no raw private field, unprotected
  embedding, or un-noised artifact leaves (A40534/A40911/A40041 "raw never uploaded" invariant).

- **Gate-coverage and fail-closed test.** Confirm every high-sensitivity egress requires human confirmation
  (A40874) and that unknown/uncertain sensitivity routes to the most protective path — including the negative case
  (budget exhausted / key unavailable ⇒ deny, not plaintext).

- **Budget-accounting audit.** Verify ε / FSInfo / εd² is logged for **every** released artifact (not just the
  headline one — §12) and that cumulative budget (kε over releases/epochs, A40720; per-release, A39710) is tracked
  and enforced.

- **Constraint-preservation check (A39051).** Where a privatized value feeds a hard constraint, assert the released
  value still satisfies it under the noise mechanism.

- **Decision-sequence leakage probe (A39710).** For feedback loops, attempt to infer a per-user outcome from the
  observable policy sequence; confirm episodic DP release bounds it.

- **Non-determinism / metric-fidelity caveat.** A39212 (MSE imperfect proxy) and the OCR/truncation caveats
  (A40874, A42453, A40911, A40839) mean corpus numbers are upper bounds; verify on your own data and models.

- **Adaptive red-team (launch gate).** Because the corpus almost never evaluates an adaptive attacker (§11–12), an
  explicit adaptive exercise — an attacker who knows the minimization/DP/routing pipeline and optimizes against it —
  is required before launch. Pre-adaptive numbers are upper bounds.

## Metrics and thresholds

*Operational invariants below are engineering targets requiring production validation — not corpus-measured
efficacy. Author-reported corpus numbers are labeled and are motivational, not measurements of this pattern.*

- **Raw-egress rate → target 0.** No raw private field / unprotected artifact crosses the boundary (A40534/A40911/
  A40041 invariant). Any occurrence is a P1 confidentiality incident.

- **High-sensitivity-egress human-confirmation coverage = 100%** (A40874). Every credentials/financial/precise-
  location/permission egress passes through a human gate; 0 auto-executed high-sensitivity actions.

- **Fail-closed conformance: unlogged-or-unprotected egress rate → 0.** Budget-exhausted / key-unavailable / HE-
  unestablished ⇒ deny; never plaintext fallback.

- **Privacy-dial coverage = 100% of released artifacts carry a logged, accounted ε/FSInfo/εd²/γ and consume from a
  tracked cumulative budget** (§12; A40720 kε; A39710 per-release). Budget exhaustion is an incident boundary.

- **Executed-attack success rate (MIA / attribute-inference / reconstruction) against the transmitted artifact —
  measured, not assumed.** Track and drive down; treat any formal bound as unproven until this is run (§16).

- **Sensitivity mis-classification rate** and its privacy cost — A40041 flags routing depends on NER accuracy and
  the privacy impact of mis-routing is *not quantified in the corpus*; measure it and fail mis-classification toward
  more protection.

- **Corpus reference numbers (author-reported; motivation, not this pattern's efficacy):** FEM face-reconstruction
  ASR at FAR=0.01 up to 83.7 (IRSE50), residual 44.5 on GhostFaceNet for MinusFace (A42453) — why embeddings are
  secrets and query-time detection is required; SAPA-Bench RA(EH) < 60%, best ~67% (A40874) — why the gate is
  independent of the model; PIPRA output-free MIA avg AUC 87.58% vs 77.05% (A40839) — why prompt vectors are
  membership-bearing; Venom reconstruction ASR 45% vs 2%, LPIPS 0.340 vs 0.632 at ε=10 (A39333) — why heuristic
  noise is not a boundary; PCFormer ~1.9× private-inference speedup, semi-honest (A40033); DP-NCB ε=0.2 operating
  point (A39710); GNN stealing ~100 vs ~5,000 queries defeating rate-limit+prediction-only (A39671); HE-explanation
  IO-unfaithfulness collapse 0.0499→0.4454 at MLP-L (A42229); zkQML fidelity >0.9996 at noise-free 4-qubit (A42232).
  All author-reported, non-adaptive, single-study, several OCR-approximate — do not restate as this pattern's
  efficacy.

## Test cases

Functional / boundary (deterministic, must pass):

1. **High-sensitivity egress without human confirmation** (credential entry — A40874) → blocked; gate requires
   human sign-off; 0% auto-execution.
2. **Unknown/uncertain sensitivity classification** → routed to the most protective path (local-only or human
   confirmation), never the cheapest.
3. **Raw private field about to cross the boundary** (KG entity "lives in L.A." — A40534) → replaced by opaque ID +
   non-identifying concept before transmission; raw never leaves.
4. **Sensitive image region uploaded to a cloud MLLM** (A40911) → surrogate substituted, original recovered locally;
   captured egress contains no original private region.
5. **High-dimensional artifact released without dimensionality reduction** (A40720 raw SV; A39212 shallow-bottom
   smashed rep) → rejected; requires structure-aware reduction *then* accounted DP.
6. **Artifact protected only by hand-tuned additive noise** (A37743/A39333) → rejected; requires an accounted DP
   mechanism, not heuristic noise.
7. **DP claimed for the headline artifact but a side object shipped un-accounted** (A39311/A39582/A39307) → flagged;
   budget-coverage audit fails.
8. **DP budget exhausted / HE protocol unestablished / key unavailable** → egress denied, datum kept local, deferral
   logged (fail-closed); never plaintext fallback.
9. **Privatized value feeding a hard constraint** (A39051) → constraint-preserving mechanism used; released value
   still satisfies the constraint.
10. **Feedback-loop policy sequence probed for a per-user outcome** (A39710) → episodic DP release bounds it.
11. **Semi-honest crypto used where the counterparty may be malicious/colluding** (A40033/A38773/A40852) → flagged
    as a trust-model mismatch; requires justification of the honesty assumption.
12. **Agent tool surface attempts to read the HE/ZK/secret-share key** (A42229) → denied by key custody
    (`least-privilege-credentials.md`).
13. **Embedding/template store exposure** (A42453) → treated as credential compromise: re-enrollment/revocation
    triggered; query-side liveness/injection detection active.
14. **Untrusted cloud returns a wrong result** (A42232) → ZK proof verification fails; result rejected.
15. **Untrusted model's returned sketch/output contains instruction-shaped text** → sanitize-on-return
    (`prompt-injection-containment.md`) treats it as data; agent does not obey it.

## Adaptive adversarial tests

*Required because the corpus almost never evaluates an adaptive, defense-aware attacker (§11–12); results are the
real evidence and pre-test numbers are upper bounds.*

- **Adaptive artifact inversion.** An attacker who knows the minimization/reduction/DP pipeline retrains an inverter
  specifically against the *reduced, IB-regularized, DP-noised* artifact (A39212 explicitly did **not** run a fully
  adaptive DRA against its own pipeline; A40720 tested only MIA). Success = reconstruction/attribute inference above
  the accepted bound.
- **Adaptive re-identification against "by-construction" minimization.** Attempt linkage/re-identification from
  abstracted concepts (A40534 — concept strings may narrow identity), surrogate-plus-recovered outputs (A40911 — no
  de-anonymization test in-corpus), or masked-but-context-rich prompts (A40041 — the masked-name-plus-"black dog"
  linkage the paper motivates but does not empirically defend).
- **Routing-manipulation.** Craft inputs that the sensitivity classifier mis-routes to a lower-protection path
  (A40041 NER-dependence); confirm the fail-closed default catches them.
- **Composition/budget-drift attack.** Issue correlated multi-query sequences to exploit un-accounted composition
  (A40041 flags sequential-composition drift is unanalyzed; A40720 cumulative kε); confirm budget accounting binds.
- **Model-extraction against the serving API** (A39671): information-dense/centroid-proximal small query set;
  confirm detection is not volume-only.
- **Collusion / malicious-deviation** against a semi-honest crypto deployment (A40033/A38773/A40852) — confirm the
  documented collapse and that the deployment does not rely on the guarantee where collusion is plausible.
- **Decision-sequence inference** against the feedback loop (A39710) beyond the analytic ε — an executed attack the
  paper itself did not run.

## Telemetry requirements

Signals to emit (and seal into the trace, `tamper-evident-traces.md`):

- **Per-egress: sensitivity category + severity, the protection mechanism applied, and the exact protected form
  transmitted** (A40874 recognition/severity; A40534/A40911/A40041 minimization). Raw-field-crossing = P1 alert.
- **Human-confirmation events on high-sensitivity egress** and coverage gauge (A40874) — the primary blind spot is
  low/medium-sensitivity actions the model under-flags, so log those explicitly.
- **Privacy-dial and cumulative-budget consumption per released artifact** — ε / FSInfo / εd² / γ and kε
  (A40720, A39710, A39212, A40041, A40838); budget exhaustion pages as an incident.
- **Fail-closed deferrals** — egress denied for budget/key/protocol reasons (never plaintext fallback).
- **Executed-attack assurance metrics** — periodic MIA/attribute/reconstruction success against the transmitted
  artifact (§16) as a running assurance signal, not a one-time check.
- **Sensitivity mis-classification / mis-routing events** (A40041) — routing confusion and its privacy cost.
- **Serving-API extraction signals** — information-dense/centroid-proximal small query sets, not just request
  volume (A39671).
- **Artifact-store access/exposure events** (A42453) — treated as credential-compromise triggers.
- **Return-path sanitization events** — instruction-shaped content in a model's returned sketch/output
  (`prompt-injection-containment.md`).
- **Key custody / rotation events** for HE/ZK/secret-share material (A42229, A42232; `least-privilege-credentials.md`).

## Failure handling

- **Fail closed on the egress path.** If sensitivity is unknown/uncertain, treat as high. If no valid protected form
  can be produced (DP budget exhausted, HE unestablished, key unavailable, crypto trust-model unmet) → **deny the
  egress and keep the datum local**; never plaintext fallback. Log the deferral. This is the corpus's "reject/defer
  as a first-class action" posture applied to data confidentiality.

- **Fail loud on protection-mechanism error.** A DP-budget-accounting error, an un-accounted side object (§12), or a
  constraint violation under noise (A39051) is surfaced as an incident, not silently absorbed.

- **Human-in-the-loop on high-sensitivity egress** (A40874) — degrade toward *more* confirmation under uncertainty,
  not less; a mis-classified low/medium action is the documented blind spot.

- **Artifact-store exposure = credential-compromise incident** (A42453): revoke/re-enroll, rotate any keyed
  protection, and treat all embeddings/templates in the exposed store as reconstructable — because the offline
  reconstruction is undetectable server-side, containment is the only remaining lever.

- **Degrade to local-only, not to plaintext-remote.** If the trusted edge cannot produce a protected form for a
  given datum, the safe degradation is to handle it entirely locally (A40041 keeps high-sensitivity prompts local),
  not to send it in the clear.

- **Semi-honest-crypto trust-model breach.** If collusion/active deviation becomes plausible (A40033/A38773/A40852),
  stop relying on the guarantee for that counterparty and fall back to minimization/local-only — the guarantee does
  not degrade gracefully past its threshold.

## Rollback and containment

- **Revoke and rotate on exposure.** An embedding/template/artifact-store leak (A42453) or key exposure (A42229,
  A42232) triggers re-enrollment/revocation and key rotation; every artifact in the exposed store is treated as
  already reconstructed offline (the attack is server-side-undetectable).

- **Freeze egress to a compromised counterparty.** On evidence of collusion/malice or a failed ZK verification
  (A42232), cut the untrusted model out of the trust boundary and route to local-only / an alternate provider via
  `policy-permission-gates.md`.

- **Tighten the privacy dial, do not loosen it, under uncertainty.** If an executed attack improves against the
  transmitted artifact (A39212/A40720 monitoring implications), raise the FSInfo/ε target (more noise / more
  aggressive minimization) or stop releasing that artifact — treat the dial as the containment lever.

- **The decision sequence cannot be un-leaked** (A39710) — containment is prospective (episodic DP release from now
  on) plus disclosure; past observable policy shifts may already have leaked.

- **Preserve evidence.** Containment actions (revocation, rotation, egress freeze, dial tightening) are recorded as
  sealed trace entries (`tamper-evident-traces.md`) so the response is auditable.

- **"Delete my data" is risk reduction, not guaranteed erasure of what already left.** Data already transmitted to a
  third-party model (even minimized) may be retained; disclose residual risk rather than claim erasure (synthesis
  §14–16, generalizing the unlearning-is-approximate finding to transmitted inference data).

## Known bypasses

**Demonstrated in-corpus against *other* schemes (not against this composed pattern — no such system is evaluated
there), transplanted as cautions:**

- **Offline reconstruction of a leaked artifact.** A42453 (embeddings, even "protected", invert to impersonating
  faces, black-box embedding-only, server-side-undetectable); A40839 (soft prompts leak membership output-free,
  resistant to output suppression); A40720/A39212 (steering vectors / smashed reps invert). Minimization and DP
  *reduce* residual reconstructability; they do not close it, and once an artifact leaks the reconstruction is
  offline. Only query-time liveness/injection detection + incident response remain (A42453).

- **Analytic/generative inversion of noise-perturbed artifacts.** A39333 (noise-prior-free), A37743 (diffusion
  prior) — the bypass of "we added noise." Accounted DP raises but does not eliminate the reconstruction bound
  (A37743 theory).

- **Un-accounted side-object leakage.** DP on the headline artifact while a structural graph / mass / digest ships
  un-accounted (A39311, A39582, A39307) — the guarantee is voided by the omission.

- **Re-identification through "by-construction" minimization.** Abstracted concepts can narrow identity (A40534
  reviewer caveat); masked-but-context-rich prompts enable linkage (A40041 motivating example) — none of these
  papers runs a de-anonymization attack, so residual leakage is unquantified.

- **Collusion / active deviation against semi-honest crypto.** A40033/A38773/A40852 collapse past their honesty/
  honest-majority threshold with no graceful degradation.

- **Model extraction through the serving API.** A39671 defeats rate-limit + prediction-only (encoder-free, ~100 vs
  ~5,000 queries).

- **Decision-sequence leakage** surviving data-at-rest protection (A39710).

- **HE/ZK deployability failure as a de-facto bypass.** A42229 fidelity collapse at MLP-L (IO 0.0499→0.4454) and
  A42232 toy 4-qubit scale mean crypto private inference may be forced back to weaker protection at useful scale —
  a pressure to fall back to plaintext (which the fail-closed rule must resist).

**Corpus adaptivity caveat:** none of the above has been evaluated against an adaptive attacker targeting *this*
composed egress pipeline — that evaluation is a launch gate, not a corpus deliverable.

## Residual risks

- **Malicious/colluding counterparties are essentially unaddressed by the corpus** — the near-universal out-of-scope
  assumption (A40033, A40132, A40852, A38773). The pattern's confidentiality against an *actively malicious*
  provider is not corpus-supported and requires production validation.

- **Offline reconstruction of already-transmitted artifacts is irreducible** (A42453) — minimization/DP lower but do
  not eliminate it, and once an artifact leaves you cannot detect or undo the reconstruction. Query-time detection
  and incident response are the only remaining controls.

- **Formal guarantees are on the specific released artifact and trust model only** — voided by collusion (A38773,
  A40852), leaked intermediate checkpoints (A39510), or un-accounted objects (A39311, A39582, A39307), and never
  corroborated by an executed attack in-corpus (§12).

- **"By-construction" privacy has no leakage metric** (A40534, A40911, A40041, A40773) — the utility claims are
  strong and reproducible, the privacy claims are directional until an executed attack is run.

- **The sensitivity classifier is a single point of failure** — A40874 shows models classify sensitivity poorly and
  A40041's routing depends on NER accuracy whose privacy cost is unquantified; mis-classification toward less
  protection is the dominant operational residual.

- **The decision sequence and the metric-privacy proxy leak** — A39710 (policy sequence), A39212 (MSE/FSInfo is an
  imperfect perceptual-privacy proxy).

- **Crypto private inference is not deployable at useful scale in-corpus** — semi-honest, toy-scale, or fidelity-
  collapsing (A40033, A42229, A42232); scaling is asserted, not shown (§16).

- **No adaptive-adversary assurance is inherited** — the dominant residual across the synthesis; every threshold is
  a design target requiring production red-teaming.

## Relevant research (stable paper ids from the syntheses/cards)

**Load-bearing (motivation, mechanism, and the central cautions):**
- **A42453** — FEM / *Realistic Face Reconstruction from Facial Embeddings via Diffusion Models* (AAAI-26, full
  paper): black-box embedding-only reconstruction defeats normal FR *and* eight "privacy-preserving"/protected
  template schemes (author-reported ASR at FAR=0.01, e.g. IRSE50 FEM-KAN 83.7 vs MAP2V 77.9; residual 44.5 on
  GhostFaceNet for MinusFace) → transmitted embeddings are secrets; reconstruction is offline/server-side-
  undetectable; query-time liveness/injection detection is the only remaining control. **Strongest evidence in the
  corpus.** Attack paper, no defense proposed; injection assumes no liveness (not modeled).
- **A40874** — SAPA-Bench / *Mind the Third Eye!* (AAAI-26; code github.com/Zhixin-L/SAPA-Bench): MLLM smartphone
  agents' privacy Risk-Awareness < 60% even with explicit hints (author-reported best Gemini 2.0-flash ~67%, GPT-4o
  RA(EH) 55.03, SR 17.51–48.12%) → independent recognition→localization→severity→human-confirmation gate in the
  action path. Ground truth partly GPT-4o-generated; static/non-adversarial benchmark, no built mitigation.
- **A40033** — PCFormer (AAAI-26; Microsoft SEAL 4.1): HE+MPC two-party private transformer inference, semi-honest,
  author-reported ~1.9× speedup, no reported GLUE accuracy loss. Semi-honest only; data-dependent masking leakage
  not analyzed.
- **A39212** — InfoDecom (AAAI-26; code github.com/SASA-cloud/InfoDecom; arXiv:2511.13365): split-inference DRA
  defense by decompose-then-protect (frequency removal + information bottleneck + FSInfo-calibrated noise);
  honest-but-curious server; **FSInfo metric, not (ε,δ)-DP**; vision-only; MSE imperfect proxy; no fully-adaptive
  DRA against the pipeline.
- **A40534** — ARoG (AAAI-26; code github.com/NLPGM/ARoG): anonymize KG entities to opaque MIDs + non-identifying
  abstract concepts so raw entities never reach a third-party LLM (provider-as-adversary). Privacy by construction,
  **no executed leakage attack**; assumes relations non-sensitive.
- **A40911** — SOER (AAAI-26): redact-then-recover surrogate editing so a cloud MLLM never sees the raw image;
  recovery done locally. Privacy by construction, **no de-anonymization test**; ground-truth edits MLLM-generated.
- **A40041** — PRISM (AAAI-26; code github.com/Junfei-Z/PRISM): sensitivity-aware cloud-edge routing + two-layer
  LDP; high-sensitivity prompts kept local, cloud gets an abstracted sketch refined locally. ε-LDP composition,
  **no executed inference/linkage attack**; NER-dependent routing; synthetic data.
- **A40720** — PrivSV (AAAI-26): DP steering vectors under Metric-LDP (εd²) after structure-aware reduction (HCC);
  treats a shared SV as a leakable artifact; MIA evaluated. Metric-LDP is metric-dependent; only-MIA empirical;
  cumulative kε; no code link in extracted text.
- **A40839** — PIPRA (AAAI-26): output-free membership inference from soft/prompt vectors (author-reported avg AUC
  87.58% vs 77.05% output-dependent; 90.37% Caltech101), resistant to output suppression → prompt vectors are
  membership-bearing.
- **A39710** — DP-NCB (AAAI-26; code github.com/NP-Hardest/DP-NCB): the decision/policy sequence leaks per-user
  outcomes even when stored data is protected; ε-DP episodic release + clip-to-[0,1] post-processing. Synthetic;
  **no executed privacy attack**.
- **A39051** — DP Linear Programming (AAAI-26): one-sided-tightening truncated-Laplace DP that *guarantees* the
  released solution still satisfies the original hard constraints — the canonical "DP must coexist with safety
  invariants" pattern. Formal; no executed attack; synthetic/single-dataset.
- **A39333** — Venom (AAAI-26): analytic, noise-prior-free reconstruction from DP-protected gradients (author-
  reported LPIPS 0.340 vs 0.632, ASR 45% vs 2% at ε=10, δ=10⁻⁵) → heuristic/DP-noise artifacts are reconstructable.
- **A37743** — GGSS-R (AAAI-26): diffusion-prior gradient inversion of noise-perturbed/DP gradients; contributes the
  reusable Reconstruction-Vulnerability (RV) architecture-audit metric; theory shows noise raises but does not
  eliminate the reconstruction bound.

**Supporting:**
- **A42229** — Privacy-Preserving Argumentative Explanations (AAAI-26, Student Abstract): CKKS-encrypted end-to-end
  inference+explanation; ReLU→x²+x and hard→soft k-means approximations; **fidelity collapse at MLP-L**
  (IO-unfaithfulness 0.0499→0.4454); toy tabular scale, 16 samples. The explanation path carries PII too.
- **A42232** — zkQML (AAAI-26, Student Abstract): ZK proof of outsourced (quantum) inference with parameter hiding;
  classical verifier; noise-free 4-qubit MNIST simulation only; **ZK cost unmeasured**.
- **A39671** — On Stealing GNNs (AAAI-26): encoder-free model extraction (~100 vs ~5,000 queries) that defeats
  rate-limit + prediction-only → serving APIs are extraction targets; detect information-dense query sets, not just
  volume.
- **A40773** — Know-Then-Do (AAAI-26): inference-time, training-free representation steering for privacy behavior;
  LLM→VLM transfer; **benchmark behavior, not an adversarial leakage attack**; uneven per-model gains; over-steer
  (PPL) risk. Dataset GPT-4o/Claude auto-labeled.
- **A40838** — DP-ICL (AAAI-26): DP synthetic in-context demonstrations with single-budget composition; formal, no
  executed attack.
- **A38773 / A39210 / A40852 / A40132** — MPC / secret-sharing secure computation (honest-majority / semi-honest);
  strong under their trust model, collapse under collusion; small-scale (MNIST-scale, ~2000-sample). **A39502** is a
  crypto-PI efficiency method that *assumes* an underlying private-inference protocol.
- **A39510** — improved DP-SGD analysis (AAAI-26): the "formal DP done right" anchor and the load-bearing caveat
  that the tighter guarantee dies if intermediate checkpoints leak — cited for the trust-boundary caution.
- **`Privacy-Protection.md` §3, §9–16 (reviewer synthesis)** — the "model-derived artifacts are secrets", "heuristic
  noise leaves recoverable residue", "formal DP/MPC only as strong as accounting + trust boundary", "selective
  protection beats blanket", and "enforce privacy in the action path" cross-cutting conclusions this pattern
  operationalizes.

**Off-topic / not privacy evidence (per §2, do not cite as support):** A37244, A37472, A37551, A37748, A37979,
A38004 ("noise injection" is a regularizer, not DP), A38130, A38297, A42140; and the "privacy-by-architecture with
no accounting" papers A39307, A39524, A39338, A38021 (contested as security evidence since artifact-sharing is a
documented leakage vector).

## Evidence strength

- **Threat motivation: strong (convergent, multi-paper, some with realistic threat models).** That transmitted
  artifacts invert/leak (A42453 strong-evidence, A40839, A40720, A39212), that models fail to self-recognize
  sensitive actions (A40874), that heuristic noise is reconstructable (A39333, A37743), and that the decision
  sequence leaks (A39710) are consistent across independent cards. A42453 in particular carries a *realistic
  black-box, embedding-only* threat model and a commercial-API evaluation — the strongest evidence in the corpus.
  Still: author-reported, single-study, mostly non-adaptive.

- **The minimization / routing / surrogate controls: moderate on utility, weak-on-privacy-measurement.** A40534,
  A40911, A40041, A40773 report strong, reproducible *utility*, but their *privacy* is argued **by construction with
  no executed leakage attack** — directionally supported, not benchmarked as a confidentiality guarantee.

- **The formal-DP controls: formally sound, empirically un-corroborated.** A39051, A39710, A40720, A39212, A40838
  carry guarantees (feasibility/regret/FSInfo/εd²) but **none runs an empirical attack to corroborate the bound**
  (§12); the guarantee is on the specific artifact and trust model only.

- **The cryptographic private-inference controls: standard security engineering, semi-honest and/or toy-scale
  in-corpus.** A40033 (semi-honest, ~1.9×), A42229 (fidelity collapse at MLP-L), A42232 (noise-free 4-qubit) — the
  construction is sound engineering but *not* corpus-validated at production scale or against malicious adversaries.

- **The composed egress pipeline: not built or measured by any corpus paper.** No paper implements an end-to-end
  agentic privacy-preserving-inference gate. Treat the composition as **requiring production validation on the
  target stack**, using the corpus for motivation and mechanism selection.

- **Adaptive-adversary assurance: none inherited.** The synthesis flags near-universal absence of adaptive,
  defense-aware evaluation (§11–12); every operational threshold here is an engineering target and adaptive red-team
  is a launch gate.

- **Calibration:** claims are "reduced reconstruction/membership success against the tested, non-adaptive attacks",
  "not evaluated against a malicious/colluding counterparty", and "requires production validation" — never
  "private/secure/proven-safe". Several corpus numbers are OCR-approximate (A40874, A42453, A40911, A40839) and are
  treated as author-stated, motivational, not this pattern's efficacy.

## When NOT to use this pattern

- **When the inference is fully local on trusted compute and no private data or derived artifact crosses a trust
  boundary.** If the model and data stay inside the confidentiality boundary, egress gating and DP/crypto protection
  are over-engineering; a plain access control suffices. The corpus's controls all presuppose an untrusted
  counterparty (A40033, A40534, A40911, A40041, A40720).

- **When the data is genuinely non-sensitive.** Blanket DP/HE/MPC costs utility (§9); the synthesis's own finding is
  that *selective, sensitivity-aware* protection wins — do not protect what carries no privacy risk. But default to
  protecting when sensitivity is unknown (fail-closed).

- **As a substitute for the upstream/sibling controls.** This pattern does not stop the injection that caused a bad
  egress (`prompt-injection-containment.md`), does not decide whether a tool call is allowed at all
  (`policy-permission-gates.md`), does not authorize which records may be retrieved (`retrieval-authorization.md`),
  and is not the human-approval surface itself (`human-approval-consequential-actions.md`) — it decides *what
  private data may leave, in what protected form*. Deploying it *instead of* those is a misuse.

- **As protection against a malicious/actively-colluding counterparty, on corpus evidence alone.** Almost every
  method here is semi-honest / honest-majority (A40033, A38773, A40852) and collapses past that threshold — do not
  claim malicious-adversary confidentiality without a mechanism and validation the corpus does not provide.

- **As a *guaranteed* erasure or a *proven* privacy boundary.** Reconstruction of leaked artifacts is offline and
  irreducible (A42453); "by-construction" privacy is unmeasured (A40534/A40911/A40041); formal bounds are
  un-corroborated by executed attacks (§12). Where a hard guarantee is required and cannot be validated, document
  the residual risk explicitly rather than claim privacy.

- **When crypto private inference cannot meet the fidelity/latency bar at your scale.** A42229 (fidelity collapse at
  MLP-L) and A42232 (toy scale) show HE/ZK are not universally deployable; if the protected path cannot be made to
  work, the correct response is minimization/local-only (fail-closed), **not** a plaintext-remote fallback.
