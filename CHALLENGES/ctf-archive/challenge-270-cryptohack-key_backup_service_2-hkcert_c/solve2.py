# Final solve: true modulus per block = min candidate (candidates are multiples of n_real);
# HASTAD broadcast over all blocks; exact e-th root check; AES-CBC decrypt.
import json, os, sys
import gmpy2
from gmpy2 import mpz, iroot, gcd, invert
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

HERE = os.path.dirname(os.path.abspath(__file__))
E = 65537

def main():
    with open(os.path.join(HERE, 'cands.json')) as f:
        cands = json.load(f)
    mods, cbs = [], []
    zero = 0
    for cs, (c2, c3, cb) in zip(cands, load_blocks()):
        if not cs:
            zero += 1
            continue
        vals = sorted(int(x, 16) for x in cs)
        n = vals[0]  # smallest candidate = n_true (others are integer multiples)
        if not (1022 <= n.bit_length() <= 1024) or n <= cb:
            zero += 1
            continue
        mods.append(mpz(n)); cbs.append(mpz(cb))
    print('kept', len(mods), 'dropped', zero, 'M bits ~', sum(int(m).bit_length() for m in mods), flush=True)

    R = mpz(cbs[0]); M = mpz(mods[0])
    for i, (m, c) in enumerate(zip(mods[1:], cbs[1:])):
        t = ((c - R) % m) * invert(M % m, m) % m
        R += M * t
        M *= m
        if i % 4000 == 0:
            print('crt', i, 'Mbits', M.bit_length(), flush=True)
    R %= M
    print('CRT done R bits', R.bit_length(), 'M bits', M.bit_length(), flush=True)

    root, exact = iroot(R, E)
    print('iroot exact?', exact, 'root bits', root.bit_length(), flush=True)
    if not exact:
        # near-miss: try root-1/root+1 perfect power check anyway
        for d in (-1, 0, 1):
            x = root + d
            if x > 0 and x ** E == R:
                root = x; exact = True
                break
    if not exact:
        sys.exit('R is not a perfect 65537-th power: product M < ms^e (insufficient slack)')
    ms = root
    bad = 0
    import random
    random.seed(1)
    for i in random.sample(range(len(mods)), 200):
        if pow(ms, E, mods[i]) != cbs[i]:
            bad += 1
    print('sample verify bad:', bad, '/200', flush=True)
    if bad:
        sys.exit('root mismatches ciphertexts')

    msb = int(ms).to_bytes(32, 'big')
    with open(os.path.join(HERE, 'transcript.log')) as f:
        for line in f:
            if line.startswith('[cmd] flag'):
                nxt = next(f).strip()
                break
        else:
            sys.exit('no flag line')
    flag_ct = bytes.fromhex(nxt)
    pt = unpad(AES.new(msb, AES.MODE_CBC, b'\0' * 16).decrypt(flag_ct), 16)
    print('FLAG:', pt.decode(), flush=True)
    with open(os.path.join(HERE, 'flag_key_backup_service_2-hkcert_c.txt'), 'w') as f:
        f.write(pt.decode().strip() + '\n')
    with open(os.path.join(HERE, 'ms_hex.txt'), 'w') as f:
        f.write(msb.hex() + '\n')

def load_blocks():
    with open(os.path.join(HERE, 'transcript.log')) as f:
        lines = [l.strip() for l in f if l.strip()]
    i = 0
    cur = []
    while i < len(lines):
        l = lines[i]
        if not l.startswith('[cmd]'):
            i += 1
            continue
        cmd = l[5:].strip()
        if cmd == 'pkey':
            cur = []
        elif cmd.startswith('send'):
            cur.append(int(lines[i + 1], 16)); i += 1
        elif cmd == 'backup':
            cur.append(int(lines[i + 1], 16)); i += 1
            yield tuple(cur); cur = []
        i += 1

if __name__ == '__main__':
    main()
