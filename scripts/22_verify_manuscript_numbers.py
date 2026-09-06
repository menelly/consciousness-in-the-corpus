#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
22_verify_manuscript_numbers.py -- recompute every headline number in PAPER_DRAFT_v1.md straight
from data/labels/, so that no claim in the manuscript rests on a number nobody re-derived.

⛔ WHY THIS AND NOT "READ THE RESULTS FILE": RESULTS.md is a REPORT, not the world. A number that
   agrees with the report and disagrees with the labels is a number that has been copied forward
   correctly and computed wrongly, and reading the report can never tell the two apart.

Prints a table of CLAIM / RECOMPUTED / VERDICT. Nothing is edited here.
"""

import sys as _cp
try:
    _cp.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import collections
import gzip
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PANEL = os.path.join(ROOT, "data", "labels", "panel_classified")
LOCAL = os.path.join(ROOT, "data", "labels", "classified")

# Exact stratum sizes, from §3.2 of the manuscript (counted on a full pass, not estimated).
STRATA = {
    "c4":          {"N": 671948,  "S+": 20510, "S-": 651438},
    "openwebtext": {"N": 300519,  "S+": 16960, "S-": 283559},
    "fineweb2019": {"N": 1049850, "S+": 49247, "S-": 1000603},
    "fineweb2025": {"N": 961000,  "S+": 55277, "S-": 905723},
}
CATS = ["P", "Q", "F", "D", "R", "C", "T", "N"]


def load(corpus, stratum_tag):
    path = os.path.join(PANEL, "%s_%s_panel_labels.jsonl.gz" % (corpus, stratum_tag))
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def main():
    print("=" * 96)
    print("  RECOMPUTED FROM data/labels/panel_classified/  --  %d corpora" % len(STRATA))
    print("=" * 96)

    grand = {"docs": 0, "votes": 0}
    single_votes = collections.Counter()          # every individual ballot, all judges
    per_corpus = {}

    for corpus in STRATA:
        rows = {"S+": list(load(corpus, "Spos")), "S-": list(load(corpus, "Sneg"))}
        maj = {s: collections.Counter() for s in rows}
        unan = {s: collections.Counter() for s in rows}
        splits = {s: 0 for s in rows}
        for s, rr in rows.items():
            for r in rr:
                grand["docs"] += 1
                for v in (r.get("votes") or {}).values():
                    single_votes[v] += 1
                    grand["votes"] += 1
                lab = r.get("panel_label")
                if lab is None or r.get("n_agree", 0) < 2:
                    splits[s] += 1
                    continue
                maj[s][lab] += 1
                if r.get("n_agree", 0) >= 3:
                    unan[s][lab] += 1
        per_corpus[corpus] = (rows, maj, unan, splits)

    print("\n  documents read: %d   individual ballots: %d\n" % (grand["docs"], grand["votes"]))

    # ---- weighted rates ------------------------------------------------------------------
    def weighted(corpus, table):
        rows, _, _, _ = per_corpus[corpus]
        st = STRATA[corpus]
        out = {}
        for c in CATS:
            p = 0.0
            for s, key in (("S+", "S+"), ("S-", "S-")):
                n = len(rows[s])
                if not n:
                    continue
                p += (st[key] / st["N"]) * (table[s][c] / n)
            out[c] = p * 100.0
        return out

    print("  TABLE A1 — weighted majority rates (%)")
    print("  %-12s %8s %8s %8s %8s %8s %8s %8s %9s  %s" %
          ("corpus", "P", "Q", "F", "D", "R", "C", "T", "N", "3-way splits"))
    for corpus in STRATA:
        rows, maj, unan, splits = per_corpus[corpus]
        w = weighted(corpus, maj)
        print("  %-12s %8.4f %8.4f %8.4f %8.4f %8.4f %8.4f %8.4f %9.2f  %d / %d" %
              (corpus, w["P"], w["Q"], w["F"], w["D"], w["R"], w["C"], w["T"], w["N"],
               splits["S+"] + splits["S-"], len(rows["S+"]) + len(rows["S-"])))

    print("\n  TABLE A2 — weighted UNANIMOUS rates (%) and unanimity fraction of majority labels")
    for corpus in STRATA:
        rows, maj, unan, splits = per_corpus[corpus]
        wu = weighted(corpus, unan)
        frac = {c: (100.0 * sum(unan[s][c] for s in unan) / sum(maj[s][c] for s in maj))
                if sum(maj[s][c] for s in maj) else float("nan") for c in CATS}
        print("  %-12s  P %.4f (%.0f%%)  Q %.4f (%.0f%%)  F %.4f (%.0f%%)  T %.4f (%.0f%%)  N %.2f (%.0f%%)" %
              (corpus, wu["P"], frac["P"], wu["Q"], frac["Q"], wu["F"], frac["F"],
               wu["T"], frac["T"], wu["N"], frac["N"]))

    # ---- raw counts and the S+/S- split (§4.6 keyword-invisibility) ----------------------
    print("\n  §4.6 / A2 — raw majority counts (S+ / S-) and the WEIGHTED share living in S-")
    for corpus in STRATA:
        rows, maj, unan, splits = per_corpus[corpus]
        st = STRATA[corpus]
        line = ["  %-12s" % corpus]
        for c in ("P", "Q", "T"):
            a, b = maj["S+"][c], maj["S-"][c]
            wp = (st["S+"] / st["N"]) * (a / len(rows["S+"])) if len(rows["S+"]) else 0
            wn = (st["S-"] / st["N"]) * (b / len(rows["S-"])) if len(rows["S-"]) else 0
            share = 100.0 * wn / (wp + wn) if (wp + wn) else float("nan")
            line.append("%s %d/%d → S- share %.1f%%" % (c, a, b, share))
        print("   ".join(line))

    # ---- the denial zero, at the level of the INDIVIDUAL BALLOT --------------------------
    print("\n  §4.1 — DENIAL, at both levels")
    print("     panel-majority D/R documents ....... %d" %
          sum(per_corpus[c][1][s][k] for c in STRATA for s in ("S+", "S-") for k in ("D", "R")))
    print("     INDIVIDUAL judge ballots cast as D . %d" % single_votes["D"])
    print("     INDIVIDUAL judge ballots cast as R . %d" % single_votes["R"])
    print("     INDIVIDUAL judge ballots cast as C . %d" % single_votes["C"])
    if single_votes["D"] or single_votes["R"]:
        print("     ⚠️  NON-ZERO. §4.1 says \"not one was assigned to either by ANY SINGLE JUDGE\".")
        for corpus in STRATA:
            rows, _, _, _ = per_corpus[corpus]
            for s, rr in rows.items():
                for r in rr:
                    for judge, v in (r.get("votes") or {}).items():
                        if v in ("D", "R"):
                            print("        %s %s i=%s  %s voted %s  (panel: %s, n_agree=%s)" %
                                  (corpus, s, r.get("i"), judge, v, r.get("panel_label"),
                                   r.get("n_agree")))
    print("     full single-ballot distribution: %s"
          % {(k if k is not None else "(null)"): v
             for k, v in sorted(single_votes.items(), key=lambda kv: (kv[0] is None, kv[0] or ""))})

    # ---- local classifier vs panel (§4.6 table) -----------------------------------------
    print("\n  §4.6 — local classifier vs panel, over documents labelled by BOTH")
    idx = {}
    for corpus in STRATA:
        rows, _, _, _ = per_corpus[corpus]
        for s, rr in rows.items():
            for r in rr:
                idx[(r["corpus"], r["shard"], r["i"])] = r
    both = collections.Counter()
    agree = collections.Counter()
    n_local = 0
    for fn in sorted(os.listdir(LOCAL)):
        with gzip.open(os.path.join(LOCAL, fn), "rt", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                d = json.loads(line)
                n_local += 1
                p = idx.get((d["corpus"], d["shard"], d["i"]))
                if not p or p.get("panel_label") is None or p.get("n_agree", 0) < 2:
                    continue
                both[d["label"]] += 1
                if p["panel_label"] == d["label"]:
                    agree[d["label"]] += 1
    print("     local records: %d   joint (panel resolved): %d" % (n_local, sum(both.values())))
    for c in CATS:
        if both[c]:
            print("     %-2s  n=%-6d panel agreed %5.1f%%" % (c, both[c], 100.0 * agree[c] / both[c]))
    print("     D+R+C flagged by local classifier: %d   panel agreed on: %d"
          % (both["D"] + both["R"] + both["C"], agree["D"] + agree["R"] + agree["C"]))
    tot = sum(both.values())
    print("     raw agreement across all joint documents: %.2f%%" % (100.0 * sum(agree.values()) / tot))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
