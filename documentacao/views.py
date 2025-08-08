# documentacao/views.py
from django.shortcuts import render
from pathlib import Path
import markdown
import re
from datetime import datetime

def extrair_metadados_texto_md(caminho_arquivo):
    """
    Lê o arquivo Markdown e extrai metadados usando a extensão 'meta'.
    Espera um bloco de metadados no início do arquivo (ex: --- \n key: value \n ---).
    """
    titulo = caminho_arquivo.stem # Fallback padrão
    autores = "Autor(es) não especificado(s)"
    ano_publicacao = None
    
    try:
        with open(caminho_arquivo, encoding='utf-8') as f:
            md_content = f.read()
            
            # Cria uma instância Markdown com a extensão 'meta'
            md = markdown.Markdown(extensions=['meta'])
            
            # Processa o conteúdo. Os metadados serão preenchidos em md.Meta
            md.convert(md_content) 
            
            # Extrai os metadados
            if md.Meta:
                # O processador 'meta' retorna uma lista de strings para cada valor.
                # Pegamos o primeiro item da lista para cada chave.
                if 'titulo' in md.Meta and md.Meta['titulo']:
                    titulo = md.Meta['titulo'][0].strip()
                
                if 'autores' in md.Meta and md.Meta['autores']:
                    # Juntar os autores em uma única string (ex: 'Nome1; Nome2')
                    # Eles vêm como ['Nome1', 'Nome2'] se houver várias linhas 'autores:'
                    # ou ['Nome1; Nome2'] se for uma única linha com ;
                    autores_raw = md.Meta['autores'][0].strip()
                    # Substituímos ';' por ' / ' para usar no filtro formatar_autores se ele espera isso
                    # Ou podemos passar a lista de autores para o filtro
                    
                    # Vamos formatar os autores aqui já no padrão "SOBRENOME, Nome"
                    # A função formatar_autores será adaptada para receber uma string "Nome Sobrenome; Nome Sobrenome"
                    # ou uma lista ['Nome Sobrenome', 'Nome Sobrenome']
                    autores = autores_raw # Passamos o string cru para ser processado pelo filtro

                if 'ano_publicacao' in md.Meta and md.Meta['ano_publicacao']:
                    ano_publicacao = md.Meta['ano_publicacao'][0].strip()
                    # Opcional: validar que é um ano de 4 dígitos e > 2022
                    if not (ano_publicacao.isdigit() and int(ano_publicacao) > 2022):
                        ano_publicacao = None # Invalidar se não for o formato esperado
            
    except Exception as e:
        print(f"Erro ao extrair metadados com extensão 'meta' de {caminho_arquivo}: {e}")

    return {
        'titulo': titulo,
        'autores': autores, # String no formato 'Nome1; Nome2' ou 'Nome1 / Nome2'
        'ano_publicacao': ano_publicacao,
    }

def texto(request, nome_arquivo=None):
    base_path = Path(__file__).resolve().parent / 'textos'
    
    # 1. Processar 'prefacio.md' separadamente
    prefacio_slug = 'prefacio'
    path_prefacio = base_path / f'{prefacio_slug}.md'
    prefacio_info = None
    if path_prefacio.exists():
        prefacio_info_base = extrair_metadados_texto_md(path_prefacio)
        prefacio_info = {
            'slug': prefacio_slug, # Adiciona o slug aqui
            'titulo': prefacio_info_base['titulo'],
            'autores': prefacio_info_base['autores'],
            'ano_publicacao': prefacio_info_base['ano_publicacao'],
            # Pode-se também usar {**prefacio_info_base, 'slug': prefacio_slug} para mergear
        }

    # 2. Ler arquivos das subpastas para categorização
    tecnicos_path = base_path / 'tecnicos'
    curiosidades_path = base_path / 'curiosidades'

    textos_tecnicos = []
    textos_curiosidades = []

    if tecnicos_path.exists():
        for path in sorted(tecnicos_path.glob('*.md')):
            slug = path.stem.strip()
            if slug:
                item_info = extrair_metadados_texto_md(path)
                item_info['slug'] = slug
                textos_tecnicos.append(item_info)

    if curiosidades_path.exists():
        for path in sorted(curiosidades_path.glob('*.md')):
            slug = path.stem.strip()
            if slug:
                item_info = extrair_metadados_texto_md(path)
                item_info['slug'] = slug
                textos_curiosidades.append(item_info)

    # Combina todas as listas de arquivos para verificar se há algum conteúdo
    todos_arquivos_disponiveis = []
    if prefacio_info:
        todos_arquivos_disponiveis.append(prefacio_info)
    todos_arquivos_disponiveis.extend(textos_tecnicos)
    todos_arquivos_disponiveis.extend(textos_curiosidades)


    if not todos_arquivos_disponiveis:
        return render(request, 'documentacao/404.html', {'mensagem_erro': 'Nenhum texto de documentação encontrado.'}, status=404)

    # Lógica para definir o arquivo a ser exibido:
    slug_do_arquivo_a_exibir = nome_arquivo # Se um slug foi passado pela URL

    if not slug_do_arquivo_a_exibir:
        # Se nenhum slug específico foi passado pela URL, o padrão é 'prefacio'
        if prefacio_info:
            slug_do_arquivo_a_exibir = prefacio_info['slug']
        elif todos_arquivos_disponiveis: # Se prefácio não existir, pega o primeiro disponível
            slug_do_arquivo_a_exibir = todos_arquivos_disponiveis[0]['slug']
        # Else: (já coberto por not todos_arquivos_disponiveis acima)

    info_do_arquivo_ativo = next((item for item in todos_arquivos_disponiveis if item['slug'] == slug_do_arquivo_a_exibir), None)

    # Constrói o caminho completo para o arquivo Markdown selecionado
    caminho_md_selecionado = None
    if info_do_arquivo_ativo:
        if info_do_arquivo_ativo['slug'] == prefacio_slug:
            caminho_md_selecionado = path_prefacio
        elif info_do_arquivo_ativo in textos_tecnicos: # Este 'in' não é robusto para listas grandes, mas funciona
            caminho_md_selecionado = tecnicos_path / f'{info_do_arquivo_ativo["slug"]}.md'
        elif info_do_arquivo_ativo in textos_curiosidades:
            caminho_md_selecionado = curiosidades_path / f'{info_do_arquivo_ativo["slug"]}.md'
        # Uma alternativa mais robusta para caminho_md_selecionado:
        # Se você armazenasse 'path' no extrair_metadados_texto_md:
        # item_info['path'] = path
        # E então usasse: caminho_md_selecionado = info_do_arquivo_ativo['path']
        # Isso seria mais direto e menos propenso a erros.


    if not caminho_md_selecionado or not caminho_md_selecionado.exists():
        mensagem = f"O texto '{slug_do_arquivo_a_exibir}.md' não foi encontrado."
        return render(request, 'documentacao/404.html', {'mensagem_erro': mensagem, 'arquivos': todos_arquivos_disponiveis}, status=404)

    with open(caminho_md_selecionado, encoding='utf-8') as f:
        conteudo_html = markdown.markdown(f.read(), extensions=['extra', 'smarty', 'meta'])

    context = {
        'conteudo': conteudo_html,
        'prefacio': prefacio_info,
        'textos_tecnicos': textos_tecnicos,
        'textos_curiosidades': textos_curiosidades,
        'ativo': slug_do_arquivo_a_exibir,
        'info_do_arquivo_ativo': info_do_arquivo_ativo,
        'now': datetime.now().date(), # Para a data de acesso no template
    }
    return render(request, 'documentacao/home.html', context)