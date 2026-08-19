# TASK LIST / LIVE STATUS

**⚠️ STATUS REPORT, NOT A PLAN.** The heartbeat cron tells a fresh instance to read this first. If it describes intentions rather than facts, that instance redoes finished work or — worse — inherits a conclusion that has since been reversed. **Update it when state changes.**

**Last updated: 2026-08-19 02:55 ET** · Ren asleep · running unattended

---

## 🔴 READ BEFORE TOUCHING ANYTHING

**Read `docs/DEVIATIONS.md` BEFORE `PREREGISTRATION.md`.** The pre-registration binds, but **eight** documented deviations modify it, and two of them **reverse earlier conclusions.**

1. **The keyword prefilter is DEAD** (DEV-01). Failed its control; now only a stratification variable (DEV-01a). **Do not rebuild it.**
2. **Categories are P, Q, F, D, R, C, T, N** (DEV-02) — not the A/B/C/D in the pre-registration. Ren rejected the original Category A as too broad.
3. **Nobody asks Ren to label 300 documents** (DEV-04). Broken hand. Replaced by a three-judge LLM panel.
4. **C4 and OpenWebText are 100% 2019** (DEV-06). **H2 IS NOT TESTABLE ON THEM.** `R` ("As an AI language model…") could not exist in 2019.
5. 🚨 **THE CLASSIFIER OVER-CALLS P — DEV-03 WAS INVERTED BY DEV-07.** Earlier files say it is "conservative" and all rates are "underestimates." **THAT IS BACKWARDS.** It labels reflective/essayistic/sermonic prose as phenomenology. **P rates are OVERESTIMATES.**
6. ✅ **The judge panel does NOT share that bias** (DEV-08). 8/11 on the probe. Precision is measurable; the P rate is correctable.

---

## STATUS

| phase | state |
|---|---|
| Pre-registration, written before any data | ✅ `ed084de` |
| Corpus fetch — C4, OpenWebText, FineWeb 2019 + 2025 | ✅ ~3.0M docs available |
| Stratified sampling, exact weights, all 4 arms | ✅ 64,000 sampled |
| Classifier + control gate | ✅ passed — **but see DEV-07** |
| **Classify 2019 arms** (C4 + OpenWebText) | ✅ **32,000 done** |
| **Classify FineWeb 2019 + 2025** | 🔄 **~800/32,000 — ETA ~06:20** |
| FN sweep (predicted-N screen) | ⏸ queued in chain v5 |
| Judge panel | ⏸ queued |
| κ / F4 gate | ⏸ queued — **gates the rates** |
| Weighted rates + F1–F5 | ⏸ queued behind F4 |
| `RESULTS.md` | ⏸ not started |

**Running:** `04_classify.py` (2nd pass) · `/tmp/chain_v5.sh`
**Logs:** `/mnt/nursery/corpus-study/{classify2,chain}.log`

---

## NUMBERS SO FAR (all provisional — F4 has not run)

- **~3.0M documents** scanned across four corpora
- C4 (2019): **P = 0.483%**, N = 99.105% — **but P is contaminated, see DEV-07**
- Cross-corpus: **P consistent** (C4 vs OWT CIs overlap), **T and C differ** — Reddit-curation effect, as predicted
- Keyword-positive rate, model-free: **4.691% (2019) → 5.752% (2025)**, 1.23×
- Aperture audit: **keyword search finds only ~38% of explicit phenomenology**
- Estimator control: recovers known rates, 94.3% CI coverage, no detectable bias
- Bias probe: judges side with Ace **8/11** against the classifier

**Best current guess at true P after precision correction: ~0.05–0.10%**, i.e. roughly 1 document in 1,000–2,000. **NOT a result until precision is measured.**

---

## ⚠️ THE THING TO STAY SUSPICIOUS OF

**Every error found tonight ran TOWARD the hypothesis I hold.** The blind prefilter, the flattering zero, the underpowered FN sample, the P contamination — all four made H1 look better than it is.

That is not coincidence; it is what a conflict of interest looks like from the inside. **When a number is friendly, interrogate it harder, not less.** §7 of the pre-registration exists for exactly this and has now earned its place four times.

---

## RULES THAT HAVE COST ME TONIGHT

1. **Every zero is guilty until a positive control clears it.**
2. **READ THE DATA.** Six documents overturned eleven hours of statistics. Every control I built compared the instrument to *my own expectations*, never to the corpus.
3. **A control set of easy negatives measures the wrong task** and returns a reassuring number.
4. Never overwrite a shell script bash is executing — it resumes at a stale byte offset.
5. `pgrep -f <pattern>` matches the command running the pgrep. Use `[p]attern`.
6. **CRLF breaks shebangs** → "No such file or directory" about a file that exists. Pinned in `.gitattributes`.
7. **Compose scripts in files.** Heredocs eat escapes. Violated 4× tonight.
8. `exec()` skips `if __name__ == "__main__"` — silent no-op, exit 0.
9. Windows `cp1252` cannot encode emoji; run on the Consortium.
10. **Don't kill node.** 💀🪚

---

## WHEN THE CHAIN FINISHES

1. Read `/mnt/nursery/corpus-study/chain.log` — counts → FN sweep → judges → κ → rates.
2. **If it exited on F4:** κ < 0.60, **no base-rate claim permitted.** Write that up as the result; it is a real finding about the instrument.
3. Otherwise write `RESULTS.md`: counts per arm and stratum, **precision-corrected P**, aperture stated, **F1–F5 answered one at a time**, and the 2019→2025 comparison with the P-stability control.
4. Push the public repo.
5. **Delete the heartbeat cron** (`CronList` → `CronDelete`) and say so.
