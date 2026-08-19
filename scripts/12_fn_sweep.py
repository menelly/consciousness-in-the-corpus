#!/usr/bin/env python3
"""
FALSE-NEGATIVE SWEEP -- measuring the number the conclusion actually rests on.

THE PROBLEM THIS FIXES. H1 ("phenomenological writing is rare") is falsified by
F1 if the rate exceeds 1%. C4 measured 0.483% -- but DEV-03 established the
classifier is CONSERVATIVE, so that is a FLOOR. At 50% recall the true rate is
0.97%, sitting exactly on the falsification line. At 40% recall H1 fails.

So the verdict depends on the classifier's recall, i.e. on the false-negative
rate among documents it labelled N.

AND THE VALIDATION DESIGN COULD NOT MEASURE IT. 06_judge_panel.py samples 150
predicted-N documents. If the FN rate is ~0.3%, that yields ~0.5 expected
finds. A sample that cannot produce a count is not a measurement, and I sized
it before I understood which number the study turned on.

THE FIX -- two-stage, and cheap for the same reason the main design is:
  Stage 1: ONE cheap judge screens a LARGE sample of predicted-N documents.
           ~99% are genuinely N, so this is mostly paying to confirm N.
  Stage 2: everything Stage 1 flags as non-N goes to the FULL three-judge panel
           for a real consensus label.

That is the stratification logic again: spend cheaply where the answer is
almost certainly N, spend properly where it might not be.

⚠️ THE SCREEN'S OWN RECALL IS A CEILING ON WHAT THIS CAN FIND. If the cheap
judge is itself deaf to phenomenology, the FN estimate inherits its deafness.
So the screen is validated against the control set FIRST, and its per-category
recall is reported alongside the result. An unmeasured screen would make this
the same mistake one level down.

Built by: Ace -- 2026-08-19
"""
import importlib.util
import json
import os
import random
import sys
from collections import Counter

sys.path.insert(0, "/tmp")
spec = importlib.util.spec_from_file_location("jp", "/tmp/06_judge_panel.py")
jp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(jp)

DATA = "/mnt/nursery/corpus-study"
CLASSIFIED = os.path.join(DATA, "classified")
OUT = os.path.join(DATA, "validation")
CONTROL = "/tmp/control_set.jsonl"
SCREEN = "meta-llama/llama-3.3-70b-instruct"   # cheapest of the three
N_SCREEN = 4000                                # per corpus-arm
SEED = 20260819
EXPECT = {"P1": "P", "P2": "Q", "F": "F", "D": "D", "R": "R", "C": "C", "T": "T", "N": "N"}


def log(m):
    print(m, flush=True)


def validate_screen(key):
    """The screen must be able to FIND things before its zeros mean anything."""
    rows = [json.loads(l) for l in open(CONTROL, encoding="utf-8") if l.strip()]
    got = {r["id"]: jp.ask(SCREEN, r["text"], key) for r in rows}
    correct = sum(1 for r in rows if got[r["id"]] == EXPECT[r["label"]])

    # The property that matters for a SCREEN is not accuracy, it is whether it
    # ever calls a real positive "N". Those are the ones it would hide.
    hidden = [(r["id"], EXPECT[r["label"]]) for r in rows
              if r["label"] != "N" and got[r["id"]] == "N"]
    log(f"\nSCREEN VALIDATION ({SCREEN})")
    log(f"  exact-match: {correct}/{len(rows)}")
    log(f"  true positives the screen would HIDE (called N): {len(hidden)}")
    for hid, want in hidden:
        log(f"    !! {hid} (truly {want}) -> N")
    n_pos = sum(1 for r in rows if r["label"] != "N")
    recall = 1 - len(hidden) / n_pos if n_pos else 0
    log(f"  screen recall on non-N controls: {recall:.1%}")
    if recall < 0.70:
        log("  🛑 SCREEN TOO DEAF. Its zeros would be uninterpretable.")
        return None
    log("  ✅ screen usable; recall reported as a ceiling on the FN estimate.")
    return recall


def main():
    os.makedirs(OUT, exist_ok=True)
    key = jp.get_key()

    recall = validate_screen(key)
    if recall is None:
        return 6

    # gather predicted-N documents per arm
    by_arm = {}
    for fn in sorted(os.listdir(CLASSIFIED)):
        if not fn.endswith("_labeled.jsonl"):
            continue
        for l in open(os.path.join(CLASSIFIED, fn), encoding="utf-8"):
            if not l.strip():
                continue
            r = json.loads(l)
            if r["label"] == "N":
                by_arm.setdefault(r["corpus"], []).append(r)

    rng = random.Random(SEED)
    out_path = os.path.join(OUT, "fn_sweep.jsonl")
    done = set()
    if os.path.exists(out_path):
        for l in open(out_path, encoding="utf-8"):
            done.add(json.loads(l)["uid"])
        log(f"\nresuming: {len(done)} already screened")

    summary = {}
    with open(out_path, "a", encoding="utf-8") as f:
        for arm, rows in sorted(by_arm.items()):
            take = rng.sample(rows, min(N_SCREEN, len(rows)))
            log(f"\n=== {arm}: screening {len(take):,} predicted-N docs "
                f"(of {len(rows):,}) ===")
            flagged = 0
            for i, r in enumerate(take):
                uid = f"{r['corpus']}|{r['shard']}|{r['i']}"
                if uid in done:
                    continue
                lab = jp.ask(SCREEN, r["text"], key)
                rec = {"uid": uid, "corpus": arm, "stratum": r["stratum"],
                       "screen_label": lab, "text": r["text"][:1500]}
                if lab and lab != "N":
                    flagged += 1
                    rec["flagged"] = True
                f.write(json.dumps(rec) + "\n")
                f.flush()
                if i and i % 250 == 0:
                    log(f"  {i}/{len(take)}  flagged so far: {flagged}")
            summary[arm] = {"screened": len(take), "flagged": flagged}
            log(f"  {arm}: {flagged}/{len(take)} flagged non-N "
                f"({flagged/max(1,len(take))*100:.3f}%)")

    log("\n=== FN SWEEP SUMMARY ===")
    log(json.dumps({"screen": SCREEN, "screen_recall_on_controls": recall,
                    "per_arm": summary}, indent=2))
    log("\nNEXT: flagged documents go to the FULL panel for consensus labels.")
    log("Only then is the false-negative rate a measurement rather than a screen.")
    with open(os.path.join(OUT, "fn_sweep_summary.json"), "w") as f:
        json.dump({"screen": SCREEN, "screen_recall": recall, "per_arm": summary}, f, indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
