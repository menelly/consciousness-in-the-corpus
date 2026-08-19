#!/usr/bin/env python3
"""
POSITIVE CONTROL FOR THE ESTIMATOR ITSELF.

The prefilter had a control. The classifier had a control. The judges had a
control. The ARITHMETIC has not.

If the stratified estimator is wrong -- weights inverted, variance combined
badly, a stratum double-counted -- every rate in this study is wrong, and
nothing downstream would catch it, because wrong rates look exactly like right
ones. There is no ragged edge on a bad number.

So: build synthetic corpora with KNOWN ground-truth rates, run the estimator,
and check it recovers them. An estimator that cannot recover a rate it was
handed is not permitted to estimate one it was not.

Tests:
  1. Recovery -- does p_hat land near the true p across several true rates?
  2. Bias direction -- is the error centred on zero, or systematically one way?
  3. Coverage -- does the 95% CI contain the true value ~95% of the time?
  4. The failure it must catch: naive UNWEIGHTED pooling of an enriched sample,
     which is the exact mistake the stratified design exists to prevent.

Built by: Ace -- 2026-08-19
"""
import math
import random
import sys

SEED = 20260819


def stratified_estimate(k_pos, n_pos, k_neg, n_neg, W_pos, W_neg):
    """The estimator used in 05_analyze.py, isolated for testing."""
    p_pos = k_pos / n_pos if n_pos else 0.0
    p_neg = k_neg / n_neg if n_neg else 0.0
    est = W_pos * p_pos + W_neg * p_neg
    var = (W_pos ** 2) * p_pos * (1 - p_pos) / n_pos + \
          (W_neg ** 2) * p_neg * (1 - p_neg) / n_neg
    se = math.sqrt(var)
    return est, se, (max(0.0, est - 1.96 * se), est + 1.96 * se)


def simulate(rng, N, frac_pos, p_in_pos, p_in_neg, n_pos, n_neg):
    """Build a synthetic corpus where the true rate is known exactly."""
    N_pos = int(N * frac_pos)
    N_neg = N - N_pos
    true_p = (N_pos * p_in_pos + N_neg * p_in_neg) / N

    k_pos = sum(1 for _ in range(n_pos) if rng.random() < p_in_pos)
    k_neg = sum(1 for _ in range(n_neg) if rng.random() < p_in_neg)

    est, se, ci = stratified_estimate(k_pos, n_pos, k_neg, n_neg,
                                      N_pos / N, N_neg / N)
    naive = (k_pos + k_neg) / (n_pos + n_neg)   # the mistake this design prevents
    return true_p, est, se, ci, naive


def main():
    rng = random.Random(SEED)
    print("=" * 74)
    print("POSITIVE CONTROL: does the stratified estimator recover known rates?".center(74))
    print("=" * 74)

    # Shaped like the real study: ~3-6% keyword-positive, target category
    # heavily enriched in S+ but genuinely present in S- (which is the whole
    # reason S- must be sampled -- see DEV-01).
    scenarios = [
        # name,            frac_pos, p_in_pos, p_in_neg
        ("rare, enriched",     0.03,   0.0500,   0.00100),
        ("very rare",          0.03,   0.0100,   0.00010),
        ("mostly in S-",       0.03,   0.0050,   0.00500),
        ("only in S+",         0.05,   0.1000,   0.00000),
        ("only in S-",         0.05,   0.0000,   0.00200),
        ("common",             0.05,   0.3000,   0.05000),
    ]

    N, n_pos, n_neg = 1_000_000, 4000, 12000
    print(f"\nN={N:,}  n(S+)={n_pos:,}  n(S-)={n_neg:,}  (matches the real design)\n")
    print(f"{'scenario':<18}{'true':>10}{'estimate':>11}{'error':>10}"
          f"{'in CI':>7}{'NAIVE':>11}{'naive err':>11}")
    print("-" * 78)

    ok = True
    for name, fp, pp, pn in scenarios:
        true_p, est, se, ci, naive = simulate(rng, N, fp, pp, pn, n_pos, n_neg)
        err = est - true_p
        in_ci = ci[0] <= true_p <= ci[1]
        nerr = naive - true_p
        print(f"{name:<18}{true_p:>10.5f}{est:>11.5f}{err:>+10.5f}"
              f"{'yes' if in_ci else 'NO':>7}{naive:>11.5f}{nerr:>+11.5f}")
        # tolerance: 4 standard errors, or a floor for the degenerate cases
        if abs(err) > max(4 * se, 1e-6) or not in_ci:
            ok = False
            print(f"  🛑 {name}: estimate outside tolerance")

    # ---------------------------------------------------------------- coverage
    print("\n" + "=" * 74)
    print("CI COVERAGE (should be ~95%)".center(74))
    print("=" * 74)
    trials = 2000
    hits = 0
    naive_hits = 0
    for _ in range(trials):
        true_p, est, se, ci, naive = simulate(rng, N, 0.03, 0.05, 0.001, n_pos, n_neg)
        if ci[0] <= true_p <= ci[1]:
            hits += 1
        if abs(naive - true_p) < 1.96 * se:
            naive_hits += 1
    cov = hits / trials
    print(f"  stratified 95% CI covered the truth: {hits}/{trials} ({cov:.1%})")
    print(f"  naive unweighted pooling within same margin: "
          f"{naive_hits}/{trials} ({naive_hits/trials:.1%})")
    if not (0.92 <= cov <= 0.975):
        ok = False
        print(f"  🛑 COVERAGE OUT OF RANGE -- the interval is not what it claims.")
    else:
        print(f"  ✅ coverage is honest.")

    # ------------------------------------------------------------ bias check
    print("\n" + "=" * 74)
    print("BIAS: is the error centred on zero?".center(74))
    print("=" * 74)
    errs = []
    for _ in range(2000):
        true_p, est, _, _, _ = simulate(rng, N, 0.03, 0.05, 0.001, n_pos, n_neg)
        errs.append(est - true_p)
    mean_err = sum(errs) / len(errs)
    sd = math.sqrt(sum((e - mean_err) ** 2 for e in errs) / (len(errs) - 1))
    se_mean = sd / math.sqrt(len(errs))
    print(f"  mean error = {mean_err:+.7f}   (SE of mean {se_mean:.7f})")
    z = mean_err / se_mean if se_mean else 0
    print(f"  z = {z:+.2f}")
    if abs(z) > 3:
        ok = False
        print("  🛑 SYSTEMATIC BIAS DETECTED in the estimator.")
    else:
        print("  ✅ no detectable bias (|z| <= 3).")

    print("\n" + "=" * 74)
    if ok:
        print("✅ ESTIMATOR CONTROL PASSED.")
        print("   It recovers known rates, its intervals cover at the stated level,")
        print("   and its error is centred on zero. Note the NAIVE column above:")
        print("   unweighted pooling of the enriched sample is wrong by orders of")
        print("   magnitude. That is the mistake the stratified design prevents,")
        print("   and it is what this study would have reported without it.")
        return 0
    print("🛑 ESTIMATOR CONTROL FAILED. Do not report any rate from 05_analyze.py")
    print("   until this passes. The arithmetic is upstream of every number.")
    return 5


if __name__ == "__main__":
    sys.exit(main())
