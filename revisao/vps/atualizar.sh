#!/bin/bash
# Executado pelo systemd, como usuário dicbio: baixa o ramo configurado e refaz a
# tela se algo mudou.
set -euo pipefail
BASE=/srv/dicbio
RAMO=$(cat "$BASE/ramo.txt")
cd "$BASE/repo"
git fetch --quiet --depth 1 origin "$RAMO"
NOVO=$(git rev-parse FETCH_HEAD)
if [ "$NOVO" = "$(cat "$BASE/publicado.txt")" ]; then
  exit 0
fi
git reset --quiet --hard FETCH_HEAD
python3 -B revisao/gerar_site.py --saida "$BASE/publico/site" --imagens "$BASE/imagens"
echo "$NOVO" > "$BASE/publicado.txt"
