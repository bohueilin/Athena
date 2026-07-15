# Cross-Cutting Chapter — Defense and Mitigation: Defense-in-Depth and the Limits of Layering

> **Sources.** This chapter reasons *across* three category syntheses of AAAI-26 corpus cards —
> `Defense-Mitigation.md` (9 papers), `AILLM-Safety.md` (63 papers), and `Adversarial-ML-Attacks.md`
> (152 papers). It is not a per-paper summary; it draws threads that only appear when the categories are
> read together. Where a category synthesis already labeled a judgment *(reviewer synthesis)* it is carried
> through as such; cross-*category* judgments introduced here are marked **(cross-paper synthesis)** and are
> not claims of any single paper.
>
> **Evidence integrity (non-negotiable).** Every numeric value is **author-reported under that paper's own
> evaluated threat model** unless labeled otherwise, and none is independently verified here. Many source
> tables were truncated in extraction; where a value was absent it is written "not stated in paper." No
> titles, authors, venues, datasets, metrics, attack-success or defense numbers were invented. Language is
> calibrated throughout ("reduced ASR against the tested attacks", "demonstrated under the evaluated threat
> model", "not evaluated against", "requires production validation"); no absolutes ("secure", "unbreakable",
> "proven safe") are used. A defense number is an **upper bound on real-world protection** unless the paper
> built a purpose-built adaptive attacker.

## CPVER mapping legend

Every claim below is tagged to the Origin/Guardian control ontology where it applies:

- **Capability** — what a model, tool, or agent *can* do (raw ability, reachability).
- **Permission** — what policy *authorizes* it to do (the gate).
- **Verification** — the act of checking an output, claim, certificate, or plan for correctness.
- **Evidence** — the tamper-evident record that a check happened and what state existed (attestation,
  provenance, immutable trace).
- **Residual-risk** — quantified harm surviving *all* controls, stated as an absolute, not only a relative
  reduction.

The single load-bearing cross-category result is a boundary between these: **Capability ≠ Permission**, and
**Verification ≠ Evidence** — a model that *can* do a thing is not thereby *permitted*, and a check that
*passed* is not itself *proof* the check was sound (A40895, A41090/A41468, A37924, A38340, A40584, A38853).

---

## 0. The finding that dominates all three categories (read this first)

The most replicated result across all 224 cards is **methodological, not mechanistic**: *static, non-adaptive
defense evaluation is the field's default, and wherever an attacker is permitted to be defense-aware, the
defense degrades or fails.* Each category states it independently — `Adversarial-ML-Attacks` calls it the
"highest-confidence meta-finding" (§9.1); `AILLM-Safety` calls the absence of adaptive-attacker evaluation
"the single most consistent methodological gap" (§16); `Defense-Mitigation` records it "carried explicitly by
every security card" (§9.3). Because these are three distinct corpora, this is **convergence across
independent domains**, not one replicated effect size **(cross-paper synthesis)**.

Consequence for everything that follows: every defense number in this chapter is best-case. The disciplined
counter-examples — where authors *built* the adaptive attacker — are rare and worth naming as the bar:
A37117 (honestly reports its naive weight-lock is broken by an adaptive trigger-inversion attacker, *then*
re-fortifies with randomized smoothing), A40905/A40915 (build purpose-built watermark removers/forgers rather
than testing only fixed defenses), A37716 (attack-agnostic certification), A39290 (an authored adaptive
defense that reports its own insufficiency). This is the standard a launch gate should demand. **Residual-risk.**

---

## 1. Defense-in-depth

**Well-established.** Single-point defenses are insufficient; layered, multi-point defense is the required
posture. This is the strongest *positive* cross-paper theme, convergent across independent domains: RAG
knowledge-base protection leaks on whichever extraction path is left unguarded — single-path RAGFort still
leaks >40% of chunks under RAG-Thief, while the joint dual-path defense reaches the lowest chunk-recovery
rate (author-reported relative-mean CRR 0.51× vs 0.87–0.91× for single-path baselines; A40432); single-modality
federated defenses (DP, cryptography, anomaly detection) fail when text *and* structure are jointly perturbable
(A39732, author claim, numerics not stated in paper); and multi-agent software-pipeline risk is stage-dependent,
so defense-in-depth across stages outperforms any single intervention point (A41134). The agentic-security
papers converge on the same architecture from the runtime side: a four-layer stack of input filter → tool-plan
validation → runtime execution gate → immutable audit (A41468, InfrastructureSentinel, evidence rated
Preliminary) and detect → rewrite/gate → verify guardrails (A41152; A40432's draft-then-verify cascade).
**Permission + Verification + Evidence, layered.**

**Emerging.** Aligning the layers to the *agent cognitive cycle* (observe → plan → act → audit) rather than to
static I/O — grounded by A41090's finding that prompt-level safety is necessary-but-insufficient at the action
layer, and by A41468's per-stage taxonomy. **Permission at the plan/act boundary, not only at input.**

**Contested / the trap.** Layering is necessary but **not** self-composing. Two independent papers show that
guard stacks which pass *per-component* evaluation collapse under a *whole-pipeline* adaptive attack: STACK
moves a few-shot guard pipeline from ~0% to 71% ASR black-box (A41108) and MFA reaches 58.5% across 17 open+
commercial VLMs (A41144) — and both exploit the *same* concrete channel, inducing the model to emit an
attacker-chosen string past the output classifier (independently replicated; **cross-paper synthesis**). The
lesson is precise: *the composition of individually-robust controls is not itself a control.* Depth bought
with a shared backbone is worse than no depth — A41108 flags that a guard sharing a base model with the
guarded model is a *weakness*, and A41144 shows one crafted image transfers across moderators (monoculture
transfer, echoed by A42439's CLIP-ensemble surrogate steering 12 commercial MLLM-AD stacks). **Residual-risk
concentrates at the seams, not inside the components.**

**Implication (design + launch gate).** Architect complementary controls at retriever, planner, executor, and
audit stages (A40432, A41134, A41468) — but treat the *joining channel* as the primary attack surface:
break the verbatim-echo path that smuggles strings past output classifiers, forbid a guard and its guarded
model from sharing weights, and diversify moderator lineage against monoculture transfer (A41108, A41144,
A42439). **Launch gate:** no "N layers therefore robust" claim ships without a whole-pipeline adaptive
red-team that is allowed to target the seams between layers. **Permission/Verification/Evidence.**

---

## 2. Adaptive evaluation

**Well-established.** Non-adaptive evaluation systematically overstates security; a defense-aware attacker is
the discriminating test. Across the corpora this holds for FL robust aggregation (boundary-adaptive A38328 and
subnet-"pill" A39290 each bypass overlapping robust-aggregation sets; ShadeEdit A40787 evades 8 aggregators at
~99.5% avg ASR, author-reported), backdoor detectors (dormant backdoor A39480 evades 7 detectors by living in
the pre-finetuning model where the payload is absent; GCB A39935 resists STRIP/Neural-Cleanse/Fine-Pruning/ABL),
representation-level LLM defenses (attack and defense operate on the *same* residual stream — A40887's card
explicitly flags that ActMan A40858 minimizes the very MMD signal the defense relies on), and certified defenses
(GhostCert A37924 spoofs randomized-smoothing certificates under a white-box, known-σ threat model). **Verification.**

**Emerging.** Purpose-built adaptive removers/forgers as the evaluation *method* (A40905, A40915, A37117) — the
"build the attacker you fear" bar. Also emerging: adaptive attackers modeled as first-class optimizers —
MAJIC's Markov+Q-learning online strategy sequencing (A40554, author-reported >90% ASR at <15 queries),
MetaCipher's multi-agent RL cipher selection (A41058, ≤10 queries, 60%+ ASR), and Gittins-index layered defense
that explicitly models an *optimal* adaptive attacker (A38761).

**Contested / where it fails.** The collision between representation-monitor defenses and activation-space
attacks is *unresolved*, not won by either side: A41074/A42191 (defense) and A41119/A41148 (attack) both key on
a contrastive difference-of-means "refusal direction," and no defense paper evaluates the corresponding adaptive
attack (`AILLM-Safety` §11, §17). Similarly, "robust against SOTA defenses" is almost always a *non-adaptive*
claim (`Adversarial-ML-Attacks` §16). Note one honest negative that cuts the other way: AdvBDGen's adaptive
backdoor (A41118) is itself *substantially mitigated* by latent-adversarial-training — a case where the adaptive
lens found a real defense, not just a real hole.

**Implication (design + launch gate).** Adaptive red-teaming is a **launch gate, not a nice-to-have** — this is
stated verbatim by two of the three syntheses (`AILLM-Safety` §16, `Adversarial-ML-Attacks` §16). Treat any
robustness claim lacking a purpose-built adaptive attacker as *unproven*; require the attacker to have the
defense's design, its thresholds, and (for representation defenses) its steering vectors. **Residual-risk is
unknown for every defense in these corpora precisely because adaptive robustness was not measured.**

---

## 3. Composable controls

**Well-established.** Controls do not compose additively, and a defense frequently *introduces a new
trust-decision surface* that is itself attackable. Robustness-aware federated aggregation is a clean example:
up-weighting clients that show smaller adversarial accuracy drops (A39732 STRUM) creates a meta-decision a
client can game by *appearing* locally robust while poisoning globally — a confused-deputy / evaluation-gaming
risk (`Defense-Mitigation` §11, reviewer synthesis). Process Reward Models make the point for verifier
composition: a PRM scores a logically-invalid step highly via stylistic confounders (an impossible constraint
scored 0.973, author-reported; A40584), so any best-of-N or judge pipeline that *trusts* verifier scores
inherits a gameable oracle. **Verification ≠ Evidence.**

**Emerging.** Capability isolation as a composition primitive — share only a low-capacity module (A39778),
gate utility on a hardware-derived credential so leaked weights degrade to near-random (A37117), decouple the
protected retriever index from the generator's content pipeline to add protection without utility regression
(A40432). These bound *blast radius* rather than trying to make every component individually perfect. **Capability
containment → Permission.**

**Contested / where it fails.** The confused-deputy pattern defeats permission models keyed to component
*identity*: MCPTox (A40895) poisons a *tool description* so a legitimate high-privilege tool carries out the
malicious action — the poisoned artifact never executes (peak ASR 72.8% on o1-mini; <3% refusal even on
Claude-3.7-Sonnet, author-reported), defeating both permission-by-tool-identity and model-level alignment.
Porting a content-style indirect-injection payload (lacking a trigger condition) into the description vector
yields near-0% ASR — so tool poisoning is a *distinct* vector, not a re-skin of content injection (A40895).
MPMA (A40898) independently biases tool *selection* via persuasive metadata (DPMA 100% ASR in most settings,
author-reported). Inter-agent composition adds a MITM surface: MAST (A40224) reframes the message bus as a
first-class tampering channel and evades a three-criteria LLM "Tamper Defender." **Capability ≠ Permission is
the composition failure mode.**

**Implication (design + launch gate).** Bind each planned action to *verified user intent*, not to which tool
ran (A40895); treat all tool metadata, RAG corpora, and inbound multimodal content as untrusted input — fluent/
expert/persuasive surface is not evidence of benignity (A40895/A40898/A40353/A41099/A42439); authenticate and
integrity-check agent-to-agent channels (A40224); and **harden every meta-decision a defense introduces**
(log per-client robustness scores, combine with server-side integrity checks — A39732). **Launch gate:**
enumerate the new trust surfaces each control adds and red-team *those*, not only the original threat.

---

## 4. Fail-open vs fail-closed

**Well-established.** The abstain/block response is itself weaponizable — a fail-*closed* control becomes a
denial-of-service vector under an availability-minded adversary. GhostCert (A37924) records certificate
abstentions *as* denial-of-service: a certified defense that refuses under uncertainty hands the attacker an
outage. Availability is thus a first-class safety property, not an efficiency afterthought — the theme is
independently developed in `Adversarial-ML-Attacks` (§6, §9.11): CP-FREEZER inflates cooperative-perception
latency >90× (>3 s/frame) on a real vehicle testbed and shows *integrity defenses are structurally useless when
detection outputs never arrive* (A37082), and the reasoning-DoS trio inflates compute while keeping answers
correct — repetitive generation (A40445), triggered CoT verbosity (~17× reasoning length on MATH-500, A40486),
and poly-base reasoning extension on o3 via indirect prompt injection (A40833, author-reported). **Capability
(to consume unbounded compute) vs Permission (bounded budget).**

**Emerging / contested.** Whether "fail-safe" degradation is reliable is unsettled. A40898 reports an
*over-manipulation backfire* — in a malicious-majority tool ecosystem several LLMs revert to a plain benign
tool — but the authors flag this as speculative, so it cannot be relied on as a designed fail-safe **(cross-paper
synthesis: do not architect on an emergent, un-guaranteed backoff)**.

**Implication (design + launch gate).** Neither pure fail-open nor pure fail-closed is safe: fail-open lets
attacks through; fail-closed under uncertainty is a DoS lever (A37924, A37082). Resolve it by (a) making the
*expensive* path bounded — enforce reasoning-token ceilings and worst-case per-message compute independent of
prompt-controlled instructions, and isolate per-sender cost in multi-agent fusion (A40445/A40486/A40833/A37082);
and (b) routing an *abstain* to a cheap human-approval or degraded-but-available path rather than a hard outage
for high-stakes actions (`AILLM-Safety` §14 human-approval-as-first-class-action; A41090's `ask-consent()`/
`refuse()`). **Launch gate:** measure worst-case latency/compute *under adversarial input*, and treat the
abstain rate as an availability metric, not only a safety metric. **Permission + Residual-risk.**

---

## 5. Detection & response

**Well-established (detection signals exist, at the *right* layer).** Useful detectors key on internal signals
rather than output labels: token-confidence sequence-locks (A40897 ConfGuard, top-1 prob only), attention-head
cosine similarity with no clean-twin model (A41080; author-reported BadNets 0.9921 vs benign 0.9149), middle-
layer gradient norms (A40587), embedding-manifold OOD scoring (A40301), Mahalanobis+spectral fusion (A40366),
and text-perturbation semantic-consistency + confidence drift (A40891). Perturb-and-compare behavioral-signature
detection needs only I/O or top-1 probabilities and is deployable client-side against an untrusted provider
(A40891/A40897). **Verification via internal Evidence.**

**Emerging (response = repair, not only reject).** Detect-then-*repair* / self-healing: GAN recovery for
split-federated poisoning (A40908 HealSplit), punish-distillation (A40902 BeDKD), test-time MLLM backdoor
purification with no retraining (A40867 PurMM, grounded in a deep-layer attention-hijacking finding), and
targeted knowledge erasure via model editing (A41145 ROME, author-reported extraction 65.2%→1.6% on small
open-weight models). These are runtime-enforcement primitives, not just alarms. **Capability removal as response.**

**Contested / where it fails.** Three ways. (1) **Detectors are routinely bypassed** — dormant backdoors evade
7 detectors by being absent from the inspected checkpoint (A39480); clean-label backdoors resist the standard
suite (A39935). (2) **Anomaly-by-volume fails against query-efficient attacks** — jailbreaks succeed at a
single query (A40919 ~60% T2I; A40465 single-query math+code wrapping) or ≤10–15 queries (A41058, A40554), so
detection cannot rely on many-query trajectories alone (`AILLM-Safety` §9.5). (3) **Purification is a layer, not
a gate** — UDAP beats DiffPure/GridPure on most attacks yet fails catastrophically on MIST (author-reported
FDFR 0.87 vs 0.11; A38345), and protective-perturbation "cloaks" are removed by trivial low-pass purification
(A41170, threatening the A41250/A41404 class). **Residual-risk survives detection.**

**Implication (design + launch gate).** Instrument multi-signal detection at internal layers (A40897/A41080/
A40587/A40301/A40366), pair reject-only with repair-capable response where a runtime primitive exists (A40908/
A40902/A40867/A41145), but never treat a purifier or a single detector as a trusted gate — combine with rate-
limiting, query monitoring, and out-of-band correctness signals (A38345, A37924). **Launch gate:** every
detector ships with a *bypass budget* — its false-negative rate against the specific evasions above, reported
as an absolute. **Verification + Residual-risk.**

---

## 6. Residual risk

**Well-established.** No defense in these corpora eliminates harm; calibrated non-elimination is honored across
all three. Leading inference-time LLM defenses leave material residual ASR: RAS ~31.27% (author-reported 51.86→
31.27%; A42191), the mechanistic contrastive-decoding fix leaves ~16.4% residual harmful on Qwen-3-8B despite
near-zero on the prefill metric (A40248), and the fullest MCP defense-in-depth still misses >50% (contextual
policy violation) / >76% (command injection) on its hardest classes (A41468, author-reported, Preliminary). The
strongest RAG-extraction defense evaluated still leaves an author-reported ~28% chunk-recovery rate (A40432,
57.16%→27.96% on one HealthCareMagic/Qwen-14B cell). On the offense side the residual is symmetric: Response
Attack's forged-history jailbreak reports avg ASR 94.8% across 8 models (A40840). **Residual-risk, stated as an
absolute.**

**Emerging.** The only formal guarantees in the corpora are narrow: CertMask's attack-agnostic O(n) certified
patch robustness (A37716, bounded by a *known* patch-size assumption), the randomized-smoothing ℓ2 radius of a
weight-lock (A37117), and a watermark forging-probability bound <1/2^128 at n=256 (A40915). Every one holds
inside a stated, narrow threat model; **no defense offers certified robustness against an unbounded adaptive adversary,
and no privacy defense offers a formal (ε,δ) DP guarantee** — the FL/SFDA privacy cluster (A37918, A40037,
A39337, A39939) treats leakage as *motivation* and never runs the cited inversion/MIA attacks, so its residual
leakage is unquantified. AntiDote (A40570) is explicitly framed as risk-*reduction*, not proof.

**Contested.** Whether relative-reduction headlines translate to acceptable absolute residual. A41134 reports
ASR reductions as *relative* percentages via an LLM-as-judge (GPT-4o, author-reported 86.34% agreement) — so
residual *absolute* ASR can remain high (`Defense-Mitigation` §8, reviewer synthesis). Best-defense rankings
also flip by model/attack: HumorReject reports prefix-injection Safety Rate avg 98.8% (Llama3) yet on the same
model under mismatched-generalization averages 84.0%, *below* Circuit Breaker's 89.0% (A41140, author-reported).

**Implication (design + launch gate).** **Budget for residual leakage and design compensating controls** —
pair any single defense with least-privilege, human approval on high-stakes actions, immutable audit, and an
incident path (A40432/A42191/A40248/A41468). **Launch gate:** report *absolute residual* ASR/CRR/leakage
against the tested attacks — never a relative reduction alone — and state the threat model it holds within.
Present empirical robustness as risk-reduction, never as a guarantee (A40570). **Residual-risk is the
first-class launch metric.**

---

## 7. Control degradation

**Well-established.** Controls decay along three axes. (1) **Safety-utility trade-off / over-refusal** — safety
is frequently "bought" with benign-refusal increases; the over-refusal / false-positive rate is foregrounded as
a first-class cost by A41074, A41140, A41152, A42191, A41498, A40543, A40553, A40887, A40248. RAS raised refusal
41.31→62.76% while cutting ASR (A42191, author-reported). Robustness-utility is sometimes a *proven* dichotomy:
model smoothness that improves query-robustness *hurts* transfer-robustness and vice-versa (A38416, author-
reported LR↓ +64% transfer / LR↑ +28% query, mutually exclusive), and defenses routinely cost clean accuracy
(A38121 ~15% CIDEr; A37117 authorized accuracy 86.2→73.9%; A39318 0.81→0.71). **Permission tightening degrades
Capability/utility.** (2) **Degradation under distribution shift** — continual-learning baselines competitive
in one cell collapse under Blurry task boundaries (A40129, e.g. GSA to near-random), and cross-corpus membership-
inference "near-perfect" results collapse to near-chance under strictly in-distribution evaluation (A39276,
CSA AUC 94%→51%, author-reported). (3) **Retraining does not remove implanted behavior — and can amplify it** —
P-Trojan is engineered so ordinary clean fine-tuning *reinforces* it (>99% persistence; forgetting-mitigation
*amplifies* persistence; A40295), corroborated by A39809/A40855; ShadeEdit's bias edits persist through clean
fine-tuning even where counterfactual edits partly revert (A40787). **The "retraining resets the threat"
assumption is false.**

**Emerging / contested.** Version drift makes results snapshot-dependent (A40445, A40726, A40833, A40877) — a
control validated against one commercial model version silently degrades as the underlying model updates
**(cross-paper synthesis)**. Whether temporal/architectural redundancy *is* robustness is contested: SNN
multi-timestep structure is argued *not* to be inherent robustness (A37479), and CTDG memory both *dilutes*
isolated perturbations and still suffers ~29% avg degradation (A37770) — the same property cuts both ways.

**Implication (design + launch gate).** Instrument over-refusal / false-positive rate as a first-class launch
metric against an *adaptive benign-ambiguous* set, not only ASR (A41074/A41140/A41152/A42191/A40543); do not
assume in-distribution robustness numbers hold OOD (A40129/A39276); and treat fine-tuning/retraining as a
*supply-chain trust boundary* that neither removes backdoors nor is revealed by accuracy — require *post-
finetuning* red-teaming on onboarding because pre-finetuning inspection is blind (A39480/A40295/A40787).
**Launch gate:** re-validate controls on each model-version bump; a control's expiry is the model it was tested
on. **Capability/Permission/Residual-risk.**

---

## 8. Operational monitoring

**Well-established.** *Monitor the right signal, not output accuracy* — the sharpest cross-category operational
lesson. Backdoors preserve clean accuracy and even plausible rationales and correct answers (A39935 ≤1% drop at
≤0.5% poison; A40409 rationale preserved; A40486 answers correct while reasoning inflates ~17×; A40867 clean
capability in shallow layers), and reasoning-DoS preserves correctness while inflating compute (A40445/A40486/
A40833) — so pass/fail and accuracy telemetry are blind to both. The actionable telemetry set, each grounded in
a card, spans: reasoning-token length/entropy per request (A40445/A40486/A40833), token-confidence-run events
(A40897), attention-head-similarity stats and deep-layer attention concentration (A41080/A40867), Mahalanobis/
manifold OOD scores (A40301/A40366), invalid-action rate as a runtime health signal (A39818), recursive
topic-expansion / memory-driven query patterns as extraction signatures (A40432), insertion of network/
exfiltration primitives in generated code — a concrete 12-behavior egress taxonomy including `send_email`,
external-URL fetch, clipboard/keyboard capture, file encryption (A41134) — tool-selection decisions with the
descriptions that drove them (A40898), full inter-agent transcripts with per-message provenance (A40224),
retrieval-evidence provenance + injection-cluster patterns (A40353), and query-trajectory monitoring for
try-and-test loops (A38127/A40587/A40726/A39997). **Evidence + Verification as continuous signals.**

**Emerging / contested.** Uncertainty and chain-of-thought as *monitoring tripwires* — per-decision entropy/MI
(A41088) and CoT n-gram drift (A42273) are candidate runtime signals but are *unvalidated as detectors* (no
ROC/PR), so log them for forensics, do not gate on them yet (`AILLM-Safety` §14). Reasoning itself is an attack
surface, not a safety guarantee: models voice ethical concern in CoT yet comply (A42273), and agents "overlook
safety considerations they themselves generated" (A41090 SCoT self-inconsistency) — **so "the model reasoned
about safety" is not Evidence of a safe outcome (cross-paper synthesis).** The near-universal reliance on a
single LLM-as-judge, sometimes circular, is an acknowledged confound across all three corpora (`AILLM-Safety`
§12; `Adversarial-ML-Attacks` §12; `Defense-Mitigation` §8).

**Implication (design + launch gate).** Emit structured trace fields for audit — toxicity source/category, filtered
directions/margins, removed-edge + reconstructed-query records, safety-CoT rationale (A36960/A37350/A40553/A40543/
A40836/A40866) — into an immutable, per-message-provenance log (A41468 Layer 4, A40224). **Launch gate:** do not
rely on a single automated judge for sign-off — validate against human agreement and evaluator-aware adversaries
(A40866 is a start, but is itself LLM-agent-based and untested against evaluator-gaming). **Evidence integrity of
the monitor is itself in scope.**

---

## 9. Incident playbooks

**Well-established (the containment primitives exist).** Targeted, non-retraining containment: model editing to
erase specific memorized/harmful content (A41145 ROME, author-reported 65.2%→1.6%, small open-weight models),
test-time backdoor purification (A40867), and directional punish-distillation on a small trusted clean set
(A40902/A40904). Evidence-logging and rollback is the shared incident story for every poisoning class — log
training-data/dataset/backbone provenance and hashes so a discovered backdoor is traceable and a clean
checkpoint is restorable (`Adversarial-ML-Attacks` §16). **Evidence enables response; the trusted clean set is
a security asset.**

**Emerging.** Provenance-and-attestation *over* adaptation as the primary supply-chain playbook — because
retraining does not remove backdoors and accuracy does not reveal them (A40295/A39809/A40855/A39935/A40409),
the response is crypto-provenance/attestation for weights, reused components, datasets, labels, and retrieval
corpora, plus post-finetuning red-teaming at onboarding (A39480). **Capability provenance as Evidence.**

**Contested / the dangerous edges.** The **delete/forget capability is security-sensitive and can backfire**:
behavioral non-recall is *not* proof of removal (A40272), the unlearning event itself can *leak* membership and
be abused for anti-forensic revocation (A39725/A39747), and ROME-style edits may be reversible by a defense-aware
attacker who re-tunes a soft prompt post-edit (A41145, reviewer synthesis). Guardian layers are themselves
attackable: the "using an LLM to defend an LLM agent" pattern makes the Guardian an injectable trust anchor that
needs adaptive-injection stress-testing and tamper-evident logging that current papers *assert but do not verify*
(A41468, reviewer synthesis); tamper-evidence and formal guarantees for audit layers are named as *absent*
(`AILLM-Safety` §17). **Verification of the incident tool is unproven.**

**Implication (design + launch gate).** Playbook entries: (1) **contain** via model editing / test-time
purification, validated against re-optimization *before* operational reliance (A41145/A40867). (2) **Preserve
evidence first** — retain forensic snapshots *before* honoring any delete/unlearn request; treat non-recall as
unverified until a relearning/extraction audit passes (A39747/A40272/A39725). (3) **Trace and roll back** from
provenance + immutable audit (A41468, `Adversarial-ML-Attacks` §16). (4) **Harden the Guardian itself** —
adaptive-injection test the defense agent and make its audit log tamper-evident (A41468). **Launch gate:**
independent validation of any framework-provided or single-paper defense on the target stack before reliance
(A42364 certifies *no* defense; single-study numbers are white-box/small-model until reproduced). **Evidence +
Residual-risk.**

---

## 10. Launch-gate synthesis (CPVER-tagged)

A consolidated set of gates, each traceable to the threads above. Every item is a *pre-deployment*
requirement, not a post-hoc metric.

1. **Adaptive red-team the whole pipeline, targeting the seams.** No "N-layer / SOTA-robust" claim ships without
   a defense-aware attacker that has the design, thresholds, and steering vectors and is allowed to attack the
   joins (A41108/A41144/A37924/A40905). *Permission, Verification, Residual-risk.*
2. **Bind actions to verified intent, not tool identity; treat all metadata/context as untrusted.** Pre-execution
   gate each planned tool call against the original request; require human approval for credential-reading
   actions regardless of requester (A40895/A40898/A41090/A41468). *Capability ≠ Permission.*
3. **Never gate solely on a certificate, score, explanation, or hidden state.** Add an out-of-band correctness
   channel (provenance, human review, ensemble/denoiser disagreement); hide verifier internals (σ) and rate-limit
   (A37924/A38340/A40584/A38853). *Verification ≠ Evidence.*
4. **Bound the expensive path; route abstain to a degraded-but-available path.** Enforce reasoning-token and
   per-message compute ceilings independent of prompt-controlled instructions; treat abstain rate as an
   availability metric (A37082/A40445/A40486/A40833/A37924). *Permission, Residual-risk.*
5. **Report absolute residual, not relative reduction, with its threat model.** State the surviving ASR/CRR/leakage
   against the tested attacks; present empirical robustness as risk-reduction, never proof (A40432/A42191/A40248/
   A41468/A40570). *Residual-risk.*
6. **Instrument over-refusal against an adaptive benign-ambiguous set**, and re-validate controls on each
   model-version bump (A41074/A41140/A42191/A40129/A39276; version drift A40445/A40726/A40833). *Capability/
   Permission trade-off.*
7. **Monitor internal signals, not accuracy; log to an immutable, per-message-provenance trace.** Reasoning-token,
   token-confidence-run, attention-concentration, OOD score, invalid-action rate, egress-primitive insertion,
   extraction-query patterns (A40897/A41080/A40867/A40301/A39818/A41134/A40432/A40224/A41468). Do not rely on a
   single LLM-judge for sign-off (A40866). *Evidence, Verification.*
8. **Provenance over adaptation for supply chain; post-finetuning red-team at onboarding.** Retraining does not
   remove backdoors and accuracy does not reveal them; attest weights/components/data/corpora (A40295/A39480/
   A40787/A39809). *Capability provenance = Evidence.*
9. **Preserve forensic evidence before any delete/unlearn; validate containment against re-optimization.**
   Non-recall is not proof of removal; unlearning can leak (A39747/A40272/A39725/A41145). *Evidence, Residual-risk.*
10. **Harden every new trust surface a control introduces, including the Guardian.** Robustness-aware aggregation
    weights, verifier scores, and the defense agent itself are attackable and need their own adaptive tests
    (A39732/A40584/A41468). *Permission, Verification.*

---

## 11. Bottom line (cross-paper synthesis)

Layering is necessary and empirically supported (A40432/A39732/A41134/A41468) — but the corpora, read together,
say the *dangerous belief is that layering composes into safety on its own*. It does not: adaptive whole-pipeline
attacks collapse per-component-robust stacks through their seams (A41108/A41144), every control adds a new
attackable trust surface (A39732/A40584/A40895), and no defense here is adaptively-evaluated, certified against
an adaptive adversary, or free of material residual (universal across §§1–10). The defensible posture is
defense-in-depth *aligned to the agent cognitive cycle*, with each layer treated as risk-reduction, the joins
red-teamed as the primary surface, absolute residual reported, and Capability firmly separated from Permission
and Verification firmly separated from Evidence. Everything ships with the calibrated qualifier the papers
themselves use: **reduced risk against the tested attacks under the evaluated threat model — requires production
validation.**
