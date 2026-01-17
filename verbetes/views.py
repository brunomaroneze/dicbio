# verbetes/views.py

from django.shortcuts import render, get_object_or_404, redirect
from .models import Verbete, Definition, OcorrenciaCorpus
from django.db.models import Prefetch, Q # Importar Q para buscas complexas
from django.urls import reverse
from collections import defaultdict
from django.utils.timezone import now
import unicodedata
from django.contrib import messages
from django.http import JsonResponse
from django.template.loader import render_to_string

def remover_acentos(texto):
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    ).lower()

# A função verbete_detalhe permanece a mesma, pois já recebe o slug correto.
def verbete_detalhe(request, slug):
    # ... (código existente da sua função verbete_detalhe) ...
    verbete = get_object_or_404(Verbete, slug=slug)
    # Prefetch otimizado
    ocorrencias_prefetch = Prefetch(
        'ocorrencias',
        queryset=OcorrenciaCorpus.objects.select_related('definicao').order_by('data'),
        to_attr='ocorrencias_carregadas'
    )
    definicoes = Definition.objects.filter(verbete=verbete).order_by('sensenumber').prefetch_related(ocorrencias_prefetch)

    # Processamento de exemplos... (o seu código atual aqui)
    exemplos_tmp = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list))))
    ocorrencias = OcorrenciaCorpus.objects.filter(verbete=verbete).select_related('definicao')
    for o in ocorrencias:
        sense = o.definicao.sensenumber if o.definicao else '0'
        gram = o.gram.strip() or 'N/A'
        autor = o.autor.strip().upper() or 'N/A'
        token_ocorrencia = o.token.strip()
        exemplo = {
           'token': o.token, 'gram': gram, 'frase': o.frase, 'autor': autor,
           'data': o.data, 'titulo_obra': o.titulo_obra, 'slug_obra': o.slug_obra,
           'pagina_obra': o.pagina_obra,
        }
        grupo = exemplos_tmp[str(sense)][token_ocorrencia][gram][autor]
        tam = len(o.frase)
        if 100 <= tam <= 300:
            grupo.insert(0, exemplo)
        else:
            grupo.append(exemplo)
            
    exemplos_por_sense = { sense: { token_val: { gram: dict(autores) for gram, autores in gram_dict.items() } for token_val, gram_dict in token_dict.items() } for sense, token_dict in exemplos_tmp.items() }

    lista_verbetes = sorted(
        Verbete.objects.all(),
        key=lambda v: remover_acentos(v.termo)
    )
    context = {
        'verbete': verbete,
        'definicoes': definicoes,
        'exemplos_por_sense': exemplos_por_sense,
        'lista_verbetes': lista_verbetes,
        'now': now(),
    }
    return render(request, 'verbetes/home.html', context)


# A função 'home' é a que lida com a busca inicial
def home(request):
    termo_busca = request.GET.get('q', '').strip()
    lista_verbetes = sorted(
        Verbete.objects.all(),
        key=lambda v: remover_acentos(v.termo)
    )
    
    # Contexto padrão
    context = {
        'lista_verbetes': lista_verbetes,
        'verbete': None,
        'definicoes': [],
        'exemplos_por_sense': {},
        'mensagem_busca': None,
        'termo_busca': termo_busca, # Passar o termo buscado de volta para o template
    }

    if termo_busca:
        # Passo 1: Tentar encontrar uma correspondência exata (case-insensitive) no termo do verbete.
        verbete_encontrado = Verbete.objects.filter(termo__iexact=termo_busca).first()

        if verbete_encontrado:
            # Se encontrou um verbete principal, redireciona para a página de detalhe dele.
            return redirect('verbetes:detalhe', slug=verbete_encontrado.slug)
        
        # Passo 2: Se não encontrou no verbete principal, procurar por uma variante (token).
        # Procura por uma OcorrenciaCorpus que tenha o 'token' correspondente.
        ocorrencia_variante = OcorrenciaCorpus.objects.filter(token__iexact=termo_busca).select_related('verbete').first()
        
        if ocorrencia_variante:
            # Se encontrou uma ocorrência com o token, pega o verbete associado a ela e redireciona.
            verbete_lematizado = ocorrencia_variante.verbete
            # Adiciona uma mensagem para informar o usuário sobre o redirecionamento
            from django.contrib import messages
            messages.info(request, f'A forma "{termo_busca}" foi encontrada como uma variante do verbete "{verbete_lematizado.termo}".')
            return redirect('verbetes:detalhe', slug=verbete_lematizado.slug)
            
        # Passo 3: Se não encontrou nem no verbete principal nem como variante.
        # Define a mensagem de "não encontrado" para ser exibida no template.
        context['mensagem_busca'] = f"Nenhum verbete ou variante encontrada para '{termo_busca}'."

    # Renderiza a página 'home.html' com o contexto.
    # Se nenhuma busca foi feita, mostra a página inicial com a lista.
    # Se uma busca foi feita e nada foi encontrado, mostra a mensagem de erro.
    return render(request, 'verbetes/home.html', context)

# Função para fazer o concordanciador
def concordancia_por_definicao(request, def_id):
    definicao = get_object_or_404(Definition, id=def_id)
    # Pegamos todas as ocorrências, sem o limite de 1 que usamos no detalhe
    ocorrencias = OcorrenciaCorpus.objects.filter(definicao=definicao).order_by('data')
    
    # Renderizamos um pequeno template apenas com a lista de exemplos
    html = render_to_string('verbetes/includes/lista_concordancia.html', {
        'ocorrencias': ocorrencias,
        'termo': definicao.verbete.termo
    })
    
    return JsonResponse({'html': html, 'total': ocorrencias.count()})

# Nova view para exibir verbete a partir do arquivo Turtle

import rdflib
from django.shortcuts import render
from rdflib.namespace import RDF, RDFS, SKOS
from rdflib import Namespace, Literal

# 1. Carregue o grafo FORA da função para ele ficar na memória (Singleton)
# No futuro, você pode colocar isso no apps.py para ser mais elegante
G = rdflib.Graph()
G.parse("data/DicionarioBiologia.ttl", format="turtle")

def verbete_pelo_turtle(request, lema):
    # Definimos os Namespaces
    ns = {
        "ontolex": "http://www.w3.org/ns/lemon/ontolex#",
        "skos": "http://www.w3.org/2004/02/skos/core#",
        "etym": "http://lari-datasets.ilc.cnr.it/lemonEty#",
        "lexinfo": "http://www.lexinfo.net/ontology/2.0/lexinfo#",
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    }

    # AJUSTE NA QUERY: Agora buscamos a etimologia DENTRO do sense
    query = """
    SELECT ?pos ?definition ?etymComment WHERE {
        # Busca a entrada pelo writtenRep (lema)
        ?entry ontolex:canonicalForm [ ontolex:writtenRep ?lemma ] .
        
        # Pega a classe gramatical (opcional)
        OPTIONAL { ?entry lexinfo:partOfSpeech ?pos . }
        
        # Busca o sentido (obrigatório para ter definição)
        ?entry ontolex:sense ?sense .
        
        # Pega a definição do sentido
        OPTIONAL { ?sense skos:definition ?definition . }
        
        # Pega a etimologia ligada ao SENTIDO (como mudamos agora)
        OPTIONAL { ?sense etym:etymology [ rdfs:comment ?etymComment ] . }
        
        # Filtro para bater o lema exato (sensível a maiúsculas/minúsculas)
        FILTER(STR(?lemma) = ?targetLema)
    }
    """

    # Executa a query passando o parâmetro targetLema de forma segura
    results = G.query(query, initNs=ns, initBindings={'targetLema': Literal(lema, lang="pt")})

    verbete_data = {
        'lemma': lema,
        'pos': '',
        'definitions': [], 
        'etymology_list': [] # Criamos uma lista caso sentidos diferentes tenham etimologias diferentes
    }

    for row in results:
        # Preenche o POS (Classe gramatical)
        if not verbete_data['pos'] and row.pos:
            verbete_data['pos'] = str(row.pos).split('#')[-1]

        # Adiciona a definição
        if row.definition:
            verbete_data['definitions'].append(str(row.definition))

        # Adiciona o comentário etimológico (se existir e não for repetido)
        if row.etymComment and str(row.etymComment) not in verbete_data['etymology_list']:
            verbete_data['etymology_list'].append(str(row.etymComment))

    # Se não achou nada, 404
    if not verbete_data['definitions'] and not verbete_data['etymology_list']:
        return render(request, '404_verbete.html', {'lema': lema}, status=404)

    return render(request, 'verbetes/verbete_turtle.html', {'verbete': verbete_data})