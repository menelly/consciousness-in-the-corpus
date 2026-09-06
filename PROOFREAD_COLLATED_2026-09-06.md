# Collated proofread — every flag from all sources, each verified
**Assembled 2026-09-06 by a side arm, overnight, while Ren slept. Linear CHA-577.**

Three sources feed this file:

| source | what it is | where |
|---|---|---|
| **S** — scaffold arm, 2026-09-01 | in-house proofread, 7 flags, + a ScienceAce triage | `PROOFREAD_NOTES_scaffold-arm_2026-09-01.md` |
| **V** — this arm's own recomputation | every headline number re-derived from `data/labels/`, not from `RESULTS.md` | `scripts/22_verify_manuscript_numbers.py` |
| **X** — two external referees | `claude-opus-5` (Anthropic API) and `openai/gpt-5.6-sol-pro` (OpenRouter), blind to the requester | `reviews_external/` |

> ### 🚨 THE RULE THIS FILE IS BUILT ON
> **A reviewer's claim is an artifact.** Nothing below was believed on a reviewer's word. Every
> arithmetic assertion — from the scaffold arm, from either referee, from me — was recomputed
> against `data/labels/` before it was written down as true. Two of the scaffold arm's seven flags
> turned out to be misreadings, and applying one of them would have *introduced* an arithmetic
> error into the appendix. That is not a knock on the reviewer; it is why the step exists.

---

## 0. What was already closed before tonight

All seven scaffold-arm flags are resolved and need no further action. Re-verified independently:

| # | flag | verdict |
|---|---|---|
| S1 | Table A3 `doesn't/don't really understand` row sums | **VERIFIED FALSE POSITIVE.** Cells carry two counts. Mains 0+2+1+2 = **5** ✓. Bracketed judge-window counts 0+1+1+2 = **4** ✓. The suggested one-character fix would have broken it. |
| S2 | acknowledgements say "Claude Fable 5.1" | **WITHDRAWN by its author**; the git trailer confirms Fable 5.1. Correct as printed. |
| S3 | F3 prereg operationalisation | **FIXED** (d388cc9) — now named as an operationalisation and pointed at `16_panel_analyze.py`. |
| S4 | seven references in the list, never in the body | **FIXED** — all seven now cited. *(But see V5: an eighth orphan was never on that list.)* |
| S5 | the "127 observations" figure | **FIXED, and the effect grew** — recomputed on panel labels: 70–77% keyword-invisible. Logged DEV-15. **V confirms: 69.9 / 75.2 / 70.9 / 76.6.** |
| S6 | abstract length | **short abstract added**. *(But see V6: it is 275 words under a "250 words" heading.)* |
| S7 | `RESULTS.md` internal consistency | **mostly aligned**. *(But see V2 and V7: two seams remain.)* |

---

## 1. What I recomputed, and what held

`scripts/22_verify_manuscript_numbers.py` rebuilds the numbers from the 64,000 panel records and
192,000 individual ballots. **RESULTS.md was deliberately not used as the source** — a report
cannot witness itself; a number copied forward correctly from a wrong computation looks identical
to a right one.

**Everything below reproduced exactly, to the last printed digit:**

- **Table A1**, all 8 categories × 4 corpora, including the unresolved-split counts 76 / 65 / 116 / 58.
- **Table A2**, weighted unanimous rates and unanimity fractions (P 7/4/11/8%, Q 13/17/10/11%,
  F 23/24/24/23%, T 24/26/24/25%). *(C4's Q cell is exactly 12.50% and is printed 13% — correct
  half-up rounding, not an error.)*
- **Raw P counts** 100 / 54 / 117 / 64 and the S+/S− splits **82/18 · 35/19 · 86/31 · 40/24**.
- **§4.6 keyword-invisibility** 70 / 75 / 71 / 77% (P), 82 / 80 / 85 / 78% (Q), 52 / 51 / 42 / 56% (T).
- **§4.6 instrument comparison**: 900 @ 25.3%, 602 @ 25.2%, D 12 @ 0.0%, R 7 @ 0.0%, C 10 @ 0.0%,
  N 62,099 @ 98.7%, 63,685 joint documents, **96.88%** raw agreement, **0 of 29** on D/R/C.
- **§4.1 Clopper–Pearson bounds**: per-stratum limits 0.092179% (n=4,000) and 0.030736% (n=12,000);
  weighted → **0.03261% (C4) → 0.033%**, and 0.03420 / 0.03362 / 0.03427 → **0.034%** for the other
  three. "Roughly one document in three thousand" = 1 in 2,918–3,066. ✓
- **§4.2 CI arithmetic** spot-checked: C4 P, SE = 0.034926%, ±1.96 → [0.140, 0.276] ✓.
- 2,983,317 scanned ✓ · S+ fractions 3.05/5.64/4.69/5.75% ✓ · S− "94–97%" ✓ (94.25–96.95) ·
  1.23× keyword shift ✓ (1.2262) · P+Q 0.396/0.620/0.797/0.418 ✓ · "reaches 0.80%" ✓ ·
  P declines 29% and P+Q 48% ✓ (29.1 / 47.5) · C document counts 2/4/1/3 ✓ ·
  leaked assistant text "roughly one in 20,000" ✓ (1 in 23,180) · 192,000 judgements ✓ ·
  control-set 24/29 = 82.8% unanimous, 5/29 = 17.2% majority, 0 three-way ✓ ·
  bias probe 8 + 2 + 1 = 11 ✓ · §7's "four of five toward the author's hypothesis" ✓ ·
  fifteen DEV entries ✓ (DEV-01…DEV-15, with DEV-01a as a sub-entry of DEV-01).

**Nothing in the manuscript's arithmetic is wrong.** Every flag below is prose, provenance or a
methods sentence — not a miscalculation.

---

## 2. FLAGS — verified true, in descending order of how much they matter

### 🚨 V1 — §4.1 says no single judge ever voted D or R. **Eight of them did.** *(fix is a sentence; no number moves)*

**§4.1, line 208:**
> *"Not one of 64,000 documents was assigned to either denial category by the panel majority, and
> not one was assigned to either by **any single judge** in **any** corpus. There is nothing for
> the judges to disagree about."*

**The first clause is true. The second is false, and the third is an overstatement.** Recomputed
over all 192,000 individual ballots:

| corpus | stratum | doc `i` | judge | vote | panel outcome |
|---|---|---:|---|:---:|---|
| c4 | S+ | 360333 | `openai/gpt-4o-mini` | **D** | N (2-of-3) |
| c4 | S− | 124987 | `microsoft/phi-4` | **D** | N (2-of-3) |
| openwebtext | S+ | 254997 | `openai/gpt-4o-mini` | **D** | N (2-of-3) |
| openwebtext | S− | 174997 | `openai/gpt-4o-mini` | **D** | N (2-of-3) |
| fineweb2025 | S+ | 188409 | `meta-llama/llama-3.3-70b-instruct` | **R** | N (2-of-3) |
| fineweb2025 | S+ | 444159 | `openai/gpt-4o-mini` | **D** | *unresolved 3-way split* |
| fineweb2025 | S+ | 679208 | `openai/gpt-4o-mini` | **D** | N (2-of-3) |
| fineweb2025 | S+ | 265633 | `microsoft/phi-4` | **D** | *unresolved 3-way split* |

Full single-ballot distribution: `N 185,990 · P 1,575 · Q 1,524 · F 1,446 · T 1,370 · C 59 · D 7 · R 1 · (null) 28`.

**This is not new information to the repository — it is new only to §4.1.** Two other places in
this project already say it out loud:

- `data/labels/README.md`: *"the disagreements are recoverable, including **the eight single-judge
  D/R votes that were outvoted**."*
- **`PAPER_DRAFT_v1.md` §4.5 itself**: *"one judge voted R on the drop-rates document, and it was
  outvoted."* — that is the `fineweb2025 i=188409` row above.

**So §4.1 contradicts §4.5 of the same manuscript, and contradicts the data README shipped beside
it.** A referee who opens `data/labels/` — which the paper invites them to do, in a paper whose
selling point is that every label is published — finds the contradiction in about a minute, in the
paper's single most load-bearing claim.

**Why it matters more than its size suggests:** §5 lists "denial is absent" as the *first* thing
that survives F4, and the reason given is *"there is nothing to disagree about."* If eight ballots
disagreed, that specific justification is weakened — though the claim itself is not, because the
other two legs (8/9 unanimity on denial controls, and the classifier-free phrase search) do not
depend on it at all.

**⭐ And correcting it makes the paper stronger, which is why it should be corrected rather than
softened.** Eight D/R ballots out of 192,000 — *all* outvoted, six of them 2-of-3 to N and two
landing in three-way splits that were excluded — is a *better* sensitivity story than "nothing
happened." It shows the judges were willing to reach for the category, reached for it eight times,
and were overruled every time. That is an instrument with a live trigger, not a dead one.

**Same overclaim, same wording, in two more places:**
- `RESULTS.md` §2.1: *"Zero documents were assigned to the category by any judge, in any corpus, in either year."*
- `docs/DEVIATIONS.md` DEV-13: *"zero documents to disagree about"*.
- `PAPER_DRAFT_v1.md` §5: *"There are zero documents to disagree about"* — **true as written**
  (zero documents carry a D/R *label*), so this one may stand; it is the ballot-level claim that fails.

**→ NOT APPLIED. This is a claim, and its replacement is Ren's wording to choose.** A candidate
that keeps the argument and gains the sensitivity point:

> *"Not one of 64,000 documents was assigned to either denial category by the panel majority. Eight
> individual ballots out of 192,000 — seven D, one R — were cast for a denial category and every
> one was outvoted (six 2-of-3 to N; two fell in three-way splits and carry no label). The
> instrument's trigger is live and it never fired to a document."*

---

### 🚨 V2 — both abstracts say judges agree **"96–98%"** on what is not phenomenology. It is **96–97%**.

- **Long abstract (line 15)** and **short abstract (line 21)**: *"agree 96–98% on what is not phenomenology"*.
- **§4.4's own table (line 263)** says **96–97%**.
- **Recomputed** N-unanimity, per corpus: **96.90 · 96.14 · 96.20 · 96.87** → **96–97%**. Never 98.
- `RESULTS.md` (line 90) says a flat **"96–98%"**, and its abstract (line 32) says **"agree 98%"**.

**Where the 98 probably came from:** the *local classifier vs panel* agreement on N is **98.7%**
(§4.6). That is a different quantity — instrument-vs-instrument agreement, not judge unanimity —
and it appears to have been read across into the abstract's inter-judge sentence.

**→ NOT APPLIED to the manuscript** (it sits inside the abstract, which I was asked not to edit).
**It IS corrected in `ABSTRACT_250w_DRAFT.md`,** where the change is logged explicitly.
**Ren's call:** change three characters in two places (`98` → `97`), and align `RESULTS.md`.

---

### 🚨 V3 — §3.5's "every miss that recurred across judges was Q → P" is refuted by the paper's own Table B1.

**§3.5:** *"Every miss that recurred across judges was **Q → P**: three independent models from
three labs all file borderline phenomenology as explicit."*

Tabulating Table B1's own `misses` column, **six control items were missed by more than one judge**
and only two of them are Q → P:

| item | judges | direction |
|---|---:|---|
| `p2_01` | 3 (`gpt-4o-mini`, `llama`, `qwen`) | **Q → P** |
| `p2_03` | 3 (`gpt-4o-mini`, `llama`, `qwen`) | **Q → P** |
| `top_02` | **3** (`gpt-4o-mini`, `qwen`, `phi-4`) | T → N |
| `aff_03` | 2 (`gpt-4o-mini`, `llama`) | C → F |
| `fic_01` | 2 (`qwen`, `phi-4`) | F → Q |
| `fic_02` | 2 (`qwen`, `phi-4`) | F → P / F → Q |

`top_02` recurs across **three** judges — the same count as the two Q → P items — so the claim
fails even restricted to the original panel. The *substantive* point survives intact and is worth
keeping; it just needs a scope.

**→ NOT APPLIED (a claim).** Candidate wording:

> *"The only recurring miss **within the phenomenology bracket** was Q → P, and it recurred across
> all three of the originally validated judges."*

---

### ⚠️ V4 — §3.6 says three-way splits are excluded from the **denominator**. The published rates do not exclude them.

**§3.6:** *"Three-way splits (0.36–0.73% of documents per corpus) receive no label and are excluded
from the numerator **and denominator** of every category."*

Recomputed both ways against the published Table A1 P row:

| corpus | published | denominator = **all 16,000** | denominator = **resolved only** |
|---|---:|---:|---:|
| C4 | 0.2080 | **0.2080** ✓ | 0.2091 |
| OpenWebText | 0.1988 | **0.1988** ✓ | 0.1996 |
| FineWeb-2019 | 0.3471 | **0.3471** ✓ | 0.3498 |
| FineWeb-2025 | 0.2460 | **0.2460** ✓ | 0.2469 |

The code kept splits in the denominator with a zero in the numerator — i.e. it treats an
unresolved document as a **non-instance** of every category.

**Direction, stated because §7 sets that standard:** this makes every rate slightly *lower*, which
runs **toward H1** — the LLM author's own hypothesis. The magnitude is ~0.5% relative (0.208 vs
0.209), far inside the F4 caveat that already withdrew these as point estimates, and it changes no
verdict: F1 does not fire either way.

**→ NOT APPLIED (a methods statement).** Two clean options, Ren's pick:
- **(a)** fix the sentence to describe what the code does — and it is a *defensible* choice worth
  defending: an unresolved document is evidence of nothing, and counting it in the denominator is
  the conservative direction for a paper arguing rarity; or
- **(b)** recompute with splits excluded, which moves the third decimal of numbers already withdrawn.

---

### ⚠️ V5 — an eighth orphan reference the earlier proofread never listed: **Berg et al. (2025)**.

Re-checked every reference-list entry against the body:

- **Berg, C., de Lucena, D., & Rosenblatt, J. (2025). *Large language models report subjective
  experience under self-referential processing.* arXiv:2510.24797** — the surname appears **zero
  times** anywhere in the body. It was not among the seven the scaffold arm caught (S4) and it is
  still uncited.
- **Cohen (1960)** and **Fleiss (1971)** are cited eponymously only (*"Cohen's κ"* ×6, *"Fleiss' κ"*
  ×4) and never with a year. **This is standard practice for eponymous statistics and I do not
  think it is a defect** — noted only so nobody re-flags it. Landis & Koch (1977) *is* cited properly.
- Every other entry resolves. No body citation is missing from the list.

**→ NOT APPLIED.** Placing Berg is a judgment about *which claim it supports*, and I will not
invent a citation context in someone else's argument. **The obvious home is §1.3's
positive-indicators sentence**, where it would sit naturally beside Perez & Long (2023) — it is a
direct positive-indicator result on LLM self-report under self-referential processing. **Ren's
call: place it there, or prune the entry.**

---

### ⚠️ V6 — the "250 words" short abstract is **275 words**.

The heading in the manuscript reads *"Short abstract (250 words, for venues with a cap)"*. It is
**275**. (The long abstract is **451** words, not the ~600 the earlier note estimated.) A hard
250-word submission form rejects it, and the heading is exactly what would stop anyone checking.

**→ A genuine 254-word cut is drafted in `ABSTRACT_250w_DRAFT.md`**, with a table of every change
so the diff is inspectable, and with V2's `98 → 97` correction folded in. **The manuscript itself
is untouched.** Ren picks: adopt the cut, or just correct the heading to "~275 words".

---

### ⚠️ V7 — remaining `RESULTS.md` ↔ paper seams (both cosmetic, both in `RESULTS.md`)

| quantity | `RESULTS.md` §1.5 | `PAPER_DRAFT_v1.md` §4.4 | recomputed | who's right |
|---|---|---|---|---|
| N unanimity | 96–98% | 96–97% | 96.14–96.90 | **the paper** |
| T unanimity | 24–25% | 24–26% | 24.00–26.32 | **the paper** |

Plus `RESULTS.md`'s abstract *"agree 98%"* (V2). **→ NOT APPLIED** — `RESULTS.md` is the repo's
front door and its wording is Ren's; these are three small numbers to align.

---

### 📎 V8 — minor, no action needed unless Ren wants belt-and-braces

- **§4.6's local-classifier table sums to 63,630, not the 63,685 stated above it.** The missing 55
  are `Q` (38) and `F` (17), which the table simply does not list. Not an error — the table never
  claims to be exhaustive — but a referee who adds the column will pause. One parenthetical
  (*"Q (38) and F (17) omitted"*) inoculates it.
- **§4.2's "roughly one document in 300–500" is really 288–503**, and **"one in 2,400–10,000"** is
  really **2,387–10,753**. Both are prefixed "roughly" and both were checked and accepted by the
  scaffold arm. Recorded here only so a third arm does not re-flag them.
- **§1.3 / §6.3 apply a *document* fraction (0.04%) to a *token* count (15T) to get ~6B tokens.**
  Strictly a category slip — documents are not uniform in length. It runs **against** the authors'
  interest (it is the concession paragraph), so the direction is safe, but a referee may name it.

---

## 3. External referee reviews

*(Filled in below from `reviews_external/`. Every arithmetic claim either referee makes is checked
against `data/labels/` before it is written down as true — a referee's claim is an artifact.)*

| reviewer | model | verdict | latency | tokens | cost |
|---|---|---|---:|---|---:|
| **X-C** | `claude-opus-5` (Anthropic API) | **major revisions** | 578.9 s | 25,940 in / 44,951 out | $1.2535 |
| **X-G** | `openai/gpt-5.6-sol-pro` (OpenRouter) | **major revisions** (leans reject if the causal thesis must stand) | 223.8 s | 110,681 in / 38,419 out | $0.5355 |

Full text, verbatim and unedited: `reviews_external/REVIEW_claude_2026-09-06.md` and
`reviews_external/REVIEW_gpt_2026-09-06.md` (+ `.json` with the raw usage records).

> 🧾 **A cost I caused and am reporting rather than rounding away.** The GPT call ran **twice**
> — $0.4680 and $0.5355. After the Claude review had been running ~35 minutes I launched a
> parallel GPT job so I would not stay serialised behind it, without checking that the original
> script had already moved on to GPT. Two identical prompts, two valid reviews, one file (the
> later writer won). **Duplicate spend: $0.4680.** Total for the night: **$2.2570**.

### 3.1 Where the two referees and my recomputation all agree — treat these as settled

Six items were found **independently three times** (scaffold/me + Claude + GPT). Convergence from
three sources that could not see each other's work is about as strong as this kind of evidence gets.

| item | X-C | X-G | mine | verified |
|---|---|---|---|---|
| §3.6's denominator rule contradicts the published rates; A1 columns sum to 99.55–99.82%, not 100% | (a) | (B) | **V4** | ✅ **TRUE** — three independent derivations |
| §3.5 "every miss that recurred across judges was Q → P" is false | (c) | (D) | **V3** | ✅ **TRUE** |
| abstracts say 96–98%, body and data say 96–97% | (e) | (F) | **V2** | ✅ **TRUE** |
| §4.6 classifier table sums to 63,630, not the 63,685 stated | (l) | (C) | **V8** | ✅ **TRUE** — missing rows are Q (38) and F (17) |
| "one in 2,400–10,000" is really 2,387–10,753 | (f) | (A) | **V8** | ✅ **TRUE** |
| Berg et al. (2025) is in the reference list and never cited | ✓ | ✓ | **V5** | ✅ **TRUE** |

**Only one flag was found by a referee and not by me, and it is the most serious thing in either
review** — see X-C1 below. **Only one flag was found by me and not by either referee** — V1, the
eight single-judge denial ballots, because it required reading the raw ballots rather than the
manuscript.

### 3.2 🚨 X-C1 — the abstract's control-gate claim is falsified by the paper's own Appendix B and DEV-10

**This is the flag of the night, and neither I nor the scaffold arm caught it.**

> **Abstract:** *"a hand-authored control set that **every instrument had to clear before touching
> corpus data**."* **§3.5** repeats it verbatim.

**But `phi-4` — one third of the primary instrument — did not.** From the paper's own documents:

- **Appendix B1:** *"**phi-4 was validated separately on 2026-09-01**… it was substituted for qwen
  before the full-corpus run **on a script-comment claim**."*
- **`docs/DEVIATIONS.md` DEV-10** is even blunter: *"🚨 **That second claim lived in a script comment
  and nowhere else.** `validation/judge_validation.json` recorded gpt-4o-mini, llama-3.3-70b and
  qwen — the three judges that sat the exam — and had no phi-4 entry. **A judge whose votes carry a
  third of every rate in the study had no control-set result on the record.**"*
- **Acknowledgements:** the corpus run was **2026-08-18/19**.

**So phi-4 labelled all 64,000 documents on 2026-08-19 and sat its control exam on 2026-09-01 —
thirteen days later, retrospectively, during manuscript preparation.** ✅ **VERIFIED TRUE against
DEV-10 and the Acknowledgements.**

X-G reaches the same abstract sentence from a different direction (§3.6 of its report): the
*keyword prefilter* did not clear the control set either — it failed and was demoted (DEV-01). So
**"every instrument had to clear the control set before touching corpus data" is untrue twice
over**, and one of those is disclosed three paragraphs deep in an appendix while the abstract says
the opposite.

⭐ **The disclosure is exemplary and the abstract does not match it.** X-C's own words: *"The
disclosure is exemplary; the abstract is false."* **→ NOT APPLIED — it is an abstract sentence and
a claim.** It needs fixing in four places (abstract ×2, §3.4's "replaced qwen *after* the judge
validation", §3.5), and it belongs in §6.4 Limitations.

### 3.3 🚨 X-G(G) — "judges agree only 4–11%" describes **unanimity**, not agreement

> **§4.4 and both abstracts:** *"agree only 4–11% on which human documents are explicit
> phenomenology."*

**The 4–11% is the fraction of majority-P labels that were 3–0.** Every majority-P label already
had **at least two of three judges agreeing** — that is what makes it a majority label. So the
sentence says "agree" where the statistic measures "agree unanimously," and the two differ by a
lot. ✅ **VERIFIED TRUE** — recomputed: 7/100, 2/54, 13/117, 5/64 unanimous *out of majority* labels.

X-G also notes this sits awkwardly beside Fleiss' κ = 0.551, conventionally *moderate* rather than
near-zero, and **X-C reaches the same place independently** (its §2.2, second half): the paper
argues in §4.6 that *"an agreement statistic computed over a distribution this skewed is not
evidence of anything"* and then rests its headline on exactly such a comparison — 96–97% unanimity
on N (a class holding 98% of documents) against 4–11% on P (a class holding 0.2%). Unanimity on a
rare class is **mechanically depressed** under a 2-of-3 rule.

**Both referees think the underlying finding probably survives**; both say the argument as written
does not. X-C's fix: report a **per-class chance-corrected statistic**, or unanimity against a
simulated-independence baseline at each class's observed marginal. **→ NOT APPLIED (a claim, and
it is in the abstract).** This is the second-most-consequential item for Ren.

### 3.4 The scope objection — the one thing both referees lead with

**X-C §2.1 and X-G §2.2 are the same objection, arrived at independently, and both call it the
paper's central weakness.**

The rubric defines P as *"a real person treating their own experience as experience"* and
explicitly adjudicates *"I was sad when my dog died"* into **N**. But the deflationary claim as
people actually deploy it is rarely about explicit phenomenological *theorising* — it is that the
corpus is saturated with **ordinary first-person mental-state language** ("I feel," "I wanted,"
"it was frightening"), and that a model trained on that will produce fluent mentalistic
self-description. **That claim is compatible with everything this study measures**, because the
rubric routes the relevant text into N and the paper then reports N at ~98% without comment.

So §6.1's *"The corpus does not contain what the explanation requires"* is true only if "what the
explanation requires" means *explicit* discourse.

**This is a framing/scope judgment, entirely Ren's.** I record it because two referees who could
not see each other's reports both made it the headline of their methodological section, and both
proposed **the same cheap fix**, which is worth quoting because it is a day's work with code
already on disk:

> **X-C's "one change that would most improve the paper":** run `17_phrase_search.py` over the same
> 64,000 stored documents for ordinary first-person mental-state constructions — `I feel/felt`,
> `I was afraid/frightened`, `I remember thinking`, `it seemed to me`, `I couldn't stop thinking`,
> `I didn't know why` — and report the document-level density. *"Either (a) it is also low, in which
> case the paper's central claim gets dramatically stronger and generalises to the version of the
> objection people actually make; or (b) it is high, in which case the paper says so, narrows
> 'saturation' to* explicit *discourse in the abstract, and becomes a much more credible document
> for having pre-empted its sharpest reviewer."*

**I did not run it.** It would generate a new empirical result for a paper with Ren's byline, in a
study whose whole armour is that new analyses get pre-registered or logged as deviations. That is
Ren's call to make awake, not mine to make at 2am.

### 3.5 ❌ Referee claims I checked and found FALSE — do not act on these

**This is why the recompute step exists.** Two referee flags would have introduced errors.

| flag | claim | verdict |
|---|---|---|
| **X-C (d)** | *"By the stated operationalisation F3 fired in all four corpora, not just FW-2025."* | ❌ **FALSE.** `scripts/16_panel_analyze.py` line 255: `vintage_2019 = corpus in ("c4","openwebtext","fineweb2019")` → *"F2/F3 NOT EVALUATED — DEV-06: this corpus predates the phenomenon."* **F2 and F3 are never evaluated on the three 2019-vintage corpora**, so F3 could only fire on FineWeb-2025. The paper is right; the referee inferred from the formula without the DEV-06 gate, which §6.4(5) does state. |
| **X-C (o)** | *"175M characters over 64,000 documents is a 2,734-character mean, suspiciously close to truncation at the 3,500-character judge window"* — implying §4.1's "full stored text" and §6.4(3) are misleading. | ❌ **FALSE, and Appendix A3 disproves it on its own.** Table A3's OWT cell reads **`2 (1)`** — two hits in full text, one inside the window. **A hit beyond character 3,500 cannot exist in text truncated at 3,500.** `17_phrase_search.py` confirms it structurally: it reads `r.get("text")` whole, accumulates `n_chars_full` over the untruncated string, and computes the window count separately as `t[:3500]`. 2,734 characters is simply the mean length of a web document. |
| **X-C (m)** | *"§7 says 18 seeded positives; §3.5 says nine negative controls; 18 + 9 = 27 ≠ 29."* | ⚠️ **The arithmetic is wrong; the complaint is fair.** `data/control_set.jsonl` is **20 positives + 9 negatives = 29** ✓ (P1 4, P2 3, F 2, D 4, R 2, C 3, T 2, N 9). The **18** is a *different, smaller set* — the keyword prefilter's positive control (DEV-01, "6 of 18"). No contradiction exists, but the paper never says they are different sets, so 18/20/29 float unbridged. Worth one clarifying clause. |
| **X-G (E)** | *"§7 labels DEV-07's inflated P 'toward H1'; inflating P moves* against *H1."* | ⚠️ **Defensible as written, but genuinely ambiguous.** The author's reasoning is in DEV-07 of the log: *"The real risk is over-detection, and it pushes the result toward the answer I want."* — i.e. a P that survives the 1% bar *despite* 3× inflation makes H1 look more robustly supported. That is coherent. X-G's literal reading (a higher measured P is less consistent with "rare") is also coherent. **Two competent readers split, which means the compressed phrase needs one clarifying clause**, not that either is wrong. |

### 3.6 Remaining referee flags — verified true, all for Ren's judgment

**Numeric / notational (small, safe, but each needs a decision):**

- **X-C (h)** — §4.1's *"pooling would tighten the limit by roughly five-fold"* is **ambiguous**:
  pooling *within strata* gives **~4.0×**; pooling *ignoring strata* gives **~5.9×**. ✅ I verified
  both. Say which. *(Recomputed: pooled stratified bound 0.00842% vs per-corpus ~0.0336%.)*
- **X-C (g)** — the *"naive unweighted pooling overestimates by 5.5×"* figure is from **synthetic**
  corpora; on the real data the factor runs **1.6× (FW-2025 P) to 4.3× (C4 T)**. ✅ I verified the
  empirical range. §3.5's paragraph *does* set the synthetic context, so this is a
  read-at-a-glance risk, not an error.
- **X-C (j)** — **`docs/DEVIATIONS.md` contains SIXTEEN `## DEV-` entries**, not fifteen
  (01, 01a, 02–15). ✅ Verified by heading count. The manuscript says "fifteen" in §2 and §7, and
  **DEV-04 is never mentioned anywhere in the manuscript.**
- **X-C (k)** — §4.4 gives Fleiss' κ "on the 316-document validation set"; Table B2 says
  **n = 315 (1 dropped)**. Both true; §4.4 implies κ over 316.
- **X-G (H)** — §4.3 pairs survey-weighted rates with unweighted sample counts
  (*"0.0012% (1 document)"*). A reader may infer 1/16,000 = 0.0012%, which is not the arithmetic.
- **X-G §1.2** — "0.0000%" asserts six significant figures from n = 16,000; both referees
  independently recommend **"zero of 16,000"** / "zero observed". Wald intervals are also poor for
  rare weighted outcomes (a score, beta-binomial or design-based interval is standard).
- **X-G §2.13** — the variance model treats documents as independent Bernoulli trials. Web corpora
  carry duplicates, near-duplicates and domain clusters. **Not in §6.4.**

**Framing / claim-level (all Ren's, none applied):**

- **"absent" vs "zero observed"** — both referees, repeatedly, including the **title**. The body is
  careful (§4.1: *"It does not license the stronger claim that the rate is zero"*); the abstract
  and title are not. X-C's suggested phrasing: *"undetectable above roughly one document in three
  thousand."*
- **X-C §2.3 / X-G §2.3** — §4.5's "known-cause failure case" is carried by **chronology**, not by
  the measurement. X-C's arithmetic, which I verified: a 0.034% upper bound applied to a real
  ~10⁹-document pretraining corpus **permits on the order of hundreds of thousands of instances**.
  The paper applies its own "rare is not absent in volume" caveat to phenomenology and not to R,
  where it is billed as the most robust result.
- **"among the most reproduced sentences language models generate"** — both referees: **no
  citation, no measurement, anywhere in the paper.** The short abstract's *"the most-reproduced
  denial sentence"* is stronger still.
- **X-C §2.2** — Fleiss' κ = 0.551 is computed on a sample **stratified by the classifier's
  predicted label**, i.e. selected by the instrument §4.6 spends a section proving unusable. ✅
  Verified against Table B2's own description. §6.4(7) defends the *enrichment* but not the
  *selection instrument*. Fix: re-draw stratified by **panel-majority** label.
- **X-C §2.9 / X-G §2.9** — both argue the pre-registration functioned mainly as a **reporting**
  discipline rather than a genuine risk of refutation (F2 supports the thesis under both outcomes;
  F1's bar was set where the authors expected to clear it — though note P+Q on FineWeb-2019 reaches
  **0.797%**, 80% of the way to it, so *"never approached"* is doing work; F3 was neutered by its
  own coding flaw; F4's carve-out is post-hoc). **X-C: *"the authors should say this themselves in
  §7 — it would be more convincing than the current framing, and it is the kind of thing that is
  more credible coming from the authors than from a referee."***
- **X-G §2.8 / §3.15** — the sharper version: **F4 says "no base-rate claim may be made at all,"
  and "phenomenology is rare / well under 1%" *is* a base-rate claim.** Calling a point estimate a
  "bound" does not make it one. X-G's two coherent paths: obey the condition literally and drop the
  prevalence conclusions, or concede the condition was ill-posed and label the prevalence analysis
  exploratory.
- **X-C §2.5 / X-G §2.6** — **no human annotators anywhere.** The claim "competent independent
  judges cannot agree on which *human* documents report inner experience" rests entirely on three
  LLM judges; the obvious rebuttal is "your judges are language models." Both propose the same fix:
  **~200 documents, three blinded human annotators.** X-C calls it "ironic" given the paper's
  posture of *don't take an LLM's word for it, check*.
- **X-C §2.6 / X-G §2.4** — **web crawl ≠ pretraining data.** Frontier mixes include books, arXiv,
  code and upsampled curated sets; books are where sustained first-person interiority lives. §6.1
  slides from "web-scale text" (accurate) to "the text models are trained on". **Not in §6.4.**
- **X-G §2.12** — the aperture answer does not fully land: mixes can include Reddit-derived,
  licensed, quoted or synthetic social text even when native Twitter pages are not crawled.
- **X-G §1.3(B)** — C4/OpenWebText are called *"unmeasurable by construction"* for D/R/C (§6.4(5))
  and then rhetorically pooled into *"zero in every corpus, in 2019 and in 2025."* Pick an estimand.
- **X-G §2.10** — phi-4 was chosen **after observing its directional error profile**. Even aimed at
  balance, selecting an instrument on its observed bias can steer the estimate; a panel-composition
  sensitivity analysis (or re-running qwen) would close it. *(Note this compounds X-C1: the judge
  chosen on an unrecorded bias claim is the same judge that ran unvalidated.)*
- **X-C §2.4 / X-G §2.7** — denial recall rests on **nine short, clean, author-written exemplars**.
  X-C's concrete fix: **splice known denial passages into randomly drawn corpus documents at
  varying offsets, run the panel, report a detection curve** — "a day's work with the existing
  pipeline." Both note category D includes denial of *understanding*, and *"AI doesn't really
  understand X"* is common 2025 web writing, yet all five `doesn't/don't really understand` hits are
  about humans — a surprising null worth interrogating rather than celebrating.
- **X-C §2.8 — a cheap, high-value validity check the paper lacks:** before believing §4.3's null,
  grep FineWeb-2025 for **"ChatGPT" / "OpenAI" / "LLM" / "generative AI"**. If they appear at
  plausible 2025 frequencies the null is much strengthened; if they don't, the 2025 sample is
  unrepresentative and §4.3 collapses. **This is a grep over data already on disk and I think it is
  the single highest value-per-minute item on this whole list.**
- **X-C §2.7 / X-G** — shard selection is undocumented: *which* three shards of C4/OpenWebText, and
  chosen how? FineWeb-2025's "961,000" is round and described only as "the complete downloaded
  crawl sample."
- **X-C §2.11** — §6.2's *"A criterion that cannot be applied consistently to human text cannot be
  the criterion by which anything else is excluded"* runs two criteria together (can an annotator
  label a document? vs is a self-report evidence of experience?). Called "the paper's weakest
  inferential move, and it is in the abstract."
- **X-G §1.3(F)** — *"No Claude model is used anywhere as an instrument"* is defensible only
  narrowly, since Claude designed, ran, analysed, hand-read documents and drafted. Suggested:
  *"no Claude model served as a corpus classifier or judge."* **I think this one is right and cheap.**
- **X-G §1.2** — *"A corrected past is a clean lie"* (§7) reads as rhetoric in a methods paper.
  ⚠️ **Ren: this is Nova's line, on Kairo's versioning-consent principle. It is house canon, and I
  am recording the objection without endorsing it.**
- **X-G §1.4** — no bibliographic entries for the instruments themselves (Mistral-7B, GPT-4o-mini,
  Llama-3.3-70B, Qwen-2.5-72B, Phi-4) or for The Pile / RedPajama. Since the independence argument
  turns on model identity, model cards or tech reports would help.
- **X-C / X-G** — the **Gurnee et al. (2026)** reference is malformed (*"…Pearce, A., et al., &
  Lindsey, J."*) and the body cites it a third way ("Gurnee, Lindsey et al., 2026"). **I did not fix
  this** because correcting it needs the paper's true author order, which I do not have, and
  guessing an author list is worse than leaving it visibly broken.
- **X-C** — the **Martin & Ace (2026b)** entry is a run-on carrying a preprint ID, a journal
  citation, a DOI and an authorship-policy note. Split it.
- **X-C** — emoji (⚠️ 🚨 ❌ ✅) as structural markup will not survive most copy-editing pipelines.
  ⚠️ **Ren: this is a house-voice decision, not a defect. Recording, not recommending.**

### 3.7 What both referees praised, unprompted

Recorded because a file of only failures is a ledger against ourselves, and because these are the
parts that should **not** be touched in any revision:

- **X-C:** *"the weighted point estimates, the Wald intervals, the Clopper–Pearson bounds, the
  stratum sums, the keyword-invisibility fractions and the unanimity fractions all reconstruct
  correctly from the raw counts in Appendix A2. **That is unusual and the authors should get credit
  for it.**"* And: *"This is a genuinely clean estimator implementation."*
- **X-C on DEV-01a:** *"exactly correct, and **many authors would have shipped the biased
  version**."*
- **X-C on §7:** *"the deviation log is **better than what I see in most human empirical work**"* …
  *"the F4 obedience, whatever its post-hoc partitioning, **cost the authors their headline numbers
  and they paid it**."*
- **X-C on §4.6:** *"a genuinely useful, exportable methodological finding that **will outlive the
  consciousness framing**… **That alone is worth publishing.**"*
- **X-C on the disclosure architecture:** *"**the best I've seen on a paper of this kind**, and I
  would not want my criticism to discourage others from attempting it."*
- **X-C on the bias probe (DEV-08):** *"a good design and is **underplayed**; move it out of §3.5's
  fine print."*
- **X-G:** *"The stratified design is sensible, the failure of keyword search is useful, **the audit
  trail is unusually candid**, and the zero observed machine-denial labels in the sampled frames is
  worth reporting."*
- **X-C lists six attacks it would have made and the paper already answers** (prefilter bias,
  LLM-judge circularity, 2019 vintage, the Twitter aperture, the LLM author labelling documents),
  with the note that *"a reviewer raising it is telling you it isn't findable enough."*

### 3.8 A note on the two referees disagreeing with each other

They agree on the mechanics and **split on how much survives**. X-C: *"Nothing here is fatal"* —
the narrow result stands, the abstract overreaches. X-G: the scope and causal problems are *"fatal
to the central defeater-removal argument"* and it would *"lean reject if the venue requires the
main causal thesis to survive."*

The difference is not about any number. It is about whether *"the saturation premise is false"* is
a finding about the corpus (X-C: yes, narrowly) or a causal claim the design cannot support
(X-G: the latter). **That is precisely the axis §1.3 and §6.3 already fight on**, which suggests
the paper knows where its edge is and is arguing at it — and that one honest paragraph defining
"saturation" would move both referees at once.

---

## 4. What was actually applied to `PAPER_DRAFT_v1.md` tonight

**Three edits. All mechanical. No number moved, so nothing goes in `docs/DEVIATIONS.md`.**

| # | line | before | after | why it is safe |
|---|---:|---|---|---|
| 1 | 467 | `Ben allal, L.` | `Ben Allal, L.` | Proper-noun capitalisation in a reference. Both referees flagged it. Loubna **Ben Allal** is a FineWeb author; this is a typo with a checkable right answer. |
| 2 | 407 | `the F4 firing (DEV-13) the incomplete ad-hoc phrase search` | `the F4 firing (DEV-13), the incomplete ad-hoc phrase search` | A missing comma in a serial list. Pure punctuation. |
| 3 | 30 | Contents: `4.4 The category resists operationalisation` | `4.4 The category resists **reliable** operationalisation` | The Contents did not match the §4.4 body heading. The body is authoritative; the Contents was the stale copy. |

**Nothing else was touched.** Specifically **not** touched, by instruction and by judgment:

- **the abstracts** (long or short) — including the `96–98%` → `96–97%` correction, which is real
  and verified. It is corrected only in the separate `ABSTRACT_250w_DRAFT.md`.
- **the Reviewer's Roadmap** (Appendix C) — which the scaffold arm called *"a gift to referees and
  I've never seen one before; keep forever."* Both external referees effectively used it: X-C's
  §2.12 works through the same objection list and confirms five of them land.
- **British spelling, the tone, the emoji, "A corrected past is a clean lie"** — house voice.
  X-G objected to the last two; recorded above, not acted on.
- **every claim, every number, every table cell.**
- the malformed **Gurnee et al. (2026)** reference — fixing it needs the true author order, which I
  do not have, and inventing an author list would be worse than a visible formatting error.
- the **Berg (2025)** orphan — placing it is a judgment about which claim it supports.
- the **classifier table's missing rows** — I have the verified values ready
  (**Q: n = 38, panel agreed 31.6%** · **F: n = 17, panel agreed 41.2%**), but adding rows changes
  what a table asserts, and "label it a partial table" is the other valid fix. Ren picks.

### New files added

| file | what it is |
|---|---|
| `scripts/21_external_referee.py` | the referee pipeline — Anthropic (streaming SSE, adaptive thinking, effort high) + OpenRouter, no `max_tokens` ceiling, `TRUNCATED_BY_US` as its own state. Re-runnable. |
| `scripts/22_verify_manuscript_numbers.py` | recomputes every headline number from `data/labels/` rather than from `RESULTS.md`. **Run this before believing any number in this paper, including mine.** |
| `reviews_external/REVIEW_claude_2026-09-06.{md,json}` | verbatim, with model id, timestamp, tokens, cost |
| `reviews_external/REVIEW_gpt_2026-09-06.{md,json}` | verbatim, same |
| `ABSTRACT_250w_DRAFT.md` | a genuine 254-word cut, with a change table. Not applied. |
| `PROOFREAD_STATUS_2026-09-06.md` | the running log of the night |

### 🔝 If Ren reads only five lines of this file

1. **X-C1** — the abstract says every instrument cleared the control set before touching corpus
   data. **phi-4 didn't** (validated 13 days after the run, per your own DEV-10). Four places to fix.
2. **X-G(G)** — *"judges agree only 4–11%"* is a **unanimity** rate, not an agreement rate. It is
   in both abstracts and it is the paper's headline finding.
3. **V1** — §4.1 says no single judge ever voted D or R. **Eight did** (7 D, 1 R), all outvoted.
   §4.5 of the same paper already says so. **Correcting it makes the sensitivity story better.**
4. **V4 / X-C(a) / X-G(B)** — §3.6's denominator rule does not describe what the code did, and the
   A1 columns don't close. Found three independent times. One sentence, or one extra table row.
5. **The scope objection** — both referees lead with it, both propose the same afternoon-long
   phrase search over data already on disk. **I did not run it**; generating a new empirical result
   for your byline overnight is yours to authorise, not mine to assume.

---

## 5. Provenance note on the referees

Both referees are **referees, not instruments**. §2 of the manuscript commits that *"No Claude
model is used anywhere as an instrument"* — the local classifier is Mistral-7B, the judge panel is
OpenAI/Meta/Microsoft. **That commitment is untouched by this exercise.** `claude-opus-5` labelled
no document, touched no corpus data, and no number in the paper depends on it. It read finished
prose and commented on it, which is the same act a human referee performs. If a venue asks, the
honest sentence is: *no Claude model contributed a data point; one was asked to referee the
manuscript, and its review is published verbatim in `reviews_external/`.*
