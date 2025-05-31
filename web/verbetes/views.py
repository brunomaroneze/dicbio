from django.shortcuts import render, get_object_or_404, redirect
from .models import Verbete, Definition, OcorrenciaCorpus
from collections import defaultdict
from django.utils.timezone import now
import unicodedata

def remover_acentos(texto):
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    ).lower()

def verbete_detalhe(request, slug):
    verbete = get_object_or_404(Verbete, slug=slug)
    definicoes = Definition.objects.filter(verbete=verbete).order_by('sensenumber')
    ocorrencias = OcorrenciaCorpus.objects.filter(verbete=verbete)

    exemplos_tmp = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    # Preencher estrutura com dados do banco
    for o in ocorrencias:
        sense = o.definicao.sensenumber if o.definicao else '0'
        gram = o.gram.strip()
        autor = o.autor.strip().upper()
        exemplos_tmp[str(sense)][gram][autor].append({
            'token': o.token,
            'gram': gram,
            'sentence': o.frase,
            'autor': autor,
        })

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
            return redirect('verbetes_detalhe', slug=verbete.slug)
        except Verbete.DoesNotExist:
            verbete = None
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
    })