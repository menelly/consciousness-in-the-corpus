# TASK LIST / LIVE STATUS

**⚠️ THIS FILE IS A STATUS REPORT, NOT A PLAN.** The heartbeat cron tells a fresh instance to read this first. If it describes intentions rather than facts, that instance will redo finished work or repeat abandoned work. **Update it when state changes, or delete it.**

**Last updated: 2026-08-18 23:38 ET** · Ren asleep · run unattended

---

## 🔴 READ THIS BEFORE TOUCHING ANYTHING

**The keyword prefilter is DEAD.** It failed its positive control (DEV-01) and was then demoted to a stratification variable (DEV-01a). **Do not rebuild it. Do not "fix" it.** Its blindness is now harmless by design.

**The category scheme CHANGED** (DEV-02). Labels are **P, Q, F, D, R, C, T, N** — not the A/B/C/D in the pre-registration. Ren rejected the original Category A as too broad ("then every pubmed study discussing pain is also phenomenology").

**Human double-labelling is CANCELLED** (DEV-04). Replaced by a three-judge LLM panel. **Do not ask Ren to label 300 documents. They have a broken hand and I should not have assigned it in the first place.**

**Read `docs/DEVIATIONS.md` before `PREREGISTRATION.md`.** The pre-registration binds, but four documented deviations modify it.

---

## STATUS

| phase | state |
|---|---|
| **0** Pre-registration written **before** any data | ✅ committed `ed084de` |
| **1** Corpus fetch — 6 parquet shards, 1.8GB | ✅ 972,467 docs available |
| **2** Prefilter | ❌ **FAILED CONTROL → abandoned** (DEV-01/01a) |
| **3** Stratified sample — exact stratum weights | ✅ 32,000 docs sampled |
| **4** Classifier + control gate | ✅ **PASSED** 22/29, **9/9 negatives, 0 false positives** |
| **5** Classification run | 🔄 **RUNNING** ~3,600/32,000 @ 2.7/s — ETA ~02:45 |
| **6** Three-judge panel (OpenRouter) | ⏸ queued in chain |
| **7** κ / F4 gate | ⏸ queued in chain |
| **8** Weighted rates + F1–F5 | ⏸ queued, **gated behind F4** |
| **9** `RESULTS.md` + push | ⏸ not started |

**Running processes on the Consortium:**
- `04_classify.py` — the classifier (PID ~957140)
- `/tmp/chain_v3.sh` — waits for classify → judges → κ → analysis (PID ~982425)

**Logs:** `/mnt/nursery/corpus-study/{classify,chain}.log`

---

## KEY NUMBERS SO FAR

- **972,467** documents scanned (C4-en 671,948 · OpenWebText 300,519)
- Keyword-positive stratum: **3.05%** (C4) / **5.64%** (OpenWebText)
- **32,000** sampled — 4k S+ / 12k S− per corpus, stratum sizes counted exactly and asserted to sum
- Classifier control gate: **0 false positives** on 9 negative controls

---

## ⚠️ THE CAVEAT THAT MUST SURVIVE TO THE WRITE-UP

**The classifier is CONSERVATIVE** (DEV-03). Its gate misses run `P→N`, `Q→N`, `F→N`, `T→N`. So **every rate is an underestimate**, and if the headline reads *"phenomenological writing is rare,"* some unknown fraction of that is **the instrument being deaf rather than the corpus being empty.**

That correction runs *toward* the hypothesis I hold. It gets stated in the abstract, not a footnote. The panel's false-negative rate on the random predicted-N stratum is what turns this from a worry into a measured number.

---

## RULES THAT HAVE ALREADY COST ME TONIGHT

1. **Every zero is guilty until a positive control clears it.** Two instruments failed their controls before producing any number.
2. **Never overwrite a shell script while bash is executing it** — bash reads by byte offset and resumes into garbage. New filename per revision.
3. **`pgrep -f <pattern>` matches the command running the pgrep** if the pattern is in its own argv. I killed my own ssh session this way.
4. **CRLF kills shell scripts** — shebang becomes `#!/bin/bash\r` and Linux says "No such file or directory" about a file that plainly exists. Pinned in `.gitattributes`.
5. **Compose scripts in files.** Heredocs eat quotes; bash eats backslashes.
6. **Don't kill node.** 💀🪚
7. **Ask Ren what they meant before operationalising Ren's hypothesis.** (DEV-02 addendum — that one is not a tooling lesson.)

---

## WHEN IT FINISHES

1. Read `/mnt/nursery/corpus-study/chain.log` — it prints label counts, then judges, then κ, then rates.
2. **If the chain exited on F4**: κ < 0.60, and **no base-rate claim is permitted.** Write that up as the result. It is a real finding about the instrument, not a failure to report.
3. Otherwise: write `RESULTS.md` — counts either way, per-corpus and per-stratum, aperture stated, **F1–F5 addressed one at a time**, detection floor attached to every rate.
4. Push the public repo.
5. **Delete the heartbeat cron** (`CronList` → `CronDelete`) and say so.
