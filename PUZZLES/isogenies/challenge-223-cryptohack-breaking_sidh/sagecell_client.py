"""Drive a Sage cell on sagecell.sagemath.org headlessly (SockJS-era Jupyter protocol)."""
import json, sys, time, uuid, urllib.request, urllib.parse
import websocket

BASE = "https://sagecell.sagemath.org/"

def _post(path, data, tries=5):
    for k in range(tries):
        try:
            req = urllib.request.Request(BASE + path,
                data=urllib.parse.urlencode(data).encode(),
                headers={"Referer": BASE, "User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.loads(r.read().decode())
        except Exception:
            if k == tries - 1:
                raise
            time.sleep(15)

def run(code, timeout=850, verbose=False, max_wait=None):
    """Execute `code` in a fresh Sage kernel; return (stdout, ename, evalue)."""
    if max_wait is None:
        max_wait = timeout + 120
    d = _post("kernel", {"timeout": str(timeout), "accepted_tos": "true",
                         "CellSessionID": str(uuid.uuid4())})
    ws_url = d["ws_url"].replace("http", "ws", 1) + f"kernel/{d['id']}/channels"
    for k in range(5):
        try:
            ws = websocket.create_connection(ws_url, timeout=60,
                                             origin="https://sagecell.sagemath.org",
                                             header={"Referer": BASE})
            break
        except Exception:
            if k == 4: raise
            time.sleep(10)
            d = _post("kernel", {"timeout": str(timeout), "accepted_tos": "true",
                                 "CellSessionID": str(uuid.uuid4())})
            ws_url = d["ws_url"].replace("http", "ws", 1) + f"kernel/{d['id']}/channels"
    session = str(uuid.uuid4())
    def msg(mtype, content):
        return {"header": {"msg_type": mtype, "msg_id": str(uuid.uuid4()),
                           "username": "u", "session": session, "version": "5.0"},
                "parent_header": {}, "metadata": {}, "content": content, "buffers": []}
    ws.send(json.dumps(msg("execute_request", {
        "code": code, "silent": False, "store_history": False,
        "user_expressions": {}, "allow_stdin": False})))
    out, err = [], (None, None)
    t0 = time.time()
    got_reply = False
    while time.time() - t0 < max_wait:
        try:
            ws.settimeout(max_wait - (time.time() - t0))
            r = json.loads(ws.recv())
        except Exception as e:
            err = ("client_exc", repr(e)[:200]); break
        mt = r.get("header", {}).get("msg_type", "")
        ch = r.get("channel", "")
        c = r.get("content", {})
        if ch == "iopub" and mt == "stream":
            out.append(c.get("text", ""))
            if verbose:
                sys.stdout.write(c.get("text", "")); sys.stdout.flush()
        elif mt == "error":
            err = (c.get("ename", "?"), c.get("evalue", "")[:400])
        elif ch == "shell" and mt == "execute_reply":
            got_reply = True
            if c.get("status") == "aborted":
                err = ("aborted", str(c)[:200])
            break
        elif ch == "iopub" and mt == "status" and c.get("execution_state") == "dead":
            if not got_reply:
                err = err[0] and err or ("kernel_dead", "kernel died mid-run")
            break
    try: ws.close()
    except Exception: pass
    return "".join(out), err[0], err[1]

if __name__ == "__main__":
    code = open(sys.argv[1]).read() if len(sys.argv) > 1 else "print(2+2)"
    to = int(sys.argv[2]) if len(sys.argv) > 2 else 120
    o, en, ev = run(code, timeout=to, verbose=True)
    print(f"\n[client] ename={en} evalue={ev}")
