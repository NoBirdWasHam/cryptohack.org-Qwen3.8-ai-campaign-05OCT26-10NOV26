#!/usr/bin/env bash
# Retry solve.py against the LIVE service; one connection per attempt, polite spacing.
# Exit early on success (exit 0 from solve.py => flag printed + flag_local.json written).
cd "$(dirname "$0")"
PY="~/tools/crypto-ctf/venv/Scripts/python.exe"
LOG=retry_live_2026-11-07.log
ATTEMPTS=${1:-10}
SLEEP=${2:-60}
for i in $(seq 1 "$ATTEMPTS"); do
  TS=$(date +"%Y-%m-%dT%H:%M:%S%z")
  echo "=== attempt $i at $TS" >> "$LOG"
  "$PY" solve.py archive.cryptohack.org 21970 >> "$LOG" 2>&1
  RC=$?
  echo "--- attempt $i rc=$RC" >> "$LOG"
  if [ $RC -eq 0 ]; then
    echo "SUCCESS on attempt $i" >> "$LOG"
    echo "RETRYLIVE_RESULT=success attempt=$i"
    exit 0
  fi
  sleep "$SLEEP"
done
echo "RETRYLIVE_RESULT=exhausted attempts=$ATTEMPTS"
exit 1
