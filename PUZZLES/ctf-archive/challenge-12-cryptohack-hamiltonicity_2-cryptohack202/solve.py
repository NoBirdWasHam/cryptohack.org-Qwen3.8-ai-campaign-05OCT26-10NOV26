# Honest Fiat-Shamir prover for Hamiltonicity ZKP (example.py logic, raw sockets).
# Works if the server's hidden graph HAS a hamiltonian cycle (LocalTest=True style).
import json, random, socket, sys, time
from hamiltonicity import commit_to_graph, open_graph, permute_graph
from hamiltonicity import hash_committed_graph, comm_params, get_r_vals

HOST, PORT = "archive.cryptohack.org", 34597
if len(sys.argv) > 3:
    HOST, PORT = sys.argv[1], int(sys.argv[2])
LOCAL = len(sys.argv) > 4 and sys.argv[4] == "local"
if LOCAL:
    HOST, PORT = "127.0.0.1", 9999

numrounds = 128
N = 5
cycle = [(0, 4), (4, 2), (2, 3), (3, 1), (1, 0)]
G = [
    [0, 1, 1, 0, 1],
    [1, 0, 0, 0, 0],
    [0, 0, 0, 1, 0],
    [0, 1, 1, 0, 0],
    [1, 0, 1, 1, 0],
]

A_vars, opening_vars, permutation_vars = [], [], []
for i in range(numrounds):
    A, openings = commit_to_graph(G, N)
    permutation = list(range(N))
    random.shuffle(permutation)
    A_permuted = permute_graph(A, N, permutation)
    assert permute_graph(G, N, permutation) == open_graph(A_permuted, N, permute_graph(openings, N, permutation))
    A_vars.append(A_permuted)
    opening_vars.append(openings)
    permutation_vars.append(permutation)

FS_state = b''
for i in range(numrounds):
    FS_state = hash_committed_graph(A_vars[i], FS_state, comm_params)
challenge_bits = bin(int.from_bytes(FS_state, 'big'))[-numrounds:]

proofs = []
for i in range(numrounds):
    A = A_vars[i]; openings = opening_vars[i]; permutation = permutation_vars[i]
    if int(challenge_bits[i]):
        permuted_cycle = [[permutation.index(x[0]), permutation.index(x[1])] for x in cycle]
        rvals = get_r_vals(openings, N, cycle)
        proofs.append(json.dumps({"A": A, "z": [permuted_cycle, rvals]}))
    else:
        proofs.append(json.dumps({"A": A, "z": [permutation, permute_graph(openings, N, permutation)]}))

s = socket.create_connection((HOST, PORT), timeout=15)
buf = b''
def readuntil(tok, timeout=30):
    global buf
    end = time.time() + timeout
    while tok not in buf and time.time() < end:
        s.settimeout(max(0.1, end - time.time()))
        try:
            d = s.recv(65536)
        except socket.timeout:
            break
        if not d:
            break
        buf += d
    return buf

readuntil(b"send fiat shamir proof: ")
for i in range(numrounds):
    s.sendall(proofs[i].encode() + b"\n")
    readuntil(b"send fiat shamir proof: ", timeout=20)
print("--- all 128 sent; waiting for verdicts ---")
s.settimeout(60)
try:
    while True:
        d = s.recv(65536)
        if not d:
            break
        print(d.decode(errors="replace"), end="")
except Exception as e:
    print("<recv end>", e)
