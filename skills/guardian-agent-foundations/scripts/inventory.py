#!/usr/bin/env python3
"""Phase 1 — deterministic corpus inventory + text extraction for the AAAI-Security-2026
corpus. No LLM. Produces the manifest, audit, exceptions log, and per-paper extracted text
that the card-extraction agents read (far cheaper than rendering PDFs).

Idempotent: re-run to refresh. Detects exact dups by content hash and near-dups by title.
"""
import os, re, csv, json, hashlib, subprocess, sys
from collections import defaultdict

CORPUS = (os.environ.get("ATHENA_CORPUS") or os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "corpus", "aaai-security-2026")))
SKILL = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
OUT = os.path.join(SKILL, "references", "corpus")
TXT = os.path.join(OUT, "extracted-text")
os.makedirs(TXT, exist_ok=True)

EXPECTED = {
    "AILLM-Safety": 63, "Adversarial-ML-Attacks": 152, "Privacy-Protection": 73,
    "Multi-keyword-match": 69, "Network-Cyber-Security": 31, "Model-IP-Protection": 22,
    "Deepfake-Forgery-Detection": 13, "Defense-Mitigation": 9,
}
# folder slug -> canonical category label
CAT_LABEL = {
    "AILLM-Safety": "AILLM-Safety", "Adversarial-ML-Attacks": "Adversarial-ML-Attacks",
    "Privacy-Protection": "Privacy-Protection", "Multi-keyword-match": "Multi-keyword-match",
    "Network-Cyber-Security": "Network-Cyber-Security", "Model-IP-Protection": "Model-IP-Protection",
    "Deepfake-Forgery-Detection": "Deepfake-Forgery-Detection", "Defense-Mitigation": "Defense-Mitigation",
}
HEAD, TAIL = 22000, 9000
DOI_RE = re.compile(r"10\.1609/[A-Za-z0-9.\-/]+")
ARXIV_RE = re.compile(r"arXiv:\s*(\d{4}\.\d{4,5})", re.I)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def pdf_pages(path):
    try:
        out = subprocess.run(["pdfinfo", path], capture_output=True, text=True, timeout=60).stdout
        m = re.search(r"^Pages:\s+(\d+)", out, re.M)
        return int(m.group(1)) if m else None
    except Exception:
        return None


def pdf_title_meta(path):
    try:
        out = subprocess.run(["pdfinfo", path], capture_output=True, text=True, timeout=60).stdout
        m = re.search(r"^Title:\s+(.+)$", out, re.M)
        t = m.group(1).strip() if m else ""
        return t if len(t) > 6 and not t.lower().endswith(".dvi") and "untitled" not in t.lower() else ""
    except Exception:
        return ""


def extract_text(path):
    try:
        r = subprocess.run(["pdftotext", "-q", "-enc", "UTF-8", path, "-"],
                           capture_output=True, text=True, timeout=180)
        return r.stdout or ""
    except Exception:
        return ""


def slug_from_name(fn):
    base = re.sub(r"\.pdf$", "", fn)
    base = re.sub(r"^\d+_", "", base)
    return base.replace("-", " ").strip()


def norm_title(t):
    return re.sub(r"[^a-z0-9]+", " ", (t or "").lower()).strip()


def main():
    rows = []
    exceptions = []
    by_cat = defaultdict(int)
    hashes = defaultdict(list)
    titles = {}

    pdfs = []
    for root, _, files in os.walk(CORPUS):
        for fn in files:
            if fn.lower().endswith(".pdf"):
                pdfs.append(os.path.join(root, fn))
    pdfs.sort()
    print(f"found {len(pdfs)} pdf files")

    for i, path in enumerate(pdfs, 1):
        fn = os.path.basename(path)
        cat_slug = os.path.basename(os.path.dirname(path))
        category = CAT_LABEL.get(cat_slug, cat_slug)
        m = re.match(r"^(\d+)_", fn)
        aid = m.group(1) if m else hashlib.md5(fn.encode()).hexdigest()[:8]
        paper_id = f"A{aid}"
        size = os.path.getsize(path)
        chash = sha256(path)
        hashes[chash].append(paper_id)
        pages = pdf_pages(path)
        text = extract_text(path)
        readable = bool(text and len(text.strip()) > 500)
        if not readable:
            exceptions.append((paper_id, category, fn, f"low/empty text extraction ({len(text.strip())} chars)"))
        # title: prefer pdf metadata, else filename slug (never invented)
        meta_title = pdf_title_meta(path)
        title = meta_title or slug_from_name(fn)
        titles[paper_id] = norm_title(title)
        doi = (DOI_RE.search(text).group(0) if DOI_RE.search(text) else "")
        arxiv = (ARXIV_RE.search(text).group(1) if ARXIV_RE.search(text) else "")
        # save truncated text for agents
        if readable:
            body = text if len(text) <= HEAD + TAIL else (text[:HEAD] + "\n\n[...TRUNCATED...]\n\n" + text[-TAIL:])
            with open(os.path.join(TXT, f"{paper_id}.txt"), "w", encoding="utf-8") as f:
                f.write(body)
        rows.append({
            "paper_id": paper_id, "file_name": fn,
            "relative_path": os.path.relpath(path, CORPUS), "category": category,
            "file_type": "pdf", "file_size": size, "content_hash": chash,
            "canonical_title": title, "title_source": "pdf-metadata" if meta_title else "filename",
            "authors": "", "year": "", "venue": "AAAI 2026 (proceedings)",
            "doi": doi, "arxiv_id": arxiv,
            "source_url": f"https://ojs.aaai.org/index.php/AAAI/article/view/{aid}" if m else "",
            "abstract_available": readable, "full_text_available": readable,
            "page_count": pages, "extraction_status": "ok" if readable else "failed",
            "extraction_quality": "good" if len(text.strip()) > 8000 else ("partial" if readable else "none"),
            "duplicate_group": "", "supersedes_or_superseded_by": "",
            "processing_status": "inventoried", "notes": "",
        })
        by_cat[category] += 1
        if i % 50 == 0:
            print(f"  [{i}/{len(pdfs)}] processed")

    # exact-duplicate groups (same content hash)
    for chash, ids in hashes.items():
        if len(ids) > 1:
            for r in rows:
                if r["paper_id"] in ids:
                    r["duplicate_group"] = "EXACT:" + chash[:12]
                    r["notes"] = (r["notes"] + " exact-duplicate-of:" + ",".join(x for x in ids if x != r["paper_id"])).strip()
    # near-duplicate by normalized title
    tnorm = defaultdict(list)
    for pid, nt in titles.items():
        if nt:
            tnorm[nt].append(pid)
    for nt, ids in tnorm.items():
        if len(ids) > 1:
            for r in rows:
                if r["paper_id"] in ids and not r["duplicate_group"]:
                    r["duplicate_group"] = "NEARTITLE"
                    r["notes"] = (r["notes"] + " same-title-as:" + ",".join(x for x in ids if x != r["paper_id"])).strip()

    # write manifest
    with open(os.path.join(OUT, "corpus-manifest.jsonl"), "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    cols = list(rows[0].keys())
    with open(os.path.join(OUT, "corpus-manifest.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)

    # audit
    dup_exact = sum(1 for r in rows if r["duplicate_group"].startswith("EXACT"))
    near = sum(1 for r in rows if r["duplicate_group"] == "NEARTITLE")
    with open(os.path.join(OUT, "corpus-audit.md"), "w", encoding="utf-8") as f:
        f.write("# Corpus Audit — AAAI-Security-2026\n\n")
        f.write(f"- Files discovered: **{len(rows)}**\n- Expected (spec): **432**\n")
        f.write(f"- Reconciliation: {'MATCH' if len(rows)==432 else 'MISMATCH'}\n")
        f.write(f"- Readable (text extracted): {sum(1 for r in rows if r['extraction_status']=='ok')}\n")
        f.write(f"- Unreadable / low-text: {sum(1 for r in rows if r['extraction_status']!='ok')}\n")
        f.write(f"- Exact-duplicate files: {dup_exact}  · Same-title (near-dup) groups flagged: {near}\n\n")
        f.write("## Per-category reconciliation\n\n| Category | Expected | Found | Delta |\n|---|--:|--:|--:|\n")
        for c, exp in EXPECTED.items():
            got = by_cat.get(c, 0)
            f.write(f"| {c} | {exp} | {got} | {got-exp:+d} |\n")
        extra = set(by_cat) - set(EXPECTED)
        for c in extra:
            f.write(f"| {c} (unexpected) | 0 | {by_cat[c]} | {by_cat[c]:+d} |\n")
        f.write(f"| **Total** | **432** | **{len(rows)}** | **{len(rows)-432:+d}** |\n")
        f.write("\n## Extraction-quality distribution\n\n")
        q = defaultdict(int)
        for r in rows:
            q[r["extraction_quality"]] += 1
        for k, v in sorted(q.items()):
            f.write(f"- {k}: {v}\n")
        f.write("\n_Metadata note: authors/year are intentionally left blank in the manifest — they are "
                "extracted per-paper by the card agents from the paper text (traceable), never invented here._\n")

    with open(os.path.join(OUT, "exceptions-and-unreadable-files.md"), "w", encoding="utf-8") as f:
        f.write("# Exceptions & Unreadable Files\n\n")
        if not exceptions:
            f.write("No unreadable files — all discovered PDFs yielded usable text.\n")
        else:
            f.write(f"{len(exceptions)} file(s) need manual attention (still inventoried, card agents will fall back to reading the PDF directly):\n\n")
            for pid, cat, fn, why in exceptions:
                f.write(f"- **{pid}** [{cat}] `{fn}` — {why}\n")

    print(f"\nDONE: {len(rows)} papers, {sum(1 for r in rows if r['extraction_status']=='ok')} readable, "
          f"{len(exceptions)} exceptions, {dup_exact} exact-dups, {near} near-title-dups")
    print(f"manifest + audit + exceptions -> {OUT}")


if __name__ == "__main__":
    main()
