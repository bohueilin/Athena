# Cross-Cutting Chapter — Retrieval and Multi-Keyword Systems

> **What this chapter is.** A cross-paper reading of retrieval-security threads that emerge only when the
> *Multi-keyword-match* and *Privacy-Protection* AAAI-26 syntheses are analyzed together. It is not a paper list;
> it is an argument about where retrieval-layer defenses hold, where they break under adaptive/compositional/
> real-world adversaries, and what that means for launch gates on an enterprise RAG / guardian-agent stack.
>
> **Source provenance.** Every claim traces to one of two upstream syntheses in this repo:
> `references/syntheses/Multi-keyword-match.md` (69 AAAI-26 papers) and `references/syntheses/Privacy-Protection.md`
> (73 AAAI-26 papers). Paper ids (e.g. A40462) are the upstream identifiers. Numbers are **author-reported under
> each paper's evaluated threat model** unless labeled "reviewer synthesis"; a value absent upstream is written
> **"not stated in paper."** No titles, authors, venues, datasets, metrics, or attack/defense numbers are
> invented here. Where the upstream synthesis marked a table "truncated in extracted text," that limitation is
> carried forward and the number is treated as author-stated, not reviewer-verified.
>
> **Calibrated language.** Findings hold "under the evaluated threat model" and "against the tested attacks." No
> absolutes (secure / unbreakable / proven-safe). "Reduced ASR against the tested attacks" ≠ "robust."

---

## 0. Two evidence-integrity warnings that gate everything below

**Warning 1 — the bucket is keyword-assembled, not retrieval-security-curated.** The upstream *Multi-keyword-match*
category was built by token overlap ("adversarial", "robustness", "privacy", "federated", …), **not** by retrieval
relevance — its own synthesis states this as the category's "most important structural fact." So "Retrieval and
Multi-Keyword Systems" here means *the retrieval-relevant subset of two keyword buckets*, read across teams. Do not
read "N papers on retrieval security" out of it.

**Warning 2 — classical searchable-encryption is absent.** Neither synthesis contains a paper on searchable
symmetric encryption, multi-keyword-ranked-search-over-encrypted-cloud-data, or ORAM-style access-pattern hiding.
The "multi-keyword" in the chapter title is the reviewer's *category-assembly method*, not a paper about encrypted
keyword search. The closest cryptographic work in-corpus is private **inference** (A40033 HE+MPC transformer,
A39502, A42229 CKKS, A42232 ZK inference) and secure **computation** (A38773, A39210, A40132, A40852) — **not**
private **search**. Consequently, the classical retrieval-security threads (access-pattern leakage, query
confidentiality against an encrypted-index server, ranking integrity over encrypted data) are represented here only
by *LLM/RAG analogues*, and several threads below are **thin or emerging by corpus construction, not because the
problem is solved.** This absence is itself a finding: an enterprise RAG launch cannot cite this corpus as evidence
that encrypted-search access-pattern leakage is handled — it is not studied.

### Mapping legend (used inline as tags on load-bearing claims)

The task's five-way mapping, aligned to the house `worldview.md` loop *models propose → environments verify →
gates decide → traces prove*:

| Tag | Meaning in the retrieval setting |
|-----|----------------------------------|
| **[Cap]** Capability | What the retrieval/model layer *can* surface, infer, or reconstruct — including undesired capability (invert a prompt, promote an item, recognize-but-still-act). "Capability is not permission." |
| **[Perm]** Permission | What the layer is *authorized* to retrieve / surface / act on — gating at the retrieval and inter-agent boundary, least-privilege on context, write-access to the index. |
| **[Verif]** Verification | Pre-action checking — reasoning judge, corroboration, shadow-sim, representation-level deletion test, executed-attack red-team. |
| **[Evid]** Evidence | Provenance, structured logged verdicts, per-fact source attribution, the logged privacy dial — the auditable trace. |
| **[Resid]** Residual-risk | What survives after the defense: the adaptive/compositional gap, the new single point of trust, what "requires production validation." |

---

## 1. Executive synthesis (what the two buckets say together)

Read jointly, the retrieval-relevant papers converge on one architecture and one recurring failure.

**The convergent architecture (well-established as a *direction*, not as a *guarantee*).** Independent teams arrive
at the same shape: *treat retrieved content, interaction history, and inter-agent messages as attacker-writable
input* **[Perm]**, *put a reasoning-based gate anchored to a trusted source between retrieval and use* **[Verif]**,
*emit structured verdicts as telemetry* **[Evid]**, and *abstain / route-to-human on inconclusive cases* **[Perm]**.
This is A40462 (RAG2RAG) and A40725 (ShieldRAG) on the RAG boundary, A40231 (MPAS) on the inter-agent boundary,
A40189 (TAPA) as the only full propose→verify→gate→prove loop, and A41436 (DIG) contributing per-fact provenance.
The upstream synthesis calls reasoning-based gating outperforming single-purpose filters its strongest *convergent*
retrieval finding (A40462, A40725; reinforced by A37023, A38606) — convergence across independent teams, **not**
replicated effect sizes.

**The recurring failure (the dominant residual risk).** Two field-wide gaps, each stated on essentially every
defense card:

1. **Defenses are almost never evaluated against an adaptive, defense-aware adversary** — so every retrieval-defense
   number below is an **upper bound on non-adaptive protection [Resid]**. The one demonstrated adaptive attack in the
   whole *Multi-keyword-match* bucket (A40297, a machine-text detector repurposed offensively) is offensive, not a
   defense-breaking retrieval attack.
2. **The verifier / judge / trusted-source becomes the new single point of trust and is left unhardened [Resid]** —
   A40462's "value-based" corpus, A40725's safety scorer, A40231's selective aggregator, A40189's trusted RAG
   provenance store. Compromise of that one component is unmodeled.

**The privacy corollary the second bucket adds.** *Privacy-Protection* supplies the missing confidentiality half:
the query, the retrieved context, the embeddings, and even the interaction *sequence* are identity-/membership-
bearing secrets. Prompts invert from outputs alone (A40004) **[Cap]**; soft prompts leak membership with output
access suppressed (A40839) **[Cap]**; "protected" embeddings still invert to impersonating identities (A42453)
**[Cap]**; and the decision/policy *sequence* leaks per-user outcomes even when data at rest is protected (A39710)
**[Cap]**. The transferable control set: keep private content local and send only anonymized/abstracted/surrogate
data to external models (A40534, A40911, A40041) **[Perm]**, and put an independent privacy/human-approval gate in
the *action* path, because off-the-shelf agents recognize sensitive actions poorly (A40874, RA <60% even with
hints, author-reported) **[Perm]** — the clearest "capability is not permission" datapoint for retrieval-driven
agents.

---

## 2. Thread — Search & matching (retrieval as an attack surface)

**Well-established.** That retrieval/RAG pipelines must treat retrieved content as *attacker-writable input* is the
most operationally recurrent threat in the bucket (reviewer synthesis, upstream). Reasoning-based gating — a
separate judge that *reasons* about what may be surfaced, anchored to a trusted value source — reduced attack
success against the tested poisoning suites while preserving utility in two independent frameworks: A40462 (RAG2RAG)
reports BPI ASR 0.94→0.00 and WPI 0.97→0.00 with accuracy gains across 2 languages / 6 domains / 7 attacks / 7
baselines with released code (author claim, under evaluated conditions); A40725 (ShieldRAG) bakes a safety score
into the retriever's shared encoder across 7 datasets / 5 LLMs / 2 attacks (quantitative results **truncated in
extracted text**). **[Cap→Verif]**: the model's *capability* to retrieve is decoupled from *authority* to surface by
a verification gate.

**Emerging.** DRIFTBENCH (A37023) reframes "matching" as a robustness problem: GenAI can cheaply mass-produce
*claim diversity* plus adversarially contaminated evidence against a retrieval-augmented verifier — a 16k-instance,
human-validated-at-98.6% (κ=0.872 for real variants) benchmark, but generator-coupled (GPT-4o / FLUX.1 + live web
retrieval), single-team, not independently replicated.

**Contested / mislabeled.** "Search & matching" is largely a **token collision** in this bucket — A40370 is a RAG
*quality* method with no adversary/threat model; classical encrypted keyword search is absent (Warning 2). Do not
generalize the RAG-security results to searchable-encryption matching; they are different problems.

**Where defenses fail (adaptive / compositional / real-world).**
- Both gating defenses evaluate **fixed, non-adaptive** attack suites. Reviewer-anticipated next moves: *poison the
  trusted value source* or *prompt-inject the Judge* (A40462); *evade the safety scorer* (A40725). **[Resid]**
- A40725 **scopes to toxic content only** and explicitly leaves *manipulative-but-benign* (non-toxic, instruction-
  level) injection unaddressed — the exact compositional case where retrieved text is clean-looking but steers the
  agent. **[Resid]**
- A40725's defense **creates a new artifact** — a reverse-tuned "unlocked" toxic generator — a de-alignment liability
  of the defense itself. **[Resid]**

**Implication (design / launch gate).**
- **Design:** place a reasoning gate with a trusted-source anchor at the retrieval boundary; run it *co-triggered /
  in parallel* to bound latency (A40462) or fold it into the retriever's encoder to avoid a second hop (A40725).
  Emit the verdict as structured telemetry **[Evid]**.
- **Launch gate:** do **not** ship on non-adaptive ASR alone. Re-test with a defense-aware attacker that (a)
  prompt-injects the judge, (b) poisons the trusted corpus, and (c) uses **non-toxic** instruction injection. Treat
  the judge/trusted-source as a hardening target, not a root of trust. **[Resid]**

---

## 3. Thread — Secure / privacy-preserving retrieval

**Well-established (as a pattern, not a measured guarantee).** The recurring, most deployment-realistic model for
agentic RAG/tool-use is **provider-as-adversary / untrusted third-party model** — the closest in-corpus
confused-deputy framing (reviewer synthesis). The convergent control is *keep the raw private artifact local; send
only anonymized/abstracted/surrogate data to the external model*: A40534 (ARoG) anonymizes/abstracts KG entities so
raw data never reaches a third-party LLM; A40911 (SOER) redact-then-recovers so the cloud MLLM never sees the raw
image; A40041 (PRISM) routes high-sensitivity prompts to a trusted local edge (sketch-then-refine). **[Perm]**: the
external model is placed *inside* the trust boundary and denied the raw asset.

**Emerging.** DP-mediated retrieval inputs: A40838 (DP-ICL) generates DP synthetic in-context demonstrations;
A40720 (PrivSV) privatizes a shared steering vector via structure-aware reduction + Metric-LDP. Cryptographic
retrieval-adjacent compute (HE/MPC/ZK private *inference*, §0) exists but at MNIST/2000-sample/4-qubit toy scale
(A40852, A42229, A42232) — deployability at RAG scale is asserted, not shown.

**Contested.** Most of these controls establish privacy **"by construction" with no leakage metric** — A40534,
A40911, A40041, A42372 report *no* executed membership-inference/reconstruction attack; A40720/A40838 state formal
bounds but run no empirical attack. The upstream synthesis flags "formal-guarantee-without-executed-attack" as
pervasive and names A42453 (FEM) as the cautionary counterexample: eight *named* "privacy-preserving" embedding
schemes still invert to impersonating identities under a black-box embedding-only adversary (ASR reduced, not
eliminated — author-reported). **[Resid]**: "privacy-preserving retrieval" in product copy is contested evidence
until an attack is run.

**Where defenses fail (adaptive / compositional / real-world).**
- "By-construction" abstraction (A40534/A40911) has **no quantified residual** — an adversary reconstructing the
  private entity from the abstraction is untested. **[Resid]**
- Any *transmitted* retrieval artifact is reconstructable: gradients (A37743, A39333 — heuristic noise analytically
  invertible), smashed split-inference reps (A39212), soft prompts (A40839), embeddings (A42453). A retrieval system
  that ships embeddings/representations over an untrusted channel inherits these. **[Cap]/[Resid]**
- Formal DP/crypto is only as strong as its accounting and trust boundary — voided by a colluding majority (A38773,
  A40852) or un-accounted shared objects; two-non-colluding-party anchors (A40852, A40889) collapse under collusion.
  **[Resid]**

**Implication (design / launch gate).**
- **Design:** model the external retrieval/LLM provider as in-boundary; anonymize/abstract/surrogate at the edge;
  prefer *accounted* DP + secure aggregation over heuristic noise; treat every transmitted artifact (embedding,
  gradient, prototype, steering vector, smashed rep) as a reconstructable secret with egress control. **[Perm]**
- **Launch gate:** require an **executed-attack red-team** (reconstruction / MIA / linkage) before asserting any
  "privacy-preserving retrieval" claim; A42453 is the standing counterexample. Log the privacy dial (ε/γ/FSInfo)
  as configuration-of-record **[Evid]**. Validate crypto retrieval at production scale before assurance claims —
  toy-scale evidence does not transfer. **[Resid]**

---

## 4. Thread — Access-pattern leakage

**Corpus-thin — state honestly.** No paper studies retrieval access-pattern leakage in the classical
ORAM/searchable-encryption sense (Warning 2). The transferable evidence is analogues from *Privacy-Protection*, and
they point one direction: **the interaction/query sequence is itself a channel, independent of the data at rest.**

**Well-established (the load-bearing analogue).** A39710 shows a bandit's **arm-selection *sequence* leaks per-user
outcomes even when stored data is protected** (ε-DP + Nash-regret; synthetic evaluation, author-reported). Read
across to retrieval: *which documents an agent retrieves, in what order, in response to which user* is a leakage
surface that data-at-rest encryption does not close. **[Cap]**: the access pattern is an inferential capability
handed to the observer.

**Emerging.** A40862 elevates a **single-message Bayesian data-reconstruction attack to a first-class LDP design
axis** for frequency/telemetry — i.e. even one report/query is treated as reconstructable, the right posture for a
retrieval-telemetry pipeline. A40839 (PIPRA) proves an **output-free** membership-inference (avg AUC 87.58% vs
77.05% for output-dependent baselines; 90.37% acc on Caltech101, author-reported): suppressing the *response* does
not suppress the leak when the query representation is observable. **[Cap]**

**Contested / not studied.** Whether encrypted-index access-pattern leakage is mitigable is **not evaluated in this
corpus.** Any claim otherwise would be unsupported. **[Resid]**

**Where defenses fail (adaptive / compositional / real-world).**
- Output suppression / rate-limiting is the naive access-pattern defense and it **fails**: A40839 leaks with outputs
  suppressed; A39671 (On Stealing GNNs) extracts an encoder in ~100 queries vs ~5,000 for prior SOTA (author-
  reported) and **defeats a rate-limit-plus-prediction-only defense in place** — volume-based throttling misses
  embedding-guided, centroid-proximal, information-dense *small* query sets. **[Resid]**

**Implication (design / launch gate).**
- **Design:** treat the *interaction trace* (query sequence, retrieval order, per-user access pattern) as a
  first-class protected asset, not only the datastore (A39710). Detect *information-dense small query sets*, not
  just request volume (A39671). **[Perm]/[Evid]**
- **Launch gate:** because this corpus does **not** validate encrypted-search access-pattern hiding, an enterprise
  RAG launch must **not** claim access-pattern confidentiality on the strength of these papers; scope any such claim
  to "not evaluated" and require dedicated validation. **[Resid]**

---

## 5. Thread — Ranking integrity

**Well-established.** Stealthy, adaptive manipulation of *what surfaces / what ranks* is demonstrated and evades
single-granularity detectors. A38606 (CREAT) poisons individual interaction histories to **promote a target item**
under a stealth constraint, adaptively (RL), while evading distribution-shift detectors — the canonical
ranking/promotion-integrity attack. A40462's attack taxonomy includes *blocker/jamming* and *adversarial-passage
injection* (surface-vs-suppress control), and *targeted control* and *refusal DoS*. A41436 (DIG) assumes
**trafficker-controlled source ads** — the adversary owns the ranked sources. **[Cap]**: an outside writer gains the
capability to move rank; **[Perm]**: the fix is authorization over who can influence rank + corroboration before
trusting it.

**Emerging.** A37023 (DRIFTBENCH) frames ranking-adjacent integrity as *adversarial evidence contamination* biasing
a retrieval-augmented verifier's judgment; A40231 (MPAS) generalizes "what surfaces" to inter-agent misinformation
injected at **topologically critical nodes**, with a node-redundancy + per-agent message-vetting defense reporting
*relative* backdoor-threat reduction of 7.4–26.3% (better in 94.4% of tests, author claim) — note it reports
**relative** reduction, **not** post-defense absolute ASR. **[Verif]/[Evid]**

**Contested.** Redundancy is a double-edged control: A40824 (ResMAS) finds more agents/links → more *resilience*
(to **random**, non-strategic failure), while A40231 (and A40824's own reviewer note) find more nodes/links → *more*
injection points and faster harmful-info spread. Resilience-to-random-failure and security-against-adversary can
point in opposite directions (reviewer synthesis). **[Resid]**

**Where defenses fail (adaptive / compositional / real-world).**
- CREAT's very premise is that **aggregate / single-granularity anomaly detectors are bypassable** by finer-grained,
  stealth-constrained poisoning — the compositional case. **[Resid]**
- A40231's message-vetting is evaluated non-adaptively; the anticipated bypass is *craft messages that pass the
  selective aggregator's reliability check* (reviewer synthesis). The selective aggregator is a new trust root.
  **[Resid]**

**Implication (design / launch gate).**
- **Design:** treat interaction history and inter-agent messages as attacker-influenceable ranking inputs; add
  cross-source corroboration and **finer-than-aggregate** anomaly monitoring (A37023, A38606); treat communication
  topology as a security parameter but account for the redundancy↔attack-surface tension (A40231, A40824). **[Verif]**
- **Launch gate:** require **absolute** post-defense ASR, not relative reduction, before certifying ranking
  integrity; re-test with a *stealth-constrained adaptive* promoter (CREAT-style) and a *reliability-check-aware*
  message crafter (MPAS-style). **[Resid]**

---

## 6. Thread — Query confidentiality

**Well-established (as an *unmet* property).** For LLM-RAG the query is the prompt, and prompt/query confidentiality
is demonstrated to be leaky *and* currently undefended. A40004 (Inv2A) recovers hidden user/system prompts **from
model text outputs alone**, and its own defense evaluation shows output-perturbation defenses are **largely
bypassed** — the paper states it "fails to find a really valid schema" to overcome the inversion (author-stated open
problem; single 7B model, white-box; surface-overlap metrics TokenF1/BLEU that *under*-measure semantic-but-
non-verbatim recovery). A40839 (PIPRA) shows the query representation (soft prompt) leaks *membership* even with
outputs suppressed. **[Cap]**: the system exposes an unintended inference capability over the confidential query.

**Emerging.** The defensive direction is *keep the sensitive query local / abstract it before it leaves the trust
boundary* — A40041 (PRISM) local routing, A40534 (ARoG) entity abstraction, A40911 (SOER) surrogate editing,
A40720 (PrivSV) DP on shared vectors. All establish privacy **by construction with no leakage metric** (§3
contested). **[Perm]/[Resid]**

**Contested.** Whether query confidentiality is *achievable* against an output-observing adversary is an open
problem the corpus does not resolve: A40004 reports no working defense; the by-construction routers report no attack.
**[Resid]**

**Where defenses fail (adaptive / compositional / real-world).**
- Output perturbation — the intuitive query-privacy defense — is **bypassed** (A40004). **[Resid]**
- Output suppression does not stop *representation-space* leakage (A40839). **[Resid]**
- "Latent inference" over the query/context (A40593 prefix-conditioned membership/pretraining-data detection;
  A41230 (FLAME) domain-guided sensitive-attribute inference) is a **dual-use capability**: the same machinery that
  audits also attacks. **[Cap]**

**Implication (design / launch gate).**
- **Design:** treat prompts, system prompts, and query embeddings as **confidential assets with access control +
  logging**, not innocuous features (A40004, A40839); gate "latent inference" over a query as a *sensitive action*
  (least-privilege on context, output-granularity limits, audit of inferred attributes) (A40593, A41230). **[Perm]/[Evid]**
- **Launch gate:** do **not** market query confidentiality against an output-observing adversary — the in-corpus
  evidence is that it is **unmet** (A40004). If a confidentiality claim ships, scope it to "reduced against the
  tested, non-adaptive attacks; not evaluated against prompt-inversion-from-outputs." **[Resid]**

---

## 7. Thread — Index poisoning

**Well-established.** Retrieval corpora, agent memory, and inter-agent knowledge are **attacker-writable**, and
defenses reduce ASR against the *tested* poison sets while leaving adaptive/compositional cases open. A40462
(RAG2RAG) enumerates seven attack types — including targeted control, refusal DoS, blocker/jamming, adversarial-
passage injection, and grammar-trigger backdoors — and assumes write/inject access to open knowledge bases;
A40725 (ShieldRAG) targets PoisonedRAG-/BadRAG-style corpus poisoning; A37023 (DRIFTBENCH) models adversarial
evidence contamination; A38606 (CREAT) poisons interaction history/memory; A40231 (MPAS) injects misinformation at
critical inter-agent nodes. **[Perm]**: the root cause is unauthorized *write* to what the retriever/agents trust;
**[Verif]**: the mitigation is a gate over ingested/retrieved content.

**Emerging.** Adversarial data synthesis to cover unknown poison distributions where labels are scarce (A40725:
reverse-tuned toxic generator + generator-evaluator co-training). Per-fact provenance to source+extractor (A41436,
DIG) as the trust primitive that lets a poisoned fact be traced and excluded. **[Evid]**

**Contested / gap.** The standout runtime-enforcement loop, A40189 (TAPA), **leaves the RAG/knowledge store and
synthesized code trusted** — it verifies the *agent's action* in shadow-simulation but does not harden the *index*
it reads from (reviewer synthesis). So even the reference propose→verify→gate→prove architecture does not, by
itself, close index poisoning. **[Resid]**

**Where defenses fail (adaptive / compositional / real-world).**
- All poison defenses are evaluated **non-adaptively**; anticipated bypasses: poison the *trusted value source*,
  prompt-inject the *Judge* (A40462); **non-toxic instruction-level injection** is explicitly unaddressed by A40725.
  **[Resid]**
- A38606 shows **single-granularity distribution-shift detectors are evadable** by stealth-constrained poisoning.
  **[Resid]**
- There is **no evaluated defense against malicious knowledge-editing of open weights** (A40269) — a supply-chain
  "poison the model rather than the index" path, where one edit can also shift *global* fairness. Merge-prevention
  (A40433) *prevents* capability theft but **does not attribute**. **[Resid]**

**Implication (design / launch gate).**
- **Design:** treat retrieved evidence, interaction history, and inter-agent messages as untrusted; add
  near-duplicate / AI-generated-evidence detection, cross-source corroboration, finer-than-aggregate anomaly
  monitoring, and **per-fact provenance** so a poisoned fact is traceable and revocable (A37023, A38606, A40462,
  A40725, A41436). Harden the *index*, not only the *action* (the gap A40189 leaves). **[Perm]/[Verif]/[Evid]**
- **Launch gate:** require adaptive re-test (judge-injection, trusted-source poisoning, **non-toxic** instruction
  injection) and **model provenance/attestation** for any third-party open weights before adoption — signed weights
  / hash pinning / known-good baselines + post-hoc factual and bias probing, because no defense against malicious
  editing is evaluated and bias auditing must cover *unrelated* categories (A40269, A40433). **[Resid]**

---

## 8. Thread — Retrieval authorization

**Corpus-thin — state honestly.** Retrieval authorization in the strict sense (row-/document-level access control,
"who may retrieve which record" enforced in the RAG path) is **not studied** in either bucket. The transferable
primitives are least-privilege on retrieved context and treating sensitive *inference/action* as gated. This is the
sharpest **[Cap] vs [Perm]** thread: the papers repeatedly show *capability without permission enforcement*.

**Well-established (the negative results that motivate authorization).**
- A40188 (personalized web agent) **concentrates LLM-inferred user data — including demographics — with no access
  control and no minimization**; the paper is an attack-surface catalog, deferring privacy/minimization to future
  work. **[Perm gap]**
- A40874 (SAPA-Bench) quantifies that off-the-shelf MLLM smartphone agents **recognize sensitive actions at RA below
  60% even with explicit hints** (best Gemini 2.0-flash ~67%, author-reported; privacy labels partly GPT-4o-
  generated). The recommended control is an **independent recognition→localization→severity→human-confirmation gate
  before high-sensitivity actions** — the direct "capability is not permission" datapoint for retrieval-driven
  agents. **[Perm]/[Verif]**

**Emerging.** A37135 (PriAgent) is the only genuinely agentic (multi-agent, RAG, tool-use) system in-corpus — an
LLM privacy-compliance auditor over decompiled code + policy — and it contributes an **evidence-linked verdict**
pattern (flow / code / policy snippet + reasoning + confidence) that maps directly onto authorization audit records.
**[Evid]** But it runs LLM agents over **attacker-influenced** decompiled input **with no injection control** (a
reviewer-flagged *unimplemented* gate). A42372 offers confidential-evaluation authorization via output-abstraction +
sandboxing + human gating (self-acknowledged-subjective LLM judge). Gating "latent inference" as a sensitive action
(A40593, A41230) is an authorization primitive over what may be *inferred*, not just *read*.

**Contested / not studied.** Document-level retrieval authorization, delegated retrieval authority, and attenuated
delegation are **absent** — the corpus provides no evidence on them. **[Resid]**

**Where defenses fail (adaptive / compositional / real-world).**
- Agents cannot be relied on to self-authorize: A40874 shows sub-60% sensitive-action recognition — an **internal**
  gate is insufficient, an **external** gate is required (consistent with the house "alignment is shallow"
  worldview). **[Resid]**
- A37135's auditor over untrusted decompiled content is a **prompt-injection surface** with no implemented control —
  authorization logic that itself ingests untrusted retrieved text is corruptible. **[Resid]**

**Implication (design / launch gate).**
- **Design:** put an **independent** privacy/human-approval gate in the *action* path (recognition→localization→
  severity→human-confirmation) before executing high-sensitivity retrieval-driven actions — credentials, financial,
  precise location, permission grants (A40874); apply least-privilege + minimization on retrieved/inferred context
  (A40188); gate latent inference as a sensitive action (A40593, A41230); harden any authorization component that
  ingests untrusted content against injection (A37135). Map cleanly onto a PolicyGuard/ActionGuard-style gate.
  **[Perm]/[Verif]**
- **Launch gate:** because document-level retrieval authorization is **not** validated in this corpus, do not claim
  it on this evidence; require a dedicated design + test. Do not ship an agent that self-authorizes sensitive
  retrieval actions on internal recognition alone (A40874). **[Resid]**

---

## 9. Thread — Enterprise RAG implications (synthesis of 2–8)

Pulling the threads together for an enterprise RAG / guardian-agent deployment. Each row states the control, the
strongest supporting evidence, the mapping, and the residual risk that gates launch.

| Control | Evidence (author-reported, under evaluated threat model) | Mapping | Residual risk → launch gate |
|---|---|---|---|
| Reasoning gate at the retrieval boundary, trusted-source anchor, run co-triggered | A40462 (BPI 0.94→0.00, WPI 0.97→0.00; 2 lang/6 dom/7 atk/7 base; code), A40725 (results truncated) | [Cap→Verif] | Judge/trusted-source is a new SPOF; non-toxic injection unaddressed → **adaptive re-test incl. judge-injection + non-toxic injection** |
| Treat retrieved content, memory, inter-agent messages as attacker-writable; per-fact provenance | A37023, A38606, A40462, A40725, A40231, A41436 | [Perm]/[Evid] | Single-granularity detectors evadable (A38606); index left trusted even by A40189 → **harden the index, not only the action** |
| Provider-as-adversary: anonymize/abstract/surrogate before external model; keep private artifact local | A40534, A40911, A40041, A40720 | [Perm] | "By construction," **no leakage metric** → **executed-attack red-team before any privacy claim** |
| Treat query/prompt + embeddings as confidential assets with access control + logging | A40004 (prompt inversion from outputs, defenses bypassed), A40839 (output-free MIA) | [Cap]/[Perm]/[Evid] | Query confidentiality is **unmet** vs output-observing adversary → **do not market it; scope to tested attacks** |
| Interaction trace (query sequence / access pattern) is a leakage channel | A39710 (sequence leaks), A40862 (single-message DRA), A39671 (encoder theft ~100 vs ~5,000 queries, defeats rate-limit) | [Cap]/[Perm] | Output suppression + rate-limit **fail**; encrypted-search access-pattern hiding **not studied** → **do not claim access-pattern confidentiality** |
| Independent privacy/human-approval gate in the action path | A40874 (agents recognize sensitive actions RA <60%; best ~67%) | [Perm]/[Verif] | Internal recognition insufficient → **external gate mandatory; no self-authorization of sensitive actions** |
| Least-privilege + minimization on retrieved/inferred context; gate latent inference | A40188 (no access control on inferred data), A40593, A41230 (dual-use inference) | [Cap] vs [Perm] | Doc-level retrieval authorization **not validated in corpus** → **design + test separately** |
| Provenance/attestation for third-party open weights before adoption | A40269 (no defense vs malicious editing; single edit shifts global fairness), A40433 (prevents merge theft, no attribution) | [Verif]/[Evid] | Supply-chain "poison the model not the index" → **signed weights / hash pin / known-good baseline + factual & unrelated-category bias probe** |
| Abstain / route-to-human as safe default; structured verdicts as telemetry | A40189 (Alert primitive, provenance chain), A40462 (labeled verdicts), A42311 (calibrated-uncertainty abstention — proposal only, zero results) | [Perm]/[Evid] | A42311 is framing only → **do not cite as validated; treat abstention plumbing as required, not proven** |

**The single most reusable architecture** is A40189 (TAPA): *propose → shadow-simulation verify → degradation-
threshold gate → backup-meta-policy rollback → human-approval Alert → provenance chain*. It is the only in-corpus
instantiation of the full propose→verify→gate→prove loop **[Cap→Verif→Perm→Evid]**. For enterprise RAG the required
*addition* is integrity/authenticity on the RAG index and synthesized artifacts that TAPA leaves trusted (§7) — plus
the confidentiality half (§3, §6) the *Multi-keyword-match* bucket does not supply and *Privacy-Protection* does.

---

## 10. Cross-thread residual-risk register (what "requires production validation")

Every item below is a **[Resid]** the corpus itself names — carry each into launch review; none is closed by the
evidence here.

1. **Non-adaptive evaluation is universal.** Every retrieval-defense number (A40462, A40725, A40231, A38606, A37023,
   and the privacy defenses A40534/A40911/A40041/A40720/A40838) is an **upper bound under non-adaptive conditions.**
   Re-test each against a defense-aware adversary before shipping.
2. **The verifier/judge/trusted-source is the new single point of trust** and is left unhardened (A40462, A40725,
   A40231, A40189). Harden or cross-check it; never treat its verdict as a root of trust.
3. **Query/prompt confidentiality is unmet** against an output-observing adversary; output perturbation is bypassed
   (A40004); output suppression does not stop representation-space leakage (A40839).
4. **Encrypted-search access-pattern hiding is not studied** in this corpus (Warning 2); the only evidence is that
   the interaction *sequence* leaks (A39710) and volume-based throttling fails (A39671). Do not claim it.
5. **Index poisoning has no adaptive-robust defense here**, and the model-supply-chain variant (malicious
   knowledge-editing, A40269) has **no evaluated defense at all**; merge-prevention (A40433) does not attribute.
6. **"Privacy-preserving retrieval" is largely by-construction with no leakage metric** (A40534, A40911, A40041,
   A42372); A42453 is the standing proof that "privacy-preserving" labels invert under test.
7. **Retrieval authorization at document/delegation granularity is absent**; agents self-recognize sensitive actions
   at RA <60% (A40874) — external enforcement is mandatory.
8. **Metrics are instrument-dependent.** LLM-as-judge is repeatedly both the measurement instrument and an
   unhardened attack target (A40498, A40913 in-bucket; A40874/A40773/A40911 use model-generated ground truth).
   Judge-dependent scores are **not release-grade on their own**.
9. **Several key result tables are truncated in extracted text** (A40725 quantitative results; A40874/A42453
   limitations) — those specific numbers are author-stated, **not** reviewer-verified.
10. **Convergence ≠ replication.** All "convergent" findings above are cross-team agreement across independent,
    non-overlapping benchmarks — there is **no** independent replication of any effect size in this corpus.

---

## 11. Papers referenced in this chapter (id → role, as recorded upstream)

*Multi-keyword-match bucket:* A37023 (DRIFTBENCH — RAG-verifier evidence contamination benchmark), A38606 (CREAT —
stealthy adaptive history/ranking poisoning), A40004 (Inv2A — prompt inversion from outputs), A40188 (personalized
web agent — unprotected inferred-data catalog), A40189 (TAPA — full propose/verify/gate/prove loop, index left
trusted), A40231 (MPAS — inter-agent backdoor + topology-as-security), A40269 (Editing Attack — malicious
knowledge-editing, no evaluated defense), A40297 (HLPD — the one demonstrated adaptive attack, offensive), A40370
(RAG quality, no threat model — peripheral), A40433 (MergeBarrier — merge-theft prevention, no attribution), A40462
(RAG2RAG — reasoning Detective+Judge RAG gate, released code), A40593 (DSC-Prefix — prefix-conditioned MIA /
pretraining-data detection, dual-use), A40725 (ShieldRAG — safety-aware retriever, toxic-only, results truncated),
A40824 (ResMAS — resilience vs **random** failure, redundancy tension), A40913 (EmoAgent — "capability ≠ permission"
via reasoning-trace attack), A41230 (FLAME — latent sensitive-attribute inference, dual-use), A41345 (detector
survey — no new results), A41436 (DIG — per-fact provenance to source+extractor), A42311 (Hallucinations at the
Firewall — abstention proposal, zero results).

*Privacy-Protection bucket:* A37135 (PriAgent — only agentic RAG system; evidence-linked verdicts; unimplemented
injection gate), A37743 (GGSS-R — gradient inversion of noised gradients), A39212 (split-inference reconstruction
from smashed reps), A39333 (Venom — analytic noise-prior-free gradient reconstruction), A39373 (IDI — behavioral
unlearning metrics gameable), A39671 (On Stealing GNNs — encoder theft defeating rate-limit), A39710 (bandit
arm-selection **sequence** leaks per-user outcomes), A40041 (PRISM — sensitivity-aware local prompt routing), A40534
(ARoG — entity abstraction before third-party LLM), A40720 (PrivSV — DP steering vectors), A40838 (DP-ICL — DP
in-context demonstrations), A40839 (PIPRA — output-free membership inference from prompt vectors), A40862 (RNS LDP —
single-message DRA as design axis), A40874 (SAPA-Bench — agent sensitive-action recognition RA <60%), A40911 (SOER —
redact-then-recover for cloud MLLM), A41120 (PrivUB — unlearning-attack benchmark; deletion reactivatable), A42372
(confidential multi-agent evaluation via output-abstraction), A42453 (FEM — "protected" embeddings still invert to
impersonating identities). Crypto/secure-compute context only (private *inference*, not private *search*): A40033,
A39502, A42229, A42232, A38773, A39210, A40132, A40852, A40889.

> **Distinguishing direct findings from reviewer synthesis:** author-reported values (e.g. A40462 BPI 0.94→0.00,
> A40231 7.4–26.3% relative reduction, A40874 RA <60% / ~67%, A40839 AUC 87.58% vs 77.05%, A39671 ~100 vs ~5,000
> queries, A39333 LPIPS 0.340 vs 0.632 / ASR 45% vs 2% at ε=10 δ=10⁻⁵, A37023 16k / 98.6% / κ=0.872) are the
> papers' own claims under their own evaluated threat models. All statements labeled "reviewer synthesis," every
> anticipated-bypass, and the redundancy↔attack-surface tension are the upstream synthesists' cross-paper
> inferences, not paper results. Where a value is "truncated in extracted text" (A40725 quantitative results;
> A40874/A42453 limitations) it is author-stated and not independently verifiable from the cards.
