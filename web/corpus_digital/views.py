from django.shortcuts import render, get_object_or_404
from .models import Obra
from lxml import etree
from pathlib import Path
from django.utils.text import slugify
from django.urls import reverse

def home(request, slug=None):
    obras = Obra.objects.all().order_by('autor', 'titulo')
    obra = None
    conteudo_html = None

    if slug:
        obra = get_object_or_404(Obra, slug=slug)
        caminho = Path('web/corpus_digital') / obra.caminho_arquivo
        if caminho.exists():
            tree = etree.parse(str(caminho))
            conteudo_html = converter_tei_para_html(tree)
        else:
            conteudo_html = "<p>Arquivo não encontrado.</p>"

    context = {
        'obras': obras,
        'obra_atual': obra,
        'conteudo_html': conteudo_html
    }

    return render(request, 'corpus_digital/home.html', context)

def converter_tei_para_html(tree):
    ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
    body = tree.find('.//tei:body', namespaces=ns)

    if body is None:
        return "<p>(Sem conteúdo)</p>"

    for term in body.xpath('.//tei:term', namespaces=ns):
        lemma = term.get('lemma') or (term.text or '').strip()
        slug = slugify(lemma)
        a = etree.Element('a', href=reverse('verbetes_detalhe', kwargs={'slug': slug}))
        a.text = term.text or lemma
        term.getparent().replace(term, a)

    return etree.tostring(body, method='html', encoding='unicode')
