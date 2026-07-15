# Virtue AI Products & Positioning

The product/market corpus (blog posts) — what the platform does and the naming patterns to reuse for Origin.

## Company frame
Virtue AI: AI-agent security / guardrails company founded by academics — **Bo Li** (CEO; UIUC), **Dawn Song**
(Board; UC Berkeley), **Sanmi Koyejo** (Head of AI; Stanford), Carlos Guestrin. Flagship platform **AgentSuite**,
a **two-sided model**: **AgentSuite-Blue** (defense: runtime security, governance, observability) and
**AgentSuite-Red / VirtueRed** (offense: red-teaming + validation). Core thesis: *secure agents as complete
systems, not at the prompt layer.*

## The Blue side (defense / observability / enforcement)

- **Shadow AI** — discovery layer. A lightweight endpoint collector (Linux/macOS/Windows) that detects AI at the
  *system* level — commercial tools (ChatGPT, Claude, Copilot), self-hosted models, browser extensions, IDE
  plugins, informal agentic pipelines — with **no domain allowlist required**. **Agent Behavior Analysis**
  captures the full behavioral *sequence* (order, structure, context across process/network/file/tool activity),
  reasoning over how actions *connect* vs. signature matching. The **Shadow AI Dashboard** maps which agents on
  how many devices and which policy triggered a flag; the full **agent action trajectory** is pullable on demand.
  Native integration with CrowdStrike Falcon & Microsoft Defender. *(The "autonomy trace" foundation.)*

- **PolicyGuard** — runtime policy definition + enforcement. Policies authored in **natural language** *or*
  auto-extracted from existing docs (ingests **PDF/JSON** → structured enforceable controls). **Action-level
  enforcement**: evaluates **agent traces and function calls**, applying policy to inputs, outputs, and the
  actions between — following the **full decision chain** across tool calls and multi-step workflows. **Original-
  language evaluation** (lightweight runtime model, no translation blind spots). **Async explainability** — every
  allow/block carries a rationale generated asynchronously (**zero added latency**). **Policy Lab** — backend
  agents that analyze coverage, close gaps, and "Improve Policy" against custom datasets. Centralized dashboard
  (queries, violations, policy groups, users, API keys, latency). Metrics per guard/policy group: F1, Recall,
  FPR, Accuracy, Precision. Deploys on-prem / cloud / SaaS. Sample violation taxonomy: Prompt Injection &
  Command Hijacking (34%), Sensitive Data / Privacy (14%), Unauthorized Action & Privilege Escalation (6%),
  Illegal/Harmful Content (4%).

- **ActionGuard** — runtime monitor that **blocks malicious tool calls before they fire** (the active action-level
  blocking layer; cf. pattern P1).

- **MCPGuard** — scans MCP tools & source code for hidden prompt injections, vulnerabilities, and data-leakage
  paths (the MCP/tool enforcement level).

- **VirtueGuard-Code** — purpose-built, *small* code-vulnerability-detection model. Ranks **#1 in overall F1**
  (function- and repo-level, C/Python/Java): **+5.9 F1 over GPT-5.3, +7.0 over Claude Opus 4.6**; **Precision
  0.896** vs ~0.66 for general models. Integrates into VS Code, VSCodium, Gitpod, Eclipse Theia, Cursor,
  Windsurf, CI/CD; flags insecure patterns / unsafe ops / vulnerable deps *before merge*, prioritized by severity
  & privilege impact, with review-ready explanations. **Metric: "Guard Score"** plotted vs. latency ("top-left =
  high Guard Score, low latency"). Thesis: **AI security is a specialized layer, not a byproduct of general
  intelligence** — "bigger isn't better for security; specialized is."

## The Red side (offense / validation)

- **Agent ForgingGround** — enterprise-scale, security-focused **testing ground**: **50+ production-grade
  enterprise environments** (Databricks, Google Workspace, PayPal, ServiceNow, Atlassian), each **generated from
  the ground up** and wrapped as an **MCP with identical tool structure**, mirroring both user and agent (MCP +
  HTML) interfaces. **Built-in red-teaming agents** stress-test single- and multi-agent systems with **1,000+
  proprietary red-teaming algorithms** (injection skills, attack algorithms, memory). **Verifiable Attack Judge**
  — fully rule-based, deterministic final-outcome check against environment state (**Task Pass/Fail × Attack
  Pass/Fail**) → reproducible, benchmarkable. Threat models: **Direct** (malicious user) & **Indirect** (user +
  attacker), across Environment / MCP & Tool / Prompt Injection. Runs before/during/after deployment, CI/CD-
  integrable; supports OpenAI Agents SDK, ChatGPT Atlas, Google ADK, Claude Code SDK, Cursor, LangChain.

- **VirtueRed (for Agent)** — the engine organizing **policy-based risk categories** (Healthcare, Customer
  Service, CRM, E-Commerce, Finance, OS, File system, Legal, Telecom, Research, Travel, HR, Workflow, Coding,
  RecSys) and real-world use-case-driven risks. (The product face of the RedCodeAgent / ARMs / MASTRIKE research
  line.)

## External validation & framing

- **Gartner "Guardian Agents"** (the market category Origin should align to). Gartner's definition:
  > *"AI agents make deliberate choices, introducing new risks beyond traditional AI. Guardian agents supervise
  > AI agents and help ensure their actions align with goals and boundaries: monitoring and blocking risky
  > actions and enforcing policies across platforms."*
  Virtue AI recognitions (2026): Representative Vendor, Market Guide for Guardian Agents (Feb); Sample Vendor,
  Hype Cycle for Agentic AI (Apr); Sample Vendor, Hype Cycle for SRE (2026). Unifying claim across all three:
  *"as agentic systems scale, human oversight alone cannot keep pace; organizations need AI-native controls that
  discover, monitor, and govern AI agents end-to-end."*

- **NIST CAISI (Center for AI Standards & Innovation)** — issued an RFI on AI agent security; Virtue AI's comment
  is the source of the canonical **stateless/deterministic/bounded → stateful/probabilistic/unbounded** framing
  and the "**AI agents are becoming operational infrastructure**" line. NIST-cited risk evolution: direct prompt
  injection → indirect injection, tool abuse, **memory poisoning**, autonomous misuse, plus **backdoor attacks**
  and **specification gaming**. (RFI = public consultation, not regulation.)

- **CTRL+AI** — Virtue AI's conference (June 4, 2026, The Presidio, SF) to close the *research-to-operations gap*
  between AI-security researchers and CISOs ("dangerous lag").

## Naming patterns to reuse for Origin
- `*Guard` for enforcement components: PolicyGuard, ActionGuard, MCPGuard, VirtueGuard-Code.
- `*ForgingGround` / `*Red` for the offensive/validation side.
- `Shadow *` for the discovery layer.
- Umbrella suite split into **Blue / Red**.
- Standard nouns: **Guards, Policy Groups, Policy Lab, Guard Score, Verifiable Attack Judge, agent action
  trajectory, continuous operational record, delegated authority, constitution.**

---

## 2026 UPDATE — Virtue AI corporate + product changes (Jul 2026 sweep)

**Provenance caveat (read first):** the founder-researchers whose work this whole skill distills — **Bo Li, Dawn
Song, Sanmi Koyejo** — were **hired by Meta Superintelligence Labs (reported Jun 25 2026)**; Li & Song report to Nat
Friedman, Koyejo to Rob Fergus (FAIR). On **Jun 29 2026** Virtue AI named **Sohaib Shaikh** (ex-C3 AI GVP Sales) as
**CEO**, Daniel Le (ex-dbt Labs) CFO/COO — a shift from **founder-researcher-led → GTM-led**. So: the *worldview* in
this skill is now largely *inside Meta*; the *company* Virtue AI continues as a product vendor. When citing "Virtue
AI's thesis," attribute to the **founders/research**, which is the durable part.

**Product line as of mid-2026** (virtueai.com; tagline "The Leading Enterprise AI Security Platform for Agents &
LLMs"; **600% YoY growth**; still **$30M** total raised — seed + Series A, Walden Catalyst / Lightspeed):
- **AgentSuite** (launched **Jan 29 2026**, "first end-to-end security platform for enterprise AI agents"),
  reorganized into:
  - **AgentSuite-Red** — enterprise-scale agent red-teaming, 50+ sandboxed MCP environments, 100+ agent-specific
    attack strategies (prompt/tool/environment injection). (The **Agent ForgingGround** capability.)
  - **AgentSuite-Blue** — security/governance/compliance: **MCPGuard** (scans MCP server/tool code for CWEs +
    injections), **ActionGuard** (real-time enforcement on action trajectories), **Shadow AI** discovery, and a new
    **Unified Agent Gateway** (single enforcement chokepoint between agents and tools).
- **VirtueRed** — continuous automated red-teaming (100+ algorithms, 1,000+ risk categories).
- **VirtueGuard** — real-time guardrails across text/image/video/audio/code, 100+ languages, **<10ms** latency.
- **VirtueGov** — **new** governance product (appears in footer/homepage, 2026).
- **Shadow AI** went to a launched endpoint product **Jun 23 2026** (Linux/Win/macOS collector; can take rogue
  agents offline; standalone or alongside CrowdStrike Falcon / MS Defender). Head of Agent Security: **Wenbo Guo**.
- **Customers now public**: AllianceBernstein (case study), Uber, NVIDIA, OpenAI, Zoom, Microsoft, Google DeepMind.
- **Recognition**: Representative Vendor, first-ever **Gartner Market Guide for Guardian Agents** (Feb 2026; blog
  Mar 11); Sample Vendor in Hype Cycles for Agentic AI + SRE 2026. Submitted formal commentary to **NIST CAISI**'s
  agent-security RFI. Held inaugural **CTRL+AI** conference **Jun 4 2026** (Presidio, SF) — ~3 weeks before the Meta
  departure was reported.

> Naming note: `Guard` for enforcement, `*Red` for offense, `Shadow *` for discovery, Blue/Red suite split — all
> confirmed still in use in 2026; **`Gov`** joins the pattern for governance. Origin's `*Guard`/trace/broker naming
> stays consistent with the category leader's lexicon.

## Corpus index (products) — update when ingesting new files
Covered blog-post PDFs in the folder:
- Shadow AI (security-team visibility) ✓
- Agent ForgingGround (built-in red-teaming agents) ✓
- PolicyGuard ✓
- NIST national conversation on AI agent security ✓
- Gartner Hype Cycle for SRE 2026 ✓
- Gartner Market Guide for Guardian Agents ✓
- Gartner Hype Cycle for Agentic AI ✓
- VirtueGuard-Code #1 ranking ✓
- CTRL+AI conference (closing research↔risk gap) ✓
