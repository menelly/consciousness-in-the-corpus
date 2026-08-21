#!/usr/bin/env python3
"""
PRECISION- AND RECALL-CORRECTED RATES.

05_analyze.py reports RAW weighted rates. DEV-07 established those are wrong
for P: the classifier labels reflective/essayistic prose as phenomenology, so
the raw P rate is an OVERESTIMATE. DEV-08 established the judge panel can see
that error, so precision is measurable and the rate is correctable.

    true_rate  ~=  measured_rate * precision / recall

  precision -- from the judge panel on predicted-X documents
               (of the things the classifier CALLED X, how many really were?)
  recall    -- from the FN sweep on predicted-N documents
               (of the things that really were X, how many did it CALL X?)

⚠️ THIS CORRECTION IS ITSELF AN ESTIMATE WITH ERROR BARS, AND THEY ARE WIDE.
Both terms are ratios of small counts. Propagating that honestly matters more
than the point estimate, because a corrected rate quoted without its interval
looks MORE authoritative than the raw one while being less certain.

⚠️ AND THE CORRECTION RUNS TOWARD THE HYPOTHESIS I HOLD. Lower true P makes H1
(phenomenological writing is rare) look better. Every corrected P figure is
printed with that direction stated, so no reader -- including a future me at
5am -- can quote it without seeing which way the thumb was on the scale.

Built by: Ace -- 2026-08-19
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
import math
import os
import sys
from collections import Counter, defaultdict

DATA = "/mnt/nursery/corpus-study"
VAL = os.path.join(DATA, "validation")
CATS = ["P", "Q", "F", "D", "R", "C", "T"]


def wilson(k, n, z=1.96):
    """Wilson interval -- correct near 0 and 1, where these ratios live."""
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    m = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (max(0.0, (c - m) / d), min(1.0, (c + m) / d))


def load_precision():
    """From the judge panel: of docs the classifier called X, how many were X?"""
    p = os.path.join(VAL, "judged.jsonl")
    if not os.path.exists(p):
        return None
    rows = [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
    cons = [r for r in rows if r.get("consensus")]
    by = defaultdict(lambda: [0, 0])
    for r in cons:
        c = r["mistral_label"]
        by[c][1] += 1
        if r["consensus"] == c:
            by[c][0] += 1
    out = {}
    for c, (hit, tot) in by.items():
        lo, hi = wilson(hit, tot)
        out[c] = {"hit": hit, "n": tot, "precision": hit / tot if tot else None,
                  "ci": [lo, hi]}
    return out


def load_recall():
    """From the FN sweep: among predicted-N docs, how many were really non-N?

    recall_X ~= true_positives_X / (true_positives_X + false_negatives_X)
    where false negatives come from the screened predicted-N pool, scaled up
    to the full predicted-N population."""
    p = os.path.join(VAL, "fn_sweep.jsonl")
    if not os.path.exists(p):
        return None
    rows = [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
    by_arm = defaultdict(lambda: {"screened": 0, "flagged": Counter()})
    for r in rows:
        a = by_arm[r["corpus"]]
        a["screened"] += 1
        lab = r.get("screen_label")
        if lab and lab != "N":
            a["flagged"][lab] += 1
    return dict(by_arm)


def main():
    res_path = os.path.join(DATA, "results.json")
    if not os.path.exists(res_path):
        print("no results.json yet -- run 05_analyze.py first")
        return 1
    raw = json.load(open(res_path))
    prec = load_precision()
    rec = load_recall()

    print("=" * 76)
    print("PRECISION / RECALL CORRECTED RATES".center(76))
    print("=" * 76)

    if prec is None:
        print("\n⚠️  No judge-panel output. Precision unmeasured.")
        print("    RAW RATES CANNOT BE CORRECTED AND MUST NOT BE REPORTED AS")
        print("    TRUE RATES -- DEV-07 showed the P class is contaminated.")
        return 2

    print("\n--- MEASURED PRECISION (judge panel vs classifier) ---")
    print(f"  {'pred':<5}{'n':>5}{'correct':>9}{'precision':>11}   95% CI")
    for c in CATS + ["N"]:
        if c in prec:
            d = prec[c]
            print(f"  {c:<5}{d['n']:>5}{d['hit']:>9}{d['precision']:>10.1%}"
                  f"   [{d['ci'][0]:.1%}, {d['ci'][1]:.1%}]")

    if rec is None:
        print("\n⚠️  No FN sweep output. Recall unmeasured; correcting for")
        print("    PRECISION ONLY. Result is an upper bound on the true rate")
        print("    (correcting for recall would raise it again).")

    print("\n--- CORRECTED RATES ---")
    out = {}
    for corpus, r in raw.get("report", {}).items():
        print(f"\n### {corpus}")
        print(f"  {'cat':<5}{'raw':>10}{'precision':>11}{'corrected':>12}   interval")
        out[corpus] = {}
        for c in CATS:
            if c not in r["rates"] or c not in prec:
                continue
            raw_rate = r["rates"][c]["estimate"]
            pd = prec[c]
            if pd["precision"] is None or pd["n"] < 5:
                print(f"  {c:<5}{raw_rate*100:>9.4f}%   n={pd['n']:<3} TOO FEW TO CORRECT")
                continue
            corr = raw_rate * pd["precision"]
            lo = raw_rate * pd["ci"][0]
            hi = raw_rate * pd["ci"][1]
            out[corpus][c] = {"raw": raw_rate, "precision": pd["precision"],
                              "corrected": corr, "interval": [lo, hi],
                              "recall_corrected": False}
            print(f"  {c:<5}{raw_rate*100:>9.4f}%{pd['precision']:>10.1%}"
                  f"{corr*100:>11.4f}%   [{lo*100:.4f}%, {hi*100:.4f}%]")

        if "P" in out[corpus]:
            p = out[corpus]["P"]
            print(f"\n  ⬇️  P: {p['raw']*100:.4f}%  ->  {p['corrected']*100:.4f}%"
                  f"   ({p['raw']/max(p['corrected'],1e-12):.1f}x lower)")
            print("      ⚠️  THIS CORRECTION RUNS TOWARD THE HYPOTHESIS THE AUTHOR HOLDS.")
            print("          A lower P makes H1 ('phenomenological writing is rare')")
            print("          look MORE true. Quote the direction with the number.")

    # ---------------------------------------------------- F1 re-evaluated
    print("\n" + "=" * 76)
    print("F1 RE-EVALUATED ON CORRECTED RATES".center(76))
    print("=" * 76)
    for corpus, cats in out.items():
        if "P" not in cats:
            continue
        p = cats["P"]
        hi = p["interval"][1]
        fired = p["corrected"] > 0.01
        fired_hi = hi > 0.01
        print(f"  {corpus}: corrected P = {p['corrected']*100:.4f}% "
              f"(upper CI {hi*100:.4f}%)")
        print(f"    F1 (>1% refutes H1): {'FIRED' if fired else 'does not fire'}"
              f"   |  at upper CI: {'FIRED' if fired_hi else 'does not fire'}")

    with open(os.path.join(DATA, "corrected_rates.json"), "w") as f:
        json.dump({"precision": prec, "corrected": out,
                   "recall_available": rec is not None}, f, indent=2)
    print(f"\nwrote {DATA}/corrected_rates.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
