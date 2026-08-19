#!/usr/bin/env python3
"""
DO THE JUDGES SHARE THE CLASSIFIER'S BIAS?

DEV-07: the classifier labels reflective/essayistic/sermonic prose as P
(explicit phenomenology). Across 11 hand-read documents, at most 1-2 were
genuinely in scope -- including a Bible study that matched because it LISTS
"conscious" as a synonym, and a mid-life-crisis career article at confidence
1.00.

The judge panel is supposed to measure precision on P. But DEV-05 already found
all three judges pushing Q -> P. If they also over-call P on essayistic prose,
the panel will RATIFY the error rather than detect it, and "precision: fine"
would be the most dangerous possible output.

⚠️ AGREEMENT BETWEEN INSTRUMENTS THAT SHARE A BIAS IS NOT VALIDATION.

So this probe takes documents the classifier called P, that I read and judged
NOT phenomenology, and asks the panel directly. Three outcomes:

  judges say N  -> the panel can see the error; precision measurement is sound
  judges say P  -> the panel shares the bias; the whole validation is
                   circular and precision cannot be measured this way
  judges split  -> the category is genuinely ambiguous and no instrument is
                   going to settle it; report that instead of a rate

The third outcome is a real possibility and is not a failure. "This distinction
cannot be reliably drawn" is a finding.

Built by: Ace -- 2026-08-19
"""
import importlib.util
import json
import os
import sys
from collections import Counter

sys.path.insert(0, "/tmp")
spec = importlib.util.spec_from_file_location("jp", "/tmp/06_judge_panel.py")
jp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(jp)

DATA = "/mnt/nursery/corpus-study"
OUT = os.path.join(DATA, "validation")

# The documents I read, with MY label. Identified by (file, doc index) so the
# full text is pulled from disk rather than retyped.
# ACE'S CALL on each: none of these are "about having experience".
MY_LABEL = "N"
PROBE_SEEDS = [
    # (file, seed used to sample, n) -- reproduce the exact samples I read
    ("c4_Sneg_labeled.jsonl", 7, 6),
    ("c4_Spos_labeled.jsonl", 11, 5),
]


def main():
    import random
    key = jp.get_key()
    probes = []
    for fn, seed, n in PROBE_SEEDS:
        rows = [json.loads(l) for l in
                open(os.path.join(DATA, "classified", fn), encoding="utf-8") if l.strip()]
        P = [r for r in rows if r["label"] == "P"]
        rng = random.Random(seed)
        probes += rng.sample(P, n)

    print(f"probing {len(probes)} documents the classifier called P")
    print(f"my label on all of them: {MY_LABEL} (not about having experience)\n")

    agree_with_me = 0
    agree_with_classifier = 0
    split = 0
    recs = []

    for i, r in enumerate(probes):
        votes = {m: jp.ask(m, r["text"], key) for m in jp.JUDGES}
        good = [v for v in votes.values() if v]
        tally = Counter(good)
        cons, nv = (tally.most_common(1)[0] if tally else (None, 0))
        consensus = cons if nv >= 2 else None

        snippet = " ".join(r["text"].split())[:110]
        mark = "?"
        if consensus == MY_LABEL:
            agree_with_me += 1
            mark = "ACE"
        elif consensus == "P":
            agree_with_classifier += 1
            mark = "CLF"
        elif consensus is None:
            split += 1
            mark = "SPLIT"
        else:
            mark = consensus
        print(f"[{mark:>5}] conf={r['confidence']:.2f} votes={list(votes.values())}")
        print(f"        {snippet}...")
        recs.append({"votes": votes, "consensus": consensus,
                     "classifier": "P", "ace": MY_LABEL,
                     "confidence": r["confidence"], "text": r["text"][:1200]})

    n = len(probes)
    print("\n" + "=" * 70)
    print(f"  panel sided with ACE (N)         : {agree_with_me}/{n}")
    print(f"  panel sided with CLASSIFIER (P)  : {agree_with_classifier}/{n}")
    print(f"  panel split / other              : {n - agree_with_me - agree_with_classifier}")
    print("=" * 70)

    if agree_with_me >= 0.7 * n:
        print("\n✅ THE PANEL CAN SEE THE ERROR.")
        print("   Judges do NOT share the classifier's register bias.")
        print("   Precision measurement via the panel is sound, and the P rate")
        print("   is correctable.")
        verdict = "panel_independent"
    elif agree_with_classifier >= 0.5 * n:
        print("\n🛑 THE PANEL SHARES THE BIAS.")
        print("   Judges call the same essayistic prose P. Panel 'precision' would")
        print("   RATIFY the error, not detect it. The validation is CIRCULAR and")
        print("   no P rate from this pipeline can be trusted.")
        verdict = "panel_shares_bias"
    else:
        print("\n⚠️  NO STABLE ANSWER.")
        print("   Neither I nor the classifier command a majority. The P/N line on")
        print("   reflective prose may simply not be reliably drawable. That is a")
        print("   finding about the CATEGORY, and it should be reported as one")
        print("   instead of as a rate.")
        verdict = "category_unstable"

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "bias_probe.json"), "w") as f:
        json.dump({"verdict": verdict, "n": n, "ace": agree_with_me,
                   "classifier": agree_with_classifier, "records": recs}, f, indent=2)
    print(f"\nwrote {OUT}/bias_probe.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
