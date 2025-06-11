from django.shortcuts import render
from verbetes.models import Verbete, Definition # Para Palavra do Dia e Últimos Verbetes
from documentacao.views import extrair_titulo # Reutilizar a função se os textos da documentação forem lidos aqui
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
    textos_curiosidades = []
    try:
        # Caminho para os textos de documentacao (ajuste se for diferente)
        # Esta parte é um pouco redundante com a view de documentacao.
        # O ideal seria ter uma forma mais centralizada de listar os "documentos" se for comum.
        base_path_doc = Path(__file__).resolve().parent.parent / 'documentacao' / 'textos'
        todos_arquivos_md_paths = list(base_path_doc.glob('*.md'))

        # Remover 'prefacio.md', 'equipe.md', 'metodologia.md' da lista de curiosidades, se desejar
        slugs_excluir = ['prefacio', 'equipe', 'metodologia'] # adicione outros slugs a excluir
        arquivos_md_curiosidades_paths = [
            p for p in todos_arquivos_md_paths if p.stem not in slugs_excluir
        ]

        if len(arquivos_md_curiosidades_paths) >= 2:
            textos_sorteados_paths = random.sample(arquivos_md_curiosidades_paths, 2)
        elif arquivos_md_curiosidades_paths: # Se tiver apenas 1
            textos_sorteados_paths = random.sample(arquivos_md_curiosidades_paths, 1)
        else:
            textos_sorteados_paths = []

        for path_md in textos_sorteados_paths:
            slug = path_md.stem
            titulo = extrair_titulo(path_md) # Reutiliza a função de documentacao.views
            
            imagem_url = None
            try:
                with open(path_md, 'r', encoding='utf-8') as f_md:
                    conteudo_md = f_md.read()
                    imagem_url = extrair_primeira_imagem_md(conteudo_md)
            except Exception:
                pass # Falha ao ler ou extrair imagem

            textos_curiosidades.append({
                'slug': slug,
                'titulo': titulo,
                'imagem_url': imagem_url
            })
    except Exception as e:
        print(f"Erro ao carregar textos de curiosidades: {e}") # Para debug
        pass # Permite que a página carregue mesmo se esta seção falhar

    context['texto_diverso_1'] = textos_curiosidades[0] if len(textos_curiosidades) > 0 else None
    context['texto_diverso_2'] = textos_curiosidades[1] if len(textos_curiosidades) > 1 else None


    # 3. Últimos Verbetes Adicionados/Atualizados
    try:
        # Ordena por data de atualização (mais recente primeiro), depois por data de criação
        context['ultimos_verbetes'] = Verbete.objects.all().order_by('-atualizado_em', '-criado_em')[:5] # Pega os 5 últimos
    except Exception:
        context['ultimos_verbetes'] = None

    # Links para "Sobre o Dicionário" já estão no template.
    # "Apoio" já está no template.

    return render(request, 'pagina_inicial/home.html', context)