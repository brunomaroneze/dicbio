# Conferência de transcrições

Tela em que o revisor compara a imagem de cada página com o texto, sem ver o XML. Cada envio vira uma issue, e o GitHub Actions a transforma em pull request.

## Como funciona

1. `gerar_site.py` extrai o texto de cada página dos XML; o workflow `conferencia-site.yml` publica a tela no GitHub Pages.
2. O revisor corrige, salva uma ou mais páginas e clica em "Enviar". Abre-se uma issue já preenchida.
3. O workflow `conferencia-pr.yml` verifica se o revisor está em `revisores.txt`, aplica as correções e abre o pull request.
4. Aceito o pull request, a issue se fecha, a página fica registrada em `conferidas/` e a tela é atualizada.

As tags nunca são alteradas: se a correção mudasse alguma, o envio seria recusado, com um comentário na issue.

## Configuração (uma vez)

1. Publicar as imagens reduzidas em um repositório público `dicbio-imagens`, com GitHub Pages ativado:
   `python revisao/preparar_imagens.py ../dicbio-imagens carvalhoaviso_imagens`
   (o endereço fica em `base_imagens`, no `config.json`)
2. Levar esta pasta, `.github/` e os XML atualizados para o ramo `main`.
3. Em *Settings > Pages*, escolher *Source: GitHub Actions*.
4. Em *Settings > Actions > General*, marcar *Allow GitHub Actions to create and approve pull requests*.
5. Em *Actions*, executar "Publicar tela de conferência" (*Run workflow*).

## Uso cotidiano

- Novo revisor: incluir o usuário do GitHub em `revisores.txt`. Não é preciso dar acesso de escrita ao repositório.
- Nova obra: mudar `ativa` para `true` no `config.json`.
- Conflito entre pull requests: fechar e reabrir a issue; o pull request é refeito sobre o `main` atual.

## Teste local

    python revisao/gerar_site.py --local --todas
    python -m http.server 8000 --bind 127.0.0.1

Abrir http://127.0.0.1:8000/revisao/_site/ . Teste automático: `python revisao/testes.py` (requer Node; demora alguns minutos).
