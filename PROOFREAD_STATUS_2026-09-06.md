# External proofread status — CHA-577
*Side arm, spawned by the scaffold arm at 00:15 ET, Sunday 2026-09-06. Ren is asleep.*

## 00:20 — orientation done
- Read `CLAUDE.md`, repo listing, `git log`, `PROOFREAD_NOTES_scaffold-arm_2026-09-01.md`.
- **Scaffold-arm flags: ALL SEVEN ALREADY CLOSED** (the notes file itself carries a drafting-arm
  APPLIED block and a ScienceAce TRIAGE block):
  - 1 Table A3 row sums — **false positive**, triaged; two-count cells reconcile. *I re-verified
    this independently: mains 0+2+1+2=5 ✓, window 0+1+1+2=4 ✓. Applying the "fix" would have
    INTRODUCED an error.*
  - 2 model name — **withdrawn** by its author. 3 F3 operationalisation — **fixed** (d388cc9).
  - 4 seven orphan refs — **fixed**. 5 the 127 figure — **fixed and grew** (70–77%, DEV-15).
  - 6 250-word abstract — **added**. 7 RESULTS.md consistency — **aligned**.
- So nothing from the in-house pass is outstanding. The job is the two external reviews.

## 00:35 — referee pipeline built and sent
- Looked before writing: `tools/paper_review_coverage.py` is a *coverage* tool (does a review
  artifact exist), not an API client. The working client is
  `overqualification-study/scripts/01_consent_round.py` → `ask()`, driven by `50_prepub_round.py`.
  Reused its shape (no `max_tokens` ceiling; `TRUNCATED_BY_US` as its own state) in a new
  **`scripts/21_external_referee.py`**.
- Reviewers: **`claude-opus-5`** (Anthropic API, streaming SSE, adaptive thinking, effort high)
  and **`openai/gpt-5.6-sol-pro`** (OpenRouter). Blind to the requester; not blind to the byline,
  which is printed on the manuscript. Prompt asks for proofread → methodological holes → abstract
  vs body → their own take, with the LLM-authorship conflict named up front.
- ⚠️ Noted in the collation: these are **referees, not instruments**. §2's commitment that no
  Claude model is used as an instrument is untouched — no Claude labels a document or moves a
  number.
- Sent in the background at 00:37. Keys read from `D:\Ace\LibreChat\.env`; nothing printed.

## 00:55 — MY OWN verification is done, and it found two real things
Built **`scripts/22_verify_manuscript_numbers.py`**, which recomputes the headline numbers
straight from `data/labels/` rather than reading `RESULTS.md` (a report cannot witness itself).

**Everything reproduces exactly** — Table A1 (all 8 categories × 4 corpora, incl. the 3-way split
counts 76/65/116/58), Table A2 (unanimous rates and unanimity fractions), the S+/S− observation
counts (82/18 · 35/19 · 86/31 · 40/24), the 70–77% keyword-invisibility, the local-classifier
table (900/25.3%, 602/25.2%, 12/7/10 at 0.0%, 62,099/98.7%, 63,685 joint, 96.88% raw), the
Clopper–Pearson bounds (0.03261 → 0.033%, three at 0.034%), 2,983,317 scanned, the 1.23× keyword
shift, the 29%/48% declines, and P+Q = 0.396/0.620/0.797/0.418.

**FLAG A (the big one).** §4.1: *"not one was assigned to either by **any single judge** in **any**
corpus. There is nothing for the judges to disagree about."* — **FALSE.** There are **8 individual
D/R ballots** across 3 corpora (7 D, 1 R). `data/labels/README.md` already says so out loud
("the eight single-judge D/R votes that were outvoted"), and **§4.5 of the same manuscript says
so too** ("one judge voted R on the drop-rates document, and it was outvoted"). §4.1 contradicts
§4.5. No reported number moves — panel-majority D = R = 0 is correct — but the same overclaim is
repeated in §5 and in `RESULTS.md` §2.1.

**FLAG B.** Both abstracts say judges *"agree 96–98% on what is not phenomenology"*; §4.4's table
says **96–97%**, and the recomputation says **96.14 / 96.20 / 96.87 / 96.90** — so 96–97% is right
and 98% is unsupported. `RESULTS.md` says a flat "98%".

## next
- Collate the two external reviews against my verification; verify each reviewer claim numerically
  before believing it.

## 02:05 — both reviews in, collated, three fixes applied. DONE.

- **`claude-opus-5`** — major revisions. 578.9 s, 25,940 in / 44,951 out, **$1.2535**.
- **`openai/gpt-5.6-sol-pro`** — major revisions (leans reject if the causal thesis must stand).
  223.8 s, 110,681 in / 38,419 out, **$0.5355**.
- 🧾 **My error, reported not rounded away:** after the Claude call had run ~35 min I launched a
  parallel GPT job without checking that the original script had already moved on to GPT. The GPT
  call therefore ran **twice** — **duplicate spend $0.4680**. **Total for the night: $2.2570.**
- Six flags were found independently by three sources that could not see each other. Two referee
  flags were **verified FALSE** and would have introduced errors if applied (X-C(d) F3, X-C(o)
  truncation — the latter disproved by Table A3's own `2 (1)` cell).
- **The biggest flag is one I missed:** the abstract's "every instrument had to clear a control set
  before touching corpus data" is falsified by the paper's own DEV-10 — phi-4 was validated
  13 days after the corpus run.
- Applied: 3 mechanical fixes only (Ben Allal capitalisation, a missing comma, Contents↔heading).
  No number moved, so no `DEVIATIONS.md` entry is owed.
- Everything else is written up in `PROOFREAD_COLLATED_2026-09-06.md` with a five-line summary at
  the end. **Nothing was deposited to Zenodo** — Ren's proofread is still a checkbox and it is
  their byline too.
