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
    Cria <span> com id e classes para os marcadores de página.
    """
    ns_tei_com_chaves = f'{{{ns_tei_url_sem_chaves}}}'

    # --- Processar <tei:titlePage> ---
    title_pages = list(element.xpath(f'.//tei:titlePage', namespaces={'tei': ns_tei_url_sem_chaves}))
    for tp_el in title_pages:
        url_imagem = tp_el.get('facs')
        if url_imagem:
            # Gerar um ID único para o marcador da titlePage (ex: pagina_titlepage_0)
            page_id = f"pagina_titlepage_{tp_el.get('n', '0')}" 
            display_num = tp_el.get('n', 'Título') # Para a legenda

            marcador = etree.Element('span')
            marcador.set('id', page_id)
            marcador.set('class', 'marcador-pagina marcador-titlepage') # ESSENCIAL: 'marcador-pagina' e 'marcador-titlepage'
            marcador.text = f'[Pág. {display_num}] '
            marcador.set('data-facs', url_imagem)
            marcador.set('data-pagina-numero', display_num)

            parent = tp_el.getparent()
            if parent is not None:
                tp_el.addprevious(marcador)


    # --- Processar <tei:pb> (page breaks) ---
    page_breaks = list(element.xpath(f'.//tei:pb', namespaces={'tei': ns_tei_url_sem_chaves}))
    for pb_el in page_breaks:
        num_pagina = pb_el.get('n', '?')
        url_imagem = pb_el.get('facs')

        marcador = etree.Element('span')
        marcador.set('id', f'pagina_{num_pagina}') # ESSENCIAL: id="pagina_N"
        marcador.set('class', 'marcador-pagina')  # ESSENCIAL: class="marcador-pagina"
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
    ns_map = {'tei': 'http://www.tei-c.org/ns/1.0', 'xml': 'http://www.w3.org/XML/1998/namespace'} # Adicionado namespace xml
    tei_ns_url = 'http://www.tei-c.org/ns/1.0'

    text_element = tree.find('.//tei:text', namespaces=ns_map)

    if text_element is None:
        return "<p>(Sem conteúdo na seção TEI <text>)</p>"

    # 1. Transformar tei:term em <a> (e adicionar data-lemma)
    for term_el in text_element.xpath('.//tei:term', namespaces=ns_map):
        lemma = term_el.get('lemma') or (term_el.text or '').strip()
        slug_do_lemma = slugify(lemma)
        token_superficie = term_el.text or lemma

        term_el.tag = 'a'
        try:
            url_consulta = reverse('verbetes:detalhe', args=[slug_do_lemma])
            term_el.set('href', url_consulta)
        except Exception as e:
            # print(f"AVISO: Falha ao gerar URL para o termo '{lemma}' (slug: '{slug_do_lemma}'). Erro: {e}.")
            term_el.set('href', f"/verbetes/{slug_do_lemma}/")

        term_el.text = token_superficie
        if lemma:
            term_el.set('data-lemma', lemma)

        # Limpar atributos TEI específicos de tei:term
        tei_term_attrs_to_remove = ['lemma', 'norm', 'msd', 'senseNumber', 'type', 'ana', 'corresp', 'ref']
        for attr_name in list(term_el.attrib.keys()):
            if attr_name in tei_term_attrs_to_remove:
                del term_el.attrib[attr_name]

    # 2. Chamar a função para substituir/modificar outras tags TEI (pb, titlePage, s, note)
    # Esta função opera em todo o <text>
    substituir_tags_inadequadas(text_element, tei_ns_url)

    # --- NOVO PASSO: Adicionar classe para elementos com xml:lang="la" ---
    # XPath para encontrar qualquer elemento (*) com o atributo xml:lang igual a "la"
    # O namespace 'xml' é predefinido em lxml e geralmente não precisa ser declarado no ns_map para @xml:lang,
    # mas é uma boa prática incluí-lo para clareza e robustez.
    # No entanto, lxml pode tratar @xml:lang diretamente. Vamos testar.
    # Se xpath com @xml:lang não funcionar, usaremos .get('{http://www.w3.org/XML/1998/namespace}lang')
    
    # Tentativa 1: XPath direto (mais limpo se funcionar)
    # Nota: O namespace 'xml' é 'http://www.w3.org/XML/1998/namespace'
    # elementos_latinos = text_element.xpath(".//*[@xml:lang='la']", namespaces=ns_map)
    
    # Tentativa 2: Iterar e verificar o atributo com namespace (mais robusto)
    # O namespace para xml:lang é '{http://www.w3.org/XML/1998/namespace}lang'
    xml_lang_attr_qname = etree.QName(ns_map['xml'], 'lang') # Forma correta de obter o nome qualificado

    for el_latim in text_element.xpath(".//*[attribute::*[local-name()='lang' and namespace-uri()='http://www.w3.org/XML/1998/namespace'] = 'la']", namespaces=ns_map):
    # Alternativa mais simples se a de cima for complexa de ler: iterar e checar
    # for el_latim in text_element.iter('*'):
    #    if el_latim.get(xml_lang_attr_qname) == 'la':
        
        # Adiciona a classe CSS
        classes_existentes = el_latim.get('class')
        if classes_existentes:
            if 'texto-latim' not in classes_existentes.split():
                el_latim.set('class', classes_existentes + ' texto-latim')
        else:
            el_latim.set('class', 'texto-latim')
        
        # Opcional: transferir xml:lang para lang no HTML ou remover xml:lang
        # Para manter o atributo lang no HTML:
        el_latim.set('lang', 'la') # Adiciona o atributo lang="la" padrão do HTML
        if xml_lang_attr_qname in el_latim.attrib:
             del el_latim.attrib[xml_lang_attr_qname] # Remove o xml:lang original
    # --------------------------------------------------------------------

# --- NOVO PASSO: Processar tags <g> com referências ---
    # Este loop deve rodar ANTES da limpeza final de namespaces TEI,
    # mas depois que outras transformações de tag já aconteceram.

    # Primeiro, vamos construir um mapa das definições de caracteres do <charDecl>
    char_map = {}
    for char_el in tree.xpath('.//tei:charDecl/tei:char', namespaces=ns_map):
        char_id = char_el.get('{http://www.w3.org/XML/1998/namespace}id')
        if char_id:
            mapping_el = char_el.find('tei:mapping[@type="unicode"]', namespaces=ns_map)
            desc_el = char_el.find('tei:desc', namespaces=ns_map)
            unicode_val = mapping_el.text.replace('U+', '') if mapping_el is not None and mapping_el.text else None
            desc_val = desc_el.text if desc_el is not None and desc_el.text else char_id
            char_map[f"#{char_id}"] = {'unicode': unicode_val, 'desc': desc_val}

    # Agora, encontre todas as tags <g> com um atributo ref e processe-as
    for g_el in text_element.xpath('.//tei:g[@ref]', namespaces=ns_map):
        ref = g_el.get('ref')
        
        # Opcional: manter o texto original do <g> se houver, para fallback
        # original_text = g_el.text or ""
        
        # Substituir por uma Entidade Numérica HTML
        if ref in char_map and char_map[ref]['unicode']:
            unicode_hex = char_map[ref]['unicode']
            html_entity = f"&#x{unicode_hex};" # Ex: 톗
            
            # Criar um novo elemento <span> para conter a entidade
            # Usar etree.fromstring para parsear a entidade corretamente.
            # O texto da tag será a entidade, que os navegadores renderizarão como o símbolo.
            # Para que o lxml não escape a entidade, precisamos de um truque.
            # Vamos criar um span e definir seu 'tail' para a entidade,
            # então o nó <g> vazio será substituído pelo span, e o tail será inserido.
            
            span_substituto = etree.Element('span')
            span_substituto.set('class', 'special-char') # Para estilização opcional
            span_substituto.set('title', char_map[ref]['desc']) # Tooltip com a descrição
            
            # Adicionar a entidade como 'tail' do elemento que vem ANTES de <g>
            # ou como 'text' do elemento PAI se for o primeiro filho.
            # A forma mais segura é substituir <g> por um nó de texto contendo a entidade.
            # Mas lxml escapa o '&'. A solução é usar um nó de comentário e depois
            # substituir na string final.
            placeholder = f"__CHAR_ENTITY_{unicode_hex}__"
            g_el.tag = 'span' # Transforma <g> em <span>
            g_el.text = placeholder
            g_el.set('class', 'special-char')
            g_el.set('title', char_map[ref]['desc'])
            # Limpar atributos antigos
            del g_el.attrib['ref']
     
        # --------------------------------------------------


    # 3. Limpeza final de namespaces TEI (manter namespaces de outros como HTML 'lang')
    for el in text_element.iter('*'):
        # Remover namespace TEI da tag
        if el.tag.startswith(f'{{{tei_ns_url}}}'):
            el.tag = el.tag.split('}', 1)[1]
        
        # Remover atributos com namespace TEI
        # Mas preservar atributos de outros namespaces como o 'xml' (que se torna 'lang' no HTML)
        # ou atributos sem namespace (como 'class', 'id', 'href', 'data-lemma', 'lang' que acabamos de adicionar)
        for attr_qname_str in list(el.attrib.keys()):
            if attr_qname_str.startswith(f'{{{tei_ns_url}}}'): # Se for um atributo TEI
                del el.attrib[attr_qname_str]
            # Se for um atributo xml:*, como xml:id, e você quiser mantê-lo como id,
            # uma lógica similar à de xml:lang pode ser necessária.
            # Por agora, o xml:lang foi tratado acima e convertido para 'lang'.


    html_string = etree.tostring(text_element, method='html', encoding='unicode', pretty_print=True)

    # Passo final para substituir os placeholders de entidades por entidades reais
    for ref_id, char_data in char_map.items():
        if char_data['unicode']:
            placeholder = f"__CHAR_ENTITY_{char_data['unicode']}__"
            html_entity = f"&#x{char_data['unicode']};"
            html_string = html_string.replace(placeholder, html_entity)
            
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