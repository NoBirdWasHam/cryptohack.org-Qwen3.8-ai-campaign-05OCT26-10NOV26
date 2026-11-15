#!/usr/bin/env python3
# Live health probe 2026-11-07: connect once, read banner fully (idle-timeout),
# then try a minimal menu interaction. Log everything with timestamps.
import socket, time, sys, json

HOST = "archive.cryptohack.org"
PORT = 21970
IDLE = 25  # seconds of silence after which we consider stream stalled

def read_chunky(s, idle=IDLE, max_bytes=200000):
    buf = b""
    t_start = time.time()
    marks = []
    s.settimeout(idle)
    while True:
        try:
            chunk = s.recv(4096)
        except socket.timeout:
            marks.append(("idle_timeout", time.time() - t_start))
            return buf, False, marks
        except Exception as e:
            marks.append(("recv_error:%r" % e, time.time() - t_start))
            return buf, True, marks
        if not chunk:
            marks.append(("eof", time.time() - t_start))
            return buf, True, marks
        buf += chunk
        marks.append((len(chunk), round(time.time() - t_start, 3)))
        if len(buf) >= max_bytes:
            return buf, False, marks

def main():
    log = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
    s = socket.create_connection((HOST, PORT), timeout=15)
    buf, eof, marks = read_chunky(s)
    log["banner_bytes"] = len(buf)
    log["eof_first_phase"] = eof
    log["chunk_marks"] = marks[:40]
    log["banner_repr"] = repr(buf[:400].decode("utf-8", "replace"))
    lines = buf.decode("utf-8", "replace").splitlines()
    digit_lines = [l for l in lines if l.strip().isdigit()]
    log["digit_line_count"] = len(digit_lines)
    if eof:
        log["note"] = "server closed after banner; no interaction possible"
        s.close()
        print(json.dumps(log, indent=1))
        return
    # not eof: try menu interaction
    s.settimeout(12)
    def try_send(payload, label):
        try:
            s.sendall(payload)
        except Exception as e:
            log.setdefault("sends", {})[label] = "send_error:%r" % e
            return b""
        data = b""
        while True:
            try:
                ch = s.recv(4096)
            except socket.timeout:
                break
            if not ch:
                data += b"<EOF>"
                break
            data += ch
            if len(data) > 4000:
                break
        log.setdefault("sends", {})[label] = repr(data[:800].decode("utf-8", "replace"))
        return data
    r = try_send(b"1\n", "menu:1")
    if r and b"Choose N" in r:
        r = try_send(b"131\n", "N:131")
        if r and b"hexadecimal" in r:
            r = try_send(b"00 00\n", "msg:0000")
            if r and b"> " in r:
                r = try_send(b"3\n", "decrypt")
    s.close()
    print(json.dumps(log, indent=1))

if __name__ == "__main__":
    main()
