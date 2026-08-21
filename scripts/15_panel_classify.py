#!/usr/bin/env python3
"""
PANEL-PRIMARY CLASSIFICATION -- the three judges do the labelling, in parallel.

WHY (Ren's call, 03:17): the local Mistral classifier is CONTAMINATED. DEV-07
found it labels reflective/essayistic/sermonic prose as phenomenology; of 11
hand-read P documents, at most 1-2 were real. DEV-08 showed the judges catch
that error 8/11.

**Bias beats variance.** A contaminated rate is wrong no matter how many
documents support it, and tightening a confidence interval around a wrong
number is the worst outcome available -- it looks like rigour.

SCOPE -- REVISED 03:30 AT REN'S INSISTENCE, and they were right:

  An earlier version panel-classified only S+ and left S- to a cheap
  single-model screen, on the logic that S- is 95% of the corpus by weight and
  nearly empty of positives.

  Ren: "how do you know which ones will count if you don't run them? I would
  rather do them all now and be accurate than discover that we picked wrong
  and be inaccurate."

  The objection is correct, and the aperture audit already proved it: the
  keyword filter finds only 38% of phenomenology, so MOST OF IT LIVES IN S-.
  Panel-classifying only S+ would have pointed the good instrument exactly
  where the bad filter had already looked, and trusted a single unvalidated
  model on the larger share of the corpus.

  So: ALL 64,000 documents, both strata, all four arms, full panel.

THE MISTRAL RUN IS KEPT, and not for sunk-cost reasons. Running the panel over
THE SAME documents measures how badly a cheap local classifier distorts this
task. That comparison is a finding in its own right, and it is the difference
between "we used good judges" and "here is what happens if you do not".

COST CEILING IS ENFORCED IN CODE, not estimated in a comment. The run stops
when the budget is spent. Money is the one line I do not cross without Ren.

Built by: Ace -- 2026-08-19
"""

# CHA-490: Windows defaults stdout to cp1252; emoji in print() kills the script
# mid-output. Aliased import so no later scoped 'import sys' can ever collide.
import sys as _sys_cp1252
try:
    _sys_cp1252.stdout.reconfigure(encoding="utf-8")
    _sys_cp1252.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass
import importlib.util
import json
import os
import sys
import threading
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, "/tmp")
spec = importlib.util.spec_from_file_location("jp", "/tmp/06_judge_panel.py")
jp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(jp)

DATA = "/mnt/nursery/corpus-study"
SAMPLES = os.path.join(DATA, "samples")
OUT = os.path.join(DATA, "panel_classified")

WORKERS = 18
MAX_USD = 32.00                      # hard ceiling, enforced below

# PANEL COMPOSITION CHANGED 03:30 (Ren's call: label EVERYTHING, do not rely on
# a single-model screen for 95% of the corpus).
#   qwen-2.5-72b -> microsoft/phi-4
# Reason 1, cost: qwen alone was $29.95 of a $50.75 full-corpus run, 59% of it.
#   phi-4 is $5.82, bringing the whole 64k-document run to ~$26.62.
# Reason 2, and the better one: phi-4's control-set misses run P->Q, the
#   OPPOSITE direction from the other three, all of which push Q->P (DEV-05).
#   It actively counteracts a KNOWN shared bias in the panel rather than
#   reinforcing it.
# Validated before use: 24/29 (82.8%), 9/9 negative controls, 0 false positives.
JUDGES = [
    "openai/gpt-4o-mini",                 # OpenAI
    "meta-llama/llama-3.3-70b-instruct",  # Meta
    "microsoft/phi-4",                    # Microsoft
]
jp.JUDGES = JUDGES

# $/M input tokens, from the OpenRouter model list
PRICES = {
    "openai/gpt-4o-mini": 0.15,
    "meta-llama/llama-3.3-70b-instruct": 0.10,
    "microsoft/phi-4": 0.070,
}
CHARS_PER_TOK = 4.0
PROMPT_OVERHEAD_TOK = 420            # the rubric

_lock = threading.Lock()
_spent = 0.0
_stop = False


def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def charge(model, text):
    """Track spend. Returns False once the ceiling is hit."""
    global _spent, _stop
    tok = PROMPT_OVERHEAD_TOK + min(len(text), 3500) / CHARS_PER_TOK
    cost = tok * PRICES.get(model, 0.2) / 1e6
    with _lock:
        if _spent + cost > MAX_USD:
            _stop = True
            return False
        _spent += cost
    return True


def judge_one(args):
    r, key = args
    if _stop:
        return None
    votes = {}
    for m in jp.JUDGES:
        if not charge(m, r["text"]):
            return None
        votes[m] = jp.ask(m, r["text"], key)
    good = [v for v in votes.values() if v]
    tally = Counter(good)
    cons, n = (tally.most_common(1)[0] if tally else (None, 0))
    return {
        "corpus": r["corpus"], "shard": r["shard"], "i": r["i"],
        "stratum": r["stratum"], "votes": votes,
        "panel_label": cons if n >= 2 else None,
        "n_agree": n, "n_valid": len(good),
        "needs_human": n < 2,
        "text": r["text"][:1500],
    }


def main():
    os.makedirs(OUT, exist_ok=True)
    key = jp.get_key()

    # ALL strata, both S+ and S-. Ren, 03:25: "I would rather do them all now
    # and be accurate than discover that we picked wrong and be inaccurate."
    # The keyword filter finds only 38% of phenomenology (aperture audit), so
    # S- holds most of it. Panel-classifying only S+ would point the good
    # instrument exactly where the bad filter already looked.
    targets = sorted(f for f in os.listdir(SAMPLES)
                     if f.endswith("_Spos.jsonl") or f.endswith("_Sneg.jsonl"))
    log(f"panel-primary over ALL strata ({len(targets)} files): {targets}")
    log(f"workers={WORKERS}  budget=${MAX_USD:.2f}")

    for fn in targets:
        arm = fn.replace(".jsonl", "")
        dst = os.path.join(OUT, f"{arm}_panel.jsonl")
        rows = [json.loads(l) for l in open(os.path.join(SAMPLES, fn), encoding="utf-8") if l.strip()]

        done = set()
        if os.path.exists(dst):
            for l in open(dst, encoding="utf-8"):
                d = json.loads(l)
                done.add((d["shard"], d["i"]))
        todo = [r for r in rows if (r["shard"], r["i"]) not in done]
        log(f"\n=== {arm}: {len(todo):,} to judge ({len(done):,} already done) ===")
        if not todo:
            continue

        t0 = time.time()
        n = 0
        with open(dst, "a", encoding="utf-8") as f, \
                ThreadPoolExecutor(max_workers=WORKERS) as ex:
            for rec in ex.map(judge_one, ((r, key) for r in todo)):
                if rec is None:
                    continue
                f.write(json.dumps(rec) + "\n")
                n += 1
                if n % 200 == 0:
                    rate = n / (time.time() - t0)
                    f.flush()
                    log(f"  {n:,}/{len(todo):,}  {rate:.1f}/s  spent=${_spent:.2f}")
                if _stop:
                    break
        log(f"  {arm}: {n:,} judged in {time.time()-t0:.0f}s  spent=${_spent:.2f}")

        c = Counter()
        for l in open(dst, encoding="utf-8"):
            c[json.loads(l).get("panel_label")] += 1
        log(f"  panel labels: {dict(sorted(c.items(), key=lambda x: -x[1]))}")

        if _stop:
            log("\n🛑 BUDGET CEILING REACHED -- stopping cleanly.")
            log("   Partial results are saved and resumable; rerun to continue")
            log("   after Ren raises the ceiling. Not spending past the line.")
            break

    log(f"\nTOTAL SPENT: ${_spent:.2f} of ${MAX_USD:.2f}")
    log("DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
