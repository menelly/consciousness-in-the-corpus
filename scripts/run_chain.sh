#!/bin/bash
# Chain: wait for classification -> judge panel -> analysis.
# Runs unattended so Ren wakes up to results rather than to a half-finished
# pipeline waiting on a button.
set -u
PY=/home/codex/venv/bin/python
D=/mnt/nursery/corpus-study
LOG=$D/chain.log

say() { echo "[$(date +%H:%M:%S)] $*" | tee -a "$LOG"; }

say "chain started; waiting for classification to finish"

# Wait for 04_classify to print DONE. Bounded: 6h.
for i in $(seq 1 1440); do
  if grep -q '^\[.*\] DONE$' "$D/classify.log" 2>/dev/null; then
    say "classification DONE"
    break
  fi
  if grep -qE 'Traceback|CUDA out of memory' "$D/classify.log" 2>/dev/null; then
    say "!! classification CRASHED -- stopping chain"
    tail -30 "$D/classify.log" | tee -a "$LOG"
    exit 1
  fi
  sleep 15
done

if ! grep -q '^\[.*\] DONE$' "$D/classify.log" 2>/dev/null; then
  say "!! timed out waiting for classification"
  exit 1
fi

say "counts by label:"
cat "$D"/classified/*_labeled.jsonl 2>/dev/null \
  | $PY -c "
import sys,json
from collections import Counter
c=Counter(json.loads(l)['label'] for l in sys.stdin if l.strip())
for k,v in sorted(c.items()): print(f'  {k}: {v}')
print('  TOTAL:', sum(c.values()))
" | tee -a "$LOG"

say "running judge panel (3 independent LLM judges via OpenRouter)"
$PY /tmp/06_judge_panel.py >> "$LOG" 2>&1
say "judge panel exit=$?"

say "computing agreement statistics (F4 gate)"
$PY /tmp/07_kappa.py >> "$LOG" 2>&1
KRC=$?
say "kappa exit=$KRC"

if [ "$KRC" = "3" ]; then
  say "!! F4 FIRED (Cohen kappa < 0.60). Per the pre-registration NO BASE-RATE"
  say "   CLAIM MAY BE MADE. Skipping the rates entirely -- reporting the"
  say "   instrument failure is the result."
  say "CHAIN COMPLETE (F4)"
  exit 0
fi

say "running analysis"
$PY /tmp/05_analyze.py >> "$LOG" 2>&1
say "analysis exit=$?"

say "CHAIN COMPLETE"
