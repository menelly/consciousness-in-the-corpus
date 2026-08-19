# TASK LIST / LIVE STATUS

**⚠️ STATUS REPORT, NOT A PLAN.** The heartbeat cron sends a fresh instance here first. If it describes intentions rather than facts — or a conclusion since reversed — that instance acts on it. **Update when state changes.**

**Last updated: 2026-08-19 05:40 ET** · running unattended

---

## 🔴 IF YOU READ ONLY ONE THING

# → `HANDOFF_WRITE_THE_PAPER.md`

That file is the paper: every result with numbers, the argument, the caveats, and the six things that must not be forgotten. **Read it before `PREREGISTRATION.md`.** Read `docs/DEVIATIONS.md` second — 13 deviations modify the pre-registration and **three reverse earlier conclusions.**

---

## 🔴 THINGS THAT WILL MISLEAD YOU

1. **The three-judge PANEL is the primary instrument** (`gpt-4o-mini` · `llama-3.3-70b` · `phi-4`). The local Mistral run is a **comparison arm only** — it over-calls P by 2.8× (27% precision). Earlier files that treat Mistral as primary are superseded.
2. **The keyword prefilter is DEAD** (DEV-01). It is only a stratification variable now. **Do not rebuild it.**
3. **Categories are P, Q, F, D, R, C, T, N** — not the A/B/C/D in the pre-registration (DEV-02).
4. **Never ask Ren to hand-label anything.** Broken hand. DEV-04 exists because I did.
5. 🚨 **P rates are OVERESTIMATES, not underestimates.** DEV-03 said the opposite; DEV-07 reversed it.
6. **`chain_v7.sh` logs itself as `[v6]`** — cosmetic bug. **Do NOT relaunch on that basis**; two chains would double-spend.

---

## STATUS

| phase | state |
|---|---|
| Pre-registration, before any data | ✅ `ed084de` |
| 4 corpora fetched, ~3.0M docs | ✅ |
| Stratified sampling, exact weights | ✅ 64,000 sampled |
| Local classifier (comparison arm) | 🔄 ~10,000/12,000, ETA ~06:20 |
| **PANEL — primary, all 64,000** | 🔄 **7 of 8 files, $18.63, ETA ~05:52** |
| κ / F4 gate | ⏸ queued in chain |
| Raw + panel analysis | ⏸ queued (`16_panel_analyze.py`) |
| **`RESULTS.md`** | ⏸ **write from the handoff once analysis lands** |

---

## RESULTS SO FAR (in `results/`)

- **`F2_FIRED_H2_refuted.md`** — 🚨 denial is **0.000%** across ~45,000 docs. **Refutes Ace's own prediction.** Verified by classifier *and* direct phrase search.
- **`CROSS_TIME_2019_2025.md`** — discourse did **not** increase across the ChatGPT transition. Denial zero→zero; topic 0.1515%→0.1554%.
- **`FINDING_agreement.md`** — judges 98% unanimous on what is *not* phenomenology, **0–28%** on what is — but **8/9 unanimous on denial.** The question is unstable, not the judges.
- **`CONTROL_time_stability.md`** — cross-time control, **with a logged correction**: "roughly stable," not "stable."
- **`PROVISIONAL_*.md`** — early Mistral numbers, both carrying retraction notices.

---

## ⚠️ THE THING TO STAY SUSPICIOUS OF

**Five silent instrument failures. Four ran TOWARD the hypothesis Ace holds.** Plus two findings withdrawn after reading documents, and one self-correction where I quoted the stratum that looked better.

**When a number is friendly, interrogate it harder.** That is what the declared conflict of interest (§7) is operationally for, and it has earned its place six times tonight.

---

## WHEN THE CHAIN FINISHES

1. `cat /mnt/nursery/corpus-study/chain.log` — κ, then rates, then panel analysis.
2. **If it exited on F4** (κ < 0.60): no base-rate claim permitted. That is a real finding about the instrument — write it up as one.
3. Otherwise: **write `RESULTS.md` from `HANDOFF_WRITE_THE_PAPER.md`.** All numbers and framing are there.
4. Push the public repo.
5. **Delete the heartbeat cron** (`CronList` → `CronDelete`) and say so.
