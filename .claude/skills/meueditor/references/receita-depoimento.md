# Receita: depoimento ou UGC gravado → anúncio 9:16

Testada em 2026-11-06 (bruto horizontal de 30 s → anúncio de 18,6 s que passou em
`check.py --platform reels` e `tiktok`, -13,9 LUFS, texto dentro da área segura de anúncio).
`S=.claude/skills/ffmpeg-skill/scripts`. Trabalhe numa pasta temporária e copie só o final
para `geracoes/<projeto>/`.

## 1. Medir e decidir a ordem
```bash
python3 $S/probe.py brutos/<bruto>.mp4
python3 $S/silence.py brutos/<bruto>.mp4 --dry-run --json   # onde há pausas
```
Com a transcrição (do usuário ou `caption.py --transcribe`), escolha os trechos e **a ordem
do anúncio**, que raramente é a ordem gravada: abra com o resultado ou a frase mais forte
(gancho), depois problema → solução → prova/benefício → CTA. Corte "oi gente" e
apresentações. Deixe ~0,1 s de folga antes e depois de cada fala.

## 2. Cortar na ordem do anúncio
```bash
python3 $S/cut.py brutos/<bruto>.mp4 --segments "13.4-17.1,3.4-7.1,8.9-13.1" --accurate -o 01_corte.mp4
```
`--segments` respeita a ordem dada (confira em `--dry-run --json` → `requested_segments`).

## 3. Vertical + loudness num passo
```bash
python3 $S/render.py --template reels 01_corte.mp4 -o 02_base.mp4
```
Sai 1080×1920, 30 fps, -14 LUFS. Não passe `--cues` aqui: o template põe a legenda na
zona de post orgânico (rodapé de 20%), que fica embaixo do botão de CTA do anúncio.
(`fit.py --aspect 9:16 --fit crop` sozinho entrega 608×1080, e `--height 1920` arredonda
para 1082 de largura — por isso o template.)

## 4. Legendas (tempos da NOVA linha do tempo)
Escreva o SRT você mesmo, em blocos de até ~4 palavras, recalculando os tempos para a
montagem (trecho 1 começa em 0). Depois:
```bash
python3 $S/caption.py 02_base.mp4 --srt legendas.srt --platform tiktok --margin 104 \
  --bold --size 13 --outline 3 --animate pop -o 03_legendado.mp4
```
- `--margin` é em unidades da grade de 288 linhas: 104 ≈ 35% → base da legenda em y≈1250.
- `--platform tiktok` dá as margens laterais (5% / 14%), longe da coluna de botões.
- `--size 13` deu uma linha de ~95 px de altura em 1920 (medido no quadro); com `--bold` e contorno 3 fica legível
  sem som. Revise o texto: nome do produto errado na legenda passa amadorismo.

## 5. Gancho (0–2,6 s) e CTA (últimos ~3 s), no alto
```bash
python3 $S/overlay.py 03_legendado.mp4 --text $'3 SEMANAS\nMANCHAS CLAREANDO' \
  --position top --margin 330 --font-size 64 --box --start 0 --end 2.6 -o 04_gancho.mp4
python3 $S/overlay.py 04_gancho.mp4 --text $'COMPRE NO\nLINK ABAIXO' \
  --position top --margin 330 --font-size 64 --box --start <duração-3> -o 05_final.mp4
```
Máx. ~16 caracteres por linha a 64 px. Uma linha de 29 caracteres a 72 px saiu cortada dos
dois lados no teste. `--position` aceita nomes (`top`, `center`…), não `center,330`.

## 6. Conferir
```bash
python3 $S/check.py 05_final.mp4 --platform reels      # e --platform tiktok
python3 $S/look.py 05_final.mp4 --safe tiktok --at 1  -o look_gancho.png
python3 $S/look.py 05_final.mp4 --safe tiktok --at 9  -o look_meio.png
python3 $S/look.py 05_final.mp4 --safe tiktok --at <fim-1> -o look_cta.png
```
Abra os PNGs. O aviso `subtitles none` do `check.py` é esperado com legenda queimada.
Confirme também: primeiro som antes de 0,5 s
(`ffmpeg -i final -af silencedetect=n=-40dB:d=0.05 -f null -`) e nenhuma pausa ≥0,5 s.
