#!/usr/bin/env python3
"""Phase 1 — deterministic corpus inventory for the AAAI security corpus.
Produces corpus-manifest.jsonl/.csv, corpus-audit.md, exceptions-and-unreadable-files.md
under the skill's references/. Uses sha256, pdfinfo (pages), pdftotext (title/arxiv/doi)."""
import os, re, csv, json, hashlib, subprocess, sys
from collections import defaultdict, Counter

CORP = (os.environ.get("ATHENA_CORPUS") or os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "corpus", "aaai-security-2026")))
REF = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "references"))
CARDS = os.path.join(REF, "research-cards")
EXPECTED = {  # AAAI-26 (from the user's spec) + FAR AI (ingested 2026-07-14)
    "AILLM-Safety": 63, "Adversarial-ML-Attacks": 152, "Privacy-Protection": 73,
    "Multi-keyword-match": 69, "Network-Cyber-Security": 31, "Model-IP-Protection": 22,
    "Deepfake-Forgery-Detection": 13, "Defense-Mitigation": 9, "FAR-AI": 15,
}
ARXIV = re.compile(r"arXiv:\s*(\d{4}\.\d{4,5})(v\d+)?", re.I)
DOI = re.compile(r"\b(10\.\d{4,9}/[-._;()/:A-Z0-9]+)\b", re.I)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def pages(path):
    try:
        out = subprocess.run(["pdfinfo", path], capture_output=True, text=True, timeout=30).stdout
        m = re.search(r"^Pages:\s*(\d+)", out, re.M)
        return int(m.group(1)) if m else None
    except Exception:
        return None


def first_text(path, n=2):
    try:
        out = subprocess.run(["pdftotext", "-f", "1", "-l", str(n), path, "-"],
                             capture_output=True, text=True, timeout=45).stdout
        return out
    except Exception:
        return ""


def main():
    rows, exceptions, by_hash = [], [], defaultdict(list)
    cat_counts = Counter()
    pdfs = []  # (category, file_name, path, paper_id, relative_path, venue)
    for cat in sorted(os.listdir(CORP)):
        d = os.path.join(CORP, cat)
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if fn.lower().endswith(".pdf"):
                pid = "A" + fn.split("_")[0]
                pdfs.append((cat, fn, os.path.join(d, fn), pid, f"{cat}/{fn}", "AAAI-26"))
    # Extra source: FAR AI (frontier-lab safety) — flat dir, stable ids FAR01.. by sorted order,
    # single category "FAR-AI". Optional (skipped if the symlink/dir is absent, e.g. a fresh clone).
    FAR = os.path.normpath(os.path.join(os.path.dirname(CORP), "far-ai"))
    if os.path.isdir(FAR):
        far_files = sorted(f for f in os.listdir(FAR) if f.lower().endswith(".pdf"))
        for idx, fn in enumerate(far_files, 1):
            pid = f"FAR{idx:02d}"
            pdfs.append(("FAR-AI", fn, os.path.join(FAR, fn), pid, f"far-ai/{fn}", "FAR AI"))
    print(f"scanning {len(pdfs)} pdfs...")
    for i, (cat, fn, path, pid, rel_path, venue) in enumerate(pdfs):
        rec = {
            "paper_id": pid, "file_name": fn, "relative_path": rel_path,
            "category": cat, "file_type": "pdf",
            "file_size": os.path.getsize(path), "content_hash": None,
            "canonical_title": None, "authors": None, "year": 2026,
            "venue": venue, "doi": None, "arxiv_id": None, "source_url": None,
            "abstract_available": None, "full_text_available": None, "page_count": None,
            "extraction_status": "ok", "extraction_quality": "high",
            "duplicate_group": None, "supersedes_or_superseded_by": None,
            "processing_status": None, "notes": "",
        }
        try:
            rec["content_hash"] = sha256(path)
            rec["page_count"] = pages(path)
            txt = first_text(path)
            rec["full_text_available"] = bool(txt and len(txt) > 200)
            rec["abstract_available"] = "abstract" in txt.lower()
            m = ARXIV.search(txt)
            if m:
                rec["arxiv_id"] = m.group(1)
                rec["source_url"] = f"https://arxiv.org/abs/{m.group(1)}"
            md = DOI.search(txt)
            if md:
                rec["doi"] = md.group(1).rstrip(".")
            # title = first non-empty line block before "Abstract" heuristic
            lines = [l.strip() for l in txt.splitlines() if l.strip()]
            if lines:
                rec["canonical_title"] = " ".join(lines[:2])[:300]
            if not txt or len(txt) < 200:
                rec["extraction_status"] = "low_text"
                rec["extraction_quality"] = "low"
                exceptions.append((pid, cat, fn, "pdftotext returned <200 chars (scanned/figure-heavy?)"))
        except Exception as e:  # noqa: BLE001
            rec["extraction_status"] = "error"
            rec["extraction_quality"] = "failed"
            exceptions.append((pid, cat, fn, f"{type(e).__name__}: {e}"))
        # card coverage — and prefer the card's H1 as the canonical title (authoritative,
        # avoids AAAI first-page boilerplate leaking in from pdftotext).
        card = os.path.join(CARDS, cat, pid + ".md")
        if os.path.exists(card):
            rec["processing_status"] = "card-present"
            try:
                h1 = open(card, encoding="utf-8", errors="ignore").readline().strip()
                mt = re.match(r"#\s*\[?" + re.escape(pid) + r"\]?\s*[:\-]?\s*(.+)", h1)
                if mt:
                    rec["canonical_title"] = mt.group(1).strip()[:200]
            except Exception:
                pass
        else:
            rec["processing_status"] = "card-missing"
        by_hash[rec["content_hash"]].append(pid)
        cat_counts[cat] += 1
        rows.append(rec)
        if (i + 1) % 100 == 0:
            print(f"  {i+1}/{len(pdfs)}")

    # duplicate detection (exact by hash)
    dupes = {h: ids for h, ids in by_hash.items() if h and len(ids) > 1}
    id2row = {r["paper_id"]: r for r in rows}
    for h, ids in dupes.items():
        for pid in ids:
            id2row[pid]["duplicate_group"] = h[:12]
            id2row[pid]["notes"] = (id2row[pid]["notes"] + f" exact-dup-of:{','.join(x for x in ids if x!=pid)}").strip()

    os.makedirs(REF, exist_ok=True)
    with open(os.path.join(REF, "corpus-manifest.jsonl"), "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    with open(os.path.join(REF, "corpus-manifest.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    missing_cards = [r["paper_id"] for r in rows if r["processing_status"] == "card-missing"]
    with open(os.path.join(REF, "corpus-audit.md"), "w") as f:
        f.write("# Corpus Audit — AAAI-26 Security Corpus + FAR AI\n\n")
        f.write(f"Total PDFs discovered: **{len(rows)}** (expected {sum(EXPECTED.values())})\n\n")
        f.write("## Category reconciliation (observed vs expected)\n\n")
        f.write("| Category | Observed | Expected | Delta |\n|---|--:|--:|--:|\n")
        for cat in sorted(EXPECTED):
            obs = cat_counts.get(cat, 0)
            f.write(f"| {cat} | {obs} | {EXPECTED[cat]} | {obs-EXPECTED[cat]:+d} |\n")
        f.write(f"| **Total** | **{sum(cat_counts.values())}** | **{sum(EXPECTED.values())}** | **{sum(cat_counts.values())-sum(EXPECTED.values()):+d}** |\n\n")
        f.write("## Integrity\n\n")
        f.write(f"- Exact-duplicate content hashes: **{len(dupes)}** group(s)")
        f.write((" — " + "; ".join(f"{','.join(v)}" for v in list(dupes.values())[:10])) if dupes else " (none)")
        f.write("\n")
        f.write(f"- Files with low/failed text extraction: **{len(exceptions)}** (see exceptions file)\n")
        f.write(f"- arXiv id resolved: **{sum(1 for r in rows if r['arxiv_id'])}** / {len(rows)}\n")
        f.write(f"- Research cards present: **{len(rows)-len(missing_cards)}** / {len(rows)}"
                f" (missing: {len(missing_cards)})\n")
        if missing_cards:
            f.write("\n### Cards still missing\n\n" + ", ".join(missing_cards) + "\n")
    with open(os.path.join(REF, "exceptions-and-unreadable-files.md"), "w") as f:
        f.write("# Exceptions & Unreadable Files\n\n")
        if not exceptions:
            f.write("No unreadable or low-extraction files. All 432 PDFs yielded usable text.\n")
        else:
            f.write(f"{len(exceptions)} file(s) with extraction issues (still hashed & inventoried; "
                    "cards may rely on figures/OCR):\n\n")
            f.write("| paper_id | category | file | issue |\n|---|---|---|---|\n")
            for pid, cat, fn, msg in exceptions:
                f.write(f"| {pid} | {cat} | {fn[:50]} | {msg} |\n")
    print(f"DONE. manifest={len(rows)} dupes={len(dupes)} exceptions={len(exceptions)} "
          f"cards_present={len(rows)-len(missing_cards)} missing={len(missing_cards)}")


if __name__ == "__main__":
    main()
