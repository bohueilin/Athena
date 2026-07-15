# Partial Synthesis — Network-Cyber-Security, chunk 0 (31 papers)

Papers: A36959, A36976, A37021, A37053, A37087, A37125, A37144, A37475, A37756, A37844, A38538, A38541, A38588, A38682, A39096, A39721, A39770, A40100, A40210, A40815, A40903, A40925, A41065, A41178, A41464, A42153, A42239, A42249, A42318, A42369, A42470 (all AAAI-26).

> Evidence-integrity note: every claim below traces to a specific card. "Paper" = author-stated finding; "reviewer" = synthesis/limitation added in the card. Numbers are quoted only where the card states them; where a card marks a value truncated/absent it is written "not stated in paper". No claim is elevated to "secure/proven"; detectors are described as "reduced/raised metric X under the evaluated (non-adaptive) threat model."

## 0. Composition of this chunk (load-bearing caveat)
This "Network-Cyber-Security" chunk is dominated by **defensive ML detectors evaluated under non-adversarial threat models**, not by agent-runtime security. Roughly:
- **Code/vulnerability detection**: A37021 (GNN smart-contract), A37087 (LLM long-context C/C++), A36976 (vuln-fixing-commit ID), A42369 (VulnBench eval harness).
- **Malware / intrusion / fraud / anomaly detection**: A36959 (LLM malware-script self-training), A37053 (deep-RL Android malware under drift), A38682 (zero-shot NIDS), A38541 + A38588 (graph-LLM fraud), A38538 + A39096 + A39770 (graph/time-series anomaly), A40815 (LLM EDR endpoint threat detection).
- **Steganography / covert channel / IP-protective perturbation**: A37125 (image LDM stego), A40903 (content-preserving text stego), A37756 (anti-style-mimicry), A37844 (anti-malicious-edit).
- **Privacy-preserving ML / model access-control**: A39721 (secure 2-PC MoE), A40100 (federated split LLM vs inversion), A40925 (multi-party trigger access-control).
- **Adversarial-ML attack**: A37475 (geometry-aware white-box evasion of hyperbolic nets).
- **Game-theoretic**: A37144 (urban interdiction NE solver), A42318 (AI-vs-AI deception, proposal only).
- **Genuinely agent-security core**: A40210 (offensive CTF agents), A42239 (option-level injection into LLM choices), A42249 (computer-use-agent security eval), A41065 (multi-agent LLM resilience).
- **Off-topic / miscategorized**: A41178 (disaster-risk geospatial ML), A41464 (water-pipeline monitoring), A42153 (doctoral TSAD abstract), A42470 (autonomous-driving hazard detection — "threat" = physical hazard, not adversary).

Consequence: the strongest *transferable* signal for a guardian/autonomy stack comes from a **minority** of papers (A42249, A42239, A40210, A41065, A42369, plus the privacy pair A39721/A40100 and access-control A40925). Most others contribute *methods* (hybrid detectors, verify-before-trust pipelines, telemetry compression) rather than *agent threat-model evidence*.

## 1. Dominant threat models
Two clusters:
- **Non-adaptive "detection-target" threat model** (the majority): the "adversary" is malware/fraud/vulnerable-code/anomalous-traffic present in data; the model is the defender and is **not** stress-tested against an attacker who adapts to it (A36959, A36976, A37021, A37053, A37087, A38538, A38541, A38588, A38682, A39096, A39770, A40815, A42369). Every one of these cards explicitly flags "no adaptive/evasion adversary evaluated" as a reviewer limitation.
- **True adversary-vs-system threat models** (the minority): white-box gradient evasion (A37475); honest-but-curious confidentiality (A39721 semi-honest 2-PC; A40100 curious-server + colluding-client inversion); model theft / unauthorized activation (A40925); adaptive AI attacker (A42318, proposal); prompt-injection / broad-privilege abuse at the agent layer (A42239, A42249); coordinated/malicious peer agents (A41065). Steganography papers (A37125, A40903) invert the frame — the "adversary" is a passive **warden/steganalyst**, and the paper's method is the evasive channel.

Reviewer synthesis: the chunk's recurring *implicit* assumption is **trusted inputs/telemetry/labels** — data integrity, label provenance, and pipeline (GitHub API in A36976; EDR telemetry in A40815; NVD labels in A36976/A37021) are assumed non-adversarial, which is the single most consistent unguarded surface.

## 2. Major attack families
- **Prompt injection at the decision/action layer** — authoritative text embedded *inside a candidate answer option* drives an LLM off-policy (A42239: "attack success rate of up to 50%" E-adoption, accuracy collapse to ≈0.27, single model QwQ-32B); prompt-injection susceptibility of computer-use agents (A42249, qualitative).
- **Broad-privilege / confused-deputy agent abuse** — unauthorized software install in 100% of certain planning tasks, brute-force login attempts, sensitive-app exposure (A42249, small-n exploratory).
- **Adversarial evasion** — geometry-aware white-box attack (A37475: AGSM/PAGD beat FGSM/PGD at equal ε; radial component "≈no effect", angular drives failure); concept-drift-as-evasion (A37053); fraud camouflage/collusion (A38588).
- **Model inversion / input reconstruction** in split learning under server+client collusion (A40100).
- **Access-pattern side channel** — expert-selection routing leaks client input semantics in MoE serving (A39721).
- **Model theft / unauthorized adaptation** — stolen weights, style-mimicry fine-tuning (A40925; and the *modeled misuse* in A37756/A37844).
- **Covert channel / exfiltration** — steganography that evades standard steganalyzers and text/pixel DLP (A37125: steganalysis Pe≈0.5; A40903: claimed 100% extraction from unmodified cover text).
- **Offensive-agent capability uplift** — LLM CTF agents across pwn/web/RE/forensics/crypto (A40210).
- **Eval-integrity attacks (unintentional)** — benchmark contamination / label leakage inflating detector scores (A42369).

## 3. Major defense families
- **Learned detectors** (GNN / hypergraph / contrastive / LLM-hybrid) for malware/vuln/fraud/intrusion/anomaly — the bulk of the chunk. Common refinement: **hybrid LLM + small/specialized model with an ensemble gate** (A36976 AdaBoost over message+patch channels; A36959 LLM annotator + Phi-3.5 consistency filter; A38541/A38588 selective-LLM + graph; A40815 hypergraph-compression + LLM).
- **Verify-before-trust / multi-signal validation of training data** (A36959: cross-temperature consistency + separate-model agreement + confidence threshold before admitting pseudo-labels).
- **Reject/defer + human-in-the-loop as a first-class action** (A37053 explicit `reject` action routing to manual review; A42318 human authorizes deception deployment; A42249 proposes command-validation gate + human approval).
- **Least-privilege / command-validation gate between agent intent and execution** (A42249, proposed; A42239 reviewer-implied allow-list on valid actions).
- **Privacy-preserving inference** — cryptographic 2-PC/HE with oblivious branch selection (A39721); forward-activation Gaussian noise in federated split (A40100, empirical not formal-DP).
- **Multi-party / threshold authorization bound to model execution** (A40925).
- **Proactive protective perturbation** (A37756, A37844 — "poison-to-protect" media against fine-tuning/editing misuse).
- **Immune-inspired anomaly detection + probabilistic trust/reputation + gossip isolation + FL-with-HE** as a layered multi-agent runtime defense (A41065).
- **Evaluation-integrity harness** (A42369 threshold optimization + leakage control + multi-seed CIs; A40210 trajectory-level competency scoring).

## 4. Strongest replicated findings (cross-paper agreement)
- **Evaluation methodology dominates measured "capability."** A42369 is the load-bearing statement: threshold optimization improves F1 in 100% of model-dataset combos (median +0.082, up to +0.542), synthetic sets (Juliet 0.900, VulDeepecker 0.959) vastly overstate vs real-world (DiverseVul 0.307, Reveal 0.486); it cites (Risse et al. 2025) that ~9/10 vuln-detection studies use inappropriate evaluation. This is corroborated in spirit by A37053 (time-aware TESSERACT splits vs inflated IID), A37087 (context-length stratification exposing brittleness single-function benchmarks hide), and A36959/A40210 (LLM-as-judge disagreement).
- **LLM-only underperforms tuned small/specialized models on subtle security-code discrimination** (A36976 explicit negative result; A37021/A37087 use structure-aware learned detectors; A40815 compresses before invoking LLM). The recurring design answer is capability-partitioning + ensembling, not a single large model.
- **"Capability is not permission"** — broad standing system access converts ordinary agent errors into security incidents (A42249, directionally credible / small-n).
- **Authoritative injected text breaks in-policy behavior**, but weak/noisy injections can *raise* accuracy via extra verification (A42239 — a within-paper nuance, single model).
- **Near-universal shared gap**: no adaptive-adversary evaluation. This is a *replicated absence*, not a replicated positive result — treat every detection number in this chunk as "under the evaluated non-adaptive distribution."

## 5. Conflicting / tension findings
- **"Provable security" claims vs reviewer caution.** A37125 asserts information-theoretic security (DKL=0 by construction, sign-invariance from a 100-image study); A40903 claims "perfect security" from content-preservation and 100% extraction. Reviewer syntheses in both cards downgrade these to *contingent on idealized distribution assumptions and non-adaptive steganalyzers* — no adaptive/model-level steganalysis shown.
- **Do protective perturbations actually protect creators?** A37756/A37844 report strong protection under their (largely non-adaptive) fine-tuning/editing threat models, yet both cards cite Hönig et al. 2024 that such perturbations "cannot reliably protect" against a purifying/retraining adversary.
- **LLM-as-judge reliability.** A36959 shows judges disagree with each other and with humans (Phi-3.5/Mixtral favor V1; Claude-3.7/GPT-5 favor V2; humans marginally prefer V1); A40210 relies on a Claude-family judge to score solvers (self-referential-bias risk noted). Same tool, opposite reliability posture between papers.
- **Summary-quality "improvement" is ambiguous** even when detection improvement is significant (A36959: McNemar p<1e-5 for detection, but summary win-rates are near-tie and human-vs-LLM-judge disagree).

## 6. Defense bypasses documented
- **Steganography bypasses steganalysis + content-inspection DLP** (A37125 Pe≈0.5 against SRNet/XuNet/SiaStegNet; A40903 stego==cover at text layer).
- **Concept drift bypasses static classifiers** (A37053); **fraud camouflage/collusion bypasses single-view GNNs** (A38588); **borderline structuring** places fraudsters near the decision boundary.
- **Geometry-agnostic robustness evaluation understates true vulnerability** — FGSM/PGD miss the angular-direction exposure AGSM exploits (A37475).
- **Collusion (curious server + malicious client) bypasses peer-to-peer encryption** in split learning (A40100).
- **Access-pattern leak bypasses payload encryption** — plaintext expert selection reveals routing even when input is encrypted (A39721).
- **Partial-trigger fusion partially bypasses multi-party access control** — residual Acc-Fusion up to ≈15% (VGG16 CIFAR-10) is meaningfully above chance (A40925).
- **Agents bypass their own safety semantics** — hallucinated task completion masks skipped/unsafe steps (A42249).

## 7. Benchmark / eval limitations (recurring)
- **Non-adaptive evaluation is near-universal** (§1, §4). Treat all ASR/detection numbers as non-adaptive lower/upper bounds.
- **Synthetic-benchmark inflation & label leakage** (A42369 explicit; A37021/A37087/A40815 rely on tool-consensus or self-generated labels the cards flag as noisy).
- **Single-model / single-dataset / single-framework scope** — A42239 (QwQ-32B, MMLU only; "50%" is one model's worst case), A42249 (3 agents, 5×5 trials, partly subjective video scoring), A40210 (D-CIPHER only; hosted-model non-determinism).
- **LLM-as-judge calibration gaps** (A36959, A40210) — no inter-judge/human-agreement calibration reported.
- **Truncated result tables** in many extracted cards (A37021, A37125, A37756, A37844, A38538, A38541, A38588, A39096, A39770, A40903, A41065) — several headline metrics are "not stated in paper" / recoverable only qualitatively.
- **Proposals with zero results** (A42318) and **research-plan abstracts with no new experiments** (A42153) must be treated as agendas, not evidence.

## 8. Recurring implementation patterns (transferable)
- **LLM + small-model/graph hybrid with ensemble or selective escalation** — invoke the expensive model only on hard/borderline cases (A38588 "LLM as guide" on lowest-score anchors; A37053 reject/defer; A36976 capability partitioning).
- **Compress high-volume structured telemetry into graph/hypergraph embeddings, subtract a benign baseline, then let an LLM reason** — fits ultra-long action/telemetry logs into context (A40815; A38541 dual-granularity summarization + diffusion trimming).
- **Multi-signal verify-before-trust for data/label provenance** (A36959).
- **Tool-grounded reasoning with external verifiers + structured-output reward shaping to avoid degenerate/reward-hacked outputs** (A42470 prediction-number reward counters non-repeat-reward collapse; A42249's proposed toolchain).
- **Human-authority separation** ("model proposes; human/gate decides") (A42318, A42249, A37053).
- **Trajectory-level evidence logging + competency scoring** as the unit of agent evaluation (A40210).
- **Oblivious one-of-N branch selection** to hide routing metadata (A39721) — reusable for confidential tool/skill routing.

## 9. Product / architecture implications (Origin / guardian stack)
- **Environment-side validity gate / action allow-list** that rejects out-of-set selections regardless of model output — directly motivated by A42239 (choice-level injection) and A42249 (broad-privilege abuse). Treat *every model-visible field* (answer options, tool results, retrieved text) as an injection surface, not just the user/system prompt.
- **Least-privilege + JIT authorization + command validation between agent intent and execution** (A42249). Gate irreversible/consequential actions (install, auth, outbound send) behind human approval.
- **Autonomy-trace / evidence-logging as first-class** — trajectory summarization + multi-dimension competency scoring (A40210) maps onto the trace console; interaction+video logs as audit evidence (A42249).
- **Treat routing metadata and intermediate activations as sensitive assets** — split/offloaded inference leaks input via activations (A40100) and via expert-selection access patterns (A39721); prefer forward-activation perturbation over gradient noise (A40100).
- **Multi-party / threshold authorization for model execution** (A40925) — "no single party (or thief) can activate the model."
- **Layered multi-agent runtime defense** — per-agent monitoring + system-level anomaly detection + reputation-based isolation + privacy-preserving adaptation (A41065), with the reviewer caveat that its evidence is task-accuracy, not measured attack-success.
- **Detectors are noisy triage aids, not gates** — real-world vuln-detection F1 ≈0.3–0.6 (A42369); LLM security outputs need corroboration and human review (A36959, A40815).
- **Egress/DLP monitoring must assume covert channels invisible at text/pixel layer** (A37125, A40903) → shift to model/provenance attestation and anomalous-fine-tuning monitoring.
- **LLM-judge components need their own calibration + anti-gaming controls** (A36959, A40210).

## 10. Open problems
- **Adaptive/adversarial robustness of essentially every detector in this chunk** — untested (§1, §7).
- **Formal privacy guarantees** — A40100's noise is empirical (no reported ε); A39721 covers only semi-honest, not malicious, adversaries; neither addresses membership inference / model extraction by an accumulating client.
- **Byzantine-robust aggregation vs poisoning** in FL multi-agent settings (A41065: HE hides updates but does not prevent poisoning; honest-majority assumption unverified against Sybil/collusion).
- **Deployable prompt-injection defenses for agents** — A42239 proposes none; A42249's hardened architecture is unbuilt/unevaluated.
- **Reliable security-dataset ground truth** — NVD/tool-consensus/self-generated labels are noisy (A36976, A37021, A40815, A42369).
- **Model-level / adaptive steganalysis** for content-preserving covert channels (A40903).
- **Equilibrium tractability + defender-AI integrity** for AI-vs-AI deception (A42318 — unbuilt; defender LLM is itself an injection/poisoning surface).
- **Adaptive gradient-based activation attacks** against learned access-control triggers (A40925 residual Acc-Fusion unclosed).

## 11. Most load-bearing papers (for an agent-security stack)
1. **A42249 — computer-use-agent security eval.** Cleanest empirical grounding for "capability ≠ permission," least-privilege gating, human approval on consequential actions, and hallucinated-completion as a monitorable failure. (Preliminary / small-n; version-bound numbers.)
2. **A42239 — malicious MCQ option injection.** Demonstrates that *any* model-visible field is an injection surface and motivates an environment-side validity gate / action allow-list. (Preliminary; single model.)
3. **A40210 — offensive CTF agents.** Establishes trajectory-level (not pass/fail) evaluation, dual-use capability measurement, decoding-hyperparameter sensitivity, and LLM-judge-needs-calibration — directly informs autonomy-trace + eval-harness design. (Moderate.)
4. **A42369 — VulnBench.** The evaluation-integrity anchor: threshold selection, class imbalance, and dataset leakage separate genuine capability from artifact; real-world detector F1 is modest — so detectors are triage aids, not gates. (Moderate.)
5. **A41065 — multi-agent LLM resilience.** The most complete *architecture* for layered runtime defense (monitoring + reputation isolation + FL-with-HE), useful as a design template with the caveat that its security evidence is weak (task-accuracy, no measured attack-success). (Moderate.)
6. **A40100 + A39721 (privacy pair).** Show that offloaded/split inference leaks input via activations (A40100 collusion inversion) and via routing access patterns (A39721) — intermediate state is a first-class confidentiality asset in any multi-tenant agent-hosting design. (Moderate.)
