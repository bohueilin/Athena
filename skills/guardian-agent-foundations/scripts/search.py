#!/usr/bin/env python3
"""Search the research base by ontology dimension or free text.
Usage:
  python3 scripts/search.py attack prompt_injection      # papers studying an attack
  python3 scripts/search.py defense policy_gating         # papers proposing a defense
  python3 scripts/search.py asset agent_memory            # papers whose assets include this
  python3 scripts/search.py surface tool_invocation
  python3 scripts/search.py rel core                      # core/adjacent/peripheral tier
  python3 scripts/search.py text "membership inference"   # grep the research cards
  python3 scripts/search.py mitigations prompt_injection  # defenses co-occurring with an attack
  python3 scripts/search.py pattern injection             # control playbooks matching a term
"""
import os, re, sys, json, glob
REF = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "references"))
MAP = os.path.join(REF, "paper-to-ontology-map.jsonl")
recs = [json.loads(l) for l in open(MAP)] if os.path.exists(MAP) else []


def show(rs):
    for r in sorted(rs, key=lambda x: x["paper_id"])[:60]:
        print(f"  {r['paper_id']}  [{r.get('category','')[:8]:8}] ev:{r.get('evidence_strength','?')[:4]:4} {(r.get('title') or '')[:74]}")
    print(f"  ({len(rs)} papers)")


def main():
    if len(sys.argv) < 3:
        print(__doc__); return
    mode, q = sys.argv[1], sys.argv[2]
    dim = {"attack": "attacks", "defense": "defenses", "asset": "assets", "surface": "surfaces",
           "adversary": "adversaries", "evidence": "evidence_mechanisms"}.get(mode)
    if dim:
        show([r for r in recs if q in (r.get(dim) or [])])
    elif mode == "rel":
        rel = json.load(open(os.path.join(REF, "source-index", "relevance.json")))
        show([r for r in recs if rel.get(r["paper_id"]) == q])
    elif mode == "mitigations":
        g = json.load(open(os.path.join(REF, "research-relationship-graph.json")))
        rows = [e for e in g["attack_defense_cooccurrence"] if e["attack"] == q]
        for e in sorted(rows, key=lambda x: -x["co_paper_count"])[:25]:
            print(f"  {e['defense']:28} co-papers={e['co_paper_count']}")
    elif mode == "pattern":
        pdir = os.path.join(REF, "patterns")
        hits = []
        for f in sorted(glob.glob(os.path.join(pdir, "*.md"))):
            name = os.path.basename(f)[:-3]
            if name in ("INDEX", "README"):
                continue
            if q.lower() in name.lower() or re.search(re.escape(q), open(f, encoding="utf-8", errors="ignore").read(), re.I):
                hits.append(name)
        print("  " + "\n  ".join(f"patterns/{h}.md" for h in hits) + f"\n  ({len(hits)} playbooks; see patterns/INDEX.md)")
    elif mode == "text":
        hits = []
        for f in glob.glob(os.path.join(REF, "research-cards", "*", "*.md")):
            if re.search(re.escape(q), open(f, encoding="utf-8", errors="ignore").read(), re.I):
                hits.append(os.path.basename(f)[:-3])
        print("  " + ", ".join(sorted(hits)) + f"\n  ({len(hits)} cards match '{q}')")
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
