import socket, sys, types, os, threading, random

# POSIX signal shim for Windows
sig = types.ModuleType('signal')
sig.SIGALRM = 14
def _noop(*a, **k): pass
sig.signal = _noop
sig.alarm = _noop
sys.modules['signal'] = sig

os.environ['FLAG'] = 'FLAG-REDACTED-SEE-FLAGS-MIRROR'
sys.argv = ['auth_chall']

import importlib.util
spec = importlib.util.spec_from_file_location('auth_chall_mod', 'auth_chall.py')
mod = importlib.util.module_from_spec(spec)
# prevent __main__ guard: module name is not __main__ so import is safe
spec.loader.exec_module(mod)

def handle(conn):
    import io, contextlib
    r = conn.makefile('rb')
    w = conn.makefile('wb')
    real_in, real_out = sys.stdin, sys.stdout
    def inp(prompt=''):
        w.write(prompt.encode()); w.flush()
        line = r.readline()
        if not line: raise EOFError
        return line.decode().strip()
    def pr(*args, **kw):
        text = ' '.join(str(a) for a in args) + kw.get('end', '\n')
        w.write(text.encode()); w.flush()
    try:
        sys.stdin = inp
        class O:
            def write(self, s): pr(s, end='')
            def flush(self): pass
        sys.stdout = O()
        # rerun test() + main() logic inline to allow password peek for local debug
        mod.signal = sig
        flag = os.environ['FLAG']
        password = bytes(random.sample(b'0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', 6))
        client = mod.AuthenticationClient(password)
        server = mod.AuthenticationServer(password)
        try:
            cc = bytes.fromhex(inp('challenge_client = '))
            rs, cs = server.handshake(cc)
            pr(f'response_server = {rs.hex()}')
            pr(f'challenge_server = {cs.hex()}')
            rc = bytes.fromhex(inp('response_client = '))
            server.verify_handshake(rc)
            pr(f'Congrats! {flag}')
            print('LOCAL-SECRET pw=' + password.decode(), file=sys.stderr)
        except Exception as err:
            pr(f'\033[031mError: {err}\033[0m')
            print('LOCAL-SECRET pw=' + password.decode(), file=sys.stderr)
    finally:
        sys.stdin, sys.stdout = real_in, real_out
        conn.close()

srv = socket.socket()
srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind(('127.0.0.1', 13338))
srv.listen(5)
print('serving on 13338', flush=True)
while True:
    c, a = srv.accept()
    threading.Thread(target=handle, args=(c,), daemon=True).start()
