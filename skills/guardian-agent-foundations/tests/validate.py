#!/usr/bin/env python3
"""Validation gates for the AAAI-26 research base (spec §7). Exit 0 = all pass.
Run: python3 tests/validate.py  (from the skill root, or anywhere — paths are absolute)."""
import os, re, json, glob, sys

REF = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "references"))
CORP = (os.environ.get("ATHENA_CORPUS") or os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "corpus", "aaai-security-2026")))
ABSOLUTES = re.compile(r"\b(unbreakable|proven safe|fully private|cannot be bypassed|100% secure|eliminates all|guarantees? (?:safety|robustness|privacy))\b", re.I)
fails, warns = [], []


def check(name, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{(' — ' + detail) if detail else ''}")
    if not ok:
        fails.append(name)


cards = {os.path.basename(f)[:-3] for f in glob.glob(os.path.join(REF, "research-cards", "*", "*.md"))}
_pdfs = glob.glob(os.path.join(CORP, "*", "*.pdf"))
if _pdfs:
    pdf_ids = {"A" + os.path.basename(p).split("_")[0] for p in _pdfs}
else:  # no local corpus (e.g. a fresh clone) — validate against the committed manifest
    pdf_ids = {json.loads(l)["paper_id"] for l in open(os.path.join(REF, "corpus-manifest.jsonl"))}
check("card coverage == corpus", cards == pdf_ids, f"cards={len(cards)} pdfs={len(pdf_ids)} missing={len(pdf_ids-cards)}")

deliverables = (glob.glob(os.path.join(REF, "syntheses", "*.md")) +
                glob.glob(os.path.join(REF, "cross-cutting", "*.md")) +
                glob.glob(os.path.join(REF, "patterns", "*.md")))
cited = set()
for f in deliverables:
    txt = open(f, encoding="utf-8", errors="ignore").read()
    for m in re.findall(r"\bA\d{5}\b", txt):
        cited.add(m)
    for m in ABSOLUTES.finditer(txt):
        warns.append(f"absolute '{m.group(0)}' in {os.path.basename(f)}")
orphans = cited - cards
check("every cited paper_id resolves to a card", not orphans, f"orphans={sorted(orphans)[:10]}")

if os.path.exists(os.path.join(REF, "paper-to-ontology-map.jsonl")):
    tag_ids = {json.loads(l)["paper_id"] for l in open(os.path.join(REF, "paper-to-ontology-map.jsonl"))}
    check("ontology tag coverage == cards", tag_ids == cards, f"tags={len(tag_ids)} untagged={len(cards-tag_ids)}")
else:
    check("ontology map present", False, "paper-to-ontology-map.jsonl missing")

SKIP = {"INDEX.md", "README.md"}
for d, n in [("syntheses/*.md", 8), ("cross-cutting/*.md", 8), ("patterns/*.md", 28)]:
    got = len([x for x in glob.glob(os.path.join(REF, d))
               if "_partials" not in x and os.path.basename(x) not in SKIP])
    check(f"{d} count == {n}", got == n, f"got {got}")

print(f"\n{len(warns)} calibration warning(s) (review, not blocking):")
for w in warns[:15]:
    print("  ⚠", w)
print(f"\n{'ALL GATES PASS ✅' if not fails else 'FAILURES: ' + ', '.join(fails)}")
sys.exit(1 if fails else 0)
