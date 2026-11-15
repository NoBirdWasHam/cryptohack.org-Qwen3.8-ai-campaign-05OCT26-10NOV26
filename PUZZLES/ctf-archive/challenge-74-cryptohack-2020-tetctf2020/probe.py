import socket, sys, re

HOST, PORT = "archive.cryptohack.org", 63222

def session(idx_lines, guess="0", wait_after_send=False):
    s = socket.create_connection((HOST, PORT), timeout=15)
    s.settimeout(20)
    data = b""
    # send indices + guess immediately (stdout is block-buffered anyway)
    payload = "\n".join(idx_lines) + "\n" + guess + "\n"
    s.sendall(payload.encode())
    try:
        while True:
            b = s.recv(65536)
            if not b: break
            data += b
    except socket.timeout:
        pass
    s.close()
    return data.decode(errors="replace")

if __name__ == "__main__":
    d1 = session(["0", "1"])
    d2 = session(["0", "1"])
    nums1 = re.findall(r"^(\d+)$", d1, re.M)
    nums2 = re.findall(r"^(\d+)$", d2, re.M)
    print("S1 lines:", len(d1.splitlines()), "numbers:", nums1)
    print("S2 lines:", len(d2.splitlines()), "numbers:", nums2)
    print("S1 non-numeric samples:", sorted(set(l for l in d1.splitlines() if not l.isdigit()))[:5])
    print("same-values-across-sessions:", nums1 == nums2)
