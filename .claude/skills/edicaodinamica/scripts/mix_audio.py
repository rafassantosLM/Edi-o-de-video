"""Mixagem final: diálogo limpo + trilha (filtrada no gancho, drop no corte, ducking sob a voz) + efeitos sonoros leves.

Cada efeito tem o PICO alinhado ao tempo da deixa (exceto o riser, que termina no corte).
"""
import json, subprocess, wave
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
W, A = ROOT / "work", ROOT / "edicao/assets"
SR = 48000
TOTAL = json.loads((W / "edl.json").read_text(encoding="utf-8"))["total"]
CUT = 6.2           # corte gancho -> conteúdo (imagem)
MUSIC_FILE = ROOT / "audio/trilha_A.wav"
MUSIC_OFFSET = 1.35  # drop da trilha (7.55s) cai no corte (6.2s)

# (tempo da deixa, arquivo, ganho dB)
SFX = [
    (0.80, "pop", -20),
    (2.50, "pop", -14),            # chip "Claude"
    (6.20, "impact-bass-1", -12),  # drop
    (6.17, "whoosh-short", -15),
    (7.20, "click-soft", -17),     # card de upload entra
    (8.95, "glitch-1", -24),       # "não"
    (10.78, "whoosh-short", -17),  # punch "não é assim"
    (11.87, "whoosh", -19),        # corte
    (13.30, "sparkle", -17),       # "método"
    (14.02, "pop", -18),           # chip Claude
    (16.30, "whoosh", -16),        # vídeo vira "tela"
    (17.90, "whoosh-short", -17),  # volta
    (19.25, "click-soft", -15),
    (21.02, "click-soft", -15),
    (22.74, "click-soft", -15),
    (23.42, "whoosh-short", -16),  # CTA
    (24.22, "key-press", -20),
    (24.40, "key-press", -21),
    (24.58, "key-press", -20),
    (24.86, "pop", -13),           # enviar comentário
    (25.12, "notification", -19),  # DM
]


def load(path):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"],
                       capture_output=True, check=True)
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


N = int(round(TOTAL * SR))
voice = load(W / "dialogo_final.wav")[:N]
voice = np.pad(voice, ((0, N - len(voice)), (0, 0)))

# ---------- trilha ----------
m = load(MUSIC_FILE)
m = m[int(MUSIC_OFFSET * SR):][:N]
m = np.pad(m, ((0, N - len(m)), (0, 0)))
# gancho: passa-baixa que vai abrindo (sweep) até o drop — feito com filtro de 1 polo por blocos
cut_i = int(CUT * SR)
hook = m[:cut_i].copy()
out = np.zeros_like(hook)
state = np.zeros(2, dtype=np.float32)
blk = 480
for s in range(0, len(hook), blk):
    t = s / SR
    prog = min(1.0, max(0.0, (t - 2.8) / (CUT - 0.1 - 2.8)))
    fc = 700 * (9000 / 700) ** (prog ** 2)        # 700 Hz -> 9 kHz
    a = 1 - np.exp(-2 * np.pi * fc / SR)
    x = hook[s:s + blk]
    y = np.empty_like(x)
    for k in range(len(x)):
        state += a * (x[k] - state)
        y[k] = state
    out[s:s + blk] = y
m[:cut_i] = out * db(5)
# micro-silêncio antes do drop (já existe na trilha) + leve fade de saída
fade = int(0.9 * SR)
m[-fade:] *= np.linspace(1, 0, fade)[:, None] ** 1.5

# ducking pela voz (envelope suave)
env = np.abs(voice).mean(1)
win = int(0.03 * SR)
env = np.convolve(env, np.ones(win) / win, mode="same")
speech = (env > db(-38)).astype(np.float32)
att, rel = int(0.04 * SR), int(0.35 * SR)
g = np.empty_like(speech)
cur = 0.0
for i in range(0, N, 240):  # 5 ms
    target = speech[i]
    step = 240 / (att if target > cur else rel)
    cur = cur + np.clip(target - cur, -step, step)
    g[i:i + 240] = cur
duck = 1 - g * (1 - db(-7))
music_gain = db(-13)
m *= (music_gain * duck)[:, None]

# ---------- efeitos ----------
sfx_bus = np.zeros((N, 2), dtype=np.float32)
for t, name, gain in SFX:
    c = load(A / "sfx" / f"{name}.mp3") * db(gain)
    peak = int(np.argmax(np.abs(c).mean(1)))
    place(sfx_bus, c, t - peak / SR)
# riser: termina no corte (pico em ~3.4s do arquivo)
r = load(A / "sfx/riser.mp3")[int(0.4 * SR):int(3.4 * SR)] * db(-15)
r *= np.linspace(0, 1, len(r))[:, None] ** 0.7
place(sfx_bus, r, CUT - len(r) / SR)

def rms_db(x, mask):
    return 20 * np.log10(np.sqrt(np.mean(x[mask] ** 2)) + 1e-9)


sp = speech > 0.5
hook_sp, body_sp = sp.copy(), sp.copy()
hook_sp[cut_i:], body_sp[:cut_i] = False, False
print(f"voz vs trilha (durante a fala): gancho {rms_db(voice, hook_sp) - rms_db(m, hook_sp):.1f} dB | "
      f"conteúdo {rms_db(voice, body_sp) - rms_db(m, body_sp):.1f} dB")

mix = voice + m + sfx_bus
mix = mix.astype(np.float32)
raw = W / "mix_raw.wav"
with wave.open(str(raw), "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes())

# loudness final para Reels/TikTok: -14 LUFS, true peak -1
import re
r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(raw), "-af", "loudnorm=I=-14:TP=-1:LRA=9:print_format=json", "-f", "null", "-"],
                   capture_output=True, text=True)
j = json.loads(re.search(r"\{[\s\S]*\}", r.stderr).group(0))
ln = (f"loudnorm=I=-14:TP=-1:LRA=9:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:"
      f"measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af", f"{ln},aresample={SR},apad,atrim=end_sample={N}", "-ar", str(SR), str(A / "mix.wav")], check=True)
print("mix ok", N / SR, "s")
