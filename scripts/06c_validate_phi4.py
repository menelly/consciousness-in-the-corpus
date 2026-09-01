#!/usr/bin/env python3
"""
VALIDATE THE FOURTH JUDGE.

06b_validate_judges.py validated gpt-4o-mini, llama-3.3-70b and qwen-2.5-72b on
the 29-item control set (DEV-05). At 03:30 on 2026-08-19 qwen was replaced by
microsoft/phi-4 for the full-corpus panel run (15_panel_classify.py), for cost
and because its control-set misses reportedly ran P->Q, opposite to the other
judges. That claim lives in a script comment. validation/judge_validation.json
has no phi-4 entry. A judge whose labels carry a third of every rate in the
study needs its control-set result ON THE RECORD, not in a comment.

This runs phi-4 alone on the same 29 items with the same rubric and appends the
result to judge_validation.json under a separate key, so the original file's
three-judge record is preserved untouched.

Cost: 29 calls, well under a cent.

Built by: Ace -- 2026-09-01
"""
import sys as _sys_cp1252
try:
    _sys_cp1252.stdout.reconfigure(encoding="utf-8")
    _sys_cp1252.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

import json
import os
import sys
from collections import Counter

sys.path.insert(0, "/tmp")
from importlib import import_module
jp = import_module("06_judge_panel")

CONTROL = "/tmp/control_set.jsonl"
OUT = "/mnt/nursery/corpus-study/validation/judge_validation.json"
JUDGE = "microsoft/phi-4"
EXPECT = {"P1": "P", "P2": "Q", "F": "F", "D": "D", "R": "R", "C": "C", "T": "T", "N": "N"}


def main():
    key = jp.get_key()
    rows = [json.loads(l) for l in open(CONTROL, encoding="utf-8") if l.strip()]
    print(f"control items: {len(rows)}  judge: {JUDGE}")
    got = {}
    for i, r in enumerate(rows):
        got[r["id"]] = jp.ask(JUDGE, r["text"], key)
        print(f"  {r['id']:<10} want {EXPECT[r['label']]}  got {got[r['id']]}", flush=True)

    answered = sum(1 for v in got.values() if v)
    correct = sum(1 for r in rows if got.get(r["id"]) == EXPECT[r["label"]])
    negs = [r for r in rows if r["label"] == "N"]
    neg_bad = [(r["id"], got.get(r["id"])) for r in negs if got.get(r["id"]) not in (None, "N")]
    misses = [(r["id"], EXPECT[r["label"]], got.get(r["id"]))
              for r in rows if got.get(r["id"]) != EXPECT[r["label"]]]
    direction = Counter(f"{w}->{g}" for _, w, g in misses)

    print("\n" + "=" * 60)
    print(JUDGE)
    print(f"  answered            : {answered}/{len(rows)}")
    print(f"  exact-match accuracy: {correct}/{len(rows)} ({correct/len(rows):.2%})")
    print(f"  negative controls   : {len(negs)-len(neg_bad)}/{len(negs)} correct")
    for nid, g in neg_bad:
        print(f"    !! FALSE POSITIVE {nid} -> {g}")
    for mid, w, g in misses:
        print(f"    miss {mid}: wanted {w}, got {g}")
    print(f"  miss directions     : {dict(direction)}")
    print("  (the comment in 15_panel_classify.py claims phi-4's misses run P->Q;")
    print("   the line above is the measurement, and it wins over the comment)")

    rec = {"answered": answered, "accuracy": correct / len(rows),
           "neg_false_positives": len(neg_bad),
           "misses": [{"id": m, "wanted": w, "got": g} for m, w, g in misses],
           "raw": got, "validated_on": "2026-09-01",
           "note": "run separately from the 2026-08-19 three-judge validation; "
                   "phi-4 replaced qwen-2.5-72b for the full-corpus panel"}
    data = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {}
    data.setdefault("per_judge_added_later", {})[JUDGE] = rec
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=1)
    print(f"\nappended to {OUT} under per_judge_added_later")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
