#!/usr/bin/env bash
# Gera o depoimento sintético (não há gravação real no repositório: vídeos não vão para o Git).
# Imagem: fundo com o texto "cliente falando"; áudio: tons nos trechos de fala, silêncio nas pausas.
set -eu
out=Documentos/Estudio-Ads-IA/brutos/depoimento-lumi.mp4
mkdir -p "$(dirname "$out")"
[ -f "$out" ] && exit 0
speech="between(t,1.8,3)+between(t,3.5,7)+between(t,9,13)+between(t,13.5,17)+between(t,20,24)+between(t,24.5,27)"
ffmpeg -hide_banner -loglevel error -y \
  -f lavfi -i "color=c=0x8a6f5c:s=1920x1080:r=30:d=30" \
  -f lavfi -i "aevalsrc='0.25*sin(2*PI*(180+40*sin(2*PI*3*t))*t)*gt(${speech},0)':s=48000:d=30" \
  -vf "drawbox=x=760:y=180:w=400:h=720:color=0xe8c4a8:t=fill,drawtext=text='cliente falando (bruto sintetico)':fontcolor=white:fontsize=48:x=(w-tw)/2:y=960" \
  -c:v libx264 -pix_fmt yuv420p -c:a aac -ac 2 -shortest "$out"
