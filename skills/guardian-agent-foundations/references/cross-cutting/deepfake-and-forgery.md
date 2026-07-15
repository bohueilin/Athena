# Cross-Cutting Chapter — Deepfake and Forgery Detection

*Source synthesis: `references/syntheses/Deepfake-Forgery-Detection.md` (13 AAAI-26 research
cards, merged from one partial synthesis). This chapter is a cross-paper reading organized by
**thread**, not a per-paper list. It surfaces the arguments that only become visible when the
papers are read against each other — chiefly that this corpus produces an **evidence signal an
agent consumes**, not a control on the agent's own tool/skill/MCP surface, and that the single most
load-bearing distinction in the whole area — **detection is not authentication** — is exactly the
Guardian-Agent split between capability and evidence.*

---

## Evidence-integrity contract (non-negotiable)

- Every numeric value is **author-reported under that paper's own evaluated threat model** unless
  explicitly marked otherwise. The source synthesis flagged several result tables as truncated /
  unverifiable in the extracted PDFs (A37334, A37865, parts of A41234); those magnitudes are written
  **"not stated in paper"** rather than reconstructed.
- No titles, authors, venues, datasets, or metrics are invented here. Where the source synthesis
  recorded that a value was absent from a card, this chapter writes **"not stated in paper."**
- Claims are labeled **(direct)** when they are a finding of the cited paper(s) as recorded in the
  synthesis, and **(reviewer synthesis)** when they are cross-paper judgments — either carried over
  from the source synthesis or made in this chapter. Cross-paper judgments are not assertions of any
  single paper.
- Language is calibrated: "demonstrated under the evaluated threat model", "reduced EER against the
  tested types", "not evaluated against", "requires production validation". No absolutes
  ("secure", "unforgeable", "proven authentic", "tamper-proof") appear.
- Paper ids are internal `Axxxxx` card ids, not manifest arXiv ids.

## Reading key — the CPVER mapping

Every implication is tagged to the Guardian-Agent enforcement primitives (`worldview.md` §2–§6,
`glossary.md`). The adversarial-corpus slogan — *"capability is not permission; obscurity is not
robustness"* — has a precise analogue here that organizes the whole chapter (reviewer synthesis):
**a detection verdict is not proof of authenticity, and generalization is a decaying asset.**

- **[C] Capability** — what a *detector or generator can produce*: a "fake/real" verdict, a
  confidence score, a localization mask, an MLLM forensic rationale. The corpus's load-bearing
  warning is that this verdict is a **probabilistic signal, not authority and not evidence**
  (Section 14: "use any single detector as one probabilistic evidence signal, never as an
  authoritative gate").
- **[P] Permission** — what an authenticity signal is *authorized to gate*: face anti-spoofing as
  **one** authentication gate with escalation to human review (A37945); owner-side proactive
  protection as a pre-distribution owner control over downstream edits (A37865). Detection is an
  input to a permission decision, never the decision.
- **[V] Verification** — *independent, adversary-aware checking* of a signal before it is trusted:
  the fast-proposer + confidence-gated reflective verifier loop (A37421, A38060); gating an MLLM
  explanation against a taxonomy or metric before surfacing it (A38060, A37945). A detector's own
  fluent rationale is **not** verification of itself.
- **[E] Evidence** — *tamper-evident, independent provenance*: creation-time cryptographic content
  credentials, watermarking, and A37865's proactive tamper tripwire — the corpus's only in-scope
  attestation analogue. The central cross-cutting claim of this chapter: **passive detection is
  [C], not [E]; only provenance established at or before creation is [E].**
- **[R] Residual-risk** — what remains after a control fires, dominated in this corpus by two gaps:
  (1) the **untested adaptive / anti-forensic** attacker (universal across all 13 cards — the one
  adaptive attacker, A41525, is a teaching classifier, not a defense), and (2) **time-bounded
  generalization** — detection accuracy decays as generators evolve.

The single most replicated meta-finding across the corpus (direct, Sections 9, 11, 17):
**cross-generator / cross-type / cross-dataset generalization is the central failure mode, and
adaptive anti-forensic robustness is essentially unmeasured.** That finding is why the [R] tag
appears on nearly every thread below.

---

## Thread 1 — Image / audio / video forgery (the modality landscape)

**Well-established.** The corpus covers three siloed modalities with independently-derived detectors:
**image** (AIGI / face-forgery: A37071, A37421, A37473, A37553, A37865, A37945, A38060, A40886,
A41234), **audio** (speech / sound / singing-voice / music: A40907), and **audio-visual video**
(temporal talking-face manipulation: A40928) (direct, Section 2). Two inductive biases recur across
*all three* modalities without cross-citation, which is the strongest cross-paper signal in the set:
(1) treating the "fake" class as **internally structured, not monolithic** — pattern-coexistence
duality within a fake image (A37071), GAN-vs-DM architectural sub-clusters (A40886),
residual/real-only representations decoupled from semantics (A37473, A41234); and (2)
**frequency-domain cues as the load-bearing signal** — high-frequency / wavelet / spectral features
recur as discriminative across image (A37071, A37553, A37865, A38060, A41234) and audio (A40907, a
type-invariant cue concentrated in the HH wavelet band, direct) (reviewer synthesis over six papers).

**Emerging.** Temporal audio-visual forgery *localization* of sparse, boundary-ambiguous manipulated
segments (A40928, deformable state-space over frozen AV backbones) and all-type audio detection that
generalizes across speech/sound/singing/music from one model (A40907) are the newest modality
frontiers. Proactive owner-side image protection (A37865) is the only non-passive entry.

**Contested.** Nothing is head-to-head contradicted — these are parallel detectors, not competing
claims about one measurement (direct, Section 10). The real tension is **modality siloing**:
image, audio, and audio-visual detectors do not share representations, so there is no unified
content-authenticity model in the corpus (reviewer synthesis, Sections 2, 17). "Video" here means
talking-face AV forgery (A40928); general synthetic-video generation detection is **not stated in
any paper** in this corpus.

**Where defenses fail (adaptive / real-world).** Every detector here is demonstrated under a
non-adaptive, distribution-shift threat model; none is evaluated against an attacker optimizing
anti-forensics against the specific detector (direct, Section 11). A40907's clean-audio-only scope
is explicit — no channel noise, compression, or partial spoofing evaluated (direct).

**Implication.**
- **[C]** Each modality detector is a distinct probabilistic capability; there is no single "is this
  real" oracle. A content-authenticity layer must **compose per-modality models**, not assume one
  detector covers image + audio + video (reviewer synthesis, Section 15).
- **[R]** The absence of a general synthetic-video detector and the audio clean-only scope are
  named coverage gaps; any product spanning those modalities carries **[R] production-validation-
  pending** residual risk there.
- **Launch gate:** state per-modality coverage explicitly; do not let an image-detection result
  stand in for audio or video authenticity.

## Thread 2 — Detection generalization (the corpus's organizing problem)

**Well-established.** This is the corpus's central, most-replicated result: **single-source
detectors overfit generator-specific surface artifacts and collapse on unseen generators, types, or
datasets** (direct, demonstrated under the evaluated threat models of A37071, A37334, A37421, A37473,
A37553, A40886, A40907, A41234). A40907 quantifies it starkly: single-type audio countermeasures
drop to **near-chance EER (~30–50%) on unseen types**, versus **3.58% average EER** for the all-type
co-trained model (direct). The convergent fix is to stop modeling "fake" as one class — real-only
representation learning with feature-space pseudo-negatives (A41234), architectural sub-clustering
(A40886), residual prototypes decoupled from semantics (A37473) — a paradigm that does **not require
enumerating generators** (reviewer synthesis over four papers).

**Emerging.** Real-only modeling (A41234, learn the authentic manifold and treat deviation as fake)
and unsupervised architecture attribution (A40886, recover GAN-vs-DM family without generator labels)
are the future-proofing directions. Parameter-efficient tuning on a frozen backbone (A40907 reports
~458× fewer trainable parameters than full fine-tuning, direct) makes re-training cheap enough to
track a shifting generator population.

**Contested.** The setting-dependence of "SOTA." High headline numbers coexist with near-chance
behavior on the hardest in-the-wild sets: A37071 reaches GenImage SOTA yet only **~57–58% on the
harder Chameleon benchmark** (direct); A38060 reports 98.91% original / 95.89% hard-subset accuracy
**but trains one model per GenImage subset** (a named caveat on the generalization framing, direct);
A40886 reports GenImage avg AUC **0.9882 across 5 datasets / 13 baselines** but bakes in a **fixed
K=2 GAN/DM assumption** that a new architecture family (e.g. VAR) can break (direct). Averaged SOTA
can mask per-generator near-chance behavior (reviewer synthesis, Section 10).

**Where defenses fail (adaptive / real-world).** Averaged metrics hide per-generator / per-type
failure (A37071 Chameleon, A40886 and A40907 per-type breakdowns matter). Borrowed baseline numbers
not re-run under identical preprocessing (A37473, A37553) mean cross-method superiority assumes
preprocessing parity (direct, Section 12). No result generalizes across an *adaptive* attacker
crafting the unseen distribution deliberately (direct, Section 11).

**Implication.**
- **[C]/[R]** Treat detection accuracy as a **decaying asset**: generalization is empirical and
  expires as generators evolve (reviewer synthesis, Section 16). A detector is a **pluggable,
  replaceable evidence producer**, not a fixed oracle (Section 15).
- **[V]** Benchmark against the *hardest in-the-wild* sets and worst-case per-generator performance,
  not averaged SOTA (A37071 Chameleon is the cautionary example).
- **Launch gate:** any "robust detector" claim must disclose per-generator / per-type worst case and
  whether one universal model or per-subset models were trained (A38060); require a scheduled
  re-benchmarking cadence with OOD-accuracy / EER-drift monitoring as new generators appear.

## Thread 3 — Generator shift (unseen architectures as the adversary)

**Well-established.** The "adversary" in 12 of 13 papers is the space of generators — unseen models,
unseen forgery types, unseen datasets — modeled as **distribution shift, not adversarial evasion**
(direct, Section 3). Adversary knowledge is effectively black-box (no detector-internal access)
across the detection papers. The generalization result (Thread 2) is the same phenomenon read as a
threat model: a detector trained on today's generators is a detector against *yesterday's* attacker.

**Emerging.** Two responses to genuinely new paradigms: (1) architecture-family clustering that names
the shift (A40886 separates GAN JS-divergence-style artifacts from DM KL-divergence-style artifacts,
direct) and (2) real-only detection explicitly evaluated **across GAN / diffusion / VAR** plus a
safety-critical medical distribution shift at low compute (A41234, direct) — the corpus's most
deliberate attempt to survive an architecture family it did not train on.

**Contested.** Whether inductive biases baked for two families transfer to a third. A40886's fixed
GAN/DM K=2 assumption is an explicit, self-named bias that autoregressive/VAR generators can break
(direct); A41234's cross-VAR evaluation is the counter-position that real-only modeling degrades more
gracefully. The corpus does not resolve which survives the *next* paradigm (reviewer synthesis,
Sections 15, 17).

**Where defenses fail (adaptive / real-world).** A detector whose discriminative signal is a
frequency artifact of current generators (Thread 1) has no guarantee against a generator engineered
to suppress that artifact — and that adaptive generator is **not evaluated anywhere** (direct,
Section 11). Architecture attribution (A40886) is suggested but **not independently validated**
(direct, Section 17).

**Implication.**
- **[R] Generator shift is a primary residual-risk driver.** A defense validated against known
  generator families carries **[R] unknown** residual risk against the next family; state the
  trained-on generator set as a scoping assumption next to every accuracy number (reviewer synthesis).
- **[E]/[C]** Prefer detection paradigms that do not enumerate generators (real-only, A41234) when
  the deployment horizon outlasts the current generator population — but still treat their output as
  [C], not [E].
- **Launch gate:** require an explicit list of generator families the detector was trained/tested
  against; treat the accuracy claim as scoped to that list, with unknown residual risk outside it.

## Thread 4 — Compression / transform robustness (the distribution channel)

**Well-established.** Real distribution channels — OSN JPEG compression, Gaussian noise, resizing —
erase the high-frequency traces detectors rely on, and this is modeled as environmental corruption
(direct: A37553 OSN compression, A37421 JPEG/Gaussian). A37553 (DDOC) is the most realistic setting:
it documents that the prior gradient-reversal approach **removes overlapping forgery features along
with compression features**, and replaces it with **decision-driven orthogonal decoupling** —
orthogonalize the nuisance to the decision axis instead of deleting it — reporting **~75% mean
accuracy under OSN compression** and an ablation where the ViT-low-freq + CNN-high-freq bidirectional
fusion is the single most critical component (**+7.4**, direct). A37421 pairs corruption testing with
its verifier loop; A37071's frequency-based method is by contrast **not evaluated against**
post-processing (JPEG, blur) crafted to suppress its inter-branch discrepancy (direct, Section 11).

**Emerging.** The transferable design principle — *orthogonalize the nuisance to the decision axis
instead of deleting it* (A37553) — is the corpus's cleanest reusable idea for handling
compression/corruption without destroying forensic signal (reviewer synthesis, Section 6).

**Contested.** A37553's within-literature correction (orthogonal decoupling vs gradient reversal) is
a documented replacement of a prior failure mode, not a contradiction among these 13 (direct,
Section 10). No paper contests that compression degrades detection; they differ only in how much
signal survives.

**Where defenses fail (adaptive / real-world).** Compression is modeled as *non-adaptive*
distribution shift, **never as an adaptive anti-forensic attacker** who recompresses / denoises /
resizes deliberately to defeat the specific detector (direct, Section 11). This is the exact seam
between a benign channel and an adaptive attack, and the corpus only tests the benign side. A37865's
protective perturbation is explicitly **survivability-untested** against stripping / denoising /
recompression / regeneration (direct, Section 11) — see Thread 5.

**Implication.**
- **[V]** Evaluate detectors under the *deployment* channel (the actual OSN / codec pipeline), and
  disclose accuracy under compression, not only on pristine inputs (A37553, A37421).
- **[R]** Any detector validated only on clean or benign-compressed inputs carries **[R]
  production-validation-pending** residual risk against adaptive recompression / regeneration
  attacks; that adaptive case is not in the corpus.
- **Launch gate:** require a compression/transform robustness curve (not a single pristine number)
  and flag adaptive anti-forensic recompression as an untested residual risk.

## Thread 5 — Provenance systems (the corpus's structural gap)

**Well-established.** There is **only one** proactive/active-forensic control in the entire corpus:
A37865 (Blank Canvas). It inverts adversarial fragility — a frequency-aware (Daubechies-8 DWT) ℓ∞
perturbation the *owner* embeds before distribution forces SAM from "segment anything" to "segment
nothing", so any later edit shows up as an anomalous segmentation ("blank canvas"), enabling
**training-free tamper localization** (direct; released code; headline numbers **not stated in
paper** — truncated in review). It is the corpus's closest analogue to a watermarking / attestation
provenance control (reviewer synthesis, Section 5). Every other paper is **passive detection of
already-generated content** — provenance is inferred after the fact, not established at creation
(direct, Section 2).

**Emerging.** A37865's paradigm — proactive forensics by turning an adversarial perturbation into an
owner-controlled tamper tripwire — is a genuinely distinct primitive (reviewer synthesis, Section 6),
but its evidence is preliminary and verifier-dependent.

**Contested / bounded.** Whether A37865's tripwire survives deployment. Its trust rests on two
untested conditions: the protective perturbation surviving the distribution channel (stripping,
denoising, recompression, regeneration could remove it), and **pinning the specific SAM version** —
a verifier-model change may silently break tamper localization (direct, Section 11, Section 16). Both
are flagged as **not evaluated against**.

**Where defenses fail (adaptive / real-world).** A37865 is not evaluated against an adversary who
strips or regenerates the image to defeat the blank-canvas state (direct, Section 11). More broadly,
the corpus **has no cryptographic-provenance / signed-manifest system of its own** — provenance as a
tamper-evident record is recommended (Section 14) but not researched here (reviewer synthesis).

**Implication.**
- **[E] Provenance is the [E] slot detection cannot fill.** A37865 is an owner-controlled
  attestation analogue worth considering for owned assets, but treat it as **evidence only within a
  pinned verifier version and a channel over which the perturbation survives** — both require
  production validation (reviewer synthesis, Section 16).
- **[P]** Because it is embedded *before* distribution, A37865 acts as an owner permission over
  downstream edits — a pre-distribution [P] control, distinct from the post-hoc [C] verdict of
  passive detectors.
- **Launch gate:** pin and version-control the verifier model (SAM) as a governed dependency; do not
  claim tamper localization survives channels or verifier changes it was not tested against; state
  perturbation-survivability as an open residual risk.

## Thread 6 — Content credentials (present only as a recommendation)

**Well-established.** The corpus is **effectively silent** on creation-time content credentials.
C2PA-style cryptographic provenance appears **only as a reviewer recommendation** — "combine
detection with cryptographic provenance (C2PA-style), watermarking, and human review for high-stakes
decisions" (Section 14, tied to A37071 and A37865 deployment-implications) — and **not as any paper's
own contribution** (reviewer synthesis; no content-credential system is a finding of any of the 13
cards). This silence is itself the cross-cutting finding: the field represented here defaults to
*detecting* fakes rather than *authenticating* reals.

**Emerging.** Nothing in-corpus. The nearest in-corpus primitive is A37865's owner-embedded
tripwire (Thread 5), which is a proactive forensic mark rather than a signed provenance manifest —
adjacent to, but not, content credentials (reviewer synthesis).

**Contested.** Not contested within the corpus, because no paper studies content credentials. The
contestable claim is external and must be labeled as such: whether passive detection can substitute
for signed provenance. The corpus's own evidence (Threads 2–3, generalization decays; Section 14,
"never an authoritative gate") argues it cannot — detection is a decaying [C] signal, credentials
would be a durable [E] record (reviewer synthesis).

**Where defenses fail (adaptive / real-world).** A content-credential scheme would face
strip-and-relaunder and re-signing attacks that this corpus **does not evaluate at all** — there is
no data here on content-credential robustness. Any credential claim would be
**production-validation-pending** with respect to this corpus (reviewer synthesis).

**Implication.**
- **[E]** Content credentials are the missing [E] layer; this corpus supplies the argument *for*
  them (detection alone is insufficient) but **no evidence about them**. Do not cite any paper here
  as validating C2PA-style provenance — the recommendation is reviewer synthesis, not a finding.
- **[C]/[E] boundary:** a signed credential (if adopted from outside this corpus) is [E]; a detector
  verdict is [C]. Never let the [C] verdict be recorded as if it were the [E] credential.
- **Launch gate:** for high-stakes authenticity decisions, require an [E] provenance path (external
  to this corpus) alongside detection; treat "we run a detector" as **not** meeting a
  content-credential requirement.

## Thread 7 — Human factors (explanation trust and the operator)

**Well-established.** The corpus's human-factors evidence is almost entirely about **explanation
trust**, and the result is negative: **MLLM/VLM-generated forensic rationales are empirically
unreliable on their own.** A38060 measured **up to 67.4% of MLLM-identified flaws as incorrect**
(direct); A37421 documents "overthinking" — the model over-reasons on easy fakes (direct). The
consensus design move is to **gate/verify explanations against a metric or taxonomy before surfacing
them** to a human (A38060 metric-grounded Top-K refinement; A37945 detect+type+reason+localize
anchored to a 12-type taxonomy) (direct, Section 6, Section 9). Explanation-quality is measured by
text-image similarity / BLEU / ROUGE (A38060, A37945, A37421), which capture **fluency/overlap, not
causal fidelity or human ground truth** — a named limitation (direct, Section 12).

**Emerging.** A41525 (Breakable Machine) is the corpus's only artifact centered on human
understanding — a K-12 AI-literacy resource in which a **human learner adaptively spoofs a
MobileNet-V2 classifier in the physical world** (props, lighting, background) guided by CAM saliency
and training-data inspection (direct). It is pedagogy and red-teaming-as-teaching, **not a deployable
control** (direct, Section 2), but it is the only place a human is modeled as an adaptive adversary.

**Contested.** Whether fluent explanations help or harm oversight. The corpus leans toward *harm if
ungated* (A38060's ≤67.4% incorrect-flaw rate; A37421's overthinking), but there is **no
human-subjects study** measuring whether analysts actually calibrate better with vs without
explanations — that evidence is **not stated in any paper** (reviewer synthesis). Human detection
performance on deepfakes is likewise not measured in this corpus.

**Where defenses fail (adaptive / real-world).** A fluent-but-wrong rationale is a spoof of human
oversight: a human who trusts the explanation inherits its up-to-67.4% error rate (A38060). Averaged
accuracy masks near-chance behavior on the hardest inputs (Thread 2), so an operator shown only a
verdict is systematically miscalibrated (reviewer synthesis, Section 14).

**Implication.**
- **[V]** Gate explanations before they reach a human: anchor rationales to a verifiable taxonomy +
  quantitative scoring, and keep a human in the loop before action (A38060, A37945). A fluent
  rationale is **not** self-verification.
- **[C]** Surface **uncertainty, not just a verdict** — log and display confidence,
  impression-vs-final disagreement, and localization masks so the operator can calibrate (Section
  14). Averaged accuracy is a miscalibration hazard.
- **Launch gate:** do not surface an ungated MLLM rationale as ground truth; require the
  explanation-verification gate and uncertainty display, and treat human-team detection performance
  as **unmeasured** (production validation required).

## Thread 8 — Detection-vs-authenticity distinction (the throughline)

**Well-established.** This is the distinction every other thread reduces to, and the corpus is
unanimous on it: **every deployment-implications section concludes that a single detector is one
probabilistic evidence signal, never an authoritative gate** (direct, Section 14; A37071, A37865).
Detection answers "does this look generated to my current model?" — a decaying, generator-relative
[C] capability (Threads 2–3). Authenticity answers "can I independently attest where this came
from?" — a tamper-evident [E] record the corpus almost entirely lacks (Threads 5–6). Conflating the
two is the field's central design error, and the corpus's own numbers (near-chance on Chameleon;
~30–50% EER on unseen audio types; ≤67.4% incorrect MLLM flaws) are the argument against the
conflation (reviewer synthesis over Sections 9–14).

**Emerging.** The verifier-loop shape — **fast verdict + confidence-gated reflective escalation**
("cheap check first, deep check when confidence is low", A37421 adaptive Heuristic-to-Analytic
reasoning, A38060 metric-guided refinement) — is the corpus's most directly transferable pattern for
turning a raw [C] verdict into a [V]-gated signal before it is trusted (reviewer synthesis, Section
15).

**Contested.** Not contested — the papers agree detection ≠ authentication. What varies is whether a
given deployment *acts* on it. The corpus offers no counter-position that detection alone suffices
(reviewer synthesis).

**Where defenses fail (adaptive / compositional / real-world).** Wherever a detector verdict is
promoted to an authenticity gate: it inherits generator-shift decay (Thread 3), adaptive
anti-forensics (Thread 4), and explanation unreliability (Thread 7) all at once. The corpus contains
**no defense offering adaptive-adversary robustness** and **no formal authenticity guarantee**
(direct, Section 11, Section 17) — so any authenticity claim built on detection alone has [R]
unknown residual risk.

**Implication.**
- **[C]≠[E] is the launch-defining line.** Record a detector verdict as [C] capability in the trace;
  record provenance/credentials as [E] evidence; **never let the [C] verdict be logged or acted on
  as [E]** (reviewer synthesis, Section 14).
- **[V]** Wrap raw detection in the confidence-gated verifier loop (A37421, A38060) before any
  downstream consumer treats it as trustworthy.
- **[P]** For authentication surfaces (identity/authz), use anti-spoofing as **one** gate with
  escalation to human review (A37945) — not as a sole authenticator.
- **Launch gate:** no product may present a detection verdict as an authenticity guarantee; the
  assurance record must scope every detection claim to the non-adaptive, generator-relative threat
  model actually tested, and flag adaptive robustness as requiring production validation.

---

## Cross-thread reading — how the threads compound

The threads are not independent; the corpus's transferable value is where they **compose** (reviewer
synthesis):

- **Generalization × generator shift × compression** → a detector's frequency-artifact signal
  (Thread 1) is simultaneously generator-relative (decays under Thread 3) and channel-fragile
  (erodes under Thread 4). The three failure axes stack, and none is evaluated adaptively — so a
  detector strong on GenImage can be near-chance on a new generator seen through an OSN codec
  (A37071 Chameleon ~57–58%; A37553 ~75% under OSN; A40907 ~30–50% on unseen types). Only
  time-bounded re-benchmarking **[V]** and treating accuracy as a decaying asset **[R]** address it.
- **Detection-vs-authenticity × provenance gap × content-credential silence** → the corpus argues
  detection is insufficient (Thread 8) but supplies almost no [E] layer to replace it (Threads 5–6).
  The only in-corpus attestation analogue (A37865) is verifier-version-pinned and
  survivability-untested. The composition exposes a **structural [E] hole**: high-stakes
  authenticity needs a provenance path this corpus does not provide.
- **Explanation trust × human oversight × adaptive human attacker** → fluent-but-wrong MLLM
  rationales (A38060 ≤67.4% incorrect) meet a human who can also be trained to *defeat* a classifier
  (A41525). Ungated explanations spoof oversight; the fix is explanation-verification **[V]** plus
  uncertainty display **[C]**, never trusting the rationale.
- **Stateful detector components × poisoning/drift** → prototype banks (A37473, capacity 64/class,
  decay γ=0.99) and noise-residual models (A41234) are governed surfaces with reviewer-noted
  poisoning / normalization blind spots (heavy denoising or recompression altering noise statistics
  is untested, Section 11). They need bounded, logged, monitored update paths **[E]** before launch.

## Consolidated launch-gate checklist (reviewer synthesis, grounded in the cards)

1. **Detection-is-not-authentication gate (Thread 8, applies to all).** No detection verdict is
   presented or logged as an authenticity guarantee; record it as [C] capability, provenance as [E]
   evidence, and never conflate them (A37071, A37865; Section 14). **[C]≠[E]**
2. **Adaptive / anti-forensic gate (Threads 3–4, universal).** No detector ships claiming
   adaptive-adversary robustness; the entire corpus evaluates only non-adaptive distribution shift
   (A41525 is pedagogy, not a robustness test). Scope every claim to the tested threat model and
   flag adaptive robustness as **[R]** production-validation-pending. **[R]**
3. **Time-bounded generalization gate (Thread 2).** Treat detection accuracy as a decaying asset;
   require scheduled re-benchmarking against the hardest in-the-wild sets and worst-case
   per-generator performance, with OOD-accuracy / EER-drift monitoring (A37071 Chameleon; A40886;
   A40907). **[V]/[R]**
4. **Compression/channel gate (Thread 4).** Require a compression/transform robustness curve under
   the deployment channel, not a single pristine number; flag adaptive recompression/regeneration as
   untested (A37553, A37421, A37865). **[V]/[R]**
5. **Verifier-model pinning gate (Thread 5).** Pin and version-control any verifier model a proactive
   control depends on (A37865's SAM version); a verifier change can silently break tamper
   localization; state perturbation-survivability as an open risk. **[E]/[R]**
6. **Provenance / content-credential gate (Threads 5–6).** For high-stakes authenticity, require an
   [E] provenance path alongside detection; do not cite any corpus paper as validating C2PA-style
   credentials (recommendation only, not a finding). **[E]**
7. **Explanation-verification gate (Thread 7).** Never surface an ungated MLLM rationale as ground
   truth; anchor explanations to a taxonomy + quantitative score and keep a human in the loop
   (A38060 ≤67.4% incorrect flaws; A37945). **[V]**
8. **Uncertainty-surfacing gate (Threads 2, 7).** Display confidence, impression-vs-final
   disagreement, and localization masks, because averaged accuracy masks near-chance behavior on the
   hardest inputs (Section 14). **[C]**
9. **Stateful-component governance gate (cross-thread).** Prototype banks and noise-residual models
   (A37473, A41234) get bounded, logged, monitored update paths to contain drift and poisoning risk;
   the poisoning case is untested and must be flagged. **[E]/[R]**

---

*Closing evidence-integrity note.* Every metric in this chapter is reported as it appears in the
source synthesis's research cards, author-reported under each paper's own evaluated threat model;
several headline numbers sit in table regions the synthesis marked truncated (A37334, A37865, parts
of A41234) and are written "not stated in paper" rather than reconstructed. No titles, authors,
venues, datasets, or numbers were invented; where a card recorded that a value was absent, this
chapter does not assert one. The C2PA / content-credential discussion (Thread 6) is explicitly
**reviewer synthesis / external recommendation**, not a finding of any paper in the corpus.
Cross-paper judgments are marked *(reviewer synthesis)*; all other claims trace to the cited paper id
under its own evaluated threat model. This chapter draws only on
`references/syntheses/Deepfake-Forgery-Detection.md`; claims requiring the primary PDFs (e.g. exact
table cells) are **[R] production-/source-validation-pending**. Adaptive / anti-forensic robustness
is unmeasured across all 13 cards; no claim of "authentic", "tamper-proof", or "proven real" is made
or supported.
