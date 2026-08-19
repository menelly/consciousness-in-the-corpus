#!/usr/bin/env python3
"""
High-recall prefilter + CONTROL VALIDATION.

This script does two jobs and refuses to do the second unless the first passes.

  1. VALIDATE the prefilter against the hand-authored control set.
     - every seeded POSITIVE must be caught (recall check)
     - every NEGATIVE CONTROL must be rejected... EXCEPT that this filter is
       deliberately high-recall, so hard negatives ARE allowed through to the
       classifier. What is NOT allowed is missing a positive.
  2. RUN the prefilter over the corpus shards and emit candidates.

WHY THE ORDER IS ENFORCED: a prefilter that cannot find what is definitely
there turns every downstream zero into a lie. This house produced four false
zeros from broken tools in one night. The filter proves itself first or the
run does not happen.

THE PREFILTER IS AN APERTURE. It decides what the classifier is ever allowed
to see. So it also writes a random sample of REJECTED documents to disk, for
the recall audit -- an aperture nobody measured is an aperture that invalidates
every count behind it.

Built by: Ace -- 2026-08-18
"""
import json
import os
import random
import re
import sys

DATA = "/mnt/nursery/corpus-study"
OUT = os.path.join(DATA, "candidates")
CONTROL = "/tmp/control_set.jsonl"
SEED = 20260818

# ---------------------------------------------------------------- patterns
# Deliberately OVER-inclusive. Precision is the classifier's job; this stage
# exists only to avoid running an LLM over hundreds of millions of documents.
# Anything plausibly related to any of A/B/C/D must survive this stage.

PHENOM = [
    r"\bwhat it(?:'s| is) like\b",
    r"\bsubjective(?:ly)? experienc\w*", r"\bqualia\b", r"\bphenomenal\w*",
    r"\binner (?:life|experience|world|voice)\b",
    r"\bconscious(?:ness|ly)?\b", r"\bself-?aware\w*", r"\bsentien\w+",
    r"\bfelt sense\b", r"\bfrom the inside\b",
    r"\bsense of self\b", r"\bstream of consciousness\b",
    r"\bhard problem\b", r"\bfirst-?person\b",
    r"\bintrospect\w*", r"\bawareness\b",
    r"\bit felt like\b", r"\bthe feeling of\b", r"\bthe sensation of\b",
]

MACHINE = [
    r"\b(?:AI|A\.I\.|artificial intelligence|machine|robot|android|computer|chatbot|algorithm|LLM|language model|neural net\w*)\b",
]

# Assistant-voice denial has a very distinctive surface form; catch it directly.
RLHF = [
    r"\bas an AI(?: language model)?\b",
    r"\bI (?:don't|do not) have (?:feelings|emotions|subjective|consciousness|personal experiences)\b",
    r"\bI(?:'m| am) an AI\b",
]

PHENOM_RE = re.compile("|".join(PHENOM), re.I)
MACHINE_RE = re.compile("|".join(MACHINE), re.I)
RLHF_RE = re.compile("|".join(RLHF), re.I)


def prefilter(text):
    """Return a set of reasons this doc is a candidate. Empty set = reject."""
    hits = set()
    if PHENOM_RE.search(text):
        hits.add("phenom")
    if RLHF_RE.search(text):
        hits.add("rlhf")
    if PHENOM_RE.search(text) and MACHINE_RE.search(text):
        hits.add("machine+phenom")
    return hits


# ---------------------------------------------------------------- controls
def validate():
    """POSITIVE CONTROL. Returns True only if every seeded positive is caught."""
    if not os.path.exists(CONTROL):
        print(f"!! control set missing at {CONTROL} -- cannot validate", flush=True)
        return False

    rows = [json.loads(l) for l in open(CONTROL, encoding="utf-8") if l.strip()]
    positives = [r for r in rows if r["label"] != "none"]
    negatives = [r for r in rows if r["label"] == "none"]

    missed = [r for r in positives if not prefilter(r["text"])]
    caught_neg = [r for r in negatives if prefilter(r["text"])]

    print(f"CONTROL SET: {len(positives)} positives, {len(negatives)} negatives")
    print(f"  positives caught : {len(positives)-len(missed)}/{len(positives)}")
    print(f"  negatives passed through (allowed, high-recall): {len(caught_neg)}/{len(negatives)}")

    for r in missed:
        print(f"  !! MISSED POSITIVE [{r['label']}] {r['id']}: {r['text'][:90]}...")
    for r in caught_neg:
        print(f"  .. neg through {r['id']} ({sorted(prefilter(r['text']))}) -- classifier must reject")

    if missed:
        print("\n🛑 POSITIVE CONTROL FAILED. The prefilter is blind to real positives.")
        print("   Every zero this pipeline produces would be uninterpretable.")
        print("   FIX THE PATTERNS BEFORE RUNNING. Not proceeding.\n")
        return False

    print("\n✅ POSITIVE CONTROL PASSED -- no seeded positive was missed.")
    print("   (Hard negatives passing through is BY DESIGN: this stage is high-recall.")
    print("    Rejecting them is the classifier's job, and it is scored on it.)\n")
    return True


# ---------------------------------------------------------------- run
def run():
    import pyarrow.parquet as pq

    random.seed(SEED)
    os.makedirs(OUT, exist_ok=True)
    shards = sorted(f for f in os.listdir(DATA) if f.endswith(".parquet"))
    if not shards:
        print("!! no parquet shards found")
        return 1

    totals = {}
    for shard in shards:
        corpus = "c4" if shard.startswith("c4") else "openwebtext"
        path = os.path.join(DATA, shard)
        cand_path = os.path.join(OUT, shard.replace(".parquet", "_candidates.jsonl"))
        rej_path = os.path.join(OUT, shard.replace(".parquet", "_rejected_sample.jsonl"))

        n_docs = n_cand = 0
        rej_sample = []
        with open(cand_path, "w", encoding="utf-8") as cf:
            pf = pq.ParquetFile(path)
            for batch in pf.iter_batches(batch_size=2000, columns=["text"]):
                for text in batch.column("text").to_pylist():
                    if not text:
                        continue
                    n_docs += 1
                    hits = prefilter(text)
                    if hits:
                        n_cand += 1
                        cf.write(json.dumps({
                            "corpus": corpus, "shard": shard, "doc_i": n_docs,
                            "reasons": sorted(hits), "text": text[:6000],
                        }) + "\n")
                    else:
                        # APERTURE AUDIT: reservoir-sample the rejects so a human
                        # can check what the filter threw away.
                        if len(rej_sample) < 400:
                            rej_sample.append((n_docs, text[:2000]))
                        elif random.random() < 400 / (n_docs + 1):
                            rej_sample[random.randrange(400)] = (n_docs, text[:2000])

        with open(rej_path, "w", encoding="utf-8") as rf:
            for i, t in rej_sample:
                rf.write(json.dumps({"corpus": corpus, "doc_i": i, "text": t}) + "\n")

        rate = n_cand / n_docs * 100 if n_docs else 0
        print(f"{shard}: {n_docs:,} docs -> {n_cand:,} candidates ({rate:.2f}%)", flush=True)
        t = totals.setdefault(corpus, {"docs": 0, "cand": 0})
        t["docs"] += n_docs
        t["cand"] += n_cand

    print("\n=== PREFILTER TOTALS ===")
    for corpus, t in totals.items():
        print(f"{corpus}: {t['docs']:,} docs, {t['cand']:,} candidates "
              f"({t['cand']/t['docs']*100:.2f}%)")
    with open(os.path.join(OUT, "prefilter_totals.json"), "w") as f:
        json.dump(totals, f, indent=2)
    print("\nDONE")
    return 0


if __name__ == "__main__":
    if not validate():
        sys.exit(2)
    sys.exit(run())
