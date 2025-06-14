from django.shortcuts import render, get_object_or_404, redirect
from .models import Verbete, Definition, OcorrenciaCorpus
from collections import defaultdict
from django.utils.timezone import now
import unicodedata
from django.urls import reverse
from django.db.models import Prefetch

def remover_acentos(texto):
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    ).lower()

def verbete_detalhe(request, slug):
    verbete = get_object_or_404(Verbete, slug=slug)
    # Prefetch das definições para otimizar, como antes
    definicoes = Definition.objects.filter(verbete=verbete).order_by('sensenumber').prefetch_related(
        # Prefetch das ocorrências ligadas a cada definição (se a definição tiver um related_name para ocorrencias)
        # Se você precisa que 'o.definicao' seja carregado para acessar 'sensenumber' de forma otimizada
        Prefetch('ocorrencias', queryset=OcorrenciaCorpus.objects.all(), to_attr='ocorrencias_carregadas')
    )

    # NOVO: Para otimizar a busca das ocorrências, especialmente se a definição não for encontrada
    # Prefetch todas as ocorrências de uma vez, mas filtrando pelo verbete
    ocorrencias = OcorrenciaCorpus.objects.filter(verbete=verbete).select_related('definicao') # Usa select_related para a definicao

    exemplos_tmp = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    # Preencher estrutura com dados do banco
    for o in ocorrencias:
        # PROBLEMA POTENCIAL AQUI: Se a definição estiver nula para a ocorrência, ou o.definicao.sensenumber não existir.
        # Definicao pode ser None se definicao=models.ForeignKey(..., null=True, blank=True)
        # E se o.definicao é None, o acesso o.definicao.sensenumber vai falhar.
        sense = o.definicao.sensenumber if o.definicao else '0' # Trata o caso de definicao ser None

        # Certifique-se que 'gram' e 'autor' não são strings vazias que causem problemas de chave
        gram = o.gram.strip() or 'N/A' # Fallback se gram for vazio
        autor = o.autor.strip().upper() or 'N/A' # Fallback se autor for vazio

        exemplo = {
           'token': o.token,
            'gram': gram,
            'frase': o.frase, # NOME DA CHAVE NO MODELO E NO CSV É 'frase', NÃO 'sentence'
            'autor': autor,
            'data': o.data,
            'titulo_obra': o.titulo_obra,
            'slug_obra': o.slug_obra,
            'pagina_obra': o.pagina_obra,
        }

        # Usamos a chave do sentido e da gramática para selecionar exemplos
        grupo = exemplos_tmp[str(sense)][gram][autor]

        # Substitui o exemplo anterior se este for mais adequado (lógica existente)
        tam = len(o.frase) # Usa 'o.frase'
        if 100 <= tam <= 300:
            grupo.insert(0, exemplo)
        else:
            grupo.append(exemplo)


    # Agora convertemos exemplos_tmp para dict normal (para o template)
    exemplos_por_sense = {
        sense: {
            gram: dict(autores)
            for gram, autores in gram_dict.items()
        }
        for sense, gram_dict in exemplos_tmp.items()
    }

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


def home(request):
    termo_busca = request.GET.get('q', '').strip()
    lista_verbetes = sorted(
        Verbete.objects.all(),
        key=lambda v: remover_acentos(v.termo)
    )

    if termo_busca:
        try:
            verbete = Verbete.objects.get(termo__iexact=termo_busca)
            return redirect('verbetes:detalhe', slug=verbete.slug)
        except Verbete.DoesNotExist:
            verbete = None
            mensagem_busca = f"Nenhum verbete encontrado para '{termo_busca}'."
            definicoes = []
            exemplos_por_sense = {}
    else:
        verbete = None
        definicoes = []
        exemplos_por_sense = {}

    return render(request, 'verbetes/home.html', {
        'verbete': verbete,
        'definicoes': definicoes,
        'exemplos_por_sense': exemplos_por_sense,
        'lista_verbetes': lista_verbetes,
        'mensagem_busca': mensagem_busca if 'mensagem_busca' in locals() else None,
    })