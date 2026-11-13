#!/bin/bash
# One heavy job at a time: staged BKZ, up to 2 attempts per stage, checkpoint-resume.
cd "~/Practice_runs/cryptohack_org/challenge-280-cryptohack-origami-nns_ctf_20252025"
PY="~/tools/crypto-ctf/venv/Scripts/python.exe"
for k in 20 25 30 40; do
  if [ -f "M_$k.txt.gz" ] || [ -f flag_origami-nns_ctf_20252025.txt ]; then continue; fi
  for try in 1 2; do
    echo "=== stage k=$k attempt=$try $(date +%T)"
    "$PY" solve7.py "$k" && break
    code=$?
    echo "=== k=$k attempt=$try exit=$code $(date +%T)"
    [ -f flag_origami-nns_ctf_20252025.txt ] && exit 0
    sleep 5
  done
done
echo "ALL_DONE $(date +%T)"
