from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from corpus_digital.models import Obra
from lxml import etree
from pathlib import Path # Path não é mais estritamente necessário aqui se settings.CORPUS_XML_ROOT é usado e já é Path
from django.utils.text import slugify
from django.urls import reverse # Para gerar URLs para os termos

# Função para substituir tags TEI problemáticas ou que precisam de mapeamento específico
def substituir_tags_inadequadas(element, ns_tei_url_sem_chaves):
    """
    Substitui tags TEI por equivalentes HTML adequados e processa <pb>.
    'element' é geralmente o elemento <body> do TEI.
    'ns_tei_url_sem_chaves' é a string do namespace TEI, ex: 'http://www.tei-c.org/ns/1.0'.
    """
    ns_tei_com_chaves = f'{{{ns_tei_url_sem_chaves}}}' # Namespace formatado para comparação de tag

    # Processar <pb> primeiro (transforma em span com data-attributes)
    # É bom fazer isso antes da iteração geral para que 'iter()' já veja os spans modificados
    # ou, se a ordem não importar criticamente com as outras tags, pode ser dentro do loop geral.
    # A abordagem de iterar separadamente para <pb> é mais limpa.
    page_breaks = list(element.xpath(f'.//tei:pb', namespaces={'tei': ns_tei_url_sem_chaves}))
    for pb_el in page_breaks:
        num_pagina = pb_el.get('n', '?')
        url_imagem = pb_el.get('facs')

        marcador = etree.Element('span') # Será o nosso novo elemento (não mais um 'pb' TEI)
        marcador.set('id', f'pagina_{num_pagina}')
        marcador.set('class', 'marcador-pagina') # Para JS e estilo
        marcador.text = f'[p. {num_pagina}] '   # Conteúdo textual do marcador

        if url_imagem:
            marcador.set('data-facs', url_imagem)
        if num_pagina and num_pagina != '?':
            marcador.set('data-pagina-numero', num_pagina)

        # Preservar o 'tail'
        if pb_el.tail:
            marcador.tail = pb_el.tail
            pb_el.tail = None # Limpa o tail do original

        parent = pb_el.getparent()
        if parent is not None:
            parent.replace(pb_el, marcador)

    # Agora iterar sobre todos os elementos (incluindo os novos spans de <pb>)
    # para outras substituições
    for el in element.iter(): # Itera sobre 'element' (o body) e todos os seus descendentes
        tag = el.tag # el.tag já vem com o namespace completo se o XML tiver namespaces

        # Se o elemento já foi modificado (ex: <pb> para <span>) e não tem mais namespace,
        # ou se queremos apenas processar elementos TEI, podemos verificar o namespace.
        # No entanto, para <s> e <note>, é provável que ainda sejam TEI neste ponto.

        if tag == f'{ns_tei_com_chaves}s': # Verifica se é um <tei:s>
            el.tag = 'span' # Muda para <span>. Pode-se adicionar classes se necessário.
                            # Se 's' em TEI tiver um significado específico que você queira preservar
                            # com uma classe, adicione-a: el.set('class', 'tei-s')

        elif tag == f'{ns_tei_com_chaves}note': # Verifica se é um <tei:note>
            el.tag = 'div'
            el.set('class', 'nota-tei') 

        # Você pode adicionar mais cláusulas 'elif' aqui para outras tags TEI
        # elif tag == f'{ns_tei_com_chaves}outraTagTEI':
        #     el.tag = 'novaTagHTML'
        #     el.set('class', 'classe-para-outra-tag')


# Função principal de conversão TEI para HTML
def converter_tei_para_html_para_comando(tree):
    ns_map = {'tei': 'http://www.tei-c.org/ns/1.0'} # Mapa de namespace para funções xpath
    tei_ns_url = 'http://www.tei-c.org/ns/1.0'    # String da URL do namespace TEI

    body = tree.find('.//tei:body', namespaces=ns_map)

    if body is None:
        return "<p>(Sem conteúdo no corpo TEI)</p>"

    # 1. Transformar tei:term em <a>
    # É bom fazer transformações estruturais maiores primeiro.
    for term_el in body.xpath('.//tei:term', namespaces=ns_map):
        lemma = term_el.get('lemma') or (term_el.text or '').strip()
        slug = slugify(lemma) # slugify já importado
        token = term_el.text or lemma # O texto visível do link

        term_el.tag = 'a' # Transforma o <term> em <a>
        try:
            url_consulta = reverse('verbetes:detalhe', args=[slug])
            term_el.set('href', url_consulta)
        except Exception as e:
            # Este fallback é para desenvolvimento, idealmente o reverse() sempre funciona
            print(f"AVISO: Falha ao gerar URL para o termo '{lemma}' (slug: '{slug}'). Erro: {e}. Usando caminho relativo hardcoded.")
            term_el.set('href', f"/consulta/{slug}/") # Verifique sua estrutura de URL

        term_el.text = token # Define o texto do link
        # Limpa atributos TEI que não são mais necessários no <a>
        # Adicione outros atributos específicos do <term> TEI que você quer remover
        for attr_name in list(term_el.attrib.keys()): # Itera sobre uma cópia das chaves para poder deletar
            if attr_name not in ['href', 'class', 'id', 'style', 'title']: # Mantenha atributos HTML padrão
                # Se o atributo tiver namespace (ex: xml:lang), precisa de tratamento especial ou lxml cuida disso
                # ao remover. Verifique se atributos como 'lemma' são removidos.
                # A forma mais segura é listar explicitamente os que quer remover:
                # for attr_to_remove in ['lemma', 'norm', 'msd', 'senseNumber', '{http://www.w3.org/XML/1998/namespace}lang']:
                if attr_name in ['lemma', 'norm', 'msd', 'senseNumber', 'type', 'ana', 'corresp', 'ref']: # Adicione outros atributos TEI aqui
                    del term_el.attrib[attr_name]


    # 2. Chamar a função para substituir/modificar outras tags TEI como <pb>, <s>, <note>
    substituir_tags_inadequadas(body, tei_ns_url)


    # 3. Limpeza final de namespaces (OPCIONAL, mas recomendado para HTML puro)
    # Esta etapa remove os prefixos de namespace (ex: tei:) das tags e atributos,
    # tornando o HTML mais "puro".
    # CUIDADO: Faça isso por último, depois que todas as manipulações baseadas em tags TEI (com namespace)
    # já foram feitas.
    for el in body.iter('*'): # Itera sobre todos os elementos dentro de <body>
        if '}' in el.tag: # Se a tag ainda tiver um namespace URI (ex: {http://www.tei-c.org/ns/1.0}p)
            el.tag = el.tag.split('}', 1)[1] # Pega apenas a parte local da tag (ex: 'p')
        # Limpar atributos com namespace também, se houver
        for attr_name_ns in list(el.attrib.keys()):
            if '}' in attr_name_ns:
                local_attr_name = attr_name_ns.split('}', 1)[1]
                el.attrib[local_attr_name] = el.attrib.pop(attr_name_ns)

    # Converte a árvore lxml (o elemento body modificado) para uma string HTML
    html_string = etree.tostring(body, method='html', encoding='unicode', pretty_print=True)
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

        if not obras_a_processar.exists() and not slug_especifico: # Mudança aqui para verificar se existe antes de count()
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
                # Chama a função de conversão principal
                html_content = converter_tei_para_html_para_comando(tree)

                obra.conteudo_html_processado = html_content
                obra.save()
                self.stdout.write(self.style.SUCCESS(f'  HTML gerado e salvo para "{obra.titulo}"'))

            except etree.ParseError as e:
                self.stderr.write(self.style.ERROR(f'  Erro ao parsear XML para "{obra.titulo}": {e}'))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f'  Erro inesperado ao processar "{obra.titulo}": {e}'))
                # Para depuração, pode ser útil ver o traceback completo em desenvolvimento
                import traceback
                traceback.print_exc()


        self.stdout.write(self.style.SUCCESS('Processamento concluído.'))