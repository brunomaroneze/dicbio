#!/bin/bash
# Uso: sudo bash revisao/vps/instalar_envio.sh
# Instala o serviço de login e de envio das conferências. Pode ser repetido; para
# trocar o token, apague antes /etc/dicbio/token.
# Na primeira vez, troca a senha do navegador (auth_basic) pelo login por
# formulário; a configuração anterior fica em /etc/dicbio/nginx-antes-do-login.conf.
set -euo pipefail
[ "$(id -u)" = 0 ] || { echo "Execute com sudo"; exit 1; }
SITE=/etc/nginx/sites-available/dicbio-conferencia
SENHAS=/etc/nginx/dicbio.htpasswd
[ -f "$SITE" ] || { echo "Não encontrei $SITE"; exit 1; }
grep -q 'ssl_certificate ' "$SITE" || { echo "Ative o HTTPS antes"; exit 1; }
nginx -V 2>&1 | grep -q http_auth_request_module || { echo "O nginx não tem o módulo auth_request"; exit 1; }
python3 -c 'import bcrypt' 2>/dev/null || apt-get install -y python3-bcrypt

install -d -m 700 /etc/dicbio
if [ ! -s /etc/dicbio/token ]; then
  read -r -s -p "Cole o token do GitHub (não aparece na tela) e tecle Enter: " TOKEN; echo
  [[ $TOKEN =~ ^github_pat_[A-Za-z0-9_]+$ ]] || { echo "Não parece um fine-grained token"; exit 1; }
  (umask 077; printf '%s' "$TOKEN" > /etc/dicbio/token)
fi
# Assina os cookies de login. Apagar e reinstalar desconecta todo mundo.
[ -s /etc/dicbio/segredo ] || (umask 077; head -c 32 /dev/urandom | base64 > /etc/dicbio/segredo)

# Fica fora do repositório: só muda quando este instalador é executado.
install -m 644 "$(dirname "$0")/envio.py" /usr/local/lib/dicbio-envio.py
cat > /etc/systemd/system/dicbio-envio.service <<FIM
[Unit]
Description=Login e envio das conferencias do DicBio
Wants=network-online.target
After=network-online.target
[Service]
ExecStart=/usr/bin/python3 -I -B /usr/local/lib/dicbio-envio.py
LoadCredential=token:/etc/dicbio/token
LoadCredential=segredo:/etc/dicbio/segredo
Environment=DICBIO_SENHAS=$SENHAS
DynamicUser=yes
# Para ler o arquivo de senhas (root:www-data, 640).
SupplementaryGroups=www-data
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

TRECHO=/etc/nginx/snippets/dicbio-envio.conf
COPIA=$(mktemp); COPIA_TRECHO=$(mktemp)
cp "$SITE" "$COPIA"
[ -f "$TRECHO" ] && cp "$TRECHO" "$COPIA_TRECHO" || : > "$COPIA_TRECHO"
cat > "$TRECHO" <<'FIM'
# Login por formulário: o nginx pergunta ao serviço se o cookie vale.
auth_request /_sessao;
error_page 401 = @dicbio_entrar;
location = /_sessao {
    internal;
    proxy_pass http://127.0.0.1:8377/sessao;
    proxy_pass_request_body off;
    proxy_set_header Content-Length "";
}
location @dicbio_entrar {
    return 302 /entrar?volta=$request_uri;
}
location = /entrar {
    auth_request off;
    client_max_body_size 4k;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_pass http://127.0.0.1:8377;
}
location = /sair {
    auth_request off;
    proxy_pass http://127.0.0.1:8377;
}
location = /api/enviar {
    auth_request off;   # o próprio serviço confere o cookie
    client_max_body_size 200k;
    proxy_pass http://127.0.0.1:8377;
}
FIM
if grep -q 'auth_basic' "$SITE"; then
  [ -f /etc/dicbio/nginx-antes-do-login.conf ] || cp "$SITE" /etc/dicbio/nginx-antes-do-login.conf
  sed -i '/^\s*auth_basic/d' "$SITE"
fi
if ! grep -q 'snippets/dicbio-envio.conf' "$SITE"; then
  sed -i '0,/^\s*root \/srv\/dicbio\/publico\/site;/s//&\n    include snippets\/dicbio-envio.conf;/' "$SITE"
fi
# Se a configuração tiver erro, desfaz para não afetar os outros sites.
if ! grep -q 'snippets/dicbio-envio.conf' "$SITE" || ! nginx -t; then
  cp "$COPIA" "$SITE"; cp "$COPIA_TRECHO" "$TRECHO"
  echo "Erro na configuração do nginx; ela foi restaurada, mas o envio só volta a funcionar depois de corrigir e reinstalar."; exit 1
fi
systemctl reload nginx
sleep 1
systemctl is-active dicbio-envio.service
echo "Instalado. Teste em https://$(grep -m1 -oP 'server_name\s+\K[^ ;]+' "$SITE")/"
