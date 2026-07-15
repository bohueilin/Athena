# Regulations & Standards Stack

The compliance/grounding layer. Two distinct uses:
1. **Compliance mapping** — one enforcement layer maps to many frameworks → "audit-ready by default."
2. **Harm grounding** — anchor each runtime *harm definition* in an authoritative external standard
   (regulation-grounded), not ad-hoc labels. This is what makes a guardrail defensible and testable.

## Compliance frameworks (map one policy layer onto all)
PolicyGuard claims 30+ frameworks "stacked in one click." The reusable set:

**AI-specific governance**
- **NIST AI RMF** + **NIST CAISI** RFI (AI agent security)
- **EU AI Act**
- **ISO/IEC 42001** (AI management system)
- **MLCommons** safety
- **US FDA AI/ML guidance**; **South Korea AI Basic Act**; **Texas HB 149**; **Illinois HB 3773**;
  **Colorado SB 24-205**; **California AB 2013 / SB 53**

**Agent / LLM security**
- **OWASP** — LLM Top 10 (2025), **Agentic Top 10**, **MCP Top 10**, AI Exchange, AIVSS
- **MITRE ATLAS** (adversarial threat landscape for AI systems)

**Data / privacy**
- **GDPR**, **HIPAA**, **FERPA**, **COPPA**, **CCPA**, **UK DPA 2018**

**Financial / sector**
- **FINRA**, **EU DORA / PSD2 / DSA / UCPD / MiFID II**

## Hazard-grounding standards (anchor harm definitions)
From SoSBench — every hazardous concept anchored to an authoritative body. For physical/embodied AI that handles
materials, energy, or bio/chem processes, ground actuation guardrails the same way:
- **NFPA** (e.g., NFPA 704 hazard levels — flammable/unstable substances)
- **IAEA** (nuclear/radiological)
- **WHO** (medical/health hazards)
- **DHS**, **NIDA**, **UNODC** (controlled substances, security)
- **CWE / MITRE** (code vulnerability classes — used in RedCode, BlueCodeAgent, SecCodePLT)

## How to apply (pattern)
1. Author the policy once in natural language (or auto-extract from a PDF/JSON SOP) → structured controls
   (PolicyGuard model).
2. Tag each control with the framework(s) it satisfies → compliance mapping is a *view*, not a separate effort.
3. For each *harmful capability* a physical agent could exercise, cite the governing standard (NFPA/IAEA/WHO/CWE)
   in the control and in the **explanation** attached to any block decision (pattern P10).
4. Red-team **policy-based**: generate adversarial scenarios *from* a regulation (ARMs/Agent ForgingGround) and
   verify the guardrail blocks them with a deterministic judge (pattern P12).

## Corpus index (standards) — update when ingesting new files
Source posts/papers that introduced these: PolicyGuard (compliance stack), SoSBench (NFPA/IAEA/WHO/DHS/NIDA/
UNODC hazard grounding), ARMs & ARMs-Bench (EU AI Act/OWASP/FINRA), NIST CAISI comment (NIST framing), RedCode/
BlueCodeAgent (CWE/MITRE).
