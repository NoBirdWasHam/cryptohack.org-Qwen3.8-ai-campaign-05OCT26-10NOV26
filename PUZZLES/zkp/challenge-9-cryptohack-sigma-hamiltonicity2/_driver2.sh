#!/bin/bash
# Driver v2: gate on shadow validation PASS, then production 6h each.
cd ~/Practice_runs/cryptohack_org/challenge-237-cryptohack-sigma-hamiltonicity2 || exit 1
PY=~/tools/crypto-ctf/venv/Scripts/python.exe
while ! (grep -q '"event": "done"' shadow_h2h1.log 2>/dev/null && grep -q '"event": "done"' shadow_h1h2.log 2>/dev/null); do
  sleep 30
done
echo "SHADOWS-FINISHED"
grep -h 'shadow' shadow_h2h1.log shadow_h1h2.log | grep -E 'PASS|FAIL'
ok1=$(grep -c -- '-> PASS' shadow_h2h1.log)
ok2=$(grep -c -- '-> PASS' shadow_h1h2.log)
if [ "$ok1" -ge 1 ] && [ "$ok2" -ge 1 ]; then
  echo "SHADOWS-PASS launching production"
  "$PY" kangaroo_window.py --dir h2h1 --max-hours 6 --stats-every 300 --ckpt kangaroo_h2h1.ckpt.json > prod_h2h1.log 2>&1 &
  p1=$!
  "$PY" kangaroo_window.py --dir h1h2 --max-hours 6 --stats-every 300 --ckpt kangaroo_h1h2.ckpt.json > prod_h1h2.log 2>&1 &
  p2=$!
  wait $p1
  wait $p2
  echo "PROD-FINISHED"
  grep -h '"event": "done"' prod_h2h1.log prod_h1h2.log
  if ls SOLUTION_*.txt >/dev/null 2>&1; then
    echo "KANGAROO-HIT: dlog found in window"
    cat SOLUTION_*.txt
  else
    echo "KANGAROO-NEGATIVE bounded verdict ready"
  fi
else
  echo "SHADOWS-FAIL production aborted"
fi
echo ALL-DONE
