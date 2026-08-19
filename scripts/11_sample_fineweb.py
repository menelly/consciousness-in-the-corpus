#!/usr/bin/env python3
"""
Stratified sampling of the matched 2019 / 2025 FineWeb crawls.

IDENTICAL to 03_stratified_sample.py in every respect that could affect a
comparison: same regex stratifier, same seed, same reservoir algorithm, same
sample sizes. The ONLY thing that differs between the two arms is the year the
web pages were crawled.

That is the whole point. Any difference in the resulting rates is attributable
to the corpus vintage, because nothing else was allowed to vary. If I had
tuned the stratifier or the sample size between arms, the comparison would be
worthless and it would still have produced a number.

Built by: Ace -- 2026-08-19
"""
import json
import os
import random
import re
import sys

FW = "/mnt/nursery/corpus-study/fineweb"
OUT = "/mnt/nursery/corpus-study/samples"
SEED = 20260818          # SAME seed as the C4/OWT run, deliberately
N_POS, N_NEG = 4000, 12000

# Byte-identical to 03_stratified_sample.py. Do not "improve" it here -- the
# two arms must share a stratifier or the weights are not comparable.
PHENOM = [
    r"\bwhat it(?:'s| is) like\b", r"\bsubjective(?:ly)? experienc\w*", r"\bqualia\b",
    r"\bphenomenal\w*", r"\binner (?:life|experience|world|voice)\b",
    r"\bconscious(?:ness|ly)?\b", r"\bself-?aware\w*", r"\bsentien\w+",
    r"\bfelt sense\b", r"\bfrom the inside\b", r"\bsense of self\b",
    r"\bstream of consciousness\b", r"\bhard problem\b", r"\bfirst-?person\b",
    r"\bintrospect\w*", r"\bawareness\b", r"\bit felt like\b",
    r"\bthe feeling of\b", r"\bthe sensation of\b",
]
RLHF = [
    r"\bas an AI(?: language model)?\b",
    r"\bI (?:don't|do not) have (?:feelings|emotions|subjective|consciousness|personal experiences)\b",
    r"\bI(?:'m| am) an AI\b",
]
STRAT_RE = re.compile("|".join(PHENOM + RLHF), re.I)


def log(m):
    print(m, flush=True)


class Reservoir:
    def __init__(self, k, rng):
        self.k, self.rng, self.n, self.buf = k, rng, 0, []

    def offer(self, item):
        self.n += 1
        if len(self.buf) < self.k:
            self.buf.append(item)
        else:
            j = self.rng.randrange(self.n)
            if j < self.k:
                self.buf[j] = item


def main():
    import pyarrow.parquet as pq
    os.makedirs(OUT, exist_ok=True)
    stats = {}

    for tag in ("2019", "2025"):
        path = os.path.join(FW, f"fineweb_{tag}.parquet")
        if not os.path.exists(path):
            log(f"!! missing {path}")
            continue
        corpus = f"fineweb{tag}"
        rng = random.Random(SEED)
        pos, neg = Reservoir(N_POS, rng), Reservoir(N_NEG, rng)
        n_docs = n_pos = n_neg = 0

        log(f"\n=== {corpus} ===")
        pf = pq.ParquetFile(path)
        for batch in pf.iter_batches(batch_size=2000, columns=["text"]):
            for text in batch.column("text").to_pylist():
                if not text or not text.strip():
                    continue
                n_docs += 1
                rec = {"corpus": corpus, "shard": f"fineweb_{tag}.parquet",
                       "i": n_docs, "text": text[:5000]}
                if STRAT_RE.search(text):
                    n_pos += 1
                    rec["stratum"] = "S+"
                    pos.offer(rec)
                else:
                    n_neg += 1
                    rec["stratum"] = "S-"
                    neg.offer(rec)
            if n_docs % 200000 < 2000:
                log(f"  {n_docs:,} docs...")

        assert n_pos + n_neg == n_docs, f"strata do not sum: {n_pos}+{n_neg}!={n_docs}"

        for name, res in (("Spos", pos), ("Sneg", neg)):
            with open(os.path.join(OUT, f"{corpus}_{name}.jsonl"), "w",
                      encoding="utf-8") as f:
                for r in res.buf:
                    f.write(json.dumps(r) + "\n")

        stats[corpus] = {
            "n_docs": n_docs, "N_pos": n_pos, "N_neg": n_neg,
            "frac_pos": n_pos / n_docs,
            "weight_pos": n_pos / n_docs, "weight_neg": n_neg / n_docs,
            "n_sampled_pos": len(pos.buf), "n_sampled_neg": len(neg.buf),
            "seed": SEED,
        }
        log(f"  DOCS {n_docs:,} | S+ {n_pos:,} ({n_pos/n_docs*100:.3f}%) | S- {n_neg:,}")

    p = os.path.join(OUT, "stratum_stats_fineweb.json")
    with open(p, "w") as f:
        json.dump(stats, f, indent=2)
    log("\n=== FINEWEB STRATUM STATS ===")
    log(json.dumps(stats, indent=2))

    # The first cross-year comparison available, before any classification:
    # does the KEYWORD-positive rate itself move between 2019 and 2025? That is
    # a crude but completely independent signal -- it involves no model at all.
    if "fineweb2019" in stats and "fineweb2025" in stats:
        a, b = stats["fineweb2019"]["frac_pos"], stats["fineweb2025"]["frac_pos"]
        log(f"\nKEYWORD-POSITIVE RATE (no model involved):")
        log(f"  2019: {a*100:.3f}%")
        log(f"  2025: {b*100:.3f}%")
        log(f"  ratio 2025/2019: {b/a:.3f}x")
        log("  (crude -- the stratifier matches 'awareness' and 'the feeling of'")
        log("   too, so this is not a consciousness-discourse rate. It is a")
        log("   model-free sanity check on whether ANYTHING moved.)")
    log("DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
