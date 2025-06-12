# documentacao/views.py
from django.shortcuts import render
from pathlib import Path
import markdown
import re
from datetime import datetime

def extrair_metadados_texto_md(caminho_arquivo):
    titulo = caminho_arquivo.stem # Fallback padrão
    autores = "Autor(es) não especificado(s)"
    ano_publicacao = None
    
    try:
        with open(caminho_arquivo, encoding='utf-8') as f:
            lines = f.readlines()
            
            found_title = False
            
            for i, line in enumerate(lines):
                stripped_line = line.strip()

                if not found_title and stripped_line.startswith('# '):
                    titulo = stripped_line[2:].strip()
                    found_title = True
                    # Não continue aqui, pois a próxima linha pode ser os autores
                
                # Procura autores na linha seguinte ao título (ou qualquer linha após o título)
                # MUDANÇA AQUI: .lower() para ser insensível a maiúsculas/minúsculas
                if found_title and stripped_line.lower().startswith('por '):
                    autores = stripped_line[4:].strip() # Remove "Por " ou "por "
                    # Se você quer garantir que só pega a primeira linha 'Por', pode adicionar um 'break' aqui,
                    # mas para este caso, o loop continua e a variável 'autores' é sobrescrita se encontrar mais.
                    
                    # Tenta extrair o ano (que agora deve vir da linha da data)
                    if i + 1 < len(lines): # A linha da data é a próxima
                        data_line_for_year = lines[i+1].strip()
                        match_year = re.search(r'\b(\d{4})\b', data_line_for_year)
                        if match_year:
                            found_year_str = match_year.group(1)
                            try:
                                found_year_int = int(found_year_str)
                                if found_year_int > 2022:
                                    ano_publicacao = found_year_str
                                    # Se a data e os autores estão sempre juntos, podemos sair do loop aqui
                                    break # Sai do loop principal for i, line
                            except ValueError:
                                pass

    except Exception as e:
        print(f"Erro ao extrair metadados de {caminho_arquivo}: {e}")

    return {
        'titulo': titulo,
        'autores': autores,
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
        conteudo_html = markdown.markdown(f.read(), extensions=['extra', 'smarty'])

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