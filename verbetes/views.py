# verbetes/views.py

from django.shortcuts import render, get_object_or_404, redirect
from .models import Verbete, Definition, OcorrenciaCorpus
from django.db.models import Prefetch, Q # Importar Q para buscas complexas
from django.urls import reverse
from collections import defaultdict
from django.utils.timezone import now
import unicodedata
from django.contrib import messages

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