# Self-test of decode glue against deterministic ground truth (default sample flag).
from Crypto.Util.Padding import pad

l = 50
P = 5 ** l
cs = [-2, -1, 0, 1, 2]

def btq(a_bytes):
    a = int.from_bytes(a_bytes, "little")
    res = []
    while a > 0:
        res.append(cs[a % 5]); a //= 5
    return res

def fold(msg: str) -> bytes:
    mm = pad(msg.encode(), 16)
    oo = b"\x00" * 16
    for q in range(0, len(mm), 16):
        oo = bytes(x ^ y for x, y in zip(oo, mm[q:q + 16]))
    return oo

for flag in ["BZHCTF{0000000000000000}", "BZHCTF{deadbeefcafe1234}", "BZHCTF{a1b2c3d4e5f60789}"]:
    out = fold(flag)
    a = int.from_bytes(out, "little")
    digs = btq(out)
    val = sum(digs[i] * 5 ** i for i in range(min(l, len(digs)))) + (P - 1) // 2
    delta = a - val
    print(f"{flag}: m={len(digs)} delta%P=={delta % P == 0} c={delta // P if delta % P == 0 else None} c>=0={delta >= 0}")
    # reconstruct via scan (known-plaintext structural decode)
    known = b"BZHCTF{"
    found = None
    c = 0
    while True:
        outv = val + c * P
        if outv >= 1 << 128: break
        if outv >= 0:
            o = outv.to_bytes(16, "little")
            tail = bytes(x ^ b for x, b in zip(o[:7], known))
            if all(48 <= y <= 57 or 97 <= y <= 102 for y in tail):
                mid = bytes(o[ii] ^ (0x7d if ii == 7 else 0x08) for ii in range(7, 16))
                if all(48 <= y <= 57 or 97 <= y <= 102 for y in mid):
                    cand = "BZHCTF{" + mid.decode() + tail.decode() + "}"
                    if fold(cand) == o:
                        found = (c, cand)
        c += 1
    print("   scan found:", found, " expected:", (delta // P if delta % P == 0 else None, flag))
