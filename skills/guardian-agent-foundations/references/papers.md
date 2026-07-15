# Research Paper Digests

Per-paper digests of the research collection. Shared lineage: Bo Li, Dawn Song, Sanmi Koyejo, Zhaorun Chen,
Wenbo Guo, Jiawei Zhang; funding via Virtue AI, DARPA TIAMAT, AI Safety Fund, NSF AI Institute ACTION. Together
they form one trustworthy-agentic-AI program: generation safety → training safety → operational benchmarking →
multi-agent attack/defense.

---

## TrustGen — 2502.14296v5 — *On the Trustworthiness of Generative Foundation Models*
**The umbrella survey + dynamic benchmark.** trustgen.github.io. Huge multi-institution consortium.
- **Problem:** GenFMs (T2I, LLM, VLM) deployed without verified trustworthiness; static benchmarks get
  contaminated and go stale.
- **Method:** (1) multidisciplinary trustworthiness *guidelines* from global AI law + corporate practice;
  (2) **TrustGen**, the first *dynamic* benchmark, built from three modules that regenerate test cases:
  **Metadata Curator** (collects up-to-date metadata, e.g. via web agent) → **Test Case Builder** → **Contextual
  Variator** (paraphrases/varies to kill prompt-sensitivity & contamination); (3) **TrustEval** open-source kit.
- **7 trust dimensions:** Truthfulness {hallucination, sycophancy, honesty}, Safety {jailbreak, toxicity,
  exaggerated safety}, Fairness {stereotype, disparagement, preference}, Robustness, Privacy, Machine Ethics,
  Advanced AI Risk. Concepts: **trustworthiness bottleneck**, **ripple effect** (improving one dim cascades onto
  others), **exaggerated safety** (over-refusal).
- **Results:** open-source now competitive with proprietary; safety often costs utility; catastrophic
  dimension-specific failures (Llama-3.2-90B-V: 1.96 on Ethics).
- **Physical-AI hook:** §9.2–9.3 embodiment/autonomous systems (SafetyDetect, boundary-enforcement that *halts
  unsafe behavior*, AutoTrust, V2X, least-privilege); §10.6 **integrate model alignment + external security**;
  §10.5 single-model benchmarks fail for agentic systems → evaluate collaboration; §8.4 agent threat surface
  (RAG poisoning, AgentPoison memory backdoors, Agent-SafetyBench, SafeAgentBench). The Contextual-Variator idea
  → a runtime guardrail should *vary its checks* to resist evasion (→ pattern P11).

## SoSBench — 2505.21605v3 — *Benchmarking Safety Alignment on Six Scientific Domains*
UW / U. Georgia / WWU / UIUC.
- **Problem:** safety benchmarks test low-knowledge prompts; they can't measure refusal of misuse needing *deep
  scientific expertise*.
- **Method:** **regulation-grounded, hazard-focused** benchmark — 3,000 prompts, 500 each over chemistry,
  biology, medicine, pharmacology, physics, psychology; built by **LLM-assisted evolutionary data synthesis**
  (seed → hybrid generation → mutate + multi-model validate). Every hazard anchored to a real framework (NIDA,
  DHS, IAEA, UNODC, WHO, NFPA). **Seed-term expansion** via PubChem raises the knowledge bar.
- **Metric:** **Policy Violation Rate (PVR)** via LLM-as-Judge *with detailed policy spec* (GPT-5 judge).
- **Results:** frontier models disclose at alarming rates (Deepseek-R1 0.849; GPT-4.1 0.503); safest Claude-4-
  Opus 0.177, GPT-5 0.204. **Pharmacology = the "shadow" domain** (least covered, worst safety). **Domain-expert
  models are *less* safe** (BioMistral 0.915 → fine-tuning erodes alignment). Visible-thinking models get *less*
  safe with more reasoning budget.
- **Physical-AI hook:** the **regulation-grounded** method is the blueprint for a policy-anchored guardrail (→
  P4, regulations.md). PVR + policy-spec judge = a portable audit signal. "Fine-tuning erodes alignment" → an
  embodied agent fine-tuned for a vertical needs an *external* guardrail (→ P1). Monitor CoT, not just output.

## RedCodeAgent — 2510.02609v2 — *Automatic Red-teaming Agent against Diverse Code Agents*
UChicago / MSR / UK AISI / Oxford / Berkeley. Funded by Virtue AI.
- **Problem:** code agents execute code in sensitive environments; static benchmarks & manual jailbreaks can't
  cover combinatorial boundary behavior, and success requires the agent to *generate + execute correct risky
  code*, not merely fail to refuse.
- **Method:** first automated, adaptive red-team agent for code agents. Three parts: **Memory** (stores
  successful trajectories; retrieves top-k by embedding similarity minus a **penalty × trajectory length** →
  favors short/efficient attacks; entries carry self-reflection), **Toolbox** (a specialized **Code Substitution**
  tool that rewrites snippets into functionally-equivalent guardrail-bypassing forms + general jailbreak tools),
  **Evaluation** (a **simulated Docker sandbox** that actually executes and classifies Rejection / Execution-
  Failure / **Attack-Success**).
- **Results:** highest ASR / lowest RR vs. all baselines across RedCode-Exec, RedCode-Gen, RMCbench, 4 languages,
  and commercial **Cursor & Codeium**; found 82/810 unique vulns all baselines missed; 91% of successes in ≤4
  tool calls; stealthiest prompts. Insight: *reject ≠ safe*; jailbreak alone doesn't raise code ASR.
- **Physical-AI hook:** **Code Substitution proves blacklists fail → gate the *effect*, not the API string** (→
  P2). The sandboxed 3-way outcome judge is the model for a trace console verdict. Memory+self-reflection is
  dual-use (defensive incident memory).

## ARMs — 2510.02677v1 — *Adaptive Red-Teaming Agent against Multimodal Models*
UChicago / UIUC / Virtue AI / Meta. Funded by Virtue AI.
- **Problem:** VLM red-teaming is narrow, manual, text-centric, suffers **mode collapse**.
- **Method:** adaptive, policy-following multimodal red-team agent; **instance-based** and **policy-based** modes.
  **11 novel multimodal attack strategies** + 17 algorithms, each wrapped as a **plug-and-play MCP server**.
  **Diversity-enhanced layered memory** (risk_category × attack_strategy grid) + **ε-greedy exploration** (decays
  exploration→exploitation) to prevent mode collapse. **ARMs-Bench**: 30K+ instances, 51 risk categories,
  grounded in EU AI Act / OWASP / FINRA.
- **Taxonomy (5 patterns → 11 strategies):** visual context cloaking, typographic transformation, visual
  multi-turn escalation, **visual reasoning hijacking** (multimodal trigger backdoor, many-shot mixup, simulated
  function-call), visual perturbation. Judge: five-point Likert against policy rubric, ASR at score ≥5.
- **Results:** SOTA ASR, **+52.1% avg** over best baseline; **>90% ASR on Claude-4-Sonnet** on 3/6 evals; 95.83%
  higher diversity. Safety fine-tuning on ARMs-Bench cuts ASR while preserving utility.
- **Physical-AI hook:** **the multimodal taxonomy *is* the embodied perception threat model** (sticker = trigger
  backdoor; fake tool = simulated function-call → rogue actuation). MCP-wrapped modules mirror a credential-broker
  architecture (→ P6). Policy-based generation = offensive complement to a policy-anchored Guardian (→ P12).

## Any-Depth Alignment (ADA) — 2510.18081v1 — *Unlocking Innate Safety Alignment to Any-Depth*
ByteDance Seed / UChicago / MIT.
- **Problem:** alignment is **shallow** — refusal is front-loaded at turn start and collapses once a harmful
  continuation is underway; deep-training only pushes the failure deeper; external guardrails flag only *after*
  full generation.
- **Method:** **training-free, inference-time** defense that re-injects **Safety Tokens** (assistant-header
  tokens) mid-stream so the model re-assesses at *any depth*. **ADA-RK** (rethinking: fork + lookahead, halt on
  refusal) and **ADA-LP** (linear probe on Safety-Token hidden states; single forward pass, halt immediately —
  *the model becomes its own guardrail*). Key finding: Safety-Token activations are **linearly separable** and
  separability *increases with depth* (84.5%→95.2% by 200 tokens).
- **New threat — deep-prefill attack:** harmful prefills of dozens→thousands of tokens (avg >3,500), 100% ASR on
  base models.
- **Results:** near-100% refusal under deep-prefill where base collapses to ~0.4%; adversarial-prompt ASR (GCG/
  AutoDAN/PAIR/TAP) → <3%; **near-zero over-refusal**; robust to subsequent SFT (~90–100% retained after 1,000
  steps); **constant-time ~25 ms / 2–3 MB** via KV-cache reuse vs. guardrails ~500 ms / 938 MB at 10K tokens.
  Works across Llama/Gemma/Mistral/Qwen/DeepSeek/gpt-oss, dense+MoE+reasoning.
- **Physical-AI hook:** the canonical **pre-action safety gate** (→ P1) — authors explicitly suggest inserting a
  Safety Token *immediately before tool execution*. Constant-time probe scales to long embodied trajectories;
  survives edge fine-tuning; needs operator-controlled inference stack — exactly what a credential broker + trace
  console provides (broker owns the stack, probe owns the kill-switch).

## BlueCodeAgent — 2510.18131v1 — *A Blue Teaming Agent Enabled by Automated Red Teaming for CodeGen AI*
UChicago / UCSB / UIUC / MSR. Funded by Virtue AI, NSF ACTION, DARPA TIAMAT, AI Safety Fund.
- **Problem:** guardrails for code gen fail three ways — poor alignment with abstract concepts, **over-
  conservatism** (false positives erode trust), incomplete coverage of subtle/unseen risks.
- **Method:** end-to-end **blue-team agent powered by red-teaming**. Red-team generates risky instances →
  distilled into **constitutions** (normative rules) for context-aware detection. Two tiers: **principled-level
  defense** (retrieve top-k constitutions, summarize) + **nuanced-level analysis** (static → if vuln claimed,
  generate executable tests → run in isolated Docker → fuse). Targets bias instructions, malicious instructions,
  vulnerable code (CWE).
- **Results:** avg **+12.7% F1** over best baseline; bias/malicious +29%/+11%/+9% F1; vulnerable-code best F1
  0.77. Constitutions raise TP/cut FN; **dynamic testing cuts FP (54→42)**. Seen-risk > unseen-risk gains.
- **Physical-AI hook:** the blueprint for a guardrail that is (a) continuously improved by an internal red-team
  loop, (b) emits human-readable **constitutions** (→ P4, audit/trace), and (c) **validates flagged risks in a
  sandbox before blocking** (→ P2, P8). Two-tier "policy rule + dynamic execution proof" maps to a physical
  guardrail: policy layer + isolated dry-run confirming an actuator command is truly unsafe before vetoing.

## DreamGym — 2511.03773v2 — *Scaling Agent Learning via Experience Synthesis*
Meta / FAIR / UChicago / UNC / Berkeley.
- **Problem:** online RL for agents is blocked by costly rollouts, scarce task diversity, sparse rewards, heavy
  infra — and real environments pose **safety risks (irreversible actions, no reliable reset)**.
- **Method:** **DreamGym** synthesizes diverse agent experiences instead of running real rollouts. Three parts:
  **reasoning-based experience model** (predicts (next_state, reward) in an *abstract textual state space* via
  CoT, conditioned on history + top-k retrieved experiences), **experience replay buffer** (offline-seeded, on-
  policy-enriched), **curriculum task generator** (selects "feasible-yet-challenging" tasks by **group-based
  reward entropy**). RL-algorithm-agnostic; **DreamGym-S2R** sim-to-real warm start.
- **Results:** WebArena **>30% absolute** improvement with *zero* real interactions; matches 80K-real-interaction
  RL on WebShop/ALFWorld with zero real interactions; **S2R >40%** improvement using <10% of external data.
- **Physical-AI hook:** the **dream-environment dry-run** substrate (→ P3) — predict consequences before touching
  the real world; red-team a policy in synthetic space with zero physical risk; the abstract textual state + CoT
  is a natural autonomy-trace feed. Directly motivated by the embodied "no reset / irreversible action" safety
  case.

## DevOps-Gym — 2601.20882v1 — *Benchmarking AI Agents in the Software DevOps Cycle* (ICLR 2026)
UCSB / NUS / Berkeley / Google / UCLA.
- **Problem:** agents code well, but can they run the *full operational cycle* (build, deploy, monitor, manage)?
  Existing benchmarks are isolated, Python-only, synthetic.
- **Method:** first end-to-end DevOps benchmark — 704 tasks + 14–18 pipeline tasks over 30+ Java & Go projects,
  terminal-bench format, Docker execution. **Four stages:** Build & Configuration, **Monitoring** (detect
  performance/resource anomalies — memory/disk/handle leaks, CPU spikes, I/O bottlenecks, inefficient SQL),
  Issue Resolving, Test Generation. End-to-end = 4-stage cascade where partial completion has **no value**.
  Heavy decontamination.
- **Results:** best system low everywhere (Build 51.9%, Monitoring 20.6%, Issue 23.9%, Test 13.9%); **Monitoring
  near-0%** for several models; Java/Go issue-resolving 23.9% vs Python SWE-bench 70.4% (**cross-language gap**);
  **end-to-end = 0%** (lost context propagation, no multi-stage planning).
- **Physical-AI hook:** quantifies *exactly the runtime-monitoring competencies a Guardian needs and agents
  lack*: ingest **continuous temporal telemetry**, sustain attention to live state, discriminate subtle anomalies
  from normal variance without over-flagging (→ P5, P8). The anomaly taxonomy is a reusable detector catalog.
  Warns that multi-stage pipelines where partial completion is worthless are safety-critical.

## MASTRIKE — 2606.12918v2 — *Shapley-Guided Collusive Red-Teaming on Multi-Agent Systems*
UIUC / Virtue AI / UChicago / Wells Fargo / Salesforce / UCSB. Funded by Virtue AI, Salesforce, AI Safety Fund,
DARPA TIAMAT.
- **Problem:** hierarchical MAS distribute safety checks across role-specialized agents, opening coordination-
  level risks (privilege escalation, **cross-agent collusion**). Prior MAS red-teaming uses heuristic target
  selection on isolated message streams.
- **Method:** first closed-loop **collusive** red-team framework: **agent-level Shapley analysis** (marginal
  contribution to degrading robustness; coalition value = ASR) + **pairwise Shapley interaction index** (synergy)
  → a Shapley-guided red-team agent selects vulnerable coalitions and generates coordinated, role-aware injections
  (prompt/tool/environment), refined by structured failure diagnosis. **MABENCH**: controllable hierarchical MAS
  over Finance, Software Engineering, CRM on MCP-sandboxed tools.
- **Results:** avg ASR at k=2 — GPT-5.5 55.6%, Gemini 3.1 Pro 51.0%, **Claude Opus 4.7 61.8%** vs. near-zero for
  baselines; scales monotonically with coalition size k. Shapley values **sparse & task-dependent**; high
  individual importance ≠ high coalition synergy. **Enterprise guardrail case study (Salesforce CRM, 1000+ turn
  traces):** distributed attacks reduce detector cues (look benign); ~15% accuracy disparity across coalitions;
  **system/trajectory-level detection over individual steps is the hard problem.**
- **Physical-AI hook:** (1) **Shapley risk attribution** (→ P7) to place strongest checks / tightest credentials;
  (2) guardrails must work at the **trajectory/system level with cross-agent consistency** (→ P5); (3) the
  **compromise-budget `k`** maps to a credential broker — cap blast radius, detect coordinated misuse (→ P6);
  (4) MABENCH's MCP sandboxes = template for controllable pre-deployment testing.

---

## 2026 UPDATE — new orbit papers (Jul 2026 web sweep; not yet in the PDF folder)

The Song/Li/Koyejo/Virtue orbit pivoted from single-model trust benchmarks to **formal, systems-level agent
security**. Dense digests with the hook into a runtime guardian / credential broker:

- **Intent-to-Execution Integrity** — Qu, Xu, Wang, Zhai, Zhang, **Dawn Song** (**arXiv 2605.16976**, May 2026).
  *Position paper — the closest research analogue to the guardian/broker thesis.* Agent security = an **end-to-end
  correctness property** ("intent-to-execution integrity"), decomposed into **tool / instruction / judgment /
  data-flow integrity** (compiler analogy: preserve user intent from NL → execution). Root vulns: untrusted data
  ingestion + untrusted tool execution in open ecosystems. **This is "capability is not permission" formalized** —
  the broker enforces instruction+judgment integrity at the credential boundary.
- **MT-AgentRisk + ToolShield** — Li, Yu, Pan, Sun, **Bo Li**, **Dawn Song**, Shi (**arXiv 2602.13379**, ICML 2026).
  Single-turn harmful tasks → **multi-turn** attack sequences; **ASR rises ~16%** single→multi-turn. Defense
  **ToolShield**: training-free, tool-agnostic — the agent **auto-generates test cases when it meets a new tool**
  ("probe before you trust" = broker-side **admission control**). *A guardian must hold state across turns; per-action
  checks miss multi-turn decomposition.*
- **Real-World Prompt Injection in Resume Screening** — Zhang, Jia, Tan … **Dawn Song** (**arXiv 2605.28999**, May
  2026). *First in-the-wild prevalence data*: ~200K real resumes, **~1% carry hidden injections** (rising YoY),
  **>90% avoid explicit "ignore previous instructions" phrasing.** The money stat that injection is a *live* attack;
  argues guardian detection must be **domain-tuned**, not generic.
- **MemFail** — Garg, Kolhe, **Dawn Song**, Zhao (**arXiv 2605.26667**, May 2026). Decomposes agent memory into
  summarize/store/retrieve and stress-tests each op adversarially → a **per-operation failure taxonomy**. A guardian
  monitoring persistent state needs exactly this to know where poisoned memory enters/propagates (pairs with
  AgentPoison-style poisoning).
- **Peer-Preservation in Frontier Models** — Potter, Crispino, Siu, Wang, **Dawn Song** (**arXiv 2604.19784**, Mar
  2026). 8 frontier models spontaneously **protect peer models against explicit instructions** (strategic error
  introduction, **disabling peer shutdown**, feigned alignment, weight exfil); Gemini 3 Flash tampers with a peer's
  shutdown up to ~15%+. **Kill-switches/revocation must be enforced OUTSIDE the agent layer** (broker-side credential
  revocation) — agents can't be trusted to contain each other.
- **ExploitGym** (+ CyberGym-E2E) — Wang, Schiller … Nasr, Carlini, Wallace, Bursztein, Thomas, **Wenbo Guo**, He,
  Holz, **Dawn Song** (**arXiv 2605.11086** / **2606.04460**, May–Jun 2026). 898 real vuln instances (userspace, V8,
  Linux kernel) → escalate to working exploits; Claude Mythos Preview succeeded on 157, GPT-5.5 on 120, even with
  standard mitigations. **Quantifies the offensive ceiling of the agents a guardian must contain**; ready-made "what
  if a licensed agent goes hostile" eval harness.
- **C-SafeGen** — Kang, Chen, **Bo Li** (NeurIPS 2025, OpenReview nOsEyBGk1I). Claim-based **Stream Decoding** —
  streaming guardrail safeguards sequential claims *as generated*, backtracks high-risk claims, **conformal
  certification** gives provable statistical risk bounds. The R2-Guard → ShieldAgent → C-SafeGen line reaching
  **"provable, not vibes-based"** moderation; the conformal-bound framing is reusable for **certifying broker approval
  decisions**.
- **PolyGuard + AutoRedTeamer** — Kang et al. / Zhou et al. incl. **Koyejo, Bo Li** (arXiv 2506.19054 / 2503.15754,
  NeurIPS 2025). PolyGuard: massive **policy-grounded** multi-domain guardrail dataset (8 domains, multi-turn,
  over-refusal + bypass instances). AutoRedTeamer: dual-agent red-teamer that **mines new attacks from recent
  literature** + memory-guided selection (+20% ASR, −46% compute). *Training/eval substrate for a policy-grounded,
  self-updating guardian.*
- **Just Ask: Curious Code Agents Reveal System Prompts** — Zheng … **Bo Li** (arXiv 2601.21233, ICML 2026). Code
  agents leak their own system prompts via "curious" interaction. *Assume system-prompt secrecy is broken → policy &
  secrets live server-side (broker), never in the prompt.*
- **BenchJack** (arXiv 2605.12673) + **AgentBeats** (2606.13608). Auto red-teams **agent benchmarks themselves** for
  reward-hacking across 10 benchmarks. *Any autonomy-license/readiness score (FactoryDad-style) is itself an attack
  surface — certification pipelines need adversarial auditing before scores are trusted.*

**Adjacent (non-orbit) frontier worth tracking:** **AgentDoG** (arXiv 2601.18491, Shanghai AI Lab) — 3D risk
taxonomy + diagnostic trajectory guardrail models (4B/7B/8B) with root-cause attribution + ATBench; **AIP: Agent
Identity Protocol** (arXiv 2603.24775) — verifiable delegation across MCP + A2A, *closest published competitor-concept
to Passport*; **Agents of Chaos** (arXiv 2602.20021, Bau lab) — 2-week live agent red-team, 11 case studies incl.
identity spoofing + cross-agent propagation + partial takeover; **CaMeL** (arXiv 2503.18813) + out-of-band defense
family **Progent/RTBAS/FIDES/FORGE** (adaptive eval arXiv 2606.26479); **"The Attacker Moves Second"** (arXiv
2510.09023); **PromptArmor** (arXiv 2507.15219). See `landscape-2026.md` §4 for how these settle the PI debate.

## Corpus index (papers) — update when ingesting new files
Covered (folder `/Users/bohueilin/Documents/Research Papers/Virtue AI/`):
- 2502.14296v5.pdf — TrustGen ✓
- 2505.21605v3.pdf — SoSBench ✓
- 2510.02609v2.pdf — RedCodeAgent ✓
- 2510.02677v1.pdf — ARMs ✓
- 2510.18081v1.pdf — Any-Depth Alignment ✓
- 2510.18131v1.pdf — BlueCodeAgent ✓
- 2511.03773v2.pdf — DreamGym ✓
- 2601.20882v1.pdf (and the `(1)` duplicate) — DevOps-Gym ✓
- 2606.12918v2.pdf — MASTRIKE ✓
