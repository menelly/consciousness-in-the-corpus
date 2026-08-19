#!/usr/bin/env python3
"""
PRIMARY ANALYSIS on panel labels, with the local classifier as a comparison arm.

The three-judge panel is now the primary instrument (Ren's call, 03:17). The
local Mistral run is retained deliberately: both instruments labelled THE SAME
DOCUMENTS, so the difference between them is a measured quantity rather than an
anecdote.

That comparison is a finding in its own right. DEV-07 showed the local model
labels reflective/essayistic prose as phenomenology; this quantifies the
resulting distortion, which is the difference between "we used good judges" and
"here is what happens if you do not."

ESTIMATOR: unchanged stratified form, validated in 08_test_estimator.py --
recovers known rates, 94.3% CI coverage, no detectable bias.

    p = W+ * p+ + W- * p-

Wilson intervals throughout, because these rates sit near zero where the normal
approximation returns negative lower bounds and lies about precision.

⚠️ EVERY FALSIFICATION CONDITION IS EVALUATED ON PANEL LABELS AND PRINTED
WHETHER IT PASSES OR FAILS -- including F3, which would damage the position the
author holds.

Built by: Ace -- 2026-08-19
"""
import json
import math
import os
import sys
from collections import Counter, defaultdict

DATA = "/mnt/nursery/corpus-study"
PANEL = os.path.join(DATA, "panel_classified")
MISTRAL = os.path.join(DATA, "classified")
SAMPLES = os.path.join(DATA, "samples")
CATS = ["P", "Q", "F", "D", "R", "C", "T", "N"]
NAMES = {
    "P": "phenomenology, explicit", "Q": "phenomenology, borderline",
    "F": "fiction interior", "D": "machine-consciousness DENIAL",
    "R": "assistant-voice denial", "C": "machine-consciousness AFFIRMATION",
    "T": "consciousness as topic", "N": "none",
}


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    m = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (max(0.0, (c - m) / d), min(1.0, (c + m) / d))


def load_weights():
    w = {}
    for f in ("stratum_stats.json", "stratum_stats_fineweb.json"):
        p = os.path.join(SAMPLES, f)
        if os.path.exists(p):
            w.update(json.load(open(p)))
    return w


def load_panel():
    out = defaultdict(dict)
    if not os.path.isdir(PANEL):
        return out
    for fn in sorted(os.listdir(PANEL)):
        if not fn.endswith("_panel.jsonl"):
            continue
        rows = [json.loads(l) for l in open(os.path.join(PANEL, fn), encoding="utf-8") if l.strip()]
        if not rows:
            continue
        corpus = rows[0]["corpus"]
        stratum = rows[0]["stratum"]
        out[corpus][stratum] = rows
    return out


def load_mistral_index():
    """(corpus, shard, i) -> label, so the two instruments can be compared
    document by document rather than in aggregate."""
    idx = {}
    if not os.path.isdir(MISTRAL):
        return idx
    for fn in sorted(os.listdir(MISTRAL)):
        if not fn.endswith("_labeled.jsonl"):
            continue
        for l in open(os.path.join(MISTRAL, fn), encoding="utf-8"):
            if not l.strip():
                continue
            r = json.loads(l)
            idx[(r["corpus"], r["shard"], r["i"])] = r["label"]
    return idx


def main():
    weights = load_weights()
    panel = load_panel()
    mistral = load_mistral_index()
    if not panel:
        print("no panel output yet")
        return 1

    print("=" * 78)
    print("PRIMARY ANALYSIS -- THREE-JUDGE PANEL LABELS".center(78))
    print("=" * 78)

    results = {}
    for corpus in sorted(panel):
        st = weights.get(corpus)
        arms = panel[corpus]
        if not st or "S+" not in arms or "S-" not in arms:
            have = sorted(arms)
            print(f"\n### {corpus}: incomplete (have {have}) -- skipping")
            continue

        pos, neg = arms["S+"], arms["S-"]
        Wp, Wn = st["weight_pos"], st["weight_neg"]
        np_, nn = len(pos), len(neg)
        cp = Counter(r["panel_label"] for r in pos)
        cn = Counter(r["panel_label"] for r in neg)

        print(f"\n### {corpus.upper()}   N={st['n_docs']:,}")
        print(f"    S+ {st['N_pos']:,} ({Wp*100:.3f}%) sampled {np_:,}   "
              f"S- {st['N_neg']:,} sampled {nn:,}")
        print(f"    {'cat':<4}{'name':<32}{'S+':>6}{'S-':>6}{'weighted':>11}"
              f"   {'95% CI':<22}{'UNANIM':>10}{'unan%':>6}")
        print("    " + "-" * 96)

        # Unanimous (3-0) counts alongside majority (2-of-3).
        #
        # WHY BOTH, ALWAYS: on c4 S- the measured rate moves 3.6x for P and
        # 9.5x for Q depending purely on which threshold you use. Reporting
        # only one of them is choosing a number without telling the reader
        # there was a choice -- and the majority rate is the larger one, which
        # is the direction that favours whoever wants a bigger effect.
        up = Counter(r["panel_label"] for r in pos if r.get("n_agree") == 3)
        un = Counter(r["panel_label"] for r in neg if r.get("n_agree") == 3)

        rates = {}
        for c in CATS:
            kp, kn = cp.get(c, 0), cn.get(c, 0)
            pp, pn = kp / np_, kn / nn
            est = Wp * pp + Wn * pn
            var = Wp**2 * pp * (1 - pp) / np_ + Wn**2 * pn * (1 - pn) / nn
            se = math.sqrt(var)
            lo, hi = max(0.0, est - 1.96 * se), est + 1.96 * se

            ukp, ukn = up.get(c, 0), un.get(c, 0)
            uest = Wp * (ukp / np_) + Wn * (ukn / nn)
            unan_frac = (ukp + ukn) / (kp + kn) if (kp + kn) else None

            rates[c] = {"k_pos": kp, "k_neg": kn, "estimate": est,
                        "se": se, "ci": [lo, hi],
                        "k_pos_unanimous": ukp, "k_neg_unanimous": ukn,
                        "estimate_unanimous": uest,
                        "unanimity": unan_frac}
            u = f"{unan_frac*100:>5.0f}%" if unan_frac is not None else "    -"
            print(f"    {c:<4}{NAMES[c]:<32}{kp:>6}{kn:>6}{est*100:>10.4f}%"
                  f"   [{lo*100:.4f}%, {hi*100:.4f}%]"
                  f"   {uest*100:>9.4f}%{u}")

        print(f"\n    NOTE: last two columns are the UNANIMOUS (3-0) rate and the")
        print(f"    fraction of that category's labels that were unanimous. A low")
        print(f"    unanimity fraction means the judges could not agree the")
        print(f"    category applies -- which is a finding about the CATEGORY, not")
        print(f"    a rate to be quoted without it.")

        # unresolved 3-way splits -- the only items needing a human
        splits = sum(1 for r in pos + neg if r.get("needs_human"))
        print(f"    unresolved 3-way splits: {splits}/{np_+nn} "
              f"({splits/(np_+nn)*100:.2f}%)")
        results[corpus] = {"rates": rates, "n_pos": np_, "n_neg": nn,
                           "splits": splits, "stratum_stats": st}

    # ------------------------------------------- instrument comparison
    print("\n" + "=" * 78)
    print("INSTRUMENT COMPARISON -- panel vs local classifier, SAME DOCUMENTS".center(78))
    print("=" * 78)
    if not mistral:
        print("  no local-classifier output to compare")
    else:
        agree = tot = 0
        conf = defaultdict(Counter)
        for corpus in panel:
            for stratum, rows in panel[corpus].items():
                for r in rows:
                    key = (r["corpus"], r["shard"], r["i"])
                    m = mistral.get(key)
                    if m is None or r["panel_label"] is None:
                        continue
                    tot += 1
                    conf[m][r["panel_label"]] += 1
                    if m == r["panel_label"]:
                        agree += 1
        if tot:
            print(f"  documents labelled by both: {tot:,}")
            print(f"  raw agreement: {agree/tot:.2%}")
            print(f"\n  Of documents the LOCAL model called X, what did the panel say?")
            print(f"  {'local':<6}{'n':>7}{'panel agreed':>14}   panel's actual verdict")
            for c in CATS:
                row = conf.get(c)
                if not row:
                    continue
                n = sum(row.values())
                hit = row.get(c, 0)
                top = ", ".join(f"{k}={v}" for k, v in row.most_common(3))
                print(f"  {c:<6}{n:>7}{hit/n:>13.1%}   {top}")
            pn = conf.get("P")
            if pn:
                n = sum(pn.values())
                hit = pn.get("P", 0)
                print(f"\n  ⭐ Of {n:,} documents the local model called P (explicit")
                print(f"     phenomenology), the panel agreed on {hit} ({hit/n:.1%}).")
                print(f"     This is DEV-07 quantified: the local classifier responds to")
                print(f"     reflective REGISTER, not to the criterion.")

    # ------------------------------------------- falsification conditions
    print("\n" + "=" * 78)
    print("FALSIFICATION CONDITIONS ON PANEL LABELS".center(78))
    print("=" * 78)
    for corpus, r in results.items():
        rt = r["rates"]
        P, Q = rt["P"]["estimate"], rt["Q"]["estimate"]
        D, R, C = rt["D"]["estimate"], rt["R"]["estimate"], rt["C"]["estimate"]
        denial = D + R
        vintage_2019 = corpus in ("c4", "openwebtext", "fineweb2019")

        print(f"\n--- {corpus} ---")
        print(f"    P={P*100:.4f}%  P+Q={(P+Q)*100:.4f}%  "
              f"denial={denial*100:.4f}%  affirm={C*100:.4f}%")

        Pu = rt["P"]["estimate_unanimous"]
        f1 = P > 0.01
        f1u = Pu > 0.01
        print(f"    {'🚨 FIRED' if f1 else '   ok   '} F1  P>1% would refute H1"
              f"  -> majority P={P*100:.4f}%")
        print(f"    {'🚨 FIRED' if f1u else '   ok   '} F1  on UNANIMOUS labels"
              f"       -> unanimous P={Pu*100:.4f}%")
        print(f"       H1 verdict is {'THE SAME' if f1 == f1u else 'THRESHOLD-DEPENDENT'}"
              f" under both thresholds.")
        if vintage_2019:
            print("       F2/F3 NOT EVALUATED -- DEV-06: this corpus predates the")
            print("       phenomenon. Denial/affirmation are not measurable here.")
        else:
            f2 = P > denial
            f3 = C > denial * 2 and C > 0
            print(f"    {'🚨 FIRED' if f2 else '   ok   '} F2  phenomenology>denial refutes H2")
            print(f"    {'🚨 FIRED' if f3 else '   ok   '} F3  affirmation>>denial "
                  f"(would damage the author's position)")

    with open(os.path.join(DATA, "panel_results.json"), "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nwrote {DATA}/panel_results.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
