#!/usr/bin/env bash
# t280_fpy_probe.sh — run fpylll in-process BKZ probes with hard watchdogs
cd "~/Practice_runs/cryptohack_org/challenge-280-cryptohack-origami-nns_ctf_20252025" || exit 1
PY="~/tools/crypto-ctf/venv/Scripts/python.exe"
: > probe_fpy_rc.txt
for M in "bkz20 20" "bkz64 64" "embed64 64"; do
  set -- $M
  "$PY" -u probe_fpy_t280.py "$1" "$2" > "probe_fpy_$1.log" 2>&1 &
  P=$!
  ( sleep 150; kill -9 $P 2>/dev/null ) &
  WP=$!
  wait $P; rc=$?
  kill $WP 2>/dev/null
  echo "MODE=$1 rc=$rc" >> probe_fpy_rc.txt
done
echo FPY_PROBES_DONE >> probe_fpy_rc.txt
