import sys, wave
import numpy as np

path, t0, t1 = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
step = float(sys.argv[4]) if len(sys.argv) > 4 else 0.05
with wave.open(path) as wf:
    sr = wf.getframerate()
    a = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
n = int(step * sr)
for i in range(int(t0 * sr), min(int(t1 * sr), len(a) - n), n):
    rms = np.sqrt(np.mean(a[i:i + n] ** 2)) + 1e-9
    db = 20 * np.log10(rms)
    print(f"{i / sr:6.2f} {db:6.1f} " + "#" * max(0, int((db + 60) / 1.5)))
