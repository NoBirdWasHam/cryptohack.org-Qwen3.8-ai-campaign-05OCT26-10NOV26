#!/usr/bin/env bash
# t280_chain70p_dd.sh — ESCALATION chain: pruned+recursive BKZ-70 dd on the REAL
# origami lattice. Fixes the flaw found 2026-11-07: without -s, fplll builds
# EmptyStrategy = unpruned, non-recursive (what chain60c runs). This chain passes
# -s default.json (pruning tables + 70<-50 preprocessing recursion = more frequent
# time-check boundaries). Own checkpoints; NEVER touches cur60b/next60b/chain60c.
# RSS cap 2 GB per process per host rule.
cd "~/Practice_runs/cryptohack_org/challenge-280-cryptohack-origami-nns_ctf_20252025" || exit 1
FPLLL="~/tools/crypto-ctf/fplll-build/prefix3/bin/fplll.exe"
SDEF="~/tools/crypto-ctf/fplll-build/prefix3/share/fplll/strategies/default.json"
PY="~/tools/crypto-ctf/venv/Scripts/python.exe"
export PATH="~/tools/msys64/ucrt64/bin:$PATH"
TAG="${TAG:-70p}"
K="${K:-70}"
SLICE="${SLICE:-43200}"   # NOTE: fplll checks max_time only at TOUR boundaries
NSL="${NSL:-12}"          # (bkz.cpp:588) => a slice = >=1 full tour, ~15-20h est
RSS_CAP_MB="${RSS_CAP_MB:-2000}"
FAILS=0
[ -s t280_${TAG}_cur.fplll ] || cp -f cur60b.fplll t280_${TAG}_cur.fplll   # resume-safe seed from best checkpoint
for i in $(seq 1 "$NSL"); do
  echo "=== s${TAG} slice $i start $(date -u +%F_%H:%M:%S)"
  "$FPLLL" -a bkz -b "$K" -nolll -f dd -s "$SDEF" -bkzmaxtime "$SLICE" \
     < t280_${TAG}_cur.fplll > t280_${TAG}_next.fplll 2> t280_${TAG}_err_$i.txt &
  FP=$!
  RSSHIT=0
  while kill -0 $FP 2>/dev/null; do
    R=$(powershell.exe -NoProfile -Command "(Get-Process -Id $FP -ErrorAction SilentlyContinue).PrivateMemorySize64/1MB" 2>/dev/null | tr -d '\r')
    R=${R%.*}
    if [ -n "$R" ] && [ "$R" -gt "$RSS_CAP_MB" ] 2>/dev/null; then
      echo "RSS-CAP ${R}MB > ${RSS_CAP_MB}MB -> killing slice"; kill -9 $FP; RSSHIT=1; break
    fi
    sleep 30
  done
  wait $FP; rc=$?
  if [ "$RSSHIT" = 1 ]; then
    echo "S7P-SLICE-FAIL rc=rss cap retry $((FAILS+1))/5"
    FAILS=$((FAILS+1)); [ $FAILS -ge 5 ] && { echo S7P_CHAIN_ABORTED; exit 2; }; sleep 30; continue
  fi
  if [ ! -s t280_${TAG}_next.fplll ]; then
    echo "S7P-SLICE-FAIL rc=$rc empty-out (retry $((FAILS+1))/5)"
    head -c 200 t280_${TAG}_err_$i.txt
    FAILS=$((FAILS+1))
    if [ $FAILS -ge 5 ]; then echo S7P_CHAIN_ABORTED; exit 2; fi
    sleep 30; continue
  fi
  FAILS=0
  mv -f t280_${TAG}_next.fplll t280_${TAG}_cur.fplll
  "$PY" -u scan_cli.py t280_${TAG}_cur.fplll 2>&1 | tail -4
  if [ -f flag_origami-nns_ctf_20252025.txt ]; then echo FLAG-FILE-WRITTEN; break; fi
done
echo S7P_CHAIN_EXHAUSTED
