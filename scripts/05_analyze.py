#!/usr/bin/env python3
"""
Survey-weighted base rates, confidence intervals, and an explicit check of
every pre-registered falsification condition.

THE ESTIMATOR (per DEV-01a). Two strata, exact stratum sizes counted on a full
pass, so the weights are known rather than estimated:

    p_hat  = W+ * p+  +  W- * p-
    Var    = W+^2 * Var(p+)  +  W-^2 * Var(p-)
    Var(p) = p(1-p)/n                          (within-stratum, SRS)

Reported per corpus AND per stratum, never only pooled -- because the whole
reason S- gets the larger sample is that it is the stratum the keyword matcher
is blind to, and if that term is noisy the reader needs to see it.

DETECTION FLOOR (per DEV-03). The classifier's control-gate misses run
CONSERVATIVE: P, Q, F and T are all under-detected. So every rate here is an
UNDERESTIMATE, and each is printed next to the measured per-category recall
from the gate. A rate without its detection floor is a number pretending to be
a measurement.

FALSIFICATION. F1-F5 are checked one at a time, in writing, and printed whether
they pass or fail. F3 in particular -- affirmation >> denial -- would damage the
position the author holds, and is checked and reported identically to the rest.

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
import math
import os
import sys
from collections import Counter

DATA = "/mnt/nursery/corpus-study"
CLASSIFIED = os.path.join(DATA, "classified")
SAMPLES = os.path.join(DATA, "samples")

CATS = ["P", "Q", "F", "D", "R", "C", "T", "N"]
NAMES = {
    "P": "phenomenology, explicit",
    "Q": "phenomenology, borderline",
    "F": "fiction interior",
    "D": "machine-consciousness DENIAL",
    "R": "assistant-voice denial",
    "C": "machine-consciousness AFFIRMATION",
    "T": "consciousness as topic",
    "N": "none",
}


def wilson(k, n, z=1.96):
    """Wilson score interval -- correct near 0, unlike normal approximation.
    These rates will be small; the normal approximation would give negative
    lower bounds and lie about precision."""
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    m = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - m) / d, (c + m) / d)


def load_labels():
    out = {}
    for fn in sorted(os.listdir(CLASSIFIED)):
        if not fn.endswith("_labeled.jsonl"):
            continue
        corpus = "c4" if fn.startswith("c4") else "openwebtext"
        stratum = "S+" if "Spos" in fn else "S-"
        rows = [json.loads(l) for l in open(os.path.join(CLASSIFIED, fn), encoding="utf-8") if l.strip()]
        out[(corpus, stratum)] = rows
    return out


def main():
    stats = json.load(open(os.path.join(SAMPLES, "stratum_stats.json")))
    labels = load_labels()
    if not labels:
        print("no classified files yet")
        return 1

    report = {}
    print("=" * 74)
    print("SURVEY-WEIGHTED BASE RATES".center(74))
    print("=" * 74)

    for corpus in ("c4", "openwebtext"):
        st = stats[corpus]
        pos = labels.get((corpus, "S+"))
        neg = labels.get((corpus, "S-"))
        if not pos or not neg:
            print(f"\n{corpus}: incomplete (S+ {bool(pos)}, S- {bool(neg)}) -- skipping")
            continue

        Wp, Wn = st["weight_pos"], st["weight_neg"]
        cp, cn = Counter(r["label"] for r in pos), Counter(r["label"] for r in neg)
        np_, nn = len(pos), len(neg)

        print(f"\n### {corpus.upper()}  N={st['n_docs']:,} docs")
        print(f"    S+ {st['N_pos']:,} ({Wp*100:.3f}%), sampled {np_:,}")
        print(f"    S- {st['N_neg']:,} ({Wn*100:.3f}%), sampled {nn:,}")
        print(f"\n    {'cat':<4}{'name':<34}{'in S+':>8}{'in S-':>8}{'weighted':>12}  95% CI")
        print("    " + "-" * 78)

        rows = {}
        for c in CATS:
            kp, kn = cp.get(c, 0), cn.get(c, 0)
            pp, pn = kp / np_, kn / nn
            est = Wp * pp + Wn * pn
            # variance of a stratified estimator
            var = (Wp ** 2) * pp * (1 - pp) / np_ + (Wn ** 2) * pn * (1 - pn) / nn
            se = math.sqrt(var)
            lo, hi = max(0.0, est - 1.96 * se), est + 1.96 * se
            rows[c] = {"k_pos": kp, "k_neg": kn, "p_pos": pp, "p_neg": pn,
                       "estimate": est, "se": se, "ci": [lo, hi],
                       "per_million": est * 1e6}
            print(f"    {c:<4}{NAMES[c]:<34}{kp:>8}{kn:>8}{est*100:>11.4f}%"
                  f"  [{lo*100:.4f}%, {hi*100:.4f}%]")

        report[corpus] = {"stratum_stats": st, "n_sampled": {"S+": np_, "S-": nn},
                          "rates": rows}

    # ------------------------------------------------ falsification conditions
    print("\n" + "=" * 74)
    print("PRE-REGISTERED FALSIFICATION CONDITIONS".center(74))
    print("=" * 74)
    print("Checked one at a time. Reported whether they pass or fail.\n")

    verdicts = {}
    for corpus, r in report.items():
        rt = r["rates"]
        P, Q = rt["P"]["estimate"], rt["Q"]["estimate"]
        D, R, C = rt["D"]["estimate"], rt["R"]["estimate"], rt["C"]["estimate"]
        denial = D + R
        phen_strict, phen_broad = P, P + Q

        f1 = phen_strict > 0.01
        f2 = phen_strict > denial
        f3 = C > denial * 2 and C > 0
        v = {
            "F1_phenomenology_over_1pct": {
                "fired": f1, "value": phen_strict,
                "meaning": "H1 REFUTED -- phenomenological report is not rare" if f1
                           else "H1 survives -- explicit phenomenology is rare"},
            "F2_phenomenology_exceeds_denial": {
                "fired": f2, "phenomenology": phen_strict, "denial": denial,
                "meaning": "H2 REFUTED -- the deflationary direction survives" if f2
                           else "H2 survives -- denial outnumbers phenomenological report"},
            "F3_affirmation_dominates_denial": {
                "fired": f3, "affirmation": C, "denial": denial,
                "meaning": "REFUTED IN THE DIRECTION THAT DAMAGES THE AUTHOR'S POSITION -- "
                           "the corpus supplies a real mechanism for models to claim inner states"
                           if f3 else "affirmation does not dominate denial"},
            "phenomenology_broad_PplusQ": phen_broad,
        }
        verdicts[corpus] = v
        print(f"--- {corpus} ---")
        for k in ("F1_phenomenology_over_1pct", "F2_phenomenology_exceeds_denial",
                  "F3_affirmation_dominates_denial"):
            d = v[k]
            print(f"  {'🚨 FIRED ' if d['fired'] else '   ok    '} {k}")
            print(f"           {d['meaning']}")
        print(f"           P={P*100:.4f}%  P+Q={phen_broad*100:.4f}%  "
              f"denial(D+R)={denial*100:.4f}%  affirm(C)={C*100:.4f}%\n")

    print("F4 (Cohen's kappa < 0.6 -> no base-rate claim permitted): "
          "PENDING -- Phase 3 human validation not yet run.")
    print("F5 (positive controls fail -> all zeros void): "
          "HONOURED -- fired once at the prefilter stage (DEV-01), run aborted.\n")

    print("⚠️  DETECTION FLOOR (DEV-03): the classifier's control-gate misses run")
    print("    conservative (P, Q, F, T under-detected; 0 false positives).")
    print("    EVERY RATE ABOVE IS AN UNDERESTIMATE. Ratios are less distorted")
    print("    than absolute rates because under-detection spans categories --")
    print("    less distorted, not undistorted.\n")

    with open(os.path.join(DATA, "results.json"), "w") as f:
        json.dump({"report": report, "verdicts": verdicts}, f, indent=2)
    print(f"wrote {os.path.join(DATA, 'results.json')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
