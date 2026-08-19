#!/bin/bash
# Full pipeline chain, v5.
#
# WHY v5: v4 ran classify -> judges -> kappa -> analysis. It did not include
# the false-negative sweep, and the FN rate is the number H1's verdict actually
# rests on (see 12_fn_sweep.py). A chain that skips the load-bearing
# measurement would have produced a complete-looking result without it.
#
# NEW FILE, not an edit of the running one. Overwriting a script bash is
# executing makes it resume at a stale byte offset and run garbage.
set -u
PY=/home/codex/venv/bin/python
D=/mnt/nursery/corpus-study
LOG=$D/chain.log

say() { echo "[$(date +%H:%M:%S)] [v5] $*" | tee -a "$LOG"; }

say "chain v5 started"

# ---- 1. wait for the in-flight classifier ------------------------------------
say "waiting for the running classifier to exit"
for i in $(seq 1 2880); do
  pgrep -f "[0]4_classify.py" > /dev/null 2>&1 || { say "classifier exited"; break; }
  sleep 15
done

# ---- 2. second pass: picks up FineWeb arms -----------------------------------
say "second classify pass (skips done files; does the FineWeb arms)"
$PY /tmp/04_classify.py >> "$D/classify2.log" 2>&1
say "second pass exit=$?"

say "labelled files:"
ls -1 "$D"/classified/ 2>/dev/null | sed 's/^/    /' | tee -a "$LOG"

say "label counts per arm and stratum:"
cat "$D"/classified/*_labeled.jsonl 2>/dev/null | $PY -c "
import sys, json
from collections import Counter, defaultdict
per = defaultdict(Counter)
for l in sys.stdin:
    if not l.strip(): continue
    r = json.loads(l)
    per[(r['corpus'], r['stratum'])][r['label']] += 1
for k in sorted(per):
    tot = sum(per[k].values())
    top = ' '.join(f'{c}={n}' for c, n in sorted(per[k].items(), key=lambda x: -x[1]))
    print(f'  {k[0]:<14}{k[1]:<4}n={tot:<7}{top}')
" | tee -a "$LOG"

# ---- 3. FALSE-NEGATIVE SWEEP -- the load-bearing measurement -----------------
say "FN sweep: screening predicted-N docs (H1's verdict depends on this)"
$PY /tmp/12_fn_sweep.py >> "$LOG" 2>&1
say "fn sweep exit=$?"

# ---- 4. judge panel ----------------------------------------------------------
say "judge panel (3 independent LLMs)"
$PY /tmp/06_judge_panel.py >> "$LOG" 2>&1
say "judge panel exit=$?"

# ---- 5. F4 gate --------------------------------------------------------------
say "agreement statistics (F4 gate)"
$PY /tmp/07_kappa.py >> "$LOG" 2>&1
KRC=$?
say "kappa exit=$KRC"

if [ "$KRC" = "3" ]; then
  say "!! F4 FIRED (Cohen kappa < 0.60)."
  say "   Per the pre-registration NO BASE-RATE CLAIM MAY BE MADE."
  say "   Skipping rates. Reporting the instrument failure IS the result."
  say "CHAIN COMPLETE (F4)"
  exit 0
fi

# ---- 6. rates ----------------------------------------------------------------
say "analysis (weighted rates, F1-F5)"
$PY /tmp/05_analyze.py >> "$LOG" 2>&1
say "analysis exit=$?"

say "CHAIN COMPLETE"
