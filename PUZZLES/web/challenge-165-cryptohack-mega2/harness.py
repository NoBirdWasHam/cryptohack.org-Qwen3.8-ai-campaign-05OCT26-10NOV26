# Local harness: run the challenge source in-process with a stubbed listener.
import sys, types, json, importlib.util

def load_challenge(src_path):
    mod = types.ModuleType("utils")
    class _L:
        @staticmethod
        def start_server(port=0): pass
    mod.listener = _L
    sys.modules["utils"] = mod
    spec = importlib.util.spec_from_file_location("chal_src", src_path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.Challenge()

def drive(ch, msgs):
    """msgs: list of dicts. Returns list of (response, before_send_text)."""
    out = []
    for msg in msgs:
        ch.exit = False
        resp = ch.challenge(msg)
        out.append(resp)
        if getattr(ch, "exit", False):
            break
    return out

if __name__ == "__main__":
    import os
    base = os.path.dirname(os.path.abspath(__file__))
    src = sys.argv[1]
    ch = load_challenge(src)
    print("before_input:\n", ch.before_input[:400], flush=True)
