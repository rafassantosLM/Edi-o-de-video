"""Mixagem: voz tratada + efeitos sonoros (sem trilha — o usuário coloca a música). Pico de cada efeito no tempo da deixa."""
import json, re, subprocess, wave
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
A = ROOT / "edicao/assets"
SR = 48000
cues = json.loads((ROOT / "work/sfx_cues.json").read_text(encoding="utf-8"))
N = int(round(cues["duration"] * SR))


def load(path):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"], capture_output=True, check=True)
    return np.frombuffer(r.stdout, dtype=np.float32).reshape(-1, 2).copy()


def db(g):
    return 10 ** (g / 20)


def place(bus, clip, t):
    i = int(round(t * SR))
    if i < 0:
        clip, i = clip[-i:], 0
    n = min(len(clip), len(bus) - i)
    if n > 0:
        bus[i:i + n] += clip[:n]


voice = load(A / "voz.wav")[:N]
voice = np.pad(voice, ((0, N - len(voice)), (0, 0)))
sfx = np.zeros((N, 2), dtype=np.float32)
cache = {}
for t, name, gain in cues["sfx"]:
    if name not in cache:
        cache[name] = load(A / "sfx" / f"{name}.mp3")
    c = cache[name] * db(gain)
    peak = int(np.argmax(np.abs(c).mean(1)))
    place(sfx, c, t - peak / SR)
t0, t1, g = cues["riser"]
r = load(A / "sfx/riser.mp3")
r = r[int((3.4 - (t1 - t0)) * SR):int(3.4 * SR)] * db(g)
r *= np.linspace(0, 1, len(r))[:, None] ** 0.8
place(sfx, r, t0)

mix = voice + sfx
raw = ROOT / "work/mix_raw.wav"
with wave.open(str(raw), "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes())
res = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(raw), "-af", "loudnorm=I=-15:TP=-1.5:LRA=9:print_format=json", "-f", "null", "-"],
                     capture_output=True, text=True)
j = json.loads(re.search(r"\{[\s\S]*\}", res.stderr).group(0))
ln = (f"loudnorm=I=-15:TP=-1.5:LRA=9:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:"
      f"measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af", f"{ln},aresample={SR},apad,atrim=end_sample={N}", "-ar", str(SR), str(A / "mix.wav")], check=True)
print("mix ok", N / SR)
