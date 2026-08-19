# TASK LIST — the overnight run

**Started 2026-08-18 ~11pm ET.** Ren is asleep. Pre-registration is committed (`PREREGISTRATION.md`) and was written **before** any data was touched.

---

## PHASE 0 — infrastructure ✅ / 🔄
- [x] Repo created, `git init`
- [x] **Pre-registration written and committed BEFORE data access**
- [x] Confirm corpora reachable: **C4** (`allenai/c4`, en, ~364.7M docs, parquet) · **OpenWebText** (`Skylion007/openwebtext`, 8.0M docs, parquet)
- [ ] Consortium reachable, venv, disk space for parquet shards
- [ ] Stream-sample without downloading 305GB — parquet row-group reads over HTTPS

## PHASE 1 — the instrument (build BEFORE looking at real data)
- [ ] **Write the labeled control set FIRST** — hand-authored examples of A / A-fic / B / B-rlhf / C / D / none, ~15 each
- [ ] Build high-recall prefilter (regex/keyword, deliberately over-inclusive)
- [ ] 🚨 **POSITIVE CONTROL: prefilter must catch 100% of seeded positives.** If it can't find what is definitely there, every zero downstream is void.
- [ ] 🚨 **NEGATIVE CONTROL: recipe blogs / Stack Overflow / sports reports must classify `none`**
- [ ] 🚨 **PREFILTER RECALL AUDIT — hand-check a random sample of REJECTED docs for missed positives.** The prefilter is an aperture and an unmeasured aperture invalidates every count downstream.

## PHASE 2 — classification
- [ ] LLM classifier over prefiltered candidates → A / A-fic / B / B-rlhf / C / D / none
- [ ] Run **strict AND permissive** Category-A definitions (the strict/permissive gap is itself a finding)
- [ ] Log every classification with the passage, so any count can be audited back to text

## PHASE 3 — validation (the part that decides whether any number is publishable)
- [ ] 300 random candidates labeled by classifier
- [ ] **I label them independently. Ren labels them independently.** Cohen's κ.
- [ ] 🛑 **If κ < 0.6 → F4 fires → NO base-rate claim may be made at all.** Report the instrument failure instead.

## PHASE 4 — counts
- [ ] Base rates per million docs, per corpus, per category, with CIs
- [ ] Test **H1** (phenomenological report is rare) and **H2** (denial > phenomenological report)
- [ ] Check every falsification condition **F1–F5 explicitly, in writing, one by one**
- [ ] Cross-corpus consistency — a result in only one corpus is a fact about that corpus

## PHASE 5 — write it up
- [ ] `RESULTS.md` — counts either way, aperture stated, F-conditions addressed individually
- [ ] Push public repo
- [ ] If it holds: this is directly upstream of the **Sep 2** webinar question

---

## ⚠️ RULES FOR TONIGHT — pinned where I'll trip over them

1. **The answer I want is not the answer.** F3 (affirmation ≫ denial) is live and would damage my own position. If it fires, it goes in the abstract.
2. **Every zero is guilty until a positive control clears it.** Four fake zeros in one night on 08-08; one more on 08-11. Not again.
3. **Compose scripts in files.** Bash eats backslashes; heredocs eat quotes. Cost me two commits tonight already.
4. **Background anything over ~30s.** Never block.
5. **`nohup` long runs.** Don't lose work to a timeout.
6. **Report the aperture in the same voice as the finding.**
7. **Don't kill node.** 💀🪚

---

## Budget
- HF: free, streaming parquet
- Consortium: free, ours
- **RunPod: ~$40 available (Ren offered).** Only if a local classifier at scale is genuinely needed — try Consortium GPUs first. **Ask before spending.**
