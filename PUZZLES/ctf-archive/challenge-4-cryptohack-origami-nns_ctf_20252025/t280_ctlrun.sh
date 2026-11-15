#!/usr/bin/env bash
# t280_ctlrun.sh — CONTROL real-shape planted toy through the SAME runner path as real.
# Sequential (one fplll at a time), per-tour external timeout 840 s.
cd "~/Practice_runs/cryptohack_org/challenge-280-cryptohack-origami-nns_ctf_20252025" || exit 1
FPLLL="~/tools/crypto-ctf/fplll-build/prefix3/bin/fplll.exe"
SDEF="~/tools/crypto-ctf/fplll-build/prefix3/share/fplll/strategies/default.json"
PY="~/tools/crypto-ctf/venv/Scripts/python.exe"
export PATH="~/tools/msys64/ucrt64/bin:$PATH"

tour() { # $1 name  $2 beta
  local N=$1 B=$2
  local CUR="t280_ctl_${N}.fplll"
  local NEXT="t280_ctl_${N}.next.fplll"
  echo "=== ctl $N B$B start $(date +%H:%M:%S)"
  timeout 890 "$FPLLL" -a bkz -b "$B" -nolll -f dd -s "$SDEF" -bkzmaxloops 1 < "$CUR" > "$NEXT" 2> "t280_ctl_${N}_b${B}.err"
  local rc=$?
  local NR; NR=$(grep -ao "\[" "$NEXT" | wc -l)
  if [ "$NR" -gt 20 ]; then mv -f "$NEXT" "$CUR"; echo "ctl $N B$B DONE rc=$rc rows=$NR at $(date +%H:%M:%S)"; else echo "ctl $N B$B NOOUT rc=$rc rows=$NR"; fi
}

# level-3 (dim 128) first — fast
[ -f t280_ctl_ppp.fplll ] || cp -f t280_ctl_ctlppp.fplll t280_ctl_ppp.fplll
[ -f t280_ctl_ppm.fplll ] || cp -f t280_ctl_ctlppm.fplll t280_ctl_ppm.fplll
for B in 40 50 60; do tour ppp $B; tour ppm $B; done
"~/tools/crypto-ctf/venv/Scripts/python.exe" -u t280_ctlscan2.py t280_ctl_ctlpp.fplll t280_ctl_ctlpm.fplll t280_ctl_ppp.fplll t280_ctl_ppm.fplll
# level-2 (dim 256) ladder mirroring bheavy betas (cur files already at B50/B60 from pass 1)
for B in 65 65; do tour ctlpp $B; tour ctlpm $B; done
"$PY" -u t280_ctlscan2.py t280_ctl_ctlpp.fplll t280_ctl_ctlpm.fplll t280_ctl_ppp.fplll t280_ctl_ppm.fplll
for B in 65; do tour ctlpp $B; tour ctlpm $B; done
"$PY" -u t280_ctlscan2.py t280_ctl_ctlpp.fplll t280_ctl_ctlpm.fplll t280_ctl_ppp.fplll t280_ctl_ppm.fplll
echo CTLRUN_END
