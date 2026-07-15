#!/usr/bin/env python3
"""Download the AAAI security PDFs listed in aaai_list.txt into an organized folder.
Just downloads — no parsing of PDF content. Polite: limited concurrency, retries,
resume (skips files already present), full manifest + failure log."""
import os, re, sys, csv, time, random, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
LIST = os.path.join(HERE, "aaai_list.txt")
OUT = (os.environ.get("ATHENA_CORPUS") or os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "corpus", "aaai-security-2026")))
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
DL_RE = re.compile(r"/AAAI/article/download/(\d+)/(\d+)")
WORKERS = 4
DRY = "--dry" in sys.argv


def slug(s, n=90):
    s = re.sub(r"[^\w\s-]", "", s).strip()
    s = re.sub(r"\s+", "-", s)
    return s[:n].rstrip("-") or "paper"


def parse():
    """-> list of dicts {cat, num, title, aid, gid, url, folder, fname}."""
    items, cat = [], "Uncategorized"
    for line in open(LIST, encoding="utf-8"):
        line = line.rstrip("\n")
        if line.startswith("## "):
            cat = line[3:].strip()
            continue
        m = DL_RE.search(line)
        if not m:
            continue
        aid, gid = m.group(1), m.group(2)
        # title = text between leading "N. " and " PDF URL:"
        t = line
        t = re.sub(r"^\s*\d+\.\s*", "", t)
        t = re.split(r"\s*PDF URL:", t)[0].strip()
        items.append({
            "cat": cat, "title": t, "aid": aid, "gid": gid,
            "url": f"https://ojs.aaai.org/index.php/AAAI/article/download/{aid}/{gid}",
            "folder": slug(cat, 60),
            "fname": f"{aid}_{slug(t)}.pdf",
        })
    return items


def fetch(it):
    dest_dir = os.path.join(OUT, it["folder"])
    os.makedirs(dest_dir, exist_ok=True)
    path = os.path.join(dest_dir, it["fname"])
    if os.path.exists(path) and os.path.getsize(path) > 20_000:
        return ("skip", it, os.path.getsize(path))
    last = ""
    for attempt in range(4):
        try:
            req = urllib.request.Request(it["url"], headers={"User-Agent": UA, "Accept": "application/pdf,*/*"})
            with urllib.request.urlopen(req, timeout=90) as r:
                data = r.read()
            if len(data) < 1000 or data[:4] != b"%PDF":
                last = f"not-a-pdf ({len(data)}B, head={data[:8]!r})"
                raise ValueError(last)
            tmp = path + ".part"
            with open(tmp, "wb") as f:
                f.write(data)
            os.replace(tmp, path)
            return ("ok", it, len(data))
        except Exception as e:  # noqa: BLE001
            last = f"{type(e).__name__}: {e}"
            time.sleep(1.5 * (attempt + 1) + random.random())
    return ("fail", it, last)


def main():
    items = parse()
    # de-dup by article id (a couple of papers appear in >1 category)
    seen, uniq = set(), []
    for it in items:
        if it["aid"] in seen:
            continue
        seen.add(it["aid"])
        uniq.append(it)
    cats = {}
    for it in uniq:
        cats[it["cat"]] = cats.get(it["cat"], 0) + 1
    print(f"Parsed {len(items)} lines -> {len(uniq)} unique papers across {len(cats)} categories")
    for c, n in cats.items():
        print(f"  {n:>4}  {c}")
    if DRY:
        # surface any line that looked like an entry but yielded no URL
        bad = [l.strip()[:70] for l in open(LIST, encoding="utf-8")
               if re.match(r"^\s*\d+\.", l) and not DL_RE.search(l)]
        print(f"\nEntries missing a valid download URL: {len(bad)}")
        for b in bad[:20]:
            print("  !", b)
        return

    os.makedirs(OUT, exist_ok=True)
    ok = skip = fail = 0
    rows, fails = [], []
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = {ex.submit(fetch, it): it for it in uniq}
        done = 0
        for fut in as_completed(futs):
            status, it, info = fut.result()
            done += 1
            if status == "ok":
                ok += 1
            elif status == "skip":
                skip += 1
            else:
                fail += 1
                fails.append(f"{it['aid']}\t{it['url']}\t{info}")
            rows.append([it["cat"], it["aid"], it["gid"], it["title"], it["folder"], it["fname"], status, info])
            if done % 20 == 0 or status == "fail":
                print(f"[{done}/{len(uniq)}] ok={ok} skip={skip} fail={fail}  last={status}:{it['aid']}", flush=True)
            time.sleep(0.15 + random.random() * 0.2)  # polite jitter

    with open(os.path.join(OUT, "manifest.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["category", "article_id", "galley_id", "title", "folder", "filename", "status", "info"])
        w.writerows(rows)
    if fails:
        with open(os.path.join(OUT, "failures.txt"), "w", encoding="utf-8") as f:
            f.write("\n".join(fails) + "\n")
    print(f"\nDONE. downloaded={ok} skipped={skip} failed={fail}  -> {OUT}")
    print(f"manifest.csv written; {'failures.txt written' if fails else 'no failures'}")


if __name__ == "__main__":
    main()
