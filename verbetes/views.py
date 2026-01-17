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
from django.conf import settings

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
from rdflib import Namespace, Literal
from django.http import HttpResponse
import os
from lxml import etree

def buscar_contexto_no_xml(xml_id):
    # 1. Identifica a obra pelo ID (ex: p_santucci_0001 -> santucci)
    try:
        partes = xml_id.split('_')
        obra_slug = partes[1]
    except IndexError:
        return "Erro no formato do ID"

    # 2. Mapeia o slug para o nome real do arquivo (ajuste os nomes conforme necessário)
    mapa_arquivos = {
        "santucci": "anatomiasantucci.xml",
        "brotero1": "compendio1brotero.xml",
        "brotero2": "compendio2brotero.xml",
        "vandelli": "diciovandelli.xml",
        "semmedo": "observSemmedo.xml"
    }

    nome_arquivo = mapa_arquivos.get(obra_slug)
    if not nome_arquivo:
        return f"[Obra '{obra_slug}' não mapeada no dicionário de arquivos]"

    # 2. Constrói o caminho correto apontando para corpus_digital/obras_convertidas
    caminho_xml = os.path.join(settings.BASE_DIR, "corpus_digital", "obras_convertidas", nome_arquivo)

    # Debug para você ver no console se o caminho está batendo
    print(f"Tentando abrir: {caminho_xml}")

    if not os.path.exists(caminho_xml):
        return f"[Arquivo não encontrado: {caminho_xml}]"

    # 3. Abre o XML e busca o elemento pelo ID
    try:
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.parse(caminho_xml, parser)
        
        # Definimos o namespace 'xml' explicitamente para o XPath
        ns = {'xml': 'http://www.w3.org/XML/1998/namespace'}
        
        # A consulta XPath agora usa o prefixo 'xml:' que acabamos de definir
        busca_id = f"//*[@xml:id='{xml_id}']"
        elementos = tree.xpath(busca_id, namespaces=ns)

        if elementos:
            # Pega o texto de todo o nó (incluindo o que estiver dentro de <term>, <i>, etc.)
            texto = "".join(elementos[0].itertext()).strip()
            # Limpa espaços e quebras de linha excessivas
            return " ".join(texto.split())
        else:
            return f"[ID {xml_id} não localizado no arquivo {nome_arquivo}]"

    except Exception as e:
        return f"[Erro ao processar XML: {str(e)}]"

# Carregamos os dois grafos (Dicionário e Índice de Exemplos)
G = rdflib.Graph()
G.parse("data/DicionarioBiologia.ttl", format="turtle")
G.parse("data/corpus_index.ttl", format="turtle") # <--- Novo arquivo de índice NIF

def verbete_pelo_turtle(request, lema):
    # 1. Verifique se o grafo carregou (Debug simples)
    if len(G) == 0:
        return HttpResponse("Erro: O arquivo Turtle não foi carregado corretamente.")

    # 2. Monte a URI da entrada usando o lema que vem da URL (que já é um slug)
    # Ex: se a URL é /botanica, vira dicbio:entry_botanica
    uri_entrada = rdflib.URIRef(f"http://dicbio.fflch.usp.br/recurso/entry_{lema}")

    ns = {
        "ontolex": "http://www.w3.org/ns/lemon/ontolex#",
        "skos": "http://www.w3.org/2004/02/skos/core#",
        "etym": "http://lari-datasets.ilc.cnr.it/lemonEty#",
        "lexinfo": "http://www.lexinfo.net/ontology/2.0/lexinfo#",
        "itsrdf": "http://www.w3.org/2005/11/its/rdf#", # <--- Para o link do corpus
        "nif": "http://persistence.uni-leipzig.org/nlp2rdf/ontologies/nif-core#", # <--- Para o corpus
    }

    # QUERY SIMPLIFICADA: Buscamos direto pela URI da entrada
    query = """
    SELECT ?lemmaText ?pos ?definition ?etymComment ?anchor ?contextID WHERE {
        # Usamos a URI da entrada que passamos via bind
        ?entry_uri a ontolex:LexicalEntry .
        
        # Pega o lema original (com acento) para exibir no título
        ?entry_uri ontolex:canonicalForm [ ontolex:writtenRep ?lemmaText ] .
        
        OPTIONAL { ?entry_uri lexinfo:partOfSpeech ?pos . }
        
        ?entry_uri ontolex:sense ?sense .
        OPTIONAL { ?sense skos:definition ?definition . }
        OPTIONAL { ?sense etym:etymology [ rdfs:comment ?etymComment ] . }
        
        OPTIONAL {
            ?occurrence itsrdf:taIdentRef ?sense ;
                        nif:anchorOf ?anchor ;
                        nif:referenceContext ?contextURI .
            BIND(STRAFTER(STR(?contextURI), "recurso/") AS ?contextID)
        }
    }
    """


    results = G.query(query, initNs=ns, initBindings={'entry_uri': uri_entrada})

    verbete_data = {
        'lemma': lema,
        'pos': '',
        'definitions': [], 
        'etymology_list': [],
        'exemplos': [] # Nova lista para os exemplos do Santucci/Vandelli
    }

    for row in results:
        # Preenche POS
        if not verbete_data['pos'] and row.pos:
            verbete_data['pos'] = str(row.pos).split('#')[-1]

        # Adiciona definição (evitando duplicatas)
        if row.definition and str(row.definition) not in verbete_data['definitions']:
            verbete_data['definitions'].append(str(row.definition))

        # Adiciona etimologia
        if row.etymComment and str(row.etymComment) not in verbete_data['etymology_list']:
            verbete_data['etymology_list'].append(str(row.etymComment))

        # Adiciona exemplos do corpus
        if row.anchor:
            xml_id_contexto = str(row.contextID)
            exemplo = {
                'termo': str(row.anchor),
                'xml_id': xml_id_contexto,
                # BUSCA O TEXTO COMPLETO AQUI:
                'contexto_completo': buscar_contexto_no_xml(xml_id_contexto)
            }
            if exemplo not in verbete_data['exemplos']:
                verbete_data['exemplos'].append(exemplo)

    if not verbete_data['definitions'] and not verbete_data['etymology_list']:
        return render(request, 'verbetes/404_verbete.html', {'lema': lema}, status=404)

    return render(request, 'verbetes/verbete_turtle.html', {'verbete': verbete_data})