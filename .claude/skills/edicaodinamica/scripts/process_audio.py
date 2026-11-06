"""Limpa o diálogo: tira ruído, EQ de voz, compressão, normaliza em -16 LUFS e compensa a latência dos filtros."""
import json, re, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
W = ROOT / "work"
SR = 48000
LATENCY = 1584  # 33 ms medidos (afftdn + anlmdn) com lagcheck.py

total = json.loads((W / "edl.json").read_text(encoding="utf-8"))["total"]
n = round(total * SR)
chain = ("highpass=f=75,afftdn=nr=18:nf=-42:tn=1,anlmdn=s=4:p=0.002:r=0.006,"
         "equalizer=f=220:t=q:w=1.0:g=-2.5,equalizer=f=3200:t=q:w=1.2:g=2.5,highshelf=f=9000:g=1.5,"
         "acompressor=threshold=-22dB:ratio=3:attack=8:release=140:makeup=2,"
         "agate=threshold=0.012:ratio=1.8:range=0.25:attack=4:release=160,apad")


def ff(*a, capture=False):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-y", *a], capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(r.stderr)
    return r.stderr


ff("-i", str(W / "dialogo_bruto.wav"), "-af", chain + f",atrim=end_sample={n + LATENCY}", "-ar", str(SR), str(W / "dialogo_pre.wav"))
m = json.loads(re.search(r"\{[\s\S]*\}", ff("-i", str(W / "dialogo_pre.wav"), "-af", "loudnorm=I=-16:TP=-1.5:LRA=7:print_format=json", "-f", "null", "-")).group(0))
ln = (f"loudnorm=I=-16:TP=-1.5:LRA=7:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:"
      f"measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
ff("-i", str(W / "dialogo_pre.wav"), "-af", f"{ln},aresample={SR},atrim=start_sample={LATENCY},asetpts=PTS-STARTPTS,apad,atrim=end_sample={n}",
   "-ar", str(SR), str(W / "dialogo_final.wav"))
print("ok", n / SR)
