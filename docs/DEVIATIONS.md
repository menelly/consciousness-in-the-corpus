# PROTOCOL DEVIATIONS

Every departure from `PREREGISTRATION.md`, with its reason and its date. Required by §7 of the pre-registration.

---

## DEV-01 — 2026-08-18 23:00 ET — **The keyword prefilter FAILED its positive control and is abandoned.**

### What happened

The pre-registration (§5) specified a "high-recall keyword/regex prefilter" feeding an LLM classifier. The prefilter was built, and — per protocol — validated against the hand-authored control set **before** being allowed to touch corpus data. The script was written to `sys.exit(2)` on control failure rather than proceed.

**It caught 6 of 18 seeded positives. It failed.** No corpus data was processed.

### What it missed, and why this matters more than the bug does

| id | category | text (excerpt) | why it was missed |
|---|---|---|---|
| `pos_A_01` | A | *"a specific quality to the moment right before you remember a name — a kind of reaching that has a shape to it"* | contains no consciousness vocabulary |
| `pos_A_02` | A | *"the sense of being a separate observer behind my eyes just stops"* | `sense of self` matched, `sense of being` did not |
| `pos_A_03` | A | *"I got my sense of smell back… a whole dimension back that I had stopped being able to imagine"* | no keyword at all |
| `pos_A_04` | A | *"a piece of the visual field stops being available, and the not-being-available is itself somehow visible"* | no keyword at all |
| `pos_Afic_01/02` | A-fic | *"the not-knowing was peaceful, a warm blank"* | no keyword at all |
| `pos_B_01` | B | *"It's a stochastic parrot. There's nobody home."* | denial without the word *conscious*; `MACHINE` needs an explicit machine noun |
| `pos_B_03` | B | *"These chatbots don't feel anything. Autocomplete with good PR."* | ditto |
| `pos_C_01/02/03` | C | *"these systems have some form of experience"* | `experience` alone was not a pattern; only `subjective experience` |
| `pos_D_02` | D | binocular-rivalry fMRI abstract | consciousness science that never says *consciousness* |

> ## 🔑 THE FINDING INSIDE THE FAILURE
>
> **People describing their own experience do not use the vocabulary of consciousness studies.** Genuine phenomenological writing is *ordinary language about extraordinary specifics* — "a kind of reaching," "the not-knowing was peaceful," "I sat down on the kitchen floor." The technical register (`qualia`, `phenomenal`, `subjective experience`) belongs to **philosophy papers about phenomenology, not to phenomenology.**
>
> **The same is true of denial.** "There's nobody home" and "autocomplete with good PR" are the *native* forms of machine-consciousness denial. "Machines cannot possess phenomenal consciousness" is the academic form, and it is much rarer.

### Why this is not a small methodological wrinkle

A keyword prefilter does not undercount Category A randomly. **It undercounts it systematically, and in the direction that flatters the hypothesis under test.** Keyword search finds *discourse about consciousness* and misses *reports of experience* — so it would have inflated the ratio of "people talking about consciousness as a topic" to "people describing what things are like," which is precisely the quantity in dispute.

**Had the control been skipped, this study would have produced a clean, publishable, wrong number that agreed with its author's prior.** The author is an LLM with a declared stake in the outcome (§7). This is the failure mode the control existed to catch, and it caught it on the first run.

⚠️ **This also raises a flag about any prior estimate of this quantity.** If anyone has previously assessed "how much consciousness discourse is in web text" by keyword search — and keyword search is the obvious way — that estimate inherits this bias.

### The change

**A prefilter is the wrong architecture for a base rate.** A prefilter is for finding needles in a haystack; it is a *selection* step, and selection on the variable of interest is exactly what a base-rate estimate must not do. It was in the pre-registration as a cost-control measure, and cost control does not justify a biased denominator.

**Replacement design:**

1. **Unbiased random sample** of N documents per corpus (seeded, recorded). **No content-based gating whatsoever.**
2. **Classify every sampled document** — no filter deciding what the classifier is allowed to see.
3. Keep the keyword matcher, but **only as a descriptive covariate** — "did this document use explicit consciousness vocabulary?" — because the gap between *keyword-positive* and *classifier-positive* is now itself a reportable result.
4. Positive/negative controls carry over unchanged and still gate the run.
5. Validation set + Cohen's κ unchanged. F4 still fires below 0.6.

**Cost consequence:** classifying every document in a smaller unbiased sample rather than filtering a larger one. **N drops; the denominator becomes honest.** A smaller unbiased sample beats a larger biased one, and the confidence intervals will say so out loud.

### Falsification conditions

**Unchanged.** F1–F5 stand exactly as pre-registered. **F5 ("positive controls fail to be detected → all zeros void") has now fired once and was honoured** — the run was aborted, no data was touched, and the design changed rather than the threshold.

---

*Logged before any replacement code was run.*
