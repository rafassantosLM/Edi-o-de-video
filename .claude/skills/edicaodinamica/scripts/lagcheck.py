"""Confere se o áudio processado continua alinhado ao bruto (lag por correlação em várias janelas)."""
import sys, wave
import numpy as np


def load(p):
    with wave.open(p) as w:
        sr = w.getframerate()
        a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
        if w.getnchannels() > 1:
            a = a.reshape(-1, w.getnchannels()).mean(1)
    return a, sr


a, sr = load(sys.argv[1])
b, _ = load(sys.argv[2])
print("dur", len(a) / sr, len(b) / sr)
win, maxlag = int(1.0 * sr), int(0.5 * sr)
for t in np.arange(1.0, min(len(a), len(b)) / sr - 1.6, 3.0):
    i = int(t * sr)
    x = a[i:i + win]
    best, bl = -1, 0
    seg = b[max(0, i - maxlag):i + win + maxlag]
    c = np.correlate(seg, x, mode="valid")
    lag = int(np.argmax(np.abs(c))) - (i - max(0, i - maxlag))
    print(f"t={t:5.1f}s lag={lag / sr * 1000:7.1f} ms")
