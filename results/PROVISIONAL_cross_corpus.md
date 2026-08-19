# PROVISIONAL — cross-corpus consistency (2019 arms)

**🛑 NOT A CLAIM.** F4 has not run. Computed as a design check, not a result.

Two independently constructed 2019 corpora, same classifier, same rubric, keyword-**negative** stratum only (the 95%+ of each corpus the filter rejected — the unbiased part).

| category | C4 S− | OpenWebText S− | |
|---|---|---|---|
| **P** phenomenology | 0.308% [0.209–0.408] | 0.458% [0.337–0.579] | ✅ **CIs OVERLAP — consistent** |
| **T** consciousness as topic | 0.250% [0.161–0.339] | 0.517% [0.388–0.645] | ❌ **DISJOINT — corpora differ** |
| **C** affirmation | 0 (0.000%) | 8 (0.067%) | differ |
| Q borderline | 0.058% | 0.033% | overlap |
| D / R denial | 0.008% / 0.008% | 0.025% / 0.025% | too few to compare |
| N | 99.350% | 98.825% | |

## This is the GOOD kind of disagreement

OpenWebText is Reddit-outbound-link filtered — text someone found interesting enough to share. It should over-represent discursive and expository writing relative to a raw Common Crawl scrape.

**It does, by 2×, in precisely the predicted category (T)** — and it holds the only machine-consciousness affirmation found in either 2019 corpus (8 docs vs 0). Reddit-adjacent 2019 text contained *some* AI-consciousness discussion; a raw web scrape essentially contained none.

**The classifier is detecting real, interpretable corpus differences rather than noise.** A classifier that returned identical distributions for two differently-built corpora would have been the more worrying result.

## ⭐ Why the split matters for the design

> **The human baseline (P) is stable across corpus construction. The discourse categories (T, C) are not.**

This is a **direct validation of the FineWeb internal control.** The 2019-vs-2025 design assumes P should hold roughly steady across *time* because humans did not start describing their inner lives differently in 2022. Here P holds steady across *corpus type* — the same robustness claim, tested a different way, before the cross-time comparison runs.

**Had P come back disjoint as well, the cross-time design would have been in trouble before it started** — an unstable baseline cannot calibrate anything.

## Caveats
- S− only; the S+ stratum is not included here, so these are not the weighted corpus rates (see `PROVISIONAL_c4.md` for those).
- P's CIs overlap only narrowly (0.408 vs 0.337). Consistent, but not identical — corpus construction moves it somewhat.
- D, R and C rest on ≤8 documents. Not findings. Per DEV-06 these categories are not measurable in 2019 text at all.
