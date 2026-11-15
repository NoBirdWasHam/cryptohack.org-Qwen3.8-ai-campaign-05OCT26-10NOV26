# Local harness: run the real chall.py logic over a socket (localhost only).
import socketserver, os, sys
os.environ['FLAG'] = 'firebird{local_test_flag}'
SRC = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chall.py')).read()

class H(socketserver.StreamRequestHandler):
    def handle(self):
        si, so = self.rfile, self.wfile
        def inp(*a):
            line = si.readline()
            if not line:
                raise EOFError
            return line.decode().rstrip('\r\n')
        def prn(*a, **k):
            so.write((' '.join(map(str, a)) + '\n').encode())
            so.flush()
        g = {'__name__': '__main__', 'input': inp, 'print': prn}
        try:
            exec(compile(SRC, 'chall.py', 'exec'), g)
        except (SystemExit, EOFError):
            pass
        try:
            with open('true_gp.log', 'a') as f:
                f.write("%d %d\n" % (g.get('g', -1), g.get('p', -1)))
        except Exception:
            pass

socketserver.ThreadingTCPServer.allow_reuse_address = True
socketserver.ThreadingTCPServer(('127.0.0.1', 19391), H).serve_forever()
