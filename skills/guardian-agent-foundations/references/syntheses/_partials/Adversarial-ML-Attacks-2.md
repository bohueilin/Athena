# Adversarial-ML-Attacks — Partial Synthesis (chunk 2 of 40 papers)

Scope: AAAI-26 "Adversarial-ML-Attacks" category, 40 research cards (A39604, A39668, A39725,
A39747, A39752, A39778, A39803, A39809, A39935, A39954, A39997, A40051, A40054, A40176, A40224,
A40272, A40295, A40301, A40353, A40366, A40409, A40445, A40447, A40486, A40570, A40584, A40587,
A40726, A40787, A40833, A40842, A40846, A40849, A40854, A40855, A40859, A40867, A40876, A40877,
A40878).

Evidence-integrity note: every claim below traces to a specific card. Numeric values are **author-reported**
(many result tables were truncated in the extracts and are flagged as such on the cards). "Reviewer synthesis"
marks cross-paper inference by the card authors or this synthesis, not paper claims. Calibrated language is used:
findings hold "under the evaluated threat model / against the tested attacks," not as guarantees. A recurring
data-integrity caveat across ~10 cards: the corpus manifest's arXiv IDs are frequently **mis-extracted citation
IDs**, not the paper's own identifier (flagged on A39668, A39725, A39747, A39803, A40176, A40224, A40272,
A40295, A40301) — do not trust manifest arXiv IDs for these.

## Composition of this chunk
Roughly balanced attack/defense mix. **Attack papers** (~24): A39604, A39668, A39725, A39747, A39809,
A39935, A39997, A40176, A40224, A40295, A40353, A40409, A40445, A40486, A40587, A40726, A40787,
A40833, A40842, A40846, A40849, A40855, A40878 (and A40054 contributes both). **Defense papers** (~15):
A39752, A39778, A39803, A39954, A40051, A40054, A40272, A40301, A40366, A40447, A40570, A40584,
A40854, A40859, A40867, A40876, A40877. Note: several are filed under "Adversarial-ML-Attacks" but are
defenses (cards flag the category mismatch, e.g., A39752, A39778, A39803, A39954, A40051).

Agent-security centrality (reviewer synthesis, per cards): **core** — A40353 (agentic RAG poisoning),
A40224 (LLM-MAS message tampering), A40295 (persistent LLM backdoor), A40570 (open-weight tamper-resistance),
A40445 / A40486 / A40833 (LLM/LRM availability + indirect injection), A40726 (multimodal-RAG MIA),
A40867 (MLLM backdoor purification), A40876 (RAG embedding inversion). **Adjacent/peripheral** — the graph/GNN,
federated-learning, recommender, audio, sensor, LiDAR, and 6DoF-pose papers (transferable lessons, non-LLM victims).

## Dominant threat models
1. **Training-time / supply-chain injection (poisoning & backdoors).** The largest cluster. Adversary controls
   data, a component, or the pre-release model, and the victim later trusts/deploys it: node injection on
   LLM-enhanced GNNs (A39604), graph-structure poisoning (A39668), clean-image label poisoning (A39935),
   DRL component/post-training backdoors (A39809), persistent LLM backdoors that ride downstream fine-tuning
   (A40295), rationalization-model backdoors (A40409), CoT "overthinking" backdoors (A40486), federated-LLM
   knowledge editing (A40787), physical LiDAR backdoors (A40842), 6DoF-pose backdoors (A40855), MLLM
   fine-tune backdoors (A40867 attack side). Recurring premise: victims cannot audit provenance of weights,
   components, labels, or datasets.
2. **Federated-learning insider / malicious participant.** A39725 (retaliation via unlearning leakage),
   A39778 (backdoor under domain skew), A40051 (federated graph backdoor), A40787 (FedIT knowledge edit),
   A40859 (vertical-FL backdoor with label knowledge), A40878 (graph-VFL dominating input + reward gaming).
3. **Black-box inference-time attacks against deployed services.** Evasion, membership inference, and resource
   exhaustion via API/query access: A40176 (MARL observation perturbation), A40353 (KB injection),
   A40445 / A40833 (energy-latency / reasoning-extension DoS), A40587 / A40726 / A40846 (membership inference),
   A40849 (audio transfer evasion), A40877 (geo-privacy), A40878 (GVFL surrogate attack).
4. **Privacy inference / reconstruction.** Membership inference (A40587 white-box, A40726 black-box multimodal
   RAG, A40846 recommender), embedding inversion (A40876), attribute/geo inference (A39752, A40447, A40877),
   visual-concept retention (A40272), and unlearning-induced leakage/reconstruction (A39725).
5. **Availability / economic-DoS on reasoning LLMs.** A distinct emerging model: A40445 (repetitive generation),
   A40486 (triggered CoT verbosity), A40833 (poly-base reasoning extension) all inflate compute/latency while
   preserving output correctness — invisible to accuracy-only QA.
6. **Machine-unlearning interface as dual-use surface.** A39725, A39747, and A40272 treat "forget/delete my
   data" as a security-relevant action that can leak, be abused for anti-forensic backdoor revocation, or
   cause collateral forgetting — a cross-cutting lesson for any "revoke" capability in agentic data systems.

## Major attack families
- **Backdoors** (dominant): clean-label (A39935, A39747), component/post-training (A39809), fine-tune-persistent
  (A40295, A40409, A40486, A40867), physical/3D-trigger (A40842, A40855), VFL (A40859 attack side). Recurring
  design goal: high attack-success-rate (ASR) with negligible clean-accuracy drop, defeating accuracy-only
  acceptance testing.
- **Data / graph / corpus poisoning:** A39604 (node injection), A39668 (edge perturbation), A40353 (RAG
  sub-claim poisoning), A40787 (federated knowledge edit), A40854 (citation shilling — attack side), A40878.
- **Membership inference / inversion / attribute inference:** A40587 (gradient-norm + robustness signals),
  A40726 (cross-modal image-membership from text), A40846 (relative-metric MIA on hybrid recommenders),
  A40876 (embedding inversion — defended against), A39725 (unlearning-induced MIA + reconstruction).
- **Evasion / adversarial examples & transferability:** A40176 (MARL observations), A40849 (audio ASR/ASV/KWS
  transfer booster), A40878 (dominating GVFL input); the AT papers A39954 / A40054 / A40301 defend this class.
- **Agentic / multi-agent subversion:** A40224 (man-in-the-middle inter-agent message tampering), A40353
  (mirror the agent's own task decomposition + exploit its justifications), A40176 (adaptive single-agent
  selection in MARL).
- **Availability / resource exhaustion (DoS):** A40445, A40486, A40833.
- **Provenance / watermark manipulation:** A39997 (overwrite neural audio watermarks to hijack ownership).
- **Model extraction / surrogate-driven:** A40878 (out-of-domain surrogate of a proprietary server model),
  A40176 (imitation-learned proxies for white-box gradients), A39997 (gray-box surrogate embedders).

## Major defense families
- **Adversarial training / robust optimization:** A39954 (game-theoretic sample re-grouping), A40054
  (per-modality vulnerability-aware AT), A40570 (bi-level tamper-resistance for open-weight LLMs against
  malicious fine-tuning).
- **Detection of adversarial/backdoor inputs & samples:** A39803 (embedding-stability probe for adversarial
  text), A40301 (embedding-manifold OOD-detect-and-correct), A40366 (Mahalanobis + spectral fusion detector),
  A40867 (attention-hijacking localization), A40584 (SAE + causal feature identification for reward hacking),
  A40859 (embedding clustering + dual-model loss-difference).
- **Purification / backdoor removal:** A40051 (server-side multi-teacher distillation), A40366 (LoRA
  distillation-unlearning), A40867 (test-time token zeroing), A40272 (adversarial unlearning of a visual concept).
- **Capability isolation / least privilege in multi-party training:** A39778 ("don't aggregate the component
  that can carry the attack" — share only a low-capacity style module), A40859 (defend on observable interface
  artifacts when participant models are inaccessible).
- **Privacy-preserving transformations:** A39752 (real-time on-device sensor perturbation), A40447 (client-side
  prompt desensitization), A40876 (mutual-information-optimized embedding obfuscation), A40877 (pre-sharing
  image perturbation vs VLM geolocation).
- **Robust recommendation via provenance-weighted metric:** A40854 (reshape the distance metric so injected
  nodes have less influence, rather than detecting them).

## Strongest / most-replicated findings
- **Static, non-adaptive defenses repeatedly fail; adaptive testing is the missing axis.** Nearly every card —
  attack and defense alike — notes that no defense-aware adversary was evaluated. Attack cards demonstrate
  evasion only against fixed defenses (A40353 vs PPL/paraphrase/clustering; A40787 vs 8 robust aggregators;
  A40224 vs an LLM message inspector; A39935 vs STRIP/Neural-Cleanse/ABL; A39668 transfers vs robust GNNs;
  A39809 evades BIRD/SHINE), and defense cards concede adaptive robustness is unproven (A39803, A40301, A40570,
  A40867, A40876). Reviewer synthesis: this chunk's central methodological gap.
- **Fine-tuning / retraining does not reliably remove implanted behavior.** A39809 (compromised component
  re-injects after retraining), A40295 (clean fine-tuning *reinforces* a gradient-aligned backdoor;
  forgetting-mitigation methods *amplify* persistence), A40855 (fine-tuning shifts but does not remove the
  pose-offset backdoor). Direct implication: provenance/attestation, not adaptation, is the control.
- **Backdoors can preserve clean accuracy (and even plausible rationales / correct answers), defeating
  accuracy-only QA.** A39935 (≤1% clean-accuracy drop at ≤0.5% poison, author-reported), A40409 (interpretable
  rationale preserved), A40486 (answers stay correct while reasoning length inflates ~17× on MATH-500,
  author-reported), A40867 (clean capability retained in shallow layers). Monitoring must move beyond output
  accuracy to representation-, length-, and provenance-level signals.
- **Agentic structure is not automatically protective.** A40353 shows claim-decomposition + cross-aggregation
  blunts *naive* RAG poisoning but is defeated by an attacker who mirrors the decomposition and exploits the
  system's own justifications (author-reported 8–16× poison-budget reduction, effective at ~0.1% poison). A40787
  shows robust aggregation is insufficient for knowledge-integrity. A40878 shows a proprietary server model is
  not a security boundary (surrogate built from out-of-domain data).
- **The unlearning / "right-to-be-forgotten" interface is a genuine attack surface**, not only a compliance
  feature (A39725 leakage+retaliation; A39747 anti-forensic revocation; A40272 collateral forgetting of
  neighboring concepts). Behavioral non-recall ≠ provable removal (reviewer synthesis on A40272).
- **Reasoning/inference compute is an availability attack surface.** Three independent papers (A40445, A40486,
  A40833) weaponize output length / reasoning length while keeping answers correct — a coherent, novel
  economic-DoS theme for LLM/LRM serving.
- **"Security through obscurity" of model weights is fragile.** A39997 (surrogate watermark embedders converge
  to similar strategies → near-100% overwrite ASR across white/gray/black-box, author-reported) and A40878
  (out-of-domain surrogate of a proprietary model) both undercut weight-secrecy as a defense.

## Conflicting / in-tension findings
- **Capability isolation "works" vs "untested against adaptive attackers."** A39778 and A40859 report strong
  ASR reduction from architectural isolation, but both cards flag that an attacker shaping updates to the shared
  component / to enlarge intra-cluster distance was not evaluated — so the claims are bounded to known attacks.
  No paper directly refutes them; the tension is claim-strength, not contradiction.
- **Unlearning as reliable removal vs unlearning as leaky/abusable.** A40272 argues precise behavioral
  forgetting is achievable; A39725/A39747 argue the unlearning event itself leaks membership and can be abused.
  Reviewer synthesis: not contradictory (different objectives) but jointly caution that "delete" operations are
  security-sensitive and behavioral metrics are insufficient evidence of removal.
- **Verifier/reward signals are trustworthy vs game-able.** A40584 shows Process Reward Models assign high
  scores to logically invalid steps via stylistic confounders (an illustrative impossible constraint scored
  0.973, author-reported) — a caution against trusting verifier/judge scores that other agentic pipelines rely on.
- **DP as privacy defense: partial only.** A40846 reports DP yields only a slight ASR decrease against the
  relative-metric MIA (author-reported); A40587's threat is untested against DP-SGD entirely. No paper in this
  chunk validates a strong privacy guarantee; all privacy defenses here are empirical (no formal DP guarantee in
  A39752, A40447, A40876, A40877).

## Documented defense bypasses (attacks defeating specific evaluated defenses)
- A40353 Fact2Fiction evades paraphrasing, K-means clustering detection, and perplexity filtering (author-reported).
- A40787 ShadeEdit evades 8 robust aggregators (FedAvg, Multi-Krum, Median, Trimmed-Mean, CRFL, RFLBAT, FLAME,
  SFed variants) at ~99.5% average ASR (author-reported); counterfactual edits partly reversible by clean
  fine-tuning, **bias edits persist** (>80% counterfactual drop vs strong bias persistence, author-reported).
- A40224 MAST evades a three-criteria LLM "Tamper Defender" via semantic+embedding similarity constraints.
- A39935 GCB resists STRIP, Neural Cleanse, Fine-Pruning, ABL, and label-cleaning ("most, not all" defenses —
  author hedge).
- A39668 MetaDist transfers against robust-GNN defenses (non-adaptive).
- A39809 TrojanentRL survives retraining-based defenses; InfrectroRL evades BIRD and SHINE.
- A40855 6DAttack survives a clean-fine-tuning defense (residual offset persists — honest negative reported).
- A40833 ExtendAttack argues pattern-matching purification and perplexity filtering are brittle (conceptual,
  not a full defender-vs-attacker study).
- A40295 P-Trojan persists through worst-case clean "Cleanup SFT" and cross-task fine-tuning (against benign,
  not backdoor-aware, fine-tuning).

## Benchmark / evaluation limitations (recurring)
- **Truncated result tables.** Many extracts cut the main results; headline numbers are read from abstracts/intros
  and tagged as author claims (A39604, A39668, A39747, A40176, A40224, A40295, A40301, A40584, A40587, A40846,
  A40854, A40878, and others). Effect sizes cannot be independently verified from the cards.
- **Non-adaptive defenders** in essentially all evaluations (see above).
- **Narrow scale / scope.** OR-MIA capped at 6B (A40587); AT-Field single ResNet-18 on 3 small datasets with
  marginal AutoAttack deltas (A39954); VARMAT single HighMMT backbone (A40054); AUVIC single LLaVA-1.5 + ~6–8
  concepts (A40272); watermarking only 3 systems / speech (A39997); Fact2Fiction 2 victim systems / 1 benchmark
  (A40353).
- **Commercial-model version drift** makes results snapshot-dependent (A40445, A40726, A40833, A40877).
- **Manifest arXiv-ID mis-extraction** (data-integrity issue, see top note).
- **Proxy metrics.** Output length as an energy/latency proxy without wall-clock energy (A40445); behavioral
  non-recall as an unlearning proxy without membership-inference/relearning audits (A40272).

## Recurring implementation patterns (method-level)
- **Bi-level / min-max optimization with a differentiable proxy** to avoid intractable nested fine-tuning:
  A40570 (adversarial hypernetwork generating LoRA attack patches), A39747 (inject↔unlearn simulation with
  PCGrad), A39668 (teacher/student distillation attack).
- **GCG-style discrete token/suffix search:** A40295 (gradient-alignment trigger), A40445 (repetition-inducing
  suffix), lineage cited by A40447.
- **LoRA-based injection or purification:** A40272, A40366, A40570, A40787, A40867 — parameter-efficient both for
  attackers (cheap injection) and defenders (cheap purification without retraining).
- **Representation/attention-level analysis as the signal:** A39803 (masking-induced embedding sensitivity),
  A40301 (manifold OOD likelihood), A40366 (Mahalanobis + spectral signature), A40867 (hierarchical attention
  hijacking), A40584 (SAE features), A40587 (middle-layer gradient norms).
- **Distillation-based unlearning/purification:** A40051, A40366.
- **Surrogate/proxy + ensemble for black-box transfer:** A40176, A40849 (multi-shuffle gradient fusion), A40878
  (domain-adversarial surrogate), A39997 (surrogate embedders), A40877 (surrogate encoder ensembles). Exception:
  A39604 deliberately avoids surrogates (gradient-free evolutionary search on non-differentiable LLM features).
- **Multi-round planning for stealthy agentic attacks:** A40224 (MCTS → step-level DPO), A40353 (Planner/Executor
  agents mirroring the victim).

## Product / architecture implications (reviewer synthesis, grounded in cards)
- **Provenance & attestation as the primary control** for model weights, reused components, datasets, labels, and
  retrieval corpora — because retraining/fine-tuning does not remove backdoors (A39809, A40295, A40855) and
  accuracy metrics do not reveal them (A39935, A40409, A40486, A40867). Retain forensic snapshots *before*
  honoring unlearning/delete requests (A39747).
- **Runtime monitoring keyed to the right signal**, not output accuracy: per-request output-length/entropy and
  reasoning-token telemetry for DoS (A40445, A40486, A40833); deep-layer attention concentration for MLLM
  backdoors (A40867); Mahalanobis/spectral or manifold-likelihood scores for adversarial inputs (A40366, A40301);
  full inter-agent transcripts with per-message provenance for MAS (A40224); retrieval-evidence provenance and
  injection-cluster patterns for RAG (A40353).
- **Authenticated, integrity-checked channels for agent-to-agent communication** — A40224's MITM premise is
  directly negated by message signing / mutual auth; content-only trust is unsafe.
- **Retrieval-corpus trust scoring, provenance, and isolation for RAG** (A40353, A40726, A40876); treat open-web
  KBs as attacker-writable and minimize/sanitize exposed justifications (transparency–security trade-off, A40353).
- **Reasoning-token budgets / hard ceilings independent of prompt-controlled instructions** for LRM serving
  (A40445, A40486, A40833); indirect prompt-injection variant means retrieved context must be sanitized before it
  enters a reasoning model (A40833).
- **Least-privilege / capability isolation and interface-artifact-only defense in multi-party training**
  (A39778, A40859) — bound any single party's influence rather than relying on server-model secrecy (A40878).
- **Client-side privacy shims** at data/prompt/image egress (A39752, A40447, A40877) and embedding-serving
  obfuscation before vector-store writes (A40876) — all empirical, not guarantees; embedding stores remain
  sensitive (up to ~5% tokens recoverable, author-reported for A40876).
- **Query monitoring / rate limiting** against membership-inference and watermark-overwrite try-and-test loops
  (A40587, A40726, A40846, A39997).
- **Tamper-resistance-by-design before open-weight release** (A40570) as risk-reduction (author-reported up to
  27.4% more robust / 78% harmful-score reduction / <0.5% utility loss) — explicitly a proxy for an intractable
  min-max, not a guarantee.

## Open problems
- Adaptive, defense-aware attackers are essentially untested across the chunk → residual risk unknown for every
  defense here.
- Formal guarantees vs empirical robustness: no defense in this chunk offers certified robustness; privacy
  defenses provide no formal DP guarantee.
- Verifiable unlearning: behavioral non-recall is not proof of removal; relearning/extraction audits are absent
  (A40272), while the unlearning interface is simultaneously leaky and abusable (A39725, A39747).
- Cross-modal / semantic / global triggers and true over-the-air physical realizability remain under-demonstrated
  (A40842, A40855, A40867, A40176).
- Verifier/reward-model robustness (A40584) and its interaction with agentic best-of-N / judge pipelines.
- Scaling attacks/defenses to frontier-scale and to genuinely black-box production models (A40587, A40570).

## Most load-bearing papers (this chunk)
1. **A40353 Fact2Fiction** — the best-substantiated and most agent-central paper (card rates evidence *strong*):
   targeted, black-box, decomposition-aware poisoning of *agentic* fact-checking/RAG that exploits the system's
   own justifications and evades three defenses; released code + external arXiv ID. Establishes that agentic
   decomposition is not self-protective.
2. **A40295 P-Trojan** — pre-release LLM backdoor engineered so ordinary clean fine-tuning *reinforces* it
   (gradient alignment; theory + author-reported >99% persistence). Core supply-chain / safety-bypass result.
3. **A40224 MAST** — reframes the inter-agent *message bus* as a first-class attack surface (MITM tampering,
   MCTS+DPO planning under stealth constraints). Core agent-to-agent security.
4. **A40570 AntiDote** — the strongest *defense* contribution: efficient tamper-resistance for open-weight LLMs
   against malicious fine-tuning via a differentiable hypernetwork proxy; 10 models (0.6B–27B) × 52-attack suite.
   Calibrated as reduction, not proof.
5. **A40833 ExtendAttack** — black-box resource-depletion on reasoning LLMs (including o3) that *preserves answer
   accuracy* and works via *indirect prompt injection* — a clean intersection of DoS + injection for LRM serving.
6. **A40867 PurMM** — a deployable, no-retraining test-time backdoor-purification mechanism for MLLM agents,
   grounded in a novel mechanistic finding (hierarchical deep-layer attention hijacking). Runtime-enforcement
   primitive at the model-serving boundary.

Honorable mentions: A40445 / A40486 (the availability-attack pair completing the DoS theme), A39809 (supply-chain
DRL-backdoor threat-model contribution), A40726 / A40876 (RAG confidentiality: membership inference + embedding
inversion).
