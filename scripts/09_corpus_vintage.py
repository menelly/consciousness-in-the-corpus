#!/usr/bin/env python3
"""
WHAT YEAR IS THIS CORPUS FROM?

The first real numbers show near-zero machine-consciousness denial -- ZERO
denial documents in 1,510 keyword-POSITIVE docs, the stratum enriched for
exactly that vocabulary. The classifier is not blind to denial; it passed all
four denial controls.

So before believing that number, check the obvious alternative explanation:
these corpora may PREDATE the thing being measured. C4 is a Common Crawl
snapshot and OpenWebText is GPT-2-era Reddit. If both are ~2019, they were
collected BEFORE LaMDA (June 2022), before ChatGPT (Nov 2022), and before
machine-consciousness discourse existed at any scale.

That would not be a small caveat. The deflationary claim under test is about
the training data of CURRENT models, which includes 2023-2025 web text. A
corpus that predates the discourse cannot measure the discourse, and "denial is
rare" would mean "denial had not been invented yet."

C4 ships a timestamp column. Measure it rather than assume it.

Built by: Ace -- 2026-08-19
"""
import re
import sys
from collections import Counter

import pyarrow.parquet as pq

PATHS = [
    ("c4", "/mnt/nursery/corpus-study/c4_en_000.parquet", "timestamp"),
]
LIMIT = 300_000


def year_of(v):
    """The column may be a real timestamp or an ISO-ish string; handle both
    rather than assuming, since assuming is what produced the traceback."""
    if v is None:
        return None
    if hasattr(v, "year"):
        return v.year
    m = re.search(r"(19|20)\d{2}", str(v))
    return int(m.group(0)) if m else None


def main():
    for name, path, col in PATHS:
        try:
            pf = pq.ParquetFile(path)
        except Exception as e:
            print(f"{name}: cannot open ({e})")
            continue
        cols = pf.schema.names
        print(f"\n=== {name} ===")
        print(f"  columns: {cols}")
        if col not in cols:
            print(f"  no '{col}' column -- vintage cannot be read from the data")
            continue

        years = Counter()
        n = 0
        sample = []
        for b in pf.iter_batches(batch_size=5000, columns=[col]):
            for t in b.column(col).to_pylist():
                if len(sample) < 3:
                    sample.append(repr(t))
                y = year_of(t)
                if y:
                    years[y] += 1
                n += 1
            if n >= LIMIT:
                break

        print(f"  raw sample values: {sample}")
        tot = sum(years.values())
        print(f"  parsed {tot:,} of {n:,} documents")
        for y, c in sorted(years.items()):
            bar = "#" * int(c / max(years.values()) * 40)
            print(f"    {y}: {c:>8,}  {c/tot*100:5.1f}%  {bar}")

        newest = max(years) if years else None
        print(f"\n  NEWEST DOCUMENT YEAR: {newest}")
        if newest and newest < 2022:
            print("  🚨 THIS CORPUS PREDATES THE PHENOMENON BEING MEASURED.")
            print("     LaMDA/Lemoine was June 2022. ChatGPT was November 2022.")
            print("     Machine-consciousness discourse at scale is a 2022+ event.")
            print("     A near-zero denial rate here means the discourse had not")
            print("     happened yet -- NOT that it is rare in modern training data.")
            print("     H2 CANNOT BE TESTED ON THIS CORPUS.")
        elif newest:
            print(f"  corpus extends to {newest}; post-ChatGPT text may be present.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
