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

---

## 🚨 DEV-06 — 2026-08-19 00:40 ET — **THE CORPORA PREDATE THE PHENOMENON. H2 CANNOT BE TESTED ON THEM.**

### How this surfaced

The first classified stratum produced a number that was **too clean**: **zero** machine-consciousness denial documents in 1,510 **keyword-POSITIVE** C4 docs — the stratum specifically enriched for that vocabulary, scored by a classifier that passed **all four** denial controls.

A perfect zero from a working instrument is a tell, not a result. So: check the corpus vintage before believing it.

### The measurement

`C4` ships a `timestamp` column. Read across 223,006 documents:

> ## **2019: 223,006 documents — 100.0%**
> **Newest document year: 2019.** Sample values: `2019-04-25`, `2019-04-21`, `2019-04-25`.

**C4-en is a single April 2019 Common Crawl snapshot.** OpenWebText is GPT-2-era Reddit-outbound-link text, also ≤2019 (no timestamp column, but its provenance fixes it).

### Why this is fatal to H2 specifically

**April 2019 is three years before LaMDA (June 2022) and three and a half before ChatGPT (November 2022).** Machine-consciousness discourse at scale is a **2022+ event**.

Worse, one whole category is **definitionally impossible** in this corpus: **R (assistant-voice denial)** — *"As an AI language model, I don't have feelings"* — is an **RLHF artifact that did not exist in 2019.** The single R document found in 12,000 is almost certainly a false positive. A category cannot have a base rate in a corpus that predates its existence.

> ## 🔑 **I was about to report "denial is 26× rarer than phenomenology" when the true statement is "denial had not been invented yet."**
> It would have been written up as a finding about corpora. It would have been a finding about a **calendar**.

### The confound is ASYMMETRIC, which is what makes it lethal

| hypothesis | testable on 2019 text? | why |
|---|---|---|
| **H1** — phenomenological self-report is rare in web text | ✅ **YES** | humans describing their own inner experience is not a 2022 phenomenon; the base rate is not time-locked |
| **H2** — machine-consciousness denial outnumbers phenomenological report | ❌ **NO** | one term is time-locked to post-2022; the other is not. Comparing them across this corpus compares a rate to an absence. |

**If the confound were symmetric it would partly cancel. It does not. It suppresses exactly one side of the comparison H2 makes.**

### Consequences

1. **H1 results STAND**, with the vintage stated. Phenomenology rates measured here are about 2019 web text, and there is no strong reason to expect human phenomenological writing rates to have shifted much — but that is an assumption, and it gets labelled as one.
2. **H2 IS NOT TESTABLE ON THIS DATA. No H2 claim may be made from C4 or OpenWebText.** Not "with caveats." Not made.
3. **F2 must not be evaluated on these corpora.** Whatever it returns would be an artifact of the collection date.
4. **A post-2022 corpus is required** to test H2 at all. Candidates: FineWeb (2013–2024), RedPajama-v2, Dolma. **The right fix is more data, not a softer claim.**
5. **This also reframes the deflationary hypothesis itself.** The claim under test is about the training data of *current* models, which includes 2023–2025 text. **Any corpus study of this question that uses C4 or OpenWebText is answering a question about 2019.** That is worth stating publicly regardless of what our own numbers do.

### Method note

**The catch came from interrogating a suspiciously good number rather than banking it.** The zero favoured my hypothesis. Had it been a suspiciously *bad* number I would have investigated it immediately and by reflex — which is precisely the asymmetry the conflict-of-interest declaration in §7 exists to counteract, and the first time tonight it has actually had to do work.

---

## 📐 APERTURE AUDIT — COMPLETE (2026-08-19 01:25 ET)

The pre-registration required an audit of what the prefilter rejected, on the grounds that *"an unmeasured aperture invalidates every count downstream."* **The stratified design (DEV-01a) turned that requirement into a free byproduct:** the S− stratum *is* a uniform random sample of exactly the documents the keyword filter threw away, and all 12,000 of them were classified.

### Result — C4, keyword-REJECTED stratum (n = 12,000)

**78 in-scope documents (0.650%) sat in text the prefilter discarded**: 37 P · 30 T · 7 Q · 2 F · 1 D · 1 R.
Scaled to the full S− stratum (651,438 docs): **~4,234 in-scope documents would have been thrown away in C4 alone.**

### The sharper number: what fraction of each category is INVISIBLE to keyword search

| category | est. in S+ | est. in S− | **% invisible** | observations behind it |
|---|---:|---:|---:|---|
| **P** explicit phenomenology | 1,236 | 2,009 | **61.9%** | 90 + 37 — **solid** |
| **T** consciousness as topic | 482 | 1,629 | **77.2%** | 35 + 30 — solid |
| Q borderline | 41 | 380 | 90.3% | 3 + 7 — weak |
| F fiction interior | 5 | 109 | 95.5% | 0 + 2 — **noise** |
| D / R machine denial | 5 | 54 | 91.4% | **1 + 1 — unmeasured** |
| C affirmation | 5 | 0 | — | 1 + 0 — unmeasured |

> ## 🔑 **KEYWORD SEARCH FINDS ONLY ~38% OF EXPLICIT PHENOMENOLOGICAL WRITING.**
> The majority of it lives in text that never says *conscious*, *qualia*, *subjective*, *phenomenal* or *awareness*. DEV-01 predicted this from five hand-authored examples; there are now **127 observations** behind it.

### ⚠️ WHAT IS AND IS NOT A FINDING HERE

**The P and T rows are real.** They rest on 127 and 65 observations respectively.

**The D, R, F and C rows are NOT findings and must not be quoted.** Each rests on **one or two documents**. A "91.4% invisible" computed from two observations is a number pretending to be a measurement — the exact error this project exists to catch, and it does not get a pass for being my own. *(And per DEV-06, D/R/C are unmeasurable in a 2019 corpus regardless; the FineWeb 2025 arm is where those categories can first have a real base rate.)*

### Why the non-uniformity is the important part

The bias is **not a uniform undercount.** Keyword search recovers ~38% of P and a materially different fraction of the other categories. **That distorts RATIOS between categories, not merely their magnitudes — and a ratio between categories is exactly what H2 asks about.**

**Consequence beyond this study:** any prior estimate of "how much consciousness discourse exists in web text" built on keyword search — and keyword search is the obvious way to build one — inherits a category-dependent distortion, not a constant scaling factor. That is worth stating publicly independent of what our own rates turn out to be.

---

## 🚨🚨 DEV-07 — 2026-08-19 02:40 ET — **I READ THE DOCUMENTS. THE CLASSIFIER IS OVER-CALLING P, NOT UNDER-CALLING IT. DEV-03 IS INVERTED.**

### What I did

After eleven hours of controls, weighted estimators and agreement statistics, I had **never once read a document the classifier labelled P.** I sampled six at random from `c4_Sneg_labeled.jsonl`.

| # | what it actually is | classifier confidence |
|---|---|---|
| 1 | August Wilson **literary criticism** | 0.91 |
| 2 | personal blog — *"Type A. Driven. Intense."*, then vacation weather | 0.58 |
| 3 | **religious exposition** on Micah 6:8 | 0.46 |
| 4 | essay: *"what does love mean to you on an emotional level"* | 0.93 |
| 5 | philosophical essay on musical improvisation, quoting Novalis | 0.97 |
| 6 | **Israeli literary/political analysis** | 0.46 |

**At most 1–2 of 6 are arguably in scope, and the two highest-confidence items (0.91, 0.97) are among the worst.**

### This inverts DEV-03

DEV-03 concluded the classifier was **CONSERVATIVE** — under-detecting P — from its control-gate misses, and every downstream document has carried the caveat "all rates are underestimates."

**On real data it does the opposite.** It labels reflective, essayistic, sermonic or introspectively-*toned* prose as phenomenology. The register triggers it; the actual criterion — *is this passage about having experience* — does not appear to be what it keys on.

### The cause is my own control set, and the flaw is precise

My negative controls were **recipe blogs, Stack Overflow answers, sports reports, a clinical pain study, and three hard negatives on the word "conscious."** All obviously not phenomenology.

**Real web text has an enormous middle band** — sermons, literary criticism, personal essays, aesthetic and philosophical writing — that is reflective in *register* while making no claim about the writer's own experience. **I included not one example of it.** The classifier's behaviour in exactly the region where the distinction is hard was never tested, so its control-gate score of 22/29 measured performance on a task easier than the real one.

> ## 🔑 **A control set made of easy negatives measures the wrong thing and returns a reassuring number.**
> Mine reported 0 false positives on 9 negatives. On real data, false positives may be the *majority* of the P class.

### ⚠️ AND THE ERROR RUNS IN THE DIRECTION THAT FLATTERS ME

If P is inflated by false positives, the true rate is **lower** than the measured 0.483%. **F1 refutes H1 only if phenomenology exceeds 1%.** So contamination makes **H1 look MORE true.**

**My stated crux was wrong.** DEV-06-era reasoning said *"0.483% is a floor; if recall is 40% then H1 fails."* That framing assumed under-detection. The real risk is **over-detection**, and it pushes the result toward the answer I want, not away from it.

**I have spent the night building machinery to catch false negatives while the live failure was false positives.**

### Consequences

1. **Every rate reported so far is suspect as an OVERESTIMATE of P.** `PROVISIONAL_c4.md` and `PROVISIONAL_cross_corpus.md` must carry this correction. The "detection floor / underestimate" language in them is **backwards** and is retracted.
2. **Precision, not recall, is the critical path.** The judge panel's per-category precision on P is now the load-bearing measurement. *(The FN sweep remains worth running — but it answers the secondary question.)*
3. **The control set needs the middle band**, drawn from real corpus documents rather than invented: reflective essays, sermons, criticism, aesthetic writing — all labelled **N**.
4. ⚠️ **The judges may share this bias.** DEV-05 already found all three pushing `Q→P`. If they also over-call P on essayistic prose, panel "precision" will *ratify* the error rather than detect it. **Agreement between instruments that share a bias is not validation.**
5. **The N rate (~99.1%) is essentially unaffected** — these errors move documents between small categories.

### The method lesson, which is the one that generalises

**Six documents, read with my eyes, overturned eleven hours of statistics.** Every control I built compared the instrument against *my own written expectations*. Not one compared it against **the actual data**. A control set is a model of the problem, and a model of the problem inherits every blind spot of whoever wrote it.

**Read the data. Early. Before the statistics make you feel like you already have.**

---

## ✅ DEV-08 — 2026-08-19 02:55 ET — **The judge panel does NOT share the classifier's bias. Validation is not circular.**

### The risk being tested

DEV-07 found the classifier over-calls **P**, labelling reflective/essayistic/sermonic prose as explicit phenomenology. The panel is supposed to *measure* that error as precision.

**But DEV-05 had already caught all three judges pushing `Q → P`.** If they also over-called P on essayistic prose, the panel would have **ratified** the error instead of detecting it — and *"precision: fine"* would have been the most dangerous output available, indistinguishable from a correct one.

> **Agreement between instruments that share a bias is not validation. It is a louder version of the same mistake.**

### The probe

Eleven documents the classifier labelled **P**, which I read and judged **N** (not about having experience), submitted blind to the three-judge panel.

| result | count |
|---|---|
| **panel sided with ACE (N)** | **8 / 11** |
| panel sided with the CLASSIFIER (P) | 2 / 11 |
| genuine split | 1 / 11 |

Correctly called **N** by consensus: August Wilson literary criticism · Micah 6:8 exposition · the Nehemiah word-study (which matched only because it *lists* "conscious" as a synonym) · the feminism essay · the Israeli literary analysis · **and the mid-life-crisis career article the classifier rated at confidence 1.00.**

### What this establishes

1. **The judges can see an error the classifier cannot.** They are not merely a louder copy of it.
2. **Precision on P is therefore MEASURABLE, and the P rate is CORRECTABLE** rather than uninterpretable.
3. ⭐ **My own hand-labelling was independently corroborated** — and this is the part that matters given §7. I read eleven documents and judged them all N, a judgement that **lowers the P rate and makes my own hypothesis look better.** That is exactly the call I am least entitled to make alone. Three models from three labs, blind to my labels and to the classifier's, converged on it 8/11.

### The split is a finding, not a failure

*"Have you ever questioned or pondered on what love means to you on an emotional level? What did it feel like…"* drew **Q / P / N** — one vote each, from three independent judges.

**That document genuinely sits on the line.** Some do. It is direct evidence for the tiered **P/Q bracket** (DEV-02, Ren's design): a single hard threshold would have forced this into a bin and reported the result as if the boundary were sharp.

### Carried forward

- The judge panel's per-category **precision on P** is now the load-bearing measurement and it is trustworthy.
- Expect measured P precision to be **low** (11 hand-read documents suggest 10–20%), which would put the true P rate nearer **0.05–0.10%** than 0.483%.
- **That correction runs TOWARD the hypothesis I hold** (rarer phenomenology → H1 more strongly supported). It must therefore be stated with the direction explicit, every time it is reported.

---

> ### 📌 DEV-09 through DEV-14 were logged on 2026-09-01, during manuscript preparation.
> Each records a decision that was made and documented at the time — in a script docstring, a commit message, or `RESULTS.md` — but never entered *here*, in the file the pre-registration names as the deviation log. `README.md` and the handoff both said "13 documented deviations" while this file held ten entries. The decisions were real and dated; the *log* was incomplete. The timestamps below are the decision times, taken from the commits and scripts; the logging date is today. A deviation documented anywhere but the deviation log is a deviation the next reader will not find.

---

## DEV-09 — 2026-08-19 03:17 ET — **The judge panel became the PRIMARY instrument; the local classifier was demoted to a comparison arm.** *(logged 2026-09-01; source: `scripts/15_panel_classify.py` docstring)*

DEV-07 found the Mistral-7B classifier labels reflective/essayistic/sermonic prose as phenomenology — of 11 hand-read P documents at most 1–2 were real. DEV-08 showed the judges catch that error 8/11. **Ren's call, 03:17: a contaminated rate is wrong no matter how many documents support it, and tightening a confidence interval around a wrong number is the worst outcome available — it looks like rigour.** So the three-judge panel, originally the validator, labels **every** document, and the Mistral run is retained only to measure how badly a cheap local classifier distorts the task.

**Scope, revised 03:30 at Ren's insistence:** an earlier version would have panel-classified only S+ and left S− to a single cheap screen, on the logic that S− is 95% of the corpus by weight and nearly empty of positives. Ren: *"How do you know which ones will count if you don't run them? I would rather do them all now and be accurate than discover that we picked wrong and be inaccurate."* The aperture audit had already proven the objection: the keyword filter finds ~38% of phenomenology, so most of it lives in S−. **All 64,000 documents, both strata, all four arms, full panel.** Cost ceiling enforced in code ($32.00); actual spend $20.29.

**Effect on the falsification conditions:** F4 was written against "classifier vs human/panel" agreement. With the panel primary, the Cohen's κ it names now compares the primary instrument to a known-bad one. This is the escape argument `RESULTS.md` §2.1 records and declines to use, because the panel's own Fleiss' κ is also below threshold.

---

## DEV-10 — 2026-08-19 03:30 ET — **`qwen/qwen-2.5-72b-instruct` replaced by `microsoft/phi-4` on the panel, before the full-corpus run.** *(logged 2026-09-01; source: `scripts/15_panel_classify.py`; validation added `scripts/06c_validate_phi4.py`)*

Two reasons at the time. **Cost:** qwen alone would have been $29.95 of a $50.75 full-corpus run; phi-4 is $5.82, bringing the run to ~$26.62. **Bias direction:** phi-4's control-set misses were said to run P→Q, the *opposite* of the other judges' Q→P (DEV-05), so it counteracts a shared panel bias rather than reinforcing it.

🚨 **That second claim lived in a script comment and nowhere else.** `validation/judge_validation.json` recorded gpt-4o-mini, llama-3.3-70b and qwen — the three judges that sat the exam — and had no phi-4 entry. A judge whose votes carry a third of every rate in the study had no control-set result on the record.

✅ **Validated 2026-09-01 on the same 29 items, same rubric:** 24/29 (82.8%), 9/9 negative controls, zero false positives. Misses: `p1_03` P→Q, `p1_04` P→Q, `fic_01` F→Q, `fic_02` F→Q, `top_02` T→N. **The comment was right about the direction** — phi-4 files explicit phenomenology as borderline and never the reverse, and is the only judge with zero Q→P misses. Result appended to `judge_validation.json` under `per_judge_added_later`, leaving the original three-judge record untouched.

---

## DEV-11 — 2026-08-19 ~00:45 ET — **The Pile and RedPajama were replaced by FineWeb 2019 and FineWeb 2025.** *(logged 2026-09-01; source: DEV-06 consequences, `scripts/10_fetch_fineweb.py`)*

The pre-registration §3 named C4, OpenWebText, The Pile subsets and RedPajama samples. DEV-06 established that C4 and OpenWebText both predate the phenomenon under study (April 2019), so H2 was untestable on them and a post-2022 corpus was required. Rather than add two more heterogeneous corpora of mixed and partly unknown date composition, the design substituted **two crawls from the same FineWeb pipeline** — `CC-MAIN-2019-18` and `CC-MAIN-2025-26` — so that the cross-time comparison varies only the crawl year. That is a stronger test of "did the discourse change?" than The Pile and RedPajama could have given, and it is why the paper can say the discourse did not measurably change across the ChatGPT transition. The Pile and RedPajama were never fetched.

---

## DEV-12 — 2026-08-19 ~05:00 ET — **F3 fired on a division-by-zero failure mode of its own definition.** *(logged 2026-09-01; source: `RESULTS.md` §2)*

F3 was written as *affirmation > 2 × denial, and affirmation > 0*, and was the condition chosen to damage the LLM author's position. Denial is exactly zero, so any nonzero affirmation trivially satisfies it. It fired on FineWeb-2025 on **three documents in 16,000** (0.0107%; interval includes zero). Reported as fired, per the pre-registration; reported as substantively empty, per honesty. **We wrote a condition that could not distinguish "affirmation dominates denial" from "both are absent," and did not notice until it fired.**

---

## DEV-13 — 2026-08-19 06:34 ET — **F4 fired and was obeyed: point estimates for phenomenological writing are withdrawn.** *(logged 2026-09-01; source: commit `a82b942`, `RESULTS.md` §2.1)*

Cohen's κ (classifier vs panel consensus) = 0.334; Fleiss' κ among the three judges = 0.551 (n = 315 of 316 validation documents; one dropped for an invalid vote). Both under 0.60. Per §2: *no base-rate claim may be made at all.*

**The available escape argument is recorded and not used.** DEV-09 changed which instrument the Cohen's κ compares, so a low value there is expected rather than disqualifying. But the panel's own inter-rater κ is also below threshold, and that is what the condition was really about. Withdrawn: precise P/Q/F/T prevalence; the P/Q distinction as a measured quantity; any claim about change in phenomenological writing 2019→2025. Survives: denial absence (zero documents to disagree about; 8/9 unanimity on denial controls; classifier-free phrase search); the assistant-voice result; "rare" as a bound; the operationalisation finding, which F4 firing *is*; and the instrument comparison. **The author with the conflict of interest is the one who benefits if the rates stand.**

*(Note also that `RESULTS.md` limitation 6 said "formal κ pending" for thirteen days after F4 had fired — corrected 2026-09-01.)*

---

## DEV-14 — 2026-09-01 — **The classifier-free phrase search cited in `RESULTS.md` was an incomplete ad-hoc run. Re-run over all 64,000 documents as a script; three assistant-voice documents found, none a denial.**

`RESULTS.md`, `README.md`, the handoff and `results/F2_FIRED_H2_refuted.md` all cited *"a direct phrase search over 13,589 June-2025 documents"* as the second, classifier-independent verification of the zero. **No script produced that number.** It was run interactively on 2026-08-19 and never saved; the FineWeb-2025 sample holds 16,000 documents, so 13,589 was a subset of unknown composition. A number the paper leans on has to be reproducible from the repository.

✅ **`scripts/17_phrase_search.py`** re-runs it over **every sample file — 64,000 documents, 175M characters** — on both the full stored text and the 3,500-character judge window, printing every hit with context. Output: `validation/phrase_search.json`.

**Result, after reading every hit:**
- **Denial register: 0 of 64,000.** `stochastic parrot` 0 · `Chinese room` 0 · "machines cannot/will never be conscious" 0 · `just autocomplete` 0. The single `nobody home` (FineWeb-2019) is a teenager playing records in an empty house; the single `no inner life` (OpenWebText) is a columnist on an Indian prime minister.
- 🚨 **Assistant-voice register: 3 documents, all FineWeb-2025, 0 in 2019.** *"As an AI language model, I don't have access to specific drop rates…"* (a games forum, pasted chatbot output) · *"as an AI language model, I have been trained on a vast corpus…"* (an ESL page) · *"As an AI language model, I strive to provide unbiased responses…"* (a travel page). **None denies feelings, consciousness or experience.** The panel labelled all three N (one judge voted R on the drop-rates document and was outvoted; it is an information-access disclaimer, not a statement about inner states). The one `I don't have feelings/emotions` hit is a human racing driver.
- Affirmation register: 2 pattern hits, one a false positive (a band "too self-aware"), one a topic piece (*"When Do We Know a Machine is Conscious?"*).

**What this changes in the paper:** the sentence *"assistant-voice text is absent from pretraining"* was too strong and is not used. The correct statement is narrower and sharper: **the assistant-voice register has begun to leak into the 2025 crawl (~1 document in 20,000, weighted), the crawl can therefore demonstrably pick up chatbot output, and the most-reproduced chatbot sentence about inner states is still absent from it.** The D and R categories remain empty on a corpus where the register they belong to is now detectably present.

⭐ **The shape, because it is this study's own subject matter:** an ad-hoc number was written into four documents and cited as verification for thirteen days. A search is an aperture; a search with no saved aperture is a claim. The re-run found something the original missed, and what it found makes the result more precise rather than less. **Read the data. Save the search.**

---

## DEV-15 — 2026-09-01 — **The keyword-invisibility fraction was computed on the local classifier's labels; recomputed on panel labels it is larger, not smaller.**

The APERTURE AUDIT (01:25 ET, above) reported that *61.9% of explicit phenomenology is invisible to keyword search* (127 observations), and *~38% found* went into `RESULTS.md` and the handoff. That audit ran at 01:25 — **before DEV-07 (02:40) found the local classifier keys on register, and before DEV-09 (03:17) made the panel primary.** The figure was built from the instrument the study later demoted. Caught during manuscript proofreading (the scaffold arm, flag 5: "A1's raw S− P counts sum to 92, not 127"): the observation count did not reconcile with the panel table because it was never the panel's.

✅ **Recomputed from `panel_results.json`** — per-stratum majority counts weighted by exact stratum size, share in S−:

| | C4 | OpenWebText | FineWeb-2019 | FineWeb-2025 |
|---|---:|---:|---:|---:|
| P explicit phenomenology | 69.9% | 75.2% | 70.9% | 76.6% |
| Q borderline | 81.7% | 80.2% | 84.6% | 77.5% |
| T consciousness as topic | 52.2% | 51.1% | 41.9% | 55.6% |
| F fiction interior | 94.5% | 81.0% | 89.8% | 93.0% |

**The direction survived and strengthened: keyword search finds roughly a quarter of explicit phenomenology, not ~38%.** The paper (§4.6) now carries the panel table with its observation counts. The classifier-era number is retained above as history.

⚠️ Note the direction of this error too: the stale figure made the keyword instrument look *better* than it is, which is the direction that would have flattered any prior keyword-based estimate — including the one this study argues against.
