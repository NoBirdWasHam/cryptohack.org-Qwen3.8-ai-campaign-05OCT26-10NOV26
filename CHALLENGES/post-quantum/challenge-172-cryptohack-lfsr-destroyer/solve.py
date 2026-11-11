# lfsr-destroyer: 128-bit LFSR (taps [0,1,2,7]) + nonlinear filter over taps
# [0,16,32,64,96,127] with 27 monomials (degree 5). Chosen-plaintext oracle
# (encrypt zeros -> raw keystream). Recover key with z3 SAT, ask server for flag.
import json, socket, sys, time

_T = [0, 1, 2, 7]
_P = [0, 16, 32, 64, 96, 127]
_F = [[0,1,2,3],[0,1,2,4,5],[0,1,2,5],[0,1,2],[0,1,3,4,5],[0,1,3,5],[0,1,3],
      [0,1,4],[0,1,5],[0,2,3,4,5],[0,2,3],[0,3,5],[1,2,3,4,5],[1,2,3,4],
      [1,2,3,5],[1,2],[1,3,5],[1,3],[1,4],[1],[2,4,5],[2,4],[2],[3,4],[4,5],[4],[5]]

def keystream_bits(key_int, nbits, skip=256):
    s = [(key_int >> (127 - i)) & 1 for i in range(128)]
    # faithful re-implementation of the challenge class
    def clock2():
        x = [s[p] for p in _P]
        s[:] = s[1:] + [s[_T[0]] ^ s[_T[1]] ^ s[_T[2]] ^ s[_T[3]]]
        out = 1
        for m in _F:
            prod = 1
            for v in m:
                prod &= x[v]
            out ^= prod
        return out
    for _ in range(skip):
        clock2()
    return [clock2() for _ in range(nbits)]

def solve_key(ks_bits, T=None):
    import z3
    T = T or len(ks_bits)
    k = [z3.Bool(f"k{i}") for i in range(128)]
    # state as z3 expressions; simulate LFSR symbolically
    s = list(k)
    def clock_expr():
        x = [s[p] for p in _P]
        nb = s[_T[0]] ^ s[_T[1]] ^ s[_T[2]] ^ s[_T[3]]
        s[:] = s[1:] + [nb]
        acc = z3.Not(False)  # start with 1 (b=1)
        for m in _F:
            prod = x[m[0]]
            for v in m[1:]:
                prod = z3.And(prod, x[v])
            acc = z3.Xor(acc, prod)
        return acc
    for _ in range(256):
        clock_expr()
    solver = z3.Solver()
    for t in range(T):
        o = clock_expr()
        solver.add(o == (ks_bits[t] == 1))
    if solver.check() != z3.sat:
        return None
    m = solver.model()
    return sum(int(z3.is_true(m.evaluate(k[i]))) << (127 - i) for i in range(128))

def count_solutions(ks_bits, T, cap=4):
    import z3
    k = [z3.Bool(f"k{i}") for i in range(128)]
    s = list(k)
    def clock_expr():
        x = [s[p] for p in _P]
        nb = s[_T[0]] ^ s[_T[1]] ^ s[_T[2]] ^ s[_T[3]]
        s[:] = s[1:] + [nb]
        acc = z3.Not(False)
        for m in _F:
            prod = x[m[0]]
            for v in m[1:]:
                prod = z3.And(prod, x[v])
            acc = z3.Xor(acc, prod)
        return acc
    for _ in range(256):
        clock_expr()
    solver = z3.Solver()
    for t in range(T):
        o = clock_expr()
        solver.add(o == (ks_bits[t] == 1))
    sols = []
    while len(sols) < cap:
        if solver.check() != z3.sat:
            break
        m = solver.model()
        bits = [int(z3.is_true(m.evaluate(k[i]))) for i in range(128)]
        key = sum(b << (127 - i) for i, b in enumerate(bits))
        sols.append(key)
        solver.add(z3.Or([k[i] == (bits[i] == 0) for i in range(128)]))
    return sols

def selftest():
    import os, random
    for trial in range(3):
        key = random.getrandbits(128)
        ks = keystream_bits(key, 512)
        t0 = time.time()
        got = solve_key(ks, 512)
        print(f"trial {trial}: recovered={got == key} ({time.time()-t0:.1f}s)")
        assert got == key

def remote():
    host, port = "socket.cryptohack.org", 13404
    NBYTES = 512
    with socket.create_connection((host, port), timeout=30) as sock:
        f = sock.makefile("rwb")
        hello = f.readline()
        print("hello:", hello.decode(errors="replace").strip())
        def send(obj):
            f.write((json.dumps(obj) + "\n").encode())
            f.flush()
            line = f.readline()
            return json.loads(line.decode())
        r = send({"option": "encrypt", "plaintext": "00" * NBYTES})
        ks_hex = r["ciphertext"]
        print("got keystream bytes:", len(ks_hex) // 2)
        ks = [(int(ks_hex, 16) >> (8 * (NBYTES - 1 - i))) & 0xFF for i in range(NBYTES)]
        bits = [(b >> (7 - j)) & 1 for b in ks for j in range(8)]
        t0 = time.time()
        key = solve_key(bits, 512)
        print(f"solved key={key} ({time.time()-t0:.1f}s)")
        if key is None:
            print("UNSAT with 512 bits?!"); return
        # sanity: keystream matches
        assert keystream_bits(key, 512) == bits[:512]
        r = send({"option": "get_flag", "key": str(key)})
        print("flag resp:", r)
        if "flag" in r:
            open("flag_lfsr-destroyer.txt", "w").write(r["flag"])

if __name__ == "__main__":
    if "selftest" in sys.argv:
        selftest()
    else:
        remote()
