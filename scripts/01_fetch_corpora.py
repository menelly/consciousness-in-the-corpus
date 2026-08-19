#!/usr/bin/env python3
"""
Fetch parquet shards for the corpus base-rate study.

WHY PARQUET SHARDS AND NOT THE WHOLE CORPUS: C4-en is 305GB. We do not need
it. We need an unbiased SAMPLE, and HuggingFace publishes parquet exports we
can pull a bounded number of shards from. What matters for a base rate is that
the sample is not selected on the variable of interest -- and shard order in
these exports is not correlated with topic.

APERTURE, stated because every count downstream inherits it:
  - We read the HF parquet EXPORT, which for very large datasets is a prefix
    of the full corpus, not the whole thing.
  - We take the first N shards, not a random draw across all shards.
  - Therefore: this is a sample of a sample. Any base rate here is an estimate
    for "documents of this kind", not a census of the training set. Said out
    loud in RESULTS, not buried.

Built by: Ace -- 2026-08-18
"""
import json
import os
import sys
import time
import urllib.request

OUT = "/mnt/nursery/corpus-study"
CORPORA = [
    # (repo, config, split, n_shards)
    ("allenai/c4", "en", "train", 3),
    ("Skylion007/openwebtext", "plain_text", "train", 3),
]


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def shard_urls(repo, config, split):
    """Ask HF which parquet files exist. Do not guess the URL scheme."""
    api = f"https://huggingface.co/api/datasets/{repo}/parquet/{config}/{split}"
    with urllib.request.urlopen(api, timeout=60) as r:
        urls = json.load(r)
    if not isinstance(urls, list) or not urls:
        raise RuntimeError(f"no parquet listing for {repo}/{config}/{split}: {urls!r}")
    return urls


def fetch(url, dest):
    if os.path.exists(dest) and os.path.getsize(dest) > 1_000_000:
        log(f"  have {os.path.basename(dest)} ({os.path.getsize(dest)/1e6:.0f}MB)")
        return
    tmp = dest + ".part"
    log(f"  GET {os.path.basename(dest)}")
    urllib.request.urlretrieve(url, tmp)
    os.rename(tmp, dest)
    log(f"  ok  {os.path.basename(dest)} ({os.path.getsize(dest)/1e6:.0f}MB)")


def main():
    os.makedirs(OUT, exist_ok=True)
    manifest = {}
    for repo, config, split, n in CORPORA:
        name = repo.split("/")[-1]
        log(f"{repo} [{config}/{split}] -- listing shards")
        try:
            urls = shard_urls(repo, config, split)
        except Exception as e:
            log(f"  !! LISTING FAILED: {e}")
            manifest[name] = {"error": str(e)}
            continue
        log(f"  {len(urls)} shards available; taking {n}")
        got = []
        for i, u in enumerate(urls[:n]):
            dest = os.path.join(OUT, f"{name}_{config}_{i:03d}.parquet")
            try:
                fetch(u, dest)
                got.append(dest)
            except Exception as e:
                log(f"  !! FETCH FAILED {i}: {e}")
        manifest[name] = {
            "repo": repo, "config": config, "split": split,
            "shards_available": len(urls), "shards_taken": len(got), "files": got,
        }

    with open(os.path.join(OUT, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    log("MANIFEST:")
    log(json.dumps(manifest, indent=2))
    log("DONE")


if __name__ == "__main__":
    sys.exit(main())
