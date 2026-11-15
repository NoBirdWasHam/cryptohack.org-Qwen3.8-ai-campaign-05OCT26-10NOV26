# Attack core for "Sign In Please, Again" (HKCERT CTF 2021).
# Technique source (author's postmortem): https://mystiz.hk/posts/2021-11-18-hkcert-ctf-2/
# Transport-agnostic: all functions take a spy(pbox, salt_bytes)->hexdigest callback.
import hashlib
from sha256ext import compress, state_from_hex, state_to_hex

IDENT = list(range(21))
def sigma_star():
    # len 65: p(16) | s1^4 | s2 | s3 | s1*41 | s4 | pepper
    return list(range(16)) + [16, 16, 16, 16, 17, 18] + [16] * 41 + [19, 20]
def sigma_n(n):
    # len 66: p(16) | s1^4 | s2 | s3 | s1*41 | s4 | p_n | pepper
    return list(range(16)) + [16, 16, 16, 16, 17, 18] + [16] * 41 + [19, n, 20]

# block2 continuation tails (bytes after the data bytes of block2)
TAIL65 = b'\x80' + b'\x00' * 60 + b'\x02\x08'   # 65-byte msg: [j] + tail, len 520 bits
TAIL66 = b'\x80' + b'\x00' * 59 + b'\x02\x10'   # 66-byte msg: [c][fresh pepper] + tail, len 528 bits

ALPHA = b'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'

def _char_task(args):
    """Task: for candidate char c, try all 256 fresh-pepper values at block2 byte 65."""
    st, target, c = args
    for j in range(256):
        if state_to_hex(compress(st, bytes([c, j]) + TAIL66)) == target:
            return c, j
    return None

def _t_task(args):
    """Task: t_j for one identity digest (pepper-phase helper)."""
    st, j = args
    return state_to_hex(compress(st, bytes([j]) + TAIL65)), j

def recover_pepper(spy, n_id=16, n_cand=16, pool=None, log=None):
    """Returns (known_state_hex, its_pepper_byte) or None. ~64% success."""
    ids = [spy(IDENT, b'\x00\x00\x00\x00') for _ in range(n_id)]
    cands = {}
    for x in range(n_cand):
        d = spy(sigma_star(), bytes([0x00, x, 0x80, 0xA8]))
        cands[d] = x
    # t[h][j] = H(h, [j][TAIL65]); match any sigma* digest v_x -> x == that identity's pepper
    for h in ids:
        st = state_from_hex(h)
        if pool is None:
            tmap = {state_to_hex(compress(st, bytes([j]) + TAIL65)): j for j in range(256)}
        else:
            tmap = dict(pool.map(_t_task, [(st, j) for j in range(256)], chunksize=16))
        hit = set(tmap) & set(cands)
        if hit:
            t = hit.pop()
            if log: log(f"pepper hit: state {h[:16]}.. pepper=0x{cands[t]:02x} (sigma* r'=0x{tmap[t]:02x})")
            return h, cands[t]
    return None

def recover_password(spy, h_hex, r, pool=None, log=None):
    """Given state h produced by payload P||0000||r, recover the 16 b64 chars.
    Each sigma_n call's digest = H(h, [p_n][r'][TAIL66]) with fresh unknown r',
    so we brute-force (char, r') per call — parallelized when a Pool is given."""
    st = state_from_hex(h_hex)
    pw = bytearray(16)
    for n in range(16):
        d = spy(sigma_n(n), bytes([0x00, r, 0x80, 0xA8]))
        tasks = [(st, d, c) for c in ALPHA]
        if pool is None:
            res = [_char_task(t) for t in tasks]
        else:
            res = pool.map(_char_task, tasks, chunksize=1)
        hits = [x for x in res if x is not None]
        if not hits:
            if log: log(f'char {n}: NO CANDIDATE MATCH (state/pepper assumption broken)')
            return None
        if len(hits) > 1 and log:
            log(f'char {n}: WARNING {len(hits)} hits {[chr(h0) for h0,_ in hits]} (collision?)')
        pw[n] = hits[0][0]
        if log: log(f"char {n}: {chr(hits[0][0])!r} (sigma* pepper'=0x{hits[0][1]:02x})")
    return bytes(pw)

def solve_connection(spy, begin_auth, answer, log=print, workers=16):
    """Full attack on one connection. Returns flag string or None. 48 spy + 1 auth."""
    import multiprocessing as mp
    with mp.Pool(workers) as pool:
        pr = recover_pepper(spy, pool=pool, log=log)
        if pr is None:
            log('pepper recovery missed (expected ~36% of the time) -> reconnect')
            return None
        h, r = pr
        pw = recover_password(spy, h, r, pool=pool, log=log)
    if pw is None:
        return None
    log(f'password recovered: {pw!r}')
    pbox, salt = begin_auth()
    payload = pw + salt + b'\x00'          # pepper 0: server scans all 256
    digest = hashlib.sha256(bytes(payload[i] for i in pbox)).hexdigest()
    out = answer(digest)
    log(f'auth reply: {out[:80]}')
    if out.startswith('\U0001f3c1'):
        return out[1:].strip()
    return None
