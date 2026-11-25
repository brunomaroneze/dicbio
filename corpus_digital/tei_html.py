"""Converte uma obra TEI em HTML.

Um <p> que contenha nota ou outro bloco vira <div class="tei-p">: o navegador
fecha o <p> ao encontrar um <div> dentro dele.
"""
import sys
from pathlib import Path

from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify
from lxml import etree

sys.path.append(str(settings.BASE_DIR / 'revisao'))
from nucleo import paginas  # noqa: E402  (identificadores das imagens da conferência)

TEI = '{http://www.tei-c.org/ns/1.0}'
XML_ID = '{http://www.w3.org/XML/1998/namespace}id'
XML_LANG = '{http://www.w3.org/XML/1998/namespace}lang'

MAPA = {
    'text': 'div', 'front': 'div', 'body': 'div', 'back': 'div', 'div': 'div',
    'p': 'p', 's': 'span', 'note': 'div', 'a': 'a',
    'item': 'li', 'table': 'table', 'row': 'tr', 'cell': 'td',
    'lg': 'div', 'l': 'div',
    'entry': 'div', 'form': 'span', 'sense': 'span', 'dictScrap': 'span',
    'titlePage': 'div', 'docTitle': 'div', 'titlePart': 'div', 'byline': 'div',
    'docImprint': 'div', 'epigraph': 'blockquote', 'salute': 'div',
    'signed': 'div', 'closer': 'div', 'trailer': 'div',
}  # os demais elementos viram <span>
CLASSE_FIXA = {'s': 'tei-sentence', 'note': 'nota-tei',
               'titlePage': 'title-page-content', 'a': 'tei-term-link'}
BLOCOS = {'div', 'p', 'ul', 'li', 'table', 'blockquote', 'h3', 'h4', 'h5', 'h6'}


def nome(el):
    return el.tag.rsplit('}', 1)[-1]


def imagens(caminho_xml):
    """Endereço da imagem de cada <pb>, na ordem do texto.

    Imagens locais e cópias feitas por revisao/baixar_imagens.py são servidas pelo
    próprio site; sem cópia, fica o endereço original.
    """
    with open(caminho_xml, encoding='utf-8', newline='') as f:
        lista = paginas(f.read())
    raiz, obra = Path(settings.IMAGENS_ROOT), Path(caminho_xml).stem
    urls = []
    for p in lista:
        if p.n in ('folha de rosto', 'sem indicação'):  # não vêm de um <pb>
            continue
        url = p.facs
        if url.startswith(('http://', 'https://')):
            copia = f'{obra}_imagens/{p.id}.jpg'
            if (raiz / copia).exists():
                url = settings.IMAGENS_URL + copia
        elif url:
            url = settings.IMAGENS_URL + url
        urls.append(url)
    return urls


def marca_pagina(pb, url):
    n = pb.get('n', '?')
    caixa = etree.Element('span', {'class': 'page-break-indicator'})
    etree.SubElement(caixa, 'span', {'class': 'page-separator'})
    marca = etree.SubElement(caixa, 'span', {
        'id': pb.get(XML_ID) or 'pagina_' + n.replace(' ', '_'),
        'class': 'marcador-pagina', 'data-pagina-numero': n})
    if url:
        marca.set('data-facs', url)
    marca.text = f'[p. {n}] '
    pai = nome(pb.getparent())
    if pai == 'list':
        fora = etree.Element('li', {'class': 'quebra-pagina'})
        fora.append(caixa)
    elif pai == 'table':
        fora = etree.Element('tr', {'class': 'quebra-pagina'})
        etree.SubElement(fora, 'td', {'colspan': '99'}).append(caixa)
    else:
        fora = caixa
    fora.tail = pb.tail
    pb.tail = None
    pb.getparent().replace(pb, fora)


def slug_do_termo(term):
    ref = term.get('ref')
    if ref:
        return ref.split('/')[-1].replace('entry_', '').split('_sense')[0]
    return slugify(term.get('lemma') or (term.text or '').strip())


def converter(caminho_xml, slugs_verbetes):
    arvore = etree.parse(str(caminho_xml))
    etree.strip_tags(arvore, etree.Comment, etree.ProcessingInstruction)
    texto = arvore.find(f'.//{TEI}text')
    if texto is None:
        return '<p>(Sem conteúdo na seção TEI text)</p>'

    pbs, urls = list(texto.iter(f'{TEI}pb')), imagens(caminho_xml)
    if len(pbs) != len(urls):
        raise ValueError(f'{len(pbs)} quebras de página, mas {len(urls)} imagens')
    for pb, url in zip(pbs, urls):
        marca_pagina(pb, url)

    # Só há link quando o verbete existe.
    for term in list(texto.iter(f'{TEI}term')):
        slug = slug_do_termo(term)
        if slug in slugs_verbetes:
            term.tag = f'{TEI}a'
            term.set('href', reverse('verbetes:detalhe', args=[slug]))

    # Títulos: o nível depende de quantos <div> os contêm.
    for head in list(texto.iter(f'{TEI}head')):
        pai = nome(head.getparent())
        if pai == 'list':
            head.tag = 'div'
        elif pai == 'table':
            head.tag = 'caption'
        else:
            nivel = sum(1 for _ in head.iterancestors(f'{TEI}div'))
            head.tag = f'h{min(6, 2 + max(1, nivel))}'
        for a in list(head.attrib):
            if a != XML_ID:
                del head.attrib[a]
        head.set('class', 'tei-head')

    # <list>: o título fica fora do <ul>.
    for lista in list(texto.iter(f'{TEI}list')):
        tipo, lid = lista.get('type'), lista.get(XML_ID)
        ul = etree.Element('ul', {'class': 'tei-list'})
        ul.text = '\n'
        for filho in list(lista):
            if not (filho.tag == 'div' and filho.get('class') == 'tei-head'):
                ul.append(filho)
        lista.append(ul)
        lista.tag = 'div'
        lista.attrib.clear()
        lista.set('class', f'tei-lista tei-lista-{slugify(tipo)}' if tipo else 'tei-lista')
        if lid:
            lista.set('id', lid)

    for el in list(texto.iter(etree.Element)):
        if not el.tag.startswith(TEI):
            if XML_ID in el.attrib:
                el.set('id', el.attrib.pop(XML_ID))
            continue
        n, attrs = nome(el), dict(el.attrib)
        el.attrib.clear()
        el.tag = MAPA.get(n, 'span')
        if n == 'row' and attrs.get('role'):
            el.set('data-role', attrs['role'])
        if n == 'cell':
            if 'label' in (attrs.get('role'), el.getparent().get('data-role')):
                el.tag = 'th'
            for a, b in (('rows', 'rowspan'), ('cols', 'colspan')):
                if attrs.get(a):
                    el.set(b, attrs[a])
        el.set('class', CLASSE_FIXA.get(n, f'tei-{n}'))
        if XML_ID in attrs:
            el.set('id', attrs[XML_ID])
        if XML_LANG in attrs:
            el.set('lang', {'lat': 'la'}.get(attrs[XML_LANG], attrs[XML_LANG]))
        if 'href' in attrs:
            el.set('href', attrs['href'])

    for p in list(texto.iter('p')):
        if any(d is not p and d.tag in BLOCOS for d in p.iter(etree.Element)):
            p.tag = 'div'
    etree.cleanup_namespaces(texto)
    # Sem pretty_print, que poderia inserir espaços no texto.
    return etree.tostring(texto, method='html', encoding='unicode', with_tail=False)
