#!/bin/bash
# Monta a parte de imagem do anúncio (15 s, 1080x1920, 30 fps) a partir dos 4 keyframes,
# com movimento de câmera feito no FFmpeg (o plano gratuito da Higgsfield não gera vídeo).
# Uso: bash montar_imagem.sh   (rodar dentro da pasta do projeto)
set -euo pipefail
cd "$(dirname "$0")"
K=keyframes; W=work; mkdir -p $W
FPS=30

# cena <entrada> <saida> <frames> <expr_zoom> <expr_x> <expr_y>
# A imagem é ampliada para 2160x3840 antes do zoompan para o movimento não "tremer" em pixels inteiros.
cena() {
  ffmpeg -hide_banner -loglevel error -y -loop 1 -i "$1" -vf \
    "scale=2160:3840:flags=lanczos,zoompan=z='$4':x='$5':y='$6':d=$3:s=1080x1920:fps=$FPS,format=yuv420p" \
    -frames:v "$3" -c:v libx264 -preset medium -crf 16 "$2"
}

# 1) Gancho 0–2 s: zoom rápido + tremor + leve deriva para baixo-esquerda (acompanha o deslize)
cena $K/01_gancho-iceberg.png $W/c1.mp4 60 \
  "1.18+0.004*on" \
  "iw/2-(iw/zoom/2)-on*4+sin(on*1.9)*16" \
  "ih/2-(ih/zoom/2)+on*5+cos(on*2.3)*12"

# 2) Resgate 2–9 s: aproximação lenta na lata e na pessoa; "soco" de zoom aos 4,9 s da cena
#    (fim de "chegou reforço gelado!")
cena $K/02_resgate-escritorio.png $W/c2.mp4 210 \
  "1.0+0.0007*on+if(gte(on,147),0.10,0)" \
  "iw*0.42-(iw/zoom/2)" \
  "ih*0.55-(ih/zoom/2)"

# 3) Close 9–13 s: sobe devagar até o topo da lata, onde estão as gotas
cena $K/03_close-gotas.png $W/c3.mp4 120 \
  "1.0+0.0035*on" \
  "iw/2-(iw/zoom/2)" \
  "ih*(0.5-0.0012*on)-(ih/zoom/2)"

# 4) Final 13–15 s: afastamento que revela a lata (espaço livre em cima para marca e CTA)
cena $K/04_final-joinha.png $W/c4.mp4 60 \
  "1.15-0.0025*on" \
  "iw/2-(iw/zoom/2)" \
  "ih/2-(ih/zoom/2)"

# Cortes secos (ritmo de anúncio) — junta as 4 cenas
printf "file 'c%d.mp4'\n" 1 2 3 4 > $W/lista.txt
ffmpeg -hide_banner -loglevel error -y -f concat -safe 0 -i $W/lista.txt -c copy $W/imagem.mp4
ffprobe -v error -show_entries format=duration:stream=width,height,r_frame_rate -of csv=p=0 $W/imagem.mp4
