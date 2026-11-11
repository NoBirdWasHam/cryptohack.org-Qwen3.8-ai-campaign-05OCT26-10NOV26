# rsa-or-hmac-2 solver: recover RSA modulus from RS256 signatures (gcd(s^e - m)),
# rebuild exact RSAPublicKey_out PEM, forge HS256 (alg confusion) -> flag.
import json, base64, hashlib, hmac, urllib.request, subprocess, sys, time
from gmpy2 import mpz, gcd, powmod  # noqa

BASE = "https://web.cryptohack.org/rsa-or-hmac-2"
def get(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return r.read()
def b64u(b): return base64.urlsafe_b64encode(b).rstrip(b"=")
def b64u_dec(s): return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))

DI = bytes.fromhex("3031300d060960864801650304020105000420")  # DigestInfo SHA-256
def padded_block(si, k=256):
    t = DI + hashlib.sha256(si).digest()
    return b"\x00\x01" + b"\xff" * (k - len(t) - 3) + b"\x00" + t

E = 65537
toks = [json.loads(get(f"{BASE}/create_session/{u}/"))["session"] for u in ("alice", "bob", "carol")]
print("tokens fetched", flush=True)
Ss, Ms, Sigs = [], [], []
for tok in toks:
    h, p, s = tok.split(".")
    m = mpz(int.from_bytes(padded_block(f"{h}.{p}".encode()), "big"))
    sig = mpz(int.from_bytes(b64u_dec(s), "big"))
    t = time.time()
    S = sig ** mpz(E) - m              # multiple of n (full exp, GMP)
    print("  exp done", round(time.time()-t, 1), "s, S bits", S.bit_length(), flush=True)
    Ss.append(S); Ms.append(m); Sigs.append(sig)

t = time.time()
n = gcd(Ss[0], Ss[1])
n = gcd(n, Ss[2])
while n % 2 == 0:
    n //= 2
print("gcd done", round(time.time()-t, 1), "s; n bits", n.bit_length(), flush=True)

for sig, m in zip(Sigs, Ms):
    assert powmod(sig, mpz(E), n) == m, "verification failed"
print("n verified against all 3 signatures", flush=True)
n_int = int(n)

# --- rebuild exact PEM bytes (openssl rsa -RSAPublicKey_out => RSAPublicKey DER) ---
def der_len(L):
    if L < 0x80: return bytes([L])
    lb = L.to_bytes((L.bit_length() + 7) // 8, "big")
    return bytes([0x80 | len(lb)]) + lb
def der_int(x):
    b = x.to_bytes((x.bit_length() + 7) // 8, "big")
    if b[0] & 0x80: b = b"\x00" + b
    return b"\x02" + der_len(len(b)) + b
body = der_int(n_int) + der_int(E)
der = b"\x30" + der_len(len(body)) + body
b64 = base64.encodebytes(der).decode()
pem = f"-----BEGIN RSA PUBLIC KEY-----\n{b64}-----END RSA PUBLIC KEY-----\n".encode()
open("pubkey_recovered.pem", "wb").write(pem)
r = subprocess.run(["openssl", "rsa", "-RSAPublicKey_in", "-in", "pubkey_recovered.pem", "-noout", "-modulus"],
                   capture_output=True, text=True)
print("openssl parse:", r.returncode, (r.stdout or r.stderr)[:100], flush=True)

# --- HS256 forge: secret = exact PEM bytes ---
def forge(payload, secret):
    h = b64u(json.dumps({"typ": "JWT", "alg": "HS256"}, separators=(",", ":")).encode())
    p = b64u(json.dumps(payload, separators=(",", ":")).encode())
    si = h + b"." + p
    return (si + b"." + b64u(hmac.new(secret, si, hashlib.sha256).digest())).decode()

payloads = [{"username": "admin", "admin": True}, {"admin": True, "username": "admin"}]
secrets = {"pem": pem, "pem_no_nl": pem.rstrip(b"\n")}
found = None
for pn, sec in secrets.items():
    for pl in payloads:
        tok = forge(pl, sec)
        resp = get(f"{BASE}/authorise/{tok}/").decode()
        print(pn, "->", resp[:160], flush=True)
        if "flag" in resp:
            found = resp; break
    if found: break
if found:
    print("FLAG RESPONSE:", found)
    open("flag_response.json", "w").write(found)
else:
    print("no flag yet — check PEM byte-exactness")
