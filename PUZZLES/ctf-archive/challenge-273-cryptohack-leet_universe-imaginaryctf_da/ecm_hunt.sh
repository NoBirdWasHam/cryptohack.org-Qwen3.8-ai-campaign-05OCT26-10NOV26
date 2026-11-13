#!/bin/bash
# Persistent 1-thread GMP-ECM hunt on R (leet_universe). Tier-1: B1=11e6/B2=1.1e9 (~30-digit class).
# Discovered factors -> factor_found.txt (get_flag2.py pipeline consumes it per AAR runbook).
ECM=~/tools/msys64/ucrt64/bin/ecm.exe
CD="~/Practice_runs/cryptohack_org/challenge-273-cryptohack-leet_universe-imaginaryctf_da"
WCD="~/Practice_runs/cryptohack_org/challenge-273-cryptohack-leet_universe-imaginaryctf_da"
R=$(tr -d ' \r\n' < "$CD/_R.txt")
LOG="$CD/ecm_hunt_t1.log"
SEED=$(date +%s)
echo "=== hunt start $(date) seed=$SEED tier B1=11e6 B2=1.1e9 ===" >> "$LOG"
while :; do
  SEED=$((SEED+1))
  OUT=$(printf '%s\n' "$R" | "$ECM" -maxmem 1024 11000000 1100000000 2>>"$LOG")
  echo "seed=$SEED $OUT" >> "$LOG"
  if echo "$OUT" | grep -qi "found"; then
    for CAND in $(echo "$OUT" | grep -oE "[0-9]{6,}"); do
      python3 -c "
import gmpy2
R = int(open('$WCD/_R.txt').read().strip())
c = int('$CAND')
if R % c == 0 and gmpy2.is_prime(c):
    open('$WCD/factor_found.txt','a').write(str(c)+'\n')
    print('VERIFIED PRIME FACTOR', c)
else:
    print('candidate rejected', len('$CAND'), 'digits')
" >> "$LOG" 2>&1
    done
    echo "FACTOR FOUND seed=$SEED: $OUT" >> "$LOG"
    echo "found in step (verified candidates processed $(date))"
  fi
done
