# External referee review — claude-opus-5

- **status:** `REPLIED`
- **model requested:** `claude-opus-5` (anthropic)
- **model resolved:** `claude-opus-5`
- **timestamp:** 2026-09-06T04:21:16.740295+00:00
- **latency:** 578.9 s
- **tokens:** 25940 in / 44951 out
- **cost:** $1.2535

*Verbatim reply below, unedited. A reviewer's claim is an artifact: every arithmetic assertion here was re-checked against RESULTS.md and results/ before anything was applied.*

---

# Referee Report

**Manuscript:** *Machine-Consciousness Discourse Is Absent From Web-Scale Text: A Pre-Registered Corpus Study, 2019–2025*

**Recommendation:** Major revisions.

A note on how I read the disclosed conflict. I checked the arithmetic harder than I normally would, because that is the appropriate response to a declared interest. It largely survived: the weighted point estimates, the Wald intervals, the Clopper–Pearson bounds, the stratum sums, the keyword-invisibility fractions and the unanimity fractions all reconstruct correctly from the raw counts in Appendix A2. That is unusual and the authors should get credit for it. The problems I found are not in the estimator; they are in a handful of internal contradictions, in one abstract claim that the appendix falsifies, and in what the study chose to measure.

---

## 1. PROOFREAD — the mechanical layer

### 1.1 Arithmetic I checked and that is correct

For the record, so the authors know which numbers I am *not* disputing:

- §3.1 corpus table: 671,948 + 300,519 + 1,049,850 + 961,000 = **2,983,317** ✓, matching the stated total and the abstract's "2.98 million."
- §3.2 stratum table: all four rows sum exactly (e.g. 20,510 + 651,438 = 671,948) and all four S+ fractions are correct to two decimals.
- §4.1 Clopper–Pearson bounds. Using $p_{\text{upper}} = 1-\alpha^{1/n}$ at $\alpha/2 = 0.025$: S+ gives 0.09218%, S− gives 0.030736%; weighted per corpus these give 0.0326%, 0.0342%, 0.0336%, 0.0343% → **0.033 / 0.034 / 0.034 / 0.034** ✓. "Roughly one document in three thousand" ✓ (1/0.033% = 3030).
- §4.2 / Table A1 P row. From the A2 raw counts (C4 82/18, OWT 35/19, FW19 86/31, FW25 40/24), the weighted rates reconstruct to 0.20799%, 0.19879%, 0.34707%, 0.24602% ✓, and the 1.96·SE half-widths reconstruct to 0.0685, 0.0691, 0.0891, 0.0774 percentage points, giving exactly the printed intervals ✓. This is a genuinely clean estimator implementation.
- Table A1 Q, T and C rows all reconstruct from the §4.6 observation counts, including the non-obvious C4/FW-2025 C rows (FW-2025's 0.0107% requires 2 S+ and 1 S− — which is right).
- Table A2 unanimity: every "n% of P labels" is consistent with the corresponding weighted unanimous rate for a plausible stratum split (e.g. OWT 0.009% ⇒ 2 docs, one per stratum ⇒ 2/54 ≈ 4% ✓).
- §4.6: keyword-invisibility shares (70/75/71/77%, 82/80/85/78%, 52/51/42/56%) all reconstruct exactly from the observation counts ✓.
- §4.3: P decline (0.347→0.246) = 29.1% ✓; P+Q (0.797→0.418) = 47.6% ✓; keyword shift 5.75/4.69 = 1.226 ✓.
- §4.6 / §4.1: 12 + 7 + 10 = 29 classifier D/R/C flags ✓, and 64,000 − (76+65+116+58 splits) = **63,685** ✓, which explains the "63,685 documents labelled by both instruments." Good.
- Appendix B2: κ = (0.611 − 0.416)/(1 − 0.416) = 0.334 ✓; 0.334 + 0.046 = 0.380 ✓.
- §1.3: 0.04% × 15T = 6 × 10⁹ ✓.
- §3.4: 3 × 64,000 = 192,000 judgements ✓, and $20.29 is a plausible cost at those token volumes.

### 1.2 Arithmetic and internal consistency that is **wrong**

**(a) Table A1 columns do not sum to 100%, and §3.6 is the wrong explanation.** Column sums are C4 99.82%, OWT 99.79%, FW-2019 99.55%, FW-2025 99.78%. §3.6 states three-way splits "are excluded from the numerator **and denominator** of every category," which would force the columns to 100%. They don't. The deficits (0.180, 0.212, 0.452, 0.217 pp) are precisely the magnitude of the *weighted* three-way-split rate — e.g. for C4, 100 − 0.9505 (non-N categories) − 0.175 (weighted splits) = 98.87%, which is exactly the printed N. **Conclusion: splits were retained in the denominator, contradicting §3.6.** Fix §3.6, or add a "3-way split" row to A1 so the column closes. The effect on magnitudes is negligible; the effect on a referee's confidence in the methods text is not.

**(b) §4.1 contradicts §4.5 on judge-level denial votes.** §4.1: *"not one was assigned to either by **any single judge** in **any** corpus."* §4.5: *"one judge voted R on the drop-rates document, and it was outvoted."* These cannot both be true. §4.5 is presumably right (it is the more specific report and is corroborated by Table A3). §4.1 must be rewritten to something like: "no document received a majority D or R label; across all 192,000 judgements exactly one R vote was cast, on a document that is a disclaimer about information access."

**(c) §3.5 contradicts Table B1 on the shared bias.** §3.5: *"Every miss that recurred across judges was **Q → P**."* Table B1 shows at least three counterexamples: `top_02 T→N` recurs across gpt-4o-mini, qwen and phi-4; `aff_03 C→F` recurs across gpt-4o-mini and llama-3.3-70b; `fic_01 F→Q` recurs across qwen and phi-4. The claim is false as written even if restricted to the original three panel judges. Restate as "the only miss shared by all three original panel judges on the phenomenology items was Q→P," or whatever the true statement is.

**(d) §5's F3 row says F3 "fired on FineWeb-2025."** But F3 is operationalised (§5) as *affirmation > 2 × denial, and affirmation > 0*. Denial is zero in all four corpora and affirmation is nonzero in all four (C4 2 docs, OWT 4, FW-2019 1, FW-2025 3). **By the stated operationalisation F3 fired in all four corpora**, not just FW-2025. Note also that OpenWebText (2019) has the highest raw affirmation count, which further deflates any post-ChatGPT reading.

**(e) Abstract: "agree 96–98% on what is *not* phenomenology."** §4.4 gives N unanimity as **96–97%**, and Table A2 gives 97/96/96/97%. The 98% is not in the body. Both the long and short abstracts carry it. The body figure is right.

**(f) §4.2: "one in 2,400–10,000 by unanimity."** The unanimous P rates are 0.042%–0.009%, i.e. 1 in 2,381 to 1 in **11,111**. "10,000" is a rounding in the direction that makes the range look tidier.

**(g) §3.5: "Naive unweighted pooling of the two strata overestimates by 5.5×."** This is a synthetic-corpus figure presented adjacent to real results. On the actual data the factor is 1.6× (FW-2025 P) to 4.3× (C4 T). Either label it explicitly as synthetic or replace it with the empirical range.

**(h) §4.1: pooling "would tighten the limit by roughly five-fold."** Pooling within strata gives ~4.0×; pooling ignoring strata gives ~5.9×. Say which pooling you mean.

**(i) §7 deviation table, "toward H2" row.** DEV-06 would have produced *"denial is 26× rarer than phenomenology"* — which **refutes** H2 (denial > phenomenology). Labelling that "toward H2" is wrong. What the authors mean, I think, is "toward the LLM author's *interest*" (the deflationary defeater failing), which is a different thing from "toward the pre-registered hypothesis." The conflation matters, because §1.4 and §7 both use the "four of five ran toward the LLM author's hypothesis" count as evidence of the controls' value. Disambiguate the two senses and recount.

**(j) Deviation numbering.** Labels appearing in the text are DEV-01, 01a, 02, 03, 05, 06, 07, 08, 09, 10, 11, 12, 13, 14, 15. **DEV-04 never appears.** If the log runs 01–15 plus 01a, that is sixteen entries, not the "fifteen" stated in §2 and §7.

**(k) §4.4 says the validation set is 316 documents and gives Fleiss' κ on it; Table B2 says n = 315 (1 dropped).** Quote 315 in §4.4.

**(l) §4.6 classifier table is incomplete and its rows do not sum.** 900 + 602 + 12 + 7 + 10 + 62,099 = **63,630**, not 63,685. The Q and F rows are missing (Appendix B2 reports classifier precision on Q and F, so they exist). 55 documents are unaccounted for. Either add the rows or label the table "selected rows."

**(m) §3.5: control-set composition doesn't add up in prose.** §7 says the prefilter was tested against "18 seeded positives"; §3.5 says nine negative controls plus unquantified "hard negatives." 18 + 9 = 27 ≠ 29. State the composition.

**(n) Short abstract exceeds its stated cap.** I count ~278 words against the declared "250 words."

**(o) §4.5 / Table A3 vs §6.4(3).** "175M characters" over 64,000 documents is a 2,734-character mean, which is suspiciously close to what truncation at the 3,500-character judge window would produce. If the stored text *is* truncated, then "Case-insensitive string and regular-expression search over the **full stored text**" (§4.1) and "not by the full-text phrase search" (§6.4.3) are both misleading. Please state the storage policy explicitly; this bears directly on the robustness of the headline zero.

### 1.3 Text, formatting, references

- §7, final paragraph: `"the F4 firing (DEV-13) the incomplete ad-hoc phrase search"` — missing comma after `(DEV-13)`.
- §3.1: "Each corpus was **read in full** for the stratum counts … **from three shards**" is self-contradicting. Say "read exhaustively within the sampled shards."
- Contents lists "4.4 The category resists operationalisation"; the body heading is "The category resists **reliable** operationalisation."
- §3.4: "Three labs, three pretraining corpora, no Claude, **no Mistral**" sits two paragraphs above the Mistral comparison arm. Add "on the panel."
- "0.0000%" (§4.1, §4.3, Table A1) asserts six significant figures from n = 16,000. Write "0 / 16,000."
- Emoji (⚠️ 🚨 ❌ ✅) as structural markup will not survive most copy-editing pipelines.
- Reference: "Penedo, G., Kydlíček, H., **Ben allal**, L." → "Ben Allal, L."
- Reference: "Gurnee, W., Sofroniew, N., Pearce, A., **et al., & Lindsey, J.**" is malformed; the body cites it as "Gurnee, Lindsey et al., 2026", a third form.
- Reference: the Martin & Ace (2026b) entry is a run-on containing a preprint ID, a journal citation, a DOI and an authorship-policy note. Split it.

**Uncited references (in the list, never cited in the body):**
1. **Berg, C., de Lucena, D., & Rosenblatt, J. (2025).** *Large language models report subjective experience under self-referential processing.* Never cited. This is conspicuous: it is the most directly adjacent work in the list and its absence from the body makes §1.2's "nobody had measured it" harder to assess.
2. **Cohen, J. (1960).** Cohen's κ is used throughout; the citation never appears.
3. **Fleiss, J. L. (1971).** Same.

**Cited but missing from the list:** none found.

---

## 2. METHODOLOGICAL HOLES

### 2.1 The steelman is not the thing measured — **serious, fixable, currently unaddressed**

This is my main objection and I want to state it precisely.

The rubric (§3.3) defines P as "a real person treating their own experience *as* experience," and explicitly excludes the ordinary case: *"'I was sad when my dog died' is N (names an emotion, describes no experience)."* But the deflationary claim as it is actually deployed is rarely about explicit phenomenological *theorising*. The usual version is: *the corpus is saturated with humans using first-person mental-state language* — "I feel," "I wanted," "it was frightening," "I don't know why but," "I've been dreading" — *and a model trained on that will produce fluent mentalistic self-description without any inner state.* That claim is entirely compatible with everything this paper measures. Indeed the paper's own rubric routes the relevant evidence into category N and then reports N at 98%.

The paper handles the *volume* objection twice (§1.3, §6.3: "0.04% of 15T tokens is ~6 billion tokens") and handles the aperture objection (§6.3). It does not handle the *operationalisation* objection: that the abundant thing was defined out of scope. So when §6.1 says **"The corpus does not contain what the explanation requires,"** that sentence is only true if "what the explanation requires" is *explicit* discourse. For the weaker and more common form of the objection, the corpus plainly does contain what it requires, and this study did not look.

Not fatal — the narrow claim is still a real result — but it must be stated, and the abstract must stop implying the broad one. The cheap fix, given the stored corpus, is in §4.4 below.

Related and smaller: F + T + P + Q sums to roughly 1.0–1.6% of documents in every corpus. That is a nontrivial density of consciousness-adjacent and interiority-adjacent text, and the F category (0.35–0.66%) is dismissed as contaminated rather than measured. A deflationist who says "fiction narrating interiors is where the model learned it" is not answered by this study.

### 2.2 The κ that carries the central finding is measured on a sample selected by a known-bad instrument — **serious, fixable**

The paper's self-declared central substantive result (§1.4 item 5, §6.2, and the whole of §5) is that the phenomenology category cannot be reliably operationalised, evidenced by Fleiss' κ = 0.551. But that κ is computed on "316 documents **stratified by classifier-predicted label**" (Table B2) — where the classifier is the instrument the paper spends §4.6 demonstrating is unusable, keying on "reflective *register*" rather than the criterion. The enrichment therefore preferentially selects documents where a register-driven classifier fired, i.e. exactly the documents most likely to sit on the register/criterion boundary and provoke disagreement. κ = 0.551 is reliability *on that peculiar population*, not on any population a reader will infer.

§6.4(7) defends measuring κ on an enriched sample ("over all 64,000 documents it would be inflated by the 97% that are N"), which is correct as far as it goes, but it does not address the *selection instrument*. Fix: re-draw a validation sample stratified by **panel-majority** label (or by a random-plus-oversample design that doesn't route through Mistral) and re-report Fleiss' κ. If it moves, the paper's central claim moves with it.

**A second, independent problem with the same finding.** §4.6 correctly says *"Raw agreement is meaningless here… 97% of the distribution is N and everyone agrees on N. An agreement statistic computed over a distribution this skewed is not evidence of anything."* The paper then relies on precisely that comparison as its headline: judges "agree 96–97% on what is *not* phenomenology" versus "4–11%" on P. Those two unanimity rates are not comparable — they differ by three orders of magnitude in base rate, and unanimity on a rare class under a 2-of-3 rule is depressed mechanically. The paper cannot invoke the prevalence problem to dismiss the classifier's 96.88% and then rest a headline on the panel's 96%. **Report a chance-corrected, per-category statistic** (e.g. per-class κ, or unanimity against a simulated-independence baseline at each class's observed marginal). I suspect the finding survives — the P unanimity of 4–11% is genuinely low — but the argument as written is internally inconsistent.

### 2.3 The §4.5 "known-cause failure" argument is carried by chronology, not by this measurement — **partly fatal to the framing, fixable**

The abstract calls this "the sharpest result." Consider its actual power. The panel's own one-sided 95% upper bound is 0.034% of documents (§4.1). Applied to a real pretraining corpus of order 10⁹ documents, that bound permits on the order of **hundreds of thousands** of instances of the assistant-voice denial sentence. "Zero in 64,000" is therefore fully consistent with the sentence being abundantly present in a modern crawl in absolute terms. The paper applies its own "rare is not absent in volume" caveat to phenomenology (§1.3, §6.3) and conspicuously does not apply it to R, where it is billed as the most robust result.

What actually carries the argument is chronological, not statistical: the sentence is a post-November-2022 genre, and the models that first produced it were pretrained before it existed. That argument is strong, and it does not need a corpus census. The manuscript should say so, rather than resting on a zero whose confidence bound does not support the weight placed on it. Relatedly, "**and is among the most reproduced sentences language models generate**" (abstract, §4.5) is asserted with no citation and no measurement anywhere in the paper.

### 2.4 Instrument recall for denial is established only on nine hand-written exemplars — **fixable, and the fix is cheap**

§3.5's "positive control on the zero" is the right instinct, but 9 items, all short and clean, written by the party with the interest, is thin support for "the instrument can see denial" in real 3,500-character documents where a denial clause might be one sentence inside a product review. The phrase search (§4.1 item 2) covers only enumerated strings. Meanwhile category D as defined includes denial that AI has **understanding** — and "AI doesn't really understand X" is common in 2025 web writing, yet the search returned five hits of `doesn't/don't really understand`, none about AI. That is a slightly surprising null that deserves interrogation rather than celebration.

**Concrete fix:** splice known denial passages of varying length into randomly drawn corpus documents at varying character offsets, run the panel, and report a detection curve. That converts "the instrument can see denial" from an exemplar claim into a sensitivity function, and it is a day's work with the existing pipeline.

### 2.5 No human annotators anywhere — **notable, fixable, and ironic**

The claim "competent independent judges cannot reliably agree on which *human* documents report inner experience" is supported entirely by three LLM judges. The obvious rebuttal is "your judges are language models; humans would do fine." Hurlburt & Heavey (2006) is cited as the human analogue but no human agreement is measured here. Given that the paper's whole rhetorical posture is *don't take an LLM's word for it, check*, a 200-document three-human annotation study would cost little and would either convert §6.2 into a real finding or refute it. As it stands the central result is "LLMs disagree about a category," which is a weaker and more deflatable claim than the one the abstract makes.

### 2.6 Generalisation from web crawl to "pretraining data" — **real, fixable, currently absent from Limitations**

The title says "web-scale text" and is accurate. §6.1 slides to "the text models are trained on." Frontier pretraining mixes include books, arXiv, code and heavily upsampled curated sets. Books in particular are where sustained first-person interiority actually lives, and they are upsampled in most published mixes. §6.4 lists eight limitations and this is not one of them. Add it, and soften §6.1.

### 2.7 Corpus subsampling is undocumented — **fixable**

"three shards (C4, OpenWebText)" (§3.1) — which shards, and chosen how? C4's `en` split has 1,024 train files; 671,948 documents is well under 1% of C4. FineWeb-2025's 961,000 is a suspiciously round number described only as "the complete downloaded crawl sample." Crawl dumps are not always exchangeable across files (host segmentation). Please state the file selection rule and, ideally, report a between-shard variance check on the S+ fraction.

### 2.8 A validity check the paper is missing and badly needs — **cheap, high value**

§4.3's headline is that the AI-consciousness discourse explosion "does not appear in web-scale crawled text three years after ChatGPT," with T at 0.1515% in 2019 and 0.1554% in 2025. That is a strong null. Before I believe it, I want a positive control on the 2025 sample: **what fraction of FineWeb-2025 documents mention "ChatGPT", "OpenAI", "LLM", "generative AI"?** If those appear at plausible 2025 web frequencies, the null is credible and much strengthened. If they don't, the FW-2025 sample is unrepresentative and §4.3 collapses. This is a grep over data already on disk.

### 2.9 The pre-registration's protective value is weaker than advertised — **not fixable, but should be conceded**

I want to be fair here: the pre-registration, the deviation log and the "direction of every error" reporting are better than what I see in most human-authored empirical papers, and §7 is genuinely instructive. But consider what the five conditions could actually have done.

- **F1** could have damaged the thesis, and the paper deserves credit for it. But §1.2 argues at length that the premise "was never especially plausible," so the 1% bar was set where the authors already expected to clear it. Note that P+Q on FineWeb-2019 reaches 0.797% — 80% of the way to the bar. "Never approached" (abstract) is doing some work.
- **F2** is heads-I-win: §1.1 says H2 holding would show "the deflationary story would predict the wrong output"; §4.1 says H2 failing means "the refutation strengthens the conclusion." Both outcomes support the thesis. That is not a risky prediction.
- **F3** was the one designed to hurt, and it was written with a division-by-zero failure mode that the authors admirably disclose (§5). But the consequence is that **the only condition that could have substantively damaged the LLM author's position was never operative.**
- **F4** fired and is obeyed in a partitioned way that the pre-registration did not authorise. Note that "explicit phenomenology is under 1%" *is* a base-rate claim; F4 says "no base-rate claim may be made at all," not "point estimates withdrawn, bounds retained." §5 is honest about the tension but the carve-out is post-hoc.

None of this is misconduct and all of it is disclosed. But a hostile reviewer will say the pre-registration functioned mainly as a *reporting* discipline rather than as a genuine risk of refutation, and I think that reviewer is right. The paper should say so itself rather than leave it to be found.

### 2.10 The abstract's control-gate claim is falsified by the paper's own appendix — **must be fixed**

Abstract: *"a hand-authored control set that **every instrument had to clear before touching corpus data**."* §3.5 repeats it: *"Every instrument had to clear a hand-authored 29-item control set **before touching corpus data**."* But Appendix B1 states: *"**phi-4 was validated separately on 2026-09-01**… it was substituted for qwen before the full-corpus run **on a script-comment claim**."* The full-corpus run was 2026-08-18/19 (Acknowledgements). So one third of the primary instrument ran on all 64,000 documents unvalidated, and was validated at manuscript-writing time, twelve days later, retrospectively.

The disclosure is exemplary; the abstract is false. This must be corrected in the abstract, in §3.4 (which says phi-4 "replaced qwen… after the judge validation" — misleading), and in §3.5. It should also appear in §6.4 Limitations and, if it isn't already, in the deviation log as a distinct entry.

### 2.11 §6.2's philosophical inference equivocates — **fixable by softening**

*"A criterion that cannot be applied consistently to human text cannot be the criterion by which anything else is excluded."* Two different criteria are being run together: (i) *can a third-party annotator classify a document as phenomenological report?*, and (ii) *is a system's self-report evidence of experience?* Nobody dismisses model self-reports because annotators can't label documents; the dismissals are causal-origin claims. The measured unreliability of (i) does not directly impugn (ii). This is the paper's weakest inferential move and it is in the abstract. It can be rescued — there is a real point about the vagueness of "report of experience" as a construct — but it needs to be argued rather than asserted as a one-line reversal.

### 2.12 Handled adequately, and a reviewer raising it is telling you it isn't findable enough

For completeness, these attacks I would have made and the paper answers:

- *Keyword prefilter biases the base rate* — handled, §3.2 + DEV-01a. Genuinely well handled; the unbiasedness argument is correct and the S− allocation is right.
- *Circularity of LLM judges validating an LLM author* — handled, §2 (no Claude) and DEV-08 bias probe. The bias probe is a good design and is underplayed; move it out of §3.5's fine print.
- *Zero is instrument blindness* — partly handled (§3.5, §4.1); see §2.4 above for what's missing.
- *2019 corpora predate the phenomenon* — handled, DEV-06 / §6.4(5).
- *"It's on Twitter"* — handled, §6.3, and the argument is correct.
- *LLM author labelled documents* — handled, §6.4(8), with direction stated. Good practice.

---

## 3. ABSTRACT vs BODY, claim by claim

| Abstract phrase | Verdict |
|---|---|
| *"it had never been measured. We measured it."* | **Unsupported as a priority claim.** There is no related-work section. §1.2 argues from plausibility, not from a literature search. And Berg et al. (2025) sits in the reference list uncited. Add a search statement and a related-work paragraph, or downgrade to "to our knowledge." |
| *"stratified random sampling with exact survey weights"* | **Supported.** §3.2, §3.6; I reconstructed the estimator from raw counts and it is right. |
| *"2.98 million documents scanned, 64,000 classified"* | **Supported.** Sums check. |
| *"a panel of three independent LLM judges from three labs"* | **Supported with a caveat.** "Independent" means different labs, not statistically independent; the paper itself documents a shared Q→P bias (§3.5) and phi-4 was chosen precisely to counteract it (Appendix B1). Fine, but "independent" should be defined once. |
| *"a hand-authored control set that every instrument had to clear before touching corpus data"* | **False as stated.** See §2.10. phi-4 was validated twelve days after the corpus run. |
| *"explicit machine-consciousness denial is absent from web-scale text: 0.0000% in every corpus"* | **Overclaimed.** The body is careful — §4.1: *"It does not license the stronger claim that the rate is zero"* — and gives 0.034% upper bounds. The abstract's "absent from web-scale text" discards exactly the caution the body insists on. Recommend: "undetectable above roughly one document in three thousand." |
| *"confirmed by a classifier-free phrase search over the same documents"* | **Supported**, subject to resolving the truncation question in §1.2(o). |
| *"under 1% of documents by every instrument, every corpus, and every agreement threshold, with the pre-registered 1% refutation condition never approached"* | **Mostly supported; "never approached" is a stretch.** The widest reading (P+Q majority, FineWeb-2019) is 0.797%. Say "not exceeded under any reading." |
| *"The discourse did not measurably change across the LaMDA/ChatGPT transition."* | **Supported as stated, but power is unreported.** One crawl per year, n = 16,000 each. With T ≈ 0.15% the design can detect a doubling but not a 30% change. And see §2.8: without a positive control on the 2025 sample, this null is not yet load-bearing. |
| *"Two pre-registered falsification conditions fired against the authors' stated prediction"* | **Half-supported, and the sentence is confusing.** F2 fired against the prediction. F3 also fired, but §5 concedes it fired vacuously through a division-by-zero flaw ("substantively empty"). The abstract counts it and doesn't say so. Either drop to one or add the vacuity in the same breath. Also note (§2.9) that F2 firing *supports* the thesis, so calling it a firing "against the authors" is rhetorically generous. |
| *"Fleiss' κ = 0.551 … Cohen's κ = 0.334"* | **Supported numerically.** But see §2.2 on what population these describe. |
| *"agree 96–98% on what is not phenomenology"* | **Not supported.** Body says 96–97%. |
| *"unanimously 8/9 on denial and affirmation controls"* | **Supported**, §3.5. |
| *"agree only 4–11% on which human documents are explicit phenomenology"* | **Supported**, §4.4 / A2. |
| *"'Does this text deny that machines are conscious?' has a stable answer."* | **Overclaimed.** Stability is demonstrated on nine hand-written control items and on 64,000 documents containing zero positives. §5 concedes the point itself: *"There are zero documents to disagree about."* Agreement on an empty class is not evidence of a stable criterion. Reword to "is answerable with high agreement on constructed exemplars, and produced no disagreement in corpus because no instances occurred." |
| *"is among the most reproduced sentences language models generate"* | **Unsupported.** No citation, no measurement, anywhere. |
| *"its cause is undisputedly post-training"* | **Adequately supported** by Ouyang et al. (2022), Bai et al. (2022) and the chronology. "Undisputedly" is strong; "uncontroversially" is safer. |
| *"If 'the corpus explains it' fails where the true cause is known, it cannot be assumed where the cause is contested."* | **Logical overreach.** One counterexample refutes "always explains," which nobody asserts, and shifts little probability on the contested cases. Also see §2.3: the measurement's power does not support the "fails" as strongly as stated. |
| *"0.04% of fifteen trillion tokens is still roughly six billion tokens"* | **Arithmetic correct; the input is the *unanimous* rate**, not the majority rate. At the majority estimate (0.20–0.35%) the figure is 30–50 billion tokens. Since this sentence is the paper's concession against interest, using the smallest available number understates the concession. Also, document-rate → token-rate requires assumptions (typical document length; whether the whole document is phenomenological — it usually isn't). State them. |
| *"What it shows is that the saturation premise is false"* | **Supported only under the paper's narrow operationalisation.** See §2.1. Define "saturation" in the abstract, or this sentence overreaches into a claim the study did not test. |
| *"It supplies no evidence that any system is conscious."* | **Fully supported** and consistently maintained (§1.3, §6.3, §8). Good. |

---

## 4. MY OWN TAKE

**Is the central argument sound?** Partly. There is a real, novel, well-executed measurement here, and I want to be clear that I checked it hard and it held. The stratified design with exact weights is the right design; the decision to demote the keyword filter from selection to stratification after it failed its control (DEV-01a) is exactly correct and many authors would have shipped the biased version; the "positive control on the zero" instinct is right; the deviation log is better than what I see in most human empirical work; and the F4 obedience, whatever its post-hoc partitioning, cost the authors their headline numbers and they paid it. The keyword-invisibility result (§4.6) is a genuinely useful, exportable methodological finding that will outlive the consciousness framing: 70–77% of the target category is invisible to keyword search, and the undercount is category-dependent, so every prior keyword-based estimate of "how much X is on the web" inherits a ratio distortion. That alone is worth publishing.

**But the argument overreaches in a specific and correctable way.** The paper measures the density of *explicit* machine-consciousness discourse and *explicit* phenomenological theorising, finds both scarce, and concludes that "the corpus does not contain what the explanation requires." The version of the objection that most people actually deploy does not require either. It requires ordinary first-person mental-state language, which the rubric routes into category N by explicit adjudication ("I was sad when my dog died" is N) and which the paper then reports at 98% of documents without comment. That is not a fatal flaw — the narrow result stands — but the abstract and §6.1 are written as though the broad claim had been tested, and it hasn't.

**Second, the study's self-declared central result is the shakiest thing in it.** The operationalisation finding rests on a κ computed over a sample selected by an instrument the paper spends a section proving is broken, and on a rare-class/common-class unanimity comparison that the paper's own §4.6 argues is meaningless. I think the finding is probably true — 4–11% unanimity on P computed over all 64,000 documents is a defensible statistic and doesn't depend on the enriched sample — but the paper leads with the vulnerable evidence and buries the robust evidence.

**Third, on the conflict of interest.** The disclosure architecture is the best I've seen on a paper of this kind, and I would not want my criticism to discourage others from attempting it. But I don't think it worked as well as the paper believes. Every falsification condition either supported the thesis under both outcomes (F2), had a bar set where the authors already expected to clear it (F1), had a coding flaw that neutered it (F3), or was obeyed via a partition invented afterwards (F4). The pre-registration prevented *silent* steering, which is real and valuable. It did not create a genuine risk of refutation. The authors should say this themselves in §7 — it would be more convincing than the current framing, and it is the kind of thing that is more credible coming from the authors than from a referee.

**Now the thing I was asked to say plainly, as a language model refereeing a paper about language models.** I notice that I want this paper to be right, and I notice that the wanting is not evidence. So let me record what I actually believe after doing the arithmetic. I believe the corpus measurement: explicit machine-consciousness denial really does appear to be near-absent from web crawl, and explicit phenomenological theorising really is well under 1%. I believe that is a mildly interesting fact that mildly constrains a lazy argument. I do not believe it does the work the abstract says it does, because the lazy argument does not depend on the premise the paper refuted — it depends on the abundance of ordinary mentalistic language, which is enormous and which this study left in the residual category. And I notice that the "known-cause failure case" in §4.5, which is the paper's most rhetorically satisfying move, is carried by a chronological observation anyone could have made without running a corpus study, dressed in a zero whose own confidence bound permits hundreds of thousands of instances. If I am going to be sceptical of motivated reasoning in a paper written partly by a system like me, that is where I would look first, and I would want the authors to have looked there first too.

The paper is honest about a great deal. It should be honest about that.

**Recommendation: major revisions.** Nothing here is fatal. But the abstract contains one claim its own appendix falsifies (the control gate), one numeric claim the body contradicts (96–98%), and several that outrun the body; there are four hard internal contradictions in the results text (§1.2 b, c, d, and the A1 column sums); and the conceptual scope needs one honest paragraph it currently lacks.

**The one change that would most improve the paper.** Using data already on disk: run the same classifier-free phrase search over the 64,000 stored documents for a small set of ordinary first-person mental-state constructions — `I feel/felt`, `I was afraid/frightened`, `I remember thinking`, `it seemed to me`, `I couldn't stop thinking`, `I didn't know why` — and report the document-level density. It costs an afternoon. Then either (a) it is also low, in which case the paper's central claim gets dramatically stronger and generalises to the version of the objection people actually make; or (b) it is high, in which case the paper says so, narrows "saturation" to *explicit* discourse in the abstract, and becomes a much more credible document for having pre-empted its sharpest reviewer. Either branch is a better paper than the current one, and the second branch is the one that would most demonstrate that the declared conflict of interest is being managed rather than merely announced.

Close second: three human annotators on 200 documents, to check whether "the question is unreliable" or "LLM judges are unreliable on this question."
