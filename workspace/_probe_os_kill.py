import os
import subprocess
import sys
import time

p = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(10)"])
time.sleep(1)
probe_ok = True
try:
    os.kill(p.pid, 0)
except OSError:
    probe_ok = False
time.sleep(1)
alive = p.poll() is None
print("platform:", sys.platform)
print("probe returned without error:", probe_ok)
print("still alive after probe:", alive)
p.terminate()