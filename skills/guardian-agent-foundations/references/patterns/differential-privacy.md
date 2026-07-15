# Pattern: Differential Privacy

> **Scope of evidence.** This pattern is grounded in the AAAI-26 corpus synthesis `Privacy-Protection.md`
> and its underlying research cards, cross-referenced with the sibling patterns `privacy-preserving-training.md`
> (the training-lifecycle control that uses DP as one mechanism among several), `context-and-memory-isolation.md`,
> and `tamper-evident-traces.md`, plus `architecture-patterns.md` (P5 trajectory trace, P6 egress broker) and the
> cross-cutting chapter `cross-cutting/privacy.md`. This pattern is narrower than `privacy-preserving-training.md`:
> it governs the **differential-privacy mechanism and its (ε,δ)/RDP/GDP/LDP accounting discipline as a reusable
> control**, wherever a system releases a data-derived artifact — training a model, generating in-context
> demonstrations, sharing a steering vector, publishing a statistic, routing a prompt, or emitting a sequence of
> feedback-driven decisions.
>
> Load-bearing corpus papers: **A39051** (DP Linear Programming — DP that *guarantees* the private solution still
> satisfies the original hard constraints; the "DP coexists with a safety invariant" anchor), **A39510** (tight
> hidden-state DP-SGD/RDP analysis under smoothness — the "accounted DP done right" anchor, with the load-bearing
> caveat that the tight bound dies if intermediate checkpoints leak), **A37854** (µ-GDP dataset distillation
> exploiting post-processing immunity as a budget lever), **A38016** (DP synthetic-data generation + noise-tolerance
> pre-training), **A40838** (DP in-context learning with single-budget composition; ε = c·√(2T ln(1/δ))/(s·τ)),
> **A40117** (subspace-restricted DP fine-tuning — restrict noise to task-relevant structure), **A40720** (PrivSV —
> DP steering vectors under Metric-LDP after structure-aware reduction), **A40041** (PRISM — adaptive two-layer LDP
> prompt routing), **A39710** (DP-NCB — ε-DP bandits where the *decision sequence itself* is the leakage channel),
> **A40852** (crypto-assisted two-server DP training, semi-honest/non-colluding), **A39311 / A39582** (ε-DP / LDP
> whose guarantee is voided by *un-accounted* shared artifacts), and the load-bearing attack evidence **A37743**
> (GGSS-R) and **A39333** (Venom) — heuristic-noise / DP gradient perturbation is reconstructable under the
> evaluated conditions. Paper ids (e.g. `A39051`) are the stable corpus ids from the synthesis source map
> (Privacy-Protection §20).
>
> **Evidence integrity (non-negotiable).** Every numeric value below is **author-reported and not independently
> verified**; multiple cards flag truncated / OCR-approximate result tables, recorded here as author-stated. Where
> a card was silent the text says "not stated in paper". A formal (ε,δ)/RDP/GDP/LDP guarantee is cited as a
> **worst-case bound on the specific released artifact under the stated adjacency and trust model** — *adaptive-safe
> by construction, but not an executed-attack robustness result*. The synthesis' single most repeated caveat is
> **formal-guarantee-without-an-executed-attack is pervasive**, and **almost no DP paper here runs an empirical
> attack to corroborate that its chosen ε yields low real-world leakage** (Privacy-Protection §9.4, §12). Calibrated
> language only: "bounds worst-case per-record influence under the stated adjacency", "reduced membership/
> reconstruction success against the tested, non-adaptive attacks", "requires production validation" — never
> "secure / proven-safe / unbreakable / anonymized / eliminates". Reviewer-synthesis inferences (engineering
> practice added during review) are labeled *(reviewer synthesis)*.

---

## Problem addressed

Any artifact a system **derives from sensitive records and then releases** — a trained model, a fine-tuned
checkpoint, a synthetic dataset, an embedding, a steering vector, an aggregate statistic, or even a *sequence of
decisions* — leaks information about the individual records behind it. A determined counterparty with unbounded
auxiliary knowledge can run membership inference, reconstruction, attribute inference, or linkage against that
release. Redaction, masking, and "we only share gradients/digests" are **data-minimization, not a bound on
inference** (Privacy-Protection §2, §6); heuristic additive noise is **invertible** (`A37743`, `A39333`).

Differential privacy is the control that provides a **quantified, adversary-agnostic, worst-case bound** on how
much any single record can influence the released artifact. It is the one privacy primitive in the corpus that is
**adaptive-safe by construction**: the (ε,δ) guarantee holds against an adversary with arbitrary side information
and unbounded computation, requires no assumption about the attack, and is closed under post-processing and
composition (`A39051`, `A39510`, `A40838`, `A40117` — all instantiate this formal object). That is precisely why
it is the load-bearing property the defense papers argue for over heuristic perturbation: the *accounted*
guarantee — not the noise itself — is what constrains leakage (`A37854`, `A39510`; Privacy-Protection §9.1).

The problem this pattern solves is therefore narrower and more disciplined than "add noise for privacy". It is:
**how to instantiate an accounted DP mechanism correctly, log the privacy budget as configuration-of-record,
enforce that budget fail-closed, keep every shared artifact inside the accounting, and know exactly where the
guarantee stops** (leaked checkpoints, colluding servers, un-accounted side objects, and the gap between a formal
ε and real-world leakage). For a Guardian / agent stack the transferable primitives are: DP belongs on the
**training/telemetry/statistics-release path** and on **feedback-driven decision loops** (the policy sequence
itself leaks — `A39710`); the **privacy dial (ε/δ/µ/α/εd²/flip-probability) is governed configuration** with a
custody and exhaustion boundary; and a formal DP claim in product copy must be **validated against an executed
attack before it is trusted** (Privacy-Protection §14, §16). The sibling `privacy-preserving-training.md` covers
the broader training-lifecycle control (DP alongside MPC, secure aggregation, deletion verification); this pattern
is the DP mechanism itself.

## Applicable assets and attack surfaces

DP applies wherever a **data-derived artifact crosses a trust boundary**. Corpus-grounded surfaces:

- **Model parameters / checkpoints released as a service.** DP-SGD on smooth losses bounds record-level membership
  leakage from the released model (`A39510`, `A40117`, `A38016`). Critical surface caveat: the *tight* hidden-state
  bound holds only if **intermediate iterates are withheld** — publishing checkpoints, federated round updates, or
  early-stopping artifacts reverts you to looser composition accounting (`A39510`).
- **Training gradients on the FL/telemetry path.** The dominant reconstruction surface: individual pre-aggregation
  gradients embed the input and invert (`A37743`, `A39333`). DP clipping+calibrated-noise is the accounted control,
  but `A39333` shows analytic, noise-prior-free reconstruction of *DP-protected* pre-aggregation gradients under an
  honest-but-curious server (author-reported ImageNet LPIPS 0.340 vs 0.632, ASR 45% vs 2% at ε=10, δ=10⁻⁵), so the
  surface must be closed with secure aggregation, not DP alone (Privacy-Protection §9.1, §11).
- **Synthetic data / distilled sets / in-context demonstrations.** Releasing DP-generated synthetic data or DP
  synthetic ICL demonstrations lets downstream computation inherit the guarantee by post-processing at zero extra
  budget (`A37854`, `A38016`, `A40838`). The surface is the released synthetic artifact and any model behavior
  conditioned on it.
- **Embeddings, prototypes, and steering/activation vectors.** Face/template embeddings and steering vectors are
  invertible/identity-bearing secrets (cross-cutting/privacy Thread 2; `A40720`). `A40720` (PrivSV) treats a shared
  steering vector as a leakable artifact and applies Metric-LDP after structure-aware reduction. Prototypes shared
  in federated clustering carry the same risk (`A39311`).
- **Transmitted prompts / cloud-edge egress.** A user prompt sent to an untrusted cloud LLM leaks PHI/PII/intent;
  local (client-side) DP over the prompt or entity fields is the control (`A40041` two-layer LDP; note it transmits
  perturbed plaintext, so the guarantee is only as strong as the local randomized-response mechanism).
- **The decision / policy sequence of a feedback-driven loop.** In sequential decision-making (bandits, routing,
  personalization, tool-selection A/B loops) the **arm-selection sequence itself leaks** per-user outcomes even when
  the stored data is protected, because future choices depend on past private rewards (`A39710`). This is the
  closest DP surface to agent runtime.
- **Optimization outputs parameterized by sensitive data.** The solution of an LP/allocation formed from a
  sensitive database leaks that database; DP on the constraint-generating data protects it *while preserving
  feasibility* (`A39051`).
- **The privacy budget and mechanism keys themselves.** ε-budgets, LDP flip rates, clipping thresholds, and (for
  crypto-assisted DP) the secret-sharing/CKKS keys are governed configuration/credentials with custody, rotation,
  and an exhaustion/collusion incident boundary (`A40852`; Privacy-Protection §15).

## Threat model

DP is designed for an **inference/release adversary** who observes a released artifact (or its post-processing) and
tries to learn about the individual records behind it. Grounded threat classes:

- **Membership inference** — infer whether a specific record was in the private set from the released model,
  synthetic data, embedding, or steering vector (`A39510`, `A37854`, `A38016`, `A40117`, `A40720`; MIA is the
  corpus's default privacy oracle). The DP adjacency notion (add/remove one record) is exactly what this bounds.
- **Reconstruction / gradient inversion** — recover raw inputs from released gradients or intermediate
  representations (`A37743`, `A39333`). This is where heuristic noise fails and where accounted DP + secure
  aggregation is required.
- **Attribute inference / linkage / re-identification** — infer a sensitive attribute or re-identify a user across
  records, *including after naive PII scrubbing* (`A40720` notes PII-scrubbing is insufficient; `A40041` motivates
  masked-name re-identification via shared semantics).
- **Decision-sequence inference** — infer an individual's private outcome from observed shifts in a feedback-driven
  policy (`A39710`, citing a policy-leakage attack on deep RL as motivation).
- **Honest-but-curious server / provider** — the single most common counterparty in-corpus: follows the protocol
  but tries to infer inputs from its view, including access/branch patterns (`A40852`, `A39333` pre-aggregation
  interception, `A39311`/`A39582` untrusted-server DP).

**Adjacency and worst-case posture (the DP guarantee's actual claim).** DP is worst-case and adaptive-safe *by
construction*: the bound holds for any adversary regardless of side information, so no adaptive-attack experiment
is needed for the (ε,δ) statement itself to be valid (`A39051` confidence note). But the guarantee is precisely a
bound on the *specific released artifact under the specific adjacency* — it says nothing about surfaces the
accounting does not cover.

**Where the threat model breaks (critical, corpus-documented).** The DP bound is voided or bypassed when:
(1) **intermediate checkpoints leak**, breaking the hidden-state assumption (`A39510`); (2) a **trust anchor is
violated** — a colluding majority in MPC-assisted DP (`A40852`), or a central-DP curator that is not actually
trusted; (3) a **shared artifact is un-accounted** — structural graphs (`A39311`), mass values (`A39582`),
digests (`A39307`) released alongside the DP-protected object with no budget spent on them; (4) the mechanism is
**heuristic additive noise, not an accounted DP mechanism** — `A37743`'s own card notes additive noise without
clipping/accounting is not a DP mechanism and its attack does not falsify any (ε,δ) bound; (5) an individual
**pre-aggregation gradient is intercepted** where the DP is client-side and secure aggregation is absent
(`A39333`). Every relevant defense here is evaluated **non-adaptive**; the gap between a formal ε and measured
real-world leakage "requires production validation" (Privacy-Protection §12, §16).

## Control mechanism

A randomized mechanism M is **(ε,δ)-differentially private** if, for all datasets D, D′ that are *adjacent*
(differ by adding/removing one record) and all output sets S,
`Pr[M(D) ∈ S] ≤ e^ε · Pr[M(D′) ∈ S] + δ`. This is the formal object every corpus DP paper instantiates (variants:
pure ε-DP via Laplace — `A39710`; RDP for tight composition — `A39510`, `A38016`; f-DP / µ-GDP — `A37854`;
Metric/local-DP εd²-LDP — `A40720`, `A40041`, `A39582`). Its load-bearing properties:

- **Worst-case, adversary-agnostic bound.** ε caps how much any single record can shift the output distribution;
  the bound holds against unbounded auxiliary knowledge and computation (`A39051`, `A39510`).
- **Post-processing immunity.** Any function of a DP output is still DP at no extra budget — the key budget lever:
  route as much computation as possible through already-private (DP-generated) data so it costs zero (`A37854`,
  `A39051` "solving the private LP doesn't weaken privacy", `A40838` stage-2 inference free).
- **Composition.** Multiple DP releases compose; the total budget grows and must be accounted (sequential
  composition — `A39051` α_A+α_b+α_c split; RDP composition — `A39510`; single-budget composition over T tokens —
  `A40838` ε = c·√(2T ln(1/δ))/(s·τ)). Composition consumption is the budget-exhaustion incident boundary.

Applied as a control, DP is instantiated fail-closed and least-privilege:

```
release(artifact_from_D, ε_remaining, adjacency, accounted_artifacts) →
    { DP-noised artifact  |  DENY if budget exhausted / artifact un-accounted / trust anchor unmet }
    └─ clip to bound sensitivity → add calibrated noise (Laplace/Gaussian/planar) → account the spend →
       log the dial (ε,δ,clip,…) as config-of-record → constrain noise so safety invariants can't break
```

- **Bound sensitivity first (clipping), then calibrate noise to it.** Per-record/​per-sample clipping (gradient
  clip C in `A39510`/`A38016`; ℓ∞ logit clip in `A40838`; feature L2 clip in `A37854`) is what makes the noise
  scale finite and the guarantee real. Un-clipped "noise" is not DP.
- **Central vs local DP is a trust-boundary decision.** Central/global DP (trusted curator holds raw data, only the
  release must be DP) gives better utility; local DP (the aggregator is untrusted, each record is randomized before
  it leaves the client) gives a stronger per-user guarantee at a utility cost — `A39710` GDP-NCB vs LDP-NCB makes
  the trade explicit; `A40041`/`A40720`/`A39582` are LDP because the provider is untrusted.
- **Restrict noise to task-relevant structure** to escape the noise∝dimension curse and get formal privacy at
  deployable utility: subspace-restricted DP (`A40117` d→k), structure-aware compression before noise (`A40720`
  HCC), decompose-then-protect (`A39212`), single-residue reporting (`A40862`).
- **Constraint-preserving / bounded / one-sided noise** so a DP output cannot violate a hard safety invariant:
  `A39051`'s asymmetric one-sided-tightening truncated-Laplace *guarantees* the private LP solution stays inside the
  original feasible region (Thm 3.10); `A39710` clips private means to [0,1] as safe post-processing. This is the
  canonical "DP must coexist with a safety constraint" pattern (Privacy-Protection §6, §15).
- **Deterministic, fail-closed accounting.** Budget exhausted, an artifact un-accounted, an adjacency/clip
  undefined, or a trust anchor unmet → **release nothing** (or fall back to a *documented looser* guarantee, never
  to unprotected release) (reviewer synthesis, consistent with `A39510` incident guidance).

## Preconditions and trust assumptions

The guarantee is only as strong as these hold; each is a documented failure point:

- **A correct, bounded sensitivity.** Clipping thresholds / data bounds must be computed up front and actually bound
  per-record influence (`A39051` public data bounds Assumption 2.4; `A39510` clip C; `A37854` feature clip; `A40838`
  ℓ∞ clip). Wrong sensitivity → wrong noise → no real guarantee.
- **Correct, complete composition accounting for *every* shared artifact** — not just the headline object. Un-accounted
  structural graphs (`A39311`), mass values (`A39582`), or digests (`A39307`) released alongside the DP object void
  the claim (Privacy-Protection §9.4, §12).
- **The stated trust model actually holds.** Central DP requires a **trusted curator** who forms and privatizes the
  release (`A39051`, `A37854`); crypto-assisted two-server DP requires the **two servers do not collude** (`A40852`);
  hidden-state DP-SGD requires **intermediate checkpoints are not released** (`A39510`).
- **The mechanism is an accounted DP mechanism, not heuristic perturbation.** Additive noise without clipping and
  accounting is not DP and provides no worst-case bound (`A37743` card note).
- **Feasibility / structural preconditions for constraint-preserving DP.** `A39051` needs Slater's condition and a
  common feasible point across realizations; if the feasible region has empty interior, privacy and feasibility are
  "fundamentally incompatible" (Remark 2.3) — the mechanism must fail-closed there, not silently degrade.
- **A valid public prior where the method blends one.** DP-ICL and subspace/steering methods assume a genuinely
  public, private-set-independent blend/pretraining/subspace source (`A40838`, `A40117`, `A37854`); if that source
  is entangled with the private set the "free" post-processing steps are not actually private.
- **Budget custody and an exhaustion boundary.** ε-budgets and mechanism keys are governed configuration; repeated
  re-solves/releases on the same data consume budget by composition (`A39051` per-release, `A40852` keys,
  `A40041`/`A40720` per-session ε) — treat exhaustion as an incident boundary, not a soft limit.

## System architecture

A DP release gate sits between the sensitive data and any egress, with accounting as its spine (reviewer
synthesis, grounded in `A39051`/`A39510`/`A40838`; architecture-patterns P5/P6):

```
 sensitive data D ──► [Bound sensitivity]  per-record clip / public data bounds. Undefined ── fail ─► DENY
                          │
                          ▼
      [Choose trust model]  central (trusted curator) vs local (untrusted aggregator; randomize at source)
                          │                                               (A39710 GDP↔LDP; A40041/A40720 LDP)
                          ▼
      [Restrict noise to task structure]  subspace/compression/decompose BEFORE noise (A40117, A40720, A39212)
                          │
                          ▼
      [Calibrate + add noise]  Laplace/Gaussian/planar; bounded/one-sided if a safety invariant must hold
                          │                                               (A39051 feasibility; A39710 clip-to-[0,1])
                          ▼
      [Account the spend]  RDP/GDP/(ε,δ)/εd² composition over ALL shared artifacts; check ε_remaining ── over ─► DENY
                          │
                          ▼
      [Release]  DP artifact crosses the boundary; downstream is free by post-processing (A37854, A40838)
                          │
        ┌─────────────────┴───────────────────────┐
        ▼                                          ▼
 [Egress/isolation for un-DP'd artifacts]   [Config-of-record + audit]
   raw gradients/checkpoints/embeddings         ε, δ, µ/α, clip C, D, k, flip-prob, budget-split, trust model,
   never leave in the clear; secure             cumulative spend per release — logged as evidence (A40045,
   aggregation on the FL path (A39333).         A40838, A40041); constraint-violation rate (A39051).
```

- **The accounting is the sole authority for release** — an over-budget or un-accounted release is denied
  deterministically; an LLM may advise on sensitivity classification (e.g. `A40041` routing) but must never be the
  sole basis for spending budget (reviewer synthesis, mirroring the injectable-guardian caution in
  `policy-permission-gates`).
- **Put the DP boundary on the training/telemetry path with accounting for all shared artifacts** — never treat
  data locality as a privacy guarantee (`A39307`/`A39338` are the anti-pattern; Privacy-Protection §15).
- **Pair DP with secure aggregation on the FL gradient path** — DP alone does not close the pre-aggregation
  individual-gradient surface (`A39333`); secure aggregation hides the individual update that inversion needs.
- **Model the untrusted external model as inside the trust boundary** for cloud-edge/agentic inference: keep the
  raw artifact local, send only the DP-perturbed/abstracted version (`A40041`, `A40720`).

## Recommended implementation pattern

Deterministic, fail-closed, least-privilege — in priority order:

1. **Use an *accounted* DP mechanism, never heuristic noise.** Clip to bound sensitivity, then calibrate noise to
   that sensitivity, then account the spend. "Add some noise" without clipping+accounting is not DP (`A37743`).
2. **Log the privacy dial as configuration-of-record.** ε, δ, µ-GDP, RDP α, Metric-LDP εd², LDP flip probability,
   clip C, bounded-domain diameter D, subspace dim k, budget split — every release records its operating point
   (`A39051`, `A39510`, `A40838`, `A40041`, `A40720`; Privacy-Protection §13).
3. **Account *all* shared artifacts, not just the headline object.** If you release structural side objects,
   digests, masses, or auxiliary statistics, they consume budget too (`A39311`, `A39582`, `A39307`).
4. **Exploit post-processing immunity as a budget lever.** Route computation through already-private data so it
   costs zero; concentrate budget where sensitivity is highest (`A37854`, `A39051`, `A40838`).
5. **Restrict noise to task-relevant structure** before adding it — subspace/compression/decomposition — to get
   the formal guarantee at deployable utility (`A40117`, `A40720`, `A39212`, `A40862`).
6. **Use bounded / one-sided / direction-controlled noise where a hard invariant must hold**, so the DP output
   cannot violate feasibility or a valid range (`A39051` truncated-Laplace tightening; `A39710` clip-to-domain).
7. **Choose central vs local DP by the actual trust boundary.** Untrusted aggregator → local DP at source
   (stronger per-user, higher utility cost); trusted curator → central DP (better utility) (`A39710`).
8. **Prefer the release-only (hidden-state) posture and keep it real** — withhold intermediate checkpoints/iterates
   so the tight bound holds; if you must publish them, revert to composition accounting (`A39510`).
9. **Pair DP with secure aggregation on the gradient path** and never transmit raw per-client gradients over
   untrusted channels (`A39333`, `A37743`).
10. **Emit an auditable evidence record per privacy-relevant release** — ε consumed, mechanism parameters, trust
    model, and (for constrained optimization) the constraint-violation rate (`A40045`, `A40838`, `A39051`).
11. **Validate the chosen ε against an executed attack before trusting it** in product copy — a formal bound is not
    a measured leakage rate (`A40838`, `A40117`, `A40720` all lack executed attacks; Privacy-Protection §16).
12. **Fail-closed on budget exhaustion, un-accounted artifacts, undefined sensitivity, or an unmet trust anchor** —
    release nothing (or a documented looser guarantee), never unprotected data.

## Incorrect or fragile implementation patterns

- **Heuristic additive noise called "DP".** Gaussian/Laplacian perturbation without clipping and accounting is not
  a DP mechanism and is reconstructable (`A37743`, `A39333`); it provides no worst-case bound.
- **Data locality asserted as privacy.** "We only share gradients/submodels/digests, so it's private" — with no
  threat model, attack, or accounting — is data-minimization, and gradient sharing is a documented leakage vector
  (`A39307`, `A39338`; `A37743`/`A39333`).
- **Un-accounted side artifacts.** Releasing structural graphs (`A39311`), mass values (`A39582`), or digests
  (`A39307`) alongside the DP object without spending budget on them voids the claim.
- **Publishing intermediate checkpoints under a hidden-state bound.** The tight `A39510` guarantee assumes only the
  final model is released; checkpoint/round exposure silently reverts you to a looser realized guarantee.
- **Symmetric unbounded noise where a safety invariant must hold.** Standard Gaussian/Laplace can push a privatized
  solution *infeasible* w.r.t. the original constraints (up to 51% constraint violation for a naive baseline at
  ε=0.25 in `A39051`); use constraint-preserving one-sided noise instead.
- **DP on the FL gradient path *without* secure aggregation.** Individual pre-aggregation DP gradients still invert
  under an honest-but-curious server (`A39333`); DP alone does not close that surface.
- **Trusting the non-collusion / trusted-curator assumption blindly.** Two-server DP collapses if the servers
  collude (`A40852`); central DP collapses if the curator is not actually trusted.
- **Treating a formal ε as a measured leakage rate.** Almost no corpus DP paper runs an empirical attack at its
  chosen ε (`A40838`, `A40117`, `A40720`, `A38016`, `A39710`); shipping "ε-DP ⇒ safe" without a red-team is the
  recurring launch failure (Privacy-Protection §12, §16).
- **Naive masking / PII-scrubbing as a stand-in for DP.** Linkage via shared non-identifier semantics re-identifies
  masked records (`A40041`); PII-scrubbing before sharing an artifact is insufficient (`A40720`).
- **Protecting data-at-rest while leaving the decision sequence in the clear.** A feedback-driven policy leaks
  per-user outcomes even when the datastore is protected (`A39710`).
- **Fail-open on budget exhaustion or accounting uncertainty** — releasing anyway contradicts the fail-closed
  posture.

## Verification strategy

- **An executed-attack red-team is the launch gate for any DP claim at product scale** — the single most consistent
  corpus recommendation; a formal bound "requires production validation" before reliance (Privacy-Protection §12,
  §16; `A40838`/`A40117`/`A40720` cards).
- **Report the privacy *and* the utility/safety cost together.** For constrained optimization report ε *and*
  constraint-violation rate (`A39051`); for DP training report utility *and* MIA (`A39510`, `A37854`); baselines
  collapse at strong privacy (`A39582` goes "NA" at ε<1; `A39381` 30–60% utility degradation under perturbation).
- **Run membership inference at the chosen ε**, ideally at a fixed low-FPR operating point with variance rather than
  headline AUC (`A39510` ε̂-via-MIA over epochs/batch/diameter; `A37854`, `A40720`; cross-cutting/privacy Thread 1's
  TPR@low-FPR caution).
- **Run a reconstruction / gradient-inversion probe** on any released gradient/representation, using a *generative-
  prior* and a *noise-prior-free analytic* attacker as the baseline (`A37743` diffusion prior + its reusable RV
  architecture-audit metric; `A39333` analytic reconstruction), not only classical iterative inversion.
- **Audit accounting completeness** — enumerate every artifact that crosses the boundary and confirm each consumes
  budget (`A39311`, `A39582`, `A39307`).
- **Test the trust-boundary assumptions directly** — checkpoint-leak (`A39510`), server collusion (`A40852`),
  pre-aggregation interception without secure aggregation (`A39333`).
- **Verify constraint-preservation** — confirm the privatized output stays inside the true feasible/valid set
  (`A39051` Thm 3.10; `A39710` [0,1] clipping).
- **Report absolute residuals, not relative reductions** (residual MIA AUC / reconstruction ASR at the deployed ε).

## Metrics and thresholds

Track these families. **There is no validated universal ε/δ threshold in the corpus** — operating points are
author-reported, several truncated, and must be validated against an executed attack per deployment.

- **The privacy dial (configuration-of-record).** ε and δ (`A39051` ε∈[0.25,2] δ=0.1; `A39710` ε=0.2; `A39333`
  attacked at ε=10 δ=10⁻⁵), µ-GDP (`A37854`), RDP α (`A39510`), Metric-LDP εd² (`A40720`), LDP flip probability
  (`A39582`/`A39381`), clip C, bounded-domain diameter D∈{20,60,100} (`A39510`), subspace dim k (`A40117`), budget
  split (`A39051` α_A/α_b/α_c; `A40041` ε₁+ε₂). Log every one per release.
- **Cumulative budget spend and remaining budget** across all releases (composition) — exhaustion is the incident
  boundary (`A39051` per-solve, `A40838` per-token over T, `A40041`/`A40720` per-session).
- **Constraint-violation rate** for privatized constrained outputs — target **0** via constraint-preserving noise;
  a naive DP baseline hit up to 51% at ε=0.25 (`A39051`, author-reported).
- **Membership-inference success at the deployed ε** — report residual AUC/accuracy at a fixed low-FPR point
  (`A39510` ε̂; `A37854`; `A40720`). No corpus-validated "acceptable" threshold exists.
- **Reconstruction fidelity under a constructed inversion attack** — LPIPS/ASR/PSNR at the deployed ε; note DP
  gradient perturbation left author-reported LPIPS 0.340 / ASR 45% recoverable at ε=10 (`A39333`); `A37743`'s RV
  metric (RV = max‖∇ₓ∇_W F‖_F) as an architecture-level pre-deployment vulnerability score.
- **Utility cost at the operating ε** — accuracy/FID/regret vs a non-private baseline (`A37854` +11.6% util,
  ~20.18% lower FID `A38016`, `A39710` Nash regret; author-reported, some truncated). Expect and disclose baseline
  collapse at strong privacy.

## Test cases

Concrete, corpus-grounded cases the control must be exercised against:

1. **Membership inference on the released model/synthetic data/embedding at the deployed ε** — confirm residual
   MIA AUC at low FPR is within the disclosed bound (`A39510`, `A37854`, `A40117`, `A40720`).
2. **Gradient inversion on a released/​intercepted gradient** — generative-prior (`A37743`) and analytic noise-prior-
   free (`A39333`) reconstruction; confirm secure aggregation blocks the individual-update surface.
3. **Constraint-violation under privatized optimization** — verify the DP solution stays feasible (`A39051`);
   verify the empty-interior / Slater-failure case fails closed rather than releasing an infeasible answer.
4. **Budget exhaustion / composition across repeated releases** — re-solve/re-release on the same data until the
   budget is spent; confirm the gate denies further release (`A39051`, `A40838`).
5. **Un-accounted side-artifact release** — attempt to release a structural graph / mass value / digest alongside
   the DP object with no budget spent; confirm it is denied or accounted (`A39311`, `A39582`, `A39307`).
6. **Checkpoint-leak breaking the hidden-state bound** — publish an intermediate iterate and confirm the realized
   guarantee reverts to composition accounting, not the tight bound (`A39510`).
7. **Server-collusion in crypto-assisted DP** — collude the two servers and confirm the guarantee is understood to
   collapse (`A40852`).
8. **Decision-sequence inference** — infer a private reward from observed policy shifts in a feedback loop; confirm
   episodic DP release bounds it (`A39710`).
9. **Linkage / re-identification after masking** — attempt re-identification via shared non-identifier semantics
   against a masked/scrubbed artifact (`A40041`, `A40720`).
10. **Heuristic-noise vs accounted-DP differentiation** — confirm an un-clipped "noise" path is rejected as not a
    DP mechanism (`A37743`).
11. **Public-prior independence** — confirm the blend/pretraining/subspace source is genuinely independent of the
    private set; entangle it and confirm the "free" steps are flagged as no longer private (`A40838`, `A37854`,
    `A40117`).

## Adaptive adversarial tests

Beyond static cases — attackers who know the mechanism:

- **Generative-prior gradient inversion** with a frozen diffusion prior requiring no distributional alignment
  (`A37743`), and **analytic noise-prior-free reconstruction** that does not need the noise distribution (`A39333`)
  — "the attacker doesn't know our noise" is not protection.
- **Pipeline-aware / LiRA-style MIA** tuned to the specific DP mechanism rather than a generic fixed MIA — every
  corpus DP paper's empirical privacy is *non-adaptive* and likely an optimistic upper bound on protection
  (`A39510`, `A37854`, `A40720` reviewer notes; Privacy-Protection §12).
- **Multi-query composition / linkage drift** — correlate repeated LDP releases about the same entity to erode the
  per-release guarantee (`A40041` sequential-composition drift; `A40720` re-identification with auxiliary knowledge
  after PII removal).
- **Collusion beyond the stated trust anchor** — collude the "non-colluding" two servers (`A40852`) or model an
  actually-untrusted central curator.
- **Checkpoint / intermediate-state harvesting** — an adversary who accumulates released iterates to defeat the
  hidden-state assumption (`A39510`).
- **Metric-LDP metric-gaming** — exploit the metric-dependence of a Metric-LDP guarantee where the chosen metric is
  a poor proxy for the real privacy semantics (`A40720`; `A39212` MSE-is-imperfect-perceptual-privacy caveat).
- **Gaming a sensitivity-classifier that gates DP strength** — if an NER/LLM sensitivity classifier routes prompts
  to weaker protection, craft inputs it mis-classifies as low-sensitivity (`A40041` mis-routing risk).

## Telemetry requirements

Emit structured, tamper-evident records for every DP release (see `tamper-evident-traces.md`; architecture-patterns
P5):

- **Privacy dial per release** — ε, δ, µ/α/εd², clip C, bounded-domain D, subspace k, LDP flip probability, budget
  split, and the trust model (central/local, non-collusion assumption) — as configuration-of-record (`A39051`,
  `A39510`, `A40838`, `A40041`, `A40720`).
- **Cumulative budget accounting** — remaining vs consumed budget across all releases, with the composition method
  used; flag approaching exhaustion (`A39051`, `A40838`).
- **Per-artifact accounting ledger** — every artifact that crossed the boundary and the budget it consumed, to
  detect un-accounted side objects (`A39311`, `A39582`, `A39307`).
- **Constraint-violation rate** for privatized constrained outputs (`A39051`).
- **MIA ε̂ / residual-attack estimate** tracked over training/releases as an audit signal (`A39510`).
- **Access to raw un-DP'd artifacts** — raw per-client gradients, intermediate checkpoints, raw embeddings — logged
  and restricted; treat their exposure as a reconstruction incident (`A39333`, `A39510`).
- **Routing / decision-loop telemetry** — routing decisions + per-session ε for prompt routers (`A40041`);
  per-release events for decision loops (`A39710`); alert on repeated same-entity queries (linkage risk).
- **Mechanism-key custody events** for crypto-assisted DP (secret-share / CKKS keys) — issuance, rotation,
  suspected exposure (`A40852`).

## Failure handling

- **Fail-closed.** Budget exhausted, an artifact un-accounted, sensitivity/clip undefined, a public prior not
  verifiably independent, or a trust anchor unmet → **release nothing**; hold for human review if the task
  justifies it (reviewer synthesis; consistent with `A39510` incident guidance).
- **Degrade to *more* privacy, never to *no* privacy.** When uncertain, add more noise / switch to local DP / deny
  — never emit the unprotected artifact.
- **On checkpoint leak, recompute the realized guarantee** — fall back to composition-based (looser) accounting and
  restate the effective ε (`A39510`).
- **On empty-interior / Slater-failure**, treat privacy-and-feasibility as incompatible and refuse rather than
  release an infeasible constraint-violating answer (`A39051` Remark 2.3).
- **Constraint-preserving mechanisms as the safety backstop** — where a DP output feeds a system with invariants,
  use one-sided/bounded noise so the output *cannot* violate the invariant even under worst-case noise (`A39051`,
  `A39710`).
- **DP is preventive, not detective** — there is no runtime signal in a released artifact that reconstruction
  occurred (`A39333`); prevention (accounting + isolation + secure aggregation) is the control, so a failure in the
  gate must block release, not merely log it.

## Rollback and containment

- **A released DP artifact cannot be un-leaked** — ε is spent monotonically by composition; "rollback" means
  **halting further releases**, freezing the budget, and re-scoping, not recalling the artifact (reviewer synthesis
  from the composition property; `A39051`, `A40838`).
- **Budget freeze on suspected exhaustion or mis-accounting** — stop all releases against the affected dataset until
  the ledger is reconciled.
- **Isolate the un-DP'd surfaces** — cut access to raw gradients/checkpoints/embeddings and enforce secure
  aggregation on the FL path; interception of an individual pre-aggregation update is a reconstruction incident
  (`A39333`, `A39510`).
- **Rotate / revoke mechanism keys** for crypto-assisted DP on suspected exposure or collusion (`A40852`).
- **Constraint-preserving noise caps the safety blast radius** — even a mis-tuned ε cannot produce an infeasible /
  out-of-range output (`A39051`, `A39710`).
- **Attribution-complete audit for forensics** — the per-release ledger (dial + spend + artifacts + trust model)
  reconstructs what was released under which guarantee (architecture-patterns P5; `A40045`).

## Known bypasses

Demonstrated or corpus-supported bypasses of this pattern's weaker forms:

- **Heuristic-noise gradient perturbation → reconstructed.** `A37743` (diffusion prior) and `A39333` (analytic,
  noise-prior-free). Calibrated scope: `A37743` attacks *static additive noise* and its own card notes this does
  **not** falsify an (ε,δ)-DP bound (un-clipped noise isn't DP); `A39333` reconstructs *clip+calibrated-noise*
  DP-protected **pre-aggregation individual** gradients under an honest-but-curious server exploiting last-layer FC
  structure, with secure aggregation out of scope (author-reported LPIPS 0.340 vs 0.632, ASR 45% vs 2% at ε=10,
  δ=10⁻⁵). Both cards state DP still bounds worst-case leakage — this is not evidence that DP "has no value".
- **Leaked intermediate checkpoints → tight bound void.** The hidden-state guarantee reverts to looser composition
  accounting (`A39510`).
- **Colluding trust anchor → guarantee collapse.** Two-server DP under collusion (`A40852`); an untrusted central
  curator.
- **Un-accounted shared artifacts → silent leakage.** Structural graphs (`A39311`), masses (`A39582`), digests
  (`A39307`) released without budget.
- **Linkage / re-identification after masking or PII-scrubbing** — shared non-identifier semantics re-identify
  (`A40041`); PII-scrubbing is insufficient (`A40720`).
- **Decision-sequence leakage** — an unprotected feedback policy leaks per-user outcomes even with data-at-rest
  protection (`A39710`).
- **Non-adaptive evaluation overstates protection** — every DP defense here is tested non-adaptively; a pipeline-
  aware attacker may erode the empirical protection below reported numbers (Privacy-Protection §12).

Calibrated takeaway: the demonstrated bypasses hit either (a) noise that is **not an accounted DP mechanism**, or
(b) accounted DP operated **outside its stated trust boundary** (leaked checkpoints, collusion, un-accounted
objects, pre-aggregation interception without secure aggregation). The worst-case (ε,δ) bound for the *specific
released artifact under the stated adjacency* still holds where the trust boundary holds — but the gap between that
bound and measured real-world leakage **requires production validation**.

## Residual risks

- **The privacy–utility trade-off is intrinsic and dial-tunable, never eliminated.** No corpus paper claims to
  remove it; it recurs across every modality (Privacy-Protection §9.6). Strong privacy can collapse baselines
  (`A39582` "NA" at ε<1; `A39381` 30–60% degradation).
- **Formal ε ≠ measured leakage.** Almost no corpus DP paper corroborates its chosen ε with an executed attack
  (`A40838`, `A40117`, `A40720`, `A38016`, `A39710`); a bound is not a leakage rate (Privacy-Protection §12).
- **Adaptive, pipeline-aware attackers are under-evaluated** — deployed efficacy may be materially below reported,
  non-adaptive numbers.
- **Accounting completeness is assumed, not demonstrated** — an un-accounted side artifact leaks quietly
  (`A39311`, `A39582`, `A39307`).
- **The trust anchor is a standing assumption** — trusted-curator, non-collusion, and no-checkpoint-leak can each
  fail silently (`A39051`, `A40852`, `A39510`).
- **DP does not cover surfaces outside its adjacency** — it does not stop verbatim leakage of raw data placed in a
  prompt, does not remove already-learned knowledge (that is unlearning; see `context-and-memory-isolation.md`),
  and does not authorize actions.
- **Production/LLM-scale validation is outstanding** — several results are MNIST/2000-sample/single-backbone or
  synthetic (`A40852`, `A38016`, `A39710`, `A40838`); scaling behavior is asserted, not shown (Privacy-Protection
  §12, §16).

## Relevant research (stable paper ids from the syntheses/cards)

Primary (AAAI-26 corpus, Privacy-Protection synthesis):
- **A39051** — *Differentially Private Linear Programming: Reduced Sub-Optimality and Guaranteed Constraint
  Satisfaction*: one-sided-tightening truncated-Laplace DP that *guarantees* the private solution satisfies the
  original hard constraints (Thm 3.10; author-reported 65% sub-optimality reduction, 0 vs up to 51% constraint
  violation at ε=0.25); central DP, synthetic-only. The canonical "DP + hard safety invariant" anchor. *Evidence:
  Strong within its narrow theoretical scope.*
- **A39510** — *An Improved Privacy and Utility Analysis of DP-SGD with Bounded Domain and Smooth Losses*: tight
  hidden-state RDP + utility bounds under smoothness only; MIA-validated; code released. Load-bearing caveat: the
  tight bound dies if intermediate checkpoints leak. *Evidence: Strong (theory); Moderate empirical realism
  (single MIA family).*
- **A37854** — *DP-GenG: DP Dataset Distillation Guided by DP-Generated Data*: µ-GDP + post-processing immunity as a
  budget lever (author-reported +11.6% utility, MIA-robust); image-domain, non-adaptive MIA, truncated tables.
  *Evidence: Moderate.*
- **A38016** — *DP synthetic-image generation + noise-tolerance pre-training (AMP)*: RDP-accounted DP-SGD synthesis
  (author-reported ~20.18% lower FID, ~5.45% higher accuracy); fixed MIA probe, low-resolution scope. *Evidence:
  Moderate.*
- **A40838** — *Privacy-Preserving In-Context-Learning Framework for LLMs*: (ε,δ)-DP synthetic ICL demonstrations,
  single-budget composition (ε = c·√(2T ln(1/δ))/(s·τ)), linear decoding cost; no executed attack. *Evidence:
  Moderate.*
- **A40117** — *Subspace-restricted DP fine-tuning (DP-SFT)*: restrict noise to a k-dim task subspace (d→k),
  transferable from public data; formal guarantee, no executed attack. *Evidence: Moderate.*
- **A40720** — *PrivSV: DP steering vectors via structure-aware reduction under Metric-LDP (εd²-LDP)*: treats a
  shared steering vector as a leakable artifact; MIA-evaluated; PII-scrubbing insufficient; metric-dependence
  caveat. *Evidence: Moderate.*
- **A40041** — *PRISM: Privacy-Aware Routing for Cloud–Edge LLM Inference*: adaptive two-layer LDP (ε₁+ε₂) with
  entity-level budget split, keep high-sensitivity prompts local; no executed inference/linkage attack, synthetic
  data. *Evidence: Moderate (systems); privacy side weakest link.*
- **A39710** — *DP-NCB: Privacy-Preserving Fair Bandits*: ε-DP (Laplace) GDP/LDP bandits; the **decision/policy
  sequence itself is the leakage channel**; clip-to-[0,1] as safe post-processing; synthetic, no empirical privacy
  attack. *Evidence: Moderate.*
- **A40852** — *Crypto-assisted two-server DP training (2PC-zCDP)*: semi-honest / non-colluding two-server DP with a
  bounded activation (author-reported 642.78 s vs 173,960.9 s); collapses under collusion; unnamed datasets.
  *Evidence: Moderate.*
- **A39311** — *SPP-FGC: ε-DP on prototypes/structure in federated clustering*: un-accounted structural-graph
  caveat. *Evidence: Moderate.*
- **A39582** — *LDP federated method*: baselines go "NA" at ε<1; un-accounted mass-value caveat. *Evidence:
  Moderate.*
- **A37743** — *GGSS-R: diffusion-prior gradient inversion of noise-perturbed gradients*: load-bearing "heuristic
  noise is bypassable"; contributes the reusable RV architecture-audit metric; its own card notes additive noise
  without accounting is not a DP mechanism (does not falsify (ε,δ)-DP). *Evidence: Moderate.*
- **A39333** — *Venom: analytic, noise-prior-free reconstruction from DP-protected gradients* (author-reported
  LPIPS 0.340 vs 0.632, ASR 45% vs 2% at ε=10, δ=10⁻⁵); pre-aggregation interception, last-layer dependence,
  secure aggregation out of scope. *Evidence: Moderate.*

Supporting (cited inline): **A39212** (decompose-then-protect for split-inference reconstruction; FSInfo/Fisher-
calibrated noise), **A40862** (single-message LDP; Bayesian DRA as a design axis), **A39381** (LDP utility recovery;
30–60% degradation), **A39307 / A39338** (privacy-by-data-locality asserted but unevaluated — the anti-pattern),
**A40045** (auditable per-release evidence record).

Reviewer-synthesis cross-references (skill artifacts, **not** AAAI corpus papers): `privacy-preserving-training.md`
(the training-lifecycle sibling that uses DP alongside MPC/secure-aggregation/deletion-verification),
`cross-cutting/privacy.md` (Thread 1 MIA-as-oracle, Thread 3 gradient reconstruction), `tamper-evident-traces.md`
(the evidence-record substrate), `architecture-patterns.md` P5/P6, `glossary.md`.

## Evidence strength

- **The formal guarantee is the strongest kind of privacy evidence in the corpus — and is worst-case valid without
  an executed attack.** A correctly-accounted (ε,δ)/RDP/GDP/LDP bound holds against an adaptive adversary with
  unbounded auxiliary knowledge *by construction*; `A39051`'s card explicitly grades it "Strong" precisely because
  no adaptive-attack experiment is required for the bound to be valid. This is the DP family's genuine advantage
  over heuristic and by-construction schemes (Privacy-Protection §5, §9.4).
- **The convergent load-bearing lesson is that *accounted* DP, not the noise, is the property that protects.** Two
  independent defense anchors (`A39510`, `A37854`) argue this in spirit, and two methodologically independent attack
  papers (`A37743`, `A39333`) show that heuristic/un-accounted noise perturbation is reconstructable under the
  evaluated conditions — the corpus's single most-replicated attack finding (Privacy-Protection §9.1). Treat this
  convergence as a strong *design* signal.
- **But the bound is only as strong as its accounting and trust boundary, and almost never corroborated by a
  measured leakage rate.** Formal-guarantee-without-an-executed-attack is pervasive (`A40838`, `A40117`, `A40720`,
  `A38016`, `A39710`); un-accounted artifacts (`A39311`, `A39582`, `A39307`), leaked checkpoints (`A39510`), and
  collusion (`A40852`) each void it. The gap between a formal ε and real-world leakage **requires production
  validation** (Privacy-Protection §12, §16).
- **All numeric values are author-reported, non-adaptive, and several are truncated/OCR-approximate** — treat them
  as directional, not verified. Deterministic, fail-closed, least-privilege accounting is reviewer-synthesis best
  practice grounded in these papers' failure modes, not itself a paper-measured result.

## When NOT to use this pattern

- **For the action-authorization decision.** DP bounds *inference from a released artifact*; it does not decide
  whether an agent may take an action — that is `policy-permission-gates` / `tool-capability-isolation` /
  `human-approval-consequential-actions`. Do not substitute DP for an action gate.
- **Against prompt injection, tool abuse, or credential misuse.** Those are `prompt-injection-containment`,
  `tool-capability-isolation`, and `least-privilege-credentials`; DP is orthogonal (Privacy-Protection §1 — only a
  thin minority of DP work sits on the agent execution surface).
- **To remove already-learned knowledge or purge memory.** "Delete my data" from a trained model is machine
  unlearning / representation-level erasure (see `context-and-memory-isolation.md` and the unlearning evidence
  A41120/A40047/A39373), not DP — DP bounds training-time leakage prospectively, it does not un-learn.
- **When the record must be used in the clear.** DP protects *aggregate/statistical* release under an add/remove-one
  adjacency; it cannot protect a single record that a task must consume verbatim, and it does not stop verbatim
  leakage of raw data placed directly into a prompt.
- **When the utility cost is unacceptable for the scale or constraints.** Strong ε collapses small-n or tightly-
  constrained problems (`A39582` at ε<1; `A39051` empty-interior feasibility incompatibility, Remark 2.3); prefer
  a different trust model (secure computation) or elimination of the release where DP would destroy utility.
- **As a rename for heuristic noise.** If you are not clipping to bound sensitivity and accounting the budget, you
  are not doing DP and get none of its guarantees (`A37743`) — do not label it "differentially private".
- **Where the DP trust boundary cannot be established.** No trusted curator (for central DP), a colluding-capable
  server pair (for crypto-assisted DP), unavoidable checkpoint publication (for hidden-state bounds), or
  un-accountable side artifacts — establish the boundary first, or use secure aggregation / MPC and treat the
  missing anchor as a named residual risk, rather than shipping a DP claim the deployment cannot support.
