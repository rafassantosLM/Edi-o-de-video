import sys
import numpy as np, librosa

for p in sys.argv[1:]:
    y, sr = librosa.load(p, sr=22050, mono=True)
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr, units="time")
    rms = librosa.feature.rms(y=y, hop_length=512)[0]
    t = librosa.times_like(rms, sr=sr, hop_length=512)
    low = librosa.feature.rms(y=librosa.effects.preemphasis(y, coef=-0.97), hop_length=512)[0]
    print("==", p.split("\\")[-1], "tempo", np.round(tempo, 1), "n_beats", len(beats))
    print("beats:", " ".join(f"{b:.2f}" for b in beats[:40]))
    # energia por segundo (para ver intro/drop)
    for s in range(0, int(t[-1]) + 1):
        m = (t >= s) & (t < s + 1)
        db = 20 * np.log10(rms[m].mean() + 1e-9)
        print(f"{s:3d}s {db:6.1f} " + "#" * max(0, int((db + 40) / 1.0)))
