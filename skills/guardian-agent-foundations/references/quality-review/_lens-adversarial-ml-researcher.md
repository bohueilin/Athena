# Quality Review — Lens: Adversarial ML Researcher

> **Reviewer seat.** Evasion / poisoning / backdoor / transferability + certified-vs-empirical robustness.
> Question I held the base to: *are robustness claims scoped to the tested threat model and to adaptive attacks?*
> **Slice read:** syntheses `AILLM-Safety`, `Adversarial-ML-Attacks` (full), `Defense-Mitigation` (full); patterns
> `adversarial-training`, `backdoor-detection`, `adaptive-red-teaming`, `evaluation-holdout-protection`; plus
> `ontology.md`, `source-index/relevance-triage.md`, and targeted cross-file consistency greps. Paths below are
> relative to `…/guardian-agent-foundations/references/`.
>
> **Headline:** the base is *solid* on my lens — genuinely calibrated, threat-model-scoped, and obsessive about
> flagging non-adaptive evaluation. Every finding below is a **precision / consistency / cross-linking** defect in
> the *certified-robustness* story, not a fabricated flaw. There are no "empirical result sold as a guarantee"
> problems; the KB leans the other way.

---

## 1. Findings

### F1 — [BLOCKING] "certified robustness against an adaptive adversary" is technically false as written, and self-contradicts the KB's own CertMask description
**Where:** `syntheses/Adversarial-ML-Attacks.md` §1 (lines 62–63) and §17 (lines 604–605); propagated verbatim to
`cross-cutting/adversarial-ml.md:300`, `cross-cutting/defense-in-depth.md:243`,
`patterns/evaluation-holdout-protection.md:38` & `:456`, `patterns/backdoor-detection.md:592`.

**Problem.** The headline sentence — *"No defense in the corpus offers certified robustness against an adaptive
adversary"* — is wrong to the exact audience this KB is written for. Certified robustness (randomized smoothing,
patch certification) is by construction a **worst-case, attack-agnostic** guarantee: it holds against *any*
adversary, including a fully defense-aware/adaptive one, **so long as the perturbation stays inside the certified
set** (ℓ2 radius / known patch size). The same synthesis describes CertMask (A37716) as *"attack-agnostic … certified
patch robustness"* (§5 line 177–178) and A37117 as *"ℓ2-certified within the modeled radius"* (line 180) — i.e. it
*already asserts* adaptive-inclusive guarantees within a bound, then two lines earlier denies any exist. A sophisticated
adversarial-ML reader flags this on first pass, and it corrodes trust in the rest of the KB. Notably,
`patterns/adaptive-red-teaming.md` (lines 43, 143, 613) **already uses the correct form** — *"unbounded adaptive
adversary"* — proving the KB knows the right phrasing; five other sites just didn't inherit it.

**Fix.** Global replace the unqualified claim with the bounded one everywhere it appears:
*"No defense in the corpus offers certified robustness against an **unbounded** adaptive adversary (i.e. one permitted
to exceed the certified threat model — larger radius/patch, a different norm, or a different surface)."* This makes the
sentence true, reconciles it with the CertMask/A37117 characterization, and matches the language `adaptive-red-teaming.md`
already ships. One-word class of fix; high credibility payoff.

---

### F2 — [MAJOR] GhostCert (A37924, "Breaking Certified Defences with Ghost Certificates") is not cross-linked in the high-traffic robustness files where certified defenses are promoted or where "certificate ≠ oracle" is argued
**Where (omissions):** `syntheses/Adversarial-ML-Attacks.md` §5/§17/§18 (CertMask A37716 & A37117 presented as the
corpus's cleanest `strong` certified defenses, caveated *only* as "narrow threat model"); `patterns/adaptive-red-teaming.md`
oracle-gaming section (lines 114, 135–136, 268–269 cite A40584/A40916/A40866/A38340 but **not** A37924);
`patterns/evaluation-holdout-protection.md` (line 46 lists "a robustness certificate" as a gameable measurement, and
argues "certificate ≠ correctness oracle" throughout, but grounds it in A40584/A40916/A38127 — never A37924);
`patterns/adversarial-training.md` (A37716/A37117 cited as "adjacent certified defenses" with no spoofing caveat).

**Problem.** A37924 is the single most on-point result in the whole corpus for my lens: a white-box, known-σ adversary
**spoofs randomized-smoothing certificates so a *wrong* class receives a large certified radius** (author-reported ASR
30–100%; abstentions become DoS; RS+ResNet50 / Smoothed-Ensemble / DensePure, per `syntheses/Defense-Mitigation.md`
lines 78–79, 108, 243–246, 485–487). That is *exactly* the "your verification artifact can be gamed" thesis the
adaptive-red-teaming and evaluation-holdout patterns are built on — and it targets a **certificate**, the one artifact
those patterns otherwise treat as the trustworthy end of the spectrum. The KB *has* the material and uses it correctly
in `cross-cutting/defense-in-depth.md` (lines 33, 104, 168, 375, 379–384, which cleanly connect A37924 to
certificate-gating and to A41108/A40905). The defect is that it's **siloed by corpus folder**: the reader who goes to
the Adversarial-ML synthesis or the adaptive-RT / eval-holdout patterns to evaluate certified defenses never sees it,
and could over-trust CertMask/A37117 certificates.

**Fix.** (a) In `Adversarial-ML-Attacks.md` §5 and §18 where A37716/A37117 are promoted, add a one-line cross-ref:
*"Certificates are label-correctness-blind: GhostCert (A37924, `Defense-Mitigation`) spoofs randomized-smoothing
certificates to assign a large radius to a wrong class — a certificate bounds perturbation, it does not verify the
label."* (b) Add A37924 to the oracle-gaming test list in `adaptive-red-teaming.md` §"Threat model"/§"Test cases"
(alongside A40584/A40916) as *the* certificate-as-oracle gaming case. (c) Add it to
`evaluation-holdout-protection.md` where "a robustness certificate" is named as a gameable measurement (line 46) and
in the "certificate ≠ correctness oracle" discussion.

---

### F3 — [MINOR] Citation-fidelity slip: `adaptive-red-teaming.md` attributes "unbounded adaptive adversary" to "Adversarial §1", but §1 does not contain "unbounded"
**Where:** `patterns/adaptive-red-teaming.md:43` (*"…certified robustness against an unbounded adaptive adversary
(Adversarial §1)"*) vs the actual `Adversarial-ML-Attacks.md` §1 text (lines 62–63, no "unbounded").

**Problem.** The pattern silently *corrected* the synthesis (good instinct — see F1) but kept the citation, so a
load-bearing qualifier now traces to a source that doesn't say it. Under this KB's own strict evidence-integrity
contract ("every claim traces to a paper card / synthesis section"), that's a traceability defect, however benign.

**Fix.** Resolve by fixing the source (F1): once §1 carries "unbounded," the `adaptive-red-teaming.md` citation
becomes faithful and no separate edit is needed. Until then, the pattern should mark the qualifier as *(reviewer
synthesis, sharpening §1)* rather than a bare "(Adversarial §1)."

---

### F4 — [MINOR] "fine-tuning / retraining does not remove implanted behavior" is over-generalized in a few sites, and the KB's own A41118 is a counterexample
**Where:** `patterns/evaluation-holdout-protection.md:141–142` (*"fine-tuning does not remove implanted behavior
(A40295 …)"*) and `patterns/backdoor-detection.md:274` (*"Assuming retraining / fine-tuning launders a suspect
artifact. It does not"*). Contrast the **accurate** phrasing in `Adversarial-ML-Attacks.md` §9.3 (line 306ff), which
carefully says *"clean fine-tuning"* and *"does not **reliably** remove."*

**Problem.** The evidence base (A40295 P-Trojan, A39809, A40855) shows *adversary-engineered* backdoors survive or are
*reinforced by ordinary clean fine-tuning*. Generalizing to the flat universal *"fine-tuning does not remove implanted
behavior"* over-reaches: purpose-built defensive fine-tuning **does** remove backdoors — including the KB's own
`adaptive-red-teaming.md:260` / `:390` example, A41118, where *"latent-adversarial-training mitigates its own
backdoor."* The two claims sit unreconciled in the same KB. The operational conclusion ("don't rely on retraining as
remediation; use provenance") is correct and should stay; only the phrasing overreaches.

**Fix.** Restore the two dropped qualifiers wherever the flat form appears: *"**ordinary/clean** fine-tuning does not
**reliably** remove implanted behavior, and adversary-engineered backdoors can survive or be reinforced by it (A40295,
A39809, A40855); purpose-built defensive fine-tuning may remove some (A41118) but is not a general launder."*

---

### F5 — [MINOR] The certified-defense discussion does not distinguish *probabilistic* (randomized-smoothing) from *deterministic* (patch) certificates — which is the exact seam GhostCert attacks
**Where:** `syntheses/Adversarial-ML-Attacks.md` §5 (lines 177–181) and §8 (line 276) treat A37716 (CertMask,
deterministic double-masking patch certificate) and A37117 (randomized-smoothing, ℓ2) under one undifferentiated
"certified" umbrella. A40915's *probabilistic* nature is flagged ("forging bound < 1/2^128"), but A37117's is not.

**Problem.** For this audience the distinction is load-bearing: randomized-smoothing certificates are **probabilistic**
(hold w.p. ≥ 1−α, with a Monte-Carlo sample budget and an **abstain** outcome), whereas deterministic patch
certificates do not abstain. GhostCert (F2) exploits precisely the probabilistic/abstention structure (abstentions →
DoS). Lumping them hides *why* one certified family is spoofable and where the residual sits.

**Fix.** One clause in §5: note that A37117 is a **probabilistic** certificate (confidence 1−α, abstain option, MC
sample budget) while A37716 is a **deterministic** patch certificate, and that the probabilistic/abstain structure is
the surface GhostCert (A37924) targets. Ties F2 and F5 together for the reader.

---

## 2. What is DONE WELL

- **The adaptive-attacker meta-finding is correctly elevated to the #1 cross-cutting result and threaded everywhere.**
  `Adversarial-ML-Attacks.md` §9.1, `adaptive-red-teaming.md`, and `adversarial-training.md` all lead with "non-adaptive
  evaluation systematically overstates security," and each headline number is explicitly tagged non-adaptive with the
  A40905/A40915/A37117 "build a purpose-built adaptive attacker" bar named as the standard. This is exactly the
  scoping discipline my lens exists to check, and it is done rigorously.

- **Evidence-integrity hygiene is genuinely best-in-class.** Every magnitude is tagged author-reported, truncated
  tables are flagged (§12), reviewer-synthesis is separated from paper claims, and repeated numbers are *consistent*
  across files (spot-checked A37117 `9.25% ≈ clean 9.47%; 86.2%→73.9%`; A38416 `+64%/+28%` dichotomy; A36964 `80.1% /
  73.2% post-defense`; CertMask `O(n) vs O(n²), +13.4%` — all internally consistent). No number-drift found.

- **Scope boundaries between defense classes are drawn carefully and correctly.** `adversarial-training.md` explicitly
  refuses to let AT be presented as a backdoor/poisoning control or as certified (A39318 "AT is not a poisoning
  defense," A41122 "inference-time, not AT"); `backdoor-detection.md` correctly frames its own strongest evidence as
  *negative/methodological* (detectors get bypassed) and subordinates detection to provenance. The transferability
  story (A38416 dichotomy, A41144/A42439 monoculture, loss-landscape geometry A36964/A37912) is handled with the right
  no-free-lunch framing.

---

## 3. Biggest risk from my seat

**The KB's greatest strength on empirical robustness — its relentless "non-adaptive ≠ safe" discipline — has a blind
spot at the *certified* end: it over-trusts certificates it never cross-links to GhostCert, and it states the
certified-vs-adaptive relationship in a form (F1) that is technically false to the very experts it is written for — so
the one place a sophisticated reader would catch the KB being imprecise is exactly the certified-robustness claim it
most wants them to trust.**
