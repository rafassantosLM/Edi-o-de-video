"""Gera o b-roll no Higgsfield: etapa 'images' (frames iniciais) ou 'videos' (Kling 3.0 Pro a partir do frame).

Uso: python gen_broll.py images|videos [id ...]
Roda os jobs em paralelo e baixa os resultados para ../broll/.
"""
import json, subprocess, sys, urllib.request, concurrent.futures as cf
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "broll"
OUT.mkdir(exist_ok=True)
SHOTS = json.loads((ROOT / "scripts/broll.json").read_text(encoding="utf-8-sig"))
HF = "higgsfield.cmd"


def run(args):
    r = subprocess.run([HF, *args, "--wait", "--wait-timeout", "25m", "--json"], capture_output=True, text=True, encoding="utf-8")
    if r.returncode:
        raise RuntimeError(r.stderr.strip() or r.stdout.strip())
    data = json.loads(r.stdout)
    job = data[0] if isinstance(data, list) else data
    if job.get("status") != "completed" or not job.get("result_url"):
        raise RuntimeError(f"status={job.get('status')} {job}")
    return job


def image(s):
    job = run(["generate", "create", s["image_model"], "--prompt", s["image_prompt"], *s["image_args"]])
    url = job["result_url"]
    ext = Path(url.split("?")[0]).suffix or ".png"
    dst = OUT / f"{s['id']}{ext}"
    urllib.request.urlretrieve(url, dst)
    return f"{s['id']}: imagem ok -> {dst.name}"


def video(s):
    src = next((p for p in OUT.glob(f"{s['id']}.*") if p.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp")), None)
    if not src:
        return f"{s['id']}: sem imagem"
    job = run(["generate", "create", "kling3_0", "--prompt", s["video_prompt"], "--start-image", str(src),
               "--aspect_ratio", "9:16", "--duration", "5", "--mode", "pro", "--sound", "off"])
    dst = OUT / f"{s['id']}.mp4"
    urllib.request.urlretrieve(job["result_url"], dst)
    return f"{s['id']}: vídeo ok -> {dst.name}"


if __name__ == "__main__":
    stage, ids = sys.argv[1], set(sys.argv[2:])
    todo = [s for s in SHOTS if not ids or s["id"] in ids]
    fn = image if stage == "images" else video
    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(fn, s): s["id"] for s in todo}
        for f in cf.as_completed(futs):
            try:
                print(f.result(), flush=True)
            except Exception as e:  # noqa: BLE001
                print(f"{futs[f]}: ERRO {e}", flush=True)
