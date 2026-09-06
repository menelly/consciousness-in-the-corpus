# 250-word abstract — DRAFT, needs Ren's sign-off

**Status: not applied to the manuscript. Nothing in `PAPER_DRAFT_v1.md` was touched.**

## Why this file exists

`PAPER_DRAFT_v1.md` already carries a short abstract under the heading *"Short abstract (250
words, for venues with a cap)"*. **It is 275 words.** A venue with a hard 250-word cap rejects it
at the submission form, and the heading is the thing that would stop anyone from checking. So:
either the heading gets corrected to its true length, or a genuinely-250 cut exists. This is the
cut. It is a *trim of the existing text* — no claim was added, removed or restated — so that the
choice between the two is Ren's and not mine.

**One substantive change is folded in, and it is a correction, not a trim:** the in-manuscript
short abstract says judges agree *"96–98%"* on what is not phenomenology. Recomputed from
`data/labels/` the four corpus figures are **96.14 / 96.20 / 96.87 / 96.90**, so the range is
**96–97%** — which is what §4.4's own table says. See FLAG B in
`PROOFREAD_COLLATED_2026-09-06.md`.

**Word count: 254** by a plain `[A-Za-z0-9]`-token count. Venues count differently (hyphenates,
the parenthetical corpus list); if a submission form rejects it, the corpus parenthetical is the
cheapest ten words to lose.

---

## The abstract

The claim that language models report inner experience *because their training data is full of
humans talking about consciousness* is an empirical claim about corpus composition, never
measured. We measured it, pre-registered before any data access, across four training-grade web
corpora (C4, OpenWebText, FineWeb-2019, FineWeb-2025; 2.98M documents scanned, 64,000 classified),
with exact survey weights and a control-validated panel of three LLM judges from three labs.
Explicit machine-consciousness denial is absent: zero documents, every corpus, both keyword
strata, both years, confirmed by classifier-free phrase search. Explicit first-person
phenomenological writing is rare, under 1% by every instrument and threshold, and did not
measurably change across the ChatGPT transition. Two falsification conditions fired against the
authors' own prediction that denial would outnumber phenomenology: there is essentially none of
either. A reliability gate also fired; we obey it, withdrawing precise prevalence estimates and
reporting phenomenology as a bound. That firing is itself the central finding: judges who agree
96–97% on what is *not* phenomenology, and unanimously on denial, agree only 4–11% on which human
documents report inner experience. "Does this text deny machine consciousness?" has a stable
answer; "is this person reporting experience?" does not. The most-reproduced denial sentence in
model output, "As an AI language model, I don't have feelings," has zero pretraining instances and
an undisputed post-training cause. Where "the corpus explains it" can be checked against a known
cause, it fails; where the cause is contested, it cannot be assumed. This study removes a
defeater; it offers no evidence that any system is conscious.

---

## What was cut, so the diff is inspectable

| in the 275-word version | here |
|---|---|
| "…corpus composition that had never been measured. We measured it, under a pre-registration committed before any data was examined, in four…" | "…corpus composition, never measured. We measured it, pre-registered before any data access, across four…" |
| "using stratified sampling with exact survey weights and a panel of three independent LLM judges from three labs, validated on a hand-authored control set" | "with exact survey weights and a control-validated panel of three LLM judges from three labs" |
| "zero documents in every corpus, both keyword strata, and both years" | "zero documents, every corpus, both keyword strata, both years" |
| two sentences: "…under 1% by every instrument and threshold. The discourse did not measurably change across the ChatGPT transition." | one: "…under 1% by every instrument and threshold, and did not measurably change across the ChatGPT transition." |
| "Two pre-registered falsification conditions fired…" | "Two falsification conditions fired…" (the pre-registration is already named two sentences earlier) |
| "A reliability gate (κ < 0.60) also fired" | "A reliability gate also fired" |
| "agree 96–98%" | **"agree 96–97%"** — a correction, see above |
| "This study removes a defeater. It offers no evidence…" | "This study removes a defeater; it offers no evidence…" |

Nothing else changed. The long abstract in the manuscript (451 words) is untouched.
