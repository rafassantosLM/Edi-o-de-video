"""Gera o b-roll no Higgsfield: etapa 'images' (frames iniciais) ou 'videos' (Kling 3.0 Pro a partir do frame).

Uso:
  python gen_broll.py cost images|videos <id ...> | --all   # só estima créditos, não gera
  python gen_broll.py images|videos <id ...> | --all        # gera e baixa para ../broll/

Sempre rode `cost` antes e mostre o total ao usuário (regra de custo da meueditor).
Sem ids nem --all o script recusa: nunca dispara o lote inteiro por engano.
"""
import json, re, shutil, subprocess, sys, urllib.request, concurrent.futures as cf
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "broll"
SHOTS = json.loads((ROOT / "scripts/broll.json").read_text(encoding="utf-8-sig"))
HF = shutil.which("higgsfield") or shutil.which("higgsfield.cmd") or "higgsfield"
VIDEO_ARGS = ["--aspect_ratio", "9:16", "--duration", "5", "--mode", "pro", "--sound", "off"]


def run(args):
    r = subprocess.run([HF, *args, "--wait", "--wait-timeout", "25m", "--json"], capture_output=True, text=True, encoding="utf-8")
    if r.returncode:
        raise RuntimeError(r.stderr.strip() or r.stdout.strip())
    data = json.loads(r.stdout)
    job = data[0] if isinstance(data, list) else data
    if job.get("status") != "completed" or not job.get("result_url"):
        raise RuntimeError(f"status={job.get('status')} {job}")
    return job


def frame_of(s):
    return next((p for p in OUT.glob(f"{s['id']}.*") if p.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp")), None)


def cost(stage, s):
    if stage == "images":
        args = ["generate", "cost", s["image_model"], "--prompt", s["image_prompt"], *s["image_args"]]
        note = ""
    else:
        src = frame_of(s)
        args = ["generate", "cost", "kling3_0", "--prompt", s["video_prompt"], *VIDEO_ARGS]
        if src:
            args += ["--start-image", str(src)]  # a imagem é enviada à Higgsfield já na estimativa
        note = "" if src else " (sem quadro ainda: estimativa sem --start-image)"
    r = subprocess.run([HF, *args], capture_output=True, text=True, encoding="utf-8")
    m = re.search(r"([\d.]+)\s*credits?", r.stdout + r.stderr)
    if not m:
        raise RuntimeError((r.stderr or r.stdout).strip())
    return float(m.group(1)), note


def image(s):
    job = run(["generate", "create", s["image_model"], "--prompt", s["image_prompt"], *s["image_args"]])
    url = job["result_url"]
    ext = Path(url.split("?")[0]).suffix or ".png"
    dst = OUT / f"{s['id']}{ext}"
    urllib.request.urlretrieve(url, dst)
    return f"{s['id']}: imagem ok -> {dst.name}"


def video(s):
    src = frame_of(s)
    if not src:
        return f"{s['id']}: sem imagem"
    job = run(["generate", "create", "kling3_0", "--prompt", s["video_prompt"], "--start-image", str(src), *VIDEO_ARGS])
    dst = OUT / f"{s['id']}.mp4"
    urllib.request.urlretrieve(job["result_url"], dst)
    return f"{s['id']}: vídeo ok -> {dst.name}"


def pick(ids):
    if not ids:
        sys.exit("Diga quais cenas (ids do broll.json) ou passe --all. Rode 'cost' antes.")
    if ids == ["--all"]:
        return SHOTS
    known = {s["id"] for s in SHOTS}
    missing = [i for i in ids if i not in known]
    if missing:
        sys.exit(f"ids desconhecidos: {', '.join(missing)}")
    return [s for s in SHOTS if s["id"] in ids]


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    if args[0] == "cost":
        stage, todo = args[1], pick(args[2:])
        total = 0.0
        for s in todo:
            c, note = cost(stage, s)
            total += c
            print(f"{s['id']}: {c:g} créditos{note}")
        print(f"TOTAL ({stage}, {len(todo)} cenas): {total:g} créditos")
        sys.exit(0)
    stage, todo = args[0], pick(args[1:])
    if stage not in ("images", "videos"):
        sys.exit(__doc__)
    OUT.mkdir(exist_ok=True)
    fn = image if stage == "images" else video
    with cf.ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(fn, s): s["id"] for s in todo}
        for f in cf.as_completed(futs):
            try:
                print(f.result(), flush=True)
            except Exception as e:  # noqa: BLE001
                print(f"{futs[f]}: ERRO {e}", flush=True)
