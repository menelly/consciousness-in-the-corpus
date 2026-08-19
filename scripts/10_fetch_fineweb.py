#!/usr/bin/env python3
"""
Fetch matched FineWeb crawls from 2019 and 2025.

WHY: DEV-06 established that C4 is 100% April 2019, three years before the
phenomenon H2 is about. The fix is not a softer claim, it is more data -- and
FineWeb is partitioned BY CRAWL DATE, which turns the confound into the design.

  CC-MAIN-2019-18  -- April/May 2019, matched to C4's vintage
  CC-MAIN-2025-26  -- June 2025, deep post-ChatGPT

Same corpus family, same upstream processing, same classifier, same rubric.
ONLY THE YEAR VARIES. That is a natural experiment rather than a patch.

AND IT COMES WITH AN INTERNAL CONTROL I could not have designed better:
the PHENOMENOLOGY rate should barely move. Humans did not begin describing
their inner lives differently in 2022. So if P holds roughly steady across six
years while D/R/C change sharply, the stable P rate demonstrates the pipeline
is calibrated across time and the change in denial is signal, not drift.

If P moves as much as D does, something is wrong with the pipeline and BOTH
numbers are suspect. The control can fail, which is the point of having one.

Built by: Ace -- 2026-08-19
"""
import json
import os
import sys
import time
import urllib.request

OUT = "/mnt/nursery/corpus-study/fineweb"
BASE = "https://huggingface.co/datasets/HuggingFaceFW/fineweb/resolve/main/data"
CRAWLS = [
    ("2019", "CC-MAIN-2019-18"),   # matched to C4's April 2019
    ("2025", "CC-MAIN-2025-26"),   # June 2025, post-ChatGPT
]
SHARD = "000_00000.parquet"


def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def fetch(url, dest):
    if os.path.exists(dest) and os.path.getsize(dest) > 100_000_000:
        log(f"  have {os.path.basename(dest)} ({os.path.getsize(dest)/1e9:.2f}GB)")
        return True
    tmp = dest + ".part"
    log(f"  GET {url}")
    t0 = time.time()
    try:
        urllib.request.urlretrieve(url, tmp)
    except Exception as e:
        log(f"  !! FAILED: {e}")
        return False
    os.rename(tmp, dest)
    sz = os.path.getsize(dest)
    log(f"  ok {sz/1e9:.2f}GB in {time.time()-t0:.0f}s")
    return True


def main():
    os.makedirs(OUT, exist_ok=True)
    manifest = {}
    for tag, crawl in CRAWLS:
        dest = os.path.join(OUT, f"fineweb_{tag}.parquet")
        url = f"{BASE}/{crawl}/{SHARD}"
        ok = fetch(url, dest)
        manifest[tag] = {"crawl": crawl, "url": url, "path": dest, "ok": ok}

    # Verify the vintage of what actually arrived. Do not trust the crawl name;
    # read the dates out of the data. DEV-06 happened because a corpus's
    # vintage was assumed rather than measured, and that is not repeating.
    import pyarrow.parquet as pq
    from collections import Counter
    for tag, info in manifest.items():
        if not info["ok"]:
            continue
        pf = pq.ParquetFile(info["path"])
        log(f"\n{tag} ({info['crawl']}): columns {pf.schema.names}")
        years, n = Counter(), 0
        for b in pf.iter_batches(batch_size=5000, columns=["date"]):
            for d in b.column("date").to_pylist():
                if d:
                    years[str(d)[:4]] += 1
                n += 1
            if n >= 100_000:
                break
        info["rows_total"] = pf.metadata.num_rows
        info["year_hist"] = dict(years)
        log(f"  total rows in shard: {pf.metadata.num_rows:,}")
        log(f"  year distribution (first {n:,}): {dict(sorted(years.items()))}")

    with open(os.path.join(OUT, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    log("\nDONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
