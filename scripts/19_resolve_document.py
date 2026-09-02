#!/usr/bin/env python3
"""
Resolve a label record back to the document it labels.

The label files in data/labels/ are TEXT-FREE on purpose. The documents belong to
C4, OpenWebText and FineWeb -- public upstream datasets that we cite rather than
redistribute. Each label instead carries a pointer, and this script follows it.

    python3 scripts/19_resolve_document.py --corpus c4 --i 68
    python3 scripts/19_resolve_document.py --corpus fineweb2025 --i 375113 --data /path/to/parquets

--------------------------------------------------------------------------------
THE POINTER IS NOT A PARQUET ROW INDEX. READ THIS BEFORE ASSUMING IT IS.
--------------------------------------------------------------------------------
From scripts/03_stratified_sample.py, which assigned it:

    n_docs = 0                                  # ONCE PER CORPUS, not per shard
    for shard in sorted(shards for this corpus):
        for text in shard["text"]:
            if not text or not text.strip():
                continue                        # EMPTY DOCUMENTS ARE SKIPPED
            n_docs += 1
            rec = {"corpus": ..., "shard": shard, "i": n_docs, ...}

So `i` is a 1-based position in the corpus's NON-EMPTY document stream, accumulated
across that corpus's shards in sorted filename order. `shard` records which file the
document fell in; it does not index into it.

Consequences, both of which have already bitten:
  * pq.read_table(shard)[i] is WRONG. It is off by every empty document skipped so
    far, and for a later shard it is off by the whole preceding shard as well. The
    first version of the export script did exactly this and raised IndexError --
    which is the lucky failure. A silently in-range wrong row would have shipped.
  * Reconstruction requires replaying the skip rule, which is what this script does.

The trade is deliberate: 720 KB of labels that need this resolver, instead of 275 MB
of someone else's corpus text redistributed under our name.

Exit codes:  0 = resolved     1 = not found (i beyond the corpus)     2 = could not look
"""
import argparse
import os
import sys

# how 01_fetch_corpora.py / 10_fetch_fineweb.py name the shards, and how
# 03_stratified_sample.py grouped them into corpora
CORPUS_PREFIX = {
    "c4": ("", "c4_en_"),
    "openwebtext": ("", "openwebtext_plain_text_"),
    "fineweb2019": ("fineweb", "fineweb_2019"),
    "fineweb2025": ("fineweb", "fineweb_2025"),
}


def shards_for(corpus, data_dir):
    subdir, prefix = CORPUS_PREFIX[corpus]
    d = os.path.join(data_dir, subdir) if subdir else data_dir
    if not os.path.isdir(d):
        print("COULD-NOT-LOOK: %s is not a directory" % d, file=sys.stderr)
        print("  Point --data at the directory holding the upstream parquet shards.",
              file=sys.stderr)
        sys.exit(2)
    found = sorted(os.path.join(d, f) for f in os.listdir(d)
                   if f.startswith(prefix) and f.endswith(".parquet"))
    if not found:
        print("COULD-NOT-LOOK: no %s*.parquet under %s" % (prefix, d), file=sys.stderr)
        sys.exit(2)
    return found


def resolve(corpus, want_i, data_dir):
    """Replay the sampler's own walk and return (text, shard) at stream position want_i."""
    try:
        import pyarrow.parquet as pq
    except ImportError:
        print("COULD-NOT-LOOK: pyarrow not installed (pip install pyarrow)",
              file=sys.stderr)
        sys.exit(2)

    n = 0
    for path in shards_for(corpus, data_dir):
        pf = pq.ParquetFile(path)
        for batch in pf.iter_batches(batch_size=2000, columns=["text"]):
            for text in batch.column("text").to_pylist():
                if not text or not text.strip():
                    continue          # the skip that makes i != row index
                n += 1
                if n == want_i:
                    return text, os.path.basename(path)
    return None, None


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--corpus", required=True, choices=sorted(CORPUS_PREFIX))
    ap.add_argument("--i", required=True, type=int,
                    help="the 'i' field from a label record (1-based, non-empty stream)")
    ap.add_argument("--data", default=os.environ.get("CORPUS_DATA", "."),
                    help="directory holding the upstream parquet shards "
                         "(default: $CORPUS_DATA or cwd)")
    ap.add_argument("--chars", type=int, default=0,
                    help="print only the first N characters (0 = all)")
    args = ap.parse_args()

    if args.i < 1:
        print("i is 1-based; %d is not a valid position" % args.i, file=sys.stderr)
        sys.exit(1)

    text, shard = resolve(args.corpus, args.i, args.data)
    if text is None:
        print("NOT FOUND: %s has fewer than %d non-empty documents"
              % (args.corpus, args.i), file=sys.stderr)
        sys.exit(1)

    print("# corpus=%s i=%d shard=%s chars=%d" % (args.corpus, args.i, shard, len(text)))
    print(text[:args.chars] if args.chars else text)


if __name__ == "__main__":
    main()
