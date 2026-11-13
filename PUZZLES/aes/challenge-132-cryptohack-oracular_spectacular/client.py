#!/usr/bin/env python3
"""Robust client for oracular_spectacular with optional pipelining."""
import socket, json, os

HOST, PORT = "socket.cryptohack.org", 13423

class Client:
    def __init__(self):
        self.s = socket.create_connection((HOST, PORT), timeout=60)
        self.s.settimeout(60)
        self.buf = b""
        # greeting
        while b"\n" not in self.buf:
            d = self.s.recv(65536)
            if not d: raise EOFError("closed on greeting")
            self.buf += d
        self.greeting = self.buf[:self.buf.index(b"\n")+1]
        self.buf = self.buf[self.buf.index(b"\n")+1:]

    def _recv_obj(self):
        dec = json.JSONDecoder()
        while True:
            # skip whitespace
            i = 0
            b = self.buf
            while i < len(b) and b[i:i+1] in (b" ", b"\n", b"\r", b"\t"):
                i += 1
            if i < len(b) and b[i:i+1] == b"{":
                try:
                    o, end = dec.raw_decode(b[i:].decode("utf-8", "ignore"))
                    self.buf = b[i:][end:]
                    return o
                except (json.JSONDecodeError, UnicodeDecodeError):
                    pass
            d = self.s.recv(65536)
            if not d: raise EOFError("closed")
            self.buf += d

    def _send(self, obj):
        self.s.sendall((json.dumps(obj) + "\n").encode())

    def encrypt(self):
        self._send({"option": "encrypt"})
        return bytes.fromhex(self._recv_obj()["ct"])

    def unpad(self, ct: bytes):
        self._send({"option": "unpad", "ct": ct.hex()})
        return self._recv_obj()

    def unpad_batch(self, cts, chunk=10):
        """Pipelined unpad queries: one sendall per batch, payload < 1024 B
        (server does a single recv(1024) and splits on newlines; a partial
        trailing line would abort the connection). Returns list of bool."""
        results = []
        i = 0
        while i < len(cts):
            batch = cts[i:i+chunk]
            payload = "".join(json.dumps({"option": "unpad", "ct": c.hex()}) + "\n" for c in batch)
            assert len(payload) < 1000, len(payload)
            self.s.sendall(payload.encode())
            for _ in batch:
                o = self._recv_obj()
                if "result" not in o:
                    raise RuntimeError(f"unexpected: {o}")
                results.append(o["result"])
            i += chunk
        return results

    def check(self, message):
        self._send({"option": "check", "message": message})
        return self._recv_obj()

    def close(self):
        try: self.s.close()
        except Exception: pass
