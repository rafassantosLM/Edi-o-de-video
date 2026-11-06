"""Monta a base do edit: cortes (erros/respiros), J-cuts, cor, 1080x1920, e o áudio de diálogo limpo.

Segmentos definidos pelo ÁUDIO (fala). O vídeo do segmento seguinte entra `L` segundos
depois do áudio dele (J-cut): o som chega antes da imagem.
"""
import json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FPS = 30
SRC = {"H": ROOT / "src/gancho.mp4", "C": ROOT / "src/conteudo.mp4"}

# (fonte, inicio_audio, fim_audio, J-cut L para a entrada da IMAGEM deste segmento, rótulo)
SEGS = [
    ("H", 0.64, 6.58, 0.00, "Gancho"),
    # 0.44–2.02 era a 1ª tentativa ("Mas calma que se você" + pausa): descartada, a 2ª saiu inteira
    ("C", 3.36, 9.18, 0.25, "Mas calma que se você subir um vídeo lá agora... não é assim."),
    ("C", 19.64, 25.68, 0.12, "Isso porque a gente utiliza um método..."),
    ("C", 26.64, 34.90, 0.12, "CTA"),
]
VIDEO_TAIL_END = 35.55  # último plano segura um pouco depois da fala

GRADE = ("hqdn3d=2:1.5:4:3,hflip,scale=1080:1920:flags=lanczos,"
         "eq=brightness=0.04:contrast=1.08:saturation=1.05:gamma=1.12,"
         "colorbalance=rs=0.03:bs=-0.05:rm=0.04:bm=-0.04:rh=0.02:bh=-0.02,unsharp=5:5:0.6")


def q(t):  # quantiza para o grid de quadros
    return round(t * FPS) / FPS


def main():
    # tempos de saída do áudio
    out_a, t = [], 0.0
    for src, a0, a1, L, lab in SEGS:
        a0, a1 = q(a0), q(a1)
        out_a.append((src, a0, a1, t, L, lab))
        t += a1 - a0
    audio_end = t

    # vídeo: segmento i vai de (O_i + L_i) até (O_{i+1} + L_{i+1}); fonte deslocada igual para manter sincronia
    vsegs = []
    for i, (src, a0, a1, o, L, lab) in enumerate(out_a):
        v_out0 = q(o + L)
        if i + 1 < len(out_a):
            v_out1 = q(out_a[i + 1][3] + out_a[i + 1][4])
            v_src1 = a0 + (v_out1 - o)
        else:
            v_src1 = q(VIDEO_TAIL_END)
            v_out1 = q(o + (v_src1 - a0))
        v_src0 = a0 + (v_out0 - o)
        vsegs.append(dict(src=src, src0=round(v_src0, 4), src1=round(v_src1, 4), out0=round(v_out0, 4), out1=round(v_out1, 4), label=lab))
    total = vsegs[-1]["out1"]

    fc, vlab, alab = [], [], []
    for i, v in enumerate(vsegs):
        inp = 0 if v["src"] == "H" else 1
        fc.append(f"[{inp}:v]trim=start={v['src0']}:end={v['src1']},setpts=PTS-STARTPTS,fps={FPS},{GRADE},setsar=1[v{i}]")
        vlab.append(f"[v{i}]")
    for i, (src, a0, a1, o, L, lab) in enumerate(out_a):
        inp = 0 if src == "H" else 1
        d = a1 - a0
        fc.append(f"[{inp}:a]atrim=start={a0}:end={a1},asetpts=PTS-STARTPTS,aresample=48000,"
                  f"afade=t=in:d=0.012,afade=t=out:st={d - 0.018:.4f}:d=0.018[a{i}]")
        alab.append(f"[a{i}]")
    fc.append("".join(vlab) + f"concat=n={len(vlab)}:v=1:a=0[vout]")
    fc.append("".join(alab) + f"concat=n={len(alab)}:v=0:a=1,apad=whole_dur={total}[aout]")

    work = ROOT / "work"
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", str(SRC["H"]), "-i", str(SRC["C"]),
           "-filter_complex", ";".join(fc),
           "-map", "[vout]", "-c:v", "libx264", "-preset", "slow", "-crf", "14", "-pix_fmt", "yuv420p", "-r", str(FPS),
           "-t", str(total), str(work / "base_video.mp4"),
           "-map", "[aout]", "-c:a", "pcm_s16le", "-ac", "1", "-t", str(total), str(work / "dialogo_bruto.wav")]
    subprocess.run(cmd, check=True)

    edl = dict(fps=FPS, total=total, audio_end=round(audio_end, 4),
               audio=[dict(src=s, a0=a0, a1=a1, out0=round(o, 4), out1=round(o + a1 - a0, 4), label=lab) for s, a0, a1, o, L, lab in out_a],
               video=vsegs)
    (work / "edl.json").write_text(json.dumps(edl, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(edl, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
