from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from corpus_digital.models import Obra
from lxml import etree
from pathlib import Path
from django.utils.text import slugify
from django.urls import reverse

def substituir_tags_inadequadas(element, ns_tei_url_sem_chaves):
    """
    Substitui tags TEI por equivalentes HTML adequados e processa <pb> e <titlePage>.
    'element' é o elemento raiz a ser processado (agora pode ser <text>).
    'ns_tei_url_sem_chaves' é a string do namespace TEI, ex: 'http://www.tei-c.org/ns/1.0'.
    """
    ns_tei_com_chaves = f'{{{ns_tei_url_sem_chaves}}}'

    # --- NOVO BLOCO: Processar <tei:titlePage> para extrair imagem e criar marcador ---
    title_pages = list(element.xpath(f'.//tei:titlePage', namespaces={'tei': ns_tei_url_sem_chaves}))
    for tp_el in title_pages:
        url_imagem = tp_el.get('facs') # Pega o atributo facs da titlePage
        if url_imagem:
            # Gerar um ID único para o marcador. 'titlePage' é um bom descritivo
            # Podemos tentar pegar 'n' se existir na titlePage, ou usar um nome fixo
            page_id = f"pagina_titlepage_{tp_el.get('n', '0')}" # Adiciona 'n' se existir, ou '0'
            display_num = tp_el.get('n', 'Título') # Para exibir na legenda, usa 'n' ou 'Título'

            marcador = etree.Element('span')
            marcador.set('id', page_id)
            marcador.set('class', 'marcador-pagina marcador-titlepage') # Adiciona uma classe específica para estilizar
            marcador.text = f'[Pág. {display_num}] ' # Texto que aparece no documento
            marcador.set('data-facs', url_imagem)
            marcador.set('data-pagina-numero', display_num)

            # Inserir o marcador ANTES do elemento <titlePage> no HTML
            # Isso faz com que a imagem apareça antes do texto da página de título.
            parent = tp_el.getparent()
            if parent is not None:
                tp_el.addprevious(marcador)

        # Opcional: Transformar <titlePage> em um <div> comum e adicionar uma classe para estilização
        # (se você quiser que o texto da titlePage tenha um estilo específico no HTML)
        # tp_el.tag = 'div'
        # tp_el.set('class', 'tei-titlepage-content')


    # Processar <pb> (page breaks)
    # A lógica existente para <pb> permanece a mesma e pode vir aqui ou antes, dependendo da ordem desejada
    # para os marcadores de página. Geralmente, não há sobreposição de lógica entre titlePage e pb.
    page_breaks = list(element.xpath(f'.//tei:pb', namespaces={'tei': ns_tei_url_sem_chaves}))
    for pb_el in page_breaks:
        num_pagina = pb_el.get('n', '?')
        url_imagem = pb_el.get('facs')

        marcador = etree.Element('span')
        marcador.set('id', f'pagina_{num_pagina}')
        marcador.set('class', 'marcador-pagina') # Para JS e estilo
        marcador.text = f'[p. {num_pagina}] '
        if url_imagem:
            marcador.set('data-facs', url_imagem)
        if num_pagina and num_pagina != '?':
            marcador.set('data-pagina-numero', num_pagina)

        if pb_el.tail:
            marcador.tail = pb_el.tail
            pb_el.tail = None

        parent = pb_el.getparent()
        if parent is not None:
            parent.replace(pb_el, marcador)

    # Agora iterar sobre todos os elementos para outras substituições (s, note)
    # Esta iteração é mais genérica e pega elementos já transformados também.
    for el in element.iter(): 
        tag = el.tag 

        if tag == f'{ns_tei_com_chaves}s':
            el.tag = 'span'

        elif tag == f'{ns_tei_com_chaves}note':
            el.tag = 'div'
            el.set('class', 'nota-tei') 

        # Adicione mais cláusulas 'elif' aqui para outras tags TEI se precisar de transformações.
        # Por exemplo, se quiser que <front> e <back> se tornem <div>s:
        # elif tag == f'{ns_tei_com_chaves}front':
        #     el.tag = 'div'
        #     el.set('class', 'tei-front')
        # elif tag == f'{ns_tei_com_chaves}back':
        #     el.tag = 'div'
        #     el.set('class', 'tei-back')


# Função principal de conversão TEI para HTML
def converter_tei_para_html_para_comando(tree):
    ns_map = {'tei': 'http://www.tei-c.org/ns/1.0'}
    tei_ns_url = 'http://www.tei-c.org/ns/1.0'

    text_element = tree.find('.//tei:text', namespaces=ns_map)

    if text_element is None:
        return "<p>(Sem conteúdo na seção TEI <text>)</p>"

    # 1. Transformar tei:term em <a>
    for term_el in text_element.xpath('.//tei:term', namespaces=ns_map):
        lemma = term_el.get('lemma') or (term_el.text or '').strip()
        slug = slugify(lemma)
        token = term_el.text or lemma

        term_el.tag = 'a'
        try:
            url_consulta = reverse('verbetes:detalhe', args=[slug])
            term_el.set('href', url_consulta)
        except Exception as e:
            print(f"AVISO: Falha ao gerar URL para o termo '{lemma}' (slug: '{slug}'). Erro: {e}. Usando caminho relativo hardcoded.")
            term_el.set('href', f"/consulta/{slug}/")

        term_el.text = token
        for attr_name in list(term_el.attrib.keys()):
            if attr_name not in ['href', 'class', 'id', 'style', 'title']:
                if attr_name in ['lemma', 'norm', 'msd', 'senseNumber', 'type', 'ana', 'corresp', 'ref']:
                    del term_el.attrib[attr_name]


    # 2. Chamar a função para substituir/modificar outras tags TEI
    # Esta função agora opera em todo o <text> e processa titlePage, pb, s, note
    substituir_tags_inadequadas(text_element, tei_ns_url)


    # 3. Limpeza final de namespaces
    for el in text_element.iter('*'):
        if '}' in el.tag:
            el.tag = el.tag.split('}', 1)[1]
        for attr_name_ns in list(el.attrib.keys()):
            if '}' in attr_name_ns:
                local_attr_name = attr_name_ns.split('}', 1)[1]
                el.attrib[local_attr_name] = el.attrib.pop(attr_name_ns)

    html_string = etree.tostring(text_element, method='html', encoding='unicode', pretty_print=True)
    return html_string


class Command(BaseCommand):
    help = 'Converte os arquivos TEI-XML das obras para HTML e salva no banco de dados.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--slug',
            type=str,
            help='Processa apenas a obra com o slug especificado.',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Força o reprocessamento mesmo que já exista HTML.',
        )

    def handle(self, *args, **options):
        slug_especifico = options['slug']
        forcar_reprocessamento = options['force']

        obras_a_processar = Obra.objects.all()
        if slug_especifico:
            try:
                obras_a_processar = Obra.objects.filter(slug=slug_especifico)
                if not obras_a_processar.exists():
                    raise CommandError(f'Obra com slug "{slug_especifico}" não encontrada.')
            except Obra.DoesNotExist:
                raise CommandError(f'Obra com slug "{slug_especifico}" não encontrada.')

        if not obras_a_processar.exists() and not slug_especifico:
             self.stdout.write(self.style.WARNING('Nenhuma obra encontrada para processar.'))
             return

        self.stdout.write(self.style.SUCCESS(f'Iniciando processamento de {obras_a_processar.count()} obra(s)...'))

        for obra in obras_a_processar:
            self.stdout.write(f'Processando: {obra.titulo} (Slug: {obra.slug})')

            if obra.conteudo_html_processado and not forcar_reprocessamento:
                self.stdout.write(self.style.NOTICE(f'  HTML já existe para "{obra.titulo}". Use --force para reprocessar.'))
                continue

            if not obra.caminho_arquivo:
                self.stderr.write(self.style.ERROR(f'  Campo "caminho_arquivo" não definido para a obra "{obra.titulo}"'))
                continue

            caminho_xml_completo = settings.CORPUS_XML_ROOT / obra.caminho_arquivo

            if not caminho_xml_completo.exists():
                self.stderr.write(self.style.ERROR(f'  Arquivo XML não encontrado para "{obra.titulo}" em: {caminho_xml_completo}'))
                self.stderr.write(self.style.NOTICE(f'  Verifique se CORPUS_XML_ROOT em settings.py ({settings.CORPUS_XML_ROOT}) está correto e se obra.caminho_arquivo ("{obra.caminho_arquivo}") está correto.'))
                continue

            try:
                tree = etree.parse(str(caminho_xml_completo))
                html_content = converter_tei_para_html_para_comando(tree)

                obra.conteudo_html_processado = html_content
                obra.save()
                self.stdout.write(self.style.SUCCESS(f'  HTML gerado e salvo para "{obra.titulo}"'))

            except etree.ParseError as e:
                self.stderr.write(self.style.ERROR(f'  Erro ao parsear XML para "{obra.titulo}": {e}'))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f'  Erro inesperado ao processar "{obra.titulo}": {e}'))
                import traceback
                traceback.print_exc()


        self.stdout.write(self.style.SUCCESS('Processamento concluído.'))