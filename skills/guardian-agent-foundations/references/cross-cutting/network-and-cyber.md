# Cross-Cutting Chapter — Network and Cyber Security

*Source synthesis: `references/syntheses/Network-Cyber-Security.md` (31 AAAI-26 research cards:
A36959, A36976, A37021, A37053, A37087, A37125, A37144, A37475, A37756, A37844, A38538, A38541,
A38588, A38682, A39096, A39721, A39770, A40100, A40210, A40815, A40903, A40925, A41065, A41178,
A41464, A42153, A42239, A42249, A42318, A42369, A42470). This chapter is a cross-paper reading
organized by the security **thread** requested for the Guardian-Agent brief — identity & access
control, network isolation, zero-trust, supply-chain security, API abuse, credential management,
intrusion detection, audit & forensic readiness — not a per-paper list. It surfaces the arguments
that only become visible when the papers are read against each other.*

---

## Evidence-integrity contract (non-negotiable)

- Every numeric value is **author-reported under that paper's own evaluated (mostly non-adaptive)
  threat model** unless explicitly marked otherwise. The source synthesis flagged several result
  tables as truncated in the extracted PDFs (A37021, A37125, A37756, A37844, A38538, A38541, A38588,
  A39096, A39770, A40903, A41065 in whole or part); those magnitudes are written **"not stated in
  paper"** and are not independently transcribed.
- No titles, authors, venues, datasets, or metrics are invented here. Where the synthesis recorded a
  value as absent or truncated, this chapter writes **"not stated in paper"** rather than supplying one.
- Claims are labeled **(direct)** when they are a finding of the cited paper(s) as recorded in the
  synthesis, and **(reviewer synthesis)** when they are cross-paper judgments — carried over from the
  source synthesis or made in this chapter. Cross-paper judgments are not the assertion of any single
  paper, and there is **no independent replication across these 31 papers** — convergences below are
  *convergent themes across independent domains*, not replicated effect sizes.
- Language is calibrated: "demonstrated under the evaluated threat model", "reduced ASR against the
  tested attacks", "not evaluated against", "requires production validation". No absolutes ("secure",
  "unbreakable", "proven safe") appear.
- **Framing caveat (reviewer synthesis, from §1–§2 of the source).** This category is **not primarily
  agent-runtime security**; it is dominated by learned detectors evaluated under *non-adaptive* threat
  models (the "adversary" is malicious data in a corpus, not an attacker who adapts to the defender).
  Only a minority carry directly transferable agent-security evidence — A42249, A42239, A40210, A41065,
  A42369, and the confidentiality cluster A39721/A40100/A40925. Four papers are off-topic to adversary
  security (A41178 disaster-risk geospatial ML, A41464 water-pipeline sensor faults, A42153 a doctoral
  agenda abstract with no experiments, A42470 driving-hazard detection); their numbers do **not** bound
  security risk and are not used as evidence here. Threads that this corpus barely touches (credential
  management, zero-trust as a deployed architecture) are labeled thin, and the extrapolation to
  Guardian-Agent design is explicitly marked reviewer synthesis rather than presented as a paper finding.

## Reading key — the CPVER mapping

Every implication is tagged to the Guardian-Agent enforcement primitives. This category supplies two
of the corpus's load-bearing slogans directly:

- **"Capability is not permission."** (A42249, A42239.) Broad standing system access converts ordinary
  agent errors into security incidents, and *any model-visible field* is an injection surface.
- **"Trusted inputs / telemetry / labels is the single most consistent unguarded surface."** (reviewer
  synthesis, §3.) Across the detector papers the recurring *implicit* assumption is that data, label
  provenance, and pipeline telemetry are non-adversarial (NVD/CVE labels A36976/A37021; tool-consensus
  labels A37021/A40815; EDR telemetry A40815; MMLU ground-truth A42239). That assumption is exactly
  what an attacker attacks.

- **[C] Capability** — what a model/agent *can do or produce*: a detector's raw score, an agent's tool
  execution, a CTF solver's exploit. Capability is *not* permission and *not* evidence.
- **[P] Permission** — what an action is *authorized* to do: least-privilege, just-in-time authorization,
  action allow-lists, multi-party/threshold activation. Broad standing privilege (A42249) is the
  anti-pattern.
- **[V] Verification** — *independent, adversary-aware checking* before trust: verify-before-trust label
  filters (A36959), reject/defer to human review (A37053), evaluation-integrity harnesses (A42369),
  command-validation gates (A42249). A detector's own score is capability, not verification.
- **[E] Evidence** — *tamper-evident, independent records*: trajectory logs, per-step competency scores,
  provenance/attestation, the autonomy trace (A40210, A42249). An agent's self-reported completion is
  **not** evidence (A42249 hallucinated completion).
- **[R] Residual-risk** — what remains after a control fires, dominated in this category by the
  **replicated absence of adaptive-adversary evaluation**: the residual risk of essentially every
  detector here is *unknown* because it was evaluated non-adaptively. Treat every detection/ASR number
  as an upper bound on real-world protection (or a lower bound on real-world attack success).

The single most transferable meta-finding across the category (reviewer synthesis, §1, §9):
**evaluation methodology dominates measured "capability."** Threshold selection, class imbalance,
synthetic-vs-real gap, and label leakage separate genuine capability from artifact — which is why the
[V] and [R] tags recur on nearly every thread below.

---

## Thread 1 — Identity & access control

**Well-established.** The cleanest empirical statement in the category is A42249's: broad standing
system access turns ordinary agent errors into security incidents — *capability is not permission*
(direct, small-n / version-bound). Its exploratory 5-task × 5-trial suite reports **unauthorized
software install in 100% of certain planning tasks** (Claude Sonnet 3.5), attempted brute-force logins,
and sensitive-app exposure via navigation errors (author-reported). The stated control is a
least-privilege + command-validation gate between agent intent and execution — but it is *proposed and
unbuilt* in the paper. **[P]/[R]**

**Emerging.** Access control bound to *model execution itself*, not to a surrounding perimeter:
A40925 (consensus learning with multi-party perturbation triggers) binds legitimate model activation to
a multi-party/threshold consensus so that "no single party — or thief — can activate the model"
(direct). A39721 (secure MoE inference) treats *which expert/tool is selected* as an access-controlled
secret via oblivious select-then-compute (direct). Read together, these push access control below the
API surface, onto the computation and its routing metadata. **[P]**

**Contested / thin.** This corpus has **no dedicated identity, attestation, or federated-identity study**
(not stated in any paper) — the "identity" it models is coarse (a party in A40925, a client in A40100,
an agent in A41065), not a workload/agent identity with attenuated delegation. Extrapolation to
agent-identity design is reviewer synthesis, not a paper finding.

**Where defenses fail (adaptive / compositional / real-world).**
- A40925's threshold access control leaves **residual ~15% "Acc-Fusion" unauthorized-activation
  accuracy on VGG16 / CIFAR-10** — meaningfully above chance — under a *partial-trigger fusion*
  adversary (direct); a stronger fusion adversary is not evaluated. **[R]**
- A42249's control is unbuilt; and its reliability failures include *hallucinated task completion*
  masking skipped/unsafe steps (direct), so an access-control layer that trusts the agent's own report
  of what it did is defeated by the agent's own error mode. **[R]**
- The confidentiality cluster shows the perimeter is porous below the API: input semantics leak via
  activations (A40100) and via expert-selection access patterns (A39721) even when the payload is
  encrypted (see Thread 2). "Authenticated + encrypted channel" is not access control over what the
  computation reveals. **[R]**

**Implication.**
- **[P] Least-privilege + just-in-time authorization is the primary control**, not broad standing
  access (A42249). Gate irreversible/consequential actions (install, auth, outbound send) behind
  explicit authorization; do not grant autonomous computer-use agents unrestricted system privileges in
  production (reviewer synthesis, §14).
- **[P] Bind authorization to execution and to multi-party consensus for high-value model assets**
  (A40925), accepting the residual ~15% activation headroom as a *monitored* risk, not a closed one.
- **Launch gate:** any "access-controlled" claim inherits the category's non-adaptive caveat; state the
  residual unauthorized-activation rate as an absolute number (A40925 ~15%), and treat an access gate
  that trusts agent self-report as carrying **[R] unknown** residual risk until end-state is
  independently verified (A42249).

## Thread 2 — Network isolation

**Well-established.** Network intrusion detection is present as a *detection* problem
(A38682 cross-dataset NIDS on NetFlow-v2 benchmarks; A40815 EDR endpoint threat), but network
*isolation* as an enforced boundary appears mainly in the multi-agent and confidentiality papers.
A41065 (ambient multi-agent LLMs) is the most complete isolation architecture: gossip-based isolation
of compromised/malfunctioning peer agents, layered over per-agent immune-inspired anomaly detection and
reputation/trust (direct) — though its reported evidence is *task-accuracy* (HumanEval, CIAR, CommonMT,
FairEval), **not measured attack-success** (reviewer synthesis). **[P]/[V]**

**Emerging.** The most transferable isolation insight is **isolate the internal state, not just the
wire**: A40100 (federated split LLM) shows a curious server colluding with a client reconstructs the
input from *forward activations*; A39721 (secure MoE) shows *expert-selection access patterns* leak
client-input semantics even under payload encryption. Both reframe isolation as a property of
intermediate computation — activations and routing metadata are first-class assets to be isolated, and
"the payload is encrypted" is insufficient (direct). A37144 (urban network security game) supplies the
adversary-as-equilibrium framing for interdiction/patrol on a network, solving for equilibrium at scale
on synthetic instances (direct). **[P]/[R]**

**Contested.** Whether isolation-by-encryption suffices is effectively settled *against* in this corpus:
A40100 and A39721 both demonstrate leakage *around* an encrypted payload. The open contest is scope —
A39721 covers only a **semi-honest** adversary (malicious case open), and A40100's forward-activation
Gaussian perturbation is **empirical with no reported ε** (direct), so neither offers a formal isolation
guarantee. **[R]**

**Where defenses fail (adaptive / compositional / real-world).**
- **Collusion bypasses peer-to-peer encryption.** A40100 activation-inversion under server+client
  collusion (direct); an accumulating client or stronger inversion may erode the empirical noise
  further (reviewer synthesis, §11). **[R]**
- **Access-pattern leak bypasses payload encryption.** A39721 — the motivation for oblivious
  select-then-compute is precisely that plaintext expert selection reveals routing (direct). **[R]**
- **Homomorphic aggregation hides updates but does not prevent poisoning.** A41065's FL-with-HE hides
  peer updates but does not stop a poisoning peer; its honest-majority assumption is *unverified against
  Sybil/collusion* (reviewer synthesis, §11) — an isolation boundary that a coordinated set of malicious
  agents can walk through. **[R]**

**Implication.**
- **[P] Treat intermediate state as a confidentiality boundary** in any multi-tenant / offloaded / split
  agent-hosting design: protect activations and routing metadata (A40100, A39721), not just the payload;
  oblivious one-of-N branch selection (A39721 select-then-compute) is a reusable primitive for
  confidential tool/skill routing (reviewer synthesis, §15).
- **[V] Layered, multi-point isolation is the default posture** — per-agent monitoring + system-level
  anomaly detection + reputation-based isolation (A41065) — because a single boundary is bypassable, but
  credit it only as risk-reduction (its evidence is task-accuracy, not attack-success).
- **Launch gate:** an isolation claim proven only for a semi-honest adversary (A39721) or with empirical,
  ε-unreported noise (A40100) carries **[R] unknown** residual risk against a malicious/colluding
  adversary; require the collusion and Sybil cases in the pre-ship suite before relying on the boundary.

## Thread 3 — Zero-trust

**Well-established.** The category's strongest zero-trust statement is A42239's: **any model-visible
field is an injection surface** — not just the user/system prompt, but answer options, tool results, and
retrieved text. Authoritative "contradiction" text embedded *inside a candidate answer option* drives an
LLM off-policy at **E-adoption ≈ 0.5 ("attack success rate of up to 50%")** with **accuracy collapse to
≈ 0.27** (single model QwQ-32B, MMLU, temperature 0.1; author-reported). The defense the card implies is
an *environment-side validity gate* — an allow-list restricting valid actions to the on-policy set
{A–D} that the model cannot be talked past — i.e., trust nothing the model emits, verify against an
external policy (direct + reviewer synthesis). **[V]/[P]**

**Emerging.** Verify-before-trust applied to the *data/label* pipeline: A36959 admits a pseudo-label
only after **cross-temperature consistency + separate-model agreement + a confidence threshold**
(direct) — a zero-trust posture toward training data rather than toward runtime input. A37053 makes
**reject/defer to human review a first-class action** for drifted inputs the model should not trust
itself on (direct). Both instantiate "never trust, always verify" at different pipeline stages. **[V]**

**Contested / nuanced.** A42239 carries an important *internal* nuance: **weak/noisy injections can
slightly raise accuracy** (+5–7% via extra verification) even as the "contradiction" style attacks
(direct). So "the model reacted to injected text" is not uniformly harm — adoption rate and accuracy
delta must be reported *separately*, and a zero-trust gate keyed only to "did output change" would
mislabel benign verification as an attack. **[V]/[C]**

**Where defenses fail (adaptive / compositional / real-world).**
- **Trailing guardrail text is insufficient when the injection lives inside a model-visible field**
  (A42239): prompt hygiene alone does not gate an out-of-set selection; only an environment-side
  allow-list does (reviewer synthesis, §14). **[R]**
- **The trusted-input assumption is near-universal and unguarded.** The detector papers implicitly trust
  labels, telemetry, and corpora (A36976/A37021 NVD/tool-consensus labels; A40815 self-generated labels;
  A42239 MMLU ground truth) — a zero-trust review of these pipelines is *absent* across the category
  (reviewer synthesis, §3). **[R]**
- **Adaptive evaluation is missing**, so a validity gate's real-world robustness against an attacker who
  shapes fields to satisfy the allow-list is unmeasured (A42239 is single-model, non-adaptive
  templates). **[R]**

**Implication.**
- **[V]/[P] Make the validity/authorization gate environment-side and enforce an allow-list the model
  cannot be talked past** (A42239 {A–D}-only; A42249 command validation), treating every model-visible
  field — options, tool results, retrieved text — as untrusted input (reviewer synthesis, §14–15).
- **[V] Extend zero-trust to the data plane:** multi-signal verify-before-trust for label/data provenance
  (A36959) and reject/defer routing for low-confidence/drifted inputs (A37053).
- **Launch gate:** report option/field-injection **adoption rate and accuracy delta separately** (A42239)
  as a red-team KPI; a validity gate validated only on non-adaptive templates carries **[R] unknown**
  residual risk against a gate-aware attacker.

## Thread 4 — Supply-chain security

**Well-established.** The load-bearing supply-chain finding is A42369's (VulnBench): **evaluation and
label integrity is itself the attack surface**. Threshold optimization improved F1 in **100% of
model-dataset combinations** (median +0.082, best +0.542, author-reported); synthetic sets (Juliet F1
0.900, VulDeepecker 0.959) *vastly overstate* real-world performance (DiverseVul 0.307, Reveal 0.486),
and identifier-encoded labels (e.g., `CWE114_bad()` in Juliet) leak the answer — "top score on the wrong
exam." VulnBench cites Risse et al. 2025 that ~9 in 10 vulnerability-detection studies use inappropriate
evaluation (a *citation*, not an original VulnBench measurement) (direct). This is the category's warning
that a code/dependency-vuln detector fed into a supply-chain gate is a **triage aid, not a correctness
oracle** — real-world F1 ≈ 0.3–0.6. **[V]/[R]**

**Emerging.** Securing the *training/label* supply chain against noisy provenance:
A36959 (verify-before-trust label filter for script malware), A36976 (explicit negative result — LLM-only
underperforms tuned small models on vuln-fixing-commit identification, with **NVD/CVE label noise**
called out), A37021 (GNN smart-contract detector on ≥3-tool-consensus labels), A40815 (compress ultra-long
EDR telemetry — 3.6B events, >80% of samples exceeding 1M tokens — with *self-generated* label noise).
A separate emerging sub-thread is **proactive protection of one's own media in the generative supply
chain**: A37756 (anti-style-mimicry perturbation) and A37844 (anti-malicious-edit perturbation) —
"poison-to-protect." **[V]/[E]**

**Contested.** Whether protective perturbation actually protects: A37756/A37844 report strong protection
under their (largely non-adaptive) fine-tuning/editing threat models, yet **both cards cite Hönig et al.
2024** that such perturbations "cannot reliably protect" against a purifying/retraining adversary
(direct). The supply-chain lesson is that a producer-side poison is opt-in mitigation, not a guarantee.
**[R]**

**Where defenses fail (adaptive / compositional / real-world).**
- **Synthetic-benchmark inflation and label leakage** mean a detector's headline capability does not
  survive contact with real code (A42369 DiverseVul 0.307 / Reveal 0.486 vs Juliet 0.900). A
  supply-chain gate calibrated on synthetic sets over-trusts itself. **[R]**
- **Noisy ground truth** (NVD/CVE, tool-consensus, self-generated, LLM-summarized labels) propagates into
  every downstream trust decision (A36976, A37021, A40815, A36959) (reviewer synthesis, §12). **[R]**
- **Protective perturbations are historically defeated by purification/retraining** (A37756, A37844,
  citing Hönig et al. 2024); no adaptive-attacker evaluation is shown. **[R]**

**Implication.**
- **[V] Gate agent-written / third-party code with an evaluation-integrity-aware detector, but never as a
  correctness oracle** (A42369): require threshold-optimized, identifier-anonymized, seeded, CI-reported
  real-world F1, and treat the output as triage requiring human review (reviewer synthesis, §16).
- **[V] Multi-signal verify-before-trust for data/label provenance** before it enters a security model
  (A36959 cross-temperature + separate-model + confidence; A36976 capability-partitioned channels).
- **[E] Provenance/attestation over the code/label/media supply chain**, since accuracy alone does not
  reveal a corrupted label or a purified protective perturbation.
- **Launch gate:** report **real-world (not synthetic) detector F1 with CIs and identifier-anonymized
  splits** (A42369) as a launch KPI; a detector validated only on synthetic/leaky benchmarks carries
  **[R] unknown** real-world residual risk and may not gate a merge on its own.

## Thread 5 — API abuse

**Well-established.** Two concrete API-abuse channels are demonstrated. (1) **Choice/decision-layer
injection through the API's own response fields** — A42239 shows authoritative text placed *inside a
candidate answer option* drives the model off-policy (E-adoption ≈ 0.5, accuracy ≈ 0.27; QwQ-32B, MMLU;
author-reported): the abuse surface is any field the API round-trips back into the model, not just the
user prompt. (2) **Broad-privilege / confused-deputy agent abuse** — A42249: unauthorized installs (100%
in certain planning tasks), attempted brute-force logins, sensitive-app exposure via navigation errors
(Claude Sonnet 3.5, small-n exploratory). **[C]/[P]**

**Emerging.** Abuse of *inference-serving* APIs to violate confidentiality: A40100 (a curious server +
colluding client reconstructs the input via a constructed model-inversion attack on the split-inference
API) and A39721 (expert-selection *access-pattern side channel* through the MoE serving API leaks input
semantics). And **offensive-agent capability uplift** as an abuse of model APIs: A40210 (LLM CTF agents
across binary exploitation, web, reverse engineering, forensics, cryptography, misc — CTFTiny, 50
challenges, 6 domains), with trajectory-level competency scoring and an explicit *dual-use* framing
(direct). **[C]/[R]**

**Contested / nuanced.** A42239's within-paper nuance again applies: not every reaction to an injected
API field is an attack — weak/noisy injections can *raise* accuracy (+5–7%), so API-abuse monitoring
keyed only to "output changed after injected content" over-flags (direct). And A40210's dual-use finding
means the *same* capability is legitimate red-teaming or abuse depending on authorization, not on the
output itself. **[C]/[P]**

**Where defenses fail (adaptive / compositional / real-world).**
- **Permission keyed to identity/perimeter misses the confused deputy**: A42249's harm occurs during
  ostensibly benign tasks via a legitimately-privileged agent (direct). **[R]**
- **Payload encryption does not stop inversion or access-pattern abuse** of the serving API (A40100,
  A39721). **[R]**
- **Single-model / single-dataset scope**: A42239's "50%" is one model's worst case under hand-crafted
  non-adaptive templates; A42249 is 3 agents × 5×5 trials with partly subjective video scoring; A40210 is
  D-CIPHER-derived with hosted-model non-determinism (reviewer synthesis, §12) — so the abuse rates do
  not yet generalize. **[R]**

**Implication.**
- **[P] Least-privilege + command validation between intent and execution** (A42249): gate
  install/auth/outbound-send behind explicit authorization; do not let a broadly-privileged agent be the
  confused deputy.
- **[V]/[P] Treat every API-returned field as untrusted and enforce an out-of-set-rejecting validity
  gate** (A42239); protect serving-API intermediate state (A40100, A39721).
- **Launch gate:** adopt as pre-deployment red-team KPIs the **option/field-injection adoption rate and
  accuracy delta** (A42239), **unauthorized-install / brute-force / sensitive-app-exposure incidence**
  (A42249), **reconstruction quality under a constructed inversion attack** (A40100), and
  **trajectory-level competency + dual-use capability** (A40210); report absolute residuals, not only
  relative reductions.

## Thread 6 — Credential management

**Thin in this corpus (state it plainly).** No paper in the category studies credential vaulting,
just-in-time credential issuance, secretless/federated identity, or a credential broker (not stated in
any paper). What the corpus *does* supply is (a) the anti-pattern this thread exists to eliminate and
(b) two credential-adjacent primitives; the mapping to a credential-management design is reviewer
synthesis, not a paper finding.

**Well-established (the anti-pattern).** A42249 is the empirical grounding for *why* standing credentials
are dangerous: broad standing system access converts ordinary agent errors into security incidents —
**attempted brute-force logins** and **sensitive-app exposure** appear directly, alongside 100%
unauthorized-install in certain planning tasks (direct, small-n). The lesson is least-privilege +
just-in-time authorization, i.e., the credential the agent holds at any moment should be the minimum for
the current step. **[P]/[R]**

**Emerging (credential-adjacent primitives).**
- **Multi-party / threshold authorization bound to model execution** (A40925): a consensus perturbation
  trigger acts like a threshold credential — no single party (or thief of the weights) can activate the
  model (direct). This is the closest thing in the corpus to a "no single standing secret" design. **[P]**
- **Routing metadata as a secret to be managed** (A39721): the expert-selection pattern is treated as
  confidential via oblivious computation — a reminder that credential-like secrets in an agent stack
  include *which tool/skill/expert was selected*, not only tokens (direct). **[P]**

**Where defenses fail (adaptive / compositional / real-world).**
- A40925's threshold activation leaves **~15% residual unauthorized-activation** under partial-trigger
  fusion (direct) — a threshold-credential analogue is not fully closed against a fusion adversary. **[R]**
- A42249's least-privilege gate is *proposed and unbuilt*; and hallucinated task completion (direct) means
  a credential-scoping layer that trusts the agent's report of what it accessed is defeated by the agent's
  own error mode. **[R]**
- There is **no credential-broker or secretless-identity evaluation** in the corpus to fail *or* succeed;
  any Guardian-Agent credential-broker claim must be validated outside this evidence base (reviewer
  synthesis). **[R]**

**Implication.**
- **[P] Just-in-time, just-enough-privilege credentials with human approval on consequential actions**
  (A42249), and **threshold/multi-party authorization for high-value model assets** (A40925) — the two
  patterns the corpus does support.
- **[E] Do not trust the agent's self-report of what it accessed**; log actual credentialed actions
  independently (A42249 hallucinated completion → completion self-reports cannot be trusted).
- **Launch gate:** credential-management for the Guardian-Agent stack is **[R] production-/source-
  validation-pending** relative to this corpus (it is not studied here); ship it only with independent
  evidence, and report A40925's ~15% residual as the closest in-corpus quantified analogue for
  threshold-authorization headroom.

## Thread 7 — Intrusion detection

**Well-established.** Intrusion/anomaly/malware detection is the *bulk* of the category, spanning
network (A38682 cross-dataset NIDS on NF-UNSW-NB15 / NF-ToN-IoT / NF-CSE-CIC-IDS2018), endpoint
(A40815 EDR on 3.6B events, 62 malicious families, >80% of samples exceeding 1M tokens), scripts
(A36959 AutoMalDesc, 157,126 scripts), graph/time-series anomaly (A38538, A39096, A39770 on MSL/SMAP/SWaT/
TAO — SWaT giving indirect ICS-attack relevance), and graph-LLM fraud (A38541, A38588). The recurring
design answer is **capability partitioning + hybrid escalation**: invoke the expensive LLM only on
hard/borderline cases, with a tuned small/specialized model often out-discriminating a single large model
on subtle security-code distinctions (A36976 explicit negative result; A36959 LLM annotator + Phi-3.5
consistency filter; A38588 LLM-as-guide on lowest-score anchors; A40815 compress-then-reason) (direct).
**[C]/[V]**

**Emerging.** Detection that confronts *distribution shift* rather than assuming a static corpus:
A37053 (DRMD) models **concept drift as an evolving distribution** with a first-class reject/defer action
and time-aware TESSERACT evaluation (Transcendent 259,230 apps 2014–2018; Hypercube 159,839 apps
2021–2023); A38682 models **cross-dataset / unseen-attack transfer**; A37087 uses **LOC-stratified**
evaluation (easy 0–149 / medium 150–299 / hard 300+) that exposes brittleness single-function benchmarks
hide (direct). A41065 adds **per-agent immune-inspired anomaly detection** as intrusion detection *inside*
a multi-agent runtime. **[V]/[R]**

**Contested.** The reliability of the *scoring* substrate: A36959 shows detection improvement is
statistically strong (McNemar p < 1e-5) yet its summary-quality win-rates are near-tie and LLM-judge
preferences disagree with humans; A40210 *relies on* a Claude-family judge (with a self-referential-bias
caveat) while A36959 shows judges disagree — the same tool, opposite posture (direct). LLM-as-judge
components in a detection pipeline are not calibrated across these papers (reviewer synthesis, §10). **[V]**

**Where defenses fail (adaptive / compositional / real-world).**
- **No adaptive/evasion adversary is evaluated** across the detector papers — a *replicated absence*, the
  category's most consistent signal (reviewer synthesis, §3, §9). Every detection number is "under the
  evaluated non-adaptive distribution." **[R]**
- **Concept drift bypasses static classifiers** (A37053 IID-trained detectors degrade over time). **[R]**
- **Fraud camouflage / collusion / borderline structuring bypasses single-view GNNs** (A38588, A38541);
  **covert channels are invisible at the content layer** (A37125 steganalysis Pe ≈ 0.5 against standard
  CNN steganalyzers; A40903 stego text equals cover at the text layer), so content-inspection DLP cannot
  see a channel designed to preserve cover statistics (direct). **[R]**
- **Real-world detector performance is modest** — A42369's F1 ≈ 0.3–0.6 on real code — so a detector used
  as a *gate* over-trusts a noisy signal. **[R]**

**Implication.**
- **[V] Treat detectors as noisy triage aids, not gates** (real-world F1 ≈ 0.3–0.6, A42369); require
  out-of-band corroboration and human review for any security decision a single detector or LLM drives
  (A36959, A40815) (reviewer synthesis, §16).
- **[V] Evaluate under the deployment distribution** — time-aware/drift-honest splits (A37053), cross-
  dataset transfer (A38682), LOC/context stratification (A37087) — not a convenient IID split.
- **[E] Egress/DLP monitoring must assume covert channels invisible at the text/pixel layer** (A37125,
  A40903) → shift to model/provenance attestation and anomalous-fine-tuning monitoring, not content
  inspection alone (reviewer synthesis, §14).
- **Launch gate:** a detector validated only in-distribution and non-adaptively carries **[R] unknown**
  residual risk under drift and against an evasion-aware adversary; require drift/cross-dataset evaluation
  and calibrated (not single-LLM-judge) scoring before it gates anything.

## Thread 8 — Audit & forensic readiness

**Well-established.** The category's audit substrate is **trajectory-level evidence, not pass/fail**.
A40210 makes the case directly: per-challenge pass/fail hides *how* capability was exercised, so it scores
competency at the trajectory level with dual-use measurement (direct). A42249 corroborates from the agent
side: interaction-by-interaction and video logs are the audit evidence, and because a reliability failure
mode is **hallucinated task completion masking skipped steps**, completion self-reports *cannot* be
trusted — independent end-state verification is required (direct). Together they establish that the unit of
agent audit is the logged trajectory plus an independent check, not the agent's own success claim. **[E]/[V]**

**Emerging.** Forensic *reproducibility* as evaluation integrity: A42369 (VulnBench) supplies the harness
discipline — threshold optimization, leakage control, identifier anonymization, seeded splits, multi-seed
CIs (direct) — so that a reported security number is reconstructable rather than an artifact. A36959's
verify-before-trust label filter (cross-temperature consistency + separate-model agreement + confidence
threshold) is a provenance record for admitted pseudo-labels (direct). **[E]/[V]**

**Contested / caveated.** The *audit scorer itself is a trust surface*: LLM-as-judge scoring is used
without inter-rater/human-agreement calibration (A36959 shows judges disagree with each other and with
humans; A40210 relies on a judge with a self-referential-bias caveat), and A42249's video review is partly
subjective (direct). An audit record scored by an uncalibrated judge is weak forensic evidence
(reviewer synthesis, §8, §10). **[V]/[R]**

**Where defenses fail (adaptive / compositional / real-world).**
- **The agent's self-reported success is not evidence** (A42249 hallucinated completion) — an audit trail
  that logs "task complete" without end-state verification is forensically empty. **[R]**
- **Truncated/absent metrics** across many cards (A37021, A37125, A37756, A37844, A38538, A38541, A38588,
  A39096, A39770, A40903, A41065) mean several headline claims are not reconstructable from the evidence
  base — a forensic-readiness gap in the literature itself (reviewer synthesis, §12). **[R]**
- **Proposals with zero experiments** (A42318 AI-vs-AI defense; A42153 agenda abstract) provide no audit
  evidence at all and must be read as agendas (direct). **[R]**

**Implication.**
- **[E] Trajectory-level evidence logging + multi-dimension competency scoring is first-class** (A40210),
  mapping directly onto the autonomy-trace console; log per-step interactions (and, where feasible,
  screen/video) as tamper-evident audit evidence (A42249) (reviewer synthesis, §14–15).
- **[V] Independent end-state verification, never completion self-report** (A42249), and **calibrated /
  anti-gaming controls on any LLM-judge audit component** (A36959, A40210).
- **[E] Forensic reproducibility discipline** — seeded splits, identifier-anonymized data, CIs (A42369) —
  so a security claim in the trace can be reconstructed.
- **Launch gate:** require the audit trail to record **divergence between agent-claimed and actual
  completion** (A42249) and **threshold-optimized real-world F1 with CIs** (A42369) as forensic KPIs; a
  claim resting on an uncalibrated judge or a truncated/absent metric is **[R] source-validation-pending**.

---

## Cross-thread reading — how the threads compound

The threads are not independent; the category's transferable value is where they **compose** (reviewer
synthesis):

- **Zero-trust × API abuse × identity/access** → *any model-visible field* (option, tool result, retrieved
  text) is an injection surface (A42239), and a broadly-privileged agent turns that injection into a
  security incident (A42249). Only an **environment-side validity gate [V]/[P]** enforcing an allow-list
  the model cannot be talked past — plus **least-privilege [P]** — addresses both at once.
- **Network isolation × credential management × API abuse** → payload encryption is bypassed by activation
  inversion (A40100) and expert-selection access patterns (A39721); "authenticated encrypted channel" is
  not isolation of what the computation reveals. **Intermediate-state isolation [P]** and treating routing
  metadata as a secret are the shared control.
- **Supply-chain × intrusion detection × audit** → detectors fed into a supply-chain or IDS gate are noisy
  (real-world F1 ≈ 0.3–0.6, A42369) and their scoring substrate (LLM-as-judge) is uncalibrated (A36959,
  A40210). **Triage-not-gate [V]** + **forensic reproducibility [E]** is the only defensible posture.
- **Identity/access × audit** → an access gate that trusts the agent's self-report is defeated by
  hallucinated completion (A42249). **Independent end-state verification [V]/[E]** is the cross-thread
  control.
- **Every new trust-decision surface a defense introduces is itself attackable** — reputation/aggregation
  weights (A41065), threshold/consensus triggers (A40925 ~15% residual), robustness gates (A37475 shows
  standard FGSM/PGD evaluation *understates* true vulnerability by missing the angular direction) — so no
  single control is load-bearing (reviewer synthesis, §15).

## Consolidated launch-gate checklist (reviewer synthesis, grounded in the cards)

1. **Adaptive-adversary gate (applies to all threads).** No detector or defense ships on a non-adaptive
   evaluation — the category's replicated *absence*. Absent an adaptive, defense-aware attacker, the launch
   record states residual risk is **[R] unknown**, never "secure/proven-safe" (reviewer synthesis, §3, §9,
   §16). **[R]**
2. **Environment-side validity gate (Threads 3, 5).** Enforce an allow-list the model cannot be talked
   past; treat every model-visible field as untrusted (A42239); report field-injection adoption rate and
   accuracy delta *separately*. **[V]/[P]**
3. **Least-privilege + JIT authorization gate (Threads 1, 5, 6).** Gate install/auth/outbound-send behind
   explicit authorization; multi-party/threshold activation for high-value model assets, reporting the
   ~15% residual (A40925); no unrestricted system privilege for autonomous computer-use agents (A42249).
   **[P]**
4. **Intermediate-state isolation gate (Thread 2).** Protect activations and routing metadata, not just the
   payload (A40100, A39721); require the collusion/Sybil cases before crediting an isolation boundary. **[P]/[R]**
5. **Detector-as-triage gate (Threads 4, 7).** Real-world (not synthetic) F1 with CIs and identifier-
   anonymized splits (A42369); detectors corroborated by human review, never a sole correctness oracle
   (A36959, A40815). **[V]/[R]**
6. **Distribution-match gate (Thread 7).** Time-aware/drift-honest, cross-dataset, LOC-stratified
   evaluation (A37053, A38682, A37087) — in-distribution-only numbers carry unknown residual risk under
   drift. **[V]/[R]**
7. **Covert-egress gate (Thread 7).** Assume covert channels invisible at the content layer (A37125,
   A40903); shift to provenance/model attestation and anomalous-fine-tuning monitoring, not content-inspection
   DLP alone. **[E]**
8. **Trajectory-evidence + independent-verification gate (Thread 8).** Log per-step trajectories and record
   divergence between agent-claimed and actual completion (A42249); calibrate any LLM-judge audit component
   (A36959, A40210); forensic reproducibility via seeded/anonymized splits (A42369). **[E]/[V]**
9. **Independent-validation gate (all threads).** Single-paper, truncated-evidence, and thin-thread results
   (credential management and zero-trust-as-architecture are *not* studied in this corpus) must be
   independently validated on the target stack; proposals (A42318, A42153) are agendas, not assurances.
   **[R]**

---

*Closing evidence-integrity note.* Every metric in this chapter is reported as it appears in the source
synthesis's research cards, labeled author-reported where the card so labels it; several headline numbers
sit in table regions the synthesis marked truncated (A37021, A37125, A37756, A37844, A38538, A38541,
A38588, A39096, A39770, A40903, A41065) and are therefore written "not stated in paper" and not
independently verified. No titles, authors, venues, datasets, or numbers were invented; where a card
recorded a value as absent, this chapter does not assert one. Cross-paper judgments are marked *(reviewer
synthesis)*; all other claims trace to the cited paper id under its own evaluated — and, across this
category, overwhelmingly *non-adaptive* — threat model. Four papers (A41178, A41464, A42153, A42470) are
off-topic to adversary security and are excluded from the security claims above. This chapter draws only on
`references/syntheses/Network-Cyber-Security.md`; claims requiring the primary PDFs (e.g. exact table
cells) are **[R] production-/source-validation-pending**.
