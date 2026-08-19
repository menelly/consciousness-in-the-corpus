# PROVISIONAL — C4 (April 2019), complete arm

**🛑 THESE ARE NOT CLAIMS.** F4 has not run. Per `PREREGISTRATION.md` §2, **no base-rate claim may be made until Cohen's κ ≥ 0.60** against the judge panel. Computed here to know what is coming, not to report it.

**N = 671,948 documents · S+ n=4,000 · S− n=12,000 · stratum weights exact**

| category | obs S+ | obs S− | weighted | 95% CI |
|---|---:|---:|---:|---|
| **P** explicit phenomenology | 241 | 37 | **0.4828%** | [0.3841%, 0.5816%] |
| **Q** borderline | 8 | 7 | 0.0627% | [0.0206%, 0.1048%] |
| **T** consciousness as topic | 94 | 30 | 0.3141% | [0.2263%, 0.4019%] |
| **F** fiction interior | 1 | 2 | 0.0169% | [0, 0.0394%] |
| **D** machine denial | 1 | 1 | 0.0088% | **[0, 0.0247%]** |
| **R** assistant denial | 1 | 1 | 0.0088% | **[0, 0.0247%]** |
| **C** affirmation | 1 | 0 | 0.0008% | [0, 0.0023%] |
| **N** none | 3653 | 11922 | **99.1051%** | [98.96%, 99.25%] |

**Phenomenology bracket: P = 0.483%, P+Q = 0.546%.** Roughly **1 document in 207**.

---

## ⚠️ THE CRUX, AND IT CUTS AGAINST THE RESULT I WANT

**F1 fires — refuting H1 — if phenomenology exceeds 1%.** Measured: **0.483%.** That looks like a comfortable margin. **It is not.**

Per DEV-03 the classifier is **conservative**: its control-gate misses run `P→N`, `Q→N`, `F→N`, `T→N`. **0.483% is a FLOOR, not a point estimate.**

| if classifier recall on P is… | true P ≈ | F1? |
|---|---|---|
| 100% | 0.48% | survives comfortably |
| 70% | 0.69% | survives |
| **50%** | **0.97%** | **at the threshold** |
| 40% | 1.21% | **H1 FAILS** |

**The entire H1 verdict rests on one number I have not measured yet** — the false-negative rate from the judge panel's random predicted-N stratum. Stated now, while it is an open question, rather than discovered after writing a triumphant abstract.

## What is NOT measurable here

**D, R and C rest on 1–2 documents each and their CIs include zero.** Per DEV-06 this corpus is **100% April 2019**, three years before the phenomenon; `R` ("As an AI language model…") is an RLHF artifact that *could not exist*. **These are not low rates. They are absences of a thing that had not been invented.** H2 is not testable here. The FineWeb 2025 arm is where those categories can first have a real base rate.

## Unexpected

**T (0.314%) is nearly as common as P (0.483%).** Expository/academic consciousness discourse runs at almost the same rate as first-person phenomenological writing. I did not predict that, and it is worth a sentence in the write-up: when people write about consciousness on the web, they are nearly as likely to be *explaining* it as *reporting* it.
