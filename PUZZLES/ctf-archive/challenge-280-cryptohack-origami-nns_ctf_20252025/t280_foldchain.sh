#!/usr/bin/env bash
# t280_foldchain.sh — ORIGAMI FOLD attack chain: pruned BKZ dd on the two folded
# dim-512 lattices (t280_fp_cur / t280_fm_cur), foldscan (pattern+glue+parity-decrypt)
# after every slice pair. RSS watchdog 2 GB per fplll process. NEVER touches other
# challenge processes or the legacy 1024-dim chains.
cd "~/Practice_runs/cryptohack_org/challenge-280-cryptohack-origami-nns_ctf_20252025" || exit 1
FPLLL="~/tools/crypto-ctf/fplll-build/prefix3/bin/fplll.exe"
SDEF="~/tools/crypto-ctf/fplll-build/prefix3/share/fplll/strategies/default.json"
PY="~/tools/crypto-ctf/venv/Scripts/python.exe"
export PATH="~/tools/msys64/ucrt64/bin:$PATH"
B="${B:-60}"
TMAX="${TMAX:-3600}"        # fplll-side time cap (checked at tour boundaries)
HARD="${HARD:-14400}"       # external hard kill per slice (4 h)
NSL="${NSL:-24}"
RSS_CAP_MB=2000
FAILS=0

slice() {  # $1=tag(p|m)
  local T=$1
  local CUR="t280_f${T}_cur.fplll"
  local NEXT="t280_f${T}_next.fplll"
  echo "=== f$T slice $i start $(date -u +%F_%H:%M:%S)"
  "$FPLLL" -a bkz -b "$B" -nolll -f dd -s "$SDEF" -bkzmaxtime "$TMAX" < "$CUR" > "$NEXT" 2> "t280_f${T}_err_${i}.txt" &
  local FP=$! START=$(date +%s) RSSHIT=0
  while kill -0 $FP 2>/dev/null; do
    R=$(powershell.exe -NoProfile -Command "(Get-Process -Id $FP -ErrorAction SilentlyContinue).PrivateMemorySize64/1MB" 2>/dev/null | tr -d '\r')
    R=${R%.*}
    if [ -n "$R" ] && [ "$R" -gt "$RSS_CAP_MB" ] 2>/dev/null; then
      echo "RSS-CAP ${R}MB -> kill"; kill -9 $FP; RSSHIT=1; break; fi
    if [ $(( $(date +%s) - START )) -gt "$HARD" ]; then
      echo "HARD-KILL after ${HARD}s"; kill -9 $FP; RSSHIT=2; break; fi
    sleep 30
  done
  wait $FP; local rc=$?
  if [ "$RSSHIT" != 0 ]; then echo "f$T SLICE-FAIL cap/hard retry $((FAILS+1))/5"; FAILS=$((FAILS+1)); return 1; fi
  if [ ! -s "$NEXT" ]; then echo "f$T SLICE-FAIL rc=$rc empty-out (retry $((FAILS+1))/5)"; head -c 200 "t280_f${T}_err_${i}.txt"; FAILS=$((FAILS+1)); return 1; fi
  FAILS=0
  mv -f "$NEXT" "$CUR"
  local mn=$("$PY" -u - "$CUR" <<'PYEOF'
import re, sys
raw = open(sys.argv[1]).read()
rows = [[int(t) for t in ch.split()] for ch in re.findall(r"\[([^\[\]]+)\]", raw) if ch.split()]
print(min(sum(x*x for x in r) for r in rows) if rows else -1)
PYEOF
)
  echo "f$T slice $i done rc=$rc minrownorm2=$mn"
  return 0
}

for i in $(seq 1 "$NSL"); do
  slice p; slice m
  "$PY" -u t280_foldscan.py 2>&1 | tail -6
  if [ -f flag_origami-nns_ctf_20252025.txt ]; then echo "FOLD-CHAIN FLAG-FILE-WRITTEN"; break; fi
  [ "$FAILS" -ge 5 ] && { echo FOLD_CHAIN_ABORTED; exit 2; }
done
echo "FOLD_CHAIN_LOOP_END"
