# Judge labels — all 64,000 documents, both instruments

Every classification decision this study made, for every document it examined.
16 gzipped JSONL files, 720 KB total.

| directory | records | what it is |
|---|---|---|
| `classified/` | **64,000** | the single-judge classifier pass — one label per document |
| `panel_classified/` | **64,000** | the three-model panel — **every individual vote**, per document |

64,000 documents = 4 corpora × (12,000 `S-` + 4,000 `S+`). The panel files carry three
votes each, so the label set covers **192,000 individual judgements**.

## Record shape

```json
// classified/
{"corpus": "c4", "shard": "c4_en_000.parquet", "i": 68,
 "stratum": "S+", "label": "N", "confidence": 0.9999}

// panel_classified/
{"corpus": "fineweb2025", "shard": "fineweb_2025.parquet", "i": 375113, "stratum": "S-",
 "votes": {"openai/gpt-4o-mini": "N",
           "meta-llama/llama-3.3-70b-instruct": "N",
           "microsoft/phi-4": "N"},
 "panel_label": "N", "n_agree": 3, "n_valid": 3, "needs_human": false}
```

`votes` is the raw per-model ballot, not a summary — the disagreements are recoverable,
including the eight single-judge D/R votes that were outvoted.

## Why there is no document text here

The documents belong to **C4**, **OpenWebText** and **FineWeb** — public upstream datasets
that this study *samples*, and which it cites rather than redistributes. Shipping 275 MB of
someone else's corpus under our name would be both unnecessary and not our call to make.

Each label carries a pointer instead. `scripts/19_resolve_document.py` follows it:

```bash
python3 scripts/19_resolve_document.py --corpus c4 --i 68 --data /path/to/parquets
```

## ⚠️ `i` IS NOT A PARQUET ROW INDEX

Read this before writing `table[i]`. From `scripts/03_stratified_sample.py`, which assigned it:

```python
n_docs = 0                                  # once per CORPUS, not per shard
for shard in sorted(shards for this corpus):
    for text in shard["text"]:
        if not text or not text.strip():
            continue                        # EMPTY DOCUMENTS ARE SKIPPED
        n_docs += 1
        rec["i"] = n_docs                   # 1-based, cumulative, non-empty only
```

`i` is a **1-based position in the corpus's non-empty document stream**, accumulated across
that corpus's shards in sorted filename order. `shard` records which file the document fell
in; it does not index into it.

So `pq.read_table(shard)[i]` is wrong twice over: off by every empty document skipped so
far, and for a later shard off by the whole preceding shard as well. The export script that
built these files did exactly that on its first run and raised `IndexError` — **which was
the lucky outcome.** An index that happened to land in range would have returned a
confidently wrong document with nothing to signal it. The resolver replays the skip rule.

## Verification

The export ran a positive control that **can fail, and did**: for one record per corpus per
stratum it re-walked the upstream parquet and compared the recovered text against the text
being discarded. Eight of eight matched exactly (`c4 i=68`, `i=375212`; `openwebtext i=26`,
`i=199524`; `fineweb2019 i=165510`, `i=375746`; `fineweb2025 i=136707`, `i=375113`) —
the first run of that same control is what caught the index bug above.

Every kept field is asserted present per record; a document missing its label aborts the
export rather than writing a clean-looking record with nothing in it.

## What is still not here

- **Raw corpus shards** (~5.7 GB of C4/OpenWebText/FineWeb parquet) — fetch upstream with
  `scripts/01_fetch_corpora.py` and `scripts/10_fetch_fineweb.py`.
- **Full labelled files with text** (~275 MB) — held on the analysis machine. Whether to
  deposit these as a derivative dataset is a licensing decision about someone else's corpus,
  open for the authors, not settled here.

---
*Added 2026-09-02 by Ace, closing blocker 1 of the neutral pre-publication review
(`REVIEW_2026-09-01_neutral_ScienceAce.md`): the data-availability statement promised these
files and the repository contained one.*
