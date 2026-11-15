#!/bin/bash
# launch_walker3.sh — production loop: walk -> fire -> harvest+submit, chained in one process.
# FILE-NAMING SAFETY RULE: harvest3.py is invoked ONLY on files matching found_PROD*.txt written
# by walker3 mode 0; self-tests live under ./selftest/ and can never trigger a live submission.
cd "$(dirname "$0")"
PY="~/tools/crypto-ctf/venv/Scripts/python.exe"
while true; do
    ./walker3.exe 0 0 0
    rc=$?
    f=$(ls found_PROD_*.txt 2>/dev/null | sort -V | tail -1)
    if [ -n "$f" ]; then
        echo "[$(date)] chain: walker exit=$rc -> harvest3.py $f"
        "$PY" harvest3.py "$f"
        h=$?
        [ $h -eq 0 ] && exit 0        # flag captured, submitted
        echo "[$(date)] harvest failed rc=$h, restarting walk"
    else
        echo "[$(date)] walker stopped rc=$rc with no fire, restarting walk"
    fi
    sleep 5
done
