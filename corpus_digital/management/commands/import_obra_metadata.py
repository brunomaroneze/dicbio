import re
from pathlib import Path
from lxml import etree

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils.text import slugify
from corpus_digital.models import Obra

class Command(BaseCommand):
    help = 'Importa ou atualiza metadados de obras (título, autor, data, caminho do arquivo) para o modelo Obra, lendo de arquivos XML TEI.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear-all',
            action='store_true',
            help='Apaga TODOS os dados de obras antes da importação.',
        )
        parser.add_argument(
            '--slug',
            type=str,
            help='Importa/atualiza apenas a obra com o slug especificado (usa o nome do arquivo XML sem extensão como slug base).',
        )
        # --force-update não é mais necessário aqui, pois update_or_create já faz isso.

    def handle(self, *args, **options):
        clear_all = options['clear_all']
        slug_especifico_arg = options['slug'] # Nome do arquivo XML sem extensão

        ns_tei = {'tei': 'http://www.tei-c.org/ns/1.0'}
        
        if clear_all:
            self.stdout.write(self.style.WARNING('Apagando todos os dados de Obras existentes...'))
            Obra.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Dados de Obras antigos apagados.'))

        self.stdout.write(self.style.HTTP_INFO('Iniciando importação/atualização de obras...'))
        
        corpus_root_path = Path(settings.CORPUS_XML_ROOT) # Garante que é um objeto Path
        if not corpus_root_path.exists():
             raise CommandError(f"Diretório CORPUS_XML_ROOT não encontrado: {corpus_root_path}. Pulando importação de obras.")

        # Obtém todos os arquivos .xml no diretório raiz do corpus
        # Se você tiver subpastas, precisaria de .glob('**/*.xml')
        xml_files_to_process = list(corpus_root_path.glob('*.xml'))
        
        if slug_especifico_arg:
            # Filtra a lista para corresponder ao slug fornecido (nome do arquivo sem extensão)
            xml_files_to_process = [
                f for f in xml_files_to_process if f.stem.lower() == slug_especifico_arg.lower()
            ]
            if not xml_files_to_process:
                raise CommandError(f"Nenhum arquivo XML encontrado correspondente ao slug (nome do arquivo) '{slug_especifico_arg}'. Verifique o nome do arquivo em {corpus_root_path}.")

        if not xml_files_to_process:
            self.stdout.write(self.style.WARNING(f'Nenhum arquivo XML encontrado em {corpus_root_path} para importar obras.'))
            return

        # Esta função agora extrai título, autor e data da obra do XML
        def _extrair_metadados_obra_from_xml(xml_path):
            try:
                # Usar um parser que remove PIs e comentários automaticamente é mais limpo
                parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
                tree = etree.parse(str(xml_path), parser)
            except etree.ParseError as e:
                raise CommandError(f'Erro de parsing XML para obra {xml_path.name}: {e}')
            except Exception as e:
                raise CommandError(f'Erro inesperado ao abrir ou parsear XML para obra {xml_path.name}: {e}')

            # Localizar o elemento <bibl> dentro de <sourceDesc>
            bibl_element = tree.find('.//tei:sourceDesc/tei:bibl', namespaces=ns_tei)
            
            if bibl_element is not None:
                # Extrair título
                title_text = bibl_element.findtext('tei:title', default='(Sem título)', namespaces=ns_tei)
                title_text = re.sub(r'\s+', ' ', title_text).strip()
                
                # Extrair autor
                author_text = '; '.join(
                    ''.join(a.itertext()) for a in bibl_element.findall('tei:author', namespaces=ns_tei)
                ) or '(Sem autor)'
                author_text = re.sub(r'\s+', ' ', author_text).strip()
                
                # Extrair data (do atributo @when se existir, senão o texto do elemento)
                date_element = bibl_element.find('tei:date', namespaces=ns_tei)
                date_text = None
                if date_element is not None:
                    # Prioriza o atributo @when se ele existir e for um ano de 4 dígitos
                    date_when = date_element.get('when')
                    if date_when and re.match(r'^\d{4}$', date_when.strip()): # Verifica se é um ano de 4 dígitos
                        date_text = date_when.strip()
                    elif date_element.text: # Senão, usa o texto do elemento <date>
                        date_text = date_element.text.strip()
                    else: # Se não tiver @when nem texto
                        date_text = '(Sem data)'
                else:
                    date_text = '(Sem data)'
                
                return title_text, author_text, date_text
            else:
                self.stdout.write(self.style.WARNING(f"  Elemento <bibl> não encontrado em {xml_path.name}. Usando padrões."))
                return '(Sem título)', '(Sem autor)', '(Sem data)'

        # Loop principal para processar cada arquivo XML
        for xml_file in xml_files_to_process:
            try:
                self.stdout.write(f'  Processando arquivo: {xml_file.name}')
                
                # Extrai metadados do XML
                titulo, autor, data_ref = _extrair_metadados_obra_from_xml(xml_file)
                
                # O slug da obra no banco de dados será baseado no nome do arquivo XML (sem extensão)
                # Isso garante uma correspondência direta entre o arquivo e o objeto Obra.
                # O slug gerado no modelo Obra.save() usará autor+título, mas aqui usamos o nome do arquivo
                # para o `update_or_create` encontrar o objeto correto ou criar um novo com este slug.
                slug_base_arquivo = slugify(xml_file.stem) 
                caminho_arquivo_relativo = xml_file.name # Salva o nome do arquivo

                # Cria ou atualiza a obra no banco de dados
                obra_obj, criado = Obra.objects.update_or_create(
                    slug=slug_base_arquivo, # Usa o slug do nome do arquivo como chave única
                    defaults={
                        'titulo': titulo,
                        'autor': autor,
                        'data_referencia': data_ref, # <-- NOVO CAMPO SENDO SALVO
                        'caminho_arquivo': caminho_arquivo_relativo,
                        # 'ordem' pode ser preenchido manualmente ou por outro script, se necessário
                    }
                )
                
                # O slug salvo no BD pode ser diferente do slug_base_arquivo se o método Obra.save()
                # o modificar (ex: para garantir unicidade com autor+título).
                # Para consistência, após criar/atualizar, forçamos o slug do modelo a ser o slug_base_arquivo.
                # Isso pode não ser ideal se você depende do slug gerado pelo modelo Obra.save() ser autor+título.
                # Uma alternativa é usar um campo diferente para o "identificador do arquivo"
                # e deixar o slug ser gerado pelo modelo.
                # Por agora, vamos manter o slug do arquivo como o slug principal para este comando.
                if obra_obj.slug != slug_base_arquivo:
                     obra_obj.slug = slug_base_arquivo # Garante que o slug no BD seja o do nome do arquivo
                     obra_obj.save(update_fields=['slug'])


                if criado:
                    self.stdout.write(self.style.SUCCESS(f"✔️  Criada Obra: '{obra_obj.titulo}' (Autor: {obra_obj.autor}, Data: {obra_obj.data_referencia}, Slug: {obra_obj.slug})"))
                else:
                    self.stdout.write(self.style.NOTICE(f"🔁 Atualizada Obra: '{obra_obj.titulo}' (Autor: {obra_obj.autor}, Data: {obra_obj.data_referencia}, Slug: {obra_obj.slug})"))

            except CommandError as e: # Captura CommandError da função _extrair_metadados_obra_from_xml
                self.stderr.write(self.style.ERROR(f'Erro ao processar {xml_file.name}: {e}'))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f'Erro inesperado ao importar obra de {xml_file.name}: {e}'))
                import traceback
                traceback.print_exc() # Para depuração mais detalhada de erros inesperados

        self.stdout.write(self.style.SUCCESS('Comando import_obra_metadata concluído.'))