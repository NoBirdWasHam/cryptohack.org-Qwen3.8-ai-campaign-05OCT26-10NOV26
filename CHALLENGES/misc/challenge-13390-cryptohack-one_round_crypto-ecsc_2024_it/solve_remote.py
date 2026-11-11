#!/usr/bin/env python3
"""Play the one_round_crypto game vs archive.cryptohack.org:62821."""
import socket, sys, time
from attack_core import build_message, Decryptor

HOST, PORT = 'archive.cryptohack.org', 62821
T, EXTRA = 96, 256

def payload(line):
    s = line.decode(errors='replace').strip()
    if s.startswith('>'): s = s[1:].strip()
    if not s or set(s) == {'='}: return None
    return s

def main():
    t0 = time.time()
    rng = __import__('random').Random()
    pblocks = build_message(T=T, extra=EXTRA, rng=rng)
    msg = ''.join(b.hex() for b in pblocks).encode()
    print("blocks", len(pblocks), "line", len(msg), flush=True)
    sock = socket.create_connection((HOST, PORT), timeout=180)
    rf = sock.makefile('rb')
    def readline():
        l = rf.readline()
        if not l: raise EOFError("server closed")
        return l
    sock.sendall(msg + b"\n")
    line = readline()               # "> " + big hex
    big = payload(line)
    assert big and len(big) % 32 == 0, repr(line[:80])
    print("got first response %.1fs len %d" % (time.time()-t0, len(big)), flush=True)
    cblocks = [bytes.fromhex(big[32*i:32*i+32]) for i in range(len(pblocks))]
    dec = Decryptor(pblocks, cblocks, T)
    print("built decryptor %.1fs atoms=%d dims=%s ker=%s" %
          (time.time()-t0, dec.n_atoms, sorted(set(dec.dims))[:4], sorted(set(dec.kernel_dims))[:4]), flush=True)
    line = readline()               # ==== line
    assert set(payload(line) or '=') == {'='}, repr(line[:40])
    solved = 0
    for k in range(100):
        line = readline()
        e = payload(line)
        if e is None:
            print("unexpected:", line[:80]); break
        blk = dec.decrypt(bytes.fromhex(e.strip()))
        if blk is None:
            print("DECRYPT FAIL at", k, "sending dummy", flush=True)
            sock.sendall(b"00"*15 + b"\n")
            continue
        sock.sendall(blk[:15].hex().encode() + b"\n")
        solved += 1
        if k % 10 == 0:
            print("answered %d (%.1fs)" % (k+1, time.time()-t0), flush=True)
    print("answered", solved, flush=True)
    # read flag
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
