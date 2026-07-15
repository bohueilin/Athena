---
name: guardian-agent-foundations
description: Knowledge base on AI-agent security, guardrails, red/blue-teaming, runtime enforcement, agent identity, and trustworthy agentic AI — distilled from the Virtue AI research + product corpus, the 1Password agent-identity brief, and a mid-2026 field sweep. Use when designing or discussing the Origin Physical AI safety stack (Guardian Agent, autonomy trace console, credential broker, runtime guardrails, PolicyGuard/ActionGuard-style enforcement) or the Passport agent-identity product, when reasoning about agent threat models (prompt/tool/skill/environment injection, memory poisoning, collusion, delegated authority), about machine/agent identity and credential access (Zero Standing Privilege, just-in-time / just-enough-privilege, attestation, federated/secretless identity, Workload Identity Federation/OIDC, intent-based access, attenuated delegation, the 1Password Credential Broker / Apono, Okta XAA/ID-JAG, Entra Agent ID, SPIFFE, CIBA step-up), when grounding harm in regulation/standards (NIST AI RMF/CAISI, EU AI Act + Digital Omnibus, OWASP LLM/Agentic(ASI)/MCP/Skills Top 10, MITRE ATLAS), when PREPARING FOR AN AGENT-SECURITY INTERVIEW (frameworks, the four debates, benchmark numbers, talking points), or when the user references Virtue AI, Guardian Agents, "capability is not permission," "secure agents as complete systems," or any of the papers/products in /Users/bohueilin/Documents/Research Papers/Virtue AI. Also use to ingest new material the user adds (folder PDFs or pasted briefs) or to refresh the 2026 landscape. Also use for EVIDENCE-BACKED design reviews grounded in the 432-paper AAAI-26 security corpus (`references/` — research cards, ontology + relationship graph, 8 category syntheses, 8 cross-cutting chapters, 28 control playbooks): threat-modeling an agentic workflow; designing prompt-injection / RAG / privacy / model-extraction / deepfake defenses; defining evaluation plans, launch gates, and residual-risk decisions with evidence thresholds; assessing a defense against an adaptive attacker; comparing approaches; or converting research findings into PRD requirements — every claim traceable to a paper id, with calibrated (never absolute) language.
user-invocable: true
---

# Guardian Agent Foundations

A living knowledge base for the **safety / security / trust layer of Origin Physical AI**, distilled from the
"Virtue AI" research-and-product corpus the user maintains at
`/Users/bohueilin/Documents/Research Papers/Virtue AI/`. It captures a coherent worldview — *agents must be
secured as complete systems, not moderated at the prompt layer* — plus the threat models, enforcement
architecture, evaluation methods, and vocabulary needed to design products like a **Guardian Agent**, an
**autonomy trace console**, a **credential broker**, and **runtime guardrails** for embodied / physical AI.

This is a **reference skill**, not a procedure. When a task touches the topics in the `description`, read the
relevant file below and apply the framing, taxonomy, and design patterns. Cite the specific source (paper id or
product) when it strengthens a recommendation. The user will keep adding material — see **Growing this skill**.

## The one-paragraph worldview

Traditional software is **stateless, deterministic, and bounded**; agentic systems are **stateful, probabilistic,
and unbounded**. The risk has moved from *what a model says* to *what an agent does* — its tool calls, its full
decision chain, its delegated authority. So safety must be a **separate, external, adaptive, policy-grounded
runtime layer**, because model alignment is empirically *shallow* (it refuses at the start of a turn, on shallow
knowledge, against blacklist strings — and collapses at depth, on expert knowledge, against semantics-preserving
rewrites, and under fine-tuning). The defensive layer ("Blue": discover → monitor → govern) is only credible if
continuously validated by an offensive layer ("Red": automated, adaptive, memory-driven red-teaming grounded in
real regulations). Optimize the precision/recall frontier — over-blocking (exaggerated safety) erodes trust as
surely as under-blocking lets harm through.

## Reference files (read on demand)

- **`references/worldview.md`** — The full Virtue AI thesis: the stateless→stateful shift, the four enforcement
  levels (prompt / action / MCP / skill), the Blue/Red two-sided model, the discover→monitor→govern triad, and
  the "alignment is shallow" evidence chain. **Start here** for framing and positioning language.
- **`references/threat-models.md`** — The canonical agent threat taxonomy: direct vs. indirect threat models;
  prompt / tool / skill / environment injection; memory poisoning; backdoors; specification gaming; deep-prefill
  attacks; code substitution; multimodal/perception attacks; multi-agent collusion + compromise budget. The
  catalog a Guardian must defend against.
- **`references/agent-identity.md`** — The **identity/credential half** of the thesis (from the 1Password "Agent
  Identity Build Day" brief): machine identity, how credentials become breaches, the three principles (minimize
  standing access; prove authority at runtime via attestation/federation; delegated-but-accountable), Zero Standing
  Privilege, JEP+JIT, secretless/WIF-OIDC, intent-based access, attenuated delegation, the 1Password stack
  (Environments, Credential Broker, Apono), and a **Passport applicability matrix** (have vs. gaps). Read this for
  anything about the credential broker, delegated authority, or "who answers when the agent acts."
- **`references/architecture-patterns.md`** — Reusable design patterns for Origin Physical AI: pre-action safety
  gate, effect/execution-based evaluation (sandbox dry-run), constitution-distillation, trajectory-level (not
  step-level) monitoring, least-privilege credential broker, Shapley-based risk attribution, async zero-latency
  explainability, deterministic verifiable judge, dynamic/contamination-resistant checks. **The build playbook.**
- **`references/papers.md`** — Per-paper digests of the research collection (TrustGen, SoSBench, RedCodeAgent,
  ARMs, Any-Depth Alignment, BlueCodeAgent, DreamGym, DevOps-Gym, MASTRIKE): problem, method, results, and the
  specific hook into a physical-AI guardrail.
- **`references/products.md`** — Virtue AI's product/positioning corpus (AgentSuite Blue/Red, Shadow AI,
  PolicyGuard, ActionGuard, MCPGuard, Agent ForgingGround, VirtueRed, VirtueGuard-Code) plus the Gartner
  "Guardian Agents" definition and the NIST CAISI framing. Naming patterns to reuse.
- **`references/glossary.md`** — Standardized vocabulary so Origin uses one consistent lexicon.
- **`references/regulations.md`** — The compliance/standards stack (NIST AI RMF, EU AI Act, OWASP LLM/Agentic/MCP
  Top 10, MITRE ATLAS, ISO/IEC 42001, FINRA, HIPAA, NFPA/IAEA/WHO for hazard grounding) and how to map one
  enforcement layer onto many frameworks.
- **`references/landscape-2026.md`** — *(NEW, Jul 2026 sweep)* Current field state: the hardened standards (OWASP
  ASI/MCP/AST, NIST CAISI, NSA MCP), the real incidents (GTG-1002, ClawHavoc, MCP-RCE, browser-agent injection),
  first-party platform containment (Anthropic/OpenAI/Google) and the wedge it leaves, the prompt-injection debate
  resolution + benchmark numbers, market consolidation, the OTel-GenAI trace standard + the tamper-evident-audit
  white space, and the EU Digital Omnibus timing shift. **Read for "what's true right now."**
- **`references/interview-agent-security.md`** — *(NEW)* Interview prep for agent-security roles: what strong
  candidates sound like, the framework canon, the **four debates with your position + citations**, the numbers to
  have ready, the memorizable one-liners, and **how to use Origin + Passport as portfolio proof** (each claim → a
  shipped piece, plus the honest frontier gaps). **Read before any interview or pitch Q&A.**

> **Provenance note (2026):** the founder-researchers this skill distills — **Bo Li, Dawn Song, Sanmi Koyejo** —
> were hired by **Meta Superintelligence Labs (Jun 2026)**; Virtue AI continues under a GTM-led CEO. Attribute the
> *worldview* to the founders/research (the durable part); treat *Virtue AI the company* as one vendor among many
> (`products.md` + `landscape-2026.md`).

## How to apply this to Origin Physical AI

When designing or reviewing an Origin feature, run it through this lens:

1. **Which enforcement level?** prompt / action / MCP-tool / skill. Physical actuation is an *action-level*
   concern → it needs a pre-action gate, not an output filter.
2. **Which threat model?** Direct (malicious operator) or indirect (injected via perception/environment/tool)?
   Embodied agents perceive the world, so indirect/perception attacks (trigger backdoors on a sticker/sign,
   typographic injection, simulated function-calls) are first-class.
3. **Discover → monitor → govern.** Is there an inventory (autonomy trace)? A continuous operational record of
   ordered, contextual action trajectories? Policy enforcement on the decision chain?
4. **Effect over string.** Gate the *effect* (motor into a human-occupied cell, irreversible action, file delete),
   not the API name — blacklists fall to semantics-preserving substitution.
5. **Least privilege via the credential broker.** Cap the blast radius of any single compromise; detect
   *coordinated* cross-credential misuse, not just isolated abuse (collusion).
6. **Prove before you veto.** Validate a flagged risk in a sandbox / dream-environment dry-run before blocking, so
   the guardrail isn't over-conservative and operators keep trusting it.
7. **Explain every decision.** Each allow/block carries a cited rationale (which policy, which regulation),
   generated asynchronously for zero added latency, written to the trace.
8. **Red-team continuously.** Pair every defensive control with an adaptive red-team that tries to break it,
   grounded in real regulations and replayable via a deterministic verifiable judge.

## The AAAI-26 security research base (432 papers)

A second, evidence-anchored layer sits under `references/` — a research-to-engineering knowledge system built
from **432 AAAI-26 security papers** (`~/Documents/Research Papers/AAAI-Security-2026/`, 8 categories). The
worldview files above give positioning + design *framing*; **this layer is the evidence** for design reviews,
threat models, evaluation plans, and launch gates, with every substantive claim traceable to a paper id.
Governing principle: **Models propose. Environments verify. Gates decide. Traces prove.**

**Layout & retrieval** (read on demand — never inline hundreds of summaries):
- `references/corpus-manifest.{jsonl,csv}` + `corpus-audit.md` — inventory (432 found · 0 duplicate · 0 unreadable · per-category counts reconciled); `exceptions-and-unreadable-files.md` for any gaps.
- `references/research-cards/<category>/A#####.md` — **one structured card per paper** (research question, threat model, method, datasets, metrics, main + negative findings, author + reviewer limitations, reproducibility, design/impl/eval/deploy/monitoring implications, applicability boundaries, evidence strength). The primary evidence unit — **cite by id**.
- `references/ontology.md` + `ontology.json` — normalized assets / adversaries / surfaces / attacks / defenses / evidence vocab with corpus frequencies; `paper-to-ontology-map.jsonl` = per-paper tags; `research-relationship-graph.json` = queryable edges (which attacks target an asset · which defenses co-occur with an attack · under which threat models · with what evidence).
- `references/syntheses/<category>.md` — **8 category syntheses** (threat/attack/defense families, replicated vs contested findings, defense bypasses, benchmark limits, product/architecture/launch implications, foundational + frontier papers, source map).
- `references/cross-cutting/*.md` — **8 chapters** that emerge only across papers (AI/LLM safety, adversarial ML, privacy, retrieval/RAG, network/cyber, model-IP, deepfake/forgery, defense-in-depth).
- `references/patterns/*.md` — **28 engineering control playbooks** (policy/permission gates, tool/capability isolation, sandboxed execution, human approval, retrieval authorization, prompt-injection containment, context/memory isolation, least-privilege credentials, tamper-evident traces, signed provenance, model-extraction defenses, DP, adversarial training, backdoor detection, deepfake detection, watermarking, network segmentation, runtime anomaly detection, adaptive red-teaming, holdout protection, incident containment, safe rollback, kill switches, …). Each: threat model · control mechanism · correct vs **fragile** implementation · verification · metrics/thresholds · adaptive-adversarial tests · telemetry · known bypasses · residual risks · relevant paper ids · evidence strength · **when NOT to use**.
- `references/source-index/` — by-id / by-category indexes + **`relevance-triage.md`**: a heuristic split of the 432 into **core 137 / adjacent 245 / peripheral 50** relative to Origin/Passport agent-security — so you don't over-weight off-topic ML papers as if they were agent-security evidence.

**To find the right evidence for a decision:** start at the relevant `syntheses/<category>.md` or `patterns/<control>.md` (see `patterns/INDEX.md`) → use `ontology.md` / the relationship graph to jump from an asset/attack/defense to papers → open `research-cards/` for depth → confirm the id in `source-index/`. See `references/README.md` for the map and the search recipes.

> **Maturity (read before lifting a pattern as a spec):** a 10-lens adversarial review (`final-quality-review.md`) rates this **fit as a reference/knowledge skill**, **not yet a build-ready spec**. The patterns are research-grounded *design guidance*; five cross-pattern seams are open work, not settled controls — eval-awareness defeater, un-owned root-of-trust/attestation, fail-closed≠halt for embodied actuators, no inter-agent authorization pattern, no canonical trace schema (some runtime figures are transplanted analogies). See `references/README.md` §"Maturity & known gaps" and the QA Top-8 (#4–8).

### Research-to-decision framework (A→H)
For any proposed feature / model / control / architecture, work these and write the answers into the design doc:
**A. User value** (outcome, friction, who's affected) · **B. Threat & harm** (assets, adversary, access/capabilities, credible harms, assumptions) · **C. Capability vs permission** (what it *can* do vs is *permitted* to; where permission is enforced; can the actor influence that point?) · **D. Verification** (which independent component verifies the action; deterministic/probabilistic/model/human; verifier integrity; can it be gamed?) · **E. Evidence** (what trace proves what happened — complete, replayable, tamper-evident, attributable; does it capture denied/failed actions too?) · **F. Metrics** (FAR/FRR, ASR, detection, precision/recall, calibration, privacy budget, utility loss, robustness under shift, latency, time-to-detect/contain/recover) · **G. Launch gates** (min evidence; blocking vs non-blocking; red-team done; holdout + adaptive-attack perf; independent review; rollback + IR readiness; **named residual-risk owner**) · **H. Residual risk** (what remains possible, what's untested, fragile assumptions, owner, rollback triggers).
Keep the distinctions explicit: **capability ≠ permission ≠ verification ≠ evidence ≠ residual risk**, and name the **autonomy level**.

### Evidence discipline (non-negotiable)
- **Trace every substantive claim to a paper id.** Distinguish direct paper finding vs reviewer synthesis vs engineering inference vs recommendation vs open question.
- **Calibrated language only** — "demonstrated under the evaluated threat model", "reduced ASR against the tested attacks", "not evaluated against", "requires production validation". Never *secure / unbreakable / proven safe / eliminates / guarantees*.
- **Conflicting research:** present both sides with their threat models + evidence strength — don't flatten (the syntheses' *Conflicting findings* + *Defense bypasses* sections are the anchor).
- **Insufficient evidence:** say so, state the evaluation that would resolve it, and default to the more conservative **fail-closed** control.
- **Lab ≠ production:** an evaluated result is not a production guarantee; name the assumptions that must hold.

### Invoke this (research-backed) for
Threat-model an agentic workflow · design prompt-injection defenses for enterprise RAG · compare privacy-preserving training · define an evaluation plan for model-extraction resistance · review whether a watermarking claim is defensible · build a deepfake-detection launch plan · design permission/verification gates for an autonomous agent · assess a defense against an adaptive attacker · create red-team cases for multi-agent deception · define telemetry for privacy leakage · judge whether a benchmark supports a production claim · convert findings into PRD requirements · build a launch-gate scorecard with evidence thresholds · identify the strongest papers for a proposed architecture.

### Do NOT invoke this for
General coding / refactoring with no security or agent-safety dimension · a substitute for reading the source papers on a load-bearing decision (cards cite the PDF path — read it) · a production-certified control library (patterns are design guidance, not build-ready specs — see the Maturity note) · absolute assurances ("prove this is secure"): this skill answers in *evidence + residual risk*, never guarantees.

### Codebase / design-review audit recipe
When auditing a module, service, or design doc for comprehensive coverage, run this loop (it *is* the A→H framework applied):
1. **Enumerate** — from the code/design, list the **assets**, **adversaries**, **attack surfaces**, and **trust boundaries** using the `ontology.md` vocabulary (or `scripts/search.py asset <token>`).
2. **Map attacks** — for each asset/surface, pull the relevant **attack classes** (`search.py attack <token>` → papers; the relationship graph → which attacks target which asset).
3. **Map controls** — for each live attack, pull the matching **defense playbook** (`patterns/INDEX.md` / `search.py pattern <term>` / `search.py mitigations <attack>` = what to build). For every enforcement point apply the **CPVER lens**: is *Capability* separated from *Permission*, where is it *Verified*, what *Evidence*/trace proves it, and who owns the *Residual risk*?
4. **Find the gaps** — flag every attack with **no owning control**, every control that is *fail-open* where it should be *fail-closed*, every claim with **no evidence tier**, and check it against the five open seams in `references/README.md` §Maturity (eval-awareness, root-of-trust, embodied safe-state, inter-agent authz, trace schema).
5. **Launch-gate scorecard** — output a table: control · threat covered · evidence strength (strong/moderate/preliminary/insufficient) · paper ids · residual risk · owner · blocking? — using `patterns/defense-in-depth.md` §10 as the template.

Copy-paste invocation: *"Use guardian-agent-foundations to audit `<path or design doc>`: enumerate assets/adversaries/surfaces, map attacks→controls with the CPVER lens, flag uncovered attacks and fail-open gaps, and produce a launch-gate scorecard with evidence tiers, paper ids, and residual-risk owners."*

## Growing this skill

The user actively feeds `/Users/bohueilin/Documents/Research Papers/Virtue AI/`. When asked to ingest new content
(or when you notice files not yet covered in `references/papers.md` / `references/products.md`):

1. List the folder and diff against the "Corpus index" at the bottom of `references/papers.md` and
   `references/products.md` to find new files.
2. Read each new PDF (for long PDFs pass the `pages` parameter to the Read tool, in batches).
3. For each: add a digest in the matching reference file (papers vs. products) using the existing template
   (id/title, problem, method, key concepts, results, vocabulary, physical-AI hook).
4. Fold genuinely new cross-cutting ideas into `worldview.md` / `architecture-patterns.md`, new terms into
   `glossary.md`, and new threats into `threat-models.md` — don't duplicate; extend.
5. Update the "Corpus index" so the next ingest knows what's already covered.

Keep entries dense and technical — this corpus is source material for product design, not marketing.

**Refreshing the 2026 landscape** (separate from PDF ingest): when the user asks to update on the field, run a
web sweep (Virtue AI corporate/product news, new orbit papers on arXiv, standards/incidents, the agent-identity
market, interview signal) and fold verified findings into `landscape-2026.md` / `interview-agent-security.md`,
with new identity items into `agent-identity.md` §7 and new papers into `papers.md`. Always keep a URL + date +
confidence (verified / single-source / inferred) per finding, and note the "as of" month at the top of the file.

**Maintaining the AAAI-26 research base** (separate from the Virtue-AI worldview ingest above): the corpus is a
reproducible pipeline, not hand-curation. To add or refresh papers, follow the incremental procedure in
`RESEARCH_UPDATE_LOG.md` — `scripts/build_manifest.py` detects new/changed files (content hash + `card-missing`),
the card workflow extracts only the missing cards, `scripts/assemble_ontology.py` rebuilds the ontology + graph,
only affected category syntheses are recomputed, and `tests/validate.py` re-checks the §7 gates. **Stable ids
(`A<article-id>`) never change**; update `SKILL.md` only when a control pattern's guidance materially shifts. See
`references/README.md` for the layer map + `scripts/search.py` recipes, and `CHANGELOG.md` for build history.
