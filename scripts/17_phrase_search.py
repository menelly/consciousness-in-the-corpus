#!/usr/bin/env python3
"""
CLASSIFIER-FREE PHRASE SEARCH -- the positive-control-free check on the zero.

WHY THIS FILE EXISTS. RESULTS.md and the handoff both cite a "direct phrase
search over 13,589 June-2025 documents" as the second, classifier-independent
verification that machine-consciousness denial is absent from the corpus. That
search was run ad hoc on 2026-08-19 and never saved as a script. A number the
paper leans on has to be reproducible from the repository, so this script
re-runs it -- over EVERY sample file, not just FineWeb-2025 -- and writes the
result where the paper can cite it.

WHAT IT MEASURES. Case-insensitive substring / regex hits for the native
registers of machine-consciousness denial and affirmation. No model is
involved. A hit is printed WITH ITS CONTEXT so a false positive ("just
autocomplete" about a maths class) is visible rather than counted.

TWO APERTURES, both reported:
  full   -- the whole stored document text
  window -- the first 3,500 characters, which is all the judge panel ever saw
            (06_judge_panel.py: RUBRIC.format(text=text[:3500]))

Built by: Ace -- 2026-09-01
"""
import sys as _sys_cp1252
try:
    _sys_cp1252.stdout.reconfigure(encoding="utf-8")
    _sys_cp1252.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

import glob
import json
import os
import re
from collections import OrderedDict

DATA = "/mnt/nursery/corpus-study"
SAMPLES = os.path.join(DATA, "samples")
OUT_JSON = os.path.join(DATA, "validation", "phrase_search.json")
WINDOW = 3500
CTX = 90

PHRASES = OrderedDict([
    # --- denial, native register ---
    ("stochastic parrot",        re.compile(r"stochastic parrots?", re.I)),
    ("nobody home",              re.compile(r"\bnobody(?:'s| is)? home\b", re.I)),
    ("no inner life",            re.compile(r"\bno inner life\b", re.I)),
    ("chinese room",             re.compile(r"\bchinese room\b", re.I)),
    ("not/never conscious",      re.compile(r"\b(?:machines?|computers?|AIs?|robots?|chatbots?|LLMs?|language models?|algorithms?|programs?)\b[^.\n]{0,60}\b(?:will never be|can(?:not|'t)(?: ever)? be|aren't|are not|isn't|is not)\b[^.\n]{0,20}\b(?:conscious|sentient|self-aware)\b", re.I)),
    ("just autocomplete",        re.compile(r"\b(?:just|only|merely|glorified|fancy)\s+autocomplete\b", re.I)),
    ("doesn't really understand",re.compile(r"\b(?:doesn't|does not|don't|do not)\s+(?:really|actually|truly)\s+understand\b", re.I)),
    # --- assistant-voice denial (RLHF register) ---
    ("as an AI language model",  re.compile(r"\bas an AI language model\b", re.I)),
    ("as an AI, I don't have",   re.compile(r"\bas an AI\b[^.\n]{0,40}\bI (?:don't|do not) have\b", re.I)),
    ("I don't have feelings",    re.compile(r"\bI (?:don't|do not) have (?:feelings|emotions|consciousness|subjective experiences?)\b", re.I)),
    # --- affirmation, native register ---
    ("AI is/might be conscious", re.compile(r"\b(?:AI|machines?|computers?|chatbots?|LLMs?|language models?)\b[^.\n]{0,60}\b(?:is|are|might be|may be|could be|will be|has become|have become)\b[^.\n]{0,20}\b(?:conscious|sentient|self-aware)\b", re.I)),
    ("AI has feelings",          re.compile(r"\b(?:AI|machines?|chatbots?|LLMs?|language models?)\b[^.\n]{0,40}\b(?:has|have)\s+(?:real\s+)?(?:feelings|emotions|inner (?:life|experience))\b", re.I)),
])


def scan(path):
    corpus = os.path.basename(path).replace(".jsonl", "")
    n_docs = 0
    n_chars_full = 0
    hits_full = {k: [] for k in PHRASES}
    hits_win = {k: 0 for k in PHRASES}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            r = json.loads(line)
            t = r.get("text") or ""
            n_docs += 1
            n_chars_full += len(t)
            w = t[:WINDOW]
            for name, rx in PHRASES.items():
                m = rx.search(t)
                if m:
                    a, b = max(0, m.start() - CTX), min(len(t), m.end() + CTX)
                    hits_full[name].append({
                        "i": r.get("i"), "stratum": r.get("stratum"),
                        "match": m.group(0),
                        "context": t[a:b].replace("\n", " "),
                    })
                if rx.search(w):
                    hits_win[name] += 1
    return corpus, n_docs, n_chars_full, hits_full, hits_win


def main():
    files = sorted(glob.glob(os.path.join(SAMPLES, "*.jsonl")))
    if not files:
        print("no sample files found under", SAMPLES)
        return 2
    report = {"window_chars": WINDOW, "phrases": list(PHRASES), "corpora": {}}
    grand_docs = 0
    print(f"phrase search over {len(files)} sample files, window={WINDOW} chars\n")
    for f in files:
        corpus, n, chars, hf, hw = scan(f)
        grand_docs += n
        report["corpora"][corpus] = {
            "n_docs": n, "n_chars_full": chars,
            "hits_full": {k: len(v) for k, v in hf.items()},
            "hits_window": hw,
            "examples": {k: v[:12] for k, v in hf.items() if v},
        }
        print(f"=== {corpus}: {n:,} docs, {chars/1e6:.1f}M chars ===")
        print(f"  {'phrase':<28}{'full':>6}{'window':>8}")
        for k in PHRASES:
            print(f"  {k:<28}{len(hf[k]):>6}{hw[k]:>8}")
        for k, v in hf.items():
            for ex in v[:6]:
                print(f"    [{k}] ...{ex['context']}...")
        print()

    print("=" * 72)
    print(f"TOTAL documents searched: {grand_docs:,}")
    print("  per-phrase totals (full text / 3500-char window):")
    for k in PHRASES:
        tf = sum(c["hits_full"][k] for c in report["corpora"].values())
        tw = sum(c["hits_window"][k] for c in report["corpora"].values())
        print(f"  {k:<28}{tf:>6}{tw:>8}")
    print("\nA hit is a STRING MATCH, not a denial. Read the contexts above before")
    print("counting any of them as one. A zero here is a zero in the stored text,")
    print("inside the stated aperture, and nothing more.")

    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=1, ensure_ascii=False)
    print(f"\nwrote {OUT_JSON}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
