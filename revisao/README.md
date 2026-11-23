# Conferência de transcrições

Tela em que o revisor compara a imagem de cada página com o texto, sem ver o XML. Cada envio vira uma issue, e o GitHub Actions a transforma em pull request.

## Como funciona

1. Na VPS, uma tarefa agendada baixa o `main` a cada 5 minutos e executa `gerar_site.py`, que extrai dos XML o texto de cada página. A tela e as imagens ficam no mesmo endereço, protegidas por senha.
2. O revisor corrige, salva uma ou mais páginas e clica em "Enviar". Abre-se uma issue já preenchida.
3. O workflow `conferencia-pr.yml` verifica se o revisor está em `revisores.txt`, aplica as correções e abre o pull request.
4. Aceito o pull request, a issue se fecha, a página fica registrada em `conferidas/` e a tela é atualizada.

As tags nunca são alteradas: se a correção mudasse alguma, o envio seria recusado, com um comentário na issue.

## Instalação na VPS (uma vez)

1. No painel do domínio, criar um registro `A` para o subdomínio (por exemplo, `conferencia`), com o IP da VPS. Conferir com `getent hosts conferencia.DOMINIO`.
2. Na VPS:

       git clone --depth 1 -b main https://github.com/brunomaroneze/dicbio.git ~/dicbio-instalar
       sudo bash ~/dicbio-instalar/revisao/vps/instalar.sh conferencia.DOMINIO main

   Para testar antes do merge, usar o nome da branch em lugar de `main` nos dois comandos. Depois do merge, apagar `~/dicbio-instalar` e executar os dois comandos de novo, com `main`.
3. Ativar o HTTPS **antes** de criar senhas: `sudo certbot --nginx --redirect -d conferencia.DOMINIO`
4. Criar os acessos (ver abaixo).
5. Enviar as imagens locais. No computador (PowerShell):

       python revisao/preparar_imagens.py "$HOME\dicbio-imagens" carvalhoaviso_imagens
       scp -r "$HOME\dicbio-imagens\carvalhoaviso_imagens" USUARIO@IP_DA_VPS:/srv/dicbio/imagens/

6. No GitHub, em *Settings > Actions > General*, marcar *Allow GitHub Actions to create and approve pull requests*.

O workflow só funciona depois que estiver no `main`.

## Uso cotidiano

- **Incluir revisor:** na VPS, `sudo htpasswd -B /etc/nginx/dicbio.htpasswd NOME` (o programa pede a senha); e incluir o usuário do GitHub em `revisores.txt`.
- **Remover revisor:** `sudo htpasswd -D /etc/nginx/dicbio.htpasswd NOME`; e retirá-lo de `revisores.txt`.
- **Nova obra:** mudar `ativa` para `true` no `config.json`.
- **Copiar imagens do Internet Archive ou de Coimbra** (na VPS; repetir o primeiro comando se houver erros):

       python3 -B /srv/dicbio/repo/revisao/baixar_imagens.py compendio1brotero /srv/dicbio/imagens
       sudo truncate -s 0 /srv/dicbio/publicado.txt
       sudo systemctl start dicbio-conferencia.service

- **Conflito entre pull requests:** fechar e reabrir a issue; o pull request é refeito sobre o `main` atual.
- **A tela não atualiza:** `journalctl -u dicbio-conferencia -n 30`

## Teste local

    python revisao/gerar_site.py --local --todas
    python -m http.server 8000 --bind 127.0.0.1

Abrir http://127.0.0.1:8000/revisao/_site/ . Teste automático: `python revisao/testes.py` (requer Node; demora alguns minutos).
