# t280_mk_noprune.py — unpruned twin of prefix3 default.json: same block sizes /
# gh_factor entries / preprocessing recursion, but all pruning coefficients = 1.0.
import json
SRC = r"~/tools/crypto-ctf/fplll-build/prefix3/share/fplll/strategies/default.json"
DST = r"~/Practice_runs/cryptohack_org/challenge-280-cryptohack-origami-nns_ctf_20252025/t280_strat_noprune.json"
d = json.load(open(SRC))
for strat in d:
    for entry in strat.get("pruning_parameters", []):
        entry[1] = [1.0] * len(entry[1])
        entry[2] = 1.0
json.dump(d, open(DST, "w"))
print("wrote", DST, "blocks:", len(d))
