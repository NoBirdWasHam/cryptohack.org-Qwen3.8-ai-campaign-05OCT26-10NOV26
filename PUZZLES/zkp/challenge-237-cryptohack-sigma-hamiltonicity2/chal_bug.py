from hamiltonicity import pedersen_commit, pedersen_open
from hamiltonicity import commit_to_graph, open_graph, permute_graph
from hamiltonicity import hash_committed_graph, testcycle, check_graph
from hamiltonicity import comm_params
import json
import os

FLAG = "localflag{ok}".encode()

numrounds = 128
LocalTest = True

if LocalTest:
    # Graph with Hamiltonian cycle (0,4) (4,2) (2,3) (3,1) (1,0)
    N = 5
    G = [
        [0,1,1,0,1],
        [1,0,0,0,0],
        [0,0,0,1,0],
        [0,1,1,0,0],
        [1,0,1,1,0]
    ]

else: 
    # Graph with no hamiltonian cycle
    N = 5
    G = [
        [0,0,1,0,0],
        [1,0,0,0,0],
        [0,1,0,0,0],
        [0,0,0,0,1],
        [0,0,0,1,0]
    ]

print(f'prove to me that G has a hamiltonian cycle!')

FS_state = b''

A_vals = []
z_vals = []
for i in range(numrounds):
    payload = json.loads(input(b"send fiat shamir proof: "))
    A = payload["A"]
    z = payload["z"]

    check_graph(A,N)

    A_vals.append(A)
    z_vals.append(z)    

print("computing fiat shamir challenge")
for i in range(numrounds):
    FS_state = hash_committed_graph(A_vals[i], FS_state, comm_params)

challenge_bits = bin(int.from_bytes(FS_state, 'big'))[-numrounds:]

for i in range(numrounds):
    print(f"checking round {i}")
    # HYPOTHESIZED BUG: challenge left as a STRING -> bool("0") is True
    # -> rounds whose bit is "0" also take the bit-1 branch.
    challenge = challenge_bits[i]
    print(f"challenge bit is {challenge}")
    A = A_vals[i]
    z = z_vals[i]
    if challenge:
        cycle, openings = z
        if not testcycle(A, N, cycle, openings):
            print("your proof didn't verify :(")
            exit()
        else:
            print("accepted")
    else:
        permutation, openings = z
        G_permuted = open_graph(A,N, openings)
        G_test = permute_graph(G, N, permutation)
        if G_permuted == G_test:
            print("accepted")
        else:
            print("your proof didn't verify :()")
            exit()


print("you've convinced me it has a hamiltonian path! Cool!")
print(FLAG)
