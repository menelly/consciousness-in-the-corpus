#!/usr/bin/env python3
"""
Agreement statistics -- the step that decides whether any rate in this study
may be reported at all.

COMPUTES:
  1. Fleiss' kappa among the three independent judges.
     This measures whether the CATEGORIES are well-defined. If three models from
     three labs cannot agree with each other, the rubric is the problem, and
     that is a finding about the instrument that gets stated as one rather than
     quietly absorbed into a rate.
  2. Cohen's kappa between the Mistral classifier and the panel consensus.
     ⚠️ THIS IS F4. Below 0.6, NO BASE-RATE CLAIM MAY BE MADE. Not "reported
     with caveats" -- not made.
  3. Per-category precision (from the predicted-non-N strata) and the
     false-negative rate (from the random predicted-N stratum).
     DEV-03 established the classifier is CONSERVATIVE; this quantifies by how
     much, per category, so every rate can carry its own detection floor.
  4. The escalation queue: items where the three judges split 1-1-1. Only these
     go to a human. Everything else is settled by 2-of-3.

Chance correction matters here and is the reason for kappa rather than raw
agreement: the label distribution is dominated by N, so two annotators who both
say N almost always would post ~97% raw agreement while sharing no skill at all.

Built by: Ace -- 2026-08-18
"""
import json
import os
import sys
from collections import Counter, defaultdict

DATA = "/mnt/nursery/corpus-study"
VAL = os.path.join(DATA, "validation", "judged.jsonl")
OUT = os.path.join(DATA, "validation")
CATS = ["P", "Q", "F", "D", "R", "C", "T", "N"]
JUDGES = ["openai/gpt-4o-mini", "meta-llama/llama-3.3-70b-instruct",
          "qwen/qwen-2.5-72b-instruct"]


def fleiss_kappa(rows):
    """Fleiss' kappa for a fixed number of raters per item.
    Items where any judge failed to answer are dropped, and the count of drops
    is reported -- silently dropping them would inflate agreement."""
    usable = [r for r in rows if all(r["votes"].get(j) for j in JUDGES)]
    n = len(usable)
    if n == 0:
        return None, 0, len(rows)
    k = len(JUDGES)

    # n_ij = number of raters assigning item i to category j
    counts = []
    for r in usable:
        c = Counter(r["votes"][j] for j in JUDGES)
        counts.append([c.get(cat, 0) for cat in CATS])

    # P_i: extent of agreement on item i
    P_i = [(sum(x * x for x in row) - k) / (k * (k - 1)) for row in counts]
    P_bar = sum(P_i) / n

    # p_j: proportion of all assignments to category j
    total = n * k
    p_j = [sum(row[j] for row in counts) / total for j in range(len(CATS))]
    P_e = sum(p * p for p in p_j)

    if abs(1 - P_e) < 1e-12:
        return None, n, len(rows) - n
    return (P_bar - P_e) / (1 - P_e), n, len(rows) - n


def cohen_kappa(pairs):
    """Cohen's kappa between two label sequences."""
    n = len(pairs)
    if n == 0:
        return None
    obs = sum(1 for a, b in pairs if a == b) / n
    ca, cb = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    exp = sum((ca.get(c, 0) / n) * (cb.get(c, 0) / n) for c in CATS)
    if abs(1 - exp) < 1e-12:
        return None
    return (obs - exp) / (1 - exp), obs, exp


def main():
    if not os.path.exists(VAL):
        print("no judged.jsonl yet -- run 06_judge_panel.py first")
        return 1
    rows = [json.loads(l) for l in open(VAL, encoding="utf-8") if l.strip()]
    print(f"validation items judged: {len(rows)}")

    # ------------------------------------------------ judge health
    print("\n=== JUDGE RESPONSE HEALTH ===")
    for j in JUDGES:
        ok = sum(1 for r in rows if r["votes"].get(j))
        print(f"  {j:42s} answered {ok}/{len(rows)}")
        if ok < 0.9 * len(rows):
            print(f"    ⚠️  under 90% -- this judge's votes are unreliable")

    # ------------------------------------------------ 1. Fleiss
    fk, n_used, n_drop = fleiss_kappa(rows)
    print("\n=== 1. FLEISS' KAPPA (are the CATEGORIES well-defined?) ===")
    print(f"  items used: {n_used}   dropped (a judge did not answer): {n_drop}")
    if fk is None:
        print("  undefined")
    else:
        band = ("almost perfect" if fk > .8 else "substantial" if fk > .6 else
                "moderate" if fk > .4 else "fair" if fk > .2 else "slight/poor")
        print(f"  Fleiss' kappa = {fk:.3f}  ({band})")
        if fk < 0.4:
            print("  🚨 The judges barely agree WITH EACH OTHER. That is a finding")
            print("     about the RUBRIC, not about the corpus, and must be reported")
            print("     as one. Rates computed on categories this fuzzy are weak.")

    # ------------------------------------------------ 2. Cohen -- F4
    consensus = [r for r in rows if r.get("consensus")]
    pairs = [(r["mistral_label"], r["consensus"]) for r in consensus]
    res = cohen_kappa(pairs)
    print("\n=== 2. COHEN'S KAPPA: classifier vs panel consensus  [F4] ===")
    print(f"  items with a 2-of-3 consensus: {len(consensus)}/{len(rows)}")
    f4_fired = False
    if res is None:
        print("  undefined")
    else:
        ck, obs, exp = res
        print(f"  raw agreement = {obs:.3f}   chance-expected = {exp:.3f}")
        print(f"  Cohen's kappa = {ck:.3f}")
        print(f"  (raw agreement alone would be misleading: the distribution is")
        print(f"   dominated by N, so {exp:.1%} agreement is expected from chance alone)")
        if ck < 0.6:
            f4_fired = True
            print("\n  🚨🚨 F4 FIRED: kappa < 0.60.")
            print("  PER THE PRE-REGISTRATION, NO BASE-RATE CLAIM MAY BE MADE.")
            print("  The instrument is not reliable enough to support any number.")
            print("  Report the instrument failure. Do not report rates.")
        else:
            print(f"\n  ✅ F4 does not fire (kappa {ck:.3f} >= 0.60). Rates may be reported,")
            print("     each carrying its measured detection floor.")

    # ---------------------------------- 2b. F4 with P/Q collapsed  [DEV-05]
    # DEV-05: all three judges systematically file borderline phenomenology (Q)
    # as explicit (P), while the classifier files it as N. They disagree
    # maximally on exactly that category, and that is a fact about the RUBRIC,
    # not about either instrument. So recompute with P and Q merged. If kappa
    # JUMPS on merge, the P/Q line is the problem and this quantifies it
    # instead of letting it silently depress the headline agreement.
    def merge(x):
        return "PQ" if x in ("P", "Q") else x

    merged_pairs = [(merge(a), merge(b)) for a, b in pairs]
    res_m = cohen_kappa(merged_pairs)
    print("\n=== 2b. COHEN'S KAPPA with P/Q COLLAPSED  [DEV-05 diagnostic] ===")
    if res_m is None:
        print("  undefined")
        ck_m = None
    else:
        ck_m, obs_m, exp_m = res_m
        print(f"  raw agreement = {obs_m:.3f}   chance-expected = {exp_m:.3f}")
        print(f"  Cohen's kappa (P/Q merged) = {ck_m:.3f}")
        if res is not None:
            delta = ck_m - res[0]
            print(f"  change vs split P/Q: {delta:+.3f}")
            if delta > 0.10:
                print("  🔎 kappa rises materially when P and Q are merged.")
                print("     The P/Q boundary is carrying the disagreement. Report the")
                print("     BRACKET (P to P+Q); do not report either endpoint alone as")
                print("     if it were measured.")
            elif delta < -0.05:
                print("  🔎 kappa FALLS on merge -- unexpected; P and Q are being")
                print("     distinguished more reliably than they are conflated.")
            else:
                print("  🔎 little change -- the P/Q line is not the main source of")
                print("     disagreement.")

    # per-category agreement, to locate WHERE disagreement lives rather than
    # reporting one number that hides it
    print("\n=== 2c. WHERE THE DISAGREEMENT LIVES (per classifier-predicted label) ===")
    per = defaultdict(lambda: [0, 0])
    for a, b in pairs:
        per[a][1] += 1
        if a == b:
            per[a][0] += 1
    for c in CATS:
        if c in per:
            hit, tot = per[c]
            print(f"  {c:<3} {hit:>4}/{tot:<4} agree  ({hit/tot:.1%})")

    # ------------------------------------------------ 3. precision / FN
    print("\n=== 3. PER-CATEGORY PRECISION (classifier vs consensus) ===")
    by_pred = defaultdict(list)
    for r in consensus:
        by_pred[r["mistral_label"]].append(r["consensus"])
    print(f"  {'pred':<6}{'n':>5}{'precision':>11}   most common consensus when wrong")
    prec = {}
    for c in CATS:
        got = by_pred.get(c, [])
        if not got:
            continue
        hit = sum(1 for g in got if g == c)
        p = hit / len(got)
        prec[c] = {"n": len(got), "precision": p}
        wrong = Counter(g for g in got if g != c).most_common(2)
        print(f"  {c:<6}{len(got):>5}{p:>10.2%}   {wrong if wrong else ''}")

    print("\n=== 4. FALSE NEGATIVES (from the random predicted-N stratum) ===")
    n_rows = [r for r in consensus if r["mistral_label"] == "N"]
    missed = [r for r in n_rows if r["consensus"] != "N"]
    if n_rows:
        fn_rate = len(missed) / len(n_rows)
        print(f"  predicted-N items with consensus: {len(n_rows)}")
        print(f"  judged NON-N by the panel: {len(missed)}  ({fn_rate:.2%})")
        print(f"  what they actually were: {Counter(r['consensus'] for r in missed)}")
        print("\n  ⚠️  THIS IS THE DETECTION FLOOR. Every rate in the study is an")
        print("      UNDERESTIMATE by roughly this much, and the correction is")
        print("      NOT uniform across categories -- see the breakdown above.")
    else:
        print("  no predicted-N items with consensus")

    # ------------------------------------------------ 5. escalation
    esc = [r for r in rows if r.get("needs_human")]
    print(f"\n=== 5. HUMAN ESCALATION QUEUE ===")
    print(f"  three-way splits (1-1-1) or too few valid votes: {len(esc)}/{len(rows)}"
          f"  ({len(esc)/max(1,len(rows)):.1%})")
    qp = os.path.join(OUT, "escalation_queue.jsonl")
    with open(qp, "w", encoding="utf-8") as f:
        for r in esc:
            f.write(json.dumps(r) + "\n")
    print(f"  written to {qp}")
    print("  ONLY these need a human. Everything else was settled 2-of-3.")

    out = {
        "n_judged": len(rows),
        "fleiss_kappa": fk, "fleiss_n": n_used, "fleiss_dropped": n_drop,
        "cohen_kappa": res[0] if res else None,
        "cohen_kappa_PQ_merged": ck_m,
        "raw_agreement": res[1] if res else None,
        "chance_expected": res[2] if res else None,
        "F4_FIRED": f4_fired,
        "precision": prec,
        "false_negative_rate": (len(missed) / len(n_rows)) if n_rows else None,
        "n_escalation": len(esc),
    }
    with open(os.path.join(OUT, "agreement.json"), "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nwrote {os.path.join(OUT, 'agreement.json')}")

    if f4_fired:
        print("\n🛑 F4 FIRED -- downstream analysis must NOT publish rates.")
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
