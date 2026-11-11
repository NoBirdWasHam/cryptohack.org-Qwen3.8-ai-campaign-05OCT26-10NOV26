# Live solver: archive.cryptohack.org:45400 rsa_permutation-wacon2022
import socket, hashlib, subprocess, sys, time, os, re
from multiprocessing import Pool

HOST, PORT = 'archive.cryptohack.org', 45400
Z = b'\x00\x00\x00'

def _pow_chunk(args):
    sb, lo, hi = args
    h = hashlib.sha256
    for i in range(lo, hi):
        if h(sb + str(i).encode()).digest()[:3] == Z:
            return str(i)
    return None

def solve_pow(sb):
    W, CH = 12, 2_000_000
    with Pool(W) as pool:
        start = 0
        while True:
            jobs = [(sb, start + w * CH, start + (w + 1) * CH) for w in range(W)]
            start += W * CH
            for r in pool.imap_unordered(_pow_chunk, jobs):
                if r is not None:
                    return r

def run_client(open_conn):
    s, f = open_conn()
    def rdline(t=15):
        s.settimeout(t)
        try:
            return f.readline().decode(errors='replace')
        except socket.timeout:
            return ''
    print("banner:", rdline().strip(), flush=True)
    chal = rdline().strip()
    print("pow challenge:", chal, flush=True)
    t0 = time.time()
    ans = solve_pow(chal.encode())
    print("pow answer:", ans, f"({time.time()-t0:.1f}s)", flush=True)
    s.sendall((ans + '\n').encode())
    n = int(rdline(20).strip())
    sp = rdline(20).strip()
    sq = rdline(20).strip()
    print("n bits:", n.bit_length(), "len sp,sq:", len(sp), len(sq), flush=True)
    assert len(sp) == 256 and len(sq) == 256
    open('live_instance.txt', 'w').write(str(n) + '\n' + sp + '\n' + sq + '\n')
    print("running DP...", flush=True)
    t0 = time.time()
    with open('live_dp.log', 'w') as lf:
        subprocess.run(['./dp4.exe', 'live_instance.txt'], stdout=lf, stderr=subprocess.STDOUT, timeout=560, cwd=os.getcwd())
    out = open('live_dp.log').read()
    print("dp done in", time.time() - t0, "s; solutions:", out.count('SOLUTION'), flush=True)
    m = re.search(r'\np=([0-9a-f]{100,})', out)
    if not m:
        print("NO SOLUTION:", out[-600:], flush=True); sys.exit(2)
    p = int(m.group(1), 16)
    assert n % p == 0, "p does not divide n!"
    q = n // q if False else n // p
    print("factored ok; sending u,v", flush=True)
    s.sendall((str(p) + '\n').encode())
    s.sendall((str(q) + '\n').encode())
    time.sleep(2)
    resp = ''
    for _ in range(6):
        resp += rdline(8)
    print("RESPONSE:", resp.strip(), flush=True)
    open('flag_raw.txt', 'w').write(resp)

def live():
    s = socket.create_connection((HOST, PORT), timeout=25)
    return s, s.makefile('rb')

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--local':
        # pipe-adapter local test against chal.py subprocess
        import types
        pro = subprocess.Popen([sys.executable, 'chal.py'], stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, env=dict(os.environ, FLAG='crypto{local_test_flag}'))
        class Adp:
            def __init__(self, pro): self.pro = pro
            def settimeout(self, t): pass
            def readline(self):
                ln = self.pro.stdout.readline()
                return ln
            def sendall(self, b):
                self.pro.stdin.write(b); self.pro.stdin.flush()
        a = Adp(pro)
        run_client(lambda: (a, a))
    else:
        run_client(live)
