#!/bin/bash
cd "~/Practice_runs/cryptohack_org/challenge-221-cryptohack-meet_me_claw"
# wait for forward table
while [ ! -f fwd_tbl.pkl ]; do sleep 10; done
echo "PKL at $(date)" >> pipeline.log
python3 -u solve.py bwd >> pipeline.log 2>&1
echo "BWD done $(date)" >> pipeline.log
python3 -u final.py >> pipeline.log 2>&1
echo "FINAL done $(date)" >> pipeline.log
