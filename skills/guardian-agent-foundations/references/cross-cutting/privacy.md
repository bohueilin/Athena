# Cross-Cutting Chapter — Privacy

**What this chapter is.** A cross-paper reading of privacy across the AAAI-26 corpus, organized by *threat thread* rather than by paper. The claims emerge only when the papers are read together: the same conclusion (approximate privacy leaves an adversarially recoverable residue; model-derived artifacts are secrets, not opaque tokens) is reached independently by attack papers, unlearning-evaluation papers, and formal-guarantee papers that never cite each other.

**Sources and provenance.** Primary source is the `Privacy-Protection` category synthesis (73 AAAI-26 papers). Threads that straddle categories (membership inference, model/embedding inversion, federated learning, retrieval/log leakage) additionally draw on the `Adversarial-ML-Attacks` and `AILLM-Safety` category syntheses (same AAAI-26 corpus, different folder). Every paper id below is an internal `Axxxxx` card id, not a manifest arXiv id (the underlying corpus flags manifest ids as frequently mis-extracted).

**Evidence integrity (non-negotiable, applied throughout).**
- Numbers are **author-reported** unless explicitly marked otherwise. Several underlying result tables are flagged **truncated / OCR-approximate** in the source cards; those are recorded as *author-stated, not reviewer-verified* and I repeat that flag inline.
- **Direct paper finding** = a result the paper's own authors report. **Reviewer synthesis** = cross-paper inference added during review (mine or the underlying synthesis's). I mark the boundary at each use.
- Cross-category numbers (e.g. from the Adversarial-ML-Attacks synthesis) are labelled *"author-reported per the [category] synthesis"* because I am one indirection removed from the paper.
- No absolutes. I use *"demonstrated under the evaluated threat model," "reduced ASR against the tested attacks," "not evaluated against," "requires production validation."* Where a value was absent, I write **"not stated in paper."**

**Mapping legend (applied per thread).** Each thread closes with a mapping to the guardian-agent control frame — the throughline is *"capability is not permission":*
- **Capability (C)** — what a model, artifact, or adversary can technically do.
- **Permission (P)** — the authorization / policy gate that must stand between a capability and an egress or action.
- **Verification (V)** — the *executed* test that confirms a claimed privacy property (not a formal statement alone).
- **Evidence (E)** — the auditable, logged record: privacy dial as configuration-of-record, certificates, tamper-evident logs.
- **Residual-risk (R)** — the leakage that remains after the control and must be disclosed.

---

## Thread 1 — Membership inference (MIA)

**Well-established.** MIA is the corpus's workhorse privacy *oracle*: the default probe for both unlearning completeness and prompt/artifact leakage (A37499, A38196, A39038, A39895, A39510, A38016 all use fixed MIA as their privacy metric — direct paper findings). The load-bearing cross-cutting result is that membership signal survives *output suppression*: A40839 (PIPRA) infers training-set membership from soft prompts with **no output access at all** (author-reported avg AUC 87.58% vs 77.05% for output-dependent baselines; 90.37% accuracy on Caltech101 — single-setting, author-reported). Cross-category corroboration that membership leaks through channels other than confidence scores: hard-label-API membership via an iteration-count-to-craft-an-AE signal (A40912 IMIA), white-box gradient-norm + robustness MIA (A40587 OR-MIA, capped at 6B), and cross-modal image-membership inference on multimodal RAG from text alone (A40726) — all author-reported per the Adversarial-ML-Attacks synthesis.

**Emerging.** *Former*-membership inference: even after a deletion operation, a single black-box query detects the "was-a-member" imprint (A40047 FMIA, AUC reported "up to ~0.9+" but with **cells truncated** — author-stated, not reviewer-verified). And the *unlearning event itself amplifies* membership leakage (A38134 dual-view unlearning-verification; A38576 unlearning-amplified MIA on graph encoders; A39725 unlearning-induced MIA + reconstruction — cross-category, reviewer synthesis that deletion is a leakage trigger, not only a leakage remedy).

**Contested.** MIA numbers cut *both ways* as evidence and the field has no settled operating point. On one side, behavioral MIA parity *understates* leakage: A39373 (IDI) achieves black-box MIA/JSD parity with cosmetic output changes while the encoder still fully encodes the forget set. On the other side, cross-corpus MIA *overstates* leakage: A39276 (rethinking CLIP MIA) shows distribution mismatch inflates AUC, and a reported CSA collapses from 94% to 51% under in-distribution evaluation (author-reported per the Adversarial-ML-Attacks synthesis); that synthesis criticizes the field for omitting **TPR@low-FPR** and variance (A39449, A39276). So "MIA success" is a contested oracle: gameable downward and inflatable upward depending on setup.

**Where defenses fail (adaptive / real-world).** Output-suppression defenses do not stop embedding-space MIA (A40839 remains effective when output-based MIAs fail). DP is only a partial mitigation against the strongest tested MIAs — A40846 reports DP yields *only a slight ASR decrease* against relative-metric MIA, and A40587's threat is *untested against DP-SGD* (author-reported per the Adversarial-ML synthesis). Using MIA as the *sole* privacy oracle is itself a named benchmark limitation (a single lower-bound estimator standing in for "privacy").

**System-design & launch-gate implication.** Do not accept MIA parity as a standalone privacy acceptance test. A defensible gate requires (a) reporting at a fixed low-FPR operating point with variance, not headline AUC; (b) an *artifact-only* MIA (soft prompt / gradient / hidden state), because output suppression is not a boundary; and (c) a former-membership probe on any "delete my data" path. Treat MIA as necessary-but-insufficient, always paired with the representation-level probe from Thread 3.

**Mapping.** **C:** artifacts (soft prompts, gradients, hidden states) carry membership signal independent of output access. **V:** MIA is a verification instrument but a weak/gameable one — require TPR@low-FPR + a representation probe. **E:** log the attack family and FPR operating point as configuration-of-record. **R:** the former-membership imprint persists post-deletion; disclose it.

---

## Thread 2 — Model / embedding inversion

**Well-established.** "Privacy-preserving" embeddings remain invertible under a realistic black-box, embedding-only adversary. The strongest-evidence entry in the corpus is A42453 (FEM): diffusion+KAN reconstruction of impersonating faces from face-recognition and *privacy-preserving* FR embeddings, defeating **eight named protection schemes** (DCTDP, HFCF, PartialFace, MinusFace, PolyProtect, MLP-Hash, SlerpFace, Fawkes) against multiple backbones and a commercial API. Author-reported ASR at fixed FAR=0.01 (e.g. IRSE50 FEM-KAN 83.7 vs MAP2V 77.9); crucially, protection *reduces but does not eliminate* ASR (e.g. residual 44.5 on GhostFaceNet for MinusFace — "reduced, not eliminated"). Inversion generalizes beyond faces: RAG text-embedding inversion recovers tokens (A40876, up to ~5% tokens recoverable — author-reported per the Adversarial-ML synthesis) and split-LLM hidden-state inversion recovers prompts (A38853).

**Emerging.** The operationally dangerous property is that **inversion is offline and server-undetectable**: once an embedding is intercepted, reconstruction happens on the attacker's machine with no query to the victim, so no server-side rate-limit or anomaly detector can observe it (reviewer synthesis over A42453). Steering vectors and pseudo-source reconstructions also carry recoverable structure (A40720, A39975), extending "invertible artifact" to the activation-editing surface now entering production.

**Contested.** Whether template-protection schemes provide *any* meaningful anonymization is contested between vendor framing and A42453's finding: all eight tested schemes are marketed as privacy-preserving, yet all invert to impersonating identities under the paper's threat model. This is closer to a demonstrated bypass than a live scientific debate — but it is contested in the sense that the schemes are still deployed as if protective.

**Where defenses fail (adaptive / real-world).** Every tested PPFR scheme still yields impersonating reconstructions (A42453). The empirical defenses that do exist — direction-preserving activation scaling (A38853), MI-optimized embedding obfuscation (A40876) — are evaluated against non-adaptive attackers and **require production validation**.

**System-design & launch-gate implication.** Treat any embedding or template as *reconstructable-if-intercepted*; never treat "protected embedding" as "anonymized." Because inversion is offline, the only viable query-time controls are liveness/injection detection plus hard **egress control** on embeddings (they must not leave the trust boundary in the clear). Launch gate: no "privacy-preserving embedding" claim ships without an executed inversion red-team, and the residual per-scheme ASR must be disclosed.

**Mapping.** **C:** embeddings/hidden states invert to raw identity or prompt. **P:** embedding egress must be permission-gated as a secret, not a token. **V:** the executed inversion attack is the acceptance test — a "by-construction" claim is insufficient (A42453 is the cautionary example). **R:** residual ASR after protection is nonzero and offline-recoverable; disclose per scheme.

---

## Thread 3 — Data reconstruction (gradients & split inference)

**Well-established.** Heuristic additive noise on gradients is not a robust privacy boundary — the corpus's single most-replicated attack finding, reached by two methodologically independent papers: A37743 (GGSS-R, diffusion-prior inversion of Gaussian/Laplacian-perturbed gradients) and A39333 (Venom, *analytic, noise-prior-free* reconstruction from DP-protected gradients; author-reported LPIPS 0.340 vs 0.632 and ASR 45% vs 2% for prior SOTA at ε=10, δ=10⁻⁵). Both reconstruct client images from noise-perturbed / DP gradients under an honest-but-curious FL server. In split inference, smashed intermediate representations invert back to raw input, worst when the client-side "bottom" model is shallow (A39212).

**Emerging.** A39333's *noise-prior-free* analytic reconstruction is the escalation that matters: it does not need to know the noise distribution, so "the attacker doesn't know our noise" is not protection. A37743 also contributes a reusable **Reconstruction-Vulnerability (RV)** metric as an architecture-audit primitive — a way to score a split point before deployment.

**Contested.** "Noise defends" vs "noise fails" is a live tension rather than a strict contradiction. A37743's own theory reconciles it: additive noise *raises* the reconstruction-error lower bound but does not eliminate it — noise has value and is insufficient alone (direct paper finding). The defense-side DP papers agree in spirit that the *accounted* guarantee, not the perturbation, is load-bearing (A37854, A39510).

**Where defenses fail (adaptive / real-world).** Heuristic/DP gradient perturbation is reconstructed by both A37743 and A39333. Federated methods that assert privacy from "we only share gradients / digests / prototypes" carry **no accounting** and are contested as security evidence, because gradient sharing is a documented leakage vector (A39307, A39524, A39338; cross-category A39500 federated attribute/gradient leakage; A40037 adds Laplace noise but with *no formal (ε,δ) budget*).

**System-design & launch-gate implication.** Never ship raw per-client gradients or smashed representations over an untrusted channel. The convergent recommended stack is **secure aggregation + clipping-with-DP-accounting (+ optional compression)**, red-teamed with a *generative-prior* reconstructor. Launch gate: any "gradients are private / data stays on device" claim on an FL or split path must survive an executed noise-prior-free reconstruction attack before it appears in product copy.

**Mapping.** **C:** gradients and smashed reps reconstruct to raw input. **V:** the RV metric plus an executed generative-prior reconstruction is the audit. **E:** log the privacy dial (ε, guidance rate mr, FSInfo level) as configuration-of-record. **R:** noise raises but does not eliminate reconstruction error — residual leakage remains under an adaptive analytic attacker.

---

## Thread 4 — Differential privacy

**Well-established.** DP is the corpus's one *adaptive-safe-by-construction* family: its guarantee is worst-case over unbounded auxiliary knowledge for the specific released artifact. Formal anchors: A39510 (tight hidden-state RDP + utility bounds under only smoothness), A39051 (DP linear programming whose one-sided-tightening truncated-Laplace noise **guarantees the released solution still satisfies the original constraints** — the canonical "DP that cannot violate a safety invariant" pattern), A37854 (µ-GDP dataset distillation exploiting post-processing immunity), A38016 (DP-SGD synthesis). Two reusable levers: **post-processing immunity** (route computation through already-private, DP-generated data at zero additional budget — A37854, A39051) and **constraint-preserving noise** for systems with hard invariants (A39051; A39710 clip-to-domain post-processing).

**Emerging.** Structure/subspace-restricted DP to escape the noise-∝-dimension curse: A40117 (subspace-restricted DP fine-tuning), A40720 (structure-aware reduction then Metric-LDP for *steering vectors*), A40862 (single-residue LDP). DP synthetic in-context demonstrations with single-budget composition (A40838).

**Contested / caveated.** DP's *empirical* strength at real operating points is under-validated. Formal-guarantee-without-executed-attack is pervasive: A39051, A39710, A39582, A40117, A40838, A40720, A40852 argue privacy via (ε,δ)/LDP/Metric-LDP composition but run **no** empirical MIA/reconstruction/linkage attack (reviewer synthesis; the underlying cards independently recommend pairing formal bounds with red-team attacks). Cross-category, DP underperforms as a shield against the strongest MIAs: A40846 reports DP gives *only a slight ASR decrease*.

**Where defenses fail (adaptive / compositional / real-world).** The guarantee is only as strong as its accounting and trust boundary, and is *voided* by: leaked intermediate checkpoints (A39510's tighter hidden-state bound dies if checkpoints leak), a colluding majority (A38773, A40852), or **un-accounted shared artifacts** — DP claimed for the headline object but not the structural graphs (A39311), mass values (A39582), or digests (A39307) shared alongside it. Calling gradient perturbation "DP" without accounting does not protect (A37743, A39333). Utility also collapses at strong privacy (A39582 baselines go "NA" at ε<1; A39381 reports 30–60% GPL degradation under perturbation).

**System-design & launch-gate implication.** Prefer *accounted* DP over heuristic noise; log ε/δ **and** the accounting for every shared artifact as configuration-of-record; treat budget exhaustion or an accounting error as an *incident boundary*. Where a privatized output feeds a system with invariants (feasibility, valid ranges, safety envelopes), use constraint-preserving DP (A39051) rather than symmetric noise that can violate them. Launch gate: require an executed-attack red-team before trusting a formal-DP claim at product scale, and validate at production scale — the in-corpus DP evidence is toy-scale.

**Mapping.** **C:** DP bounds what a counterparty can infer about the *specific released artifact*. **P/E:** the ε-budget is a governed credential — custody, rotation, incident boundary. **V:** an executed MIA/reconstruction red-team must accompany the formal bound (currently the pervasive gap). **R:** the guarantee voids under leaked checkpoints, collusion, or un-accounted artifacts — enumerate these as residual risks.

---

## Thread 5 — Federated learning

**Well-established.** A large fraction of "federated privacy" in the corpus is **data-minimization-by-architecture with no threat model, attack, or accounting**, and is contested as security evidence: A39307, A39524, A39338 (and the informal A38021) assert privacy from "we only share gradients/prototypes/digests." Cross-category, the same pattern recurs: A37918 (FedSDA), A40037 (FedPKDA), A39337 (FedTopo), A39939 (SFDA) share representations/prototypes/models instead of raw data but *cite the gradient-inversion/MIA attacks without running them*, so residual leakage is unquantified; A40037 adds Laplace noise but with no formal (ε,δ) budget. The cross-cutting rule: **data locality is not a privacy guarantee** — gradient/digest sharing is a documented leakage vector (A37743, A39333, A39500).

**Emerging.** Verifiable, poisoning-robust aggregation: A40889 (MartDE) uses encrypted scoring, commitment-based verifiable client selection, and norm-normalization before cosine-similarity trust scoring; it survives norm/scaling model-poisoning (tested to 80% malicious data-providers) where plain cosine defenses collapse below 20% accuracy. Federated *unlearning* with audit records: A39895 (FedShard, exact sharded unlearning), A40045 (Oblivionis, LoRA-targeted unlearning with an auditable evidence record).

**Contested.** FL-as-privacy-technology vs FL-as-attack-surface. The federated *channels* are adversary-controlled: the deletion-request channel enables poisoning (A39895 — malicious clients issue deletion requests to damage similar-data victims; "unfair forgetting" is the vulnerability), and the update channel enables knowledge-edit poisoning that evades eight aggregators (A40787 ShadeEdit, ~99.5% ASR — author-reported per the Adversarial-ML synthesis) and split-federated poisoning (A40908 HealSplit). So FL simultaneously *introduces* privacy and integrity attack surfaces.

**Where defenses fail (adaptive / real-world).** Robust aggregation is bypassable: cosine-similarity defenses collapse under norm/scaling attacks (A40889's motivating failure), and knowledge-edit poisoning evades FedAvg/Multi-Krum/etc. (A40787). Malicious/active/colluding adversaries are almost universally **out of scope** and stated so (A40033, A40132, A40852); two-non-colluding-party and honest-majority anchors collapse under collusion.

**System-design & launch-gate implication.** Never present "federated / data stays local" as a privacy control in product copy. Put a DP/secure-aggregation boundary on the training/telemetry path with accounting for *all* shared artifacts, and treat the update and deletion channels as adversary-controlled — bound the cross-principal blast radius and cost variance of any single participant. Launch gate: an FL privacy claim requires accounted DP + an executed gradient-reconstruction red-team + a Byzantine/poisoning evaluation that *includes scaling attacks*.

**Mapping.** **C:** shared updates are both reconstructable and poisonable. **P:** the update/deletion channel is adversary-controlled — require authorization and blast-radius bounding, not just receipt. **V:** gradient-reconstruction + scaling-poisoning red-team. **E:** commitment-based verifiable selection and per-operation audit records (A40889, A40045). **R:** collusion voids honest-majority/two-party anchors; the aggregate still leaks without DP noise.

---

## Thread 6 — Secure aggregation & secure computation

**Well-established (as recommended primitive).** "Secure aggregation + accounted DP" is the *convergent design recommendation* against the gradient-interception adversary — pair aggregation with clipping and DP accounting rather than heuristic per-client noise (reviewer synthesis in the Privacy-Protection doc, grounded in the Thread-3 attacks). It is important to state the evidentiary status precisely: the corpus recommends this pattern but contains **no dedicated secure-aggregation protocol benchmark**; the nearest in-corpus artifact is verifiable *robust* aggregation (A40889). The secure-computation building blocks that do exist are semi-honest / honest-majority only: A38773 (honest-majority Shamir sharing, *perfect security under honest majority only*, with oblivious fixed-structure restructuring of leaky dynamic-graph artifacts), A39210 (2PC secret-shared Boolean matmul + k-anonymous supernodes, semi-honest), A40132 (RMFE-packed Shamir over Z₂ᵏ, MNIST-scale), A40852 (2PC-zCDP two-server DP training, semi-honest non-colluding).

**Emerging.** Verifiable aggregation / verifiable outsourced compute: A40889 (commitment-based verifiable selection + encrypted scoring, anytrust non-collusion); A42232 (ZK proof of quantum inference with parameter hiding against an untrusted host — but noise-free 4-qubit simulation only). HE+MPC transformer inference with efficiency gains but semi-honest (A40033 PCFormer, ~1.9× speedup author-reported).

**Contested / limits.** No graceful degradation past the trust threshold. MPC collapses under a colluding majority (A38773, A40852) and malicious adversaries are out of scope (A40033, A40132, A40852). The k-anonymity layer in A39210 is reviewer-flagged **weak to linkage/auxiliary-information attacks** with no ℓ-diversity/DP layer. Efficiency and maturity diverge within the family: A40852 reports two-orders-of-magnitude training-time reduction (642.78 s vs 173,960.9 s — author-reported) yet stays semi-honest, while A42229 degrades in fidelity at useful scale (IO unfaithfulness 0.0499→0.4454 collapse at MLP-L).

**Where defenses fail (adaptive / compositional / real-world).** Collusion / malicious majority; k-anonymity linkage; and **toy scale** (MNIST / ~2000-sample / 4-qubit) where scaling is asserted, not shown. Critically, secure aggregation *alone* still leaks: the aggregate of honest clients is informative without added DP noise.

**System-design & launch-gate implication.** Secure aggregation is the right *default* for the FL telemetry path, but it must be paired with DP accounting (aggregate leakage) and architected for collusion *detection or resistance* before you rely on a non-collusion assumption. Treat the non-collusion assumption and the crypto keys (ChaCha20/CKKS, verifiable-selection commitments) as governed configuration with custody, rotation, and an incident boundary. Launch gate: do not attach assurance claims to toy-scale MPC/HE/ZK evidence; production scale is unvalidated here.

**Mapping.** **C:** aggregation hides individual updates *only* under the stated trust model. **P/E:** the non-collusion assumption and keys are governed config; commitment-based verifiable selection is the evidence artifact. **V:** verify at the trust threshold (collusion detection); verify correctness of outsourced compute (A42232) where it matters. **R:** collusion or a malicious majority voids the guarantee, and the aggregate still leaks without DP.

---

## Thread 7 — Leakage via embeddings / retrieval / memory / logs

**Well-established.** *Model-derived artifacts are secrets, not opaque tokens* — the corpus's second most-replicated principle. Gradients, smashed reps, soft prompts (A40839), steering vectors (A40720), and even "protected" embeddings (A42453) invert or leak membership, sometimes with no output access. The **retrieval/RAG** surface is directly implicated cross-category: RAG embedding inversion recovers tokens (A40876), cross-modal image-membership inference operates on multimodal RAG (A40726), and split-LLM hidden-state inversion recovers prompts (A38853) — all author-reported per the Adversarial-ML synthesis. The **log/memory/interaction-trace** surface is its own channel: the decision/policy *sequence* leaks per-user outcomes even when stored data is protected (A39710 — a bandit's arm-selection sequence), and sensitive-information disclosure through the I/O layer is an OWASP-LLM-#2 concern with a taxonomy-grounded financial detector (A41498 GARD, cross-category).

**Emerging.** Output-free / embedding-only leakage that is *resistant to output suppression* (A40839 PIPRA). Provider-as-adversary controls for RAG/tool-use: keep raw content local and send only anonymized/abstracted/surrogate data to external models — entity abstraction (A40534 ARoG), redact-then-recover surrogate editing (A40911 SOER), local-first routing (A40041 PRISM), DP steering vectors (A40720).

**Contested.** Whether "by-construction" anonymization *bounds* leakage. A40534, A40911, and A42372 report **no leakage metric** — the leakage reduction is asserted, not quantified (reviewer synthesis; an explicitly named open problem). So these controls reduce the attack surface but do not yet carry evidence of *how much* residual leakage remains.

**Where defenses fail (adaptive / real-world).** Output suppression does not stop embedding-space attacks (A40839). "Protected" embeddings still invert (A42453). Anonymization schemes ship without leakage quantification (A40534, A40911). And the retrieval context is itself **attacker-writable** — a prompt-injection surface (A40353, A40726, A40876, cross-category), so retrieval leakage and retrieval injection are the same trust-boundary problem.

**System-design & launch-gate implication.** Treat every stored or transmitted artifact — embeddings, retrieval indices, agent memory, logs, interaction traces — as a first-class secret with egress control, and **instrument the interaction trace, not only the datastore** (A39710). Minimize and sanitize exposed reasoning/justifications in logs. For the provider-as-adversary path, keep raw content local and send only abstracted/surrogate data. Launch gate: RAG and agent-memory features require an embedding-inversion + retrieval-injection red-team and a residual-leakage disclosure before shipping a "private RAG / private memory" claim.

**Mapping.** **C:** embeddings, hidden states, and traces are invertible / membership-bearing. **P:** egress of artifacts *and* the (attacker-writable) retrieval context must be permission-gated. **V:** inversion + injection red-team; a leakage metric for anonymization schemes (currently missing). **E:** sanitized, tamper-evident logs; log the interaction trace as an evidence record. **R:** offline, server-undetectable inversion of any egressed artifact — disclose.

---

## Thread 8 — Utility–privacy tradeoffs

**Well-established.** The tradeoff is intrinsic, dial-tunable, and recurs across *every* modality — text (A40041, A40838), embeddings (A40206, A40720), voice (A42113), images (A40911), explanations (A42229), telemetry (A40862), tabular/graph/vision. **No paper claims to eliminate it.** Baseline utility collapses at strong privacy (A39582 baselines go "NA" at ε<1; A39381 reports 30–60% GPL degradation under perturbation). The reusable win: **selective, sensitivity-aware protection beats blanket DP/HE/MPC on utility** — "no free lunch is reduced, not removed." Protect only the sensitive part (A40206 NashCoder, A40041 PRISM, A40534, A40911) or restrict noise/computation to task-relevant structure (A40117 subspace, A40720 compression, A40862 single-residue, A39212 decompose-then-protect).

**Emerging.** Crypto approximations trade *fidelity* for confidentiality via HE/MPC-friendly op swaps (ReLU→x²+x, hard→soft k-means), with a recurring faithfulness penalty — A42229 reports fidelity collapse (IO unfaithfulness 0.0499→0.4454 at MLP-L). Crypto pipelines report latency gains but stay semi-honest (A40033 ~1.9×; A40852's large speedup — author-reported).

**Contested.** Whether the sensitivity-aware "utility win" is *security* or merely a smaller attack surface. These papers report near-non-private utility but **run no empirical attack** on the privacy axis (A40206's surrogate attacker is acknowledged weaker than a real one; A42113 evaluates only an "ignorant" attacker). So the favorable tradeoff is demonstrated on the utility axis while the privacy axis is unvalidated — the contested core.

**Where defenses fail (adaptive / real-world).** Utility figures are author-reported, often on toy/single-dataset settings; the privacy side of the curve is not attack-validated, and weaker-than-real surrogate attackers likely overstate the achievable tradeoff (A40206, A42113).

**System-design & launch-gate implication.** Expose the privacy dial (ε / γ / mr / FSInfo / D / εd²) as a governed, logged setting. Prefer sensitivity-aware protection where a sensitive sub-part is identifiable, but **validate the privacy axis with an executed attack** — do not accept the utility win as evidence of privacy. Launch gate: publish the *operating point* — dial value + measured utility + measured attack success — never utility alone.

**Mapping.** **C/R:** the dial position sets the residual-leakage-vs-utility operating point. **E:** log the dial as configuration-of-record. **V:** measure attack success *at the chosen dial*, not only utility.

---

## Thread 9 — Composition & repeated-query risk

**Well-established.** DP composition is the canonical accounting primitive; per-round/per-query budget must be composed (A40838 single-budget composition; A40117, A40852, A40720 (ε,δ)/LDP composition). The recurring failure is **under-specified accounting**: DP is claimed for the headline artifact but not for every shared object — structural graphs (A39311), mass values (A39582), digests (A39307) — and per-round composition for iterative variants is flagged as *"not analyzed."* Repeated / iterative queries escalate leakage and enable extraction: encoder-free model extraction from a query API (A39671, ~100 queries vs ~5,000 for prior SOTA — author-reported), iterative-resubmission attacks on confidential-agent evaluation (A42372), and query-trajectory signals as attack fuel (cross-category A38127, A38416, A40587, A40726, A40846).

**Emerging.** Composition *over time* in agentic loops: A39710 shows the arm-selection *sequence* of a feedback-driven bandit leaks per-user outcomes — composition over an interaction trace, not just over queries. **Deployment-operations composition** is a distinct and under-appreciated axis: fine-tuning *after* unlearning reactivates forgotten data more than quantization does (A41120), and RTT relearning restores forgotten knowledge (A40343) — so an unlearning operation and a later routine fine-tune *compose* into a leak.

**Contested.** Whether per-artifact DP accounting captures the true multi-artifact / multi-query budget. The corpus flags that most papers account only the headline object, so the composed budget over all egressed artifacts and repeated queries is unquantified (reviewer synthesis; an explicitly named open problem — "formal accounting for all shared artifacts").

**Where defenses fail (compositional / adaptive / real-world).** Un-accounted shared artifacts and un-analyzed per-round composition (A39311, A39582, A39307). Volume-based rate-limiting misses the *compositional structure* of queries: a small, information-dense, centroid-proximal query set defeats the "rate-limit + prediction-only" defense (A39671), and a *single* benign query already suffices for former-membership inference (A40047). Deployment fine-tuning re-composes forgotten data back into the model (A41120, A40343).

**System-design & launch-gate implication.** Treat cumulative privacy budget across **all** egressed artifacts *and* repeated queries as the accounting unit; budget exhaustion is an incident boundary. Rate-limit on query information-content / centroid-proximity, not just volume (A39671). For agentic loops, account the interaction trace over time, not per-call (A39710), and treat post-deployment fine-tuning as a reactivation hazard that must trigger re-audit (A41120, A40343). Launch gate: the composition budget must cover every egressed artifact plus a repeated/adaptive-query red-team (extraction, iterative resubmission, former-membership) before any "private under repeated use" claim.

**Mapping.** **C:** repeated/adaptive queries compose into extraction and membership capability. **P:** a query budget + information-content rate-limit is the authorization gate. **E:** cumulative ε across all artifacts logged as configuration-of-record; exhaustion is an incident. **V:** repeated-query / extraction / resubmission red-team, plus re-audit after any fine-tune. **R:** un-accounted artifacts and deployment fine-tuning re-compose to leakage — disclose.

---

## Cross-thread synthesis: where privacy defenses systematically fail

Reading the nine threads together, three failure patterns recur independently and are the load-bearing takeaways for a guardian/agent stack (reviewer synthesis, each grounded below):

1. **Approximate ⇒ recoverable.** Heuristic noise (A37743, A39333), behavioral unlearning parity (A39373, A40047, A40343, A40818, A41120), and "protected" embeddings (A42453) all leave an adversarially recoverable residue. *"Deletion ≠ unrecoverable; noise ≠ private; protected ≠ anonymized."* The missing acceptance test is always a **representation-level / relearning / inversion probe**, not a behavioral one.

2. **The trust boundary, not the mechanism, is the weak point.** Formal DP/MPC is adaptive-safe *by construction* yet is voided by a leaked checkpoint (A39510), a colluding majority (A38773, A40852), or an un-accounted shared artifact (A39311, A39582, A39307). The mechanism is rarely broken; the *boundary and the accounting* are.

3. **Evaluation lags the adversary.** Formal-guarantee-without-executed-attack (A39051, A39710, A40117, A40838, A40720, A40852), non-adaptive attackers, MIA-as-sole-oracle, LLM-as-judge privacy labels, and toy scale are pervasive. Every privacy claim in this corpus is scoped to a *non-adaptive, non-colluding, often toy-scale* threat model; adaptive and production-scale robustness **requires production validation**.

## Consolidated launch gates (C/P/V/E/R)

| Gate | Requirement | Grounding |
|---|---|---|
| **V — Deletion acceptance test** | Right-to-be-forgotten / memory-purge must pass a *representation-level* probe (residual-information or relearning attack), not behavioral MIA/accuracy parity; re-audit after any fine-tune or output-layer patch. | A39373, A40047, A40343, A41120 |
| **V — Executed-attack red-team** | No formal-DP / crypto / "privacy-preserving embedding" claim ships without an executed MIA / reconstruction / inversion attack at product scale. | A42453 (cautionary), A40117, A40838, A40852, A40720 |
| **E — Privacy dial as config-of-record** | Log ε/δ/γ/mr/FSInfo/D *and* accounting for every shared artifact; budget exhaustion / accounting error is an incident boundary. | A39510, A39311, A39582, A39307, A40041 |
| **P — Artifact egress control** | Treat gradients, smashed reps, soft prompts, steering vectors, embeddings, retrieval indices, and interaction traces as secrets with egress permission gates. | A37743, A39333, A39212, A40839, A42453, A40720, A40876, A38853 |
| **P — Action-path privacy gate** | An independent recognition→localization→severity→human-confirmation stage before high-sensitivity agent actions — "capability is not permission." | A40874 (RA <60% even with hints; best ~67% author-reported), A39710 |
| **R — Residual-risk disclosure** | "Delete my data" and "privacy-preserving" features must disclose that deletion is approximate/reactivatable and protected embeddings invert offline. | A41120, A40047, A42453 |
| **V — Composition & repeated-query red-team** | Account cumulative budget across all artifacts + repeated queries; rate-limit on query information-content; red-team extraction / resubmission / former-membership. | A39671, A40047, A42372, A41120 |
| **P/E — Governed trust assumptions** | Non-collusion / honest-majority assumptions and crypto keys are governed dependencies with custody, rotation, and an incident boundary; architect for collusion detection before relying on them. | A38773, A40852, A40889 |

**Most agent-core evidence.** A40874 (SAPA-Bench) is the single most transferable result: off-the-shelf MLLM smartphone agents recognize sensitive actions at recognition-awareness **below 60% even with explicit hints** (best Gemini 2.0-flash ~67% — author-reported; some result tables in the underlying card are flagged truncated). Data-at-rest protection is insufficient when the *action path itself* lacks privacy awareness — the direct motivation for a PolicyGuard/ActionGuard-style gate with human approval on sensitive tool calls, and the reason privacy in an agent stack must live in the decision path (Thread 7's A39710, Thread 9's composition risk), not only in the datastore.
