# Quality Review — Lens: Independent Auditor

**Focus:** evidence integrity — uncalibrated absolutes (secure / proven / unbreakable), any claim
not traceable to a paper id, any lab→production leap presented as deployable fact.

**Slice reviewed:** all 8 authoritative syntheses (`AILLM-Safety`, `Adversarial-ML-Attacks`,
`Privacy-Protection`, `Multi-keyword-match`, `Network-Cyber-Security`, `Model-IP-Protection`,
`Deepfake-Forgery-Detection`, `Defense-Mitigation`, full); `patterns/human-approval-consequential-actions.md`
(full) + the risk-bearing sections (Metrics/Known-bypasses/Residual/When-NOT) of
`prompt-injection-containment`, `tamper-evident-traces`, `kill-switches`, `evaluation-holdout-protection`,
`least-privilege-credentials`, `sandboxed-execution`; `ontology.md`, `source-index/relevance-triage.md`,
`README.md`, `corpus-audit.md`, `agent-identity.md`. **Mechanical cross-checks run:** every `A#####` id
cited in `patterns/` (284 distinct) and authoritative `syntheses/` (432 distinct) against the 432-paper
master set in `paper-to-ontology-map.jsonl`; evidence-strength + category + triage-tier aggregate counts
against the raw JSONL; one-card-per-paper coverage of `research-cards/` against the master set; an
assertion-style-absolutes grep across every doc layer.

**Bottom line:** On the three things I was sent to break, this base is **unusually clean**. Paper-id
traceability is effectively total (100% of pattern citations and 100% of authoritative-synthesis
citations resolve to a real card; 432/432 cards present with 0 orphans). Uncalibrated absolutes appear
**only** inside the disclaimer lines that forbid them. Lab→production leaps are actively pre-empted —
every numeric target is tagged an engineering/policy choice "requiring production validation," every
corpus number is labeled author-reported and non-adaptive. **No blocking issues.** The findings below
are one stale *assurance artifact* that contradicts the repository, one untraceable id quarantined in a
superseded file, and a source-independence caveat on the base's least-verifiable numbers. I did not
manufacture defects — the evidence-integrity discipline here is the best I've reviewed.

---

## 1. Findings

### F1 — [MAJOR] `corpus-audit.md` under-reports card coverage; the traceability-assurance doc contradicts the repo
**Where:** `corpus-audit.md` → "## Integrity", the lines `Research cards present: 415 / 432 (missing: 17)`
and the enumerated missing list (`A38722, A38730, A38761, A38785, A38853, A38949, A39085, A39276, A39290,
A39301, A39318, A39336, A39382, A39428, A39438, A39449, A39480`); also `arXiv id resolved: 7 / 432`.

**Problem:** The actual tree is **432/432 cards, 0 gaps, 0 orphans** (verified: every `A#####.md` under
`research-cards/` diffed against the 432 master ids). All 17 "missing" cards exist as substantive ~24 KB
structured cards — e.g. `research-cards/Adversarial-ML-Attacks/A39276.md` is 145 lines / 23 KB. This is
not a cosmetic drift: several of the "missing" papers are load-bearing. **A39276** is cited across
`Adversarial-ML-Attacks.md` (§9.7, §18) and rated *"Strong (methodological)"* and used as the calibration
anchor ("what honest ≈ chance looks like") in `patterns/evaluation-holdout-protection.md`; **A38853**
(split-LLM activation inversion) and **A38949** are cited as foundational. The one document whose job is
to *certify* the evidence chain is the one telling readers 4% of it is missing. The stale
`arXiv id resolved: 7 / 432` line is corroborating drift — many more arXiv ids already live in the cards
(e.g. A37053 `2508.18839`, A40100 `2505.15683`, A40210 `2508.05674` per `Network-Cyber-Security.md` §20).

**Why it matters (my lens):** An auditor or downstream agent that trusts `corpus-audit.md` will wrongly
believe the backbone is incomplete, and — worse — its "0 dup / 0 unreadable" assurances inherit the same
staleness, so their current truth is unestablished. A reconciliation artifact that isn't regenerated with
the tree is a silent-integrity hazard.

**Fix:** Regenerate `corpus-audit.md` from the current tree (the README documents the build scripts:
`build_manifest.py` produces this reconciliation), and add it to the `tests/validate.py` §7 gate so
card-coverage/dup/extraction counts cannot drift from reality. Minimum interim fix: stamp the file with
`generated: <commit/date>` and correct the 415→432 / 7-arXiv numbers.

### F2 — [MINOR] One untraceable paper id (`A38449`) survives in a retained superseded partial
**Where:** `syntheses/_partials/Adversarial-ML-Attacks-1.md:183` — "…Hide confidence/logits where possible
(A38095, A38127, **A38449** logit-dependent distillation)…".

**Problem:** `A38449` is **not** one of the 432 master ids and has no card — the only untraceable `A#####`
anywhere in the tree. The authoritative merge already caught it: `Adversarial-ML-Attacks.md` §15 (API
hygiene) rewrites that bullet without `A38449`, so the shipped authoritative layer is 100% traceable. But
all 14 `syntheses/_partials/*.md` ship in the tree carrying only an in-body "superseded by the merge" note
and no file-level DEPRECATED marker, so a broad grep or a retrieval agent can still surface the untraceable
id as if it were evidence. The citation-resolution gate evidently does not cover `_partials/`.

**Why it matters (my lens):** Traceability is the base's headline guarantee ("Every substantive claim
traces to a paper id", `README.md`). A single reachable exception is worth closing precisely because the
rest is spotless.

**Fix:** Delete or move `syntheses/_partials/` out of the shipped references tree (they are explicitly
superseded), OR prepend a `> DEPRECATED — superseded by ../<category>.md; do not cite` banner to each, AND
extend the citation-resolution validator to scan `_partials/` so a stray/typo'd id fails the build.

### F3 — [MINOR] The base's least-verifiable numbers are second-hand from a single commercially-interested brief
**Where:** `patterns/least-privilege-credentials.md:59-61` and `agent-identity.md:29` — machine identities
outnumber humans "~45:1 to >80:1", average machine secret "**>600 days**", "**~1 in 20** holds full-admin",
"**~1/3 of private repos** contain a plaintext secret."

**Problem:** These four statistics are the load-bearing motivation for the ZSP / credential-broker
recommendation, yet they are secondary data: sourced to the 1Password *"Identity for Reasoning Agents"*
brief (`agent-identity.md:3`), which *itself* cites unnamed primary reports, and which vends the credential
broker the pattern recommends. The KB handles the provenance **honestly** — every instance is tagged
*"(agent-identity brief; cited by it, not a corpus measurement)"*, which is exactly the right discipline —
but no primary citation is given, so these figures are un-checkable, and they are the only quantitative
claims in the base with a plausible source-of-interest.

**Why it matters (my lens):** Not a defect in framing (the disclosure is correct), but a source-independence
gap: everywhere else, magnitudes trace to a re-readable card + PDF path; here they bottom out at a vendor
brief with a product to sell. An independent auditor should be able to reach a neutral primary source.

**Fix:** Add primary citations for each statistic (or mark each `[primary source: unverified]`), and add a
one-line source-independence caveat where the recommendation is made, noting the figures are uncorroborated
secondary data from a party with a commercial interest in the recommended control.

---

## 2. What is done well

- **Traceability is effectively total and mechanically verifiable.** 100% of the 284 distinct pattern
  citations and 100% of the 432 distinct authoritative-synthesis citations resolve to a real card;
  432/432 papers have a substantive card (0 gaps, 0 orphans); and the machine-derived aggregates are
  internally exact — evidence-strength `312 moderate / 65 insufficient / 38 preliminary / 17 strong`,
  per-category counts, and triage tiers `137 core / 245 adjacent / 50 peripheral` all reproduce from the
  raw JSONL. Claims are anchored, not asserted.

- **Absolutes are structurally banned, not just avoided.** The only occurrences of "unbreakable / proven
  safe / secure" across the entire tree are inside the disclaimer lines that prohibit them. Where a real
  formal guarantee exists (DP/crypto), the word "guarantee" is scoped precisely to the mechanism and
  repeatedly bounded — "the accounted guarantee, not the noise, is the load-bearing property… voided by any
  unaccounted shared object… do not market as a guarantee" (`Privacy-Protection.md` §9, `differential-privacy.md`,
  `privacy-preserving-inference.md`). This is exactly correct calibration.

- **The lab→production seam is defended, not crossed.** Every pattern separates author-reported/non-adaptive
  corpus numbers from engineering targets, tags the latter "requires production validation," and reports
  *residuals* rather than wins (A41468 >50% miss on hardest class, A42191 ~31%, A40248 ~16%, A40432 ~28%
  CRR, A40925 ~15% Acc-Fusion). The base even self-discloses a data-quality hole rather than hiding it —
  `Adversarial-ML-Attacks.md` §2 warns "the corpus manifest's arXiv IDs are frequently mis-extracted…
  trust the internal Axxxxx ids, not manifest arXiv IDs." A knowledge base that flags its own weak field
  is the opposite of an overclaim.

---

## 3. Biggest risk from my seat

The evidence *content* is trustworthy; the risk is that the **generated assurance artifacts drift out from
under it** — `corpus-audit.md` already claims 17 cards are missing that in fact exist, so any reader who
trusts the audit over the tree gets a false picture of exactly the traceability the whole base sells; wire
these reconciliation docs into the build/validate gate so they cannot lie about a corpus that is, in
reality, complete.
