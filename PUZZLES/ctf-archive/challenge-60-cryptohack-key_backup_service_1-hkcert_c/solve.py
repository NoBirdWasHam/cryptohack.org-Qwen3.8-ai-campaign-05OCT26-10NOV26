# Attack: Hastad broadcast on e=17 encryption of the same 256-bit master_secret
# under 5 fresh RSA moduli (ms^17 < prod(n_i)), plus modulus recovery per key:
#   send(m=2^61) -> c ; m^17 - c = k*n with k in (2^13, 2^15] (n in [2^1022,2^1024))
#   -> divisors of D in that window give candidate n (usually unique).
# 15 calls (pkey+backup+send)x5, 16th = flag. AES-CBC(ms, IV=0) decrypt offline.
import os, re, socket, subprocess, sys, itertools
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import gmpy2

E = 17
M = 1 << 61  # M^17 = 2^1037, so k = floor((M^17-c)/n) in (2^13, 2^15]
LO, HI = 1 << 1022, 1 << 1024  # guaranteed range of n = p*q (p,q 512-bit, top bit set)

def n_candidates(c, m=M):
    D = pow(m, E) - c
    kmin = D // HI + 1
    kmax = D // LO
    out = []
    for k in range(kmin, kmax + 1):
        if D % k == 0:
            n = D // k
            if LO <= n < HI and n % 2 == 1 and n % E != 0:
                out.append(n)
    return out

def crt(pairs):
    x, mod = 0, 1
    for r, n in pairs:
        t = (r - x) * gmpy2.invert(mod, n) % n
        x += mod * t
        mod *= n
    return x % mod, mod

def read_until(f, tok=b'[cmd] '):
    buf = b''
    while tok not in buf:
        ch = f.read(1)
        if not ch:
            break
        buf += ch
    return buf.decode(errors='replace')

def get_conn(mode):
    if mode == 'local':
        env = dict(os.environ, FLAG='hkcert21{local_smoke_test_flag}')
        p = subprocess.Popen([sys.executable, '-u', 'chall.py'], stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env,
                             cwd=os.path.dirname(os.path.abspath(__file__)), bufsize=0)
        return p, p.stdout, lambda s: (p.stdin.write((s + '\n').encode()), p.stdin.flush())
    s = socket.create_connection(('archive.cryptohack.org', 4077), timeout=120)
    f = s.makefile('rwb')
    return s, f, lambda x: (f.write((x + '\n').encode()), f.flush())

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'live'
    conn, f, sendline = get_conn(mode)
    pre = read_until(f)
    print('PRE:', repr(pre[:80]), file=sys.stderr)

    def cmd(line):
        sendline(line)
        return read_until(f)

    keys = []
    for i in range(5):
        cmd('pkey')
        resp = cmd('backup')
        cs = int(re.search(r'0x([0-9a-f]+)', resp).group(1), 16)
        resp = cmd('send ' + hex(M))
        c = int(re.search(r'0x([0-9a-f]+)', resp).group(1), 16)
        cands = n_candidates(c)
        print(f'key{i}: {len(cands)} n-candidates', file=sys.stderr)
        keys.append((cs, cands))

    resp = cmd('flag')
    ct_hex = re.search(r'([0-9a-f]{32,})', resp.strip()).group(1)

    combos = itertools.product(*[k[1] for k in keys])
    ms = None
    for ns in combos:
        X, prod = crt([(k[0], n) for k, n in zip(keys, ns)])
        assert X < prod
        r, exact = gmpy2.iroot(X, E)
        if exact and r < (1 << 256):
            if all(pow(r, E, n) == k[0] for k, n in zip(keys, ns)):
                ms = int(r)
                break
    if ms is None:
        print('FAIL: no consistent ms (n candidates wrong?)', file=sys.stderr)
        sys.exit(2)
    ms_bytes = ms.to_bytes(32, 'big')
    pt = unpad(AES.new(ms_bytes, AES.MODE_CBC, b'\x00' * 16).decrypt(bytes.fromhex(ct_hex)), 16)
    print(pt.decode())
    if mode == 'local':
        conn.terminate()
    else:
        conn.shutdown(socket.SHUT_RDWR)

if __name__ == '__main__':
    main()
