# Final Quality Review — Guardian Agent Foundations

**Audit lead:** independent roll-up of 10 per-lens adversarial reviews
(`quality-review/_lens-*.md`): adaptive-attacker, adversarial-ML-researcher, AI-safety-researcher,
future-retrieval-agent, implementation-engineer, independent-auditor, privacy-engineer,
product-manager, red-team-operator, security-architect.
**Date:** 2026-07-14.

---

## Overall verdict

**SHIP — conditional.** The knowledge base is **fit to ship as a reference / knowledge skill** once
the single blocking correctness fix and a short "index-integrity" punch-list are cleared. Every lens
independently reached the same headline: this is an *unusually well-calibrated, traceable, and
threat-model-scoped* base — three lenses (AI-safety, independent-auditor, privacy-engineer) returned
**"no blocking issues"** outright, and the rest state plainly that they did *not* manufacture defects
to fill a quota. Evidence integrity and citation traceability are effectively total (100% of the 284
distinct pattern citations and 432 synthesis citations resolve; 432/432 cards on disk; 0 orphans).

The one qualifier that keeps this from an unconditional "ship": the base **reads** more build-ready
than it is. The confident System-architecture and Metrics blueprints are abstracted largely from a
single *Preliminary* paper (A41468) and a single vendor brief, and several load-bearing runtime
seams — root-of-trust / identity attestation, a safe-state definition for embodied actuators,
inter-agent delegated authority, and a unified trace schema — are honestly *disclosed* but *un-owned*
by any playbook. That is fine for a knowledge skill and **not** fine for anyone lifting these pages
as a production spec for the Origin/Passport stack.

- **Ship as a reference skill:** yes, after the blocking fix + dead-link/stale-artifact cleanup (Top-8 #1–3).
- **Rely on as a build-ready guardian spec:** not yet — resolve or explicitly mark as known-limitations
  the cross-pattern architectural gaps (Top-8 #4–8).

Severity tally across the merged set: **1 blocking · 22 major · 17 minor** (duplicates merged;
"major" is dominated by *cross-pattern seams no single playbook owns*, not by errors in the evidence).

---

## Consolidated findings

Blocking first, then major, then minor. Duplicate findings raised by multiple lenses are merged into
one row with all corroborating lenses named.

### BLOCKING

| # | Lens(es) | File / section | Issue | Fix |
|---|----------|----------------|-------|-----|
| B1 | adversarial-ML | `syntheses/Adversarial-ML-Attacks.md` §1, §17 (propagated to `cross-cutting/adversarial-ml.md:300`, `defense-in-depth.md:243`, `evaluation-holdout-protection.md:38,456`, `backdoor-detection.md:592`) | "No defense offers certified robustness against an adaptive adversary" is **technically false to the target audience** — certified robustness *is* a worst-case, attack-agnostic guarantee that holds against any adversary *within its bound* — and self-contradicts the KB's own CertMask/A37117 description two lines away. A sophisticated reader flags this on first pass; it corrodes trust in the rest of the base. | Global-replace with "…against an **unbounded** adaptive adversary (permitted to exceed the certified threat model — larger radius, different norm/surface)." The correct form already ships in `adaptive-red-teaming.md`. Also closes the citation-fidelity slip (adv-ML F3: `adaptive-red-teaming.md:43` attributes "unbounded" to §1, which doesn't yet contain it). |

### MAJOR

| # | Lens(es) | File / section | Issue | Fix |
|---|----------|----------------|-------|-----|
| M1 | adaptive-attacker *(its #1 risk)* | runtime patterns' **Verification** sections + `evaluation-holdout-protection.md` (Known-bypasses 446–448) | The base's most-repeated verification claim — "pass an adaptive, defense-aware red-team = launch gate" — has a **named, un-wired defeater**: an eval-aware / conditionally-defecting agent (A40486, A39480, A41129) passes every offline gate and defects in prod. `evaluation-holdout` terminates the thread at "measurement cannot cover it" and never cross-links the runtime layer built to compensate. | In each runtime pattern's Verification, append: adaptive red-team is necessary but cannot cover eval-aware/conditional defection — pair with the runtime compensating control. Cross-link `evaluation-holdout` → `runtime-anomaly-detection.md` naming concrete measures (prod-distribution canaries, eval-vs-prod behavioral-divergence, the A41090 stated-vs-executed self-inconsistency tripwire, kill-switches). |
| M2 | security-architect *(its #1 risk)* | `human-approval-*`, `kill-switches.md`, `least-privilege-credentials.md` — Preconditions | **Root-of-trust is un-owned.** Three enforcement playbooks forward "authenticated principal" to "the agent-identity/credential controls," which itself names local attestation as *the unshipped gap* and gives a fallback only for itself. Approval + kill-switch are told to "assume secure." The entire control plane presumes an authenticator that is unbuilt and un-owned. | Promote the `agent-identity.md` "no trusted identity without a trusted issuer" material to an owned `identity-attestation-root-of-trust` pattern: name the issuer/verification chain, and define fail-closed **per consumer** when attestation is unavailable (deny / hold-for-out-of-band-step-up — not "assume secure"). |
| M3 | security-architect + implementation-engineer | `kill-switches.md`, `policy-permission-gates.md`, `human-approval-*`, `safe-rollback.md` — Failure-handling / When-NOT | **Fail-closed = halt/deny is assumed universally, but the null action is not the safe action for embodied actuators** (cutting power to an arm under load, freezing an actuator mid-trajectory). Separately, irreversible external effects punt to "prevent only" with no reserve/stage/idempotency/dry-run design. Wrong for the Physical-AI stack this skill exists to ground. | Introduce a per-actuator **"safe-state"** abstraction; redefine fail-closed for latency-critical/embodied actions as *transition to a declared reachable safe state*, not deny/terminate. Add reserve-then-commit / idempotency-keys / dry-run-in-P3-dream-env (`architecture-patterns.md` P1/P3) as the staged path for irreversible effects. |
| M4 | security-architect | `policy-permission-gates.md` L4 / Telemetry; `human-approval-*` Failure-handling | **Audit is off the fail-closed path.** For performance, audit is async/zero-latency — so a consequential/irreversible action can fire *before* its decision record is durable, and audit-write failure is not a fail-closed trigger. Non-repudiation/forensic gap for exactly the class these gates protect. | Tier audit durability to the action's risk tier: for consequential/irreversible actions require **synchronous write-ahead commit of the decision record before actuation**, and make audit-write failure a fail-closed trigger (deny/hold). Keep async audit only for the reversible/low-stakes path. |
| M5 | security-architect | `patterns/` (missing pattern) | **No enforcement point for inter-agent (agent→agent) delegated authority** — the corpus's own "least-solved / highest-consequence" case (BU-MA A41134 drops ASR only 7%; A40231 MPAS). Every gate sits at the agent→tool boundary, *inside* which a compromised peer with a legit-scoped credential operates. Diagnosis without prescription. | Add an `inter-agent-authorization` / `attenuated-delegation` pattern: deterministic gate at the orchestrator/message-bus chokepoint, deny-by-default on peer-emitted actions, structural enforcement that a sub-delegated scope is a strict subset, N-hop attribution to the originating human, peer messages untrusted for *authority* as well as content. |
| M6 | implementation-engineer | Telemetry sections of `kill-switches`, `policy-permission-gates`, `safe-rollback`, `human-approval`, `runtime-anomaly-detection` vs `tamper-evident-traces.md` | **No unified canonical trace-event schema**, yet `tamper-evident-traces` makes a stable canonical envelope a hard prerequisite to hash-chain (`entry_hash = H(canonical(entry)‖prev_hash)`). Each pattern emits a bespoke prose field list; an engineer must hand-reconcile ~8 of them, and any drift silently breaks chain verification — the exact failure the base warns about. Directly blocks wiring into `autonomy-trace-console`. | Add `references/trace-event-schema.md` (canonical envelope: `{event_id, prev_hash, writer_identity, ts, event_type∈{intent,gate_decision,approval,actuation,trigger,snapshot,restore,end_state,divergence}, payload, exec_context}`); change each Telemetry section to "conforms to schema, event_type=X". |
| M7 | implementation-engineer + product-manager | `kill-switches`, `safe-rollback`, `human-approval` — Metrics/thresholds | Trigger patterns punt ("no corpus number, validate in prod") while the base's one **threshold-derivation recipe** (A42369: threshold optimization + CIs + anonymized splits, calibrated to real-world F1≈0.3–0.6) lives in `runtime-anomaly-detection.md` and is cross-referenced from six *other* patterns — but **not** the three that must set a tunable trigger. Engineer left with "good luck." | Cross-ref the A42369 recipe from those three §Metrics as the standard way to pick/calibrate the starter threshold (tripwire, rollback ξ, is-consequential classifier), carrying the real-world-F1 caveat. PM overlap: add a "how to set the starter threshold" method note per metric. |
| M8 | red-team-operator | Known-bypasses / Adaptive-tests across `network-segmentation`, `sandboxed-execution`, `tool-capability-isolation`, `incident-containment`, `runtime-anomaly-detection`, `tamper-evident-traces`, `least-privilege-credentials`, `policy-permission-gates`, `prompt-injection-containment` | **Transplanted numbers create false concreteness on the runtime controls Origin/Passport ship.** A41134 "7%" in 9 patterns, A37924 in 9, **A40925 "~15% Acc-Fusion" (an MNIST/CIFAR image-classifier consensus gate) in 7**, A40432 "~28%" in 8 — the source *domain* is silently dropped, so a reader reads an analogy from a different modality as a measured residual of a tool gate. Coverage looks 6× deeper than it is. | Add a 4–6 word origin+analogy tag to each transplanted figure (`A40925 ~15% — consensus image classifier, transplanted as analogy, not measured on a tool gate`). Add a `MATURITY: LOW — transplanted analogies + reviewer synthesis; corpus ran no defense-aware eval of this control` banner atop each runtime pattern's Adaptive-tests section. |
| M9 | red-team-operator | `human-approval-consequential-actions.md` Known-bypasses/Adaptive-tests; cited as backstop in `adaptive-red-teaming.md` + runtime patterns | **The universal compensating control is the least-evidenced.** Human approval is the fallback for every other control's residual, yet its two likeliest breaks are its least grounded: approval-summary poisoning is an *analogy* to A41108/A41144 never tested on an actual approval summary, and approval-fatigue is "reviewer synthesis, no measured rate." | Add an explicit caveat everywhere human-approval is invoked as a compensating control: "untested in-corpus against a defense-aware summarizer attacker and against approval fatigue; production-validate before counting it as residual mitigation." |
| M10 | adaptive-attacker | `retrieval-authorization.md` R2 (215–218), Control (151–153) | **Ingestion tier conflates "authenticated origin" with "not attacker-writable."** An internal wiki, shared blackboard, or the agent's own episodic memory carry a first-party provenance tag *and* are attacker-writable — the pattern cites CREAT (A38606) and memory-as-unprotected-asset (A40188), then routes authenticated-source content straight to EVIDENCE without the reasoning verifier. CREAT's exact surface is the one R2 admits by construction. | Re-key the tier on **write-authorization strength**, orthogonal to origin authenticity. Authenticated-but-writable (wiki, shared memory, peer channel) → `ROUTE_TO_VERIFIER`, not `EVIDENCE`. State explicitly that agent memory/interaction history is authenticated-origin *and* attacker-writable. |
| M11 | adaptive-attacker | `human-approval-consequential-actions.md` item 6 (178–180), Test-case-4, Failure-handling | **"Aggregate-aware gating" is a scalar running-total threshold that cannot see the non-additive set-relational inference it claims to counter** (A40484 SafeNLIDB: "list all students" + "list healthy students" → set-difference leaks a protected attribute). Each query moves no scalar total and is sub-tier; the harm is the join. An attacker decomposes into individually-benign quantity-free reads. | Replace "running total crosses a tier boundary" with **joint-reachability / query-correlation** tracking: maintain a session model of what already-returned results make jointly inferable, re-gate when the reachable-inference set crosses a protected boundary. Keep A40484 inline; cite APO enforcement in the recommendation, not only in Rollback. |
| M12 | adaptive-attacker (+ related security-architect F5) | `policy-permission-gates.md` When-NOT (453–456); `tool-capability-isolation.md` | **"Advisory-only LLM" is circular for open-ended-effect tools** (shell, code-exec, arbitrary HTTP). Advisory-only is meaningful only relative to a deterministic authority; where no allow-list exists, it collapses to either "nothing is ever allowed" or "the LLM is the de-facto grant authority" — the injectable single-artifact authority the same pattern forbids. Shipping pressure resolves toward the dangerous branch. | State the deterministic default: for open-ended effect space the gate defaults to `DENY`/`STEP_UP`, and the LLM signal may only *narrow* (force deny/step-up), never *grant* ALLOW. Pair with `sandboxed-execution.md` as the only ALLOW path. (Sec-arch F5: rank canonicalization as *advisory*; default-deny on any argument class the canonicalizer cannot certify as fully normalized — treat "unable to certify canonical" as the fail-closed trigger, not only "detected ambiguity.") |
| M13 | adversarial-ML | `Adversarial-ML-Attacks.md` §5/§17/§18, `adaptive-red-teaming.md`, `evaluation-holdout-protection.md:46` | **GhostCert (A37924) is not cross-linked in the high-traffic robustness files** where certified defenses (CertMask A37716, A37117) are promoted or where "certificate ≠ oracle" is argued. It is the single most on-point result for this lens — spoofs a randomized-smoothing certificate to give a *wrong* class a large radius — but is siloed in `defense-in-depth.md`, so a reader evaluating certified defenses never sees it and over-trusts the certificate. | Add A37924 cross-refs at each CertMask/A37117 promotion and in the certificate-as-oracle discussion. Distinguish **probabilistic** (randomized-smoothing: confidence 1−α, abstain→DoS) from **deterministic** (patch) certificates — the exact seam GhostCert attacks (adv-ML F5). |
| M14 | AI-safety | `prompt-injection-containment.md` Threat-model/Control; `landscape-2026.md:97-99`, `agent-identity.md:164` | **Injection-containment under-elevates data exfiltration.** Harm is framed almost entirely as unauthorized *action execution*; silent read-then-exfiltrate — arguably the dominant real-world indirect-PI harm — is only a test case, and the base's own Rule-of-Two / lethal-trifecta egress gate is never cross-linked. An implementer could block harmful actuation while leaving the confidentiality channel open. | Add a first-class **"data exfiltration / confidentiality breach"** threat bullet + a named **egress-control / break-a-trifecta-leg** mechanism; cross-link the `landscape-2026` / `interview-agent-security` Rule-of-Two material so breaking an egress leg reads as the floor. |
| M15 | AI-safety | `adaptive-red-teaming.md:13` (propagated to `evaluation-holdout:21`, `kill-switches:105`, `human-approval:72`) | **The flagship meta-claim is over-quantified.** "Wherever an attacker is allowed to be defense-aware, the defense degrades or fails" is stated as a near-universal law but the in-domain LLM/agent sample is thin and drawn largely from non-LLM domains (FL aggregators, watermark removers, VLM repetition); the one adaptively-evaluated AILLM defense (A37350 EigenShield) *survived*. An over-strong "all defenses fail adaptively" prior justifies either fatalism or "our red-team pass is the real proof." | Reword at the source and carry the caveat downstream: "wherever it has been tested, a defense-aware attacker has substantially degraded the evaluated defense — a strong directional prior extrapolated across domains, not a proven universal; A37350 survived with honest asymptotic caveats." |
| M16 | privacy-engineer | `differential-privacy.md` Known-bypasses; `cross-cutting/privacy.md` Thread 3; `Privacy-Protection.md` §4/§9.1 | **The load-bearing "DP gradient perturbation is bypassable" evidence is demonstrated only at ε=10** (e¹⁰≈22,000× likelihood-ratio budget — essentially no meaningful DP), cited ~a dozen times, and *no file caveats the budget magnitude*. A reader generalizes to "accounted DP is bypassable" when the honest reading is "DP at a near-useless budget is bypassable; reconstruction at deployable budgets (ε≤1) is not demonstrated in-corpus." | Annotate every ε=10 citation with a budget note; add "reconstruction-vs-ε curve at deployable budgets" to §Residual/§Open items. |
| M17 | privacy-engineer | `differential-privacy.md` Control/Applicable-assets; `privacy-preserving-training.md:111`; RTBF framing | **Record-level vs user-level DP mismatch, never flagged.** Adjacency is stated as example-level ("add/remove one record") throughout, but the product framings these patterns feed — RTBF, "delete *my* data," per-user personalization, FL where a client = a person — are user-level (group) DP, weaker at the same ε by ~the group size. A team logs a record-level ε and lets a user believe "*I* am protected." | State the quoted adjacency is example-level; RTBF/FL/personalization generally require user-level (group) DP; require every logged ε to record **which unit** (per-record vs per-user) it bounds. |
| M18 | privacy-engineer | `differential-privacy.md` §Composition; `privacy-preserving-training.md` §Recommended | **No privacy-amplification-by-subsampling and no multi-round DP-SGD/RDP composition recipe** — the two factors that dominate real DP-SGD ε. The base names composition abstractly and even flags the FL per-round gap, but never states a single-release ε is not the deployed ε under iterated rounds, so the "log the ε dial" discipline can log the wrong number. | Add subsampling amplification + multi-round RDP composition: the deployed budget is the composed, subsampling-adjusted ε over all rounds, and the accountant (not a per-step σ) is the authority. |
| M19 | product-manager | `cross-cutting/defense-in-depth.md` §10; every pattern Metrics/Residual; syntheses §16 | **Launch gates and residual risks are ownerless** — no RACI / accountable sign-off. The KB adopts launch-review voice ("a pre-deployment requirement, not a post-hoc metric") but never names who signs a gate off or who *accepts* each residual. A PM cannot run a go/no-go review off an ownerless gate list. | Add a one-line **"Sign-off owner / residual acceptance"** per gate in §10 (role placeholders fine: release owner signs, security lead accepts) + an "Owner" field in each pattern's Metrics. |
| M20 | future-retrieval | `scripts/search.py`, `ontology.{md,json}`, `patterns/` (no index) | **No crosswalk from ontology defense tokens (or `search.py`) to the 28 pattern files** — the pattern layer is a *reachability island*. Filenames diverge from tokens exactly for the enforcement controls (`policy_gating`→`policy-permission-gates.md`); 8 tokens have no pattern, 5 patterns (incl. `kill-switches`) have no token (`kill_switch` appears 0× in `ontology.json`). Largest retrieval friction in the base. | Add `patterns/INDEX.md` (file · defense token(s) · attacks addressed · one-line use-when); teach `search.py` a `pattern <token|keyword>` mode; add missing controls (`kill_switch`, …) to the ontology vocab. |
| M21 | future-retrieval | all 8 `syntheses/*.md` + `cross-cutting/*.md` | **Syntheses never link forward to patterns** (grep for `patterns/<name>.md` across all syntheses = 0), though patterns link back richly. The landscape→control hop is one-way: an agent landing on "indirect PI is the single most product-relevant threat" has no pointer to the containing controls. | Add an "Operational controls" line/footer per major synthesis section naming the relevant `patterns/*.md`. |
| M22 | product-manager + future-retrieval | `references/README.md` artifact table | **README's "fastest path to a decision" points to files that don't exist** — `../executive-summary.md` and `../final-quality-review.md`. The exec summary is the artifact a busy reader opens first; the front door over-promises. *(This review file resolves the `final-quality-review.md` half.)* | Create `executive-summary.md` (highest-leverage single doc); the `final-quality-review.md` row is now satisfied. Mark any still-missing row "(pending)". |
| M23 | independent-auditor | `corpus-audit.md` → "## Integrity" | **The traceability-assurance doc contradicts the repo.** It reports `Research cards present: 415/432 (missing: 17)` and `arXiv id resolved: 7/432` when the tree is **432/432, 0 gaps, 0 orphans**; several "missing" cards are load-bearing (A39276 is the "what honest ≈ chance looks like" calibration anchor). The one document whose job is to certify the evidence chain tells readers 4% of it is missing. | Regenerate `corpus-audit.md` from the current tree and add card-coverage/dup/extraction counts to `tests/validate.py` §7 so they can't drift. Interim: stamp `generated: <commit/date>` and correct 415→432. |

### MINOR

| # | Lens(es) | File / section | Issue | Fix |
|---|----------|----------------|-------|-----|
| m1 | AI-safety | `AILLM-Safety.md:295` | Wording error inverts polarity: a bypassed representation-level defense is described as "**led by**" the ablation attack — ambiguous, can read as the defense winning in a sentence whose point is that it was broken. | Replace "led by" → "**bypassed by**". |
| m2 | adversarial-ML | `evaluation-holdout-protection.md:141`, `backdoor-detection.md:274` | "Fine-tuning does not remove implanted behavior" is over-generalized; the KB's own A41118 (LAT mitigates its own backdoor) is a counterexample. | Restore the dropped qualifiers: "**ordinary/clean** fine-tuning does not **reliably** remove … purpose-built defensive fine-tuning may remove some (A41118) but is not a general launder." |
| m3 | adversarial-ML | `Adversarial-ML-Attacks.md` §5/§8 | Probabilistic (randomized-smoothing, abstain option) vs deterministic (patch) certificates lumped under one "certified" umbrella — the exact seam GhostCert exploits. | One clause distinguishing them (folds into M13). |
| m4 | AI-safety + independent-auditor | `ontology.md:34`; `least-privilege-credentials.md:59-61`; `agent-identity.md:29` | The enforcement thesis (ZSP/JIT/broker) rests on a 7/432-paper corpus slice + a single 1Password vendor brief; its least-verifiable stats (>600-day secret, 45:1, ~1/3 repos with a plaintext secret) are second-hand from a commercially-interested party with no primary citation. Disclosure is *honest* everywhere; the gap is source-independence. | Carry a one-line vendor-framing caveat into the *syntheses* (not only the credentials pattern); add primary citations for each statistic or mark `[primary source: unverified]`. |
| m5 | independent-auditor | `syntheses/_partials/Adversarial-ML-Attacks-1.md:183` | The only untraceable id in the tree — `A38449` (not in the 432 master, no card) — survives in a retained superseded partial; the citation validator doesn't scan `_partials/`. The authoritative merge already dropped it. | Delete/move `_partials/` out of the shipped tree, or prepend a `DEPRECATED — do not cite` banner to each, AND extend the citation validator to scan `_partials/`. |
| m6 | privacy-engineer | `differential-privacy.md` §Metrics "privacy dial" | Central-DP ε, local-DP ε, and Metric-LDP εd² are listed in one bullet, inviting apples-to-oranges ranking (a local-DP ε is far weaker than a central-DP ε at the same value). Prose distinguishes them elsewhere — presentation slip. | Tag each ε with its DP variant; add "not comparable across central/local/metric DP; compare only within a variant." |
| m7 | privacy-engineer | `differential-privacy.md` §Metrics/§Telemetry | δ=10⁻⁵ is quoted repeatedly but never paired with N; the δ≪1/N guideline is unstated, so a logged δ is un-auditable for safety. | Add "log N alongside δ; require δ ≪ 1/N" to the config-of-record discipline. |
| m8 | privacy-engineer | `privacy-preserving-inference.md` §Metrics/§Verification | The TPR@low-FPR MIA discipline enforced in `cross-cutting/privacy.md` and `differential-privacy.md` is not propagated here — the one surface where MIA-on-the-transmitted-artifact is actually run reverts to headline-AUC framing. | Cross-ref Thread 1: report MIA at a fixed low-FPR operating point with variance, not headline AUC. |
| m9 | implementation-engineer + AI-safety | `policy-permission-gates.md` (A41468) | The flagship four-layer enforcement architecture *and* the only quantitative ADR table rest on A41468, the enforcement stack's **lowest-evidence (Preliminary)** paper; the caveats are correct but scattered across three sections, and the ADR "%">" figures invite misuse as acceptance criteria. | Add a one-line "load-bearing-but-Preliminary" callout near the top consolidating: reference architecture is a design template not a validated result; ADR table is *not* an acceptance bar; the audit-integrity layer must be supplied via `tamper-evident-traces.md`. Frame the four-layer design as a hypothesis to validate. |
| m10 | implementation-engineer | `kill-switches.md` §Metrics | The halt-latency metric ("switch must actuate faster than the harmful trajectory completes") implies a race it cannot win against single-query *irreversible* actions (A40919/A40465) — could steer an engineer to over-invest in latency instead of pre-act-gate coverage. | State: against single-query irreversible actions the kill switch is post-hoc containment-of-further-harm only and cannot substitute for the pre-act gate; latency targets apply to multi-step/reversible trajectories. |
| m11 | adaptive-attacker | `prompt-injection-containment.md` item 7; `policy-permission-gates.md:208` | The runtime out-of-band "ensemble/denoiser disagreement" channel lacks the shared-base circularity guard that `evaluation-holdout` applies to judges — a shared-backbone ensemble is jointly gamed with one adversarial optimization, silently degrading to a single detector. | Propagate the no-shared-base guard to the runtime patterns; prefer a structurally-different channel (deterministic provenance, human) over a same-family model vote. One-line cross-ref to `evaluation-holdout §Judge-integrity`. |
| m12 | red-team-operator | `deepfake-detection.md` Known-bypasses | Zero demonstrated adaptive break of any corpus method (only A41525 — a K-12 spoof of a MobileNet-V2 *teaching* classifier, not a corpus defense); structurally weaker evidence than siblings but not flagged up front. | Promote the honesty to a first-line banner: "adaptive posture UNVALIDATED; all items plausible-not-benchmarked except A41525 (a teaching classifier)." |
| m13 | red-team-operator | ~19 patterns citing `architecture-patterns.md` / `defense-in-depth` | Bare-filename cross-refs 404 when resolved relative to `patterns/` (targets live 1–2 dirs up). Navigability only; recurs in ~19 files. | Mechanical sed: `../architecture-patterns.md#p11`, `../cross-cutting/defense-in-depth.md#0`. |
| m14 | future-retrieval | `source-index/by-id.md` (cat column) | The category column is truncated (`Adversaria`, `Multi-keyw`…) ≠ real folder names, so the advertised id→card path can't be built mechanically from the human index. | Stop truncating the `cat` column, or add a README line: resolve full category via `paper-to-ontology-map.jsonl` or `search.py text A#####`. |
| m15 | future-retrieval + independent-auditor | `source-index/by-id.md` (arXiv column) | The advertised arXiv lookup is 98% empty (7/432; `arxiv_id` null throughout the manifest), so the id→arXiv hop almost always wastes a step. | Drop arXiv from the advertised `by-id.md` lookup until populated; point at the card PDF path under `~/Documents/Research Papers/…` for the source hop. |
| m16 | product-manager | patterns' "Problem addressed" | User value / capability-unlocked is under-articulated relative to friction; patterns are risk-complete but value-thin (a human-approval gate's value is "it lets a user *safely delegate* irreversible actions," stated nowhere). | Add one "User value / capability unlocked" line per pattern, complementing the harm framing. |
| m17 | product-manager | patterns' Metrics | Metrics are named but unvalued — no starter target to paste into a PRD acceptance criterion. *(Correct honesty; usability gap, not a rigor defect — overlaps M7.)* | Bridge with method not numbers: "gate `unapproved-consequential-execution` at 0 by construction (fail-closed)"; "derive the over-prompting ceiling from a 2-week shadow run vs an adaptive benign-ambiguous set." |

---

## Strengths

Consistent, cross-lens praise — these are the base's load-bearing assets and must not regress under any fix:

1. **Evidence-integrity discipline is best-in-class** (every lens said so). Author-reported vs
   reviewer-synthesis is separated everywhere; the only occurrences of "unbreakable / proven safe /
   secure" are inside the disclaimer lines that forbid them; every magnitude is tagged
   author-reported / non-adaptive / best-case; truncated source tables are flagged; where a real
   formal guarantee exists (DP/crypto) the word "guarantee" is scoped precisely and repeatedly
   bounded. The base leans *toward* under-claiming.

2. **Traceability is effectively total and mechanically verifiable.** 100% of the 284 distinct
   pattern citations and 432 distinct synthesis citations resolve to a real card; 432/432 papers have
   a substantive card (0 gaps, 0 orphans); machine and human indexes agree exactly (evidence-strength
   312/65/38/17; triage 137/245/50; per-category counts) with no silent drift. An agent that follows
   any citation always lands on a real card.

3. **The adaptive-attacker gap is correctly elevated to the #1 meta-finding and made a fail-closed
   launch gate** — not a footnote. `adaptive-red-teaming.md` treats defense-aware evaluation as a
   program, foregrounds oracle/verifier gaming (A40584 PRM 0.973 on an invalid step, A40916 circular
   scoring, A40866 best-judge untested), and gates launch on absolute residuals + over-refusal, not
   relative deltas. Most red-team checklists never question their own scorer.

4. **The enforcement architecture is correct and applied uniformly.** "Capability ≠ permission ≠
   safety" as the spine; the deterministic-authority / advisory-LLM split (the guardian-LLM is never
   an ALLOW path); enforce-at-the-last-controllable-point, environment-side, not-model-injectable;
   the credential-side (govern the means) vs action-side (govern the action) division; and
   "**treat every new trust-decision surface a defense introduces as attackable**" — gate-LLM
   injectability, release-path injection, approval-summary poisoning, trigger suppression *and*
   forgery are all handled head-on.

5. **Fail-closed is a first-class, enumerated section in every control** — concrete triggers (gate
   error, timeout, missing/ambiguous context, provenance-unestablished, LLM/policy disagreement) →
   concrete actions (deny / STEP_UP / degrade-to-least-privilege). `kill-switches.md` uniquely
   handles both failure directions (miss *and* weaponization / abstention-as-DoS).

6. **Every pattern is a complete, buildable template with cited fragile-pattern warnings**
   (Problem→Threat→Control→Architecture→numbered-recommendation→Incorrect/fragile→Metrics→Telemetry→
   Failure-handling→Rollback→Known-bypasses→Adaptive-tests→When-NOT-to-use), and the fail-closed
   *correctness* metrics are genuinely shippable (0-by-construction gates, 100% containment-completeness).
   `tamper-evident-traces.md` is a directly implementable evidence substrate.

7. **The one load-bearing concrete break is correctly identified and threaded everywhere** — the
   STACK/MFA whole-pipeline output-repetition channel (A41108 ~0→71%; A41144 58.5% across 17 VLMs, an
   independent replication) with the correct lesson: *composition of individually-robust controls is
   not itself a control.*

8. **The privacy slice is the strongest-disciplined in the base** — composition/repeated-query is a
   dedicated first-class thread, the "gradient-inversion does not falsify any (ε,δ) bound" distinction
   is stated precisely, and MIA is treated as a gameable two-sided oracle (TPR@low-FPR + variance
   required), not a scalar truth.

9. **Genuinely decision-oriented, not a survey** — every synthesis carries §14 product / §15
   architecture / §16 launch-and-assurance implications; `defense-in-depth.md` §10 is a consolidated
   CPVER-tagged pre-deployment launch-gate checklist; all 28 patterns carry "When NOT to use," and
   over-refusal / approval-fatigue / false-positive rate is a repeated first-class metric.

---

## Top 8 fixes before relying on this

Prioritized by severity × leverage × cost. #1–3 are the cheap must-fixes that gate "ship as a
reference skill"; #4–8 are what must be closed (or explicitly marked as known-limitations) before
anyone treats these pages as a build-ready spec for the Origin/Passport stack.

1. **Fix the blocking certified-robustness phrasing (bundle B1 + M13 + m3).** Global-replace the
   unqualified "certified robustness against an adaptive adversary" with "against an **unbounded**
   adaptive adversary," and while in those files add the GhostCert (A37924) cross-links and the
   probabilistic-vs-deterministic certificate distinction. One-word-class edit, highest credibility
   payoff — this is the one thing a sophisticated reader catches on page one.

2. **Repair the front door (M22 + M23).** Create `executive-summary.md`, mark any still-missing
   README rows "(pending)," regenerate the stale `corpus-audit.md` (415→432, 7→actual arXiv), and
   wire card-coverage/dup counts into `tests/validate.py` so the assurance artifacts can never again
   lie about a corpus that is, in reality, complete. Cheap; removes every dead link and self-contradiction
   a first-time reader hits.

3. **Make the pattern layer reachable (M20 + M21).** Add `patterns/INDEX.md` (file · defense token ·
   attacks · use-when), a `search.py pattern` mode, missing ontology tokens (`kill_switch`), and an
   "Operational controls" forward-link from each synthesis section. Today an agent can retrieve every
   relevant paper and still never reach the playbook that answers "what do I build."

4. **Wire the eval-awareness defeater to a runtime backstop (M1).** The base's most-repeated
   verification claim ("adaptive red-team = launch gate") has a named, un-wired defeater. Append the
   caveat to every runtime pattern's Verification and cross-link `evaluation-holdout` →
   `runtime-anomaly-detection` with concrete measures (prod canaries, eval-vs-prod divergence, the
   A41090 self-inconsistency tripwire). This is the single thing an attacker most wants you to trust.

5. **Stop the false concreteness on the runtime controls Origin/Passport actually ship (M8 + M9).**
   Tag every transplanted figure with its origin domain + an analogy flag, add a `MATURITY: LOW`
   banner to each runtime pattern's Adaptive-tests section, and caveat human-approval as an
   *untested-in-corpus* compensating control. Prevents shipping a stack whose only real adaptive break
   is the output-repetition channel everyone already knows while every pattern-specific break remains
   un-built.

6. **Redefine fail-closed for the physical stack (M3 + M4).** Introduce a per-actuator "safe-state"
   abstraction (fail-closed = transition-to-declared-safe-state, not halt/terminate), add
   reserve/stage/idempotency/dry-run for irreversible effects, and make audit-commit a synchronous
   precondition of consequential actuation. This skill exists to ground a Physical-AI safety stack;
   "halt the arm under load" and "actuate before the record is durable" are exactly the wrong defaults
   for it.

7. **Own the root-of-trust and the inter-agent boundary (M2 + M5).** Promote agent-identity
   attestation to an owned pattern with per-consumer fail-closed-when-unavailable behavior, and add an
   `inter-agent-authorization` / attenuated-delegation pattern at the orchestrator chokepoint. These
   are the two seams the corpus itself flags as least-solved/highest-consequence and that no current
   playbook owns — every enforcement point presumes an authenticated principal that is unbuilt.

8. **Ship the shared substrate and close the calibration gaps (M6 + M7 + M10–M12 + M16–M18).** Add
   the canonical `trace-event-schema.md` (so `tamper-evident-traces` can actually hash-chain), wire the
   A42369 threshold-derivation recipe to the three trigger patterns, and land the highest-leverage
   scoping fixes: re-key retrieval ingestion on write-authorization (not origin authenticity), set the
   deterministic default for open-ended-effect tools, replace scalar aggregate-gating with
   joint-reachability, elevate data-exfiltration in injection-containment, and add the DP budget/unit
   caveats (ε=10 is near-vacuous; record-level ≠ user-level; subsampling + multi-round composition).
