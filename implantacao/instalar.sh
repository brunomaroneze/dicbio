#!/bin/bash
# Uso: sudo bash implantacao/instalar.sh dicbio.org [ramo]
# Instala o site do dicionário na VPS. Pode ser repetido. Não altera a conferência
# nem os outros sites. Requer Ubuntu com Python 3.12 ou superior.
set -euo pipefail
[ "$(id -u)" = 0 ] || { echo "Execute com sudo"; exit 1; }
DOMINIO=${1:?informe o domínio}
RAMO=${2:-main}
REPO=https://github.com/brunomaroneze/dicbio.git
BASE=/srv/dicbio/site
IMAGENS=/srv/dicbio/imagens
PORTA=8378
if ! [[ $DOMINIO =~ ^[a-z0-9.-]+$ && $RAMO =~ ^[A-Za-z0-9._/-]+$ ]]; then
  echo "Argumento inválido"; exit 1
fi
if ! git ls-remote --exit-code "$REPO" "refs/heads/$RAMO" >/dev/null; then
  echo "O ramo $RAMO não existe no GitHub"; exit 1
fi
python3 -c 'import sys; sys.exit(sys.version_info < (3, 12))' || { echo "É preciso Python 3.12 ou superior"; exit 1; }

apt-get update -q
apt-get install -y -q --no-upgrade git nginx python3-venv
command -v certbot >/dev/null || apt-get install -y -q certbot python3-certbot-nginx

# O mesmo usuário da conferência: sem senha nem sudo.
id dicbio &>/dev/null || useradd --system --user-group --home-dir /srv/dicbio --shell /usr/sbin/nologin dicbio
install -d -m 755 /srv/dicbio
[ -d "$IMAGENS" ] || install -d -m 755 "$IMAGENS"
install -d -m 755 -o dicbio -g dicbio "$BASE" "$BASE/repo" "$BASE/venv"
echo "$RAMO" > "$BASE/ramo.txt"
: > "$BASE/publicado.txt"
chown dicbio: "$BASE/publicado.txt"
if [ ! -d "$BASE/repo/.git" ]; then
  runuser -u dicbio -- git clone --quiet --depth 1 --branch "$RAMO" "$REPO" "$BASE/repo"
fi
[ -x "$BASE/venv/bin/python" ] || runuser -u dicbio -- python3 -m venv "$BASE/venv"

install -d -m 755 /etc/dicbio-site
AMBIENTE=/etc/dicbio-site/ambiente
if [ ! -s "$AMBIENTE" ]; then
  (umask 077; cat > "$AMBIENTE" <<FIM
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(50))')
DJANGO_ENV=production
DEBUG=False
ALLOWED_HOSTS=$DOMINIO,www.$DOMINIO
IMAGENS_ROOT=$IMAGENS
FIM
  )
fi

# O script fica fora do repositório: só muda quando este instalador é executado.
install -m 755 "$(dirname "$0")/atualizar.sh" /usr/local/bin/dicbio-site-atualizar
cat > /etc/systemd/system/dicbio-site.service <<FIM
[Unit]
Description=Site do DicBio
After=network.target
[Service]
User=dicbio
EnvironmentFile=$AMBIENTE
Environment=PYTHONDONTWRITEBYTECODE=1
WorkingDirectory=$BASE/atual
ExecStart=$BASE/venv/bin/gunicorn --bind 127.0.0.1:$PORTA --workers 2 --timeout 60 dicbio.wsgi:application
Restart=on-failure
NoNewPrivileges=yes
ProtectSystem=strict
ProtectHome=yes
PrivateTmp=yes
[Install]
WantedBy=multi-user.target
FIM
# O "+" faz só o reinício do serviço (não o código do repositório) rodar como root.
cat > /etc/systemd/system/dicbio-site-atualizar.service <<FIM
[Unit]
Description=Atualiza o site do DicBio
Wants=network-online.target
After=network-online.target
[Service]
Type=oneshot
User=dicbio
EnvironmentFile=$AMBIENTE
Environment=HOME=$BASE
ExecStart=/usr/local/bin/dicbio-site-atualizar
ExecStartPost=+/bin/sh -c 'if [ -e $BASE/reiniciar ]; then rm -f $BASE/reiniciar; systemctl restart dicbio-site.service; fi'
TimeoutStartSec=20min
NoNewPrivileges=yes
ProtectSystem=strict
ProtectHome=yes
PrivateTmp=yes
ReadWritePaths=$BASE
FIM
cat > /etc/systemd/system/dicbio-site-atualizar.timer <<FIM
[Unit]
Description=Procura atualizacoes do site do DicBio
[Timer]
OnBootSec=3min
OnUnitInactiveSec=10min
[Install]
WantedBy=timers.target
FIM
systemctl daemon-reload
systemctl enable dicbio-site.service
echo "Preparando o site (pode demorar alguns minutos)..."
systemctl start dicbio-site-atualizar.service
systemctl enable --now dicbio-site-atualizar.timer

SITE=/etc/nginx/sites-available/dicbio-site
ATIVO=/etc/nginx/sites-enabled/dicbio-site
if [ -f "$SITE" ]; then
  echo "Mantida a configuração existente: $SITE"
else
  cat > "$SITE" <<FIM
server {
    listen 80;
    server_name $DOMINIO www.$DOMINIO;
    charset utf-8;
    gzip on;
    gzip_types text/css application/javascript application/json;
    location /static/ {
        alias $BASE/atual/staticfiles/;
        add_header Cache-Control "public, max-age=3600";
    }
    location /media/ {
        alias $BASE/atual/mediafiles/;
    }
    # Só as obras com imagens liberadas (OBRAS_COM_IMAGENS, em dicbio/settings.py).
    location ~ ^/imagens/((?:carvalhoaviso|diciovandelli|fazendeiroimbert|observSemmedo)_imagens/.+)\$ {
        alias $IMAGENS/\$1;
        add_header Cache-Control "public, max-age=604800";
    }
    location /imagens/ {
        return 404;
    }
    # O banco é refeito a cada atualização; a administração não é usada.
    location /admin {
        return 404;
    }
    location / {
        proxy_pass http://127.0.0.1:$PORTA;
        proxy_set_header Host \$host;
        proxy_set_header X-Forwarded-For \$remote_addr;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
FIM
  ln -s "$SITE" "$ATIVO"
  # Se a configuração tiver erro, desfaz para não afetar os outros sites.
  if ! nginx -t; then
    rm "$ATIVO" "$SITE"
    echo "Erro na configuração do nginx; nada foi ativado."; exit 1
  fi
  systemctl reload nginx
fi
sleep 2
systemctl is-active dicbio-site.service
echo "Instalado. Com o DNS já apontando para esta VPS, ative o HTTPS:"
echo "  sudo certbot --nginx --redirect -d $DOMINIO -d www.$DOMINIO"
