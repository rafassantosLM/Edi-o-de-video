#!/bin/bash
# Rotina de início de sessão (SessionStart hook) para sessões na nuvem.
#
# Reinstala a Higgsfield CLI, que não sobrevive entre sessões porque fica fora do
# repositório (/usr/local/bin). As skills em .claude/skills/ já vêm com o repositório.
#
# Segurança: em vez de rodar `curl ... | sh` a cada sessão, a versão e o SHA-256 do
# pacote oficial ficam fixados aqui. Se o arquivo baixado não bater com o SHA-256,
# nada é instalado. Para atualizar a CLI, troque HF_VERSION e os dois SHA-256 pelos
# valores do checksums.txt da nova release em github.com/higgsfield-ai/cli/releases.
#
# A rotina nunca impede a sessão de começar: se a rede bloquear o download, ela só
# avisa e segue.
set -euo pipefail

# Só roda nas sessões na nuvem; no seu computador não faz nada.
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

HF_VERSION="1.2.3"
SHA256_LINUX_AMD64="0ed594ae42646d494b9eaeec4359211f6cfd653ce4f790aa4ca6a48c1a431529"
SHA256_LINUX_ARM64="efa302d6d189b81d98d09884830f6b0f89cab7a8c07117825b758d2cc6b49259"
BIN_DIR="/usr/local/bin"

warn() { echo "[session-start] AVISO: $*" >&2; }

# Já instalada na versão certa? Então não faz nada (rápido em resume/clear/compact).
if command -v higgsfield >/dev/null 2>&1 \
  && higgsfield version 2>/dev/null | grep -q "higgsfield ${HF_VERSION} "; then
  exit 0
fi

case "$(uname -m)" in
  x86_64 | amd64) ARCH="amd64"; EXPECTED="$SHA256_LINUX_AMD64" ;;
  aarch64 | arm64) ARCH="arm64"; EXPECTED="$SHA256_LINUX_ARM64" ;;
  *) warn "arquitetura $(uname -m) não suportada; Higgsfield CLI não instalada."; exit 0 ;;
esac

TARBALL="hf_${HF_VERSION}_linux_${ARCH}.tar.gz"
URL="https://github.com/higgsfield-ai/cli/releases/download/v${HF_VERSION}/${TARBALL}"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

if ! curl -fsSL --retry 3 --max-time 120 -o "$TMP/$TARBALL" "$URL"; then
  warn "não consegui baixar a Higgsfield CLI (rede bloqueada?). Sessão segue sem ela."
  exit 0
fi

ACTUAL="$(sha256sum "$TMP/$TARBALL" | awk '{print $1}')"
if [ "$ACTUAL" != "$EXPECTED" ]; then
  warn "SHA-256 não confere para $TARBALL (esperado $EXPECTED, recebido $ACTUAL). Nada foi instalado."
  exit 0
fi

tar -xzf "$TMP/$TARBALL" -C "$TMP" hf
install -m 0755 "$TMP/hf" "$BIN_DIR/higgsfield"
ln -sf "$BIN_DIR/higgsfield" "$BIN_DIR/higgs"
# O atalho `hf` não é criado de propósito: ele pertence à CLI do Hugging Face.

echo "[session-start] $(higgsfield version 2>/dev/null | head -1) instalada (SHA-256 verificado)." >&2
