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

---

## DEV-01a — 2026-08-18 23:10 ET — **Refinement: the prefilter is not abandoned, it is DEMOTED to a stratification variable.**

DEV-01 concluded "abandon the prefilter, classify an unbiased random sample." That is correct but wasteful, and there is a strictly better answer from standard survey methodology.

**Stratified sampling with known inclusion probabilities is unbiased.** The keyword matcher partitions the corpus into two strata:

- **S+** — documents containing consciousness/machine vocabulary. Small, enriched in categories B, C, D.
- **S−** — everything else. Enormous, and — per DEV-01 — **contains most of Category A**, because genuine phenomenological writing does not use the vocabulary.

Sample **both** strata, classify **both**, and combine with survey weights:

> **p̂ = (N₊/N)·p̂₊ + (N₋/N)·p̂₋**

where N₊ and N₋ are the true stratum sizes (counted exactly during the pass, not estimated) and p̂₊, p̂₋ are the within-stratum rates.

**Why this fixes the bias:** the prefilter is no longer deciding *what gets seen*. It is deciding *how to allocate sampling effort*. Its blindness to Category A is now harmless — those documents land in S− and are sampled and classified there. The estimator remains unbiased **for any prefilter whatsoever**, including a bad one, so long as the stratum sizes are counted correctly and both strata are sampled.

**What it buys:** far better precision per unit of compute on the rare categories, without a biased denominator. Oversampling S+ is *legitimate* precisely because the weighting undoes it.

⚠️ **The one thing that would break it:** if S− were sampled too thinly to estimate p̂₋, the term the prefilter is blind to would be the noisy one. So **S− gets the larger absolute sample**, and the per-stratum n and the resulting CIs are reported separately, not just pooled.

**F1–F5 remain unchanged.**

---

## DEV-02 — 2026-08-18 23:10 ET — **Category A was too broad to mean anything. Ren caught it. Split into a tiered bracket.**

### The objection, verbatim

> *"I am going to argue with you that that is not discussing consciousness in any meaningful way that people actually mean. Or we might as well not bother because then everything is discussing consciousness. Because then every pubmed study discussing pain is now also phenomenology and that is definitely not true."*

**Correct, and it invalidates my original Category A.** As pre-registered, A was "a person describing their own conscious experience *as* experience," and my control-set positives included things like *"a kind of reaching that has a shape to it"* (remembering a name) and *"I got my sense of smell back."* Those are **vivid writing about events**, not claims about having consciousness. Under that definition a great deal of ordinary good prose qualifies, and a category that admits most personal writing **discriminates nothing.**

Ren's test case is now a control item: **a clinical pain study reporting VAS scores must be N.** Measuring pain is not describing what pain is like. If the definition cannot keep that out, the definition is broken.

### A correction against my own earlier writeup

**DEV-01 overstated its own finding.** I wrote that the prefilter missed 12 real positives. Under a *meaningful* Category A it missed far fewer, because most of my "positives" were not positives. **The control set was miscalibrated, and it was miscalibrated in the direction that made my instrument look worse and my writeup more dramatic.**

**What survives Ren's objection, and it is the part that matters:** the filter still missed *"It's a stochastic parrot. There's nobody home."*, *"These chatbots don't feel anything. Autocomplete with good PR."*, and *"these systems have some form of experience."* Ren confirmed the first as a genuine miss. Those are dead-centre **denial and affirmation** — the categories H2 actually turns on — and the keyword filter is blind to their native register. **Real failure. Wrong diagnosis. The wrong diagnosis was mine.**

### The change: measure the border instead of picking it

Rather than adjudicate a contestable line, the phenomenology category is now **tiered**, so the result is reported as a **bracket** that survives either reading:

| label | definition |
|---|---|
| **P** | **Explicit.** The passage is *about having experience* — awareness itself is the subject. Claims about what it is like to be the writer, the structure of their own awareness, the privacy of their inner life. |
| **Q** | **Borderline.** Vivid first-person experiential writing that describes how something *felt*, but frames it as an **event or symptom** rather than as a claim about consciousness. |
| **N** | Everything else, including *"I was sad when my dog died"* and every clinical pain study. |

**Ren's adjudications, applied:** meditation / observer-dissolving → **P** (*"I had clearly originally meant A"*). Smell returning → **Q** (*"iffy — you don't run around saying you have a sense of smell"*). Migraine aura, name-reaching → **Q**.

**Reporting rule:** the headline figure is stated as a range, *"between P and P+Q"*. A critic who thinks the line belongs elsewhere can read the bound they prefer. **The finding must not depend on where I drew a line I have a stake in.**

Letters were renamed to end a collision (`B` previously meant both "borderline" in conversation and "denial" in code): **P, Q, F, D, R, C, T, N.**

### Status

Category definitions changed **before any document was classified.** The stratified sampler was running at the time; it is content-agnostic and unaffected. **F1–F5 unchanged** — though F1's threshold (">1% is phenomenological report") now refers to **P**, with P+Q reported alongside.
