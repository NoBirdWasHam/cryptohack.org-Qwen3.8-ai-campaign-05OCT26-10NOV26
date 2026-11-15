#!/bin/bash
# chained BKZ-60 dd on real lattice from real.fplll, scan each slice
cd "~/Practice_runs/cryptohack_org/challenge-280-cryptohack-origami-nns_ctf_20252025" || exit 1
export PATH="~/tools/msys64/ucrt64/bin:$PATH"
PY="~/tools/crypto-ctf/venv/Scripts/python.exe"
FPLLL="~/tools/crypto-ctf/fplll-build/prefix3/bin/fplll.exe"
K="${K:-60}"
SLICE="${SLICE:-1200}"
cp -f real.fplll cur60b.fplll
for i in $(seq 1 24); do
  echo "=== s60 slice $i start $(date -u +%H:%M:%S)"
  "$FPLLL" -a bkz -b "$K" -nolll -f dd -bkzmaxtime "$SLICE" \
     < cur60b.fplll > next60b.fplll 2> err60b_$i.txt
  rc=$?
  if [ ! -s next60b.fplll ]; then echo "S60-SLICE-FAIL rc=$rc empty-out"; head -c 200 err60b_$i.txt; break; fi
  if [ -s next60b.fplll ]; then mv -f next60b.fplll cur60b.fplll; fi
  "$PY" -u scan_cli.py cur60b.fplll 2>&1 | tail -4
  if [ -f flag_origami-nns_ctf_20252025.txt ]; then echo FLAG-FILE-WRITTEN; break; fi
done
echo S60_CHAIN_DONE
