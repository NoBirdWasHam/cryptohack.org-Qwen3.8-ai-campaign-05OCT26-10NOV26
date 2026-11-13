#!/bin/bash
# chained BKZ-60 dd on real lattice from real.fplll, scan each slice
cd "~/Practice_runs/cryptohack_org/challenge-280-cryptohack-origami-nns_ctf_20252025" || exit 1
export PATH="~/tools/msys64/ucrt64/bin:$PATH"
PY="~/tools/crypto-ctf/venv/Scripts/python.exe"
FPLLL="~/tools/crypto-ctf/fplll-build/prefix3/bin/fplll.exe"
K="${K:-60}"
SLICE="${SLICE:-1500}"
cp -f real.fplll cur60.fplll
for i in $(seq 1 24); do
  echo "=== s60 slice $i start $(date -u +%H:%M:%S)"
  "$FPLLL" -a bkz -b "$K" -nolll -f dd -bkzmaxtime "$SLICE" \
     -bkzdumpgso "gso60_$i.json" < cur60.fplll > next60.fplll 2> err60_$i.txt
  rc=$?
  if [ $rc -gt 1 ]; then echo "S60-SLICE-FAIL rc=$rc"; head -c 200 err60_$i.txt; break; fi
  if [ -s next60.fplll ]; then mv -f next60.fplll cur60.fplll; fi
  "$PY" -u scan_cli.py cur60.fplll 2>&1 | tail -4
  if [ -f flag_origami-nns_ctf_20252025.txt ]; then echo FLAG-FILE-WRITTEN; break; fi
done
echo S60_CHAIN_DONE
