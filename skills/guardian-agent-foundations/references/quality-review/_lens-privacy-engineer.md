# Quality Review — Lens: Privacy Engineer

**Reviewer lens.** Membership-inference / model-&-embedding inversion / DP / federated / leakage.
**Question I was asked to answer.** Are privacy claims tied to a budget + threat model, and are
composition / repeated-query risks stated?

**Headline verdict.** Yes — overwhelmingly. This is the strongest-disciplined slice of the base I
read. Every privacy claim I checked is scoped to a named threat model and trust boundary, carries the
"formal-guarantee-without-an-executed-attack" caveat, and composition/repeated-query risk gets a
dedicated cross-cutting thread (`cross-cutting/privacy.md` Thread 9). The base is **solid**; the
findings below are calibration and completeness gaps a DP/FL specialist would flag before a launch
claim ships — not fabrications, and none rises to a factual error in the papers as cited.

Files read in full: `syntheses/Privacy-Protection.md`, `patterns/differential-privacy.md`,
`patterns/privacy-preserving-training.md`, `patterns/privacy-preserving-inference.md`,
`patterns/model-extraction-defenses.md`, `cross-cutting/privacy.md`; plus `ontology.md` and
`source-index/relevance-triage.md` heads.

---

## 1. Findings

### F1 — [MAJOR] The load-bearing "DP gradient perturbation is bypassable" evidence is demonstrated only at ε=10 (a near-vacuous budget), and no file surfaces this.
- **Where.** `patterns/differential-privacy.md` §Known bypasses (the A39333/Venom + A37743 lines,
  "ASR 45% vs 2% at ε=10, δ=10⁻⁵"), also §Metrics/thresholds, §Evidence strength;
  `cross-cutting/privacy.md` Thread 3; `syntheses/Privacy-Protection.md` §4, §9.1, §18.
- **Problem.** The corpus's single most-replicated attack finding — cited ~a dozen times as the
  reason to distrust noised gradients — is anchored on A39333/A37743 at **ε=10, δ=10⁻⁵**. ε=10 gives
  an adversary an e¹⁰ ≈ 22,000× likelihood-ratio budget; it is essentially *no* meaningful DP. The
  files correctly caveat the *surface* (pre-aggregation individual gradients, secure aggregation out
  of scope, "this does not falsify (ε,δ)-DP") but **never caveat the budget magnitude**. A privacy
  engineer skimming "reconstruction succeeds under DP at ε=10" can wrongly generalize to "accounted
  DP is bypassable," when the honest reading is "DP at a near-useless budget is bypassable, and
  reconstruction at deployable budgets (ε≤1) is *not demonstrated in-corpus*." Confirmed absent: a
  grep for weak/large-budget framing across the DP patterns returns nothing.
- **Fix.** Annotate every `ε=10` citation with a one-clause budget note ("ε=10 is a very weak
  budget; the corpus does **not** demonstrate reconstruction at ε≤1") and add "reconstruction-vs-ε
  curve at deployable budgets" to `differential-privacy.md` §Residual risks / §Open items. This
  turns an over-general scare into an accurate, scoped one.

### F2 — [MAJOR] DP adjacency is stated as record/example-level throughout, but the base applies DP to user-level problems (RTBF, "delete my data", agent-memory purge, federated personalization) without ever flagging the record↔user mismatch.
- **Where.** `patterns/differential-privacy.md` §Control mechanism (adjacency = "differ by
  adding/removing one record") and §Applicable assets ("record-level membership leakage");
  `patterns/privacy-preserving-training.md` L111 ("record-level inference"); the RTBF / memory-purge
  framing in `differential-privacy.md` §When NOT to use and `cross-cutting/privacy.md` Thread 1/launch
  gates.
- **Problem.** "Add/remove one record" is **example-level** DP. But the product framings these
  patterns feed — right-to-be-forgotten, "delete *my* data," per-user personalization, FL where a
  client = a person — have a privacy unit of a *person*, i.e. **user-level (group) DP**, which at the
  same ε is weaker by roughly the group size (a user contributing k records needs kε, or k× the
  noise). Confirmed absent: no file in the base mentions "user-level," "group privacy," or the
  record↔user gap in the DP sense (the only "user-level" hits are the unrelated multi-agent
  containment topic). A team could log a record-level ε and let a user believe "*I* am protected."
- **Fix.** In `differential-privacy.md` §Control mechanism and §Preconditions, state explicitly that
  the quoted adjacency is example-level; that RTBF / FL / personalization generally require user-level
  (group) DP; and require every logged ε to record **which unit** (per-record vs per-user) it bounds.

### F3 — [MAJOR] No privacy-amplification-by-subsampling and no multi-round FL/DP-SGD composition recipe — the single most impactful factor in real DP-SGD budget accounting is missing.
- **Where.** `patterns/differential-privacy.md` §Control mechanism/§Composition (lists RDP/GDP/(ε,δ)
  and single-budget-over-T-tokens, but not subsampling); `patterns/privacy-preserving-training.md`
  §Control mechanism (DP-SGD on the FL path); `cross-cutting/privacy.md` Thread 9 (flags per-round
  composition "not analyzed" but supplies no recipe).
- **Problem.** Real DP-SGD ε is dominated by (a) the moments/RDP accountant over **many training
  rounds** and (b) **privacy amplification by subsampling** (Poisson/minibatch sampling can reduce
  effective ε by an order of magnitude). The base names composition abstractly and even flags the FL
  per-round gap, but never states that a single-release ε is *not* the deployed ε under iterated
  rounds, and never mentions subsampling amplification at all. For a DP/FL lens this is the core
  accounting primitive, and its absence means the "log the ε dial" discipline can log the wrong number.
- **Fix.** Add subsampling amplification and multi-round RDP composition to
  `differential-privacy.md` §Composition and `privacy-preserving-training.md` §Recommended pattern:
  the deployed budget is the composed, subsampling-adjusted ε over all rounds, and the accountant —
  not a per-step σ — is the authority.

### F4 — [MINOR] Central-DP ε, local-DP ε, and Metric-LDP εd² are enumerated in one "privacy dial" bullet, inviting apples-to-oranges comparison.
- **Where.** `patterns/differential-privacy.md` §Metrics and thresholds, "The privacy dial" bullet
  (A39051 ε∈[0.25,2]; A39710 ε=0.2; A39333 attacked at ε=10; A40720 Metric-LDP εd²; A39582/A39381
  LDP flip-probability) — all listed together.
- **Problem.** A local-DP ε is far weaker than a central-DP ε at the same numeric value, and εd²
  (Metric-LDP) is a different unit entirely. The surrounding prose *does* distinguish central vs local
  as a trust-boundary decision, so this is a presentation slip, not a conceptual one — but a reader
  lifting the bullet as a comparison table will mis-rank guarantees.
- **Fix.** Tag each ε with its DP variant and add one clause: "these ε are not comparable across
  central / local / metric DP; compare only within a variant."

### F5 — [MINOR] δ=10⁻⁵ is quoted repeatedly but never paired with N, so the reader can't judge whether δ is safe.
- **Where.** `patterns/differential-privacy.md` §Metrics ("δ (`A39333` attacked at ε=10 δ=10⁻⁵)"),
  §Telemetry (logs δ as config-of-record); `cross-cutting/privacy.md` Thread 3/4.
- **Problem.** The standard guideline is δ ≪ 1/N (δ ≥ 1/N admits mechanisms that blatantly leak
  individual records with probability δ). The base treats δ as a loggable dial but never states the
  δ-vs-N relationship or records the dataset size, so a logged δ=10⁻⁵ is un-auditable for safety.
- **Fix.** Add "log N alongside δ; require δ ≪ 1/N (ideally ≤ 1/N^{1.1})" to the config-of-record
  discipline in §Telemetry and §Preconditions.

### F6 — [MINOR] The TPR@low-FPR MIA discipline is required in `cross-cutting/privacy.md` and `differential-privacy.md` but not propagated to `privacy-preserving-inference.md`.
- **Where.** `cross-cutting/privacy.md` Thread 1 ("report at a fixed low-FPR operating point with
  variance, not headline AUC") and `differential-privacy.md` §Verification/§Metrics both enforce it;
  `patterns/privacy-preserving-inference.md` §Metrics/§Verification (the "Executed-attack success rate
  (MIA / attribute / reconstruction) … track and drive down" bullet) omits it.
- **Problem.** The inference pattern is where MIA-on-the-transmitted-artifact is actually run, yet it
  reverts to an AUC-style "drive it down" framing — letting the weaker headline-AUC evaluation back
  in on the one surface where the strong discipline matters most.
- **Fix.** Cross-reference Thread 1 in `privacy-preserving-inference.md` §Metrics: report MIA at a
  fixed low-FPR operating point with variance, not headline AUC.

---

## 2. Done well

- **Composition / repeated-query is a first-class, dedicated thread** (`cross-cutting/privacy.md`
  Thread 9) and it is genuinely comprehensive: cumulative budget as the accounting *unit* across all
  egressed artifacts + repeated queries; extraction via low-volume information-dense query sets
  (A39671, ~100 vs ~5,000 queries) defeating volume-only rate-limits; single-query former-membership
  (A40047); and — rarely stated anywhere — **deployment-operations composition**, i.e. a routine
  fine-tune *after* unlearning re-composes forgotten data back in (A41120, A40343). This directly and
  correctly answers my lens question.
- **The "heuristic/un-clipped noise is NOT a DP mechanism, and the gradient-inversion attacks do not
  falsify any (ε,δ) bound" distinction is stated precisely and repeatedly** (`differential-privacy.md`
  §Threat-model-breaks pt.4, §Incorrect patterns, §Known bypasses). This is the exact error most
  write-ups make (conflating "an attack inverted a noised gradient" with "DP is broken"), and the base
  gets it right — including A37743's own theory that noise raises but never eliminates the
  reconstruction-error bound.
- **MIA is treated as a two-sided, gameable oracle, not a scalar truth** (`cross-cutting/privacy.md`
  Thread 1): behavioral MIA parity *understates* leakage (A39373 gaming), while distribution mismatch
  *inflates* it (A39276, CSA 94%→51% under in-distribution eval), with TPR@low-FPR + variance required
  and an artifact-only MIA mandated because output suppression is not a boundary (A40839 PIPRA). That
  is a sophisticated, correct read of the membership-inference literature.

## 3. Biggest risk from my seat

The base is solid on threat-model scoping and composition; the load-bearing risk is a **unit/strength
mismatch it never names** — its DP evidence is anchored at a weak budget (ε=10) and *record-level*
adjacency, while the product framings it feeds (RTBF, "delete my data," agent-memory purge, "data
stays local" FL) are *user-level* problems evaluated at deployable budgets, so a team can faithfully
log the ε dial and still ship a guarantee whose unit and strength don't match what a user thinks
"delete me / my data is private" means.
