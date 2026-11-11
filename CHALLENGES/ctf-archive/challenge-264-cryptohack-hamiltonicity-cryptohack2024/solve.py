# Hamiltonicity 1 (sigma-hamiltonicity) — break the per-round Fiat-Shamir.
#
# Vuln: the verifier derives each round's challenge bit as
#   FS_state = sha256(str(comm_params) || FS_state || str(A entries))
#   challenge = FS_state[-1] & 1
# i.e. the challenge depends ONLY on the prover's commitment matrix A.
# Pedersen commitments are re-randomizable (c*h2^r' opens to the same
# message with r+r'), so the prover can grind fresh randomness until the
# challenge bit is 0, then always answer the "reveal permutation" branch
# (which is trivially satisfiable for a permuted G). Soundness 1/2 per
# round collapses to 1 because the prover picks the challenge.
import json, random, socket, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hamiltonicity import (pedersen_commit, pedersen_open, commit_to_graph,
                           open_graph, permute_graph, hash_committed_graph,
                           comm_params)

HOST, PORT = "archive.cryptohack.org", 14635
N = 5
G = [
    [0,0,1,0,0],
    [1,0,0,0,0],
    [0,1,0,0,0],
    [0,0,0,0,1],
    [0,0,0,1,0],
]
NUMROUNDS = 128

def commit_permuted(state):
    """Commit to a random permutation of G; grind randomness until the
    FS challenge bit for this round is 0."""
    perm = list(range(N)); random.shuffle(perm)
    Gp = permute_graph(G, N, perm)
    tries = 0
    while True:
        A, openings = commit_to_graph(Gp, N)
        st = hash_committed_graph(A, state, comm_params)
        tries += 1
        if st[-1] & 1 == 0:
            return A, openings, perm, st, tries

def main():
    s = socket.create_connection((HOST, PORT), timeout=30)
    f = s.makefile("rwb")
    def recv_until(b):
        data = b""
        while not data.endswith(b):
            chunk = f.read(1)
            if not chunk:
                raise RuntimeError("EOF: %r" % data)
            data += chunk
        return data
    def sendline(x):
        f.write(x + b"\n"); f.flush()

    print(recv_until(b"hamiltonian cycle!").decode(errors="replace"))
    FS_state = b""
    total_tries = 0
    for i in range(NUMROUNDS):
        A, openings, perm, FS_state, tries = commit_permuted(FS_state)
        total_tries += tries
        # challenge bit is 0 -> z = [permutation, openings of everything]
        z = [perm, openings]
        recv_until(b"send fiat shamir proof: ")
        sendline(json.dumps({"A": A, "z": z}).encode())
        resp = f.readline()
        if b"accepted" not in resp:
            print("FAILED round", i, resp)
            return None
        if i % 16 == 0 or i == NUMROUNDS-1:
            print(f"round {i} ok (grinds so far {total_tries})")
    # after 128 accepted rounds the server prints the flag
    rest = f.read()
    print(rest.decode(errors="replace"))
    flag = None
    for tok in rest.split():
        t = tok.decode(errors="replace") if isinstance(tok, bytes) else tok
        if t.startswith("crypto{") and t.endswith("}"):
            flag = t
    if flag:
        out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "flag_hamiltonicity-cryptohack2024.txt")
        open(out, "w").write(flag + "\n")
        print("FLAG SAVED:", flag)
    return flag

if __name__ == "__main__":
    main()
