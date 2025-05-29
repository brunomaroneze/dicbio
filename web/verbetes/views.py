from django.shortcuts import render, get_object_or_404
from .models import Verbete, Definition, OcorrenciaCorpus
from collections import defaultdict

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

    context = {
        'verbete': verbete,
        'definicoes': definicoes,
        'exemplos_por_sense': exemplos_por_sense,
    }
    return render(request, 'verbetes/home.html', context)


def home(request):
    return render(request, 'verbetes/home.html')
