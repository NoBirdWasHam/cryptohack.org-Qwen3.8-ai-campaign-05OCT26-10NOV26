#!/bin/bash
# challenge-273 leet_universe — owner-ordered ECM ladder on R (opened 2026-11-06, NOTHING GETS CLOSED)
# Light job: single thread, -maxmem 1024 (~8 MB peak measured). Stop conditions: factor found, or
# all stages exhausted -> LADDER_EXHAUSTED logged (door stays OPEN; ladder re-runnable).
cd ~/Practice_runs/cryptohack_org/challenge-273-cryptohack-leet_universe-imaginaryctf_da
ECM=~/tools/msys64/ucrt64/bin/ecm.exe
LOG=ecm_ladder_273.log
R=$(grep -oE "[0-9]{200,}" _R.txt | head -1)   # R stored by ECM probe as _R.txt
if [ -z "$R" ]; then echo "NO_R_CONSTANTS" >> $LOG; exit 1; fi
for st in "1100000 50000" "4300000 25000" "11000000 8000" "43000000 2000"; do
  B1=${st% *}; N=${st#* }
  echo "=== STAGE B1=$B1 n=$N $(date -u +%F_%T)Z" >> $LOG
  i=0
  B2=$((B1*100))
  while [ $i -lt $N ]; do
    # 7.0.7 usage: ecm [opts] B1 B2 < number-file  (number on STDIN; positional number = "too large B1" silent no-op)
    out=$(printf '%s\n' "$R" | "$ECM" -maxmem 1024 "$B1" "$B2" 2>&1)
    rc=$?
    if echo "$out" | grep -qiE "found.*factor"; then
      echo "$out" >> $LOG; echo "ECM273_FACTOR $(date -u +%F_%T)Z" >> $LOG
      echo "$out" > ECM273_FACTOR.txt; exit 0
    fi
    i=$((i+1))
    if [ $((i % 50)) -eq 0 ]; then echo "stage $B1 curves=$i/$N $(date -u +%F_%T)Z" >> $LOG; fi
  done
  echo "=== STAGE B1=$B1 done $(date -u +%F_%T)Z" >> $LOG
done
echo "LADDER_EXHAUSTED $(date -u +%F_%T)Z (door remains OPEN)" >> $LOG
