# Conferência de transcrições

Tela em que o revisor compara a imagem de cada página com o texto, sem ver o XML. Cada envio vira uma issue, e o GitHub Actions a transforma em pull request.

## Como funciona

1. Na VPS, uma tarefa agendada baixa o `develop` a cada 5 minutos e executa `gerar_site.py`, que extrai dos XML o texto de cada página. A tela e as imagens ficam no mesmo endereço, protegidas por senha.
2. O revisor corrige, salva uma ou mais páginas e clica em "Enviar". Um serviço na VPS (`vps/envio.py`) cria uma issue com um token do projeto; o revisor não precisa de conta no GitHub.
3. O workflow `conferencia-pr.yml` verifica se o autor da issue (o dono do token) está em `revisores.txt`, aplica as correções e abre o pull request.
4. Aceito o pull request (dirigido ao `develop`), o workflow `conferencia-fechar.yml` fecha a issue, a página fica registrada em `conferidas/` e a tela é atualizada.

As tags nunca são alteradas: se a correção mudasse alguma, o envio seria recusado, com um comentário na issue.

## Instalação na VPS (uma vez)

1. No painel do domínio, criar um registro `A` para o subdomínio (por exemplo, `conferencia`), com o IP da VPS. Conferir com `getent hosts conferencia.DOMINIO`.
2. Na VPS:

       git clone --depth 1 -b develop https://github.com/brunomaroneze/dicbio.git ~/dicbio-instalar
       sudo bash ~/dicbio-instalar/revisao/vps/instalar.sh conferencia.DOMINIO develop

   Para a VPS seguir outro ramo: `echo RAMO | sudo tee /srv/dicbio/ramo.txt`.
3. Ativar o HTTPS **antes** de criar senhas: `sudo certbot --nginx --redirect -d conferencia.DOMINIO`
4. Criar os acessos (ver abaixo).
5. Enviar as imagens locais. No computador (PowerShell):

       python revisao/preparar_imagens.py "$HOME\dicbio-imagens" carvalhoaviso_imagens
       scp -r "$HOME\dicbio-imagens\carvalhoaviso_imagens" USUARIO@IP_DA_VPS:/srv/dicbio/imagens/

6. No GitHub, em *Settings > Actions > General*, marcar *Allow GitHub Actions to create and approve pull requests*.

Os workflows precisam estar no `main` e no `develop`: o que cria o pull request roda a partir do `main`, e o que fecha a issue, a partir do `develop`. O ramo de destino está em `conferencia-pr.yml`.

## Uso cotidiano

- **Incluir revisor:** na VPS, `sudo htpasswd -B /etc/nginx/dicbio.htpasswd NOME` (o programa pede a senha). O nome (letras, números, ponto, hífen ou sublinhado) fica público nos pull requests e em `conferidas/`.
- **Remover revisor:** `sudo htpasswd -D /etc/nginx/dicbio.htpasswd NOME`.
- **Login:** os revisores entram por um formulário (`/entrar`); o login vale por 30 dias naquele navegador, e `/sair` encerra a sessão. Trocar a senha de alguém ou removê-lo do arquivo de senhas encerra as sessões dele na hora. Depois de 10 senhas erradas para o mesmo usuário, ele fica bloqueado por 15 minutos. Antes era usada a janela de senha do próprio navegador (`auth_basic`), que a rede de algumas universidades bloqueia; a configuração antiga do nginx ficou em `/etc/dicbio/nginx-antes-do-login.conf`.
- **Tentativas de login:** `journalctl -u dicbio-envio -n 30` (mostra quem entrou, senhas erradas e o IP).
- **Token do GitHub** (*fine-grained*, só o repositório `dicbio`, só *Issues: Read and write*): instalar com `sudo bash revisao/vps/instalar_envio.sh`, que também instala o login. Para trocar quando vencer: `sudo rm /etc/dicbio/token` e executar o instalador de novo.
- **O envio falha:** `journalctl -u dicbio-envio -n 30`
- **Nova obra:** mudar `ativa` para `true` no `config.json`.
- **Copiar imagens do Internet Archive ou de Coimbra** (na VPS; repetir o primeiro comando se houver erros):

       python3 -B /srv/dicbio/repo/revisao/baixar_imagens.py compendio1brotero /srv/dicbio/imagens
       sudo truncate -s 0 /srv/dicbio/publicado.txt
       sudo systemctl start dicbio-conferencia.service

- **Conflito entre pull requests:** fechar e reabrir a issue; o pull request é refeito sobre o `develop` atual.
- **A tela não atualiza:** `journalctl -u dicbio-conferencia -n 30`

## Teste local

    python revisao/gerar_site.py --local --todas
    python -m http.server 8000 --bind 127.0.0.1

Abrir http://127.0.0.1:8000/revisao/_site/ . Teste automático: `python revisao/testes.py` (requer Node; demora alguns minutos).
