#!/bin/bash
# Uso: sudo bash revisao/vps/instalar_envio.sh
# Instala o envio automático das conferências. Pode ser repetido; para trocar o
# token, apague antes /etc/dicbio/token.
set -euo pipefail
[ "$(id -u)" = 0 ] || { echo "Execute com sudo"; exit 1; }
SITE=/etc/nginx/sites-available/dicbio-conferencia
[ -f "$SITE" ] || { echo "Não encontrei $SITE"; exit 1; }
grep -q 'ssl_certificate ' "$SITE" || { echo "Ative o HTTPS antes"; exit 1; }

install -d -m 700 /etc/dicbio
if [ ! -s /etc/dicbio/token ]; then
  read -r -s -p "Cole o token do GitHub (não aparece na tela) e tecle Enter: " TOKEN; echo
  [[ $TOKEN =~ ^github_pat_[A-Za-z0-9_]+$ ]] || { echo "Não parece um fine-grained token"; exit 1; }
  (umask 077; printf '%s' "$TOKEN" > /etc/dicbio/token)
fi

# Fica fora do repositório: só muda quando este instalador é executado.
install -m 644 "$(dirname "$0")/envio.py" /usr/local/lib/dicbio-envio.py
cat > /etc/systemd/system/dicbio-envio.service <<FIM
[Unit]
Description=Recebe as conferencias do DicBio e cria issues no GitHub
Wants=network-online.target
After=network-online.target
[Service]
ExecStart=/usr/bin/python3 -I -B /usr/local/lib/dicbio-envio.py
LoadCredential=token:/etc/dicbio/token
DynamicUser=yes
Restart=on-failure
NoNewPrivileges=yes
ProtectSystem=strict
ProtectHome=yes
PrivateTmp=yes
[Install]
WantedBy=multi-user.target
FIM
systemctl daemon-reload
systemctl enable dicbio-envio.service
systemctl restart dicbio-envio.service

cat > /etc/nginx/snippets/dicbio-envio.conf <<'FIM'
location = /api/enviar {
    client_max_body_size 200k;
    proxy_set_header X-Revisor $remote_user;
    proxy_set_header Host $host;
    proxy_pass http://127.0.0.1:8377;
}
FIM
if ! grep -q 'snippets/dicbio-envio.conf' "$SITE"; then
  COPIA=$(mktemp)
  cp "$SITE" "$COPIA"
  sed -i '0,/^\s*root \/srv\/dicbio\/publico\/site;/s//&\n    include snippets\/dicbio-envio.conf;/' "$SITE"
  # Se a configuração tiver erro, desfaz para não afetar os outros sites.
  if ! grep -q 'snippets/dicbio-envio.conf' "$SITE" || ! nginx -t; then
    cp "$COPIA" "$SITE"
    echo "Erro na configuração do nginx; nada foi alterado nela."; exit 1
  fi
fi
systemctl reload nginx
sleep 1
systemctl is-active dicbio-envio.service
echo "Instalado."
