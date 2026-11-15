#!/bin/bash
# RUN 2026-11-02: final 129-bit DLP in F_q, corrected invocation
# (params.p40 absolute path; NCPUS_FAKE=2 -> cado believes 2 cores: honors host-load rule)
export NCPUS_FAKE=2
export PYTHONPATH=~/tools/cado-nfs/scripts
cd ~/tools/cado-nfs/build/$(hostname) || exit 9
python3 -u cado-nfs.py -dlp \
  --parameters ~/tools/cado-nfs/parameters/dlp/params.p40 \
  --workdir ~/dlp_work \
  -ell 103054661089505908941391709972776183181 \
  target=3321385147483577619458640425416114852,163720576515724884349491368582227595136 \
  206109322179011817882783419945552366363 \
  tasks.sieve.allow_largesq=true \
  > ~/dlp_srv.log 2>&1
echo DLP_EXIT=$? >> ~/dlp_srv.log
