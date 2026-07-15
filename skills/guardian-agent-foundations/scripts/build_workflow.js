export const meta = {
  name: 'corpus-research-build',
  description: 'Parallel research-to-engineering build over the 432-paper AAAI security corpus: cards, ontology, syntheses, cross-cutting chapters, engineering patterns',
  phases: [
    { title: 'Cards', detail: 'one evidence-anchored research card per paper (batched agents)' },
    { title: 'Ontology', detail: 'normalized ontology + relationship graph from card tags' },
    { title: 'Syntheses', detail: '8 category syntheses' },
    { title: 'CrossCutting', detail: '8 cross-category chapters' },
    { title: 'Patterns', detail: 'engineering control/design playbooks' },
  ],
}

const c = (typeof args === 'string' ? JSON.parse(args) : args) || {} // config paths (tolerate string args)
const VOCAB = [
  'ASSETS: model_weights, training_data, user_data, prompts_context, embeddings, retrieval_corpus, agent_memory,',
  'tool_credentials, execution_environment, model_outputs, safety_policies, evaluation_artifacts, audit_records, ip, identity_authz.',
  'ADVERSARIES: external_attacker, malicious_user, insider, compromised_tool, compromised_data_source, malicious_model_provider,',
  'malicious_app_developer, supply_chain_attacker, coordinating_agents, adaptive_evaluator_aware, physical_world_attacker, model_extractor.',
  'ATTACK_SURFACES: training_pipeline, fine_tuning, preference_optimization, post_training, model_serving, api_boundary, prompt_context,',
  'rag_ingestion, retrieval, embeddings, tool_invocation, agent_to_agent, memory, browser_computer_use, network, identity_authz,',
  'data_storage, logging_telemetry, model_distribution, physical_sensors, human_approval.',
  'ATTACK_CLASSES: prompt_injection, jailbreak, data_poisoning, backdoor, evasion, adversarial_example, model_extraction, model_inversion,',
  'membership_inference, attribute_inference, training_data_reconstruction, privacy_leakage, gradient_leakage, tool_abuse,',
  'privilege_escalation, confused_deputy, cross_agent_deception, reward_hacking, specification_gaming, verifier_gaming,',
  'benchmark_contamination, evaluation_overfitting, deepfake_generation, forgery, network_intrusion, supply_chain_compromise, dos,',
  'side_channel, watermark_removal, fingerprint_evasion, model_theft, unauthorized_adaptation, provenance_manipulation.',
  'DEFENSE_CLASSES: input_filtering, output_filtering, policy_gating, sandboxing, least_privilege, capability_isolation, human_approval,',
  'cryptographic_provenance, authentication, authorization, trusted_execution, differential_privacy, federated_learning,',
  'secure_aggregation, adversarial_training, robust_optimization, certified_robustness, detection, watermarking, fingerprinting,',
  'rate_limiting, query_monitoring, retrieval_isolation, memory_isolation, data_validation, supply_chain_controls, red_teaming,',
  'runtime_monitoring, incident_containment, rollback, evidence_logging.',
].join(' ')

const INTEGRITY = `EVIDENCE INTEGRITY (mandatory): every substantive claim must be traceable to the paper text. NEVER invent titles, authors, dates, venues, datasets, metrics, attack-success rates, or defense effectiveness — if not stated, write "not stated in paper". Distinguish author-claim vs reviewer-synthesis. Use calibrated language ("demonstrated under evaluated conditions", "reduced attack success against the tested threat model", "remains vulnerable to", "not evaluated against") — never "secure/unbreakable/proven safe/guarantees/eliminates". Governing lens: Models propose. Environments verify. Gates decide. Traces prove. Distinguish capability vs permission vs verification vs evidence vs autonomy vs residual-risk.`

const CARDS_SCHEMA = {
  type: 'object', additionalProperties: false, required: ['cards'],
  properties: { cards: { type: 'array', items: {
    type: 'object', additionalProperties: false,
    required: ['paper_id', 'title', 'wrote', 'evidence_strength'],
    properties: {
      paper_id: { type: 'string' }, title: { type: 'string' },
      year: { type: 'string' }, venue: { type: 'string' },
      authors_present: { type: 'boolean' }, external_id: { type: 'string' },
      assets: { type: 'array', items: { type: 'string' } },
      attack_surfaces: { type: 'array', items: { type: 'string' } },
      attack_classes: { type: 'array', items: { type: 'string' } },
      defense_classes: { type: 'array', items: { type: 'string' } },
      threat_phase: { type: 'array', items: { type: 'string' } },
      evidence_strength: { type: 'string', enum: ['Strong', 'Moderate', 'Preliminary', 'Contested', 'Insufficient'] },
      reproducibility: { type: 'string' },
      agent_security_relevance: { type: 'string', enum: ['core', 'adjacent', 'peripheral'] },
      related_ids: { type: 'array', items: { type: 'string' } },
      wrote: { type: 'boolean' },
    },
  } } },
}

function cardPrompt(batch) {
  const list = batch.map((p) =>
    `- paper_id=${p.paper_id} | category=${p.category}\n` +
    `    text_file=${c.txtDir}/${p.paper_id}.txt\n` +
    `    card_out=${c.cardsDir}/${p.category}/${p.paper_id}.md`).join('\n')
  return `You are a senior AI-safety + adversarial-ML + privacy + security research analyst extracting structured, evidence-anchored research cards from AAAI-2026 papers.
${INTEGRITY}
Follow the card template EXACTLY — read it once: ${c.template}
Tag using ONLY these canonical ontology terms: ${VOCAB}

For EACH paper below:
1) Read its text_file (pre-extracted paper text). The canonical title, authors, year, and venue are near the top of the text — use them verbatim (never invent). If text_file is missing/empty, Bash-grep the paper_id in ${c.manifest} to get relative_path, then Read the source PDF under the corpus (pages parameter, in batches).
2) If card_out already exists and is longer than 800 chars, DO NOT rewrite it — set wrote=false and derive the return tags from the existing card. Otherwise: create the parent directory (Bash: mkdir -p) and WRITE a complete card to card_out following every template section.
3) Fill Threat model, Datasets, Metrics, Main findings, Negative results, Limitations (author) AND additional reviewer-identified limitations, Reproducibility, all *implications* sections, Applicability boundaries, Evidence strength (justified by experimental quality / threat-model realism / adaptive testing / reproducibility — NOT paper count), Related papers.
4) Set agent_security_relevance: core (directly about LLM/agent/tool/prompt/MCP security), adjacent (ML security transferable to AI systems), or peripheral (off-topic to agent security, e.g. generic clustering/vision — say so in Applicability boundaries).

Papers in this batch:
${list}

Return one tag object per paper (paper_id, title, year, venue, authors_present, external_id, assets, attack_surfaces, attack_classes, defense_classes, threat_phase, evidence_strength, reproducibility, agent_security_relevance, related_ids, wrote).`
}

const SYN_SECTIONS = '1 Executive summary; 2 Scope/boundaries; 3 Dominant threat models; 4 Major attack families; 5 Major defense families; 6 Most influential concepts; 7 Common datasets/benchmarks; 8 Evaluation metrics; 9 Strongest replicated findings; 10 Conflicting findings; 11 Defense bypasses; 12 Known benchmark limitations; 13 Implementation patterns; 14 Product design implications; 15 Architecture implications; 16 Launch/assurance implications; 17 Open research problems; 18 Recommended foundational papers (by paper_id); 19 Recommended frontier papers (by paper_id); 20 Source map (paper_id -> one-line).'

function synthPrompt(cat, tags) {
  return `You are writing the category synthesis for "${cat}" from the AAAI-2026 security corpus.
${INTEGRITY}
Inputs: research cards live in ${c.cardsDir}/${cat}/ (one .md per paper). Compact per-paper tags for this category (title + attack/defense/evidence/relevance) are below. Use Bash/Grep/Read to open the strongest ~12-18 cards (favor Strong/Moderate evidence and 'core' relevance) for depth; skim the rest via the tags. Do NOT treat paper count as evidence weight — weigh experimental quality, reproducibility, threat-model realism, independent replication, recency.
Write a comprehensive synthesis to ${c.synDir}/${cat}.md with these 20 sections: ${SYN_SECTIONS}
Cite specific paper_ids throughout so claims are traceable. Calibrated language only.

Tags (${tags.length} papers):
${JSON.stringify(tags)}

Create the file, then reply with one line: "wrote ${cat}.md (<n> paper_ids cited)".`
}

const CHAPTERS = [
  { slug: 'ai-llm-safety', name: 'AI and LLM safety', topics: 'jailbreaks & prompt injection; misuse prevention; alignment limitations; agentic risk; tool-mediated side effects; multi-agent deception/coordination failure; reward hacking & verifier gaming; evaluation integrity; rare-harm measurement; runtime safeguards; model-level vs system-level controls' },
  { slug: 'adversarial-ml', name: 'Adversarial machine learning', topics: 'evasion; poisoning; backdoors; transferability; physical-world attacks; adaptive attackers; certified vs empirical robustness; robustness-accuracy tradeoffs; distribution shift' },
  { slug: 'privacy', name: 'Privacy', topics: 'membership inference; model inversion; data reconstruction; differential privacy; federated learning; secure aggregation; leakage via embeddings/retrieval/memory/logs; utility-privacy tradeoffs; composition & repeated-query risks' },
  { slug: 'retrieval-and-matching', name: 'Retrieval and multi-keyword systems', topics: 'search/matching algorithms; secure & privacy-preserving retrieval; access-pattern leakage; ranking integrity; query confidentiality; index poisoning; retrieval authorization; enterprise RAG implications' },
  { slug: 'network-cyber', name: 'Network and cyber security', topics: 'identity & access control; network isolation; zero-trust; supply-chain security; API abuse; credential management; intrusion detection; audit & forensic readiness' },
  { slug: 'model-ip', name: 'Model intellectual-property protection', topics: 'model extraction; weight theft; API imitation; watermarking; fingerprinting; ownership verification; tamper resistance; FP/FN risks; watermark removal & laundering' },
  { slug: 'deepfake-forgery', name: 'Deepfake and forgery detection', topics: 'image/audio/video forgery; detection generalization; generator shift; compression/transformation robustness; provenance systems; content credentials; human factors; detection-vs-authenticity distinction' },
  { slug: 'defense-mitigation', name: 'Defense and mitigation', topics: 'defense-in-depth; adaptive evaluation; composable controls; fail-open vs fail-closed; detection & response; residual risk; control degradation; operational monitoring; incident playbooks' },
]

function crossPrompt(ch) {
  return `You are writing a CROSS-CATEGORY research chapter: "${ch.name}" — insights that emerge only when papers are analyzed together.
${INTEGRITY}
Cover at least: ${ch.topics}.
Sources: category syntheses in ${c.synDir}/ and research cards in ${c.cardsDir}/**. Use Bash/Grep to find the relevant paper_ids across ALL categories (not just one), Read the strongest, and synthesize what is well-established vs emerging vs disputed vs weakly-supported. Highlight defense bypasses, adaptive-attacker results, and where lab results would NOT justify production claims.
Write to ${c.crossDir}/${ch.slug}.md. Cite paper_ids. End with a short "design implications" list tied to: Models propose / Environments verify / Gates decide / Traces prove.
Reply with one line confirming the file + count of paper_ids cited.`
}

const PATTERNS = [
  'policy-and-permission-gates', 'tool-and-capability-isolation', 'sandboxed-execution',
  'human-approval-for-consequential-actions', 'retrieval-authorization', 'prompt-injection-containment',
  'context-and-memory-isolation', 'least-privilege-credentials', 'tamper-evident-traces', 'signed-provenance',
  'model-extraction-defenses', 'privacy-preserving-training', 'privacy-preserving-inference', 'differential-privacy',
  'adversarial-training', 'backdoor-detection', 'input-and-output-detection', 'deepfake-detection',
  'content-provenance', 'watermarking-and-fingerprinting', 'network-segmentation', 'secure-logging',
  'runtime-anomaly-detection', 'adaptive-red-teaming', 'evaluation-holdout-protection', 'incident-containment',
  'safe-rollback', 'kill-switches',
]
const PAT_SECTIONS = 'Problem addressed; Applicable assets & attack surfaces; Threat model; Control mechanism; Preconditions & trust assumptions; System architecture; Recommended implementation pattern; Incorrect/fragile implementation patterns; Verification strategy; Metrics & thresholds; Test cases; Adaptive adversarial tests; Telemetry requirements; Failure handling; Rollback & containment; Known bypasses; Residual risks; Relevant research (paper_ids + local source); Evidence strength; When NOT to use this pattern.'

function patternPrompt(slug) {
  return `You are writing a research-backed ENGINEERING CONTROL / DESIGN PATTERN playbook: "${slug}".
${INTEGRITY}
Ground it in the corpus: use Bash/Grep over ${c.cardsDir}/ and ${c.manifest} to find the specific paper_ids whose evidence supports (or bypasses) this control; Read the strongest. Also cross-link to the existing curated patterns in ${c.ontDir}/architecture-patterns.md (P1..P13) where relevant — reference, don't duplicate.
Write ${c.patDir}/${slug}.md with these sections: ${PAT_SECTIONS}
Every "Known bypasses" and "Residual risks" claim must cite a paper_id or be labelled reviewer-synthesis. Calibrated language only.
Reply with one line confirming the file + count of paper_ids cited.`
}

// ---------------- run ----------------
// papers come compactly via args as ["<paper_id>:<catIndex>", ...] — no index agent.
const CATS_LIST = c.cats
const papers = c.papers.map((s) => { const [pid, ci] = s.split(':'); return { paper_id: pid, category: CATS_LIST[Number(ci)] } })
log(`loaded ${papers.length} papers from args (no index agent)`)
if (papers.length < 400) throw new Error(`args under-populated: ${papers.length}`)

phase('Cards')
const B = c.batchSize || 6
const batches = []
for (let i = 0; i < papers.length; i += B) batches.push(papers.slice(i, i + B))
log(`cards: ${papers.length} papers in ${batches.length} batches of ${B}`)
const cardResults = await parallel(batches.map((b) => () =>
  agent(cardPrompt(b), { agentType: 'general-purpose', schema: CARDS_SCHEMA, phase: 'Cards',
    label: `cards:${b[0].paper_id}..${b[b.length - 1].paper_id}` })))
const tags = cardResults.filter(Boolean).flatMap((r) => (r && r.cards) || [])
log(`cards done: ${tags.length} card tags collected; wrote=${tags.filter((t) => t.wrote).length}`)

// compact tags for downstream
const slim = tags.map((t) => ({ id: t.paper_id, cat: (papers.find((p) => p.paper_id === t.paper_id) || {}).category,
  title: t.title, ac: t.attack_classes, dc: t.defense_classes, as: t.assets,
  ev: t.evidence_strength, rel: t.agent_security_relevance }))

phase('Ontology')
await agent(
  `You are building the normalized research ontology + relationship graph for the corpus.
${INTEGRITY}
Canonical vocabulary (use these exact terms as node ids): ${VOCAB}
Below are per-paper tags (${slim.length} papers). Build a cross-corpus ontology, NOT category silos.
Write FOUR files:
1) ${c.ontDir}/ontology.md — human-readable: the six dimensions (assets, adversaries, attack surfaces, attack classes, defense classes, evidence/assurance mechanisms), each term with a one-line definition and the count of papers touching it.
2) ${c.ontDir}/ontology.json — machine-readable: { assets:[], adversaries:[], attack_surfaces:[], attack_classes:[], defense_classes:[], evidence_mechanisms:[] } with per-term paper_id lists.
3) ${c.ontDir}/corpus/paper-to-ontology-map.jsonl — one line per paper: {paper_id, category, assets, attack_surfaces, attack_classes, defense_classes, evidence_strength, relevance}.
4) ${c.ontDir}/research-relationship-graph.json — { nodes:[{id,type}], edges:[{from,to,type,paper_ids}] } supporting: which attacks target an asset (attack->asset), which defenses mitigate an attack (defense->attack), and defense->evidence_strength, with paper_ids on every edge. Include a top-level "queries" object with 6 example resolved queries (e.g. attacks_targeting: prompt_context, defenses_for: prompt_injection, with paper_id lists).
Tags:
${JSON.stringify(slim)}
Reply with one line listing the 4 files written.`,
  { agentType: 'general-purpose', phase: 'Ontology', label: 'ontology' })

phase('Syntheses')
const CATS = [...new Set(papers.map((p) => p.category))]
await parallel(CATS.map((cat) => () =>
  agent(synthPrompt(cat, slim.filter((s) => s.cat === cat)), { agentType: 'general-purpose', phase: 'Syntheses', label: `synth:${cat}` })))

phase('CrossCutting')
await parallel(CHAPTERS.map((ch) => () =>
  agent(crossPrompt(ch), { agentType: 'general-purpose', phase: 'CrossCutting', label: `cross:${ch.slug}` })))

phase('Patterns')
await parallel(PATTERNS.map((slug) => () =>
  agent(patternPrompt(slug), { agentType: 'general-purpose', phase: 'Patterns', label: `pat:${slug}` })))

return {
  papers: papers.length, card_tags: tags.length, cards_written: tags.filter((t) => t.wrote).length,
  categories: CATS.length, cross_chapters: CHAPTERS.length, patterns: PATTERNS.length,
  relevance: { core: slim.filter((s) => s.rel === 'core').length, adjacent: slim.filter((s) => s.rel === 'adjacent').length, peripheral: slim.filter((s) => s.rel === 'peripheral').length },
}
