#!/usr/bin/env bash
# t280_run2tag.sh TAG — single-tag ORIGAMI fold ladder (see t280_run2.sh header).
cd "~/Practice_runs/cryptohack_org/challenge-280-cryptohack-origami-nns_ctf_20252025" || exit 1
T=$1
FPLLL="~/tools/crypto-ctf/fplll-build/prefix3/bin/fplll.exe"
SDEF="~/tools/crypto-ctf/fplll-build/prefix3/share/fplll/strategies/default.json"
PY="~/tools/crypto-ctf/venv/Scripts/python.exe"
export PATH="~/tools/msys64/ucrt64/bin:$PATH"
RSS_CAP_MB=2000
CUR="t280_f${T}_cur.fplll"
OTHER="t280_fm_cur.fplll"; [ "$T" = "m" ] && OTHER="t280_fp_cur.fplll"

tour() {  # $1=beta
  local B=$1
  local NEXT="t280_f${T}_next_${T}.fplll"
  echo "=== f$T B$B start $(date +%H:%M:%S)"
  "$FPLLL" -a bkz -b "$B" -nolll -f dd -s "$SDEF" -bkzmaxloops 1 < "$CUR" > "$NEXT" 2> "t280_f${T}_e3_${B}.txt" &
  local FP=$!
  local START; START=$(date +%s)
  while kill -0 $FP 2>/dev/null; do
    local NOW; NOW=$(date +%s); local EL=$((NOW-START))
    local RSS; RSS=$(powershell -NoProfile -Command "(Get-Process -Id $FP -ErrorAction SilentlyContinue).PrivateMemorySize64/1MB" 2>/dev/null | tr -d '\r')
    RSS=${RSS%.*}; RSS=${RSS:-0}
    if [ "$RSS" -gt "$RSS_CAP_MB" ]; then
      echo "!!! RSS cap f$T B$B"; powershell -NoProfile -Command "Stop-Process -Id $FP -Force -ErrorAction SilentlyContinue"; break
    fi
    if [ "$EL" -gt 14400 ]; then
      echo "!!! HARD4H f$T B$B"; powershell -NoProfile -Command "Stop-Process -Id $FP -Force -ErrorAction SilentlyContinue"; break
    fi
    sleep 30
  done
  wait $FP; local rc=$?
  local EL=$(( $(date +%s) - START ))
  local NR; NR=$(grep -ao "\[" "$NEXT" | wc -l)
  if [ "$NR" -gt 500 ]; then
    mv -f "$NEXT" "$CUR"
    echo "f$T B$B DONE rc=$rc rows=$NR at ${EL}s"
    "$PY" -u t280_foldscan.py "$CUR" "$OTHER" | grep -aE "min norm2|PATTERN|candidates|glue|FLAG"
    "$PY" t280_bestnorm.py
    [ -f FLAG_FOUND.txt ] && { echo "RUN2 FLAG-FILE-WRITTEN"; exit 0; }
  else
    echo "f$T B$B NOOUT rc=$rc rows=$NR at ${EL}s"; head -2 "t280_f${T}_e3_${B}.txt"
  fi
}

for pass in 1 2 3 4 5 6 7 8 9 10; do
  if [ "$pass" = "1" ]; then BL="40 50 60 50 60"; else BL="60"; fi
  for B in $BL; do tour "$B"; [ -f FLAG_FOUND.txt ] && break 2; done
done
echo "RUN2_${T}_END"
