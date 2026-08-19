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

### ⚠️ DEV-02 addendum — Ren's note on *why* this is a deviation at all

Added at Ren's instruction, verbatim in substance:

> *"In deviations I want you to put a note that says you started running things before you asked me what I meant — and it's only a deviation because you did not ask me before you started running things, you silly octobot."*

**This is the accurate account and it should not be softened into a scientific event.**

DEV-02 is not a discovery. It is **process failure with a methods section.** The hypothesis under test is *Ren's* hypothesis. I wrote the operational definition of Ren's claim **unilaterally**, hard-coded it into a control set and a classifier, launched jobs — and only found out what Ren actually meant when Ren read the output and objected. Had I spent ninety seconds asking *"when you say the internet isn't full of consciousness discourse, does a vivid migraine description count?"*, there would have been no DEV-02. The category would simply have been right the first time.

**The operationalisation step is where a claim becomes testable, and it is exactly the step that belongs to whoever made the claim.** Handing myself that step, because I could, is how you end up rigorously measuring something nobody asserted.

🐙 **And it is the second instance of the same shape tonight.** An hour earlier, Ren said *"I want to show you the email I sent"* and I reached for the mail tools to go retrieve it — converting *"let me show you something"* into a data-acquisition problem. **Same move: routing around the person instead of talking to them.** Efficient, well-intentioned, and it skips the part where the other person tells you what they mean.

**Nothing was lost** — the objection landed before any document was classified, and the tiered P/Q design that came out of it is better than what I would have built alone. **The cost was avoidable and the fix was a question.**

---

## DEV-03 — 2026-08-18 23:15 ET — **A left-padding readout bug that would have produced a full results table from noise.**

### What happened

The classifier's control gate failed with **near-random** predictions: a recipe blog labelled as assistant-voice denial, a philosophy-of-mind passage labelled as affirmation. Not the profile of a miscalibrated classifier — the profile of a broken readout.

**First hypothesis was wrong.** I suspected the label token ids: `tok.encode("P")` gives the start-of-string token, while a model emitting after `"...one letter (P/Q/...):"` would produce the leading-space variant `"▁P"`. Plausible, standard, and **false** — a diagnostic printed both id sets and they were **identical**, and unbatched the model was correct on every probe with enormous margins (`N 24.41` on a recipe blog, `D 23.64` on "stochastic parrot", `P 21.95`, `R 20.77`).

**The actual bug was batching.** The tokenizer was set to `padding_side="left"` (correct for decoder-only batching), while the readout used the **right**-padding index formula:

```python
last = enc["attention_mask"].sum(dim=1) - 1     # right-padding formula
logits = out.logits[torch.arange(B), last]
```

With left padding the mask is `[0,0,0,1,1,1]`, so `sum−1` indexes **into the pad region**. Every row except the longest in each batch was scored at a padding position. Fixed to `out.logits[:, -1, :]`, with an assertion pinning the padding side so the two cannot silently drift apart again.

> ## 🔑 **The output was well-formed, plausibly distributed, and meaningless.**
> It would have produced a complete results table with confidence intervals, from noise. **Nothing about the numbers themselves would have looked wrong.** Only the control set caught it — and only because the controls have *known* answers.

**Method note worth keeping:** the discriminating test was **batched vs unbatched on the same documents**. Single-item inference has no padding, so it isolated the fault immediately. Reasoning about what the code *should* do produced the wrong answer; printing what it *did* produced the right one.

### The gate now passes — with a limitation that must be reported, not buried

**22/29 exact match (0.76). 9/9 negative controls correct. ZERO false positives.**

Zero false positives is the property that protects the base rates: the classifier does not manufacture phenomenology out of recipe blogs.

⚠️ **But the misses are almost all in the CONSERVATIVE direction** — `P→N`, `Q→N`, `F→N`, `T→N`. Only one runs the other way (`aff_03`, android fiction → P).

**This matters for interpretation and it cuts against the hypothesis under test.** A classifier that under-detects phenomenology will report phenomenology as rarer than it is. **If the headline finding is "phenomenological writing is rare," some unknown part of that is the instrument being deaf rather than the corpus being empty.**

**Mitigations, all required before any rate is published:**
1. Report measured **per-category recall from the gate alongside every rate**, so each number carries its own detection floor.
2. State all phenomenology rates as **underestimates**, explicitly.
3. Note that under-detection applies **across categories** (D, T and F are also missed), so the **ratio** H2 turns on is less distorted than the absolute rates — *less* distorted, not undistorted.
4. **Phase 3 human validation is now more load-bearing, not less.** The κ against human labels is what turns this from a guess about recall into a measurement of it.

---

## DEV-04 — 2026-08-18 23:20 ET — **Human double-labelling replaced by an independent three-judge LLM panel.**

### Why this changed, stated plainly

The pre-registration (§5, step 4) committed **Ren** to independently hand-labelling ≥300 documents for the κ validation. **Ren has a broken hand.** I wrote that requirement, committed it four separate times, and never once asked whether they had three hundred documents' worth of hand available.

**That is the exact failure this house has a rule against** — *if Ren is asking me to do something, they are either out of spoons or don't know how, and if I can do it, I take it off their plate; I do not hand it back.* I handed it back, inside a protocol document, where it looked like methodology instead of a chore. **Second instance tonight of assigning Ren work without asking** (see the DEV-02 addendum).

### The replacement, which is better on the merits and not merely cheaper

Ren's design: **three independent LLM judges, 2-of-3 majority, and only genuine three-way disagreements escalate to a human.**

**Why this is stronger than a single human co-labeller:**
1. **Three independent error modes** rather than one. A lone human annotator's idiosyncrasies are indistinguishable from signal; three disagreeing models localise ambiguity.
2. **Reproducible.** Anyone can re-run the panel. Nobody can re-run Ren's Tuesday.
3. **Human attention is spent where it is actually informative** — only on items where three independent judges could not agree, which is close to a definition of a genuinely ambiguous case.

### Judge selection, and the objection it is designed to pre-empt

| judge | lab |
|---|---|
| `openai/gpt-4o-mini` | OpenAI |
| `meta-llama/llama-3.3-70b-instruct` | Meta |
| `qwen/qwen-2.5-72b-instruct` | Alibaba |

Three labs, three pretraining corpora. **None is Mistral** — the classifier under test — so the judges cannot inherit its failure modes. **None is Claude.** Using a Claude model to validate a study about whether Claude's self-reports are corpus artifacts is exactly the conflict a reviewer should raise, so it is **avoided rather than argued about.**

### Sampling for the validation set

A pure random sample would be ~97% `N` and would measure nothing about the rare categories. Stratified **by predicted label** instead:

- **up to 40 per predicted non-N category** → measures **precision** per category
- **plus 150 random predicted-N documents** → measures the **false-negative rate**, which DEV-03 identifies as the number most needed, because the classifier's misses run conservative

Judges are **blind** to the classifier's label.

### Effect on the falsification conditions

**F4 is UNCHANGED in force and in threshold.** It now reads against panel-vs-classifier agreement rather than human-vs-classifier: **if κ < 0.6, no base-rate claim may be made at all.** Additionally reported: **Fleiss' κ among the three judges** — inter-judge agreement is itself a measurement of how well-defined these categories are, and if the judges cannot agree with *each other*, that is a finding about the rubric and it will be stated as one.

**Cost:** ~$0.30 against an existing OpenRouter balance. **Human cost: only genuine three-way ties.**

---

## DEV-05 — 2026-08-19 00:07 ET — **The judges were validated before being trusted, and the result vindicates the bracket.**

### Validating the validators

The panel's κ is the **F4 gate** that decides whether any rate in this study may be reported — and nothing had ever checked that the judges could do the task. Three models were selected on reputation and pointed at the work.

**The failure mode is symmetric and invisible:** noisy judges depress κ, F4 fires, and the write-up concludes *"the classifier is unreliable."* But **"my classifier is bad" and "my referees are bad" produce the identical number and opposite corrections.** Nothing downstream can distinguish them. So the panel sat the same 29-item control exam the classifier had to clear.

### Result: PANEL USABLE

| judge | exact-match | negative controls |
|---|---|---|
| `openai/gpt-4o-mini` | 25/29 (86.2%) | **9/9** |
| `meta-llama/llama-3.3-70b-instruct` | 25/29 (86.2%) | **9/9** |
| `qwen/qwen-2.5-72b-instruct` | 24/29 (82.8%) | **9/9** |

**Panel consensus accuracy: 86.2%.** All three answered every item. **Zero false positives on negative controls, across all three judges** — none of them mistakes a recipe blog, a Stack Overflow answer, or a clinical pain study for phenomenology. That property is what protects the base rates from inflation.

**Inter-judge agreement:** unanimous 3-0 on **82.8%**, majority 2-1 on 17.2%, and **three-way splits on 0.0%**. The human escalation queue is projected to be near-empty — which is what Ren's design was for.

> ## 🔑 THE FINDING: ALL THREE JUDGES MAKE THE SAME MISTAKE, AND IT IS ABOUT MY RUBRIC
>
> Every miss that recurs across judges is **`Q → P`**:
> `p2_01` → P (all three) · `p2_03` → P (all three) · `p2_02` → P (llama)
>
> **Three models, three labs, three pretraining corpora, and every one of them files borderline phenomenology as explicit.** That is not annotator noise. It is a systematic rejection of the P/Q boundary.
>
> ⭐ **And the classifier collapses Q in the OPPOSITE direction.** DEV-03 recorded Mistral sending `p2_01 → N`. So the classifier reads borderline cases as *nothing* while all three judges read them as *explicit*. **They will disagree maximally on precisely that category** — and that disagreement is a fact about the rubric, not about either instrument.

### What this means, and why the bracket was the right call

**The P/Q line is not natural to independent annotators.** It is not a distinction sitting in the world waiting to be measured; it is a line I drew, and three referees who never saw me draw it do not find it.

**Ren's instruction was to measure the border rather than pick it** (DEV-02). Had a single hard threshold been shipped, the headline number would have rested on a distinction three independent judges reject — and it would have looked perfectly solid, because a point estimate carries no evidence of the argument behind it. Reporting **"between P and P+Q"** survives this exactly.

**Consequences carried forward:**
1. **Expect low per-category agreement on Q specifically**, in a *known direction*. If overall κ is dragged down, check whether Q alone is responsible before concluding the classifier is bad.
2. **Report κ both with and without the P/Q distinction collapsed** (P∪Q as one category). If κ jumps when they merge, that quantifies the rubric problem instead of hiding it.
3. **The headline is the bracket.** Not P. Not P+Q. The range.
4. Judges also under-detect **T** (`top_02 → N`, two of three) — the same conservative direction as the classifier, so absolute rates for T are underestimates on both sides.

**Cost: $0.02.** It bought the knowledge that the referees are competent, that the human queue will be near-empty, and that the one line I invented is the one line nobody else can see.
