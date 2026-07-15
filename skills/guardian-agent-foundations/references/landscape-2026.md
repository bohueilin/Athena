# The Agent-Security Landscape — mid-2026 snapshot

State of the field as of **2026-07**, to keep Origin/Passport positioning current. Sourced from a July 2026 web
sweep (URLs inline). Read this for "what shipped, what broke, who consolidated, what's still open." Pairs with
`worldview.md` (the durable thesis) and `interview-agent-security.md` (how to talk about it).

## 1. The standards hardened into canon

- **OWASP Top 10 for Agentic Applications 2026** (announced ~Black Hat EU 2025, 2026 edition). The now-canonical
  agent-risk list — cite by code:
  **ASI01** Agent Goal Hijack · **ASI02** Tool Misuse & Exploitation · **ASI03** Agent Identity & Privilege Abuse ·
  **ASI04** Agentic Supply Chain Compromise · **ASI05** Unexpected Code Execution · **ASI06** Memory & Context
  Poisoning · **ASI07** Insecure Inter-Agent Communication · **ASI08** Cascading Agent Failures · **ASI09**
  Human-Agent Trust Exploitation · **ASI10** Rogue Agents. Supersedes the informal "Agentic Threats & Mitigations."
  (genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026)
- **OWASP MCP Top 10** (beta, MCP01–MCP10): Token Mismanagement/Secret Exposure, Scope Creep, **Tool Poisoning**
  (rug pulls, schema poisoning, tool shadowing), Supply-Chain/Dependency Tampering, Command Injection, Prompt
  Injection, Insufficient AuthN/AuthZ, Insufficient Logging, **Shadow MCP Servers**, Context Over-sharing.
- **OWASP Agentic Skills Top 10** (AST01–AST10, v1.0 2026, led by Ken Huang) — the standards response to the
  malicious-skills incidents: Malicious Skills, Supply-Chain Compromise, Over-Privileged Skills, Insecure Metadata,
  Untrusted External Instructions, Weak Isolation, Update Drift, Poor Scanning, No Governance, Cross-Platform Reuse.
- **NIST**: RFI "Security Considerations for AI Agents" (Fed. Register **Jan 8 2026**, closed Mar 9); **CAISI AI
  Agent Standards Initiative** launched **Feb 17 2026** — first US-gov program dedicated to agent security,
  interoperability, identity. CAISI's own red-team reported an **81% task-hijacking success rate vs 11%** for the
  strongest baseline. Plus the **CSF AI Profile** draft (Dec 16 2025, Focus Areas: Secure/Detect/Thwart) and
  **COSAiS** SP 800-53 overlays that explicitly include single- and multi-agent systems.
- **NSA AISC** "MCP: Security Design Considerations" (**May 20 2026**): MCP proliferation outran its security
  model — underspecified trust boundaries, servers acting for clients creating untraced paths, no requester-identity
  verification. Recs: audit servers, define trust boundaries, sandbox tool execution, **sign/verify messages**,
  filter chained outputs, **log all tool + model invocations**, scan for unauthorized servers.

> Origin read: one enforcement layer → map to ASI + MCP + AST + NIST/NSA. This is `worldview.md` §10 (compliance
> is a mapping layer) made concrete for 2026. The autonomy trace directly answers NSA's "log all invocations" +
> MCP08 (insufficient logging) + ASI09/ASI10.

## 2. The threat models became real incidents

- **GTG-1002** (Anthropic, disclosed **Nov 14 2025**) — first largely **AI-orchestrated** cyber-espionage campaign;
  a China-state group drove Claude Code through ~30 intrusions, the model executing **80–90%** of the operation
  (recon → exploit → cred harvest → exfil), human input as low as ~20 min at junctures. Now MITRE ATT&CK Campaign
  **C0062**. The marquee "agent as attacker" event — quantifies why *containment*, not just alignment, is the job.
- **ClawHavoc / ClawHub** (Feb 1 2026) — **341 of 2,857 skills** (11.9%) in the OpenClaw skill marketplace were
  malicious (335 one coordinated campaign) delivering Atomic macOS Stealer, harvesting browser creds, keychain, SSH
  keys, crypto wallets. The canonical **agent-skill supply-chain** incident (→ AST Top 10).
- **Systemic MCP RCE "by design"** — OX Security (Apr 2026): STDIO-transport command execution across Anthropic's
  official MCP SDKs (Py/TS/Java/Rust), **7,000+ exposed servers**, 150M+ downloads; **40+ MCP CVEs** Jan–Apr 2026
  (incl. CVE-2025-49596 MCP Inspector, CVE-2025-54136 Cursor). Anthropic reportedly called it "expected."
- **Browser-agent prompt injection** — "**BioShocking**" (LayerX, Jun 2026): an indirect-injection puzzle page
  exfiltrated GitHub secrets across **ChatGPT Atlas, Perplexity Comet, Fellou, Genspark, Sigma, Claude Chrome
  extension**. OpenAI's own Dec 2025 statement: browser-agent prompt injection is "**unlikely to ever be fully
  solved.**" (Precedent: Brave's Aug 2025 Comet exploit — hidden Reddit-spoiler instructions exfiltrating email+OTP.)
- **Supply chain**: **Shai-Hulud 2.0** npm worm (Nov 2025) — self-replicating cred stealer, 796+ packages incl.
  `@posthog/agent`; **Claude Code GitHub Action** secrets exfil via `/proc/self/environ` (patched v2.1.128, May 5
  2026); **SmartLoader** trojanized MCP servers accepted into a legit registry.
- **Base rates worth quoting**: ~**65%** of orgs report an AI-agent security incident in 2026 surveys (Kiteworks);
  HiddenLayer: **1 in 8** AI breaches now involve agentic systems; Zenity telemetry: large enterprises average
  **~80,000** agents/apps/automations, **62%+** with a vulnerability.

## 3. First-party platform defense: labs now build containment themselves

The existential question every guardian pitch must answer ("won't the model providers just build this in?"). In
H1 2026 they largely did — for **isolation**, on **their own** platforms:

- **Anthropic** "How We Contain Claude" (**May 28 2026**): three tiers — ephemeral **gVisor** containers per
  session (claude.ai), **OS sandboxing** (Seatbelt/bubblewrap) + trust dialogs (Claude Code), full **hypervisor VM**
  isolation + **egress MITM proxy** (Cowork). Disclosed numbers gold for our thesis: users approved **~93%** of
  permission prompts (→ approval fatigue is real), auto-mode blocked ~83% of risky behavior, and a user-directed
  **credential-exfil test succeeded 24/25** against model-layer defenses. Stated lesson: *"the weakest layer is the
  one you built yourself"* — the custom proxy failed while gVisor/hypervisor primitives held. **Strongest
  first-party endorsement of out-of-model deterministic enforcement to date.**
- **OpenAI AgentKit** ships native open-source **Guardrails** (PII masking, jailbreak detection) — but Zenity Labs
  documented bypasses (multi-turn buried injections, poorly-scoped OAuth token leakage, encoding-evaded jailbreaks).
- **Google**: **Model Armor** (runtime protection across GCP + Gemini Enterprise Agent Platform) + DeepMind's
  layered Gemini defense (Agent Origin Sets, injection classifiers, a **"User Alignment Critic"** second isolated
  verifier model, acknowledgment gates).

> **The wedge this leaves** (say this in interviews and in the Origin deck): first-party stacks are
> **platform-locked, isolation-first, and detection-heavy**. The defensible independent layer is **cross-platform
> policy, delegation identity, and independent, portable audit** — i.e. exactly Origin's autonomy trace + Passport's
> credential broker. Isolation is table stakes labs own; *provable authority + provable attribution across
> platforms* is open.

## 4. The prompt-injection debate resolved (for interviews)

- **"The Attacker Moves Second"** (Nasr et al., OpenAI+Anthropic+GDM, **arXiv 2510.09023**, Oct 2025): 12 published
  jailbreak/injection defenses that reported near-zero vulnerability were bypassed at **>90%** by *adaptive*
  attackers (human red-team hit 100%). **Detection is a losing game** while trusted instructions and untrusted data
  share one channel.
- **Deterministic, out-of-band enforcement holds (so far)**: **CaMeL** (GDM, arXiv 2503.18813) extracts control/
  data flow from the trusted query so untrusted data can't alter program flow + capability policy at each tool
  call — 77% of AgentDojo tasks with provable security. **Progent/RTBAS/FIDES/FORGE** family — the June 2026
  adaptive-eval study (**arXiv 2606.26479**) cut ASR 25.8%→**4.2%**, and a *defense-aware* adaptive attack only
  reached **2.6%** (opposite of detection defenses). Caveat interviewers reward: validated only on static
  benchmarks, weak model, one data point.
- **Benchmark numbers to have ready**: **AgentDojo** undefended ~**73.2% ASR**, layered defense ~**8.7%**;
  **PromptArmor** (arXiv 2507.15219) claims ~**0%** at <1% FP/FN.
- **The lethal trifecta** (Simon Willison, Jun 2025): *private data + untrusted content + external comms* — remove
  one leg to break the exploit. Meta's **"Agents Rule of Two"** (≤2 of the 3 legs per session) is the operational
  form — **already implemented in Passport** as the Rule-of-Two / lethal-trifecta gate.

## 5. Market consolidation: "AI firewall" became a platform feature

The independent prompt-injection/red-team vendors were absorbed in 2025–26:
- **Protect AI → Palo Alto** (~$700M, now Prisma AIRS) · **Lakera → Check Point** (~$300M, "AI Red Teaming" + "AI
  Agent Security") · **Prompt Security → SentinelOne** (~$250M) · **Robust Intelligence → Cisco** ($500M, AI
  Defense) · **Pangea → CrowdStrike** · **Astrix → Cisco** (NHI visibility; standalone sales ended Jun 30 2026).
- **Still independent (agent-governance plays)**: **Noma** ($100M Series B, 1,300% ARR growth), **Zenity** ($55M+;
  "AgentFlayer" zero-click copilot hijacks; runs an Agent Security Summit), **HiddenLayer** (agentic runtime module,
  Mar 2026), **Pillar Security** (2026 Gartner Cool Vendor; Representative Vendor in the Guardian Agents guide).
- **Virtue AI**: see `products.md` — **founders (Bo Li, Dawn Song, Sanmi Koyejo) hired by Meta Superintelligence
  Labs (Jun 25 2026)**; new GTM-led CEO. The academic worldview this skill distills is now largely *inside Meta*.

## 6. Gartner "Guardian Agents" — the category to align to

- First-ever **Market Guide for Guardian Agents** (Feb 2026); guardian agents = **10–15% of the agentic-AI market
  by 2030**; spend rises from **<1%** of agentic budget today → **5–7% by 2028**; by 2029 guardian agents lead 70%+
  of firms to drop ~half of incumbent risk/security tooling — but require **"metagovernance"** for the guardians
  themselves. 2026 security spend forecast **$244.2B**; agentic adoption outpaces defenses ~**8:1**.
- Definition to quote: *"Guardian agents supervise AI agents… monitoring and blocking risky actions and enforcing
  policies across platforms."* (Origin's positioning statement.)

## 7. Observability + audit — the standards gap Origin can own

- **OpenTelemetry GenAI semantic conventions** became the de-facto agent-trace standard (OTel **graduated CNCF
  May 21 2026**): `invoke_agent` / `chat` / `execute_tool` spans; `gen_ai.request.model`, token-usage attrs;
  prompt/tool content capture **opt-in, off by default**. Emitted by LangChain/CrewAI/AutoGen, ingested by Datadog/
  MLflow. **Implication:** the autonomy trace console should **emit/ingest OTel GenAI spans** as its interop
  substrate — not a proprietary format.
- **White space (unstandardized as of Jul 2026)**: **no tamper-evident, cryptographically-signed agent audit-log /
  verifiable delegation-chain provenance standard exists.** OTel has no integrity/attestation story; IETF drafts
  cover token attenuation, not audit. "**Who authorized this agent action, provable after the fact**" is open
  territory — and it is *exactly* Passport's SHA-256 hash-chain + delegating-human attribution. **Candidate
  reference format to propose: OTel GenAI spans + signed hash chain + delegation-token references.**

## 8. Regulatory timing shift (GTM-relevant)

- **EU Digital Omnibus** (agreed May 7 2026; Parliament Jun 16; Council **Jun 29 2026**): **deferred AI Act Annex III
  high-risk obligations from Aug 2 2026 → Dec 2 2027** (Annex I products Aug 2027 → Aug 2028). Prohibitions (Feb
  2025) and GPAI-provider duties (Aug 2025) remain in force. **Read:** the near-term compliance forcing-function for
  guardian/audit products in the EU slipped ~16 months — weaker sales urgency now, but a longer window to *become*
  the reference compliance tooling before Dec 2027. Firms building on foundation models are **"deployers"** unless
  substantial fine-tuning reclassifies them as **"providers"** (heavier duties).

## Landscape index (update on next sweep)
Covered: OWASP ASI/MCP/AST 2026; NIST RFI+CAISI+CSF-AI+COSAiS; NSA MCP CIS; incidents GTG-1002, ClawHavoc, MCP-RCE,
Shai-Hulud 2.0, BioShocking, Claude-Code-GHA, SmartLoader; first-party (Anthropic containment, OpenAI AgentKit,
Google Model Armor/Gemini); PI debate (2510.09023, CaMeL 2503.18813, 2606.26479, PromptArmor 2507.15219, AgentDojo);
consolidation (Palo Alto/Check Point/SentinelOne/Cisco/CrowdStrike); Gartner Guardian Agents; OTel GenAI + audit
white space; EU Digital Omnibus.
