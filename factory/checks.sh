#!/usr/bin/env bash
# As verificacoes deste repositorio. Sai 0 so quando o branch esta pronto para revisao.
# O gate corre este script com a worktree do job como directorio de trabalho.
# Mantem-no rapido, determinista e nao interactivo: sem watch, sem prompts,
# e sem nada que reescreva ficheiros (--fix, --update-snapshots).
set -euo pipefail
export CI=true

echo "factory/checks.sh ainda nao tem verificacoes. Acrescenta os comandos de teste, lint, typecheck e build deste repositorio." >&2
exit 1
