#!/usr/bin/env python
# no_difference: hash is GF(2)-linear (permute = bit transpose, SBOX affine).
# Find nonzero d with M(d1,d2)=0 for 2-block messages -> collision pair.
import socket, json, re

SBOX = [
    0xf0, 0xf3, 0xf1, 0x69, 0x45, 0xff, 0x2b, 0x4f, 0x63, 0xe1, 0xf3, 0x71, 0x44, 0x1b, 0x35, 0xc8,
    0xbe, 0xc0, 0x1a, 0x89, 0xec, 0x3e, 0x1d, 0x3a, 0xe3, 0xbe, 0xd3, 0xcf, 0x20, 0x4e, 0x56, 0x22,
    0xe4, 0x43, 0x9a, 0x6f, 0x43, 0xa9, 0x87, 0x37, 0xec, 0x2, 0x3b, 0x8a, 0x7a, 0x13, 0x7e, 0x79,
    0xcc, 0x92, 0xd7, 0xd1, 0xff, 0x5e, 0xe2, 0xb1, 0xc9, 0xd3, 0xda, 0x40, 0xfb, 0x80, 0xe6, 0x30,
    0x79, 0x1a, 0x28, 0x13, 0x1f, 0x2c, 0x73, 0xb9, 0x71, 0x9e, 0xa6, 0xd5, 0x30, 0x84, 0x9d, 0xa1,
    0x9b, 0x6d, 0xf9, 0x8a, 0x3d, 0xe9, 0x47, 0x15, 0x50, 0xb, 0xe2, 0x3d, 0x3f, 0x1, 0x59, 0x9b,
    0x85, 0xe4, 0xe5, 0x90, 0xe2, 0x2d, 0x80, 0x5e, 0x6b, 0x77, 0xa1, 0x10, 0x99, 0x72, 0x7f, 0x86,
    0x1f, 0x25, 0xa3, 0xea, 0x57, 0x5f, 0xc4, 0xc6, 0x7d, 0x7, 0x15, 0x90, 0xcb, 0x8c, 0xec, 0x11,
    0x9b, 0x59, 0x1, 0x3f, 0x3d, 0xe2, 0xb, 0x50, 0x15, 0x47, 0xe9, 0x3d, 0x8a, 0xf9, 0x6d, 0x9b,
    0xa1, 0x9d, 0x84, 0x30, 0xd5, 0xa6, 0x9e, 0x71, 0xb9, 0x73, 0x2c, 0x1f, 0x13, 0x28, 0x1a, 0x79,
    0x11, 0xec, 0x8c, 0xcb, 0x90, 0x15, 0x7, 0x7d, 0xc6, 0xc4, 0x5f, 0x57, 0xea, 0xa3, 0x25, 0x1f,
    0x86, 0x7f, 0x72, 0x99, 0x10, 0xa1, 0x77, 0x6b, 0x5e, 0x80, 0x2d, 0xe2, 0x90, 0xe5, 0xe4, 0x85,
    0x22, 0x56, 0x4e, 0x20, 0xcf, 0xd3, 0xbe, 0xe3, 0x3a, 0x1d, 0x3e, 0xec, 0x89, 0x1a, 0xc0, 0xbe,
    0xc8, 0x35, 0x1b, 0x44, 0x71, 0xf3, 0xe1, 0x63, 0x4f, 0x2b, 0xff, 0x45, 0x69, 0xf1, 0xf3, 0xf0,
    0x30, 0xe6, 0x80, 0xfb, 0x40, 0xda, 0xd3, 0xc9, 0xb1, 0xe2, 0x5e, 0xff, 0xd1, 0xd7, 0x92, 0xcc,
    0x79, 0x7e, 0x13, 0x7a, 0x8a, 0x3b, 0x2, 0xec, 0x37, 0x87, 0xa9, 0x43, 0x6f, 0x9a, 0x43, 0xe4,
]
# verify affinity: S(x)^S(y)^S(0) == S(x^y^0)?
assert all(SBOX[x ^ y ^ 0] == (SBOX[x] ^ SBOX[y] ^ SBOX[0]) for x in range(256) for y in range(256) if True) , "not affine"
assert SBOX[0] == 0, f"SBOX[0]={SBOX[0]}"
print("SBOX affine with S(0)=0 confirmed")

# state as 64-bit int: byte i at bits 8i..8i+7
def permute64(v):
    # byte i bit j -> byte j bit i
    out = 0
    for i in range(8):
        x = (v >> (8*i)) & 0xFF
        for j in range(8):
            if (x >> j) & 1:
                out |= 1 << (8*j + i)
    return out
def substitute64(v):
    out = 0
    for i in range(8):
        out |= SBOX[(v >> (8*i)) & 0xFF] << (8*i)
    return out
def round64(v):
    return substitute64(permute64(v))

# matrix columns: images of basis vectors
COLS = [round64(1 << b) for b in range(64)]
def apply_mat(vec):  # vec: 64-bit int over basis
    out = 0
    for b in range(64):
        if (vec >> b) & 1:
            out ^= COLS[b]
    return out

def apply_matN(vec, n):
    for _ in range(n):
        vec = apply_mat(vec)
    return vec

# output function: upper half bytes 4..7 of state after 16 rounds (twice)
def out_bits(vec):
    # after 16 rounds: state = M^16 v ; output = upper48.. first output = state[4:8] of that state
    return (vec >> 32) & 0xFFFFFFFF

# For 2-block msg: v = d1 e + d2 (e XOR into upper half). Need M^16(d1 e + d2) upper32 == 0
# Build 64 x 64 matrix N: rows = out bits of M^16 applied to basis combos.
# basis: e_j (block2 diff) and f_j = E_j e (block1 diff byte j)
E_e = 0x00000000FFFFFFFF0000000000000000  # bytes4..7 = FF? no: byte j of block -> bit 8*(4+j)
def evec(j):  # block2 basis byte j (bits 32+8j..39+8j)
    return 1 << (32 + 8*j)
def fvec(j):  # block1 basis byte j XORed into state byte 4+j
    return 1 << (32 + 8*j)
# NOTE both blocks XOR into the SAME state half: block byte j -> state byte 4+j.
# So total diff = (d1 XOR d2) into upper half. => only 32-dim image! Need >=3 blocks? NO:
# diff of two 2-block msgs: state diff = (d1^d2) in upper half — 32-dim space.
# Solve: find nonzero u (4 bytes) with out(M^16 (u in upper half)) == 0 : 32 unknowns, 32 equations.
# Generically kernel=0 -> use 3 blocks: diffs u1,u2,u3 (96 unknowns) -> kernel >= 64.
def solve_kernel(nblocks):
    # unknowns: u_b bytes (nblocks*32 bits). equations: 32 output bits.
    rows = []  # each: (mask over unknowns, rhs=0)
    # build matrix columns: contribution of unknown k (block b byte j bit t)
    cols = []
    for b in range(nblocks):
        for t in range(32):
            v = 1 << (32 + t)
            for _ in range(nblocks - 1 - b):  # inter-block rounds after block b
                v = apply_mat(v)
            v = apply_matN(v, 16)
            cols.append((b, out_bits(v)))
    # gaussian over 32-bit outputs
    piv = {}
    eqs = []
    for k, (b, ob) in enumerate(cols):
        # equation bits: for each output bit r: coefficient
        pass
    # Build 32 equations: eq r: XOR over k of bit_r(col_k)*x_k = 0
    # unknown index k = b*32+t
    nk = nblocks * 32
    # represent each unknown as 32-bit column; find kernel of the 32 x nk matrix
    # do elimination on rows = equations: row r has bits over unknowns
    rowsr = []
    for r in range(32):
        m = 0
        for k, (b, ob) in enumerate(cols):
            if (ob >> r) & 1:
                m |= 1 << k
        rowsr.append(m)
    # solve for kernel: standard
    pivots = {}
    for r, m in enumerate(rowsr):
        mm = m
        while mm:
            j = mm.bit_length() - 1
            if j in pivots:
                mm ^= pivots[j]
            else:
                pivots[j] = mm
                break
    free = [k for k in range(nk) if k not in pivots]
    if not free:
        return None
    k = free[0]
    x = 1 << k
    for j in sorted(pivots):
        pm = pivots[j]
        # ensure equation j satisfied: x_j = parity(pm & x) (since rhs 0)
        if bin(pm & x).count("1") & 1:
            x |= 1 << j
        else:
            x &= ~(1 << j)
    # verify
    tot = 0
    for kk in range(nk):
        if (x >> kk) & 1:
            b, ob = cols[kk]
            tot ^= ob
    assert tot == 0, "kernel verify failed"
    # build messages
    ub = []
    for b in range(nblocks):
        u = 0
        for t in range(32):
            if (x >> (b*32 + t)) & 1:
                u |= 1 << t
        ub.append(u)
    a = bmsg = b""
    for b in range(nblocks):
        a = bytes(4) + a
        bb = ub[b].to_bytes(4, "big")
        a = a  # placeholder
    # message A = zeros; message B = blocks ub (diff applied to B)
    B = b"".join(ub[b].to_bytes(4, "big") for b in range(nblocks))
    A = b"\x00" * (4 * nblocks)
    assert A != B
    return A, B

def local_hash(data):
    state = [16, 32, 48, 80, 80, 96, 112, 128]
    v = 0
    for i in range(8):
        v |= state[i] << (8*i)
    v = v  # affine constant; but linearity of DIFFERENCES unaffected
    def rnd(v):
        return substitute64(permute64(v))
    for i in range(0, len(data), 4):
        blk = int.from_bytes(data[i:i+4], "big")
        # block byte j -> state byte 4+j (big-endian block: data[i] is byte0)
        up = 0
        for j in range(4):
            up |= ((blk >> (8*(3-j))) & 0xFF) << (8*(4+j))
        v ^= up
        v = rnd(v)
    for _ in range(16):
        v = rnd(v)
    o1 = (v >> 32) & 0xFFFFFFFF
    v = rnd(v)
    return o1.to_bytes(4, "big") + ((v >> 32) & 0xFFFFFFFF).to_bytes(4, "big")

for nb in (2, 3):
    r = solve_kernel(nb)
    if r:
        A, B = r
        ha, hb = local_hash(A), local_hash(B)
        print(f"nb={nb} A={A.hex()} B={B.hex()} ha={ha.hex()} hb={hb.hex()} match={ha==hb}")
        if ha == hb and A != B:
            s = socket.create_connection(("socket.cryptohack.org", 13395), timeout=15)
            s.settimeout(10)
            buf = b""
            while b"}" not in buf and b"\n" not in buf:
                d = s.recv(4096)
                if not d: break
                buf += d
                if len(buf) > 200: break
            s.sendall((json.dumps({"a": A.hex(), "b": B.hex()}) + "\n").encode())
            resp = b""
            try:
                while True:
                    d = s.recv(4096)
                    if not d: break
                    resp += d
            except Exception:
                pass
            print("SERVER:", resp.decode(errors="replace"))
            m = re.search(r"crypto\{[^}]+\}", resp.decode(errors="replace"))
            if m:
                open("flag.txt", "w").write(m.group(0))
                print("FLAG:", m.group(0))
            s.close()
            break
