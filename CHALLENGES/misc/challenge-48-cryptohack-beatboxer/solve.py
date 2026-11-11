#!/usr/bin/env python3
"""beatboxer live solver.
  Cipher = AES-128-ECB with affine sbox[x]=42*x^42  =>  E_key(P) = M.P ^ E_key(0).
  M (columns) is key-independent (in M_matrix.json); D=E_key(0) recovered from the ONE allowed
  encrypt_message of a known 16-byte plaintext.  One connection:
    1) encrypt_flag    -> C_flag (unlimited)
    2) encrypt_message P_m -> C_m  =>  D = C_m ^ M.P_m
    3) each flag block: P_i = Minv.(C_i ^ D); strip PKCS7 -> flag.
"""
import socket, json, sys

J = json.load(open("M_matrix.json"))
M = J["M"]; Minv = J["Minv"]
N = 128
def to_int(b): return int.from_bytes(b, "little")
def to_bytes(x): return x.to_bytes(16, "little")
def apply_cols(cols, x):
    y = 0
    for j in range(N):
        if x >> j & 1:
            y ^= cols[j]
    return y

def main():
    s = socket.create_connection(("socket.cryptohack.org", 13406), timeout=30)
    banner = s.recv(4096).decode(errors="replace")
    print("BANNER:", banner.strip(), file=sys.stderr)

    def send(o):
        s.sendall(json.dumps(o).encode() + b"\n")
        buf = b""
        while b"\n" not in buf:
            c = s.recv(4096)
            if not c: raise ConnectionError("EOF")
            buf += c
        return json.loads(buf.decode().strip())

    C_flag = bytes.fromhex(send({"option": "encrypt_flag"})["encrypted_flag"])
    print("C_flag: %d bytes, %d blocks" % (len(C_flag), len(C_flag)//16), file=sys.stderr)

    P_m = bytes(range(16))
    C_m = bytes.fromhex(send({"option": "encrypt_message", "message": P_m.hex()})["encrypted_message"])
    D = to_int(C_m) ^ apply_cols(M, to_int(P_m))
    print("D =", to_bytes(D).hex(), file=sys.stderr)
    assert to_bytes(apply_cols(M, to_int(P_m)) ^ D) == C_m, "D self-check failed"

    plain = b""
    for i in range(0, len(C_flag), 16):
        plain += to_bytes(apply_cols(Minv, to_int(C_flag[i:i+16]) ^ D))
    pl = plain[-1]
    if 1 <= pl <= 16 and plain[-pl:] == bytes([pl])*pl:
        plain = plain[:-pl]
    flag = plain.decode(errors="replace")
    print("\nPLAIN:", plain, file=sys.stderr)
    print("FLAG:", flag)
    open("flag.txt", "w").write(flag)
    s.close()

main()
