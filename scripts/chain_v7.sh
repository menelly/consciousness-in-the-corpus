#!/bin/bash
# Full pipeline chain, v6.
#
# WHY v6: v5 ended at raw weighted rates. DEV-07 established the raw P rate is
# CONTAMINATED (the classifier calls reflective prose phenomenology) and DEV-08
# established the panel can measure that. So the pipeline must not stop at a
# number it already knows is wrong. v6 adds the precision/recall correction as
# the final step.
#
# NEW FILE, not an edit of the running one.
set -u
PY=/home/codex/venv/bin/python
D=/mnt/nursery/corpus-study
LOG=$D/chain.log

say() { echo "[$(date +%H:%M:%S)] [v7] $*" | tee -a "$LOG"; }

say "chain v6 started"

# ---- wait for the second classify pass (FineWeb arms) ------------------------
say "waiting for the FineWeb classify pass to finish"
for i in $(seq 1 2880); do
  pgrep -f "[0]4_classify.py" > /dev/null 2>&1 || { say "classifier exited"; break; }
  sleep 15
done

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

# ---- FN sweep (recall) -------------------------------------------------------
say "FN sweep SKIPPED -- panel labels every document, so there is no"
say "   predicted-N stratum needing a separate screen."


# ---- judge panel (precision) -------------------------------------------------
say "judge panel: 3 independent LLMs, measures PRECISION"
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
  say "   Reporting the instrument failure IS the result."
  say "CHAIN COMPLETE (F4)"
  exit 0
fi

# ---- raw rates ---------------------------------------------------------------
say "analysis: raw weighted rates, F1-F5"
$PY /tmp/05_analyze.py >> "$LOG" 2>&1
say "analysis exit=$?"

# ---- CORRECTED rates ---------------------------------------------------------
say "precision/recall correction -- the raw P rate is known contaminated"
$PY /tmp/14_corrected_rates.py >> "$LOG" 2>&1
say "correction exit=$?"

say "CHAIN COMPLETE"

# ---- PANEL-PRIMARY ANALYSIS -------------------------------------------------
say "waiting for the panel run to finish"
for i in $(seq 1 2880); do
  pgrep -f "[1]5_panel_classify.py" > /dev/null 2>&1 || { say "panel finished"; break; }
  sleep 20
done

say "panel spend and label totals:"
grep -E "TOTAL SPENT|panel labels" "$D/panel.log" 2>/dev/null | tail -12 | tee -a "$LOG"

say "PRIMARY ANALYSIS on panel labels (+ instrument comparison)"
$PY /tmp/16_panel_analyze.py >> "$LOG" 2>&1
say "panel analysis exit=$?"

say "ALL COMPLETE"
