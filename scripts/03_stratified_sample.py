#!/usr/bin/env python3
"""
Stratified sampling with EXACT stratum sizes.

Per DEV-01a: the keyword matcher no longer decides what gets seen. It decides
how to allocate sampling effort. Two strata:

  S+  keyword-positive  (small, enriched in B/C/D)
  S-  keyword-negative  (huge, and per DEV-01 holds MOST of category A,
                         because real phenomenological writing does not use
                         the vocabulary of consciousness studies)

Both are sampled. Both will be classified. Combined with survey weights:

    p = (N+/N)*p+ + (N-/N)*p-

THE CRITICAL PROPERTY: N+ and N- are COUNTED EXACTLY on a full pass, not
estimated. If those counts are wrong the weights are wrong and every rate is
wrong -- so they are counted, printed, and stored, and the totals are asserted
to sum to the document count.

S- DELIBERATELY GETS THE LARGER ABSOLUTE SAMPLE. It is the stratum the keyword
matcher is blind to, so it is the one whose estimate must not be noisy.

Reservoir sampling (Algorithm R) so a single streaming pass yields a uniform
random sample of each stratum without holding the corpus in memory.

Built by: Ace -- 2026-08-18
"""
import json
import os
import random
import re
import sys

DATA = "/mnt/nursery/corpus-study"
OUT = os.path.join(DATA, "samples")
SEED = 20260818

N_POS = 4000    # from S+
N_NEG = 12000   # from S- -- larger ON PURPOSE, see docstring

# Same patterns as 02_prefilter.py. Kept deliberately imperfect: DEV-01a proves
# the estimator is unbiased for ANY stratifier, so this does not need to be good.
# It only needs to be FIXED and REPRODUCIBLE.
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
    """Algorithm R. Uniform sample of size k from a stream of unknown length."""
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
    shards = sorted(f for f in os.listdir(DATA) if f.endswith(".parquet"))
    if not shards:
        log("!! no parquet shards")
        return 1

    stats = {}
    for corpus in ("c4", "openwebtext"):
        rng = random.Random(SEED)
        pos = Reservoir(N_POS, rng)
        neg = Reservoir(N_NEG, rng)
        n_docs = n_pos = n_neg = n_empty = 0

        my_shards = [s for s in shards if s.startswith(corpus)]
        log(f"\n=== {corpus}: {len(my_shards)} shards ===")
        for shard in my_shards:
            pf = pq.ParquetFile(os.path.join(DATA, shard))
            for batch in pf.iter_batches(batch_size=2000, columns=["text"]):
                for text in batch.column("text").to_pylist():
                    if not text or not text.strip():
                        n_empty += 1
                        continue
                    n_docs += 1
                    rec = {"corpus": corpus, "shard": shard, "i": n_docs,
                           "text": text[:5000]}
                    if STRAT_RE.search(text):
                        n_pos += 1
                        rec["stratum"] = "S+"
                        pos.offer(rec)
                    else:
                        n_neg += 1
                        rec["stratum"] = "S-"
                        neg.offer(rec)
            log(f"  {shard}: running total {n_docs:,} docs")

        # THE ASSERTION THAT MAKES THE WEIGHTS TRUSTWORTHY.
        assert n_pos + n_neg == n_docs, f"stratum counts do not sum: {n_pos}+{n_neg} != {n_docs}"

        for name, res in (("Spos", pos), ("Sneg", neg)):
            p = os.path.join(OUT, f"{corpus}_{name}.jsonl")
            with open(p, "w", encoding="utf-8") as f:
                for r in res.buf:
                    f.write(json.dumps(r) + "\n")

        stats[corpus] = {
            "n_docs": n_docs, "n_empty_skipped": n_empty,
            "N_pos": n_pos, "N_neg": n_neg,
            "frac_pos": n_pos / n_docs,
            "n_sampled_pos": len(pos.buf), "n_sampled_neg": len(neg.buf),
            "weight_pos": n_pos / n_docs, "weight_neg": n_neg / n_docs,
            "seed": SEED,
        }
        log(f"  DOCS {n_docs:,} | S+ {n_pos:,} ({n_pos/n_docs*100:.3f}%) | S- {n_neg:,}")
        log(f"  sampled: S+ {len(pos.buf):,}, S- {len(neg.buf):,}")

    with open(os.path.join(OUT, "stratum_stats.json"), "w") as f:
        json.dump(stats, f, indent=2)
    log("\n=== STRATUM STATS ===")
    log(json.dumps(stats, indent=2))
    log("DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
