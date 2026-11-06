import json, sys, wave
import numpy as np
from faster_whisper import WhisperModel

model = WhisperModel(sys.argv[1], device="cpu", compute_type="int8")
for path in sys.argv[2:]:
    with wave.open(path) as wf:
        audio = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
    segs, info = model.transcribe(audio, language="pt", word_timestamps=True, vad_filter=False,
                                  beam_size=5, condition_on_previous_text=False,
                                  initial_prompt="Transcrição literal, incluindo repetições, hesitações e erros: é, hum, tipo, né.")
    words = []
    print("==", path)
    for s in segs:
        print(f"[{s.start:6.2f}-{s.end:6.2f}] {s.text}")
        for w in s.words:
            words.append({"text": w.word.strip(), "start": round(w.start, 3), "end": round(w.end, 3), "p": round(w.probability, 2)})
    out = path.rsplit(".", 1)[0] + ".words.json"
    json.dump(words, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
