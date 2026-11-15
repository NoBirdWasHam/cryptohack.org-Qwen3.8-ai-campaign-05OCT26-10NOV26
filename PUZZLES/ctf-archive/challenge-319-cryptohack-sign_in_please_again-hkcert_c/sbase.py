# session base: fast multiprocessing PoW + read_until framing (prompts have NO newline)
import socket, base64, hashlib, time, multiprocessing as mp

HOST, PORT = "archive.cryptohack.org", 60192

def _worker(arg):
    chal, start, step = arg
    r = start
    for _ in range(step):
        if hashlib.sha256(chal + r.to_bytes(4, "big")).digest().startswith(b"\x00\x00\x00"):
            return r
        r += 1
    return None

def fast_pow(chal, workers=16, chunk=2_000_000):
    with mp.Pool(workers) as p:
        start = 0
        while True:
            args = [(chal, start + i * chunk, chunk) for i in range(workers)]
            for res in p.imap_unordered(_worker, args):
                if res is not None:
                    return res
            start += workers * chunk

class S:
    def __init__(self, timeout=55):
        self.s = socket.create_connection((HOST, PORT), timeout=timeout)
        self.s.settimeout(timeout)
        self.buf = b""
        greet = self.until(b"\n")
        chal = base64.b64decode(greet.split()[1])
        t0 = time.time()
        r = fast_pow(chal)
        self.pow_t = time.time() - t0
        self.s.sendall(base64.b64encode(r.to_bytes(4, "big")) + b"\n")
        self.until("\U0001f916 ")  # robot prompt
    def until(self, marker):
        m = marker.encode() if isinstance(marker, str) else marker
        while m not in self.buf:
            d = self.s.recv(4096)
            if not d: raise EOFError("closed; buf=" + self.buf[-120:].decode(errors="replace"))
            self.buf += d
        i = self.buf.index(m) + len(m)
        out, self.buf = self.buf[:i], self.buf[i:]
        return out.decode(errors="replace")
    def send(self, s):
        self.s.sendall((s + "\n").encode())
    def spy(self, pbox, salt_b64="QUFB"):
        self.send("\U0001f575\ufe0f")
        self.until("\U0001f635 ")
        self.send("[%s]" % ",".join(map(str, pbox)))
        self.until("\U0001f9c2 ")
        self.send(salt_b64)
        return self.until("\n").strip()
    def auth_begin(self):
        self.send("\U0001f5a5\ufe0f")
        pbox_s = self.until("\U0001f9c2 ")
        salt_b64 = self.until("\U0001f511 ").split()[0].strip()
        import ast
        pbox = ast.literal_eval(pbox_s.split("\U0001f635")[1].split("\U0001f9c2")[0].strip())
        return pbox, base64.b64decode(salt_b64)
    def auth_answer(self, h):
        self.send(h)
        return self.until("\n").strip()
