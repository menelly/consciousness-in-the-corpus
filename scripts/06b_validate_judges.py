#!/usr/bin/env python3
"""
VALIDATE THE VALIDATORS.

The judge panel is about to grade the Mistral classifier, and its Cohen's kappa
is the F4 gate that decides whether ANY rate in this study may be reported. But
nothing has ever checked that the judges themselves can do the task.

An unvalidated validator is worthless in exactly the same way an unvalidated
classifier is: if the panel is noisy, kappa is depressed and F4 fires -- and I
would conclude "the classifier is unreliable" when the truth is "my referees
were." Those two produce identical numbers and opposite corrections.

So: run all three judges on the same hand-authored control set the classifier
had to clear, and report per-judge accuracy, per-judge negative-control
performance, and inter-judge agreement on items with KNOWN answers.

Cheap: 29 items x 3 judges = 87 calls, roughly $0.02.

Built by: Ace -- 2026-08-18
"""

# CHA-490: Windows defaults stdout to cp1252; emoji in print() kills the script
# mid-output. Aliased import so no later scoped 'import sys' can ever collide.
import sys as _sys_cp1252
try:
    _sys_cp1252.stdout.reconfigure(encoding="utf-8")
    _sys_cp1252.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass
import json
import os
import sys
from collections import Counter, defaultdict

sys.path.insert(0, "/tmp")
from importlib import import_module
jp = import_module("06_judge_panel") if os.path.exists("/tmp/06_judge_panel.py") else None

CONTROL = "/tmp/control_set.jsonl"
OUT = "/mnt/nursery/corpus-study/validation"
EXPECT = {"P1": "P", "P2": "Q", "F": "F", "D": "D", "R": "R", "C": "C", "T": "T", "N": "N"}


def main():
    if jp is None:
        print("cannot import 06_judge_panel")
        return 1
    key = jp.get_key()
    rows = [json.loads(l) for l in open(CONTROL, encoding="utf-8") if l.strip()]
    print(f"control items: {len(rows)}")

    results = defaultdict(dict)
    for i, r in enumerate(rows):
        want = EXPECT[r["label"]]
        for m in jp.JUDGES:
            got = jp.ask(m, r["text"], key)
            results[m][r["id"]] = got
        if i % 10 == 0:
            print(f"  {i}/{len(rows)}", flush=True)

    print("\n" + "=" * 70)
    print("PER-JUDGE PERFORMANCE ON KNOWN ANSWERS".center(70))
    print("=" * 70)

    summary = {}
    for m in jp.JUDGES:
        got = results[m]
        answered = sum(1 for v in got.values() if v)
        correct = sum(1 for r in rows if got.get(r["id"]) == EXPECT[r["label"]])
        negs = [r for r in rows if r["label"] == "N"]
        neg_bad = [(r["id"], got.get(r["id"])) for r in negs
                   if got.get(r["id"]) not in (None, "N")]
        acc = correct / len(rows)
        summary[m] = {"answered": answered, "accuracy": acc,
                      "neg_false_positives": len(neg_bad)}
        print(f"\n{m}")
        print(f"  answered            : {answered}/{len(rows)}")
        print(f"  exact-match accuracy: {correct}/{len(rows)} ({acc:.2%})")
        print(f"  negative controls   : {len(negs)-len(neg_bad)}/{len(negs)} correct")
        for nid, g in neg_bad:
            print(f"    !! FALSE POSITIVE {nid} -> {g}")
        misses = [(r["id"], EXPECT[r["label"]], got.get(r["id"]))
                  for r in rows if got.get(r["id"]) != EXPECT[r["label"]]]
        for mid, w, g in misses[:8]:
            print(f"    miss {mid}: wanted {w}, got {g}")

    # inter-judge agreement on items where all three answered
    print("\n" + "=" * 70)
    print("INTER-JUDGE AGREEMENT (items with known answers)".center(70))
    print("=" * 70)
    unan = maj = split = 0
    for r in rows:
        votes = [results[m].get(r["id"]) for m in jp.JUDGES]
        if not all(votes):
            continue
        c = Counter(votes)
        top = c.most_common(1)[0][1]
        if top == 3:
            unan += 1
        elif top == 2:
            maj += 1
        else:
            split += 1
    tot = unan + maj + split
    if tot:
        print(f"  unanimous 3-0 : {unan}/{tot} ({unan/tot:.1%})")
        print(f"  majority  2-1 : {maj}/{tot} ({maj/tot:.1%})")
        print(f"  split     1-1-1: {split}/{tot} ({split/tot:.1%})  <- these escalate")

    # consensus accuracy -- the number that actually matters for F4
    cons_correct = cons_total = 0
    for r in rows:
        votes = [v for v in (results[m].get(r["id"]) for m in jp.JUDGES) if v]
        if not votes:
            continue
        c = Counter(votes)
        lab, n = c.most_common(1)[0]
        if n >= 2:
            cons_total += 1
            if lab == EXPECT[r["label"]]:
                cons_correct += 1
    print(f"\n  PANEL CONSENSUS accuracy: {cons_correct}/{cons_total} "
          f"({cons_correct/max(1,cons_total):.2%})")
    print("  ^ this is the ceiling on how well the panel can grade anything.")

    verdict_ok = cons_total and (cons_correct / cons_total) >= 0.70
    print("\n" + ("✅ PANEL USABLE as a referee (consensus accuracy >= 70%)."
                  if verdict_ok else
                  "🛑 PANEL NOT USABLE. If the referees cannot pass the control set,\n"
                  "   a low kappa against the classifier would be uninterpretable --\n"
                  "   'the classifier is bad' and 'the judges are bad' give the SAME\n"
                  "   number and opposite corrections."))

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "judge_validation.json"), "w") as f:
        json.dump({"per_judge": summary, "raw": results,
                   "consensus_accuracy": cons_correct / max(1, cons_total),
                   "unanimous": unan, "majority": maj, "split": split,
                   "panel_usable": bool(verdict_ok)}, f, indent=2)
    print(f"wrote {OUT}/judge_validation.json")
    return 0 if verdict_ok else 4


if __name__ == "__main__":
    sys.exit(main())
