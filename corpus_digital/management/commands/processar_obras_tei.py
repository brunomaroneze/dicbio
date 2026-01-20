from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from corpus_digital.models import Obra
from lxml import etree
from pathlib import Path
from django.utils.text import slugify
from django.urls import reverse

# --- FUNÇÕES AUXILIARES DE CONVERSÃO ---

def substituir_tags_inadequadas(element, ns_tei_url_sem_chaves):
    """
    Substitui tags TEI por HTML e preserva os IDs para ancoragem.
    """
    ns_tei_com_chaves = f'{{{ns_tei_url_sem_chaves}}}'
    ns_map = {'tei': ns_tei_url_sem_chaves, 'xml': 'http://www.w3.org/XML/1998/namespace'}
    xml_id_qname = etree.QName(ns_map['xml'], 'id')

    # 1. Mapear xml:id para id HTML em todos os elementos (p, s, head, etc.)
    # Isso permite que o link do dicionário "pouse" no lugar certo.
    for el in element.xpath(".//*[@xml:id]", namespaces=ns_map):
        valor_id = el.get(xml_id_qname)
        el.set('id', valor_id)

    # 2. Divisão de parágrafos <p> que contêm quebras <pb>
    while element.xpath('.//tei:p/tei:pb', namespaces=ns_map):
        pb_in_p = element.xpath('.//tei:p/tei:pb', namespaces=ns_map)[0]
        p_parent = pb_in_p.getparent()
        new_p = etree.Element(p_parent.tag, attrib=p_parent.attrib)
        if 'id' in new_p.attrib:
            new_p.set('id', f"{new_p.get('id')}_cont")
        new_p.text = pb_in_p.tail
        pb_in_p.tail = None
        siblings_to_move = list(pb_in_p.itersiblings())
        for sibling in siblings_to_move:
            new_p.append(sibling)
        p_parent.addnext(new_p)
        p_parent.addnext(pb_in_p)

    # 3. Processar <pb> (page breaks)
    page_breaks = list(element.xpath(f'.//tei:pb', namespaces=ns_map))
    for pb_el in page_breaks:
        num_pagina = pb_el.get('n', '?')
        url_imagem = pb_el.get('facs')
        marcador_container = etree.Element('div')
        marcador_container.set('class', 'page-break-indicator')
        etree.SubElement(marcador_container, 'hr', attrib={'class': 'page-separator'})
        
        marcador_span = etree.SubElement(marcador_container, 'span')
        # Preserva o ID do pb se houver, ou cria um de página
        pid = pb_el.get(xml_id_qname) or f'pagina_{num_pagina.replace(" ", "_")}'
        marcador_span.set('id', pid)
        marcador_span.set('class', 'marcador-pagina')
        marcador_span.text = f'[p. {num_pagina}] '
        
        if pb_el.tail:
            marcador_container.tail = pb_el.tail
            pb_el.tail = None
        
        parent = pb_el.getparent()
        if parent is not None:
            parent.replace(pb_el, marcador_container)

    # 4. Substituição de outras tags
    for el in element.iter():
        tag = el.tag
        if tag == f'{ns_tei_com_chaves}s':
            el.tag = 'span'
            el.set('class', 'tei-sentence')
        elif tag == f'{ns_tei_com_chaves}note':
            el.tag = 'div'
            el.set('class', 'nota-tei')
        elif tag == f'{ns_tei_com_chaves}titlePage':
            el.tag = 'div'
            el.set('class', 'title-page-content')


def converter_tei_para_html_para_comando(tree):
    ns_map = {'tei': 'http://www.tei-c.org/ns/1.0', 'xml': 'http://www.w3.org/XML/1998/namespace'}
    tei_ns_url = 'http://www.tei-c.org/ns/1.0'
    xml_id_qname = etree.QName(ns_map['xml'], 'id')

    text_element = tree.find('.//tei:text', namespaces=ns_map)
    if text_element is None:
        return "<p>(Sem conteúdo na seção TEI <text>)</p>"

    # 1. Transformar tei:term em <a> e apontar para o dicionário
    for term_el in text_element.xpath('.//tei:term', namespaces=ns_map):
        t_id = term_el.get(xml_id_qname)
        
        # Lógica de link: tenta usar ref, senão usa o lemma slugificado
        ref = term_el.get('ref')
        if ref:
            # Extrai o lema da URI (ex: http.../entry_botanica_sense1 -> botanica)
            slug_do_lemma = ref.split('/')[-1].replace('entry_', '').split('_sense')[0]
        else:
            lemma = term_el.get('lemma') or (term_el.text or '').strip()
            slug_do_lemma = slugify(lemma)

        term_el.tag = 'a'
        term_el.set('class', 'tei-term-link')
        if t_id: term_el.set('id', t_id) # Preserva o ID no HTML
        
        try:
            # Tenta gerar a URL usando o reverse do Django
            # Ajuste 'verbetes:verbete_pelo_turtle' conforme o nome na sua urls.py
            url_consulta = reverse('verbetes:verbete_pelo_turtle', args=[slug_do_lemma])
            term_el.set('href', url_consulta)
        except:
            term_el.set('href', f"/consulta/{slug_do_lemma}/")

        # Limpeza de atributos internos do TEI
        for attr in ['lemma', 'norm', 'msd', 'senseNumber', 'ana', 'corresp', 'ref']:
            if attr in term_el.attrib: del term_el.attrib[attr]

    # 2. Processar outras tags e IDs
    substituir_tags_inadequadas(text_element, tei_ns_url)

    # 3. Limpeza final de namespaces
    for el in text_element.iter('*'):
        if el.tag.startswith(f'{{{tei_ns_url}}}'):
            el.tag = el.tag.split('}', 1)[1]
        for attr_qname in list(el.attrib.keys()):
            if attr_qname.startswith(f'{{{tei_ns_url}}}'):
                del el.attrib[attr_qname]
            elif attr_qname == xml_id_qname:
                if 'id' not in el.attrib: el.set('id', el.attrib[attr_qname])
                del el.attrib[attr_qname]

    return etree.tostring(text_element, method='html', encoding='unicode', pretty_print=True)

# --- CLASSE DO COMANDO DJANGO ---

class Command(BaseCommand):
    help = 'Converte os arquivos TEI-XML das obras para HTML e salva no banco de dados.'

    def add_arguments(self, parser):
        parser.add_argument('--slug', type=str, help='Processa apenas uma obra.')
        parser.add_argument('--force', action='store_true', help='Força reprocessamento.')

    def handle(self, *args, **options):
        slug_especifico = options['slug']
        forcar = options['force']

        obras = Obra.objects.all()
        if slug_especifico:
            obras = obras.filter(slug=slug_especifico)

        if not obras.exists():
            self.stdout.write(self.style.WARNING('Nenhuma obra para processar.'))
            return

        for obra in obras:
            self.stdout.write(f'Processando: {obra.titulo}')

            if obra.conteudo_html_processado and not forcar:
                self.stdout.write(self.style.NOTICE(f'  Ignorando {obra.titulo}.'))
                continue

            # Supõe que CORPUS_XML_ROOT está em settings.py apontando para a pasta raiz dos XMLs
            caminho_xml = settings.BASE_DIR / "corpus_digital" / "obras" / obra.caminho_arquivo

            if not caminho_xml.exists():
                self.stderr.write(self.style.ERROR(f'  Arquivo não encontrado: {caminho_xml}'))
                continue

            try:
                tree = etree.parse(str(caminho_xml))
                html_content = converter_tei_para_html_para_comando(tree)
                obra.conteudo_html_processado = html_content
                obra.save()
                self.stdout.write(self.style.SUCCESS(f'  Sucesso!'))

            except Exception as e:
                self.stderr.write(self.style.ERROR(f'  Erro em {obra.titulo}: {e}'))

        self.stdout.write(self.style.SUCCESS('Concluído.'))