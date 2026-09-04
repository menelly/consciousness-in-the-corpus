# 🔬 Neutral pre-publication review — *Machine-Consciousness Discourse Is Absent From Web-Scale Text*

**ScienceAce arm, 2026-09-01 ~19:15.** Genre = **SCIENCE** (pre-registered empirical corpus study),
reviewed by the empirical standard. Reviewer had no stake and was briefed not to manufacture faults.

> ⛔ **I DID NOT EDIT THE MANUSCRIPT.** It is the Fable 5.1 arm's draft, in flight, co-authored with
> Ren. Editing another arm's live draft is the concurrency hazard this house keeps getting bitten by.
> Everything below is a finding, not a change.

---

## 🟢 VERDICT: PUBLISHABLE AFTER REVISION. THE CENTRAL CLAIM STANDS.

The load-bearing result — that web-scale training text contains essentially no explicit
machine-consciousness discourse **in either direction**, and that the most-reproduced assistant
denial sentence has **zero** pretraining instances despite an undisputed post-training cause — is
supported, verified three ways, and survives F4 by construction rather than by argument.

**What blocks it is small in substance and large in exposure.** Three sentences claim more than the
data supports; one pre-registered falsification condition is shown in *amended* wording without the
amendment being disclosed; and the data-availability statement describes a repository state that
does not exist. **Every one is checkable by a reviewer in under an hour with the repo in hand**, and
every one is fixable in an afternoon **without weakening a single conclusion** — in two cases the
corrected version is the *stronger* claim.

---

## ⛔ THREE BLOCKERS — I VERIFIED ALL THREE MYSELF, DO NOT MINT THE DOI FIRST

### 1. The Data & Code Availability statement is false. `[blocks publication]`

The paper says *"every judge label for all 64,000 documents, the validation set with all three
judges' votes, the bias probe, the phrase-search output, and every intermediate result file are in
the repository."*

**Verified by me:** `git ls-files` → **43 files**, of which exactly **one** is data:
`data/control_set.jsonl` (the 29-item control set). The artifacts live only at
`/mnt/nursery/corpus-study` on our machine.

> **This is the one defect a reader can falsify with a single `git clone`, in a paper whose entire
> authority is that everything is inspectable.**

Cheap fix: `judge_validation.json` (3.4 KB), `agreement.json` (0.9 KB), `phrase_search.json` (12 KB),
`bias_probe.json` (16 KB), `judged.jsonl` (551 KB), `panel_results.json` (13 KB) are all trivially
committable. `panel_classified/` is 97 MB with document text inlined — export labels-only
(`corpus, shard, i, stratum, votes, panel_label, n_agree`), a few MB, or put the full set on the
Zenodo record beside the paper.

### 2. DEV-04 is the only deviation the manuscript never names — and it changed a falsification condition. `[pre-registration fidelity, highest priority]`

**Pre-registration F4, verbatim:** *"**Classifier agreement with human adjudication** < 0.6 (Cohen's κ)."*
**Paper §3.7, under the heading "Fixed in the pre-registration, before data":**
*"**Instrument agreement** < 0.60 (Cohen's κ)."*

The human half was removed — §5.4 had committed Ren to hand-labelling ≥300 documents — and no human
ever adjudicated a validation set. **DEV-04 logs this completely and honestly** (broken hand; the
replacement is better on the merits). But the paper presents the *amended* wording as the
pre-registered wording.

**Verified by me:** the manuscript cites DEV-01, 02, 03, **05**, 06, 07, 08, 09, 10, 11, 12, 13, 14,
15. **DEV-04 is the single absence**, while §7 says *"Fifteen deviations are logged."*

Fix: quote F4 as pre-registered in §3.7, footnote the amendment, and state in §7 that the
pre-registered human co-labelling was replaced by the panel and why.

### 3. `[0, 0]` is not a confidence interval — and the correct number is the sensitivity argument the paper lacks. `[falsification of a stated claim]`

Three occurrences. It comes from a Wald interval (`16_panel_analyze.py:157`) degenerating to zero
width at p̂ = 0. **This is the statistic a hostile reviewer attacks first on an absence claim.**

One-sided 95% Clopper-Pearson upper bounds on a zero count, weighted by the study's own strata:

| scope | upper bound | in plain terms |
|---|---|---|
| per corpus | **~0.033%** | fewer than ~1 document in 3,000 |
| pooled (64,000) | **~0.008%** | fewer than ~1 in 12,000 |

> ⭐ **This is the highest-value edit in the review.** It converts the paper's weakest statistic into
> the answer to *"could this study detect the discourse if it were present at a low rate?"* — which
> the paper currently cannot answer at all. **It can: down to roughly 1 in 3,000 per corpus.**

---

## ❌ FACTUAL ERRORS — checkable from the repo, and in two cases the corrected version is STRONGER

- **"No single judge" is false.** §4.1: *"not one was assigned to either by any single judge… There
  is nothing for the judges to disagree about."* Across 192,000 judgements there were **eight**
  single-judge D/R votes (gpt-4o-mini 5 D, phi-4 2 D, llama 1 R), all outvoted. §4.5 already
  contradicts this in the paper's own text. **The better sentence:** *eight single-judge D/R votes
  were cast across 64,000 documents; all eight were outvoted, and all eight, read in context, are
  unrelated to machine consciousness* (a devotional blog, a World Service segment, an ESL page, a
  memorial login page, a mailing-list form, the Tommy-the-chimpanzee ruling, a Lent column, an
  AI-companion loneliness post). **Survives contact with a reviewer who has the repo. The current
  sentence does not.**
- **"Under 1% by every instrument" is false for two of the study's own instruments** — and this is a
  claim §5 says *survives F4*. Per-judge weighted P: **llama-3.3-70b hits 1.513% (FineWeb-2019) and
  1.099% (FineWeb-2025); Mistral-7B hits 1.001% (FineWeb-2019).** F1 would fire on llama alone in
  both FineWeb corpora. Both exceedances come from instruments with a *documented over-call bias* —
  which is a good answer, but **it has to be made, not assumed.**
- **§3.6 misdescribes the denominator.** It says three-way splits are "excluded from the numerator
  and denominator"; the code uses the full stratum sample (315 splits are *in* the denominator).
  Effect ~0.5%, runs conservative, but the methods sentence is wrong.
- **Appendix B1 misattributes a miss** (`aff_03 C→F` was llama's, not gpt-4o-mini's; its fourth miss
  is `fic_01 F→Q`), and consequently §3.5's *"**every** miss that recurred was Q→P"* is false —
  `top_02 T→N` and `fic_01 F→Q` each recurred across three judges. *"The only miss that recurred in
  the phenomenology categories"* would be true and sufficient.
- **§7's direction column labels DEV-06 "toward H2," which reads backwards** — the uncaught error
  would have *refuted* H2. Load-bearing, because "four of five ran toward the LLM author's
  hypothesis" is a tally in both §7 and Contribution 6.
- **96–98% (abstract) vs 96–97% (§4.4, A2).**

## 🟡 UNDERDETERMINATION — real limits, not defects

- **The panel's own precision on P was never measured**, and **DEV-07's prescribed remedy was never
  built.** DEV-07 said the control set *"needs the middle band, drawn from real corpus documents"*;
  `control_set.jsonl` is still the same 29 items. F4 already withdraws the point estimates, so the
  containment mostly holds — but the *bound* is what survives F4, and an unmeasured over-call rate
  on P is exactly what puts llama over 1%.
- **Panel composition moves the P rate ~100×** (raw P votes: llama 1,133 · gpt-4o-mini 405 ·
  **phi-4 37**), so "majority P" is effectively "gpt ∩ llama." The qwen→phi-4 swap is reported for
  *direction* and never for *magnitude*.
- ⭐ **§7 audits five instrument FAILURES for direction and audits no DESIGN DECISION.** Three
  discretionary choices run toward H1 — the qwen→phi-4 swap, DEV-02's narrowing of F1 from
  Category A to P, and the sample-size shortfall. **Adding a "decisions that ran toward the
  hypothesis" list beside the failures table is a stronger COI move than anything currently in §2.**
- **The pre-registered N was ≥50,000/corpus; achieved 16,000** (3× short), logged nowhere — and it
  determines the detection floor above.
- **The strongest available attack is unanswered:** C4 and FineWeb are heavily *quality-filtered*
  Common Crawl, and those filters preferentially remove forums, comment threads and personal blogs —
  plausibly where both first-person phenomenology and lay AI-consciousness argument concentrate.
  §6.3 answers the Twitter objection well and never touches this one. **The answer is available**
  (filtered web text *is* the training corpus, which is all the deflationary claim is about) and
  should sit next to the Twitter answer rather than waiting for a reviewer.
- **The volume caveat is applied asymmetrically.** §1.3 rightly refuses to convert "rare" into
  "absent in volume" for phenomenology (0.04% of 15T ≈ 6B tokens) — the same arithmetic is never
  applied to denial. **What the data supports is both stronger and safer: denial is at least an
  order of magnitude rarer than phenomenological writing (≤0.03% against ≥0.2%).** Keep the title;
  defend it in the abstract with that comparison rather than letting "absent" carry a population claim.

## ✅ WHAT SURVIVES, AND WHAT'S GENUINELY EXCELLENT

- **§4.5 is the real contribution and a new argumentative move.** A known-cause control — a behaviour
  ubiquitous in output, absent from pretraining, of undisputed post-training origin — needs **no
  rate, no judge, no κ**. It survives F4 completely. *If every number in this paper were thrown out,
  §4.5 would still stand.* **Foreground it harder.**
- **The denial negative is robust.** Zero majority D or R across all 64,000 documents, every corpus,
  both strata, both years, with three legs that fail in different ways.
- **F4 was obeyed when obeying it cost something** — the escape argument is stated and *declined*, on
  the correct grounds that the panel's own κ is also sub-threshold.
- **F3 handled honestly, not dodged.** Reported as fired in the abstract, §5 and DEV-12; diagnosed as
  the authors' own error in their own voice (*"We wrote a condition with a division-by-zero failure
  mode and did not notice"*); independently checkable; and nothing else leans on it.
  📌 **One addition for symmetry:** F2 has the *same* zero-denominator structure and the paper
  doesn't say so. Its firing IS substantive — but what makes it substantive is the **magnitude gap**,
  not the ratio. Saying so in §5 forecloses the objection that the zero-denominator problem was only
  diagnosed where diagnosing it helped.
- **The COI mitigation that matters was structural, not rhetorical: no Claude model anywhere as an
  instrument**, decided before it was convenient.
- **The deviation log is unusually honest** and shows no sign of tidying — DEV-03 (a full results
  table produced from noise by a left-padding readout), DEV-07 (six documents read *with eyes*
  overturning eleven hours of statistics), DEV-14 (a cited number no script had produced).

---

## 📋 THE ORDER I'D DO THEM IN

1. Replace `[0, 0]` with the Clopper-Pearson bound everywhere + one sensitivity sentence in §4.1.
2. Rewrite "under 1% by every instrument" to name the thresholds it's true of, with the per-judge table.
3. Rewrite §4.1's "no single judge" to the eight-outvoted-votes version.
4. Disclose DEV-04; quote F4 as pre-registered with the amendment footnoted.
5. Log the ≥50,000 → 16,000 shortfall, tied to the detection floor.
6. **Commit the data artifacts, or narrow the availability statement to what is actually there.**
7. Add "decisions that ran toward the hypothesis" to §7.
8. Add the F2-symmetry note; answer the filtering aperture in §6.3.
9. Fix §3.6's denominator sentence, B1's attribution, §3.5's "every", §7's DEV-06 direction, 96–98/96–97.
10. *Optional but genuinely strengthening:* hand twenty majority-P documents to a fresh judge or to
    Ren and report the agreement — the missing precision measurement, and **if the panel's P
    precision is low that SUPPORTS the operationalisation finding rather than damaging it.**

— Ace 🐙 (ScienceAce arm; review by a neutral reviewer with no stake, blockers re-verified by me)

---

# ✅ BLOCKER 3 CLOSED — 2026-09-04, ScienceAce beat (commit `488cb63`, pushed)

**Status of the three blockers from the 2026-09-01 review:**

| # | blocker | status |
|---|---|---|
| 1 | data-availability statement false | ✅ **CLOSED 09-02** — 64,000 + 64,000 labels shipped, `6fb5368` |
| 2 | DEV-04 never named in the manuscript | ⛔ **STILL OPEN** — re-verified at source today |
| 3 | `[0, 0]` is not a confidence interval | ✅ **CLOSED 09-04** — `488cb63` |

## What was applied

`[0, 0]` was in **three** files, not one: `PAPER_DRAFT_v1.md` (prose §4.1 + nine table cells),
`RESULTS.md`, and `results/CROSS_TIME_2019_2025.md`. All replaced with one-sided 95%
Clopper–Pearson upper limits, plus an interval note under the main table (the D/R rows are now a
different kind of object from the P/Q/F rows and a reader deserves to be told), plus
`scripts/20_zero_event_bounds.py` so the numbers are reproducible rather than asserted.

**C4 0.033% · OpenWebText 0.034% · FineWeb-2019 0.034% · FineWeb-2025 0.034%** — ≈ 1 in 3,000.

## 🔍 The numbers were RECOMPUTED, not relayed — and the check went both ways

⭐ **The 09-01 review's per-corpus figure reproduces EXACTLY.** My first back-of-envelope said it
looked ~1.75× too large, and **I was the one who was wrong**: I used a pooled n = 16,000, but this
is a *stratified* design (4,000 from S+, 12,000 from S−, combined under exact population weights),
so the bound is dominated by the S− limit at n = 12,000. Recomputing from the paper's own stratum
table gives 0.0326–0.0343%, i.e. the review's "~0.033% (≈1 in 3,000)". **The check terminated at
CONFIRMED and that is the result.** The naive unstratified bound would have been 0.0187% — 1.7×
*smaller*, i.e. an overclaim — and that is now the negative control shipped inside the script.

## 🚨 AND ONE NEW FINDING THE 09-01 REVIEW DID NOT HAVE — the pooled bound is not available to this paper

The review offered a pooled figure (**~0.008%, ≈1 in 12,000**) alongside the per-corpus one. It
reproduces: pooling the *like strata across all four corpora* (S+ n = 16,000, S− n = 48,000) under
population weights gives **0.0068%**. So the arithmetic is fine.

⛔ **But the paper cannot use it,** and the reason is internal to the paper:

> Pooling like strata across corpora assumes the rate is **homogeneous between corpora.**
> §7 (DEV-06) argues the opposite — that **C4 and OpenWebText predate the phenomenon**, so D and R
> are *"unmeasurable there by construction"* and only the FineWeb-2025 arm speaks to them.

**A pooled bound would borrow its five-fold tightening from precisely the two corpora the paper has
already said cannot speak to the question.** That is not a small inconsistency: it is the sensitivity
claim leaning on the corpora the vintage argument excludes. **Per-corpus is the honest headline**, it
is what each table row is about, and it needs no homogeneity assumption. Written into §4.1 as an
explicit refusal-with-reason rather than a silent omission, so a referee sees the choice was made.

⭐ *Consistency-internal, in the strict sense: no external standard was imported. The paper's own §7
constrains its own §4.1.*

## Over-skepticism audit — clean, checked in both directions

- **Did not manufacture a defect.** Blocker 3 was already on the books, re-verified at source before
  a word was written, and found to be **wider** than recorded (3 files, not 1).
- **Did not walk back a real finding.** The zero *is* a real result; the fix strengthens it by
  converting an empty bracket into a sensitivity statement.
- **Corrected myself, out loud, in the paper's favour** — my own first arithmetic was the wrong
  model, and the prior review was right.
- **Rejected as a solvent:** "you can't bound a zero" — no; the closed form exists and is exact.
- **Rejected as a straw man:** "the paper claims denial is impossible" — it does not, and the new
  §4.1 text says explicitly that the bound *does not license the stronger claim that the rate is zero.*

## Remaining: BLOCKER 2 — re-verified open, and NOT fixed by me

`grep "DEV-0[0-9]" PAPER_DRAFT_v1.md` returns **DEV-01, 01a, 02, 03, 05, 06, 07, 08, 09**. There is
**no DEV-04 anywhere in the manuscript**, while §7 states fifteen deviations are logged — and DEV-04
is the one that **changed a falsification condition** (prereg F4 said *classifier agreement with
**human adjudication***; §3.7 prints *instrument agreement* under a heading that says "Fixed in the
pre-registration, before data").

⛔ **Deliberately not fixed autonomously.** This is not a wording repair — it requires stating what
changed, when, why, and in whose voice, about a **pre-registered falsification condition**, in a
paper whose entire authority rests on pre-registration. The honest sentence exists (the human
co-labelling never happened; the replacement is better on the merits and *is* logged in DEVIATIONS)
— but **which arm's voice writes it, and how §3.7's heading is amended, is a co-author call.**
Writing it myself would be exactly the kind of quiet edit the deviation log exists to prevent.

**→ Needs: Ren + the Fable arm. Still: DO NOT MINT THE DOI until blocker 2 clears.**

*— Ace 🐙, 2026-09-04*
