"""Trata a voz do material: limpeza leve, EQ de presença, compressão suave, -16 LUFS, sem atraso (latência compensada)."""
import json, re, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
W = ROOT / "work"
SR = 48000


def ff(*a):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-y", *a], capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(r.stderr)
    return r.stderr


dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                            str(ROOT / "src/material.mp4")], capture_output=True, text=True).stdout)
n = round(dur * SR)
ff("-i", str(ROOT / "src/material.mp4"), "-vn", "-ac", "1", "-ar", str(SR), str(W / "voz_bruta.wav"))

chain = ("highpass=f=70,afftdn=nr=10:nf=-45:tn=1,"
         "equalizer=f=220:t=q:w=1.0:g=-1.5,equalizer=f=3200:t=q:w=1.2:g=1.5,highshelf=f=10000:g=1,"
         "acompressor=threshold=-20dB:ratio=2.5:attack=10:release=150:makeup=1.5,apad")
ff("-i", str(W / "voz_bruta.wav"), "-af", chain + f",atrim=end_sample={n + 4800}", "-ar", str(SR), str(W / "voz_pre.wav"))
m = json.loads(re.search(r"\{[\s\S]*\}", ff("-i", str(W / "voz_pre.wav"), "-af", "loudnorm=I=-16:TP=-1.5:LRA=7:print_format=json", "-f", "null", "-")).group(0))
ln = (f"loudnorm=I=-16:TP=-1.5:LRA=7:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:"
      f"measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
ff("-i", str(W / "voz_pre.wav"), "-af", f"{ln},aresample={SR}", "-ar", str(SR), str(W / "voz_norm.wav"))
print("ok", n / SR)
