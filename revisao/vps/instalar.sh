#!/bin/bash
# Uso: sudo bash revisao/vps/instalar.sh conferencia.exemplo.org [ramo]
# Pode ser repetido (por exemplo, para trocar o ramo). Não altera os outros sites.
set -euo pipefail
DOMINIO=${1:?informe o subdomínio}
RAMO=${2:-main}
REPO=https://github.com/brunomaroneze/dicbio.git
BASE=/srv/dicbio
DONO=${SUDO_USER:?execute com sudo, a partir do seu usuário}
if ! [[ $DOMINIO =~ ^[a-z0-9.-]+$ && $RAMO =~ ^[A-Za-z0-9._/-]+$ ]]; then
  echo "Argumento inválido"; exit 1
fi
if ! git ls-remote --exit-code "$REPO" "refs/heads/$RAMO" >/dev/null; then
  echo "O ramo $RAMO não existe no GitHub"; exit 1
fi

apt-get update -q
apt-get install -y -q --no-upgrade apache2-utils python3-pil
if ! command -v certbot >/dev/null; then
  apt-get install -y -q certbot python3-certbot-nginx
fi

# Usuário próprio, sem senha nem sudo: é ele quem executa o código do repositório.
id dicbio &>/dev/null || useradd --system --user-group --home-dir "$BASE" --shell /usr/sbin/nologin dicbio
install -d -m 755 -o root -g root "$BASE"
install -d -m 755 -o dicbio -g dicbio "$BASE/repo" "$BASE/publico"
install -d -m 755 -o "$DONO" -g "$(id -gn "$DONO")" "$BASE/imagens"
echo "$RAMO" > "$BASE/ramo.txt"
: > "$BASE/publicado.txt"
chown dicbio: "$BASE/publicado.txt"
if [ ! -d "$BASE/repo/.git" ]; then
  runuser -u dicbio -- git clone --quiet --depth 1 --branch "$RAMO" "$REPO" "$BASE/repo"
fi

# O script fica fora do repositório: só muda quando este instalador é executado.
install -m 755 "$(dirname "$0")/atualizar.sh" /usr/local/bin/dicbio-atualizar
cat > /etc/systemd/system/dicbio-conferencia.service <<FIM
[Unit]
Description=Atualiza a tela de conferencia do DicBio
Wants=network-online.target
After=network-online.target
[Service]
Type=oneshot
User=dicbio
ExecStart=/usr/local/bin/dicbio-atualizar
Environment=HOME=$BASE
TimeoutStartSec=10min
NoNewPrivileges=yes
ProtectSystem=strict
ProtectHome=yes
PrivateTmp=yes
ReadWritePaths=$BASE/repo $BASE/publico $BASE/publicado.txt
FIM
cat > /etc/systemd/system/dicbio-conferencia.timer <<FIM
[Unit]
Description=Atualiza a tela de conferencia do DicBio a cada 5 minutos
[Timer]
OnBootSec=2min
OnUnitInactiveSec=5min
[Install]
WantedBy=timers.target
FIM
systemctl daemon-reload
systemctl start dicbio-conferencia.service
systemctl enable --now dicbio-conferencia.timer

SENHAS=/etc/nginx/dicbio.htpasswd
[ -f "$SENHAS" ] || touch "$SENHAS"
chown root:www-data "$SENHAS"
chmod 640 "$SENHAS"
SITE=/etc/nginx/sites-available/dicbio-conferencia
ATIVO=/etc/nginx/sites-enabled/dicbio-conferencia
if [ -f "$SITE" ]; then
  echo "Mantida a configuração existente: $SITE"
else
  cat > "$SITE" <<FIM
server {
    listen 80;
    server_name $DOMINIO;
    root $BASE/publico/site;
    index index.html;
    charset utf-8;
    auth_basic "Conferencia DicBio";
    auth_basic_user_file $SENHAS;
    add_header X-Robots-Tag "noindex, nofollow" always;
    location /imagens/ {
        alias $BASE/imagens/;
        add_header Cache-Control "private, max-age=86400";
        add_header X-Robots-Tag "noindex, nofollow" always;
    }
    location / {
        try_files \$uri \$uri/ =404;
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
echo
echo "Instalado. Próximos passos, nesta ordem:"
echo "  sudo certbot --nginx --redirect -d $DOMINIO"
echo "  sudo htpasswd -B $SENHAS NOME"
