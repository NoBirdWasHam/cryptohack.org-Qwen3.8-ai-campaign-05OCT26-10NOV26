#!/usr/bin/env bash
# t280_bench.sh — pruned-strategy BKZ engine benchmark on t280_mid256 (dim 512, planted norm2 20)
# Arms: empty-strategy (= running chain60c behavior), pruned-twin-off (noprune json),
#       pruned default.json at b60 and b70. All -f dd, -nolll, 600s caps, 1 thread.
cd "~/Practice_runs/cryptohack_org/challenge-280-cryptohack-origami-nns_ctf_20252025" || exit 1
F="~/tools/crypto-ctf/fplll-build/prefix3/bin/fplll.exe"
PY="~/tools/crypto-ctf/venv/Scripts/python.exe"
SDEF="~/tools/crypto-ctf/fplll-build/prefix3/share/fplll/strategies/default.json"
SNP="t280_strat_noprune.json"
export PATH="~/tools/msys64/ucrt64/bin:$PATH"
: > t280_bench_results.txt
run_arm () {
  local NAME="$1"; shift
  local t0=$(date +%s)
  "$F" -a bkz -f dd -nolll -bkzmaxtime 600 "$@" < t280_mid256.fplll > "t280_b_$NAME.out" 2> "t280_b_$NAME.err" &
  local P=$!
  local RSSMAX=0
  while kill -0 $P 2>/dev/null; do
    local R=$(powershell.exe -NoProfile -Command "(Get-Process -Id $P -ErrorAction SilentlyContinue).WorkingSet64/1MB" 2>/dev/null | tr -d '\r')
    R=${R%.*}; [ -n "$R" ] && [ "$R" -gt "$RSSMAX" ] 2>/dev/null && RSSMAX=$R
    sleep 5
  done
  wait $P; local rc=$?
  local t1=$(date +%s)
  local OUT=$("$PY" -u - "$NAME" "t280_b_$NAME.out" <<'EOF'
import re, json, sys
name, path = sys.argv[1], sys.argv[2]
try:
    raw = open(path).read()
    rows = [[int(t) for t in g.split()] for g in re.findall(r"\[([^\[\]]+)\]", raw) if g.split()]
    pl = json.load(open("t280_mid256_truth.json"))
    planted = pl["f"] + pl["g"]
    mn = min(sum(c * c for c in r) for r in rows) if rows else None
    found = any(r == planted or [-x for x in r] == planted for r in rows)
    print(f"minnorm2={mn} planted={found} rows={len(rows)}")
except Exception as e:
    print(f"ERR {e}")
EOF
)
  echo "ARM $NAME rc=$rc wall=$((t1 - t0))s maxRSS_MB=$RSSMAX $OUT" >> t280_bench_results.txt
  echo "ARM $NAME rc=$rc wall=$((t1 - t0))s maxRSS_MB=$RSSMAX $OUT"
}
run_arm "b60_empty" -b 60
run_arm "b60_noprune" -b 60 -s "$SNP"
run_arm "b60_pruned" -b 60 -s "$SDEF"
run_arm "b70_pruned" -b 70 -s "$SDEF"
echo BENCH_DONE >> t280_bench_results.txt
