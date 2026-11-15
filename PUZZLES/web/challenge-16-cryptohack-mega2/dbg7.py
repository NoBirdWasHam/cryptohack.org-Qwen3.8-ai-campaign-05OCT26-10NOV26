import sys, os, json, math
base = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, base)
from harness import load_challenge

for trial in range(2):
    ch = load_challenge(os.path.join(base, "13409.py"))
    mat = json.loads([l for l in ch.before_input.split("\n") if l.startswith("{")][0])
    n, e = mat["share_key_pub"]
    ske = bytes.fromhex(mat["share_key_enc"])
    mke = mat["master_key_enc"]
    p_true = ch.C.share_key.p
    M = (1 << 1024) + 12345
    bad = bytearray(ske)
    for j in range(16): bad[160 + j] ^= 0xFF
    h = "%x" % pow(M, e, n)
    if len(h) % 2: h = "0" + h
    ch.challenge({"action": "wait_login"})
    r = ch.challenge({"action": "send_challenge", "SID_enc": h, "share_key_enc": bytes(bad).hex(), "master_key_enc": mke})
    sid = bytes.fromhex(r["SID"])
    m_top = int.from_bytes(sid, "big")
    Y = m_top * (1 << 128) - M
    print(f"trial {trial}: sid_len={len(sid)} m_top_bits={m_top.bit_length()} Y_bits={Y.bit_length()} Y>0={Y>0}")
    # brute enumeration as in offline_mega2b
    hit = None
    for f in (1, 2, 3):
        for d in range(-255, 256, 2):
            if d == 0: continue
            for w in range(-1100, 1101):
                num = Y + w * n + (1 << 127)
                den = f * d
                if den < 0: num, den = -num, -den
                if num <= 0: continue
                qv = num // den
                p_ = math.isqrt(qv)
                for cand in (p_ - 1, p_, p_ + 1):
                    if cand > 1 and n % cand == 0:
                        hit = (f, d, w, cand)
                        break
                if hit: break
            if hit: break
        if hit: break
    print("  hit:", hit, " true p:", p_true)
    if hit:
        f, d, w, cand = hit
        print("  cand == p_true?", cand == p_true, " cand == n//p_true?", cand == n // p_true)
        # what is m-M vs cand^2*f*d - w*n ?
        print("  f*d*cand^2 - w*n - Y bits:", (f*d*cand*cand - w*n - Y).bit_length())
