from django.shortcuts import render
from pathlib import Path
import markdown

def extrair_titulo(caminho_arquivo):
    """Lê o primeiro título Markdown do arquivo (linha que começa com '# ')"""
    with open(caminho_arquivo, encoding='utf-8') as f:
        for linha in f:
            if linha.strip().startswith('# '):
                return linha.strip()[2:]  # remove exatamente os 2 primeiros caracteres "# "
    return caminho_arquivo.stem  # fallback se não houver título

def texto(request, nome_arquivo=None):
    base_path = Path(__file__).resolve().parent / 'textos'
    arquivos_md = sorted(base_path.glob('*.md'))

    if not arquivos_md:
        return render(request, 'documentacao/404.html', status=404)

    # lista com slug (nome do arquivo) e título extraído
    arquivos = []
    for path in sorted(base_path.glob('*.md')):
        slug = path.stem.strip()
        if not slug:
            continue  # ignora arquivos sem nome base

        titulo = extrair_titulo(path)
        arquivos.append({'slug': slug, 'titulo': titulo})

    # se nenhum nome for passado, usa o primeiro
    nome_arquivo = nome_arquivo or arquivos[0]['slug']
    caminho = base_path / f'{nome_arquivo}.md'

    if not caminho.exists():
        return render(request, 'documentacao/404.html', status=404)

    with open(caminho, encoding='utf-8') as f:
        conteudo = markdown.markdown(f.read(), extensions=['extra', 'smarty'])

    return render(request, 'documentacao/texto.html', {
        'conteudo': conteudo,
        'arquivos': arquivos,
        'ativo': nome_arquivo,
    })
