import sys, re
src = open("chall.py").read()
src = src.replace("from secret import message", "message = b'crypto{local_test_flag_ends_with_a_dot}.'")
open("chall_local.py", "w").write(src)
