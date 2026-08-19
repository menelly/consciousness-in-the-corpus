#!/bin/bash
# Full pipeline chain, v4.
#
# WHY v4 EXISTS: 04_classify.py snapshots os.listdir(SAMPLES) at launch. The
# running instance started BEFORE the FineWeb 2019/2025 samples were written,
# so it will never see them. chain_v3 would have fired the judge panel on a
# half-classified corpus and reported rates for two arms when only one existed.
#
# Fix: after the current classifier exits, re-run it. It skips files whose
# output already exists, so the second pass does exactly the FineWeb arms.
#
# NEW FILE, not an edit of a running one -- overwriting a script bash is
# executing makes it resume at a stale byte offset and run garbage. Learned
# that at 23:30 tonight.
set -u
PY=/home/codex/venv/bin/python
D=/mnt/nursery/corpus-study
LOG=$D/chain.log

say() { echo "[$(date +%H:%M:%S)] [v4] $*" | tee -a "$LOG"; }

say "chain v4 started"

# ---- wait for the in-flight classifier to exit -------------------------------
say "waiting for the running classifier to finish its file list"
for i in $(seq 1 2880); do
  if ! pgrep -f "[0]4_classify.py" > /dev/null 2>&1; then
    say "classifier process has exited"
    break
  fi
  sleep 15
done

# ---- second pass: picks up FineWeb --------------------------------------------
say "second classify pass (skips completed files, does FineWeb arms)"
$PY /tmp/04_classify.py >> "$D/classify2.log" 2>&1
say "second pass exit=$?"

say "labelled files now present:"
ls -1 "$D"/classified/ 2>/dev/null | sed 's/^/    /' | tee -a "$LOG"

say "label counts across everything:"
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

# ---- judges ------------------------------------------------------------------
say "judge panel (3 independent LLMs via OpenRouter)"
$PY /tmp/06_judge_panel.py >> "$LOG" 2>&1
say "judge panel exit=$?"

# ---- F4 gate -----------------------------------------------------------------
say "agreement statistics (F4 gate)"
$PY /tmp/07_kappa.py >> "$LOG" 2>&1
KRC=$?
say "kappa exit=$KRC"

if [ "$KRC" = "3" ]; then
  say "!! F4 FIRED (Cohen kappa < 0.60)."
  say "   Per the pre-registration NO BASE-RATE CLAIM MAY BE MADE."
  say "   Skipping the rates. Reporting the instrument failure IS the result."
  say "CHAIN COMPLETE (F4)"
  exit 0
fi

# ---- rates -------------------------------------------------------------------
say "analysis (weighted rates, F1-F5)"
$PY /tmp/05_analyze.py >> "$LOG" 2>&1
say "analysis exit=$?"

say "CHAIN COMPLETE"
