# Site na VPS

A cada 10 minutos, a VPS verifica se o `main` mudou. Se mudou, prepara uma versão completa numa pasta nova (banco SQLite, HTML das obras, arquivos estáticos), confere se as páginas abrem e só então a põe no ar. Se algo falhar, o site anterior continua funcionando.

## Instalação (uma vez)

1. No painel do domínio, apontar os registros `A` de `dicbio.org` e `www` para o IP da VPS, sem mexer em `conferencia`. Conferir com `getent hosts dicbio.org`.
2. Na VPS, com estes arquivos já no `main`:

       git clone --depth 1 -b main https://github.com/brunomaroneze/dicbio.git ~/dicbio-site-instalar
       sudo bash ~/dicbio-site-instalar/implantacao/instalar.sh dicbio.org

3. Ativar o HTTPS:

       sudo certbot --nginx --redirect -d dicbio.org -d www.dicbio.org

## Imagens

O site usa `/srv/dicbio/imagens`, a mesma pasta da conferência, mas **sem senha**. Se uma página não tiver cópia ali, vale o endereço original do `facs`. Para copiar as imagens de uma obra, ver `revisao/README.md`. Depois de copiar, refazer o site:

    sudo truncate -s 0 /srv/dicbio/site/publicado.txt
    sudo systemctl start dicbio-site-atualizar.service

## Uso cotidiano

- **Publicar:** levar as mudanças ao `main`. Para não esperar: `sudo systemctl start dicbio-site-atualizar.service`
- **A atualização falhou:** `journalctl -u dicbio-site-atualizar -n 40`
- **O site não abre:** `journalctl -u dicbio-site -n 40`
- **PDF:** gerar no computador (`pip install -r requirements-local.txt` e `python manage.py generate_full_pdf`) e fazer o commit de `mediafiles/dicionario_completo.pdf`.
- **Voltar à versão anterior** (vale até o próximo commit no `main`):

       ls /srv/dicbio/site/versoes
       sudo ln -sfn /srv/dicbio/site/versoes/PASTA /srv/dicbio/site/atual
       sudo systemctl restart dicbio-site

- **O instalador mudou:** repetir o passo 2 com o repositório atualizado. A configuração do nginx e a chave secreta são mantidas.
- **`/admin`:** desativado na VPS; o banco é refeito a cada atualização.
