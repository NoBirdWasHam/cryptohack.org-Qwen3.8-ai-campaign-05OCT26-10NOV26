# Run chall.py locally on Windows (signal.alarm is Unix-only -> stub it).
import signal
signal.alarm = lambda n: None
import runpy
runpy.run_path('chall.py', run_name='__main__')
