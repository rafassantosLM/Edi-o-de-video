"""Converte os tempos das palavras (fonte) para o tempo do vídeo editado, usando o edl.json."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
edl = json.loads((ROOT / "work/edl.json").read_text(encoding="utf-8"))
words = {"H": json.loads((ROOT / "work/gancho.words.json").read_text(encoding="utf-8")),
         "C": json.loads((ROOT / "work/conteudo.words.json").read_text(encoding="utf-8"))}
FIX = {"Claudio": "Claude", "Claudio,": "Claude,"}

out = []
for seg in edl["audio"]:
    for w in words[seg["src"]]:
        mid = (w["start"] + w["end"]) / 2
        if seg["a0"] - 0.02 <= mid <= seg["a1"] + 0.02:
            s = max(w["start"], seg["a0"]) - seg["a0"] + seg["out0"]
            e = min(w["end"], seg["a1"]) - seg["a0"] + seg["out0"]
            out.append({"text": FIX.get(w["text"], w["text"]), "start": round(s, 3), "end": round(e, 3)})
(ROOT / "work/words_out.json").write_text(json.dumps(out, ensure_ascii=False, indent=0), encoding="utf-8")
for w in out:
    print(f"{w['start']:6.2f} {w['end']:6.2f} {w['text']}")
