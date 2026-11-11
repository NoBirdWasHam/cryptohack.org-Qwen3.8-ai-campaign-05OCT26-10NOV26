import hashlib, sys, ast

def gen_pubkey(secret: bytes, hasher=hashlib.sha256):
    def hash(m): return hasher(m).digest()
    state = hash(secret)
    pubkey = []
    for _ in range(len(hash(b'0')) * 4):
        pubkey.append(int.from_bytes(state, 'big'))
        state = hash(state)
    return pubkey

def solve_block(P, c, n_cols_bytes, venv=True):
    """P: list of 128 ints (pubkeys). c: list of 128 ints.
    Recover 32-byte big-endian block whose bytes 0..n_cols_bytes-1 may be
    nonzero ASCII (MSB=0), rest zero. Returns 32 bytes or None."""
    from fpylll import IntegerMatrix, BKZ
    bits = []
    for b in range(n_cols_bytes):
        base = (31 - b) * 8
        bits += [base + r for r in range(7)]  # exclude MSB (bit7)
    n = len(bits)
    m = len(c)
    # lattice rows: [2e_j | 2P_j | 0]; embedding row [1^n | 2c | C]
    C = 12
    D = n + m + 1
    M = IntegerMatrix(n + 1, D)
    for j, bit in enumerate(bits):
        M[j, j] = 2
        for i in range(m):
            M[j, n + i] = 2 * ((P[i] >> bit) & 1)
    for i in range(m):
        M[n, n + i] = 2 * c[i]
    for j in range(n):
        M[n, j] = 1
    M[n, n + m] = C
    BKZ.bkz(M, block_size=60)
    for r in range(M.nrows()):
        if abs(M[r, n + m]) == C:
            sign = 1 if M[r, n + m] == C else -1
            # embedding row minus sign*row = (t - v, 0)... recover error
            e = [int(M[r, k]) for k in range(n)]
            # row = sign*(t - v) style; try x_j = (1 - e_j)/2
            xs = []
            ok = True
            for j in range(n):
                val = (1 - sign * e[j]) / 2.0
                if abs(val - round(val)) > 1e-9 or not (0 <= round(val) <= 1):
                    ok = False
                    break
                xs.append(int(round(val)))
            if not ok:
                continue
            # verify P x == c
            for i in range(m):
                acc = 0
                for j, bit in enumerate(bits):
                    if xs[j]:
                        acc += (P[i] >> bit) & 1
                if acc != c[i]:
                    ok = False
                    break
            if ok:
                blk = bytearray(32)
                for j, bit in enumerate(bits):
                    if xs[j]:
                        blk[31 - bit // 8] |= (1 << (bit % 8))
                return bytes(blk)
    return None

def solve_all(P, enc):
    out = b""
    for bi, c in enumerate(enc):
        found = None
        ks = [32] if bi < len(enc) - 1 else range(31, -1, -1)
        for k in ks:
            blk = solve_block(P, c, k)
            if blk is not None:
                found = blk
                break
        if found is None:
            print(f"BLOCK {bi}: FAILED"); return None
        print(f"block{bi}: {found!r}")
        out += found
    return out

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "live"
    if mode == "test":
        # local fingerprint test with known flag
        secret = bytes.fromhex("ebdec93fb662a13f09047e7ae5bc12dd")
        # replicate encrypt from source
        A = gen_pubkey(secret)
        def happiness(x): return x - sum((x >> i) for i in range(1, x.bit_length()))
        def enc_msg(P, message):
            segment_len = len(P) // 4
            message += bytes(segment_len - len(message) % segment_len)
            eb = []
            for i in range(0, len(message), segment_len):
                blk = int.from_bytes(message[i:i+segment_len], 'big')
                eb.append([happiness(p & blk) for p in P])
            return eb
        flag = b"seki{this_is_a_dummy_flag_of_length_44_for_testing!!}"[:44]
        e = enc_msg(A, flag)
        res = solve_all(A, e)
        print("TEST FLAG:", res)
    else:
        data = open("live_output.txt", "rb").read().decode().strip().splitlines()
        secret = bytes.fromhex(data[0])
        enc = ast.literal_eval(data[1])
        A = gen_pubkey(secret)
        print("blocks:", len(enc), "eqs/block:", len(enc[0]))
        res = solve_all(A, enc)
        if res:
            print("RAW:", res)
            txt = res.rstrip(b"\x00").decode(errors="replace")
            print("FLAG:", txt)
            open("live_flag_candidate.txt", "w").write(txt)
