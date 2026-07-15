#!/usr/bin/env python3
"""Phase 3 — assemble ontology.json, paper-to-ontology-map.jsonl, research-relationship-graph.json
and ontology.md deterministically from the per-chunk ontology-tags/*.jsonl the workflow emitted.
No agent reproduction: reliable counts + a queryable graph."""
import os, re, json, glob
from collections import Counter, defaultdict

REF = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "references"))
DIMS = ["assets", "adversaries", "surfaces", "attacks", "defenses", "evidence_mechanisms"]

# manifest for id -> category/title/arxiv
man = {}
for line in open(os.path.join(REF, "corpus-manifest.jsonl")):
    r = json.loads(line)
    man[r["paper_id"]] = r

tags, bad = {}, []
for fp in sorted(glob.glob(os.path.join(REF, "ontology-tags", "*.jsonl"))):
    for ln, line in enumerate(open(fp), 1):
        line = line.strip()
        if not line:
            continue
        try:
            t = json.loads(line)
            pid = t.get("paper_id")
            if not pid:
                raise ValueError("no paper_id")
            tags[pid] = t
        except Exception as e:  # noqa: BLE001
            bad.append((os.path.basename(fp), ln, str(e)[:60]))

# counts per dimension
counts = {d: Counter() for d in DIMS}
strength = Counter()
for pid, t in tags.items():
    for d in DIMS:
        for tok in t.get(d, []) or []:
            counts[d][tok] += 1
    strength[t.get("evidence_strength", "insufficient")] += 1

# paper-to-ontology map (enriched)
with open(os.path.join(REF, "paper-to-ontology-map.jsonl"), "w") as f:
    for pid in sorted(tags):
        t = tags[pid]
        m = man.get(pid, {})
        rec = {"paper_id": pid, "category": m.get("category"),
               "title": (m.get("canonical_title") or "")[:200], "arxiv_id": m.get("arxiv_id")}
        for d in DIMS:
            rec[d] = t.get(d, []) or []
        rec["threat_model"] = t.get("threat_model", {})
        rec["evidence_strength"] = t.get("evidence_strength", "insufficient")
        rec["related_ids"] = t.get("related_ids", []) or []
        f.write(json.dumps(rec) + "\n")

# ontology.json — vocabulary + frequency
ont = {"generated_from_papers": len(tags), "dimensions": {}, "evidence_strength": dict(strength)}
for d in DIMS:
    ont["dimensions"][d] = dict(counts[d].most_common())
json.dump(ont, open(os.path.join(REF, "ontology.json"), "w"), indent=2)

# relationship graph — nodes + typed edges supporting the required queries
edges = []
EDGE = {"assets": "targets_asset", "adversaries": "faces_adversary", "surfaces": "on_surface",
        "attacks": "studies_attack", "defenses": "proposes_defense", "evidence_mechanisms": "verified_by"}
for pid, t in tags.items():
    for d, pred in EDGE.items():
        for tok in t.get(d, []) or []:
            edges.append({"s": pid, "p": pred, "o": tok})
    for rid in t.get("related_ids", []) or []:
        if rid != pid:
            edges.append({"s": pid, "p": "related_to", "o": rid})
# derived attack<->defense co-occurrence (which defenses are studied alongside which attacks)
ad = Counter()
for pid, t in tags.items():
    for a in set(t.get("attacks", []) or []):
        for de in set(t.get("defenses", []) or []):
            ad[(a, de)] += 1
mitig = [{"attack": a, "defense": de, "co_paper_count": n} for (a, de), n in ad.most_common()]

nodes = [{"id": pid, "type": "paper", "category": man.get(pid, {}).get("category"),
          "evidence_strength": t.get("evidence_strength", "insufficient")} for pid, t in tags.items()]
for d in DIMS:
    for tok, n in counts[d].items():
        nodes.append({"id": f"{d}:{tok}", "type": d[:-1] if d.endswith('s') else d, "paper_count": n})
graph = {"nodes": nodes, "edges": edges,
         "attack_defense_cooccurrence": mitig,
         "queries": {
             "attacks_targeting_asset": "filter edges p=targets_asset by o=<asset> -> papers; then their studies_attack edges",
             "defenses_mitigating_attack": "attack_defense_cooccurrence where attack=<attack>, ranked by co_paper_count",
             "threat_models_for_defense": "paper-to-ontology-map.jsonl -> papers with defense -> their threat_model",
             "evidence_for_defense": "papers with defense -> verified_by edges + evidence_strength",
         }}
json.dump(graph, open(os.path.join(REF, "research-relationship-graph.json"), "w"))

# ontology.md narrative
def table(d):
    rows = counts[d].most_common(18)
    out = "| token | papers |\n|---|--:|\n" + "".join(f"| `{k}` | {v} |\n" for k, v in rows)
    return out

with open(os.path.join(REF, "ontology.md"), "w") as f:
    f.write("# Normalized Research Ontology\n\n")
    f.write(f"Derived from **{len(tags)}** tagged papers (one normalized tag record per paper in "
            "`paper-to-ontology-map.jsonl`). Machine-readable vocab + frequencies in `ontology.json`; "
            "queryable graph in `research-relationship-graph.json`.\n\n")
    f.write("> Frequency = how many papers touch a token. It reflects **corpus coverage, not evidence weight** — "
            "weight is judged in the syntheses by reproducibility, threat-model realism, and replication.\n\n")
    f.write("## Evidence strength distribution\n\n")
    f.write("| strength | papers |\n|---|--:|\n" + "".join(
        f"| {k} | {v} |\n" for k, v in strength.most_common()) + "\n")
    for d in DIMS:
        f.write(f"## Top {d.replace('_', ' ')} (of {len(counts[d])} distinct)\n\n{table(d)}\n")
    f.write("## Relationship-graph queries\n\n"
            "- **Which attacks target an asset?** edges `p=targets_asset, o=<asset>` → papers → their `studies_attack`.\n"
            "- **Which defenses mitigate an attack?** `attack_defense_cooccurrence[attack=<x>]` ranked by `co_paper_count`.\n"
            "- **Under which threat models was a defense tested?** map records with that defense → `threat_model`.\n"
            "- **What evidence supports a defense?** those papers' `verified_by` + `evidence_strength`.\n"
            "- **Which papers relate?** `related_to` edges.\n\n")
    f.write("## Provenance & integrity\n\n"
            f"- Tag lines parsed: **{len(tags)}** / 432. Malformed lines: **{len(bad)}**"
            + ((" — " + "; ".join(f"{b[0]}:{b[1]}" for b in bad[:8])) if bad else " (none)") + ".\n")

print(f"papers_tagged={len(tags)} malformed={len(bad)}")
print("attacks(top):", counts['attacks'].most_common(6))
print("defenses(top):", counts['defenses'].most_common(6))
print("evidence_strength:", dict(strength))
if bad:
    print("BAD LINES:", bad[:10])
