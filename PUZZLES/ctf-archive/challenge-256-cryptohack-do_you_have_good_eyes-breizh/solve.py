# Solver: "Do you have good eyes?" (Breizh CTF, CryptoHack archive 43607).
#
# Game: 130 rounds; each round A (8x7 in Rq), t (8 in Rq); t = A*s+e (MLWE)
# or t uniform. Need 128 correct.
#
# Distinguisher (first principles): x-1 divides x^256-1, so evaluation at
# x=1 is a ring hom Rq -> Fq. Integer sums keep smallness:
#   sigma_j = sum_k s_j[k] in [-512,512],  mu_m = sum_k e_m[k] in [-512,512].
# MLWE  =>  there exist integer sigma (7), mu (8), all |.|<=512, w (8) with
#   T_m = sum_j A1_j * sigma_j + mu_m + q*w_m,  where A1_j = A_j(1), T = t(1).
# i.e. CVP in dim-15 lattice L = {(sigma, A1.sigma + q z)} (det q^8) for target
# (0^7 | T): closest-point distance = ||(sigma,mu)|| <= 512*sqrt(15) ~ 1985.
# For uniform T the nearest lattice point sits near Gaussian width
# sqrt(15/2pi e) * q^(8/15) ~ 4.6e3, and expected box solutions e^{-24}.
# Kannan embedding + LLL (dim 16) decides.
import re, socket, sys, json
from fpylll import IntegerMatrix, LLL

Q = 8380417
K, L, N = 8, 7, 256
R_ACCEPT = 2200.0   # > 512*sqrt(15)=1985, << lambda2 ~ 4600
KAPPA = 500         # scaling row; MLWE vector norm ~ sqrt(88^2+500^2)=508 worst sqrt(1985^2+500^2)=2047

import base64, gzip
from ast import literal_eval

def decode_mat(s):
    return literal_eval(gzip.decompress(base64.b64decode(s)).decode())

def is_mlwe(A, t):
    A1 = [sum(poly) % Q for row in A for poly in row]      # order: rows of 7 -> just need 7 sums? careful
    # A is 8x7 of polynomials; A1_j = A_j(1) must be summed per COLUMN j over ROWS? No:
    # T_m = sum_j A1[j][m] * sigma[j] + mu[m], sigma[j] = sum_k s[j][k]; A1 is 8x7.
    A1m = [[sum(A[m][j]) % Q for j in range(L)] for m in range(K)]
    T = [sum(t[m]) % Q for m in range(K)]
    rows = []
    for j in range(L):
        rows.append([1 if c == j else 0 for c in range(L)] + [A1m[m][j] % Q for m in range(K)] + [0])
    for m in range(K):
        rows.append([0]*L + [Q if c == m else 0 for c in range(K)] + [0])
    rows.append([0]*L + [T[m] % Q for m in range(K)] + [KAPPA])
    M = IntegerMatrix.from_iterable(len(rows), L+K+1, iter(v for r in rows for v in r))
    LLL.reduction(M)
    for i in range(M.nrows):
        v = [int(M[i][j]) for j in range(L+K+1)]
        if v[-1] == 0:
            continue
        if abs(v[-1]) != KAPPA:
            continue
        d2 = sum(x*x for x in v[:-1])
        if 0 <= d2 <= R_ACCEPT*R_ACCEPT:
            return True
    return False

def read_till(s, pat, buf=b"", timeout=60):
    buf = bytes(buf)
    s.settimeout(timeout)
    while not re.search(pat, buf):
        d = s.recv(65536)
        if not d:
            raise EOFError(buf[-300:])
        buf += d
    return buf

def main():
    HOST, PORT = "archive.cryptohack.org", 43607
    s = socket.create_connection((HOST, PORT), timeout=90)
    log = []
    buf = b""
    for rnd in range(131):
        buf = read_till(s, rb"sanitize_vec\(t\) = '([^']+)'", buf)
        m = re.search(rb"sanitize_mat\(A\) = '([^']+)'", buf)
        tv = re.search(rb"sanitize_vec\(t\) = '([^']+)'", buf)
        A = decode_mat(m.group(1))
        t = decode_mat(tv.group(1))
        ans = 1 if is_mlwe(A, t) else 0
        buf = buf[tv.end():]
        s.sendall(f"{ans}\n".encode())
        buf = read_till(s, rb"(wp, \d+/\d+|oups, \d+/\d+|flag|Well played)", buf, timeout=90)
        mm = re.search(rb"(wp|oups), (\d+)/(\d+)", buf)
        line = mm.group(0).decode() if mm else ""
        log.append((rnd, ans, line))
        print(rnd, "ans", ans, "|", line[:60], flush=True)
        if b"flag" in buf or b"Well played" in buf:
            print("FLAGLINE:", buf.decode(errors="replace")[:400], flush=True)
            break
        buf = buf[mm.end():] if mm else buf
    s.close()
    json.dump(log, open("game_log.json", "w"), indent=0)
    errs = sum(1 for _, _, l in log if l.startswith("oups"))
    print("errors:", errs)

if __name__ == "__main__":
    main()
