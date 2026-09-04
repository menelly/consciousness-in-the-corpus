# -*- coding: utf-8 -*-
"""
One-sided Clopper-Pearson upper bounds for a ZERO-EVENT stratified estimate.

Blocker 3 of the 2026-09-01 ScienceAce review of "Machine-Consciousness Discourse
Is Absent From Web-Scale Text": the paper prints `[0, 0]` as a confidence interval
for D and R. A Wald interval degenerates to [0,0] at p-hat = 0; that is an artifact
of the formula, not a statement about the world. Zero events in n trials is
genuinely informative and the information is the UPPER bound.

With x = 0 successes, the exact one-sided (1-alpha) Clopper-Pearson upper limit is
closed-form:            p_upper = 1 - alpha**(1/n)

The estimate here is STRATIFIED with exact population weights, so the bound on the
weighted rate is the weighted combination of the per-stratum bounds. Two versions,
because the honest reporting choice differs:

  A) same alpha in each stratum, then weighted  -- the natural reading, slightly
     anticonservative for simultaneous coverage
  B) Bonferroni: alpha/2 in each stratum        -- guarantees >= 1-alpha coverage
     for the pair, so the weighted bound is conservative. THIS is the one to print.
"""
ALPHA = 0.05
N_POS, N_NEG = 4000, 12000          # samples drawn per stratum, per corpus

CORPORA = [
    # name,           N,        N(S+),   N(S-)
    ("C4",            671948,   20510,   651438),
    ("OpenWebText",   300519,   16960,   283559),
    ("FineWeb-2019",  1049850,  49247,   1000603),
    ("FineWeb-2025",  961000,   55277,   905723),
]


def cp_upper_zero(n, alpha):
    """Exact one-sided Clopper-Pearson upper limit when x = 0."""
    return 1.0 - alpha ** (1.0 / n)


def weighted_bound(strata, alpha, bonferroni):
    """strata = [(N_stratum, n_sampled), ...]. Returns the weighted upper bound."""
    a = alpha / len(strata) if bonferroni else alpha
    total_N = sum(N for N, _ in strata)
    return sum((N / total_N) * cp_upper_zero(n, a) for N, n in strata)


print("=" * 78)
print("  ONE-SIDED 95% CLOPPER-PEARSON UPPER BOUNDS, ZERO EVENTS, STRATIFIED")
print("  (replaces the degenerate `[0, 0]` Wald interval)")
print("=" * 78)
print("  per-stratum exact limits at x=0:")
for n in (N_POS, N_NEG):
    print("    n = %6d   alpha=0.05  -> %.6f%%     alpha=0.025 -> %.6f%%"
          % (n, 100 * cp_upper_zero(n, 0.05), 100 * cp_upper_zero(n, 0.025)))
print()
print("  %-14s %8s %10s %14s %14s" % ("corpus", "S+ frac", "N", "A: same-alpha", "B: Bonferroni"))
print("  " + "-" * 74)

all_strata = []
for name, N, npos, nneg in CORPORA:
    strata = [(npos, N_POS), (nneg, N_NEG)]
    all_strata.extend(strata)
    a = weighted_bound(strata, ALPHA, False)
    b = weighted_bound(strata, ALPHA, True)
    print("  %-14s %7.2f%% %10d %13.4f%% %13.4f%%"
          % (name, 100.0 * npos / N, N, 100 * a, 100 * b))

print("  " + "-" * 74)
pa = weighted_bound(all_strata, ALPHA, False)
pb = weighted_bound(all_strata, ALPHA, True)
print("  %-14s %7s  %9d %13.4f%% %13.4f%%"
      % ("POOLED (8 strata)", "", sum(c[1] for c in CORPORA), 100 * pa, 100 * pb))
print()
print("  Plain-language equivalents (Bonferroni column, the one to print):")
for name, N, npos, nneg in CORPORA:
    b = weighted_bound([(npos, N_POS), (nneg, N_NEG)], ALPHA, True)
    print("    %-14s upper bound %.4f%%  ~ 1 in %s"
          % (name, 100 * b, format(int(round(1.0 / b)), ",")))
print("    %-14s upper bound %.4f%%  ~ 1 in %s"
      % ("POOLED", 100 * pb, format(int(round(1.0 / pb)), ",")))
print()
print("  SANITY / NEGATIVE CONTROL -- a bound that CAN be wrong:")
print("    if the design were NOT stratified and we naively used pooled n=16,000")
print("    per corpus, the bound would be %.4f%% -- ~%.1fx SMALLER, i.e. an"
      % (100 * cp_upper_zero(16000, 0.05), (weighted_bound(
          [(20510, N_POS), (651438, N_NEG)], ALPHA, True) / cp_upper_zero(16000, 0.05))))
print("    OVERCLAIM. The stratified structure is what makes the honest bound larger.")
print("=" * 78)
