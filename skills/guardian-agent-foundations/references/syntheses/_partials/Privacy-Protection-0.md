# Privacy-Protection — Partial Synthesis (chunk 0, 40 papers)

Scope: research cards A37135, A37244, A37284, A37472, A37499, A37551, A37735, A37743, A37748, A37854, A37930, A37979, A38004, A38016, A38021, A38130, A38196, A38297, A38773, A39038, A39051, A39210, A39212, A39307, A39311, A39333, A39338, A39373, A39381, A39431, A39496, A39502, A39510, A39524, A39582, A39671, A39681, A39710, A39750, A39895. All AAAI-26 papers. Claims below trace to the individual cards; reviewer synthesis is marked as such. Calibrated language throughout — findings hold only "under the evaluated threat model."

## 0. Composition of the chunk (evidence-integrity caveat)

This "Privacy-Protection" folder is heterogeneous, and several cards flag their own paper as mis-filed. Roughly three tiers:

- **Genuine privacy/security contributions (~26):** DP mechanisms and analysis (A39051, A39510, A37854, A38016, A39710, A39311, A39582), machine unlearning + deletion evaluation (A37499, A38196, A39038, A39373, A39431, A39750, A39895, A39681), gradient/data-reconstruction attacks (A37743, A39333), split-inference defense (A39212), MPC/secret-sharing (A38773, A39210), cryptographic private-inference efficiency (A39502), steganographic covert-channel inference (A37284), model IP protection / extraction (A39496, A39671), provenance/attribution/auditing (A37135, A37735, A37930).
- **Privacy-motivated but privacy-unevaluated (~3):** federated methods whose "privacy" is data-minimization-by-architecture with no threat model or attack (A39307, A39524, A39338; also the informal-synthesis paper A38021).
- **Explicitly off-topic / mis-categorized (~8):** pure computer-vision/graphics reconstruction or efficiency papers with no adversary, asset, or threat model — A37244 (driving-VLA token pruning), A37472 (EEG-to-video decoding; reviewer flags dual-use privacy *threat*, not a defense), A37551 (video grounding), A37748 (MRI reconstruction), A37979 (slender-structure 3D), A38004 (dynamic-scene NVS; its "noise injection" is a regularizer, explicitly *not* differential privacy), A38130 (semi-transparent surface reconstruction), A38297 (hyperspectral reconstruction). These should not be cited for any privacy/security claim.

Reviewer synthesis: the folder label alone is not evidence of a privacy mechanism; each card had to be read to separate real defenses from category artifacts. A recurring trap is conflating "noise injection" (generalization regularizer, e.g. A38004) or "data locality" (A39338, A39524) with a privacy guarantee.

## 1. Dominant threat models

Five recur across the genuine-privacy papers:

1. **Honest-but-curious / semi-honest server or party** (most common) — federated, split, MPC, and clustering settings: A39210 (semi-honest 2PC), A39212 (honest-but-curious server running data-reconstruction attacks with surrogate knowledge), A38773 (semi-honest servers, honest-majority), A39311 / A39582 (semi-honest/untrusted server under DP), A39038 (honest server). Malicious/colluding servers are almost universally out of scope.
2. **Formal DP worst-case adversary** — information-theoretic, adaptive-safe by construction, unbounded auxiliary knowledge, per-record adjacency: A39051, A39510, A37854, A38016, A39710, A39311, A39582. These papers argue privacy from the (ε,δ)/ε/µ-GDP guarantee rather than from an executed attack.
3. **Membership-inference verifier as the privacy oracle for unlearning** — MIA (and MIA-gap to a retrain oracle) is the standard, and nearly always *non-adaptive*, instrument: A37499, A38196, A39038, A39895, A39510, A38016.
4. **Gradient-interception attacker in federated learning** — honest-but-curious server or eavesdropper reading per-client (pre-aggregation) updates: A37743, A39333. Both target the *training* path.
5. **Model-confidentiality / IP-theft adversary** — model extraction from a query API (A39671) or unauthorized execution of publicly-released weights (A39496). Here the protected asset is `model_weights`/`ip`, not user data.

A sixth pattern is the **non-adversarial "target under audit"**: A37135 (a possibly non-compliant app), A37735 (an infringing model), A37930 (a generator whose outputs are attributed) — no active, adapting attacker is modeled.

## 2. Major attack families

- **Gradient inversion / training-data reconstruction from FL gradients** (A37743 GGSS-R, A39333 Venom). Both reconstruct client images from *noise-perturbed / DP* gradients; A39333 does so analytically without knowing the noise distribution, A37743 uses a generic (unaligned) diffusion prior. This is the chunk's strongest attack signal (see §4).
- **Data-reconstruction attacks (DRAs) in split inference** (A39212) — invert smashed intermediate representations back to the raw input, worst when the client-side "bottom" model is shallow.
- **Membership inference** — pervasive as an *evaluation* probe rather than a headline attack (A37499, A38196, A39038, A39895, A39510, A38016).
- **Model extraction / stealing** (A39671) — encoder reconstructed offline for free (random init inductively, self-supervised transductively), only a lightweight head needs victim labels; ~100 queries vs ~5,000 for prior SOTA.
- **Verifier gaming / evaluation attack** (A39373) — "Head Distillation" satisfies black-box unlearning metrics (MIA/JSD) while leaving the encoder — and all residual forget-set information — identical to the original.
- **Data-poisoning weaponizing the unlearning-request channel** (A39895 DPA) — malicious clients issue deletion requests to damage similar-data victims; unfair forgetting is itself the vulnerability.
- **Oracle-guided key-recovery** against hardware model-locking (A39496) — approximate attacks flip/mute outlier neurons and enumerate permutations to approximate the oracle.

## 3. Major defense families

- **Differential privacy.** Central DP with formal accounting: A39051 (LP with a truncated/one-sided-tightening Laplace mechanism that *guarantees original-constraint feasibility*), A39510 (tight hidden-state RDP for smooth non-convex losses), A37854 (µ-GDP dataset distillation exploiting post-processing), A38016 (DP-SGD synthesis + noise-tolerance pre-training), A39710 (ε-DP + Nash-regret bandits). Local DP: A39582, A39381 (utility recovery atop LDP). ε-DP on prototypes: A39311.
- **Machine unlearning / deletion.** A37499 (CUPID, disentangle causal vs bias pathways), A38196 (PeriUn, forget only low-confidence peripheral samples), A39038 (PAGE, federated-graph residual-permeation removal), A39431 (DIET, retain-data-free VLM concept removal via hyperbolic geometry), A39750 (GFOES, few-shot zero-glance via synthetic erasure samples), A39895 (FedShard, exact sharded federated unlearning), plus the *evaluation* of unlearning (A39373 IDI) and the *repurposing* of unlearning for fairness/robustness (A39681).
- **Cryptographic MPC / secret sharing.** A38773 (private cake-cutting, honest-majority Shamir sharing; re-architect leaky dynamic-graph artifacts into oblivious fixed-structure form), A39210 (2PC secret-shared secure Boolean matmul + k-anonymous supernodes). A39502 is an efficiency method that *assumes* an underlying crypto-PI protocol.
- **Split-inference information decomposition** (A39212) — strip task-irrelevant/redundant information (frequency-domain + information-bottleneck) *before* adding closed-form noise calibrated to an FSInfo/Fisher metric.
- **Provenance / attribution / detection** — A37930 (training-free double-reconstruction loss-ratio image attribution), A37735 (DP-analog memorization/copyright detection via paired learning/unlearning branches), A37135 (LLM multi-agent privacy-compliance auditing over decompiled code + policy).
- **Model-asset protection** — A39496 (hardware-anchored logic-locking; "activated accelerator = license").
- **Covert-channel confidentiality** — A37284 (hide sensitive video in a cover, analyze in the steganographic domain).
- **Federated-by-architecture data minimization (asserted, not evaluated)** — A39307, A39524, A39338.

## 4. Strongest replicated findings

1. **Heuristic additive noise on gradients is not a robust privacy defense.** Independently demonstrated by two attack papers — A37743 (diffusion-prior inversion of Gaussian/Laplacian-perturbed gradients) and A39333 (analytic, noise-prior-free reconstruction from DP-protected gradients, e.g. LPIPS 0.340 vs 0.632 and ASR 45% vs 2% for the prior SOTA at ε=10, δ=10⁻⁵). The defense-side DP papers agree in spirit: A37854 and A39510 argue the *accounted* DP guarantee — not heuristic perturbation — is the load-bearing property, and A37743's own theory shows noise still raises the reconstruction-error lower bound (so noise has value but is insufficient alone). Convergent design implication across all four: combine secure aggregation + clipping-with-DP-accounting + (optionally) compression, and red-team with a generative-prior attacker.

2. **Behavioral / black-box unlearning metrics understate residual retention.** A39373 shows MIA/JSD parity can be achieved by cosmetic output-layer changes while the encoder still fully encodes the forget set (recoverable to >82% forget-test accuracy by retraining a head on 2% of data, vs ≤41% for a true retrain). A37499 shows standard unlearning under bias erases the *shortcut*, not the class ("shortcut unlearning"). A38196 shows only low-confidence "peripheral" samples actually change under the retrain oracle. Reviewer synthesis: papers claiming "complete forgetting" purely behaviorally (A39431 forget-acc 8.06%; A39750 A_Df=0) are, by their own related-work cards, *not* adversarially verified — a representation-level or relearning/MIA probe is the missing acceptance test.

3. **Formal DP/MPC guarantees are adaptive-safe by construction but only as strong as their accounting and trust boundary.** A39051 (feasibility + sub-optimality theorems), A39510 (RDP + utility bounds), A38773 (perfect security *under honest majority*), A39582/A39311/A39710 (ε-DP). Repeated caveat: the guarantee is worst-case for the *specific* released artifact and trust model — leaking intermediate checkpoints (A39510), a colluding majority (A38773), or un-accounted shared artifacts (A39311 structural graphs; A39582 mass values) voids it.

4. **The privacy–utility trade-off is explicit and dial-tunable.** A single knob recurs and should be logged as configuration-of-record: ε (A39051/A39510/A39582/A39311/A39710), local-DP flip probability (A39381), compression ratio γ (A39210), guidance rate mr (A37743), FSInfo level (A39212), bounded-domain diameter D (A39510). Multiple papers show baseline collapse at strong privacy (A39582 baselines go "NA" at ε<1; A39381 reports 30–60% GPL degradation under perturbation).

## 5. Conflicting / in-tension findings

- **Formal guarantee vs asserted-by-architecture privacy.** A39051/A39510/A38773/A39311/A39582 provide formal DP or MPC; A39307/A39524/A39338 (and informally A38021) assert privacy from "we only share gradients/digests/prototypes" with *no* attack or accounting. The cards themselves stage this as a direct contrast (e.g. A39311 SPP-FGC with ε-DP vs A39307 FedAI with no formal layer; A39210 MPC/k-anonymity vs A39307). Reviewer synthesis: gradient/digest sharing is a documented leakage vector (cf. A37743, A39333), so the asserted-privacy papers are contested as security evidence.
- **"Noise defends" vs "noise fails."** Not a strict contradiction but a live tension: defense papers add noise for privacy; attack papers (A37743, A39333) show noise-only is bypassable; A37743's theory reconciles by showing noise raises but does not eliminate the error bound.
- **Which privacy family to use** — cryptographic MPC (A38773, A39210: strong under honest-majority/semi-honest, communication cost, no graceful degradation past the threshold) vs statistical DP (A39311, A39582: worst-case per-record, composition cost, utility loss) vs metric-privacy (A39212: FSInfo bound, but MSE is a known-imperfect perceptual-privacy proxy). No paper adjudicates; they occupy different trust models.

## 6. Defense bypasses (demonstrated or acknowledged)

- DP/heuristic-noise gradient perturbation → reconstructed by A37743 and A39333.
- Black-box unlearning metrics → gamed by A39373's Head Distillation.
- "Rate-limit + prediction-only" GNN API → bypassed by encoder-free stealing (A39671), which remains effective even with an extraction defense in place.
- Single-reconstruction-loss attribution → collapses to near-chance on SOTA generators like FLUX (A37930's motivating failure of prior work).
- k-anonymity on supernodes → reviewer-flagged weak to linkage/auxiliary-information attacks; no ℓ-diversity/DP layer (A39210).
- Hardware logic-locking → authors acknowledge an unresolved **block-replacement** attack (retrain/replace the protected block rather than recover the key) (A39496).

## 7. Benchmark / evaluation limitations (recurring)

- **Non-adaptive adversaries are near-universal.** Almost no paper evaluates an attacker specifically optimized against its own pipeline (A39212 has surrogate-knowledge but not fully adaptive DRAs; A37854/A38196/A39038/A39895 use fixed MIA; A39496 and A39671 are the notable adaptive/defense-in-place exceptions).
- **MIA as sole privacy oracle** — a single, lower-bound-estimator attack family standing in for "privacy" (A37499, A38196, A39038, A39895, A39510).
- **Privacy asserted but not attacked** — formal-DP papers rely on the guarantee without an executed attack (A39051, A39710, A39582); architecture-privacy papers report only utility (A39307, A39524, A39338, A39381).
- **Behavioral forgetting ≠ deletion** — accuracy/MIA-gap metrics miss representation-level residual (A39373, and by extension the unverified-forgetting caveat on A39431/A39750).
- **Scope confinement** — overwhelmingly vision classifiers / image data; no LLM, generative-model, or agent-memory unlearning is actually validated, though several assert transfer (A37499, A38196, A39373, A39431).
- **Synthetic-only or single-dataset evaluation** (A39051, A39710 synthetic; A37472 single dataset) and **truncated result tables** in many extracted texts (numbers taken from abstract/visible cells; several FedShard/GFOES/DP-NCB figures are OCR-approximate).
- **Underspecified accounting** — DP claimed for the headline artifact but not for every shared object (A39311 structural graphs; A39582 mass values; per-round composition for iterative variants not analyzed).

## 8. Recurring implementation patterns

- **Expose and log the privacy dial** (ε/γ/mr/FSInfo/D) as the configuration-of-record; treat budget-accounting error or budget exhaustion as an incident boundary (A39051, A39510, A39311, A38016, A39710).
- **Post-processing immunity as a budget lever** — route as much computation as possible through already-private (DP-generated) data so it costs zero additional budget (A37854; also A39051 "solving the private LP doesn't weaken privacy").
- **Bounded / one-sided / direction-controlled noise** to preserve hard constraints or valid ranges (A39051 truncated-Laplace tightening for feasibility; A39710 clip-to-[0,1] as safe post-processing).
- **Decompose-then-protect** — strip redundant/task-irrelevant information before adding noise (A39212), coarsen structure into k-anonymous supernodes (A39210), share *structure* not embeddings/raw prototypes (A39311).
- **Oblivious restructuring of leaky artifacts** — replace an input-dependent dynamic graph with a fixed graph + cryptographic edge weights so timing/structure leaks nothing (A38773).
- **Isolate-then-merge sharding** for root-path-local, bounded-blast-radius exact unlearning (A39895).
- **Difference/consistency signals over absolute values** — double-reconstruction *ratio* (A37930), learning-vs-unlearning branch *divergence* (A37735), difference-maximizing adversarial graph as a residual-knowledge probe (A39038) — more robust than a single absolute loss.
- **Cross-batch statistics + EMA smoothing / second-order (Taylor/Fisher) importance** (A39502, A39333, A39681 influence functions).

## 9. Product / architecture implications (for a guardian / agent-security stack)

- **Treat transmitted gradients, submodels, prototypes, digests, and smashed representations as sensitive assets** — assume reconstructable if intercepted (A37743, A39333, A39212). Prefer accounted DP and/or secure aggregation over heuristic noise; never ship raw per-client gradients over untrusted channels (A39333).
- **The decision/policy sequence is itself a leakage channel.** A39710 shows a bandit's arm-selection sequence leaks per-user outcomes even when stored data is protected — relevant to any feedback-driven agentic routing/personalization loop. Protecting data at rest is insufficient.
- **Deletion / right-to-be-forgotten must be verified at the representation level.** Output-only evidence (MIA/accuracy parity) is necessary-but-insufficient; add a residual-information probe (feature MI or head-retraining recoverability) to the acceptance test, keep audit evidence, and re-verify after any output-layer patch (A39373, A37499, A38196).
- **Treat the unlearning-request channel as adversary-controlled** and bound the cross-principal blast radius and cost variance (A39895 — unfair forgetting enables poisoning and cascaded departures).
- **LLM multi-agent tooling over untrusted content is a prompt-injection surface.** A37135 runs LLM agents over decompiled code/strings — attacker-influenced input — without an injection control; reviewer synthesis flags this as an unimplemented gate. Its evidence-linked verdicts (flow/code/policy snippet + reasoning + confidence) are, however, a strong `audit_records` pattern ("traces prove").
- **Model-asset protection is a distinct axis** — serving APIs are extraction targets even with strict rate limits (A39671: detect embedding-guided, centroid-proximal, information-dense small query sets, not just volume); publicly-released weights can be usage-gated via a hardware root-of-trust (A39496), contingent on the tamper-proof key store and "no unauthorized model on the hardware" assumption.
- **Provenance/attribution are governance building blocks but probabilistic evidence, not proof** — A37930/A37735 outputs should gate/triage, not autonomously certify, and are not robust to adaptive evasion (both explicitly out-of-scope for post-processing/memorization-hiding adversaries).

## 10. Open problems

- **Adaptive-attacker-verified, certified deletion for generative / LLM / agent-memory settings** — every unlearning paper here is vision-classifier-scoped and behaviorally (not adversarially) validated (A37499, A38196, A39431, A39750, A39373, A39895).
- **Robust privacy for gradient exchange beyond heuristic noise** — secure aggregation + accounted DP + generative-prior red-teaming, and defenses that survive noise-prior-free analytic attacks (A37743, A39333); most FL efficiency work (A39338) ships gradients/submodels with no such protection.
- **Formal accounting for *all* shared artifacts**, not just the headline object (A39311 structural graphs, A39582 masses, A39307 digests).
- **Malicious (not just semi-honest) adversaries, collusion, and malicious-server-holding-caches** — universally deferred (A38773, A39210, A39038, A39895, A39212).
- **Black-box / API-only forensic detection** — A37735 memorization detection is white-box-only; litigation-realistic settings are black-box.
- **Adaptive-evasion-robust provenance/attribution** (A37930, A37735) and **surrogate-distillation / block-replacement-robust model locking** (A39496).

## 11. Most load-bearing papers (by id)

- **A39333 (Venom)** and **A37743 (GGSS-R)** — jointly the load-bearing "heuristic-noise / DP gradient perturbation is bypassable" evidence; independent methods (analytic vs diffusion-prior), same conclusion. A37743 also contributes the reusable Reconstruction-Vulnerability (RV) architecture-audit metric.
- **A39373 (IDI)** — reframes how deletion must be evaluated: black-box metrics are gameable (Head Distillation), residual information persists in intermediate layers; supplies a representation-level metric. Directly shapes any RTBF/safety-forgetting acceptance test.
- **A39510 (improved DP-SGD analysis)** — the "formal DP done right" anchor: tight hidden-state RDP + utility bounds under only smoothness, with the load-bearing operational caveat that the tighter guarantee dies if intermediate checkpoints leak.
- **A39671 (On Stealing GNNs)** — strong, realistic model-extraction threat under hard query caps and prediction-only outputs; defeats the "rate-limit + withhold-embeddings" defense, relevant to any encoder–head serving API.
- **A39051 (DP Linear Programming)** — the strongest formal contribution in-chunk: DP that *guarantees* original-constraint feasibility via one-sided-tightening truncated-Laplace noise; canonical pattern for "DP must coexist with hard safety constraints."

Secondary but agent-relevant: **A37135 (PriAgent)** as the only genuinely *agentic* (multi-agent, RAG, tool-use) system, whose untrusted-decompiled-input injection surface and evidence-linked audit trail transfer directly to guardian-agent design.
