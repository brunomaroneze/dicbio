# documentacao/views.py
from django.shortcuts import render
from pathlib import Path
import markdown

def extrair_titulo(caminho_arquivo):
    # ... (sua função extrair_titulo continua a mesma) ...
    with open(caminho_arquivo, encoding='utf-8') as f:
        for linha in f:
            if linha.strip().startswith('# '):
                return linha.strip()[2:]
    return caminho_arquivo.stem

def texto(request, nome_arquivo=None): # nome_arquivo vem da URL (pode ser None)
    base_path = Path(__file__).resolve().parent / 'textos'
    
    # Construir a lista de arquivos com slug e título
    arquivos_info = []
    # Usar sorted aqui garante que a lista 'arquivos_info' esteja ordenada alfabeticamente
    # o que pode ser bom para a exibição na sidebar, mas não afeta a seleção do prefácio.
    for path in sorted(base_path.glob('*.md')): # Ordena por nome de arquivo
        slug = path.stem.strip()
        if not slug:
            continue
        titulo = extrair_titulo(path)
        arquivos_info.append({'slug': slug, 'titulo': titulo})

    if not arquivos_info:
        # Nenhum arquivo .md encontrado na pasta 'textos'
        return render(request, 'documentacao/404.html', {'mensagem_erro': 'Nenhum texto de documentação encontrado.'}, status=404)

    # Lógica para definir o arquivo a ser exibido:
    slug_do_arquivo_a_exibir = nome_arquivo # Se um slug foi passado pela URL

    if not slug_do_arquivo_a_exibir:
        # Nenhum slug específico foi passado pela URL, então definimos o padrão.
        # Priorizar 'prefacio'
        prefacio_info = next((item for item in arquivos_info if item['slug'] == 'prefacio'), None)
        
        if prefacio_info:
            slug_do_arquivo_a_exibir = prefacio_info['slug']
        elif arquivos_info: # Se 'prefacio' não existir, pega o primeiro da lista ordenada
            slug_do_arquivo_a_exibir = arquivos_info[0]['slug']
        else:
            # Este caso não deveria acontecer se a verificação anterior de not arquivos_info funcionou,
            # mas é uma salvaguarda.
            return render(request, 'documentacao/404.html', {'mensagem_erro': 'Nenhum texto de documentação disponível para exibição.'}, status=404)

    # Construir o caminho para o arquivo Markdown a ser exibido
    caminho_md_selecionado = base_path / f'{slug_do_arquivo_a_exibir}.md'

    if not caminho_md_selecionado.exists():
        mensagem = f"O texto '{slug_do_arquivo_a_exibir}.md' não foi encontrado."
        # Pode ser útil mostrar a lista de arquivos ainda assim, se desejar
        return render(request, 'documentacao/404.html', {'mensagem_erro': mensagem, 'arquivos': arquivos_info}, status=404)

    with open(caminho_md_selecionado, encoding='utf-8') as f:
        conteudo_html = markdown.markdown(f.read(), extensions=['extra', 'smarty'])

    context = {
        'conteudo': conteudo_html,
        'arquivos': arquivos_info, # Lista para a sidebar
        'ativo': slug_do_arquivo_a_exibir, # Slug do arquivo atualmente ativo
    }
    return render(request, 'documentacao/home.html', context)