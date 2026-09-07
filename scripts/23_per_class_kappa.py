#!/usr/bin/env python3
"""23_per_class_kappa.py — per-class chance-corrected agreement, from data/labels/, for X-G(G).

Referees X-C and X-G (2026-09-06) both flagged that "judges agree only 4-11% on P" reports
UNANIMITY among majority-P labels, not agreement, and that unanimity on a 0.2% class under a
2-of-3 rule is mechanically depressed. Fix they both proposed: a per-class chance-corrected
statistic, or unanimity against an independence baseline at each class's observed marginal.
This script computes BOTH, per corpus, from the same panel ballots script 22 verified.

Category-specific Fleiss kappa (Fleiss 1971, eq. for kappa_j):
    kappa_j = 1 - sum_i n_ij (n - n_ij) / ( N * n * (n-1) * p_j * (1 - p_j) )
  N documents, n = 3 raters, n_ij = raters assigning category j to document i,
  p_j = overall proportion of ballots for j.  kappa_j in (-inf, 1]; 0 = chance.

Independence baseline for unanimity: with judge k's marginal m_kj for class j,
  P(all three vote j) = prod_k m_kj ;  P(majority j) = P(>=2 vote j).
  Expected unanimity-among-majority = P(3 vote j) / P(>=2 vote j).
  Compare with observed 3-0 fraction among majority-j labels.

No Claude model touches a label here; this is arithmetic over ballots already cast by
gpt-4o-mini, llama-3.3-70b and phi-4 (and qwen where it sat). Run: python scripts/23_per_class_kappa.py
"""
import os, json, gzip, collections, itertools, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PANEL = os.path.join(ROOT, "data", "labels", "panel_classified")
CORPORA = ["c4", "openwebtext", "fineweb2019", "fineweb2025"]
CATS = ["P", "Q", "F", "T", "C", "D", "R", "N"]

def load(corpus, tag):
    p = os.path.join(PANEL, "%s_%s_panel_labels.jsonl.gz" % (corpus, tag))
    with gzip.open(p, "rt", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)

def main():
    out = {}
    print("per-class chance-corrected agreement, from data/labels/panel_classified/\n")
    for corpus in CORPORA:
        rows = list(load(corpus, "Spos")) + list(load(corpus, "Sneg"))
        # ballots per doc: list of votes (only docs with exactly 3 valid votes)
        ballots = []
        judge_votes = collections.defaultdict(collections.Counter)
        for r in rows:
            votes = r.get("votes") or {}
            vs = [v for v in votes.values() if v in CATS]
            if len(vs) != 3:
                continue
            ballots.append(vs)
            for j, v in votes.items():
                if v in CATS:
                    judge_votes[j][v] += 1
        N, n = len(ballots), 3
        total_ballots = N * n
        p = {c: sum(b.count(c) for b in ballots) / total_ballots for c in CATS}
        kappa = {}
        for c in CATS:
            if p[c] in (0.0, 1.0):
                kappa[c] = float("nan"); continue
            num = sum(b.count(c) * (n - b.count(c)) for b in ballots)
            kappa[c] = 1.0 - num / (N * n * (n - 1) * p[c] * (1 - p[c]))
        # observed unanimity among majority labels, and independence baseline
        judges = sorted(judge_votes)
        marg = {j: {c: judge_votes[j][c] / sum(judge_votes[j].values()) for c in CATS} for j in judges}
        obs, base = {}, {}
        for c in CATS:
            maj = [b for b in ballots if b.count(c) >= 2]
            unan = [b for b in maj if b.count(c) == 3]
            obs[c] = (len(unan), len(maj), (len(unan) / len(maj)) if maj else float("nan"))
            # independence baseline using the three judges' marginals for class c
            ms = [marg[j][c] for j in judges[:3]]
            p3 = ms[0] * ms[1] * ms[2]
            p2 = sum(ms[a] * ms[b] * (1 - ms[k]) for a, b, k in [(0, 1, 2), (0, 2, 1), (1, 2, 0)])
            base[c] = p3 / (p3 + p2) if (p3 + p2) > 0 else float("nan")
        out[corpus] = {"N_docs": N, "judges": judges, "ballot_share": p, "kappa_per_class": kappa,
                       "unanimity_obs": {c: {"unanimous": obs[c][0], "majority": obs[c][1], "frac": obs[c][2]} for c in CATS},
                       "unanimity_indep_baseline": base}
        print("%-12s N=%d  judges=%s" % (corpus, N, ",".join(j.split("/")[-1] for j in judges)))
        print("   class  share%%   kappa_j   unan/maj   obs_frac  indep_baseline")
        for c in CATS:
            u, m, fr = obs[c]
            print("   %-5s %7.3f  %8.3f  %5d/%-5d  %8s  %8s" % (
                c, 100 * p[c], kappa[c], u, m,
                ("%.3f" % fr) if fr == fr else "  n/a",
                ("%.3f" % base[c]) if base[c] == base[c] else "  n/a"))
        print()
    res = os.path.join(ROOT, "results", "per_class_kappa_2026-09-07.json")
    with open(res, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    print("wrote", res)

if __name__ == "__main__":
    main()
