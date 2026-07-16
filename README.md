![Athena](Athena_github.png)

# Athena — the knowledge base

**Athena is the single home for the durable, reusable knowledge I've built** — portable across
machines and across AI agents (Claude, Codex, Cursor, ChatGPT). It ships the *synthesized* knowledge
(Markdown + scripts), **not** the raw source papers.

> One thesis runs through it: **capability is not permission.** *Models propose · environments verify ·
> gates decide · traces prove.*

---

## What's inside

| Skill | What it is | Size |
|---|---|---|
| **`skills/guardian-agent-foundations`** | The flagship: an evidence-anchored decision skill for the **security, safety & privacy of AI agents and systems**. **447 research cards + 9 category syntheses** + 8 cross-cutting chapters + **28 control playbooks** + a normalized ontology & relationship graph, distilled from a 447-paper corpus (432 AAAI-26 security + 15 FAR AI frontier-lab safety) (+ Virtue AI / 1Password briefs / a 2026 field sweep). Every claim traces to a paper id; language is calibrated, never absolute. | ~25 M |
| **`skills/cerebras-hackathon`** | Playbook + hard facts for the Cerebras × Gemma hackathon (model/API gotchas, multi-agent patterns, demo/virality). | small |
| **`skills/hackathon-prep`** | Hard-won lessons for advancing at hackathons / demo days / pitch competitions (naming, architecture depth). | small |

Also included (**this repo is private**): `briefs/` — cross-project strategy + the canonical
**`briefs/Origin_Status.md`** (read-first before any Origin work; syncs to your other machines via this
private repo). Not shipped: the raw source PDFs (`corpus/`, gitignored — large + copyrighted; see
[Corpus](#the-corpus--what-its-for)).

---

## How each agent uses it

The content is plain Markdown + Python — **any** agent can consume it; only the auto-loader differs.

| Agent | How it loads Athena | What to do |
|---|---|---|
| **Claude Code** | `.claude/skills/` symlink → auto-triggers on matching prompts | run `./install.sh` once per machine |
| **Codex CLI / Cursor** | auto-reads an agents pointer at repo root | point it at this repo; it reads [`AGENTS.md`](AGENTS.md) / [`CODEX.md`](CODEX.md) |
| **ChatGPT (web)** | can't read local files | upload `SKILL.md` + syntheses into a Project/Custom GPT, **or** use the GitHub connector on this repo |

---

## Install (per machine)

```bash
git clone <this-repo> ~/hackathons/Athena
cd ~/hackathons/Athena
./install.sh        # symlinks skills/* into ~/.claude/skills/ → available in every project
make validate       # 6 integrity gates (passes with zero local PDFs)
```

`install.sh` is idempotent and reversible (`./install.sh --uninstall` removes the symlinks; nothing is
copied into your Claude config).

---

## Use it

**Claude:** just ask — it auto-triggers. Or `/guardian-agent-foundations`.

**Retrieval scripts** (deterministic, no model needed), from `skills/guardian-agent-foundations/`:
```bash
python3 scripts/search.py attack prompt_injection     # papers on an attack
python3 scripts/search.py pattern injection            # matching control playbooks
python3 scripts/search.py mitigations tool_abuse       # defenses that co-occur with an attack → what to build
python3 scripts/search.py asset agent_memory           # papers touching an asset
```

**Audit a codebase / design** (the recipe is in the skill's `SKILL.md`):
> *Use guardian-agent-foundations to audit `<path>`: enumerate assets/adversaries/surfaces, map
> attacks→controls with the CPVER lens (Capability · Permission · Verification · Evidence · Residual-risk),
> flag uncovered attacks and fail-open gaps, and produce a launch-gate scorecard with evidence tiers,
> paper ids, and residual-risk owners.*

---

## The corpus — what it's for

The `corpus/` dir (gitignored) holds the **raw source PDFs** — AAAI-Security-2026 (432), Virtue AI (20),
FAR AI (15). **You use the synthesized skill day-to-day and never touch the PDFs.** The raw corpus matters
only for (1) **provenance** — each card cites its source PDF path so you can pull the exact paper on a
load-bearing call, and (2) **re-ingestion** — folding in new papers. That's *why* it isn't pushed: the
value is extracted into Markdown; the PDFs are just the receipts (and they're copyrighted + large).

On a fresh clone the corpus is simply absent — the skill and `make validate` work fully without it.
To restore provenance locally: symlink your PDFs in, e.g. `ln -s "<pdf-dir>" corpus/aaai-security-2026`,
or set `ATHENA_CORPUS=<dir>`.

---

## Maintain

- **Add papers / refresh:** the skill's `RESEARCH_UPDATE_LOG.md` documents the incremental procedure;
  `scripts/build_manifest.py` (re)builds the inventory, `scripts/assemble_ontology.py` the ontology.
  Corpus fully ingested as of 2026-07-15 (**447 papers**: 432 AAAI-26 + 15 FAR AI); nothing outstanding.
- **Honesty:** the 28 playbooks are **research-grounded design guidance, not build-ready specs** — see
  `skills/guardian-agent-foundations/references/final-quality-review.md` for the 10-lens review and the
  five open cross-pattern seams.
