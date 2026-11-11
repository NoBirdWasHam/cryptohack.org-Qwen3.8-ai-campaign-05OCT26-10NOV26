# key_backup_service_2-hkcert_c solver (offline, transcript-based)
# Step 1: parse transcript.log -> flag_ct, blocks (c2,c3,cb)
# Step 2: n_i = gcd(2^e - c2_i, 3^e - c3_i)
# Step 3: Hastad broadcast: CRT cb_i over n_i -> ms^e as integer -> 65537-th root
# Step 4: AES-CBC decrypt flag_ct with key=ms, IV=0
import sys, os
import gmpy2
from gmpy2 import mpz, iroot, gcd, invert
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

HERE = os.path.dirname(os.path.abspath(__file__))
E = 65537

def parse(path):
    flag_ct = None
    blocks = []  # (c2, c3, cb)
    with open(path) as f:
        lines = [l.strip() for l in f if l.strip()]
    i = 0
    cur = []
    while i < len(lines):
        l = lines[i]
        assert l.startswith('[cmd]'), l
        cmd = l[5:].strip()
        if cmd == 'pkey':
            cur = []
        elif cmd.startswith('send'):
            cur.append(int(lines[i+1], 16))
            i += 1
        elif cmd == 'backup':
            cur.append(int(lines[i+1], 16))
            assert len(cur) == 3, cur
            blocks.append(tuple(cur))
            i += 1
        elif cmd == 'flag':
            flag_ct = bytes.fromhex(lines[i+1])
            i += 1
        i += 1
    return flag_ct, blocks

def main():
    flag_ct, blocks = parse(os.path.join(HERE, 'transcript.log'))
    print('blocks:', len(blocks), 'flag_ct len:', len(flag_ct) if flag_ct else None, flush=True)

    two_e = mpz(2) ** E
    three_e = mpz(3) ** E
    mods = []
    cbs = []
    for k, (c2, c3, cb) in enumerate(blocks):
        d1 = two_e - c2
        d2 = three_e - c3
        g = gcd(d1, d2)
        n = None
        for t in (1, 2, 3, 5, 7, 9, 11, 13):
            if g % t:
                continue
            cand = g // t
            if cand.bit_length() <= 1024 and pow(mpz(2), E, cand) == c2 and pow(mpz(3), E, cand) == c3:
                n = cand
                break
        if n is None:
            print('NO CLEAN n at', k, 'gbits', g.bit_length(), flush=True)
            continue
        mods.append(n)
        cbs.append(cb)
        if k % 2000 == 0:
            print('mod', k, 'bits', n.bit_length(), flush=True)
    print('kept', len(mods), 'moduli; total bits:', sum(int(m).bit_length() for m in mods), flush=True)

    # iterative CRT
    R = mpz(cbs[0]); M = mpz(mods[0])
    for m, c in zip(mods[1:], cbs[1:]):
        t = ((c - R) % m) * invert(M % m, m) % m
        R += M * t
        M *= m
    R %= M
    print('CRT done, bits:', R.bit_length(), 'M bits:', M.bit_length(), flush=True)

    ms = iroot(R, E)[0]
    print('root ms =', int(ms), 'bitlen', ms.bit_length(), flush=True)
    # verify on 5 sample moduli
    for idx in [0, len(mods)//4, len(mods)//2, 3*len(mods)//4, len(mods)-1]:
        ok = pow(ms, E, mods[idx]) == cbs[idx]
        print('verify block', idx, ok, flush=True)
        if not ok:
            sys.exit('root does not match ciphertexts — ms^e >= M, transcript too small')

    msb = int(ms).to_bytes(32, 'big')
    pt = unpad(AES.new(msb, AES.MODE_CBC, b'\0'*16).decrypt(flag_ct), 16)
    print('FLAG:', pt.decode(), flush=True)
    with open(os.path.join(HERE, 'flag_key_backup_service_2-hkcert_c.txt'), 'w') as f:
        f.write(pt.decode().strip() + '\n')

if __name__ == '__main__':
    main()
