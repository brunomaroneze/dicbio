import csv
import re
import io
import codecs
from pathlib import Path
from lxml import etree

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils.text import slugify
from corpus_digital.models import Obra

class Command(BaseCommand):
    help = 'Gera termos_extraidos.csv a partir de XMLs TEI e importa os metadados das obras para o modelo Obra.'

    def add_arguments(self, parser):
        parser.add_argument('--force-csv-regen', action='store_true', help='Força a regeneração do termos_extraidos.csv.')
        parser.add_argument('--skip-csv-regen', action='store_true', help='Pula a geração do CSV.')
        parser.add_argument('--skip-obra-import', action='store_true', help='Pula a importação das obras.')

    def handle(self, *args, **options):
        ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
        force_csv = options['force_csv_regen']
        skip_csv = options['skip_csv_regen']
        skip_obra = options['skip_obra_import']
        output_csv_file = settings.BASE_DIR / "data" / "termos_extraidos.csv"
        all_rows = []

        if not skip_csv:
            self.stdout.write(self.style.HTTP_INFO('Iniciando geração do CSV...'))

            if not settings.CORPUS_XML_ROOT.exists():
                raise CommandError(f'Diretório não encontrado: {settings.CORPUS_XML_ROOT}')

            xml_files = list(settings.CORPUS_XML_ROOT.glob('*.xml'))

            if not xml_files:
                self.stdout.write(self.style.WARNING('Nenhum arquivo XML encontrado.'))
                return

            if output_csv_file.exists() and not force_csv:
                self.stdout.write(self.style.NOTICE(f'{output_csv_file.name} já existe. Use --force-csv-regen para regenerar.'))
            else:
                for file_path in xml_files:
                    self.stdout.write(f'Processando XML: {file_path.name}')
                    try:
                        try:
                            tree = etree.parse(str(file_path))
                        except etree.ParseError:
                            # Fallback com codificações diferentes
                            xml_string = None
                            for encoding in ['utf-8-sig', 'utf-8', 'latin-1']:
                                try:
                                    with codecs.open(file_path, 'r', encoding=encoding) as f:
                                        xml_string = f.read()
                                    break
                                except Exception:
                                    continue
                            if not xml_string:
                                raise CommandError(f'Erro ao ler o arquivo {file_path.name} com qualquer codificação.')
                            
                            try:
                                tree = etree.parse(io.StringIO(xml_string))
                            except Exception as e:
                                raise CommandError(f'Erro ao parsear XML {file_path.name} no fallback: {e}')

                        root = tree.getroot()

                        # Limpeza de instruções de processamento e comentários
                        for node in list(root.xpath('./node()')):
                            if isinstance(node, etree._ProcessingInstruction) and not node.tag.startswith('xml'):
                                root.remove(node)
                            if isinstance(node, etree._Comment):
                                root.remove(node)
                        for el in root.iter():
                            for child in list(el.xpath('./node()')):
                                if isinstance(child, etree._ProcessingInstruction) and not child.tag.startswith('xml'):
                                    el.remove(child)
                                if isinstance(child, etree._Comment):
                                    el.remove(child)

                        # Extração de título
                        title_el = tree.find('.//tei:teiHeader//tei:sourceDesc//tei:bibl/tei:title', namespaces=ns)
                        title = re.sub(r'\s+', ' ', title_el.text.strip()) if title_el is not None else '(Sem título)'
                        slug_obra = file_path.stem.lower()

                        terms = tree.xpath('//tei:term', namespaces=ns)
                        if not terms:
                            self.stdout.write(self.style.WARNING(f'  Nenhum <term> em {file_path.name}.'))
                            continue

                        for term in terms:
                            token = (term.text or '').strip()
                            headword = term.get('lemma', token)
                            orth = term.get('norm', headword)
                            gram = term.get('msd', '')
                            sense_number = term.get('senseNumber', '1')

                            parent = term.getparent()
                            if parent is None:
                                continue

                            parent_copy = etree.fromstring(etree.tostring(parent, encoding='unicode'))
                            term_copy = parent_copy.xpath(f".//tei:term[@lemma='{headword}' or .='{token}']", namespaces=ns)

                            if term_copy:
                                term_el = term_copy[0]
                                bold = etree.Element('b')
                                bold.text = term_el.text
                                bold.tail = term_el.tail
                                term_el.getparent().replace(term_el, bold)
                                sentence_text = etree.tostring(parent_copy, method='text', encoding='unicode').strip()
                            else:
                                sentence_text = ''.join(parent.itertext()).strip().replace(token, f'<b>{token}</b>', 1)

                            author_el = term.xpath('.//ancestor::tei:TEI//tei:author', namespaces=ns)
                            author_raw = author_el[0].text.strip() if author_el and author_el[0].text else 'AutorDesconhecido'
                            author_surname = (author_raw.split(',')[0] if ',' in author_raw else author_raw.split()[-1]).upper()

                            date_el = term.xpath('.//ancestor::tei:TEI//tei:date', namespaces=ns)
                            date = date_el[0].text.strip() if date_el and date_el[0].text else 's.d.'

                            pb_el = term.xpath('./preceding::tei:pb[1]', namespaces=ns)
                            page = pb_el[0].get('n', '?') if pb_el else '?'

                            sentence_final = f'{sentence_text} ({author_surname}, {date}, {title}, p. {page})'

                            all_rows.append([
                                token, headword, orth, gram, sense_number,
                                sentence_final, author_surname, date, title, slug_obra
                            ])

                    except Exception as e:
                        self.stderr.write(self.style.ERROR(f'Erro ao processar {file_path.name}: {e}'))

                if all_rows:
                    output_csv_file.parent.mkdir(parents=True, exist_ok=True)
                    with open(output_csv_file, 'w', encoding='utf-8', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow([
                            "token", "Headword", "orth", "gram", "SenseNumber",
                            "sentence", "author_surname", "date", "title", "slug_obra"
                        ])
                        writer.writerows(all_rows)
                    self.stdout.write(self.style.SUCCESS(f'CSV gerado com sucesso: {output_csv_file}'))
                else:
                    self.stdout.write(self.style.WARNING('Nenhum dado para escrever no CSV.'))

        else:
            self.stdout.write(self.style.NOTICE('Geração de CSV pulada (--skip-csv-regen).'))

        # --- Parte 2: Importar obras ---
        if not skip_obra:
            self.stdout.write(self.style.HTTP_INFO('Importando obras para o modelo Obra...'))
            xml_files = list(settings.CORPUS_XML_ROOT.glob('*.xml'))
            if not xml_files:
                self.stdout.write(self.style.WARNING('Nenhum XML encontrado para importar obras.'))
                return

            for xml_file in xml_files:
                try:
                    tree = etree.parse(str(xml_file))
                    ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
                    bibl = tree.find('.//tei:teiHeader//tei:sourceDesc//tei:bibl', namespaces=ns)
                    title = bibl.findtext('tei:title', default='(Sem título)', namespaces=ns).strip()
                    author = bibl.findtext('tei:author', default='(Sem autor)', namespaces=ns).strip()
                    slug = slugify(xml_file.stem)
                    caminho = xml_file.name

                    obra, created = Obra.objects.update_or_create(
                        slug=slug,
                        defaults={
                            'titulo': title,
                            'autor': author,
                            'caminho_arquivo': caminho,
                        }
                    )
                    msg = f"✔️ Criado Obra: {title}" if created else f"🔁 Atualizado Obra: {title}"
                    self.stdout.write(self.style.SUCCESS(msg))

                except Exception as e:
                    self.stderr.write(self.style.ERROR(f'Erro ao importar {xml_file.name}: {e}'))

        self.stdout.write(self.style.SUCCESS('Comando import_corpus_data concluído.'))
