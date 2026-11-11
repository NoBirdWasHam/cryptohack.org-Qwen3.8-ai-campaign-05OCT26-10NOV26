# rsa-or-hmac-2 solver: recover RSA pubkey from signatures, then HS256 alg-confusion forge
import json, base64, hashlib, hmac, urllib.request, subprocess, sys

BASE = "https://web.cryptohack.org/rsa-or-hmac-2"

def get(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return r.read()

def b64u(b): return base64.urlsafe_b64encode(b).rstrip(b"=")
def b64u_dec(s): return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))

def get_session(username):
    tok = json.loads(get(f"{BASE}/create_session/{username}/"))["session"]
    return tok

# PKCS#1 v1.5 SHA-256 DigestInfo prefix (RFC 8017)
DIGEST_INFO_SHA256 = bytes.fromhex("3031300d060960864801650304020105000420")

def padded_block(signing_input: bytes, k=256) -> bytes:
    h = hashlib.sha256(signing_input).digest()
    t = DIGEST_INFO_SHA256 + h
    ps = b"\xff" * (k - len(t) - 3)
    return b"\x00\x01" + ps + b"\x00" + t

def i2osp(x, k): return int.to_bytes(x, k, "big")
def os2ip(b): return int.from_bytes(b, "big")

def gcd(a, b):
    while b: a, b = b, a % b
    return a

E = 65537
print("fetching sessions...", flush=True)
toks = [get_session(u) for u in ("alice", "bob", "carol")]
print("got 3 tokens", flush=True)
Ss, Ms = [], []
for tok in toks:
    h, p, s = tok.split(".")
    m = os2ip(padded_block(f"{h}.{p}".encode()))
    sig = os2ip(b64u_dec(s))
    Ss.append(pow(sig, E) - m)   # multiple of n
    Ms.append(m)
    print("sig bits", sig.bit_length(), "m bits", m.bit_length())

n = Ss[0]
for S in Ss[1:]:
    n = gcd(n, S)
# strip small common factors
while n % 2 == 0: n //= 2
print("n bits", n.bit_length())
# verify
for tok, m in zip(toks, Ms):
    h, p, s = tok.split(".")
    sig = os2ip(b64u_dec(s))
    ok = pow(sig, E, n) == m
    print("verify:", ok)
    if not ok:
        sys.exit("n wrong — try more signatures / factor out small primes")

# rebuild the exact PEM: openssl rsa -RSAPublicKey_out => "BEGIN RSA PUBLIC KEY" (RSAPublicKey DER)
def der_int(x):
    b = x.to_bytes((x.bit_length() + 8) // 8, "big")  # ensure positive (leading 0 if high bit)
    if b[0] & 0x80: b = b"\x00" + b
    return b"\x02" + der_len(len(b)) + b
def der_len(L):
    if L < 0x80: return bytes([L])
    lb = L.to_bytes((L.bit_length()+7)//8, "big")
    return bytes([0x80 | len(lb)]) + lb
der = b"\x30" + der_len(0) 
body = der_int(n) + der_int(E)
der = b"\x30" + der_len(len(body)) + body
b64 = base64.encodebytes(der).decode()  # 64-char lines + trailing newline
pem = f"-----BEGIN RSA PUBLIC KEY-----\n{b64}-----END RSA PUBLIC KEY-----\n".encode()
open("pubkey_recovered.pem", "wb").write(pem)
print(pem.decode())
# sanity: openssl should parse it
r = subprocess.run(["openssl", "rsa", "-RSAPublicKey_in", "-in", "pubkey_recovered.pem", "-noout", "-text"],
                   capture_output=True, text=True)
print("openssl parse:", r.returncode, r.stdout[:120], r.stderr[:200])

# HS256 forge with PEM bytes as secret
def forge(payload, secret):
    header = {"typ": "JWT", "alg": "HS256"}
    h = b64u(json.dumps(header, separators=(",", ":")).encode())
    p = b64u(json.dumps(payload, separators=(",", ":")).encode())
    si = h + b"." + p
    sig = b64u(hmac.new(secret, si, hashlib.sha256).digest())
    return (si + b"." + sig).decode()

variants = {
    "pem_trailing_nl": pem,
    "pem_no_trailing_nl": pem.rstrip(b"\n"),
}
for name, secret in variants.items():
    tok = forge({"username": "admin", "admin": True}, secret)
    resp = get(f"{BASE}/authorise/{tok}/").decode()
    print(name, "->", resp[:200])
    if "flag" in resp:
        print("FLAG:", resp); break
