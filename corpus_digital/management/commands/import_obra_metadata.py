import re
from pathlib import Path
from lxml import etree # lxml para parsear XML

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings # Para acessar CORPUS_XML_ROOT
from django.utils.text import slugify # Para gerar slugs
from corpus_digital.models import Obra # Para o modelo Obra

class Command(BaseCommand):
    help = 'Importa ou atualiza metadados de obras (título, autor, caminho do arquivo) para o modelo Obra, lendo de arquivos XML TEI.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear-all',
            action='store_true',
            help='Apaga TODOS os dados de obras antes da importação.',
        )
        parser.add_argument(
            '--slug',
            type=str,
            help='Importa/atualiza apenas a obra com o slug especificado.',
        )
        parser.add_argument(
            '--force-update',
            action='store_true',
            help='Força a atualização de obras existentes, mesmo que o slug já exista. (Padrão para update_or_create).',
        )

    def handle(self, *args, **options):
        clear_all = options['clear_all']
        slug_especifico = options['slug']
        # force_update é padrão no update_or_create, mas pode ser útil para clareza na UX do comando

        ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
        
        if clear_all:
            self.stdout.write(self.style.WARNING('Apagando todos os dados de Obras existentes...'))
            Obra.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Dados de Obras antigos apagados.'))

        self.stdout.write(self.style.HTTP_INFO('Iniciando importação/atualização de obras...'))
        
        if not settings.CORPUS_XML_ROOT.exists():
             raise CommandError(f"Diretório CORPUS_XML_ROOT não encontrado: {settings.CORPUS_XML_ROOT}. Pulando importação de obras.")

        xml_files_to_process = list(settings.CORPUS_XML_ROOT.glob('*.xml'))
        if slug_especifico:
            xml_files_to_process = [f for f in xml_files_to_process if f.stem.lower() == slug_especifico.lower()]
            if not xml_files_to_process:
                raise CommandError(f"Nenhum arquivo XML encontrado para o slug '{slug_especifico}'.")

        if not xml_files_to_process:
            self.stdout.write(self.style.WARNING('Nenhum arquivo XML encontrado para importar obras.'))
            return

        # Esta função extrai título e autor do XML, com a lógica de limpeza de PIs
        def _extrair_titulo_autor_obra_from_xml(xml_path):
            try:
                tree = etree.parse(str(xml_path)) # etree.parse() é mais robusto para PIs iniciais
                
                # Limpeza de PIs e comentários na árvore
                root_obra = tree.getroot()
                for node in list(root_obra.xpath('./node()')):
                    if isinstance(node, etree._ProcessingInstruction) and not node.tag.startswith('xml'):
                        root_obra.remove(node)
                    if isinstance(node, etree._Comment):
                        root_obra.remove(node)
                for el in root_obra.iter():
                     for child in list(el.xpath('./node()')):
                        if isinstance(child, etree._ProcessingInstruction) and not child.tag.startswith('xml'):
                            el.remove(child)
                        if isinstance(child, etree._Comment):
                            el.remove(child)
            except etree.ParseError as e:
                # Loga o erro de parsing e re-levanta como CommandError para parar o processo para esta obra
                raise CommandError(f'Erro de parsing XML para obra {xml_path.name}: {e}')
            except Exception as e:
                raise CommandError(f'Erro inesperado ao abrir ou parsear XML para obra {xml_path.name}: {e}')

            bibl = tree.find('.//tei:teiHeader//tei:sourceDesc//tei:bibl', namespaces=ns)
            if bibl is not None:
                title = bibl.findtext('tei:title', default='(Sem título)', namespaces=ns)
                author = bibl.findtext('tei:author', default='(Sem autor)', namespaces=ns)
                title = re.sub(r'\s+', ' ', title).strip()
                author = re.sub(r'\s+', ' ', author).strip()
                return title, author
            return '(Sem título)', '(Sem autor)'

        for xml_file in xml_files_to_process:
            try:
                self.stdout.write(f'  Importando Obra: {xml_file.name}')
                titulo, autor = _extrair_titulo_autor_obra_from_xml(xml_file)
                slug = slugify(xml_file.stem)
                caminho_arquivo_relativo = xml_file.name

                obra, criado = Obra.objects.update_or_create(
                    slug=slug, # Chave para identificar a obra
                    defaults={ # Campos a serem atualizados ou preenchidos se for criado
                        'titulo': titulo,
                        'autor': autor,
                        'caminho_arquivo': caminho_arquivo_relativo,
                    }
                )
                if criado:
                    self.stdout.write(self.style.SUCCESS(f"✔️ Criado Obra: {titulo} ({slug})"))
                else:
                    self.stdout.write(self.style.NOTICE(f"🔁 Atualizado Obra: {titulo} ({slug})"))

            except CommandError as e: # Captura CommandError específicos da função aninhada
                self.stderr.write(self.style.ERROR(f'{e}'))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f'Erro inesperado ao importar obra {xml_file.name}: {e}'))

        self.stdout.write(self.style.SUCCESS('Comando import_obra_metadata concluído.'))