import sys, time, os, random, hashlib
from pwn import remote
from quo_core import (modulus_from_line, Tower, Nest, cz_one_root, solve_mod2k, prod)
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

def unit_inv_newton(u, N1, tw, iters=8):
    L = N1.L - 1
    ub = N1.flatten(u)
    mask = 0
    for i, b in enumerate(ub):
        if b & 1: mask |= 1 << i
    assert mask != 0, "not a unit"
    v = tw.from_mask(tw.minv(mask))
    two = N1.scale(N1.one(L), 2, L)
    for _ in range(iters):
        v = N1.mul(v, N1.sub(two, N1.mul(u, v, L), L), L)
    return v

def build_cols(moduli, gbits, k):
    ds = [len(m) - 1 for m in moduli]
    D = prod(ds)
    p = 2 ** k
    T = Tower(ds, moduli)
    rbits = cz_one_root(gbits, T)
    gcoeff = [(gbits >> i) & 1 for i in range(D + 1)]
    ev = 0
    for c in reversed(gcoeff):
        ev = T.mmul(ev, rbits)
        if c: ev ^= 1
    assert ev == 0, "root check failed"
    N1 = Nest(ds, moduli, p)
    L = N1.L - 1
    theta = T.from_mask(rbits)
    gprime = [(i * ((gbits >> i) & 1)) % p for i in range(1, D + 1)]
    for _ in range(7):
        u = N1.eval_int_poly(theta, gcoeff)
        du = N1.eval_int_poly(theta, gprime)
        inv = unit_inv_newton(du, N1, T)
        theta = N1.sub(theta, N1.mul(u, inv, L), L)
    assert N1.eval_int_poly(theta, gcoeff) == N1.zero(L), "hensel failed"
    cols = []
    pw = N1.one(L)
    for i in range(D):
        cols.append(N1.flatten(pw))
        pw = N1.mul(pw, theta, L)
    return cols

def nums(line):
    return [int(t) for t in line.replace(b'>', b' ').split(b',')]

def main():
    CHALS = [(2, [2, 3]), (8, [2, 3]), (8, [2, 3, 5]), (32, [3, 4, 5]), (64, [4, 3, 5])]
    host = os.environ.get("QUO_HOST", "archive.cryptohack.org")
    port = int(os.environ.get("QUO_PORT", "23128"))
    r = remote(host, port, timeout=300)
    K = []
    t00 = time.time()
    for ci, (k, ds) in enumerate(CHALS):
        D = prod(ds)
        lines = [r.recvline().decode().strip() for _ in range(len(ds) + 1)]
        pt1line = r.recvline()
        t0 = time.time()
        moduli = [modulus_from_line(lines[i], i, ds) for i in range(len(ds))]
        gd = modulus_from_line(lines[len(ds)], 0, [D])
        gbits = sum(c << i for i, c in enumerate(gd))
        assert gd[-1] == 1 and gd[0] == 1
        cols = build_cols(moduli, gbits, k)
        p = 2 ** k
        pt1 = nums(pt1line)
        assert len(pt1) == D
        x = solve_mod2k(cols, pt1, p)
        r.sendline(','.join(str(v) for v in x).encode())
        vline = r.recvline()
        v = nums(vline)
        assert len(v) == D
        out = [sum(cols[i][rr] * v[i] for i in range(D)) % p for rr in range(D)]
        K += out
        print(f"chal{ci} done in {time.time()-t0:.1f}s (total {time.time()-t00:.1f}s)", flush=True)
    fin = r.recvline().split()
    ivhex, cthex = fin[0], fin[1]
    key = hashlib.sha256('||'.join(map(str, K)).encode()).digest()
    ct = bytes.fromhex(cthex.decode())
    pt = unpad(AES.new(key, AES.MODE_CBC, bytes.fromhex(ivhex.decode())).decrypt(ct), 16)
    print("FLAG:", pt.decode())
    with open('flag_quo_vadis-ecsc_2024_italy2024.txt', 'w') as f:
        f.write(pt.decode())
    r.close()

if __name__ == '__main__':
    main()
