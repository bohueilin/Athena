# Executive Summary — AAAI-26 Security Corpus for Origin & Passport

> **Purpose.** A decision-oriented read of 432 AAAI-26 security papers for the two products this knowledge
> base serves: **Origin** (licensed *physical* autonomy) and **Passport** (licensed *digital-agent*
> autonomy). Organizing lens is the governing principle — **"Models propose. Environments verify. Gates
> decide. Traces prove."** — and the question is not "what does the field study" but "what should we build,
> what may we claim, and what must we not claim yet."
>
> **Calibration contract.** Every magnitude below is **author-reported under that paper's own evaluated
> threat model** and **not independently verified**; many source tables were truncated in extraction. No
> absolutes ("secure", "proven safe", "unbreakable"). Cross-paper statements are reviewer synthesis, not
> replicated effect sizes — these are 432 distinct studies with almost no shared benchmark. Paper ids are the
> internal `Axxxxx` card ids; engineering controls are named by their `patterns/` filename.

---

## 1. What was analyzed

432 AAAI-26 papers across eight corpus folders, distilled into eight per-folder authoritative syntheses, a
normalized ontology (assets / adversaries / surfaces / attacks / defenses / evidence-mechanisms), a
deterministic relevance triage, 8 cross-cutting notes, and **28 engineering-control pattern files** (the
named controls in §8). Folder sizes: Adversarial-ML-Attacks 152, Privacy-Protection 73, Multi-keyword-match
69, AILLM-Safety 63, Network-Cyber-Security 31, Model-IP-Protection 22, Deepfake-Forgery-Detection 13,
Defense-Mitigation 9.

Two structural facts frame everything downstream:

- **Most folders are keyword-assembled, not security-curated.** "Adversarial", "robust", "privacy",
  "alignment" collide lexically with benign ML methods. Every synthesis independently separates a genuine
  security core from a large mislabeled tail (e.g. AILLM-Safety: ~44 of 63 are real LLM/agent-security work,
  the rest vision/representation papers mis-binned via the "alignment" collision; Multi-keyword and
  Network-Cyber are "not primarily agent-runtime" by their own reckoning).
- **The corpus is broad ML-security; the agent-execution slice is a minority.** This is the single most
  important calibration for Origin/Passport (§11).

## 2. Corpus reconciliation — were all 432 found?

Yes. Per `corpus-audit.md`: **432 PDFs discovered against 432 expected**, every category delta **+0**
(AILLM-Safety 63/63, Adversarial-ML-Attacks 152/152, Deepfake 13/13, Defense-Mitigation 9/9, Model-IP 22/22,
Multi-keyword 69/69, Network-Cyber 31/31, Privacy 73/73). **0 duplicate content hashes, 0 unreadable /
low-extraction files.** So: **432 found, 0 missing, 0 duplicates, 0 unreadable.** Ontology provenance
concurs: 432/432 tag lines parsed, 0 malformed.

## 3. What could not be (fully) processed

One gap, and it is at the *card* layer, not the *paper* layer: **415 of 432 research cards were generated;
17 are missing** — A38722, A38730, A38761, A38785, A38853, A38949, A39085, A39276, A39290, A39301, A39318,
A39336, A39382, A39428, A39438, A39449, A39480. All 17 fall in the Adversarial-ML-Attacks folder, and all 17
were nonetheless folded into that synthesis directly from PDF and appear in its source map (e.g. A38416/A38127
neighbors, A39276 MIA-auditing, A39290 "pill" FL poison, A39480 dormant CLIP backdoor). So the loss is a
missing structured summary, not lost evidence — impact on conclusions is low. Second-order limits that bound
confidence everywhere: **only 7/432 arXiv ids resolved** (identifier hygiene is weak; several folders warn
manifest arXiv ids are mis-extracted — trust the `Axxxxx` ids), and **many result tables were truncated in
extraction** (magnitudes are author-stated, not transcribed in full).

## 4. Major research themes

1. **Shallow safety alignment** — safety concentrated in early response positions / a low-rank, redundant
   ("hydra") refusal sub-circuit / surface lexical form, and this shallowness is the shared root cause of the
   strongest jailbreaks (A40248 mechanistic keystone; A40551, A41119, A41148, A40840, A36996, A40607, A41140).
2. **Untrusted context as an instruction channel** — forged conversation history (A40840, A36996) and
   environment/tool/metadata content (A41090, A41468, A40895, A40224, A40353) are trusted as authentic.
3. **Capability ≠ permission ≠ safety** — recognizing risk is not safe behavior; tool identity is not
   authorization (A40895 confused-deputy, A41090, A40874, A42249, A42239, A40913).
4. **Supply-chain persistence** — fine-tuning/retraining does not remove implanted behavior; provenance is
   the control (A40295 clean-tuning *reinforces* the backdoor, A39809, A40855, A39480).
5. **Model artifacts are secrets** — gradients, embeddings, prompts, steering vectors, smashed reps invert or
   leak membership, sometimes with no output access (A42453, A39333, A37743, A40839, A38853).
6. **Deletion ≠ erasure** — approximate unlearning leaves adversarially recoverable, often reactivatable
   residue (A41120, A39373, A40343, A40818).
7. **Availability as a security property** — latency/compute inflation on hard-real-time perception (A37082
   >90×) and reasoning LLMs (A40445, A40486, A40833) while outputs stay correct.
8. **Provenance / attribution** — watermarking & fingerprinting as post-hoc evidence, not prevention
   (Model-IP folder; Deepfake folder as evidence signals an agent consumes).
9. **The pervasive meta-theme: non-adaptive evaluation** (§5.1, §9).

## 5. Highest-confidence findings

Ranked by cross-folder convergence; still author-reported, not independently verified.

1. **Non-adaptive evaluation dominates, and defense-aware attackers degrade or defeat defenses.** The
   single most replicated finding, converged on by every major folder. The ontology quantifies the assurance
   gap: `holdout` 296 papers and `adversarial_eval` 270, but **`adaptive_attack_testing` only 28**,
   `tamper_evident_logs` 2, `continuous_monitoring` 5, `independent_audit` 3, `signed_evidence` 1. Treat every
   defense number in the corpus as an **upper bound under non-adaptive conditions**.
2. **Shallow alignment is the mechanistic root of the strongest jailbreaks** (A40248 + 6-paper convergence).
3. **Metadata/tool-descriptions are an injection surface as dangerous as content** — MCPTox (A40895) hijacks
   a legitimate high-privilege tool via a poisoned *description* (peak ASR 72.8% on o1-mini, <3% refusal even
   on Claude-3.7-Sonnet, author-reported); the poisoned artifact never executes — a confused-deputy vector
   that defeats permission models keyed to tool identity.
4. **Whole-pipeline adaptive attacks defeat guard stacks that pass per-component tests** — STACK (A41108,
   0%→71% black-box) and MFA (A41144, 0%→58.5%) independently exploit the same channel (inducing the model to
   emit an attacker-chosen string past the output classifier).
5. **Backdoors and reasoning-DoS preserve accuracy — accuracy-only QA is blind** (A39935 ≤1% drop at ≤0.5%
   poison; A40486 answers correct while reasoning inflates ~17× on MATH-500).
6. **Retraining does not remove implanted behavior; provenance is the control** (A40295, A39809, A40855).
7. **Model-derived artifacts invert/leak; heuristic noise and "by-construction" privacy understate residue**
   (A39333 analytic gradient inversion without knowing the noise; A42453 face reconstruction defeating 8
   named "privacy-preserving" template schemes; A40839 output-free prompt MIA).
8. **Agents lack privacy/safety awareness in the action path** (A40874 SAPA-Bench; A41090 MobileSafetyBench —
   prompt-level safety is necessary-but-insufficient at the action layer).
9. **Availability is first-class and under-defended** (A37082 physical testbed; reasoning-DoS trio).
10. **Shared vision/encoder backbones create systemic monoculture transfer risk** (A41144 avg 59.58% image
    ASR transfer; A42439 CLIP-surrogate patch transfers to 12 commercial/reasoning MLLM stacks).

## 6. Most important disputed / unresolved questions

- **Where safety "lives."** Autoregressive LLMs locate it in *early* tokens / low-rank refusal directions
  (A40248, A40551); diffusion LLMs argue the *opposite* — *middle* tokens (A37106). Architecture-specific;
  reinforces that safety hooks must be architecture-aware, not a contradiction.
- **Scale vs. safety.** A "scaling paradox" where mid-sized models are *most* vulnerable (A40399) vs. the
  largest model resisting best (A40465, Llama-3.1-405B). Observational on different model sets — unresolved.
- **Robustness–utility: fundamental or escapable.** A proven smoothness *dichotomy* (A38416: transfer- and
  query-robustness mutually exclusive) vs. claims it can be jointly improved (A39603). Many defenses simply
  buy safety with clean-accuracy or over-refusal cost that they do not quantify adaptively.
- **Reasoning as defense.** Helps text-answer refusal (A41129 EASE) but is insufficient and self-inconsistent
  at the embodied/action layer (A41090). A scope boundary, not a clean win.
- **The representation-monitor ↔ activation-attack collision.** Defenses (A40887, A41074, A42191) and attacks
  (A40858, A41119, A41148) operate on the *same* residual stream; **no paper tests them head-to-head** — an
  open collision, not a resolved result.
- **Unlearning: reliable removal vs. leaky/abusable.** Precise forgetting claimed (A40272) vs. the unlearning
  event itself leaking membership and being weaponizable (A39725, A39747).
- **Verifier/reward trust.** Process Reward Models score logically invalid steps high via stylistic
  confounders (A40584, an impossible constraint scored 0.973) — casting doubt on best-of-N / LLM-judge gates.
- **DP against inference attacks.** Only a slight ASR decrease against relative-metric MIA (A40846); DP is
  frequently *asserted by budget* without an executed attack.

## 7. Most consequential implications for AI system design

- **Defense-in-depth aligned to the agent cognitive cycle is the transferable reference architecture:**
  input filter → tool-plan validation → just-before-invocation execution gate → immutable post-action audit
  (A41468's four layers), reinforced by A41090 and instantiated end-to-end by exactly one paper, **A40189
  (TAPA)** — the only corpus artifact that closes the full "propose → verify → decide → prove" loop (LLM
  proposes symbolic programs → shadow-simulation verifies before live swap → degradation threshold + backup
  meta-policies decide/rollback → Alert routes to human → provenance chain logs every adaptation). TAPA is the
  closest existing blueprint for both Origin and Passport.
- **Bind actions to verified intent, not tool identity** (A40895); require human approval for
  credential-reading actions regardless of requester.
- **Treat untrusted content as data, not instructions** — history, tool output, RAG corpora, tool metadata,
  camera frames are all attacker-influenceable; fluent/expert surface is not evidence of benignity.
- **Instrument the right signal, not output accuracy** — reasoning-token/latency ceilings, output entropy,
  deep-layer attention concentration, confidence-run events (backdoors and DoS preserve correctness).
- **Provenance/attestation is the primary supply-chain control** (retraining won't clean a backdoor);
  add *post-fine-tuning* red-teaming since dormant backdoors are invisible pre-fine-tuning (A39480).
- **No inference-time refusal defense reaches a safe floor** (residuals: A42191 ~31%, A40248 ~16%, A41468
  >50% miss on its hardest agent class) — refusal must *gate* alongside least-privilege + human approval, not
  replace them.
- **Model artifacts and intermediate state are confidentiality assets with egress control** (embeddings,
  steering vectors, activations, routing metadata).
- **Availability is a defended SLA** — bound worst-case per-message compute, isolate per-sender cost, enforce
  reasoning-token ceilings independent of prompt-controlled instructions.

## 8. Highest-priority engineering controls (named patterns)

From `references/patterns/` (28 controls), prioritized by agent-load-bearing evidence:

1. **`prompt-injection-containment` + `context-and-memory-isolation`** — the shared remedy to the
   #2/#3 themes; normalize inputs to canonical intent *before* gating (A40296, A40465, A41058), attest
   history provenance (A40840, A36996), isolate tool/env/observation content (A41090, A41468).
2. **`policy-permission-gates` + `tool-capability-isolation` + `least-privilege-credentials` +
   `human-approval-consequential-actions`** — the "capability ≠ permission" quartet; the concrete answer to
   MCPTox confused-deputy (A40895) and action-path unsafety (A41090, A42249, A42239). **Note:
   `tool_credentials` is the *thinnest* asset in the whole corpus (7 papers) and `human_approval` a thin
   surface (15) — these controls are under-evidenced, which matters directly for Passport (§12).**
3. **`input-output-detection` + `runtime-anomaly-detection`** — multi-signal moderation and behavioral
   telemetry (reasoning-token/entropy, attention concentration, confidence runs), treated as noisy triage,
   not gates (real-world vuln-detection F1 ≈ 0.3–0.6 per A42369).
4. **`tamper-evident-traces` + `secure-logging` + `signed-provenance`** — the autonomy-trace substrate
   (A41468 Layer 4, A40189 provenance chain). **Caveat: tamper-evidence is *asserted, not verified* anywhere
   in the corpus** (`tamper_evident_logs` 2 papers, `signed_evidence` 1) — this is a build-and-prove area, not
   a cite-the-literature area.
5. **`adaptive-red-teaming`** — the launch gate implied by the #1 finding; a prerequisite to any robustness
   claim, not a nice-to-have.
6. **`retrieval-authorization`** — RAG/inter-agent boundary gating with a trusted-source anchor (A40353,
   A40893, A40462, A40725, A40231).
7. **`safe-rollback` + `incident-containment` + `kill-switches`** — compensating controls for the guaranteed
   residual harm (§7).
8. **`differential-privacy` + `privacy-preserving-inference` / `-training`** — prefer *accounted* DP and
   secure aggregation over heuristic noise; log the privacy dial (ε/γ) as configuration-of-record.
9. **`signed-provenance` / `content-provenance` / `watermarking-fingerprinting`** — evidence and attribution,
   explicitly *not* prevention (Model-IP folder).
10. Supporting: **`backdoor-detection`, `model-extraction-defenses`, `sandboxed-execution`,
    `network-segmentation`, `adversarial-training`, `evaluation-holdout-protection`.**

## 9. Highest-priority evaluation gaps

1. **Adaptive, defense-aware red-teaming of defenses** — the field's dominant gap (only 28/432 papers).
2. **Non-gameable, human-validated judges** — pervasive single-LLM-judge ASR with no human-agreement
   reporting, sometimes circular; A40866 (SceneJailEval) is a start but is itself an untested LLM-agent judge.
3. **Representation-monitor vs. activation-attack head-to-head** (§6 collision).
4. **Cross-model / closed-API transfer** of white-box representation defenses and detectors (most need
   internals and do not transfer to API-served frontier models).
5. **Over-refusal / benign-FPR** quantification under "resolves the safety-utility trade-off" claims, against
   an adaptive benign-ambiguous set.
6. **Verifiable unlearning acceptance tests** — representation-level residual probes / relearning attacks
   (behavioral non-recall ≠ removal; A39373, A40343, A41120).
7. **Formal privacy accounting + empirical leakage tests** for FL / by-architecture "data-minimization"
   privacy (A39307, A39524, A39338 assert privacy without running the attacks their neighbors demonstrate).
8. **Whole-pipeline guard-stack bypass mitigation** — A41108/A41144 recommend but do not build/validate fixes.
9. **Physical / over-the-air trigger realizability and cross-sensor corroboration** (Origin-relevant; A42439,
   A40881, A40472 argue by digital eval or citation).
10. **Standardized, cross-paper agent-security benchmarks** — MCP/RAG/multi-agent/reasoning-DoS work each
    ships a bespoke harness, so nothing is comparable.

## 10. Where production claims would currently be UNJUSTIFIED

- **"Robust/secure against [attack]" without adaptive red-teaming** — nearly every defense number is a
  non-adaptive upper bound.
- **"Certified" / "guaranteed" robustness** beyond narrow threat models — only CertMask (A37716, known
  single-patch-size) and the smoothing/hash bounds (A37117 ℓ2-radius; A40915 single-embedding forging bound)
  are formal; AntiDote (A40570) is explicitly reduction, **not proof**.
- **"Formal privacy guarantee"** from heuristic noise or by-architecture minimization — no privacy defense in
  the corpus offers formal DP validated against an executed attack.
- **"Data deleted / forgotten"** as guaranteed erasure — approximate unlearning is recoverable and
  fine-tuning reactivates it.
- **Single-LLM-judge ASR as release sign-off** — not validated against human agreement; sometimes circular.
- **Porting open-weight/white-box representation defenses to a closed API** — they need internals.
- **"Physically realizable"** triggers claimed from digital-only evaluation.
- **Watermark/fingerprint as misuse prevention** — it is post-hoc evidence; removal and forgery are largely
  untested (forgery named as an open gap across the Model-IP folder).
- **"Tamper-evident autonomy trace"** as a proven guarantee — the guardian/audit-layer integrity Origin and
  Passport lean on is *asserted, not demonstrated* in this corpus (A41468); it must be independently proven.
- **Trusting a Guardian LLM as an un-injectable anchor** — "an LLM defending an LLM agent" is itself an
  injection surface needing adaptive stress-testing.

## 11. The honest core / adjacent / peripheral split — and what it means

The deterministic triage reports **core 137 (31%), adjacent 245 (56%), peripheral 50 (11%)**. But that
triage is, by its own header, a *heuristic computed from ontology tags, not a hand read* — and it is
**optimistic**. The per-folder hand reads are consistently harsher about how much is truly agent-execution
load-bearing: AILLM-Safety (~44/63 core LLM/agent), Adversarial-ML "dominated by classical ML robustness"
with agent-central work a minority in chunks 2–3, Privacy "only a thin minority on the agent execution
surface" (A40874 the one agent-core paper of 73), Multi-keyword "genuine agent/LLM-security is a minority"
(A40189 the one full-loop paper of 69), Network-Cyber "not primarily agent-runtime" (~8 transferable of 31),
Model-IP (only A40910 on the execution surface of 22), Deepfake and Defense-Mitigation almost entirely
evidence-signals or peripheral.

Corroborating counts from the ontology confirm the agent runtime is thinly covered: `tool_invocation` 16
papers, `agent_to_agent` 28, `human_approval` 15, `logging_telemetry` 12, `tool_credentials` 7,
`coordinating_agents` 22 — versus `model_serving` 250 and `training_pipeline` 125.

**What this means for Origin/Passport:** the corpus is overwhelmingly a *general ML-security* body that
informs the products by **transferable principle and analogy** (robustness geometry, privacy mechanics,
provenance, poisoning). The slice that **directly shapes agent-runtime enforcement** is a minority — on the
order of a couple dozen decision-grade papers, anchored by **A41090, A41468, A40895, A40224, A40353, A40189,
A40874, A42249, A42239, A40840/A36996, A40248, A40910, A41108/A41144**. Read the "137 core" as a generous
outer bound; plan as if the load-bearing agentic evidence base is smaller and thinner than the headline share
suggests, and treat the rest as principled scaffolding rather than drop-in controls.

## 12. Recommended next research additions

Prioritized by the gaps that most constrain Origin/Passport and are *most absent* from this corpus:

1. **Delegated authority & credential brokering** — attenuated delegation, just-in-time / just-enough
   privilege, Zero Standing Privilege, secretless/federated workload identity (OIDC/SPIFFE), CIBA step-up.
   `tool_credentials` (7 papers) is the corpus's thinnest asset and is *the* Passport / credential-broker
   core — a glaring gap to fill from the identity/IAM literature, not the AAAI academic set.
2. **Tamper-evident, cryptographically-attestable audit trails with formal integrity guarantees** — the
   autonomy-trace console's central claim, and near-absent here (2 papers). Ingest transparency-log /
   append-only-ledger / signed-evidence literature.
3. **Multi-agent collusion & coordinating-agent deception at scale** — only 22 papers; MAST (A40224) is a
   start. Directly relevant to multi-agent Passport collaboration.
4. **Non-gameable, human-validated agent-safety judges / verifiers**, including PRM robustness (A40584).
5. **Verifiable unlearning / right-to-be-forgotten** with adversarial acceptance tests.
6. **Closed-API-transferable representation defenses** (most in-corpus defenses require open weights).
7. **Embodied / physical-agent (Origin) trigger realizability and cross-sensor corroboration** — over-the-air
   validation, sensor-health gating (A42439, A40881, A40472 leave this open).
8. **Governance / standards grounding** — the corpus is academic and unmapped to NIST AI RMF, EU AI Act,
   OWASP LLM/Agentic(ASI)/MCP Top 10, MITRE ATLAS; add that mapping so Origin/Passport harm claims are
   regulation-anchored.

---

*Bottom line for decision-makers.* The evidence supports building **layered, cognitive-cycle-aligned
defense-in-depth with intent-bound gating, least privilege, human approval on consequential actions,
provenance/attestation, and a tamper-evident trace** — and it supports **not** shipping any "robust",
"certified-safe", "privately-guaranteed", or "tamper-proof" claim without adaptive red-teaming and
independent verification the corpus itself has not performed. The principle **"Models propose. Environments
verify. Gates decide. Traces prove."** is well-supported as an architecture (A40189, A41468, A41090); the
"Traces prove" leg is the least evidenced in the literature and therefore the highest-value thing Origin and
Passport must prove themselves.
