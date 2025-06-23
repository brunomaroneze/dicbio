from django.shortcuts import render
from verbetes.models import Verbete, Definition # Para Palavra do Dia e Últimos Verbetes
from documentacao.views import extrair_metadados_texto_md # Reutilizar a função se os textos da documentação forem lidos aqui
from pathlib import Path
import random
import re # Para extrair imagens do Markdown
from django.core.cache import cache # Importar o módulo de cache
from django.db.models import Prefetch


# Função para extrair a primeira imagem Markdown
def extrair_primeira_imagem_md(markdown_content):
    # Regex para encontrar a primeira imagem markdown: ![alt text](url "title")
    # Este regex é simples e pega a URL da primeira ocorrência.
    match = re.search(r"!\[.*?\]\((.*?)\)", markdown_content)
    if match:
        url = match.group(1)
        # Se a URL não for absoluta (não começar com http ou /),
        # e for algo como /static/..., ela já deve funcionar.
        # Se for um caminho relativo como './img/foto.jpg', precisa de tratamento.
        # Para o seu caso de '/static/documentacao/img/...', deve estar OK.
        return url
    return None

def pagina_inicial_view(request):
    context = {}

    # 1. Palavra do Dia (com cache)
    cache_key = 'palavra_do_dia_slug' # Chave para armazenar no cache
    palavra_do_dia_slug = cache.get(cache_key) # Tenta pegar o slug do cache

    palavra_do_dia_obj = None

    if palavra_do_dia_slug:
        # Se encontrou no cache, tenta buscar o verbete pelo slug
        try:
            # Usa Prefetch para carregar as definições de uma vez (otimização)
            palavra_do_dia_obj = Verbete.objects.prefetch_related(
                Prefetch('definicoes', queryset=Definition.objects.order_by('sensenumber'), to_attr='definicoes_carregadas')
            ).get(slug=palavra_do_dia_slug)
            
            # Ajusta para o template acessar .definicoes.first.definition
#            if hasattr(palavra_do_dia_obj, 'definicoes_carregadas'):
#                palavra_do_dia_obj.definicoes = palavra_do_dia_obj.definicoes_carregadas

        except Verbete.DoesNotExist:
            # O slug estava no cache, mas o verbete não existe mais (dados inconsistentes)
            # Limpa o cache para forçar um novo sorteio
            cache.delete(cache_key)
            palavra_do_dia_slug = None # Força a lógica de sorteio abaixo
        except Exception as e:
            print(f"Erro ao carregar palavra do dia do cache: {e}")
            cache.delete(cache_key) # Limpa o cache em caso de erro
            palavra_do_dia_slug = None

    if not palavra_do_dia_slug: # Se não estava no cache ou deu erro, sorteia uma nova
        try:
            # Prefetch das definições para evitar N+1 queries ao acessar definicoes no template
            verbete_candidato = Verbete.objects.prefetch_related(
                Prefetch('definicoes', queryset=Definition.objects.order_by('sensenumber'), to_attr='definicoes_carregadas')
            ).filter(definicoes__isnull=False).distinct().order_by('?').first()

            if verbete_candidato:
                palavra_do_dia_obj = verbete_candidato
                # Ajusta para o template acessar .definicoes.first.definition
#                if hasattr(palavra_do_dia_obj, 'definicoes_carregadas'):
#                    palavra_do_dia_obj.definicoes = palavra_do_dia_obj.definicoes_carregadas

                # Armazena o slug no cache por 24 horas (ou o tempo de TIMEOUT padrão)
                cache.set(cache_key, palavra_do_dia_obj.slug)
            else:
                # Fallback se nenhum verbete com definição for encontrado
                # Pode pegar um verbete sem definição, se permitido
                palavra_do_dia_obj = Verbete.objects.order_by('?').first()

        except Exception as e:
            print(f"Erro ao sortear palavra do dia: {e}")
            palavra_do_dia_obj = None

    context['palavra_do_dia'] = palavra_do_dia_obj


    # 2. Textos Diversos / Curiosidades
    #    Lógica similar à view de documentacao, mas para sortear e pegar imagens.
    textos_curiosidades_para_exibir = []
    try:
        # Caminho para a pasta ESPECÍFICA de curiosidades
        # base_path_doc é a pasta 'documentacao/textos'
        # Então, a pasta das curiosidades é base_path_doc / 'curiosidades'
        curiosidades_folder_path = Path(__file__).resolve().parent.parent / 'documentacao' / 'textos' / 'curiosidades'
        
        # Garante que a pasta existe antes de tentar ler
        if not curiosidades_folder_path.exists():
            print(f"AVISO: Pasta de curiosidades não encontrada em: {curiosidades_folder_path}")
            # Deixe a lista vazia e a view continua sem erro
            pass 

        # Lista todos os arquivos Markdown na pasta de curiosidades
        # Não precisa mais de slugs_excluir aqui, pois já estamos na pasta certa
        arquivos_md_curiosidades_paths = list(curiosidades_folder_path.glob('*.md'))

        # Seleciona 1 ou 2 curiosidades aleatoriamente
        if len(arquivos_md_curiosidades_paths) >= 2:
            textos_sorteados_paths = random.sample(arquivos_md_curiosidades_paths, 2)
        elif arquivos_md_curiosidades_paths: # Se tiver apenas 1 curiosidade
            textos_sorteados_paths = random.sample(arquivos_md_curiosidades_paths, 1)
        else: # Nenhuma curiosidade na pasta
            textos_sorteados_paths = []

        for path_md in textos_sorteados_paths:
            slug = path_md.stem # O slug é o nome do arquivo sem extensão
            metadados = extrair_metadados_texto_md(path_md)
            titulo = metadados['titulo']
            
            imagem_url = None
            try:
                with open(path_md, 'r', encoding='utf-8') as f_md:
                    conteudo_md = f_md.read()
                    imagem_url = extrair_primeira_imagem_md(conteudo_md)
            except Exception as e:
                print(f"Erro ao ler ou extrair imagem de {path_md.name}: {e}")
                pass # Falha ao ler ou extrair imagem

            textos_curiosidades_para_exibir.append({
                'slug': slug,
                'titulo': titulo,
                'imagem_url': imagem_url
            })
    except Exception as e:
        print(f"Erro geral ao carregar textos de curiosidades: {e}") # Para debug
        pass # Permite que a página carregue mesmo se esta seção falhar

    # Atribui as curiosidades sorteadas ao contexto
    context['texto_diverso_1'] = textos_curiosidades_para_exibir[0] if len(textos_curiosidades_para_exibir) > 0 else None
    context['texto_diverso_2'] = textos_curiosidades_para_exibir[1] if len(textos_curiosidades_para_exibir) > 1 else None

    # 3. Últimos Verbetes Adicionados/Atualizados
    try:
        # Ordena por data de atualização (mais recente primeiro), depois por data de criação
        context['ultimos_verbetes'] = Verbete.objects.all().order_by('-atualizado_em', '-criado_em')[:5] # Pega os 5 últimos
    except Exception:
        context['ultimos_verbetes'] = None

    # Links para "Sobre o Dicionário" já estão no template.
    # "Apoio" já está no template.

    return render(request, 'pagina_inicial/home.html', context)