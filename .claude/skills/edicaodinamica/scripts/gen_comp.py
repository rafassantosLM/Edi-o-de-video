"""Gera edicao/index.html (HyperFrames) e work/sfx_cues.json a partir de um roteiro de edição em dados.

Tudo que é tempo vem da fala do material (material.words.json), então imagem, texto e efeitos
sonoros ficam no mesmo relógio. Rodar de novo depois de qualquer ajuste de tempo.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D = 54.5667  # duração do material (1637 quadros a 30 fps)

# ----------------------------------------------------------------------------------------------
# B-ROLL EM TELA CHEIA: (id, arquivo, início, fim, início dentro do clipe)
FULL = [
    ("f1", "b1_aerea_eua", 1.98, 2.88, 0.6),
    ("f2", "b3_notebook_noite", 10.30, 12.40, 2.7),
    ("f3", "b4_casa_abandonada", 14.52, 17.46, 0.5),
    ("f4", "b5_dolares_envelope", 22.44, 23.87, 0.6),
    ("f5", "b6_casa_moderna", 23.87, 26.92, 0.3),
    ("f6", "b7_casal_planejando", 38.84, 42.58, 0.8),
    ("f7", "b8_goteira", 43.70, 46.76, 1.6),
]
REACT = [(7.16, 10.30), (26.92, 38.84)]  # janelas do formato react
# vídeos reais do cliente (enviados pelo usuário), já cortados/enquadrados em 960x680
CLIENTES = [("c1_ratinho", 31.14, 32.58), ("c2_cumprimento", 32.58, 33.84), ("c3_ratinho2", 33.84, 36.10),
            ("c4_dagoberto", 36.10, 37.62), ("c5_joinha", 37.62, 38.84)]
LEAKS = [1.98, 2.88, 4.87, 10.30, 12.40, 14.52, 17.46, 22.44, 23.87, 38.84, 42.58, 43.70, 46.76, 52.57]
SHAKES = [(4.35, 0.5), (15.32, 1.0), (42.62, 0.5), (46.28, 1.0)]  # (tempo, força)

# CÂMERA (#cam, origem 540px 700px: rosto sobe no quadro e o letreiro do fundo sai do topo a partir de 1.45x)
#   (tempo, de, para, duração, ease)
CAM = [
    (0.00, 1.75, 2.00, 0.60, "expo.out"), (0.60, 2.00, 2.06, 1.38, "none"),
    (2.88, 1.45, 1.55, 1.18, "none"), (4.06, 1.55, 1.75, 0.12, "power3.out"),
    (4.87, 2.00, 2.10, 2.29, "none"),
    (12.40, 1.45, 1.55, 2.12, "none"),
    (17.46, 1.85, 1.88, 0.31, "none"), (17.77, 1.45, 1.62, 3.75, "none"), (21.56, 1.62, 2.00, 0.14, "power3.out"),
    (42.58, 2.05, 2.07, 0.04, "none"), (42.62, 2.07, 2.20, 0.12, "power3.out"),
    (46.76, 1.45, 1.65, 5.81, "none"),
    (52.57, 1.90, 2.00, 2.0, "none"),
]

# LETTERING: blocos com linhas; cada peça = (classe, texto, t, animação)
#   classes: sm (sans pequena), sp (sans espaçada), sf (serifada itálica), cd (condensada)
#   cores extras: red, green, gold; animações: rise, blur, pop, stamp, spread, glitch
#   peças especiais: ("strike", t) risca a linha anterior; ("pin",t) ("clock",t) ("button",texto,t)
LT = [
    ("lt1", 0.00, 1.98, 1150, [[("sp", "Um bom investimento", 0.02, "spread")],
                               [("sf big", "imobiliário", 0.82, "blur")],
                               [("sm", "aqui nos", 1.48, "rise")]]),
    ("lt1b", 1.98, 2.88, 700, [[("cd xl", "Estados", 1.99, "spread")], [("cd xl", "Unidos", 2.30, "spread")]]),
    ("lt2", 2.88, 4.87, 1100, [[("sf big", "nunca foi", 2.88, "blur")],
                               [("sm", "o mais", 3.74, "rise")],
                               [("cd xl red", "barato", 4.06, "stamp"), ("strike", 4.35)]]),
    ("lt3", 4.87, 5.90, 1150, [[("sf big", "muito mais", 4.87, "blur")], [("cd lg", "importante", 5.30, "rise")]]),
    ("lt3b", 5.90, 7.16, 1130, [[("pin", 6.42)], [("sm", "é a", 5.90, "rise")], [("cd lg gold", "localização", 6.42, "pop")]]),
    ("lt4", 10.30, 12.40, 1040, [[("sm", "e quando você olha", 10.32, "rise")], [("sf big", "somente", 11.16, "blur")],
                                 [("cd lg", "o preço", 11.76, "rise")]]),
    ("lt5", 12.40, 14.52, 1150, [[("sm", "muitas dessas", 12.48, "rise")], [("sf mid", "oportunidades", 13.20, "blur")]]),
    ("lt6", 14.52, 17.46, 820, [[("sm", "acabam", 14.68, "rise")], [("cd xl red", "deixando", 15.32, "glitch")],
                                [("cd xl red", "de ser", 15.96, "glitch")],
                                [("sf mid", "uma oportunidade", 16.42, "blur"), ("strike", 16.95)]]),
    ("lt7", 19.56, 21.52, 1150, [[("sm", "o meu", 19.56, "rise")], [("sf big", "conselho", 19.82, "blur")],
                                 [("sm", "para os meus clientes", 20.50, "rise")]]),
    ("lt8", 21.52, 22.44, 1110, [[("clock", 21.56)], [("cd lg", "esperar", 21.56, "pop")], [("sf mid", "um pouquinho", 21.88, "blur")]]),
    ("lt9", 22.44, 23.70, 1000, [[("sm", "juntar mais", 22.44, "rise")], [("cd xl green", "dinheiro", 23.32, "pop")]]),
    ("lt10", 24.84, 26.92, 980, [[("sm", "um imóvel", 24.84, "rise")], [("cd xl gold", "melhor", 25.46, "pop")],
                                 [("sf mid", "localizado", 25.80, "blur")]]),
    ("lt11", 42.58, 43.70, 1150, [[("cd lg red", "não", 42.62, "stamp")], [("sm", "olhe só", 42.76, "rise")],
                                  [("sf big", "o preço", 43.20, "blur")]]),
    ("lt12", 45.00, 46.76, 900, [[("sf big", "o barato", 45.00, "blur")], [("sm", "pode", 45.68, "rise")],
                                 [("cd xl red", "sair caro", 45.88, "glitch")]]),
    ("lt13", 50.72, 52.46, 1130, [[("sm", "que", 50.72, "rise")], [("sf big", "realmente", 50.86, "blur")],
                                  [("cd md", "fazem sentido", 51.20, "rise")]]),
    ("lt14", 52.46, D, 1130, [[("sm", "clique no", 52.46, "rise")], [("button", "link da bio", 52.88)],
                              [("sf mid", "e vamos conversar", 53.44, "blur")]]),
]

# LEGENDAS (fora do lettering e do react): (início, fim, [(palavra, t, ênfase?)])
CAPS = [
    (17.68, 18.46, [("por", 17.68), ("esse", 17.80), ("motivo,", 18.02)]),
    (18.46, 19.56, [("na", 18.46), ("maioria", 18.58), ("das", 18.82), ("vezes,", 19.10)]),
    (23.70, 24.84, [("para", 23.70), ("que", 23.88), ("você", 24.00), ("possa", 24.16), ("comprar", 24.42)]),
    (39.06, 40.10, [("se", 39.06), ("você", 39.20), ("está", 39.34), ("pensando", 39.60)]),
    (40.10, 41.20, [("em", 40.10), ("comprar", 40.32), ("um", 40.58), ("imóvel", 40.78)]),
    (41.20, 42.56, [("aqui", 41.20), ("nos", 41.58), ("Estados", 41.90), ("Unidos,", 42.14)]),
    (43.70, 45.00, [("pois", 43.70), ("muitas", 43.90), ("das", 44.34), ("vezes", 44.60)]),
    (46.76, 48.16, [("e", 46.76), ("pra", 46.86), ("você", 46.96), ("que", 47.26), ("ficou", 47.40), ("até", 47.62), ("aqui", 47.84)]),
    (48.16, 49.22, [("e", 48.16), ("quer", 48.34), ("conversar", 48.54)]),
    (49.22, 50.72, [("sobre", 49.22), ("investimentos", 49.46), ("imobiliários", 50.14)]),
]

# PÍLULAS do react (embaixo do card): (início, fim, estilo, [(palavra, t)])
PILLS = [
    (7.40, 8.48, "dark", [("uma", 7.40), ("boa", 7.56), ("localização", 7.88)]),
    (8.48, 10.30, "green", [("gera", 8.48), ("alta", 8.86), ("demanda", 9.44)]),
    (26.92, 27.68, "dark", [("é", 26.92), ("dessa", 27.10), ("maneira", 27.28)]),
    (27.68, 29.54, "dark", [("que", 27.68), ("esse", 28.20), ("imóvel", 28.42), ("vai", 28.78), ("te", 28.98), ("gerar", 29.14)]),
    (29.54, 31.14, "green", [("renda", 29.54), ("de", 30.10), ("verdade", 30.18)]),
    (31.14, 32.58, "dark", [("relacionamentos", 31.14), ("de", 31.62), ("confiança", 31.82)]),
    (32.58, 33.72, "dark", [("foram", 32.58), ("os", 32.82), ("princípios", 33.00)]),
    (33.72, 35.00, "dark", [("que", 33.72), ("mantiveram", 33.84), ("a", 34.46), ("minha", 34.52), ("empresa", 34.66)]),
    (35.00, 36.36, "gold", [("sendo", 35.00), ("referência", 35.58)]),
    (36.36, 37.48, "dark", [("aqui", 36.36), ("nos", 36.58), ("Estados", 36.80), ("Unidos", 37.10)]),
    (37.48, 38.84, "dark", [("há", 37.48), ("mais", 37.80), ("de", 38.10), ("12", 38.30), ("anos", 38.54)]),
]

# EFEITOS SONOROS: (tempo do pico, arquivo, ganho dB)
SFX = [
    (0.02, "whoosh-short", -22), (0.82, "click-soft", -20), (1.98, "whoosh", -15), (2.88, "whoosh-short", -20),
    (4.06, "click-soft", -18), (4.35, "impact-bass-2", -15), (4.87, "whoosh-short", -20), (5.30, "click-soft", -20),
    (6.42, "pop", -16), (7.16, "whoosh", -16), (8.86, "whoosh-short", -21), (10.30, "whoosh", -18),
    (11.76, "click-soft", -20), (12.40, "whoosh-short", -20), (14.52, "whoosh", -18), (15.32, "glitch-1", -17),
    (15.32, "impact-bass-1", -11), (15.96, "glitch-1", -22), (16.95, "click", -20), (17.46, "whoosh-short", -20),
    (19.82, "click-soft", -22), (21.56, "pop", -16), (21.66, "key-press", -24), (21.86, "key-press", -24),
    (22.06, "key-press", -24), (22.44, "whoosh", -18), (23.32, "pop", -17), (23.87, "whoosh-short", -20),
    (25.46, "click-soft", -20), (26.92, "whoosh", -16), (29.54, "notification", -16), (31.14, "whoosh-short", -21),
    (32.58, "whoosh-short", -24), (33.84, "whoosh-short", -24), (36.10, "whoosh-short", -24), (37.62, "whoosh-short", -25),
    (37.70, "key-press", -26), (37.86, "key-press", -26), (38.02, "key-press", -26), (38.18, "key-press", -26),
    (38.30, "sparkle", -18), (38.84, "whoosh", -18), (42.58, "whoosh-short", -18), (42.62, "impact-bass-2", -15),
    (43.70, "whoosh", -18), (45.88, "glitch-1", -17), (46.28, "impact-bass-1", -11), (46.76, "whoosh-short", -20),
    (51.20, "click-soft", -20), (52.57, "whoosh-short", -20), (52.88, "pop", -14), (53.20, "click", -18),
]
RISER = (0.18, 1.98, -20)  # riser sobe até o flash aéreo do gancho

# ----------------------------------------------------------------------------------------------
PIN_SVG = ('<svg viewBox="0 0 64 80" aria-hidden="true"><path d="M32 2C16 2 4 14 4 30c0 21 28 46 28 46s28-25 28-46C60 14 48 2 32 2z" '
           'fill="#ff8a2a"/><circle cx="32" cy="30" r="11" fill="#fff"/></svg>')
CLOCK_SVG = ('<svg viewBox="0 0 100 100" aria-hidden="true"><circle cx="50" cy="50" r="44" fill="none" stroke="#fff" stroke-width="7"/>'
             '<line x1="50" y1="50" x2="50" y2="26" stroke="#fff" stroke-width="7" stroke-linecap="round"/>'
             '<line class="clk-hand" x1="50" y1="50" x2="70" y2="50" stroke="#ffb347" stroke-width="6" stroke-linecap="round"/></svg>')


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;")


def piece_html(p, uid):
    kind = p[0]
    if kind == "strike":
        return f'<i class="strike" data-t="{p[1]}"></i>'
    if kind == "pin":
        return f'<span class="ico pin" data-t="{p[1]}" data-anim="drop">{PIN_SVG}</span>'
    if kind == "clock":
        return f'<span class="ico clock" data-t="{p[1]}" data-anim="pop">{CLOCK_SVG}</span>'
    if kind == "button":
        return (f'<span class="btn" data-t="{p[2]}" data-anim="pop"><span class="btn-ico">↗</span>{esc(p[1]).upper()}'
                f'<i class="tap" data-t="{p[2] + 0.32}"></i></span>')
    cls, text, t, anim = p
    txt = esc(text)
    if anim == "glitch":
        return (f'<span class="{cls} gl" data-layout-allow-overlap data-t="{t}" data-anim="glitch"><span class="g1" data-layout-allow-overlap aria-hidden="true">{txt}</span>'
                f'<span class="g2" data-layout-allow-overlap aria-hidden="true">{txt}</span><span class="g0" data-layout-allow-overlap>{txt}</span></span>')
    return f'<span class="{cls}" data-t="{t}" data-anim="{anim}">{txt}</span>'


def lettering_html():
    out = []
    for lid, t0, t1, top, rows in LT:
        rows_html = []
        for row in rows:
            inner = "".join(piece_html(p, lid) for p in row)
            has_strike = any(p[0] == "strike" for p in row)
            rows_html.append(f'<div class="row{" strk" if has_strike else ""}">{inner}</div>')
        out.append(f'<div id="{lid}" class="lt clip" style="top:{top}px" data-start="{t0}" data-duration="{round(t1 - t0, 3)}" '
                   f'data-track-index="6">{"".join(rows_html)}</div>')
    return "\n      ".join(out)


def words_html(words):
    return "".join(f'<span class="w" data-t="{t}">{esc(w)}</span>' for w, t in words)


def caps_html():
    return "\n      ".join(
        f'<div id="cap-{i:02d}" class="cap clip" data-start="{a}" data-duration="{round(b - a, 3)}" data-track-index="7">{words_html(ws)}</div>'
        for i, (a, b, ws) in enumerate(CAPS, 1))


def pills_html():
    return "\n      ".join(
        f'<div id="pill-{i:02d}" class="pillwrap clip" data-start="{a}" data-duration="{round(b - a, 3)}" data-track-index="7">'
        f'<div class="pill {st}">{words_html(ws)}</div></div>'
        for i, (a, b, st, ws) in enumerate(PILLS, 1))


def full_html():
    return "\n        ".join(
        f'<video id="{fid}" class="bfull clip" src="assets/broll/{f}.mp4" muted playsinline data-start="{a}" '
        f'data-duration="{round(b - a, 3)}" data-media-start="{ms}" data-track-index="3"></video>'
        for fid, f, a, b, ms in FULL)


def clientes_html():
    return "\n            ".join(
        f'<video id="r-{c}" class="pfill clip" src="assets/clientes/{c}.mp4" muted playsinline data-start="{a}" '
        f'data-duration="{round(b - a, 3)}" data-track-index="4"></video>'
        for c, a, b in CLIENTES)


def timeline_js():
    js = []
    # câmera
    for i, (t, a, b, d, e) in enumerate(CAM):
        ir = "" if i == 0 else ", immediateRender: false"
        js.append(f'tl.fromTo("#cam", {{ scale: {a} }}, {{ scale: {b}, duration: {d}, ease: "{e}"{ir} }}, {t});')
    # react
    for k, (a, b) in enumerate(REACT):
        ir = "" if k == 0 else ", immediateRender: false"
        js.append(f'tl.fromTo("#reactbg", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.2{ir} }}, {a});')
        js.append(f'tl.fromTo("#panel", {{ opacity: 0, y: -70, scale: 0.95 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.38, ease: "power3.out"{ir} }}, {a});')
        js.append(f'tl.fromTo("#card", {{ opacity: 0, y: 90, scale: 0.92 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.38, ease: "power3.out"{ir} }}, {a + 0.05});')
        js.append(f'tl.fromTo("#cardcam", {{ scale: 1 }}, {{ scale: 1.09, duration: {round(b - a, 3)}, ease: "none"{ir} }}, {a});')
        js.append(f'tl.to("#scrim", {{ opacity: 0, duration: 0.2 }}, {a});')
        js.append(f'tl.set(["#reactbg", "#panel", "#card"], {{ opacity: 0 }}, {b});')
        js.append(f'tl.set("#scrim", {{ opacity: 1 }}, {b});')
    # luz (light leak)
    for i, t in enumerate(LEAKS):
        ir = "" if i == 0 else ", immediateRender: false"
        js.append(f'tl.fromTo("#leak", {{ opacity: 0 }}, {{ opacity: 0.95, duration: 0.14, ease: "sine.out"{ir} }}, {round(t - 0.14, 3)});')
        js.append(f'tl.to("#leak", {{ opacity: 0, duration: 0.34, ease: "sine.in" }}, {round(t + 0.02, 3)});')
        js.append(f'tl.fromTo(".lk-a", {{ xPercent: -32, rotation: -5 }}, {{ xPercent: 24, rotation: 3, duration: 0.56, ease: "none"{ir} }}, {round(t - 0.18, 3)});')
        js.append(f'tl.fromTo(".lk-b", {{ xPercent: 26, yPercent: -10 }}, {{ xPercent: -20, yPercent: 8, duration: 0.56, ease: "none"{ir} }}, {round(t - 0.18, 3)});')
        js.append(f'tl.fromTo(".lk-c", {{ xPercent: -36 }}, {{ xPercent: 30, duration: 0.56, ease: "none"{ir} }}, {round(t - 0.18, 3)});')
    # tremor de câmera
    for t, k in SHAKES:
        xs = [0, -18, 15, -11, 8, -4, 0]
        ys = [0, 10, -12, 7, -5, 2, 0]
        rs = [0, -0.8, 0.7, -0.4, 0.25, -0.1, 0]
        f = lambda arr: "[" + ", ".join(str(round(v * k, 2)) for v in arr) + "]"
        js.append(f'tl.to("#shake", {{ keyframes: {{ x: {f(xs)}, y: {f(ys)}, rotation: {f(rs)} }}, duration: 0.5, ease: "none" }}, {t});')
    return "\n      ".join(js)


def build():
    html = TEMPLATE
    html = html.replace("{{D}}", str(D))
    html = html.replace("{{FULL}}", full_html())
    html = html.replace("{{CLIENTES}}", clientes_html())
    html = html.replace("{{LT}}", lettering_html())
    html = html.replace("{{CAPS}}", caps_html())
    html = html.replace("{{PILLS}}", pills_html())
    html = html.replace("{{TIMELINE}}", timeline_js())
    (ROOT / "edicao/index.html").write_text(html, encoding="utf-8", newline="\n")
    cues = {"duration": D, "sfx": SFX, "riser": RISER}
    (ROOT / "work/sfx_cues.json").write_text(json.dumps(cues, indent=1), encoding="utf-8")
    print("index.html + sfx_cues.json ok")


TEMPLATE = r"""<!doctype html>
<html lang="pt-BR">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <title>Edicao Dinamica</title>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      @font-face {
        font-family: "Playfair Display Italic";
        font-style: italic;
        font-weight: 400 900;
        src: url("assets/fonts/PlayfairDisplay-Italic.ttf") format("truetype");
      }
      * { margin: 0; padding: 0; box-sizing: border-box; }
      html, body { width: 1080px; height: 1920px; overflow: hidden; background: #000; }
      #root { position: relative; width: 100%; height: 100%; overflow: hidden; font-family: Montserrat, sans-serif; color: #fff; }

      /* ---------- imagem ---------- */
      #shake { position: absolute; inset: 0; }
      #stage, #cam { position: absolute; inset: 0; }
      #cam { transform-origin: 540px 700px; }
      .fill, .bfull { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
      #reactbg { position: absolute; inset: 0; opacity: 0;
        background: radial-gradient(70% 40% at 50% 28%, rgba(255, 122, 40, 0.22), transparent 70%),
                    radial-gradient(60% 30% at 50% 78%, rgba(255, 90, 30, 0.14), transparent 70%), #060608; }
      #panel { position: absolute; left: 60px; top: 140px; width: 960px; height: 680px; border-radius: 40px; overflow: hidden; opacity: 0; background: #0d0d10;
        box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.16), 0 0 70px rgba(255, 140, 60, 0.30), 0 30px 80px rgba(0, 0, 0, 0.65); }
      .pfill { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
      #kb { position: absolute; inset: 0; transform-origin: 50% 60%; }
      #card { position: absolute; left: 190px; top: 860px; width: 700px; height: 600px; border-radius: 40px; overflow: hidden; opacity: 0; background: #000;
        box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.18), 0 0 60px rgba(255, 140, 60, 0.32), 0 30px 80px rgba(0, 0, 0, 0.7); }
      #cardcam { position: absolute; inset: 0; transform-origin: 350px 270px; }
      .vcard { position: absolute; left: -105px; top: -420px; width: 994px; height: 1766px; object-fit: cover; }
      #scrim { position: absolute; inset: 0; pointer-events: none; opacity: 0;
        background: linear-gradient(to bottom, rgba(0, 0, 0, 0) 48%, rgba(0, 0, 0, 0.32) 62%, rgba(0, 0, 0, 0.55) 80%, rgba(0, 0, 0, 0.62) 100%); }

      /* ---------- react: mapa, gráfico, notificação, contador ---------- */
      #mpin { position: absolute; left: 448px; top: 230px; width: 64px; height: 80px; opacity: 0; }
      #mpin svg { width: 64px; height: 80px; display: block; }
      #mring { position: absolute; left: 430px; top: 286px; width: 100px; height: 36px; border-radius: 50%; border: 4px solid #ffb347; opacity: 0; }
      #chart { position: absolute; left: 40px; bottom: 40px; width: 440px; height: 300px; border-radius: 28px; opacity: 0;
        background: rgba(10, 10, 14, 0.78); box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.14); }
      #chart .lbl { position: absolute; left: 30px; top: 22px; font-weight: 800; font-size: 34px; letter-spacing: 0.08em; }
      #chart .lbl b { color: #3ee07a; }
      #chart .bars { position: absolute; left: 30px; right: 30px; bottom: 26px; height: 180px; display: flex; align-items: flex-end; gap: 18px; }
      #chart .bar { flex: 1; border-radius: 10px 10px 4px 4px; background: linear-gradient(#5ff29a, #1fa85a); transform-origin: 50% 100%; }
      #notif { position: absolute; left: 60px; right: 60px; top: 40px; height: 150px; border-radius: 34px; opacity: 0; display: flex; align-items: center; gap: 26px; padding: 0 30px;
        background: rgba(250, 250, 252, 0.96); color: #0d0d10; box-shadow: 0 20px 50px rgba(0, 0, 0, 0.45); }
      #notif .ni { width: 90px; height: 90px; border-radius: 26px; background: #1fbf6a; display: flex; align-items: center; justify-content: center; flex: none;
        font-weight: 900; font-size: 52px; color: #fff; }
      #notif .nt { font-weight: 800; font-size: 40px; line-height: 1.1; }
      #notif .ns { font-weight: 600; font-size: 30px; opacity: 0.6; }
      #notif .nck { margin-left: auto; width: 64px; height: 64px; border-radius: 50%; background: #1fbf6a; display: flex; align-items: center; justify-content: center; flex: none; }
      #notif .nck svg { width: 36px; height: 36px; display: block; }
      #counter { position: absolute; left: 0; right: 0; bottom: 0; height: 320px; display: flex; align-items: flex-end; justify-content: center; gap: 20px; padding-bottom: 34px; opacity: 0;
        background: linear-gradient(to bottom, rgba(0, 0, 0, 0), rgba(0, 0, 0, 0.82)); }
      #cnum { font-family: Oswald, sans-serif; font-weight: 700; font-size: 230px; line-height: 0.85;
        background: linear-gradient(180deg, #fff1c1 0%, #ffc35a 45%, #ff8a2a 100%); -webkit-background-clip: text; background-clip: text; color: transparent;
        filter: drop-shadow(0 8px 26px rgba(0, 0, 0, 0.7)); }
      #counter .anos { font-family: Oswald, sans-serif; font-weight: 700; font-size: 96px; line-height: 1; text-transform: uppercase; padding-bottom: 18px;
        text-shadow: 0 6px 24px rgba(0, 0, 0, 0.7); }

      /* ---------- tipografia ---------- */
      .lt { position: absolute; left: 40px; right: 40px; height: 600px; display: flex; flex-direction: column; align-items: center; justify-content: flex-start; text-align: center; gap: 4px; }
      .row { position: relative; display: flex; align-items: baseline; justify-content: center; gap: 18px; }
      .sm, .sp, .sf, .cd, .ico, .btn { display: inline-block; }
      .sm { font-weight: 700; font-size: 50px; letter-spacing: 0.005em; text-shadow: 0 3px 6px rgba(0, 0, 0, 0.6), 0 8px 30px rgba(0, 0, 0, 0.6); }
      .sp { font-weight: 700; font-size: 40px; letter-spacing: 0.22em; text-transform: uppercase; text-shadow: 0 3px 6px rgba(0, 0, 0, 0.6), 0 8px 30px rgba(0, 0, 0, 0.6); }
      .sf { font-family: "Playfair Display Italic", serif; font-style: italic; font-weight: 800; line-height: 1.02; letter-spacing: -0.01em;
        text-shadow: 0 0 26px rgba(255, 255, 255, 0.28), 0 6px 30px rgba(0, 0, 0, 0.7); }
      .sf.big { font-size: 150px; } .sf.mid { font-size: 112px; }
      .cd { font-family: Oswald, sans-serif; font-weight: 700; text-transform: uppercase; line-height: 0.95; letter-spacing: 0.01em;
        text-shadow: 0 0 26px rgba(255, 255, 255, 0.25), 0 8px 32px rgba(0, 0, 0, 0.7); }
      .cd.xl { font-size: 210px; } .cd.lg { font-size: 160px; } .cd.md { font-size: 128px; white-space: nowrap; }
      .red { color: #ff3b3b; text-shadow: 0 0 30px rgba(255, 40, 40, 0.5), 0 8px 32px rgba(0, 0, 0, 0.7); }
      .green { color: #3ee07a; text-shadow: 0 0 30px rgba(62, 224, 122, 0.45), 0 8px 32px rgba(0, 0, 0, 0.7); }
      .gold { background: linear-gradient(180deg, #fff1c1 0%, #ffc35a 45%, #ff8a2a 100%); -webkit-background-clip: text; background-clip: text; color: transparent;
        text-shadow: none; filter: drop-shadow(0 8px 26px rgba(0, 0, 0, 0.7));
        padding: 0.22em 0.04em 0.16em; margin: -0.22em -0.04em -0.16em; } /* espaço para til e cedilha não serem cortados */
      .gl { position: relative; }
      .gl .g1, .gl .g2 { position: absolute; left: 0; top: 0; mix-blend-mode: screen; text-shadow: none; }
      .gl .g1 { color: #00e5ff; opacity: 0.85; }
      .gl .g2 { color: #ffffff; opacity: 0.55; }
      .gl .g0 { position: relative; }
      .strike { position: absolute; left: -2%; width: 104%; top: 54%; height: 12px; border-radius: 6px; background: #ff3b3b; box-shadow: 0 0 18px rgba(255, 40, 40, 0.7);
        transform-origin: 0 50%; }
      .ico.pin svg { width: 96px; height: 120px; display: block; filter: drop-shadow(0 10px 24px rgba(0, 0, 0, 0.6)); }
      .ico.clock svg { width: 120px; height: 120px; display: block; filter: drop-shadow(0 8px 20px rgba(0, 0, 0, 0.6)); }
      .btn { position: relative; margin: 18px 0 10px; padding: 26px 56px 26px 44px; border-radius: 999px; background: #fff; color: #0d0d10;
        font-family: Oswald, sans-serif; font-weight: 700; font-size: 92px; line-height: 1; letter-spacing: 0.02em;
        box-shadow: 0 0 0 6px rgba(255, 179, 71, 0.9), 0 0 60px rgba(255, 140, 60, 0.6), 0 20px 50px rgba(0, 0, 0, 0.6); }
      .btn-ico { display: inline-block; margin-right: 18px; color: #ff8a2a; }
      .tap { position: absolute; right: 70px; top: 50%; width: 90px; height: 90px; margin-top: -45px; border-radius: 50%; border: 6px solid #ff8a2a; opacity: 0; }

      /* legendas e pílulas */
      .cap { position: absolute; left: 60px; right: 60px; top: 1420px; height: 110px; display: flex; align-items: center; justify-content: center; gap: 14px; }
      .cap .w { display: inline-block; font-weight: 700; font-size: 50px; text-shadow: 0 3px 6px rgba(0, 0, 0, 0.7), 0 8px 26px rgba(0, 0, 0, 0.7); }
      .pillwrap { position: absolute; left: 40px; right: 40px; top: 1488px; height: 100px; display: flex; align-items: center; justify-content: center; }
      .pill { display: flex; gap: 12px; align-items: center; padding: 16px 34px; border-radius: 999px; font-weight: 800; font-size: 44px;
        box-shadow: 0 12px 34px rgba(0, 0, 0, 0.55); }
      .pill .w { display: inline-block; }
      .pill.dark { background: rgba(16, 16, 20, 0.92); box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.16), 0 12px 34px rgba(0, 0, 0, 0.55); }
      .pill.green { background: #1fbf6a; } .pill.gold { background: linear-gradient(90deg, #ffb347, #ff8a2a); color: #160b02; }

      /* light leak (registry: organic-light-leak-overlay, embutido) */
      #leak { position: absolute; inset: -16%; opacity: 0; overflow: hidden; pointer-events: none; mix-blend-mode: screen; }
      #leak .lk { position: absolute; inset: -20%; }
      #leak .lk-a { background: radial-gradient(ellipse 52% 110% at 10% 58%, rgb(255 241 197 / 92%), transparent 45%),
                                radial-gradient(ellipse 72% 120% at 24% 54%, rgb(255 126 57 / 78%), transparent 66%); filter: blur(28px); }
      #leak .lk-b { background: radial-gradient(ellipse 58% 105% at 78% 34%, rgb(255 79 61 / 72%), rgb(255 44 92 / 28%) 48%, transparent 76%); filter: blur(40px); }
      #leak .lk-c { background: linear-gradient(104deg, transparent 24%, rgb(255 144 62 / 30%) 40%, rgb(255 247 205 / 72%) 51%, rgb(255 124 48 / 22%) 62%, transparent 78%); filter: blur(20px); }
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{{D}}" data-width="1080" data-height="1920">
      <div id="shake" data-layout-allow-overflow>
        <div id="stage">
          <div id="cam" data-layout-allow-overflow>
            <video id="v-main" class="fill clip" src="assets/base.mp4" muted playsinline data-start="0" data-duration="{{D}}" data-track-index="0"></video>
          </div>
        </div>
        <div id="reactbg"></div>
        <div id="panel">
          <video id="r-b2" class="pfill clip" src="assets/broll/b2_bairro_lago.mp4" muted playsinline data-start="7.16" data-duration="3.14" data-media-start="0.3" data-track-index="4"></video>
          <div id="kb"><img id="r-b6" class="pfill clip" src="assets/broll/b6_still.jpg" alt="" data-start="26.92" data-duration="4.22" data-track-index="4" /></div>
          {{CLIENTES}}
          <div id="mring"></div>
          <div id="mpin"><svg viewBox="0 0 64 80" aria-hidden="true"><path d="M32 2C16 2 4 14 4 30c0 21 28 46 28 46s28-25 28-46C60 14 48 2 32 2z" fill="#ff8a2a"/><circle cx="32" cy="30" r="11" fill="#fff"/></svg></div>
          <div id="chart"><div class="lbl">DEMANDA <b>↑</b></div><div class="bars"><i class="bar" style="height:30%"></i><i class="bar" style="height:46%"></i><i class="bar" style="height:58%"></i><i class="bar" style="height:76%"></i><i class="bar" style="height:100%"></i></div></div>
          <div id="notif"><div class="ni">$</div><div><div class="nt">Aluguel recebido</div><div class="ns">todo mês, sem dor de cabeça</div></div>
            <div class="nck"><svg viewBox="0 0 36 36" aria-hidden="true"><path d="M8 19l7 7 13-15" fill="none" stroke="#fff" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/></svg></div></div>
          <div id="counter"><span id="cnum">+0</span><span class="anos">anos</span></div>
        </div>
        <div id="card"><div id="cardcam"><video id="v-card1" class="vcard clip" src="assets/base.mp4" muted playsinline data-start="7.0" data-duration="3.4" data-media-start="7.0" data-track-index="5"></video><video id="v-card2" class="vcard clip" src="assets/base.mp4" muted playsinline data-start="26.8" data-duration="12.15" data-media-start="26.8" data-track-index="5"></video></div></div>
        {{FULL}}
      </div>
      <div id="scrim"></div>

      {{LT}}

      {{CAPS}}

      {{PILLS}}

      <div id="leak" aria-hidden="true" data-layout-allow-overflow data-layout-allow-occlusion><div class="lk lk-a" data-layout-allow-overflow></div><div class="lk lk-b" data-layout-allow-overflow></div><div class="lk lk-c" data-layout-allow-overflow></div></div>

      <audio id="mix" src="assets/mix.wav" data-start="0" data-duration="{{D}}" data-track-index="9" data-volume="1"></audio>
    </div>

    <script>
      const tl = gsap.timeline({ paused: true });
      const T = (el) => parseFloat(el.dataset.t);
      tl.set("#shake", { scale: 1.03 }, 0);
      tl.fromTo("#scrim", { opacity: 0 }, { opacity: 1, duration: 0.01 }, 0);

      // ---------- entradas de texto ----------
      document.querySelectorAll(".cap .w, .pill .w").forEach((el) => {
        tl.fromTo(el, { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: 0.14, ease: "power2.out" }, T(el));
      });
      document.querySelectorAll(".pillwrap").forEach((w) => {
        tl.fromTo(w.querySelector(".pill"), { opacity: 0, scale: 0.86 }, { opacity: 1, scale: 1, duration: 0.16, ease: "back.out(2)" }, parseFloat(w.dataset.start));
      });
      document.querySelectorAll('[data-anim="rise"]').forEach((el) => {
        tl.fromTo(el, { opacity: 0, yPercent: 60 }, { opacity: 1, yPercent: 0, duration: 0.26, ease: "power3.out" }, T(el));
      });
      document.querySelectorAll('[data-anim="blur"]').forEach((el) => {
        tl.fromTo(el, { opacity: 0, scale: 1.1, filter: "blur(16px)" }, { opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.34, ease: "power3.out" }, T(el));
      });
      document.querySelectorAll('[data-anim="pop"]').forEach((el) => {
        tl.fromTo(el, { opacity: 0, scale: 0.45 }, { opacity: 1, scale: 1, duration: 0.3, ease: "back.out(2.2)" }, T(el));
      });
      document.querySelectorAll('[data-anim="stamp"]').forEach((el) => {
        tl.fromTo(el, { opacity: 0, scale: 1.8 }, { opacity: 1, scale: 1, duration: 0.15, ease: "power4.in" }, T(el));
      });
      document.querySelectorAll('[data-anim="spread"]').forEach((el) => {
        tl.fromTo(el, { opacity: 0, scaleX: 1.4, filter: "blur(10px)" }, { opacity: 1, scaleX: 1, filter: "blur(0px)", duration: 0.45, ease: "power3.out" }, T(el));
      });
      document.querySelectorAll('[data-anim="drop"]').forEach((el) => {
        tl.fromTo(el, { opacity: 0, y: -90 }, { opacity: 1, y: 0, duration: 0.42, ease: "bounce.out" }, T(el));
      });
      document.querySelectorAll('[data-anim="glitch"]').forEach((el) => {
        const t = T(el);
        tl.fromTo(el, { opacity: 0, scale: 1.25 }, { opacity: 1, scale: 1, duration: 0.12, ease: "power4.in" }, t);
        [t + 0.08, t + 0.9].forEach((g, i) => {
          const im = i === 0 ? {} : { immediateRender: false };
          tl.fromTo(el.querySelector(".g1"), { x: 0 }, { keyframes: { x: [0, -16, 12, -8, 14, -5, 0], easeEach: "steps(1)" }, duration: 0.36, ease: "none", ...im }, g);
          tl.fromTo(el.querySelector(".g2"), { x: 0 }, { keyframes: { x: [0, 12, -10, 9, -12, 4, 0], easeEach: "steps(1)" }, duration: 0.36, ease: "none", ...im }, g);
        });
      });
      document.querySelectorAll(".strike").forEach((el) => {
        tl.fromTo(el, { scaleX: 0 }, { scaleX: 1, duration: 0.22, ease: "power2.out" }, T(el));
      });
      document.querySelectorAll(".clk-hand").forEach((el) => {
        tl.fromTo(el, { rotation: 0 }, { rotation: 360, duration: 0.85, ease: "power1.inOut", svgOrigin: "50 50" }, 21.6);
      });
      document.querySelectorAll(".tap").forEach((el) => {
        tl.fromTo(el, { opacity: 0.9, scale: 0.4 }, { opacity: 0, scale: 1.8, duration: 0.5, ease: "power2.out" }, T(el));
      });
      tl.fromTo(".btn", { scale: 1 }, { keyframes: { scale: [1, 0.94, 1.04, 1] }, duration: 0.4, ease: "none", immediateRender: false }, 53.2);

      // ---------- react: mapa, gráfico, notificação, contador ----------
      tl.fromTo("#mpin", { opacity: 0, y: -80 }, { opacity: 1, y: 0, duration: 0.45, ease: "bounce.out" }, 7.56);
      tl.fromTo("#mring", { opacity: 0.9, scale: 0.3 }, { opacity: 0, scale: 2.2, duration: 0.8, ease: "power2.out", repeat: 2 }, 7.9);
      tl.fromTo("#chart", { opacity: 0, y: 60 }, { opacity: 1, y: 0, duration: 0.32, ease: "power3.out" }, 8.86);
      tl.fromTo("#chart .bar", { scaleY: 0 }, { scaleY: 1, duration: 0.45, ease: "back.out(1.6)", stagger: 0.08 }, 9.0);
      tl.set(["#chart", "#mpin", "#mring"], { opacity: 0 }, 10.30);
      tl.fromTo("#kb", { scale: 1 }, { scale: 1.12, duration: 4.22, ease: "none" }, 26.92);
      tl.fromTo("#notif", { opacity: 0, y: -70 }, { opacity: 1, y: 0, duration: 0.4, ease: "back.out(1.6)" }, 29.54);
      tl.fromTo("#notif .nck", { scale: 0 }, { scale: 1, duration: 0.3, ease: "back.out(2.5)" }, 29.8);
      tl.set("#notif", { opacity: 0 }, 31.14);
      tl.fromTo("#counter", { opacity: 0 }, { opacity: 1, duration: 0.25 }, 37.55);
      tl.set("#counter", { opacity: 0 }, 38.84);
      const cnum = document.getElementById("cnum");
      const ctr = {}; let cv = 0;
      Object.defineProperty(ctr, "v", { get() { return cv; }, set(n) { cv = n; cnum.textContent = "+" + Math.round(n); } });
      tl.fromTo(ctr, { v: 0 }, { v: 12, duration: 0.72, ease: "power2.out" }, 37.6);
      tl.fromTo("#cnum", { scale: 1 }, { keyframes: { scale: [1, 1.18, 1] }, duration: 0.3, ease: "none", immediateRender: false }, 38.3);

      // ---------- câmera, react, luz, tremor ----------
      {{TIMELINE}}

      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""

if __name__ == "__main__":
    build()
