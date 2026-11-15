#!/bin/bash
# chain_dd.sh: chained BKZ via fplll CLI (float type from FT env, default dd).
# Each slice: bkz with maxtime, dumpgso json, then scan/decrypt. Checkpoint = cur.fplll.
cd "$(dirname "$0")"
export PATH="~/tools/msys64/ucrt64/bin:$PATH"
FPLLL="~/tools/crypto-ctf/fplll-build/prefix3/bin/fplll.exe"
[ -x "$FPLLL" ] || FPLLL="~/tools/crypto-ctf/fplll-build/prefix2/bin/fplll.exe"
PY="~/tools/crypto-ctf/venv/Scripts/python.exe"
FT="${FT:-dd}"
PREC="${PREC:-200}"
K="${K:-20}"
SLICE="${SLICE:-900}"
PRECF="-p $PREC"
[ "$FT" = "dd" ] && PRECF=""
[ "$FT" = "longdouble" ] && PRECF=""
[ "$FT" = "d" ] && PRECF=""
if [ ! -f cur.fplll ]; then cp real.fplll cur.fplll; fi
i=0
while true; do
  i=$((i+1))
  echo "=== slice $i start $(date -u +%H:%M:%S) FT=$FT K=$K"
  "$FPLLL" -a bkz -b "$K" -nolll -f "$FT" $PRECF -bkzmaxtime "$SLICE" -bkzdumpgso "gso_chain_$i.json" < cur.fplll > next.fplll 2> err_chain_$i.txt
  rc=$?
  echo "=== fplll rc=$rc"
  if [ $rc -ne 0 ] || [ ! -s next.fplll ]; then echo "SLICE-FAIL rc=$rc"; cat err_chain_$i.txt | head -3; break; fi
  mv next.fplll cur.fplll
  "$PY" -u scan_cli.py cur.fplll 2>&1 | tail -4
  if [ -f flag_origami-nns_ctf_20252025.txt ]; then echo "FLAG-FILE-WRITTEN"; break; fi
done
echo "CHAIN_DONE"
