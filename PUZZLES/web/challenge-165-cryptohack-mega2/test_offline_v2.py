# Offline test of the v2 attack against a local 13409.py Challenge instance.
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from harness import load_challenge
from solve_mega2_v2 import crack, M

def run(ch):
    mat = json.loads([l for l in ch.before_input.split("\n") if l.startswith("{")][0])
    n, e = mat["share_key_pub"]
    ske = bytes.fromhex(mat["share_key_enc"])
    mke = mat["master_key_enc"]
    print("blob len", len(ske), flush=True)
    h = "%x" % pow(M, e, n)
    if len(h) % 2: h = "0" + h
    for off in (639, 630, 624):
        ch.challenge({"action": "wait_login"})
        bad = bytearray(ske); bad[off] ^= 0xFF
        r = ch.challenge({"action": "send_challenge", "SID_enc": h,
                          "share_key_enc": bytes(bad).hex(), "master_key_enc": mke})
        if "SID" in r:
            m_top = int.from_bytes(bytes.fromhex(r["SID"]), "big")
            Yc = m_top * (1 << 128) - M
            p_ = crack(n, Yc)
            return off, p_
    return None, None

if __name__ == "__main__":
    import hashlib
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import unpad
    ok = 0
    for trial in range(2):
        ch = load_challenge(os.path.join(HERE, "13409.py"))
        off, p_ = run(ch)
        if p_:
            n = ch.C.share_key.n
            q_ = n // p_
            enc = bytes.fromhex(ch.challenge({"action": "get_encrypted_flag"})["encrypted_flag"])
            secret = hashlib.sha256(p_.to_bytes((p_.bit_length()+7)//8, "big") + q_.to_bytes((q_.bit_length()+7)//8, "big")).digest()
            pt = unpad(AES.new(secret, AES.MODE_ECB).decrypt(enc), 16)
            print(f"trial {trial}: OK off={off} flag={pt.decode()}", flush=True)
            ok += 1
        else:
            print(f"trial {trial}: FAILED off={off}", flush=True)
    print("ok", ok, "/2")
