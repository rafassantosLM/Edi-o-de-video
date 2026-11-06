---
name: edicaodinamica
description: Edição dinâmica de Reels/TikTok no estilo do Matheus Novais — talking head com cortes de erros e respiros, J-cut, jogo de câmera (punch-in), lettering misto (condensada + serifada itálica), legendas palavra a palavra, formato react (pessoa num card + conteúdo em cima), ênfase no negativo (P&B + vermelho + glitch + tremor), light leak, b-roll realista com IA (Higgsfield), SFX leves e trilha opcional com riser→drop. Use quando o usuário pedir "edição dinâmica", "/edicaodinamica", "edita igual a referência", ou mandar material + referência para editar.
---

# Edição Dinâmica (estilo Matheus Novais)

Responda **sempre em português do Brasil**, inclusive nos avisos curtos de progresso entre ferramentas. O usuário pode não ser técnico: explique simples, sem jargão.

Esta skill é o pacote de edição que já foi aprovado em dois projetos ("ficou ótimo"):
- Reels de criador (talking head, gancho + conteúdo, trilha gerada, riser→drop).
- Vídeo de corretor de imóveis (cliente; referência horizontal, material vertical, react, b-roll IA, vídeos reais de clientes, sem trilha).

Scripts prontos (copiar para `<projeto>/scripts/` e adaptar): pasta `scripts/` desta skill.

---

## 0. Antes de começar

> **Adaptado para o Estúdio Ads IA (nuvem Linux):** esta skill é chamada pela `meueditor`
> para edição dinâmica. As regras de custo, área segura e entrega da `meueditor` valem aqui.
> Comandos marcados "(Windows)" só se aplicam rodando no PC do usuário com PowerShell.

1. (Windows) Recarregar o PATH no PowerShell: `$env:Path = [Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [Environment]::GetEnvironmentVariable('Path','User')`. Na nuvem Linux não precisa.
2. Criar o projeto em `Documentos/Estudio-Ads-IA/geracoes/<nome>-<data>/` (na raiz do repositório; no Windows, `~/Documents/Estudio-Ads-IA/...`) com `src/ work/ scripts/ broll/ edicao/`. Copiar os arquivos do usuário de `brutos/` para `src/` (nunca editar os originais).
3. Perguntar só o que faltar, numa mensagem: referência (link/arquivo), formato (padrão vertical 9:16), **com ou sem trilha** (às vezes ele coloca a música), se tem vídeos reais de clientes/prova social, e **teto de créditos** para o projeto. Siga a regra de custo da `meueditor`: estimar antes de cada lote (`python3 scripts/gen_broll.py cost ...`), mostrar total e saldo, e gerar sem perguntar de novo só dentro do teto combinado. Informe no fim os créditos gastos.
4. Ler as skills que a etapa pedir (`hyperframes` — contrato da composição e guias em `hyperframes/references/`: `captions.md`, `motion.md`, `sound.md`, `types/vertical.md`; `hyperframes-cli`; `media-use`; `higgsfield`; `higgsfield-generate`; `cinematic-video-prompt`) — esta skill não substitui as regras delas. Versões antigas desta skill citavam `hyperframes-core`, `general-video` e `hyperframes-audio`: hoje esse conteúdo está dentro de `hyperframes`.

## 1. Estudar a referência

- Instagram: abrir no navegador do app, fechar o pop-up de cadastro (X), e montar uma folha de quadros com JS: buscar `document.querySelector('video')`, dar `currentTime` em vários tempos, desenhar num `<canvas>` fixo no topo e tirar `zoom` da região. Telas maiores que a viewport cortam — usar no máximo ~1000x700.
- Arquivo local: `ffmpeg ... fps=1/2,scale=320:-1,drawtext(tempo),tile=5x6`; detectar cortes com `select='gt(scene,0.28)',showinfo`. Aglomerados de 4–6 quadros seguidos = transição (ex.: light leak), não corte seco.
- Anotar: tipografia (pesos, itálico, caixa alta), cores por significado, posição do texto, tamanho/estilo da legenda, tipo de transição, quando entra b-roll e se fica P&B, ritmo dos cortes, formato react.
- Se a referência for um vídeo antigo do mesmo cliente com o mesmo texto, reaproveitar as escolhas de b-roll/lettering dela para as mesmas frases.

## 2. Fala: transcrição, erros, respiros, J-cut

- Transcrever com faster-whisper (o `hyperframes transcribe` pode falhar sem whisper-cpp): `uv run --no-project --with faster-whisper python -I scripts/transcribe.py large-v3 work/x.wav` (WAV 16 kHz mono). O script carrega o WAV com numpy porque o `av` pode quebrar.
- Whisper **funde retakes**: palavra com duração > 1 s é suspeita → re-transcrever o trecho isolado. Ele escreve "Claude" como "Cláudio" — corrigir nas legendas.
- Medir pausas com `scripts/envelope.py` (RMS em dB); `silencedetect` falha quando há ruído de fundo.
- Cortar erros/retakes (fica a última tentativa boa) e respiros; mostrar a lista de cortes ao usuário (tempo original + motivo).
- J-cut: o áudio do próximo trecho entra antes da imagem (0,25 s na virada gancho→conteúdo, ~0,12 s nos demais). `scripts/build_base.py` monta isso a partir de segmentos definidos pelo áudio. Se o material já veio **decupado** (cortes prontos, sem sobras), não dá J-cut verdadeiro: esconda os cortes com troca de enquadramento e use o b-roll para defasar imagem e som.
- Achar os cortes que o usuário já fez: `select='gt(scene,0.08)'` — ali entram as trocas de câmera.

## 3. Imagem base

- Câmera frontal grava espelhado: desespelhar (`hflip`) quando houver texto na roupa — avisar o usuário.
- Correção de cor no estilo "manifesto/cinema": `curves=master='0/0 0.12/0.06 0.5/0.47 0.85/0.88 1/1',eq=contrast=1.06:saturation=1.06,colorbalance=rs=-0.02:bs=0.04:rm=0.015:bm=-0.03:rh=0.04:bh=-0.04,vignette=angle=0.55`. Para vídeo escuro de celular: clarear (`eq=brightness=0.04:gamma=1.12`) e esquentar.
- Exportar a base com `-g 30 -keyint_min 30` (keyframes densos; o HyperFrames reclama de keyframes esparsos).

## 4. Áudio da voz

- Cadeia leve: `highpass=f=70,afftdn=nr=10:nf=-45:tn=1,equalizer 220Hz -1.5,equalizer 3.2kHz +1.5,highshelf 10k +1,acompressor` + `loudnorm` 2 passadas a −16 LUFS (`scripts/voz.py` / `process_audio.py`).
- **Os filtros atrasam o áudio** (25 ms só com afftdn; 33 ms com afftdn+anlmdn) e às vezes encurtam o arquivo: medir com `scripts/lagcheck.py`, compensar com `atrim=start_sample=N` e fixar o tamanho com `apad,atrim=end_sample=N`. Sempre conferir lag 0 ms no final.

## 5. Design (o que já foi aprovado)

**Lettering** (blocos de 2–4 linhas, palavra a palavra, no tempo da fala):
- Sans pequena (Montserrat 700, ~50px) para palavras de ligação; versão espaçada em caixa alta (letter-spacing 0.22em, ~40px) para abrir o gancho.
- Serifada itálica pesada (Playfair Display Italic 800, ~110–150px, baixada do Google Fonts como `@font-face` local) para a palavra de emoção: "imobiliário", "nunca foi", "conselho", "realmente".
- Condensada caixa alta (Oswald 700, 128–210px) para a palavra-chave: "BARATO", "IMPORTANTE", "ESPERAR", "FAZEM SENTIDO" (usar 128px e `nowrap` se for longa).
- Cores por significado: **vermelho #ff3b3b = negativo/alerta**, **verde #3ee07a = dinheiro/renda**, **dourado (gradiente #fff1c1→#ffc35a→#ff8a2a) = localização/positivo/prova**, branco com brilho suave no resto. No estilo Reels de criador: amarelo #ffd54a como destaque, serifada Instrument Serif Italic.
- Animações: rise (sobe com fade), blur (desfoca→foca), pop (escala com back.out), stamp (cai grande e trava), spread (scaleX + blur — **nunca animar letterSpacing**), glitch (cópias ciano/branca deslocando em steps), strike (risco vermelho desenhando por cima: "BARATO", "uma oportunidade").
- Ícones de apoio em SVG: pino de mapa caindo ("localização"), relógio girando ("esperar"), botão "LINK DA BIO" com toque/onda no CTA, barra de comentário digitando "EU QUERO" + notificação de DM (CTA de comentário), chip de marca ("✳ Claude").
- Texto com `background-clip:text` (dourado) **corta til e cedilha** → `padding: 0.22em 0.04em 0.16em; margin: -0.22em -0.04em -0.16em`.
- Texto sempre **abaixo do queixo** (zona do peito, ~y 1130–1530 em 1080x1920) e dentro da área segura do Reels (evitar topo < 220 e fundo > ~1550).
- Hook: palavra grande atrás da cabeça funciona muito bem — recorte da pessoa com `npx hyperframes remove-background` (local, ~2 min p/ 6 s) e o texto entre o vídeo e o recorte, ambos dentro do wrapper da câmera.

**Legendas** (fora dos blocos de lettering): Montserrat 700 ~50px, branca com sombra forte, 2–5 palavras por grupo, revelando palavra a palavra; palavra de ênfase em serifada itálica colorida. Esconder a legenda quando o lettering está na tela (não repetir texto). Em fundo claro (camiseta branca), adicionar um gradiente escuro (scrim) na parte de baixo; o scrim começa com `opacity:0` no CSS e é revelado no tempo 0 (regra do lint).

**Jogo de câmera** (wrapper `#cam`, `transform-origin: 540px 700px` — sobe o rosto no quadro e tira do topo letreiros do cenário a partir de 1.45x):
- Gancho: entra 1.75→2.0 (expo.out) e segue empurrando devagar.
- Alternar close (2.0x) e médio (1.45x) em todo corte; push-in lento (+0.1 em ~2–5 s) dentro dos trechos; punch rápido (+0.2 em 0.12 s) na palavra-chave.
- Nunca deixar o enquadramento mostrar letreiro cortado no topo.

**Transições**: light leak laranja/creme (bloco `light-leak` do `hyperframes-registry` — antes chamado `organic-light-leak-overlay` —, embutido como 3 camadas com `mix-blend-mode: screen`), pico de ~0,14 s em cada entrada/saída de b-roll e nos cortes secos; flash branco curto no drop (estilo Reels de criador); vídeo encolhendo para virar "tela" com etiqueta "EDITADO COM IA".

**Ênfase no negativo** (pedido explícito): b-roll em **P&B** (feito no ffmpeg: `hue=s=0,eq=contrast=1.18:brightness=-0.03,vignette`), palavra **vermelha com glitch**, **tremor de câmera** (keyframes x/y/rotation em 0,5 s no wrapper `#shake` com `scale 1.03` de folga), **impacto grave** + glitch no som.

**Formato react** (referência editor_cyborg):
- Fundo escuro com brilho laranja suave; **painel de conteúdo em cima** (960x680, x60 y140, cantos 40px, borda branca fina + brilho); **card da pessoa embaixo** (700x600, x190 y860) com push-in lento; **pílulas de legenda** sob o card (escura com borda, verde para dinheiro, dourada para prova). A pílula entra com escala junto com a 1ª palavra (não aparecer vazia).
- O card é um **segundo `<video>` do mesmo arquivo**, com início/duração diferentes por janela (mesmo src/start/duração duplicados geram `duplicate_media_discovery_risk`). Nada de vídeo temporizado dentro de wrapper temporizado.
- Conteúdo do painel: b-roll, foto com Ken Burns, motion graphics (mapa com pino pulsando, gráfico de barras "DEMANDA ↑", notificação "Aluguel recebido ✓", contador "+12 ANOS" que conta 0→12 via setter de propriedade — `onUpdate` não roda no seek), e **vídeos reais de clientes**.
- Elementos não temporizados do painel (gráfico, pino) precisam ser escondidos com `tl.set(..., {opacity:0})` ao sair da janela, senão aparecem no react seguinte.
- Ótimo para usar material horizontal num vídeo vertical.

**Prova social**: use os vídeos reais que o usuário mandar (cliente com o profissional, aperto de mão, joinha). **Nunca gerar clientes falsos com IA.** Recortar para 960x680 enquadrando os rostos, alinhar o melhor gesto (joinha) com o momento-chave da fala (ex.: contador chegando em 12).

## 6. B-roll realista com IA (Higgsfield)

- Ler `higgsfield` (+ `skills/higgsfield-prompt/SKILL.md`, `skills/shared/negative-constraints.md`), `higgsfield-generate` e `cinematic-video-prompt` antes de escrever prompts.
- Fluxo: **frame inicial → revisar → animar**. Prompts em inglês (MCSLA), sem palavras vazias ("stunning"), câmera/lente/luz reais ("Shot on Sony FX3, 24mm"), "natural skin texture", "anatomically correct hands", "no text, no logos". Vídeo i2v: descrever só o que se move + 1 movimento de câmera.
- Modelos custo-benefício (medido): frame com `soul_location` (cenários) ou `soul_cinematic` (pessoas) a 0,12 crédito; `nano_banana_2` (= Nano Banana Pro, 2 créditos) para mãos, detalhes e cenas de estrago; vídeo com `kling3_0 --mode pro --sound off --duration 5 --aspect_ratio 9:16` a 8,75 créditos. Seedance 2.5 custa 35–60 por clipe — só se o usuário pedir.
- **Antes de usar, troque o `scripts/broll.json`**: o que vem na skill é o roteiro de exemplo do projeto de imóveis (aéreas da Flórida etc.). Escreva as cenas do projeto atual.
- `scripts/gen_broll.py cost images|videos <ids>|--all` estima o custo de cada cena e o total **sem gerar** — rode sempre antes e mostre ao usuário com o saldo (`higgsfield account status`).
- `scripts/gen_broll.py images|videos <ids>|--all` gera em paralelo (até 4 de cada vez) e baixa para `broll/`. Sem ids nem `--all` ele recusa, para nunca disparar o lote inteiro por engano. Lê o JSON com `utf-8-sig` porque o PowerShell grava BOM. Jobs às vezes falham no servidor → rodar de novo só aquele id.
- Revisar cada frame: cena fraca/escura → refazer com Nano Banana Pro; logo de marca (ex.: maçã no notebook) → refazer pedindo "plain unbranded lid".
- Padronizar: `scale+crop 1080x1920, fps=30, -g 30`, leve grade quente; P&B nos negativos.
- Cenas que funcionaram para imóveis: aérea de bairro com palmeiras/lago no fim de tarde, aérea de bairro nobre à beira do lago, casa moderna com gimbal avançando, mãos guardando dólares num envelope, casal planejando no notebook, homem à noite no notebook (P&B), casa abandonada com manchas (P&B), goteira no balde (P&B).
- Trilha (quando pedida): gerar livre de direitos com `sonilo_music` (~1,9 crédito/32 s), 2 opções; achar o drop com `scripts/beats.py` (librosa) e alinhar o drop ao corte gancho→conteúdo; trilha abafada (passa-baixa abrindo) no gancho + riser terminando no corte + impacto; ducking ~13 dB abaixo da voz. Música viral famosa tem direito autoral — avisar e oferecer exportar sem trilha.

## 7. Montagem no HyperFrames

- `npx hyperframes init edicao --non-interactive --resolution portrait`; ler `hyperframes` (contrato) e `hyperframes/references/types/vertical.md`.
- Para vídeo longo, **gerar o index.html por dados** com `scripts/gen_comp.py` (listas: FULL b-roll, REACT, CLIENTES, LEAKS, SHAKES, CAM, LT lettering, CAPS legendas, PILLS, SFX). Ele grava também `work/sfx_cues.json`; `scripts/mix.py` mixa voz + SFX (pico de cada efeito no tempo da deixa, riser terminando no corte) e normaliza (−14 a −15 LUFS; sem trilha deixa −15 para o usuário somar a música). Para Reels curtos com trilha: `scripts/mix_audio.py`.
- SFX leves (biblioteca do `media-use`): whoosh/whoosh-short nas transições (−16 a −22 dB), click-soft/pop nas palavras (−18 a −22), impact-bass + glitch-1 nos negativos (−11 a −17), key-press como tique do relógio/contador/digitação, notification no "aluguel recebido"/DM, sparkle no "+12", pop no botão.
- Marcar sobreposições intencionais: `data-layout-allow-overlap` (cópias do glitch), `data-layout-allow-overflow`/`-occlusion` (luz, wrapper de câmera, texto atrás da cabeça).
- Ciclo: `npx hyperframes check` (0 erros) → `npx hyperframes snapshot --at ...` em ~30 tempos → revisar as folhas (texto sobre a boca? letreiro cortado? elemento sobrando no react? acento cortado? palavra quebrando linha? pílula vazia?) → corrigir → repetir.
- (Windows) Arquivos editados pelo PowerShell: usar Python/ferramenta de edição, nunca `Set-Content` sem `-Encoding` (quebra acentos).

## 8. Render e entrega

- **Vídeos de iPhone podem ser HDR (HLG, bt2020)** → o render vira HDR sozinho (lento e cor errada no Instagram). Checar `color_transfer` com ffprobe; converter com `zscale=tin=arib-std-b67:min=bt2020nc:pin=bt2020:rin=tv:t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p` e marcar bt709. Renderizar com `--sdr`.
- Render que cai por falta de memória do Node (no Windows aparece como exit −1073740791 / 0xC0000409): usar `NODE_OPTIONS=--max-old-space-size=12288` antes do comando (no Windows: `$env:NODE_OPTIONS="--max-old-space-size=12288"`) e `--video-frame-format auto` (JPG) em vez de PNG.
- Comando: `npx hyperframes render --sdr --quality delivery --fps 30 --video-frame-format auto --workers 3 -o <projeto>/<nome>-FINAL.mp4` em segundo plano, log em arquivo.
- Conferir e informar: ffprobe (1080x1920, 30 fps, duração, H.264, SDR bt709), `ebur128` (LUFS/pico), `freezedetect` (nada travado), `lagcheck.py` mix × final (0 ms), folha de quadros do arquivo final.
- Entregar com `SendUserFile`, resumo curto em português: o que foi feito, números, créditos gastos e onde ficou salvo. Oferecer versão sem trilha quando houver música.
