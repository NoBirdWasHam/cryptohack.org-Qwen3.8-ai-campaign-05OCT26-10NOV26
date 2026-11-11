#!/usr/bin/env python3
"""Play the one_round_crypto game vs remote using coset-pool attack."""
import socket, sys, time
from attack2 import build_message2, Decryptor2

HOST, PORT = 'archive.cryptohack.org', 62821
MCOS, DIM, EXTRA = 12, 7, 1536

def payload(line):
    s = line.decode(errors='replace').strip()
    if s.startswith('>'): s = s[1:].strip()
    if not s or set(s) == {'='}: return None
    return s

def main():
    t0 = time.time()
    rng = __import__('random').Random()
    pblocks, probes = build_message2(MCOS, DIM, EXTRA, rng)
    msg = ''.join(b.hex() for b in pblocks).encode()
    print("blocks", len(pblocks), "probes", len(probes), "line", len(msg), flush=True)
    sock = socket.create_connection((HOST, PORT), timeout=240)
    rf = sock.makefile('rb')
    def readline():
        l = rf.readline()
        if not l: raise EOFError("server closed")
        return l
    sock.sendall(msg + b"\n")
    line = readline()
    big = payload(line)
    assert big and len(big) % 32 == 0, repr(line[:80])
    print("first response %.1fs len %d" % (time.time()-t0, len(big)), flush=True)
    cblocks = [bytes.fromhex(big[32*i:32*i+32]) for i in range(len(pblocks))]
    dec = Decryptor2(pblocks, cblocks, probes)
    print("built %.1fs hits=%d atoms=%d ker=%s" %
          (time.time()-t0, dec.n_hits, dec.n_atoms, sorted(set(dec.kernel_dims))), flush=True)
    line = readline()
    assert set(payload(line) or '=') == {'='}, repr(line[:40])
    solved = 0
    for k in range(100):
        line = readline()
        e = payload(line)
        if e is None:
            print("unexpected:", line[:80]); break
        blk = dec.decrypt(bytes.fromhex(e.strip()))
        if blk is None:
            print("DECRYPT FAIL at", k, flush=True)
            sock.sendall(b"00"*15 + b"\n")
            continue
        sock.sendall(blk[:15].hex().encode() + b"\n")
        solved += 1
        if k % 25 == 0:
            print("answered %d (%.1fs)" % (k+1, time.time()-t0), flush=True)
    print("answered", solved, flush=True)
    rest = b""
    while True:
        l = rf.readline()
        if not l: break
        rest += l
        s = l.decode(errors='replace')
        if 'Wrong!' in s:
            print("SERVER: Wrong!", rest[:200]); sys.exit(1)
        if '{' in s and '}' in s:
            print("FLAG_LINE:", s.strip(), flush=True)
            open('flag_one_round_crypto-ecsc_2024_it.txt', 'w').write(s.strip())
            break
        if time.time()-t0 > 290: break
    print("total %.1fs" % (time.time()-t0), flush=True)

if __name__ == '__main__':
    main()
